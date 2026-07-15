"""Capture current official metadata for cross-event BurnLens feasibility."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

SOURCE_ID = "CROSS-EVENT-SOURCE-2026-001"
SOURCE_SCHEMA_VERSION = "0.1.0"
SOFTWARE_VERSION = "0.10.0"
COUNTY_GEOID = "41017"
COUNTY_URL = (
    "https://tigerweb.geo.census.gov/arcgis/rest/services/"
    "TIGERweb/State_County/MapServer/9"
)
MTBS_URL = "https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_MTBS_01/MapServer"
MTBS_OCCURRENCE_LAYER = 62
MTBS_BOUNDARY_LAYER = 63
CDSE_STAC_URL = "https://stac.dataspace.copernicus.eu/v1/search"
CDSE_COLLECTION_URL = (
    "https://stac.dataspace.copernicus.eu/v1/collections/sentinel-2-l2a"
)
SEARCH_ENVELOPE = [-122.2, 43.25, -120.75, 44.75]
MIN_YEAR = 2017
MAX_ACRES = 30_000.0
MAX_STAC_EVENTS = 8
AOI_VERSION = "aoi-darlene3-model-v0.2.0"
TARGET_VERSION = "target-burn-scar-v0.2.0"
LABEL_SCHEMA_VERSION = "burn-scar-five-state-schema-v0.1.0"


class CrossEventSourceError(ValueError):
    """Raised when an official metadata source is incomplete or drifts."""


def _write_utf8_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _safe_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def _request_json(url: str, params: dict[str, Any] | None = None) -> tuple[dict[str, Any], str]:
    query_url = url if not params else f"{url}?{urlencode(params)}"
    request = Request(
        query_url,
        headers={
            "Accept": "application/json, application/geo+json",
            "User-Agent": "BurnLens-Deschutes/0.10 metadata-only",
        },
    )
    try:
        with urlopen(request, timeout=60) as response:
            status = response.status
            payload = response.read()
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        raise CrossEventSourceError(f"SOURCE_REQUEST_FAILED:{_safe_url(query_url)}") from error
    if status != 200:
        raise CrossEventSourceError(f"SOURCE_HTTP_STATUS:{status}:{_safe_url(query_url)}")
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise CrossEventSourceError(f"SOURCE_JSON_INVALID:{_safe_url(query_url)}") from error
    if not isinstance(value, dict):
        raise CrossEventSourceError("SOURCE_JSON_OBJECT_REQUIRED")
    if value.get("error"):
        raise CrossEventSourceError(f"SOURCE_API_ERROR:{value['error']}")
    return value, query_url


def _require_fields(layer: dict[str, Any], required: set[str], label: str) -> list[str]:
    names = [str(item.get("name")) for item in layer.get("fields", [])]
    missing = sorted(required.difference(names))
    if missing:
        raise CrossEventSourceError(f"{label}_FIELDS_MISSING:{','.join(missing)}")
    return names


def _require_complete_arcgis_query(payload: dict[str, Any], label: str) -> None:
    if payload.get("exceededTransferLimit") is True:
        raise CrossEventSourceError(f"{label}_TRANSFER_LIMIT_EXCEEDED")


def _arcgis_polygon(geometry: dict[str, Any]) -> dict[str, Any]:
    rings = geometry.get("rings")
    if not isinstance(rings, list) or not rings:
        raise CrossEventSourceError("ARCGIS_POLYGON_RINGS_REQUIRED")
    return {"type": "Polygon", "coordinates": rings}


def _point_on_segment(
    x: float,
    y: float,
    first: list[float],
    second: list[float],
    *,
    tolerance: float = 1e-9,
) -> bool:
    x1, y1 = float(first[0]), float(first[1])
    x2, y2 = float(second[0]), float(second[1])
    cross = (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)
    scale = max(1.0, abs(x2 - x1), abs(y2 - y1))
    if abs(cross) > tolerance * scale:
        return False
    return (
        min(x1, x2) - tolerance <= x <= max(x1, x2) + tolerance
        and min(y1, y2) - tolerance <= y <= max(y1, y2) + tolerance
    )


def _point_in_ring(x: float, y: float, ring: list[list[float]]) -> bool:
    if len(ring) < 4:
        raise CrossEventSourceError("GEOMETRY_RING_INVALID")
    inside = False
    for index in range(len(ring)):
        first = ring[index]
        second = ring[(index + 1) % len(ring)]
        if _point_on_segment(x, y, first, second):
            return True
        x1, y1 = float(first[0]), float(first[1])
        x2, y2 = float(second[0]), float(second[1])
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


def _inside_geometry(longitude: float, latitude: float, geometry: dict[str, Any]) -> bool:
    coordinates = geometry.get("coordinates")
    if geometry.get("type") == "Polygon":
        polygons = [coordinates]
    elif geometry.get("type") == "MultiPolygon":
        polygons = coordinates
    else:
        raise CrossEventSourceError("GEOMETRY_POLYGON_REQUIRED")
    if not isinstance(polygons, list):
        raise CrossEventSourceError("GEOMETRY_COORDINATES_REQUIRED")
    for polygon in polygons:
        if not polygon or not _point_in_ring(longitude, latitude, polygon[0]):
            continue
        if any(_point_in_ring(longitude, latitude, hole) for hole in polygon[1:]):
            continue
        return True
    return False


def _date_from_epoch_ms(value: Any) -> datetime:
    if not isinstance(value, (int, float)):
        raise CrossEventSourceError("MTBS_IGNITION_DATE_INVALID")
    return datetime.fromtimestamp(value / 1000.0, tz=timezone.utc)


def _boundary_points(geometry: dict[str, Any]) -> list[list[float]]:
    coordinates = geometry.get("coordinates")
    if geometry.get("type") != "Polygon" or not coordinates:
        raise CrossEventSourceError("MTBS_BOUNDARY_POLYGON_REQUIRED")
    return [point for ring in coordinates for point in ring]


def _geometry_bbox(geometry: dict[str, Any]) -> list[float]:
    points = _boundary_points(geometry)
    xs = [float(point[0]) for point in points]
    ys = [float(point[1]) for point in points]
    return [min(xs), min(ys), max(xs), max(ys)]


def _expanded_bbox(bbox: list[float], degrees: float = 0.03) -> list[float]:
    return [bbox[0] - degrees, bbox[1] - degrees, bbox[2] + degrees, bbox[3] + degrees]


def _iso_day(value: datetime, *, end: bool = False) -> str:
    time = "23:59:59Z" if end else "00:00:00Z"
    return f"{value.date().isoformat()}T{time}"


def _coverage_complete(item_geometry: dict[str, Any], boundary: dict[str, Any]) -> bool:
    points = _boundary_points(boundary)
    # Full boundary-vertex containment is conservative and rejects tile-seam events.
    return all(_inside_geometry(float(point[0]), float(point[1]), item_geometry) for point in points)


def _normalize_stac_item(
    item: dict[str, Any], *, window: str, boundary: dict[str, Any]
) -> dict[str, Any] | None:
    properties = item.get("properties") or {}
    geometry = item.get("geometry") or {}
    if not _coverage_complete(geometry, boundary):
        return None
    required = (
        "datetime",
        "platform",
        "grid:code",
        "sat:relative_orbit",
        "processing:version",
        "eo:cloud_cover",
    )
    if any(properties.get(name) is None for name in required):
        raise CrossEventSourceError(f"STAC_ITEM_PROPERTY_MISSING:{item.get('id')}")
    product = (item.get("assets") or {}).get("Product") or {}
    href = product.get("href")
    route = urlsplit(href) if isinstance(href, str) else None
    allowed_product_hosts = {
        "download.dataspace.copernicus.eu",
        "zipper.dataspace.copernicus.eu",
    }
    if (
        route is None
        or route.scheme != "https"
        or route.netloc not in allowed_product_hosts
        or not route.path.startswith(("/download/", "/odata/v1/Products("))
    ):
        raise CrossEventSourceError(f"STAC_PRODUCT_ROUTE_UNEXPECTED:{item.get('id')}")
    return {
        "id": item.get("id"),
        "window": window,
        "datetime": properties["datetime"],
        "platform": properties["platform"],
        "grid_code": properties["grid:code"],
        "relative_orbit": int(properties["sat:relative_orbit"]),
        "processing_version": str(properties["processing:version"]),
        "cloud_cover_percent": float(properties["eo:cloud_cover"]),
        "snow_cover_percent": float(properties.get("eo:snow_cover") or 0.0),
        "bbox": [float(value) for value in item.get("bbox", [])],
        "product_href": href,
        "product_bytes": int(product.get("file:size") or 0),
        "provider_checksum": product.get("file:checksum"),
        "product_filename": product.get("file:local_path"),
    }


def _stac_window(
    *,
    bbox: list[float],
    start: datetime,
    end: datetime,
    window: str,
    boundary: dict[str, Any],
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "collections": "sentinel-2-l2a",
        "bbox": ",".join(f"{value:.8f}" for value in bbox),
        "datetime": f"{_iso_day(start)}/{_iso_day(end, end=True)}",
        "limit": 100,
        "sortby": "+datetime",
    }
    pages = 0
    returned = 0
    retained: dict[str, dict[str, Any]] = {}
    url = CDSE_STAC_URL
    first_url = ""
    next_params: dict[str, Any] | None = params
    while url:
        payload, query_url = _request_json(url, next_params)
        if not first_url:
            first_url = query_url
        pages += 1
        if pages > 10:
            raise CrossEventSourceError("STAC_PAGINATION_LIMIT_EXCEEDED")
        features = payload.get("features")
        if not isinstance(features, list):
            raise CrossEventSourceError("STAC_FEATURES_INVALID")
        returned += len(features)
        for item in features:
            normalized = _normalize_stac_item(item, window=window, boundary=boundary)
            if normalized is not None:
                retained[str(normalized["id"])] = normalized
        next_links = [
            link for link in payload.get("links", []) if link.get("rel") == "next"
        ]
        if not next_links:
            break
        href = next_links[0].get("href")
        if not isinstance(href, str) or not href.startswith("https://stac.dataspace.copernicus.eu/"):
            raise CrossEventSourceError("STAC_NEXT_LINK_UNEXPECTED")
        url = href
        next_params = None
    return {
        "window": window,
        "start_utc": _iso_day(start),
        "end_utc": _iso_day(end, end=True),
        "query_url": first_url,
        "page_count": pages,
        "returned_item_count": returned,
        "full_boundary_coverage_item_count": len(retained),
        "items": sorted(retained.values(), key=lambda item: (item["datetime"], item["id"])),
    }


def capture_cross_event_source(
    *, accessed_at_utc: str, run_id: str, git_source_commit: str
) -> dict[str, Any]:
    try:
        accessed = datetime.fromisoformat(accessed_at_utc.replace("Z", "+00:00"))
    except (TypeError, ValueError) as error:
        raise CrossEventSourceError("ACCESSED_AT_UTC_INVALID") from error
    if not accessed_at_utc.endswith("Z") or accessed.tzinfo is None:
        raise CrossEventSourceError("ACCESSED_AT_UTC_REQUIRED")
    if not run_id.strip():
        raise CrossEventSourceError("RUN_ID_REQUIRED")
    if not re.fullmatch(r"[0-9a-f]{40}", git_source_commit):
        raise CrossEventSourceError("GIT_SOURCE_COMMIT_INVALID")
    county_layer, county_layer_url = _request_json(COUNTY_URL, {"f": "json"})
    county_fields = _require_fields(
        county_layer,
        {"GEOID", "NAME", "STATE", "COUNTY", "AREALAND", "AREAWATER"},
        "COUNTY",
    )
    county_query, county_query_url = _request_json(
        f"{COUNTY_URL}/query",
        {
            "where": f"GEOID='{COUNTY_GEOID}'",
            "outFields": "GEOID,NAME,BASENAME,STATE,COUNTY,CENTLAT,CENTLON,AREALAND,AREAWATER",
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "json",
        },
    )
    county_features = county_query.get("features")
    if not isinstance(county_features, list) or len(county_features) != 1:
        raise CrossEventSourceError("COUNTY_FEATURE_COUNT_UNEXPECTED")
    county_geometry = _arcgis_polygon(county_features[0].get("geometry") or {})
    county_attributes = county_features[0].get("attributes") or {}
    if str(county_attributes.get("GEOID")) != COUNTY_GEOID:
        raise CrossEventSourceError("COUNTY_IDENTITY_UNEXPECTED")

    mtbs_service, mtbs_service_url = _request_json(MTBS_URL, {"f": "json"})
    occurrence_layer, occurrence_layer_url = _request_json(
        f"{MTBS_URL}/{MTBS_OCCURRENCE_LAYER}", {"f": "json"}
    )
    occurrence_fields = _require_fields(
        occurrence_layer,
        {"fire_id", "fire_name", "ig_date", "latitude", "longitude", "acres", "map_id"},
        "MTBS_OCCURRENCE",
    )
    occurrence_query, occurrence_query_url = _request_json(
        f"{MTBS_URL}/{MTBS_OCCURRENCE_LAYER}/query",
        {
            "where": "1=1",
            "geometry": ",".join(str(value) for value in SEARCH_ENVELOPE),
            "geometryType": "esriGeometryEnvelope",
            "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "fire_id,fire_name,ig_date,latitude,longitude,acres,irwinid,map_id,map_prog,perim_id,pre_id,post_id,comments",
            "returnGeometry": "false",
            "f": "json",
        },
    )
    occurrence_features = occurrence_query.get("features")
    _require_complete_arcgis_query(occurrence_query, "MTBS_OCCURRENCE")
    if not isinstance(occurrence_features, list) or not occurrence_features:
        raise CrossEventSourceError("MTBS_OCCURRENCE_FEATURES_EMPTY")
    county_occurrences: list[dict[str, Any]] = []
    for feature in occurrence_features:
        attributes = feature.get("attributes") or {}
        longitude = float(attributes["longitude"])
        latitude = float(attributes["latitude"])
        if not _inside_geometry(longitude, latitude, county_geometry):
            continue
        ignition = _date_from_epoch_ms(attributes["ig_date"])
        county_occurrences.append(
            {
                "fire_id": attributes["fire_id"],
                "fire_name": attributes["fire_name"],
                "ignition_date": ignition.date().isoformat(),
                "year": ignition.year,
                "latitude": latitude,
                "longitude": longitude,
                "acres": float(attributes["acres"]),
                "irwinid": attributes.get("irwinid"),
                "map_id": attributes.get("map_id"),
                "map_program": attributes.get("map_prog"),
                "pre_id": attributes.get("pre_id"),
                "post_id": attributes.get("post_id"),
                "perimeter_id": attributes.get("perim_id"),
                "comments": attributes.get("comments"),
            }
        )
    county_occurrences.sort(key=lambda item: (item["ignition_date"], item["fire_id"]), reverse=True)
    fire_ids = [str(item["fire_id"]) for item in county_occurrences]
    if len(fire_ids) != len(set(fire_ids)):
        raise CrossEventSourceError("MTBS_OCCURRENCE_FIRE_ID_DUPLICATE")
    recent_ids = [item["fire_id"] for item in county_occurrences if item["year"] >= MIN_YEAR]
    if not recent_ids:
        raise CrossEventSourceError("NO_RECENT_COUNTY_OCCURRENCES")

    boundary_layer, boundary_layer_url = _request_json(
        f"{MTBS_URL}/{MTBS_BOUNDARY_LAYER}", {"f": "json"}
    )
    boundary_fields = _require_fields(
        boundary_layer,
        {"fire_id", "fire_name", "year", "fire_type", "acres", "asmnt_type", "ig_date"},
        "MTBS_BOUNDARY",
    )
    quoted_ids = ",".join(f"'{value}'" for value in recent_ids)
    boundary_query, boundary_query_url = _request_json(
        f"{MTBS_URL}/{MTBS_BOUNDARY_LAYER}/query",
        {
            "where": f"fire_id IN ({quoted_ids})",
            "outFields": "fire_id,fire_name,year,startmonth,startday,fire_type,acres,irwinid,map_id,map_prog,asmnt_type,ig_date,pre_id,post_id,perim_id,dnbr_offst,dnbr_stddv,nodata_threshold,greenness_threshold,low_threshold,moderate_threshold,high_threshold,comments,latitude,longitude",
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "json",
        },
    )
    boundary_features = boundary_query.get("features")
    _require_complete_arcgis_query(boundary_query, "MTBS_BOUNDARY")
    if not isinstance(boundary_features, list):
        raise CrossEventSourceError("MTBS_BOUNDARY_FEATURES_INVALID")
    boundaries: dict[str, dict[str, Any]] = {}
    for feature in boundary_features:
        attributes = feature.get("attributes") or {}
        fire_id = str(attributes.get("fire_id"))
        geometry = _arcgis_polygon(feature.get("geometry") or {})
        boundaries[fire_id] = {
            "fire_id": fire_id,
            "fire_name": attributes.get("fire_name"),
            "year": int(attributes.get("year")),
            "fire_type": attributes.get("fire_type"),
            "acres": float(attributes.get("acres")),
            "assessment_type": attributes.get("asmnt_type"),
            "ignition_date": str(attributes.get("ig_date")),
            "pre_id": attributes.get("pre_id"),
            "post_id": attributes.get("post_id"),
            "perimeter_id": attributes.get("perim_id"),
            "thresholds": {
                "dnbr_offset": attributes.get("dnbr_offst"),
                "dnbr_standard_deviation": attributes.get("dnbr_stddv"),
                "nodata": attributes.get("nodata_threshold"),
                "greenness": attributes.get("greenness_threshold"),
                "low": attributes.get("low_threshold"),
                "moderate": attributes.get("moderate_threshold"),
                "high": attributes.get("high_threshold"),
            },
            "comments": attributes.get("comments"),
            "geometry": geometry,
            "bbox": _geometry_bbox(geometry),
        }

    collection, collection_url = _request_json(CDSE_COLLECTION_URL)
    if collection.get("id") != "sentinel-2-l2a" or collection.get("stac_version") != "1.1.0":
        raise CrossEventSourceError("STAC_COLLECTION_IDENTITY_UNEXPECTED")
    license_links = [
        link for link in collection.get("links", []) if link.get("rel") == "license"
    ]
    if len(license_links) != 1:
        raise CrossEventSourceError("STAC_COLLECTION_LICENSE_LINK_UNEXPECTED")

    enriched: list[dict[str, Any]] = []
    for occurrence in county_occurrences:
        if occurrence["year"] < MIN_YEAR:
            continue
        boundary = boundaries.get(occurrence["fire_id"])
        item = dict(occurrence)
        item["boundary"] = boundary
        item["boundary_available"] = boundary is not None
        item["pre_stac_eligible"] = bool(
            boundary
            and boundary["fire_type"] == "Wildfire"
            and 1000.0 <= occurrence["acres"] <= MAX_ACRES
        )
        enriched.append(item)
    stac_events = [item for item in enriched if item["pre_stac_eligible"]][:MAX_STAC_EVENTS]
    for event in stac_events:
        ignition = datetime.fromisoformat(event["ignition_date"]).replace(tzinfo=timezone.utc)
        bbox = _expanded_bbox(event["boundary"]["bbox"])
        event["stac_search_bbox"] = bbox
        event["stac_windows"] = [
            _stac_window(
                bbox=bbox,
                start=ignition - timedelta(days=45),
                end=ignition - timedelta(days=1),
                window="pre",
                boundary=event["boundary"]["geometry"],
            ),
            _stac_window(
                bbox=bbox,
                start=ignition + timedelta(days=10),
                end=ignition + timedelta(days=75),
                window="post_initial",
                boundary=event["boundary"]["geometry"],
            ),
            _stac_window(
                bbox=bbox,
                start=ignition + timedelta(days=300),
                end=ignition + timedelta(days=400),
                window="post_extended",
                boundary=event["boundary"]["geometry"],
            ),
        ]

    return {
        "record_id": SOURCE_ID,
        "schema_version": SOURCE_SCHEMA_VERSION,
        "serialization": "UTF-8 JSON with LF canonical line endings",
        "accessed_at_utc": accessed_at_utc,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 357,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": None,
        "aoi_version": AOI_VERSION,
        "target_version": TARGET_VERSION,
        "dataset_version": None,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "baseline_version": None,
        "model_version": None,
        "purpose": "Current official metadata-only cross-event feasibility capture; no provider imagery or label data acquired.",
        "rules": {
            "search_envelope_wgs84": SEARCH_ENVELOPE,
            "county_geoid": COUNTY_GEOID,
            "county_membership_method": "MTBS representative longitude/latitude inside official Census county polygon",
            "minimum_year": MIN_YEAR,
            "fire_type": "Wildfire",
            "minimum_acres": 1000.0,
            "maximum_acres": MAX_ACRES,
            "maximum_stac_events": MAX_STAC_EVENTS,
            "stac_windows_days": {
                "pre": [-45, -1],
                "post_initial": [10, 75],
                "post_extended": [300, 400],
            },
            "single_item_boundary_coverage_required": True,
        },
        "census": {
            "organization": "U.S. Census Bureau",
            "service": "TIGERweb State_County",
            "layer_url": county_layer_url,
            "query_url": county_query_url,
            "service_version": county_layer.get("currentVersion"),
            "fields": county_fields,
            "feature_count": 1,
            "attributes": county_attributes,
            "geometry": county_geometry,
        },
        "mtbs": {
            "organization": "Monitoring Trends in Burn Severity Program (USGS and USDA Forest Service)",
            "service_url": mtbs_service_url,
            "service_version": mtbs_service.get("currentVersion"),
            "copyright_text": mtbs_service.get("copyrightText"),
            "occurrence_layer_url": occurrence_layer_url,
            "boundary_layer_url": boundary_layer_url,
            "occurrence_query_url": occurrence_query_url,
            "boundary_query_url": boundary_query_url,
            "occurrence_fields": occurrence_fields,
            "boundary_fields": boundary_fields,
            "search_envelope_feature_count": len(occurrence_features),
            "deschutes_county_feature_count": len(county_occurrences),
            "recent_county_feature_count": len(enriched),
            "recent_boundary_feature_count": len(boundaries),
        },
        "cdse": {
            "organization": "Copernicus Data Space Ecosystem",
            "catalog": "https://stac.dataspace.copernicus.eu/v1",
            "collection_url": collection_url,
            "collection": collection["id"],
            "stac_version": collection["stac_version"],
            "license": collection.get("license"),
            "license_link": license_links[0],
            "providers": collection.get("providers"),
            "access": "public metadata; authenticated product route recorded but not exercised",
        },
        "events": enriched,
        "source_guidance": [
            {
                "organization": "MTBS Program",
                "url": "https://www.mtbs.gov/mapping-methods",
                "role": "analyst interpretation, source selection, boundary delineation, uncertainty, and distribution method",
            },
            {
                "organization": "MTBS Program",
                "url": "https://www.mtbs.gov/faqs",
                "role": "fire-level products, scale, access, revision, and interpretation limits",
            },
            {
                "organization": "MTBS Program",
                "url": "https://www.mtbs.gov/data-availability",
                "role": "current quarterly production and revision schedule",
            },
            {
                "organization": "Copernicus Data Space Ecosystem",
                "url": "https://documentation.dataspace.copernicus.eu/APIs/STAC.html",
                "role": "current public STAC search behavior and metadata filtering",
            },
            {
                "organization": "Copernicus Data Space Ecosystem",
                "url": "https://dataspace.copernicus.eu/terms-and-conditions",
                "role": "current ecosystem terms and Sentinel data legal-notice precedence",
            },
            {
                "organization": "U.S. Census Bureau",
                "url": "https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2022/TGRSHP2022_TechDoc.pdf",
                "role": "TIGER reproduction and Census source-citation guidance",
            },
            {
                "organization": "U.S. Geological Survey",
                "url": "https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits",
                "role": "USGS public-domain rule and third-party exceptions",
            },
        ],
        "boundaries": {
            "provider_imagery_downloaded": False,
            "raw_provider_bytes_retained": 0,
            "label_pixels_created": 0,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
        },
    }


def write_cross_event_source(
    *,
    output_path: Path,
    accessed_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> Path:
    record = capture_cross_event_source(
        accessed_at_utc=accessed_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
    )
    _write_utf8_lf(output_path, json.dumps(record, indent=2) + "\n")
    return output_path
