"""Fail-closed Windigo owner-response reconciliation."""

from __future__ import annotations

from collections import Counter, deque
from datetime import datetime
from hashlib import sha256
from html import escape
import json
import os
from pathlib import Path
import subprocess
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import rasterio

import burnlens
from .owner_review_batch import build_surface, validate_completed_response
from .owner_review_batch_lock import (
    LOCK_VERSION,
)
from .windigo_owner_review_surface import (
    EVENT_GROUP_ID as REVIEW_EVENT_GROUP_ID,
    EXPECTED_CANDIDATES,
    SURFACE_ID,
)
from .windigo_region_proposal import (
    EXPECTED_COUNTS,
    LABEL_SCHEMA_VERSION,
    LABEL_SET_VERSION as PRIOR_LABEL_SET_VERSION,
    REPORT_ID as PROPOSAL_ID,
    RUN_ID as PROPOSAL_RUN_ID,
    SOURCE_REPORT_SHA256,
    TARGET_VERSION,
    build_report as rebuild_proposal,
)


REPORT_ID = "WINDIGO-OWNER-RESPONSE-INTAKE-2026-001"
REPORT_VERSION = "windigo-owner-response-intake-v0.1.0"
PRIVATE_REPORT_VERSION = "windigo-owner-response-private-reconciliation-v0.1.0"
LABEL_SET_VERSION = "owner-approved-prototype-region-labels-v0.4.0"
AOI_VERSION = "multi-event-native-grids-v0.4.0"
TASK_ISSUE = 534
UNIT_ID = "P2O4-T35-U05"
MINIMUM_EVENT_GROUPS = 6
EXPECTED_EVENT_GROUP_ID = "event-windigo-2022"
EXPECTED_SURFACE_BYTES = 13_597
EXPECTED_SURFACE_SHA256 = "507a23044b2285462e5c5f7573111fbbb8a5fa52aae11a2956b99c9d8b936e12"
EXPECTED_PROPOSAL_BYTES = 29_995
EXPECTED_PROPOSAL_SHA256 = "612143b0d54f6203026f00cc7848ea4d073b219967c75014b5d119ed85ec7365"
EXPECTED_RESPONSE_BYTES = 1_061
EXPECTED_RESPONSE_SHA256 = "d1f77a9cf575f668ce1b8017a9b9607d72370022e8098b1b78f76dce95702104"
EXPECTED_RECEIPT_BYTES = 2_700
EXPECTED_RECEIPT_SHA256 = "2a5ab1e33ac431db86671356d067141e68186dc29daea3eb01fa76ad27cf5f2e"
PRIOR_INTAKE_BYTES = 9_112
PRIOR_INTAKE_SHA256 = "2897656ad13164295ad2fda78887d8a41b920dfe73e39c12396e55a034b081b5"
RECORD_BINDINGS = {
    "SOURCE-2026-036": (8_940, "d8ea91debe6f02f4ca672084ad35a02e80cda1c10469cc391d8174bb8b724128"),
    "SOURCE-2026-037": (5_666, "b19f9ca9cfcfda75216a094afc7f10056d39dfdfbddda66cd15e3ff092699b37"),
    "TERMS-2026-031": (5_902, "4ba57312c3be30c1c0b0c288b9d488cb3303159db275b2a477ecd5eb299d0f15"),
    "TERMS-2026-032": (2_361, "84c9ddafae1edbb2e5dcfa9b30e7d1d95e25341dcd6e3e2cb1e678894302a313"),
    "PRECHECK-2026-059": (7_031, "b3e2f66d0fdc15a022556387a604208591cc90bf494508dd8134c5ea8089f506"),
    "PRECHECK-2026-060": (5_676, "c70cbe543c1ed7e8c04c7ff80ec0ba141f98f9af97b208d339ef4d3d6d92ad32"),
    "PRECHECK-2026-061": (6_697, "31b513a5174ef716e6adf8f6b32ce59156992467cd3ed31e4f3934ff880891da"),
    "PRECHECK-2026-062": (6_088, "f628aa09f9831a58bf3e45c5bff5ac586cfa77bf313f7e7e388e885172f0ecea"),
    "PRECHECK-2026-063": (5_449, "71ac1e551a6a6327bcabe2ae24ff308b75cf6fe03a9357dd61db7074322ea45d"),
}
REQUIRED_RECORD_TEXT = {
    "SOURCE-2026-036": ("Windigo", "BAER", "MTBS", "RAVG"),
    "SOURCE-2026-037": ("preliminary", "RAVG", "affirmative background"),
    "TERMS-2026-031": ("Contains modified Copernicus Sentinel data",),
    "TERMS-2026-032": ("RESOLVED_FOR_ATTRIBUTED_BOUNDED_PROTOTYPE_EVIDENCE", "disclaim warranty"),
    "PRECHECK-2026-059": ("PASS_ONE_BOUNDED_WINDIGO_ATTEMPT",),
    "PRECHECK-2026-060": ("PASS_WINDIGO_OPTICAL_CUSTODY_AUTHORIZE_REFERENCE_REQUEST_PREFLIGHT",),
    "PRECHECK-2026-061": ("ACCEPT_SOURCE_FITNESS_DEFER_CANDIDATES",),
    "PRECHECK-2026-062": ("PROPOSE_EXACT_WINDIGO_TWO_CLASS_REGIONS",),
    "PRECHECK-2026-063": ("AWAITING_EXACT_OWNER_RESPONSE", "No response or U06 decision may be inferred"),
}
WARNING = (
    "Experimental owner-approved prototype regions, not ground truth, a dataset, "
    "official wildfire information, emergency guidance, or field validation. Official sources govern."
)
EVIDENCE_ORIGIN = "owner-returned-batch-response"


class WindigoOwnerResponseIntakeError(RuntimeError):
    """Raised when response custody or any promotion gate fails closed."""


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise WindigoOwnerResponseIntakeError(message)


def _sha256_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _binding(path: Path, **extra: Any) -> dict[str, Any]:
    value = {"bytes": path.stat().st_size, "sha256": _sha256_file(path)}
    value.update(extra)
    return value


def _json(data: bytes, name: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise WindigoOwnerResponseIntakeError(f"invalid UTF-8 JSON: {name}") from error
    _assert(isinstance(value, dict), f"JSON is not an object: {name}")
    return value


def _timestamp(value: Any, name: str) -> datetime:
    _assert(isinstance(value, str), f"{name} is not a timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise WindigoOwnerResponseIntakeError(f"{name} is invalid") from error
    _assert(parsed.tzinfo is not None, f"{name} lacks timezone")
    return parsed


def _assert_ignored(repository_root: Path, path: Path) -> None:
    try:
        relative = path.relative_to(repository_root)
    except ValueError as error:
        raise WindigoOwnerResponseIntakeError("private input or output is outside the repository") from error
    result = subprocess.run(
        ["git", "-C", str(repository_root), "check-ignore", "--quiet", "--no-index", "--", str(relative)],
        check=False,
    )
    _assert(result.returncode == 0, "private input or output is not ignored")


def _record_path(repository_root: Path, record_id: str) -> Path:
    if record_id.startswith("SOURCE-"):
        root = repository_root / "records/phase-two/sources"
    elif record_id.startswith("TERMS-"):
        root = repository_root / "records/phase-two/terms"
    else:
        root = repository_root / "records/phase-two/prechecks"
    matches = list(root.glob(f"{record_id}.*"))
    _assert(len(matches) == 1 and matches[0].is_file(), f"record missing or ambiguous: {record_id}")
    return matches[0]


def _record_bindings(repository_root: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for record_id, (expected_bytes, expected_sha256) in RECORD_BINDINGS.items():
        path = _record_path(repository_root, record_id)
        text = path.read_text(encoding="utf-8")
        for required in REQUIRED_RECORD_TEXT[record_id]:
            _assert(required in text, f"required gate text changed: {record_id}")
        binding = _binding(path)
        _assert(binding["bytes"] == expected_bytes, f"record size changed: {record_id}")
        _assert(binding["sha256"] == expected_sha256, f"record hash changed: {record_id}")
        result.append({"record_id": record_id, **binding})
    return result


def _validate_surface(path: Path) -> tuple[dict[str, Any], bytes]:
    data = path.read_bytes()
    _assert(len(data) == EXPECTED_SURFACE_BYTES, "surface size changed")
    _assert(_sha256_bytes(data) == EXPECTED_SURFACE_SHA256, "surface hash changed")
    surface = _json(data, path.name)
    try:
        rebuilt = build_surface(surface.get("batch_manifest"))
    except Exception as error:
        raise WindigoOwnerResponseIntakeError("surface reconstruction failed") from error
    rebuilt["software_version"] = surface.get("software_version")
    _assert(
        all(surface.get(key) == value for key, value in rebuilt.items()),
        "surface reconstruction changed",
    )
    _assert(surface.get("report_id") == SURFACE_ID, "surface identity changed")
    _assert(surface.get("task_issue") == TASK_ISSUE, "surface issue changed")
    _assert(surface.get("summary", {}).get("owner_responses") == 0, "surface already contains responses")
    _assert(surface.get("summary", {}).get("labels_created") == 0, "surface already contains labels")
    return surface, data


def _validate_receipt(
    receipt: dict[str, Any],
    *,
    response_bytes: bytes,
    surface_bytes: bytes,
) -> None:
    _assert(receipt.get("report_id") == f"{SURFACE_ID}-RECEIPT", "receipt identity changed")
    _assert(receipt.get("report_version") == LOCK_VERSION, "receipt version changed")
    _assert(receipt.get("task_issue") == TASK_ISSUE, "receipt issue changed")
    _assert(receipt.get("evidence_origin") == EVIDENCE_ORIGIN, "receipt origin changed")
    _assert(receipt.get("origin_declared_by_operator") is True, "receipt origin declaration changed")
    _assert(receipt.get("exact_response_preserved_without_overwrite") is True, "receipt lacks no-overwrite custody")
    _assert(receipt.get("decisions_revealed") is False, "receipt is not pre-reveal custody")
    _assert(receipt.get("qualifying_owner_response") is None, "receipt pre-qualifies the response")
    _assert(receipt.get("owner_yes_is_sufficient_without_other_gates") is False, "receipt weakens promotion gates")
    response = receipt.get("response_binding", {})
    surface = receipt.get("surface_binding", {})
    _assert(response.get("bytes") == len(response_bytes), "receipt response size changed")
    _assert(response.get("sha256") == _sha256_bytes(response_bytes), "receipt response hash changed")
    _assert(response.get("decision_values_read") is False, "receipt read decisions before lock")
    _assert(response.get("note_values_read") is False, "receipt read notes before lock")
    _assert(surface.get("bytes") == len(surface_bytes), "receipt surface size changed")
    _assert(surface.get("sha256") == _sha256_bytes(surface_bytes), "receipt surface hash changed")


def _load_prior_intake(repository_root: Path) -> tuple[dict[str, Any], bytes]:
    path = repository_root / (
        "samples/labels/review/grandview/phase-two/intake/"
        "GRANDVIEW-OWNER-RESPONSE-INTAKE-2026-001.json"
    )
    data = path.read_bytes()
    _assert(len(data) == PRIOR_INTAKE_BYTES, "prior accepted-region report size changed")
    _assert(_sha256_bytes(data) == PRIOR_INTAKE_SHA256, "prior accepted-region report hash changed")
    report = _json(data, path.name)
    outcome = report.get("outcome", {})
    _assert(report.get("label_set_version") == PRIOR_LABEL_SET_VERSION, "prior label set changed")
    _assert(outcome.get("cumulative_owner_approved_region_labels") == 10, "prior label count changed")
    _assert(outcome.get("event_group_count") == 5, "prior event count changed")
    _assert(report.get("dataset_version") is None, "prior report contains a dataset")
    return report, data


def _verify_candidate_raster(
    path: Path,
    surface_candidate: dict[str, Any],
    rebuilt_candidate: dict[str, Any],
    selected_candidate: dict[str, Any],
) -> dict[str, Any]:
    expected_binding = surface_candidate["candidate_raster_binding"]
    _assert(path.is_file(), f"candidate raster missing: {path.name}")
    _assert(path.stat().st_size == expected_binding["bytes"], f"candidate raster size changed: {path.name}")
    _assert(_sha256_file(path) == expected_binding["sha256"], f"candidate raster hash changed: {path.name}")
    _assert(rebuilt_candidate["candidate_id"] == surface_candidate["candidate_id"], "candidate order changed")
    _assert(rebuilt_candidate["proposal_binding_sha256"] == EXPECTED_CANDIDATES[surface_candidate["candidate_id"]]["proposal_binding_sha256"], "proposal binding changed")
    with rasterio.open(path) as dataset:
        values = dataset.read(1)
        tags = dataset.tags()
        _assert(dataset.count == 1 and dataset.dtypes == ("uint8",), "candidate dtype changed")
        _assert(dataset.crs is not None and dataset.crs.to_epsg() == 32610, "candidate CRS changed")
        _assert(dataset.nodata == 255.0, "candidate nodata changed")
        _assert(set(int(value) for value in np.unique(values)) <= {0, 1, 2}, "candidate domain changed")
        _assert(np.array_equal(values == 1, selected_candidate["core"]), "candidate core changed")
        _assert(np.array_equal(values == 2, selected_candidate["ring"]), "candidate unknown ring changed")
        _assert(tags.get("candidate_id") == surface_candidate["candidate_id"], "candidate tag changed")
        _assert(tags.get("proposed_class") == surface_candidate["proposed_class"], "candidate class tag changed")
        _assert(tags.get("owner_decision") == "none", "candidate raster embeds a decision")
        _assert(tags.get("label_created") == "false", "candidate raster embeds a label")
    return {
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
        "core_pixels": int((values == 1).sum()),
        "unknown_ring_pixels": int((values == 2).sum()),
        "crs": "EPSG:32610",
        "class_domain": [0, 1, 2],
        "exact_recomputed_core": True,
        "exact_recomputed_unknown_ring": True,
    }


def _proposal_without_written_bindings(value: dict[str, Any]) -> dict[str, Any]:
    normalized = json.loads(json.dumps(value))
    for candidate in normalized["candidates"]:
        candidate["candidate_raster_bytes"] = None
        candidate["candidate_raster_sha256"] = None
    return normalized


def build_private_reconciliation(
    *,
    repository_root: Path,
    pre_package: Path,
    post_package: Path,
    archive_path: Path,
    extracted_root: Path,
    boundary_path: Path,
    source_report_path: Path,
    proposal_path: Path,
    surface_path: Path,
    response_path: Path,
    receipt_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    """Recompute every response, source, raster, uncertainty, and leakage gate."""
    _assert(len(git_source_commit) == 40, "git source commit must be a full SHA")
    _timestamp(generated_at_utc, "generated time")
    for private_path in (
        pre_package,
        post_package,
        archive_path,
        extracted_root,
        boundary_path,
        response_path,
        receipt_path,
    ):
        _assert_ignored(repository_root, private_path)

    surface, surface_bytes = _validate_surface(surface_path)
    response_bytes = response_path.read_bytes()
    receipt_bytes = receipt_path.read_bytes()
    _assert(len(response_bytes) == EXPECTED_RESPONSE_BYTES, "production response size changed")
    _assert(_sha256_bytes(response_bytes) == EXPECTED_RESPONSE_SHA256, "production response hash changed")
    _assert(len(receipt_bytes) == EXPECTED_RECEIPT_BYTES, "production receipt size changed")
    _assert(_sha256_bytes(receipt_bytes) == EXPECTED_RECEIPT_SHA256, "production receipt hash changed")
    receipt = _json(receipt_bytes, receipt_path.name)
    _validate_receipt(receipt, response_bytes=response_bytes, surface_bytes=surface_bytes)
    response = _json(response_bytes, response_path.name)
    try:
        validation = validate_completed_response(surface, response)
    except Exception as error:
        raise WindigoOwnerResponseIntakeError("completed owner response failed validation") from error

    proposal_bytes = proposal_path.read_bytes()
    _assert(len(proposal_bytes) == EXPECTED_PROPOSAL_BYTES, "proposal size changed")
    _assert(_sha256_bytes(proposal_bytes) == EXPECTED_PROPOSAL_SHA256, "proposal hash changed")
    proposal = _json(proposal_bytes, proposal_path.name)
    _assert(proposal.get("report_id") == PROPOSAL_ID, "proposal identity changed")
    _assert(proposal.get("run_id") == PROPOSAL_RUN_ID, "proposal run changed")
    _assert(proposal.get("summary", {}).get("labels_created") == 0, "proposal already contains labels")

    rebuilt, selected, _ = rebuild_proposal(
        pre_package=pre_package,
        post_package=post_package,
        archive_path=archive_path,
        extracted_root=extracted_root,
        boundary_path=boundary_path,
        source_report_path=source_report_path,
        generated_at_utc=proposal["generated_at_utc"],
        run_id=proposal["run_id"],
        git_source_commit=proposal["git_source_commit"],
    )
    _assert(
        rebuilt == _proposal_without_written_bindings(proposal),
        "proposal does not exactly reconstruct from controlled source bytes",
    )
    _assert(rebuilt["source_report"]["sha256"] == SOURCE_REPORT_SHA256, "source report binding changed")
    _assert(rebuilt["route_evidence"]["burned"]["pixels"] == EXPECTED_COUNTS["burned_route"], "burned route changed")
    _assert(rebuilt["route_evidence"]["background"]["pixels"] == EXPECTED_COUNTS["background_route"], "background route changed")
    _assert(rebuilt["registration"]["summary"]["machine_decision"] == "PASS_LOCAL_CONTENT_REGISTRATION_GATE", "registration changed")

    prior, prior_bytes = _load_prior_intake(repository_root)
    record_bindings = _record_bindings(repository_root)
    exact_record_gate = len(record_bindings) == len(RECORD_BINDINGS)
    proposal_candidates = {item["candidate_id"]: item for item in proposal["candidates"]}
    rebuilt_candidates = {item["candidate_id"]: item for item in rebuilt["candidates"]}
    selected_candidates = {item["candidate_id"]: item for item in selected}

    units: list[dict[str, Any]] = []
    provisional_class_counts: Counter[str] = Counter()
    provisional_core_pixels = 0
    reviewed_ring_pixels = 0
    for surface_candidate, response_item in zip(surface["candidates"], response["responses"], strict=True):
        candidate_id = surface_candidate["candidate_id"]
        _assert(surface_candidate["event_group_id"] == REVIEW_EVENT_GROUP_ID, "review event identity changed")
        proposal_candidate = proposal_candidates[candidate_id]
        rebuilt_candidate = rebuilt_candidates[candidate_id]
        selected_candidate = selected_candidates[candidate_id]
        _assert(proposal_candidate["event_group_id"] == EXPECTED_EVENT_GROUP_ID, "proposal event identity changed")
        _assert(proposal_candidate["proposed_class"] == surface_candidate["proposed_class"], "proposal class changed")
        raster_path = proposal_path.parent / proposal_candidate["candidate_raster"]
        raster = _verify_candidate_raster(
            raster_path,
            surface_candidate,
            rebuilt_candidate,
            selected_candidate,
        )
        gates = {
            "owner_yes": response_item["decision"] == "yes",
            "exact_candidate_reconstruction": (
                raster["exact_recomputed_core"]
                and raster["exact_recomputed_unknown_ring"]
                and raster["sha256"] == surface_candidate["candidate_raster_binding"]["sha256"]
            ),
            "source_and_terms": exact_record_gate,
            "quality_and_registration": (
                raster["crs"] == "EPSG:32610"
                and raster["class_domain"] == [0, 1, 2]
                and rebuilt["registration"]["summary"]["machine_decision"]
                == "PASS_LOCAL_CONTENT_REGISTRATION_GATE"
            ),
            "uncertainty_ring_excluded": raster["unknown_ring_pixels"] == 51,
            "event_level_leakage_control": (
                proposal_candidate["event_group_id"] == EXPECTED_EVENT_GROUP_ID
                and surface_candidate["event_group_id"] == REVIEW_EVENT_GROUP_ID
            ),
        }
        candidate_pass = all(gates.values())
        if candidate_pass:
            provisional_class_counts[surface_candidate["proposed_class"]] += 1
            provisional_core_pixels += raster["core_pixels"]
        reviewed_ring_pixels += raster["unknown_ring_pixels"]
        units.append(
            {
                "candidate_id": candidate_id,
                "candidate_binding_sha256": surface_candidate["candidate_binding_sha256"],
                "candidate_raster_sha256": raster["sha256"],
                "event_group_id": surface_candidate["event_group_id"],
                "proposed_class": surface_candidate["proposed_class"],
                "owner_decision": response_item["decision"],
                "note_present": bool(response_item["notes"]),
                "note_sha256": _sha256_bytes(response_item["notes"].encode("utf-8")),
                "gates": gates,
                "candidate_gate_passed": candidate_pass,
                "core_pixels": raster["core_pixels"],
                "unknown_ring_pixels": raster["unknown_ring_pixels"],
            }
        )

    event_complete = (
        len(units) == 2
        and all(item["candidate_gate_passed"] for item in units)
        and provisional_class_counts == Counter({"burned": 1, "background": 1})
        and provisional_core_pixels == 50
        and reviewed_ring_pixels == 102
    )
    for unit in units:
        unit["disposition"] = (
            "OWNER_APPROVED_PROTOTYPE_REGION_LABEL"
            if event_complete
            else "EXCLUDED_NO_PARTIAL_EVENT_PROMOTION"
        )
        unit["accepted_core_pixels"] = unit["core_pixels"] if event_complete else 0
        unit["excluded_unknown_ring_pixels"] = unit["unknown_ring_pixels"] if event_complete else 0

    prior_outcome = prior["outcome"]
    added_labels = 2 if event_complete else 0
    added_core_pixels = 50 if event_complete else 0
    added_ring_pixels = 102 if event_complete else 0
    classes = Counter(prior_outcome["cumulative_prototype_label_class_counts"])
    if event_complete:
        classes.update({"burned": 1, "background": 1})
    event_count = prior_outcome["event_group_count"] + (1 if event_complete else 0)
    cumulative_core_pixels = prior_outcome["cumulative_accepted_core_pixels"] + added_core_pixels
    decision = (
        "ACCEPT_WINDIGO_AS_SIXTH_OWNER_APPROVED_PROTOTYPE_EVENT_KEEP_DATASET_SPLIT_BASELINE_MODEL_CLOSED"
        if event_complete
        else "REJECT_PARTIAL_OR_FAILED_WINDIGO_EVENT_ACTIVATE_TECHNICAL_CASE_STUDY_ONLY"
    )
    return {
        "report_id": f"{REPORT_ID}-PRIVATE",
        "report_version": PRIVATE_REPORT_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "unit_id": UNIT_ID,
        "git_source_commit": git_source_commit,
        "software_version": burnlens.__version__,
        "aoi_version": AOI_VERSION if event_complete else prior["aoi_version"],
        "target_version": TARGET_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "label_set_version": LABEL_SET_VERSION if event_complete else PRIOR_LABEL_SET_VERSION,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "input_bindings": {
            "prior_label_intake": {
                "report_id": prior["report_id"],
                "run_id": prior["run_id"],
                "bytes": len(prior_bytes),
                "sha256": _sha256_bytes(prior_bytes),
            },
            "source_report": {
                "report_id": rebuilt["source_report"]["report_id"],
                "run_id": rebuilt["source_report"]["run_id"],
                **_binding(source_report_path),
            },
            "proposal": {
                "report_id": proposal["report_id"],
                "run_id": proposal["run_id"],
                "bytes": len(proposal_bytes),
                "sha256": _sha256_bytes(proposal_bytes),
            },
            "surface": {
                "report_id": surface["report_id"],
                "run_id": surface["run_id"],
                "bytes": len(surface_bytes),
                "sha256": _sha256_bytes(surface_bytes),
                "ordered_manifest_sha256": surface["ordered_manifest_sha256"],
            },
            "response": {"bytes": len(response_bytes), "sha256": _sha256_bytes(response_bytes)},
            "receipt": {"bytes": len(receipt_bytes), "sha256": _sha256_bytes(receipt_bytes)},
        },
        "record_bindings": record_bindings,
        "response_validation": validation,
        "decision_counts": validation["decision_counts"],
        "private_units": units,
        "outcome": {
            "windigo_owner_approved_region_labels": added_labels,
            "windigo_class_counts": {"background": 1, "burned": 1} if event_complete else {},
            "windigo_accepted_core_pixels": added_core_pixels,
            "windigo_reviewed_unknown_ring_pixels": reviewed_ring_pixels,
            "windigo_excluded_unknown_ring_pixels": added_ring_pixels,
            "windigo_event_complete": event_complete,
            "no_partial_event_promotion": True,
            "cumulative_owner_approved_region_labels": (
                prior_outcome["cumulative_owner_approved_region_labels"] + added_labels
            ),
            "cumulative_prototype_label_class_counts": dict(sorted(classes.items())),
            "cumulative_accepted_core_pixels": cumulative_core_pixels,
            "cumulative_accepted_core_area_ha": round(cumulative_core_pixels * 0.04, 2),
            "cumulative_excluded_unknown_ring_pixels": (
                prior_outcome["cumulative_excluded_unknown_ring_pixels"] + added_ring_pixels
            ),
            "event_group_count": event_count,
            "minimum_event_group_count": MINIMUM_EVENT_GROUPS,
            "minimum_event_group_gate_passed": event_count >= MINIMUM_EVENT_GROUPS,
            "separate_sufficiency_evaluator_passed": False,
            "dataset_fitness_reopened": False,
        },
        "promotion_gates": {
            "exact_response_and_pre_reveal_custody": True,
            "exact_source_pixel_recomputation": True,
            "candidate_raster_reconstruction": True,
            "source_and_terms": exact_record_gate,
            "quality_and_registration": True,
            "unknown_ring_excluded": True,
            "event_level_leakage_control": True,
            "both_classes_and_no_partial_promotion": event_complete,
        },
        "decision": decision,
        "next_gate": (
            "P2O4-T35-U06 must close the milestone and hand off the August 6 portfolio assembly. "
            "A separate sufficiency evaluator is still required before any dataset or split work."
        ),
        "warning": WARNING,
    }


def public_report(private: dict[str, Any], private_binding: dict[str, Any]) -> dict[str, Any]:
    """Remove unit decisions, notes, and private paths from the public evidence."""
    outcome = private["outcome"]
    return {
        "report_id": REPORT_ID,
        "report_version": REPORT_VERSION,
        "generated_at_utc": private["generated_at_utc"],
        "run_id": private["run_id"],
        "repository": private["repository"],
        "task_issue": private["task_issue"],
        "unit_id": private["unit_id"],
        "git_source_commit": private["git_source_commit"],
        "software_version": private["software_version"],
        "aoi_version": private["aoi_version"],
        "target_version": private["target_version"],
        "label_schema_version": private["label_schema_version"],
        "label_set_version": private["label_set_version"],
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "input_bindings": {
            **private["input_bindings"],
            "private_reconciliation": private_binding,
        },
        "record_bindings": private["record_bindings"],
        "decision_counts": private["decision_counts"],
        "outcome": outcome,
        "promotion_gates": private["promotion_gates"],
        "privacy": {
            "notes_public": False,
            "unit_decisions_public": False,
            "private_paths_public": False,
        },
        "boundaries": {
            "owner_review_is_independent_ground_truth": False,
            "unknown_ring_is_background": False,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
            "accuracy_or_operational_claim_created": False,
        },
        "attribution": [
            "Contains modified Copernicus Sentinel data 2022, accessed through CDSE.",
            "BAER evidence is field-informed preliminary prototype-positive evidence with program cautions.",
            "MTBS evidence corroborates the burned proposal under program-specific limits.",
            "RAVG modeled effects remain context and conservative exclusion only.",
        ],
        "warning": private["warning"],
        "decision": private["decision"],
        "next_gate": private["next_gate"],
    }


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ):
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _render_png(report: dict[str, Any], path: Path) -> None:
    outcome = report["outcome"]
    image = Image.new("RGB", (1600, 1100), "#f4f0e8")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1600, 210), fill="#132a26")
    draw.text((70, 45), "BURNLENS / WINDIGO RESPONSE INTAKE", fill="#aee3d5", font=_font(22))
    draw.text((70, 90), "Sixth prototype event passes; dataset stays closed.", fill="white", font=_font(42))
    draw.text((70, 155), WARNING, fill="#ffe0a3", font=_font(18))
    metrics = (
        ("2", "owner yes decisions"),
        (str(outcome["windigo_owner_approved_region_labels"]), "new prototype regions"),
        (str(outcome["cumulative_owner_approved_region_labels"]), "cumulative regions"),
        (str(outcome["event_group_count"]), "complete events"),
    )
    for index, (value, label) in enumerate(metrics):
        left = 70 + index * 380
        draw.rounded_rectangle((left, 255, left + 340, 420), radius=16, fill="white", outline="#d7cec1")
        draw.text((left + 25, 285), value, fill="#006b64", font=_font(48))
        draw.text((left + 25, 360), label, fill="#263932", font=_font(19))
    rows = (
        "PASS  exact response locked before reveal; one unambiguous final",
        "PASS  exact Sentinel and BAER/MTBS/RAVG pixels recomputed",
        "PASS  both candidate rasters, cores, and unknown rings reconstruct",
        "PASS  both classes advance together; no partial event promotion",
        "BLOCK dataset: six events are necessary, never sufficient",
    )
    for index, line in enumerate(rows):
        draw.text(
            (95, 500 + index * 70),
            line,
            fill="#8a521c" if line.startswith("BLOCK") else "#006b64",
            font=_font(22),
        )
    draw.rounded_rectangle((70, 875, 1530, 1000), radius=14, fill="#fff8dd", outline="#d87618")
    draw.text((95, 905), "Decision", fill="#8a521c", font=_font(20))
    draw.text((95, 950), report["decision"], fill="#132a26", font=_font(17))
    draw.text(
        (70, 1035),
        f"BurnLens {report['software_version']} | {report['label_set_version']} | run {report['run_id']}",
        fill="#263932",
        font=_font(15),
    )
    image.save(path, format="PNG", optimize=False)


def _render_html(report: dict[str, Any]) -> str:
    counts = report["decision_counts"]
    outcome = report["outcome"]
    attribution = "".join(f"<li>{escape(value)}</li>" for value in report["attribution"])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BurnLens Windigo owner response intake</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f4f0e8;color:#17251f;font:16px/1.55 system-ui,sans-serif;overflow-wrap:anywhere}}header{{background:#132a26;color:white;padding:2.4rem max(5vw,1rem)}}header p{{max-width:900px;color:#c6ddd6}}main{{max-width:1120px;margin:auto;padding:1.2rem}}.warning,.card{{background:#fffdf8;border:1px solid #d7cec1;border-radius:14px;padding:1.1rem;margin:1rem 0}}.warning{{border-left:7px solid #d87618;font-weight:650}}.metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1rem}}.metric{{background:white;border:1px solid #d7cec1;border-radius:12px;padding:1rem}}.metric strong{{display:block;color:#006b64;font-size:2rem}}img{{display:block;width:100%;height:auto;border:1px solid #d7cec1}}code{{word-break:break-word}}li+li{{margin-top:.45rem}}@media(max-width:700px){{.metrics{{grid-template-columns:1fr 1fr}}header{{padding:1.4rem 1rem}}main{{padding:.65rem}}}}
</style></head><body><header><p>BURNLENS / PHASE TWO / ISSUE #534</p><h1>Windigo completes the sixth prototype event.</h1><p>Exact private custody, full source-pixel replay, and aggregate public evidence.</p></header><main>
<p class="warning">{escape(report['warning'])}</p><section class="metrics"><div class="metric"><strong>{sum(counts.values())}</strong>owner responses</div><div class="metric"><strong>{outcome['windigo_owner_approved_region_labels']}</strong>new regions</div><div class="metric"><strong>{outcome['cumulative_owner_approved_region_labels']}</strong>cumulative regions</div><div class="metric"><strong>{outcome['event_group_count']}</strong>complete events</div></section>
<section class="card"><h2>Aggregate result</h2><p>Owner decisions: {counts['yes']} yes / {counts['no']} no / {counts['uncertain']} uncertain. Windigo adds one burned and one background prototype region only because every non-owner gate also passes.</p><p>Exact source pixels, proposal routes, candidate rasters, native grid, uncertainty rings, terms, and event identity all reconstruct. Notes and unit decisions remain private.</p></section>
<img src="{REPORT_ID}.png" alt="Windigo owner response intake gate summary">
<section class="card"><h2>Sources and roles</h2><ul>{attribution}</ul></section>
<section class="card"><h2>Why the dataset remains blocked</h2><p>Six complete event groups meet only the frozen count minimum. The separate sufficiency evaluator has not passed class and uncertainty completeness, source-regime replication, never-tuned transfer, dominance, and leakage gates. No dataset or split exists.</p></section>
<section class="card"><h2>Decision</h2><p><strong>{escape(report['decision'])}</strong></p><p>BurnLens <code>{escape(report['software_version'])}</code> &middot; label set <code>{escape(report['label_set_version'])}</code> &middot; schema <code>{escape(report['label_schema_version'])}</code> &middot; run <code>{escape(report['run_id'])}</code> &middot; source <code>{escape(report['git_source_commit'])}</code>. Dataset, split, baseline, and model remain absent.</p></section>
</main></body></html>'''


def write_private_no_overwrite(
    repository_root: Path,
    path: Path,
    report: dict[str, Any],
) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    _assert_ignored(repository_root, path)
    payload = (json.dumps(report, indent=2) + "\n").encode("utf-8")
    try:
        with path.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        raise WindigoOwnerResponseIntakeError("refusing to overwrite private reconciliation") from error
    return {"bytes": len(payload), "sha256": _sha256_bytes(payload), "committed": False, "ignored": True}


def write_public_no_overwrite(
    report: dict[str, Any],
    output_directory: Path,
) -> list[dict[str, Any]]:
    if output_directory.exists():
        raise WindigoOwnerResponseIntakeError("public output directory already exists")
    output_directory.mkdir(parents=True)
    png_path = output_directory / f"{REPORT_ID}.png"
    html_path = output_directory / f"{REPORT_ID}.html"
    json_path = output_directory / f"{REPORT_ID}.json"
    _render_png(report, png_path)
    html_path.write_text(_render_html(report), encoding="utf-8", newline="\n")
    report["outputs"] = [
        {"path": html_path.name, **_binding(html_path), "media_type": "text/html"},
        {"path": png_path.name, **_binding(png_path), "media_type": "image/png"},
    ]
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return [
        {"path": json_path.name, **_binding(json_path), "media_type": "application/json"},
        *report["outputs"],
    ]
