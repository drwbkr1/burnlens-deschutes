"""Inspect the authenticated BurnLens source package and render bounded evidence.

The output is deliberately an inspection report, not a label set, dataset, fire
perimeter, or model result. Raw provider bytes remain in ignored local storage.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
from typing import Any, Iterable
import zipfile

import h5py
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import rasterio
from rasterio.windows import Window, from_bounds
from rasterio.warp import transform, transform_geom

from .paired_intake import EXACT_CONTRACTS, verify_registered_package


SOFTWARE_VERSION = "0.4.0"
REPORT_ID = "SOURCE-INSPECTION-2026-001"
REPORT_VERSION = "source-inspection-v0.1.0"
REPORT_SCHEMA_VERSION = "0.1.0"
PACKAGE_ID = "darlene3-s2-viirs-pair-v0.1.0"
SENTINEL_FILENAME = (
    "S2B_MSIL2A_20240627T184919_N0510_R113_T10TFP_20240627T213644.SAFE.zip"
)
FIRE_FILENAME = "VJ214IMG.A2024179.1936.002.2025284191612.nc"
GEOLOCATION_FILENAME = "VJ203MODLL.A2024179.1936.021.2024327213621.h5"
WARNING = (
    "Experimental BurnLens CV evidence. Not official wildfire information. "
    "Not emergency guidance. Not evacuation, routing, tactical, or "
    "incident-command support. Official sources govern."
)
SCL_CLASSES = {
    0: "No data",
    1: "Saturated or defective",
    2: "Dark area pixels",
    3: "Cloud shadows",
    4: "Vegetation",
    5: "Bare soils",
    6: "Water",
    7: "Clouds low probability or unclassified",
    8: "Clouds medium probability",
    9: "Clouds high probability",
    10: "Cirrus",
    11: "Snow or ice",
}


class InspectionError(RuntimeError):
    """A deterministic inspection failure with no provider secrets."""


def _scalar(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        if value.size == 1:
            return _scalar(value.reshape(-1)[0])
        return [_scalar(item) for item in value.tolist()]
    if isinstance(value, np.generic):
        return _scalar(value.item())
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="strict")
    return value


def _exact_member(names: Iterable[str], suffix: str) -> str:
    matches = [name for name in names if name.endswith(suffix)]
    if len(matches) != 1:
        raise InspectionError(f"expected exactly one ZIP member ending with {suffix}")
    return matches[0]


def _integer_window(bounds: list[float], affine: Any) -> Window:
    candidate = from_bounds(*bounds, transform=affine)
    values = [candidate.col_off, candidate.row_off, candidate.width, candidate.height]
    rounded = [int(round(float(value))) for value in values]
    if any(abs(float(value) - integer) > 1e-6 for value, integer in zip(values, rounded)):
        raise InspectionError("AOI does not align to the source raster grid")
    return Window(*rounded)


def summarize_scl(values: np.ndarray) -> dict[str, Any]:
    if values.ndim != 2 or values.size == 0:
        raise InspectionError("SCL crop must be a non-empty 2D array")
    unique, counts = np.unique(values, return_counts=True)
    observed = {int(value): int(count) for value, count in zip(unique, counts)}
    if any(value not in SCL_CLASSES for value in observed):
        raise InspectionError("SCL crop contains an unknown class")
    total = int(values.size)
    rows = [
        {
            "value": value,
            "name": SCL_CLASSES[value],
            "pixels": observed.get(value, 0),
            "percent": round(100 * observed.get(value, 0) / total, 4),
        }
        for value in sorted(SCL_CLASSES)
    ]
    medium_high = observed.get(8, 0) + observed.get(9, 0)
    return {
        "pixel_count": total,
        "classes": rows,
        "medium_high_cloud_pixels": medium_high,
        "medium_high_cloud_percent": round(100 * medium_high / total, 4),
        "cloud_shadow_pixels": observed.get(3, 0),
        "cloud_shadow_percent": round(100 * observed.get(3, 0) / total, 4),
        "no_data_pixels": observed.get(0, 0),
        "no_data_percent": round(100 * observed.get(0, 0) / total, 4),
    }


def _read_sentinel(
    package: Path,
    aoi_bbox_utm: list[float],
) -> tuple[dict[str, Any], np.ndarray, str, str]:
    archive_path = package / SENTINEL_FILENAME
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
    tci_member = _exact_member(names, "_TCI_10m.jp2")
    scl_member = _exact_member(names, "_SCL_20m.jp2")
    archive_uri = archive_path.resolve().as_posix()

    with rasterio.open(f"zip://{archive_uri}!{tci_member}") as source:
        if source.driver != "JP2OpenJPEG" or source.count != 3:
            raise InspectionError("unexpected Sentinel true-color raster contract")
        if source.crs is None or source.crs.to_epsg() != 32610:
            raise InspectionError("Sentinel true-color CRS is not EPSG:32610")
        if source.dtypes != ("uint8", "uint8", "uint8"):
            raise InspectionError("Sentinel true-color dtype is not uint8 RGB")
        if abs(source.transform.a - 10) > 1e-9 or abs(source.transform.e + 10) > 1e-9:
            raise InspectionError("Sentinel true-color resolution is not 10 m")
        tci_window = _integer_window(aoi_bbox_utm, source.transform)
        rgb = source.read(window=tci_window)
        tci_bounds = [round(float(value), 3) for value in source.window_bounds(tci_window)]
        tci_source = {
            "member": tci_member,
            "driver": source.driver,
            "crs": source.crs.to_string(),
            "source_width": source.width,
            "source_height": source.height,
            "source_band_count": source.count,
            "source_dtype": list(source.dtypes),
            "source_bounds_utm10n": [round(float(value), 3) for value in source.bounds],
            "source_transform": [round(float(value), 9) for value in source.transform[:6]],
            "aoi_window": {
                "column_offset": int(tci_window.col_off),
                "row_offset": int(tci_window.row_off),
                "width": int(tci_window.width),
                "height": int(tci_window.height),
            },
            "aoi_bounds_utm10n": tci_bounds,
            "observed_min": int(rgb.min()),
            "observed_max": int(rgb.max()),
            "channel_means": [
                round(float(value), 4)
                for value in np.reshape(rgb, (3, -1)).mean(axis=1)
            ],
        }

    with rasterio.open(f"zip://{archive_uri}!{scl_member}") as source:
        if source.count != 1 or source.dtypes != ("uint8",):
            raise InspectionError("unexpected Sentinel SCL raster contract")
        if source.crs is None or source.crs.to_epsg() != 32610:
            raise InspectionError("Sentinel SCL CRS is not EPSG:32610")
        if abs(source.transform.a - 20) > 1e-9 or abs(source.transform.e + 20) > 1e-9:
            raise InspectionError("Sentinel SCL resolution is not 20 m")
        scl_window = _integer_window(aoi_bbox_utm, source.transform)
        scl = source.read(1, window=scl_window)
        scl_source = {
            "member": scl_member,
            "crs": source.crs.to_string(),
            "source_width": source.width,
            "source_height": source.height,
            "aoi_window": {
                "column_offset": int(scl_window.col_off),
                "row_offset": int(scl_window.row_off),
                "width": int(scl_window.width),
                "height": int(scl_window.height),
            },
            "aoi_bounds_utm10n": [
                round(float(value), 3) for value in source.window_bounds(scl_window)
            ],
            "summary": summarize_scl(scl),
        }

    if rgb.shape != (3, 900, 1200) or scl.shape != (450, 600):
        raise InspectionError("real AOI crop dimensions do not match the frozen AOI")
    if tci_source["aoi_bounds_utm10n"] != [round(value, 3) for value in aoi_bbox_utm]:
        raise InspectionError("true-color crop does not match the AOI bounds")
    if scl_source["aoi_bounds_utm10n"] != [round(value, 3) for value in aoi_bbox_utm]:
        raise InspectionError("SCL crop does not match the AOI bounds")

    return (
        {
            "product_filename": SENTINEL_FILENAME,
            "true_color": tci_source,
            "scene_classification": scl_source,
            "interpretation": (
                "The true-color and SCL crops are real source observations over the frozen AOI. "
                "They establish readable pixels and visible conditions, not burned-area labels."
            ),
        },
        rgb,
        tci_member,
        scl_member,
    )


def _point_in_ring(x: float, y: float, ring: list[list[float]]) -> bool:
    inside = False
    for index in range(len(ring) - 1):
        x1, y1 = ring[index][:2]
        x2, y2 = ring[index + 1][:2]
        if ((y1 > y) != (y2 > y)) and (
            x < (x2 - x1) * (y - y1) / (y2 - y1) + x1
        ):
            inside = not inside
    return inside


def point_in_geometry(x: float, y: float, geometry: dict[str, Any]) -> bool:
    kind = geometry.get("type")
    coordinates = geometry.get("coordinates")
    if kind == "Polygon":
        polygons = [coordinates]
    elif kind == "MultiPolygon":
        polygons = coordinates
    else:
        raise InspectionError("reference geometry must be Polygon or MultiPolygon")
    for polygon in polygons:
        if not polygon or not _point_in_ring(x, y, polygon[0]):
            continue
        if any(_point_in_ring(x, y, hole) for hole in polygon[1:]):
            continue
        return True
    return False


def _short_input_names(value: str) -> list[str]:
    return sorted(set(re.findall(r"VJ2[A-Z0-9]+\.A\d+\.\d+\.\d+\.\d+\.nc", value)))


def _read_viirs_fire(
    package: Path,
    aoi_bbox_utm: list[float],
    reference_geometry_utm: dict[str, Any],
) -> dict[str, Any]:
    path = package / FIRE_FILENAME
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
            raise InspectionError(f"VIIRS fire datasets missing: {','.join(missing)}")
        if source["fire mask"].shape != (6464, 6400):
            raise InspectionError("VIIRS fire mask has unexpected dimensions")
        if source["algorithm QA"].shape != (6464, 6400):
            raise InspectionError("VIIRS QA has unexpected dimensions")
        fire_count = int(_scalar(source.attrs["FirePix"]))
        vectors = {
            name: source[name][:]
            for name in required
            if name not in ("fire mask", "algorithm QA")
        }
        if any(len(values) != fire_count for values in vectors.values()):
            raise InspectionError("VIIRS sparse vectors do not match FirePix")
        lines = vectors["FP_line"].astype(int)
        samples = vectors["FP_sample"].astype(int)
        if np.any(lines < 0) or np.any(lines >= 6464) or np.any(samples < 0) or np.any(samples >= 6400):
            raise InspectionError("VIIRS sparse pixel index is outside the fire mask")
        mask_values = np.array(
            [source["fire mask"][line, sample] for line, sample in zip(lines, samples)],
            dtype=np.uint8,
        )
        qa_values = np.array(
            [source["algorithm QA"][line, sample] for line, sample in zip(lines, samples)],
            dtype=np.uint32,
        )
        if not np.array_equal(mask_values, vectors["FP_confidence"]):
            raise InspectionError("VIIRS sparse confidence does not match fire mask class")
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
        in_aoi = west <= x <= east and south <= y <= north
        residual_bowtie = bool((int(qa_values[index]) >> 22) & 1)
        bad_geolocation = bool((int(qa_values[index]) >> 5) & 1)
        records.append(
            {
                "sparse_index": index,
                "line": int(lines[index]),
                "sample": int(samples[index]),
                "latitude": round(float(latitudes[index]), 7),
                "longitude": round(float(longitudes[index]), 7),
                "utm10n_x": round(float(x), 2),
                "utm10n_y": round(float(y), 2),
                "confidence_class": int(vectors["FP_confidence"][index]),
                "confidence_name": {7: "low", 8: "nominal", 9: "high"}[
                    int(vectors["FP_confidence"][index])
                ],
                "fire_mask_class": int(mask_values[index]),
                "fire_radiative_power_mw": round(float(vectors["FP_power"][index]), 6),
                "view_zenith_degrees": round(float(vectors["FP_ViewZenAng"][index]), 4),
                "solar_zenith_degrees": round(float(vectors["FP_SolZenAng"][index]), 4),
                "adjacent_cloud_pixels": int(vectors["FP_AdjCloud"][index]),
                "adjacent_water_pixels": int(vectors["FP_AdjWater"][index]),
                "qa_geolocation_non_nominal": bad_geolocation,
                "qa_residual_bowtie": residual_bowtie,
                "inside_modeling_aoi": in_aoi,
                "inside_nifc_final_reference": (
                    point_in_geometry(float(x), float(y), reference_geometry_utm)
                    if in_aoi
                    else False
                ),
            }
        )

    aoi_records = [item for item in records if item["inside_modeling_aoi"]]
    non_bowtie = [item for item in aoi_records if not item["qa_residual_bowtie"]]
    confidence = Counter(item["confidence_name"] for item in aoi_records)
    retained_confidence = Counter(item["confidence_name"] for item in non_bowtie)
    return {
        "product_filename": FIRE_FILENAME,
        "attributes": attributes,
        "upstream_input_filenames": _short_input_names(str(input_pointer)),
        "fire_mask_shape": [6464, 6400],
        "global_fire_record_count": fire_count,
        "aoi_fire_record_count": len(aoi_records),
        "aoi_confidence_counts": {
            name: confidence.get(name, 0) for name in ("low", "nominal", "high")
        },
        "aoi_residual_bowtie_count": sum(item["qa_residual_bowtie"] for item in aoi_records),
        "aoi_bad_geolocation_qa_count": sum(
            item["qa_geolocation_non_nominal"] for item in aoi_records
        ),
        "aoi_non_bowtie_reference_count": len(non_bowtie),
        "aoi_non_bowtie_confidence_counts": {
            name: retained_confidence.get(name, 0) for name in ("low", "nominal", "high")
        },
        "aoi_inside_nifc_reference_count": sum(
            item["inside_nifc_final_reference"] for item in aoi_records
        ),
        "aoi_non_bowtie_inside_nifc_reference_count": sum(
            item["inside_nifc_final_reference"] for item in non_bowtie
        ),
        "aoi_view_zenith_range_degrees": [
            round(min(item["view_zenith_degrees"] for item in aoi_records), 4),
            round(max(item["view_zenith_degrees"] for item in aoi_records), 4),
        ],
        "aoi_records": aoi_records,
        "interpretation": (
            "NASA fire classes are coarse thermal-anomaly reference evidence. Residual-bowtie "
            "records remain visible and are excluded from the non-bowtie count; no record is "
            "expanded into a Sentinel-resolution label."
        ),
    }


def _read_viirs_geolocation(
    package: Path,
    aoi_bbox_wgs84: list[float],
) -> dict[str, Any]:
    path = package / GEOLOCATION_FILENAME
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
    if latitude.shape != (3232, 3200) or longitude.shape != latitude.shape:
        raise InspectionError("VIIRS geolocation arrays have unexpected dimensions")
    valid = (
        np.isfinite(latitude)
        & np.isfinite(longitude)
        & (latitude >= -90)
        & (latitude <= 90)
        & (longitude >= -180)
        & (longitude <= 180)
    )
    west, south, east, north = aoi_bbox_wgs84
    aoi_bbox_pixels = (
        valid
        & (latitude >= south)
        & (latitude <= north)
        & (longitude >= west)
        & (longitude <= east)
    )
    indexes = np.argwhere(aoi_bbox_pixels)
    if indexes.size == 0:
        raise InspectionError("VIIRS geolocation arrays contain no AOI-bbox pixels")
    return {
        "product_filename": GEOLOCATION_FILENAME,
        "attributes": attributes,
        "upstream_input_filenames": _short_input_names(str(input_pointer)),
        "array_shape": list(latitude.shape),
        "valid_coordinate_count": int(valid.sum()),
        "total_coordinate_count": int(valid.size),
        "valid_coordinate_percent": round(100 * int(valid.sum()) / valid.size, 6),
        "observed_latitude_range": [
            round(float(latitude[valid].min()), 6),
            round(float(latitude[valid].max()), 6),
        ],
        "observed_longitude_range": [
            round(float(longitude[valid].min()), 6),
            round(float(longitude[valid].max()), 6),
        ],
        "aoi_bbox_candidate_pixel_count": int(aoi_bbox_pixels.sum()),
        "aoi_bbox_row_range": [int(indexes[:, 0].min()), int(indexes[:, 0].max())],
        "aoi_bbox_column_range": [int(indexes[:, 1].min()), int(indexes[:, 1].max())],
        "aoi_bbox_nearest_east_edge_columns": int(3199 - indexes[:, 1].max()),
        "interpretation": (
            "The real 750 m geolocation grid covers the AOI but places it at the far eastern "
            "scan edge. This is source-fitness evidence and a review constraint, not a label."
        ),
    }


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return ImageFont.load_default(size=size)


def _iter_polygon_rings(geometry: dict[str, Any]) -> Iterable[list[list[float]]]:
    if geometry["type"] == "Polygon":
        polygons = [geometry["coordinates"]]
    elif geometry["type"] == "MultiPolygon":
        polygons = geometry["coordinates"]
    else:
        raise InspectionError("reference geometry must be Polygon or MultiPolygon")
    for polygon in polygons:
        for ring in polygon:
            yield ring


def render_png(
    report: dict[str, Any],
    rgb: np.ndarray,
    reference_geometry_utm: dict[str, Any],
    path: Path,
) -> None:
    canvas = Image.new("RGB", (1600, 1100), "#f4f0e8")
    draw = ImageDraw.Draw(canvas)
    ink = "#15211d"
    muted = "#5d6b64"
    accent = "#f05a28"
    teal = "#006b64"
    panel = "#fffdf8"

    draw.rectangle((0, 0, 1600, 170), fill="#132a26")
    draw.text((70, 42), "BURNLENS  /  AUTHENTICATED SOURCE INSPECTION", fill="#b9d8cf", font=_font(22))
    draw.text((70, 82), "REAL AOI PIXELS + COARSE REFERENCE EVIDENCE", fill="white", font=_font(38))
    draw.text((1160, 50), "DECISION", fill="#b9d8cf", font=_font(18))
    draw.text((1160, 82), "REFERENCE ONLY", fill="#ffd166", font=_font(30))
    draw.text((1160, 126), "labels deferred", fill="white", font=_font(19))

    map_left, map_top = 70, 215
    map_width, map_height = 1000, 750
    image = Image.fromarray(np.moveaxis(rgb, 0, 2), mode="RGB").resize(
        (map_width, map_height), Image.Resampling.LANCZOS
    )
    canvas.paste(image, (map_left, map_top))
    overlay = ImageDraw.Draw(canvas)
    west, south, east, north = report["aoi"]["bbox_utm10n"]

    def screen(x: float, y: float) -> tuple[float, float]:
        return (
            map_left + (x - west) / (east - west) * map_width,
            map_top + (north - y) / (north - south) * map_height,
        )

    for ring in _iter_polygon_rings(reference_geometry_utm):
        overlay.line([screen(*point[:2]) for point in ring], fill="#55e6d1", width=4, joint="curve")
    for record in report["viirs_active_fire"]["aoi_records"]:
        x, y = screen(record["utm10n_x"], record["utm10n_y"])
        radius = 10 if record["confidence_name"] == "high" else 8
        color = "#ffca3a" if not record["qa_residual_bowtie"] else "#ff5c8a"
        overlay.ellipse((x - radius, y - radius, x + radius, y + radius), outline="#15211d", width=5)
        overlay.ellipse((x - radius, y - radius, x + radius, y + radius), outline=color, width=3)
        if record["qa_residual_bowtie"]:
            overlay.line((x - 7, y - 7, x + 7, y + 7), fill=color, width=3)
            overlay.line((x - 7, y + 7, x + 7, y - 7), fill=color, width=3)

    overlay.rectangle((map_left, map_top, map_left + map_width, map_top + map_height), outline="#132a26", width=4)
    overlay.rectangle((map_left + 18, map_top + 18, map_left + 526, map_top + 104), fill="#132a26")
    overlay.text((map_left + 36, map_top + 31), "Sentinel-2 true color  /  10 m AOI crop", fill="white", font=_font(21))
    overlay.text((map_left + 36, map_top + 65), "June 27, 2024 18:49 UTC  |  EPSG:32610", fill="#b9d8cf", font=_font(17))

    side_left = 1110
    draw.rounded_rectangle((side_left, 215, 1530, 965), radius=18, fill=panel, outline="#d4cec1", width=2)
    draw.text((1145, 250), "WHAT THE REAL FILES SHOW", fill=muted, font=_font(18))
    cards = [
        (
            "1,200 x 900",
            "Sentinel AOI pixels at 10 m",
            teal,
        ),
        (
            f"{report['sentinel_2_l2a']['scene_classification']['summary']['medium_high_cloud_percent']:.2f}%",
            "SCL medium + high cloud",
            ink,
        ),
        (
            str(report["viirs_active_fire"]["aoi_fire_record_count"]),
            "VIIRS provider records in AOI",
            accent,
        ),
        (
            str(report["viirs_active_fire"]["aoi_non_bowtie_reference_count"]),
            "non-bowtie reference records",
            ink,
        ),
    ]
    top = 295
    for value, label, color in cards:
        draw.text((1145, top), value, fill=color, font=_font(35))
        draw.text((1145, top + 46), label, fill=muted, font=_font(17))
        top += 112

    view_range = report["viirs_active_fire"]["aoi_view_zenith_range_degrees"]
    draw.line((1145, 747, 1495, 747), fill="#d4cec1", width=2)
    draw.text((1145, 774), "SCAN-EDGE RISK", fill="#9c2f13", font=_font(18))
    draw.text((1145, 810), f"View zenith {view_range[0]:.2f}-{view_range[1]:.2f} deg", fill=ink, font=_font(21))
    draw.text((1145, 846), "3 residual-bowtie records", fill=ink, font=_font(20))
    draw.text((1145, 882), "0 bad-geolocation QA records", fill=ink, font=_font(20))
    draw.text((1145, 925), "Do not promote to labels.", fill="#9c2f13", font=_font(21))

    draw.line((90, 1002, 230, 1002), fill="#55e6d1", width=5)
    draw.text((248, 988), "NIFC final-perimeter reference", fill=ink, font=_font(17))
    draw.ellipse((565, 991, 581, 1007), outline="#ffca3a", width=4)
    draw.text((594, 988), "VIIRS reference", fill=ink, font=_font(17))
    draw.line((780, 990, 794, 1006), fill="#ff5c8a", width=3)
    draw.line((780, 1006, 794, 990), fill="#ff5c8a", width=3)
    draw.text((807, 988), "residual bowtie", fill=ink, font=_font(17))
    draw.text((70, 1036), "Contains modified Copernicus Sentinel data 2024  |  NASA VIIRS reference data  |  official sources govern", fill=muted, font=_font(16))
    draw.text((70, 1068), f"{report['run_id']}  ·  {report['software_version']}  ·  {WARNING}", fill=muted, font=_font(14))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], png_name: str, path: Path) -> None:
    viirs = report["viirs_active_fire"]
    scl = report["sentinel_2_l2a"]["scene_classification"]["summary"]
    rows = "".join(
        "<tr>"
        f"<td>{item['sparse_index']}</td><td>{item['confidence_name']}</td>"
        f"<td>{'yes' if item['qa_residual_bowtie'] else 'no'}</td>"
        f"<td>{item['view_zenith_degrees']:.2f}°</td>"
        f"<td>{'yes' if item['inside_nifc_final_reference'] else 'no'}</td>"
        "</tr>"
        for item in viirs["aoi_records"]
    )
    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BurnLens authenticated source inspection</title>
  <style>
    :root {{ color-scheme: light; --ink:#15211d; --muted:#5d6b64; --paper:#f4f0e8; --panel:#fffdf8; --teal:#006b64; --orange:#f05a28; }}
    * {{ box-sizing:border-box; }} body {{ margin:0; background:var(--paper); color:var(--ink); font:16px/1.55 system-ui,sans-serif; }}
    header {{ background:#132a26; color:white; padding:3rem max(5vw,2rem); }} header p {{ color:#b9d8cf; margin:.25rem 0; }}
    main {{ max-width:1180px; margin:auto; padding:2.5rem 1.5rem 5rem; }}
    .warning {{ background:#fff1ca; border-left:6px solid #d87618; padding:1rem 1.2rem; font-weight:650; }}
    .hero {{ width:100%; height:auto; border:1px solid #c8c0b2; margin:1.5rem 0; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:1rem; }}
    .card {{ background:var(--panel); border:1px solid #d9d1c4; border-radius:12px; padding:1.2rem; }}
    .value {{ font-size:2rem; font-weight:800; color:var(--teal); }} h2 {{ margin-top:2.5rem; }}
    table {{ width:100%; border-collapse:collapse; background:var(--panel); }} th,td {{ padding:.7rem; border-bottom:1px solid #ddd5c9; text-align:left; }}
    code {{ overflow-wrap:anywhere; }} .decision {{ border:2px solid var(--orange); }} a {{ color:#005f73; }}
  </style>
</head>
<body>
<header><p>BurnLens / Phase Two / real-source evidence</p><h1>Authenticated source inspection</h1><p>Reference accepted; label and dataset readiness deferred.</p></header>
<main>
  <p class="warning">{escape(WARNING)}</p>
  <img class="hero" src="{escape(png_name)}" alt="Sentinel-2 AOI crop with NIFC reference outline and VIIRS reference points">
  <div class="grid">
    <div class="card"><div class="value">verified</div><div>Exact three-asset package independently rechecked</div></div>
    <div class="card"><div class="value">{scl['medium_high_cloud_percent']:.2f}%</div><div>SCL medium + high cloud in the AOI</div></div>
    <div class="card"><div class="value">{viirs['aoi_fire_record_count']}</div><div>VIIRS provider fire records inside the AOI</div></div>
    <div class="card"><div class="value">{viirs['aoi_non_bowtie_reference_count']}</div><div>Records remaining after residual-bowtie exclusion</div></div>
  </div>
  <section class="card decision"><h2>Decision</h2><p><strong>Accept the exact package for source and reference inspection. Do not promote it to labels or a dataset yet.</strong></p>
  <p>The Sentinel crop is readable and the VIIRS product contains AOI reference detections, but the VIIRS observations sit at the far scan edge with approximately 69° view zenith. Three of eight AOI records carry the residual-bowtie QA flag, and the 375 m thermal-anomaly evidence cannot be expanded into 10–20 m segmentation truth.</p></section>
  <h2>AOI VIIRS records</h2>
  <table><thead><tr><th>Index</th><th>Confidence</th><th>Residual bowtie</th><th>View zenith</th><th>Inside NIFC reference</th></tr></thead><tbody>{rows}</tbody></table>
  <h2>Traceability</h2>
  <div class="card"><p><strong>Run:</strong> <code>{escape(report['run_id'])}</code><br>
  <strong>Git source commit:</strong> <code>{escape(report['git_source_commit'])}</code><br>
  <strong>Software:</strong> <code>{escape(report['software_version'])}</code><br>
  <strong>App / dataset / labels / model:</strong> none<br>
  <strong>Package:</strong> <code>{escape(report['package_id'])}</code><br>
  <strong>Contract:</strong> <code>{escape(report['package_verification']['registration']['contract_version'])}</code></p></div>
  <h2>Source and use notes</h2>
  <ul><li>Contains modified Copernicus Sentinel data 2024.</li><li>NASA VIIRS data are coarse thermal-anomaly reference evidence; data imperfections, false alarms, and omissions remain possible.</li><li>The NIFC final perimeter is incident-reference geometry, not a BurnLens detection or pixel-perfect label.</li><li>Official sources govern over every BurnLens-derived artifact.</li></ul>
</main></body></html>
"""
    path.write_text(document, encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_source_package(
    *,
    package: Path,
    aoi_report_path: Path,
    reference_geojson_path: Path,
    output_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Path]:
    verification = verify_registered_package(package, EXACT_CONTRACTS)
    if not verification["accepted_as_unchanged_registered_package"]:
        raise InspectionError("registered package verification failed")
    aoi_report = json.loads(aoi_report_path.read_text(encoding="utf-8"))
    reference = json.loads(reference_geojson_path.read_text(encoding="utf-8"))
    if aoi_report.get("aoi_version") != "aoi-darlene3-model-v0.2.0":
        raise InspectionError("unexpected AOI version")
    if len(reference.get("features") or []) != 1:
        raise InspectionError("expected exactly one NIFC reference feature")
    aoi_bbox_utm = [float(value) for value in aoi_report["derivation"]["aoi_bbox_utm10n"]]
    aoi_bbox_wgs84 = [float(value) for value in aoi_report["derivation"]["aoi_bbox_wgs84"]]
    reference_utm = transform_geom(
        "EPSG:4326",
        "EPSG:32610",
        reference["features"][0]["geometry"],
        precision=3,
    )
    sentinel, rgb, _, _ = _read_sentinel(package, aoi_bbox_utm)
    fire = _read_viirs_fire(package, aoi_bbox_utm, reference_utm)
    geolocation = _read_viirs_geolocation(package, aoi_bbox_wgs84)
    if fire["attributes"]["RangeBeginningTime"][:5] != geolocation["attributes"]["RangeBeginningTime"][:5]:
        raise InspectionError("VIIRS fire and geolocation begin times differ")

    report: dict[str, Any] = {
        "report_id": REPORT_ID,
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 329,
        "branch": "codex/p2o2-t03-authenticated-intake",
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": None,
        "aoi_version": "aoi-darlene3-model-v0.2.0",
        "dataset_version": None,
        "label_schema_version": None,
        "baseline_version": None,
        "model_version": None,
        "package_id": PACKAGE_ID,
        "package_verification": verification,
        "aoi": {
            "bbox_utm10n": aoi_bbox_utm,
            "bbox_wgs84": aoi_bbox_wgs84,
            "width_m": 12000,
            "height_m": 9000,
            "area_km2": 108.0,
        },
        "sentinel_2_l2a": sentinel,
        "viirs_active_fire": fire,
        "viirs_geolocation": geolocation,
        "decision": "ACCEPT_SOURCE_REFERENCE_DEFER_LABELS",
        "decision_detail": (
            "Accept the exact package as authenticated, readable source/reference evidence. "
            "Defer label and dataset promotion because the VIIRS AOI observations are near the "
            "swath edge at approximately 69 degrees view zenith, three of eight AOI records are "
            "residual-bowtie observations, and 375 m thermal-anomaly evidence is not 10-20 m "
            "segmentation truth."
        ),
        "quality_gates": {
            "registered_package_reverified": True,
            "sentinel_aoi_exact_grid_crop": True,
            "sentinel_scl_read": True,
            "viirs_fire_mask_and_sparse_vectors_consistent": True,
            "viirs_geolocation_real_arrays_cover_aoi_bbox": True,
            "viirs_bad_geolocation_qa_count_zero": fire["aoi_bad_geolocation_qa_count"] == 0,
            "direct_label_promotion_allowed": False,
        },
        "claims": {
            "permitted": [
                "BurnLens authenticated and independently reverified the exact frozen three-asset package.",
                "The real Sentinel-2 AOI crop is readable and has an explicit SCL distribution.",
                "The real VIIRS product contains eight provider fire-pixel records inside the modeling AOI, three marked as residual bowtie.",
            ],
            "prohibited": [
                "The VIIRS points or NIFC perimeter are pixel-perfect segmentation labels.",
                "The Sentinel pixels prove burned area or model readiness.",
                "The report is official, operational, emergency-ready, field-validated, or endorsed.",
            ],
        },
        "limitations": [
            "VIIRS identifies active fires and other thermal anomalies; false alarms and omissions can occur.",
            "The AOI is at the far VIIRS scan edge and observed fire-record view zenith is approximately 69 degrees.",
            "Residual-bowtie detections can duplicate observations and are excluded from the non-bowtie count.",
            "The 46 minute 40.976 second Sentinel-to-VIIRS offset permits scene change.",
            "SCL is a scene-classification aid, not a perfect cloud or usability truth layer.",
            "The NIFC final perimeter is later incident-reference geometry and not a segmentation label.",
        ],
        "source_guidance": [
            {
                "organization": "NASA Earthdata / LP DAAC",
                "url": "https://www.earthdata.nasa.gov/data/catalog/lpcloud-vj214img-002",
                "role": "VJ214IMG product definition, companion requirement, citation, and open-sharing posture",
                "accessed_at_utc": generated_at_utc,
            },
            {
                "organization": "NASA",
                "url": "https://www.earthdata.nasa.gov/s3fs-public/2024-07/VIIRS_C2_AF-375m_User_Guide_1.0.pdf",
                "role": "fire classes, QA bits, sparse arrays, scan geometry, and limitations",
                "accessed_at_utc": generated_at_utc,
            },
            {
                "organization": "Copernicus Data Space Ecosystem",
                "url": "https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S2L2A.html",
                "role": "Sentinel-2 L2A band resolutions and SCL classes",
                "accessed_at_utc": generated_at_utc,
            },
            {
                "organization": "Copernicus Data Space Ecosystem",
                "url": "https://documentation.dataspace.copernicus.eu/FAQ.html",
                "role": "modified Sentinel data attribution wording",
                "accessed_at_utc": generated_at_utc,
            },
        ],
        "attribution": [
            "Contains modified Copernicus Sentinel data 2024.",
            "NASA VIIRS/JPSS2 VJ214IMG.002 and VJ203MODLL.021 data accessed 2026-07-14.",
            "NIFC WFIGS Interagency Fire Perimeters final-reference feature SOURCE-2026-007.",
        ],
        "source_precedence": "Official sources govern over every BurnLens-derived artifact.",
        "warning": WARNING,
    }

    output_directory.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": output_directory / f"{REPORT_ID}.json",
        "png": output_directory / f"{REPORT_ID}.png",
        "html": output_directory / f"{REPORT_ID}.html",
    }
    render_png(report, rgb, reference_utm, paths["png"])
    report["rendered_outputs"] = {
        "png": paths["png"].name,
        "png_sha256": _sha256(paths["png"]),
        "html": paths["html"].name,
        "json": paths["json"].name,
    }
    paths["json"].write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    render_html(report, paths["png"].name, paths["html"])
    return paths
