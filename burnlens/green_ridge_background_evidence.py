"""Assess an affirmative Green Ridge background-candidate evidence route."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any, Iterable
from zipfile import ZipFile

import numpy as np
from PIL import Image, ImageDraw
import rasterio
from rasterio.warp import Resampling, reproject, transform_geom

from .content_registration import _summary as registration_summary
from .cross_event_source_fitness import _read_product, measure_event_registration
from .green_ridge_background_optical_contract import (
    BACKGROUND_OPTICAL_CONTRACTS,
    CONTRACT_VERSION as EXTENDED_CONTRACT_VERSION,
    EXTENDED_CONTRACT,
    EXPECTED_METADATA as EXTENDED_EXPECTED_METADATA,
    PACKAGE_ID as EXTENDED_PACKAGE_ID,
    validate_background_optical_contracts,
)
from .green_ridge_optical_contract import (
    CONTRACT_VERSION as ORIGINAL_CONTRACT_VERSION,
    EXPECTED_METADATA as ORIGINAL_EXPECTED_METADATA,
    GREEN_RIDGE_CONTRACTS,
    PACKAGE_ID as ORIGINAL_PACKAGE_ID,
    validate_green_ridge_contracts,
)
from .green_ridge_reference_fitness import (
    PRODUCTS,
    _find,
    _inspect_raster,
    build_report as build_reference_report,
)
from .green_ridge_source_fitness import _load_candidate, _preview_tci
from .label_proposal import (
    STABLE_ABS_DNBR_MAX,
    STABLE_ABS_NDVI_CHANGE_MAX,
    STABLE_ABS_NIR_CHANGE_MAX,
    STABLE_ABS_SWIR_CHANGE_MAX,
    STABLE_NEIGHBOR_SUPPORT_MIN,
    dilate_mask,
    neighbor_support,
)
from .optical_pair_evidence import WARNING, _font, _reflectance, _write_utf8_lf, classify_pair_quality
from .paired_intake import verify_registered_package


SOFTWARE_VERSION = "0.35.0"
REPORT_ID = "GREEN-RIDGE-BACKGROUND-EVIDENCE-2026-001"
REPORT_VERSION = "green-ridge-background-evidence-v0.1.0"
PROTOCOL_VERSION = "green-ridge-background-route-protocol-v0.1.0"
TASK_ISSUE = 480
EVENT_ID = "OR4446712160520200817"
CONTEXT_BUFFER_M = 3_000
REFERENCE_BOUNDARY_BUFFER_PX = 3
PIXEL_SIZE_M = 20
ONE_HECTARE_PIXELS = 25
SOURCE_RECORD_ID = "SOURCE-2026-023"
TERMS_REVIEW_ID = "TERMS-2026-019"
PRECHECK_ID = "PRECHECK-2026-035"
LABEL_SCHEMA_VERSION = "burn-scar-five-state-schema-v0.1.0"
TARGET_VERSION = "target-burn-scar-v0.2.0"


class GreenRidgeBackgroundEvidenceError(RuntimeError):
    """Exact Green Ridge background-route evidence failed closed."""


def _points(coordinates: Any) -> Iterable[tuple[float, float]]:
    if (
        isinstance(coordinates, (list, tuple))
        and len(coordinates) >= 2
        and isinstance(coordinates[0], (int, float))
    ):
        yield float(coordinates[0]), float(coordinates[1])
        return
    if not isinstance(coordinates, (list, tuple)):
        raise GreenRidgeBackgroundEvidenceError("invalid boundary coordinates")
    for item in coordinates:
        yield from _points(item)


def _context_geometry(boundary_wgs84: dict[str, Any]) -> tuple[dict[str, Any], list[float]]:
    boundary_utm = transform_geom("EPSG:4326", "EPSG:32610", boundary_wgs84, precision=3)
    points = list(_points(boundary_utm.get("coordinates")))
    if not points:
        raise GreenRidgeBackgroundEvidenceError("empty Green Ridge boundary")
    xs = [item[0] for item in points]
    ys = [item[1] for item in points]
    bounds = [
        min(xs) - CONTEXT_BUFFER_M,
        min(ys) - CONTEXT_BUFFER_M,
        max(xs) + CONTEXT_BUFFER_M,
        max(ys) + CONTEXT_BUFFER_M,
    ]
    west, south, east, north = bounds
    rectangle_utm = {
        "type": "Polygon",
        "coordinates": [[[west, south], [east, south], [east, north], [west, north], [west, south]]],
    }
    return transform_geom("EPSG:32610", "EPSG:4326", rectangle_utm, precision=9), bounds


def _spectral_stability(
    pre_scene: dict[str, Any],
    pre: dict[str, np.ndarray],
    post_scene: dict[str, Any],
    post: dict[str, np.ndarray],
    extended_scene: dict[str, Any],
    extended: dict[str, np.ndarray],
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    original_quality, _ = classify_pair_quality(pre["SCL"], post["SCL"])
    extended_quality, _ = classify_pair_quality(pre["SCL"], extended["SCL"])
    pre_red, pre_red_valid = _reflectance(pre_scene, pre, "B04")
    ext_red, ext_red_valid = _reflectance(extended_scene, extended, "B04")
    pre_nir, pre_nir_valid = _reflectance(pre_scene, pre, "B8A")
    ext_nir, ext_nir_valid = _reflectance(extended_scene, extended, "B8A")
    pre_swir, pre_swir_valid = _reflectance(pre_scene, pre, "B12")
    ext_swir, ext_swir_valid = _reflectance(extended_scene, extended, "B12")
    valid = (
        (original_quality == 0)
        & (extended_quality == 0)
        & pre_red_valid
        & ext_red_valid
        & pre_nir_valid
        & ext_nir_valid
        & pre_swir_valid
        & ext_swir_valid
    )
    pre_nbr_denominator = pre_nir + pre_swir
    ext_nbr_denominator = ext_nir + ext_swir
    pre_ndvi_denominator = pre_nir + pre_red
    ext_ndvi_denominator = ext_nir + ext_red
    valid &= np.abs(pre_nbr_denominator) > 1e-9
    valid &= np.abs(ext_nbr_denominator) > 1e-9
    valid &= np.abs(pre_ndvi_denominator) > 1e-9
    valid &= np.abs(ext_ndvi_denominator) > 1e-9
    dnbr = np.full(valid.shape, np.nan, dtype=np.float32)
    ndvi_loss = np.full(valid.shape, np.nan, dtype=np.float32)
    dnbr[valid] = (
        (pre_nir[valid] - pre_swir[valid]) / pre_nbr_denominator[valid]
        - (ext_nir[valid] - ext_swir[valid]) / ext_nbr_denominator[valid]
    )
    ndvi_loss[valid] = (
        (pre_nir[valid] - pre_red[valid]) / pre_ndvi_denominator[valid]
        - (ext_nir[valid] - ext_red[valid]) / ext_ndvi_denominator[valid]
    )
    swir_gain = ext_swir - pre_swir
    nir_loss = pre_nir - ext_nir
    stable = (
        valid
        & (np.abs(dnbr) <= STABLE_ABS_DNBR_MAX)
        & (np.abs(ndvi_loss) <= STABLE_ABS_NDVI_CHANGE_MAX)
        & (np.abs(swir_gain) <= STABLE_ABS_SWIR_CHANGE_MAX)
        & (np.abs(nir_loss) <= STABLE_ABS_NIR_CHANGE_MAX)
    )
    coherent = stable & (neighbor_support(stable) >= STABLE_NEIGHBOR_SUPPORT_MIN)
    report = {
        "context_pixels": int(valid.size),
        "original_pair_eligible_pixels": int((original_quality == 0).sum()),
        "pre_extended_eligible_pixels": int((extended_quality == 0).sum()),
        "three_scene_valid_pixels": int(valid.sum()),
        "stable_pixels": int(stable.sum()),
        "coherent_stable_pixels": int(coherent.sum()),
        "transferred_without_tuning": True,
        "thresholds": {
            "abs_dnbr_max": STABLE_ABS_DNBR_MAX,
            "abs_ndvi_change_max": STABLE_ABS_NDVI_CHANGE_MAX,
            "abs_swir_change_max": STABLE_ABS_SWIR_CHANGE_MAX,
            "abs_nir_change_max": STABLE_ABS_NIR_CHANGE_MAX,
            "minimum_stable_neighbors_of_nine": STABLE_NEIGHBOR_SUPPORT_MIN,
        },
        "interpretation": (
            "The established Darlene stability screen is transferred unchanged to the near-anniversary "
            "Green Ridge comparison. It is affirmative optical-stability evidence, not unburned truth."
        ),
    }
    return report, {
        "valid": valid,
        "stable": stable,
        "coherent": coherent,
        "dnbr": dnbr,
        "original_quality": original_quality,
        "extended_quality": extended_quality,
    }


def _sample_categorical_preserve_zero(
    runtime: dict[str, Any], shape: tuple[int, int], transform: rasterio.Affine
) -> np.ndarray:
    destination = np.full(shape, 255, dtype=np.uint8)
    reproject(
        source=runtime["array"],
        destination=destination,
        src_transform=runtime["transform"],
        src_crs=runtime["crs"],
        src_nodata=None,
        dst_transform=transform,
        dst_crs="EPSG:32610",
        dst_nodata=255,
        resampling=Resampling.nearest,
    )
    return destination


def _reference_context(
    archive_path: Path, shape: tuple[int, int], transform: rasterio.Affine
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    sampled: dict[str, np.ndarray] = {}
    members: dict[str, str] = {}
    with ZipFile(archive_path) as archive:
        for key in ("mtbs_dnbr6", "ravg_cbi4"):
            member = _find(archive, PRODUCTS[key][1])
            _, runtime = _inspect_raster(archive, member)
            sampled[key] = _sample_categorical_preserve_zero(runtime, shape, transform)
            members[key] = member
    mtbs = sampled["mtbs_dnbr6"]
    ravg = sampled["ravg_cbi4"]
    outside_both = (mtbs == 0) & (ravg == 0)
    source_boundary = np.isin(mtbs, (1, 2, 3, 4, 5, 6)) | np.isin(ravg, (1, 2, 3, 4, 9))
    boundary_buffer = dilate_mask(source_boundary, REFERENCE_BOUNDARY_BUFFER_PX)
    report = {
        "members": members,
        "categorical_sampling": "nearest neighbor from native 30 m to the 20 m context grid; no resolution gain",
        "encoded_zero_preserved": True,
        "mtbs_class_zero_pixels": int((mtbs == 0).sum()),
        "ravg_class_zero_pixels": int((ravg == 0).sum()),
        "outside_both_program_footprints_pixels": int(outside_both.sum()),
        "boundary_buffer_pixels": REFERENCE_BOUNDARY_BUFFER_PX,
        "boundary_buffer_m": REFERENCE_BOUNDARY_BUFFER_PX * PIXEL_SIZE_M,
        "boundary_buffer_basis": (
            "60 m equals two native 30 m reference cells and is excluded to retain source-grid and mixed-boundary uncertainty."
        ),
        "role": "Official footprint agreement is context only; it cannot establish background truth without optical stability.",
    }
    return report, {
        **sampled,
        "outside_both": outside_both,
        "source_boundary": source_boundary,
        "boundary_buffer": boundary_buffer,
    }


def _component_sizes(mask: np.ndarray) -> list[int]:
    if mask.ndim != 2:
        raise GreenRidgeBackgroundEvidenceError("component mask must be two dimensional")
    seen = np.zeros(mask.shape, dtype=bool)
    sizes: list[int] = []
    for row, column in zip(*np.where(mask), strict=True):
        if seen[row, column]:
            continue
        stack = [(int(row), int(column))]
        seen[row, column] = True
        count = 0
        while stack:
            current_row, current_column = stack.pop()
            count += 1
            for row_delta in (-1, 0, 1):
                for column_delta in (-1, 0, 1):
                    if row_delta == 0 and column_delta == 0:
                        continue
                    next_row = current_row + row_delta
                    next_column = current_column + column_delta
                    if (
                        0 <= next_row < mask.shape[0]
                        and 0 <= next_column < mask.shape[1]
                        and mask[next_row, next_column]
                        and not seen[next_row, next_column]
                    ):
                        seen[next_row, next_column] = True
                        stack.append((next_row, next_column))
        sizes.append(count)
    return sorted(sizes, reverse=True)


def _registration_manifest(package: Path) -> dict[str, Any]:
    try:
        payload = json.loads((package / ".burnlens-registration.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise GreenRidgeBackgroundEvidenceError("registration manifest unreadable") from error
    return payload


def build_report(
    *,
    original_package: Path,
    extended_package: Path,
    plan_path: Path,
    reference_archive: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    original_verification = verify_registered_package(
        original_package,
        GREEN_RIDGE_CONTRACTS,
        contract_validator=validate_green_ridge_contracts,
        contract_version=ORIGINAL_CONTRACT_VERSION,
        allow_multilink_registration_manifest=True,
    )
    extended_verification = verify_registered_package(
        extended_package,
        BACKGROUND_OPTICAL_CONTRACTS,
        contract_validator=validate_background_optical_contracts,
        contract_version=EXTENDED_CONTRACT_VERSION,
        allow_multilink_registration_manifest=True,
    )
    if not original_verification["accepted_as_unchanged_registered_package"]:
        raise GreenRidgeBackgroundEvidenceError("original optical package failed verification")
    if not extended_verification["accepted_as_unchanged_registered_package"]:
        raise GreenRidgeBackgroundEvidenceError("extended optical package failed verification")
    reference_report, _ = build_reference_report(
        package=original_package,
        plan_path=plan_path,
        archive_path=reference_archive,
        generated_at_utc=generated_at_utc,
        run_id=run_id + "-reference-reverification",
        git_source_commit=git_source_commit,
    )
    _, candidate = _load_candidate(plan_path)
    context_geometry, context_bounds = _context_geometry(candidate["boundary_geometry"])
    pre_scene, pre = _read_product(original_package, GREEN_RIDGE_CONTRACTS[0], context_geometry)
    post_scene, post = _read_product(original_package, GREEN_RIDGE_CONTRACTS[1], context_geometry)
    extended_scene, extended = _read_product(extended_package, EXTENDED_CONTRACT, context_geometry)
    crop_transforms = {
        tuple(item["rasters"]["B04"]["crop_transform"])
        for item in (pre_scene, post_scene, extended_scene)
    }
    shapes = {item["B04"].shape for item in (pre, post, extended)}
    if len(crop_transforms) != 1 or len(shapes) != 1:
        raise GreenRidgeBackgroundEvidenceError("three-scene context grids differ")
    registration_windows, _ = measure_event_registration(pre_scene, pre, extended_scene, extended)
    registration = registration_summary(registration_windows)
    if registration["machine_decision"] != "PASS_LOCAL_CONTENT_REGISTRATION_GATE":
        raise GreenRidgeBackgroundEvidenceError("extended scene content registration failed")
    stability_report, stability = _spectral_stability(
        pre_scene, pre, post_scene, post, extended_scene, extended
    )
    shape = pre["B04"].shape
    transform = rasterio.Affine(*pre_scene["rasters"]["B04"]["crop_transform"])
    reference_context, reference = _reference_context(reference_archive, shape, transform)
    route = stability["coherent"] & reference["outside_both"] & ~reference["boundary_buffer"]
    sizes = _component_sizes(route)
    one_hectare_components = [size for size in sizes if size >= ONE_HECTARE_PIXELS]
    decision = (
        "OPEN_BACKGROUND_EVIDENCE_ROUTE_FOR_SEPARATE_CANDIDATE_PROPOSAL"
        if one_hectare_components
        else "REJECT_CURRENT_BACKGROUND_EVIDENCE_ROUTE"
    )
    original_manifest = _registration_manifest(original_package)
    extended_manifest = _registration_manifest(extended_package)
    report = {
        "report_id": REPORT_ID,
        "report_version": REPORT_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": None,
        "event": {
            "event_group_id": candidate["event_group_id"],
            "event_id": EVENT_ID,
            "fire_name": candidate["fire_name"],
            "context_buffer_m": CONTEXT_BUFFER_M,
            "context_bounds_utm10n": [round(value, 3) for value in context_bounds],
        },
        "trace": {
            "precheck_id": PRECHECK_ID,
            "source_record_id": SOURCE_RECORD_ID,
            "terms_review_id": TERMS_REVIEW_ID,
            "target_version": TARGET_VERSION,
            "label_schema_version": LABEL_SCHEMA_VERSION,
            "label_set_version": "owner-approved-prototype-region-labels-v0.1.0",
            "dataset_version": None,
            "split_version": None,
            "baseline_version": None,
            "model_version": None,
            "original_optical_acquisition_run_id": original_manifest["run_id"],
            "extended_optical_acquisition_run_id": extended_manifest["run_id"],
            "reference_request_run_id": reference_report["trace"]["reference_request_run_id"],
        },
        "packages": {
            "original": {
                "package_id": ORIGINAL_PACKAGE_ID,
                "provider_bytes": sum(item.expected_size_bytes for item in GREEN_RIDGE_CONTRACTS),
                "verification": original_verification["reason_codes"],
                "registration_manifest_sha256": original_verification["registration_manifest_sha256"],
            },
            "extended": {
                "package_id": EXTENDED_PACKAGE_ID,
                "provider_bytes": EXTENDED_CONTRACT.expected_size_bytes,
                "archive_sha256": extended_manifest["assets"][0]["sha256"],
                "provider_md5": EXTENDED_CONTRACT.provider_md5,
                "provider_blake3": EXTENDED_CONTRACT.provider_blake3,
                "verification": extended_verification["reason_codes"],
                "registration_manifest_sha256": extended_verification["registration_manifest_sha256"],
            },
            "reference_archive": {
                "bytes": reference_report["archive"]["bytes"],
                "sha256": reference_report["archive"]["sha256"],
                "member_count": reference_report["archive"]["member_count"],
            },
        },
        "products": [
            {
                "role": item["role"],
                "native_id": item["native_id"],
                "sensing_time_utc": item["product_metadata"]["sensing_time_utc"],
                "tile": item["product_metadata"]["tile_id"],
                "relative_orbit": (
                    EXTENDED_EXPECTED_METADATA["relative_orbit_number"]
                    if item["role"] == EXTENDED_CONTRACT.role
                    else ORIGINAL_EXPECTED_METADATA[item["role"]]["relative_orbit_number"]
                ),
                "processing_baseline": item["product_metadata"]["processing_baseline"],
            }
            for item in (pre_scene, post_scene, extended_scene)
        ],
        "extended_registration": {"summary": registration, "windows": registration_windows},
        "optical_stability": stability_report,
        "reference_context": reference_context,
        "route_evidence": {
            "eligible_pixels": int(route.sum()),
            "eligible_area_hectares": round(float(route.sum()) * 0.04, 4),
            "component_count": len(sizes),
            "largest_component_pixels": sizes[0] if sizes else 0,
            "largest_component_hectares": round((sizes[0] if sizes else 0) * 0.04, 4),
            "components_at_least_one_hectare": len(one_hectare_components),
            "largest_component_sizes_pixels": sizes[:20],
            "rule": (
                "Three-scene clear/numeric evidence; transferred four-signal near-anniversary stability; at least "
                "7 of 9 stable neighbors; MTBS and RAVG encoded class 0 agreement; outside the 60 m source-boundary "
                "uncertainty buffer. No single signal is sufficient."
            ),
            "candidate_regions_created": 0,
            "labels_created": 0,
        },
        "fitness_decision": {
            "background_evidence_route": decision,
            "next_gate": "SEPARATE_DETERMINISTIC_REGION_PROPOSAL_THEN_OWNER_YES_NO_UNCERTAIN_REVIEW",
            "checkpoint": "ACCEPT_AFFIRMATIVE_BACKGROUND_ROUTE_DEFER_CANDIDATES_LABELS_DATASET_MODEL",
        },
        "source_research": {
            "accessed_at_utc": "2026-07-20T00:30:00Z",
            "primary_urls": [
                "https://www.mtbs.gov/faqs",
                "https://www.mtbs.gov/mapping-methods",
                "https://burnseverity.cr.usgs.gov/ravg/",
                "https://documentation.dataspace.copernicus.eu/APIs/STAC.html",
                "https://dataspace.copernicus.eu/terms-and-conditions",
                "https://sentiwiki.copernicus.eu/web/s2-processing",
            ],
        },
        "claims": {
            "proven": [
                "The exact extended archive and original optical/reference custody pass deterministic verification.",
                "The near-anniversary pre/extended pair passes nine-window content registration.",
                "A reproducible multi-signal background-candidate evidence route exists outside both official program footprints.",
            ],
            "not_proven": [
                "The route is not ground truth, field validation, an official unburned map, a candidate region, or a label.",
                "No owner response, dataset, split, baseline, model, accuracy, endorsement, or operational readiness exists.",
            ],
        },
        "attribution": (
            "Contains modified Copernicus Sentinel data 2020-2021, accessed through CDSE; "
            "Monitoring Trends in Burn Severity Project (U.S. Geological Survey and USDA Forest Service); USDA Forest Service."
        ),
        "warning": WARNING,
    }
    previews = {
        "pre_tci": pre["TCI"],
        "post_tci": post["TCI"],
        "extended_tci": extended["TCI"],
        "pre_mask": pre["MASK10"],
        "post_mask": post["MASK10"],
        "extended_mask": extended["MASK10"],
        "dnbr": stability["dnbr"],
        "valid": stability["valid"],
        "coherent": stability["coherent"],
        "route": route,
        "source_boundary": reference["source_boundary"],
        "boundary_buffer": reference["boundary_buffer"],
    }
    return report, previews


def _mask_preview(previews: dict[str, np.ndarray], mode: str, size: tuple[int, int]) -> Image.Image:
    shape = previews["route"].shape
    rgb = np.zeros((*shape, 3), dtype=np.uint8)
    rgb[:] = (10, 24, 21)
    if mode == "reference":
        rgb[previews["boundary_buffer"]] = (185, 132, 56)
        rgb[previews["source_boundary"]] = (190, 72, 50)
    elif mode == "stability":
        rgb[previews["valid"]] = (47, 78, 69)
        rgb[previews["coherent"]] = (102, 203, 168)
    elif mode == "route":
        rgb[previews["boundary_buffer"]] = (95, 75, 41)
        rgb[previews["route"]] = (54, 222, 179)
    image = Image.fromarray(rgb, mode="RGB")
    image.thumbnail(size, Image.Resampling.NEAREST)
    canvas = Image.new("RGB", size, "#0a1815")
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def render_png(report: dict[str, Any], previews: dict[str, np.ndarray], path: Path) -> None:
    canvas = Image.new("RGB", (1800, 1260), "#07110f")
    draw = ImageDraw.Draw(canvas)
    draw.text((60, 38), "BURNLENS  /  GREEN RIDGE BACKGROUND EVIDENCE", fill="#b9d8cf", font=_font(21))
    draw.text((60, 76), "A background evidence route opens; no candidate or label does.", fill="#eef7f3", font=_font(30))
    draw.text((60, 126), report["fitness_decision"]["checkpoint"], fill="#ffca73", font=_font(17))
    panels = [
        ("PRE 2020-08-10", _preview_tci(previews["pre_tci"], previews["pre_mask"], (520, 315))),
        ("POST 2020-09-29", _preview_tci(previews["post_tci"], previews["post_mask"], (520, 315))),
        ("EXTENDED 2021-08-15", _preview_tci(previews["extended_tci"], previews["extended_mask"], (520, 315))),
        ("OFFICIAL FOOTPRINT + 60 m BUFFER", _mask_preview(previews, "reference", (520, 315))),
        ("TRANSFERRED COHERENT STABILITY", _mask_preview(previews, "stability", (520, 315))),
        ("ELIGIBLE ROUTE EVIDENCE", _mask_preview(previews, "route", (520, 315))),
    ]
    for index, (label, image) in enumerate(panels):
        column, row = index % 3, index // 3
        x, y = 60 + column * 575, 175 + row * 405
        draw.rounded_rectangle((x, y, x + 535, y + 375), radius=16, fill="#0e1d1a", outline="#315b50", width=2)
        draw.text((x + 18, y + 14), label, fill="#eef7f3", font=_font(17))
        canvas.paste(image, (x + 8, y + 48))
    route = report["route_evidence"]
    metrics = [
        (f"{route['eligible_pixels']:,}", "eligible evidence pixels"),
        (f"{route['eligible_area_hectares']:,.2f} ha", "eligible evidence area"),
        (f"{route['components_at_least_one_hectare']:,}", "components at least 1 ha"),
        ("0", "candidate regions / labels"),
    ]
    for index, (value, label) in enumerate(metrics):
        x = 60 + index * 430
        draw.rounded_rectangle((x, 1008, x + 395, 1123), radius=14, fill="#0e1d1a", outline="#315b50", width=2)
        draw.text((x + 20, 1028), value, fill="#78e0bd", font=_font(26))
        draw.text((x + 20, 1076), label, fill="#b9d8cf", font=_font(14))
    draw.rounded_rectangle((60, 1147, 1740, 1215), radius=14, fill="#261f12", outline="#be8a36", width=2)
    draw.text((82, 1164), WARNING, fill="#ffd997", font=_font(15))
    draw.text(
        (60, 1232),
        f"TRACE commit {report['git_source_commit'][:12]} / run {report['run_id']} / BurnLens {SOFTWARE_VERSION} / dataset-model none",
        fill="#b9d8cf",
        font=_font(13),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], png_name: str, path: Path) -> None:
    route = report["route_evidence"]
    products = "".join(
        f"<tr><td>{item['role']}</td><td><code>{item['native_id']}</code></td><td>{item['sensing_time_utc']}</td></tr>"
        for item in report["products"]
    )
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Green Ridge background evidence</title><style>
body{{margin:0;background:#07110f;color:#eef7f3;font:16px/1.55 system-ui,sans-serif}}main{{max-width:1200px;margin:auto;padding:32px}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.02}}.card{{background:#0e1d1a;border:1px solid #315b50;border-radius:16px;padding:20px;margin:18px 0}}.warn{{background:#261f12;border-color:#be8a36;color:#ffd997}}img{{width:100%;height:auto;border-radius:16px}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #315b50;vertical-align:top}}code{{overflow-wrap:anywhere}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}.metric strong{{display:block;font-size:2rem;color:#78e0bd}}
</style></head><body><main><p>BURNLENS / PHASE TWO / ISSUE #480</p><h1>A background evidence route opens; no candidate or label does.</h1><div class="card warn">{report['warning']}</div><img src="{png_name}" width="1800" height="1260" alt="Actual Green Ridge pre, post, extended, reference-footprint, stability, and route evidence"><div class="grid"><div class="card metric"><strong>{route['eligible_pixels']:,}</strong>eligible evidence pixels</div><div class="card metric"><strong>{route['eligible_area_hectares']:,.2f} ha</strong>eligible evidence area</div><div class="card metric"><strong>{route['components_at_least_one_hectare']}</strong>components at least one hectare</div><div class="card metric"><strong>0</strong>candidate regions or labels</div></div><h2>Exact optical products</h2><div class="card"><table><thead><tr><th>Role</th><th>Product</th><th>Sensing time</th></tr></thead><tbody>{products}</tbody></table></div><h2>Conjunctive evidence rule</h2><div class="card"><p>{route['rule']}</p><p>Outside-footprint status, unchanged class, low change, SCL, or apparent stability is insufficient alone. The threshold set transfers unchanged from the established protocol; no threshold was searched against this result.</p></div><h2>Gate result</h2><div class="card"><p><strong>{report['fitness_decision']['background_evidence_route']}</strong></p><p>The next gate is a separate deterministic region proposal followed by owner yes/no/uncertain review. This report creates neither.</p></div><div class="card warn"><p>{report['attribution']}</p><p>No ground truth, field validation, official unburned map, owner response, dataset, split, baseline, model, accuracy, endorsement, or operational readiness exists.</p></div><p>Trace: commit <code>{report['git_source_commit']}</code> · BurnLens <code>{SOFTWARE_VERSION}</code> · run <code>{report['run_id']}</code> · label schema <code>{LABEL_SCHEMA_VERSION}</code> · dataset/model none.</p></main></body></html>"""
    _write_utf8_lf(path, html)


def write_outputs(report: dict[str, Any], previews: dict[str, np.ndarray], directory: Path) -> dict[str, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": directory / f"{REPORT_ID}.json",
        "html": directory / f"{REPORT_ID}.html",
        "png": directory / f"{REPORT_ID}.png",
    }
    _write_utf8_lf(paths["json"], json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    render_png(report, previews, paths["png"])
    render_html(report, paths["png"].name, paths["html"])
    return paths
