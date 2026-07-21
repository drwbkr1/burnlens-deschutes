"""Inspect the exact Petes Lake Sentinel pair and render U03 source fitness."""

from __future__ import annotations

from io import BytesIO
from hashlib import sha256
from html import escape
from datetime import date, datetime
import json
import os
from pathlib import Path
import stat
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

from .content_registration import _summary as registration_summary
from .cross_event_feasibility import LABEL_SCHEMA_VERSION
from .cross_event_source_fitness import (
    _canonical_sha256,
    _read_product,
    measure_event_registration,
)
from .green_ridge_source_fitness import (
    _preview_dnbr,
    _preview_tci,
    summarize_spectral_change,
)
from .optical_pair_evidence import (
    LABEL_PROTOCOL_VERSION,
    TARGET_VERSION,
    WARNING,
    _font,
    _sha256_lf_text,
)
from .petes_lake_optical_contract import (
    CONTRACT_VERSION,
    EVENT_GROUP_ID,
    INITIAL_REVISION,
    PETES_LAKE_CONTRACTS,
    POST_CONTRACT,
    PRE_CONTRACT,
    ROUTE_PRECEDENCE,
    SOFTWARE_VERSION,
    SOURCE_RECORD_ID,
    TERMS_REVIEW_ID,
    PetesLakeOpticalRun,
    validate_u03_prerequisite,
)


REPORT_ID = "PETES-LAKE-SOURCE-FITNESS-2026-001"
REPORT_VERSION = "petes-lake-source-fitness-v0.1.0"
PROTOCOL_VERSION = "petes-lake-native-source-fitness-v0.1.0"
PLAN_REPORT_ID = "ADDITIONAL-EVENT-GROUP-PLAN-2026-001"
TASK_ISSUE = 521
UNIT_ID = "P2O4-T33-U03"
ACQUISITION_GENERATED_AT_UTC = "2026-07-21T18:40:41Z"
CUSTODY_REPORT_SHA256 = (
    "46f72f7fa7dc3b6fc3f96f6023b0d7b14f6990bcef8945a878ae04600d2e571d"
)
CUSTODY_SEMANTIC_SHA256 = (
    "a9218a830d729af8712b525acf5365f6ed1d355407947606f1491c538f30f748"
)
CUSTODY_DECISION = "PASS_PETES_LAKE_OPTICAL_CUSTODY_AUTHORIZE_U03_ONLY"
VISUAL_PENDING = "PENDING_ACTUAL_PETES_LAKE_RENDER_REVIEW"
VISUAL_PASS = "PASS_ACTUAL_PETES_LAKE_RENDER_REVIEW"
VISUAL_FAIL = "FAIL_ACTUAL_PETES_LAKE_RENDER_REVIEW"
OFFICIAL_S2L2A_DOCUMENTATION = (
    "https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S2L2A.html"
)


class PetesLakeSourceFitnessError(RuntimeError):
    """A deterministic, secret-free Petes Lake source-fitness failure."""


def _load_json_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PetesLakeSourceFitnessError(f"{label} is unreadable") from error
    if not isinstance(payload, dict):
        raise PetesLakeSourceFitnessError(f"{label} is not an object")
    return payload


def _load_candidate(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    report = _load_json_object(path, label="additional-event plan")
    if report.get("report_id") != PLAN_REPORT_ID:
        raise PetesLakeSourceFitnessError("additional-event plan identity mismatch")
    selected = report.get("selected_event_group_ids")
    if not isinstance(selected, list) or len(selected) != 3 or selected[2] != EVENT_GROUP_ID:
        raise PetesLakeSourceFitnessError("Petes Lake is not third in the frozen acquisition order")
    matches = [
        item
        for item in report.get("candidate_assessments", [])
        if isinstance(item, dict) and item.get("event_group_id") == EVENT_GROUP_ID
    ]
    if len(matches) != 1 or matches[0].get("disposition") != "FROZEN_FOR_BOUNDED_ACQUISITION":
        raise PetesLakeSourceFitnessError("frozen Petes Lake candidate mismatch")
    candidate = matches[0]
    if candidate.get("fire_id") != "OR4396912190120230825":
        raise PetesLakeSourceFitnessError("Petes Lake fire identity mismatch")
    if candidate.get("programs") != ["MTBS"]:
        raise PetesLakeSourceFitnessError("Petes Lake reference-program identity mismatch")
    return report, candidate


def _load_custody_report(path: Path) -> dict[str, Any]:
    try:
        data = path.read_bytes()
    except OSError as error:
        raise PetesLakeSourceFitnessError("Petes Lake custody report is unreadable") from error
    if sha256(data).hexdigest() != CUSTODY_REPORT_SHA256:
        raise PetesLakeSourceFitnessError("Petes Lake custody report hash mismatch")
    try:
        report = json.loads(data.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise PetesLakeSourceFitnessError("Petes Lake custody report is invalid") from error
    if not isinstance(report, dict):
        raise PetesLakeSourceFitnessError("Petes Lake custody report is not an object")
    core = report.get("semantic_record")
    if (
        report.get("report_id") != "PETES-LAKE-OPTICAL-CUSTODY-2026-001"
        or report.get("semantic_sha256") != CUSTODY_SEMANTIC_SHA256
        or not isinstance(core, dict)
        or core.get("decision") != CUSTODY_DECISION
        or core.get("disposition") != "pass"
        or core.get("next_dependency") != UNIT_ID
    ):
        raise PetesLakeSourceFitnessError("Petes Lake custody report semantic gate failed")
    return report


def summarize_probability(values: np.ndarray, mask: np.ndarray) -> dict[str, Any]:
    """Summarize an exact native 20 m Sen2Cor probability layer without thresholding."""

    if values.ndim != 2 or mask.shape != values.shape or not np.any(mask):
        raise PetesLakeSourceFitnessError("quality-probability array or boundary mask is invalid")
    observed = values[mask]
    if observed.dtype != np.uint8 or int(observed.min()) < 0 or int(observed.max()) > 100:
        raise PetesLakeSourceFitnessError("quality probability is outside the official 0-100 range")
    percentiles = np.percentile(observed.astype(np.float64), [0, 50, 90, 95, 99, 100])
    return {
        "pixel_count": int(observed.size),
        "range_contract_percent": [0, 100],
        "minimum_percent": int(observed.min()),
        "maximum_percent": int(observed.max()),
        "mean_percent": round(float(observed.mean()), 6),
        "nonzero_pixels": int(np.count_nonzero(observed)),
        "nonzero_percent": round(100 * float(np.mean(observed > 0)), 4),
        "percentiles": {
            name: round(float(value), 6)
            for name, value in zip(("p00", "p50", "p90", "p95", "p99", "p100"), percentiles)
        },
        "threshold_applied": False,
        "interpretation": (
            "Native Sen2Cor probability context only; SCL, rendered pixels, and the full "
            "uncertainty contract govern use. This summary assigns no class or label."
        ),
    }


def _validate_visual(decision: str, notes: str) -> None:
    if decision not in {VISUAL_PENDING, VISUAL_PASS, VISUAL_FAIL}:
        raise PetesLakeSourceFitnessError("visual review decision is not authorized")
    if decision == VISUAL_PENDING and notes:
        raise PetesLakeSourceFitnessError("pending visual review cannot contain review notes")
    if decision != VISUAL_PENDING and len(notes.strip()) < 40:
        raise PetesLakeSourceFitnessError("completed visual review requires specific notes")


def _single_link_asset(path: Path) -> None:
    try:
        observed = path.lstat()
    except OSError as error:
        raise PetesLakeSourceFitnessError("registered optical archive is missing") from error
    if not stat.S_ISREG(observed.st_mode) or path.is_symlink() or observed.st_nlink != 1:
        raise PetesLakeSourceFitnessError("registered optical archive is not a single-link file")


def _machine_source_decision(registration: dict[str, Any]) -> str:
    """Apply the established event-fitness invariant without hiding exclusions."""

    states = registration.get("state_counts")
    if not isinstance(states, dict) or any(
        not isinstance(states.get(name), int)
        for name in ("pass", "review-needed", "excluded", "fail-registration")
    ):
        raise PetesLakeSourceFitnessError("registration state counts are invalid")
    if states["fail-registration"] or states["pass"] == 0:
        return "REJECT_EXACT_PETES_LAKE_OPTICAL_SOURCE_FITNESS"
    if states["review-needed"] or states["excluded"]:
        return "ACCEPT_EXACT_PETES_LAKE_OPTICAL_SOURCE_FITNESS_WITH_SPATIAL_EXCLUSIONS"
    return "PASS_EXACT_PETES_LAKE_OPTICAL_SOURCE_FITNESS_GATE"


def _temporal_fitness(
    candidate: dict[str, Any],
    pre_scene: dict[str, Any],
    post_scene: dict[str, Any],
) -> dict[str, Any]:
    try:
        ignition = date.fromisoformat(candidate["ignition_date"])
        pre = datetime.fromisoformat(
            pre_scene["product_metadata"]["sensing_time_utc"].replace("Z", "+00:00")
        ).date()
        post = datetime.fromisoformat(
            post_scene["product_metadata"]["sensing_time_utc"].replace("Z", "+00:00")
        ).date()
    except (KeyError, TypeError, ValueError) as error:
        raise PetesLakeSourceFitnessError("Petes Lake temporal identity is invalid") from error
    if not pre < ignition < post:
        raise PetesLakeSourceFitnessError("Petes Lake pre/ignition/post order failed")
    return {
        "ignition_date": ignition.isoformat(),
        "pre_sensing_date": pre.isoformat(),
        "post_sensing_date": post.isoformat(),
        "pre_days_before_ignition": (ignition - pre).days,
        "post_days_after_ignition": (post - ignition).days,
        "chronological_order": "PASS_PRE_BEFORE_IGNITION_BEFORE_POST",
        "fitness_boundary": (
            "Chronology passes, but timing alone cannot overcome local snow, SCL, "
            "registration, render, or official-reference gates."
        ),
    }


def build_report(
    *,
    repository_root: Path,
    plan_path: Path,
    custody_report_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    visual_review_decision: str,
    visual_review_notes: str,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    _validate_visual(visual_review_decision, visual_review_notes)
    run = PetesLakeOpticalRun.create(
        repository_root=repository_root,
        generated_at_utc=ACQUISITION_GENERATED_AT_UTC,
        revision=INITIAL_REVISION,
        mode="full",
    )
    prerequisite_reasons = validate_u03_prerequisite(run)
    if prerequisite_reasons:
        raise PetesLakeSourceFitnessError(
            "Petes Lake U03 prerequisite failed: " + ",".join(prerequisite_reasons)
        )
    custody = _load_custody_report(custody_report_path)
    plan, candidate = _load_candidate(plan_path)
    geometry = candidate.get("boundary_geometry")
    if not isinstance(geometry, dict) or geometry.get("type") not in {"Polygon", "MultiPolygon"}:
        raise PetesLakeSourceFitnessError("Petes Lake boundary geometry is invalid")

    _single_link_asset(run.pre_destination / PRE_CONTRACT.expected_filename)
    _single_link_asset(run.post_destination / POST_CONTRACT.expected_filename)
    pre_scene, pre = _read_product(
        run.pre_destination,
        PRE_CONTRACT,
        geometry,
        expected_processing_baseline="05.10",
        include_quality_probabilities=True,
    )
    post_scene, post = _read_product(
        run.post_destination,
        POST_CONTRACT,
        geometry,
        expected_processing_baseline="05.10",
        include_quality_probabilities=True,
    )
    for scene, arrays in ((pre_scene, pre), (post_scene, post)):
        scene["quality_probabilities_inside_full_boundary"] = {
            "cloud": summarize_probability(arrays["CLD"], arrays["MASK20"]),
            "snow": summarize_probability(arrays["SNW"], arrays["MASK20"]),
        }
    windows, quality = measure_event_registration(pre_scene, pre, post_scene, post)
    registration = registration_summary(windows)
    machine_source = _machine_source_decision(registration)
    spectral, dnbr, spectral_valid = summarize_spectral_change(
        pre_scene, pre, post_scene, post
    )
    transactions = custody["semantic_record"]["transactions"]
    if [item.get("role") for item in transactions] != [PRE_CONTRACT.role, POST_CONTRACT.role]:
        raise PetesLakeSourceFitnessError("Petes Lake custody transaction order changed")
    machine_reject = machine_source.startswith("REJECT_")
    visual_complete = visual_review_decision != VISUAL_PENDING
    visual_failed = visual_review_decision == VISUAL_FAIL
    optical_pass = visual_review_decision == VISUAL_PASS and not machine_reject
    blocking_factors: list[str] = []
    if registration["state_counts"]["pass"] == 0:
        blocking_factors.append("ZERO_REGISTRATION_WINDOWS_PASS_AFTER_PAIR_QUALITY_EXCLUSIONS")
    post_snow_pixels = next(
        item["pixels"]
        for item in post_scene["scl_summary_inside_full_boundary"]["classes"]
        if item["value"] == 11
    )
    if post_snow_pixels:
        blocking_factors.append("POST_SCL_SNOW_OR_ICE_INSIDE_FULL_BOUNDARY")
    if visual_failed:
        blocking_factors.append("ACTUAL_RENDER_REVIEW_FAILED")

    if not visual_complete:
        optical_source = "PENDING_ACTUAL_PETES_LAKE_RENDER_REVIEW"
        event_status = (
            "PENDING_RENDER_REVIEW_MACHINE_REMEDIATION_INDICATED"
            if machine_reject
            else "PENDING_RENDER_REVIEW_NO_DOWNSTREAM_USE"
        )
    elif machine_reject:
        optical_source = "FAIL_EXACT_PETES_LAKE_OPTICAL_SOURCE_FITNESS_REMEDIATE_POST_SCENE"
        event_status = "REMEDIATE_POST_SCENE_LOCAL_QUALITY_BLOCKS_DEPENDENCIES"
    elif visual_failed:
        optical_source = "FAIL_ACTUAL_PETES_LAKE_RENDER_REVIEW_REMEDIATE"
        event_status = "REMEDIATE_RENDER_REVIEW_NO_DOWNSTREAM_USE"
    elif machine_source.endswith("WITH_SPATIAL_EXCLUSIONS"):
        optical_source = (
            "PASS_EXACT_PETES_LAKE_OPTICAL_SOURCE_FITNESS_WITH_SPATIAL_EXCLUSIONS"
        )
        event_status = (
            "ACCEPT_OPTICAL_SOURCE_WITH_EXCLUSIONS_DEFER_REFERENCE_AND_CANDIDATES"
        )
    else:
        optical_source = "PASS_EXACT_PETES_LAKE_OPTICAL_SOURCE_FITNESS"
        event_status = "ACCEPT_OPTICAL_SOURCE_DEFER_REFERENCE_AND_CANDIDATES"
    report = {
        "report_id": REPORT_ID,
        "report_version": REPORT_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "unit_id": UNIT_ID,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": None,
        "target_version": TARGET_VERSION,
        "label_protocol_version": LABEL_PROTOCOL_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "label_set_version": "owner-approved-prototype-region-labels-v0.3.0",
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
        "custody": {
            "contract_version": CONTRACT_VERSION,
            "source_record_id": SOURCE_RECORD_ID,
            "terms_review_id": TERMS_REVIEW_ID,
            "aggregate_run_id": custody["semantic_record"]["run_id"],
            "report_sha256": CUSTODY_REPORT_SHA256,
            "semantic_sha256": CUSTODY_SEMANTIC_SHA256,
            "acquisition_trace_commit": custody["semantic_record"]["trace"][
                "git_source_commit"
            ],
            "transactions": [
                {
                    "role": item["role"],
                    "run_id": item["run_id"],
                    "package_id": item["package_id"],
                    "registration_manifest_sha256": item["verification"][
                        "registration_manifest_sha256"
                    ],
                    "asset": item["registration"]["assets"][0],
                    "fresh_u03_prerequisite_verification": "pass",
                }
                for item in transactions
            ],
        },
        "input_hashes": {
            "additional_event_plan_sha256": _sha256_lf_text(plan_path),
            "additional_event_source_snapshot_sha256": plan["source_snapshot"]["sha256"],
            "custody_report_sha256": CUSTODY_REPORT_SHA256,
            "custody_semantic_sha256": CUSTODY_SEMANTIC_SHA256,
        },
        "source_precedence": ROUTE_PRECEDENCE,
        "official_probability_semantics": {
            "source": OFFICIAL_S2L2A_DOCUMENTATION,
            "checked_at_utc": generated_at_utc,
            "snow": "Sen2Cor snow probability; native 20 m UINT8 percent in the 0-100 range.",
            "cloud": "Sen2Cor cloud probability; native 20 m UINT8 percent in the 0-100 range.",
            "role": "quality and uncertainty evidence only; never label truth",
        },
        "method": {
            "boundary": (
                "Full frozen MTBS boundary; crop covers it outward and counts pixel centers "
                "inside it without shrinking the geometry."
            ),
            "native_pixels": (
                "TCI 10 m is preview only. B04, B8A, B12, SCL, CLD, and SNW remain "
                "on exact native EPSG:32610 grids with no reprojection, resampling, or upsampling."
            ),
            "quality": (
                "SCL governs categorical pair quality. Native CLD/SNW values are summarized "
                "without a classification threshold and assign no label."
            ),
            "registration": (
                "Independent B04/B8A/B12 reflectance gradients in deterministic event-scaled "
                "windows; the established untuned content-registration gate is reused."
            ),
            "visual": (
                "The exact rendered pre, post, and continuous dNBR panels must be inspected for "
                "cloud, smoke or haze, shadow, snow, clipping, and misleading display artifacts."
            ),
        },
        "products": [pre_scene, post_scene],
        "temporal_fitness": _temporal_fitness(candidate, pre_scene, post_scene),
        "pair_quality_inside_full_boundary": quality["inside_boundary"],
        "registration": {"summary": registration, "windows": windows},
        "spectral_change": spectral,
        "visual_review": {
            "decision": visual_review_decision,
            "notes": visual_review_notes,
            "reviewer_role": "AI-assisted author self-audit; not independent review",
        },
        "fitness_decision": {
            "machine_source_gate": machine_source,
            "optical_source": optical_source,
            "blocking_factors": blocking_factors,
            "burned_candidate_route": "BLOCKED_PENDING_U04_U05_OFFICIAL_REFERENCE_EVIDENCE",
            "background_candidate_route": "BLOCKED_PENDING_U06_U07_AFFIRMATIVE_BACKGROUND_EVIDENCE",
            "unknown_route": "REQUIRED_FROM_QUALITY_REFERENCE_WETLAND_AND_SOURCE_UNCERTAINTY",
            "event_status": event_status,
            "u04_authorized": optical_pass,
            "next_dependency": "P2O4-T33-U04" if optical_pass else "P2O4-T33-U03",
        },
        "claims": {
            "proven": [
                "Both exact registered provider archives remain byte-identical to U02 custody.",
                "The full Petes Lake MTBS boundary is readable on aligned native 20 m B04/B8A/B12/SCL/CLD/SNW grids.",
                "Actual pair quality, continuous spectral change, and deterministic registration windows are measured without assigning labels.",
            ],
            "not_proven": [
                "No MTBS reference pixel has been delivered, opened, or accepted in this run.",
                "No SCL class, probability value, dNBR value, boundary inclusion, or apparent change is label truth.",
                "No Petes Lake candidate, owner decision, label, dataset, split, baseline, model, accuracy, field validation, official status, endorsement, or operational readiness exists.",
            ],
        },
        "attribution": "Contains modified Copernicus Sentinel data 2023, accessed through CDSE.",
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


def _render_png_bytes(report: dict[str, Any], previews: dict[str, np.ndarray]) -> bytes:
    canvas = Image.new("RGB", (1800, 1240), "#07110f")
    draw = ImageDraw.Draw(canvas)
    draw.text((65, 38), "BURNLENS  /  PETES LAKE SOURCE FITNESS", fill="#b9d8cf", font=_font(22))
    draw.text((65, 76), report["fitness_decision"]["event_status"], fill="#ffca73", font=_font(29))
    draw.text(
        (65, 120),
        "Exact provider bytes / full MTBS boundary / native SCL + cloud + snow / no labels",
        fill="#eef7f3",
        font=_font(19),
    )
    panels = (
        ("PRE 2023-07-21", "pre_tci", "pre_mask"),
        ("POST 2023-10-29", "post_tci", "post_mask"),
    )
    for index, (label, image_key, mask_key) in enumerate(panels):
        x = 65 + index * 570
        draw.rounded_rectangle((x, 175, x + 535, 575), radius=18, fill="#0e1d1a", outline="#315b50", width=2)
        canvas.paste(_preview_tci(previews[image_key], previews[mask_key], (495, 320)), (x + 20, 220))
        draw.text((x + 20, 190), label, fill="#eef7f3", font=_font(19))
        draw.text((x + 20, 546), "Dimmed outside full MTBS boundary", fill="#b9d8cf", font=_font(14))
    x = 1205
    draw.rounded_rectangle((x, 175, x + 530, 575), radius=18, fill="#0e1d1a", outline="#315b50", width=2)
    canvas.paste(_preview_dnbr(previews["dnbr"], previews["dnbr_valid"], (490, 320)), (x + 20, 220))
    draw.text((x + 20, 190), "CONTINUOUS dNBR", fill="#eef7f3", font=_font(19))
    draw.text((x + 20, 546), "Blue low / red high / never a label map", fill="#b9d8cf", font=_font(14))

    quality = report["pair_quality_inside_full_boundary"]
    eligible = next(item["percent"] for item in quality["states"] if item["state"] == "eligible-comparison")
    registration = report["registration"]["summary"]
    post = report["products"][1]
    post_snow = post["quality_probabilities_inside_full_boundary"]["snow"]
    post_cloud = post["quality_probabilities_inside_full_boundary"]["cloud"]
    metrics = [
        (f"{quality['pixel_count_inside_full_boundary']:,}", "native 20 m boundary pixels"),
        (f"{eligible:.4f}%", "pair-eligible SCL quality"),
        (f"{post_snow['percentiles']['p95']:.1f}%", "post snow probability p95"),
        (f"{post_cloud['percentiles']['p95']:.1f}%", "post cloud probability p95"),
        (f"{registration['state_counts']['pass']} / {registration['window_count']}", "registration windows pass"),
    ]
    for index, (value, label) in enumerate(metrics):
        x = 65 + index * 336
        draw.rounded_rectangle((x, 620, x + 305, 755), radius=16, fill="#0e1d1a", outline="#315b50", width=2)
        draw.text((x + 18, 640), value, fill="#78e0bd", font=_font(25))
        draw.text((x + 18, 695), label, fill="#b9d8cf", font=_font(13))

    decision = report["fitness_decision"]
    draw.rounded_rectangle((65, 800, 1735, 1025), radius=18, fill="#14201d", outline="#315b50", width=2)
    draw.text((90, 822), "FITNESS BOUNDARY", fill="#eef7f3", font=_font(20))
    decision_color = "#78e0bd" if decision["u04_authorized"] else "#ff8d7a"
    draw.text(
        (90, 862),
        f"Optical: {decision['optical_source']}",
        fill=decision_color,
        font=_font(16),
    )
    draw.text((90, 898), f"Burned route: {decision['burned_candidate_route']}", fill="#ffca73", font=_font(15))
    draw.text((90, 932), f"Background route: {decision['background_candidate_route']}", fill="#ffca73", font=_font(15))
    draw.text((90, 966), f"Visual: {report['visual_review']['decision']}", fill="#eef7f3", font=_font(15))
    draw.text((90, 995), "Probability values remain uncertainty evidence; no threshold or label is applied.", fill="#b9d8cf", font=_font(14))
    draw.rounded_rectangle((65, 1055, 1735, 1150), radius=16, fill="#261f12", outline="#be8a36", width=2)
    draw.text((85, 1075), WARNING, fill="#ffd997", font=_font(15))
    draw.text((85, 1110), report["attribution"], fill="#ffd997", font=_font(14))
    draw.text(
        (65, 1178),
        f"TRACE  commit {report['git_source_commit'][:12]} / run {report['run_id']} / custody {report['custody']['aggregate_run_id']} / dataset-model none",
        fill="#b9d8cf",
        font=_font(13),
    )
    buffer = BytesIO()
    canvas.save(buffer, format="PNG", optimize=False)
    return buffer.getvalue()


def _render_html(report: dict[str, Any], png_name: str) -> str:
    product_rows = []
    for product in report["products"]:
        scl = product["scl_summary_inside_full_boundary"]
        probability = product["quality_probabilities_inside_full_boundary"]
        product_rows.append(
            "<tr>"
            f"<td><code>{escape(product['role'])}</code></td>"
            f"<td>{escape(product['product_metadata']['sensing_time_utc'])}</td>"
            f"<td>{scl['eligible_land_percent']:.4f}%</td>"
            f"<td>{scl['review_needed_percent']:.4f}%</td>"
            f"<td>{scl['excluded_percent']:.4f}%</td>"
            f"<td>{probability['snow']['percentiles']['p95']:.1f}% / {probability['snow']['maximum_percent']}%</td>"
            f"<td>{probability['cloud']['percentiles']['p95']:.1f}% / {probability['cloud']['maximum_percent']}%</td>"
            "</tr>"
        )
    quality = report["pair_quality_inside_full_boundary"]
    eligible = next(item["percent"] for item in quality["states"] if item["state"] == "eligible-comparison")
    registration = report["registration"]["summary"]
    spectral = report["spectral_change"]
    decision = report["fitness_decision"]
    blocking = "".join(
        f"<li>{escape(item)}</li>" for item in decision["blocking_factors"]
    ) or "<li>none</li>"
    residual = (
        "n/a" if registration["p95_px"] is None else f"{registration['p95_px']:.4f} px"
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Petes Lake source fitness</title><style>
body{{margin:0;background:#07110f;color:#eef7f3;font:16px/1.55 system-ui,sans-serif}}main{{max-width:1200px;margin:auto;padding:32px}}h1{{font-size:clamp(2rem,5vw,4.2rem);line-height:1.02}}h2{{margin-top:2rem}}.card{{background:#0e1d1a;border:1px solid #315b50;border-radius:16px;padding:20px;margin:18px 0}}.warn{{background:#261f12;border-color:#be8a36;color:#ffd997}}img{{width:100%;height:auto;border-radius:16px}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #315b50}}code{{overflow-wrap:anywhere}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px}}.metric strong{{display:block;font-size:2rem;color:#78e0bd}}
</style></head><body><main>
<p>BURNLENS / PHASE TWO / ISSUE #521 / U03</p>
<h1>Petes Lake optical pixels are measured; labels are not.</h1>
<div class="card warn">{escape(report['warning'])}</div>
<img src="{escape(png_name)}" width="1800" height="1240" alt="Actual Petes Lake pre and post Sentinel imagery, continuous dNBR, native quality probabilities, and registration evidence">
<div class="grid"><div class="card metric"><strong>{quality['pixel_count_inside_full_boundary']:,}</strong>native 20 m boundary pixels</div><div class="card metric"><strong>{eligible:.4f}%</strong>pair eligible</div><div class="card metric"><strong>{registration['state_counts']['pass']} / {registration['window_count']}</strong>registration windows pass</div><div class="card metric"><strong>{residual}</strong>p95 residual</div></div>
<h2>Exact optical products and local quality</h2><div class="card"><table><thead><tr><th>Role</th><th>Sensing</th><th>SCL eligible</th><th>SCL review</th><th>SCL excluded</th><th>Snow p95 / max</th><th>Cloud p95 / max</th></tr></thead><tbody>{''.join(product_rows)}</tbody></table><p>CLD and SNW are native 20 m Sen2Cor probability percentages. They are summarized without a classification threshold and assign no label.</p></div>
<h2>Continuous change</h2><div class="card"><p>{spectral['valid_pair_pixels']:,} valid pair pixels; median dNBR {spectral['dnbr_percentiles']['p50']:.6f}; p10/p90 {spectral['dnbr_percentiles']['p10']:.6f} / {spectral['dnbr_percentiles']['p90']:.6f}; {spectral['positive_change_percent']:.4f}% positive change.</p><p>{escape(spectral['interpretation'])}</p></div>
<h2>Actual render review</h2><div class="card"><p><strong>{escape(report['visual_review']['decision'])}</strong></p><p>{escape(report['visual_review']['notes'] or 'Pending: this preview cannot authorize downstream use.')}</p><p>This is an AI-assisted author self-audit, not independent review or field validation.</p></div>
<h2>Gate result</h2><div class="card"><p><strong>{escape(decision['event_status'])}</strong></p><ul><li>Machine source gate: {escape(decision['machine_source_gate'])}</li><li>Optical: {escape(decision['optical_source'])}</li><li>Burned route: {escape(decision['burned_candidate_route'])}</li><li>Background route: {escape(decision['background_candidate_route'])}</li><li>Unknown route: {escape(decision['unknown_route'])}</li></ul><p>Blocking factors:</p><ul>{blocking}</ul></div>
<div class="card warn"><p>{escape(report['attribution'])}</p><p>No reference pixel, candidate, owner decision, label, dataset, split, baseline, model, metric, field-validation, official, endorsed, operational, or emergency-ready claim exists.</p></div>
<p>Trace: commit <code>{escape(report['git_source_commit'])}</code> · BurnLens <code>{escape(report['software_version'])}</code> · evidence run <code>{escape(report['run_id'])}</code> · custody <code>{escape(report['custody']['aggregate_run_id'])}</code> · dataset/model none.</p>
</main></body></html>"""


def _write_bytes_no_overwrite(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise PetesLakeSourceFitnessError(f"output already exists: {path.name}")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
    except FileExistsError:
        raise PetesLakeSourceFitnessError(f"output already exists: {path.name}") from None
    opened: os.stat_result | None = None
    try:
        opened = os.fstat(descriptor)
        with os.fdopen(descriptor, "wb") as handle:
            if handle.write(data) != len(data):
                raise PetesLakeSourceFitnessError("output short write")
            handle.flush()
            os.fsync(handle.fileno())
        observed = path.lstat()
        if not stat.S_ISREG(observed.st_mode) or path.is_symlink() or observed.st_nlink != 1:
            raise PetesLakeSourceFitnessError("output is not a single-link regular file")
        if not os.path.samestat(opened, observed) or path.read_bytes() != data:
            raise PetesLakeSourceFitnessError("output identity or readback mismatch")
    except BaseException:
        try:
            current = path.lstat()
            if opened is not None and os.path.samestat(opened, current):
                path.unlink()
        except OSError:
            pass
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise


def write_outputs(
    report: dict[str, Any], previews: dict[str, np.ndarray], directory: Path
) -> dict[str, dict[str, Any]]:
    json_path = directory / f"{REPORT_ID}.json"
    png_path = directory / f"{REPORT_ID}.png"
    paths = {"json": json_path, "png": png_path}
    present = [path.name for path in paths.values() if path.exists() or path.is_symlink()]
    if present:
        raise PetesLakeSourceFitnessError("output already exists: " + ",".join(present))
    payloads = {
        "json": (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
        "png": _render_png_bytes(report, previews),
    }
    for name in ("json", "png"):
        _write_bytes_no_overwrite(paths[name], payloads[name])
    return {
        name: {
            "path": path.as_posix(),
            "bytes": len(payloads[name]),
            "sha256": sha256(payloads[name]).hexdigest(),
        }
        for name, path in paths.items()
    }
