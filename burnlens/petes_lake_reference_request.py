"""Fail-closed request contract for the exact Petes Lake MTBS bundle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import uuid4

from .provider_acquisition import USER_AGENT


CONTRACT_VERSION = "petes-lake-reference-request-v0.1.0"
EVENT_ID = "OR4396912190120230825"
MAP_ID = 10031414
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
    "asmt_type",
    "post_id",
    "postfire_date",
    "model",
    "dnbr_offst",
    "dnbr_stddv",
    "nodata_t",
    "incgreen_t",
    "low_t",
    "mod_t",
    "high_t",
    "comment",
)

EXPECTED_PRODUCT: dict[str, Any] = {
    "catalog_id": 50890,
    "map_id": MAP_ID,
    "program": "MTBS",
    "incident_name": "PETES LAKE",
    "event_id": EVENT_ID,
    "ignition_date": "2023-08-25",
    "assessment_type": "Extended",
    "boundary_acres": 3372,
    "post_id": "804502920240811",
    "postfire_date": "2024-08-11",
    "model": None,
    "dnbr_offset": 14,
    "dnbr_stddev": 16,
    "nodata_threshold": -970,
    "increased_greenness_threshold": -150,
    "low_threshold": 70,
    "moderate_threshold": 570,
    "high_threshold": 330,
    "provider_comment": "Fire severity could be misrepresented in wetland areas.",
    "nonstandard": False,
}

# The Portal exposes cross-program options in one menu. Petes Lake has one MTBS
# record, so this request deliberately excludes every BAER- and RAVG-only family.
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

FROZEN_REFERENCE_IDENTITY = {
    "event_id": EVENT_ID,
    "map_id": MAP_ID,
    "program": "MTBS",
    "catalog_id_frozen": 50884,
    "catalog_id_current": 50890,
    "catalog_drift_disposition": (
        "ACCEPT_CURRENT_CATALOG_ROW_FOR_ACQUISITION_WITHOUT_CLAIMING_REPLACEMENT_SEMANTICS"
    ),
    "pre_image_id": "904502920230801",
    "post_image_id": "804502920240811",
    "source_record": "SOURCE-2026-029",
    "terms_record": "TERMS-2026-025",
    "wetland_warning": "Fire severity could be misrepresented in wetland areas.",
}

CUSTODY_PATHS = {
    "request_directory": (
        "downloads/phase-two/reference-requests/petes-lake-reference-request-v0.1.0"
    ),
    "delivery_quarantine": (
        "downloads/phase-two/quarantine/P2O4-T33-U04/petes-lake-mtbs-reference-r001"
    ),
    "raw_package": "downloads/phase-two/raw/petes-lake-mtbs-reference-v0.1.0",
    "run_state": "downloads/phase-two/runs/P2O4-T33-U04/petes-lake-mtbs-reference-r001.json",
    "tracked_custody_report": (
        "samples/cross-event/phase-two/petes-lake/PETES-LAKE-REFERENCE-CUSTODY-2026-001.json"
    ),
}

UPSTREAM_U03 = {
    "run_id": "BL-2026-07-21-petes-lake-replacement-source-fitness-r002",
    "report_path": (
        "samples/cross-event/phase-two/petes-lake/"
        "PETES-LAKE-REPLACEMENT-SOURCE-FITNESS-2026-001.json"
    ),
    "report_bytes": 60069,
    "report_sha256": "1aa88c0021c610e492d2645e3f2c49a4afe96d9d907e2ee4481948a4c58f2ebd",
    "disposition": "pass-with-spatial-exclusions",
}


class PetesLakeReferenceRequestError(RuntimeError):
    """The exact Petes Lake reference request failed closed."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
        "mapping_ids": [MAP_ID],
        "mapping_products": list(MTBS_MAPPING_PRODUCTS),
        "projection": "UTM",
        "mosaics": [],
    }


def _date(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)[:10]


def normalize_metadata(raw: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PetesLakeReferenceRequestError("metadata response is not JSON") from error
    features = payload.get("features")
    if not isinstance(features, list) or len(features) != 1:
        raise PetesLakeReferenceRequestError("metadata response must contain exactly one row")
    feature = features[0]
    if not isinstance(feature, dict) or feature.get("geometry") is not None:
        raise PetesLakeReferenceRequestError("metadata response must remain property-only")
    properties = feature.get("properties")
    if not isinstance(properties, dict):
        raise PetesLakeReferenceRequestError("metadata properties are invalid")
    normalized = {
        "catalog_id": properties.get("id"),
        "map_id": properties.get("map_id"),
        "program": properties.get("map_prog"),
        "incident_name": properties.get("incid_name"),
        "event_id": properties.get("event_id"),
        "ignition_date": _date(properties.get("ig_date")),
        "assessment_type": properties.get("asmt_type"),
        "boundary_acres": properties.get("burnbndac"),
        "post_id": properties.get("post_id"),
        "postfire_date": _date(properties.get("postfire_date")),
        "model": properties.get("model"),
        "dnbr_offset": properties.get("dnbr_offst"),
        "dnbr_stddev": properties.get("dnbr_stddv"),
        "nodata_threshold": properties.get("nodata_t"),
        "increased_greenness_threshold": properties.get("incgreen_t"),
        "low_threshold": properties.get("low_t"),
        "moderate_threshold": properties.get("mod_t"),
        "high_threshold": properties.get("high_t"),
        "provider_comment": properties.get("comment"),
        "nonstandard": properties.get("nonstandard"),
    }
    if normalized != EXPECTED_PRODUCT:
        raise PetesLakeReferenceRequestError("Petes Lake metadata identity or cautions drifted")
    return normalized


def _read_bounded(response: Any, maximum: int, label: str) -> bytes:
    status = int(getattr(response, "status", 200))
    if status != 200:
        raise PetesLakeReferenceRequestError(f"{label} endpoint returned HTTP {status}")
    data = response.read(maximum + 1)
    if len(data) > maximum:
        raise PetesLakeReferenceRequestError(f"{label} response exceeds bounded size")
    return data


def fetch_metadata(*, timeout_seconds: int = 90) -> bytes:
    request = Request(metadata_url(), headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            raw = _read_bounded(response, MAX_METADATA_BYTES, "metadata")
    except OSError as error:
        raise PetesLakeReferenceRequestError("official metadata endpoint is unavailable") from error
    normalize_metadata(raw)
    return raw


def _post_queue(recipient: str, *, timeout_seconds: int = 90) -> bytes:
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", recipient):
        raise PetesLakeReferenceRequestError("recipient is missing or invalid")
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
            raw = _read_bounded(response, MAX_QUEUE_BYTES, "queue")
    except OSError as error:
        raise PetesLakeReferenceRequestError(
            "queue outcome is unknown; do not retry automatically"
        ) from error

    return raw


def _validate_queue_response(raw: bytes) -> None:
    try:
        accepted = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PetesLakeReferenceRequestError("queue response is not JSON") from error
    if accepted != {"success": True}:
        raise PetesLakeReferenceRequestError("official queue did not accept the exact request")


def submit_request(recipient: str, *, timeout_seconds: int = 90) -> bytes:
    raw = _post_queue(recipient, timeout_seconds=timeout_seconds)
    _validate_queue_response(raw)
    return raw


def _write_json_no_overwrite(path: Path, payload: dict[str, Any]) -> None:
    if path.exists():
        raise PetesLakeReferenceRequestError(f"transaction state exists; no overwrite allowed: {path.name}")
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


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
    if not (root / ".git").exists() or not (root / "pyproject.toml").is_file():
        raise PetesLakeReferenceRequestError("repository root is not a BurnLens checkout")
    expected_output = (root / CUSTODY_PATHS["request_directory"]).resolve()
    if output_directory.resolve() != expected_output:
        raise PetesLakeReferenceRequestError("output directory violates the exact custody contract")
    if output_directory.exists():
        raise PetesLakeReferenceRequestError("output directory already exists; no overwrite allowed")
    if not re.fullmatch(r"[0-9a-f]{40}", git_source_commit):
        raise PetesLakeReferenceRequestError("git source commit must be an exact lowercase SHA-1")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", recipient):
        raise PetesLakeReferenceRequestError("recipient is missing or invalid")
    output_directory.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_directory.with_name(f".{output_directory.name}.tmp-{uuid4().hex}")
    promoted = False
    try:
        temporary.mkdir()
        metadata = fetch_metadata()
        product = normalize_metadata(metadata)
        payload = request_payload()
        prepared = {
            "contract_version": CONTRACT_VERSION,
            "requested_at_utc": requested_at_utc,
            "run_id": run_id,
            "unit_id": "P2O4-T33-U04",
            "git_source_commit": git_source_commit,
            "repository": "drwbkr1/burnlens-deschutes",
            "event_id": EVENT_ID,
            "map_id": MAP_ID,
            "frozen_reference_identity": FROZEN_REFERENCE_IDENTITY,
            "upstream_u03": UPSTREAM_U03,
            "custody_contract": {
                **CUSTODY_PATHS,
                "ignored_repository_local": True,
                "no_overwrite": True,
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
                "canonical_payload_sha256": _sha256(
                    json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
                ),
                "recipient": "WITHHELD_PRIVATE",
            },
            "metadata": {
                "url": metadata_url(),
                "bytes": len(metadata),
                "sha256": _sha256(metadata),
                "product": product,
                "threshold_fields_are_raw_provider_fields": True,
                "threshold_fields_are_not_interpreted_as_semantic_order": True,
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
                "canonical_payload_sha256": prepared["request"]["canonical_payload_sha256"],
                "state": "QUEUE_POST_ATTEMPT_STARTED_DO_NOT_DUPLICATE",
                "recipient": "WITHHELD_PRIVATE",
            },
        )
        try:
            queue = _post_queue(recipient)
        except PetesLakeReferenceRequestError:
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
        try:
            (output_directory / "queue-response.json").write_bytes(queue)
        except OSError as error:
            raise PetesLakeReferenceRequestError(
                "queue response could not be retained; do not retry automatically"
            ) from error
        try:
            _validate_queue_response(queue)
        except PetesLakeReferenceRequestError:
            _write_json_no_overwrite(
                output_directory / "queue-explicit-failure.json",
                {
                    "contract_version": CONTRACT_VERSION,
                    "requested_at_utc": requested_at_utc,
                    "run_id": run_id,
                    "git_source_commit": git_source_commit,
                    "event_id": EVENT_ID,
                    "map_id": MAP_ID,
                    "state": "QUEUE_EXPLICIT_RESPONSE_REJECTED_OR_INVALID_DO_NOT_RETRY",
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
        _write_json_no_overwrite(output_directory / "request-receipt.json", receipt)
        return receipt
    except Exception:
        if not promoted:
            shutil.rmtree(temporary, ignore_errors=True)
        raise
