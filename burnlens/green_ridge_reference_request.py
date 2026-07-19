"""Fail-closed request contract for exact Green Ridge official reference bundles."""

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


CONTRACT_VERSION = "green-ridge-reference-request-v0.1.0"
EVENT_ID = "OR4446712160520200817"
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

EXPECTED_PRODUCTS: tuple[dict[str, Any], ...] = (
    {
        "catalog_id": 34629,
        "map_id": 10015623,
        "program": "BAER",
        "incident_name": "GREEN RIDGE 0684 CS",
        "event_id": EVENT_ID,
        "ignition_date": "2020-08-17",
        "assessment_type": "Emergency",
        "boundary_acres": 4362,
        "post_id": "804502920200901",
        "postfire_date": "2020-09-01",
        "model": None,
        "dnbr_offset": -23,
        "dnbr_stddev": 27,
        "nodata_threshold": None,
        "increased_greenness_threshold": None,
        "low_threshold": 73,
        "moderate_threshold": 188,
        "high_threshold": 114,
        "provider_comment": None,
        "nonstandard": False,
    },
    {
        "catalog_id": 14230,
        "map_id": 10021333,
        "program": "MTBS",
        "incident_name": "GREEN RIDGE 0684 CS",
        "event_id": EVENT_ID,
        "ignition_date": "2020-08-17",
        "assessment_type": "Extended",
        "boundary_acres": 4362,
        "post_id": "804502920210718",
        "postfire_date": "2021-07-18",
        "model": None,
        "dnbr_offset": -10,
        "dnbr_stddev": 21,
        "nodata_threshold": -970,
        "increased_greenness_threshold": -150,
        "low_threshold": 50,
        "moderate_threshold": 500,
        "high_threshold": 259,
        "provider_comment": None,
        "nonstandard": False,
    },
    {
        "catalog_id": 25564,
        "map_id": 10016049,
        "program": "RAVG",
        "incident_name": "GREEN RIDGE 0684 CS",
        "event_id": EVENT_ID,
        "ignition_date": "2020-08-17",
        "assessment_type": "Initial",
        "boundary_acres": 4334,
        "post_id": "B10TFQ20200929_30m",
        "postfire_date": "2020-09-29",
        "model": "NATL",
        "dnbr_offset": -12,
        "dnbr_stddev": 26,
        "nodata_threshold": None,
        "increased_greenness_threshold": None,
        "low_threshold": None,
        "moderate_threshold": None,
        "high_threshold": None,
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


class GreenRidgeReferenceRequestError(RuntimeError):
    """An exact Green Ridge reference request failed closed."""


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
        "mapping_ids": [item["map_id"] for item in EXPECTED_PRODUCTS],
        "mapping_products": list(MAPPING_PRODUCTS),
        "projection": "UTM",
        "mosaics": [],
    }


def _date(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)[:10]


def normalize_metadata(raw: bytes) -> list[dict[str, Any]]:
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise GreenRidgeReferenceRequestError("metadata response is not JSON") from error
    features = payload.get("features")
    if not isinstance(features, list) or len(features) != len(EXPECTED_PRODUCTS):
        raise GreenRidgeReferenceRequestError("metadata response must contain exactly three rows")
    normalized: list[dict[str, Any]] = []
    for feature in features:
        if not isinstance(feature, dict) or feature.get("geometry") is not None:
            raise GreenRidgeReferenceRequestError("metadata response must remain property-only")
        properties = feature.get("properties")
        if not isinstance(properties, dict):
            raise GreenRidgeReferenceRequestError("metadata properties are invalid")
        normalized.append(
            {
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
        )
    normalized.sort(key=lambda item: int(item["map_id"]))
    expected = sorted((dict(item) for item in EXPECTED_PRODUCTS), key=lambda item: item["map_id"])
    if normalized != expected:
        raise GreenRidgeReferenceRequestError("Green Ridge metadata identity or cautions drifted")
    return normalized


def _read_bounded(response: Any, maximum: int, label: str) -> bytes:
    status = int(getattr(response, "status", 200))
    if status != 200:
        raise GreenRidgeReferenceRequestError(f"{label} endpoint returned HTTP {status}")
    data = response.read(maximum + 1)
    if len(data) > maximum:
        raise GreenRidgeReferenceRequestError(f"{label} response exceeds bounded size")
    return data


def fetch_metadata(*, timeout_seconds: int = 90) -> bytes:
    request = Request(metadata_url(), headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            raw = _read_bounded(response, MAX_METADATA_BYTES, "metadata")
    except OSError as error:
        raise GreenRidgeReferenceRequestError("official metadata endpoint is unavailable") from error
    normalize_metadata(raw)
    return raw


def submit_request(recipient: str, *, timeout_seconds: int = 90) -> bytes:
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", recipient):
        raise GreenRidgeReferenceRequestError("recipient is missing or invalid")
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
        raise GreenRidgeReferenceRequestError(
            "queue outcome is unknown; do not retry automatically"
        ) from error
    try:
        accepted = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise GreenRidgeReferenceRequestError("queue response is not JSON") from error
    if accepted != {"success": True}:
        raise GreenRidgeReferenceRequestError("official queue did not accept the exact request")
    return raw


def acquire_request_receipt(
    output_directory: Path,
    *,
    recipient: str,
    requested_at_utc: str,
    run_id: str,
) -> dict[str, Any]:
    if output_directory.exists():
        raise GreenRidgeReferenceRequestError("output directory already exists; no overwrite allowed")
    output_directory.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_directory.with_name(f".{output_directory.name}.tmp-{uuid4().hex}")
    try:
        temporary.mkdir()
        metadata = fetch_metadata()
        products = normalize_metadata(metadata)
        queue = submit_request(recipient)
        payload = request_payload()
        receipt = {
            "contract_version": CONTRACT_VERSION,
            "requested_at_utc": requested_at_utc,
            "run_id": run_id,
            "event_id": EVENT_ID,
            "request": {
                "accepted": True,
                "projection": payload["projection"],
                "mapping_ids": payload["mapping_ids"],
                "mapping_products": payload["mapping_products"],
                "canonical_payload_sha256": _sha256(
                    json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
                ),
                "recipient": "WITHHELD_PRIVATE",
            },
            "metadata": {
                "url": metadata_url(),
                "bytes": len(metadata),
                "sha256": _sha256(metadata),
                "products": products,
            },
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
            "claim_boundaries": {
                "request_acceptance_is_delivery": False,
                "reference_pixels_opened": False,
                "candidate_or_label_created": False,
                "dataset_or_model_created": False,
            },
        }
        (temporary / "metadata-response.json").write_bytes(metadata)
        (temporary / "queue-response.json").write_bytes(queue)
        (temporary / "request-receipt.json").write_text(
            json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        temporary.rename(output_directory)
        return receipt
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise

