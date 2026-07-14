"""Deterministic Darlene 3 reference validation and modeling-AOI evidence.

The retained NIFC geometry is authoritative incident-reference evidence. BurnLens
uses it only to derive a bounded analysis envelope. It is never a detection,
label, evacuation area, or operational product.
"""

from __future__ import annotations

from hashlib import sha256
from html import escape
from pathlib import Path
import json
import math
import textwrap
from typing import Any, Iterable, Iterator, Sequence

from PIL import Image, ImageDraw, ImageFont


SOURCE_SHA256 = "3d615d4be88f65806399e3733491ab0d95e16ac91ea86b5a00b3ead81ec17abe"
SOURCE_ITEM_ID = "5e72b1699bf74eefb3f3aff6f4ba5511"
SOURCE_ITEM_URL = f"https://www.arcgis.com/home/item.html?id={SOURCE_ITEM_ID}"
SOURCE_SERVICE_URL = (
    "https://services3.arcgis.com/T4QMspbfLg3qTGWY/ArcGIS/rest/services/"
    "WFIGS_Interagency_Perimeters/FeatureServer/0"
)
SOURCE_QUERY_URL = (
    f"{SOURCE_SERVICE_URL}/query?where=OBJECTID%3D36462&outFields="
    "OBJECTID%2Cpoly_SourceOID%2Cpoly_IncidentName%2Cpoly_FeatureCategory%2C"
    "poly_MapMethod%2Cpoly_GISAcres%2Cpoly_Acres_AutoCalc%2Cpoly_PolygonDateTime%2C"
    "poly_CreateDate%2Cpoly_DateCurrent%2Cpoly_IRWINID%2Cpoly_Source%2C"
    "attr_IncidentName%2Cattr_UniqueFireIdentifier%2Cattr_FireDiscoveryDateTime%2C"
    "attr_IncidentSize%2Cattr_POOState%2Cattr_POOCounty%2Cattr_IsValid%2C"
    "attr_IsQuarantined%2Cattr_Source&returnGeometry=true&outSR=4326&f=geojson"
)

EXPECTED_PROPERTIES: dict[str, Any] = {
    "OBJECTID": 36462,
    "poly_IncidentName": "0289 NE DARLENE 3",
    "poly_FeatureCategory": "Wildfire Final Fire Perimeter",
    "poly_MapMethod": "Mixed Methods",
    "poly_IRWINID": "{5FDA24B7-9F5E-4F84-A4DE-DC55020740FA}",
    "poly_Source": "FFP",
    "attr_UniqueFireIdentifier": "2024-ORPRD-000289",
    "attr_POOState": "US-OR",
    "attr_POOCounty": "Deschutes",
    "attr_IsValid": 1,
    "attr_IsQuarantined": 0,
    "attr_Source": "FODR",
}

# Independent response from the same feature query with outSR=32610, checked
# 2026-07-14 UTC. The local projection must reproduce it within 0.10 m.
NIFC_REFERENCE_EXTENT_UTM10N = (
    622_519.472701686,
    4_833_503.35458304,
    629_489.216329493,
    4_837_710.66725407,
)

DISCOVERY_ENVELOPE_WGS84 = (-121.56, 43.61, -121.40, 43.75)
ANALYSIS_CRS = "EPSG:32610"
DISPLAY_CRS = "EPSG:4326"
BUFFER_METERS = 2_000
SNAP_METERS = 1_000
AOI_VERSION = "aoi-darlene3-model-v0.2.0"
REPORT_VERSION = "aoi-evidence-v0.1.0"
WARNING = (
    "Experimental BurnLens CV output. Not official wildfire information. "
    "Not emergency guidance. Not evacuation, routing, tactical, or "
    "incident-command support. Official sources govern."
)

_WGS84_A = 6_378_137.0
_WGS84_F = 1 / 298.257223563
_UTM_K0 = 0.9996
_UTM_FALSE_EASTING = 500_000.0
_UTM_ZONE_10_CENTRAL_MERIDIAN = math.radians(-123.0)


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _coordinate_pairs(value: Sequence[Any]) -> Iterator[tuple[float, float]]:
    if (
        len(value) >= 2
        and isinstance(value[0], (int, float))
        and isinstance(value[1], (int, float))
    ):
        yield float(value[0]), float(value[1])
        return
    for child in value:
        if isinstance(child, (list, tuple)):
            yield from _coordinate_pairs(child)


def _multipolygon_rings(geometry: dict[str, Any]) -> list[list[list[tuple[float, float]]]]:
    if geometry.get("type") != "MultiPolygon":
        raise ValueError("SOURCE_GEOMETRY_NOT_MULTIPOLYGON")
    polygons: list[list[list[tuple[float, float]]]] = []
    for polygon in geometry.get("coordinates", []):
        rings: list[list[tuple[float, float]]] = []
        for ring in polygon:
            points = [(float(point[0]), float(point[1])) for point in ring]
            if len(points) < 4 or points[0] != points[-1]:
                raise ValueError("SOURCE_RING_NOT_CLOSED")
            rings.append(points)
        if not rings:
            raise ValueError("SOURCE_POLYGON_HAS_NO_RINGS")
        polygons.append(rings)
    if not polygons:
        raise ValueError("SOURCE_MULTIPOLYGON_EMPTY")
    return polygons


def load_and_validate_source(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    if not path.is_file():
        raise ValueError("SOURCE_FILE_MISSING")
    if file_sha256(path) != SOURCE_SHA256:
        raise ValueError("SOURCE_CHECKSUM_MISMATCH")
    try:
        collection = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("SOURCE_GEOJSON_INVALID") from exc
    if collection.get("type") != "FeatureCollection":
        raise ValueError("SOURCE_NOT_FEATURE_COLLECTION")
    features = collection.get("features")
    if not isinstance(features, list) or len(features) != 1:
        raise ValueError("SOURCE_FEATURE_COUNT_NOT_ONE")
    feature = features[0]
    properties = feature.get("properties", {})
    mismatches = [
        key for key, expected in EXPECTED_PROPERTIES.items() if properties.get(key) != expected
    ]
    if mismatches:
        raise ValueError("SOURCE_IDENTITY_MISMATCH:" + ",".join(mismatches))
    polygons = _multipolygon_rings(feature.get("geometry", {}))
    coordinate_count = sum(len(ring) for polygon in polygons for ring in polygon)
    if coordinate_count < 100:
        raise ValueError("SOURCE_GEOMETRY_IMPLAUSIBLY_SMALL")
    return collection, feature


def wgs84_to_utm10n(lon: float, lat: float) -> tuple[float, float]:
    """Project WGS 84 longitude/latitude to WGS 84 / UTM zone 10N."""

    if not (-180 <= lon <= 180 and -80 <= lat <= 84):
        raise ValueError("COORDINATE_OUTSIDE_UTM_DOMAIN")
    e2 = _WGS84_F * (2 - _WGS84_F)
    ep2 = e2 / (1 - e2)
    phi = math.radians(lat)
    lam = math.radians(lon)
    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)
    tan_phi = math.tan(phi)
    n = _WGS84_A / math.sqrt(1 - e2 * sin_phi**2)
    t = tan_phi**2
    c = ep2 * cos_phi**2
    a_term = cos_phi * (lam - _UTM_ZONE_10_CENTRAL_MERIDIAN)
    m = _WGS84_A * (
        (1 - e2 / 4 - 3 * e2**2 / 64 - 5 * e2**3 / 256) * phi
        - (3 * e2 / 8 + 3 * e2**2 / 32 + 45 * e2**3 / 1024) * math.sin(2 * phi)
        + (15 * e2**2 / 256 + 45 * e2**3 / 1024) * math.sin(4 * phi)
        - (35 * e2**3 / 3072) * math.sin(6 * phi)
    )
    easting = _UTM_FALSE_EASTING + _UTM_K0 * n * (
        a_term
        + (1 - t + c) * a_term**3 / 6
        + (5 - 18 * t + t**2 + 72 * c - 58 * ep2) * a_term**5 / 120
    )
    northing = _UTM_K0 * (
        m
        + n
        * tan_phi
        * (
            a_term**2 / 2
            + (5 - t + 9 * c + 4 * c**2) * a_term**4 / 24
            + (61 - 58 * t + t**2 + 600 * c - 330 * ep2) * a_term**6 / 720
        )
    )
    return easting, northing


def utm10n_to_wgs84(easting: float, northing: float) -> tuple[float, float]:
    """Invert WGS 84 / UTM zone 10N to WGS 84 longitude/latitude."""

    e2 = _WGS84_F * (2 - _WGS84_F)
    ep2 = e2 / (1 - e2)
    sqrt_one_minus_e2 = math.sqrt(1 - e2)
    e1 = (1 - sqrt_one_minus_e2) / (1 + sqrt_one_minus_e2)
    m = northing / _UTM_K0
    mu = m / (
        _WGS84_A * (1 - e2 / 4 - 3 * e2**2 / 64 - 5 * e2**3 / 256)
    )
    fp = (
        mu
        + (3 * e1 / 2 - 27 * e1**3 / 32) * math.sin(2 * mu)
        + (21 * e1**2 / 16 - 55 * e1**4 / 32) * math.sin(4 * mu)
        + (151 * e1**3 / 96) * math.sin(6 * mu)
        + (1097 * e1**4 / 512) * math.sin(8 * mu)
    )
    sin_fp = math.sin(fp)
    cos_fp = math.cos(fp)
    tan_fp = math.tan(fp)
    c1 = ep2 * cos_fp**2
    t1 = tan_fp**2
    n1 = _WGS84_A / math.sqrt(1 - e2 * sin_fp**2)
    r1 = _WGS84_A * (1 - e2) / (1 - e2 * sin_fp**2) ** 1.5
    d = (easting - _UTM_FALSE_EASTING) / (n1 * _UTM_K0)
    latitude = fp - (n1 * tan_fp / r1) * (
        d**2 / 2
        - (5 + 3 * t1 + 10 * c1 - 4 * c1**2 - 9 * ep2) * d**4 / 24
        + (61 + 90 * t1 + 298 * c1 + 45 * t1**2 - 252 * ep2 - 3 * c1**2)
        * d**6
        / 720
    )
    longitude = _UTM_ZONE_10_CENTRAL_MERIDIAN + (
        d
        - (1 + 2 * t1 + c1) * d**3 / 6
        + (5 - 2 * c1 + 28 * t1 - 3 * c1**2 + 8 * ep2 + 24 * t1**2)
        * d**5
        / 120
    ) / cos_fp
    return math.degrees(longitude), math.degrees(latitude)


def _extent(points: Iterable[tuple[float, float]]) -> tuple[float, float, float, float]:
    values = list(points)
    if not values:
        raise ValueError("NO_COORDINATES")
    xs = [point[0] for point in values]
    ys = [point[1] for point in values]
    return min(xs), min(ys), max(xs), max(ys)


def _round_values(values: Iterable[float], digits: int = 6) -> list[float]:
    return [round(value, digits) for value in values]


def _aoi_extent(source_extent: tuple[float, float, float, float]) -> tuple[int, int, int, int]:
    xmin, ymin, xmax, ymax = source_extent
    return (
        math.floor((xmin - BUFFER_METERS) / SNAP_METERS) * SNAP_METERS,
        math.floor((ymin - BUFFER_METERS) / SNAP_METERS) * SNAP_METERS,
        math.ceil((xmax + BUFFER_METERS) / SNAP_METERS) * SNAP_METERS,
        math.ceil((ymax + BUFFER_METERS) / SNAP_METERS) * SNAP_METERS,
    )


def _rectangle_ring(extent: Sequence[float]) -> list[list[float]]:
    xmin, ymin, xmax, ymax = extent
    return [
        [xmin, ymin],
        [xmax, ymin],
        [xmax, ymax],
        [xmin, ymax],
        [xmin, ymin],
    ]


def _project_polygons(feature: dict[str, Any]) -> list[list[list[tuple[float, float]]]]:
    polygons = _multipolygon_rings(feature["geometry"])
    return [
        [[wgs84_to_utm10n(lon, lat) for lon, lat in ring] for ring in polygon]
        for polygon in polygons
    ]


def build_aoi_evidence(
    source_path: Path,
    *,
    generated_at_utc: str,
    run_id: str,
    source_commit: str,
) -> tuple[dict[str, Any], list[list[list[tuple[float, float]]]]]:
    _, feature = load_and_validate_source(source_path)
    projected_polygons = _project_polygons(feature)
    projected_points = [
        point for polygon in projected_polygons for ring in polygon for point in ring
    ]
    source_extent_utm = _extent(projected_points)
    extent_deltas = [
        abs(actual - expected)
        for actual, expected in zip(source_extent_utm, NIFC_REFERENCE_EXTENT_UTM10N)
    ]
    if max(extent_deltas) > 0.10:
        raise ValueError("PROJECTION_REFERENCE_MISMATCH")
    aoi_extent_utm = _aoi_extent(source_extent_utm)
    axmin, aymin, axmax, aymax = aoi_extent_utm
    if not all(axmin <= x <= axmax and aymin <= y <= aymax for x, y in projected_points):
        raise ValueError("AOI_DOES_NOT_CONTAIN_REFERENCE")

    aoi_corners_wgs84 = [
        utm10n_to_wgs84(x, y)
        for x, y in [(axmin, aymin), (axmax, aymin), (axmax, aymax), (axmin, aymax)]
    ]
    aoi_extent_wgs84 = _extent(aoi_corners_wgs84)
    source_points_wgs84 = list(_coordinate_pairs(feature["geometry"]["coordinates"]))
    source_extent_wgs84 = _extent(source_points_wgs84)
    dxmin, dymin, dxmax, dymax = DISCOVERY_ENVELOPE_WGS84
    source_intersects_discovery = not (
        source_extent_wgs84[2] < dxmin
        or source_extent_wgs84[0] > dxmax
        or source_extent_wgs84[3] < dymin
        or source_extent_wgs84[1] > dymax
    )
    if not source_intersects_discovery:
        raise ValueError("SOURCE_DOES_NOT_INTERSECT_DISCOVERY_ENVELOPE")
    discovery_corners_utm = [
        wgs84_to_utm10n(lon, lat)
        for lon, lat in [(dxmin, dymin), (dxmax, dymin), (dxmax, dymax), (dxmin, dymax)]
    ]
    discovery_extent_utm = _extent(discovery_corners_utm)
    discovery_width_m = discovery_extent_utm[2] - discovery_extent_utm[0]
    discovery_height_m = discovery_extent_utm[3] - discovery_extent_utm[1]
    discovery_area_km2 = discovery_width_m * discovery_height_m / 1_000_000
    width_m = axmax - axmin
    height_m = aymax - aymin
    area_km2 = width_m * height_m / 1_000_000
    reference_acres = float(feature["properties"]["poly_Acres_AutoCalc"])
    reference_area_km2 = reference_acres * 0.0040468564224
    report = {
        "report_id": "AOI-FINAL-2026-001",
        "schema_version": "0.1.0",
        "report_version": REPORT_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 321,
        "branch": "codex/p2o2-t01-final-aoi",
        "git_base_commit": "23affc85ac2c2c6cfd427cb954739e6c7b44fa66",
        "source_commit": source_commit,
        "software_version": "0.2.0",
        "application_version": None,
        "aoi_version": AOI_VERSION,
        "dataset_version": None,
        "label_schema_version": None,
        "baseline_version": None,
        "model_version": None,
        "source": {
            "record_id": "SOURCE-2026-007",
            "organization": "National Interagency Fire Center",
            "dataset": "WFIGS Interagency Fire Perimeters",
            "item_id": SOURCE_ITEM_ID,
            "item_url": SOURCE_ITEM_URL,
            "service_url": SOURCE_SERVICE_URL,
            "query_url": SOURCE_QUERY_URL,
            "object_id": feature["properties"]["OBJECTID"],
            "incident_name": feature["properties"]["poly_IncidentName"],
            "unique_fire_identifier": feature["properties"]["attr_UniqueFireIdentifier"],
            "feature_category": feature["properties"]["poly_FeatureCategory"],
            "map_method": feature["properties"]["poly_MapMethod"],
            "valid": bool(feature["properties"]["attr_IsValid"]),
            "quarantined": bool(feature["properties"]["attr_IsQuarantined"]),
            "source_crs": DISPLAY_CRS,
            "geometry_type": feature["geometry"]["type"],
            "coordinate_count": len(source_points_wgs84),
            "source_sha256": SOURCE_SHA256,
            "source_bytes": source_path.stat().st_size,
            "stored_gis_acres": feature["properties"]["poly_GISAcres"],
            "auto_geodesic_acres": reference_acres,
            "reference_area_km2": round(reference_area_km2, 6),
            "bbox_wgs84": _round_values(source_extent_wgs84),
            "bbox_utm10n": _round_values(source_extent_utm, 3),
            "reference_extent_check_max_delta_m": round(max(extent_deltas), 6),
            "role": "authoritative incident-reference geometry only",
        },
        "derivation": {
            "analysis_crs": ANALYSIS_CRS,
            "display_crs": DISPLAY_CRS,
            "buffer_m": BUFFER_METERS,
            "grid_snap_m": SNAP_METERS,
            "rule": (
                "Project the immutable reference geometry to EPSG:32610; expand its "
                "extent by 2,000 m on every side; snap each boundary outward to the "
                "nearest 1,000 m grid line."
            ),
            "aoi_bbox_utm10n": list(aoi_extent_utm),
            "aoi_bbox_wgs84": _round_values(aoi_extent_wgs84),
            "aoi_polygon_utm10n": {
                "type": "Polygon",
                "coordinates": [_rectangle_ring(aoi_extent_utm)],
            },
            "aoi_polygon_wgs84": {
                "type": "Polygon",
                "coordinates": [[
                    _round_values(point)
                    for point in aoi_corners_wgs84 + [aoi_corners_wgs84[0]]
                ]],
            },
            "width_m": width_m,
            "height_m": height_m,
            "area_km2": area_km2,
            "reference_to_aoi_area_ratio": round(reference_area_km2 / area_km2, 6),
            "supersedes_discovery_aoi": "aoi-darlene3-discovery-v0.1.0",
            "discovery_bbox_wgs84": list(DISCOVERY_ENVELOPE_WGS84),
            "discovery_projected_bbox_utm10n": _round_values(discovery_extent_utm, 3),
            "discovery_projected_area_km2": round(discovery_area_km2, 6),
            "area_reduction_from_discovery_percent": round(
                (1 - area_km2 / discovery_area_km2) * 100, 3
            ),
            "eastward_extension_beyond_discovery_m": round(
                max(0, axmax - discovery_extent_utm[2]), 3
            ),
        },
        "checks": {
            "source_checksum_exact": True,
            "source_identity_exact": True,
            "source_feature_count": 1,
            "source_rings_closed": True,
            "source_valid_and_not_quarantined": True,
            "local_projection_matches_nifc_reference_extent_within_0_10_m": True,
            "aoi_contains_complete_reference_geometry": True,
            "source_intersects_discovery_envelope": source_intersects_discovery,
            "aoi_truthfully_supersedes_discovery_envelope": True,
            "distance_and_area_measured_in_metric_analysis_crs": True,
            "aoi_within_deschutes_county": True,
            "selected_sentinel_metadata_footprint_contains_aoi": True,
            "selected_viirs_pair_metadata_footprints_contain_aoi": True,
        },
        "geography_check": {
            "organization": "U.S. Census Bureau",
            "service": "TIGERweb State_County",
            "service_vintage": "2025-01-01",
            "layer": 9,
            "county_geoid": "41017",
            "county_name": "Deschutes County",
            "query_url": "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/9/query",
            "spatial_relation": "esriSpatialRelWithin",
            "input_geometry": "final AOI WGS84 envelope",
            "result_count": 1,
            "checked_at_utc": "2026-07-14T01:37:00Z",
        },
        "source_stack_coverage": {
            "meaning": "metadata footprint coverage only; no provider asset or fire detection verified",
            "sentinel_2_l2a": {
                "item_id": "S2B_MSIL2A_20240627T184919_N0510_R113_T10TFP_20240627T213644",
                "mgrs_tile": "10TFP",
                "metadata_bbox_wgs84": [
                    -121.76796729995817,
                    43.235600960154144,
                    -120.37335402628887,
                    44.24321330733643,
                ],
                "aoi_contained": True,
                "evidence": "METADATA-2026-001 and ASSET-READINESS-2026-001",
            },
            "noaa_21_viirs_pair": {
                "active_fire_concept_id": "G3944882727-LPCLOUD",
                "geolocation_concept_id": "G4037038741-LPCLOUD",
                "shared_begin_utc": "2024-06-27T19:36:00.000Z",
                "cmr_umm_json_checked_at_utc": "2026-07-14T01:39:00Z",
                "aoi_corner_containment": [True, True, True, True],
                "aoi_contained": True,
                "evidence": "official NASA CMR UMM JSON plus ASSET-READINESS-2026-001",
            },
        },
        "decision": "ACCEPT_FINAL_MODELING_AOI",
        "decision_detail": (
            "The 12 km by 9 km analysis boundary contains the complete cited NIFC "
            "reference perimeter, preserves 2 km of context before outward grid snap, "
            "and supersedes the earlier discovery envelope because the official "
            "reference itself extends farther east."
        ),
        "claims": {
            "permitted": [
                "BurnLens has selected a reproducible modeling AOI from a cited public NIFC final-perimeter reference.",
                "The committed tool regenerates the documented AOI boundary and evidence artifacts.",
            ],
            "prohibited": [
                "The NIFC reference geometry is a BurnLens detection or label.",
                "The BurnLens AOI is an official incident perimeter, evacuation area, hazard zone, or operational product.",
                "Imagery, a dataset, model output, fire detection, or performance result exists.",
            ],
        },
        "limitations": [
            "NIFC describes the source as dynamic, not a legal document, and without warranty of accuracy, reliability, or completeness.",
            "The mixed-method final perimeter is reference evidence only; it is not pixel-perfect segmentation truth.",
            "The rectangular AOI intentionally includes context outside the reference perimeter and says nothing about fire presence there.",
            "The final AOI extends east of and supersedes the discovery-only envelope; the earlier record remains historical metadata-discovery evidence.",
            "Sentinel and VIIRS provider assets remain unacquired pending owner-approved credentials.",
            "No imagery quality, label fitness, or model readiness conclusion follows from AOI acceptance alone.",
            "Catalog-footprint containment confirms coverage metadata only; it does not establish usable pixels or a fire detection.",
        ],
        "source_precedence": "Official sources govern over every BurnLens-derived artifact.",
        "warning": WARNING,
    }
    return report, projected_polygons


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return ImageFont.load_default(size=size)


def _wrapped(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(text, width=width, break_long_words=False))


def _map_point(
    point: tuple[float, float],
    extent: Sequence[float],
    box: tuple[int, int, int, int],
) -> tuple[float, float]:
    xmin, ymin, xmax, ymax = extent
    left, top, right, bottom = box
    x = left + (point[0] - xmin) / (xmax - xmin) * (right - left)
    y = bottom - (point[1] - ymin) / (ymax - ymin) * (bottom - top)
    return x, y


def render_png(
    report: dict[str, Any],
    projected_polygons: list[list[list[tuple[float, float]]]],
    path: Path,
) -> None:
    canvas = Image.new("RGB", (1600, 1200), "#f4f1ea")
    draw = ImageDraw.Draw(canvas)
    ink = "#17211b"
    muted = "#556158"
    border = "#8c968e"
    card = "#ffffff"
    warning = "#fff0ac"
    reference_fill = "#e77948"
    reference_outline = "#7b2f16"
    aoi_fill = "#e4efe7"
    aoi_outline = "#005b46"

    draw.text((80, 52), "PHASE TWO  /  AOI EVIDENCE", fill=muted, font=_font(24))
    draw.multiline_text((80, 98), "One bounded\nmodeling AOI.", fill=ink, font=_font(68), spacing=2)
    draw.text((1020, 112), "DECISION", fill=muted, font=_font(20))
    draw.text((1020, 148), "ACCEPTED", fill=aoi_outline, font=_font(42))
    draw.multiline_text(
        (1020, 205),
        _wrapped("For modeling scope only. No imagery, label, detection, or model output exists.", 38),
        fill=ink,
        font=_font(22),
        spacing=5,
    )

    draw.rounded_rectangle((80, 300, 1520, 405), radius=12, fill=warning, outline=ink, width=3)
    draw.text((110, 322), "EXPERIMENTAL - NOT OFFICIAL WILDFIRE INFORMATION", fill=ink, font=_font(26))
    draw.text(
        (110, 365),
        "Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.",
        fill=ink,
        font=_font(19),
    )

    map_outer = (80, 440, 1050, 1000)
    draw.rounded_rectangle(map_outer, radius=12, fill=card, outline=border, width=2)
    draw.text((110, 465), "ANALYSIS GEOMETRY  /  EPSG:32610", fill=muted, font=_font(21))
    map_box = (140, 535, 990, 925)
    draw.rectangle(map_box, fill=aoi_fill, outline=aoi_outline, width=5)
    aoi_extent = report["derivation"]["aoi_bbox_utm10n"]
    for polygon in projected_polygons:
        if not polygon:
            continue
        outer = [_map_point(point, aoi_extent, map_box) for point in polygon[0]]
        draw.polygon(outer, fill=reference_fill, outline=reference_outline)
        for hole in polygon[1:]:
            hole_points = [_map_point(point, aoi_extent, map_box) for point in hole]
            draw.polygon(hole_points, fill=aoi_fill, outline=reference_outline)

    # North arrow and 2 km scale bar.
    draw.line((935, 565, 935, 625), fill=ink, width=4)
    draw.polygon([(935, 548), (925, 570), (945, 570)], fill=ink)
    draw.text((927, 520), "N", fill=ink, font=_font(18))
    scale_pixels = 2_000 / (aoi_extent[2] - aoi_extent[0]) * (map_box[2] - map_box[0])
    draw.line((165, 890, 165 + scale_pixels, 890), fill=ink, width=5)
    draw.line((165, 880, 165, 900), fill=ink, width=3)
    draw.line((165 + scale_pixels, 880, 165 + scale_pixels, 900), fill=ink, width=3)
    draw.text((165, 855), "2 km", fill=ink, font=_font(18))

    draw.rectangle((140, 950, 170, 970), fill=reference_fill, outline=reference_outline, width=2)
    draw.text((182, 946), "NIFC final-perimeter reference", fill=ink, font=_font(18))
    draw.rectangle((515, 950, 545, 970), fill=aoi_fill, outline=aoi_outline, width=3)
    draw.text((557, 946), "BurnLens modeling AOI", fill=ink, font=_font(18))
    draw.text((810, 946), "No basemap", fill=muted, font=_font(18))

    metrics = [
        (f"{report['derivation']['area_km2']:.0f} km2", "analysis area"),
        (f"{report['derivation']['width_m'] / 1000:.0f} x {report['derivation']['height_m'] / 1000:.0f} km", "analysis extent"),
        (f"{report['derivation']['buffer_m'] / 1000:.0f} km", "minimum context buffer"),
        (f"{report['source']['reference_area_km2']:.2f} km2", "reference area"),
    ]
    for index, (value, label) in enumerate(metrics):
        top = 440 + index * 130
        draw.rounded_rectangle((1090, top, 1520, top + 105), radius=10, fill=card, outline=border, width=2)
        draw.text((1120, top + 17), value, fill=ink, font=_font(34))
        draw.text((1120, top + 67), label, fill=muted, font=_font(18))

    draw.rounded_rectangle((1090, 980, 1520, 1090), radius=10, fill="#d9eadf", outline=aoi_outline, width=2)
    draw.text((1120, 1002), "SOURCE ROLES STAY SEPARATE", fill=aoi_outline, font=_font(18))
    draw.multiline_text(
        (1120, 1038),
        "Official reference  ->  modeling boundary\nNo BurnLens fire result exists.",
        fill=ink,
        font=_font(18),
        spacing=4,
    )

    draw.text(
        (80, 1142),
        f"{report['run_id']}  /  {report['aoi_version']}  /  source {report['source']['source_sha256'][:12]}...",
        fill=muted,
        font=_font(18),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def _svg_path(
    ring: Sequence[tuple[float, float]],
    extent: Sequence[float],
    width: int = 900,
    height: int = 440,
) -> str:
    points = [_map_point(point, extent, (0, 0, width, height)) for point in ring]
    return " ".join(
        ("M" if index == 0 else "L") + f"{x:.2f},{y:.2f}"
        for index, (x, y) in enumerate(points)
    ) + " Z"


def render_html(
    report: dict[str, Any],
    projected_polygons: list[list[list[tuple[float, float]]]],
) -> str:
    extent = report["derivation"]["aoi_bbox_utm10n"]
    paths = []
    for polygon in projected_polygons:
        if not polygon:
            continue
        path_data = " ".join(_svg_path(ring, extent) for ring in polygon)
        paths.append(f'<path d="{path_data}" fill-rule="evenodd"></path>')
    source = report["source"]
    derivation = report["derivation"]
    limitations = "".join(f"<li>{escape(item)}</li>" for item in report["limitations"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BurnLens Darlene 3 modeling AOI evidence</title>
  <style>
    :root {{ color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, sans-serif; background: #f4f1ea; color: #17211b; }}
    body {{ margin: 0; }} main {{ max-width: 76rem; margin: auto; padding: 2rem 1.25rem 4rem; }}
    .eyebrow {{ letter-spacing: .12em; text-transform: uppercase; font-size: .78rem; font-weight: 800; color: #556158; }}
    h1 {{ font-size: clamp(2.4rem, 7vw, 5.7rem); line-height: .92; max-width: 10ch; margin: .4rem 0 1rem; }}
    .warning, .decision {{ border: 2px solid #17211b; padding: 1rem; margin: 1rem 0; box-shadow: .35rem .35rem 0 #17211b; }}
    .warning {{ background: #fff0ac; }} .decision {{ background: #d9eadf; }}
    .layout {{ display: grid; grid-template-columns: minmax(0, 2fr) minmax(15rem, 1fr); gap: 1.25rem; margin-top: 2rem; }}
    .card {{ background: white; border: 1px solid #9aa19b; padding: 1rem; }}
    svg {{ display: block; width: 100%; height: auto; background: #e4efe7; border: 4px solid #005b46; }}
    svg path {{ fill: #e77948; stroke: #7b2f16; stroke-width: 1.5; vector-effect: non-scaling-stroke; }}
    .legend {{ display: flex; flex-wrap: wrap; gap: 1rem; margin-top: .75rem; }}
    .swatch {{ display: inline-block; width: 1.5rem; height: 1rem; margin-right: .35rem; vertical-align: middle; border: 2px solid; }}
    .reference {{ background: #e77948; border-color: #7b2f16; }} .aoi {{ background: #e4efe7; border-color: #005b46; }}
    .metrics {{ display: grid; gap: .75rem; }} .metric {{ display: block; font-size: 2rem; font-weight: 850; }}
    table {{ border-collapse: collapse; width: 100%; background: white; margin: 1rem 0 2rem; }}
    th, td {{ border: 1px solid #9aa19b; padding: .7rem; text-align: left; vertical-align: top; }} th {{ background: #dde5df; }}
    code {{ overflow-wrap: anywhere; }} a {{ color: #005b46; }}
    footer {{ border-top: 1px solid #9aa19b; margin-top: 2rem; padding-top: 1rem; color: #4d5750; }}
    @media (max-width: 48rem) {{ .layout {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body><main>
  <p class="eyebrow">Phase Two / final modeling AOI / {escape(report['report_version'])}</p>
  <h1>One bounded modeling AOI.</h1>
  <p class="warning"><strong>Use boundary:</strong> {escape(report['warning'])}</p>
  <section class="decision" aria-labelledby="decision-heading">
    <h2 id="decision-heading">Accepted for modeling scope only</h2>
    <p>{escape(report['decision_detail'])}</p>
    <p><strong>No imagery, label, detection, dataset, baseline, or model output exists.</strong></p>
  </section>
  <div class="layout">
    <section class="card" aria-labelledby="map-heading">
      <h2 id="map-heading">Analysis geometry</h2>
      <svg viewBox="0 0 900 440" role="img" aria-labelledby="map-title map-desc">
        <title id="map-title">Darlene 3 reference geometry inside the BurnLens modeling AOI</title>
        <desc id="map-desc">An orange NIFC final-perimeter reference lies fully within a green twelve-by-nine-kilometer rectangular BurnLens modeling boundary. No basemap or model output is shown.</desc>
        {''.join(paths)}
      </svg>
      <div class="legend">
        <span><span class="swatch reference"></span>NIFC final-perimeter reference</span>
        <span><span class="swatch aoi"></span>BurnLens modeling AOI</span>
        <span>No basemap</span>
      </div>
    </section>
    <aside class="metrics" aria-label="AOI metrics">
      <div class="card"><span class="metric">{derivation['area_km2']:.0f} km2</span>analysis area</div>
      <div class="card"><span class="metric">{derivation['width_m'] / 1000:.0f} x {derivation['height_m'] / 1000:.0f} km</span>analysis extent</div>
      <div class="card"><span class="metric">{derivation['buffer_m'] / 1000:.0f} km</span>minimum context buffer</div>
      <div class="card"><span class="metric">{source['reference_area_km2']:.2f} km2</span>reference area</div>
    </aside>
  </div>
  <section aria-labelledby="method-heading">
    <h2 id="method-heading">Deterministic derivation</h2>
    <p>{escape(derivation['rule'])}</p>
    <table>
      <tbody>
        <tr><th scope="row">Analysis CRS</th><td><code>{escape(derivation['analysis_crs'])}</code>, meters</td></tr>
        <tr><th scope="row">AOI extent</th><td><code>{escape(str(derivation['aoi_bbox_utm10n']))}</code></td></tr>
        <tr><th scope="row">Reference identity</th><td><code>{escape(source['unique_fire_identifier'])}</code>; object {source['object_id']}; {escape(source['feature_category'])}; {escape(source['map_method'])}</td></tr>
        <tr><th scope="row">Containment</th><td>Complete reference geometry contained.</td></tr>
        <tr><th scope="row">Discovery relationship</th><td>Supersedes <code>AOI-2026-001</code>; {derivation['area_reduction_from_discovery_percent']:.1f}% smaller by projected bounding-area comparison while extending {derivation['eastward_extension_beyond_discovery_m'] / 1000:.2f} km farther east to avoid clipping the official reference.</td></tr>
        <tr><th scope="row">Geography</th><td>Official Census TIGERweb check returns the AOI envelope within Deschutes County, <code>GEOID 41017</code>.</td></tr>
        <tr><th scope="row">Source-stack coverage</th><td>Selected Sentinel-2 and paired NOAA-21 VIIRS metadata footprints contain the AOI. This is coverage evidence only, not pixel or detection evidence.</td></tr>
      </tbody>
    </table>
  </section>
  <section aria-labelledby="roles-heading">
    <h2 id="roles-heading">Source roles and limitations</h2>
    <p>The NIFC geometry remains authoritative incident-reference evidence. The BurnLens rectangle is a lower-priority experimental analysis boundary, not wildfire information.</p>
    <ul>{limitations}</ul>
  </section>
  <section aria-labelledby="trace-heading">
    <h2 id="trace-heading">Traceability</h2>
    <dl>
      <dt>Run ID</dt><dd><code>{escape(report['run_id'])}</code></dd>
      <dt>AOI version</dt><dd><code>{escape(report['aoi_version'])}</code></dd>
      <dt>Source commit</dt><dd><code>{escape(report['source_commit'])}</code></dd>
      <dt>Source checksum</dt><dd><code>{escape(source['source_sha256'])}</code></dd>
      <dt>Dataset / label schema / model</dt><dd>Not created</dd>
    </dl>
    <p><a href="{escape(source['item_url'])}">NIFC ArcGIS item</a> / <a href="{escape(source['query_url'])}">exact source query</a></p>
  </section>
  <footer>{escape(report['source_precedence'])} Generated {escape(report['generated_at_utc'])}.</footer>
</main></body></html>
"""


def write_outputs(
    report: dict[str, Any],
    projected_polygons: list[list[list[tuple[float, float]]]],
    *,
    json_path: Path,
    html_path: Path,
    png_path: Path,
) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    html_path.write_text(render_html(report, projected_polygons), encoding="utf-8")
    render_png(report, projected_polygons, png_path)
