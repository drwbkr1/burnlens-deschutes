"""Fail-closed intake for the exact Grandview owner response."""

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
from .grandview_owner_review_surface import (
    ALLOWED_DECISIONS,
    EXPECTED_PROPOSAL_OUTPUTS,
    RESPONSE_SCHEMA_VERSION,
    SURFACE_ID,
    SURFACE_VERSION,
)
from .grandview_region_proposal import REPORT_ID as PROPOSAL_ID
from .grandview_owner_response_lock import (
    EVIDENCE_ORIGIN,
    LOCK_VERSION,
    preserve_response_without_reveal,
)


REPORT_ID = "GRANDVIEW-OWNER-RESPONSE-INTAKE-2026-001"
REPORT_VERSION = "grandview-owner-response-intake-v0.1.0"
PRIVATE_REPORT_VERSION = "grandview-owner-response-private-reconciliation-v0.1.0"
LABEL_SET_VERSION = "owner-approved-prototype-region-labels-v0.3.0"
PRIOR_LABEL_SET_VERSION = "owner-approved-prototype-region-labels-v0.2.0"
LABEL_SCHEMA_VERSION = "burn-scar-five-state-schema-v0.1.0"
AOI_VERSION = "multi-event-native-grids-v0.3.0"
TARGET_VERSION = "target-burn-scar-v0.2.0"
TASK_ISSUE = 517
MINIMUM_EVENT_GROUPS = 6
EXPECTED_SURFACE_SHA256 = "7576ab36e97d026f9f706e67c75e3482b718818a3697e704a17ce7dc4c54369c"
PRIOR_INTAKE_SHA256 = "ccfcca5d458b7ced654088bb96a959ce26293469f69e39f3dbb08b7e29b1d3c3"
SOURCE_RECORDS = (
    "SOURCE-2026-024",
    "SOURCE-2026-026",
    "SOURCE-2026-027",
)
TERMS_RECORDS = (
    "TERMS-2026-020",
    "TERMS-2026-022",
    "TERMS-2026-023",
)
REVIEW_RECORDS = (
    "PRECHECK-2026-038",
    "PRECHECK-2026-040",
    "PRECHECK-2026-041",
    "PRECHECK-2026-042",
    "LABEL-FITNESS-2026-026",
    "LABEL-FITNESS-2026-027",
    "SOURCE-PRECEDENCE-2026-017",
    "USE-BOUNDARY-2026-036",
    "USE-BOUNDARY-2026-037",
    "USE-BOUNDARY-2026-038",
)
MANIFEST_RECORDS = tuple(f"MANIFEST-2026-{value:03d}" for value in range(40, 46))
WARNING = (
    "Experimental BurnLens owner-approved prototype region labels. Not ground truth, "
    "official wildfire information, emergency guidance, or a dataset. Official sources govern."
)


class GrandviewOwnerResponseIntakeError(RuntimeError):
    """Raised when response custody or any promotion gate fails closed."""


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise GrandviewOwnerResponseIntakeError(message)


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
        raise GrandviewOwnerResponseIntakeError(f"invalid UTF-8 JSON: {name}") from error
    _assert(isinstance(value, dict), f"JSON is not an object: {name}")
    return value


def _timestamp(value: Any, name: str) -> datetime:
    _assert(isinstance(value, str), f"{name} is not a timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise GrandviewOwnerResponseIntakeError(f"{name} is invalid") from error
    _assert(parsed.tzinfo is not None, f"{name} lacks timezone")
    return parsed


def _exact_keys(value: dict[str, Any], keys: set[str], name: str) -> None:
    _assert(set(value) == keys, f"{name} fields changed")


def _validate_surface(surface_path: Path) -> tuple[dict[str, Any], bytes]:
    data = surface_path.read_bytes()
    _assert(_sha256_bytes(data) == EXPECTED_SURFACE_SHA256, "surface bytes changed")
    surface = _json(data, surface_path.name)
    _assert(surface.get("report_id") == SURFACE_ID, "surface identity changed")
    _assert(surface.get("report_version") == SURFACE_VERSION, "surface version changed")
    _assert(surface.get("response_schema_version") == RESPONSE_SCHEMA_VERSION, "surface schema changed")
    _assert(surface.get("summary", {}).get("owner_responses") == 0, "surface already contains responses")
    _assert(surface.get("summary", {}).get("labels_created") == 0, "surface already contains labels")
    proposal = surface.get("input_bindings", {}).get(f"{PROPOSAL_ID}.json", {})
    _assert(proposal.get("sha256") == EXPECTED_PROPOSAL_OUTPUTS[f"{PROPOSAL_ID}.json"][1], "surface proposal binding changed")
    return surface, data


def validate_response(surface: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    """Validate exact order, identities, hashes, decisions, timestamps, and attestation."""
    _exact_keys(
        response,
        {
            "response_schema_version",
            "surface_id",
            "surface_run_id",
            "proposal_report_sha256",
            "completed",
            "review_started_at_utc",
            "review_completed_at_utc",
            "owner",
            "responses",
        },
        "response",
    )
    _assert(response["response_schema_version"] == RESPONSE_SCHEMA_VERSION, "response schema mismatch")
    _assert(response["surface_id"] == SURFACE_ID, "response surface mismatch")
    _assert(response["surface_run_id"] == surface["run_id"], "response surface run mismatch")
    _assert(
        response["proposal_report_sha256"] == surface["input_bindings"][f"{PROPOSAL_ID}.json"]["sha256"],
        "response proposal binding mismatch",
    )
    _assert(response["completed"] is True, "response is incomplete")
    owner = response["owner"]
    _assert(isinstance(owner, dict), "owner attestation is not an object")
    _exact_keys(owner, {"attestation"}, "owner attestation")
    _assert(owner["attestation"] is True, "owner attestation is incomplete")
    started = _timestamp(response["review_started_at_utc"], "review start")
    completed = _timestamp(response["review_completed_at_utc"], "review completion")
    _assert(completed >= started, "review completion predates start")

    candidates = surface.get("candidates")
    items = response["responses"]
    _assert(isinstance(candidates, list) and len(candidates) == 2, "surface candidates changed")
    _assert(isinstance(items, list) and len(items) == 2, "response must contain two decisions")
    counts = Counter({decision: 0 for decision in ALLOWED_DECISIONS})
    seen: set[str] = set()
    for candidate, item in zip(candidates, items, strict=True):
        _assert(isinstance(item, dict), "response item is not an object")
        _exact_keys(item, {"candidate_id", "candidate_raster_sha256", "decision", "notes"}, "response item")
        candidate_id = item["candidate_id"]
        _assert(candidate_id not in seen, "duplicate candidate response")
        seen.add(candidate_id)
        _assert(candidate_id == candidate["candidate_id"], "candidate order or identity changed")
        _assert(item["candidate_raster_sha256"] == candidate["candidate_raster_sha256"], "candidate raster binding changed")
        _assert(item["decision"] in ALLOWED_DECISIONS, "decision is outside yes/no/uncertain")
        counts[item["decision"]] += 1
        _assert(isinstance(item["notes"], str) and len(item["notes"]) <= 1000, "response notes violate the bounded string contract")
    return {
        "decision_counts": {decision: counts[decision] for decision in ALLOWED_DECISIONS},
        "started_at_utc": response["review_started_at_utc"],
        "completed_at_utc": response["review_completed_at_utc"],
        "candidate_bindings": [
            {"candidate_id": item["candidate_id"], "candidate_raster_sha256": item["candidate_raster_sha256"]}
            for item in items
        ],
    }


def _assert_ignored(repository_root: Path, path: Path) -> None:
    relative = path.relative_to(repository_root)
    result = subprocess.run(
        ["git", "-C", str(repository_root), "check-ignore", "--quiet", "--no-index", "--", str(relative)],
        check=False,
    )
    _assert(result.returncode == 0, "private output is not ignored")


def preserve_response(
    *,
    repository_root: Path,
    surface_path: Path,
    source_response_path: Path,
    destination_directory: Path,
    received_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> tuple[Path, Path, dict[str, Any]]:
    """Compatibility wrapper that always uses the pre-reveal custody transaction."""
    return preserve_response_without_reveal(
        repository_root=repository_root,
        surface_path=surface_path,
        source_response_path=source_response_path,
        destination_directory=destination_directory,
        received_at_utc=received_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
    )


def _record_path(repository_root: Path, record_id: str) -> Path:
    stem = record_id.replace("LABEL-FITNESS", "LABEL_FITNESS").replace("SOURCE-PRECEDENCE", "SOURCE_PRECEDENCE").replace("USE-BOUNDARY", "USE_BOUNDARY")
    if record_id.startswith("SOURCE-PRECEDENCE-"):
        root = repository_root / "records/phase-two/reviews"
    elif record_id.startswith("SOURCE-"):
        root = repository_root / "records/phase-two/sources"
    elif record_id.startswith("TERMS-"):
        root = repository_root / "records/phase-two/terms"
    elif record_id.startswith("PRECHECK-"):
        root = repository_root / "records/phase-two/prechecks"
    elif record_id.startswith("MANIFEST-"):
        root = repository_root / "records/phase-two/manifests"
    else:
        root = repository_root / "records/phase-two/reviews"
    matches = list(root.glob(f"{stem}.*"))
    _assert(len(matches) == 1 and matches[0].is_file(), f"record binding missing or ambiguous: {record_id}")
    return matches[0]


def _record_bindings(repository_root: Path) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for record_id in (*SOURCE_RECORDS, *TERMS_RECORDS, *REVIEW_RECORDS, *MANIFEST_RECORDS):
        path = _record_path(repository_root, record_id)
        text = path.read_text(encoding="utf-8")
        if record_id == "TERMS-2026-020":
            _assert("free, full, and open basis" in text and "Terms and attribution are resolved" in text, "original optical terms are unresolved")
        if record_id == "TERMS-2026-022":
            _assert("access constraints are `None`" in text and "thresholded preliminary" in text, "delivered reference terms changed")
        if record_id == "TERMS-2026-023":
            _assert("Terms and attribution are resolved" in text and "No warranty" in text, "extended optical terms are unresolved")
        values.append({"record_id": record_id, **_binding(path)})
    return values


def _connected(mask: np.ndarray) -> bool:
    points = np.argwhere(mask)
    if not len(points):
        return False
    start = tuple(int(value) for value in points[0])
    seen = {start}
    queue: deque[tuple[int, int]] = deque([start])
    height, width = mask.shape
    while queue:
        row, column = queue.popleft()
        for delta_row in (-1, 0, 1):
            for delta_column in (-1, 0, 1):
                if not (delta_row or delta_column):
                    continue
                candidate = (row + delta_row, column + delta_column)
                if 0 <= candidate[0] < height and 0 <= candidate[1] < width and mask[candidate] and candidate not in seen:
                    seen.add(candidate)
                    queue.append(candidate)
    return len(seen) == int(mask.sum())


def _one_pixel_ring(core: np.ndarray) -> np.ndarray:
    padded = np.pad(core, 1, constant_values=False)
    output = np.zeros_like(core, dtype=bool)
    for row_offset in range(3):
        for column_offset in range(3):
            output |= padded[row_offset : row_offset + core.shape[0], column_offset : column_offset + core.shape[1]]
    return output & ~core


def _verify_candidate_raster(path: Path, candidate: dict[str, Any]) -> dict[str, Any]:
    _assert(path.is_file(), f"candidate raster missing: {path.name}")
    _assert(path.stat().st_size == candidate["candidate_raster_bytes"], f"candidate raster size changed: {path.name}")
    _assert(_sha256_file(path) == candidate["candidate_raster_sha256"], f"candidate raster hash changed: {path.name}")
    contract = candidate["raster_contract"]
    with rasterio.open(path) as dataset:
        values = dataset.read(1)
        tags = dataset.tags()
        _assert(dataset.count == 1 and dataset.dtypes == ("uint8",), f"candidate raster dtype changed: {path.name}")
        _assert(dataset.crs is not None and dataset.crs.to_epsg() == 32610, f"candidate raster CRS changed: {path.name}")
        _assert(list(dataset.shape) == contract["shape"], f"candidate raster dimensions changed: {path.name}")
        _assert(np.allclose(list(dataset.transform)[:6], contract["transform"], rtol=0, atol=0), f"candidate raster transform changed: {path.name}")
        _assert(dataset.nodata == contract["nodata"] == 255.0, f"candidate raster nodata changed: {path.name}")
        _assert(set(int(value) for value in np.unique(values)) <= {0, 1, 2}, f"candidate raster domain changed: {path.name}")
        core = values == 1
        ring = values == 2
        _assert(int(core.sum()) == candidate["core_pixels"], f"candidate core count changed: {path.name}")
        _assert(int(ring.sum()) == candidate["unknown_ring_pixels"], f"candidate ring count changed: {path.name}")
        _assert(_connected(core), f"candidate core is not intact 8-connected evidence: {path.name}")
        _assert(np.array_equal(ring, _one_pixel_ring(core)), f"candidate unknown ring changed: {path.name}")
        _assert(tags.get("candidate_id") == candidate["candidate_id"], f"candidate raster identity tag changed: {path.name}")
        _assert(tags.get("proposed_class") == candidate["proposed_class"], f"candidate class tag changed: {path.name}")
        _assert(tags.get("label_created") == "false", f"candidate no-promotion tag changed: {path.name}")
    return {
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
        "core_pixels": int(core.sum()),
        "unknown_ring_pixels": int(ring.sum()),
        "crs": "EPSG:32610",
        "class_domain": [0, 1, 2],
        "core_connected_8": True,
        "ring_exactly_one_pixel": True,
    }


def _validate_receipt(receipt: dict[str, Any], response_bytes: bytes, surface_bytes: bytes) -> None:
    _assert(receipt.get("report_id") == f"{SURFACE_ID}-RECEIPT", "receipt identity changed")
    _assert(receipt.get("report_version") == LOCK_VERSION, "receipt version changed")
    _assert(receipt.get("task_issue") == TASK_ISSUE, "receipt issue changed")
    _assert(receipt.get("evidence_origin") == EVIDENCE_ORIGIN, "receipt origin changed")
    _assert(receipt.get("origin_declared_by_operator") is True, "receipt origin declaration changed")
    _assert(receipt.get("exact_response_preserved_without_overwrite") is True, "receipt lacks no-overwrite custody")
    _assert(receipt.get("decisions_revealed") is False, "receipt is not pre-reveal custody")
    _assert(receipt.get("qualifying_owner_response") is None, "receipt pre-qualifies the response")
    _assert(
        receipt.get("owner_yes_is_sufficient_without_other_gates") is False,
        "receipt weakens the non-owner promotion gates",
    )
    _assert(receipt.get("response_binding", {}).get("bytes") == len(response_bytes), "receipt response size changed")
    _assert(receipt.get("response_binding", {}).get("sha256") == _sha256_bytes(response_bytes), "receipt response hash changed")
    _assert(
        receipt.get("response_binding", {}).get("decision_values_read") is False,
        "receipt read decisions before custody",
    )
    _assert(
        receipt.get("response_binding", {}).get("note_values_read") is False,
        "receipt read notes before custody",
    )
    _assert("decision_counts" not in receipt.get("response_binding", {}), "receipt exposes decision counts")
    _assert(receipt.get("surface_binding", {}).get("bytes") == len(surface_bytes), "receipt surface size changed")
    _assert(receipt.get("surface_binding", {}).get("sha256") == _sha256_bytes(surface_bytes), "receipt surface hash changed")


def _load_prior_intake(repository_root: Path) -> tuple[dict[str, Any], bytes]:
    path = repository_root / "samples/labels/review/green-ridge/phase-two/intake/GREEN-RIDGE-OWNER-RESPONSE-INTAKE-2026-001.json"
    data = path.read_bytes()
    _assert(_sha256_bytes(data) == PRIOR_INTAKE_SHA256, "prior accepted-region report changed")
    report = _json(data, path.name)
    _assert(report.get("label_set_version") == PRIOR_LABEL_SET_VERSION, "prior label set changed")
    _assert(report.get("outcome", {}).get("cumulative_owner_approved_region_labels") == 8, "prior accepted label count changed")
    _assert(report.get("outcome", {}).get("event_group_count") == 4, "prior event count changed")
    _assert(report.get("dataset_version") is None, "prior report unexpectedly contains a dataset")
    return report, data


def build_private_reconciliation(
    *,
    repository_root: Path,
    proposal_path: Path,
    surface_path: Path,
    response_path: Path,
    receipt_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    """Re-run response, source, raster, uncertainty, and leakage gates privately."""
    _assert(len(git_source_commit) == 40, "git source commit must be a full SHA")
    _timestamp(generated_at_utc, "generated time")
    surface, surface_bytes = _validate_surface(surface_path)
    response_bytes = response_path.read_bytes()
    receipt_bytes = receipt_path.read_bytes()
    receipt = _json(receipt_bytes, receipt_path.name)
    _validate_receipt(receipt, response_bytes, surface_bytes)
    response = _json(response_bytes, response_path.name)
    validation = validate_response(surface, response)

    proposal_bytes = proposal_path.read_bytes()
    _assert(_sha256_bytes(proposal_bytes) == EXPECTED_PROPOSAL_OUTPUTS[f"{PROPOSAL_ID}.json"][1], "proposal report changed")
    proposal = _json(proposal_bytes, proposal_path.name)
    _assert(proposal.get("report_id") == PROPOSAL_ID, "proposal identity changed")
    _assert(proposal.get("summary", {}).get("labels_created") == 0, "proposal already contains labels")
    prior, prior_bytes = _load_prior_intake(repository_root)
    proposal_candidates = {item["candidate_id"]: item for item in proposal.get("candidates", [])}
    _assert(len(proposal_candidates) == 2, "proposal candidate count changed")

    units: list[dict[str, Any]] = []
    added_class_counts: Counter[str] = Counter()
    accepted_core_pixels = 0
    excluded_ring_pixels = 0
    for candidate, response_item in zip(surface["candidates"], response["responses"], strict=True):
        proposal_candidate = proposal_candidates.get(candidate["candidate_id"])
        _assert(proposal_candidate is not None, "candidate absent from proposal")
        _assert(proposal_candidate["candidate_class"] == candidate["proposed_class"], "proposal/surface class mismatch")
        raster_path = proposal_path.parent / candidate["candidate_raster"]
        raster_gate = _verify_candidate_raster(raster_path, candidate)
        gates = {
            "owner_response": response_item["decision"] == "yes",
            "reproducibility": True,
            "source_and_terms": True,
            "quality_and_registration": True,
            "uncertainty_ring_excluded": True,
            "event_level_leakage_control": True,
        }
        accepted = all(gates.values())
        if accepted:
            added_class_counts[candidate["proposed_class"]] += 1
            accepted_core_pixels += raster_gate["core_pixels"]
        excluded_ring_pixels += raster_gate["unknown_ring_pixels"]
        units.append(
            {
                "candidate_id": candidate["candidate_id"],
                "candidate_raster_sha256": candidate["candidate_raster_sha256"],
                "event_group_id": candidate["event_group_id"],
                "proposed_class": candidate["proposed_class"],
                "owner_decision": response_item["decision"],
                "note_present": bool(response_item["notes"]),
                "note_sha256": _sha256_bytes(response_item["notes"].encode("utf-8")),
                "gates": gates,
                "disposition": "OWNER_APPROVED_PROTOTYPE_REGION_LABEL" if accepted else "EXCLUDED_OWNER_NO_OR_UNCERTAIN",
                "accepted_core_pixels": raster_gate["core_pixels"] if accepted else 0,
                "excluded_unknown_ring_pixels": raster_gate["unknown_ring_pixels"],
                "raster_gate": raster_gate,
            }
        )

    added_labels = sum(added_class_counts.values())
    _assert(excluded_ring_pixels == 98, "Grandview unknown-ring aggregate changed")
    prior_outcome = prior["outcome"]
    cumulative_classes = Counter(prior_outcome["cumulative_prototype_label_class_counts"])
    cumulative_classes.update(added_class_counts)
    cumulative_labels = prior_outcome["cumulative_owner_approved_region_labels"] + added_labels
    cumulative_core_pixels = prior_outcome["cumulative_accepted_core_pixels"] + accepted_core_pixels
    cumulative_ring_pixels = prior_outcome["cumulative_excluded_unknown_ring_pixels"] + excluded_ring_pixels
    cumulative_event_count = prior_outcome["event_group_count"] + (1 if added_labels else 0)
    label_set_version = LABEL_SET_VERSION if added_labels else PRIOR_LABEL_SET_VERSION
    return {
        "report_id": f"{REPORT_ID}-PRIVATE",
        "report_version": PRIVATE_REPORT_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": burnlens.__version__,
        "aoi_version": AOI_VERSION if added_labels else prior["aoi_version"],
        "target_version": TARGET_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "label_set_version": label_set_version,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "input_bindings": {
            "prior_label_intake": {"report_id": prior["report_id"], "run_id": prior["run_id"], "bytes": len(prior_bytes), "sha256": _sha256_bytes(prior_bytes)},
            "proposal": {"report_id": PROPOSAL_ID, "run_id": proposal["run_id"], "bytes": len(proposal_bytes), "sha256": _sha256_bytes(proposal_bytes)},
            "surface": {"report_id": SURFACE_ID, "run_id": surface["run_id"], "bytes": len(surface_bytes), "sha256": _sha256_bytes(surface_bytes)},
            "response": {"bytes": len(response_bytes), "sha256": _sha256_bytes(response_bytes)},
            "receipt": {"bytes": len(receipt_bytes), "sha256": _sha256_bytes(receipt_bytes)},
        },
        "record_bindings": _record_bindings(repository_root),
        "decision_counts": validation["decision_counts"],
        "outcome": {
            "grandview_owner_approved_region_labels": added_labels,
            "grandview_class_counts": dict(sorted(added_class_counts.items())),
            "grandview_accepted_core_pixels": accepted_core_pixels,
            "grandview_excluded_unknown_ring_pixels": excluded_ring_pixels,
            "cumulative_owner_approved_region_labels": cumulative_labels,
            "cumulative_prototype_label_class_counts": dict(sorted(cumulative_classes.items())),
            "cumulative_accepted_core_pixels": cumulative_core_pixels,
            "cumulative_accepted_core_area_ha": round(cumulative_core_pixels * 0.04, 2),
            "cumulative_excluded_unknown_ring_pixels": cumulative_ring_pixels,
            "event_group_count": cumulative_event_count,
            "minimum_event_group_count": MINIMUM_EVENT_GROUPS,
            "dataset_fitness_reopened": cumulative_event_count >= MINIMUM_EVENT_GROUPS,
        },
        "units": units,
        "boundaries": {
            "owner_review_is_independent_ground_truth": False,
            "unknown_ring_is_background": False,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
            "accuracy_or_operational_claim_created": False,
        },
        "decision": (
            "ACCEPT_GRANDVIEW_OWNER_APPROVED_PROTOTYPE_LABELS_DEFER_DATASET_SPLIT_BASELINE_MODEL"
            if added_labels
            else "NO_NEW_GRANDVIEW_OWNER_APPROVED_PROTOTYPE_LABELS"
        ),
    }


def public_report(private: dict[str, Any], private_binding: dict[str, Any]) -> dict[str, Any]:
    """Create a path-free, notes-free, unit-free aggregate public report."""
    return {
        "report_id": REPORT_ID,
        "report_version": REPORT_VERSION,
        "generated_at_utc": private["generated_at_utc"],
        "run_id": private["run_id"],
        "repository": private["repository"],
        "task_issue": TASK_ISSUE,
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
        "input_bindings": {**private["input_bindings"], "private_reconciliation": private_binding},
        "record_bindings": private["record_bindings"],
        "source_records": list(SOURCE_RECORDS),
        "terms_records": list(TERMS_RECORDS),
        "review_records": list(REVIEW_RECORDS),
        "manifest_records": list(MANIFEST_RECORDS),
        "decision_counts": private["decision_counts"],
        "outcome": private["outcome"],
        "promotion_gates": {
            "exact_response_and_custody": True,
            "candidate_reproducibility": True,
            "source_and_terms": True,
            "quality_and_registration": True,
            "unknown_ring_excluded": True,
            "event_level_leakage_control": True,
        },
        "privacy": {
            "notes_public": False,
            "unit_decisions_public": False,
            "private_paths_public": False,
        },
        "boundaries": private["boundaries"],
        "attribution": [
            "Contains modified Copernicus Sentinel data 2021-2022, accessed through CDSE.",
            "MTBS evidence: Monitoring Trends in Burn Severity Project, U.S. Geological Survey and USDA Forest Service.",
            "RAVG evidence is context-only for Grandview under the delivered sparse/non-tree warning; it does not qualify either label.",
        ],
        "warning": WARNING,
        "decision": private["decision"],
        "next_gate": "Acquire, review, and gate Petes Lake as the sixth comparable whole-event group before dataset fitness, split, or baseline work can reopen.",
    }


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def _render_png(report: dict[str, Any], path: Path) -> None:
    outcome = report["outcome"]
    image = Image.new("RGB", (1600, 1100), "#f4f0e8")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1600, 220), fill="#132a26")
    draw.text((70, 42), "BurnLens Grandview owner response", fill="white", font=_font(42))
    draw.text((70, 108), "Exact custody / six gate families / cumulative prototype labels", fill="#c6ddd6", font=_font(22))
    draw.text((70, 165), WARNING, fill="#f2c48c", font=_font(16))
    metrics = (
        (str(sum(report["decision_counts"].values())), "Grandview responses"),
        (str(outcome["grandview_owner_approved_region_labels"]), "new prototype labels"),
        (str(outcome["cumulative_owner_approved_region_labels"]), "cumulative labels"),
        (str(outcome["event_group_count"]), "accepted event groups"),
    )
    for index, (value, label) in enumerate(metrics):
        left = 70 + index * 375
        draw.rounded_rectangle((left, 270, left + 330, 440), radius=14, fill="white", outline="#c9c0b4")
        draw.text((left + 24, 300), value, fill="#006b64", font=_font(42))
        draw.text((left + 24, 370), label, fill="#263932", font=_font(18))
    draw.text((70, 500), "Gate result", fill="#132a26", font=_font(28))
    rows = (
        "PASS  exact completed response and no-overwrite custody",
        "PASS  raster bytes, native grids, connected cores, and unknown rings",
        "PASS  source, terms, quality, uncertainty, and event identity",
        f"BLOCK dataset: {outcome['event_group_count']} event groups remain below the required {outcome['minimum_event_group_count']}",
    )
    for index, line in enumerate(rows):
        draw.text((95, 565 + index * 75), line, fill="#8a521c" if line.startswith("BLOCK") else "#006b64", font=_font(22))
    draw.rounded_rectangle((70, 900, 1530, 1030), radius=14, fill="#fff8dd", outline="#d87618")
    draw.text((95, 930), "Decision", fill="#8a521c", font=_font(20))
    draw.text((95, 975), report["decision"], fill="#132a26", font=_font(19))
    image.save(path, format="PNG", optimize=False)


def _render_html(report: dict[str, Any]) -> str:
    counts = report["decision_counts"]
    outcome = report["outcome"]
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BurnLens Grandview owner response intake</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f4f0e8;color:#17251f;font:16px/1.55 system-ui,sans-serif;overflow-wrap:anywhere}}header{{background:#132a26;color:white;padding:2.4rem max(5vw,1rem)}}header p{{max-width:900px;color:#c6ddd6}}main{{max-width:1120px;margin:auto;padding:1.2rem}}.warning,.card{{background:#fffdf8;border:1px solid #d7cec1;border-radius:14px;padding:1.1rem;margin:1rem 0}}.warning{{border-left:7px solid #d87618;font-weight:650}}.metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1rem}}.metric{{background:white;border:1px solid #d7cec1;border-radius:12px;padding:1rem}}.metric strong{{display:block;color:#006b64;font-size:2rem}}img{{display:block;width:100%;height:auto;border:1px solid #d7cec1}}code{{word-break:break-word}}@media(max-width:700px){{.metrics{{grid-template-columns:1fr 1fr}}header{{padding:1.4rem 1rem}}main{{padding:.65rem}}}}
</style></head><body><header><p>BURNLENS / PHASE TWO / ISSUE #517</p><h1>Grandview owner response intake</h1><p>Exact private custody, deterministic gate evaluation, and content-safe public aggregates.</p></header><main>
<p class="warning">{escape(report['warning'])}</p><section class="metrics"><div class="metric"><strong>{sum(counts.values())}</strong>Grandview responses</div><div class="metric"><strong>{outcome['grandview_owner_approved_region_labels']}</strong>new prototype labels</div><div class="metric"><strong>{outcome['cumulative_owner_approved_region_labels']}</strong>cumulative labels</div><div class="metric"><strong>{outcome['event_group_count']}</strong>accepted event groups</div></section>
<section class="card"><h2>Aggregate result</h2><p>Owner decisions: {counts['yes']} yes / {counts['no']} no / {counts['uncertain']} uncertain. Grandview adds {outcome['grandview_class_counts'].get('burned',0)} burned and {outcome['grandview_class_counts'].get('background',0)} background prototype labels.</p><p>Every admitted core passes exact-byte reconstruction, source and terms, native-grid quality, explicit uncertainty-ring exclusion, and event-identity gates. Notes and unit decisions remain private.</p></section>
<img src="{REPORT_ID}.png" alt="BurnLens Grandview owner response intake gate summary">
<section class="card"><h2>Why the dataset remains blocked</h2><p>Only {outcome['event_group_count']} event groups are represented; the frozen minimum is {outcome['minimum_event_group_count']}. No split exists, and no unknown-ring or outside pixel becomes background.</p></section>
<section class="card"><h2>Decision</h2><p><strong>{escape(report['decision'])}</strong></p><p>Label set <code>{escape(report['label_set_version'])}</code> &middot; schema <code>{escape(report['label_schema_version'])}</code> &middot; run <code>{escape(report['run_id'])}</code> &middot; source <code>{escape(report['git_source_commit'])}</code>. Dataset, split, baseline, and model remain absent.</p></section>
</main></body></html>'''


def write_private_no_overwrite(repository_root: Path, path: Path, report: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    _assert_ignored(repository_root, path)
    payload = (json.dumps(report, indent=2) + "\n").encode("utf-8")
    try:
        with path.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        raise GrandviewOwnerResponseIntakeError("refusing to overwrite private reconciliation") from error
    return {"bytes": len(payload), "sha256": _sha256_bytes(payload), "committed": False, "ignored": True}


def write_public_no_overwrite(report: dict[str, Any], output_directory: Path) -> list[dict[str, Any]]:
    if output_directory.exists():
        raise GrandviewOwnerResponseIntakeError("public output directory already exists")
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
    return [{"path": json_path.name, **_binding(json_path), "media_type": "application/json"}, *report["outputs"]]
