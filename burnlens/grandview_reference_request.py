"""Fail-closed request contract for exact Grandview official reference bundles."""

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

from .green_ridge_reference_request import (
    MAPPING_PRODUCTS,
    MAX_METADATA_BYTES,
    MAX_QUEUE_BYTES,
    PROPERTY_NAMES,
    QUEUE_ENDPOINT,
    WFS_ENDPOINT,
)
from .provider_acquisition import USER_AGENT


CONTRACT_VERSION = "grandview-reference-request-v0.1.0"
EVENT_ID = "OR4446612140020210711"

EXPECTED_PRODUCTS: tuple[dict[str, Any], ...] = (
    {
        "catalog_id": 34407,
        "map_id": 10019092,
        "program": "BAER",
        "incident_name": "GRANDVIEW 0558 OD",
        "event_id": EVENT_ID,
        "ignition_date": "2021-07-11",
        "assessment_type": "Emergency",
        "boundary_acres": 6557,
        "post_id": "A10TFQ20210718_20m",
        "postfire_date": "2021-07-18",
        "model": None,
        "dnbr_offset": -24,
        "dnbr_stddev": 14,
        "nodata_threshold": 0,
        "increased_greenness_threshold": 0,
        "low_threshold": 61,
        "moderate_threshold": 999,
        "high_threshold": 107,
        "provider_comment": None,
        "nonstandard": False,
    },
    {
        "catalog_id": 22781,
        "map_id": 10019464,
        "program": "RAVG",
        "incident_name": "GRANDVIEW 0558 OD",
        "event_id": EVENT_ID,
        "ignition_date": "2021-07-11",
        "assessment_type": "Initial",
        "boundary_acres": 5989,
        "post_id": "B10TFQ20210815_30m",
        "postfire_date": "2021-08-15",
        "model": "NATL",
        "dnbr_offset": 1,
        "dnbr_stddev": 22,
        "nodata_threshold": None,
        "increased_greenness_threshold": None,
        "low_threshold": None,
        "moderate_threshold": None,
        "high_threshold": None,
        "provider_comment": (
            "Much of this burned area has very sparse to no pre-fire tree cover. "
            "RAVG models, which are calibrated for forest cover, are not directly applicable "
            "to other cover types. In areas with very sparse tree cover, the modeled values "
            "are less reliable since the observed reflectance is strongly dominated by the "
            "non-tree component."
        ),
        "nonstandard": False,
    },
    {
        "catalog_id": 14017,
        "map_id": 10023989,
        "program": "MTBS",
        "incident_name": "GRANDVIEW 0558 OD",
        "event_id": EVENT_ID,
        "ignition_date": "2021-07-11",
        "assessment_type": "Initial",
        "boundary_acres": 6187,
        "post_id": "804502920210718",
        "postfire_date": "2021-07-18",
        "model": None,
        "dnbr_offset": -17,
        "dnbr_stddev": 10,
        "nodata_threshold": -970,
        "increased_greenness_threshold": -150,
        "low_threshold": 15,
        "moderate_threshold": 9999,
        "high_threshold": 420,
        "provider_comment": None,
        "nonstandard": False,
    },
)


class GrandviewReferenceRequestError(RuntimeError):
    """An exact Grandview reference request failed closed."""


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
        raise GrandviewReferenceRequestError("metadata response is not JSON") from error
    features = payload.get("features")
    if not isinstance(features, list) or len(features) != len(EXPECTED_PRODUCTS):
        raise GrandviewReferenceRequestError("metadata response must contain exactly three rows")
    normalized: list[dict[str, Any]] = []
    for feature in features:
        if not isinstance(feature, dict) or feature.get("geometry") is not None:
            raise GrandviewReferenceRequestError("metadata response must remain property-only")
        properties = feature.get("properties")
        if not isinstance(properties, dict):
            raise GrandviewReferenceRequestError("metadata properties are invalid")
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
        raise GrandviewReferenceRequestError("Grandview metadata identity or cautions drifted")
    return normalized


def _read_bounded(response: Any, maximum: int, label: str) -> bytes:
    status = int(getattr(response, "status", 200))
    if status != 200:
        raise GrandviewReferenceRequestError(f"{label} endpoint returned HTTP {status}")
    data = response.read(maximum + 1)
    if len(data) > maximum:
        raise GrandviewReferenceRequestError(f"{label} response exceeds bounded size")
    return data


def fetch_metadata(*, timeout_seconds: int = 90) -> bytes:
    request = Request(metadata_url(), headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            raw = _read_bounded(response, MAX_METADATA_BYTES, "metadata")
    except OSError as error:
        raise GrandviewReferenceRequestError("official metadata endpoint is unavailable") from error
    normalize_metadata(raw)
    return raw


def submit_request(recipient: str, *, timeout_seconds: int = 90) -> bytes:
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", recipient):
        raise GrandviewReferenceRequestError("recipient is missing or invalid")
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
        raise GrandviewReferenceRequestError(
            "queue outcome is unknown; do not retry automatically"
        ) from error
    try:
        accepted = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise GrandviewReferenceRequestError("queue response is not JSON") from error
    if accepted != {"success": True}:
        raise GrandviewReferenceRequestError("official queue did not accept the exact request")
    return raw


def acquire_request_receipt(
    output_directory: Path,
    *,
    recipient: str,
    requested_at_utc: str,
    run_id: str,
) -> dict[str, Any]:
    if output_directory.exists():
        raise GrandviewReferenceRequestError("output directory already exists; no overwrite allowed")
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
