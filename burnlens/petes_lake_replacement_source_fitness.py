"""Inspect the exact Petes Lake replacement pair without rewriting failed U03 evidence."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

import numpy as np

from .content_registration import _summary as registration_summary
from .cross_event_feasibility import LABEL_SCHEMA_VERSION
from .cross_event_source_fitness import _canonical_sha256, _read_product, measure_event_registration
from .green_ridge_source_fitness import summarize_spectral_change
from .optical_pair_evidence import LABEL_PROTOCOL_VERSION, TARGET_VERSION, WARNING, _sha256_lf_text
from .petes_lake_optical_contract import PRE_CONTRACT, ROUTE_PRECEDENCE, SOFTWARE_VERSION
from .petes_lake_replacement_optical_contract import (
    ATTRIBUTION,
    CONTRACT_VERSION as REPLACEMENT_CUSTODY_CONTRACT_VERSION,
    EVENT_GROUP_ID,
    REPLACEMENT_POST_CONTRACT,
    SOURCE_RECORD_ID,
    TERMS_REVIEW_ID,
    ReplacementOpticalRun,
    _fresh_verify_replacement,
    _transaction_matches_verification,
    _validate_original_pre,
)
from .petes_lake_source_fitness import (
    OFFICIAL_S2L2A_DOCUMENTATION,
    TASK_ISSUE,
    VISUAL_FAIL,
    VISUAL_PASS,
    VISUAL_PENDING,
    PetesLakeSourceFitnessError,
    _load_candidate,
    _machine_source_decision,
    _render_png_bytes,
    _single_link_asset,
    _temporal_fitness,
    _validate_visual,
    _write_bytes_no_overwrite,
    summarize_probability,
)


REPORT_ID = "PETES-LAKE-REPLACEMENT-SOURCE-FITNESS-2026-001"
REPORT_VERSION = "petes-lake-replacement-source-fitness-v0.1.0"
PROTOCOL_VERSION = "petes-lake-native-source-fitness-v0.2.0"
UNIT_ID = "P2O4-T33-U03_REPLACEMENT_SOURCE_FITNESS_R002"
RUN_ID = "BL-2026-07-21-petes-lake-replacement-source-fitness-r002"
PREVIEW_RUN_ID = "BL-2026-07-21-petes-lake-replacement-source-fitness-preview-r002"
CUSTODY_REPORT_ID = "PETES-LAKE-OPTICAL-REMEDIATION-CUSTODY-2026-001"
CUSTODY_REPORT_BYTES = 22_246
CUSTODY_REPORT_SHA256 = "e23d601959d09fb54fc6409f5a073df4f1a3a3a8a0d040e04a9b46c2594537b1"
CUSTODY_SEMANTIC_SHA256 = "78c888b4a3b954c4038a3454773b1cd7c922bc5f71957524e803ee6534d71f75"
CUSTODY_DECISION = (
    "PASS_PETES_LAKE_REPLACEMENT_OPTICAL_CUSTODY_"
    "AUTHORIZE_U03_SOURCE_FITNESS_R002_ONLY"
)
FAILED_REPORT_ID = "PETES-LAKE-SOURCE-FITNESS-2026-001"
FAILED_REPORT_BYTES = 56_285
FAILED_REPORT_SHA256 = "ac9befd021d71ff779ec56ddefc894f4e39b92e64e65c2c4afb815663d1ad443"
SELECTION_REPORT_ID = "PETES-LAKE-SOURCE-REMEDIATION-2026-001"
SELECTION_REPORT_BYTES = 10_127
SELECTION_REPORT_SHA256 = "7fa82a61fa70d47364db29493700beedd60c9114a4b3a6d8ddbafdf77aecfc8c"


def _load_exact_json(
    path: Path,
    *,
    label: str,
    expected_bytes: int,
    expected_sha256: str,
) -> dict[str, Any]:
    try:
        data = path.read_bytes()
    except OSError as error:
        raise PetesLakeSourceFitnessError(f"{label} is unreadable") from error
    if len(data) != expected_bytes or sha256(data).hexdigest() != expected_sha256:
        raise PetesLakeSourceFitnessError(f"{label} byte identity mismatch")
    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise PetesLakeSourceFitnessError(f"{label} is invalid") from error
    if not isinstance(payload, dict):
        raise PetesLakeSourceFitnessError(f"{label} is not an object")
    return payload


def _load_replacement_custody(path: Path) -> dict[str, Any]:
    report = _load_exact_json(
        path,
        label="Petes Lake replacement custody report",
        expected_bytes=CUSTODY_REPORT_BYTES,
        expected_sha256=CUSTODY_REPORT_SHA256,
    )
    core = report.get("semantic_record")
    if (
        report.get("report_id") != CUSTODY_REPORT_ID
        or report.get("semantic_sha256") != CUSTODY_SEMANTIC_SHA256
        or not isinstance(core, dict)
        or core.get("decision") != CUSTODY_DECISION
        or core.get("disposition") != "pass"
        or core.get("replacement_u03_source_fitness_authorized") is not True
        or core.get("u04_authorized") is not False
        or core.get("next_dependency") != UNIT_ID
    ):
        raise PetesLakeSourceFitnessError("Petes Lake replacement custody semantic gate failed")
    return report


def _validate_prior_evidence(
    failed_path: Path, selection_path: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    failed = _load_exact_json(
        failed_path,
        label="failed Petes Lake source-fitness report",
        expected_bytes=FAILED_REPORT_BYTES,
        expected_sha256=FAILED_REPORT_SHA256,
    )
    selection = _load_exact_json(
        selection_path,
        label="Petes Lake replacement selection report",
        expected_bytes=SELECTION_REPORT_BYTES,
        expected_sha256=SELECTION_REPORT_SHA256,
    )
    if (
        failed.get("report_id") != FAILED_REPORT_ID
        or failed.get("fitness_decision", {}).get("u04_authorized") is not False
        or failed.get("fitness_decision", {}).get("next_dependency") != "P2O4-T33-U03"
    ):
        raise PetesLakeSourceFitnessError("failed source-fitness evidence gate changed")
    if (
        selection.get("report_id") != SELECTION_REPORT_ID
        or selection.get("decision") != "SELECT_REPLACEMENT_POST_AUTHORIZE_CONTRACT_REVISION_ONLY"
        or selection.get("disposition") != "pass-for-contract-revision-only"
        or selection.get("next_dependency")
        != "P2O4-T33-U03_REPLACEMENT_CONTRACT_AND_PREFLIGHT"
    ):
        raise PetesLakeSourceFitnessError("replacement selection evidence gate changed")
    return failed, selection


def _replacement_machine_decision(registration: dict[str, Any]) -> str:
    return _machine_source_decision(registration).replace(
        "EXACT_PETES_LAKE_OPTICAL",
        "EXACT_PETES_LAKE_REPLACEMENT_OPTICAL",
    )


def build_report(
    *,
    repository_root: Path,
    plan_path: Path,
    custody_report_path: Path,
    failed_report_path: Path,
    selection_report_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    visual_review_decision: str,
    visual_review_notes: str,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    """Build r002 from fresh archive verification and the frozen r001 chain."""

    _validate_visual(visual_review_decision, visual_review_notes)
    run = ReplacementOpticalRun.create(
        repository_root=repository_root,
        generated_at_utc=generated_at_utc,
        revision="r002",
        mode="finalize",
    )
    custody = _load_replacement_custody(custody_report_path)
    failed, selection = _validate_prior_evidence(failed_report_path, selection_report_path)
    plan, candidate = _load_candidate(plan_path)
    geometry = candidate.get("boundary_geometry")
    if not isinstance(geometry, dict) or geometry.get("type") not in {"Polygon", "MultiPolygon"}:
        raise PetesLakeSourceFitnessError("Petes Lake boundary geometry is invalid")

    _single_link_asset(run.original_pre_destination / PRE_CONTRACT.expected_filename)
    _single_link_asset(run.replacement_destination / REPLACEMENT_POST_CONTRACT.expected_filename)
    core = custody["semantic_record"]
    pre_verification = _validate_original_pre(run)
    if pre_verification != core.get("original_pre_verification"):
        raise PetesLakeSourceFitnessError("fresh original-pre custody verification changed")
    replacement_verification = _fresh_verify_replacement(run)
    transaction = core.get("replacement_transaction")
    if not isinstance(transaction, dict) or not _transaction_matches_verification(
        transaction, replacement_verification
    ):
        raise PetesLakeSourceFitnessError("fresh replacement-post custody verification changed")

    pre_scene, pre = _read_product(
        run.original_pre_destination,
        PRE_CONTRACT,
        geometry,
        expected_processing_baseline="05.10",
        include_quality_probabilities=True,
    )
    post_scene, post = _read_product(
        run.replacement_destination,
        REPLACEMENT_POST_CONTRACT,
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
    machine_source = _replacement_machine_decision(registration)
    spectral, dnbr, spectral_valid = summarize_spectral_change(pre_scene, pre, post_scene, post)
    machine_reject = machine_source.startswith("REJECT_")
    visual_complete = visual_review_decision != VISUAL_PENDING
    visual_failed = visual_review_decision == VISUAL_FAIL
    optical_pass = visual_review_decision == VISUAL_PASS and not machine_reject
    post_snow_pixels = next(
        item["pixels"]
        for item in post_scene["scl_summary_inside_full_boundary"]["classes"]
        if item["value"] == 11
    )
    blocking_factors: list[str] = []
    if registration["state_counts"]["pass"] == 0:
        blocking_factors.append("ZERO_REGISTRATION_WINDOWS_PASS_AFTER_PAIR_QUALITY_EXCLUSIONS")
    if post_snow_pixels:
        blocking_factors.append("REPLACEMENT_POST_SCL_SNOW_OR_ICE_INSIDE_FULL_BOUNDARY")
    if visual_failed:
        blocking_factors.append("ACTUAL_REPLACEMENT_RENDER_REVIEW_FAILED")

    if not visual_complete:
        optical_source = "PENDING_ACTUAL_PETES_LAKE_REPLACEMENT_RENDER_REVIEW"
        event_status = (
            "PENDING_REPLACEMENT_RENDER_REVIEW_MACHINE_REMEDIATION_INDICATED"
            if machine_reject
            else "PENDING_REPLACEMENT_RENDER_REVIEW_NO_DOWNSTREAM_USE"
        )
    elif machine_reject:
        optical_source = "FAIL_EXACT_PETES_LAKE_REPLACEMENT_OPTICAL_SOURCE_FITNESS"
        event_status = "REPLACEMENT_PAIR_SOURCE_FITNESS_FAILED_NO_DOWNSTREAM_USE"
    elif visual_failed:
        optical_source = "FAIL_ACTUAL_PETES_LAKE_REPLACEMENT_RENDER_REVIEW"
        event_status = "REPLACEMENT_RENDER_REVIEW_FAILED_NO_DOWNSTREAM_USE"
    elif machine_source.endswith("WITH_SPATIAL_EXCLUSIONS"):
        optical_source = "PASS_EXACT_PETES_LAKE_REPLACEMENT_OPTICAL_SOURCE_FITNESS_WITH_SPATIAL_EXCLUSIONS"
        event_status = "ACCEPT_REPLACEMENT_OPTICAL_SOURCE_WITH_EXCLUSIONS_DEFER_REFERENCE_AND_CANDIDATES"
    else:
        optical_source = "PASS_EXACT_PETES_LAKE_REPLACEMENT_OPTICAL_SOURCE_FITNESS"
        event_status = "ACCEPT_REPLACEMENT_OPTICAL_SOURCE_DEFER_REFERENCE_AND_CANDIDATES"

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
            "contract_version": REPLACEMENT_CUSTODY_CONTRACT_VERSION,
            "source_record_id": SOURCE_RECORD_ID,
            "terms_review_id": TERMS_REVIEW_ID,
            "aggregate_run_id": core["run_id"],
            "report_id": CUSTODY_REPORT_ID,
            "report_bytes": CUSTODY_REPORT_BYTES,
            "report_sha256": CUSTODY_REPORT_SHA256,
            "semantic_sha256": CUSTODY_SEMANTIC_SHA256,
            "acquisition_trace_commit": core["trace"]["git_source_commit"],
            "original_pre_verification": pre_verification,
            "replacement_post_verification": replacement_verification,
        },
        "input_hashes": {
            "additional_event_plan_sha256": _sha256_lf_text(plan_path),
            "additional_event_source_snapshot_sha256": plan["source_snapshot"]["sha256"],
            "failed_source_fitness_report_sha256": FAILED_REPORT_SHA256,
            "replacement_selection_report_sha256": SELECTION_REPORT_SHA256,
            "replacement_custody_report_sha256": CUSTODY_REPORT_SHA256,
            "replacement_custody_semantic_sha256": CUSTODY_SEMANTIC_SHA256,
        },
        "prior_evidence": {
            "failed_report_id": failed["report_id"],
            "failed_run_id": failed["run_id"],
            "failed_decision": failed["fitness_decision"]["optical_source"],
            "selection_report_id": selection["report_id"],
            "selection_run_id": selection["run_id"],
            "selection_decision": selection["decision"],
            "disposition": "immutable historical evidence; not overwritten or hidden",
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
            "boundary": "Full frozen MTBS boundary; crop covers it outward and counts pixel centers inside it without shrinking the geometry.",
            "native_pixels": "TCI 10 m is preview only. B04, B8A, B12, SCL, CLD, and SNW remain on exact native EPSG:32610 grids with no reprojection, resampling, or upsampling.",
            "quality": "SCL governs categorical pair quality. Native CLD/SNW values are summarized without a classification threshold and assign no label.",
            "registration": "Independent B04/B8A/B12 reflectance gradients in deterministic event-scaled windows; the established untuned content-registration gate is reused.",
            "visual": "The exact rendered pre, replacement post, and continuous dNBR panels must be inspected for cloud, smoke or haze, shadow, snow, clipping, and misleading display artifacts.",
            "threshold_policy": "All source-fitness gates are inherited unchanged from r001; no threshold or gate is tuned to rescue the replacement scene.",
        },
        "products": [pre_scene, post_scene],
        "metadata_time_reconciliation": {
            "catalogue_product_acquisition_utc": core["metadata_snapshot"]["acquisition_utc"],
            "delivered_tile_sensing_time_utc": post_scene["product_metadata"]["sensing_time_utc"],
            "same_utc_date": (
                core["metadata_snapshot"]["acquisition_utc"][:10]
                == post_scene["product_metadata"]["sensing_time_utc"][:10]
            ),
            "interpretation": (
                "The catalogue product start and delivered tile sensing time are distinct "
                "metadata fields. Both are retained; neither is rewritten or treated as drift."
            ),
        },
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
            "next_dependency": "P2O4-T33-U04" if optical_pass else UNIT_ID,
        },
        "claims": {
            "proven": [
                "The original pre and exact replacement post provider archives remain byte-identical to their separately bound custody evidence.",
                "The full Petes Lake MTBS boundary is readable on aligned native 20 m B04/B8A/B12/SCL/CLD/SNW grids.",
                "Actual pair quality, continuous spectral change, and deterministic registration windows are measured without assigning labels.",
            ],
            "not_proven": [
                "No MTBS reference pixel has been delivered, opened, or accepted in this run.",
                "No SCL class, probability value, dNBR value, boundary inclusion, or apparent change is label truth.",
                "No Petes Lake candidate, owner decision, label, dataset, split, baseline, model, accuracy, field validation, official status, endorsement, or operational readiness exists.",
            ],
        },
        "attribution": ATTRIBUTION,
        "warning": WARNING,
    }
    previews = {
        "pre_tci": pre["TCI"],
        "post_tci": post["TCI"],
        "pre_mask": pre["MASK10"],
        "post_mask": post["MASK10"],
        "boundary_mask20": pre["MASK20"],
        "pre_scl20": pre["SCL"],
        "post_scl20": post["SCL"],
        "dnbr": dnbr,
        "dnbr_valid": spectral_valid,
    }
    return report, previews


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
