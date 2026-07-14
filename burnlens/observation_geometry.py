"""Compare bounded NOAA-21 fire observations without manufacturing labels.

The checkpoint queries the official NASA CMR inventory, registers the exact
candidate files in ignored local storage, reads provider sparse fire records,
and renders an uncertainty-preserving geometry decision.  It never expands a
375 m thermal-anomaly record, a point, or a later perimeter into 10--20 m
segmentation truth.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from html import escape
import json
import math
from pathlib import Path
import re
from statistics import median
from typing import Any, Callable, Iterable
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

import h5py
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from rasterio.warp import transform, transform_geom

from .paired_intake import (
    AssetContract,
    inspect_asset,
    promote_quarantine,
    validate_asset_contracts,
    verify_registered_package,
)
from .provider_acquisition import (
    AcquisitionError,
    ProviderCredentials,
    _open_json,
    _validate_working_entries,
    build_earthdata_opener,
    stream_asset,
)
from .source_inspection import _scalar, _short_input_names, point_in_geometry


SOFTWARE_VERSION = "0.5.0"
REPORT_ID = "OBSERVATION-GEOMETRY-2026-001"
REPORT_VERSION = "observation-geometry-v0.1.0"
REPORT_SCHEMA_VERSION = "0.1.0"
PACKAGE_ID = "darlene3-vj214img-observation-screen-v0.1.0"
CONTRACT_VERSION = "observation-screen-contract-v0.1.0"
COLLECTION_CONCEPT_ID = "C2831626262-LPCLOUD"
CMR_GRANULE_URL = "https://cmr.earthdata.nasa.gov/search/granules.umm_json"
CMR_COLLECTION = "VJ214IMG.002"
GEOLOCATION_COLLECTION = "VJ203MODLL.021"
AOI_VERSION = "aoi-darlene3-model-v0.2.0"
WINDOW_START = "2024-06-25T00:00:00Z"
WINDOW_END = "2024-07-01T23:59:59Z"
EVENT_START = "2024-06-25T20:00:00Z"
SENTINEL_OBSERVATION = "2024-06-27T18:49:19.024Z"
BASELINE_NATIVE_ID = "VJ214IMG.A2024179.1936.002.2025284191612"
GEOMETRY_MARGIN_DEGREES = 10.0
USER_AGENT = "BurnLens/0.5.0 experimental-research"
WARNING = (
    "Experimental BurnLens CV evidence. Not official wildfire information. "
    "Not emergency guidance. Not evacuation, routing, tactical, or "
    "incident-command support. Official sources govern."
)


class ObservationGeometryError(RuntimeError):
    """A bounded geometry-screen failure safe to expose without secrets."""


def _parse_time(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ObservationGeometryError("timestamp must include UTC offset")
    return parsed.astimezone(timezone.utc)


def _format_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return ImageFont.load_default(size=size)


def _cmr_url(params: list[tuple[str, str]]) -> str:
    return f"{CMR_GRANULE_URL}?{urlencode(params)}"


def inventory_query_url(aoi_bbox_wgs84: list[float]) -> str:
    return _cmr_url(
        [
            ("collection_concept_id", COLLECTION_CONCEPT_ID),
            ("temporal", f"{WINDOW_START},{WINDOW_END}"),
            ("bounding_box", ",".join(str(value) for value in aoi_bbox_wgs84)),
            ("page_size", "200"),
            ("sort_key[]", "start_date"),
            ("sort_key[]", "granule_ur"),
        ]
    )


def _distribution(umm: dict[str, Any]) -> tuple[int, str | None]:
    records = (umm.get("DataGranule") or {}).get("ArchiveAndDistributionInformation") or []
    if not isinstance(records, list) or not records or not isinstance(records[0], dict):
        raise ObservationGeometryError("CMR_SIZE_METADATA_MISSING")
    record = records[0]
    if record.get("SizeUnit") != "MB":
        raise ObservationGeometryError("CMR_SIZE_UNIT_UNEXPECTED")
    try:
        size_bytes = round(float(record["Size"]) * 1024 * 1024)
    except (KeyError, TypeError, ValueError):
        raise ObservationGeometryError("CMR_SIZE_METADATA_INVALID") from None
    checksum = record.get("Checksum")
    return size_bytes, checksum if isinstance(checksum, str) else None


def _stable_data_url(umm: dict[str, Any], suffix: str) -> str:
    candidates: list[str] = []
    for item in umm.get("RelatedUrls") or []:
        if not isinstance(item, dict) or item.get("Type") != "GET DATA":
            continue
        value = item.get("URL")
        if not isinstance(value, str):
            continue
        parts = urlsplit(value)
        if (
            parts.scheme == "https"
            and parts.hostname == "data.lpdaac.earthdatacloud.nasa.gov"
            and not parts.query
            and not parts.fragment
            and parts.path.endswith(suffix)
        ):
            candidates.append(value)
    if len(candidates) != 1:
        raise ObservationGeometryError("CMR_STABLE_DATA_URL_COUNT_MISMATCH")
    return candidates[0]


def _footprint(umm: dict[str, Any]) -> list[list[float]]:
    polygons = (
        (((umm.get("SpatialExtent") or {}).get("HorizontalSpatialDomain") or {}).get("Geometry") or {})
        .get("GPolygons")
    )
    if not isinstance(polygons, list) or len(polygons) != 1:
        raise ObservationGeometryError("CMR_FOOTPRINT_COUNT_MISMATCH")
    points = ((polygons[0].get("Boundary") or {}).get("Points") or [])
    result = [
        [round(float(item["Longitude"]), 7), round(float(item["Latitude"]), 7)]
        for item in points
        if isinstance(item, dict)
    ]
    if len(result) < 4 or result[0] != result[-1]:
        raise ObservationGeometryError("CMR_FOOTPRINT_INVALID")
    return result


def _point_line_distance(point: tuple[float, float], start: tuple[float, float], end: tuple[float, float]) -> float:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    denominator = dx * dx + dy * dy
    if denominator == 0:
        return math.dist(point, start)
    return abs(dy * point[0] - dx * point[1] + end[0] * start[1] - end[1] * start[0]) / math.sqrt(
        denominator
    )


def footprint_centrality_proxy(points: list[list[float]], aoi_bbox_wgs84: list[float]) -> float:
    """Return a metadata-only 0=edge, 0.5=center cross-track proxy."""

    ring = points[:-1]
    if len(ring) != 4:
        raise ObservationGeometryError("CMR_FOOTPRINT_NOT_QUADRILATERAL")
    lon0 = (aoi_bbox_wgs84[0] + aoi_bbox_wgs84[2]) / 2
    lat0 = (aoi_bbox_wgs84[1] + aoi_bbox_wgs84[3]) / 2
    cosine = math.cos(math.radians(lat0))

    def local(point: list[float]) -> tuple[float, float]:
        return ((point[0] - lon0) * cosine, point[1] - lat0)

    local_ring = [local(item) for item in ring]
    edge_lengths = [math.dist(local_ring[index], local_ring[(index + 1) % 4]) for index in range(4)]
    opposing_pairs = ((0, 2), (1, 3))
    long_edges = max(opposing_pairs, key=lambda pair: edge_lengths[pair[0]] + edge_lengths[pair[1]])
    distances = [
        _point_line_distance((0.0, 0.0), local_ring[index], local_ring[(index + 1) % 4])
        for index in long_edges
    ]
    total = sum(distances)
    return round(min(distances) / total, 6) if total else 0.0


def _normalize_granule(item: dict[str, Any], aoi_bbox_wgs84: list[float]) -> dict[str, Any]:
    meta = item.get("meta") or {}
    umm = item.get("umm") or {}
    native_id = umm.get("GranuleUR")
    if not isinstance(native_id, str) or not native_id.startswith("VJ214IMG."):
        raise ObservationGeometryError("CMR_NATIVE_ID_INVALID")
    match = re.fullmatch(r"VJ214IMG\.(A\d{7}\.\d{4})\.002\.\d{13}", native_id)
    if match is None:
        raise ObservationGeometryError("CMR_NATIVE_ID_PATTERN_MISMATCH")
    temporal = (umm.get("TemporalExtent") or {}).get("RangeDateTime") or {}
    begin = temporal.get("BeginningDateTime")
    end = temporal.get("EndingDateTime")
    if not isinstance(begin, str) or not isinstance(end, str):
        raise ObservationGeometryError("CMR_TEMPORAL_EXTENT_MISSING")
    size_bytes, provider_checksum = _distribution(umm)
    if provider_checksum is not None:
        raise ObservationGeometryError("CMR_UNEXPECTED_PROVIDER_CHECKSUM")
    footprint = _footprint(umm)
    route = _stable_data_url(umm, ".nc")
    filename = f"{native_id}.nc"
    if not route.endswith(f"/{filename}"):
        raise ObservationGeometryError("CMR_ROUTE_NATIVE_ID_MISMATCH")
    begin_time = _parse_time(begin)
    event_start = _parse_time(EVENT_START)
    sentinel = _parse_time(SENTINEL_OBSERVATION)
    return {
        "concept_id": meta.get("concept-id"),
        "native_id": native_id,
        "filename": filename,
        "pair_token": match.group(1),
        "begin": _format_time(begin_time),
        "end": _format_time(_parse_time(end)),
        "size_bytes": size_bytes,
        "revision_date": meta.get("revision-date"),
        "footprint_wgs84": footprint,
        "metadata_cross_track_centrality_proxy": footprint_centrality_proxy(footprint, aoi_bbox_wgs84),
        "seconds_from_approximate_event_start": round((begin_time - event_start).total_seconds(), 3),
        "seconds_from_sentinel_observation": round((begin_time - sentinel).total_seconds(), 3),
        "pre_event_reference_only": begin_time < event_start,
        "stable_route": route,
    }


def normalize_inventory(payload: dict[str, Any], aoi_bbox_wgs84: list[float]) -> list[dict[str, Any]]:
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        raise ObservationGeometryError("CMR_INVENTORY_EMPTY")
    candidates = [_normalize_granule(item, aoi_bbox_wgs84) for item in items if isinstance(item, dict)]
    candidates.sort(key=lambda item: (item["begin"], item["native_id"]))
    if len(candidates) != len(items):
        raise ObservationGeometryError("CMR_INVENTORY_ITEM_INVALID")
    if len({item["concept_id"] for item in candidates}) != len(candidates):
        raise ObservationGeometryError("CMR_DUPLICATE_CONCEPT_ID")
    if len({item["native_id"] for item in candidates}) != len(candidates):
        raise ObservationGeometryError("CMR_DUPLICATE_NATIVE_ID")
    ranked = sorted(
        range(len(candidates)),
        key=lambda index: (
            candidates[index]["pre_event_reference_only"],
            -candidates[index]["metadata_cross_track_centrality_proxy"],
            abs(candidates[index]["seconds_from_sentinel_observation"]),
            candidates[index]["native_id"],
        ),
    )
    for rank, index in enumerate(ranked, start=1):
        candidates[index]["metadata_rank"] = rank
    return candidates


def fetch_inventory(
    aoi_bbox_wgs84: list[float],
    *,
    urlopen_fn: Callable[..., Any] = urlopen,
) -> tuple[list[dict[str, Any]], str]:
    url = inventory_query_url(aoi_bbox_wgs84)
    payload = _open_json(
        Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT}),
        urlopen_fn=urlopen_fn,
    )
    return normalize_inventory(payload, aoi_bbox_wgs84), url


def _fire_contract(candidate: dict[str, Any]) -> AssetContract:
    return AssetContract(
        role=f"viirs-active-fire:{candidate['pair_token']}",
        provider="NASA LP DAAC",
        source_record_id="SOURCE-2026-005",
        provider_id=candidate["concept_id"],
        native_id=candidate["native_id"],
        expected_filename=candidate["filename"],
        stable_route=candidate["stable_route"],
        expected_size_bytes=candidate["size_bytes"],
        container="hdf5",
        package_id=PACKAGE_ID,
        native_pair_token=candidate["pair_token"],
    )


def _companion_query_url(selected: dict[str, Any]) -> str:
    return _cmr_url(
        [
            ("short_name", "VJ203MODLL"),
            ("version", "021"),
            ("temporal", f"{selected['begin']},{selected['end']}"),
            ("page_size", "20"),
            ("sort_key[]", "granule_ur"),
        ]
    )


def fetch_companion_contract(
    selected: dict[str, Any],
    *,
    urlopen_fn: Callable[..., Any] = urlopen,
) -> tuple[AssetContract, dict[str, Any], str]:
    url = _companion_query_url(selected)
    payload = _open_json(
        Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT}),
        urlopen_fn=urlopen_fn,
    )
    matches: list[dict[str, Any]] = []
    for item in payload.get("items") or []:
        if not isinstance(item, dict):
            continue
        meta = item.get("meta") or {}
        umm = item.get("umm") or {}
        native_id = umm.get("GranuleUR")
        if not isinstance(native_id, str) or f".{selected['pair_token']}.021." not in native_id:
            continue
        size_bytes, provider_checksum = _distribution(umm)
        if provider_checksum is not None:
            raise ObservationGeometryError("CMR_UNEXPECTED_COMPANION_CHECKSUM")
        suffix = ".h5" if any(
            isinstance(url_item, dict)
            and isinstance(url_item.get("URL"), str)
            and url_item["URL"].endswith(".h5")
            for url_item in umm.get("RelatedUrls") or []
        ) else ".nc"
        route = _stable_data_url(umm, suffix)
        matches.append(
            {
                "concept_id": meta.get("concept-id"),
                "native_id": native_id,
                "filename": f"{native_id}{suffix}",
                "size_bytes": size_bytes,
                "revision_date": meta.get("revision-date"),
                "stable_route": route,
            }
        )
    if len(matches) != 1:
        raise ObservationGeometryError("CMR_EXACT_COMPANION_COUNT_MISMATCH")
    record = matches[0]
    contract = AssetContract(
        role=f"viirs-geolocation:{selected['pair_token']}",
        provider="NASA LP DAAC",
        source_record_id="SOURCE-2026-006",
        provider_id=record["concept_id"],
        native_id=record["native_id"],
        expected_filename=record["filename"],
        stable_route=record["stable_route"],
        expected_size_bytes=record["size_bytes"],
        container="hdf5",
        package_id=PACKAGE_ID,
        native_pair_token=selected["pair_token"],
    )
    return contract, {key: value for key, value in record.items() if key != "stable_route"}, url


def validate_screen_contracts(contracts: Iterable[AssetContract]) -> list[str]:
    items = list(contracts)
    reasons = validate_asset_contracts(items)
    fire = [item for item in items if item.role.startswith("viirs-active-fire:")]
    geo = [item for item in items if item.role.startswith("viirs-geolocation:")]
    if not fire:
        reasons.append("SCREEN_REQUIRES_FIRE_CANDIDATES")
    if len(geo) > 1:
        reasons.append("SCREEN_ALLOWS_AT_MOST_ONE_GEOLOCATION")
    if len(geo) == 1 and geo[0].native_pair_token not in {item.native_pair_token for item in fire}:
        reasons.append("SCREEN_GEOLOCATION_PAIR_TOKEN_MISMATCH")
    if any(item.native_pair_token and item.native_pair_token not in item.native_id for item in items):
        reasons.append("SCREEN_NATIVE_ID_TOKEN_MISMATCH")
    return reasons


def _inspect_fire_product(
    path: Path,
    *,
    aoi_bbox_utm: list[float],
    reference_geometry_utm: dict[str, Any],
) -> dict[str, Any]:
    required = (
        "FP_line",
        "FP_sample",
        "FP_latitude",
        "FP_longitude",
        "FP_confidence",
        "FP_power",
        "FP_ViewZenAng",
        "FP_SolZenAng",
        "FP_AdjCloud",
        "FP_AdjWater",
        "fire mask",
        "algorithm QA",
    )
    with h5py.File(path, "r") as source:
        missing = [name for name in required if name not in source]
        if missing:
            raise ObservationGeometryError(f"VIIRS_FIRE_DATASET_MISSING:{','.join(missing)}")
        fire_shape = source["fire mask"].shape
        qa_shape = source["algorithm QA"].shape
        if fire_shape != qa_shape or len(fire_shape) != 2 or fire_shape[0] not in (6432, 6464) or fire_shape[1] != 6400:
            raise ObservationGeometryError("VIIRS_FIRE_GRID_SHAPE_UNEXPECTED")
        fire_count = int(_scalar(source.attrs["FirePix"]))
        vectors = {
            name: source[name][:]
            for name in required
            if name not in ("fire mask", "algorithm QA")
        }
        if any(len(values) != fire_count for values in vectors.values()):
            raise ObservationGeometryError("VIIRS_SPARSE_VECTOR_COUNT_MISMATCH")
        lines = vectors["FP_line"].astype(int)
        samples = vectors["FP_sample"].astype(int)
        if (
            np.any(lines < 0)
            or np.any(lines >= fire_shape[0])
            or np.any(samples < 0)
            or np.any(samples >= fire_shape[1])
        ):
            raise ObservationGeometryError("VIIRS_SPARSE_INDEX_OUT_OF_RANGE")
        mask_values = np.array(
            [source["fire mask"][line, sample] for line, sample in zip(lines, samples)],
            dtype=np.uint8,
        )
        qa_values = np.array(
            [source["algorithm QA"][line, sample] for line, sample in zip(lines, samples)],
            dtype=np.uint32,
        )
        if not np.array_equal(mask_values, vectors["FP_confidence"]):
            raise ObservationGeometryError("VIIRS_CONFIDENCE_MASK_MISMATCH")
        input_pointer = _scalar(source.attrs["InputPointer"])
        attributes = {
            name: _scalar(source.attrs[name])
            for name in (
                "LocalGranuleID",
                "ShortName",
                "VersionID",
                "RangeBeginningDate",
                "RangeBeginningTime",
                "RangeEndingDate",
                "RangeEndingTime",
                "DayNightFlag",
            )
        }

    longitudes = vectors["FP_longitude"].astype(float)
    latitudes = vectors["FP_latitude"].astype(float)
    xs, ys = transform("EPSG:4326", "EPSG:32610", longitudes.tolist(), latitudes.tolist())
    west, south, east, north = aoi_bbox_utm
    records: list[dict[str, Any]] = []
    for index, (x, y) in enumerate(zip(xs, ys)):
        if not (west <= x <= east and south <= y <= north):
            continue
        confidence_class = int(vectors["FP_confidence"][index])
        if confidence_class not in (7, 8, 9):
            raise ObservationGeometryError("VIIRS_SPARSE_CONFIDENCE_UNEXPECTED")
        residual_bowtie = bool((int(qa_values[index]) >> 22) & 1)
        bad_geolocation = bool((int(qa_values[index]) >> 5) & 1)
        records.append(
            {
                "sparse_index": index,
                "line": int(lines[index]),
                "sample": int(samples[index]),
                "latitude": round(float(latitudes[index]), 7),
                "longitude": round(float(longitudes[index]), 7),
                "confidence_class": confidence_class,
                "confidence_name": {7: "low", 8: "nominal", 9: "high"}[confidence_class],
                "fire_radiative_power_mw": round(float(vectors["FP_power"][index]), 6),
                "view_zenith_degrees": round(float(vectors["FP_ViewZenAng"][index]), 4),
                "solar_zenith_degrees": round(float(vectors["FP_SolZenAng"][index]), 4),
                "adjacent_cloud_pixels": int(vectors["FP_AdjCloud"][index]),
                "adjacent_water_pixels": int(vectors["FP_AdjWater"][index]),
                "qa_geolocation_non_nominal": bad_geolocation,
                "qa_residual_bowtie": residual_bowtie,
                "inside_nifc_final_reference": point_in_geometry(float(x), float(y), reference_geometry_utm),
                "reference_qualified": confidence_class >= 8 and not residual_bowtie and not bad_geolocation,
            }
        )

    confidence = Counter(item["confidence_name"] for item in records)
    qualified = [item for item in records if item["reference_qualified"]]
    view_angles = [abs(item["view_zenith_degrees"]) for item in qualified]
    return {
        "product_filename": path.name,
        "attributes": attributes,
        "upstream_input_filenames": _short_input_names(str(input_pointer)),
        "fire_mask_shape": list(fire_shape),
        "global_fire_record_count": fire_count,
        "aoi_fire_record_count": len(records),
        "aoi_confidence_counts": {name: confidence.get(name, 0) for name in ("low", "nominal", "high")},
        "aoi_residual_bowtie_count": sum(item["qa_residual_bowtie"] for item in records),
        "aoi_bad_geolocation_qa_count": sum(item["qa_geolocation_non_nominal"] for item in records),
        "aoi_inside_nifc_reference_count": sum(item["inside_nifc_final_reference"] for item in records),
        "aoi_reference_qualified_count": len(qualified),
        "aoi_reference_qualified_inside_nifc_count": sum(
            item["inside_nifc_final_reference"] for item in qualified
        ),
        "aoi_reference_qualified_view_zenith_range_degrees": (
            [round(min(view_angles), 4), round(max(view_angles), 4)] if view_angles else None
        ),
        "aoi_reference_qualified_view_zenith_median_degrees": round(median(view_angles), 4) if view_angles else None,
        "aoi_records": records,
    }


def inspect_fire_candidates(
    directory: Path,
    inventory: list[dict[str, Any]],
    *,
    aoi_bbox_utm: list[float],
    reference_geometry_utm: dict[str, Any],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for candidate in inventory:
        inspection = _inspect_fire_product(
            directory / candidate["filename"],
            aoi_bbox_utm=aoi_bbox_utm,
            reference_geometry_utm=reference_geometry_utm,
        )
        results.append({**{key: value for key, value in candidate.items() if key != "stable_route"}, "inspection": inspection})
    return results


def choose_geometry_candidate(
    candidates: list[dict[str, Any]],
    *,
    baseline_view_range: list[float],
    baseline_residual_bowtie_share: float,
) -> dict[str, Any] | None:
    eligible: list[dict[str, Any]] = []
    for item in candidates:
        inspection = item["inspection"]
        view_range = inspection["aoi_reference_qualified_view_zenith_range_degrees"]
        record_count = inspection["aoi_fire_record_count"]
        residual_share = inspection["aoi_residual_bowtie_count"] / record_count if record_count else 0.0
        improved = (
            not item["pre_event_reference_only"]
            and inspection["aoi_reference_qualified_count"] > 0
            and view_range is not None
            and view_range[1] <= baseline_view_range[0] - GEOMETRY_MARGIN_DEGREES
            and residual_share <= baseline_residual_bowtie_share
        )
        item["material_geometry_improvement"] = improved
        item["geometry_screen_reason_codes"] = []
        if item["pre_event_reference_only"]:
            item["geometry_screen_reason_codes"].append("PRE_APPROXIMATE_EVENT_START")
        if inspection["aoi_reference_qualified_count"] == 0:
            item["geometry_screen_reason_codes"].append("NO_REFERENCE_QUALIFIED_AOI_RECORD")
        if view_range is not None and view_range[1] > baseline_view_range[0] - GEOMETRY_MARGIN_DEGREES:
            item["geometry_screen_reason_codes"].append("VIEW_GEOMETRY_MARGIN_NOT_MET")
        if residual_share > baseline_residual_bowtie_share:
            item["geometry_screen_reason_codes"].append("RESIDUAL_BOWTIE_SHARE_WORSE_THAN_BASELINE")
        if improved:
            item["geometry_screen_reason_codes"].append("MATERIAL_GEOMETRY_IMPROVEMENT")
            eligible.append(item)
    if not eligible:
        return None
    return min(
        eligible,
        key=lambda item: (
            item["inspection"]["aoi_reference_qualified_view_zenith_median_degrees"],
            item["inspection"]["aoi_reference_qualified_view_zenith_range_degrees"][1],
            -item["inspection"]["aoi_reference_qualified_count"],
            abs(item["seconds_from_sentinel_observation"]),
            item["native_id"],
        ),
    )


def valid_geolocation_shape(shape: tuple[int, ...]) -> bool:
    """Accept the observed half-resolution forms of valid 201/202-scan swaths."""

    return shape in ((3216, 3200), (3232, 3200))


def _inspect_geolocation(path: Path, aoi_bbox_wgs84: list[float]) -> dict[str, Any]:
    base = "HDFEOS/SWATHS/VJ2_750M_GEOLOCATION/Geolocation Fields"
    with h5py.File(path, "r") as source:
        latitude = source[f"{base}/Latitude"][:]
        longitude = source[f"{base}/Longitude"][:]
        input_pointer = _scalar(source.attrs["InputPointer"])
        attributes = {
            name: _scalar(source.attrs[name])
            for name in (
                "LocalGranuleID",
                "ShortName",
                "VersionID",
                "RangeBeginningDate",
                "RangeBeginningTime",
                "RangeEndingDate",
                "RangeEndingTime",
                "DayNightFlag",
            )
        }
    if not valid_geolocation_shape(latitude.shape) or longitude.shape != latitude.shape:
        raise ObservationGeometryError("VIIRS_GEOLOCATION_SHAPE_UNEXPECTED")
    valid = (
        np.isfinite(latitude)
        & np.isfinite(longitude)
        & (latitude >= -90)
        & (latitude <= 90)
        & (longitude >= -180)
        & (longitude <= 180)
    )
    west, south, east, north = aoi_bbox_wgs84
    aoi_pixels = valid & (latitude >= south) & (latitude <= north) & (longitude >= west) & (longitude <= east)
    indexes = np.argwhere(aoi_pixels)
    if indexes.size == 0:
        raise ObservationGeometryError("VIIRS_GEOLOCATION_NO_AOI_PIXEL")
    west_edge = int(indexes[:, 1].min())
    east_edge = int(3199 - indexes[:, 1].max())
    return {
        "product_filename": path.name,
        "attributes": attributes,
        "upstream_input_filenames": _short_input_names(str(input_pointer)),
        "array_shape": list(latitude.shape),
        "valid_coordinate_count": int(valid.sum()),
        "total_coordinate_count": int(valid.size),
        "aoi_bbox_candidate_pixel_count": int(aoi_pixels.sum()),
        "aoi_bbox_row_range": [int(indexes[:, 0].min()), int(indexes[:, 0].max())],
        "aoi_bbox_column_range": [int(indexes[:, 1].min()), int(indexes[:, 1].max())],
        "aoi_bbox_nearest_scan_edge_columns": min(west_edge, east_edge),
        "aoi_bbox_nearest_scan_edge": "west" if west_edge <= east_edge else "east",
    }


def _public_registration(verification: dict[str, Any]) -> dict[str, Any]:
    registration = verification.get("registration") or {}
    return {
        "package_id": verification.get("package_id"),
        "accepted_as_unchanged_registered_package": verification.get(
            "accepted_as_unchanged_registered_package"
        ),
        "contract_version": registration.get("contract_version"),
        "contract_sha256": registration.get("contract_sha256"),
        "asset_count": registration.get("asset_count"),
        "registered_bytes": sum(item.get("bytes", 0) for item in registration.get("assets") or []),
        "assets": registration.get("assets") or [],
        "reason_codes": verification.get("reason_codes"),
    }


def _label_protocol() -> dict[str, Any]:
    return {
        "protocol_version": "weak-reference-label-feasibility-v0.1.0",
        "implementation_status": "FEASIBILITY_ONLY_NO_LABEL_ARRAY_CREATED",
        "positive_reference": (
            "A nominal/high VIIRS sparse record with nominal geolocation QA and no residual-bowtie flag may remain "
            "a native-scale thermal-anomaly reference at its observation time. It is not a segmentation-positive pixel."
        ),
        "negative_candidate": (
            "A clear, in-AOI optical location without a coincident qualified VIIRS record is only a negative candidate. "
            "Non-detection is not background truth because omission, timing, cloud, smoke, mixed pixels, and scan geometry remain possible."
        ),
        "unknown": (
            "Every location not supported by an allowed reference or explicitly excluded remains unknown; unknown is never silently converted to background."
        ),
        "excluded": (
            "Residual-bowtie records, non-nominal geolocation QA, invalid coordinates, and unusable optical quality states are excluded from reference use."
        ),
        "review_needed": (
            "Qualified native-scale records still require review for time offset, cross-sensor scale, source disagreement, and intended use before any future label proposal."
        ),
        "prohibited_promotions": [
            "Do not buffer points into segmentation truth.",
            "Do not resample 375 m detections and call them genuine 10-20 m labels.",
            "Do not use the later NIFC perimeter as pixel-perfect active-fire truth.",
            "Do not convert VIIRS non-detection into ordinary background.",
        ],
    }


def build_report(
    *,
    candidates: list[dict[str, Any]],
    selected: dict[str, Any] | None,
    companion_metadata: dict[str, Any] | None,
    geolocation: dict[str, Any] | None,
    registration: dict[str, Any],
    baseline: dict[str, Any],
    aoi_bbox_utm: list[float],
    aoi_bbox_wgs84: list[float],
    inventory_query: str,
    companion_query: str | None,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    detections = [item for item in candidates if item["inspection"]["aoi_fire_record_count"] > 0]
    qualified = [item for item in candidates if item["inspection"]["aoi_reference_qualified_count"] > 0]
    selected_id = selected["native_id"] if selected else None
    for rank, item in enumerate(
        sorted(
            qualified,
            key=lambda candidate: (
                candidate["inspection"]["aoi_reference_qualified_view_zenith_median_degrees"],
                abs(candidate["seconds_from_sentinel_observation"]),
                candidate["native_id"],
            ),
        ),
        start=1,
    ):
        item["observed_geometry_rank"] = rank

    decision = "ACCEPT_IMPROVED_REFERENCE_GEOMETRY_DEFER_LABELS" if selected else "RETAIN_BASELINE_REFERENCE_DEFER_LABELS"
    if selected:
        selected_median = selected["inspection"]["aoi_reference_qualified_view_zenith_median_degrees"]
        detail = (
            f"One post-start NOAA-21 observation materially improves qualified AOI view geometry to a {selected_median:.2f}-degree "
            "median under the explicit BurnLens screen. Retain it as stronger native-scale reference evidence, but defer labels and a "
            "dataset because its time offset and 375 m support still cannot define 10-20 m segmentation truth."
        )
    else:
        detail = (
            "No post-start NOAA-21 observation with reference-qualified AOI records cleared the explicit geometry margin without worse "
            "residual-bowtie share. Retain the shipped source/reference package and continue to defer labels and a dataset."
        )

    return {
        "report_id": REPORT_ID,
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 333,
        "branch": "codex/p2o2-t04-observation-geometry",
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": None,
        "aoi_version": AOI_VERSION,
        "dataset_version": None,
        "label_schema_version": None,
        "model_version": None,
        "package_id": PACKAGE_ID,
        "search_scope": {
            "collection": CMR_COLLECTION,
            "companion_collection": GEOLOCATION_COLLECTION,
            "window_start": WINDOW_START,
            "window_end": WINDOW_END,
            "approximate_event_start": EVENT_START,
            "sentinel_observation": SENTINEL_OBSERVATION,
            "aoi_bbox_utm10n": aoi_bbox_utm,
            "aoi_bbox_wgs84": aoi_bbox_wgs84,
            "inventory_query": inventory_query,
            "companion_query": companion_query,
            "inventory_count": len(candidates),
            "metadata_ranking_role": (
                "Deterministic discovery priority only. CMR footprint centrality does not establish actual record geometry or fire presence."
            ),
        },
        "screen_rule": {
            "rule_version": "observation-geometry-screen-v0.1.0",
            "baseline_native_id": BASELINE_NATIVE_ID,
            "baseline_qualified_view_zenith_range_degrees": baseline["view_range"],
            "baseline_residual_bowtie_share": baseline["residual_bowtie_share"],
            "material_improvement_rule": (
                f"Post-approximate-start candidate; at least one nominal/high, nominal-geolocation, non-bowtie AOI record; candidate maximum "
                f"qualified view zenith at least {GEOMETRY_MARGIN_DEGREES:.0f} degrees below the baseline minimum; residual-bowtie share no worse than baseline."
            ),
            "rule_scope": "Conservative BurnLens evidence-screen rule, not a NASA validation threshold and not a label-validity claim.",
        },
        "registration": registration,
        "candidate_summary": {
            "inventory_count": len(candidates),
            "pre_approximate_start_count": sum(item["pre_event_reference_only"] for item in candidates),
            "aoi_detection_candidate_count": len(detections),
            "reference_qualified_candidate_count": len(qualified),
            "materially_improved_candidate_count": sum(item["material_geometry_improvement"] for item in candidates),
            "selected_native_id": selected_id,
        },
        "candidates": candidates,
        "selected_companion": companion_metadata,
        "selected_geolocation": geolocation,
        "label_feasibility_protocol": _label_protocol(),
        "decision": decision,
        "decision_detail": detail,
        "quality_gates": {
            "fresh_official_cmr_inventory": True,
            "every_inventory_candidate_exact_size_and_native_container": True,
            "every_candidate_sparse_record_array_inspected": True,
            "all_exclusion_reasons_preserved": True,
            "selected_companion_exact_pair_verified": bool(selected and geolocation),
            "label_array_created": False,
            "dataset_created": False,
            "direct_label_promotion_allowed": False,
        },
        "claims": {
            "permitted": [
                f"NASA CMR returned {len(candidates)} intersecting {CMR_COLLECTION} granules in the frozen window and AOI.",
                f"BurnLens opened every exact candidate and found AOI sparse fire records in {len(detections)} candidates.",
                "The comparison preserves provider QA, time, geometry, source agreement, and exclusion evidence without creating labels.",
            ],
            "prohibited": [
                "A thermal-anomaly point or later perimeter is pixel-perfect segmentation truth.",
                "No VIIRS detection means ordinary background.",
                "The screen is official, operational, emergency-ready, field-validated, or endorsed.",
            ],
        },
        "source_guidance": [
            {
                "organization": "NASA CMR",
                "url": "https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html",
                "role": "granule temporal, spatial, paging, and deterministic sort semantics",
                "accessed_at_utc": generated_at_utc,
            },
            {
                "organization": "NASA Earthdata / LP DAAC",
                "url": "https://www.earthdata.nasa.gov/data/catalog/lpcloud-vj214img-002",
                "role": "VJ214IMG definition, 375 m support, companion requirement, variables, citation, and open sharing",
                "accessed_at_utc": generated_at_utc,
            },
            {
                "organization": "NASA",
                "url": "https://www.earthdata.nasa.gov/s3fs-public/2024-07/VIIRS_C2_AF-375m_User_Guide_1.0.pdf",
                "role": "fire-mask classes, sparse arrays, QA bits, scan geometry, and limitations",
                "accessed_at_utc": generated_at_utc,
            },
        ],
        "attribution": [
            "NASA VIIRS/JPSS2 VJ214IMG.002 and selected VJ203MODLL.021 data accessed 2026-07-14.",
            "NIFC WFIGS final-perimeter feature remains incident-reference geometry only.",
        ],
        "source_precedence": "Official sources govern over every BurnLens-derived artifact.",
        "warning": WARNING,
    }


def render_png(report: dict[str, Any], path: Path) -> None:
    canvas = Image.new("RGB", (1600, 1100), "#f4f0e8")
    draw = ImageDraw.Draw(canvas)
    ink = "#15211d"
    muted = "#5d6b64"
    teal = "#006b64"
    orange = "#f05a28"
    panel = "#fffdf8"

    draw.rectangle((0, 0, 1600, 170), fill="#132a26")
    draw.text((70, 38), "BURNLENS  /  OBSERVATION GEOMETRY", fill="#b9d8cf", font=_font(22))
    draw.text((70, 78), "REAL NOAA-21 CANDIDATES, UNCERTAINTY INTACT", fill="white", font=_font(37))
    decision_label = "IMPROVED REFERENCE" if report["candidate_summary"]["selected_native_id"] else "BASELINE RETAINED"
    draw.text((1180, 48), "DECISION", fill="#b9d8cf", font=_font(18))
    draw.text((1180, 82), decision_label, fill="#ffd166", font=_font(24))
    draw.text((1180, 124), "labels deferred", fill="white", font=_font(19))

    draw.rounded_rectangle((60, 205, 1090, 760), radius=22, fill=panel, outline="#d7d0c4", width=2)
    draw.text((90, 235), "Qualified AOI fire-record geometry by observation time", fill=ink, font=_font(25))
    draw.text((90, 273), "Lower absolute view zenith is more central; blank observations remain visible in the table.", fill=muted, font=_font(18))
    plot = (110, 325, 1050, 700)
    draw.rectangle(plot, outline="#a9b5ae", width=2)
    for angle in (0, 20, 40, 60, 70):
        y = plot[3] - angle / 75 * (plot[3] - plot[1])
        draw.line((plot[0], y, plot[2], y), fill="#e3ded4", width=1)
        draw.text((72, y - 9), f"{angle}°", fill=muted, font=_font(16))
    start = _parse_time(WINDOW_START)
    end = _parse_time(WINDOW_END)
    span = (end - start).total_seconds()
    selected_id = report["candidate_summary"]["selected_native_id"]
    for item in report["candidates"]:
        value = item["inspection"]["aoi_reference_qualified_view_zenith_median_degrees"]
        if value is None:
            continue
        time_fraction = (_parse_time(item["begin"]) - start).total_seconds() / span
        x = plot[0] + time_fraction * (plot[2] - plot[0])
        y = plot[3] - min(value, 75) / 75 * (plot[3] - plot[1])
        color = teal if item["native_id"] == selected_id else orange if item["native_id"] == BASELINE_NATIVE_ID else "#617d72"
        radius = 9 if item["native_id"] in (selected_id, BASELINE_NATIVE_ID) else 6
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color, outline="white", width=2)
    draw.text((110, 716), "25 Jun", fill=muted, font=_font(17))
    draw.text((990, 716), "1 Jul", fill=muted, font=_font(17))

    summary = report["candidate_summary"]
    cards = (
        (str(summary["inventory_count"]), "CMR candidates"),
        (str(summary["aoi_detection_candidate_count"]), "with AOI records"),
        (str(summary["reference_qualified_candidate_count"]), "qualified candidates"),
        ("0", "label arrays"),
    )
    for index, (value, label) in enumerate(cards):
        top = 205 + index * 136
        draw.rounded_rectangle((1130, top, 1540, top + 112), radius=18, fill=panel, outline="#d7d0c4", width=2)
        draw.text((1160, top + 20), value, fill=teal if index < 3 else orange, font=_font(34))
        draw.text((1235, top + 32), label, fill=ink, font=_font(19))

    draw.rounded_rectangle((60, 800, 1540, 1010), radius=22, fill="#e6efeb", outline="#b8cbc3", width=2)
    draw.text((90, 828), "REFERENCE / LABEL FEASIBILITY", fill=teal, font=_font(21))
    columns = (
        ("POSITIVE / REFERENCE", "Qualified native-scale thermal anomaly; never a 10-20 m positive pixel."),
        ("NEGATIVE CANDIDATE", "No detection is not background truth; omission and timing remain possible."),
        ("UNKNOWN + EXCLUDED", "Unknown stays unknown. Bowtie, bad geolocation, and invalid quality are excluded."),
        ("REVIEW NEEDED", "Time, scale, source disagreement, and intended use remain explicit."),
    )
    for index, (title, text_value) in enumerate(columns):
        left = 90 + index * 360
        draw.text((left, 872), title, fill=ink, font=_font(18))
        words = text_value.split()
        lines: list[str] = []
        current = ""
        for word in words:
            proposed = f"{current} {word}".strip()
            if draw.textlength(proposed, font=_font(17)) > 310 and current:
                lines.append(current)
                current = word
            else:
                current = proposed
        if current:
            lines.append(current)
        for row, line in enumerate(lines[:3]):
            draw.text((left, 910 + row * 24), line, fill=muted, font=_font(17))

    draw.rectangle((0, 1040, 1600, 1100), fill="#132a26")
    draw.text((60, 1057), WARNING, fill="white", font=_font(18))
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], image_name: str, path: Path) -> None:
    rows: list[str] = []
    for item in report["candidates"]:
        inspection = item["inspection"]
        view = inspection["aoi_reference_qualified_view_zenith_median_degrees"]
        view_text = "—" if view is None else f"{view:.2f}°"
        reasons = ", ".join(item["geometry_screen_reason_codes"])
        rows.append(
            "<tr>"
            f"<td><code>{escape(item['pair_token'])}</code></td>"
            f"<td>{escape(item['begin'])}</td>"
            f"<td>{inspection['aoi_fire_record_count']}</td>"
            f"<td>{inspection['aoi_reference_qualified_count']}</td>"
            f"<td>{view_text}</td>"
            f"<td>{inspection['aoi_residual_bowtie_count']}</td>"
            f"<td>{escape(reasons)}</td>"
            "</tr>"
        )
    protocol = report["label_feasibility_protocol"]
    permitted = "".join(f"<li>{escape(item)}</li>" for item in report["claims"]["permitted"])
    prohibited = "".join(f"<li>{escape(item)}</li>" for item in report["claims"]["prohibited"])
    sources = "".join(
        f'<li><a href="{escape(item["url"])}">{escape(item["organization"])}</a> — {escape(item["role"])}</li>'
        for item in report["source_guidance"]
    )
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens observation geometry decision</title>
<style>
:root{{--ink:#15211d;--muted:#5d6b64;--paper:#f4f0e8;--panel:#fffdf8;--teal:#006b64;--orange:#f05a28}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}
header{{background:#132a26;color:white;padding:2rem max(1rem,calc((100% - 1180px)/2))}} header p{{max-width:72ch;color:#c9ddd6}}
main{{max-width:1180px;margin:auto;padding:2rem 1rem 4rem}} .status{{border-left:7px solid var(--orange);background:var(--panel);padding:1rem 1.25rem;margin:1.5rem 0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:1rem}} .card,section{{background:var(--panel);border:1px solid #d7d0c4;border-radius:14px;padding:1.25rem;margin:1rem 0}}
.metric{{display:block;color:var(--teal);font-size:2rem;font-weight:750}} img{{display:block;width:100%;height:auto;border:1px solid #d7d0c4;border-radius:14px}}
.table-wrap{{overflow-x:auto}} table{{width:100%;border-collapse:collapse;min-width:1000px}} th,td{{padding:.65rem;text-align:left;border-bottom:1px solid #ddd6ca;vertical-align:top}} th{{background:#e6efeb}}
code{{overflow-wrap:anywhere}} a{{color:var(--teal)}} .warning{{background:#132a26;color:white;padding:1rem;border-radius:10px;font-weight:650}}
dt{{font-weight:750;margin-top:.65rem}} dd{{margin-left:0;color:var(--muted)}}
</style></head><body>
<header><h1>Observation geometry before labels</h1><p>Real NOAA-21 candidates over the frozen Darlene 3 modeling AOI, compared without converting detections, non-detections, buffers, or perimeters into segmentation truth.</p></header>
<main>
<div class="status"><h2>{escape(report['decision'])}</h2><p>{escape(report['decision_detail'])}</p></div>
<div class="grid"><div class="card"><span class="metric">{report['candidate_summary']['inventory_count']}</span>CMR candidates</div><div class="card"><span class="metric">{report['candidate_summary']['aoi_detection_candidate_count']}</span>with AOI records</div><div class="card"><span class="metric">{report['candidate_summary']['reference_qualified_candidate_count']}</span>with qualified reference records</div><div class="card"><span class="metric">0</span>label arrays</div></div>
<figure><img src="{escape(image_name)}" width="1600" height="1100" alt="BurnLens chart comparing qualified AOI VIIRS record view angles over time and preserving reference, negative-candidate, unknown, excluded, and review-needed states"><figcaption>Rendered from report <code>{escape(report['report_id'])}</code>, run <code>{escape(report['run_id'])}</code>, source commit <code>{escape(report['git_source_commit'])}</code>.</figcaption></figure>
<section><h2>What the screen means</h2><p>{escape(report['screen_rule']['material_improvement_rule'])}</p><p>{escape(report['screen_rule']['rule_scope'])}</p></section>
<section><h2>Every candidate and exclusion reason</h2><div class="table-wrap"><table><thead><tr><th>Acquisition</th><th>Begin UTC</th><th>AOI records</th><th>Qualified</th><th>Median view</th><th>Bowtie</th><th>Screen result</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>
<section><h2>Weak/reference-label feasibility protocol</h2><dl><dt>Positive/reference</dt><dd>{escape(protocol['positive_reference'])}</dd><dt>Negative candidate</dt><dd>{escape(protocol['negative_candidate'])}</dd><dt>Unknown</dt><dd>{escape(protocol['unknown'])}</dd><dt>Excluded</dt><dd>{escape(protocol['excluded'])}</dd><dt>Review needed</dt><dd>{escape(protocol['review_needed'])}</dd></dl></section>
<div class="grid"><section><h2>Permitted claims</h2><ul>{permitted}</ul></section><section><h2>Prohibited claims</h2><ul>{prohibited}</ul></section></div>
<section><h2>Traceability</h2><dl><dt>Repository</dt><dd>{escape(report['repository'])}</dd><dt>Software</dt><dd>{escape(report['software_version'])}</dd><dt>Raw package</dt><dd>{escape(report['package_id'])}</dd><dt>AOI</dt><dd>{escape(report['aoi_version'])}</dd><dt>Dataset / label schema / model</dt><dd>Not created / not created / not created</dd><dt>Run</dt><dd><code>{escape(report['run_id'])}</code></dd><dt>Source commit</dt><dd><code>{escape(report['git_source_commit'])}</code></dd></dl></section>
<section><h2>Primary sources</h2><ul>{sources}</ul><p>{escape(report['source_precedence'])}</p></section>
<p class="warning">{escape(report['warning'])}</p>
</main></body></html>"""
    path.write_text(html, encoding="utf-8")


def write_report(report: dict[str, Any], output_directory: Path) -> dict[str, Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": output_directory / f"{REPORT_ID}.json",
        "html": output_directory / f"{REPORT_ID}.html",
        "png": output_directory / f"{REPORT_ID}.png",
    }
    render_png(report, paths["png"])
    report["rendered_outputs"] = {
        "json": paths["json"].name,
        "html": paths["html"].name,
        "png": paths["png"].name,
        "png_sha256": _sha256(paths["png"]),
    }
    paths["json"].write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    render_html(report, paths["png"].name, paths["html"])
    return paths


def run_observation_geometry_screen(
    *,
    credentials: ProviderCredentials | None,
    quarantine: Path,
    raw_parent: Path,
    aoi_report_path: Path,
    reference_geojson_path: Path,
    baseline_report_path: Path,
    output_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    progress: Callable[[str, int, int], None] | None = None,
) -> dict[str, Path]:
    aoi_report = json.loads(aoi_report_path.read_text(encoding="utf-8"))
    reference = json.loads(reference_geojson_path.read_text(encoding="utf-8"))
    baseline_report = json.loads(baseline_report_path.read_text(encoding="utf-8"))
    if aoi_report.get("aoi_version") != AOI_VERSION:
        raise ObservationGeometryError("AOI_VERSION_MISMATCH")
    if len(reference.get("features") or []) != 1:
        raise ObservationGeometryError("REFERENCE_FEATURE_COUNT_MISMATCH")
    if baseline_report.get("report_id") != "SOURCE-INSPECTION-2026-001":
        raise ObservationGeometryError("BASELINE_REPORT_MISMATCH")
    aoi_bbox_utm = [float(value) for value in aoi_report["derivation"]["aoi_bbox_utm10n"]]
    aoi_bbox_wgs84 = [float(value) for value in aoi_report["derivation"]["aoi_bbox_wgs84"]]
    reference_utm = transform_geom(
        "EPSG:4326",
        "EPSG:32610",
        reference["features"][0]["geometry"],
        precision=3,
    )
    inventory, inventory_query = fetch_inventory(aoi_bbox_wgs84)
    fire_contracts = tuple(_fire_contract(item) for item in inventory)
    destination = raw_parent / PACKAGE_ID
    opener = None

    if destination.exists():
        working = destination
        for contract in fire_contracts:
            if not inspect_asset(working, contract)["accepted"]:
                raise ObservationGeometryError("REGISTERED_FIRE_CANDIDATE_INVALID")
    else:
        if credentials is None:
            raise ObservationGeometryError("EARTHDATA_CREDENTIAL_REQUIRED")
        quarantine.parent.mkdir(parents=True, exist_ok=True)
        raw_parent.mkdir(parents=True, exist_ok=True)
        _validate_working_entries(quarantine, fire_contracts)
        opener = build_earthdata_opener(credentials.earthdata_username, credentials.earthdata_password)
        for contract in fire_contracts:
            stream_asset(contract, quarantine, opener=opener, progress=progress)
        working = quarantine

    candidates = inspect_fire_candidates(
        working,
        inventory,
        aoi_bbox_utm=aoi_bbox_utm,
        reference_geometry_utm=reference_utm,
    )
    baseline_fire = baseline_report["viirs_active_fire"]
    baseline_view_range = [float(value) for value in baseline_fire["aoi_view_zenith_range_degrees"]]
    baseline_total = int(baseline_fire["aoi_fire_record_count"])
    baseline_bowtie_share = int(baseline_fire["aoi_residual_bowtie_count"]) / baseline_total
    selected = choose_geometry_candidate(
        candidates,
        baseline_view_range=baseline_view_range,
        baseline_residual_bowtie_share=baseline_bowtie_share,
    )

    companion_contract = None
    companion_metadata = None
    companion_query = None
    if selected is not None:
        companion_contract, companion_metadata, companion_query = fetch_companion_contract(selected)
    final_contracts = fire_contracts + ((companion_contract,) if companion_contract else ())

    if destination.exists():
        verification = verify_registered_package(
            destination,
            final_contracts,
            contract_validator=validate_screen_contracts,
            contract_version=CONTRACT_VERSION,
        )
    else:
        if companion_contract is not None:
            if opener is None:
                raise ObservationGeometryError("EARTHDATA_OPENER_MISSING")
            _validate_working_entries(quarantine, final_contracts)
            stream_asset(companion_contract, quarantine, opener=opener, progress=progress)
        promote_quarantine(
            quarantine,
            destination,
            final_contracts,
            generated_at_utc=generated_at_utc,
            run_id=run_id,
            synthetic_fixture=False,
            contract_validator=validate_screen_contracts,
            contract_version=CONTRACT_VERSION,
        )
        verification = verify_registered_package(
            destination,
            final_contracts,
            contract_validator=validate_screen_contracts,
            contract_version=CONTRACT_VERSION,
        )
    if not verification["accepted_as_unchanged_registered_package"]:
        raise ObservationGeometryError("OBSERVATION_PACKAGE_VERIFICATION_FAILED")

    geolocation = (
        _inspect_geolocation(destination / companion_contract.expected_filename, aoi_bbox_wgs84)
        if companion_contract is not None
        else None
    )
    if selected is not None and geolocation is not None:
        fire_begin = selected["inspection"]["attributes"]["RangeBeginningTime"][:5]
        geo_begin = geolocation["attributes"]["RangeBeginningTime"][:5]
        if fire_begin != geo_begin:
            raise ObservationGeometryError("SELECTED_PAIR_BEGIN_TIME_MISMATCH")

    report = build_report(
        candidates=candidates,
        selected=selected,
        companion_metadata=companion_metadata,
        geolocation=geolocation,
        registration=_public_registration(verification),
        baseline={"view_range": baseline_view_range, "residual_bowtie_share": round(baseline_bowtie_share, 6)},
        aoi_bbox_utm=aoi_bbox_utm,
        aoi_bbox_wgs84=aoi_bbox_wgs84,
        inventory_query=inventory_query,
        companion_query=companion_query,
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
    )
    return write_report(report, output_directory)
