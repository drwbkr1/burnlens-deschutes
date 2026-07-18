"""Evaluate deterministic BurnLens owner-label promotion gates.

The evaluator makes the four post-``yes`` gates executable against the exact
shipped 56-unit surface. It can run without a response for preflight or with a
validated response for controlled prototype-label reconciliation.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from .lock_owner_review_response import validate_response
from .owner_review_surface import (
    BUNDLE_REPORT_SHA256,
    PACKET_SHA256,
    SURFACE_ID,
    OwnerReviewSurfaceError,
    build_surface,
)


PROTOCOL_VERSION = "owner-confirmed-prototype-promotion-gates-v0.1.0"
SURFACE_SHA256 = "403cc46181c851722a951f0976a88ea707971c159b34df03456432d6592e02be"
SOURCE_PRECEDENCE_ID = "SOURCE-PRECEDENCE-2026-010"
TERMS_REVIEW_ID = "TERMS-2026-012"


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _exact_json(path: Path, expected_sha256: str) -> tuple[dict[str, Any], bytes]:
    data = path.read_bytes()
    if _digest(data) != expected_sha256:
        raise OwnerReviewSurfaceError(f"exact input drift: {path.name}")
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise OwnerReviewSurfaceError(f"invalid UTF-8 JSON: {path.name}") from error
    if not isinstance(value, dict):
        raise OwnerReviewSurfaceError(f"JSON input is not an object: {path.name}")
    return value, data


def verify_surface_reconstruction(
    *,
    repository_root: Path,
    archive_dir: Path,
    packet_path: Path,
    bundle_report_path: Path,
    surface_path: Path,
) -> dict[str, Any]:
    """Rebuild the exact source-bound surface and verify every public output."""

    surface, surface_bytes = _exact_json(surface_path, SURFACE_SHA256)
    if surface.get("report_id") != SURFACE_ID or len(surface.get("units", [])) != 56:
        raise OwnerReviewSurfaceError("owner review surface identity drift")
    if surface.get("source_bindings", {}).get("historical_packet", {}).get("sha256") != PACKET_SHA256:
        raise OwnerReviewSurfaceError("historical packet binding drift")
    if surface.get("source_bindings", {}).get("current_bundle_fitness", {}).get("sha256") != BUNDLE_REPORT_SHA256:
        raise OwnerReviewSurfaceError("current bundle binding drift")

    rebuilt, _ = build_surface(
        repository_root=repository_root,
        archive_dir=archive_dir,
        packet_path=packet_path,
        bundle_report_path=bundle_report_path,
        generated_at_utc=surface["generated_at_utc"],
        run_id=surface["run_id"],
        git_source_commit=surface["git_source_commit"],
    )
    rebuilt["outputs"] = deepcopy(surface["outputs"])
    rebuilt_bytes = (json.dumps(rebuilt, indent=2) + "\n").encode("utf-8")
    if rebuilt_bytes != surface_bytes:
        raise OwnerReviewSurfaceError("owner review surface reconstruction drift")

    verified_outputs = []
    for output in surface["outputs"]:
        path = surface_path.parent / output["path"]
        data = path.read_bytes()
        if len(data) != output["bytes"] or _digest(data) != output["sha256"]:
            raise OwnerReviewSurfaceError(f"owner review public output drift: {path.name}")
        verified_outputs.append({"path": path.name, "bytes": len(data), "sha256": _digest(data)})
    return {
        "surface": surface,
        "surface_bytes": len(surface_bytes),
        "surface_sha256": SURFACE_SHA256,
        "verified_output_count": len(verified_outputs) + 1,
        "verified_outputs": verified_outputs,
    }


def _source_limitations(unit: dict[str, Any]) -> list[str]:
    limitations = [
        "current thematic classes are bounded reference evidence, not truth alone",
    ]
    programs = {item["program"] for item in unit["current_reference_evidence"]["categorical"]}
    if "MTBS" not in programs:
        limitations.append("no current MTBS categorical sample for this unit")
    if "RAVG" in programs:
        limitations.append("RAVG is forest-calibrated and timing-sensitive")
    if unit["current_reference_evidence"]["baer_dnbr"] is not None:
        limitations.append("BAER dNBR is continuous context; positive change is not a burned threshold")
    if unit["event_group_id"] == "event-darlene3-or-2024":
        limitations.append("Darlene lacks categorical cross-program confirmation")
    return limitations


def evaluate_units(
    surface: dict[str, Any],
    response: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Evaluate all gates, optionally against one already validated exact response."""

    decisions: dict[str, str] = {}
    if response is not None:
        validate_response(surface, response)
        decisions = {item["sample_id"]: item["decision"] for item in response["responses"]}

    evaluated: list[dict[str, Any]] = []
    for unit in surface["units"]:
        quality_pass = unit["frozen_proposal_state"] in {"burned", "background-candidate"}
        decision = decisions.get(unit["sample_id"])
        if decision is None:
            current_status = "PENDING_OWNER_RESPONSE"
        elif decision in {"no", "uncertain"}:
            current_status = "EXCLUDED_BY_OWNER_RESPONSE"
        elif quality_pass:
            current_status = "ELIGIBLE_OWNER_APPROVED_PROTOTYPE_LABEL"
        else:
            current_status = "EXCLUDED_QUALITY_BLOCKED_AFTER_YES"

        categorical = [
            {
                "program": item["program"],
                "value": item["value"],
                "semantic": item["semantic"],
            }
            for item in unit["current_reference_evidence"]["categorical"]
        ]
        evaluated.append({
            "sample_id": unit["sample_id"],
            "event_group_id": unit["event_group_id"],
            "candidate_label": unit["candidate_label"],
            "frozen_proposal_state": unit["frozen_proposal_state"],
            "selection_hash": unit["selection_hash"],
            "presentation_hash": unit["presentation_hash"],
            "owner_decision": decision,
            "gates": {
                "reproducibility": {
                    "status": "PASS_EXACT_RECONSTRUCTION",
                    "basis": "exact packet, current bundle, surface, unit order, selection hash, and presentation hash",
                },
                "source": {
                    "status": "PASS_BOUNDED_ROLES_WITH_LIMITATIONS",
                    "precedence_id": SOURCE_PRECEDENCE_ID,
                    "terms_review_id": TERMS_REVIEW_ID,
                    "candidate_basis": unit["candidate_basis"],
                    "categorical_evidence": categorical,
                    "limitations": _source_limitations(unit),
                    "restricted_thresholded_tepee_barc_used": False,
                },
                "quality": {
                    "status": "PASS_FROZEN_BINARY_ORIGIN" if quality_pass else "BLOCKED_NONBINARY_ORIGIN",
                    "blocker": None if quality_pass else unit["frozen_proposal_state"],
                    "owner_yes_can_override": False,
                },
                "event_leakage": {
                    "status": "PASS_GROUP_BOUND_NO_PARTITION",
                    "event_group_id": unit["event_group_id"],
                    "partition_created": False,
                    "dataset_created": False,
                    "requirement": "all derived pixels from an event remain inseparable in any later partition",
                },
                "owner_response": {
                    "status": "PENDING" if decision is None else "PASS_EXACT_COMPLETED_RESPONSE_BINDING",
                    "decision": decision,
                },
            },
            "prospective_after_owner_yes": (
                "ELIGIBLE_FOR_EXPLICIT_OWNER_APPROVED_PROTOTYPE_LABEL"
                if quality_pass
                else "REMAINS_EXCLUDED_QUALITY_BLOCKED"
            ),
            "current_status": current_status,
            "label_promoted": current_status == "ELIGIBLE_OWNER_APPROVED_PROTOTYPE_LABEL",
        })

    counts = Counter(item["current_status"] for item in evaluated)
    counts["POTENTIALLY_ELIGIBLE_AFTER_YES"] = sum(
        item["prospective_after_owner_yes"] == "ELIGIBLE_FOR_EXPLICIT_OWNER_APPROVED_PROTOTYPE_LABEL"
        for item in evaluated
    )
    counts["BLOCKED_EVEN_AFTER_YES"] = sum(
        item["prospective_after_owner_yes"] == "REMAINS_EXCLUDED_QUALITY_BLOCKED"
        for item in evaluated
    )
    return evaluated, dict(sorted(counts.items()))
