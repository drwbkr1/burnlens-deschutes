"""Build deterministic Phase Four context overlays and descriptive observations."""

from __future__ import annotations

from hashlib import sha256
import io
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Iterable

from PIL import Image, ImageDraw, ImageFont


OVERLAY_VERSION = "burnlens-phase-four-overlay-v0.1.0"
SOFTWARE_VERSION = "0.54.0"
RUN_ROOT = Path("runs/phase-four")
RUN_ID_PATTERN = re.compile(
    r"^BL-[0-9]{4}-[0-9]{2}-[0-9]{2}-p4o1-t01-u05-overlay-r[0-9]{3}$"
)
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
GEOSPATIAL_RECORD = Path(
    "records/phase-four/geospatial/"
    "PHASE-FOUR-GEOSPATIAL-RECORD-2026-001.json"
)
GEOSPATIAL_RECORD_SHA256 = (
    "002860f20df5a2441e71e4b5b27dffdc238c0269a67493900d847e9af9b2e5c9"
)
CONTEXT_RECORD = Path(
    "records/phase-four/context/"
    "PHASE-FOUR-CONTEXT-CUSTODY-RECORD-2026-001.json"
)
CONTEXT_RECORD_SHA256 = (
    "1ced1aa1ddf950f4bc70f4217d2d6a5139df82a7bae9a65aa8d88928d65f0547"
)
MTBS_REPORT = Path(
    "samples/reference/phase-two/ward-creek/reference-fitness-v0.1.1/"
    "WARD-CREEK-REFERENCE-FITNESS-2026-002.json"
)
MTBS_REPORT_SHA256 = (
    "f31bc51c64dae60b5a419146f4183b960b8504044f79e7505018a630c47c466d"
)
MTBS_ARCHIVE = Path(
    "downloads/phase-two/raw/ward-creek-mtbs-reference-v0.1.0/"
    "ward-creek-mtbs-reference-delivery-001.zip"
)
MTBS_ARCHIVE_SHA256 = (
    "d94dfb1609c882fdd26119b2be03cea486af1bbb85e4c9607f108f9455f61d18"
)
MTBS_MEMBER = (
    "mtbs/2019/mtbs_or4494912090120190812_10016337/"
    "mtbs_or4494912090120190812_10016337_20190729_20190830_burn_area.shp"
)
U03_RUN = Path(
    "runs/phase-four/BL-2026-07-26-p4o1-t01-u03-geospatial-r003"
)
CONTEXT_ENVELOPE = (657220.0, 4968520.0, 681800.0, 4991800.0)
PATCH_BOUNDS = {
    "WCP-001": (667220.0, 4978520.0, 668500.0, 4979800.0),
    "WCP-002": (670520.0, 4980520.0, 671800.0, 4981800.0),
}
ROAD_ASSETS = [
    (
        "secondary-highway",
        Path(
            "downloads/phase-four/context-custody/tnm/transportation/"
            "layer-30-secondary-highways.geojson"
        ),
    ),
    (
        "local-connecting-road",
        Path(
            "downloads/phase-four/context-custody/tnm/transportation/"
            "layer-31-local-connecting-roads.geojson"
        ),
    ),
    (
        "local-road",
        Path(
            "downloads/phase-four/context-custody/tnm/transportation/"
            "layer-32-local-roads.geojson"
        ),
    ),
]
FACILITY_ASSETS = [
    (
        "cemetery",
        Path(
            "downloads/phase-four/context-custody/tnm/structures/"
            "layer-37-cemeteries.geojson"
        ),
    ),
    (
        "post-office",
        Path(
            "downloads/phase-four/context-custody/tnm/structures/"
            "layer-38-post-offices.geojson"
        ),
    ),
    (
        "fire-ems",
        Path(
            "downloads/phase-four/context-custody/tnm/structures/"
            "layer-51-fire-ems.geojson"
        ),
    ),
    (
        "trailhead",
        Path(
            "downloads/phase-four/context-custody/tnm/structures/"
            "layer-61-trailheads.geojson"
        ),
    ),
]
BLM_ASSET = Path(
    "downloads/phase-four/context-custody/tnm/boundaries/"
    "layer-36-blm.geojson"
)


class PhaseFourOverlayError(RuntimeError):
    """The U05 overlay or descriptive-summary gate failed."""


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PhaseFourOverlayError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise PhaseFourOverlayError(f"JSON object required: {path}")
    return value


def _receipt(path: str, payload: bytes) -> dict[str, Any]:
    return {
        "path": path,
        "bytes": len(payload),
        "sha256": sha256(payload).hexdigest(),
    }


def _property(properties: dict[str, Any], name: str) -> Any:
    matches = [
        value
        for key, value in properties.items()
        if str(key).casefold() == name.casefold()
    ]
    if len(matches) != 1:
        raise PhaseFourOverlayError(f"missing or ambiguous property: {name}")
    return matches[0]


def _source_features(
    root: Path,
    relative: Path,
    *,
    category: str,
) -> list[dict[str, Any]]:
    from pyproj import Transformer
    from shapely.geometry import shape
    from shapely.ops import transform

    value = _read_json(root / relative)
    if value.get("type") != "FeatureCollection":
        raise PhaseFourOverlayError(f"FeatureCollection required: {relative}")
    transformer = Transformer.from_crs(4326, 32610, always_xy=True)
    records: list[dict[str, Any]] = []
    for feature in value.get("features", []):
        properties = feature["properties"]
        geometry_web = shape(feature["geometry"])
        geometry_native = transform(transformer.transform, geometry_web)
        if geometry_native.is_empty or not geometry_native.is_valid:
            raise PhaseFourOverlayError(f"invalid context geometry: {relative}")
        records.append(
            {
                "category": category,
                "object_id": int(_property(properties, "objectid")),
                "name": _property(properties, "name"),
                "source_dataset_id": _property(
                    properties, "source_datasetid"
                ),
                "source_originator": _property(
                    properties, "source_originator"
                ),
                "geometry_native": geometry_native,
            }
        )
    records.sort(key=lambda item: item["object_id"])
    return records


def _load_inputs(root: Path) -> dict[str, Any]:
    from burnlens.phase_four_context_intake import (
        validate_finalized_context_intake,
    )
    import pyogrio
    from shapely import union_all
    from shapely.geometry import box

    exact = [
        (GEOSPATIAL_RECORD, GEOSPATIAL_RECORD_SHA256),
        (CONTEXT_RECORD, CONTEXT_RECORD_SHA256),
        (MTBS_REPORT, MTBS_REPORT_SHA256),
        (MTBS_ARCHIVE, MTBS_ARCHIVE_SHA256),
    ]
    for relative, expected in exact:
        path = root / relative
        if not path.is_file() or _sha256_file(path) != expected:
            raise PhaseFourOverlayError(f"exact input drift: {relative}")
    context = validate_finalized_context_intake(root)
    rbr_path = U03_RUN / "vectors/rbr-accepted-polygons.gpkg"
    geospatial_record = _read_json(root / GEOSPATIAL_RECORD)
    authoritative = geospatial_record["ignored_run_inventory"]["files"][-1]
    if (
        authoritative["path"] != rbr_path.relative_to(U03_RUN).as_posix()
        or _sha256_file(root / rbr_path) != authoritative["sha256"]
    ):
        raise PhaseFourOverlayError("accepted RBR GeoPackage drift")
    rbr = pyogrio.read_dataframe(root / rbr_path, layer="rbr_accepted")
    if rbr.crs.to_string() != "EPSG:32610":
        raise PhaseFourOverlayError("accepted RBR CRS drift")
    accepted = {
        candidate_id: union_all(
            rbr.loc[rbr["candidate_id"] == candidate_id, "geometry"].tolist()
        )
        for candidate_id in PATCH_BOUNDS
    }
    if any(geometry.is_empty or not geometry.is_valid for geometry in accepted.values()):
        raise PhaseFourOverlayError("accepted RBR geometry drift")
    archive = (root / MTBS_ARCHIVE).resolve()
    mtbs = pyogrio.read_dataframe(
        f"/vsizip/{archive.as_posix()}/{MTBS_MEMBER}"
    )
    if (
        len(mtbs) != 1
        or mtbs.crs.to_string() != "EPSG:32610"
        or not bool(mtbs.geometry.is_valid.all())
    ):
        raise PhaseFourOverlayError("exact MTBS boundary drift")
    roads = [
        record
        for category, relative in ROAD_ASSETS
        for record in _source_features(root, relative, category=category)
    ]
    facilities = [
        record
        for category, relative in FACILITY_ASSETS
        for record in _source_features(root, relative, category=category)
    ]
    blm_records = _source_features(
        root,
        BLM_ASSET,
        category="blm-boundary",
    )
    if len(blm_records) != 1:
        raise PhaseFourOverlayError("BLM boundary roster drift")
    return {
        "context_validation": context,
        "accepted": accepted,
        "patches": {
            candidate_id: box(*bounds)
            for candidate_id, bounds in PATCH_BOUNDS.items()
        },
        "roads": roads,
        "facilities": facilities,
        "blm": blm_records[0]["geometry_native"],
        "mtbs": mtbs.geometry.iloc[0],
        "envelope": box(*CONTEXT_ENVELOPE),
    }


def _round_coordinates(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_round_coordinates(item) for item in value]
    if isinstance(value, list):
        return [_round_coordinates(item) for item in value]
    if isinstance(value, float):
        return round(value, 8)
    return value


def _web_geometry(geometry: Any) -> dict[str, Any]:
    from pyproj import Transformer
    from shapely.geometry import mapping
    from shapely.ops import transform

    transformer = Transformer.from_crs(32610, 4326, always_xy=True)
    web = transform(transformer.transform, geometry)
    mapped = mapping(web)
    mapped["coordinates"] = _round_coordinates(mapped["coordinates"])
    return mapped


def _feature_collection(
    features: Iterable[dict[str, Any]],
    *,
    name: str,
    warning: str,
) -> bytes:
    return _json_bytes(
        {
            "type": "FeatureCollection",
            "name": name,
            "features": list(features),
            "warning": warning,
        }
    )


def _native_metrics(inputs: dict[str, Any]) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    for candidate_id in PATCH_BOUNDS:
        accepted = inputs["accepted"][candidate_id]
        patch = inputs["patches"][candidate_id]
        mtbs_overlap = accepted.intersection(inputs["mtbs"]).area
        blm_overlap = accepted.intersection(inputs["blm"]).area
        road_classes: dict[str, Any] = {}
        for category, _relative in ROAD_ASSETS:
            lines = [
                item["geometry_native"]
                for item in inputs["roads"]
                if item["category"] == category
            ]
            intersection_length = sum(
                geometry.intersection(accepted).length for geometry in lines
            )
            nearest = min(geometry.distance(accepted) for geometry in lines)
            road_classes[category] = {
                "feature_count_in_context_package": len(lines),
                "accepted_rbr_intersection_length_m": round(
                    intersection_length, 3
                ),
                "nearest_distance_to_accepted_rbr_m": round(nearest, 1),
            }
        facility_classes: dict[str, Any] = {}
        for category, _relative in FACILITY_ASSETS:
            points = [
                item["geometry_native"]
                for item in inputs["facilities"]
                if item["category"] == category
            ]
            facility_classes[category] = {
                "feature_count_in_context_package": len(points),
                "count_inside_patch": sum(
                    geometry.within(patch) for geometry in points
                ),
                "count_inside_accepted_rbr": sum(
                    geometry.within(accepted) for geometry in points
                ),
                "nearest_distance_to_accepted_rbr_m": round(
                    min(geometry.distance(accepted) for geometry in points),
                    1,
                ),
            }
        area = accepted.area
        metrics[candidate_id] = {
            "patch_area_m2": round(patch.area, 3),
            "accepted_rbr_area_m2": round(area, 3),
            "accepted_rbr_area_ha": round(area / 10000.0, 2),
            "accepted_rbr_patch_fraction_pct": round(
                100.0 * area / patch.area, 2
            ),
            "mtbs_overlap_area_m2": round(mtbs_overlap, 3),
            "mtbs_overlap_area_ha": round(mtbs_overlap / 10000.0, 2),
            "accepted_rbr_inside_mtbs_pct": round(
                100.0 * mtbs_overlap / area, 2
            ),
            "accepted_rbr_outside_mtbs_area_ha": round(
                (area - mtbs_overlap) / 10000.0, 2
            ),
            "blm_overlap_area_m2": round(blm_overlap, 3),
            "blm_overlap_area_ha": round(blm_overlap / 10000.0, 2),
            "accepted_rbr_inside_blm_pct": round(
                100.0 * blm_overlap / area, 2
            ),
            "roads": road_classes,
            "facilities": facility_classes,
        }
    context_roads: dict[str, Any] = {}
    for category, _relative in ROAD_ASSETS:
        lines = [
            item["geometry_native"]
            for item in inputs["roads"]
            if item["category"] == category
        ]
        context_roads[category] = {
            "feature_count": len(lines),
            "clipped_length_km": round(
                sum(
                    geometry.intersection(inputs["envelope"]).length
                    for geometry in lines
                )
                / 1000.0,
                2,
            ),
        }
    return {
        "measurement_crs": "EPSG:32610",
        "distance_units": "meters",
        "length_units": "meters with display kilometers",
        "area_units": "square meters with display hectares",
        "rounding": {
            "area_m2": 3,
            "area_ha": 2,
            "percent": 2,
            "distance_m": 1,
            "length_km": 2,
        },
        "context_envelope": {
            "bounds": list(CONTEXT_ENVELOPE),
            "buffer_m": 10000,
            "road_summary": context_roads,
            "facility_count": len(inputs["facilities"]),
            "blm_feature_count": 1,
        },
        "mtbs_boundary_area_ha": round(inputs["mtbs"].area / 10000.0, 2),
        "patches": metrics,
    }


def _observations(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    first = metrics["patches"]["WCP-001"]
    second = metrics["patches"]["WCP-002"]
    return [
        {
            "observation_id": "P4O1-T01-U05-OBS-001",
            "title": "Burned prototype patch",
            "text": (
                f"Accepted RBR covers {first['accepted_rbr_area_ha']:.2f} ha "
                f"of WCP-001; {first['accepted_rbr_inside_mtbs_pct']:.2f}% "
                "of that footprint overlaps the exact MTBS burned-area "
                "boundary."
            ),
            "interpretation_boundary": (
                "This is bounded spatial agreement with an analyst-interpreted "
                "official-program reference, not field validation or complete-scar accuracy."
            ),
        },
        {
            "observation_id": "P4O1-T01-U05-OBS-002",
            "title": "Background prototype patch",
            "text": (
                f"Accepted RBR covers {second['accepted_rbr_area_ha']:.2f} ha "
                f"or {second['accepted_rbr_patch_fraction_pct']:.2f}% of "
                "WCP-002, with 0.00% overlap with the exact MTBS boundary."
            ),
            "interpretation_boundary": (
                "This full-patch result is visible false-positive-risk evidence "
                "for the baseline; it is not a label metric, prevalence estimate, or generalization claim."
            ),
        },
        {
            "observation_id": "P4O1-T01-U05-OBS-003",
            "title": "Selected road context",
            "text": (
                "No selected TNM road line intersects the accepted RBR "
                "footprint in either patch. The nearest selected secondary "
                f"highway is {first['roads']['secondary-highway']['nearest_distance_to_accepted_rbr_m'] / 1000.0:.2f} km "
                f"from WCP-001 and {second['roads']['secondary-highway']['nearest_distance_to_accepted_rbr_m'] / 1000.0:.2f} km from WCP-002."
            ),
            "interpretation_boundary": (
                "The selected layer roster and frozen envelope limit this observation; "
                "it is not access, closure, routing, or safety guidance."
            ),
        },
        {
            "observation_id": "P4O1-T01-U05-OBS-004",
            "title": "Selected public-facility context",
            "text": (
                "None of the eight selected TNM public-facility points lies "
                "inside either patch or accepted RBR footprint. The nearest "
                f"selected point is {min(value['nearest_distance_to_accepted_rbr_m'] for value in first['facilities'].values()) / 1000.0:.2f} km "
                f"from WCP-001 and {min(value['nearest_distance_to_accepted_rbr_m'] for value in second['facilities'].values()) / 1000.0:.2f} km from WCP-002."
            ),
            "interpretation_boundary": (
                "Absence or distance in this selected public dataset does not establish "
                "facility operation, availability, capacity, or emergency suitability."
            ),
        },
        {
            "observation_id": "P4O1-T01-U05-OBS-005",
            "title": "Selected planning boundary",
            "text": (
                "The selected TNM BLM boundary has zero overlap with both "
                "accepted RBR footprints."
            ),
            "interpretation_boundary": (
                "This generalized planning layer is not a cadastral, survey, "
                "access, ownership, or legal determination."
            ),
        },
    ]


def _context_geojson(inputs: dict[str, Any]) -> dict[str, bytes]:
    envelope = inputs["envelope"]
    road_features = []
    for item in inputs["roads"]:
        clipped = item["geometry_native"].intersection(envelope)
        if clipped.is_empty:
            continue
        road_features.append(
            {
                "type": "Feature",
                "id": f"{item['category']}-{item['object_id']}",
                "geometry": _web_geometry(clipped),
                "properties": {
                    "context_class": item["category"],
                    "source_object_id": item["object_id"],
                    "name": item["name"],
                    "source_dataset_id": item["source_dataset_id"],
                    "source_originator": item["source_originator"],
                    "analytical_status": "official-context",
                },
            }
        )
    facility_features = [
        {
            "type": "Feature",
            "id": f"{item['category']}-{item['object_id']}",
            "geometry": _web_geometry(item["geometry_native"]),
            "properties": {
                "context_class": item["category"],
                "source_object_id": item["object_id"],
                "name": item["name"],
                "source_dataset_id": item["source_dataset_id"],
                "source_originator": item["source_originator"],
                "analytical_status": "official-context",
            },
        }
        for item in inputs["facilities"]
    ]
    blm_clipped = inputs["blm"].intersection(envelope)
    return {
        "context/roads.geojson": _feature_collection(
            road_features,
            name="BurnLens bounded TNM road context",
            warning=(
                "Official public context only. Not access, closure, routing, "
                "tactical, safety, or emergency guidance."
            ),
        ),
        "context/facilities.geojson": _feature_collection(
            facility_features,
            name="BurnLens bounded TNM selected public-facility context",
            warning=(
                "Published selected facility points do not establish current "
                "operation, availability, capacity, or emergency suitability."
            ),
        ),
        "context/blm-boundary.geojson": _feature_collection(
            [
                {
                    "type": "Feature",
                    "id": "tnm-blm-boundary-1",
                    "geometry": _web_geometry(blm_clipped),
                    "properties": {
                        "context_class": "blm-boundary",
                        "analytical_status": "official-context",
                    },
                }
            ],
            name="BurnLens bounded TNM BLM planning context",
            warning=(
                "Generalized planning context only. Not a cadastral, survey, "
                "access, ownership, or legal determination."
            ),
        ),
        "reference/mtbs-ward-creek-boundary.geojson": _feature_collection(
            [
                {
                    "type": "Feature",
                    "id": "mtbs-OR4494912090120190812-10016337",
                    "geometry": _web_geometry(inputs["mtbs"]),
                    "properties": {
                        "event_id": "OR4494912090120190812",
                        "map_id": 10016337,
                        "program": "MTBS",
                        "analytical_status": "official-program-reference",
                    },
                }
            ],
            name="Ward Creek MTBS burned-area boundary reference",
            warning=(
                "Analyst-interpreted remotely sensed reference. Not an "
                "operational incident perimeter, field truth, or endorsement."
            ),
        ),
    }


def _geometry_parts(geometry: Any, family: str) -> list[Any]:
    if geometry.geom_type == family:
        return [geometry]
    if geometry.geom_type == f"Multi{family}":
        return list(geometry.geoms)
    if geometry.geom_type == "GeometryCollection":
        return [
            part
            for part in geometry.geoms
            if part.geom_type in {family, f"Multi{family}"}
        ]
    return []


def _quicklook(inputs: dict[str, Any], metrics: dict[str, Any]) -> bytes:
    canvas = Image.new("RGB", (1600, 1000), "#101820")
    draw = ImageDraw.Draw(canvas)
    title = ImageFont.load_default(size=34)
    body = ImageFont.load_default(size=20)
    small = ImageFont.load_default(size=16)
    draw.text(
        (50, 30),
        "BurnLens Ward Creek - accepted RBR with bounded official context",
        fill="#f5f1e8",
        font=title,
    )
    draw.text(
        (50, 82),
        "Descriptive screening evidence only. Official sources govern their own facts.",
        fill="#f5c56b",
        font=body,
    )
    map_box = (50, 140, 930, 770)
    draw.rectangle(map_box, fill="#17232a", outline="#6e7e86", width=2)
    minx, miny, maxx, maxy = CONTEXT_ENVELOPE

    def point(x: float, y: float, bounds: tuple[int, int, int, int] = map_box) -> tuple[int, int]:
        left, top, right, bottom = bounds
        return (
            int(left + (x - minx) / (maxx - minx) * (right - left)),
            int(bottom - (y - miny) / (maxy - miny) * (bottom - top)),
        )

    for geometry in inputs["accepted"].values():
        for part in _geometry_parts(geometry, "Polygon"):
            polygons = list(part.geoms) if part.geom_type == "MultiPolygon" else [part]
            for polygon in polygons:
                draw.polygon(
                    [point(x, y) for x, y in polygon.exterior.coords],
                    fill="#ff9d42",
                )
    for polygon in _geometry_parts(
        inputs["blm"].intersection(inputs["envelope"]),
        "Polygon",
    ):
        if polygon.geom_type == "MultiPolygon":
            polygons = list(polygon.geoms)
        else:
            polygons = [polygon]
        for part in polygons:
            draw.line(
                [point(x, y) for x, y in part.exterior.coords],
                fill="#68a6c9",
                width=2,
            )
    for item in inputs["roads"]:
        color = {
            "secondary-highway": "#d3c7a3",
            "local-connecting-road": "#8ea1aa",
            "local-road": "#586b75",
        }[item["category"]]
        for part in _geometry_parts(
            item["geometry_native"].intersection(inputs["envelope"]),
            "LineString",
        ):
            if part.geom_type == "MultiLineString":
                lines = list(part.geoms)
            else:
                lines = [part]
            for line in lines:
                draw.line(
                    [point(x, y) for x, y in line.coords],
                    fill=color,
                    width=2,
                )
    for part in _geometry_parts(inputs["mtbs"], "Polygon"):
        polygons = list(part.geoms) if part.geom_type == "MultiPolygon" else [part]
        for polygon in polygons:
            draw.line(
                [point(x, y) for x, y in polygon.exterior.coords],
                fill="#4ed7d1",
                width=4,
            )
    for item in inputs["facilities"]:
        x, y = point(item["geometry_native"].x, item["geometry_native"].y)
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill="#f5c56b")
    for candidate_id, patch in inputs["patches"].items():
        left, bottom, right, top = patch.bounds
        x1, y1 = point(left, top)
        x2, y2 = point(right, bottom)
        draw.rectangle((x1, y1, x2, y2), outline="#ffffff", width=3)
        draw.text((x1 + 5, y1 + 5), candidate_id, fill="#ffffff", font=small)
    draw.text((70, 705), "10 km frozen context envelope", fill="#c7d1d8", font=small)
    draw.text((970, 145), "What the bounded overlay shows", fill="#f5f1e8", font=title)
    y = 205
    for candidate_id in PATCH_BOUNDS:
        item = metrics["patches"][candidate_id]
        draw.rounded_rectangle(
            (970, y, 1545, y + 185),
            radius=12,
            fill="#242f35",
            outline="#58656b",
            width=2,
        )
        draw.text((995, y + 20), candidate_id, fill="#f5f1e8", font=body)
        draw.text(
            (995, y + 58),
            f"RBR area: {item['accepted_rbr_area_ha']:.2f} ha",
            fill="#ffb45f",
            font=body,
        )
        draw.text(
            (995, y + 92),
            f"Inside MTBS: {item['accepted_rbr_inside_mtbs_pct']:.2f}%",
            fill="#4ed7d1",
            font=body,
        )
        nearest = item["roads"]["secondary-highway"][
            "nearest_distance_to_accepted_rbr_m"
        ]
        draw.text(
            (995, y + 126),
            f"Nearest selected secondary highway: {nearest / 1000.0:.2f} km",
            fill="#d3c7a3",
            font=small,
        )
        y += 210
    draw.rounded_rectangle(
        (970, 645, 1545, 770),
        radius=12,
        fill="#322c24",
        outline="#f5c56b",
        width=2,
    )
    draw.text(
        (995, 665),
        "WCP-002 is the owner-approved background patch.",
        fill="#f5f1e8",
        font=body,
    )
    draw.text(
        (995, 704),
        "Its 66.76 ha RBR footprint has 0.00% MTBS overlap.",
        fill="#f5c56b",
        font=small,
    )
    draw.text(
        (995, 735),
        "That visible result is baseline false-positive-risk evidence.",
        fill="#f5c56b",
        font=small,
    )
    draw.rounded_rectangle(
        (50, 820, 1545, 950),
        radius=12,
        fill="#242f35",
        outline="#58656b",
        width=2,
    )
    draw.text(
        (75, 845),
        "No selected road, facility point, or BLM boundary intersects either accepted RBR footprint.",
        fill="#f5f1e8",
        font=body,
    )
    draw.text(
        (75, 885),
        "This is not access, closure, routing, safety, property, legal, tactical, or emergency guidance.",
        fill="#f5c56b",
        font=body,
    )
    draw.text(
        (75, 922),
        "The U-Net remains rejected and is not used for these measurements.",
        fill="#e267c5",
        font=small,
    )
    buffer = io.BytesIO()
    canvas.save(buffer, format="PNG", optimize=False, compress_level=9)
    return buffer.getvalue()


def build_overlay_products(
    *,
    repository_root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    root = repository_root.resolve()
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise PhaseFourOverlayError("run ID does not match U05 contract")
    if not COMMIT_PATTERN.fullmatch(git_source_commit):
        raise PhaseFourOverlayError("git source commit is invalid")
    inputs = _load_inputs(root)
    metrics = _native_metrics(inputs)
    observations = _observations(metrics)
    outputs = _context_geojson(inputs)
    outputs["analysis/OVERLAY-SUMMARY.json"] = _json_bytes(
        {
            "summary_version": OVERLAY_VERSION,
            "generated_at_utc": generated_at_utc,
            "run_id": run_id,
            "state": "accepted-baseline",
            "route": "baseline-primary-with-rejected-model-diagnostic",
            "metrics": metrics,
            "observations": observations,
            "source_precedence": [
                "USGS/USDA Forest Service MTBS governs its official-program reference facts.",
                "USGS The National Map sources govern their road, facility, and planning-context facts.",
                "BurnLens RBR is the accepted analytical output only for this bounded demonstration.",
                "The rejected U-Net is excluded from every U05 measurement."
            ],
            "warning": (
                "Experimental descriptive screening evidence. Not official, "
                "operational, field-validated, endorsed, or suitable for "
                "routing, tactical, property, legal, safety, or emergency decisions."
            ),
        }
    )
    outputs["OVERLAY-QUICKLOOK.png"] = _quicklook(inputs, metrics)
    inventory = [
        _receipt(path, payload)
        for path, payload in sorted(
            outputs.items(), key=lambda item: item[0].casefold()
        )
    ]
    manifest = {
        "overlay_version": OVERLAY_VERSION,
        "overlay_id": "PHASE-FOUR-OVERLAY-2026-001",
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "issue": 570,
        "unit_id": "P4O1-T01-U05",
        "git_source_commit": git_source_commit,
        "software_version_at_execution": SOFTWARE_VERSION,
        "state": "accepted-baseline",
        "route": "baseline-primary-with-rejected-model-diagnostic",
        "inputs": [
            {
                "path": GEOSPATIAL_RECORD.as_posix(),
                "sha256": GEOSPATIAL_RECORD_SHA256,
            },
            {
                "path": CONTEXT_RECORD.as_posix(),
                "sha256": CONTEXT_RECORD_SHA256,
            },
            {
                "path": MTBS_REPORT.as_posix(),
                "sha256": MTBS_REPORT_SHA256,
            },
            {
                "path": MTBS_ARCHIVE.as_posix(),
                "sha256": MTBS_ARCHIVE_SHA256,
                "tracked": False,
            },
        ],
        "measurement_contract": metrics,
        "observation_count": len(observations),
        "output_inventory": inventory,
        "boundaries": {
            "model_accepted": False,
            "model_outperformed_rbr": False,
            "unet_used_for_measurement": False,
            "context_is_label_truth": False,
            "context_is_model_input": False,
            "routing_closure_tactical_property_legal_safety_or_emergency_use": False,
            "phase_3b_created": False,
            "second_experiment_planned": False,
            "interface_complete": False,
            "deployment": False,
        },
        "disposition": "pass-overlay-summary-pending-interface",
        "next_dependency": "P4O1-T01-U06 repository-owned evidence interface",
    }
    outputs["OVERLAY-MANIFEST.json"] = _json_bytes(manifest)
    status = {
        "status_version": OVERLAY_VERSION,
        "run_id": run_id,
        "state": "accepted-baseline",
        "overlay_complete": True,
        "summary_complete": True,
        "interface_complete": False,
        "model_accepted": False,
        "model_outperformed_rbr": False,
        "next_dependency": "P4O1-T01-U06 repository-owned evidence interface",
    }
    outputs["STATUS.json"] = _json_bytes(status)
    return {"manifest": manifest, "outputs": outputs}


def _require_clean_head(root: Path, git_source_commit: str) -> None:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if head != git_source_commit:
        raise PhaseFourOverlayError("git source commit differs from HEAD")
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status:
        raise PhaseFourOverlayError("working tree must be clean before U05")


def _write_new(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with path.open("xb") as stream:
            created = True
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if path.read_bytes() != payload:
            raise PhaseFourOverlayError(f"output readback differs: {path}")
    except Exception:
        if created and path.exists():
            path.unlink()
        raise


def run_overlay_products(
    *,
    repository_root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    root = repository_root.resolve()
    _require_clean_head(root, git_source_commit)
    run_directory = root / RUN_ROOT / run_id
    if run_directory.exists() or run_directory.is_symlink():
        raise PhaseFourOverlayError(f"run already exists: {run_id}")
    run_directory.mkdir(parents=True)
    started = {
        "attempt_version": OVERLAY_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "status": "STARTED",
    }
    _write_new(run_directory / "RUN-STARTED.json", _json_bytes(started))
    try:
        build = build_overlay_products(
            repository_root=root,
            generated_at_utc=generated_at_utc,
            run_id=run_id,
            git_source_commit=git_source_commit,
        )
        for relative, payload in sorted(
            build["outputs"].items(), key=lambda item: item[0].casefold()
        ):
            _write_new(run_directory / relative, payload)
        complete = {
            **started,
            "status": "COMPLETE",
            "state": build["manifest"]["state"],
            "output_count": len(build["outputs"]),
            "manifest_sha256": sha256(
                build["outputs"]["OVERLAY-MANIFEST.json"]
            ).hexdigest(),
        }
        _write_new(run_directory / "RUN-COMPLETE.json", _json_bytes(complete))
        return build
    except Exception as exc:
        try:
            _write_new(
                run_directory / "FAILURE.json",
                _json_bytes(
                    {
                        **started,
                        "status": "FAILED",
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                    }
                ),
            )
        except Exception:
            pass
        raise
