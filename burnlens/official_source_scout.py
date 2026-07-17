"""Scout official fire-data sources and Deschutes candidate fires.

This module performs bounded metadata-only reconnaissance. It does not
download large products, reinterpret pixels, change the original 56 review
units, promote labels, or create a dataset, split, baseline, or model.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from html import escape
import json
from math import asin, cos, radians, sin, sqrt
from pathlib import Path
import re
from textwrap import wrap
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw, ImageFont

from .cross_event_source import (
    COUNTY_GEOID,
    COUNTY_URL,
    MTBS_BOUNDARY_LAYER,
    MTBS_OCCURRENCE_LAYER,
    MTBS_URL,
    SEARCH_ENVELOPE,
    _arcgis_polygon,
    _date_from_epoch_ms,
    _inside_geometry,
)
from .provider_acquisition import USER_AGENT


SOFTWARE_VERSION = "0.23.0"
SOURCE_ID = "OFFICIAL-SOURCE-SCOUT-SOURCE-2026-001"
SOURCE_SCHEMA_VERSION = "0.1.0"
REPORT_ID = "OFFICIAL-SOURCE-SCOUT-2026-001"
REPORT_SCHEMA_VERSION = "0.1.0"
REPORT_VERSION = "official-source-and-candidate-fire-scout-v0.1.0"
SCOUT_PROTOCOL_VERSION = "official-source-scout-protocol-v0.1.0"
TASK_ISSUE = 425
PARENT_BUNDLE_ISSUE = 416
SOURCE_RECORD_ID = "SOURCE-2026-016"
TERMS_RECORD_ID = "TERMS-2026-011"
SOURCE_PRECEDENCE_REVIEW_ID = "SOURCE_PRECEDENCE-2026-009"

LANDSAT_STAC = "https://landsatlook.usgs.gov/stac-server"
LANDSAT_COLLECTIONS_URL = f"{LANDSAT_STAC}/collections"
LANDSAT_SEARCH_URL = f"{LANDSAT_STAC}/search"
LANDSAT_BA_COLLECTION = "landsat-c2l3-ba"
LANDSAT_SR_COLLECTION = "landsat-c2l2-sr"
PORTAL_WFS = "https://edcintl.cr.usgs.gov/geoserver/wfs"
CDSE_COLLECTION_URL = "https://stac.dataspace.copernicus.eu/v1/collections/sentinel-2-l2a"
NASA_CMR_COLLECTIONS_URL = "https://cmr.earthdata.nasa.gov/search/collections.json"
NIFC_LAYER_URL = (
    "https://services3.arcgis.com/T4QMspbfLg3qTGWY/ArcGIS/rest/services/"
    "WFIGS_Interagency_Perimeters/FeatureServer/0"
)
ANNUAL_NLCD_URL = (
    "https://www.usgs.gov/data/annual-national-land-cover-database-nlcd-"
    "collection-1-products"
)

WARNING = (
    "Experimental BurnLens CV evidence. Not official wildfire information. "
    "Not emergency guidance. Not evacuation, routing, tactical, or "
    "incident-command support. Official sources govern."
)
DECISION = (
    "PRIORITIZE_LANDSAT_BURNED_AREA_AND_CROSS_PROGRAM_FIRE_SCOUTS_"
    "DEFER_ACQUISITION_LABELS_DATASET_MODEL"
)
MAX_RESPONSE_BYTES = 5 * 1024 * 1024
MAX_LANDSAT_CHECKS = 8

CURRENT_EVENT_IDS = {
    "OR4364712147820240625",  # Darlene 3
    "OR4375212142520170829",  # McKay 1035 NE
    "OR4383912111420180907",  # Tepee 1144 NE
}
CURRENT_EVENT_POINTS = (
    (43.662520, -121.437618),  # Darlene final-perimeter bbox center
    (43.75635424, -121.40030388),
    (43.84422006, -121.08323877),
)
KNOWN_CONTEXT = {
    "OR4425712174320170811": (
        "Previously visible as Milli and excluded because no single Sentinel-2 "
        "tile covered the complete MTBS boundary. Landsat ARD uses a different "
        "fixed tiling system and is worth metadata-level reconsideration; full "
        "boundary coverage remains unproved."
    )
}


class OfficialSourceScoutError(RuntimeError):
    """A bounded, secret-free source-scout failure."""


def _write_utf8_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _canonical_sha256(value: Any) -> str:
    return sha256(_canonical_bytes(value)).hexdigest()


def _safe_public_url(url: str) -> str:
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise OfficialSourceScoutError("official source route must use HTTPS")
    return url


def _request_bytes(
    url: str,
    params: tuple[tuple[str, str], ...] | None = None,
    *,
    accept: str = "application/json, application/geo+json",
    timeout_seconds: int = 60,
) -> tuple[bytes, dict[str, Any]]:
    query_url = url if not params else f"{url}?{urlencode(params)}"
    _safe_public_url(query_url)
    request = Request(
        query_url,
        headers={"Accept": accept, "User-Agent": USER_AGENT},
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            status = int(response.status)
            content_type = response.headers.get_content_type()
            payload = response.read(MAX_RESPONSE_BYTES + 1)
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        host = urlsplit(query_url).netloc
        raise OfficialSourceScoutError(
            f"official source is unavailable: {host}"
        ) from error
    if status != 200:
        raise OfficialSourceScoutError(f"official source returned HTTP {status}")
    if len(payload) > MAX_RESPONSE_BYTES:
        raise OfficialSourceScoutError("official source response exceeds bounded size")
    return payload, {
        "request_url": query_url,
        "http_status": status,
        "content_type": content_type,
        "response_bytes": len(payload),
        "response_sha256": sha256(payload).hexdigest(),
    }


def _classify_asset_probe(
    *, final_url: str, content_type: str, payload_prefix: bytes
) -> str:
    final_host = urlsplit(final_url).netloc.lower()
    lowered = payload_prefix.lower()
    if final_host in {"ers.cr.usgs.gov", "ims.cr.usgs.gov"} or (
        content_type == "text/html"
        and (b"eros registration system" in lowered or b"<title>login" in lowered)
    ):
        return "AUTHENTICATION_REQUIRED"
    if content_type in {"application/json", "application/geo+json"}:
        return "PUBLIC_METADATA_ASSET_AVAILABLE"
    return "UNEXPECTED_RESPONSE_DEFER"


def _probe_public_asset_route(
    url: str, *, timeout_seconds: int = 60
) -> dict[str, Any]:
    """Probe one small advertised metadata route without retaining its content."""

    _safe_public_url(url)
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "Range": "bytes=0-65535",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = response.read(65537)
            final_url = response.geturl()
            content_type = response.headers.get_content_type()
            status = int(response.status)
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        raise OfficialSourceScoutError("Landsat metadata asset probe failed") from error
    if len(payload) > 65536:
        raise OfficialSourceScoutError("Landsat metadata asset probe exceeded its bound")
    state = _classify_asset_probe(
        final_url=final_url,
        content_type=content_type,
        payload_prefix=payload[:4096],
    )
    return {
        "advertised_url": url,
        "final_route": f"{urlsplit(final_url).scheme}://{urlsplit(final_url).netloc}{urlsplit(final_url).path}",
        "http_status": status,
        "content_type": content_type,
        "sampled_bytes": len(payload),
        "sample_sha256": sha256(payload).hexdigest(),
        "access_state": state,
        "credentials_sent": False,
        "content_retained": False,
    }


def _json(payload: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise OfficialSourceScoutError(f"{label} is not valid UTF-8 JSON") from error
    if not isinstance(value, dict) or value.get("error"):
        raise OfficialSourceScoutError(f"{label} did not return a valid object")
    return value


def _arcgis_query(
    layer_url: str, params: tuple[tuple[str, str], ...], label: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    payload, evidence = _request_bytes(f"{layer_url}/query", params)
    value = _json(payload, label)
    if value.get("exceededTransferLimit") is True:
        raise OfficialSourceScoutError(f"{label} exceeded its transfer limit")
    features = value.get("features")
    if not isinstance(features, list):
        raise OfficialSourceScoutError(f"{label} did not return a feature list")
    return value, evidence


def _haversine_km(
    latitude_a: float,
    longitude_a: float,
    latitude_b: float,
    longitude_b: float,
) -> float:
    lat_a = radians(latitude_a)
    lat_b = radians(latitude_b)
    delta_lat = lat_b - lat_a
    delta_lon = radians(longitude_b - longitude_a)
    value = (
        sin(delta_lat / 2) ** 2
        + cos(lat_a) * cos(lat_b) * sin(delta_lon / 2) ** 2
    )
    return 6371.0088 * 2 * asin(sqrt(value))


def _minimum_current_distance_km(latitude: float, longitude: float) -> float:
    return min(
        _haversine_km(latitude, longitude, other_latitude, other_longitude)
        for other_latitude, other_longitude in CURRENT_EVENT_POINTS
    )


def _score_candidate(candidate: dict[str, Any], *, landsat_matched: int = 0) -> dict[str, int]:
    program_count = len(candidate["programs"])
    nonstandard_count = sum(1 for item in candidate["products"] if item["nonstandard"])
    evidence = min(5, 1 + program_count + (1 if landsat_matched > 0 else 0))
    acquisition = max(1, 6 - program_count - nonstandard_count)
    year = int(candidate["year"])
    time_diversity = 3 if year <= 1999 else 2 if year <= 2009 else 1 if year <= 2014 else 0
    distance = float(candidate["minimum_current_event_distance_km"])
    spatial_diversity = 2 if distance >= 50 else 1 if distance >= 25 else 0
    diversity = min(5, time_diversity + spatial_diversity)
    fit = 5 if 1000 <= float(candidate["acres"]) <= 30000 else 3
    if candidate["fire_id"] in KNOWN_CONTEXT:
        fit = min(fit, 4)
    owner_review = min(5, program_count + (2 if landsat_matched > 0 else 0))
    overall = evidence * 3 + owner_review * 2 + diversity + fit + acquisition
    return {
        "evidence_value": evidence,
        "acquisition_ease": acquisition,
        "event_geography_time_diversity": diversity,
        "deschutes_task_fit": fit,
        "owner_review_usefulness": owner_review,
        "overall": overall,
    }


def _candidate_sort_key(item: dict[str, Any]) -> tuple[Any, ...]:
    scores = item["scores"]
    return (
        -scores["overall"],
        -scores["evidence_value"],
        -scores["event_geography_time_diversity"],
        item["ignition_date"],
        item["fire_id"],
    )


def _validate_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as error:
        raise OfficialSourceScoutError("captured timestamp is invalid") from error
    if not value.endswith("Z") or parsed.tzinfo is None:
        raise OfficialSourceScoutError("captured timestamp must be UTC")
    return parsed.astimezone(timezone.utc)


def _landsat_search_params(candidate: dict[str, Any]) -> tuple[tuple[str, str], ...]:
    ignition = datetime.fromisoformat(candidate["ignition_date"]).replace(tzinfo=timezone.utc)
    longitude = float(candidate["longitude"])
    latitude = float(candidate["latitude"])
    padding = 0.06
    return (
        ("collections", LANDSAT_BA_COLLECTION),
        (
            "bbox",
            f"{longitude-padding:.6f},{latitude-padding:.6f},"
            f"{longitude+padding:.6f},{latitude+padding:.6f}",
        ),
        (
            "datetime",
            f"{(ignition-timedelta(days=45)).date().isoformat()}T00:00:00Z/"
            f"{(ignition+timedelta(days=400)).date().isoformat()}T23:59:59Z",
        ),
        ("limit", "10"),
    )


def _normalize_landsat_search(
    payload: bytes, candidate: dict[str, Any]
) -> dict[str, Any]:
    value = _json(payload, "Landsat burned-area STAC search")
    if value.get("type") != "FeatureCollection":
        raise OfficialSourceScoutError("Landsat search is not a FeatureCollection")
    features = value.get("features")
    if not isinstance(features, list):
        raise OfficialSourceScoutError("Landsat search feature list is missing")
    retained = []
    for feature in features[:10]:
        if feature.get("collection") != LANDSAT_BA_COLLECTION:
            raise OfficialSourceScoutError("Landsat search returned a different collection")
        assets = feature.get("assets") or {}
        required_assets = {"bc", "bp", "json"}
        if not required_assets.issubset(assets):
            raise OfficialSourceScoutError("Landsat item lacks required BA assets")
        normalized_assets = {}
        for name in sorted(required_assets):
            href = assets[name].get("href")
            if not isinstance(href, str) or urlsplit(href).scheme != "https":
                raise OfficialSourceScoutError("Landsat asset route is not HTTPS")
            normalized_assets[name] = {
                "href": href,
                "type": assets[name].get("type"),
                "roles": assets[name].get("roles") or [],
            }
        properties = feature.get("properties") or {}
        retained.append(
            {
                "item_id": feature.get("id"),
                "datetime": properties.get("datetime"),
                "platform": properties.get("platform"),
                "cloud_cover_percent": properties.get("eo:cloud_cover"),
                "fill_percent": properties.get("landsat:fill"),
                "grid_region": properties.get("landsat:grid_region"),
                "grid_horizontal": properties.get("landsat:grid_horizontal"),
                "grid_vertical": properties.get("landsat:grid_vertical"),
                "assets": normalized_assets,
            }
        )
    return {
        "fire_id": candidate["fire_id"],
        "point_window_only_not_full_boundary_coverage": True,
        "number_matched": int(value.get("numberMatched") or 0),
        "number_returned": int(value.get("numberReturned") or len(features)),
        "retained_items": retained,
    }


def _normalize_cmr(payload: bytes, short_name: str) -> dict[str, Any]:
    value = _json(payload, f"NASA CMR {short_name}")
    entries = ((value.get("feed") or {}).get("entry") or [])
    if not isinstance(entries, list):
        raise OfficialSourceScoutError("NASA CMR entry list is invalid")
    matches = []
    for entry in entries:
        if entry.get("short_name") != short_name:
            continue
        matches.append(
            {
                "short_name": short_name,
                "version_id": entry.get("version_id"),
                "dataset_id": entry.get("dataset_id"),
                "time_start": entry.get("time_start"),
                "time_end": entry.get("time_end"),
                "entry_id": entry.get("id"),
            }
        )
    if not matches:
        raise OfficialSourceScoutError(f"NASA CMR has no {short_name} collection")
    matches.sort(key=lambda item: str(item["version_id"]))
    return {"short_name": short_name, "collections": matches}


def capture_live_source_scout(
    *, captured_at_utc: str, run_id: str, git_source_commit: str
) -> dict[str, Any]:
    """Capture bounded current metadata from official public endpoints."""

    _validate_timestamp(captured_at_utc)
    if not run_id.strip():
        raise OfficialSourceScoutError("run ID is required")
    if not re.fullmatch(r"[0-9a-f]{40}", git_source_commit):
        raise OfficialSourceScoutError("Git source commit must be a full SHA-1")

    evidence: dict[str, Any] = {}
    county, evidence["census_county"] = _arcgis_query(
        COUNTY_URL,
        (
            ("where", f"GEOID='{COUNTY_GEOID}'"),
            ("outFields", "GEOID,NAME"),
            ("returnGeometry", "true"),
            ("outSR", "4326"),
            ("f", "json"),
        ),
        "Census county query",
    )
    if len(county["features"]) != 1:
        raise OfficialSourceScoutError("Deschutes County identity is ambiguous")
    county_geometry = _arcgis_polygon(county["features"][0].get("geometry") or {})

    occurrences, evidence["mtbs_occurrences"] = _arcgis_query(
        f"{MTBS_URL}/{MTBS_OCCURRENCE_LAYER}",
        (
            ("where", "1=1"),
            ("geometry", ",".join(str(value) for value in SEARCH_ENVELOPE)),
            ("geometryType", "esriGeometryEnvelope"),
            ("inSR", "4326"),
            ("spatialRel", "esriSpatialRelIntersects"),
            (
                "outFields",
                "fire_id,fire_name,ig_date,latitude,longitude,acres,map_id,"
                "map_prog,pre_id,post_id",
            ),
            ("returnGeometry", "false"),
            ("f", "json"),
        ),
        "MTBS occurrence query",
    )
    county_occurrences: list[dict[str, Any]] = []
    for feature in occurrences["features"]:
        attributes = feature.get("attributes") or {}
        longitude = float(attributes["longitude"])
        latitude = float(attributes["latitude"])
        if not _inside_geometry(longitude, latitude, county_geometry):
            continue
        ignition = _date_from_epoch_ms(attributes["ig_date"])
        county_occurrences.append(
            {
                "fire_id": str(attributes["fire_id"]),
                "fire_name": str(attributes["fire_name"]),
                "ignition_date": ignition.date().isoformat(),
                "year": ignition.year,
                "latitude": latitude,
                "longitude": longitude,
                "acres": float(attributes["acres"]),
                "occurrence_map_id": attributes.get("map_id"),
                "occurrence_program": attributes.get("map_prog"),
                "pre_image_id": attributes.get("pre_id"),
                "post_image_id": attributes.get("post_id"),
            }
        )
    county_occurrences.sort(key=lambda item: (item["ignition_date"], item["fire_id"]), reverse=True)
    ids = [item["fire_id"] for item in county_occurrences]
    if len(ids) != 23 or len(ids) != len(set(ids)):
        raise OfficialSourceScoutError("current Deschutes MTBS population drifted from 23 unique fires")

    quoted_ids = ",".join(f"'{value}'" for value in sorted(ids))
    boundaries, evidence["mtbs_boundaries"] = _arcgis_query(
        f"{MTBS_URL}/{MTBS_BOUNDARY_LAYER}",
        (
            ("where", f"fire_id IN ({quoted_ids})"),
            (
                "outFields",
                "fire_id,fire_name,year,fire_type,acres,asmnt_type,ig_date,"
                "map_id,map_prog,pre_id,post_id",
            ),
            ("returnGeometry", "false"),
            ("f", "json"),
        ),
        "MTBS boundary query",
    )
    boundary_by_id = {
        str(feature["attributes"]["fire_id"]): feature["attributes"]
        for feature in boundaries["features"]
    }
    if set(boundary_by_id) != set(ids):
        raise OfficialSourceScoutError("MTBS boundary population does not match occurrences")

    wfs_params = (
        ("service", "WFS"),
        ("version", "2.0.0"),
        ("request", "GetFeature"),
        ("typeNames", "mtbs:fire_polygons"),
        ("outputFormat", "application/json"),
        (
            "propertyName",
            "id,map_id,map_prog,incid_name,event_id,ig_date,burnbndac,nonstandard",
        ),
        ("cql_filter", f"event_id IN ({quoted_ids})"),
    )
    wfs_payload, evidence["burn_severity_portal_catalog"] = _request_bytes(
        PORTAL_WFS, wfs_params
    )
    wfs = _json(wfs_payload, "Burn Severity Portal catalog")
    if wfs.get("type") != "FeatureCollection":
        raise OfficialSourceScoutError("Burn Severity Portal catalog is not GeoJSON")
    products_by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for feature in wfs.get("features") or []:
        if feature.get("geometry") is not None:
            raise OfficialSourceScoutError("portal scout must remain property-only")
        props = feature.get("properties") or {}
        event_id = str(props.get("event_id"))
        if event_id not in set(ids):
            raise OfficialSourceScoutError("portal returned an unexpected event")
        program = props.get("map_prog")
        if program not in {"BAER", "MTBS", "RAVG"}:
            raise OfficialSourceScoutError("portal returned an unexpected program")
        products_by_event[event_id].append(
            {
                "catalog_id": int(props["id"]),
                "map_id": int(props["map_id"]),
                "program": program,
                "incident_name": str(props["incid_name"]),
                "boundary_acres": int(props["burnbndac"]),
                "nonstandard": bool(props["nonstandard"]),
            }
        )
    for products in products_by_event.values():
        products.sort(key=lambda item: (item["program"], item["catalog_id"]))

    candidates: list[dict[str, Any]] = []
    for occurrence in county_occurrences:
        boundary = boundary_by_id[occurrence["fire_id"]]
        item = {
            **occurrence,
            "fire_type": boundary.get("fire_type"),
            "assessment_type": boundary.get("asmnt_type"),
            "products": products_by_event.get(occurrence["fire_id"], []),
        }
        item["programs"] = sorted({product["program"] for product in item["products"]})
        item["minimum_current_event_distance_km"] = round(
            _minimum_current_distance_km(item["latitude"], item["longitude"]), 3
        )
        item["already_in_pending_seven_bundle_request"] = item["fire_id"] in CURRENT_EVENT_IDS
        item["known_context"] = KNOWN_CONTEXT.get(item["fire_id"])
        if item["fire_type"] != "Wildfire":
            continue
        item["scores"] = _score_candidate(item)
        candidates.append(item)

    new_candidates = [
        item for item in candidates if not item["already_in_pending_seven_bundle_request"]
    ]
    new_candidates.sort(key=_candidate_sort_key)
    landsat_check_ids = {item["fire_id"] for item in new_candidates[:MAX_LANDSAT_CHECKS]}
    landsat_checks = []
    for candidate in new_candidates:
        if candidate["fire_id"] not in landsat_check_ids:
            continue
        params = _landsat_search_params(candidate)
        payload, route = _request_bytes(LANDSAT_SEARCH_URL, params)
        check = _normalize_landsat_search(payload, candidate)
        route["fire_id"] = candidate["fire_id"]
        evidence.setdefault("landsat_burned_area_searches", []).append(route)
        check["request_url"] = route["request_url"]
        check["response_sha256"] = route["response_sha256"]
        landsat_checks.append(check)
        candidate["scores"] = _score_candidate(
            candidate, landsat_matched=check["number_matched"]
        )
        candidate["landsat_burned_area"] = check
    new_candidates.sort(key=_candidate_sort_key)
    top_landsat = new_candidates[0].get("landsat_burned_area") or {}
    retained_items = top_landsat.get("retained_items") or []
    if not retained_items:
        raise OfficialSourceScoutError("top candidate lacks a Landsat metadata item")
    metadata_url = retained_items[0]["assets"]["json"]["href"]
    evidence["landsat_metadata_asset_probe"] = _probe_public_asset_route(metadata_url)
    for index, item in enumerate(new_candidates, start=1):
        item["rank"] = index

    collections_payload, evidence["landsat_collections"] = _request_bytes(
        LANDSAT_COLLECTIONS_URL
    )
    collections = _json(collections_payload, "Landsat STAC collections")
    by_collection = {
        item.get("id"): item for item in collections.get("collections") or []
    }
    if not {LANDSAT_BA_COLLECTION, LANDSAT_SR_COLLECTION}.issubset(by_collection):
        raise OfficialSourceScoutError("required Landsat collections are unavailable")

    cdse_payload, evidence["sentinel_2_collection"] = _request_bytes(
        CDSE_COLLECTION_URL
    )
    cdse = _json(cdse_payload, "CDSE Sentinel-2 collection")
    if cdse.get("id") != "sentinel-2-l2a":
        raise OfficialSourceScoutError("CDSE Sentinel-2 collection identity drifted")

    nasa_collections = []
    for short_name in ("MCD64A1", "VNP64A1"):
        payload, route = _request_bytes(
            NASA_CMR_COLLECTIONS_URL,
            (("short_name", short_name), ("page_size", "10")),
        )
        evidence[f"nasa_cmr_{short_name.lower()}"] = route
        nasa_collections.append(_normalize_cmr(payload, short_name))

    nifc_payload, evidence["nifc_wfigs_layer"] = _request_bytes(
        NIFC_LAYER_URL, (("f", "json"),)
    )
    nifc = _json(nifc_payload, "NIFC WFIGS layer")
    if nifc.get("type") != "Feature Layer":
        raise OfficialSourceScoutError("NIFC perimeter layer identity drifted")

    nlcd_payload, evidence["annual_nlcd_page"] = _request_bytes(
        ANNUAL_NLCD_URL, accept="text/html,application/xhtml+xml"
    )
    nlcd_text = nlcd_payload.decode("utf-8", errors="replace")
    if "Annual National Land Cover Database" not in nlcd_text or "CC0" not in nlcd_text:
        raise OfficialSourceScoutError("Annual NLCD identity or rights are not visible")

    source_classes = [
        {
            "source_class": "Burn Severity Portal BAER/RAVG/MTBS fire bundles",
            "live_identity": f"{sum(len(value) for value in products_by_event.values())} products across 23 current Deschutes MTBS events",
            "resolution_or_scale": "typically 30 m raster plus vector/metadata products; inspect each bundle",
            "temporal_relationship": "program-specific immediate, initial, or extended post-fire assessment",
            "role": "cross-program reference and optical interpretation support",
            "label_truth_status": "never automatic truth; analyst/model/product limitations remain binding",
            "terms_status": "public catalog reconnaissance resolved; exact bundle notices govern redistribution",
            "access_route": evidence["burn_severity_portal_catalog"]["request_url"],
        },
        {
            "source_class": "USGS Landsat Collection 2 Level-3 Burned Area",
            "live_identity": by_collection[LANDSAT_BA_COLLECTION].get("title"),
            "resolution_or_scale": "30 m; fixed U.S. ARD tiles; CONUS 1984-present",
            "temporal_relationship": "acquisition-based burn probability and thresholded burn classification",
            "role": "independent algorithmic burned/background candidate reference",
            "label_truth_status": "not ground truth; QA, commission/omission, water/shadow, coverage, and optical checks required",
            "terms_status": "no Landsat use restrictions; cite the dataset; advertised asset retrieval currently redirects to EROS authentication",
            "access_state": evidence["landsat_metadata_asset_probe"]["access_state"],
            "access_route": LANDSAT_COLLECTIONS_URL,
        },
        {
            "source_class": "USGS Landsat Collection 2 Level-2 Surface Reflectance",
            "live_identity": by_collection[LANDSAT_SR_COLLECTION].get("title"),
            "resolution_or_scale": "30 m surface reflectance plus QA bands",
            "temporal_relationship": "select event-specific pre/post acquisitions",
            "role": "optical corroboration, time-series comparison, and affirmative unchanged support",
            "label_truth_status": "imagery and QA are evidence, not labels",
            "terms_status": "no Landsat use restrictions; cite the dataset",
            "access_route": LANDSAT_COLLECTIONS_URL,
        },
        {
            "source_class": "Copernicus Sentinel-2 L2A",
            "live_identity": cdse.get("title"),
            "resolution_or_scale": "10/20/60 m bands; BurnLens uses native grids",
            "temporal_relationship": "event-specific same-orbit pre/post pairs",
            "role": "primary high-resolution optical evidence for the preserved task",
            "label_truth_status": "dNBR, SCL, and imagery do not independently create truth",
            "terms_status": "free/open under the Sentinel legal notice with attribution",
            "access_route": CDSE_COLLECTION_URL,
        },
        {
            "source_class": "NIFC WFIGS Interagency Fire Perimeters",
            "live_identity": nifc.get("name"),
            "resolution_or_scale": "mixed-method vector incident geometry",
            "temporal_relationship": "incident record updated over time",
            "role": "incident identity, AOI, and perimeter context",
            "label_truth_status": "dynamic reference; not a legal document or pixel-perfect burn boundary",
            "terms_status": "public official service; source disclaimer and attribution remain binding",
            "access_route": NIFC_LAYER_URL,
        },
        {
            "source_class": "NASA MCD64A1 / VNP64A1 burned area",
            "live_identity": " / ".join(
                item["collections"][-1]["dataset_id"] for item in nasa_collections
            ),
            "resolution_or_scale": "500 m monthly global burned-area grids",
            "temporal_relationship": "monthly burn-date detection from reflectance and active-fire inputs",
            "role": "coarse temporal/context comparison only",
            "label_truth_status": "rejected as 10-30 m label truth or boundary evidence",
            "terms_status": "NASA-led data default CC0 unless marked; cite and do not imply endorsement",
            "access_route": NASA_CMR_COLLECTIONS_URL,
        },
        {
            "source_class": "USGS Annual NLCD Collection 1.2",
            "live_identity": "Annual NLCD Collection 1.2, June 2026, DOI 10.5066/P94UXNTS",
            "resolution_or_scale": "30 m annual land cover/change, CONUS 1985-present",
            "temporal_relationship": "choose the pre-fire year or same-release comparison years",
            "role": "land-cover context, stratification, and RAVG applicability screening",
            "label_truth_status": "land cover is not fire evidence or affirmative background by itself",
            "terms_status": "USGS data release is CC0 1.0; cite the dataset",
            "access_route": ANNUAL_NLCD_URL,
        },
    ]

    return {
        "source_id": SOURCE_ID,
        "source_schema_version": SOURCE_SCHEMA_VERSION,
        "captured_at_utc": captured_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "parent_bundle_issue": PARENT_BUNDLE_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "capture_scope": "public official metadata and small metadata responses only; no large product acquisition",
        "source_response_evidence": evidence,
        "population": {
            "search_envelope_wgs84": SEARCH_ENVELOPE,
            "county_geoid": COUNTY_GEOID,
            "deschutes_mtbs_fire_count": len(county_occurrences),
            "portal_product_count": sum(len(value) for value in products_by_event.values()),
            "new_candidate_count": len(new_candidates),
            "pending_bundle_event_ids": sorted(CURRENT_EVENT_IDS),
        },
        "source_classes": source_classes,
        "candidates": new_candidates,
        "landsat_checks": sorted(landsat_checks, key=lambda item: item["fire_id"]),
        "capture_sha256": None,
    }


def finalize_source_capture(source: dict[str, Any]) -> dict[str, Any]:
    finalized = json.loads(json.dumps(source))
    finalized["capture_sha256"] = None
    finalized["capture_sha256"] = _canonical_sha256(finalized)
    return finalized


def validate_source_capture(source: dict[str, Any]) -> None:
    if source.get("source_id") != SOURCE_ID:
        raise OfficialSourceScoutError("source capture identity is invalid")
    expected = source.get("capture_sha256")
    copy = json.loads(json.dumps(source))
    copy["capture_sha256"] = None
    if expected != _canonical_sha256(copy):
        raise OfficialSourceScoutError("source capture hash is invalid")
    population = source.get("population") or {}
    if population.get("deschutes_mtbs_fire_count") != 23:
        raise OfficialSourceScoutError("source capture fire population is invalid")
    candidates = source.get("candidates") or []
    if not candidates or any(item.get("already_in_pending_seven_bundle_request") for item in candidates):
        raise OfficialSourceScoutError("source capture duplicates pending bundle events")
    ranks = [item.get("rank") for item in candidates]
    if ranks != list(range(1, len(candidates) + 1)):
        raise OfficialSourceScoutError("source capture candidate ranks are invalid")


def build_official_source_scout(source: dict[str, Any]) -> dict[str, Any]:
    validate_source_capture(source)
    candidates = source["candidates"]
    top = candidates[:8]
    return {
        "report_id": REPORT_ID,
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
        "scout_protocol_version": SCOUT_PROTOCOL_VERSION,
        "generated_at_utc": source["captured_at_utc"],
        "run_id": source["run_id"],
        "repository": source["repository"],
        "task_issue": TASK_ISSUE,
        "parent_bundle_issue": PARENT_BUNDLE_ISSUE,
        "git_source_commit": source["git_source_commit"],
        "software_version": SOFTWARE_VERSION,
        "application_version": None,
        "aoi_version": "aoi-darlene3-model-v0.2.0",
        "target_version": "target-burn-scar-v0.2.0",
        "dataset_version": None,
        "split_version": None,
        "label_schema_version": "burn-scar-five-state-schema-v0.1.0",
        "owner_review_protocol_version": "owner-confirmed-prototype-label-review-v0.1.0",
        "baseline_version": None,
        "model_version": None,
        "source_record_id": SOURCE_RECORD_ID,
        "terms_record_id": TERMS_RECORD_ID,
        "source_precedence_review_id": SOURCE_PRECEDENCE_REVIEW_ID,
        "source_capture": {
            "source_id": source["source_id"],
            "capture_sha256": source["capture_sha256"],
            "source_response_count": len(source["source_response_evidence"]),
        },
        "scoring_rule": {
            "predeclared_dimensions": [
                "evidence value",
                "acquisition ease",
                "event/geography/time diversity",
                "Deschutes task fit",
                "owner-review usefulness",
            ],
            "overall_formula": "3*evidence + 2*owner_review + diversity + task_fit + acquisition_ease",
            "landsat_live_check_limit": MAX_LANDSAT_CHECKS,
            "tie_break": "evidence, diversity, older ignition date, stable fire ID",
            "important_boundary": "scores prioritize reconnaissance only and cannot promote a label",
        },
        "findings": {
            "source_class_count": len(source["source_classes"]),
            "deschutes_mtbs_fire_count": source["population"]["deschutes_mtbs_fire_count"],
            "new_candidate_count": source["population"]["new_candidate_count"],
            "landsat_checked_candidate_count": len(source["landsat_checks"]),
            "top_candidates": top,
            "source_classes": source["source_classes"],
        },
        "portfolio_recommendation": {
            "first_source_to_test": "USGS Landsat Collection 2 Level-3 Burned Area",
            "why": (
                "It supplies 30 m acquisition-based burn probability and classification "
                "across forest, shrub, and grass ecosystems through a live official route. "
                "It can challenge both burned and background candidates without inheriting "
                "the Sentinel single-tile constraint, but it remains algorithmic reference evidence. "
                "The public STAC metadata is live while the advertised asset probe redirects to "
                "EROS authentication, so acquisition remains gated rather than assumed."
            ),
            "next_acquisition_rule": (
                "Acquire only a small metadata-plus-COG-window proof for the highest-ranked "
                "candidate whose exact asset terms, full-boundary grid coverage, QA, and "
                "temporal relationship pass. Do not duplicate the seven pending bundles."
            ),
        },
        "owner_review_consequence": {
            "workflow": "Codex proposes disclosed burned/background candidates; owner answers yes/no/uncertain.",
            "use": (
                "Show Landsat BA probability/classification only beside independent optical, "
                "quality, and program evidence. A yes can advance only after source, "
                "reproducibility, quality, and leakage gates."
            ),
            "not_claimed": [
                "independent reviewer evidence",
                "ground truth",
                "inter-rater agreement",
                "field validation",
                "official or endorsed status",
                "operational or enterprise readiness",
            ],
        },
        "queue_boundary": {
            "issue": PARENT_BUNDLE_ISSUE,
            "accepted_request_duplicated": False,
            "delivered_bundle_substituted": False,
            "state": "seven exact BAER/RAVG/MTBS bundles remain pending and separately governed",
        },
        "promotion_gates": [
            "resolve exact product-level terms and notices before data retention or publication",
            "verify exact item identity, full-boundary coverage, CRS, grid, nodata, QA, and temporal relationship",
            "compare candidate pixels against optical evidence and applicable cross-program references",
            "preserve whole-event/geography/time groups before any dataset split",
            "obtain explicit owner yes; no and uncertain remain excluded",
            "publish rendered source-fitness evidence before any prototype-label promotion",
        ],
        "claim_boundaries": {
            "metadata_reconnaissance_only": True,
            "large_products_acquired": False,
            "provider_pixels_opened": False,
            "original_56_units_changed": False,
            "owner_responses_collected": False,
            "labels_promoted": False,
            "dataset_created": False,
            "split_created": False,
            "baseline_run": False,
            "model_trained": False,
            "scientific_or_field_validation_claimed": False,
        },
        "decision": DECISION,
        "warning": WARNING,
    }


def _html(report: dict[str, Any]) -> str:
    source_rows = "".join(
        "<tr>"
        f"<td>{escape(item['source_class'])}</td>"
        f"<td>{escape(item['resolution_or_scale'])}</td>"
        f"<td>{escape(item['role'])}</td>"
        f"<td>{escape(item['label_truth_status'])}</td>"
        f"<td>{escape(item['terms_status'])}</td>"
        "</tr>"
        for item in report["findings"]["source_classes"]
    )
    candidate_rows = "".join(
        "<tr>"
        f"<td>{item['rank']}</td>"
        f"<td>{escape(item['fire_name'])}<br><code>{escape(item['fire_id'])}</code></td>"
        f"<td>{item['year']}</td>"
        f"<td>{item['acres']:,.0f}</td>"
        f"<td>{escape('/'.join(item['programs']) or 'MTBS occurrence only')}</td>"
        f"<td>{item['minimum_current_event_distance_km']:.1f} km</td>"
        f"<td>{item['scores']['overall']}</td>"
        f"<td>{(item.get('landsat_burned_area') or {}).get('number_matched', 'not checked')}</td>"
        "</tr>"
        for item in report["findings"]["top_candidates"]
    )
    gate_items = "".join(
        f"<li>{escape(item)}</li>" for item in report["promotion_gates"]
    )
    not_claimed = "".join(
        f"<li>{escape(item)}</li>"
        for item in report["owner_review_consequence"]["not_claimed"]
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BurnLens official source scout</title>
<style>
:root{{--ink:#182522;--teal:#075f59;--orange:#b94b21;--cream:#f7f1e8;--panel:#fff;--muted:#53615d}}*{{box-sizing:border-box}}body{{margin:0;background:var(--cream);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header{{background:#123d39;color:#fff;padding:3rem max(1rem,calc((100% - 1160px)/2))}}header p{{max-width:900px}}main{{max-width:1160px;margin:auto;padding:2rem 1rem 5rem}}.warning,.card{{background:var(--panel);border:1px solid #d8d0c4;border-radius:12px;padding:1.2rem;margin:1rem 0}}.warning{{border-left:6px solid var(--orange)}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.05;margin:.4rem 0}}h2{{color:var(--teal);margin-top:2.2rem}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem}}.metric{{background:#e4efeb;padding:1rem;border-radius:10px}}.metric strong{{display:block;font-size:1.8rem;color:var(--teal)}}.table{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;background:#fff}}th,td{{padding:.7rem;border:1px solid #d9d1c5;text-align:left;vertical-align:top}}th{{background:#dceae6}}code{{overflow-wrap:anywhere}}a{{color:var(--teal)}}@media(max-width:700px){{header{{padding:2rem 1rem}}main{{padding:.8rem}}th,td{{font-size:.85rem}}}}
</style></head><body><header><p>BurnLens / Phase Two / issue #{TASK_ISSUE}</p><h1>Official source and candidate-fire scout</h1><p>Metadata-first reconnaissance for stronger burned candidates, affirmative background candidates, leakage-resistant diversity, and owner-confirmed review evidence.</p></header><main>
<p class="warning">{escape(report['warning'])}</p>
<section class="metrics"><div class="metric"><strong>{report['findings']['source_class_count']}</strong>official source classes</div><div class="metric"><strong>{report['findings']['deschutes_mtbs_fire_count']}</strong>current Deschutes MTBS fires</div><div class="metric"><strong>{report['findings']['new_candidate_count']}</strong>new candidate fires</div><div class="metric"><strong>0</strong>labels or datasets</div></section>
<section class="card"><h2>Decision</h2><p><strong>{escape(report['decision'])}</strong></p><p>{escape(report['portfolio_recommendation']['why'])}</p><p>The accepted seven-bundle request remains pending under issue #{PARENT_BUNDLE_ISSUE}; this scout neither duplicates it nor substitutes for delivery.</p></section>
<h2>Ranked new candidate fires</h2><div class="table"><table><thead><tr><th>Rank</th><th>Fire</th><th>Year</th><th>Acres</th><th>Current programs</th><th>Distance from current events</th><th>Score</th><th>Landsat BA items</th></tr></thead><tbody>{candidate_rows}</tbody></table></div>
<p>Each Landsat count is a point-window metadata check, not proof that a product covers the complete fire boundary. Scores prioritize reconnaissance only.</p>
<h2>Source roles and boundaries</h2><div class="table"><table><thead><tr><th>Source class</th><th>Resolution/scale</th><th>BurnLens role</th><th>Truth boundary</th><th>Terms state</th></tr></thead><tbody>{source_rows}</tbody></table></div>
<section class="card"><h2>Owner-confirmed review consequence</h2><p>{escape(report['owner_review_consequence']['workflow'])}</p><p>{escape(report['owner_review_consequence']['use'])}</p><h3>Not claimed</h3><ul>{not_claimed}</ul></section>
<section class="card"><h2>Promotion gates</h2><ol>{gate_items}</ol></section>
<section class="card"><h2>Traceability</h2><p><strong>Run:</strong> <code>{escape(report['run_id'])}</code><br><strong>Git source:</strong> <code>{escape(report['git_source_commit'])}</code><br><strong>BurnLens:</strong> <code>{escape(report['software_version'])}</code><br><strong>Source capture:</strong> <code>{escape(report['source_capture']['capture_sha256'])}</code><br><strong>Dataset / split / baseline / model:</strong> none / none / none / none</p></section>
</main></body></html>"""


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = (
        ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/Arial.ttf")
        if bold
        else ("C:/Windows/Fonts/Arial.ttf", "C:/Windows/Fonts/arial.ttf")
    )
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    *,
    width: int,
    font: ImageFont.ImageFont,
    fill: str,
    spacing: int = 8,
) -> int:
    lines = wrap(text, width=max(10, width)) or [""]
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        box = draw.textbbox((x, y), line or " ", font=font)
        y += box[3] - box[1] + spacing
    return y


def _png(report: dict[str, Any]) -> Image.Image:
    image = Image.new("RGB", (1800, 1540), "#f7f1e8")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1800, 250), fill="#123d39")
    draw.text((90, 55), "BURNLENS / PHASE TWO / OFFICIAL SOURCE SCOUT", font=_font(23, True), fill="#9fe3d8")
    draw.text((90, 102), "Evidence before acquisition", font=_font(54, True), fill="white")
    draw.text((90, 178), "Metadata-only / no labels / no dataset / no model", font=_font(25), fill="#d8eee9")
    metrics = (
        ("7", "official source classes"),
        (str(report["findings"]["deschutes_mtbs_fire_count"]), "Deschutes MTBS fires"),
        (str(report["findings"]["new_candidate_count"]), "new candidate fires"),
        ("0", "labels promoted"),
    )
    for index, (value, label) in enumerate(metrics):
        x = 90 + index * 420
        draw.rounded_rectangle((x, 285, x + 370, 405), radius=16, fill="#e0ece8")
        draw.text((x + 24, 306), value, font=_font(42, True), fill="#075f59")
        draw.text((x + 24, 362), label, font=_font(18), fill="#263b36")
    draw.text((90, 455), "RANKED METADATA SCOUTS", font=_font(25, True), fill="#075f59")
    y = 505
    for item in report["findings"]["top_candidates"]:
        draw.rounded_rectangle((90, y, 1710, y + 80), radius=10, fill="white", outline="#d3cabb")
        draw.text((110, y + 20), f"{item['rank']:02d}", font=_font(25, True), fill="#b94b21")
        draw.text((175, y + 17), item["fire_name"][:42], font=_font(22, True), fill="#182522")
        draw.text((660, y + 20), str(item["year"]), font=_font(21), fill="#354842")
        draw.text((770, y + 20), "/".join(item["programs"]) or "MTBS", font=_font(19), fill="#075f59")
        draw.text((1090, y + 20), f"{item['minimum_current_event_distance_km']:.1f} km", font=_font(19), fill="#354842")
        draw.text((1330, y + 20), f"score {item['scores']['overall']}", font=_font(20, True), fill="#075f59")
        landsat = (item.get("landsat_burned_area") or {}).get("number_matched")
        draw.text((1510, y + 20), f"BA {landsat if landsat is not None else '—'}", font=_font(19), fill="#354842")
        y += 92
    draw.rounded_rectangle((90, 1260, 1710, 1470), radius=16, fill="#fff", outline="#d3cabb")
    draw.text((120, 1292), "NEXT EVIDENCE MOVE", font=_font(22, True), fill="#075f59")
    _draw_wrapped(
        draw,
        report["portfolio_recommendation"]["why"],
        (120, 1332),
        width=112,
        font=_font(19),
        fill="#263b36",
        spacing=6,
    )
    draw.text((120, 1435), f"Run {report['run_id']}  /  dataset, split, baseline, model: none", font=_font(16), fill="#52635e")
    return image


def write_official_source_scout(
    source: dict[str, Any],
    report: dict[str, Any],
    *,
    source_json_path: Path,
    report_json_path: Path,
    html_path: Path,
    png_path: Path,
) -> None:
    _write_utf8_lf(source_json_path, json.dumps(source, indent=2) + "\n")
    _write_utf8_lf(report_json_path, json.dumps(report, indent=2) + "\n")
    _write_utf8_lf(html_path, _html(report))
    png_path.parent.mkdir(parents=True, exist_ok=True)
    _png(report).save(png_path, format="PNG", optimize=False)
