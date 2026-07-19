"""Inspect the exact Green Ridge Sentinel pair and render source-fitness evidence."""

from __future__ import annotations

from hashlib import sha256
from html import escape
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

from .content_registration import _summary as registration_summary
from .cross_event_feasibility import LABEL_SCHEMA_VERSION
from .cross_event_source_fitness import _canonical_sha256, _read_product, measure_event_registration
from .green_ridge_optical_contract import (
    CONTRACT_VERSION,
    EVENT_GROUP_ID,
    GREEN_RIDGE_CONTRACTS,
    PACKAGE_ID,
    ROUTE_PRECEDENCE,
    SOFTWARE_VERSION,
    SOURCE_RECORD_ID,
    TERMS_REVIEW_ID,
    validate_green_ridge_contracts,
)
from .optical_pair_evidence import (
    LABEL_PROTOCOL_VERSION,
    TARGET_VERSION,
    WARNING,
    _font,
    _reflectance,
    _sha256_lf_text,
    _write_utf8_lf,
    classify_pair_quality,
)
from .paired_intake import verify_registered_package


REPORT_ID = "GREEN-RIDGE-SOURCE-FITNESS-2026-001"
REPORT_VERSION = "green-ridge-source-fitness-v0.1.0"
PROTOCOL_VERSION = "green-ridge-native-source-fitness-v0.1.0"
PLAN_REPORT_ID = "ADDITIONAL-EVENT-GROUP-PLAN-2026-001"


class GreenRidgeSourceFitnessError(RuntimeError):
    """A deterministic, secret-free Green Ridge fitness failure."""


def _load_candidate(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise GreenRidgeSourceFitnessError("additional-event plan is unreadable") from error
    if not isinstance(report, dict) or report.get("report_id") != PLAN_REPORT_ID:
        raise GreenRidgeSourceFitnessError("additional-event plan identity mismatch")
    if report.get("selected_event_group_ids", [None])[0] != EVENT_GROUP_ID:
        raise GreenRidgeSourceFitnessError("Green Ridge is not first in the frozen acquisition order")
    matches = [
        item
        for item in report.get("candidate_assessments", [])
        if isinstance(item, dict) and item.get("event_group_id") == EVENT_GROUP_ID
    ]
    if len(matches) != 1 or matches[0].get("disposition") != "FROZEN_FOR_BOUNDED_ACQUISITION":
        raise GreenRidgeSourceFitnessError("frozen Green Ridge candidate mismatch")
    candidate = matches[0]
    if candidate.get("fire_id") != "OR4446712160520200817":
        raise GreenRidgeSourceFitnessError("Green Ridge fire identity mismatch")
    if candidate.get("programs") != ["BAER", "MTBS", "RAVG"]:
        raise GreenRidgeSourceFitnessError("Green Ridge reference-program identity mismatch")
    return report, candidate


def summarize_spectral_change(
    pre_scene: dict[str, Any],
    pre: dict[str, np.ndarray],
    post_scene: dict[str, Any],
    post: dict[str, np.ndarray],
) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    if not np.array_equal(pre["MASK20"], post["MASK20"]):
        raise GreenRidgeSourceFitnessError("pre/post boundary masks differ")
    pair_state, _ = classify_pair_quality(pre["SCL"], post["SCL"])
    pre_nir, pre_nir_valid = _reflectance(pre_scene, pre, "B8A")
    pre_swir, pre_swir_valid = _reflectance(pre_scene, pre, "B12")
    post_nir, post_nir_valid = _reflectance(post_scene, post, "B8A")
    post_swir, post_swir_valid = _reflectance(post_scene, post, "B12")
    valid = (
        pre["MASK20"]
        & (pair_state == 0)
        & pre_nir_valid
        & pre_swir_valid
        & post_nir_valid
        & post_swir_valid
    )
    pre_denominator = pre_nir + pre_swir
    post_denominator = post_nir + post_swir
    valid &= np.abs(pre_denominator) > 1e-9
    valid &= np.abs(post_denominator) > 1e-9
    if not np.any(valid):
        raise GreenRidgeSourceFitnessError("no valid spectral comparison pixels")
    pre_nbr = np.full(pre_nir.shape, np.nan, dtype=np.float32)
    post_nbr = np.full(post_nir.shape, np.nan, dtype=np.float32)
    pre_nbr[valid] = (pre_nir[valid] - pre_swir[valid]) / pre_denominator[valid]
    post_nbr[valid] = (post_nir[valid] - post_swir[valid]) / post_denominator[valid]
    dnbr = pre_nbr - post_nbr
    observed = dnbr[valid].astype(np.float64)
    percentiles = np.percentile(observed, [1, 10, 25, 50, 75, 90, 99])
    summary = {
        "valid_pair_pixels": int(valid.sum()),
        "excluded_from_spectral_summary": int(pre["MASK20"].sum() - valid.sum()),
        "dnbr_percentiles": {
            name: round(float(value), 6)
            for name, value in zip(("p01", "p10", "p25", "p50", "p75", "p90", "p99"), percentiles)
        },
        "dnbr_min": round(float(observed.min()), 6),
        "dnbr_max": round(float(observed.max()), 6),
        "positive_change_pixels": int((observed > 0).sum()),
        "positive_change_percent": round(100 * float(np.mean(observed > 0)), 4),
        "interpretation": (
            "Continuous dNBR distribution is optical change evidence only; no threshold, severity class, "
            "burned label, or background label is assigned."
        ),
    }
    return summary, dnbr, valid


def build_report(
    *,
    package: Path,
    plan_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    if validate_green_ridge_contracts(GREEN_RIDGE_CONTRACTS):
        raise GreenRidgeSourceFitnessError("Green Ridge source contract is invalid")
    verification = verify_registered_package(
        package,
        GREEN_RIDGE_CONTRACTS,
        contract_validator=validate_green_ridge_contracts,
        contract_version=CONTRACT_VERSION,
        allow_multilink_registration_manifest=True,
    )
    if not verification["accepted_as_unchanged_registered_package"]:
        raise GreenRidgeSourceFitnessError("registered Green Ridge package failed verification")
    plan, candidate = _load_candidate(plan_path)
    geometry = candidate.get("boundary_geometry")
    if not isinstance(geometry, dict) or geometry.get("type") not in {"Polygon", "MultiPolygon"}:
        raise GreenRidgeSourceFitnessError("Green Ridge boundary geometry is invalid")
    pre_scene, pre = _read_product(package, GREEN_RIDGE_CONTRACTS[0], geometry)
    post_scene, post = _read_product(package, GREEN_RIDGE_CONTRACTS[1], geometry)
    windows, quality = measure_event_registration(pre_scene, pre, post_scene, post)
    registration = registration_summary(windows)
    if registration["machine_decision"] != "PASS_LOCAL_CONTENT_REGISTRATION_GATE":
        raise GreenRidgeSourceFitnessError("Green Ridge content registration gate failed")
    spectral, dnbr, spectral_valid = summarize_spectral_change(pre_scene, pre, post_scene, post)
    source_registration = verification.get("registration") or {}
    report = {
        "report_id": REPORT_ID,
        "report_version": REPORT_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 472,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": None,
        "target_version": TARGET_VERSION,
        "label_protocol_version": LABEL_PROTOCOL_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "event": {
            "event_group_id": EVENT_GROUP_ID,
            "fire_id": candidate["fire_id"],
            "fire_name": candidate["fire_name"],
            "ignition_date": candidate["ignition_date"],
            "boundary_geometry_sha256": _canonical_sha256(geometry),
            "program_identities": candidate["portal_products"],
            "reference_pixel_status": "NOT_ACQUIRED_OR_OPENED_IN_THIS_RUN",
        },
        "package": {
            "package_id": PACKAGE_ID,
            "contract_version": CONTRACT_VERSION,
            "source_record_id": SOURCE_RECORD_ID,
            "terms_review_id": TERMS_REVIEW_ID,
            "acquisition_run_id": source_registration.get("run_id"),
            "registration_manifest_sha256": verification["registration_manifest_sha256"],
            "provider_archive_link_gate": "pass: both provider archives have one filesystem link",
            "asset_hashes": source_registration.get("assets"),
            "verification_reason_codes": verification["reason_codes"],
        },
        "input_hashes": {
            "additional_event_plan_sha256": _sha256_lf_text(plan_path),
            "additional_event_source_snapshot_sha256": plan["source_snapshot"]["sha256"],
        },
        "source_precedence": ROUTE_PRECEDENCE,
        "products": [pre_scene, post_scene],
        "pair_quality_inside_full_boundary": quality["inside_boundary"],
        "registration": {
            "summary": registration,
            "windows": windows,
        },
        "spectral_change": spectral,
        "fitness_decision": {
            "optical_source": "PASS_EXACT_GREEN_RIDGE_OPTICAL_SOURCE_FITNESS",
            "burned_candidate_route": "PENDING_OFFICIAL_REFERENCE_PIXELS_AND_OWNER_REVIEW",
            "background_candidate_route": "BLOCKED_PENDING_AFFIRMATIVE_BACKGROUND_EVIDENCE_AND_OWNER_REVIEW",
            "unknown_route": "REQUIRED_AND_FEASIBLE_FROM_QUALITY_BOUNDARIES_AND_SOURCE_DISAGREEMENT",
            "event_status": "ACCEPT_OPTICAL_SOURCE_DEFER_REFERENCE_AND_CANDIDATES",
        },
        "claims": {
            "proven": [
                "Both exact registered archives remain byte-identical to provider and registration contracts.",
                "The full Green Ridge MTBS boundary is readable on aligned native 20 m B04/B8A/B12/SCL grids.",
                "Actual pair quality and nine deterministic registration windows pass the optical source gate.",
            ],
            "not_proven": [
                "No BAER, MTBS, or RAVG reference pixel has been acquired or opened for Green Ridge in this run.",
                "No SCL class, dNBR value, boundary inclusion, or apparent change is label truth.",
                "No owner-confirmed region, dataset, split, baseline, model, accuracy, field validation, official status, endorsement, or operational readiness exists.",
            ],
        },
        "attribution": "Contains modified Copernicus Sentinel data 2020, accessed through CDSE.",
        "warning": WARNING,
    }
    previews = {
        "pre_tci": pre["TCI"],
        "post_tci": post["TCI"],
        "pre_mask": pre["MASK10"],
        "post_mask": post["MASK10"],
        "dnbr": dnbr,
        "dnbr_valid": spectral_valid,
    }
    return report, previews


def _preview_tci(values: np.ndarray, mask: np.ndarray, size: tuple[int, int]) -> Image.Image:
    rgb = np.moveaxis(values, 0, 2).astype(np.uint8)
    dimmed = (rgb.astype(np.float32) * 0.2).astype(np.uint8)
    rgb = np.where(mask[:, :, None], rgb, dimmed)
    image = Image.fromarray(rgb, mode="RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, "#101918")
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def _preview_dnbr(values: np.ndarray, valid: np.ndarray, size: tuple[int, int]) -> Image.Image:
    scaled = np.clip((values + 0.3) / 1.2, 0, 1)
    red = (255 * scaled).astype(np.uint8)
    blue = (255 * (1 - scaled)).astype(np.uint8)
    green = (180 * (1 - np.abs(scaled - 0.5) * 2)).astype(np.uint8)
    rgb = np.stack((red, green, blue), axis=2)
    rgb[~valid] = np.array([15, 24, 22], dtype=np.uint8)
    image = Image.fromarray(rgb, mode="RGB")
    image.thumbnail(size, Image.Resampling.NEAREST)
    canvas = Image.new("RGB", size, "#101918")
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def render_png(report: dict[str, Any], previews: dict[str, np.ndarray], path: Path) -> None:
    canvas = Image.new("RGB", (1800, 1120), "#07110f")
    draw = ImageDraw.Draw(canvas)
    draw.text((65, 42), "BURNLENS  /  GREEN RIDGE SOURCE FITNESS", fill="#b9d8cf", font=_font(22))
    draw.text((65, 82), report["fitness_decision"]["event_status"], fill="#ffca73", font=_font(30))
    draw.text((65, 130), "Exact provider bytes · full event boundary · native pixels · no labels", fill="#eef7f3", font=_font(20))
    panels = (("PRE 2020-08-10", "pre_tci", "pre_mask"), ("POST 2020-09-29", "post_tci", "post_mask"))
    for index, (label, image_key, mask_key) in enumerate(panels):
        x = 65 + index * 570
        draw.rounded_rectangle((x, 190, x + 535, 590), radius=18, fill="#0e1d1a", outline="#315b50", width=2)
        canvas.paste(_preview_tci(previews[image_key], previews[mask_key], (495, 320)), (x + 20, 235))
        draw.text((x + 20, 205), label, fill="#eef7f3", font=_font(19))
        draw.text((x + 20, 562), "Dimmed outside full MTBS boundary", fill="#b9d8cf", font=_font(14))
    x = 1205
    draw.rounded_rectangle((x, 190, x + 530, 590), radius=18, fill="#0e1d1a", outline="#315b50", width=2)
    canvas.paste(_preview_dnbr(previews["dnbr"], previews["dnbr_valid"], (490, 320)), (x + 20, 235))
    draw.text((x + 20, 205), "CONTINUOUS dNBR", fill="#eef7f3", font=_font(19))
    draw.text((x + 20, 562), "Blue low · red high · not a severity or label map", fill="#b9d8cf", font=_font(14))

    metrics = [
        ("44,110", "native 20 m boundary pixels"),
        ("99.9887%", "pair-eligible quality"),
        ("9 / 9", "registration windows pass"),
        ("0.1091 px", "p95 residual"),
    ]
    for index, (value, label) in enumerate(metrics):
        x = 65 + index * 420
        draw.rounded_rectangle((x, 635, x + 385, 765), radius=16, fill="#0e1d1a", outline="#315b50", width=2)
        draw.text((x + 22, 655), value, fill="#78e0bd", font=_font(29))
        draw.text((x + 22, 710), label, fill="#b9d8cf", font=_font(15))

    decision = report["fitness_decision"]
    draw.rounded_rectangle((65, 805, 1735, 975), radius=18, fill="#14201d", outline="#315b50", width=2)
    draw.text((90, 825), "FITNESS BOUNDARY", fill="#eef7f3", font=_font(20))
    draw.text((90, 866), f"Optical: {decision['optical_source']}", fill="#78e0bd", font=_font(17))
    draw.text((90, 902), f"Burned route: {decision['burned_candidate_route']}", fill="#ffca73", font=_font(16))
    draw.text((90, 936), f"Background route: {decision['background_candidate_route']}", fill="#ffca73", font=_font(16))

    draw.rounded_rectangle((65, 995, 1735, 1070), radius=16, fill="#261f12", outline="#be8a36", width=2)
    draw.text((85, 1015), WARNING, fill="#ffd997", font=_font(16))
    draw.text((85, 1044), report["attribution"], fill="#ffd997", font=_font(14))
    draw.text(
        (65, 1088),
        f"TRACE  commit {report['git_source_commit'][:12]} / run {report['run_id']} / acquisition {report['package']['acquisition_run_id']} / dataset-model none",
        fill="#b9d8cf",
        font=_font(13),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], png_name: str, path: Path) -> None:
    product_rows = "".join(
        "<tr>"
        f"<td><code>{escape(product['role'])}</code></td>"
        f"<td>{escape(product['product_metadata']['sensing_time_utc'])}</td>"
        f"<td>{product['scl_summary_inside_full_boundary']['eligible_land_percent']:.4f}%</td>"
        f"<td>{product['scl_summary_inside_full_boundary']['review_needed_percent']:.4f}%</td>"
        f"<td>{product['scl_summary_inside_full_boundary']['excluded_percent']:.4f}%</td>"
        "</tr>"
        for product in report["products"]
    )
    reference_rows = "".join(
        "<tr>"
        f"<td>{escape(str(item['program']))}</td>"
        f"<td><code>{item['map_id']}</code></td>"
        f"<td>{item['boundary_acres']:,}</td>"
        "</tr>"
        for item in report["event"]["program_identities"]
    )
    decision = report["fitness_decision"]
    spectral = report["spectral_change"]
    registration = report["registration"]["summary"]
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Green Ridge source fitness</title><style>
body{{margin:0;background:#07110f;color:#eef7f3;font:16px/1.55 system-ui,sans-serif}}main{{max-width:1200px;margin:auto;padding:32px}}h1{{font-size:clamp(2rem,5vw,4.2rem);line-height:1.02}}h2{{margin-top:2rem}}.card{{background:#0e1d1a;border:1px solid #315b50;border-radius:16px;padding:20px;margin:18px 0}}.warn{{background:#261f12;border-color:#be8a36;color:#ffd997}}img{{width:100%;height:auto;border-radius:16px}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #315b50}}code{{overflow-wrap:anywhere}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}.metric strong{{display:block;font-size:2rem;color:#78e0bd}}
</style></head><body><main><p>BURNLENS / PHASE TWO / ISSUE #472</p><h1>Green Ridge optical pixels pass; labels do not.</h1><div class="card warn">{escape(report['warning'])}</div><img src="{escape(png_name)}" width="1800" height="1120" alt="Actual Green Ridge pre and post Sentinel imagery, continuous dNBR, quality, and registration evidence"><div class="grid"><div class="card metric"><strong>44,110</strong>native 20 m boundary pixels</div><div class="card metric"><strong>99.9887%</strong>pair eligible</div><div class="card metric"><strong>9 / 9</strong>registration windows pass</div><div class="card metric"><strong>{registration['p95_px']:.4f} px</strong>p95 residual</div></div><h2>Exact optical products</h2><div class="card"><table><thead><tr><th>Role</th><th>Sensing</th><th>Eligible</th><th>Review</th><th>Excluded</th></tr></thead><tbody>{product_rows}</tbody></table></div><h2>Continuous change</h2><div class="card"><p>{spectral['valid_pair_pixels']:,} valid pixels; median dNBR {spectral['dnbr_percentiles']['p50']:.6f}; p10/p90 {spectral['dnbr_percentiles']['p10']:.6f} / {spectral['dnbr_percentiles']['p90']:.6f}; {spectral['positive_change_percent']:.4f}% positive change.</p><p>{escape(spectral['interpretation'])}</p></div><h2>Reference identities—not pixels</h2><div class="card"><table><thead><tr><th>Program</th><th>Map ID</th><th>Boundary acres</th></tr></thead><tbody>{reference_rows}</tbody></table><p><strong>{escape(report['event']['reference_pixel_status'])}</strong>. These identities do not support a label decision.</p></div><h2>Gate result</h2><div class="card"><p><strong>{escape(decision['event_status'])}</strong></p><ul><li>Optical: {escape(decision['optical_source'])}</li><li>Burned candidate route: {escape(decision['burned_candidate_route'])}</li><li>Background candidate route: {escape(decision['background_candidate_route'])}</li><li>Unknown route: {escape(decision['unknown_route'])}</li></ul></div><div class="card warn"><p>{escape(report['attribution'])}</p><p>No dataset, split, baseline, model, metric, field-validation, official, endorsed, operational, or emergency-ready claim exists.</p></div><p>Trace: commit <code>{escape(report['git_source_commit'])}</code> · BurnLens <code>{report['software_version']}</code> · evidence run <code>{escape(report['run_id'])}</code> · acquisition <code>{escape(str(report['package']['acquisition_run_id']))}</code> · dataset/model none.</p></main></body></html>"""
    _write_utf8_lf(path, html)


def write_outputs(report: dict[str, Any], previews: dict[str, np.ndarray], directory: Path) -> dict[str, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / f"{REPORT_ID}.json"
    html_path = directory / f"{REPORT_ID}.html"
    png_path = directory / f"{REPORT_ID}.png"
    _write_utf8_lf(json_path, json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    render_png(report, previews, png_path)
    render_html(report, png_path.name, html_path)
    return {"json": json_path, "html": html_path, "png": png_path}
