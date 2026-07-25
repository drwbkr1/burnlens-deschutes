"""Establish Ward Creek affirmative-background evidence without a proposal.

The route transfers the frozen four-signal optical-stability screen without
tuning and conservatively excludes the complete native MTBS domain plus
60 meters. It creates no candidate, owner decision, label, dataset, split,
baseline, model, metric, or inference output.
"""

from __future__ import annotations

from hashlib import sha256
from html import escape
import json
from pathlib import Path
import subprocess
from typing import Any
from zipfile import ZipFile

import numpy as np
from PIL import Image, ImageDraw
import rasterio

from .content_registration import _summary as registration_summary
from .cross_event_source_fitness import _read_product, measure_event_registration
from .green_ridge_background_evidence import _component_sizes, _context_geometry
from .green_ridge_source_fitness import _preview_tci
from .label_proposal import (
    STABLE_ABS_DNBR_MAX,
    STABLE_ABS_NDVI_CHANGE_MAX,
    STABLE_ABS_NIR_CHANGE_MAX,
    STABLE_ABS_SWIR_CHANGE_MAX,
    STABLE_NEIGHBOR_SUPPORT_MIN,
    dilate_mask,
    neighbor_support,
    spectral_evidence,
)
from .optical_pair_evidence import WARNING, _font, _write_utf8_lf, classify_pair_quality
from .paired_intake import verify_registered_package
from .replacement_event_optical_contract import (
    CONTRACT_VERSION,
    EVENT_GROUP_ID,
    EVENT_ID,
    POST_CONTRACT,
    PRE_CONTRACT,
    SOFTWARE_VERSION,
    _singleton_validator,
)
from .replacement_event_reference_fitness import (
    ARCHIVE_SHA256,
    EXPECTED_DNBR6_DOMAIN,
    EXPECTED_RASTERS,
    MAP_ID,
    _inspect_archive,
    _inspect_metadata,
    _inspect_raster,
    _load_boundary,
    _sample_reference,
)


REPORT_ID = "WARD-CREEK-BACKGROUND-EVIDENCE-2026-001"
REPORT_VERSION = "ward-creek-background-evidence-v0.1.0"
PROTOCOL_VERSION = "ward-creek-paired-stability-background-route-v0.1.0"
UNIT_ID = "P2O4-T39-U04"
TASK_ISSUE = 554
RUN_ID = "BL-2026-07-24-ward-creek-background-evidence-r001"
SOURCE_REPORT_ID = "WARD-CREEK-REFERENCE-FITNESS-2026-002"
SOURCE_REPORT_RUN_ID = "BL-2026-07-24-ward-creek-reference-fitness-r003"
SOURCE_REPORT_SHA256 = "f31bc51c64dae60b5a419146f4183b960b8504044f79e7505018a630c47c466d"
SOURCE_REPORT_COMMIT = "b1614fe0260c46570366e6bbe22f74fd24cb7523"
TARGET_VERSION = "target-burn-scar-v0.2.0"
LABEL_SCHEMA_VERSION = "burn-scar-binary-region-label-schema-v0.3.0"
INPUT_LABEL_SET_VERSION = "owner-approved-prototype-region-labels-v0.4.0"
CONTEXT_BUFFER_M = 3_000
REFERENCE_BUFFER_PIXELS = 3
REFERENCE_BUFFER_M = 60
ONE_HECTARE_PIXELS = 25
PIXEL_AREA_HECTARES = 0.04
EXPECTED_CONTEXT_SHAPE = (519, 483)
EXPECTED_COUNTS = {
    "quality_eligible": 250_582,
    "quality_review_needed": 67,
    "quality_excluded": 28,
    "numeric_valid": 250_677,
    "stable": 56_485,
    "coherent": 21_598,
    "mtbs_footprint": 20_958,
    "mtbs_buffer": 24_128,
    "route": 21_266,
    "component_count": 1_015,
    "largest_component": 1_386,
    "components_at_least_one_hectare": 167,
}


class WardCreekBackgroundEvidenceError(RuntimeError):
    """The exact Ward Creek U04 evidence contract failed closed."""


def _file_digest(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _read_source_report(path: Path) -> dict[str, Any]:
    if not path.is_file() or _file_digest(path) != SOURCE_REPORT_SHA256:
        raise WardCreekBackgroundEvidenceError("accepted U03 source report binding mismatch")
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise WardCreekBackgroundEvidenceError("accepted U03 source report is unreadable") from error
    if (
        report.get("report_id") != SOURCE_REPORT_ID
        or report.get("run_id") != SOURCE_REPORT_RUN_ID
        or report.get("git_source_commit") != SOURCE_REPORT_COMMIT
        or report.get("event", {}).get("event_group_id") != EVENT_GROUP_ID
        or report.get("event", {}).get("event_id") != EVENT_ID
        or report.get("event", {}).get("map_id") != MAP_ID
        or report.get("archive", {}).get("sha256") != ARCHIVE_SHA256
        or report.get("fitness_decision", {}).get("source")
        != "PASS_EXACT_WARD_CREEK_MTBS_SOURCE_FITNESS"
        or report.get("dataset_version") is not None
        or report.get("model_version") is not None
    ):
        raise WardCreekBackgroundEvidenceError("accepted U03 source report semantics drifted")
    return report


def _registration_manifest(package: Path) -> dict[str, Any]:
    try:
        return json.loads((package / ".burnlens-registration.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise WardCreekBackgroundEvidenceError("optical registration manifest unreadable") from error


def _verify_package(package: Path, contract: Any) -> dict[str, Any]:
    result = verify_registered_package(
        package,
        (contract,),
        contract_validator=_singleton_validator(contract),
        contract_version=CONTRACT_VERSION,
        allow_multilink_registration_manifest=True,
    )
    if not result["accepted_as_unchanged_registered_package"]:
        raise WardCreekBackgroundEvidenceError(f"{contract.role} package verification failed")
    return result


def _spectral_route(
    pre_scene: dict[str, Any],
    pre: dict[str, np.ndarray],
    post_scene: dict[str, Any],
    post: dict[str, np.ndarray],
    mtbs_values: np.ndarray,
    mtbs_profile: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    shape = pre["B04"].shape
    if shape != EXPECTED_CONTEXT_SHAPE or post["B04"].shape != shape:
        raise WardCreekBackgroundEvidenceError("context optical shape drifted")
    if (
        pre_scene["rasters"]["B04"]["crop_transform"]
        != post_scene["rasters"]["B04"]["crop_transform"]
    ):
        raise WardCreekBackgroundEvidenceError("context optical grid drifted")
    transform = rasterio.Affine(*pre_scene["rasters"]["B04"]["crop_transform"])
    pair_quality, _ = classify_pair_quality(pre["SCL"], post["SCL"])
    evidence, numeric_valid = spectral_evidence(pre_scene, pre, post_scene, post)
    usable = (pair_quality == 0) & numeric_valid
    stable = (
        (np.abs(evidence["dnbr"]) <= STABLE_ABS_DNBR_MAX)
        & (np.abs(evidence["ndvi_loss"]) <= STABLE_ABS_NDVI_CHANGE_MAX)
        & (np.abs(evidence["swir_gain"]) <= STABLE_ABS_SWIR_CHANGE_MAX)
        & (np.abs(evidence["nir_loss"]) <= STABLE_ABS_NIR_CHANGE_MAX)
    )
    coherent = stable & (neighbor_support(stable) >= STABLE_NEIGHBOR_SUPPORT_MIN)
    sampled_mtbs = _sample_reference(mtbs_values, mtbs_profile, shape, transform)
    mtbs_footprint = np.isin(sampled_mtbs, (1, 2, 3, 4, 5, 6))
    mtbs_buffer = dilate_mask(mtbs_footprint, REFERENCE_BUFFER_PIXELS)
    route = usable & coherent & ~mtbs_buffer
    components = _component_sizes(route)
    one_hectare = [size for size in components if size >= ONE_HECTARE_PIXELS]
    counts = {
        "quality_eligible": int((pair_quality == 0).sum()),
        "quality_review_needed": int((pair_quality == 1).sum()),
        "quality_excluded": int((pair_quality == 2).sum()),
        "numeric_valid": int(numeric_valid.sum()),
        "stable": int(stable.sum()),
        "coherent": int(coherent.sum()),
        "mtbs_footprint": int(mtbs_footprint.sum()),
        "mtbs_buffer": int(mtbs_buffer.sum()),
        "route": int(route.sum()),
        "component_count": len(components),
        "largest_component": components[0] if components else 0,
        "components_at_least_one_hectare": len(one_hectare),
    }
    if counts != EXPECTED_COUNTS:
        raise WardCreekBackgroundEvidenceError(
            f"frozen paired-stability route drifted: expected {EXPECTED_COUNTS}, found {counts}"
        )
    return {
        "counts": counts,
        "largest_component_sizes_pixels": components[:20],
        "eligible_area_hectares": round(counts["route"] * PIXEL_AREA_HECTARES, 4),
        "largest_component_hectares": round(
            counts["largest_component"] * PIXEL_AREA_HECTARES,
            4,
        ),
        "thresholds": {
            "stable_abs_dnbr_max": STABLE_ABS_DNBR_MAX,
            "stable_abs_ndvi_change_max": STABLE_ABS_NDVI_CHANGE_MAX,
            "stable_abs_swir_change_max": STABLE_ABS_SWIR_CHANGE_MAX,
            "stable_abs_nir_change_max": STABLE_ABS_NIR_CHANGE_MAX,
            "stable_neighbor_support_min_of_nine": STABLE_NEIGHBOR_SUPPORT_MIN,
            "mtbs_domain_buffer_pixels": REFERENCE_BUFFER_PIXELS,
            "mtbs_domain_buffer_meters": REFERENCE_BUFFER_M,
            "minimum_intact_component_pixels": ONE_HECTARE_PIXELS,
        },
        "rule": (
            "Eligible exact pre/post pixels; the frozen four-signal near-zero stability screen "
            "transferred without tuning; at least seven stable neighbors of nine; outside the "
            "complete native MTBS class 1-6 domain plus 60 meters. No signal is sufficient alone."
        ),
        "transfer": (
            "No threshold, support count, buffer, component threshold, or tie-break was searched "
            "against Ward Creek. This unit selects no component and creates no proposal."
        ),
    }, {
        **evidence,
        "pair_quality": pair_quality,
        "numeric_valid": numeric_valid,
        "usable": usable,
        "stable": stable,
        "coherent": coherent,
        "sampled_mtbs": sampled_mtbs,
        "mtbs_footprint": mtbs_footprint,
        "mtbs_buffer": mtbs_buffer,
        "route": route,
        "grid_transform": transform,
    }


def build_report(
    *,
    repository_root: Path,
    pre_package: Path,
    post_package: Path,
    archive_path: Path,
    extracted_root: Path,
    source_report_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    if run_id != RUN_ID:
        raise WardCreekBackgroundEvidenceError("run ID drifted")
    repository_root = repository_root.resolve()
    top = subprocess.run(
        ["git", "-C", str(repository_root), "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    head = subprocess.run(
        ["git", "-C", str(repository_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if Path(top).resolve() != repository_root:
        raise WardCreekBackgroundEvidenceError("repository root is not the canonical checkout")
    if len(git_source_commit) != 40 or git_source_commit != head:
        raise WardCreekBackgroundEvidenceError("git source commit must equal repository HEAD")

    accepted_source = _read_source_report(source_report_path)
    pre_verification = _verify_package(pre_package, PRE_CONTRACT)
    post_verification = _verify_package(post_package, POST_CONTRACT)
    archive_report = _inspect_archive(archive_path)
    with ZipFile(archive_path) as archive:
        terms = _inspect_metadata(archive)
        boundary_wgs84, boundary = _load_boundary(archive, extracted_root)
        mtbs_profile, mtbs_values = _inspect_raster(archive, EXPECTED_RASTERS["dnbr6"])
    if mtbs_profile["native_value_domain"] != EXPECTED_DNBR6_DOMAIN:
        raise WardCreekBackgroundEvidenceError("native MTBS class domain drifted")

    context_geometry, context_bounds = _context_geometry(boundary_wgs84)
    pre_scene, pre = _read_product(pre_package, PRE_CONTRACT, context_geometry)
    post_scene, post = _read_product(post_package, POST_CONTRACT, context_geometry)
    registration_windows, _ = measure_event_registration(pre_scene, pre, post_scene, post)
    registration = registration_summary(registration_windows)
    if (
        registration["machine_decision"] != "PASS_LOCAL_CONTENT_REGISTRATION_GATE"
        or registration["window_count"] != 9
        or registration["state_counts"]["pass"] != 9
    ):
        raise WardCreekBackgroundEvidenceError("context registration gate failed")
    route_report, route = _spectral_route(
        pre_scene,
        pre,
        post_scene,
        post,
        mtbs_values,
        mtbs_profile,
    )
    pre_manifest = _registration_manifest(pre_package)
    post_manifest = _registration_manifest(post_package)
    report = {
        "report_id": REPORT_ID,
        "report_version": REPORT_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "unit_id": UNIT_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": None,
        "target_version": TARGET_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "input_label_set_version": INPUT_LABEL_SET_VERSION,
        "output_label_set_version": None,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "event": {
            "event_group_id": EVENT_GROUP_ID,
            "event_id": EVENT_ID,
            "fire_name": "WARD CREEK 0769 RN",
            "map_id": MAP_ID,
            "context_buffer_meters": CONTEXT_BUFFER_M,
            "context_bounds_utm10n": [round(float(value), 3) for value in context_bounds],
            "context_shape_20m": list(EXPECTED_CONTEXT_SHAPE),
            "context_transform": [float(value) for value in route["grid_transform"][:6]],
        },
        "accepted_u03_source": {
            "report_id": accepted_source["report_id"],
            "run_id": accepted_source["run_id"],
            "git_source_commit": accepted_source["git_source_commit"],
            "bytes": source_report_path.stat().st_size,
            "sha256": SOURCE_REPORT_SHA256,
            "fitness_decision": accepted_source["fitness_decision"]["source"],
        },
        "custody_reverification": {
            "pre_package": {
                "package_id": PRE_CONTRACT.package_id,
                "run_id": pre_manifest["run_id"],
                "provider_bytes": PRE_CONTRACT.expected_size_bytes,
                "registration_manifest_sha256": pre_verification[
                    "registration_manifest_sha256"
                ],
                "reason_codes": pre_verification["reason_codes"],
            },
            "post_package": {
                "package_id": POST_CONTRACT.package_id,
                "run_id": post_manifest["run_id"],
                "provider_bytes": POST_CONTRACT.expected_size_bytes,
                "registration_manifest_sha256": post_verification[
                    "registration_manifest_sha256"
                ],
                "reason_codes": post_verification["reason_codes"],
            },
            "mtbs_archive": archive_report,
        },
        "terms_and_source_roles": {
            "embedded_notice_decision": terms["decision"],
            "fgdc_sha256": terms["fgdc"]["sha256"],
            "iso_sha256": terms["iso"]["sha256"],
            "mtbs_role": (
                "The complete native MTBS class 1-6 domain is conservative exclusion context "
                "only. No MTBS low, zero, outside, or other class is affirmative background evidence."
            ),
            "optical_role": (
                "The exact pre/post pair supplies transferred multi-signal stability evidence. "
                "Stability does not prove land was never burned."
            ),
            "attribution": (
                "Contains modified Copernicus Sentinel data 2019, accessed through CDSE; "
                "Monitoring Trends in Burn Severity Project "
                "(U.S. Geological Survey and USDA Forest Service)."
            ),
        },
        "products": [
            {
                "role": scene["role"],
                "native_id": scene["native_id"],
                "provider_id": contract.provider_id,
                "sensing_time_utc": scene["product_metadata"]["sensing_time_utc"],
                "tile_id": scene["product_metadata"]["tile_id"],
                "processing_baseline": scene["product_metadata"]["processing_baseline"],
            }
            for scene, contract in ((pre_scene, PRE_CONTRACT), (post_scene, POST_CONTRACT))
        ],
        "mtbs_domain": {
            "member": mtbs_profile["member"],
            "bytes": mtbs_profile["bytes"],
            "sha256": mtbs_profile["sha256"],
            "crs": mtbs_profile["crs"],
            "native_resolution_meters": mtbs_profile["resolution_m"],
            "native_value_domain": mtbs_profile["native_value_domain"],
            "sampling": "nearest neighbor onto the 20 m context grid; no resolution gain",
            "footprint_definition": "native encoded classes 1-6",
            "buffer_meters": REFERENCE_BUFFER_M,
            "buffer_basis": (
                "60 meters equals two native 30-meter MTBS cells and retains source-grid "
                "and mixed-boundary uncertainty."
            ),
            "boundary": {
                "valid": boundary["valid"],
                "crs": boundary["crs"],
                "area_square_meters": boundary["area_square_meters"],
            },
        },
        "registration": {
            "summary": registration,
            "windows": registration_windows,
        },
        "route_evidence": {
            **route_report,
            "candidate_regions_created": 0,
            "owner_responses": 0,
            "labels_created": 0,
        },
        "fitness_decision": {
            "background_evidence_route": "OPEN_AFFIRMATIVE_BACKGROUND_EVIDENCE_ROUTE",
            "checkpoint": (
                "ACCEPT_WARD_CREEK_AFFIRMATIVE_BACKGROUND_ROUTE_"
                "DEFER_CANDIDATES_LABELS_DATASET_MODEL"
            ),
            "next_dependency": "P2O4-T39-U05_EXACT_TWO_CLASS_PROPOSAL",
        },
        "claims": {
            "proven": [
                "The exact pair, MTBS archive, embedded notices, source report, and native domain reproduce from immutable custody.",
                "All nine context registration windows pass.",
                "A transferred multi-signal optical-stability route has intact components outside the complete MTBS domain plus 60 meters.",
            ],
            "not_proven": [
                "The route is not ground truth, field validation, an official unburned map, a candidate, or a label.",
                "No owner response, accepted dataset, split, baseline, model, metric, accuracy, endorsement, operational readiness, or emergency suitability exists.",
            ],
        },
        "warning": WARNING,
    }
    previews = {
        "pre_tci": pre["TCI"],
        "post_tci": post["TCI"],
        "pre_mask": pre["MASK10"],
        "post_mask": post["MASK10"],
        "dnbr": route["dnbr"],
        "ndvi_loss": route["ndvi_loss"],
        "swir_gain": route["swir_gain"],
        "nir_loss": route["nir_loss"],
        "usable": route["usable"],
        "sampled_mtbs": route["sampled_mtbs"],
        "grid_transform": route["grid_transform"],
        "coherent": route["coherent"],
        "mtbs_footprint": route["mtbs_footprint"],
        "mtbs_buffer": route["mtbs_buffer"],
        "route": route["route"],
    }
    return report, previews


def _mask_preview(
    previews: dict[str, np.ndarray],
    mode: str,
    size: tuple[int, int],
) -> Image.Image:
    shape = previews["route"].shape
    rgb = np.zeros((*shape, 3), dtype=np.uint8)
    rgb[:] = (10, 24, 21)
    if mode == "reference":
        rgb[previews["mtbs_buffer"]] = (185, 132, 56)
        rgb[previews["mtbs_footprint"]] = (190, 72, 50)
    elif mode == "stability":
        rgb[previews["coherent"]] = (102, 203, 168)
    elif mode == "route":
        rgb[previews["mtbs_buffer"]] = (95, 75, 41)
        rgb[previews["route"]] = (54, 222, 179)
    image = Image.fromarray(rgb, mode="RGB")
    image.thumbnail(size, Image.Resampling.NEAREST)
    canvas = Image.new("RGB", size, "#0a1815")
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def render_png(
    report: dict[str, Any],
    previews: dict[str, np.ndarray],
    path: Path,
) -> None:
    canvas = Image.new("RGB", (1800, 1040), "#07110f")
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (60, 38),
        "BURNLENS / WARD CREEK AFFIRMATIVE-BACKGROUND EVIDENCE",
        fill="#b9d8cf",
        font=_font(21),
    )
    draw.text(
        (60, 76),
        "A background evidence route opens; no candidate or label does.",
        fill="#eef7f3",
        font=_font(30),
    )
    draw.text(
        (60, 122),
        "Transferred paired stability outside the complete native MTBS domain plus 60 m.",
        fill="#ffca73",
        font=_font(17),
    )
    panels = [
        ("PRE 2019-08-01", _preview_tci(previews["pre_tci"], previews["pre_mask"], (520, 315))),
        ("POST 2019-08-31", _preview_tci(previews["post_tci"], previews["post_mask"], (520, 315))),
        ("MTBS DOMAIN + 60 m BUFFER", _mask_preview(previews, "reference", (520, 315))),
        ("TRANSFERRED COHERENT STABILITY", _mask_preview(previews, "stability", (520, 315))),
        ("ELIGIBLE ROUTE EVIDENCE", _mask_preview(previews, "route", (520, 315))),
    ]
    for index, (label, image) in enumerate(panels):
        x = 60 + index * 345
        draw.rounded_rectangle(
            (x, 170, x + 320, 535),
            radius=16,
            fill="#0e1d1a",
            outline="#315b50",
            width=2,
        )
        draw.text((x + 14, 186), label, fill="#eef7f3", font=_font(14))
        image.thumbnail((300, 300), Image.Resampling.NEAREST)
        canvas.paste(image, (x + 10, 224))
    route = report["route_evidence"]
    metrics = [
        (f"{route['counts']['route']:,}", "eligible evidence pixels"),
        (f"{route['eligible_area_hectares']:,.2f} ha", "eligible evidence area"),
        (
            f"{route['counts']['components_at_least_one_hectare']:,}",
            "components at least 1 ha",
        ),
        ("0", "candidate regions / labels"),
    ]
    for index, (value, label) in enumerate(metrics):
        x = 60 + index * 430
        draw.rounded_rectangle(
            (x, 585, x + 395, 705),
            radius=14,
            fill="#0e1d1a",
            outline="#315b50",
            width=2,
        )
        draw.text((x + 20, 605), value, fill="#78e0bd", font=_font(26))
        draw.text((x + 20, 655), label, fill="#b9d8cf", font=_font(14))
    draw.rounded_rectangle(
        (60, 745, 1740, 902),
        radius=14,
        fill="#261f12",
        outline="#be8a36",
        width=2,
    )
    draw.text((82, 765), WARNING, fill="#ffd997", font=_font(15))
    draw.text(
        (82, 804),
        "Paired optical stability is affirmative proposal evidence only; it does not prove land was never burned.",
        fill="#ffd997",
        font=_font(15),
    )
    draw.text(
        (82, 838),
        "MTBS low, zero, outside, and other classes are not affirmative background evidence.",
        fill="#ffd997",
        font=_font(15),
    )
    draw.text(
        (82, 872),
        "No candidate, owner decision, label, dataset, split, baseline, model, or metric exists.",
        fill="#ffd997",
        font=_font(15),
    )
    draw.text(
        (60, 958),
        (
            f"TRACE {report['git_source_commit'][:12]} / {report['run_id']} / "
            f"BurnLens {SOFTWARE_VERSION} / dataset-model none"
        ),
        fill="#b9d8cf",
        font=_font(13),
    )
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], png_name: str) -> str:
    route = report["route_evidence"]
    products = "".join(
        (
            f"<tr><td>{escape(item['role'])}</td>"
            f"<td><code>{escape(item['native_id'])}</code></td>"
            f"<td>{escape(item['sensing_time_utc'])}</td>"
            f"<td>{escape(item['processing_baseline'])}</td></tr>"
        )
        for item in report["products"]
    )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ward Creek background evidence</title><style>
html,body{{max-width:100%;overflow-x:hidden}}body{{margin:0;background:#07110f;color:#eef7f3;font:16px/1.55 system-ui,sans-serif}}main{{max-width:1200px;margin:auto;padding:32px;box-sizing:border-box}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.02}}.card{{max-width:100%;min-width:0;box-sizing:border-box;background:#0e1d1a;border:1px solid #315b50;border-radius:16px;padding:20px;margin:18px 0;overflow-wrap:anywhere}}.warn{{background:#261f12;border-color:#be8a36;color:#ffd997}}img{{display:block;max-width:100%;width:100%;height:auto;border-radius:16px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}.metric strong{{display:block;font-size:2rem;color:#78e0bd}}table{{width:100%;max-width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #315b50;vertical-align:top;overflow-wrap:anywhere}}code,strong{{overflow-wrap:anywhere}}@media(max-width:700px){{main{{padding:18px}}.table-card{{overflow-x:auto}}.table-card table{{min-width:760px}}}}
</style></head><body><main><p>BURNLENS / PHASE TWO / ISSUE #554 / U04</p><h1>A Ward Creek background evidence route opens; no candidate or label does.</h1><div class="card warn">{escape(report['warning'])}</div><img src="{escape(png_name)}" width="1800" height="1040" alt="Actual Ward Creek pre and post optical imagery, MTBS domain and buffer, coherent stability, and eligible background-route evidence"><div class="grid"><div class="card metric"><strong>{route['counts']['route']:,}</strong>eligible evidence pixels</div><div class="card metric"><strong>{route['eligible_area_hectares']:,.2f} ha</strong>eligible evidence area</div><div class="card metric"><strong>{route['counts']['components_at_least_one_hectare']}</strong>components at least one hectare</div><div class="card metric"><strong>0</strong>candidate regions or labels</div></div><h2>Exact optical products</h2><div class="card table-card"><table><thead><tr><th>Role</th><th>Product</th><th>Sensing time</th><th>Baseline</th></tr></thead><tbody>{products}</tbody></table></div><h2>Conjunctive evidence rule</h2><div class="card"><p>{escape(route['rule'])}</p><p>{escape(route['transfer'])}</p><p>Outside-domain status, low change, SCL, or apparent stability is insufficient alone. No MTBS class is affirmative background truth.</p></div><h2>Gate result</h2><div class="card"><p><strong>{escape(report['fitness_decision']['checkpoint'])}</strong></p><p>U05 may separately propose exactly one burned and one background core with unknown rings. This report creates neither.</p></div><div class="card warn"><p>{escape(report['terms_and_source_roles']['attribution'])}</p><p>No ground truth, field validation, official unburned map, owner response, dataset, split, baseline, model, metric, accuracy, endorsement, operational readiness, or emergency suitability exists.</p></div><p>Trace: commit <code>{escape(report['git_source_commit'])}</code> · BurnLens <code>{SOFTWARE_VERSION}</code> · run <code>{escape(report['run_id'])}</code> · label schema <code>{LABEL_SCHEMA_VERSION}</code> · dataset/model none.</p></main></body></html>"""


def write_outputs(
    report: dict[str, Any],
    previews: dict[str, np.ndarray],
    directory: Path,
) -> dict[str, Path]:
    if directory.exists():
        raise WardCreekBackgroundEvidenceError("output directory already exists")
    directory.mkdir(parents=True)
    paths = {
        "json": directory / f"{REPORT_ID}.json",
        "html": directory / f"{REPORT_ID}.html",
        "png": directory / f"{REPORT_ID}.png",
    }
    _write_utf8_lf(paths["json"], json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    render_png(report, previews, paths["png"])
    _write_utf8_lf(paths["html"], render_html(report, paths["png"].name))
    return paths
