"""Fail-closed request contract for the exact Windigo three-program bundle."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import uuid4

from .provider_acquisition import USER_AGENT


CONTRACT_VERSION = "windigo-reference-request-v0.1.0"
UNIT_ID = "P2O4-T35-U02"
EVENT_ID = "OR4336312205020220730"
BRANCH = "codex/p2o4-t35-windigo-deadline-gate"
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
    "comment",
)

EXPECTED_PRODUCTS: tuple[dict[str, Any], ...] = (
    {
        "catalog_id": 34817,
        "map_id": 10022395,
        "program": "BAER",
        "incident_name": "WINDIGO",
        "event_id": EVENT_ID,
        "ignition_date": "2022-07-30",
        "boundary_acres": 1201,
        "provider_comment": None,
        "nonstandard": False,
    },
    {
        "catalog_id": 25674,
        "map_id": 10022960,
        "program": "RAVG",
        "incident_name": "WINDIGO",
        "event_id": EVENT_ID,
        "ignition_date": "2022-07-30",
        "boundary_acres": 1005,
        "provider_comment": None,
        "nonstandard": False,
    },
    {
        "catalog_id": 42382,
        "map_id": 10029547,
        "program": "MTBS",
        "incident_name": "WINDIGO",
        "event_id": EVENT_ID,
        "ignition_date": "2022-07-30",
        "boundary_acres": 1068,
        "provider_comment": None,
        "nonstandard": False,
    },
)

MAPPING_PRODUCTS = (
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
    "path": (
        "samples/cross-event/phase-two/windigo/"
        "WINDIGO-OPTICAL-CUSTODY-2026-002.json"
    ),
    "bytes": 6_579,
    "sha256": "b05d3e71052331e094957717da798117776965b728e717bfe525b8b5196dc755",
    "decision": "PASS_WINDIGO_OPTICAL_CUSTODY_AUTHORIZE_REFERENCE_REQUEST_PREFLIGHT",
}

CUSTODY_PATHS = {
    "request_directory": (
        "downloads/phase-two/reference-requests/windigo-reference-request-v0.1.0"
    ),
    "delivery_quarantine": (
        "downloads/phase-two/quarantine/P2O4-T35-U03/windigo-reference-r001"
    ),
    "raw_package": "downloads/phase-two/raw/windigo-reference-v0.1.0",
    "run_state": (
        "downloads/phase-two/runs/P2O4-T35-U03/"
        "BL-2026-07-23-windigo-reference-r001.json"
    ),
}
PUBLIC_REPORT_PATH = (
    "samples/cross-event/phase-two/windigo/"
    "WINDIGO-REFERENCE-REQUEST-2026-001.json"
)


class WindigoReferenceRequestError(RuntimeError):
    """The exact Windigo reference request failed closed."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
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
    if not re.fullmatch(r"[0-9a-f]{40}", git_source_commit):
        raise WindigoReferenceRequestError("git source commit is invalid")
    top = _git(root, "rev-parse", "--show-toplevel")
    head = _git(root, "rev-parse", "HEAD")
    branch = _git(root, "branch", "--show-current")
    remote = _git(root, "rev-parse", f"origin/{BRANCH}")
    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != root:
        raise WindigoReferenceRequestError("repository root mismatch")
    if head.returncode != 0 or head.stdout.strip() != git_source_commit:
        raise WindigoReferenceRequestError("git source commit mismatch")
    if branch.returncode != 0 or branch.stdout.strip() != BRANCH:
        raise WindigoReferenceRequestError("branch mismatch")
    if remote.returncode != 0 or remote.stdout.strip() != git_source_commit:
        raise WindigoReferenceRequestError("remote checkpoint mismatch")
    if status.returncode != 0 or status.stdout.strip():
        raise WindigoReferenceRequestError("worktree must be clean")
    upstream = root / str(UPSTREAM_OPTICAL_REPORT["path"])
    if (
        not upstream.is_file()
        or upstream.stat().st_size != UPSTREAM_OPTICAL_REPORT["bytes"]
        or _sha256_file(upstream) != UPSTREAM_OPTICAL_REPORT["sha256"]
    ):
        raise WindigoReferenceRequestError("upstream optical report binding mismatch")
    payload = json.loads(upstream.read_text(encoding="utf-8"))
    if payload.get("decision") != UPSTREAM_OPTICAL_REPORT["decision"]:
        raise WindigoReferenceRequestError("upstream optical decision mismatch")
    relative = str(CUSTODY_PATHS["request_directory"])
    if _git(root, "check-ignore", "--quiet", "--no-index", "--", relative).returncode != 0:
        raise WindigoReferenceRequestError("request custody path is not ignored")
    if (root / relative).exists():
        raise WindigoReferenceRequestError(
            "request custody already exists; do not submit or retry"
        )


def metadata_url() -> str:
    query = urlencode(
        (
            ("service", "WFS"),
            ("version", "2.0.0"),
            ("request", "GetFeature"),
            ("typeNames", "mtbs:fire_polygons"),
            ("outputFormat", "application/json"),
            ("propertyName", ",".join(PROPERTY_NAMES)),
            ("cql_filter", f"event_id='{EVENT_ID}'"),
        )
    )
    return f"{WFS_ENDPOINT}?{query}"


def request_payload() -> dict[str, Any]:
    return {
        "download_type": "mapping_products",
        "mapping_bundles": [],
        "mapping_ids": [item["map_id"] for item in EXPECTED_PRODUCTS],
        "mapping_products": list(MAPPING_PRODUCTS),
        "projection": "UTM",
        "mosaics": [],
    }


def normalize_metadata(raw: bytes) -> list[dict[str, Any]]:
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise WindigoReferenceRequestError("metadata response is not JSON") from error
    features = payload.get("features")
    if not isinstance(features, list) or len(features) != 3:
        raise WindigoReferenceRequestError(
            "metadata response must contain exactly three rows"
        )
    normalized: list[dict[str, Any]] = []
    for feature in features:
        if not isinstance(feature, dict) or feature.get("geometry") is not None:
            raise WindigoReferenceRequestError(
                "metadata response must remain property-only"
            )
        properties = feature.get("properties")
        if not isinstance(properties, dict):
            raise WindigoReferenceRequestError("metadata properties are invalid")
        normalized.append(
            {
                "catalog_id": properties.get("id"),
                "map_id": properties.get("map_id"),
                "program": properties.get("map_prog"),
                "incident_name": properties.get("incid_name"),
                "event_id": properties.get("event_id"),
                "ignition_date": str(properties.get("ig_date"))[:10],
                "boundary_acres": properties.get("burnbndac"),
                "provider_comment": properties.get("comment"),
                "nonstandard": properties.get("nonstandard"),
            }
        )
    normalized.sort(key=lambda item: int(item["map_id"]))
    expected = sorted(
        (dict(item) for item in EXPECTED_PRODUCTS),
        key=lambda item: int(item["map_id"]),
    )
    if normalized != expected:
        raise WindigoReferenceRequestError(
            "Windigo metadata identity, standard status, or cautions drifted"
        )
    return normalized


def _read_bounded(response: Any, maximum: int, label: str) -> bytes:
    status = int(getattr(response, "status", 200))
    if status != 200:
        raise WindigoReferenceRequestError(
            f"{label} endpoint returned HTTP {status}"
        )
    data = response.read(maximum + 1)
    if len(data) > maximum:
        raise WindigoReferenceRequestError(f"{label} response exceeds bounded size")
    return data


def fetch_metadata(*, timeout_seconds: int = 90) -> bytes:
    request = Request(
        metadata_url(),
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            raw = _read_bounded(response, MAX_METADATA_BYTES, "metadata")
    except OSError as error:
        raise WindigoReferenceRequestError(
            "official metadata endpoint is unavailable"
        ) from error
    normalize_metadata(raw)
    return raw


def _post_queue(recipient: str, *, timeout_seconds: int = 90) -> bytes:
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", recipient):
        raise WindigoReferenceRequestError("recipient is missing or invalid")
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
        with urlopen(request, timeout=timeout_seconds) as response:
            return _read_bounded(response, MAX_QUEUE_BYTES, "queue")
    except OSError as error:
        raise WindigoReferenceRequestError(
            "queue outcome is unknown; do not retry automatically"
        ) from error


def _validate_queue_response(raw: bytes) -> None:
    try:
        accepted = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise WindigoReferenceRequestError("queue response is not JSON") from error
    if accepted != {"success": True}:
        raise WindigoReferenceRequestError(
            "official queue did not accept the exact request"
        )


def _write_json_no_overwrite(path: Path, payload: dict[str, Any]) -> None:
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError:
        raise WindigoReferenceRequestError(
            f"transaction state exists; no overwrite allowed: {path.name}"
        ) from None


def acquire_request_receipt(
    output_directory: Path,
    *,
    repository_root: Path,
    recipient: str,
    requested_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    root = repository_root.resolve()
    expected_output = (root / CUSTODY_PATHS["request_directory"]).resolve()
    if output_directory.resolve() != expected_output:
        raise WindigoReferenceRequestError(
            "output directory violates the exact custody contract"
        )
    if output_directory.exists():
        raise WindigoReferenceRequestError(
            "request custody already exists; do not submit or retry"
        )
    verify_repository_preflight(root, git_source_commit)
    if not requested_at_utc.endswith("Z"):
        raise WindigoReferenceRequestError("request time must be explicit UTC")
    if run_id != "BL-2026-07-23-windigo-reference-request-r001":
        raise WindigoReferenceRequestError("run ID mismatch")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", recipient):
        raise WindigoReferenceRequestError("recipient is missing or invalid")

    output_directory.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_directory.with_name(
        f".{output_directory.name}.tmp-{uuid4().hex}"
    )
    promoted = False
    try:
        temporary.mkdir()
        metadata = fetch_metadata()
        products = normalize_metadata(metadata)
        payload = request_payload()
        prepared = {
            "contract_version": CONTRACT_VERSION,
            "requested_at_utc": requested_at_utc,
            "run_id": run_id,
            "unit_id": UNIT_ID,
            "git_source_commit": git_source_commit,
            "repository": "drwbkr1/burnlens-deschutes",
            "event_id": EVENT_ID,
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
                "canonical_payload_sha256": _sha256(
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
                "sha256": _sha256(metadata),
                "products": products,
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
                "mapping_ids": payload["mapping_ids"],
                "canonical_payload_sha256": prepared["request"][
                    "canonical_payload_sha256"
                ],
                "state": "QUEUE_POST_ATTEMPT_STARTED_DO_NOT_DUPLICATE",
                "recipient": "WITHHELD_PRIVATE",
            },
        )
        try:
            queue = _post_queue(recipient)
        except WindigoReferenceRequestError:
            _write_json_no_overwrite(
                output_directory / "queue-outcome-unknown.json",
                {
                    "contract_version": CONTRACT_VERSION,
                    "requested_at_utc": requested_at_utc,
                    "run_id": run_id,
                    "git_source_commit": git_source_commit,
                    "event_id": EVENT_ID,
                    "mapping_ids": payload["mapping_ids"],
                    "state": "QUEUE_OUTCOME_UNKNOWN_DO_NOT_RETRY",
                    "provider_response_bytes_retained": 0,
                    "recipient": "WITHHELD_PRIVATE",
                },
            )
            raise
        (output_directory / "queue-response.json").write_bytes(queue)
        try:
            _validate_queue_response(queue)
        except WindigoReferenceRequestError:
            _write_json_no_overwrite(
                output_directory / "queue-explicit-failure.json",
                {
                    "contract_version": CONTRACT_VERSION,
                    "requested_at_utc": requested_at_utc,
                    "run_id": run_id,
                    "git_source_commit": git_source_commit,
                    "event_id": EVENT_ID,
                    "mapping_ids": payload["mapping_ids"],
                    "state": (
                        "QUEUE_EXPLICIT_RESPONSE_REJECTED_OR_INVALID_DO_NOT_RETRY"
                    ),
                    "queue_response_bytes": len(queue),
                    "queue_response_sha256": _sha256(queue),
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
                "sha256": _sha256(queue),
                "accepted": True,
            },
            "delivery": {
                "state": "PENDING_EMAIL_DELIVERY",
                "archives_received": 0,
                "provider_bytes_received": 0,
            },
        }
        _write_json_no_overwrite(
            output_directory / "request-receipt.json",
            receipt,
        )
        return receipt
    except Exception:
        if not promoted:
            shutil.rmtree(temporary, ignore_errors=True)
        raise


def build_public_request_report(
    *,
    repository_root: Path,
    reconciliation_commit: str,
) -> dict[str, Any]:
    root = repository_root.resolve()
    if not re.fullmatch(r"[0-9a-f]{40}", reconciliation_commit):
        raise WindigoReferenceRequestError("reconciliation commit is invalid")
    for arguments, expected, reason in (
        (("rev-parse", "--show-toplevel"), str(root), "repository root mismatch"),
        (("rev-parse", "HEAD"), reconciliation_commit, "reconciliation commit mismatch"),
        (("branch", "--show-current"), BRANCH, "branch mismatch"),
        (
            ("rev-parse", f"origin/{BRANCH}"),
            reconciliation_commit,
            "remote checkpoint mismatch",
        ),
    ):
        result = _git(root, *arguments)
        if result.returncode != 0 or result.stdout.strip() != expected:
            raise WindigoReferenceRequestError(reason)
    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if status.returncode != 0 or status.stdout.strip():
        raise WindigoReferenceRequestError("worktree must be clean")

    request_directory = root / str(CUSTODY_PATHS["request_directory"])
    expected_roster = (
        "metadata-response.json",
        "queue-attempt-started.json",
        "queue-response.json",
        "request-prepared.json",
        "request-receipt.json",
    )
    if not request_directory.is_dir():
        raise WindigoReferenceRequestError("private request custody is missing")
    observed_roster = tuple(
        path.name for path in sorted(request_directory.iterdir(), key=lambda path: path.name)
    )
    if observed_roster != expected_roster:
        raise WindigoReferenceRequestError("private request custody roster mismatch")
    bindings = {
        name: {
            "bytes": (request_directory / name).stat().st_size,
            "sha256": _sha256_file(request_directory / name),
        }
        for name in expected_roster
    }
    retained = b"\n".join((request_directory / name).read_bytes() for name in expected_roster)
    if re.search(rb"[^@\s]+@[^@\s]+\.[^@\s]+", retained):
        raise WindigoReferenceRequestError("private recipient leaked into custody")

    receipt = json.loads(
        (request_directory / "request-receipt.json").read_text(encoding="utf-8")
    )
    payload = request_payload()
    if (
        receipt.get("contract_version") != CONTRACT_VERSION
        or receipt.get("run_id") != "BL-2026-07-23-windigo-reference-request-r001"
        or receipt.get("git_source_commit")
        != "3bd0062abfb90ec6b0bbb542c2c2413e69ceab56"
        or receipt.get("event_id") != EVENT_ID
        or receipt.get("request", {}).get("state") != "ACCEPTED"
        or receipt.get("request", {}).get("recipient") != "WITHHELD_PRIVATE"
        or receipt.get("request", {}).get("mapping_ids") != payload["mapping_ids"]
        or receipt.get("request", {}).get("mapping_products")
        != payload["mapping_products"]
        or receipt.get("queue", {}).get("accepted") is not True
        or receipt.get("delivery", {}).get("state") != "PENDING_EMAIL_DELIVERY"
    ):
        raise WindigoReferenceRequestError("private request receipt binding mismatch")

    report = {
        "report_id": "WINDIGO-REFERENCE-REQUEST-2026-001",
        "report_schema_version": "0.1.0",
        "unit_id": UNIT_ID,
        "run_id": receipt["run_id"],
        "requested_at_utc": receipt["requested_at_utc"],
        "event_id": EVENT_ID,
        "trace": {
            "repository": "drwbkr1/burnlens-deschutes",
            "branch": BRANCH,
            "request_source_commit": receipt["git_source_commit"],
            "reconciliation_source_commit": reconciliation_commit,
            "issue": 534,
            "optical_report": UPSTREAM_OPTICAL_REPORT,
        },
        "request": {
            "state": "ACCEPTED",
            "projection": payload["projection"],
            "mapping_ids": payload["mapping_ids"],
            "mapping_products": payload["mapping_products"],
            "mapping_product_count": len(payload["mapping_products"]),
            "canonical_payload_sha256": receipt["request"][
                "canonical_payload_sha256"
            ],
            "recipient": "WITHHELD_PRIVATE",
        },
        "private_custody_bindings": bindings,
        "queue": {
            "accepted": True,
            "response_bytes": receipt["queue"]["bytes"],
            "response_sha256": receipt["queue"]["sha256"],
        },
        "delivery": {
            "state": "PENDING_EMAIL_DELIVERY",
            "archives_received": 0,
            "provider_bytes_received": 0,
        },
        "gate_results": {
            "exact_current_three_row_metadata": "pass",
            "exact_three_mapping_ids": "pass",
            "exact_eighteen_product_families": "pass",
            "single_queue_attempt": "pass",
            "explicit_queue_acceptance": "pass",
            "recipient_withheld_and_not_retained": "pass",
            "reference_notice_and_pixel_fitness": "not executed",
            "candidate_label_dataset_split_baseline_model": "not created",
        },
        "decision": "ACCEPT_REQUEST_RECEIPT_PENDING_EXACT_DELIVERY",
        "warning": (
            "Request acceptance is not source fitness, label truth, official status, "
            "field validation, operational readiness, or emergency guidance."
        ),
    }
    output = root / PUBLIC_REPORT_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    _write_json_no_overwrite(output, report)
    return report
