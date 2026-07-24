"""Build the exact two-class Windigo proposal without promoting labels."""

from __future__ import annotations

import argparse
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw
import rasterio

from .content_registration import _summary as registration_summary
from .cross_event_source_fitness import _read_product, measure_event_registration
from .green_ridge_background_evidence import _component_sizes, _context_geometry
from .green_ridge_region_proposal import (
    PIXEL_AREA_HA,
    TARGET_PIXELS,
    _evidence_image,
    _panel,
    select_region,
)
from .label_proposal import (
    BURN_DNBR_MIN,
    BURN_NEIGHBOR_SUPPORT_MIN,
    BURN_NDVI_LOSS_MIN,
    BURN_NIR_LOSS_MIN,
    BURN_SUPPORTING_SIGNALS_MIN,
    BURN_SWIR_GAIN_MIN,
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
from .region_candidate_pilot import _align_tci_to_grid
from .windigo_optical_contract import EVENT_GROUP_ID, EVENT_ID, POST_CONTRACT, PRE_CONTRACT, SOFTWARE_VERSION
from .windigo_source_fitness import (
    ARCHIVE_SHA256,
    SELECTED_RASTERS,
    _find_member,
    _inspect_native_rasters,
    _load_official_geometry,
    _sample_reference,
    build_report as build_source_report,
)


REPORT_ID = "WINDIGO-REGION-PROPOSAL-2026-001"
REPORT_VERSION = "windigo-two-class-region-proposal-v0.1.0"
GENERATOR_VERSION = "windigo-region-proposal-generator-v0.1.0"
PROTOCOL_VERSION = "windigo-two-scene-two-class-proposal-protocol-v0.1.0"
TASK_ISSUE = 534
UNIT_ID = "P2O4-T35-U04"
RUN_ID = "BL-2026-07-23-windigo-region-proposal-r001"
SOURCE_REPORT_ID = "WINDIGO-SOURCE-FITNESS-2026-006"
SOURCE_REPORT_SHA256 = "7e0ede49bcee692c130c6f04fe90898f6c393fb57f64191da1f16c1567b724b2"
LABEL_SET_VERSION = "owner-approved-prototype-region-labels-v0.3.0"
LABEL_SCHEMA_VERSION = "burn-scar-five-state-schema-v0.1.0"
TARGET_VERSION = "target-burn-scar-v0.2.0"
CONTEXT_BUFFER_M = 3_000
REFERENCE_BUFFER_PIXELS = 3
REFERENCE_BUFFER_M = 60
EXPECTED_CONTEXT_SHAPE = (453, 458)
EXPECTED_COUNTS = {
    "quality_eligible": 205_548,
    "quality_review_needed": 159,
    "quality_excluded": 1_767,
    "reference_footprint_union": 10_870,
    "reference_footprint_buffer": 13_335,
    "burned_route": 8_606,
    "background_route": 182,
    "background_largest_component": 30,
}


class WindigoRegionProposalError(RuntimeError):
    """The exact Windigo two-class proposal failed closed."""


def _file_digest(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _read_source_report(path: Path) -> dict[str, Any]:
    if not path.is_file() or _file_digest(path) != SOURCE_REPORT_SHA256:
        raise WindigoRegionProposalError("accepted U03 source report binding mismatch")
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise WindigoRegionProposalError("accepted U03 source report is unreadable") from error
    if (
        report.get("report_id") != SOURCE_REPORT_ID
        or report.get("run_id") != "BL-2026-07-23-windigo-source-fitness-r006"
        or report.get("label_set_version") != LABEL_SET_VERSION
        or report.get("dataset_version") is not None
        or report.get("model_version") is not None
        or report.get("fitness_decision", {}).get("next_dependency")
        != "P2O4-T35-U04_EXACT_TWO_CARD_PROPOSAL"
    ):
        raise WindigoRegionProposalError("accepted U03 source report semantics drifted")
    return report


def _sample_context_references(
    archive_path: Path,
    *,
    shape: tuple[int, int],
    transform: rasterio.Affine,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    profiles, runtime = _inspect_native_rasters(archive_path)
    sampled: dict[str, np.ndarray] = {}
    members: dict[str, str] = {}
    for key, (_, suffix, _) in SELECTED_RASTERS.items():
        member = _find_member(list(runtime), suffix)
        profile = next(item for item in profiles if item["member"] == member)
        sampled[key] = _sample_reference(
            {"profile": profile, **runtime[member]},
            shape=shape,
            transform=transform,
        )
        members[key] = member
    baer_footprint = np.isin(sampled["baer_sbs"], (1, 2, 3, 4))
    mtbs_footprint = np.isin(sampled["mtbs_dnbr6"], (1, 2, 3, 4, 5, 6))
    ravg_footprint = np.isin(sampled["ravg_cbi4"], (1, 2, 3, 4, 9))
    footprint_union = baer_footprint | mtbs_footprint | ravg_footprint
    footprint_buffer = dilate_mask(footprint_union, REFERENCE_BUFFER_PIXELS)
    masks = {
        **sampled,
        "baer_footprint": baer_footprint,
        "mtbs_footprint": mtbs_footprint,
        "ravg_footprint": ravg_footprint,
        "footprint_union": footprint_union,
        "footprint_buffer": footprint_buffer,
    }
    report = {
        "members": members,
        "categorical_sampling": (
            "nearest neighbor from each native reference grid onto the 20 m context grid; "
            "no resolution gain"
        ),
        "baer_sbs_domain_footprint_pixels": int(baer_footprint.sum()),
        "mtbs_domain_footprint_pixels": int(mtbs_footprint.sum()),
        "ravg_cbi_domain_footprint_pixels": int(ravg_footprint.sum()),
        "program_footprint_union_pixels": int(footprint_union.sum()),
        "program_footprint_buffer_pixels": int(footprint_buffer.sum()),
        "buffer_pixels": REFERENCE_BUFFER_PIXELS,
        "buffer_m": REFERENCE_BUFFER_M,
        "buffer_basis": "three native 20 m proposal cells, equal to two native 30 m MTBS/RAVG cells",
        "role": (
            "Every program domain is used only for conservative exclusion. "
            "RAVG modeled classes and every low/zero class remain disallowed as affirmative background evidence."
        ),
    }
    return masks, report


def _spectral_routes(
    pre_scene: dict[str, Any],
    pre: dict[str, np.ndarray],
    post_scene: dict[str, Any],
    post: dict[str, np.ndarray],
    reference: dict[str, np.ndarray],
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    pair_quality, _ = classify_pair_quality(pre["SCL"], post["SCL"])
    evidence, numeric_valid = spectral_evidence(pre_scene, pre, post_scene, post)
    usable = (pair_quality == 0) & numeric_valid
    support_count = (
        (evidence["ndvi_loss"] >= BURN_NDVI_LOSS_MIN).astype(np.uint8)
        + (evidence["swir_gain"] >= BURN_SWIR_GAIN_MIN).astype(np.uint8)
        + (evidence["nir_loss"] >= BURN_NIR_LOSS_MIN).astype(np.uint8)
    )
    burn_screen = (
        (evidence["dnbr"] >= BURN_DNBR_MIN)
        & (support_count >= BURN_SUPPORTING_SIGNALS_MIN)
    )
    burn_coherent = burn_screen & (
        neighbor_support(burn_screen) >= BURN_NEIGHBOR_SUPPORT_MIN
    )
    stable_screen = (
        (np.abs(evidence["dnbr"]) <= STABLE_ABS_DNBR_MAX)
        & (np.abs(evidence["ndvi_loss"]) <= STABLE_ABS_NDVI_CHANGE_MAX)
        & (np.abs(evidence["swir_gain"]) <= STABLE_ABS_SWIR_CHANGE_MAX)
        & (np.abs(evidence["nir_loss"]) <= STABLE_ABS_NIR_CHANGE_MAX)
    )
    stable_coherent = stable_screen & (
        neighbor_support(stable_screen) >= STABLE_NEIGHBOR_SUPPORT_MIN
    )
    burned_route = (
        usable
        & burn_coherent
        & np.isin(reference["baer_sbs"], (2, 3, 4))
        & np.isin(reference["mtbs_dnbr6"], (2, 3, 4))
    )
    background_route = usable & stable_coherent & ~reference["footprint_buffer"]
    counts = {
        "quality_eligible": int((pair_quality == 0).sum()),
        "quality_review_needed": int((pair_quality == 1).sum()),
        "quality_excluded": int((pair_quality == 2).sum()),
        "numeric_valid": int(numeric_valid.sum()),
        "usable": int(usable.sum()),
        "burn_screen_coherent": int(burn_coherent.sum()),
        "stable_screen_coherent": int(stable_coherent.sum()),
        "burned_route": int(burned_route.sum()),
        "background_route": int(background_route.sum()),
    }
    if {
        key: counts[key]
        for key in ("quality_eligible", "quality_review_needed", "quality_excluded")
    } != {
        key: EXPECTED_COUNTS[key]
        for key in ("quality_eligible", "quality_review_needed", "quality_excluded")
    }:
        raise WindigoRegionProposalError("context optical-quality counts drifted")
    return {
        **evidence,
        "pair_quality": pair_quality,
        "numeric_valid": numeric_valid,
        "usable": usable,
        "burn_screen": burn_screen,
        "burn_coherent": burn_coherent,
        "stable_screen": stable_screen,
        "stable_coherent": stable_coherent,
        "burned_route": burned_route,
        "background_route": background_route,
    }, {
        "counts": counts,
        "thresholds": {
            "burn_dnbr_min": BURN_DNBR_MIN,
            "burn_ndvi_loss_min": BURN_NDVI_LOSS_MIN,
            "burn_swir_gain_min": BURN_SWIR_GAIN_MIN,
            "burn_nir_loss_min": BURN_NIR_LOSS_MIN,
            "burn_supporting_signals_min": BURN_SUPPORTING_SIGNALS_MIN,
            "burn_neighbor_support_min_of_nine": BURN_NEIGHBOR_SUPPORT_MIN,
            "stable_abs_dnbr_max": STABLE_ABS_DNBR_MAX,
            "stable_abs_ndvi_change_max": STABLE_ABS_NDVI_CHANGE_MAX,
            "stable_abs_swir_change_max": STABLE_ABS_SWIR_CHANGE_MAX,
            "stable_abs_nir_change_max": STABLE_ABS_NIR_CHANGE_MAX,
            "stable_neighbor_support_min_of_nine": STABLE_NEIGHBOR_SUPPORT_MIN,
        },
        "transfer": (
            "The established four-signal burn and stability screens transfer unchanged. "
            "No threshold, bin, component size, or tie-break was searched against Windigo."
        ),
    }


def _candidate_binding(
    *,
    candidate: dict[str, Any],
    source_report_sha256: str,
) -> str:
    core_rows, core_columns = np.where(candidate["core"])
    ring_rows, ring_columns = np.where(candidate["ring"])
    payload = {
        "event_group_id": EVENT_GROUP_ID,
        "event_id": EVENT_ID,
        "proposed_class": candidate["candidate_class"],
        "source_report_sha256": source_report_sha256,
        "selection_tie_sha256": candidate["selection_tie_sha256"],
        "core_rows_columns": np.column_stack((core_rows, core_columns)).tolist(),
        "ring_rows_columns": np.column_stack((ring_rows, ring_columns)).tolist(),
    }
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def build_report(
    *,
    pre_package: Path,
    post_package: Path,
    archive_path: Path,
    extracted_root: Path,
    boundary_path: Path,
    source_report_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    accepted_source = _read_source_report(source_report_path)
    source_reverification, _ = build_source_report(
        pre_package=pre_package,
        post_package=post_package,
        archive_path=archive_path,
        extracted_root=extracted_root,
        boundary_path=boundary_path,
        generated_at_utc=generated_at_utc,
        run_id=f"{run_id}-source-reverification",
        git_source_commit=git_source_commit,
        pdf_visual_review="PASS_EXACT_FOUR_PROVIDER_MAP_PDFS",
    )
    for key in ("archive", "evidence_comparison", "source_precedence", "fitness_decision"):
        if source_reverification[key] != accepted_source[key]:
            raise WindigoRegionProposalError(f"U03 {key} failed exact reverification")
    geometry, _ = _load_official_geometry(boundary_path)
    context_geometry, context_bounds = _context_geometry(geometry)
    pre_scene, pre = _read_product(
        pre_package,
        PRE_CONTRACT,
        context_geometry,
        expected_processing_baseline="05.10",
    )
    post_scene, post = _read_product(
        post_package,
        POST_CONTRACT,
        context_geometry,
        expected_processing_baseline="05.10",
    )
    shape = pre["B04"].shape
    if (
        shape != EXPECTED_CONTEXT_SHAPE
        or post["B04"].shape != shape
        or pre_scene["rasters"]["B04"]["crop_transform"]
        != post_scene["rasters"]["B04"]["crop_transform"]
    ):
        raise WindigoRegionProposalError("20 m context grid drifted")
    transform = rasterio.Affine(*pre_scene["rasters"]["B04"]["crop_transform"])
    windows, _ = measure_event_registration(pre_scene, pre, post_scene, post)
    registration = registration_summary(windows)
    if (
        registration["machine_decision"] != "PASS_LOCAL_CONTENT_REGISTRATION_GATE"
        or registration["window_count"] != 9
    ):
        raise WindigoRegionProposalError("context registration gate failed")
    reference, reference_report = _sample_context_references(
        archive_path,
        shape=shape,
        transform=transform,
    )
    if (
        reference_report["program_footprint_union_pixels"]
        != EXPECTED_COUNTS["reference_footprint_union"]
        or reference_report["program_footprint_buffer_pixels"]
        != EXPECTED_COUNTS["reference_footprint_buffer"]
    ):
        raise WindigoRegionProposalError("reference exclusion footprint drifted")
    routes, spectral_report = _spectral_routes(
        pre_scene,
        pre,
        post_scene,
        post,
        reference,
    )
    if (
        int(routes["burned_route"].sum()) != EXPECTED_COUNTS["burned_route"]
        or int(routes["background_route"].sum()) != EXPECTED_COUNTS["background_route"]
    ):
        raise WindigoRegionProposalError("two-class route counts drifted")
    background_components = _component_sizes(routes["background_route"])
    if (
        not background_components
        or background_components[0] != EXPECTED_COUNTS["background_largest_component"]
    ):
        raise WindigoRegionProposalError("background component evidence drifted")
    selected = [
        select_region("burned", routes["burned_route"], routes["dnbr"]),
        select_region("background", routes["background_route"], routes["dnbr"]),
    ]
    for index, candidate in enumerate(selected, start=1):
        candidate["candidate_id"] = f"WDP-{index:03d}"
        candidate["proposal_binding_sha256"] = _candidate_binding(
            candidate=candidate,
            source_report_sha256=SOURCE_REPORT_SHA256,
        )
    if [item["core_pixels"] for item in selected] != [TARGET_PIXELS, TARGET_PIXELS]:
        raise WindigoRegionProposalError("candidate core-size contract drifted")
    if np.any(
        (selected[0]["core"] | selected[0]["ring"])
        & (selected[1]["core"] | selected[1]["ring"])
    ):
        raise WindigoRegionProposalError("candidate core/ring footprints overlap")
    public_candidates = [
        {
            "candidate_id": item["candidate_id"],
            "event_group_id": EVENT_GROUP_ID,
            "proposed_class": item["candidate_class"],
            "review_state": "unreviewed-no-promotion",
            "core_pixels": item["core_pixels"],
            "core_area_hectares": round(item["core_pixels"] * PIXEL_AREA_HA, 4),
            "unknown_ring_pixels": item["ring_pixels"],
            "bbox_rows_columns": item["bbox"],
            "dnbr_interval": item["dnbr_interval"],
            "dnbr_observed": item["dnbr_observed"],
            "eligible_component_count": item["eligible_component_count"],
            "evaluated_component_count": item["evaluated_component_count"],
            "selection_tie_sha256": item["selection_tie_sha256"],
            "proposal_binding_sha256": item["proposal_binding_sha256"],
            "candidate_raster": f"{REPORT_ID}-{item['candidate_id']}.tif",
            "candidate_raster_bytes": None,
            "candidate_raster_sha256": None,
            "owner_decision": None,
        }
        for item in selected
    ]
    report = {
        "report_id": REPORT_ID,
        "report_version": REPORT_VERSION,
        "generator_version": GENERATOR_VERSION,
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
        "input_label_set_version": LABEL_SET_VERSION,
        "output_label_set_version": None,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "event": {
            "event_group_id": EVENT_GROUP_ID,
            "event_id": EVENT_ID,
            "fire_name": "WINDIGO",
            "context_buffer_m": CONTEXT_BUFFER_M,
            "context_bounds_utm10n": [round(float(value), 3) for value in context_bounds],
            "context_shape_20m": list(shape),
            "context_transform": list(transform)[:6],
        },
        "source_report": {
            "report_id": SOURCE_REPORT_ID,
            "run_id": accepted_source["run_id"],
            "bytes": source_report_path.stat().st_size,
            "sha256": SOURCE_REPORT_SHA256,
            "source_commit": accepted_source["git_source_commit"],
            "label_set_version": accepted_source["label_set_version"],
            "fresh_reverification_run_id": source_reverification["run_id"],
            "archive_sha256": ARCHIVE_SHA256,
        },
        "registration": {
            "summary": registration,
            "windows": windows,
        },
        "spectral_evidence": spectral_report,
        "reference_exclusion": reference_report,
        "route_evidence": {
            "burned": {
                "pixels": int(routes["burned_route"].sum()),
                "area_hectares": round(int(routes["burned_route"].sum()) * PIXEL_AREA_HA, 4),
                "rule": (
                    "Eligible exact-pair pixels; transferred coherent four-signal burn screen; "
                    "BAER SBS classes 2-4 primary; MTBS dNBR6 classes 2-4 corroborating."
                ),
            },
            "background": {
                "pixels": int(routes["background_route"].sum()),
                "area_hectares": round(int(routes["background_route"].sum()) * PIXEL_AREA_HA, 4),
                "component_count": len(background_components),
                "largest_component_pixels": background_components[0],
                "largest_component_sizes_pixels": background_components[:20],
                "rule": (
                    "Eligible exact-pair pixels; transferred coherent four-signal near-zero stability; "
                    "outside the union of all delivered BAER/MTBS/RAVG program domains plus 60 m. "
                    "No delivered low/zero/outside class is affirmative evidence."
                ),
            },
        },
        "method": {
            "candidate_unit": "one intact 8-connected native 20 m component",
            "partition": "fixed 0.05 dNBR bin from the established region-candidate protocol",
            "target_pixels": TARGET_PIXELS,
            "selection": (
                "minimum absolute distance to 25 pixels, then SHA-256 of proposed class, "
                "fixed bin, and ordered native-grid coordinates"
            ),
            "unknown_ring": "one native 20 m pixel around each intact core; never promoted here",
            "invalid_vectors": (
                "BAER/RAVG invalid vectors remain retained and unused. Raster program domains are "
                "conservative exclusion only; valid MTBS geometry remains topology authority."
            ),
        },
        "summary": {
            "candidate_count": 2,
            "class_counts": {"burned": 1, "background": 1},
            "core_pixels": sum(item["core_pixels"] for item in selected),
            "core_area_hectares": round(
                sum(item["core_pixels"] for item in selected) * PIXEL_AREA_HA,
                4,
            ),
            "unknown_ring_pixels": sum(item["ring_pixels"] for item in selected),
            "owner_responses": 0,
            "labels_created": 0,
        },
        "candidates": public_candidates,
        "decision": "PROPOSE_EXACT_WINDIGO_TWO_CLASS_REGIONS_KEEP_OWNER_REVIEW_AND_PROMOTION_CLOSED",
        "next_gate": (
            "P2O4-T35-U05 must build one exact two-card owner yes/no/uncertain surface "
            "bound to these candidate raster hashes. Both yes decisions are necessary but insufficient."
        ),
        "limitations": [
            "The fixed spectral rules, dNBR bins, component target, and tie-break are evidence-coherence rules, not universal burn or severity thresholds.",
            "BAER/MTBS agreement and paired optical stability are proposal evidence, not independent ground truth.",
            "The background proposal shows stability during the exact fire-window pair outside conservative source domains; it does not prove land was never burned.",
            "RAVG modeled effects are context and conservative exclusion only, never affirmative candidate evidence.",
            "Only one burned and one background proposal are created; owner review and every non-owner promotion gate remain absent.",
        ],
        "claims": {
            "proven": [
                "Both exact proposal routes and their selected intact components reproduce from immutable custody.",
                "The two candidate core/ring footprints do not overlap and preserve per-candidate bindings.",
            ],
            "not_proven": [
                "No owner decision, label, event-six acceptance, dataset, split, baseline, model, metric, accuracy, independent validation, field validation, official status, endorsement, emergency suitability, or operational readiness exists."
            ],
        },
        "deadline": {
            "portfolio_submission": "2026-08-06",
            "sixth_event_cutoff": "2026-07-27T18:00:00-04:00",
            "fallback": "technical-case-study-only",
        },
        "warning": WARNING,
    }
    previews = {
        "pre_tci": pre["TCI"],
        "post_tci": post["TCI"],
        "grid_transform": transform,
        "routes": routes,
        "reference": reference,
    }
    return report, selected, previews


def _aligned_tci(previews: dict[str, Any], key: str) -> Image.Image:
    transform = previews["grid_transform"]
    shape = previews["routes"]["burned_route"].shape
    aligned = _align_tci_to_grid(
        previews[key],
        rasterio.Affine(
            transform.a / 2,
            0,
            transform.c,
            0,
            transform.e / 2,
            transform.f,
        ),
        transform,
        shape,
        "EPSG:32610",
    )
    return Image.fromarray(
        np.moveaxis(aligned, 0, 2).astype(np.uint8),
        mode="RGB",
    )


def _mask_image(mask: np.ndarray, color: tuple[int, int, int]) -> Image.Image:
    rgb = np.zeros((*mask.shape, 3), dtype=np.uint8)
    rgb[:] = (22, 31, 29)
    rgb[mask] = color
    return Image.fromarray(rgb, mode="RGB")


def render_png(
    report: dict[str, Any],
    selected: list[dict[str, Any]],
    previews: dict[str, Any],
    path: Path,
) -> None:
    canvas = Image.new("RGB", (1800, 1040), "#07110f")
    draw = ImageDraw.Draw(canvas)
    draw.text((55, 34), "BURNLENS / WINDIGO TWO-CLASS PROPOSAL", fill="#b9d8cf", font=_font(22))
    draw.text(
        (55, 72),
        "Two exact review candidates; zero owner decisions or labels.",
        fill="#eef7f3",
        font=_font(30),
    )
    draw.text(
        (55, 116),
        "BAER-primary burned evidence and separate optical-stability background evidence.",
        fill="#ffca73",
        font=_font(17),
    )
    pre = _aligned_tci(previews, "pre_tci")
    post = _aligned_tci(previews, "post_tci")
    routes = previews["routes"]
    reference = previews["reference"]
    for row, item in enumerate(selected):
        top = 158 + row * 370
        draw.rounded_rectangle(
            (45, top, 1755, top + 340),
            radius=15,
            fill="#0e1d1a",
            outline="#315b50",
            width=2,
        )
        draw.text(
            (65, top + 17),
            (
                f"{item['candidate_id']} / proposed {item['candidate_class']} / "
                f"core {item['core_pixels']} px / unknown ring {item['ring_pixels']} px"
            ),
            fill="#eef7f3",
            font=_font(18),
        )
        if item["candidate_class"] == "burned":
            sources = (
                pre,
                post,
                _evidence_image(routes["dnbr"], "dnbr"),
                _evidence_image(reference["baer_sbs"], "reference"),
                _evidence_image(reference["mtbs_dnbr6"], "reference"),
            )
            labels = ("pre 2022", "post 2022", "pre/post dNBR", "BAER SBS 2-4", "MTBS 2-4")
        else:
            sources = (
                pre,
                post,
                _evidence_image(routes["dnbr"], "dnbr"),
                _mask_image(routes["stable_coherent"], (72, 150, 124)),
                _mask_image(~reference["footprint_buffer"], (72, 150, 124)),
            )
            labels = (
                "pre 2022",
                "post 2022",
                "near-zero dNBR",
                "coherent stability",
                "outside source buffer",
            )
        for column, (source, label) in enumerate(zip(sources, labels, strict=True)):
            left = 65 + column * 338
            canvas.paste(_panel(source, item, (300, 225)), (left, top + 58))
            draw.text((left, top + 292), label, fill="#b9d8cf", font=_font(14))
        draw.text(
            (65, top + 316),
            f"binding {item['proposal_binding_sha256'][:24]}… / fixed dNBR bin {item['dnbr_interval']}",
            fill="#78e0bd",
            font=_font(13),
        )
    draw.rounded_rectangle(
        (55, 914, 1745, 984),
        radius=14,
        fill="#261f12",
        outline="#be8a36",
        width=2,
    )
    draw.text((78, 927), WARNING, fill="#ffd997", font=_font(14))
    draw.text(
        (78, 955),
        "Both candidates remain unreviewed. RAVG and all low/zero classes are not affirmative evidence.",
        fill="#ffd997",
        font=_font(14),
    )
    draw.text(
        (55, 1002),
        (
            f"TRACE {report['git_source_commit'][:12]} / {report['run_id']} / "
            f"BurnLens {SOFTWARE_VERSION} / labels-dataset-model none"
        ),
        fill="#b9d8cf",
        font=_font(13),
    )
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], path: Path) -> None:
    rows = "".join(
        (
            f"<tr><td><code>{escape(item['candidate_id'])}</code></td>"
            f"<td>{escape(item['proposed_class'])}</td>"
            f"<td>{item['core_pixels']}</td><td>{item['unknown_ring_pixels']}</td>"
            f"<td><code>{escape(item['proposal_binding_sha256'])}</code></td>"
            f"<td><a href='{escape(item['candidate_raster'])}'>candidate raster</a></td></tr>"
        )
        for item in report["candidates"]
    )
    burned = report["route_evidence"]["burned"]
    background = report["route_evidence"]["background"]
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Windigo region proposal</title><style>
html,body{{max-width:100%;overflow-x:hidden}}body{{margin:0;background:#07110f;color:#eef7f3;font:16px/1.55 system-ui,sans-serif}}main{{max-width:1200px;margin:auto;padding:32px;box-sizing:border-box}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.02}}.card{{max-width:100%;min-width:0;box-sizing:border-box;background:#0e1d1a;border:1px solid #315b50;border-radius:16px;padding:20px;margin:18px 0;overflow-wrap:anywhere}}.warn{{background:#261f12;border-color:#be8a36;color:#ffd997}}img{{display:block;max-width:100%;width:100%;height:auto;border-radius:16px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}.metric strong{{display:block;font-size:2rem;color:#78e0bd}}table{{width:100%;max-width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #315b50;vertical-align:top;overflow-wrap:anywhere}}code,strong{{overflow-wrap:anywhere}}a{{color:#78e0bd}}@media(max-width:700px){{main{{padding:18px}}.table-card{{overflow-x:auto}}.table-card table{{min-width:900px}}}}
</style></head><body><main><p>BURNLENS / PHASE TWO / ISSUE #534 / U04</p><h1>Two Windigo regions are proposed; neither is a label.</h1><div class="card warn">{escape(report['warning'])}</div><img src="{REPORT_ID}.png" width="1800" height="1040" alt="Actual Windigo burned and background proposal evidence with candidate cores and unknown rings"><div class="grid"><div class="card metric"><strong>2</strong>unreviewed candidates</div><div class="card metric"><strong>{burned['pixels']:,}</strong>burned-route pixels</div><div class="card metric"><strong>{background['pixels']:,}</strong>background-route pixels</div><div class="card metric"><strong>0</strong>owner decisions or labels</div></div><h2>Exact candidates</h2><div class="card table-card"><table><thead><tr><th>ID</th><th>Proposed class</th><th>Core pixels</th><th>Unknown ring</th><th>Binding SHA-256</th><th>Raster</th></tr></thead><tbody>{rows}</tbody></table></div><h2>Conjunctive routes</h2><div class="card"><p><strong>Burned:</strong> {escape(burned['rule'])}</p><p><strong>Background:</strong> {escape(background['rule'])}</p><p>{escape(report['spectral_evidence']['transfer'])}</p></div><h2>Boundaries</h2><div class="card"><ul>{''.join(f'<li>{escape(item)}</li>' for item in report['limitations'])}</ul><p><strong>{escape(report['decision'])}</strong></p><p>{escape(report['next_gate'])}</p></div><div class="card warn"><p>No ground truth, owner decision, accepted label, dataset, split, baseline, model, metric, accuracy, field validation, official status, endorsement, emergency suitability, or operational readiness exists.</p></div><p>Trace: commit <code>{escape(report['git_source_commit'])}</code> · run <code>{escape(report['run_id'])}</code> · source <code>{SOURCE_REPORT_SHA256}</code> · BurnLens <code>{SOFTWARE_VERSION}</code>.</p></main></body></html>"""
    _write_utf8_lf(path, html)


def _write_candidate_raster(
    *,
    path: Path,
    candidate: dict[str, Any],
    transform: rasterio.Affine,
    report: dict[str, Any],
) -> None:
    array = np.zeros(candidate["core"].shape, dtype=np.uint8)
    array[candidate["core"]] = 1
    array[candidate["ring"]] = 2
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=array.shape[1],
        height=array.shape[0],
        count=1,
        dtype="uint8",
        crs="EPSG:32610",
        transform=transform,
        nodata=255,
        compress="DEFLATE",
        predictor=2,
    ) as dataset:
        dataset.write(array, 1)
        dataset.update_tags(
            candidate_id=candidate["candidate_id"],
            event_group_id=EVENT_GROUP_ID,
            proposed_class=candidate["candidate_class"],
            kind="unreviewed-core-and-unknown-ring",
            generator_version=GENERATOR_VERSION,
            run_id=report["run_id"],
            git_source_commit=report["git_source_commit"],
            source_report_sha256=SOURCE_REPORT_SHA256,
            proposal_binding_sha256=candidate["proposal_binding_sha256"],
            owner_decision="none",
            label_created="false",
        )


def write_outputs(
    report: dict[str, Any],
    selected: list[dict[str, Any]],
    previews: dict[str, Any],
    directory: Path,
) -> list[Path]:
    if directory.exists():
        raise WindigoRegionProposalError("output directory already exists")
    directory.mkdir(parents=True)
    outputs: list[Path] = []
    by_id = {item["candidate_id"]: item for item in report["candidates"]}
    for candidate in selected:
        path = directory / f"{REPORT_ID}-{candidate['candidate_id']}.tif"
        _write_candidate_raster(
            path=path,
            candidate=candidate,
            transform=previews["grid_transform"],
            report=report,
        )
        public = by_id[candidate["candidate_id"]]
        public["candidate_raster_bytes"] = path.stat().st_size
        public["candidate_raster_sha256"] = _file_digest(path)
        outputs.append(path)
    png_path = directory / f"{REPORT_ID}.png"
    html_path = directory / f"{REPORT_ID}.html"
    json_path = directory / f"{REPORT_ID}.json"
    render_png(report, selected, previews, png_path)
    render_html(report, html_path)
    _write_utf8_lf(json_path, json.dumps(report, indent=2) + "\n")
    return [json_path, html_path, png_path, *outputs]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build exactly one burned and one affirmative-background Windigo "
            "review proposal without creating labels."
        )
    )
    parser.add_argument("--pre-package", required=True, type=Path)
    parser.add_argument("--post-package", required=True, type=Path)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--extracted-root", required=True, type=Path)
    parser.add_argument("--boundary", required=True, type=Path)
    parser.add_argument("--source-report", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", default=RUN_ID)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args()
    report, selected, previews = build_report(
        pre_package=args.pre_package,
        post_package=args.post_package,
        archive_path=args.archive,
        extracted_root=args.extracted_root,
        boundary_path=args.boundary,
        source_report_path=args.source_report,
        generated_at_utc=args.generated_at_utc,
        run_id=args.run_id,
        git_source_commit=args.git_source_commit,
    )
    outputs = write_outputs(report, selected, previews, args.output_directory)
    print(
        f"{report['decision']} "
        + " ".join(f"{path.suffix.lstrip('.')}={path}" for path in outputs)
    )


if __name__ == "__main__":
    main()
