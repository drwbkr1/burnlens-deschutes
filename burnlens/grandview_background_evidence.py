"""Assess an affirmative Grandview background-candidate evidence route."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import numpy as np
from PIL import Image, ImageDraw
import rasterio

from .content_registration import _summary as registration_summary
from .cross_event_source_fitness import _read_product, measure_event_registration
from .grandview_background_optical_contract import (
    BACKGROUND_OPTICAL_CONTRACTS,
    CONTRACT_VERSION as EXTENDED_CONTRACT_VERSION,
    EXTENDED_CONTRACT,
    EXPECTED_METADATA as EXTENDED_EXPECTED_METADATA,
    PACKAGE_ID as EXTENDED_PACKAGE_ID,
    validate_background_optical_contracts,
)
from .grandview_optical_contract import (
    CONTRACT_VERSION as ORIGINAL_CONTRACT_VERSION,
    EXPECTED_METADATA as ORIGINAL_EXPECTED_METADATA,
    GRANDVIEW_CONTRACTS,
    PACKAGE_ID as ORIGINAL_PACKAGE_ID,
    validate_grandview_contracts,
)
from .grandview_reference_fitness import (
    PRODUCTS,
    _find,
    _inspect_raster,
    build_report as build_reference_report,
)
from .grandview_source_fitness import _load_candidate, _preview_tci
from .green_ridge_background_evidence import (
    CONTEXT_BUFFER_M,
    ONE_HECTARE_PIXELS,
    PIXEL_SIZE_M,
    REFERENCE_BOUNDARY_BUFFER_PX,
    _component_sizes,
    _context_geometry,
    _mask_preview,
    _registration_manifest,
    _spectral_stability,
)
from .green_ridge_reference_fitness import _sample
from .label_proposal import dilate_mask
from .optical_pair_evidence import WARNING, _font, _write_utf8_lf
from .paired_intake import verify_registered_package


SOFTWARE_VERSION = "0.41.0"
REPORT_ID = "GRANDVIEW-BACKGROUND-EVIDENCE-2026-001"
REPORT_VERSION = "grandview-background-evidence-v0.1.0"
PROTOCOL_VERSION = "grandview-background-route-protocol-v0.1.0"
TASK_ISSUE = 503
EVENT_ID = "OR4446612140020210711"
SOURCE_RECORD_ID = "SOURCE-2026-027"
TERMS_REVIEW_ID = "TERMS-2026-023"
PRECHECK_ID = "PRECHECK-2026-041"
LABEL_SCHEMA_VERSION = "burn-scar-five-state-schema-v0.1.0"
TARGET_VERSION = "target-burn-scar-v0.2.0"


class GrandviewBackgroundEvidenceError(RuntimeError):
    """Exact Grandview background-route evidence failed closed."""


def _reference_route_masks(
    baer_dnbr: np.ndarray, mtbs: np.ndarray, ravg: np.ndarray
) -> dict[str, np.ndarray]:
    if baer_dnbr.shape != mtbs.shape or mtbs.shape != ravg.shape:
        raise GrandviewBackgroundEvidenceError("reference context grids differ")
    baer_footprint = np.isfinite(baer_dnbr)
    mtbs_footprint = np.isin(mtbs, (1, 2, 3, 4, 5, 6))
    ravg_footprint = np.isin(ravg, (1, 2, 3, 4, 9))
    source_footprint = baer_footprint | mtbs_footprint | ravg_footprint
    outside_all = (~baer_footprint) & (mtbs == 0) & (ravg == 0)
    boundary_buffer = dilate_mask(source_footprint, REFERENCE_BOUNDARY_BUFFER_PX)
    return {
        "baer_footprint": baer_footprint,
        "mtbs_footprint": mtbs_footprint,
        "ravg_footprint": ravg_footprint,
        "source_boundary": source_footprint,
        "outside_all": outside_all,
        "boundary_buffer": boundary_buffer,
    }


def _reference_context(
    archive_path: Path, shape: tuple[int, int], transform: rasterio.Affine
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    sampled: dict[str, np.ndarray] = {}
    members: dict[str, str] = {}
    with ZipFile(archive_path) as archive:
        for key in ("baer_dnbr", "mtbs_dnbr6", "ravg_cbi4"):
            member = _find(archive, PRODUCTS[key][1])
            _, runtime = _inspect_raster(archive, member)
            sampled[key] = _sample(runtime, shape, transform, continuous=key == "baer_dnbr")
            members[key] = member
    masks = _reference_route_masks(
        sampled["baer_dnbr"], sampled["mtbs_dnbr6"], sampled["ravg_cbi4"]
    )
    report = {
        "members": members,
        "sampling": "nearest neighbor from native 30 m to the 20 m context grid; no resolution gain",
        "baer_raster_footprint_pixels": int(masks["baer_footprint"].sum()),
        "mtbs_raster_footprint_pixels": int(masks["mtbs_footprint"].sum()),
        "ravg_raster_footprint_pixels": int(masks["ravg_footprint"].sum()),
        "outside_all_program_footprints_pixels": int(masks["outside_all"].sum()),
        "boundary_buffer_pixels": REFERENCE_BOUNDARY_BUFFER_PX,
        "boundary_buffer_m": REFERENCE_BOUNDARY_BUFFER_PX * PIXEL_SIZE_M,
        "boundary_buffer_basis": (
            "60 m equals two native 30 m reference cells and retains source-grid and mixed-boundary uncertainty."
        ),
        "ravg_role": (
            "Only encoded perimeter presence is used for conservative exclusion. RAVG modeled class meaning is "
            "not affirmative evidence because the exact delivery warns of sparse to no pre-fire tree cover."
        ),
        "use_boundary": (
            "Program-footprint exclusion is context only. Encoded zero, nodata, or outside-footprint status "
            "cannot establish background truth without independent optical stability and owner review."
        ),
    }
    return report, {**sampled, **masks}


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
        GRANDVIEW_CONTRACTS,
        contract_validator=validate_grandview_contracts,
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
        raise GrandviewBackgroundEvidenceError("original optical package failed verification")
    if not extended_verification["accepted_as_unchanged_registered_package"]:
        raise GrandviewBackgroundEvidenceError("extended optical package failed verification")
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
    pre_scene, pre = _read_product(original_package, GRANDVIEW_CONTRACTS[0], context_geometry)
    post_scene, post = _read_product(original_package, GRANDVIEW_CONTRACTS[1], context_geometry)
    extended_scene, extended = _read_product(extended_package, EXTENDED_CONTRACT, context_geometry)
    crop_transforms = {
        tuple(item["rasters"]["B04"]["crop_transform"])
        for item in (pre_scene, post_scene, extended_scene)
    }
    shapes = {item["B04"].shape for item in (pre, post, extended)}
    if len(crop_transforms) != 1 or len(shapes) != 1:
        raise GrandviewBackgroundEvidenceError("three-scene context grids differ")
    registration_windows, _ = measure_event_registration(pre_scene, pre, extended_scene, extended)
    registration = registration_summary(registration_windows)
    if registration["machine_decision"] != "PASS_LOCAL_CONTENT_REGISTRATION_GATE":
        raise GrandviewBackgroundEvidenceError("extended scene content registration failed")
    stability_report, stability = _spectral_stability(
        pre_scene, pre, post_scene, post, extended_scene, extended
    )
    stability_report["interpretation"] = (
        "The established Darlene four-signal screen transfers unchanged to the near-anniversary Grandview "
        "comparison. Metadata-derived BOA scale and offset are applied across the explicit 05.00/05.10 baseline "
        "difference. This is optical stability evidence, not unburned truth."
    )
    shape = pre["B04"].shape
    transform = rasterio.Affine(*pre_scene["rasters"]["B04"]["crop_transform"])
    reference_context, reference = _reference_context(reference_archive, shape, transform)
    route = stability["coherent"] & reference["outside_all"] & ~reference["boundary_buffer"]
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
            "label_set_version": "owner-approved-prototype-region-labels-v0.2.0",
            "dataset_version": None,
            "split_version": None,
            "baseline_version": None,
            "model_version": None,
            "original_optical_acquisition_run_id": original_manifest["run_id"],
            "extended_optical_acquisition_run_id": extended_manifest["run_id"],
            "reference_request_run_id": reference_report["trace"]["reference_request_run_id"],
            "reference_delivery_run_id": reference_report["trace"]["reference_delivery_run_id"],
        },
        "packages": {
            "original": {
                "package_id": ORIGINAL_PACKAGE_ID,
                "provider_bytes": sum(item.expected_size_bytes for item in GRANDVIEW_CONTRACTS),
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
                "boa_quantification_value": item["product_metadata"]["boa_quantification_value"],
                "boa_offsets": item["product_metadata"]["boa_offsets"],
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
                "7 of 9 stable neighbors; outside BAER, MTBS, and RAVG rasterized footprints; outside the 60 m "
                "source-boundary uncertainty buffer. No single signal is sufficient."
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
            "accessed_at_utc": "2026-07-20T22:00:00Z",
            "primary_urls": [
                "https://documentation.dataspace.copernicus.eu/APIs/STAC.html",
                "https://documentation.dataspace.copernicus.eu/APIs/OData.html",
                "https://dataspace.copernicus.eu/terms-and-conditions",
                "https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel2.html",
                "https://burnseverity.cr.usgs.gov/compare-products",
            ],
        },
        "claims": {
            "proven": [
                "The exact extended archive and original optical/reference custody pass deterministic verification.",
                "The near-anniversary pre/extended pair passes actual content registration despite the disclosed baseline change.",
                "A reproducible multi-signal background-candidate evidence route exists outside all three official program footprints.",
            ],
            "not_proven": [
                "The route is not ground truth, field validation, an official unburned map, a candidate region, or a label.",
                "RAVG modeled classes are not affirmative evidence for this sparse/non-tree event.",
                "No owner response, dataset, split, baseline, model, accuracy, endorsement, or operational readiness exists.",
            ],
        },
        "attribution": (
            "Contains modified Copernicus Sentinel data 2021-2022, accessed through CDSE; "
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
        "valid": stability["valid"],
        "coherent": stability["coherent"],
        "route": route,
        "source_boundary": reference["source_boundary"],
        "boundary_buffer": reference["boundary_buffer"],
    }
    return report, previews


def render_png(report: dict[str, Any], previews: dict[str, np.ndarray], path: Path) -> None:
    canvas = Image.new("RGB", (1800, 1260), "#07110f")
    draw = ImageDraw.Draw(canvas)
    draw.text((60, 38), "BURNLENS  /  GRANDVIEW BACKGROUND EVIDENCE", fill="#b9d8cf", font=_font(21))
    draw.text((60, 76), "A background evidence route opens; no candidate or label does.", fill="#eef7f3", font=_font(30))
    draw.text((60, 126), report["fitness_decision"]["checkpoint"], fill="#ffca73", font=_font(17))
    panels = [
        ("PRE 2021-06-03", _preview_tci(previews["pre_tci"], previews["pre_mask"], (520, 315))),
        ("POST 2021-07-23", _preview_tci(previews["post_tci"], previews["post_mask"], (520, 315))),
        ("EXTENDED 2022-06-28", _preview_tci(previews["extended_tci"], previews["extended_mask"], (520, 315))),
        ("THREE PROGRAM FOOTPRINTS + 60 m", _mask_preview(previews, "reference", (520, 315))),
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
    draw.text((82, 1158), "RAVG modeled classes remain excluded; only perimeter presence conservatively excludes pixels.", fill="#ffd997", font=_font(14))
    draw.text((82, 1186), WARNING, fill="#ffd997", font=_font(14))
    draw.text((60, 1232), f"TRACE commit {report['git_source_commit'][:12]} / run {report['run_id']} / BurnLens {SOFTWARE_VERSION} / dataset-model none", fill="#b9d8cf", font=_font(13))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], png_name: str, path: Path) -> None:
    route = report["route_evidence"]
    products = "".join(
        f"<tr><td>{item['role']}</td><td><code>{item['native_id']}</code></td><td>{item['sensing_time_utc']}</td><td>{item['processing_baseline']}</td></tr>"
        for item in report["products"]
    )
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Grandview background evidence</title><style>
body{{margin:0;background:#07110f;color:#eef7f3;font:16px/1.55 system-ui,sans-serif}}main{{max-width:1200px;margin:auto;padding:32px}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.02}}.card{{background:#0e1d1a;border:1px solid #315b50;border-radius:16px;padding:20px;margin:18px 0}}.warn{{background:#261f12;border-color:#be8a36;color:#ffd997}}img{{width:100%;height:auto;border-radius:16px}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #315b50;vertical-align:top}}code{{overflow-wrap:anywhere}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}.metric strong{{display:block;font-size:2rem;color:#78e0bd}}
</style></head><body><main><p>BURNLENS / PHASE TWO / ISSUE #503</p><h1>A background evidence route opens; no candidate or label does.</h1><div class="card warn">{report['warning']}</div><img src="{png_name}" width="1800" height="1260" alt="Actual Grandview pre, post, extended, official-footprint, stability, and route evidence"><div class="grid"><div class="card metric"><strong>{route['eligible_pixels']:,}</strong>eligible evidence pixels</div><div class="card metric"><strong>{route['eligible_area_hectares']:,.2f} ha</strong>eligible evidence area</div><div class="card metric"><strong>{route['components_at_least_one_hectare']}</strong>components at least one hectare</div><div class="card metric"><strong>0</strong>candidate regions or labels</div></div><h2>Exact optical products</h2><div class="card"><table><thead><tr><th>Role</th><th>Product</th><th>Sensing time</th><th>Baseline</th></tr></thead><tbody>{products}</tbody></table><p>The 05.00/05.10 processing difference is disclosed. Product-metadata BOA scaling and offsets plus actual content registration govern comparison.</p></div><h2>Conjunctive evidence rule</h2><div class="card"><p>{route['rule']}</p><p>Outside-footprint status, encoded zero, nodata, SCL, or apparent stability is insufficient alone. The threshold set transfers unchanged; no threshold was searched against this result.</p><p>{report['reference_context']['ravg_role']}</p></div><h2>Gate result</h2><div class="card"><p><strong>{report['fitness_decision']['background_evidence_route']}</strong></p><p>The next gate is a separate deterministic region proposal followed by owner yes/no/uncertain review. This report creates neither.</p></div><div class="card warn"><p>{report['attribution']}</p><p>No ground truth, field validation, official unburned map, owner response, dataset, split, baseline, model, accuracy, endorsement, or operational readiness exists.</p></div><p>Trace: commit <code>{report['git_source_commit']}</code> · BurnLens <code>{SOFTWARE_VERSION}</code> · run <code>{report['run_id']}</code> · label schema <code>{LABEL_SCHEMA_VERSION}</code> · dataset/model none.</p></main></body></html>"""
    _write_utf8_lf(path, html)


def write_outputs(report: dict[str, Any], previews: dict[str, np.ndarray], directory: Path) -> dict[str, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    paths = {name: directory / f"{REPORT_ID}.{name}" for name in ("json", "html", "png")}
    _write_utf8_lf(paths["json"], json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    render_png(report, previews, paths["png"])
    render_html(report, paths["png"].name, paths["html"])
    return paths
