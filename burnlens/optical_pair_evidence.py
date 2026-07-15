"""Inspect the exact Sentinel-2 pair and render non-label optical evidence.

The report proves source readability, geometry, AOI quality, continuous spectral
change, and a five-state label design. It never writes a label array, dataset,
baseline mask, or model output.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from typing import Any, Iterable
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import rasterio
from rasterio.windows import Window, from_bounds
from rasterio.warp import transform_geom

from .optical_pair_contract import (
    CONTRACT_VERSION,
    OPTICAL_CONTRACTS,
    PACKAGE_ID,
    POST_SAFE,
    PRE_SAFE,
    SOFTWARE_VERSION,
    TERMS_REVIEW_ID,
    validate_optical_contracts,
)
from .paired_intake import verify_registered_package


REPORT_ID = "OPTICAL-PAIR-2026-001"
REPORT_SCHEMA_VERSION = "0.1.0"
REPORT_VERSION = "optical-pair-protocol-evidence-v0.1.0"
TARGET_VERSION = "target-burn-scar-v0.2.0"
AOI_VERSION = "aoi-darlene3-model-v0.2.0"
LABEL_PROTOCOL_VERSION = "burn-scar-label-protocol-v0.1.0"
WARNING = (
    "Experimental BurnLens CV evidence. Not official wildfire information. "
    "Not emergency guidance. Not evacuation, routing, tactical, or "
    "incident-command support. Official sources govern."
)


SCL_CLASSES = {
    0: "No data",
    1: "Saturated or defective",
    2: "Cast or topographic shadow",
    3: "Cloud shadow",
    4: "Vegetation",
    5: "Bare soil",
    6: "Water",
    7: "Unclassified",
    8: "Cloud medium probability",
    9: "Cloud high probability",
    10: "Thin cirrus",
    11: "Snow or ice",
}
EXCLUDED_SCL = {0, 1, 2, 3, 6, 8, 9, 10, 11}
REVIEW_SCL = {7}
ELIGIBLE_SCL = {4, 5}
SELECTED_BANDS = ("B04", "B8A", "B12")
PHYSICAL_BANDS = {"B04": "B4", "B8A": "B8A", "B12": "B12"}


class OpticalPairEvidenceError(RuntimeError):
    """A deterministic, secret-free source or evidence failure."""


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return ImageFont.load_default(size=size)


def _sha256_lf_text(path: Path) -> str:
    """Hash committed UTF-8 evidence after cross-platform LF normalization."""
    try:
        with path.open("r", encoding="utf-8", newline=None) as handle:
            normalized = handle.read().encode("utf-8")
    except (OSError, UnicodeError) as error:
        raise OpticalPairEvidenceError(f"invalid UTF-8 input {path.name}") from error
    return sha256(normalized).hexdigest()


def _write_utf8_lf(path: Path, text: str) -> None:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    path.write_bytes(normalized.encode("utf-8"))


def _exact_member(names: Iterable[str], suffix: str) -> str:
    matches = [name for name in names if name.endswith(suffix)]
    if len(matches) != 1:
        raise OpticalPairEvidenceError(f"expected exactly one ZIP member ending with {suffix}")
    return matches[0]


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _elements(root: ET.Element, name: str) -> list[ET.Element]:
    return [item for item in root.iter() if _local_name(item.tag) == name]


def _exact_text(root: ET.Element, name: str) -> str:
    matches = _elements(root, name)
    if len(matches) != 1 or matches[0].text is None:
        raise OpticalPairEvidenceError(f"expected exactly one XML value for {name}")
    return matches[0].text.strip()


def _parse_xml(archive: zipfile.ZipFile, member: str) -> ET.Element:
    try:
        return ET.fromstring(archive.read(member))
    except (KeyError, ET.ParseError, UnicodeError) as error:
        raise OpticalPairEvidenceError(f"invalid XML member {member}: {type(error).__name__}") from None


def _integer_window(bounds: list[float], affine: Any) -> Window:
    candidate = from_bounds(*bounds, transform=affine)
    values = [candidate.col_off, candidate.row_off, candidate.width, candidate.height]
    rounded = [int(round(float(value))) for value in values]
    if any(abs(float(value) - integer) > 1e-6 for value, integer in zip(values, rounded)):
        raise OpticalPairEvidenceError("AOI does not align to the source raster grid")
    return Window(*rounded)


def summarize_scl(values: np.ndarray) -> dict[str, Any]:
    if values.ndim != 2 or values.size == 0:
        raise OpticalPairEvidenceError("SCL crop must be a non-empty 2D array")
    unique, counts = np.unique(values, return_counts=True)
    observed = {int(value): int(count) for value, count in zip(unique, counts)}
    if any(value not in SCL_CLASSES for value in observed):
        raise OpticalPairEvidenceError("SCL crop contains an unknown class")
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
    excluded = sum(observed.get(value, 0) for value in EXCLUDED_SCL)
    review = sum(observed.get(value, 0) for value in REVIEW_SCL)
    eligible = sum(observed.get(value, 0) for value in ELIGIBLE_SCL)
    return {
        "pixel_count": total,
        "classes": rows,
        "excluded_pixels": excluded,
        "excluded_percent": round(100 * excluded / total, 4),
        "review_needed_pixels": review,
        "review_needed_percent": round(100 * review / total, 4),
        "eligible_land_pixels": eligible,
        "eligible_land_percent": round(100 * eligible / total, 4),
    }


def classify_pair_quality(pre_scl: np.ndarray, post_scl: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    if pre_scl.shape != post_scl.shape:
        raise OpticalPairEvidenceError("pre/post SCL arrays are not aligned")
    if any(int(value) not in SCL_CLASSES for value in np.unique(pre_scl)):
        raise OpticalPairEvidenceError("pre SCL contains an unknown class")
    if any(int(value) not in SCL_CLASSES for value in np.unique(post_scl)):
        raise OpticalPairEvidenceError("post SCL contains an unknown class")
    excluded = np.isin(pre_scl, list(EXCLUDED_SCL)) | np.isin(post_scl, list(EXCLUDED_SCL))
    review = (~excluded) & (
        np.isin(pre_scl, list(REVIEW_SCL)) | np.isin(post_scl, list(REVIEW_SCL))
    )
    eligible = (~excluded) & (~review)
    if np.any(eligible & ~(
        np.isin(pre_scl, list(ELIGIBLE_SCL)) & np.isin(post_scl, list(ELIGIBLE_SCL))
    )):
        raise OpticalPairEvidenceError("pair quality contains an unclassified state")
    state = np.full(pre_scl.shape, 2, dtype=np.uint8)
    state[review] = 1
    state[eligible] = 0
    counts = Counter(int(item) for item in state.reshape(-1))
    total = int(state.size)
    rows = [
        {
            "state": name,
            "code": code,
            "pixels": counts.get(code, 0),
            "percent": round(100 * counts.get(code, 0) / total, 4),
        }
        for code, name in ((0, "eligible-comparison"), (1, "review-needed"), (2, "excluded"))
    ]
    return state, {"pixel_count": total, "states": rows}


def _percentiles(values: np.ndarray) -> dict[str, float | None]:
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return {key: None for key in ("min", "p05", "p25", "median", "p75", "p95", "max")}
    percentiles = np.percentile(finite, [0, 5, 25, 50, 75, 95, 100])
    return {
        key: round(float(value), 6)
        for key, value in zip(("min", "p05", "p25", "median", "p75", "p95", "max"), percentiles)
    }


def _product_metadata(
    archive: zipfile.ZipFile,
    names: list[str],
    expected_safe: str,
) -> dict[str, Any]:
    product_member = _exact_member(names, "/MTD_MSIL2A.xml")
    tile_member = _exact_member(names, "/MTD_TL.xml")
    product = _parse_xml(archive, product_member)
    tile = _parse_xml(archive, tile_member)
    uri = _exact_text(product, "PRODUCT_URI")
    baseline = _exact_text(product, "PROCESSING_BASELINE")
    if uri != expected_safe:
        raise OpticalPairEvidenceError("product metadata SAFE identity mismatch")
    if baseline != "05.10":
        raise OpticalPairEvidenceError("product processing baseline is not 05.10")
    spectral = {
        item.attrib.get("physicalBand"): item.attrib.get("bandId")
        for item in _elements(product, "Spectral_Information")
    }
    offsets = {
        item.attrib.get("band_id"): float((item.text or "").strip())
        for item in _elements(product, "BOA_ADD_OFFSET")
    }
    band_offsets: dict[str, float] = {}
    for band in SELECTED_BANDS:
        band_id = spectral.get(PHYSICAL_BANDS[band])
        if band_id is None or band_id not in offsets:
            raise OpticalPairEvidenceError(f"missing BOA offset for {band}")
        band_offsets[band] = offsets[band_id]
    quantification = float(_exact_text(product, "BOA_QUANTIFICATION_VALUE"))
    if quantification != 10_000 or any(value != -1000 for value in band_offsets.values()):
        raise OpticalPairEvidenceError("unexpected BOA scaling contract")
    special_text = [(item.text or "").strip() for item in _elements(product, "SPECIAL_VALUE_TEXT")]
    special_index = [int((item.text or "").strip()) for item in _elements(product, "SPECIAL_VALUE_INDEX")]
    special = dict(zip(special_text, special_index))
    if special.get("NODATA") != 0 or special.get("SATURATED") != 65535:
        raise OpticalPairEvidenceError("unexpected special pixel values")
    return {
        "product_metadata_member": product_member,
        "tile_metadata_member": tile_member,
        "product_uri": uri,
        "processing_baseline": baseline,
        "product_start_utc": _exact_text(product, "PRODUCT_START_TIME"),
        "generation_utc": _exact_text(product, "GENERATION_TIME"),
        "tile_id": _exact_text(tile, "TILE_ID"),
        "sensing_time_utc": _exact_text(tile, "SENSING_TIME"),
        "horizontal_crs": _exact_text(tile, "HORIZONTAL_CS_CODE"),
        "boa_quantification_value": quantification,
        "boa_offsets": band_offsets,
        "nodata_dn": special["NODATA"],
        "saturated_dn": special["SATURATED"],
    }


def _read_raster(
    archive_path: Path,
    member: str,
    aoi_bounds: list[float],
    *,
    resolution: int,
    expected_count: int,
    expected_dtype: str,
) -> tuple[np.ndarray, dict[str, Any]]:
    archive_uri = archive_path.resolve().as_posix()
    with rasterio.open(f"zip://{archive_uri}!{member}") as source:
        if source.driver != "JP2OpenJPEG":
            raise OpticalPairEvidenceError("unexpected Sentinel raster driver")
        if source.count != expected_count or source.dtypes != (expected_dtype,) * expected_count:
            raise OpticalPairEvidenceError("unexpected Sentinel raster band/dtype contract")
        if source.crs is None or source.crs.to_epsg() != 32610:
            raise OpticalPairEvidenceError("Sentinel raster CRS is not EPSG:32610")
        if abs(source.transform.a - resolution) > 1e-9 or abs(source.transform.e + resolution) > 1e-9:
            raise OpticalPairEvidenceError("Sentinel raster resolution mismatch")
        window = _integer_window(aoi_bounds, source.transform)
        values = source.read(window=window)
        observed_bounds = [round(float(value), 3) for value in source.window_bounds(window)]
        if observed_bounds != [round(value, 3) for value in aoi_bounds]:
            raise OpticalPairEvidenceError("Sentinel raster AOI bounds mismatch")
        metadata = {
            "member": member,
            "driver": source.driver,
            "crs": source.crs.to_string(),
            "source_width": source.width,
            "source_height": source.height,
            "source_count": source.count,
            "source_dtype": list(source.dtypes),
            "source_transform": [round(float(value), 9) for value in source.transform[:6]],
            "aoi_window": {
                "column_offset": int(window.col_off),
                "row_offset": int(window.row_off),
                "width": int(window.width),
                "height": int(window.height),
            },
            "aoi_bounds_utm10n": observed_bounds,
            "observed_min": int(values.min()),
            "observed_max": int(values.max()),
        }
    return values, metadata


def _read_scene(
    package: Path,
    contract_index: int,
    aoi_bounds: list[float],
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    contract = OPTICAL_CONTRACTS[contract_index]
    archive_path = package / contract.expected_filename
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        product = _product_metadata(archive, names, contract.native_id)
    members = {
        "TCI": _exact_member(names, "_TCI_10m.jp2"),
        "B04": _exact_member(names, "_B04_20m.jp2"),
        "B8A": _exact_member(names, "_B8A_20m.jp2"),
        "B12": _exact_member(names, "_B12_20m.jp2"),
        "SCL": _exact_member(names, "_SCL_20m.jp2"),
    }
    tci, tci_meta = _read_raster(
        archive_path,
        members["TCI"],
        aoi_bounds,
        resolution=10,
        expected_count=3,
        expected_dtype="uint8",
    )
    arrays: dict[str, np.ndarray] = {"TCI": tci}
    raster_meta: dict[str, Any] = {"TCI": tci_meta}
    for band in SELECTED_BANDS:
        values, metadata = _read_raster(
            archive_path,
            members[band],
            aoi_bounds,
            resolution=20,
            expected_count=1,
            expected_dtype="uint16",
        )
        arrays[band] = values[0]
        raster_meta[band] = metadata
    scl, scl_meta = _read_raster(
        archive_path,
        members["SCL"],
        aoi_bounds,
        resolution=20,
        expected_count=1,
        expected_dtype="uint8",
    )
    arrays["SCL"] = scl[0]
    raster_meta["SCL"] = scl_meta
    if tci.shape != (3, 900, 1200):
        raise OpticalPairEvidenceError("true-color AOI crop is not 3 x 900 x 1200")
    if any(arrays[name].shape != (450, 600) for name in (*SELECTED_BANDS, "SCL")):
        raise OpticalPairEvidenceError("20 m AOI crop is not 450 x 600")
    transforms = {tuple(raster_meta[name]["source_transform"]) for name in (*SELECTED_BANDS, "SCL")}
    if len(transforms) != 1:
        raise OpticalPairEvidenceError("20 m source grids are not aligned")
    return (
        {
            "role": contract.role,
            "source_record_id": contract.source_record_id,
            "provider_id": contract.provider_id,
            "native_id": contract.native_id,
            "filename": contract.expected_filename,
            "product_metadata": product,
            "rasters": raster_meta,
            "scl_summary": summarize_scl(arrays["SCL"]),
        },
        arrays,
    )


def _reflectance(scene: dict[str, Any], arrays: dict[str, np.ndarray], band: str) -> tuple[np.ndarray, np.ndarray]:
    metadata = scene["product_metadata"]
    values = arrays[band]
    valid = (values != metadata["nodata_dn"]) & (values != metadata["saturated_dn"])
    reflectance = np.full(values.shape, np.nan, dtype=np.float32)
    reflectance[valid] = (
        values[valid].astype(np.float32) + metadata["boa_offsets"][band]
    ) / metadata["boa_quantification_value"]
    return reflectance, valid


def _nbr(scene: dict[str, Any], arrays: dict[str, np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    nir, nir_valid = _reflectance(scene, arrays, "B8A")
    swir, swir_valid = _reflectance(scene, arrays, "B12")
    denominator = nir + swir
    valid = nir_valid & swir_valid & np.isfinite(denominator) & (np.abs(denominator) > 1e-6)
    result = np.full(nir.shape, np.nan, dtype=np.float32)
    result[valid] = (nir[valid] - swir[valid]) / denominator[valid]
    return result, valid


def _label_protocol() -> dict[str, Any]:
    return {
        "version": LABEL_PROTOCOL_VERSION,
        "implemented": False,
        "target": TARGET_VERSION,
        "final_target_values": {"background": 0, "burned": 1},
        "companion_state_required": True,
        "states": [
            {
                "state": "burned",
                "target_value": 1,
                "rule": "Requires accepted pre/post optical change, visible boundary review, valid quality, temporal plausibility, and independent approval; no single SCL, index, VIIRS, or perimeter signal is sufficient.",
            },
            {
                "state": "background-candidate",
                "target_value": 0,
                "rule": "Requires clear observable land and affirmative unchanged/unburned support; outside a perimeter, absent hotspot evidence, or low change alone is insufficient.",
            },
            {
                "state": "unknown",
                "target_value": None,
                "rule": "Use when valid observations remain insufficient, temporally ambiguous, mixed, or conflicting; exclude from loss and metrics.",
            },
            {
                "state": "excluded",
                "target_value": None,
                "rule": "Use for no data, saturation/defect, shadow, cloud/cirrus, snow/ice, water, failed registration, or disallowed processing states; never convert to background.",
            },
            {
                "state": "review-needed",
                "target_value": None,
                "rule": "Use for SCL 7 unclassified, borderline change, boundary/mixed pixels, smoke or atmosphere concerns, local registration doubt, source disagreement, and protocol exceptions until resolved.",
            },
        ],
        "scl_rules": {
            "eligible_comparison": [4, 5],
            "review_needed": [7],
            "excluded": sorted(EXCLUDED_SCL),
            "note": "Baseline 05.10 SCL 2 is shadow; burned dark features can occur in SCL 7 unclassified. SCL is a quality aid, not truth.",
        },
        "registration": {
            "source_grid": "Require exact EPSG:32610 20 m grid equality before comparison; this pair uses no reprojection or resampling for B04/B8A/B12/SCL evidence.",
            "content_residual_gate": "Before label construction, measure local content registration and require residual <= 0.5 native 20 m pixel (10 m); otherwise remediate or exclude.",
            "boundary_review": "Keep at least a one-native-pixel review band around candidate class transitions and uncertain edges.",
        },
        "temporal_leakage": {
            "group_before_tiling": "Any future split must group by incident/event, scene pair, geography, and time before patches are generated.",
            "darlene_pair_limit": "This single event cannot independently populate train, validation, and test groups.",
            "reference_separation": "Post-event imagery and later incident references used to construct labels cannot become evaluation inputs or method-selection evidence for the same held-out group.",
        },
        "independent_qa": {
            "required": True,
            "rule": "A later label checkpoint requires a second review pass independent of the initial proposal, explicit disagreement state, boundary review, and an audit sample of burned, background, unknown, excluded, and review-needed regions.",
        },
    }


def _iter_polygon_rings(geometry: dict[str, Any]) -> Iterable[list[list[float]]]:
    if geometry["type"] == "Polygon":
        polygons = [geometry["coordinates"]]
    elif geometry["type"] == "MultiPolygon":
        polygons = geometry["coordinates"]
    else:
        raise OpticalPairEvidenceError("reference geometry must be Polygon or MultiPolygon")
    for polygon in polygons:
        for ring in polygon:
            yield ring


def _dnbr_rgb(dnbr: np.ndarray, quality_state: np.ndarray) -> np.ndarray:
    if dnbr.shape != quality_state.shape or dnbr.ndim != 2:
        raise OpticalPairEvidenceError("dNBR and pair-quality arrays must be aligned 2D arrays")
    if np.any(~np.isin(quality_state, [0, 1, 2])):
        raise OpticalPairEvidenceError("pair-quality array contains an unknown state")
    clipped = np.clip(dnbr, -0.5, 0.8)
    safe = np.where(np.isfinite(clipped), clipped, 0.0)
    normalized = (safe + 0.5) / 1.3
    stops = np.array(
        [
            [34, 94, 168],
            [137, 190, 178],
            [242, 239, 221],
            [238, 154, 74],
            [151, 48, 31],
        ],
        dtype=np.float32,
    )
    scaled = normalized * (len(stops) - 1)
    lower = np.floor(scaled).astype(np.int16)
    lower = np.clip(lower, 0, len(stops) - 2)
    weight = (scaled - lower)[..., None]
    rgb = stops[lower] * (1 - weight) + stops[lower + 1] * weight
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    invalid = ~np.isfinite(dnbr)
    rgb[invalid | (quality_state == 2)] = np.array([78, 84, 82], dtype=np.uint8)
    review = (quality_state == 1) & ~invalid
    rgb[review] = (
        0.65 * rgb[review].astype(np.float32) + 0.35 * np.array([128, 56, 128])
    ).astype(np.uint8)
    return rgb


def _screen_ring(
    ring: list[list[float]],
    bounds: list[float],
    box: tuple[int, int, int, int],
) -> list[tuple[float, float]]:
    west, south, east, north = bounds
    left, top, right, bottom = box
    return [
        (
            left + (point[0] - west) / (east - west) * (right - left),
            top + (north - point[1]) / (north - south) * (bottom - top),
        )
        for point in ring
    ]


def render_png(
    report: dict[str, Any],
    pre_rgb: np.ndarray,
    post_rgb: np.ndarray,
    dnbr: np.ndarray,
    quality_state: np.ndarray,
    reference_geometry_utm: dict[str, Any],
    path: Path,
) -> None:
    canvas = Image.new("RGB", (1800, 1250), "#f4f0e8")
    draw = ImageDraw.Draw(canvas)
    ink = "#15211d"
    muted = "#5d6b64"
    teal = "#006b64"
    orange = "#f05a28"
    panel = "#fffdf8"
    draw.rectangle((0, 0, 1800, 170), fill="#132a26")
    draw.text((65, 35), "BURNLENS / EXACT OPTICAL PAIR", fill="#b9d8cf", font=_font(22))
    draw.text((65, 75), "PRE / POST PIXELS + LABEL PROTOCOL", fill="white", font=_font(38))
    draw.text((1390, 44), "DECISION", fill="#b9d8cf", font=_font(18))
    decision_label = {
        "ACCEPT_OPTICAL_PAIR_FOR_PROTOCOL_DEFER_LABELS": "PAIR ACCEPTED",
        "REJECT_OPTICAL_PAIR_REMEDIATE": "PAIR REJECTED",
        "PENDING_VISUAL_REVIEW": "REVIEW PENDING",
    }[report["decision"]]
    draw.text((1390, 78), decision_label, fill="#ffd166", font=_font(28))
    draw.text((1390, 123), "labels not created", fill="white", font=_font(18))

    boxes = [(55, 225, 575, 615), (640, 225, 1160, 615), (1225, 225, 1745, 615)]
    images = [
        Image.fromarray(np.moveaxis(pre_rgb, 0, 2), mode="RGB"),
        Image.fromarray(np.moveaxis(post_rgb, 0, 2), mode="RGB"),
        Image.fromarray(_dnbr_rgb(dnbr, quality_state), mode="RGB"),
    ]
    titles = [
        "PRE / 2024-06-25 18:59 UTC",
        "POST / 2024-07-05 18:59 UTC",
        "CONTINUOUS dNBR / PRE - POST",
    ]
    subtitles = ["Sentinel-2A true color / 10 m", "Sentinel-2A true color / 10 m", "20 m; purple = review; gray = excluded"]
    for box, image, title, subtitle in zip(boxes, images, titles, subtitles):
        image = image.resize((box[2] - box[0], box[3] - box[1]), Image.Resampling.LANCZOS)
        canvas.paste(image, (box[0], box[1]))
        for ring in _iter_polygon_rings(reference_geometry_utm):
            draw.line(_screen_ring(ring, report["aoi"]["bbox_utm10n"], box), fill="#55e6d1", width=3)
        draw.rectangle(box, outline="#132a26", width=3)
        draw.rectangle((box[0], box[1], box[2], box[1] + 68), fill="#132a26")
        draw.text((box[0] + 18, box[1] + 12), title, fill="white", font=_font(19))
        draw.text((box[0] + 18, box[1] + 40), subtitle, fill="#b9d8cf", font=_font(15))

    quality = {item["state"]: item for item in report["pair_quality"]["states"]}
    cards = [
        ("SAME GRID", "S2A / T10TFP / R013 / PB05.10", teal),
        (f"{quality['eligible-comparison']['percent']:.2f}%", "eligible comparison pixels", teal),
        (f"{quality['review-needed']['percent']:.2f}%", "review-needed pixels", "#7e3f8f"),
        (f"{quality['excluded']['percent']:.2f}%", "excluded pair pixels", orange),
    ]
    left = 55
    for value, label, color in cards:
        draw.rounded_rectangle((left, 655, left + 400, 785), radius=16, fill=panel, outline="#d4cec1", width=2)
        draw.text((left + 24, 680), value, fill=color, font=_font(30))
        draw.text((left + 24, 731), label, fill=muted, font=_font(17))
        left += 430

    draw.rounded_rectangle((55, 825, 1745, 1110), radius=18, fill="#e5efeb", outline="#aac8bf", width=2)
    draw.text((82, 850), "FIVE-STATE BINARY LABEL CONTRACT / DESIGN ONLY", fill=teal, font=_font(22))
    states = report["label_protocol"]["states"]
    column_width = 320
    for index, item in enumerate(states):
        x = 82 + index * column_width
        draw.text((x, 900), item["state"].upper(), fill=ink, font=_font(18))
        summary = {
            "burned": "1 only after\nindependent approval",
            "background-candidate": "0 only after\naffirmative support",
            "unknown": "ignored; evidence\ninsufficient",
            "excluded": "ignored; quality or\nregistration invalid",
            "review-needed": "unresolved; never\nsilently background",
        }[item["state"]]
        draw.multiline_text((x, 942), summary, fill=muted, font=_font(16), spacing=8)

    draw.text((55, 1140), "Mint outline: later NIFC incident-reference geometry (context only, never a pixel label)", fill=muted, font=_font(16))
    draw.text((55, 1171), "Contains modified Copernicus Sentinel data 2024  |  official sources govern", fill=muted, font=_font(16))
    trace = (
        f"run {report['run_id']} / source {report['git_source_commit'][:12]} / software {report['software_version']} / "
        f"AOI {report['aoi_version']} / protocol {report['label_schema_version']} / dataset none / baseline none / model none"
    )
    draw.text((55, 1202), trace, fill=muted, font=_font(14))
    draw.text((55, 1227), WARNING, fill="#33443e", font=_font(13))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], png_name: str, path: Path) -> None:
    decision_summary = {
        "ACCEPT_OPTICAL_PAIR_FOR_PROTOCOL_DEFER_LABELS": (
            "Pair accepted for protocol evidence; label pixels remain uncreated."
        ),
        "REJECT_OPTICAL_PAIR_REMEDIATE": (
            "Pair rejected after visual review; label pixels remain uncreated."
        ),
        "PENDING_VISUAL_REVIEW": (
            "Machine checks passed; visual review remains pending and label pixels remain uncreated."
        ),
    }[report["decision"]]
    quality_rows = "".join(
        f"<tr><td>{escape(item['state'])}</td><td>{item['pixels']:,}</td><td>{item['percent']:.4f}%</td></tr>"
        for item in report["pair_quality"]["states"]
    )
    protocol_rows = "".join(
        "<tr>"
        f"<td><strong>{escape(item['state'])}</strong></td>"
        f"<td>{'ignored' if item['target_value'] is None else item['target_value']}</td>"
        f"<td>{escape(item['rule'])}</td>"
        "</tr>"
        for item in report["label_protocol"]["states"]
    )
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens exact optical pair evidence</title><style>
:root {{ color-scheme:light; --ink:#15211d; --muted:#5d6b64; --paper:#f4f0e8; --panel:#fffdf8; --teal:#006b64; --orange:#f05a28; }}
* {{ box-sizing:border-box; }} body {{ margin:0; background:var(--paper); color:var(--ink); font:16px/1.55 system-ui,sans-serif; }}
header {{ background:#132a26; color:white; padding:3rem max(5vw,2rem); }} header p {{ color:#b9d8cf; margin:.3rem 0; }}
main {{ max-width:1200px; margin:auto; padding:2.5rem 1.5rem 5rem; }} .warning {{ background:#fff1ca; border-left:6px solid #d87618; padding:1rem 1.2rem; font-weight:650; }}
.hero {{ display:block; width:100%; height:auto; border:1px solid #c8c0b2; margin:1.5rem 0; }} .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:1rem; }}
.card {{ background:var(--panel); border:1px solid #d9d1c4; border-radius:12px; padding:1.2rem; }} .decision {{ border:2px solid var(--orange); }}
.value {{ color:var(--teal); font-size:2rem; font-weight:800; }} table {{ width:100%; border-collapse:collapse; background:var(--panel); }}
th,td {{ padding:.75rem; border-bottom:1px solid #ddd5c9; text-align:left; vertical-align:top; }} code {{ overflow-wrap:anywhere; }} h2 {{ margin-top:2.4rem; }}
</style></head><body><header><p>BurnLens / Phase Two / exact source evidence</p><h1>Same-orbit pre/post optical pair</h1><p>{escape(decision_summary)}</p></header><main>
<p class="warning">{escape(WARNING)}</p><img class="hero" src="{escape(png_name)}" alt="Pre and post Sentinel-2 images with a continuous dNBR evidence view and five-state label protocol">
<section class="card decision"><h2>Decision</h2><p><strong>{escape(report['decision'])}</strong></p><p>{escape(report['decision_detail'])}</p></section>
<div class="grid"><div class="card"><div class="value">same orbit</div><div>Sentinel-2A / tile 10TFP / relative orbit 13 / baseline 05.10</div></div>
<div class="card"><div class="value">20 m native</div><div>B04, B8A, B12, and SCL comparison with no reprojection or upsampling</div></div>
<div class="card"><div class="value">0 labels</div><div>No label array, dataset, split, baseline mask, model, or analytical metric was created</div></div></div>
<h2>Pair-quality states</h2><table><thead><tr><th>State</th><th>Pixels</th><th>AOI share</th></tr></thead><tbody>{quality_rows}</tbody></table>
<h2>Five-state label protocol</h2><p>This is a versioned design gate, not an implemented annotation schema or label set. Unknown, excluded, and review-needed pixels remain outside binary loss and metrics.</p>
<table><thead><tr><th>State</th><th>Future target value</th><th>Rule</th></tr></thead><tbody>{protocol_rows}</tbody></table>
<h2>Registration, leakage, and review</h2><div class="card"><ul>
<li>{escape(report['label_protocol']['registration']['source_grid'])}</li><li>{escape(report['label_protocol']['registration']['content_residual_gate'])}</li>
<li>{escape(report['label_protocol']['temporal_leakage']['group_before_tiling'])}</li><li>{escape(report['label_protocol']['temporal_leakage']['darlene_pair_limit'])}</li>
<li>{escape(report['label_protocol']['independent_qa']['rule'])}</li></ul></div>
<h2>Traceability</h2><div class="card"><p><strong>Run:</strong> <code>{escape(report['run_id'])}</code><br><strong>Git source:</strong> <code>{escape(report['git_source_commit'])}</code><br>
<strong>Software / report:</strong> <code>{escape(report['software_version'])}</code> / <code>{escape(report['report_version'])}</code><br><strong>AOI / target / protocol:</strong> <code>{escape(report['aoi_version'])}</code> / <code>{escape(report['target_version'])}</code> / <code>{escape(report['label_schema_version'])}</code><br>
<strong>Package / contract:</strong> <code>{escape(report['package_id'])}</code> / <code>{escape(report['package_contract_version'])}</code><br><strong>Sources:</strong> SOURCE-2026-009, SOURCE-2026-010; terms {escape(report['terms_review_id'])}<br>
<strong>Application / dataset / baseline / model:</strong> none / none / none / none</p></div>
<h2>Source and use notes</h2><ul><li>Contains modified Copernicus Sentinel data 2024.</li><li>The mint outline is later NIFC incident-reference geometry, not truth.</li>
<li>Continuous dNBR and SCL are evidence for review, not automatic labels or severity.</li><li>Official sources govern over every BurnLens-derived artifact.</li></ul>
</main></body></html>"""
    _write_utf8_lf(path, document)


def build_report(
    *,
    package: Path,
    aoi_report_path: Path,
    reference_geojson_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    visual_review_decision: str,
    visual_review_notes: str,
) -> tuple[dict[str, Any], dict[str, np.ndarray], dict[str, Any]]:
    verification = verify_registered_package(
        package,
        OPTICAL_CONTRACTS,
        contract_validator=validate_optical_contracts,
        contract_version=CONTRACT_VERSION,
    )
    if not verification["accepted_as_unchanged_registered_package"]:
        raise OpticalPairEvidenceError("registered optical pair verification failed")
    aoi = json.loads(aoi_report_path.read_text(encoding="utf-8"))
    reference = json.loads(reference_geojson_path.read_text(encoding="utf-8"))
    if aoi.get("aoi_version") != AOI_VERSION:
        raise OpticalPairEvidenceError("unexpected AOI version")
    if len(reference.get("features") or []) != 1:
        raise OpticalPairEvidenceError("expected exactly one NIFC reference feature")
    aoi_bounds = [float(value) for value in aoi["derivation"]["aoi_bbox_utm10n"]]
    pre_scene, pre = _read_scene(package, 0, aoi_bounds)
    post_scene, post = _read_scene(package, 1, aoi_bounds)
    for name in ("TCI", *SELECTED_BANDS, "SCL"):
        if pre_scene["rasters"][name]["aoi_bounds_utm10n"] != post_scene["rasters"][name]["aoi_bounds_utm10n"]:
            raise OpticalPairEvidenceError(f"pre/post {name} bounds differ")
        if pre_scene["rasters"][name]["source_transform"] != post_scene["rasters"][name]["source_transform"]:
            raise OpticalPairEvidenceError(f"pre/post {name} transforms differ")
    pair_state, pair_quality = classify_pair_quality(pre["SCL"], post["SCL"])
    pre_nbr, pre_valid = _nbr(pre_scene, pre)
    post_nbr, post_valid = _nbr(post_scene, post)
    dnbr = pre_nbr - post_nbr
    numeric_valid = pre_valid & post_valid & np.isfinite(dnbr)
    dnbr[~numeric_valid] = np.nan
    eligible = numeric_valid & (pair_state == 0)
    review = numeric_valid & (pair_state == 1)
    excluded = pair_state == 2
    total = int(pair_state.size)
    if visual_review_decision not in {
        "ACCEPT_OPTICAL_PAIR_FOR_PROTOCOL_DEFER_LABELS",
        "REJECT_OPTICAL_PAIR_REMEDIATE",
        "PENDING_VISUAL_REVIEW",
    }:
        raise OpticalPairEvidenceError("invalid visual review decision")
    if visual_review_decision != "PENDING_VISUAL_REVIEW" and not visual_review_notes.strip():
        raise OpticalPairEvidenceError("final visual review requires notes")
    reference_utm = transform_geom(
        "EPSG:4326",
        "EPSG:32610",
        reference["features"][0]["geometry"],
        precision=3,
    )
    decision_detail = {
        "PENDING_VISUAL_REVIEW": (
            "The two exact native products and grids pass machine checks. A human-readable visual review "
            "of pre/post pixels, continuous dNBR, and quality states is still required before acceptance."
        ),
        "ACCEPT_OPTICAL_PAIR_FOR_PROTOCOL_DEFER_LABELS": (
            "Accept the exact same-orbit pair as legally usable, readable source evidence for the burn-scar "
            "label protocol. Continuous spectral change and later incident-reference context are visibly useful, "
            "but neither is truth. Label construction, content-registration measurement, independent annotation "
            "QA, a dataset, and a baseline remain separate gates."
        ),
        "REJECT_OPTICAL_PAIR_REMEDIATE": (
            "Reject the pair for label-protocol use after visual review. Preserve the source evidence and remediate "
            "the recorded quality or interpretability weakness before label construction."
        ),
    }[visual_review_decision]
    report: dict[str, Any] = {
        "report_id": REPORT_ID,
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 343,
        "branch": "codex/p2o2-t06-optical-pair-protocol",
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": None,
        "aoi_version": AOI_VERSION,
        "target_version": TARGET_VERSION,
        "dataset_version": None,
        "label_schema_version": LABEL_PROTOCOL_VERSION,
        "label_schema_implemented": False,
        "baseline_version": None,
        "model_version": None,
        "package_id": PACKAGE_ID,
        "package_contract_version": CONTRACT_VERSION,
        "package_verification": verification,
        "terms_review_id": TERMS_REVIEW_ID,
        "input_hashes": {
            "aoi_report_sha256_lf_normalized": _sha256_lf_text(aoi_report_path),
            "reference_geojson_sha256_lf_normalized": _sha256_lf_text(reference_geojson_path),
        },
        "aoi": {
            "bbox_utm10n": aoi_bounds,
            "bbox_wgs84": aoi["derivation"]["aoi_bbox_wgs84"],
            "width_m": 12_000,
            "height_m": 9_000,
            "area_km2": 108.0,
        },
        "pre_scene": pre_scene,
        "post_scene": post_scene,
        "pair_identity": {
            "same_platform": True,
            "same_tile": True,
            "same_relative_orbit": True,
            "same_processing_baseline": True,
            "native_20m_grid_equal": True,
            "reprojection_performed": False,
            "resampling_performed_for_spectral_comparison": False,
            "elapsed_seconds": 863_980.0,
        },
        "pair_quality": pair_quality,
        "continuous_spectral_evidence": {
            "index": "dNBR = pre NBR - post NBR",
            "nir_band": "B8A at native 20 m",
            "swir_band": "B12 at native 20 m",
            "label_or_severity_interpretation_allowed": False,
            "numeric_valid_pixels": int(numeric_valid.sum()),
            "numeric_valid_percent": round(100 * numeric_valid.sum() / total, 4),
            "eligible_comparison_dnbr": _percentiles(dnbr[eligible]),
            "review_needed_dnbr": _percentiles(dnbr[review]),
            "excluded_pixels": int(excluded.sum()),
            "interpretation": (
                "Positive and negative dNBR are continuous change evidence only. Values can reflect vegetation, "
                "moisture, atmosphere, soil, mixed pixels, registration, or fire effects and are not thresholded here."
            ),
        },
        "label_protocol": _label_protocol(),
        "visual_review": {
            "decision": visual_review_decision,
            "notes": visual_review_notes,
            "rendered_source_pixels_reviewed": visual_review_decision != "PENDING_VISUAL_REVIEW",
        },
        "decision": visual_review_decision,
        "decision_detail": decision_detail,
        "quality_gates": {
            "registered_pair_reverified": True,
            "provider_md5_and_blake3_reverified": True,
            "safe_archives_and_crc_reverified": True,
            "aoi_exact_native_grids": True,
            "pre_post_20m_grid_equal": True,
            "product_scaling_offsets_parsed": True,
            "real_tci_b04_b8a_b12_scl_read": True,
            "structured_input_hashes_lf_normalized": True,
            "label_array_created": False,
            "dataset_created": False,
            "baseline_created": False,
            "model_created": False,
        },
        "claims": {
            "permitted": [
                "BurnLens acquired and independently reverified the exact same-orbit Sentinel-2 pair.",
                "The real AOI pixels, native grids, SCL quality states, and continuous spectral change are inspectable.",
                "The five-state label protocol is versioned as a design gate and remains unimplemented.",
            ],
            "prohibited": [
                "The dNBR view, SCL, VIIRS observations, or NIFC outline is a burn-scar label or severity map.",
                "The pair establishes a dataset, baseline, model, metric, application, or operational wildfire result.",
                "The evidence is official, emergency-ready, field-validated, endorsed, or suitable for incident decisions.",
            ],
        },
        "limitations": [
            "The approximate incident start time is context and does not prove every pre-scene pixel is unburned.",
            "The post scene is approximately ten days later; non-fire environmental change can contribute to dNBR.",
            "SCL can misclassify shadows, clouds, smoke, water, dark surfaces, and burned features.",
            "Exact grid equality does not prove subpixel content registration; the protocol requires a later residual measurement.",
            "The later NIFC final perimeter is mixed-method incident-reference geometry, not pixel-perfect truth.",
            "One event cannot support leakage-resistant train, validation, and test groups.",
        ],
        "attribution": [
            "Contains modified Copernicus Sentinel data 2024.",
            "NIFC WFIGS final incident-reference feature SOURCE-2026-007.",
        ],
        "source_precedence": "Official sources govern over every BurnLens-derived artifact.",
        "warning": WARNING,
    }
    return report, {"pre_tci": pre["TCI"], "post_tci": post["TCI"], "dnbr": dnbr, "quality": pair_state}, reference_utm


def write_report(
    *,
    report: dict[str, Any],
    arrays: dict[str, np.ndarray],
    reference_geometry_utm: dict[str, Any],
    output_directory: Path,
) -> dict[str, Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    json_path = output_directory / f"{REPORT_ID}.json"
    html_path = output_directory / f"{REPORT_ID}.html"
    png_path = output_directory / f"{REPORT_ID}.png"
    _write_utf8_lf(json_path, json.dumps(report, indent=2) + "\n")
    render_png(
        report,
        arrays["pre_tci"],
        arrays["post_tci"],
        arrays["dnbr"],
        arrays["quality"],
        reference_geometry_utm,
        png_path,
    )
    render_html(report, png_path.name, html_path)
    return {"json": json_path, "html": html_path, "png": png_path}


def inspect_optical_pair(
    *,
    package: Path,
    aoi_report_path: Path,
    reference_geojson_path: Path,
    output_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    visual_review_decision: str,
    visual_review_notes: str,
) -> dict[str, Path]:
    report, arrays, reference = build_report(
        package=package,
        aoi_report_path=aoi_report_path,
        reference_geojson_path=reference_geojson_path,
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
        visual_review_decision=visual_review_decision,
        visual_review_notes=visual_review_notes,
    )
    return write_report(
        report=report,
        arrays=arrays,
        reference_geometry_utm=reference,
        output_directory=output_directory,
    )
