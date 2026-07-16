"""Inspect four registered cross-event Sentinel products at native pixels.

This checkpoint verifies source readability, full-boundary SCL evidence, exact
pair grids, and pair-local content registration.  It does not create labels,
dataset partitions, baseline masks, model outputs, or application claims.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from html import escape
import json
import math
from pathlib import Path
from typing import Any, Iterable
import zipfile

import numpy as np
from PIL import Image, ImageDraw
import rasterio
from rasterio.features import bounds as geometry_bounds, geometry_mask
from rasterio.windows import Window, from_bounds
from rasterio.warp import transform_geom

from .content_registration import (
    MAX_BAND_DEVIATION_PX,
    MAX_RESIDUAL_PX,
    MIN_CONFIDENT_BANDS,
    MIN_PEAK_RATIO,
    MIN_USABLE_FRACTION,
    PIXEL_SIZE_M,
    _gradient_signal,
    _summary as registration_summary,
    estimate_subpixel_shift,
)
from .cross_event_optical_contract import (
    CONTRACT_VERSION,
    CROSS_EVENT_CONTRACTS,
    PACKAGE_ID,
    ROUTE_PRECEDENCE,
    SOFTWARE_VERSION,
    TERMS_REVIEW_ID,
    validate_cross_event_contracts,
)
from .optical_pair_evidence import (
    LABEL_PROTOCOL_VERSION,
    SELECTED_BANDS,
    TARGET_VERSION,
    WARNING,
    OpticalPairEvidenceError,
    _exact_member,
    _font,
    _product_metadata,
    _reflectance,
    _sha256_lf_text,
    _write_utf8_lf,
    classify_pair_quality,
    summarize_scl,
)
from .paired_intake import verify_registered_package


REPORT_ID = "CROSS-EVENT-SOURCE-FITNESS-2026-001"
REPORT_SCHEMA_VERSION = "0.1.0"
REPORT_VERSION = "cross-event-source-fitness-v0.1.0"
PROTOCOL_VERSION = "cross-event-native-source-fitness-v0.1.0"
FEASIBILITY_REPORT_ID = "CROSS-EVENT-FITNESS-2026-001"
EXPECTED_EVENTS = (
    "event-tepee-1144-ne-2018",
    "event-mckay-1035-ne-2017",
)
ROLE_PAIRS = {
    "event-tepee-1144-ne-2018": ("tepee-2018-pre", "tepee-2018-post"),
    "event-mckay-1035-ne-2017": ("mckay-2017-pre", "mckay-2017-post"),
}


class CrossEventSourceFitnessError(OpticalPairEvidenceError):
    """A deterministic, secret-free cross-event source-fitness failure."""


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(payload.encode("utf-8")).hexdigest()


def _load_feasibility(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CrossEventSourceFitnessError("cross-event feasibility report is unreadable") from error
    if not isinstance(report, dict) or report.get("report_id") != FEASIBILITY_REPORT_ID:
        raise CrossEventSourceFitnessError("cross-event feasibility report identity mismatch")
    candidates = report.get("candidate_assessments")
    if not isinstance(candidates, list):
        raise CrossEventSourceFitnessError("cross-event candidate assessments are missing")
    selected = [
        item for item in candidates
        if isinstance(item, dict) and item.get("event_group_id") in EXPECTED_EVENTS and item.get("eligible") is True
    ]
    by_event = {item["event_group_id"]: item for item in selected}
    if tuple(item for item in EXPECTED_EVENTS if item in by_event) != EXPECTED_EVENTS or len(by_event) != 2:
        raise CrossEventSourceFitnessError("frozen Tepee/McKay candidate set mismatch")
    contracts = {item.role: item for item in CROSS_EVENT_CONTRACTS}
    for event_id in EXPECTED_EVENTS:
        candidate = by_event[event_id]
        geometry = candidate.get("source_geometry")
        pair = candidate.get("scene_pair")
        if not isinstance(geometry, dict) or geometry.get("type") not in {"Polygon", "MultiPolygon"}:
            raise CrossEventSourceFitnessError(f"{event_id} source geometry is invalid")
        if not isinstance(pair, dict):
            raise CrossEventSourceFitnessError(f"{event_id} scene pair is missing")
        pre_role, post_role = ROLE_PAIRS[event_id]
        expected_pre = contracts[pre_role].native_id.removesuffix(".SAFE")
        expected_post = contracts[post_role].native_id.removesuffix(".SAFE")
        if pair.get("pre_scene", {}).get("id") != expected_pre or pair.get("post_scene", {}).get("id") != expected_post:
            raise CrossEventSourceFitnessError(f"{event_id} frozen scene identities mismatch")
    return report, [by_event[event_id] for event_id in EXPECTED_EVENTS]


def _covering_window(bounds: tuple[float, float, float, float], transform: Any, width: int, height: int) -> Window:
    candidate = from_bounds(*bounds, transform=transform)
    left = max(0, math.floor(float(candidate.col_off)))
    top = max(0, math.floor(float(candidate.row_off)))
    right = min(width, math.ceil(float(candidate.col_off + candidate.width)))
    bottom = min(height, math.ceil(float(candidate.row_off + candidate.height)))
    if right <= left or bottom <= top:
        raise CrossEventSourceFitnessError("event boundary does not intersect the source raster")
    return Window(left, top, right - left, bottom - top)


def _read_member(
    archive_path: Path,
    member: str,
    geometry_utm: dict[str, Any],
    *,
    resolution: int,
    count: int,
    dtype: str,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    uri = archive_path.resolve().as_posix()
    with rasterio.open(f"zip://{uri}!{member}") as source:
        if source.driver != "JP2OpenJPEG":
            raise CrossEventSourceFitnessError("unexpected Sentinel raster driver")
        if source.crs is None or source.crs.to_epsg() != 32610:
            raise CrossEventSourceFitnessError("Sentinel raster CRS is not EPSG:32610")
        if source.count != count or source.dtypes != (dtype,) * count:
            raise CrossEventSourceFitnessError("unexpected Sentinel raster band/dtype contract")
        if abs(source.transform.a - resolution) > 1e-9 or abs(source.transform.e + resolution) > 1e-9:
            raise CrossEventSourceFitnessError("Sentinel raster resolution mismatch")
        window = _covering_window(geometry_bounds(geometry_utm), source.transform, source.width, source.height)
        values = source.read(window=window)
        crop_transform = source.window_transform(window)
        inside = geometry_mask(
            [geometry_utm],
            out_shape=(int(window.height), int(window.width)),
            transform=crop_transform,
            invert=True,
            all_touched=False,
        )
        if not np.any(inside):
            raise CrossEventSourceFitnessError("event boundary contains no source pixel centers")
        observed_bounds = [round(float(value), 3) for value in source.window_bounds(window)]
        metadata = {
            "member": member,
            "driver": source.driver,
            "crs": source.crs.to_string(),
            "resolution_m": resolution,
            "source_width": source.width,
            "source_height": source.height,
            "source_count": source.count,
            "source_dtype": list(source.dtypes),
            "source_transform": [round(float(value), 9) for value in source.transform[:6]],
            "crop_transform": [round(float(value), 9) for value in crop_transform[:6]],
            "crop_window": {
                "column_offset": int(window.col_off),
                "row_offset": int(window.row_off),
                "width": int(window.width),
                "height": int(window.height),
            },
            "crop_bounds_utm10n": observed_bounds,
            "boundary_pixel_rule": "pixel center inside full MTBS source geometry; no boundary shrink",
            "inside_boundary_pixels": int(inside.sum()),
            "observed_inside_min": int(values[:, inside].min()),
            "observed_inside_max": int(values[:, inside].max()),
        }
    return values, inside, metadata


def _read_product(package: Path, contract: Any, geometry_wgs84: dict[str, Any]) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    archive_path = package / contract.expected_filename
    geometry_utm = transform_geom("EPSG:4326", "EPSG:32610", geometry_wgs84, precision=9)
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        product = _product_metadata(
            archive,
            names,
            contract.native_id,
            expected_processing_baseline="05.00",
        )
    members = {
        "TCI": _exact_member(names, "_TCI_10m.jp2"),
        "B04": _exact_member(names, "_B04_20m.jp2"),
        "B8A": _exact_member(names, "_B8A_20m.jp2"),
        "B12": _exact_member(names, "_B12_20m.jp2"),
        "SCL": _exact_member(names, "_SCL_20m.jp2"),
    }
    arrays: dict[str, np.ndarray] = {}
    masks: dict[str, np.ndarray] = {}
    rasters: dict[str, Any] = {}
    for name in ("TCI", *SELECTED_BANDS, "SCL"):
        values, mask, metadata = _read_member(
            archive_path,
            members[name],
            geometry_utm,
            resolution=10 if name == "TCI" else 20,
            count=3 if name == "TCI" else 1,
            dtype="uint8" if name in {"TCI", "SCL"} else "uint16",
        )
        arrays[name] = values if name == "TCI" else values[0]
        masks[name] = mask
        rasters[name] = metadata
    twenty_shapes = {arrays[name].shape for name in (*SELECTED_BANDS, "SCL")}
    twenty_transforms = {tuple(rasters[name]["crop_transform"]) for name in (*SELECTED_BANDS, "SCL")}
    if len(twenty_shapes) != 1 or len(twenty_transforms) != 1:
        raise CrossEventSourceFitnessError("native 20 m product grids are not aligned")
    if any(not np.array_equal(masks["SCL"], masks[name]) for name in SELECTED_BANDS):
        raise CrossEventSourceFitnessError("native 20 m boundary masks are not aligned")
    return {
        "role": contract.role,
        "source_record_id": contract.source_record_id,
        "provider_id": contract.provider_id,
        "native_id": contract.native_id,
        "filename": contract.expected_filename,
        "product_metadata": product,
        "rasters": rasters,
        "scl_summary_inside_full_boundary": summarize_scl(arrays["SCL"][masks["SCL"]].reshape(-1, 1)),
        "boundary_mask": {
            "geometry_sha256": _canonical_sha256(geometry_wgs84),
            "inside_20m_pixel_centers": int(masks["SCL"].sum()),
            "inside_10m_pixel_centers": int(masks["TCI"].sum()),
        },
    }, {**arrays, "MASK20": masks["SCL"], "MASK10": masks["TCI"]}


def _positions(length: int, size: int) -> list[int]:
    if size > length or size < 32:
        raise CrossEventSourceFitnessError("registration crop is too small")
    return sorted({0, (length - size) // 2, length - size})


def registration_window_layout(boundary_mask: np.ndarray) -> list[dict[str, int]]:
    """Return deterministic event-scaled windows intersecting the full boundary."""
    if boundary_mask.ndim != 2 or not np.any(boundary_mask):
        raise CrossEventSourceFitnessError("registration boundary mask is empty")
    height, width = boundary_mask.shape
    size = min(128, height, width)
    if size < 64:
        raise CrossEventSourceFitnessError("full-boundary registration envelope is below 64 pixels")
    windows: list[dict[str, int]] = []
    for row in _positions(height, size):
        for column in _positions(width, size):
            overlap = boundary_mask[row:row + size, column:column + size]
            if int(overlap.sum()) >= 256:
                windows.append({"row_offset": row, "column_offset": column, "height": size, "width": size})
    if not windows:
        raise CrossEventSourceFitnessError("no deterministic registration window intersects the event boundary")
    return windows


def _window_bounds(transform: Any, window: dict[str, int]) -> list[float]:
    west = transform.c + window["column_offset"] * transform.a
    north = transform.f + window["row_offset"] * transform.e
    east = west + window["width"] * transform.a
    south = north + window["height"] * transform.e
    return [round(west, 3), round(south, 3), round(east, 3), round(north, 3)]


def measure_event_registration(
    pre_scene: dict[str, Any],
    pre: dict[str, np.ndarray],
    post_scene: dict[str, Any],
    post: dict[str, np.ndarray],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    mask = pre["MASK20"]
    if not np.array_equal(mask, post["MASK20"]):
        raise CrossEventSourceFitnessError("pre/post full-boundary masks are not aligned")
    for band in (*SELECTED_BANDS, "SCL"):
        if pre[band].shape != post[band].shape or pre[band].shape != mask.shape:
            raise CrossEventSourceFitnessError("pre/post native 20 m crop grids are not aligned")
    pre_grid = pre_scene["rasters"]["B04"]
    post_grid = post_scene["rasters"]["B04"]
    if pre_grid["source_transform"] != post_grid["source_transform"] or pre_grid["crop_transform"] != post_grid["crop_transform"]:
        raise CrossEventSourceFitnessError("pre/post native source transforms differ")

    pair_state, _ = classify_pair_quality(pre["SCL"], post["SCL"])
    quality_counts = Counter(int(value) for value in pair_state[mask])
    inside_count = int(mask.sum())
    pair_quality = {
        "pixel_count_inside_full_boundary": inside_count,
        "states": [
            {
                "state": name,
                "code": code,
                "pixels": quality_counts.get(code, 0),
                "percent": round(100 * quality_counts.get(code, 0) / inside_count, 4),
            }
            for code, name in ((0, "eligible-comparison"), (1, "review-needed"), (2, "excluded"))
        ],
    }
    pre_signals: dict[str, np.ndarray] = {}
    post_signals: dict[str, np.ndarray] = {}
    signal_stats: dict[str, Any] = {}
    for band in SELECTED_BANDS:
        pre_reflectance, _ = _reflectance(pre_scene, pre, band)
        post_reflectance, _ = _reflectance(post_scene, post, band)
        pre_signals[band], pre_stats = _gradient_signal(pre_reflectance)
        post_signals[band], post_stats = _gradient_signal(post_reflectance)
        signal_stats[band] = {"pre": pre_stats, "post": post_stats}

    affine = rasterio.Affine(*pre_grid["crop_transform"])
    windows: list[dict[str, Any]] = []
    for index, window in enumerate(registration_window_layout(mask), start=1):
        rows = slice(window["row_offset"], window["row_offset"] + window["height"])
        columns = slice(window["column_offset"], window["column_offset"] + window["width"])
        inside = mask[rows, columns]
        quality = pair_state[rows, columns][inside]
        eligible_fraction = float(np.mean(quality == 0))
        review_fraction = float(np.mean(quality == 1))
        excluded_fraction = float(np.mean(quality == 2))
        band_results: dict[str, Any] = {}
        confident_vectors: list[list[float]] = []
        for band in SELECTED_BANDS:
            try:
                result = estimate_subpixel_shift(pre_signals[band][rows, columns], post_signals[band][rows, columns])
            except OpticalPairEvidenceError as error:
                band_results[band] = {"confident": False, "reason": str(error)}
                continue
            result["confident"] = result["coarse_peak_ratio"] >= MIN_PEAK_RATIO
            result["reason"] = "PEAK_RATIO_PASS" if result["confident"] else "PEAK_RATIO_BELOW_GATE"
            band_results[band] = result
            if result["confident"]:
                confident_vectors.append([result["row_shift_to_apply_px"], result["column_shift_to_apply_px"]])
        consensus: dict[str, Any] | None = None
        if len(confident_vectors) >= MIN_CONFIDENT_BANDS:
            vectors = np.asarray(confident_vectors, dtype=np.float64)
            median = np.median(vectors, axis=0)
            deviations = np.linalg.norm(vectors - median, axis=1)
            magnitude = float(np.linalg.norm(median))
            consensus = {
                "row_shift_to_apply_px": round(float(median[0]), 4),
                "column_shift_to_apply_px": round(float(median[1]), 4),
                "magnitude_px": round(magnitude, 4),
                "magnitude_m": round(magnitude * PIXEL_SIZE_M, 3),
                "max_band_deviation_px": round(float(np.max(deviations)), 4),
                "confident_band_count": len(confident_vectors),
            }
        if eligible_fraction < MIN_USABLE_FRACTION:
            state, reason = "excluded", "ELIGIBLE_FRACTION_BELOW_GATE"
        elif consensus is None:
            state, reason = "review-needed", "INSUFFICIENT_CONFIDENT_BANDS"
        elif consensus["max_band_deviation_px"] > MAX_BAND_DEVIATION_PX:
            state, reason = "review-needed", "BAND_CONSENSUS_EXCEEDS_GATE"
        elif consensus["magnitude_px"] > MAX_RESIDUAL_PX:
            state, reason = "fail-registration", "CONTENT_RESIDUAL_EXCEEDS_GATE"
        else:
            state, reason = "pass", "CONTENT_REGISTRATION_PASS"
        windows.append({
            "window_id": f"W-{index:02d}",
            "pixel_window": window,
            "bounds_utm10n": _window_bounds(affine, window),
            "inside_boundary_pixels": int(inside.sum()),
            "pair_quality_inside_boundary": {
                "eligible_fraction": round(eligible_fraction, 6),
                "review_needed_fraction": round(review_fraction, 6),
                "excluded_fraction": round(excluded_fraction, 6),
            },
            "band_measurements": band_results,
            "consensus": consensus,
            "state": state,
            "reason_code": reason,
            "label_effect": "none; registration evidence never assigns burned or background",
        })
    return windows, {"inside_boundary": pair_quality, "signal_preprocessing": signal_stats}


def _machine_decision(event_reports: Iterable[dict[str, Any]]) -> str:
    items = list(event_reports)
    if any(item["registration"]["summary"]["state_counts"]["fail-registration"] for item in items):
        return "REJECT_CROSS_EVENT_SOURCE_FITNESS"
    if any(item["registration"]["summary"]["state_counts"]["pass"] == 0 for item in items):
        return "REJECT_CROSS_EVENT_SOURCE_FITNESS"
    if any(
        item["registration"]["summary"]["state_counts"][state]
        for item in items for state in ("review-needed", "excluded")
    ):
        return "ACCEPT_CROSS_EVENT_SOURCE_FITNESS_WITH_EXCLUSIONS"
    return "PASS_CROSS_EVENT_SOURCE_FITNESS_GATE"


def _validate_visual(machine: str, decision: str, notes: str) -> None:
    allowed = {
        "PENDING_VISUAL_REVIEW",
        "ACCEPT_CROSS_EVENT_SOURCE_FITNESS",
        "ACCEPT_CROSS_EVENT_SOURCE_FITNESS_WITH_EXCLUSIONS",
        "REJECT_CROSS_EVENT_SOURCE_FITNESS",
    }
    if decision not in allowed:
        raise CrossEventSourceFitnessError("invalid visual review decision")
    if decision != "PENDING_VISUAL_REVIEW" and not notes.strip():
        raise CrossEventSourceFitnessError("final visual review requires notes")
    compatible = {
        "PASS_CROSS_EVENT_SOURCE_FITNESS_GATE": {"ACCEPT_CROSS_EVENT_SOURCE_FITNESS"},
        "ACCEPT_CROSS_EVENT_SOURCE_FITNESS_WITH_EXCLUSIONS": {
            "ACCEPT_CROSS_EVENT_SOURCE_FITNESS_WITH_EXCLUSIONS",
            "REJECT_CROSS_EVENT_SOURCE_FITNESS",
        },
        "REJECT_CROSS_EVENT_SOURCE_FITNESS": {"REJECT_CROSS_EVENT_SOURCE_FITNESS"},
    }
    if decision != "PENDING_VISUAL_REVIEW" and decision not in compatible[machine]:
        raise CrossEventSourceFitnessError("visual decision is incompatible with the machine gate")


def build_report(
    *,
    package: Path,
    feasibility_report_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    visual_review_decision: str,
    visual_review_notes: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    contract_reasons = validate_cross_event_contracts(CROSS_EVENT_CONTRACTS)
    if contract_reasons:
        raise CrossEventSourceFitnessError("cross-event source contract is invalid")
    verification = verify_registered_package(
        package,
        CROSS_EVENT_CONTRACTS,
        contract_validator=validate_cross_event_contracts,
        contract_version=CONTRACT_VERSION,
    )
    if not verification["accepted_as_unchanged_registered_package"]:
        raise CrossEventSourceFitnessError("registered cross-event source package failed verification")
    feasibility, candidates = _load_feasibility(feasibility_report_path)
    contracts = {item.role: item for item in CROSS_EVENT_CONTRACTS}
    events: list[dict[str, Any]] = []
    previews: list[dict[str, Any]] = []
    for candidate in candidates:
        event_id = candidate["event_group_id"]
        pre_role, post_role = ROLE_PAIRS[event_id]
        pre_scene, pre = _read_product(package, contracts[pre_role], candidate["source_geometry"])
        post_scene, post = _read_product(package, contracts[post_role], candidate["source_geometry"])
        windows, quality = measure_event_registration(pre_scene, pre, post_scene, post)
        summary = registration_summary(windows)
        events.append({
            "event_group_id": event_id,
            "fire_id": candidate["fire_id"],
            "fire_name": candidate["fire_name"],
            "ignition_date": candidate["ignition_date"],
            "geography_group_id": candidate["geography_group_id"],
            "scene_group_id": candidate["scene_pair"]["scene_group_id"],
            "time_group_id": candidate["time_group_id"],
            "boundary_bbox_wgs84": candidate["boundary_bbox_wgs84"],
            "source_geometry_sha256": _canonical_sha256(candidate["source_geometry"]),
            "products": [pre_scene, post_scene],
            "pair_quality": quality,
            "registration": {
                "protocol_version": PROTOCOL_VERSION,
                "summary": summary,
                "windows": windows,
            },
        })
        previews.append({
            "event_group_id": event_id,
            "fire_name": candidate["fire_name"],
            "pre_tci": pre["TCI"],
            "post_tci": post["TCI"],
            "pre_mask": pre["MASK10"],
            "post_mask": post["MASK10"],
        })
    machine = _machine_decision(events)
    _validate_visual(machine, visual_review_decision, visual_review_notes)
    registration = verification["registration"] or {}
    report = {
        "report_id": REPORT_ID,
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 361,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": None,
        "target_version": TARGET_VERSION,
        "dataset_version": None,
        "label_schema_version": LABEL_PROTOCOL_VERSION,
        "baseline_version": None,
        "model_version": None,
        "package_id": PACKAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "source_record_id": CROSS_EVENT_CONTRACTS[0].source_record_id,
        "terms_review_id": TERMS_REVIEW_ID,
        "input_hashes": {
            "feasibility_report_sha256": _sha256_lf_text(feasibility_report_path),
            "feasibility_source_snapshot_sha256": feasibility["input_hashes"]["source_snapshot_sha256"],
            "registration_manifest_sha256": sha256((package / ".burnlens-registration.json").read_bytes()).hexdigest(),
        },
        "registered_source_lineage": {
            "acquisition_run_id": registration.get("run_id"),
            "acquisition_generated_at_utc": registration.get("generated_at_utc"),
            "asset_hashes": registration.get("assets"),
        },
        "source_precedence": ROUTE_PRECEDENCE,
        "attribution": (
            "Contains modified Copernicus Sentinel-2 data (2017-2018), "
            "accessed through the Copernicus Data Space Ecosystem."
        ),
        "method": {
            "boundary": "Full frozen MTBS source geometry; crop covers it outward and counts pixel centers inside it; no shrink.",
            "native_pixels": "TCI 10 m is preview only. B04, B8A, B12, and SCL remain on their exact native EPSG:32610 20 m grids with no reprojection, resampling, or upsampling.",
            "quality": "SCL is quantified exactly inside the boundary and remains a quality aid, never truth.",
            "registration": "Independent B04/B8A/B12 reflectance gradients in deterministic event-scaled windows; Hann taper, phase-only cross-power, and localized 100x DFT refinement.",
            "registration_envelope": "Rectangular native-pixel windows may include context outside the irregular MTBS boundary only for correlation; quality fractions are computed only from boundary pixels and no outside pixel becomes evidence or a label.",
            "shared_mask_applied_to_correlation": False,
        },
        "events": events,
        "decision": {
            "machine": machine,
            "visual_review": visual_review_decision,
            "visual_review_notes": visual_review_notes,
            "next_boundary": "No label pixels, dataset, split, baseline, model, or application may be claimed from this source-fitness checkpoint.",
        },
        "claims": {
            "proven": [
                "The four exact registered provider archives remain byte-identical to their acquisition registration.",
                "The full frozen Tepee and McKay boundaries are readable at native Sentinel-2 pixels with exact SCL distributions and pair-local registration evidence.",
            ],
            "not_proven": [
                "Any SCL class, spectral signal, MTBS boundary, or registration window is a burn-scar label or severity truth.",
                "A leakage-resistant dataset, benchmark split, baseline, model, deployed application, field validity, operational readiness, or official status exists.",
            ],
        },
        "warning": WARNING,
    }
    return report, previews


def _preview_image(values: np.ndarray, mask: np.ndarray, size: tuple[int, int]) -> Image.Image:
    rgb = np.moveaxis(values, 0, 2).astype(np.uint8)
    dimmed = (rgb.astype(np.float32) * 0.24).astype(np.uint8)
    rgb = np.where(mask[:, :, None], rgb, dimmed)
    image = Image.fromarray(rgb, mode="RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, "#101918")
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def render_png(report: dict[str, Any], previews: list[dict[str, Any]], path: Path) -> None:
    canvas = Image.new("RGB", (1800, 1450), "#07110f")
    draw = ImageDraw.Draw(canvas)
    draw.text((70, 44), "BURNLENS  /  CROSS-EVENT SOURCE FITNESS", fill="#b9d8cf", font=_font(23))
    draw.text((70, 86), report["decision"]["machine"], fill="#ffca73", font=_font(32))
    draw.text((70, 132), "Four exact archives / two frozen events / full MTBS boundaries / native pixels", fill="#eef7f3", font=_font(21))
    y = 195
    event_by_id = {item["event_group_id"]: item for item in report["events"]}
    for preview in previews:
        event = event_by_id[preview["event_group_id"]]
        summary = event["registration"]["summary"]
        draw.rounded_rectangle((55, y, 1745, y + 500), radius=22, fill="#0e1d1a", outline="#315b50", width=2)
        draw.text((85, y + 28), f"{preview['fire_name']}  /  {preview['event_group_id']}", fill="#eef7f3", font=_font(25))
        pre_image = _preview_image(preview["pre_tci"], preview["pre_mask"], (660, 330))
        post_image = _preview_image(preview["post_tci"], preview["post_mask"], (660, 330))
        canvas.paste(pre_image, (85, y + 82))
        canvas.paste(post_image, (765, y + 82))
        draw.text((95, y + 424), "PRE / dimmed outside full boundary", fill="#b9d8cf", font=_font(17))
        draw.text((775, y + 424), "POST / dimmed outside full boundary", fill="#b9d8cf", font=_font(17))
        states = summary["state_counts"]
        quality = event["pair_quality"]["inside_boundary"]["states"]
        eligible = next(item["percent"] for item in quality if item["state"] == "eligible-comparison")
        draw.text((1460, y + 95), f"{states['pass']} / {summary['window_count']}", fill="#78e0bd", font=_font(31))
        draw.text((1460, y + 137), "registration windows pass", fill="#b9d8cf", font=_font(16))
        draw.text((1460, y + 192), f"{eligible:.2f}%", fill="#eef7f3", font=_font(28))
        draw.text((1460, y + 230), "pair-eligible boundary pixels", fill="#b9d8cf", font=_font(16))
        p95 = summary["p95_px"]
        draw.text((1460, y + 282), "n/a" if p95 is None else f"{p95:.3f} px", fill="#eef7f3", font=_font(28))
        draw.text((1460, y + 320), "p95 content residual", fill="#b9d8cf", font=_font(16))
        y += 535
    draw.rounded_rectangle((55, 1270, 1745, 1385), radius=18, fill="#261f12", outline="#be8a36", width=2)
    draw.text((80, 1292), WARNING, fill="#ffd997", font=_font(18))
    draw.text((80, 1330), "No labels / dataset / split / baseline / model / application. Official sources govern.", fill="#ffd997", font=_font(18))
    draw.text((80, 1362), report["attribution"], fill="#ffd997", font=_font(16))
    acquisition_run = report["registered_source_lineage"]["acquisition_run_id"]
    draw.text(
        (60, 1400),
        f"TRACE  commit {report['git_source_commit'][:12]}  /  BurnLens {report['software_version']}  /  evidence {report['run_id']}  /  acquisition {acquisition_run}",
        fill="#b9d8cf",
        font=_font(14),
    )
    draw.text(
        (60, 1426),
        f"dataset none  /  baseline none  /  model none  /  application none  /  label schema {report['label_schema_version']}",
        fill="#b9d8cf",
        font=_font(14),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], png_name: str, path: Path) -> None:
    event_cards = []
    for event in report["events"]:
        product_rows = "".join(
            "<tr>"
            f"<td><code>{escape(product['role'])}</code></td>"
            f"<td>{escape(product['product_metadata']['sensing_time_utc'])}</td>"
            f"<td>{product['scl_summary_inside_full_boundary']['eligible_land_percent']:.4f}%</td>"
            f"<td>{product['scl_summary_inside_full_boundary']['review_needed_percent']:.4f}%</td>"
            f"<td>{product['scl_summary_inside_full_boundary']['excluded_percent']:.4f}%</td>"
            "</tr>"
            for product in event["products"]
        )
        window_rows = "".join(
            "<tr>"
            f"<td><code>{escape(item['window_id'])}</code></td>"
            f"<td>{escape(item['state'])}</td>"
            f"<td>{escape(item['reason_code'])}</td>"
            f"<td>{'n/a' if item['consensus'] is None else ('%.4f px' % item['consensus']['magnitude_px'])}</td>"
            "</tr>"
            for item in event["registration"]["windows"]
        )
        summary = event["registration"]["summary"]
        event_cards.append(
            f"<section><h2>{escape(event['fire_name'])}</h2>"
            f"<p><code>{escape(event['event_group_id'])}</code> · <code>{escape(event['scene_group_id'])}</code></p>"
            f"<div class=\"grid\"><div class=\"card\"><div class=\"value\">{summary['state_counts']['pass']} / {summary['window_count']}</div><div>registration windows pass</div></div>"
            f"<div class=\"card\"><div class=\"value\">{'n/a' if summary['p95_px'] is None else ('%.3f px' % summary['p95_px'])}</div><div>p95 content residual</div></div></div>"
            "<h3>Native product quality inside the full boundary</h3><table><thead><tr><th>Role</th><th>Sensing UTC</th><th>Eligible land</th><th>Review</th><th>Excluded</th></tr></thead>"
            f"<tbody>{product_rows}</tbody></table>"
            "<h3>Pair-local registration</h3><table><thead><tr><th>Window</th><th>State</th><th>Reason</th><th>Residual</th></tr></thead>"
            f"<tbody>{window_rows}</tbody></table></section>"
        )
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(REPORT_ID)}</title><style>
body{{margin:0;background:#07110f;color:#eef7f3;font:16px/1.55 system-ui,sans-serif}}main{{max-width:1180px;margin:auto;padding:48px 24px 80px}}h1{{font-size:42px;line-height:1.1}}h2{{margin-top:48px}}h3{{margin-top:28px}}code{{color:#9ce4ca}}.warning{{padding:18px;border:1px solid #be8a36;background:#261f12;color:#ffd997;border-radius:12px}}.hero{{width:100%;height:auto;border:1px solid #315b50;border-radius:14px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px}}.card{{padding:18px;background:#0e1d1a;border:1px solid #315b50;border-radius:12px}}.value{{font-size:28px;color:#78e0bd}}table{{width:100%;border-collapse:collapse;background:#0e1d1a}}th,td{{padding:10px;text-align:left;border-bottom:1px solid #315b50}}th{{color:#b9d8cf}}a{{color:#9ce4ca}}
</style></head><body><main><p>BURNLENS / PHASE TWO / SOURCE FITNESS</p><h1>Cross-event native-pixel fitness</h1>
<p class="warning">{escape(WARNING)}</p><img class="hero" src="{escape(png_name)}" alt="Tepee and McKay pre and post Sentinel-2 previews with source-fitness metrics">
<div class="grid"><div class="card"><div class="value">4 exact archives</div><div>verified against one registered package</div></div><div class="card"><div class="value">2 frozen events</div><div>full MTBS boundary evidence</div></div><div class="card"><div class="value">0 labels</div><div>dataset, split, baseline, model, and application remain absent</div></div></div>
<h2>Decision</h2><div class="card"><p><strong>{escape(report['decision']['machine'])}</strong></p><p>Visual review: {escape(report['decision']['visual_review'])}</p><p>{escape(report['decision']['visual_review_notes'] or 'Pending rendered review.')}</p></div>
<h2>What was measured</h2><div class="card"><ul><li>{escape(report['method']['boundary'])}</li><li>{escape(report['method']['native_pixels'])}</li><li>{escape(report['method']['quality'])}</li><li>{escape(report['method']['registration'])}</li><li>{escape(report['method']['registration_envelope'])}</li></ul></div>
{''.join(event_cards)}
<h2>Interpretation boundary</h2><div class="card"><p>{escape(report['decision']['next_boundary'])}</p><p>{escape(report['attribution'])}</p><p>Trace: source commit <code>{escape(report['git_source_commit'])}</code> · BurnLens <code>{escape(report['software_version'])}</code> · evidence run <code>{escape(report['run_id'])}</code> · acquisition run <code>{escape(str(report['registered_source_lineage']['acquisition_run_id']))}</code>.</p><p>Dataset: none · baseline: none · model: none · application: none · label schema: <code>{escape(report['label_schema_version'])}</code>.</p></div>
</main></body></html>"""
    path.parent.mkdir(parents=True, exist_ok=True)
    _write_utf8_lf(path, html)


def write_report(report: dict[str, Any], previews: list[dict[str, Any]], json_path: Path, html_path: Path, png_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    _write_utf8_lf(json_path, json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    render_png(report, previews, png_path)
    render_html(report, png_path.name, html_path)
