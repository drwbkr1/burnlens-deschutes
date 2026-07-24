"""Fresh, metadata-only source gate for the P2O4-T39 replacement event.

The gate re-queries official MTBS, Burn Severity Portal, CDSE STAC, and CDSE
OData metadata. It authorizes only the exact Ward Creek optical-pair acquisition
when every frozen identity and source-use criterion passes. It never requests
or downloads provider archive bytes.
"""

from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
import subprocess
import time
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


SOFTWARE_VERSION = "0.50.0"
UNIT_ID = "P2O4-T39-U01"
SOURCE_ID = "REPLACEMENT-EVENT-SOURCE-2026-001"
ASSESSMENT_ID = "REPLACEMENT-EVENT-SOURCE-GATE-2026-001"
REPORT_ID = "REPLACEMENT-EVENT-SOURCE-GATE-REPORT-2026-001"
EVENT_ID = "OR4494912090120190812"
EVENT_NAME = "WARD CREEK 0769 RN"
MAP_ID = 10016337
CATALOG_ID = 34073
IGNITION_DATE = "2019-08-12"
EXPECTED_BOUNDARY_BOUNDS = (-120.902079, 44.915764, -120.856115, 44.955295)
EXPECTED_BOUNDARY_AREA_DEGREES = 0.0009553536724757831
EXPECTED_PROVIDER_BOUNDARY_AREA_DEGREES = 0.0009553534525000523

WFS_ENDPOINT = "https://edcintl.cr.usgs.gov/geoserver/wfs"
MTBS_ENDPOINT = "https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_MTBS_01/MapServer"
STAC_ENDPOINT = "https://stac.dataspace.copernicus.eu/v1/search"
ODATA_ENDPOINT = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

TERMS_URLS = {
    "mtbs_program": "https://www.mtbs.gov/",
    "mtbs_products": "https://www.mtbs.gov/project-overview",
    "mtbs_methods": "https://www.mtbs.gov/mapping-methods",
    "usgs_data_licensing": "https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits",
    "sentinel_legal_notice": "https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice",
    "cdse_terms": "https://dataspace.copernicus.eu/terms-and-conditions",
}

SELECTED_PRODUCTS = {
    "pre": {
        "stac_id": "S2A_MSIL2A_20190801T185921_N0500_R013_T10TFQ_20230707T221135",
        "provider_id": "f6b6697d-5b7d-4049-8caf-8b0c7fdad4b7",
        "native_id": "S2A_MSIL2A_20190801T185921_N0500_R013_T10TFQ_20230707T221135.SAFE",
        "acquisition_utc": "2019-08-01T18:59:21.024000Z",
        "size_bytes": 1_198_399_787,
        "md5": "7de4c0076a9ed4a3024ef46474b2aaac",
        "blake3": "737a71d70c36ae8d65d26df28e87730d08ed0bade1d2a327cce8a6b812a32c2a",
        "odata_cloud_cover_percent": 0.006231,
        "stac_cloud_cover_percent": 0.01,
    },
    "post": {
        "stac_id": "S2A_MSIL2A_20190831T185921_N0500_R013_T10TFQ_20230528T200015",
        "provider_id": "51ddb0b7-8456-40a2-8301-e1651c951116",
        "native_id": "S2A_MSIL2A_20190831T185921_N0500_R013_T10TFQ_20230528T200015.SAFE",
        "acquisition_utc": "2019-08-31T18:59:21.024000Z",
        "size_bytes": 1_198_420_414,
        "md5": "28f18e0328dd4cb8ab45446a1a238fb0",
        "blake3": "eaf090416dd240478d85389ba018f1d193e09c270ff40a6f346ee9c4f8110eaf",
        "odata_cloud_cover_percent": 0.001556,
        "stac_cloud_cover_percent": 0.0,
    },
}

REQUIRED_CRITERIA = (
    "identity",
    "authority",
    "access",
    "rights",
    "provenance",
    "integrity",
    "fitness",
    "privacy-security",
)

WARNING = (
    "Experimental BurnLens portfolio evidence. Not official wildfire information. "
    "Not emergency guidance. Not field validation, endorsement, or operational support. "
    "Official sources govern."
)


class ReplacementEventSourceGateError(RuntimeError):
    """Fail-closed metadata or source-gate error."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def _safe_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def _receipt(url: str, payload: bytes, content_type: str) -> dict[str, Any]:
    return {
        "url": _safe_url(url),
        "response_bytes": len(payload),
        "response_sha256": sha256(payload).hexdigest(),
        "content_type": content_type.split(";", 1)[0].strip().lower(),
    }


def _request_bytes(
    url: str,
    *,
    timeout_seconds: int = 90,
    max_attempts: int = 3,
) -> tuple[bytes, dict[str, Any]]:
    request = Request(
        url,
        headers={
            "Accept": "application/json, application/geo+json, text/html;q=0.8, */*;q=0.2",
            "User-Agent": f"BurnLens-Deschutes/{SOFTWARE_VERSION} metadata-only",
        },
    )
    last_error: OSError | None = None
    payload = b""
    content_type = ""
    status = 0
    for attempt in range(1, max_attempts + 1):
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                payload = response.read(25_000_001)
                content_type = response.headers.get("Content-Type", "")
                status = response.status
            break
        except OSError as error:
            last_error = error
            if isinstance(error, HTTPError) and 400 <= error.code < 500:
                raise ReplacementEventSourceGateError(
                    f"SOURCE_HTTP_STATUS:{error.code}:{_safe_url(url)}"
                ) from error
            if attempt < max_attempts:
                time.sleep(attempt)
    else:
        raise ReplacementEventSourceGateError(
            f"SOURCE_REQUEST_FAILED_AFTER_{max_attempts}_ATTEMPTS:{_safe_url(url)}"
        ) from last_error
    if status != 200:
        raise ReplacementEventSourceGateError(f"SOURCE_HTTP_STATUS:{status}:{_safe_url(url)}")
    if len(payload) > 25_000_000:
        raise ReplacementEventSourceGateError(f"SOURCE_RESPONSE_TOO_LARGE:{_safe_url(url)}")
    return payload, _receipt(url, payload, content_type)


def _request_json(
    url: str, params: dict[str, Any] | None = None
) -> tuple[dict[str, Any], dict[str, Any]]:
    query_url = url if params is None else f"{url}?{urlencode(params)}"
    payload, receipt = _request_bytes(query_url)
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ReplacementEventSourceGateError(
            f"SOURCE_JSON_INVALID:{_safe_url(query_url)}"
        ) from error
    if not isinstance(value, dict) or value.get("error"):
        raise ReplacementEventSourceGateError(f"SOURCE_JSON_OBJECT_INVALID:{_safe_url(query_url)}")
    return value, receipt


def _iso_utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ReplacementEventSourceGateError("ACCESSED_AT_UTC_INVALID")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ReplacementEventSourceGateError("ACCESSED_AT_UTC_INVALID") from error
    if parsed.tzinfo is None:
        raise ReplacementEventSourceGateError("ACCESSED_AT_UTC_INVALID")
    return parsed


def _validate_commit(value: str) -> None:
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ReplacementEventSourceGateError("GIT_SOURCE_COMMIT_INVALID")


def validate_repository_trace(repository_root: Path, git_source_commit: str) -> None:
    """Require the live repository to match the declared committed source."""

    _validate_commit(git_source_commit)
    try:
        top_level = subprocess.run(
            ["git", "-C", str(repository_root), "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        head = subprocess.run(
            ["git", "-C", str(repository_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status = subprocess.run(
            [
                "git",
                "-C",
                str(repository_root),
                "status",
                "--short",
                "--",
                "burnlens",
                "pyproject.toml",
                "uv.lock",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as error:
        raise ReplacementEventSourceGateError("GIT_TRACE_UNAVAILABLE") from error
    if Path(top_level).resolve() != repository_root.resolve():
        raise ReplacementEventSourceGateError("GIT_REPOSITORY_ROOT_MISMATCH")
    if head != git_source_commit:
        raise ReplacementEventSourceGateError("GIT_SOURCE_COMMIT_MISMATCH")
    if status:
        raise ReplacementEventSourceGateError("GIT_RELEVANT_WORKTREE_DIRTY")


def _criterion(
    criterion_id: str,
    *,
    evidence: list[str],
    note: str,
    requires_live: bool,
    locator: str,
    observed_at: str,
) -> dict[str, Any]:
    return {
        "id": criterion_id,
        "required": True,
        "requires_live": requires_live,
        "status": "pass",
        "evidence": [
            {
                "type": "live" if requires_live else "static",
                "locator": locator,
                "note": item,
                **({"observed_at": observed_at} if requires_live else {}),
            }
            for item in evidence
        ],
        "note": note,
    }


def _source_gate(
    *,
    source_id: str,
    name: str,
    locator: str,
    evidence: dict[str, list[str]],
    notes: dict[str, str],
    observed_at: str,
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "name": name,
        "locator": locator,
        "criteria": [
            _criterion(
                criterion_id,
                evidence=evidence[criterion_id],
                note=notes[criterion_id],
                requires_live=criterion_id in {"authority", "access", "rights"},
                locator=locator,
                observed_at=observed_at,
            )
            for criterion_id in REQUIRED_CRITERIA
        ],
    }


def _attribute_map(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        str(item.get("Name")): item.get("Value")
        for item in payload.get("Attributes") or []
        if isinstance(item, dict) and item.get("Name") is not None
    }


def _checksum_map(payload: dict[str, Any]) -> dict[str, str]:
    return {
        str(item.get("Algorithm", "")).upper(): str(item.get("Value", "")).lower()
        for item in payload.get("Checksum") or []
        if isinstance(item, dict)
    }


def _normalize_odata(payload: dict[str, Any], *, role: str) -> dict[str, Any]:
    attributes = _attribute_map(payload)
    checksums = _checksum_map(payload)
    return {
        "role": role,
        "provider_id": payload.get("Id"),
        "native_id": payload.get("Name"),
        "size_bytes": payload.get("ContentLength"),
        "online": payload.get("Online"),
        "acquisition_utc": (payload.get("ContentDate") or {}).get("Start"),
        "publication_utc": payload.get("PublicationDate"),
        "s3_path": payload.get("S3Path"),
        "md5": checksums.get("MD5"),
        "blake3": checksums.get("BLAKE3"),
        "platform": attributes.get("platformSerialIdentifier"),
        "tile_id": attributes.get("tileId"),
        "relative_orbit_number": attributes.get("relativeOrbitNumber"),
        "processor_version": attributes.get("processorVersion"),
        "product_type": attributes.get("productType"),
        "cloud_cover_percent": attributes.get("cloudCover"),
    }


def _validate_odata(value: dict[str, Any], *, role: str) -> None:
    expected = SELECTED_PRODUCTS[role]
    checks = {
        "provider_id": expected["provider_id"],
        "native_id": expected["native_id"],
        "size_bytes": expected["size_bytes"],
        "online": True,
        "acquisition_utc": expected["acquisition_utc"],
        "md5": expected["md5"],
        "blake3": expected["blake3"],
        "platform": "A",
        "tile_id": "10TFQ",
        "relative_orbit_number": 13,
        "processor_version": "05.00",
        "product_type": "S2MSI2A",
        "cloud_cover_percent": expected["odata_cloud_cover_percent"],
    }
    drift = [field for field, expected_value in checks.items() if value.get(field) != expected_value]
    if drift:
        raise ReplacementEventSourceGateError(
            f"ODATA_IDENTITY_DRIFT:{role}:{','.join(sorted(drift))}"
        )


def _normalize_stac(item: dict[str, Any], boundary: Any) -> dict[str, Any]:
    try:
        from shapely.geometry import shape
    except ImportError as error:
        raise ReplacementEventSourceGateError("SHAPELY_GEO_RESEARCH_PROFILE_REQUIRED") from error
    item_geometry = shape(item.get("geometry"))
    if item_geometry.is_empty or not item_geometry.is_valid or not item_geometry.covers(boundary):
        raise ReplacementEventSourceGateError(f"STAC_FULL_BOUNDARY_COVERAGE_FAILED:{item.get('id')}")
    properties = item.get("properties") or {}
    private = properties.get("_private") or {}
    return {
        "stac_id": item.get("id"),
        "provider_id": private.get("product_uuid"),
        "native_id": private.get("product_name"),
        "datetime": properties.get("datetime"),
        "platform": properties.get("platform"),
        "grid_code": properties.get("grid:code"),
        "relative_orbit_number": properties.get("sat:relative_orbit"),
        "processor_version": properties.get("processing:version"),
        "product_type": properties.get("product:type"),
        "cloud_cover_percent": properties.get("eo:cloud_cover"),
        "geometry_type": item_geometry.geom_type,
        "full_boundary_coverage": True,
    }


def _validate_stac(value: dict[str, Any], *, role: str) -> None:
    expected = SELECTED_PRODUCTS[role]
    checks = {
        "stac_id": expected["stac_id"],
        "provider_id": expected["provider_id"],
        "native_id": expected["native_id"],
        "datetime": expected["acquisition_utc"],
        "platform": "sentinel-2a",
        "grid_code": "MGRS-10TFQ",
        "relative_orbit_number": 13,
        "processor_version": "05.00",
        "product_type": "S2MSI2A",
        "cloud_cover_percent": expected["stac_cloud_cover_percent"],
        "full_boundary_coverage": True,
    }
    drift = [field for field, expected_value in checks.items() if value.get(field) != expected_value]
    if drift:
        raise ReplacementEventSourceGateError(
            f"STAC_IDENTITY_DRIFT:{role}:{','.join(sorted(drift))}"
        )


def capture_source_gate(
    *,
    accessed_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    """Run the live, credential-free U01 metadata gate."""

    _iso_utc(accessed_at_utc)
    _validate_commit(git_source_commit)
    if not run_id.strip():
        raise ReplacementEventSourceGateError("RUN_ID_REQUIRED")

    wfs, wfs_receipt = _request_json(
        WFS_ENDPOINT,
        {
            "service": "WFS",
            "version": "2.0.0",
            "request": "GetFeature",
            "typeNames": "mtbs:fire_polygons",
            "outputFormat": "application/json",
            "propertyName": "id,map_id,map_prog,incid_name,event_id,ig_date,burnbndac,nonstandard",
            "cql_filter": f"event_id='{EVENT_ID}' AND map_prog='MTBS'",
        },
    )
    wfs_features = wfs.get("features")
    if not isinstance(wfs_features, list) or len(wfs_features) != 1:
        raise ReplacementEventSourceGateError("PORTAL_EVENT_COUNT_DRIFT")
    portal = wfs_features[0].get("properties") or {}
    portal_expected = {
        "id": CATALOG_ID,
        "map_id": MAP_ID,
        "map_prog": "MTBS",
        "incid_name": EVENT_NAME,
        "event_id": EVENT_ID,
        "ig_date": f"{IGNITION_DATE}Z",
        "burnbndac": 2070,
        "nonstandard": False,
    }
    if any(portal.get(key) != value for key, value in portal_expected.items()):
        raise ReplacementEventSourceGateError("PORTAL_EVENT_IDENTITY_DRIFT")

    occurrence, occurrence_receipt = _request_json(
        f"{MTBS_ENDPOINT}/62/query",
        {
            "where": f"fire_id='{EVENT_ID}'",
            "outFields": "*",
            "returnGeometry": "false",
            "f": "json",
        },
    )
    occurrence_features = occurrence.get("features")
    if not isinstance(occurrence_features, list) or len(occurrence_features) != 1:
        raise ReplacementEventSourceGateError("MTBS_OCCURRENCE_COUNT_DRIFT")
    occurrence_properties = occurrence_features[0].get("attributes") or {}

    boundary_payload, boundary_receipt = _request_json(
        f"{MTBS_ENDPOINT}/63/query",
        {
            "where": f"fire_id='{EVENT_ID}'",
            "outFields": "*",
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "geojson",
        },
    )
    boundary_features = boundary_payload.get("features")
    if not isinstance(boundary_features, list) or len(boundary_features) != 1:
        raise ReplacementEventSourceGateError("MTBS_BOUNDARY_COUNT_DRIFT")
    boundary_feature = boundary_features[0]
    boundary_properties = boundary_feature.get("properties") or {}
    for properties in (occurrence_properties, boundary_properties):
        expected = {
            "fire_id": EVENT_ID,
            "fire_name": EVENT_NAME,
            "map_id": MAP_ID,
            "map_prog": "MTBS",
            "acres": 2070,
            "fire_type": "Wildfire",
            "asmnt_type": "Initial",
            "pre_id": "804502920190729",
            "post_id": "804502920190830",
            "comments": None,
        }
        if any(properties.get(key) != value for key, value in expected.items()):
            raise ReplacementEventSourceGateError("MTBS_EVENT_IDENTITY_DRIFT")
    if (
        boundary_properties.get("st_area(shape)")
        != EXPECTED_PROVIDER_BOUNDARY_AREA_DEGREES
    ):
        raise ReplacementEventSourceGateError("MTBS_PROVIDER_BOUNDARY_AREA_DRIFT")

    try:
        from shapely.geometry import shape
    except ImportError as error:
        raise ReplacementEventSourceGateError("SHAPELY_GEO_RESEARCH_PROFILE_REQUIRED") from error
    boundary = shape(boundary_feature.get("geometry"))
    if boundary.is_empty or not boundary.is_valid or boundary.geom_type != "Polygon":
        raise ReplacementEventSourceGateError("MTBS_BOUNDARY_GEOMETRY_INVALID")
    bounds = tuple(round(value, 6) for value in boundary.bounds)
    if bounds != EXPECTED_BOUNDARY_BOUNDS:
        raise ReplacementEventSourceGateError("MTBS_BOUNDARY_BOUNDS_DRIFT")
    if abs(float(boundary.area) - EXPECTED_BOUNDARY_AREA_DEGREES) > 1e-15:
        raise ReplacementEventSourceGateError("MTBS_BOUNDARY_AREA_DRIFT")
    exterior_vertices = len(boundary.exterior.coords)
    if exterior_vertices != 3340:
        raise ReplacementEventSourceGateError("MTBS_BOUNDARY_VERTEX_COUNT_DRIFT")

    search, stac_receipt = _request_json(
        STAC_ENDPOINT,
        {
            "collections": "sentinel-2-l2a",
            "bbox": ",".join(f"{value:.8f}" for value in boundary.bounds),
            "datetime": "2019-06-28T00:00:00Z/2019-10-27T23:59:59Z",
            "limit": 100,
            "sortby": "+datetime",
        },
    )
    features = search.get("features")
    if not isinstance(features, list):
        raise ReplacementEventSourceGateError("STAC_FEATURES_INVALID")
    if any(link.get("rel") == "next" for link in search.get("links") or []):
        raise ReplacementEventSourceGateError("STAC_PAGINATION_UNRESOLVED")
    by_id = {str(item.get("id")): item for item in features if isinstance(item, dict)}
    selected_stac: dict[str, dict[str, Any]] = {}
    for role, expected in SELECTED_PRODUCTS.items():
        item = by_id.get(str(expected["stac_id"]))
        if item is None:
            raise ReplacementEventSourceGateError(f"STAC_SELECTED_ITEM_MISSING:{role}")
        selected_stac[role] = _normalize_stac(item, boundary)
        _validate_stac(selected_stac[role], role=role)

    selected_odata: dict[str, dict[str, Any]] = {}
    odata_receipts: dict[str, dict[str, Any]] = {}
    for role, expected in SELECTED_PRODUCTS.items():
        payload, receipt = _request_json(
            f"{ODATA_ENDPOINT}({expected['provider_id']})",
            {
                "$select": (
                    "Id,Name,ContentLength,Online,Checksum,ContentDate,"
                    "PublicationDate,S3Path,Attributes"
                ),
                "$expand": "Attributes",
            },
        )
        selected_odata[role] = _normalize_odata(payload, role=role)
        _validate_odata(selected_odata[role], role=role)
        odata_receipts[role] = receipt

    terms_receipts: dict[str, dict[str, Any]] = {}
    for name, url in TERMS_URLS.items():
        payload, receipt = _request_bytes(url)
        if not payload.strip():
            raise ReplacementEventSourceGateError(f"TERMS_RESPONSE_EMPTY:{name}")
        terms_receipts[name] = receipt

    mtbs_source = _source_gate(
        source_id="mtbs-ward-creek-current",
        name="Current MTBS Ward Creek event metadata and boundary",
        locator=MTBS_ENDPOINT,
        evidence={
            "identity": [
                f"event {EVENT_ID}",
                f"map {MAP_ID}",
                f"Portal catalog {CATALOG_ID}",
            ],
            "authority": [
                "Current USDA Forest Service Enterprise Data Warehouse MTBS service",
                "Current USGS Burn Severity Portal catalog",
            ],
            "access": [
                f"credential-free WFS receipt {wfs_receipt['response_sha256']}",
                f"credential-free MTBS boundary receipt {boundary_receipt['response_sha256']}",
            ],
            "rights": [
                f"live USGS licensing receipt {terms_receipts['usgs_data_licensing']['response_sha256']}",
                "metadata review and internal evidence assessment only",
            ],
            "provenance": [
                "Portal, occurrence, and boundary identities agree",
                "pre 804502920190729; post 804502920190830",
            ],
            "integrity": [
                f"valid Polygon; {exterior_vertices} exterior vertices",
                f"bounds {list(bounds)}",
            ],
            "fitness": [
                "current MTBS regime needed to replace sole NIFC-context event",
                "Initial assessment; analyst-interpreted remote-sensing reference only",
            ],
            "privacy-security": [
                "public metadata only; zero credential, recipient, retrieval, or provider archive bytes"
            ],
        },
        notes={
            "identity": "Three official routes agree on the exact event and map identity.",
            "authority": "MTBS is the applicable official program source, not field truth.",
            "access": "Public metadata routes were live during this run.",
            "rights": (
                "Metadata review is permitted. Exact bundle processing or redistribution remains "
                "conditional on inspection of delivered archive notices because MTBS is interagency."
            ),
            "provenance": "Event, analyst-selected Landsat dates, map ID, and geometry are traceable.",
            "integrity": "The full valid boundary is retained for polygon coverage tests.",
            "fitness": "The source is fit for candidate-event preflight, not automatic label truth.",
            "privacy-security": "No private delivery route or credential was used or recorded.",
        },
        observed_at=accessed_at_utc,
    )
    sentinel_source = _source_gate(
        source_id="cdse-sentinel-2-ward-creek-pair",
        name="Exact CDSE Sentinel-2 L2A Ward Creek optical pair",
        locator=STAC_ENDPOINT,
        evidence={
            "identity": [
                f"pre {SELECTED_PRODUCTS['pre']['provider_id']}",
                f"post {SELECTED_PRODUCTS['post']['provider_id']}",
            ],
            "authority": [
                "Current CDSE Sentinel-2 L2A STAC collection",
                "Current CDSE OData product metadata",
            ],
            "access": [
                f"credential-free STAC receipt {stac_receipt['response_sha256']}",
                "both exact OData products online",
            ],
            "rights": [
                f"live Sentinel legal notice receipt {terms_receipts['sentinel_legal_notice']['response_sha256']}",
                f"live CDSE terms receipt {terms_receipts['cdse_terms']['response_sha256']}",
            ],
            "provenance": [
                "STAC product UUID and SAFE identity agree with OData",
                "same Sentinel-2A platform, tile 10TFQ, orbit 13, baseline 05.00",
            ],
            "integrity": [
                f"combined OData archive bytes {sum(int(item['size_bytes']) for item in selected_odata.values())}",
                "exact MD5 and BLAKE3 available for both archives",
            ],
            "fitness": [
                "Shapely full-polygon covers passes for both selected items",
                "2019-08-01 pre and 2019-08-31 post bracket 2019-08-12 ignition",
            ],
            "privacy-security": [
                "public metadata only; exact download requires the existing protected local CDSE account"
            ],
        },
        notes={
            "identity": "Frozen STAC, OData UUID, and SAFE names agree.",
            "authority": "STAC governs discovery geometry; OData governs archive size and checksums.",
            "access": "Both products are currently online; no archive route was opened.",
            "rights": "Sentinel data permit lawful reuse with required source notice and no warranty.",
            "provenance": "The pair preserves one platform, tile, orbit, processor baseline, and product type.",
            "integrity": "Future acquisition must match exact OData size, MD5, and BLAKE3.",
            "fitness": "The pair is temporal pre/post evidence; pixel fitness remains a later gate.",
            "privacy-security": "No token, credential, private URL, or provider byte is in this artifact.",
        },
        observed_at=accessed_at_utc,
    )

    gate = {
        "contract_version": "source-gate/v1",
        "assessment_id": ASSESSMENT_ID,
        "assessed_at": accessed_at_utc,
        "intended_use": {
            "summary": (
                "Select exactly one Ward Creek optical pair for controlled U02 acquisition before "
                "any pixel, label, dataset, split, baseline, or model decision."
            ),
            "planned_actions": [
                "metadata review",
                "record assessment evidence",
                "acquire the exact two frozen Ward Creek Sentinel archives into ignored repository-local custody",
            ],
        },
        "sources": [mtbs_source, sentinel_source],
        "decision": {
            "status": "ready",
            "blocking_reasons": [],
            "live_verification_pending": [],
            "approved_actions": [
                "metadata review",
                "record assessment evidence",
                "acquire the exact two frozen Ward Creek Sentinel archives into ignored repository-local custody",
            ],
        },
        "write_boundary": {
            "permitted_without_further_authorization": [
                "read supplied metadata",
                "record assessment evidence",
                "authenticate with the existing protected local CDSE account",
                "download only the two exact frozen Sentinel archives",
                "preserve exact bytes in ignored repository-local custody without overwrite",
            ],
            "requires_explicit_authorization": [
                "accept changed terms",
                "purchase",
                "acquire a different event or product",
                "publish or redistribute provider archives",
                "use any source pixel for a label",
            ],
        },
        "provider_bytes_authorized": True,
        "authorized_provider_byte_scope": {
            "provider": "Copernicus Data Space Ecosystem",
            "roles": ["pre", "post"],
            "combined_expected_bytes": sum(
                int(item["size_bytes"]) for item in SELECTED_PRODUCTS.values()
            ),
            "products": [
                {
                    "role": role,
                    "provider_id": item["provider_id"],
                    "native_id": item["native_id"],
                    "size_bytes": item["size_bytes"],
                    "md5": item["md5"],
                    "blake3": item["blake3"],
                }
                for role, item in SELECTED_PRODUCTS.items()
            ],
        },
    }

    return {
        "source_id": SOURCE_ID,
        "schema_version": "0.1.0",
        "unit_id": UNIT_ID,
        "run_id": run_id,
        "accessed_at_utc": accessed_at_utc,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "event": {
            "event_id": EVENT_ID,
            "event_name": EVENT_NAME,
            "ignition_date": IGNITION_DATE,
            "catalog_id": CATALOG_ID,
            "map_id": MAP_ID,
            "acres": 2070,
            "assessment_type": "Initial",
            "fire_type": "Wildfire",
            "mtbs_pre_id": "804502920190729",
            "mtbs_post_id": "804502920190830",
        },
        "boundary": {
            "geometry_type": boundary.geom_type,
            "valid": boundary.is_valid,
            "empty": boundary.is_empty,
            "exterior_vertex_count": exterior_vertices,
            "bounds_wgs84": list(bounds),
            "area_square_degrees": float(boundary.area),
            "coverage_predicate": "shapely.geometry.shape(item.geometry).covers(boundary)",
        },
        "catalog_search": {
            "window_utc": "2019-06-28T00:00:00Z/2019-10-27T23:59:59Z",
            "returned_item_count": len(features),
            "selected_item_count": len(selected_stac),
            "selected": selected_stac,
        },
        "odata": selected_odata,
        "receipts": {
            "portal_wfs": wfs_receipt,
            "mtbs_occurrence": occurrence_receipt,
            "mtbs_boundary": boundary_receipt,
            "cdse_stac": stac_receipt,
            "cdse_odata": odata_receipts,
            "terms": terms_receipts,
        },
        "source_gate": gate,
        "limitations": [
            "MTBS is analyst-interpreted remote-sensing evidence, not field truth.",
            "Cloud metadata is scene-level and does not prove pixel usability inside the event.",
            "No archive, raster, label, dataset, split, baseline, or model was created.",
            "Exact MTBS bundle processing and redistribution remain conditional on archive notices.",
            "No official, endorsed, field-validated, operational, or emergency-ready status is implied.",
        ],
        "warning": WARNING,
    }


def validate_source(source: dict[str, Any]) -> None:
    if source.get("source_id") != SOURCE_ID or source.get("unit_id") != UNIT_ID:
        raise ReplacementEventSourceGateError("SOURCE_IDENTITY_INVALID")
    gate = source.get("source_gate")
    if not isinstance(gate, dict) or gate.get("assessment_id") != ASSESSMENT_ID:
        raise ReplacementEventSourceGateError("SOURCE_GATE_MISSING")
    if gate.get("contract_version") != "source-gate/v1":
        raise ReplacementEventSourceGateError("SOURCE_GATE_CONTRACT_INVALID")
    if gate.get("decision", {}).get("status") != "ready":
        raise ReplacementEventSourceGateError("SOURCE_GATE_NOT_READY")
    if gate.get("provider_bytes_authorized") is not True:
        raise ReplacementEventSourceGateError("PROVIDER_SCOPE_NOT_AUTHORIZED")
    for item in gate.get("sources") or []:
        criteria = item.get("criteria") or []
        if tuple(entry.get("id") for entry in criteria) != REQUIRED_CRITERIA:
            raise ReplacementEventSourceGateError("SOURCE_GATE_CRITERIA_DRIFT")
        if any(entry.get("status") != "pass" for entry in criteria):
            raise ReplacementEventSourceGateError("SOURCE_GATE_CRITERION_NOT_PASS")
    if source.get("catalog_search", {}).get("returned_item_count") != 49:
        raise ReplacementEventSourceGateError("STAC_SEARCH_COUNT_DRIFT")
    for role in SELECTED_PRODUCTS:
        _validate_stac(source["catalog_search"]["selected"][role], role=role)
        _validate_odata(source["odata"][role], role=role)


def build_report(source: dict[str, Any]) -> dict[str, Any]:
    validate_source(source)
    products = source["source_gate"]["authorized_provider_byte_scope"]["products"]
    return {
        "report_id": REPORT_ID,
        "schema_version": "0.1.0",
        "source_binding": {
            "source_id": SOURCE_ID,
            "bytes": len(_canonical_bytes(source)),
            "sha256": sha256(_canonical_bytes(source)).hexdigest(),
        },
        "run_id": source["run_id"],
        "git_source_commit": source["git_source_commit"],
        "software_version": source["software_version"],
        "event": source["event"],
        "decision": "PASS_WARD_CREEK_U01_AUTHORIZE_EXACT_OPTICAL_PAIR_ONLY",
        "provider_bytes_acquired": 0,
        "authorized_products": products,
        "boundary": source["boundary"],
        "limitations": source["limitations"],
        "warning": WARNING,
    }


def render_html(report: dict[str, Any]) -> str:
    products = "".join(
        "<tr>"
        f"<td data-label=\"Role\">{escape(item['role'])}</td>"
        f"<td data-label=\"SAFE identity\"><code>{escape(item['native_id'])}</code></td>"
        f"<td data-label=\"Bytes\">{int(item['size_bytes']):,}</td>"
        f"<td data-label=\"Provider UUID\"><code>{escape(item['provider_id'])}</code></td>"
        "</tr>"
        for item in report["authorized_products"]
    )
    limitations = "".join(f"<li>{escape(item)}</li>" for item in report["limitations"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens Ward Creek source gate</title>
<style>
:root{{--ink:#17211d;--muted:#58645e;--paper:#f6f2e8;--card:#fffdf7;--green:#0f6b4f;--line:#d8d2c4;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);
font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}}main{{max-width:1080px;margin:auto;padding:36px 24px 64px}}
.eyebrow{{color:var(--green);font-weight:750;letter-spacing:.08em;text-transform:uppercase}}
h1{{font-size:clamp(2rem,5vw,4.5rem);line-height:1;margin:.15em 0}}.lede{{max-width:760px;color:var(--muted);font-size:1.15rem}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:28px 0}}.card{{background:var(--card);
border:1px solid var(--line);border-radius:16px;padding:20px}}.metric{{font-size:2rem;font-weight:800;color:var(--green)}}
table{{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line)}}th,td{{padding:12px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}}
code{{font-size:.8rem;overflow-wrap:anywhere}}.warning{{border-left:5px solid #9b5b23;padding:14px 18px;background:#fff6e8}}
@media(max-width:760px){{.grid{{grid-template-columns:1fr}}table,thead,tbody,tr,th,td{{display:block}}thead{{display:none}}
tr{{padding:12px;border-bottom:1px solid var(--line)}}td{{border:0;padding:5px 0}}td:before{{content:attr(data-label);font-weight:700;display:block}}}}
</style></head><body><main>
<p class="eyebrow">BurnLens / Phase Two / P2O4-T39-U01</p>
<h1>Ward Creek passes the metadata-only source gate.</h1>
<p class="lede">One exact Sentinel-2 pair may proceed to controlled acquisition. No source pixel, label, dataset, split, baseline, or model is accepted.</p>
<section class="grid">
<div class="card"><div class="metric">1</div><div>fresh candidate event</div></div>
<div class="card"><div class="metric">2</div><div>exact optical archives authorized</div></div>
<div class="card"><div class="metric">0</div><div>provider bytes acquired in U01</div></div>
</section>
<section class="card"><h2>Event binding</h2>
<p><strong>{escape(report['event']['event_name'])}</strong><br>
Event <code>{escape(report['event']['event_id'])}</code>; MTBS map {report['event']['map_id']};
ignition {escape(report['event']['ignition_date'])}; {report['event']['acres']:,} acres.</p>
<p>Valid {escape(report['boundary']['geometry_type'])}; {report['boundary']['exterior_vertex_count']:,} exterior vertices.
Coverage uses the full Shapely polygon.</p></section>
<h2>Exact acquisition scope</h2><table><thead><tr><th>Role</th><th>SAFE identity</th><th>Bytes</th><th>Provider UUID</th></tr></thead>
<tbody>{products}</tbody></table>
<section class="card"><h2>Limits retained</h2><ul>{limitations}</ul></section>
<p class="warning"><strong>Warning.</strong> {escape(report['warning'])}</p>
<p>Run <code>{escape(report['run_id'])}</code><br>Source commit <code>{escape(report['git_source_commit'])}</code></p>
</main></body></html>"""


def write_outputs(
    *,
    source: dict[str, Any],
    output_directory: Path,
) -> dict[str, Path]:
    validate_source(source)
    output_directory.mkdir(parents=True, exist_ok=True)
    paths = {
        "source": output_directory / f"{SOURCE_ID}.json",
        "gate": output_directory / f"{ASSESSMENT_ID}.json",
        "report": output_directory / f"{REPORT_ID}.json",
        "html": output_directory / f"{REPORT_ID}.html",
    }
    existing = [path for path in paths.values() if path.exists()]
    if existing:
        raise ReplacementEventSourceGateError(
            "OUTPUT_ALREADY_EXISTS:" + ",".join(path.name for path in existing)
        )
    report = build_report(source)
    payloads = {
        "source": json.dumps(source, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        "gate": json.dumps(source["source_gate"], indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        "report": json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        "html": render_html(report),
    }
    for name, text in payloads.items():
        paths[name].write_bytes(text.replace("\r\n", "\n").encode("utf-8"))
    return paths
