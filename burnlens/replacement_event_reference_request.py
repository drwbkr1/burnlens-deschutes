"""Fail-closed request contract for the exact Ward Creek MTBS bundle."""

from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import uuid4

from .provider_acquisition import USER_AGENT


CONTRACT_VERSION = "ward-creek-reference-request-v0.1.0"
UNIT_ID = "P2O4-T39-U03"
TASK_ISSUE = 554
EVENT_ID = "OR4494912090120190812"
MAP_ID = 10016337
CATALOG_ID = 34073
BRANCH = "codex/p2o4-t39-replacement-event"
REPOSITORY = "drwbkr1/burnlens-deschutes"
QUEUE_ENDPOINT = "https://burnseverity.cr.usgs.gov/downloads/addQueue.php"
WFS_ENDPOINT = "https://edcintl.cr.usgs.gov/geoserver/wfs"
MAX_METADATA_BYTES = 64 * 1024
MAX_QUEUE_BYTES = 1024

PROPERTY_NAMES = (
    "id",
    "map_id",
    "map_prog",
    "incid_name",
    "event_id",
    "ig_date",
    "burnbndac",
    "nonstandard",
)

EXPECTED_PRODUCT: dict[str, Any] = {
    "catalog_id": CATALOG_ID,
    "map_id": MAP_ID,
    "program": "MTBS",
    "incident_name": "WARD CREEK 0769 RN",
    "event_id": EVENT_ID,
    "ignition_date": "2019-08-12",
    "boundary_acres": 2070,
    "nonstandard": False,
}

MTBS_MAPPING_PRODUCTS = (
    "Metadata",
    "Pre-fire reflectance",
    "Post-fire reflectance",
    "Continuous severity (i.e dnbr)",
    "Relative continuous severity (i.e rdnbr)",
    "Burned area boundary",
    "Non-processing mask",
    "KMZ",
    "PDF",
    "6 - Class thematic severity",
)

CROSS_PROGRAM_MAPPING_PRODUCTS = (
    "Soil burn severity",
    "Continuous basal area loss",
    "4 - Class basal area loss",
    "7 - Class basal area loss",
    "Continuous canopy cover loss",
    "5 - Class canopy cover loss",
    "Continuous composite burn index",
    "4 - Class composite burn index",
)

UPSTREAM_OPTICAL_REPORT = {
    "path": "samples/reference/phase-two/WARD-CREEK-OPTICAL-CUSTODY-2026-001.json",
    "bytes": 16_317,
    "sha256": "a8d89779b7508b439fee6cb5bc99dd926a62c56ab58da181b0f1b40b1bcc1f2f",
    "decision": "PASS_WARD_CREEK_OPTICAL_CUSTODY_AUTHORIZE_U03_REFERENCE_INTAKE",
}

CUSTODY_PATHS = {
    "request_directory": (
        "downloads/phase-two/reference-requests/"
        "ward-creek-reference-request-v0.1.0"
    ),
    "delivery_quarantine": (
        "downloads/phase-two/quarantine/P2O4-T39-U03/"
        "ward-creek-mtbs-reference-r001"
    ),
    "raw_package": "downloads/phase-two/raw/ward-creek-mtbs-reference-v0.1.0",
    "run_state": (
        "downloads/phase-two/runs/P2O4-T39-U03/"
        "BL-2026-07-24-ward-creek-reference-r001.json"
    ),
}
PUBLIC_REPORT_PATH = (
    "samples/reference/phase-two/WARD-CREEK-REFERENCE-REQUEST-2026-001.json"
)


class WardCreekReferenceRequestError(RuntimeError):
    """The exact Ward Creek reference request failed closed."""


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _file_digest(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def verify_repository_preflight(root: Path, git_source_commit: str) -> None:
    root = root.resolve()
    if re.fullmatch(r"[0-9a-f]{40}", git_source_commit) is None:
        raise WardCreekReferenceRequestError("git source commit is invalid")
    checks = (
        (("rev-parse", "--show-toplevel"), root.as_posix(), "repository root mismatch"),
        (("rev-parse", "HEAD"), git_source_commit, "git source commit mismatch"),
        (("branch", "--show-current"), BRANCH, "branch mismatch"),
        (
            ("rev-parse", f"origin/{BRANCH}"),
            git_source_commit,
            "remote checkpoint mismatch",
        ),
    )
    for arguments, expected, reason in checks:
        result = _git(root, *arguments)
        observed = result.stdout.strip().replace("\\", "/")
        if result.returncode != 0 or observed != expected:
            raise WardCreekReferenceRequestError(reason)
    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if status.returncode != 0 or status.stdout.strip():
        raise WardCreekReferenceRequestError("worktree must be clean")
    upstream = root / str(UPSTREAM_OPTICAL_REPORT["path"])
    if (
        not upstream.is_file()
        or upstream.stat().st_size != UPSTREAM_OPTICAL_REPORT["bytes"]
        or _file_digest(upstream) != UPSTREAM_OPTICAL_REPORT["sha256"]
    ):
        raise WardCreekReferenceRequestError("upstream optical report binding mismatch")
    payload = json.loads(upstream.read_text(encoding="utf-8"))
    if payload.get("decision") != UPSTREAM_OPTICAL_REPORT["decision"]:
        raise WardCreekReferenceRequestError("upstream optical decision mismatch")
    for relative in (*CUSTODY_PATHS.values(),):
        if _git(root, "check-ignore", "--quiet", "--no-index", "--", relative).returncode != 0:
            raise WardCreekReferenceRequestError(
                f"private custody path is not ignored: {relative}"
            )
    request_directory = root / CUSTODY_PATHS["request_directory"]
    public_report = root / PUBLIC_REPORT_PATH
    if request_directory.exists() or public_report.exists():
        raise WardCreekReferenceRequestError(
            "request or public receipt already exists; do not submit or retry"
        )
    if (
        _git(
            root,
            "check-ignore",
            "--quiet",
            "--no-index",
            "--",
            PUBLIC_REPORT_PATH,
        ).returncode
        != 1
    ):
        raise WardCreekReferenceRequestError("public report path is ignored")


def metadata_url() -> str:
    query = urlencode(
        (
            ("service", "WFS"),
            ("version", "2.0.0"),
            ("request", "GetFeature"),
            ("typeNames", "mtbs:fire_polygons"),
            ("outputFormat", "application/json"),
            ("propertyName", ",".join(PROPERTY_NAMES)),
            ("cql_filter", f"event_id='{EVENT_ID}' AND map_prog='MTBS'"),
        )
    )
    return f"{WFS_ENDPOINT}?{query}"


def request_payload() -> dict[str, Any]:
    return {
        "download_type": "mapping_products",
        "mapping_bundles": [],
        "mapping_ids": [MAP_ID],
        "mapping_products": list(MTBS_MAPPING_PRODUCTS),
        "projection": "UTM",
        "mosaics": [],
    }


def normalize_metadata(raw: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise WardCreekReferenceRequestError("metadata response is not JSON") from error
    features = payload.get("features")
    if not isinstance(features, list) or len(features) != 1:
        raise WardCreekReferenceRequestError(
            "metadata response must contain exactly one row"
        )
    feature = features[0]
    if not isinstance(feature, dict) or feature.get("geometry") is not None:
        raise WardCreekReferenceRequestError(
            "metadata response must remain property-only"
        )
    properties = feature.get("properties")
    if not isinstance(properties, dict):
        raise WardCreekReferenceRequestError("metadata properties are invalid")
    normalized = {
        "catalog_id": properties.get("id"),
        "map_id": properties.get("map_id"),
        "program": properties.get("map_prog"),
        "incident_name": properties.get("incid_name"),
        "event_id": properties.get("event_id"),
        "ignition_date": str(properties.get("ig_date"))[:10],
        "boundary_acres": properties.get("burnbndac"),
        "nonstandard": properties.get("nonstandard"),
    }
    if normalized != EXPECTED_PRODUCT:
        raise WardCreekReferenceRequestError(
            "Ward Creek MTBS metadata identity or standard status drifted"
        )
    return normalized


def _read_bounded(response: Any, maximum: int, label: str) -> bytes:
    status = int(getattr(response, "status", 200))
    if status != 200:
        raise WardCreekReferenceRequestError(
            f"{label} endpoint returned HTTP {status}"
        )
    data = response.read(maximum + 1)
    if len(data) > maximum:
        raise WardCreekReferenceRequestError(f"{label} response exceeds bounded size")
    return data


def fetch_metadata(
    *,
    timeout_seconds: int = 90,
    urlopen_fn: Callable[..., Any] = urlopen,
) -> bytes:
    request = Request(
        metadata_url(),
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    try:
        with urlopen_fn(request, timeout=timeout_seconds) as response:
            raw = _read_bounded(response, MAX_METADATA_BYTES, "metadata")
    except OSError as error:
        raise WardCreekReferenceRequestError(
            "official metadata endpoint is unavailable"
        ) from error
    normalize_metadata(raw)
    return raw


def _post_queue(
    recipient: str,
    *,
    timeout_seconds: int = 90,
    urlopen_fn: Callable[..., Any] = urlopen,
) -> bytes:
    if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", recipient) is None:
        raise WardCreekReferenceRequestError("recipient is missing or invalid")
    form = urlencode(
        {
            "products": json.dumps(request_payload(), separators=(",", ":")),
            "email": recipient,
            "request_origin": "'viewer'",
        }
    ).encode("utf-8")
    request = Request(
        QUEUE_ENDPOINT,
        data=form,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        },
        method="POST",
    )
    try:
        with urlopen_fn(request, timeout=timeout_seconds) as response:
            return _read_bounded(response, MAX_QUEUE_BYTES, "queue")
    except OSError as error:
        raise WardCreekReferenceRequestError(
            "queue outcome is unknown; do not retry automatically"
        ) from error


def _validate_queue_response(raw: bytes) -> None:
    try:
        accepted = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise WardCreekReferenceRequestError("queue response is not JSON") from error
    if accepted != {"success": True}:
        raise WardCreekReferenceRequestError(
            "official queue did not accept the exact request"
        )


def _write_json_no_overwrite(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError:
        raise WardCreekReferenceRequestError(
            f"transaction state exists; no overwrite allowed: {path.name}"
        ) from None


def acquire_request_receipt(
    *,
    repository_root: Path,
    recipient: str,
    requested_at_utc: str,
    run_id: str,
    git_source_commit: str,
    metadata_fetch_fn: Callable[[], bytes] = fetch_metadata,
    queue_post_fn: Callable[[str], bytes] = _post_queue,
) -> dict[str, Any]:
    root = repository_root.resolve()
    output_directory = root / CUSTODY_PATHS["request_directory"]
    verify_repository_preflight(root, git_source_commit)
    if output_directory.exists() or (root / PUBLIC_REPORT_PATH).exists():
        raise WardCreekReferenceRequestError(
            "request or public receipt exists; no overwrite or retry allowed"
        )
    if not requested_at_utc.endswith("Z"):
        raise WardCreekReferenceRequestError("request time must be explicit UTC")
    if run_id != "BL-2026-07-24-ward-creek-reference-request-r001":
        raise WardCreekReferenceRequestError("run ID mismatch")
    if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", recipient) is None:
        raise WardCreekReferenceRequestError("recipient is missing or invalid")
    output_directory.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_directory.with_name(
        f".{output_directory.name}.tmp-{uuid4().hex}"
    )
    promoted = False
    try:
        temporary.mkdir()
        metadata = metadata_fetch_fn()
        product = normalize_metadata(metadata)
        payload = request_payload()
        prepared = {
            "contract_version": CONTRACT_VERSION,
            "requested_at_utc": requested_at_utc,
            "run_id": run_id,
            "unit_id": UNIT_ID,
            "git_source_commit": git_source_commit,
            "repository": REPOSITORY,
            "event_id": EVENT_ID,
            "map_id": MAP_ID,
            "upstream_optical_report": UPSTREAM_OPTICAL_REPORT,
            "custody_contract": {
                **CUSTODY_PATHS,
                "ignored_repository_local": True,
                "no_overwrite": True,
                "private_recipient_retained": False,
                "private_retrieval_url_retained": False,
            },
            "request": {
                "state": "PREPARED_NOT_SUBMITTED",
                "projection": payload["projection"],
                "mapping_ids": payload["mapping_ids"],
                "mapping_products": payload["mapping_products"],
                "excluded_cross_program_mapping_products": list(
                    CROSS_PROGRAM_MAPPING_PRODUCTS
                ),
                "canonical_payload_sha256": _digest(
                    json.dumps(
                        payload,
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ),
                "recipient": "WITHHELD_PRIVATE",
            },
            "metadata": {
                "url": metadata_url(),
                "bytes": len(metadata),
                "sha256": _digest(metadata),
                "product": product,
            },
            "delivery": {
                "state": "NOT_REQUESTED",
                "archives_received": 0,
                "provider_bytes_received": 0,
            },
            "claim_boundaries": {
                "request_acceptance_is_delivery": False,
                "reference_pixels_opened": False,
                "candidate_or_label_created": False,
                "dataset_or_model_created": False,
            },
        }
        (temporary / "metadata-response.json").write_bytes(metadata)
        _write_json_no_overwrite(temporary / "request-prepared.json", prepared)
        temporary.rename(output_directory)
        promoted = True
        _write_json_no_overwrite(
            output_directory / "queue-attempt-started.json",
            {
                "contract_version": CONTRACT_VERSION,
                "requested_at_utc": requested_at_utc,
                "run_id": run_id,
                "git_source_commit": git_source_commit,
                "event_id": EVENT_ID,
                "map_id": MAP_ID,
                "canonical_payload_sha256": prepared["request"][
                    "canonical_payload_sha256"
                ],
                "state": "QUEUE_POST_ATTEMPT_STARTED_DO_NOT_DUPLICATE",
                "recipient": "WITHHELD_PRIVATE",
            },
        )
        try:
            queue = queue_post_fn(recipient)
        except WardCreekReferenceRequestError:
            _write_json_no_overwrite(
                output_directory / "queue-outcome-unknown.json",
                {
                    "contract_version": CONTRACT_VERSION,
                    "requested_at_utc": requested_at_utc,
                    "run_id": run_id,
                    "git_source_commit": git_source_commit,
                    "event_id": EVENT_ID,
                    "map_id": MAP_ID,
                    "state": "QUEUE_OUTCOME_UNKNOWN_DO_NOT_RETRY",
                    "provider_response_bytes_retained": 0,
                    "recipient": "WITHHELD_PRIVATE",
                },
            )
            raise
        (output_directory / "queue-response.json").write_bytes(queue)
        try:
            _validate_queue_response(queue)
        except WardCreekReferenceRequestError:
            _write_json_no_overwrite(
                output_directory / "queue-explicit-failure.json",
                {
                    "contract_version": CONTRACT_VERSION,
                    "requested_at_utc": requested_at_utc,
                    "run_id": run_id,
                    "git_source_commit": git_source_commit,
                    "event_id": EVENT_ID,
                    "map_id": MAP_ID,
                    "state": (
                        "QUEUE_EXPLICIT_RESPONSE_REJECTED_OR_INVALID_DO_NOT_RETRY"
                    ),
                    "queue_response_bytes": len(queue),
                    "queue_response_sha256": _digest(queue),
                    "recipient": "WITHHELD_PRIVATE",
                },
            )
            raise
        receipt = {
            **prepared,
            "request": {**prepared["request"], "state": "ACCEPTED"},
            "queue": {
                "endpoint": QUEUE_ENDPOINT,
                "bytes": len(queue),
                "sha256": _digest(queue),
                "accepted": True,
            },
            "delivery": {
                "state": "PENDING_EMAIL_DELIVERY",
                "archives_received": 0,
                "provider_bytes_received": 0,
            },
        }
        _write_json_no_overwrite(output_directory / "request-receipt.json", receipt)
        public_report = {
            "report_id": "WARD-CREEK-REFERENCE-REQUEST-2026-001",
            "report_schema_version": "0.1.0",
            "unit_id": UNIT_ID,
            "run_id": run_id,
            "requested_at_utc": requested_at_utc,
            "event_id": EVENT_ID,
            "map_id": MAP_ID,
            "trace": {
                "repository": REPOSITORY,
                "branch": BRANCH,
                "issue": TASK_ISSUE,
                "git_source_commit": git_source_commit,
                "optical_report": UPSTREAM_OPTICAL_REPORT,
            },
            "request": {
                "state": "ACCEPTED",
                "projection": payload["projection"],
                "mapping_ids": payload["mapping_ids"],
                "mapping_products": payload["mapping_products"],
                "mapping_product_count": len(payload["mapping_products"]),
                "excluded_cross_program_mapping_products": list(
                    CROSS_PROGRAM_MAPPING_PRODUCTS
                ),
                "canonical_payload_sha256": receipt["request"][
                    "canonical_payload_sha256"
                ],
                "recipient": "WITHHELD_PRIVATE",
            },
            "metadata": receipt["metadata"],
            "queue": {
                "accepted": True,
                "response_bytes": receipt["queue"]["bytes"],
                "response_sha256": receipt["queue"]["sha256"],
            },
            "delivery": receipt["delivery"],
            "gate_results": {
                "exact_current_single_mtbs_metadata": "pass",
                "exact_single_mapping_id": "pass",
                "exact_mtbs_only_product_families": "pass",
                "single_queue_attempt": "pass",
                "explicit_queue_acceptance": "pass",
                "recipient_withheld_and_not_retained": "pass",
                "reference_notice_and_pixel_fitness": "not executed",
                "candidate_label_dataset_split_baseline_model": "not created",
            },
            "decision": "ACCEPT_WARD_CREEK_REQUEST_RECEIPT_PENDING_EXACT_DELIVERY",
            "warning": (
                "Request acceptance is not source fitness, label truth, official "
                "status, field validation, operational readiness, or emergency guidance."
            ),
        }
        _write_json_no_overwrite(root / PUBLIC_REPORT_PATH, public_report)
        return public_report
    except Exception:
        if not promoted:
            shutil.rmtree(temporary, ignore_errors=True)
        raise
