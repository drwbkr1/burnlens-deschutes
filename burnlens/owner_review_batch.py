"""Prospective manifest-driven batching for BurnLens owner-review surfaces.

This module intentionally does not replace any shipped review generator.  It
defines the reusable contract that a later event-specific adapter can populate
only after that event's proposal and evidence gates pass.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import datetime
from hashlib import sha256
from html import escape
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any

import burnlens


MANIFEST_SCHEMA_VERSION = "burnlens-owner-review-batch-manifest-v0.1.0"
REGISTRY_SCHEMA_VERSION = "burnlens-owner-review-batch-registry-v0.1.0"
SURFACE_VERSION = "owner-review-batch-surface-v0.1.0"
RESPONSE_SCHEMA_VERSION = "burnlens-owner-review-batch-response-v0.1.0"
REVIEW_PROTOCOL_VERSION = "owner-confirmed-prototype-label-review-v0.2.0"
DEFAULT_BATCH_MIN = 4
DEFAULT_BATCH_MAX = 6
HARD_BATCH_MAX = 8
ALLOWED_DECISIONS = ("yes", "no", "uncertain")
ALLOWED_CLASSES = ("burned", "background")
WARNING = (
    "Experimental BurnLens candidate review. Not ground truth, a dataset, "
    "official wildfire information, or emergency guidance. Official sources govern."
)

_TOP_LEVEL_KEYS = {
    "manifest_schema_version",
    "surface_id",
    "surface_revision",
    "surface_run_id",
    "milestone_id",
    "task_issue",
    "generated_at_utc",
    "git_source_commit",
    "title",
    "review_groups",
    "candidates",
    "batch_size_exception",
    "supersedes_surface_id",
}
_GROUP_KEYS = {"event_group_id", "event_label", "context", "candidate_ids"}
_CANDIDATE_KEYS = {
    "candidate_id",
    "event_group_id",
    "proposed_class",
    "question",
    "proposition_basis",
    "limitations",
    "facts",
    "proposal_binding",
    "candidate_raster_binding",
    "evidence_images",
}
_CANDIDATE_DERIVED_KEYS = _CANDIDATE_KEYS | {"candidate_binding_sha256"}
_RESPONSE_KEYS = {
    "response_schema_version",
    "surface_id",
    "surface_run_id",
    "surface_revision",
    "milestone_id",
    "ordered_manifest_sha256",
    "completed",
    "review_started_at_utc",
    "review_completed_at_utc",
    "owner",
    "responses",
}
_RESPONSE_ITEM_KEYS = {
    "candidate_id",
    "event_group_id",
    "candidate_binding_sha256",
    "decision",
    "notes",
}
_HEX_64 = re.compile(r"^[0-9a-f]{64}$")
_HEX_40 = re.compile(r"^[0-9a-f]{40}$")
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{1,127}$")


class OwnerReviewBatchError(RuntimeError):
    """Raised when a prospective batch violates its frozen contract."""


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise OwnerReviewBatchError(message)


def _exact_keys(value: dict[str, Any], expected: set[str], name: str) -> None:
    _assert(set(value) == expected, f"{name} fields changed")


def _text(value: Any, name: str, *, maximum: int = 2_000) -> str:
    _assert(isinstance(value, str) and value.strip() == value and 0 < len(value) <= maximum, f"{name} is invalid")
    return value


def _identifier(value: Any, name: str) -> str:
    value = _text(value, name, maximum=128)
    _assert(_ID.fullmatch(value) is not None, f"{name} is invalid")
    return value


def _timestamp(value: Any, name: str) -> datetime:
    _assert(isinstance(value, str), f"{name} is not a timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise OwnerReviewBatchError(f"{name} is invalid") from error
    _assert(parsed.tzinfo is not None, f"{name} lacks timezone")
    return parsed


def _hash(value: Any, name: str) -> str:
    _assert(isinstance(value, str) and _HEX_64.fullmatch(value) is not None, f"{name} is not a lowercase SHA-256")
    return value


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def _canonical_sha256(value: Any) -> str:
    return sha256(_canonical_bytes(value)).hexdigest()


def _safe_relative_path(value: Any, name: str) -> str:
    value = _text(value, name, maximum=240)
    _assert("\\" not in value, f"{name} must use forward slashes")
    path = PurePosixPath(value)
    _assert(not path.is_absolute() and ".." not in path.parts and "." not in path.parts, f"{name} is unsafe")
    _assert(path.as_posix() == value, f"{name} is not canonical")
    reserved = {"CON", "PRN", "AUX", "NUL", *{f"COM{index}" for index in range(1, 10)}, *{f"LPT{index}" for index in range(1, 10)}}
    for part in path.parts:
        _assert(part == part.strip() and not part.endswith("."), f"{name} has a non-portable segment")
        _assert(not any(character in '<>:"|?*#%' or ord(character) < 32 for character in part), f"{name} has a non-portable segment")
        _assert(part.split(".", 1)[0].upper() not in reserved, f"{name} has a reserved segment")
    return value


def _validate_batch_size_exception(count: int, size_exception: Any) -> str | None:
    if DEFAULT_BATCH_MIN <= count <= DEFAULT_BATCH_MAX:
        _assert(size_exception is None, "normal 4-6 candidate batches do not use a size exception")
        return None
    _assert(isinstance(size_exception, str), "non-default batch size requires an explicit exception")
    reason = _text(size_exception, "batch size exception", maximum=300)
    if count == 2:
        _assert(reason == "single-event-pair", "two-candidate batches require the single-event-pair exception")
    return reason


def _file_binding(value: Any, name: str, *, require_path: bool = True) -> dict[str, Any]:
    _assert(isinstance(value, dict), f"{name} is not an object")
    expected = {"path", "bytes", "sha256"} if require_path else {"record_id", "bytes", "sha256"}
    _exact_keys(value, expected, name)
    if require_path:
        _safe_relative_path(value["path"], f"{name} path")
    else:
        _identifier(value["record_id"], f"{name} record ID")
    _assert(isinstance(value["bytes"], int) and not isinstance(value["bytes"], bool) and value["bytes"] > 0, f"{name} byte count is invalid")
    _hash(value["sha256"], f"{name} SHA-256")
    return value


def _validate_candidate(candidate: Any, index: int) -> dict[str, Any]:
    name = f"candidate {index}"
    _assert(isinstance(candidate, dict), f"{name} is not an object")
    _assert(set(candidate) in (_CANDIDATE_KEYS, _CANDIDATE_DERIVED_KEYS), f"{name} fields changed")
    _identifier(candidate["candidate_id"], f"{name} ID")
    _identifier(candidate["event_group_id"], f"{name} event group")
    _assert(candidate["proposed_class"] in ALLOWED_CLASSES, f"{name} proposed class is invalid")
    _text(candidate["question"], f"{name} question", maximum=300)
    _text(candidate["proposition_basis"], f"{name} proposition basis", maximum=2_000)
    limitations = candidate["limitations"]
    _assert(isinstance(limitations, list) and 1 <= len(limitations) <= 20, f"{name} limitations are invalid")
    for limitation in limitations:
        _text(limitation, f"{name} limitation", maximum=1_000)
    facts = candidate["facts"]
    _assert(isinstance(facts, list) and 1 <= len(facts) <= 20, f"{name} facts are invalid")
    for fact in facts:
        _assert(isinstance(fact, dict), f"{name} fact is not an object")
        _exact_keys(fact, {"label", "value"}, f"{name} fact")
        _text(fact["label"], f"{name} fact label", maximum=100)
        _text(fact["value"], f"{name} fact value", maximum=500)
    _file_binding(candidate["proposal_binding"], f"{name} proposal", require_path=False)
    _file_binding(candidate["candidate_raster_binding"], f"{name} raster")
    evidence = candidate["evidence_images"]
    _assert(isinstance(evidence, list) and 1 <= len(evidence) <= 8, f"{name} evidence images are invalid")
    for item in evidence:
        _assert(isinstance(item, dict), f"{name} evidence image is not an object")
        _exact_keys(item, {"path", "bytes", "sha256", "alt"}, f"{name} evidence image")
        _safe_relative_path(item["path"], f"{name} evidence path")
        _assert(isinstance(item["bytes"], int) and not isinstance(item["bytes"], bool) and item["bytes"] > 0, f"{name} evidence byte count is invalid")
        _hash(item["sha256"], f"{name} evidence SHA-256")
        _text(item["alt"], f"{name} evidence alternative text", maximum=500)
        _assert(PurePosixPath(item["path"]).suffix.lower() == ".png", f"{name} evidence image must be PNG")
    if "candidate_binding_sha256" in candidate:
        _hash(candidate["candidate_binding_sha256"], f"{name} candidate binding SHA-256")
    return candidate


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize one frozen, ordered owner-review batch manifest."""
    _assert(isinstance(manifest, dict), "batch manifest is not an object")
    try:
        value = deepcopy(json.loads(json.dumps(manifest)))
    except (TypeError, ValueError) as error:
        raise OwnerReviewBatchError("batch manifest is not JSON-compatible") from error
    _exact_keys(value, _TOP_LEVEL_KEYS, "batch manifest")
    _assert(value["manifest_schema_version"] == MANIFEST_SCHEMA_VERSION, "batch manifest schema mismatch")
    _identifier(value["surface_id"], "surface ID")
    _assert(isinstance(value["surface_revision"], int) and not isinstance(value["surface_revision"], bool) and value["surface_revision"] >= 1, "surface revision is invalid")
    _identifier(value["surface_run_id"], "surface run ID")
    _identifier(value["milestone_id"], "milestone ID")
    _assert(isinstance(value["task_issue"], int) and not isinstance(value["task_issue"], bool) and value["task_issue"] > 0, "task issue is invalid")
    _timestamp(value["generated_at_utc"], "generated time")
    _assert(isinstance(value["git_source_commit"], str) and _HEX_40.fullmatch(value["git_source_commit"]) is not None, "git source commit must be a full lowercase SHA")
    _text(value["title"], "surface title", maximum=160)
    supersedes = value["supersedes_surface_id"]
    _assert(supersedes is None or _ID.fullmatch(_text(supersedes, "superseded surface ID", maximum=128)) is not None, "superseded surface ID is invalid")
    if value["surface_revision"] == 1:
        _assert(supersedes is None, "first surface revision cannot supersede another surface")
    else:
        _assert(supersedes is not None, "later surface revision must identify the superseded surface")

    groups = value["review_groups"]
    candidates = value["candidates"]
    _assert(isinstance(groups, list) and groups, "review groups are empty")
    _assert(isinstance(candidates, list) and 1 <= len(candidates) <= HARD_BATCH_MAX, f"candidate count must be between 1 and {HARD_BATCH_MAX}")
    candidate_ids: list[str] = []
    event_ids: set[str] = set()
    evidence_paths: set[str] = set()
    for index, candidate in enumerate(candidates, start=1):
        _validate_candidate(candidate, index)
        candidate_id = candidate["candidate_id"]
        _assert(candidate_id not in candidate_ids, "duplicate candidate ID")
        candidate_ids.append(candidate_id)
        for evidence in candidate["evidence_images"]:
            path_key = evidence["path"].casefold()
            _assert(path_key not in evidence_paths, "evidence output path is reused")
            evidence_paths.add(path_key)
        binding_payload = {key: candidate[key] for key in _CANDIDATE_KEYS}
        expected_candidate_binding = _canonical_sha256(binding_payload)
        if "candidate_binding_sha256" in candidate:
            _assert(
                candidate["candidate_binding_sha256"] == expected_candidate_binding,
                f"candidate {index} derived binding changed",
            )
        candidate["candidate_binding_sha256"] = expected_candidate_binding

    flattened: list[str] = []
    candidate_lookup = {candidate["candidate_id"]: candidate for candidate in candidates}
    for index, group in enumerate(groups, start=1):
        _assert(isinstance(group, dict), f"review group {index} is not an object")
        _exact_keys(group, _GROUP_KEYS, f"review group {index}")
        event_id = _identifier(group["event_group_id"], f"review group {index} event ID")
        _assert(event_id not in event_ids, "duplicate event group")
        event_ids.add(event_id)
        _text(group["event_label"], f"review group {index} label", maximum=160)
        _text(group["context"], f"review group {index} context", maximum=1_500)
        members = group["candidate_ids"]
        _assert(isinstance(members, list) and members, f"review group {index} has no candidates")
        for candidate_id in members:
            _identifier(candidate_id, f"review group {index} candidate ID")
            _assert(candidate_id in candidate_lookup, "review group references an unknown candidate")
            _assert(candidate_lookup[candidate_id]["event_group_id"] == event_id, "candidate event group binding changed")
        flattened.extend(members)
    _assert(flattened == candidate_ids, "candidate order must exactly match contiguous review-group order")
    _assert(len(flattened) == len(set(flattened)), "candidate appears in more than one review group")

    count = len(candidates)
    size_exception = _validate_batch_size_exception(count, value["batch_size_exception"])
    if size_exception == "single-event-pair":
        _assert(count == 2 and len(groups) == 1, "single-event-pair requires exactly one two-candidate group")
        _assert({candidate["proposed_class"] for candidate in candidates} == set(ALLOWED_CLASSES), "single-event-pair requires one burned and one background proposal")
    return value


def build_surface(manifest: dict[str, Any]) -> dict[str, Any]:
    """Build a blank report contract from a validated manifest; collect no response."""
    normalized = validate_manifest(manifest)
    ordered_manifest_sha256 = _canonical_sha256(normalized)
    return {
        "report_id": normalized["surface_id"],
        "report_version": SURFACE_VERSION,
        "response_schema_version": RESPONSE_SCHEMA_VERSION,
        "review_protocol_version": REVIEW_PROTOCOL_VERSION,
        "surface_revision": normalized["surface_revision"],
        "generated_at_utc": normalized["generated_at_utc"],
        "run_id": normalized["surface_run_id"],
        "milestone_id": normalized["milestone_id"],
        "task_issue": normalized["task_issue"],
        "git_source_commit": normalized["git_source_commit"],
        "software_version": burnlens.__version__,
        "ordered_manifest_sha256": ordered_manifest_sha256,
        "batch_manifest": normalized,
        "review_groups": normalized["review_groups"],
        "candidates": normalized["candidates"],
        "batch_policy": {
            "default_minimum_candidates": DEFAULT_BATCH_MIN,
            "default_maximum_candidates": DEFAULT_BATCH_MAX,
            "hard_maximum_candidates": HARD_BATCH_MAX,
            "single_event_pair_exception": "single-event-pair",
            "bulk_approval_allowed": False,
            "prefilled_decisions_allowed": False,
            "missing_decision_means_uncertain": False,
        },
        "decision_contract": {
            "yes": "owner supports the disclosed proposed class; every non-owner gate remains mandatory",
            "no": "owner rejects this proposal; no opposite class is inferred",
            "uncertain": "evidence is insufficient or conflicting; the candidate remains excluded",
            "prior_decisions_inherited": False,
        },
        "response_custody_contract": {
            "hash_named_drafts": True,
            "all_candidates_required_for_completion": True,
            "one_batch_attestation_required": True,
            "final_review_summary_required": True,
            "hash_named_exact_response": True,
            "browser_session_locks_after_finalization": True,
            "distinct_completed_exports_require_owner_designation": True,
        },
        "summary": {
            "candidate_count": len(normalized["candidates"]),
            "event_group_count": len(normalized["review_groups"]),
            "owner_responses": 0,
            "labels_created": 0,
        },
        "claim_boundaries": {
            "owner_response_collected": False,
            "label_created": False,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
            "independent_ground_truth_inter_rater_field_official_or_operational_claimed": False,
        },
        "warning": WARNING,
        "decision": "BATCH_SURFACE_CONTRACT_READY_KEEP_OWNER_RESPONSE_AND_PROMOTION_SEPARATE",
    }


def response_template(surface: dict[str, Any]) -> dict[str, Any]:
    """Return the exact blank response envelope bound to one surface manifest."""
    return {
        "response_schema_version": RESPONSE_SCHEMA_VERSION,
        "surface_id": surface["report_id"],
        "surface_run_id": surface["run_id"],
        "surface_revision": surface["surface_revision"],
        "milestone_id": surface["milestone_id"],
        "ordered_manifest_sha256": surface["ordered_manifest_sha256"],
        "completed": False,
        "review_started_at_utc": None,
        "review_completed_at_utc": None,
        "owner": {"attestation": False},
        "responses": [
            {
                "candidate_id": candidate["candidate_id"],
                "event_group_id": candidate["event_group_id"],
                "candidate_binding_sha256": candidate["candidate_binding_sha256"],
                "decision": None,
                "notes": "",
            }
            for candidate in surface["candidates"]
        ],
    }


def validate_response(surface: dict[str, Any], response: dict[str, Any], *, require_completed: bool) -> dict[str, Any]:
    """Validate a bound draft or completed response, including decision values."""
    _assert(isinstance(response, dict), "response is not an object")
    _exact_keys(response, _RESPONSE_KEYS, "response")
    expected = {
        "response_schema_version": surface["response_schema_version"],
        "surface_id": surface["report_id"],
        "surface_run_id": surface["run_id"],
        "surface_revision": surface["surface_revision"],
        "milestone_id": surface["milestone_id"],
        "ordered_manifest_sha256": surface["ordered_manifest_sha256"],
    }
    for key, expected_value in expected.items():
        if key == "surface_revision":
            _assert(
                isinstance(response[key], int)
                and not isinstance(response[key], bool)
                and response[key] >= 1,
                "response surface revision is invalid",
            )
        _assert(response[key] == expected_value, f"response binding mismatch: {key}")
    _assert(isinstance(response["completed"], bool), "response completion flag is invalid")
    if require_completed:
        _assert(response["completed"] is True, "response is incomplete")
    owner = response["owner"]
    _assert(isinstance(owner, dict), "owner attestation is not an object")
    _exact_keys(owner, {"attestation"}, "owner attestation")
    _assert(isinstance(owner["attestation"], bool), "owner attestation is invalid")
    started_value = response["review_started_at_utc"]
    completed_value = response["review_completed_at_utc"]
    started = None if started_value is None else _timestamp(started_value, "review start")
    completed = None if completed_value is None else _timestamp(completed_value, "review completion")
    if response["completed"]:
        _assert(owner["attestation"] is True, "owner attestation is incomplete")
        _assert(started is not None and completed is not None, "completed response requires both timestamps")
        _assert(completed >= started, "review completion predates start")
    else:
        _assert(completed is None, "draft response cannot have a completion timestamp")

    items = response["responses"]
    candidates = surface["candidates"]
    _assert(isinstance(items, list) and len(items) == len(candidates), "response roster length changed")
    counts = Counter({decision: 0 for decision in ALLOWED_DECISIONS})
    seen: set[str] = set()
    answered = 0
    for candidate, item in zip(candidates, items, strict=True):
        _assert(isinstance(item, dict), "response item is not an object")
        _exact_keys(item, _RESPONSE_ITEM_KEYS, "response item")
        candidate_id = item["candidate_id"]
        _assert(candidate_id not in seen, "duplicate candidate response")
        seen.add(candidate_id)
        _assert(candidate_id == candidate["candidate_id"], "candidate order or identity changed")
        _assert(item["event_group_id"] == candidate["event_group_id"], "candidate event binding changed")
        _assert(item["candidate_binding_sha256"] == candidate["candidate_binding_sha256"], "candidate binding changed")
        decision = item["decision"]
        _assert(decision is None or decision in ALLOWED_DECISIONS, "decision is outside yes/no/uncertain")
        if decision is not None:
            counts[decision] += 1
            answered += 1
        _assert(isinstance(item["notes"], str) and len(item["notes"]) <= 1_000, "response notes violate the bounded string contract")
    if response["completed"]:
        _assert(answered == len(candidates), "completed response is missing a candidate decision")
    return {
        "completed": response["completed"],
        "answered_count": answered,
        "decision_counts": {decision: counts[decision] for decision in ALLOWED_DECISIONS},
        "started_at_utc": started_value,
        "completed_at_utc": completed_value,
        "candidate_bindings": [
            {
                "candidate_id": item["candidate_id"],
                "event_group_id": item["event_group_id"],
                "candidate_binding_sha256": item["candidate_binding_sha256"],
            }
            for item in items
        ],
    }


def validate_completed_response(surface: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    """Fully validate a completed response after exact-byte custody succeeds."""
    return validate_response(surface, response, require_completed=True)


def _reconstruct_surface(surface: dict[str, Any]) -> dict[str, Any]:
    _assert(isinstance(surface, dict), "surface is not an object")
    rebuilt = build_surface(surface.get("batch_manifest"))
    _assert(set(surface) == set(rebuilt), "surface fields changed")
    _assert(surface == rebuilt, "surface does not reconstruct from its frozen manifest")
    return rebuilt


def registry_entry(surface: dict[str, Any], *, state: str = "active") -> dict[str, Any]:
    surface = _reconstruct_surface(surface)
    _assert(state in {"draft", "active", "completed", "superseded", "rejected"}, "registry state is invalid")
    return {
        "surface_id": surface["report_id"],
        "surface_revision": surface["surface_revision"],
        "milestone_id": surface["milestone_id"],
        "ordered_manifest_sha256": surface["ordered_manifest_sha256"],
        "candidate_ids": [candidate["candidate_id"] for candidate in surface["candidates"]],
        "candidate_count": len(surface["candidates"]),
        "batch_size_exception": surface["batch_manifest"]["batch_size_exception"],
        "state": state,
        "supersedes_surface_id": surface["batch_manifest"]["supersedes_surface_id"],
    }


def validate_registry(registry: dict[str, Any]) -> dict[str, Any]:
    """Reject duplicate revisions and candidate membership in active surfaces."""
    _assert(isinstance(registry, dict), "batch registry is not an object")
    _exact_keys(registry, {"registry_schema_version", "entries"}, "batch registry")
    _assert(registry["registry_schema_version"] == REGISTRY_SCHEMA_VERSION, "batch registry schema mismatch")
    entries = registry["entries"]
    _assert(isinstance(entries, list), "batch registry entries are invalid")
    normalized = deepcopy(registry)
    seen_revisions: set[tuple[str, int]] = set()
    prior_entries: dict[tuple[str, int], dict[str, Any]] = {}
    superseded_predecessors: set[tuple[str, int]] = set()
    active_candidates: dict[str, str] = {}
    allowed_states = {"draft", "active", "completed", "superseded", "rejected"}
    for index, entry in enumerate(normalized["entries"], start=1):
        _assert(isinstance(entry, dict), f"registry entry {index} is not an object")
        _exact_keys(
            entry,
            {"surface_id", "surface_revision", "milestone_id", "ordered_manifest_sha256", "candidate_ids", "candidate_count", "batch_size_exception", "state", "supersedes_surface_id"},
            f"registry entry {index}",
        )
        surface_id = _identifier(entry["surface_id"], f"registry entry {index} surface ID")
        _assert(
            isinstance(entry["surface_revision"], int)
            and not isinstance(entry["surface_revision"], bool)
            and entry["surface_revision"] >= 1,
            f"registry entry {index} revision is invalid",
        )
        revision_key = (surface_id, entry["surface_revision"])
        _assert(revision_key not in seen_revisions, "surface revision is already registered")
        seen_revisions.add(revision_key)
        _identifier(entry["milestone_id"], f"registry entry {index} milestone ID")
        _hash(entry["ordered_manifest_sha256"], f"registry entry {index} manifest SHA-256")
        _assert(entry["state"] in allowed_states, f"registry entry {index} state is invalid")
        _assert(isinstance(entry["candidate_ids"], list) and entry["candidate_ids"], f"registry entry {index} has no candidates")
        _assert(len(entry["candidate_ids"]) == len(set(entry["candidate_ids"])), f"registry entry {index} repeats a candidate")
        candidate_count = entry["candidate_count"]
        _assert(
            isinstance(candidate_count, int)
            and not isinstance(candidate_count, bool)
            and candidate_count == len(entry["candidate_ids"])
            and 1 <= candidate_count <= HARD_BATCH_MAX,
            f"registry entry {index} candidate count is invalid",
        )
        _validate_batch_size_exception(candidate_count, entry["batch_size_exception"])
        for candidate_id in entry["candidate_ids"]:
            _identifier(candidate_id, f"registry entry {index} candidate ID")
            if entry["state"] == "active":
                _assert(candidate_id not in active_candidates, f"candidate {candidate_id} appears in two active surfaces")
                active_candidates[candidate_id] = surface_id
        supersedes = entry["supersedes_surface_id"]
        _assert(
            supersedes is None or _ID.fullmatch(_text(supersedes, f"registry entry {index} supersedes field", maximum=128)) is not None,
            f"registry entry {index} supersedes field is invalid",
        )
        if entry["surface_revision"] == 1:
            _assert(supersedes is None, f"registry entry {index} first revision cannot supersede another surface")
        else:
            _assert(supersedes is not None, f"registry entry {index} later revision lacks a predecessor")
            predecessor_key = (supersedes, entry["surface_revision"] - 1)
            _assert(predecessor_key in prior_entries, f"registry entry {index} predecessor is not registered")
            predecessor = prior_entries[predecessor_key]
            _assert(predecessor["milestone_id"] == entry["milestone_id"], f"registry entry {index} predecessor milestone changed")
            _assert(predecessor_key not in superseded_predecessors, f"registry entry {index} predecessor already has a successor")
            if entry["state"] in {"active", "completed"}:
                _assert(predecessor["state"] == "superseded", f"registry entry {index} active revision requires a superseded predecessor")
            superseded_predecessors.add(predecessor_key)
        prior_entries[revision_key] = entry
    return normalized


def add_registry_entry(registry: dict[str, Any], surface: dict[str, Any], *, state: str = "active") -> dict[str, Any]:
    value = validate_registry(registry)
    value["entries"].append(registry_entry(surface, state=state))
    return validate_registry(value)


def _binding(path: Path, base: Path, **extra: Any) -> dict[str, Any]:
    data = path.read_bytes()
    value = {"path": path.relative_to(base).as_posix(), "bytes": len(data), "sha256": sha256(data).hexdigest()}
    value.update(extra)
    return value


def _write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with path.open("xb") as handle:
            created = True
            handle.write(data)
    except FileExistsError as error:
        raise OwnerReviewBatchError(f"refusing to overwrite {path.name}") from error
    except Exception:
        if created:
            path.unlink(missing_ok=True)
        raise


def _rollback_surface_output(output_directory: Path, created_paths: list[Path]) -> None:
    failures: list[str] = []
    for path in reversed(created_paths):
        try:
            path.unlink(missing_ok=True)
        except OSError:
            failures.append(path.name)
    directories = {output_directory}
    for path in created_paths:
        parent = path.parent
        while parent != output_directory:
            directories.add(parent)
            parent = parent.parent
    for directory in sorted(directories, key=lambda value: len(value.parts), reverse=True):
        try:
            directory.rmdir()
        except FileNotFoundError:
            pass
        except OSError:
            failures.append(directory.name)
    if failures:
        raise OwnerReviewBatchError(f"failed to roll back partial surface output: {', '.join(failures)}")


def _render_html(surface: dict[str, Any], template: dict[str, Any]) -> str:
    groups = {group["event_group_id"]: group for group in surface["review_groups"]}
    cards: list[str] = []
    for index, candidate in enumerate(surface["candidates"]):
        group = groups[candidate["event_group_id"]]
        choices = "".join(
            f'<label><input type="radio" name="decision-{escape(candidate["candidate_id"])}" value="{decision}"> {decision}</label>'
            for decision in ALLOWED_DECISIONS
        )
        facts = "".join(f'<dt>{escape(item["label"])}</dt><dd>{escape(item["value"])}</dd>' for item in candidate["facts"])
        limitations = "".join(f"<li>{escape(item)}</li>" for item in candidate["limitations"])
        images = "".join(
            f'<div class="evidence-scroll" tabindex="0"><img src="{escape(item["path"])}" alt="{escape(item["alt"])}"></div>'
            for item in candidate["evidence_images"]
        )
        hidden = "" if index == 0 else " hidden"
        cards.append(
            f'''<article class="candidate" data-index="{index}" data-candidate="{escape(candidate['candidate_id'])}" data-event-group="{escape(candidate['event_group_id'])}" data-binding="{candidate['candidate_binding_sha256']}"{hidden}>
<p class="eyebrow">{escape(group['event_label'])} / {escape(candidate['candidate_id'])}</p>
<h2>{escape(candidate['question'])}</h2>
<p class="proposal"><strong>Proposed class:</strong> {escape(candidate['proposed_class'])}</p>
<p>{escape(group['context'])}</p><p><strong>Why proposed:</strong> {escape(candidate['proposition_basis'])}</p>
<dl>{facts}</dl><h3>Limitations</h3><ul>{limitations}</ul>{images}
<p class="micro">Candidate binding SHA-256 <code>{candidate['candidate_binding_sha256']}</code>. The proposal is disclosed evidence, not truth.</p>
<fieldset><legend>Owner decision for this candidate</legend><div class="choices">{choices}</div><label class="notes">Optional notes<textarea data-notes maxlength="1000"></textarea></label></fieldset>
</article>'''
        )
    embedded = json.dumps(template, ensure_ascii=False).replace("</", "<\\/")
    script = r'''
const TEMPLATE=JSON.parse(document.getElementById('response-template').textContent);
const ALLOWED=new Set(['yes','no','uncertain']);const cards=[...document.querySelectorAll('[data-candidate]')];
const status=document.getElementById('status');const finalPanel=document.getElementById('final-review');
const finalList=document.getElementById('final-list');const confirmExport=document.getElementById('confirm-export');
let activeIndex=0;let startedAt=null;let completedAt=null;let summaryReady=false;
function exactKeys(value,keys){return value&&typeof value==='object'&&!Array.isArray(value)&&Object.keys(value).sort().join('|')===[...keys].sort().join('|')}
function decision(card){return card.querySelector('input[type=radio]:checked')?.value??null}
function show(index,scroll=true){activeIndex=Math.max(0,Math.min(cards.length-1,index));cards.forEach((card,i)=>card.hidden=i!==activeIndex);document.getElementById('position').textContent=`Candidate ${activeIndex+1} of ${cards.length}`;document.getElementById('previous').disabled=activeIndex===0;document.getElementById('next').disabled=activeIndex===cards.length-1;if(scroll)cards[activeIndex].scrollIntoView({behavior:'smooth',block:'start'})}
function firstUnanswered(){const index=cards.findIndex(card=>!decision(card));show(index<0?0:index)}
function invalidateSummary(){summaryReady=false;finalPanel.hidden=true;confirmExport.disabled=true}
function update(event){const count=cards.filter(card=>decision(card)).length;document.getElementById('progress').textContent=`${count} of ${cards.length} decisions`;if(event?.target?.matches('input[type=radio],textarea,#attestation'))invalidateSummary();if(count&&!startedAt)startedAt=new Date().toISOString()}
function payload(completed){return {...TEMPLATE,completed,review_started_at_utc:startedAt,review_completed_at_utc:completed?completedAt:null,owner:{attestation:document.getElementById('attestation').checked},responses:cards.map(card=>({candidate_id:card.dataset.candidate,event_group_id:card.dataset.eventGroup,candidate_binding_sha256:card.dataset.binding,decision:decision(card),notes:card.querySelector('[data-notes]').value}))}}
function validateComplete(focus){document.querySelectorAll('.invalid').forEach(value=>value.classList.remove('invalid'));const missing=cards.find(card=>!decision(card));if(missing){missing.classList.add('invalid');status.textContent=' Every candidate requires an explicit yes, no, or uncertain decision.';if(focus)show(cards.indexOf(missing));return false}if(!document.getElementById('attestation').checked){status.textContent=' Final owner attestation is required.';return false}if(!startedAt)startedAt=new Date().toISOString();return true}
function renderSummary(){finalList.replaceChildren(...cards.map(card=>{const item=document.createElement('li');item.textContent=`${card.dataset.candidate}: ${decision(card)}`;return item}));finalPanel.hidden=false;summaryReady=true;confirmExport.disabled=false;status.textContent=' Review the candidate-level summary, then export and lock.'}
async function digest(bytes){const value=await crypto.subtle.digest('SHA-256',bytes);return [...new Uint8Array(value)].map(item=>item.toString(16).padStart(2,'0')).join('')}
async function download(value,kind){const bytes=new TextEncoder().encode(JSON.stringify(value,null,2)+'\n');const hash=await digest(bytes);const link=document.createElement('a');link.href=URL.createObjectURL(new Blob([bytes],{type:'application/json'}));link.download=`${TEMPLATE.surface_id}-${kind}-${hash.slice(0,16)}.json`;link.click();setTimeout(()=>URL.revokeObjectURL(link.href),1000);status.textContent=` Exact ${kind.toLowerCase()} bytes prepared; SHA-256 ${hash}.`}
function lock(){document.querySelectorAll('input[type=radio],textarea,#attestation,#save-draft,#load-response,#review-final,#confirm-export').forEach(value=>value.disabled=true);document.getElementById('previous').disabled=true;document.getElementById('next').disabled=true;document.getElementById('resume').disabled=true;status.textContent+=' Response is locked in this browser session.'}
function zonedTime(value){const match=typeof value==='string'&&value.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d{1,6})?(Z|[+-](\d{2}):(\d{2}))$/);if(!match)return NaN;const year=Number(match[1]),month=Number(match[2]),day=Number(match[3]),hour=Number(match[4]),minute=Number(match[5]),second=Number(match[6]);const leap=year%4===0&&(year%100!==0||year%400===0);const monthDays=[0,31,leap?29:28,31,30,31,30,31,31,30,31,30,31];if(year<1||month<1||month>12||day<1||day>monthDays[month]||hour>23||minute>59||second>59)return NaN;if(match[7]!=='Z'&&(Number(match[8])>23||Number(match[9])>59))return NaN;return Date.parse(value)}
function validCompletionOrder(started,completed){const startTime=zonedTime(started),completionTime=zonedTime(completed);return Number.isFinite(startTime)&&Number.isFinite(completionTime)&&completionTime>=startTime}
function validateLoaded(value){const rootKeys=['response_schema_version','surface_id','surface_run_id','surface_revision','milestone_id','ordered_manifest_sha256','completed','review_started_at_utc','review_completed_at_utc','owner','responses'];if(!exactKeys(value,rootKeys))throw new Error('response fields changed');for(const key of ['response_schema_version','surface_id','surface_run_id','surface_revision','milestone_id','ordered_manifest_sha256'])if(value[key]!==TEMPLATE[key])throw new Error(`binding mismatch: ${key}`);if(typeof value.completed!=='boolean'||!exactKeys(value.owner,['attestation'])||typeof value.owner.attestation!=='boolean'||!Array.isArray(value.responses)||value.responses.length!==cards.length)throw new Error('response envelope changed');value.responses.forEach((item,index)=>{const card=cards[index];if(!exactKeys(item,['candidate_id','event_group_id','candidate_binding_sha256','decision','notes'])||item.candidate_id!==card.dataset.candidate||item.event_group_id!==card.dataset.eventGroup||item.candidate_binding_sha256!==card.dataset.binding||!(item.decision===null||ALLOWED.has(item.decision))||typeof item.notes!=='string'||item.notes.length>1000)throw new Error('candidate binding or response changed')});const started=value.review_started_at_utc===null?null:zonedTime(value.review_started_at_utc);if(value.completed){if(!value.owner.attestation||!validCompletionOrder(value.review_started_at_utc,value.review_completed_at_utc)||value.responses.some(item=>!ALLOWED.has(item.decision)))throw new Error('completed response is incomplete')}else if(value.review_completed_at_utc!==null||(started!==null&&!Number.isFinite(started)))throw new Error('draft timestamps are invalid')}
document.addEventListener('change',update);document.addEventListener('input',update);
document.getElementById('previous').addEventListener('click',()=>show(activeIndex-1));document.getElementById('next').addEventListener('click',()=>show(activeIndex+1));document.getElementById('resume').addEventListener('click',firstUnanswered);
document.getElementById('save-draft').addEventListener('click',()=>download(payload(false),'DRAFT'));
document.getElementById('review-final').addEventListener('click',()=>{if(validateComplete(true))renderSummary()});
confirmExport.addEventListener('click',async()=>{if(!summaryReady||!validateComplete(true))return;completedAt=completedAt??new Date().toISOString();if(!validCompletionOrder(startedAt,completedAt)){completedAt=null;status.textContent=' Completion time must not predate the review start. Reload a valid draft or begin again.';return}await download(payload(true),'RESPONSE');lock()});
document.getElementById('load-response').addEventListener('change',async event=>{const file=event.target.files[0];if(!file)return;try{const bytes=new Uint8Array(await file.arrayBuffer());const value=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));validateLoaded(value);value.responses.forEach((item,index)=>{const card=cards[index];card.querySelectorAll('input[type=radio]').forEach(input=>input.checked=false);if(item.decision)card.querySelector(`input[value="${item.decision}"]`).checked=true;card.querySelector('[data-notes]').value=item.notes});startedAt=value.review_started_at_utc;completedAt=value.review_completed_at_utc;document.getElementById('attestation').checked=value.owner.attestation;update();status.textContent=` Loaded exact bytes; SHA-256 ${await digest(bytes)}.`;if(value.completed){renderSummary();lock()}else firstUnanswered()}catch(error){status.textContent=` Load rejected: ${error.message}.`}});
show(0,false);update();
'''
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(surface['batch_manifest']['title'])}</title><style>
:root{{--ink:#17251f;--pine:#132a26;--teal:#006b64;--paper:#f4f0e8;--line:#d7cec1;--warn:#8a521c}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif;overflow-wrap:anywhere}}header{{background:var(--pine);color:white;padding:2.2rem max(5vw,1rem)}}header p{{max-width:980px;color:#c6ddd6}}main{{max-width:1260px;margin:auto;padding:1rem}}.warning,.contract,.toolbar,.candidate,.attestation,.final-review{{background:#fffdf8;border:1px solid var(--line);border-radius:14px;padding:1rem;margin:1rem 0}}.warning{{border-left:7px solid #d87618;font-weight:650}}.contract{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem}}.metric strong{{display:block;font-size:1.8rem}}.toolbar{{position:sticky;top:0;z-index:3;box-shadow:0 5px 18px #132a2620}}button,.file-label{{border:0;border-radius:8px;padding:.7rem .9rem;background:var(--teal);color:white;font-weight:700;cursor:pointer;display:inline-block;margin:.2rem}}button.secondary,.file-label.secondary{{background:#53645d}}button:disabled{{opacity:.5;cursor:not-allowed}}input[type=file]{{position:absolute;left:-9999px}}.candidate{{scroll-margin-top:130px}}.eyebrow{{font-weight:800;color:var(--teal)}}.proposal{{font-size:1.15rem}}dl{{display:grid;grid-template-columns:minmax(120px,auto) 1fr;gap:.3rem 1rem}}dt{{font-weight:750}}dd{{margin:0}}.evidence-scroll{{overflow-x:auto;border:1px solid var(--line);background:#132a26;margin:.8rem 0}}.evidence-scroll img{{display:block;width:100%;min-width:720px;height:auto}}fieldset{{border:1px solid var(--line);border-radius:10px;padding:1rem}}legend{{font-weight:800;padding:0 .4rem}}.choices{{display:flex;gap:.65rem;flex-wrap:wrap}}.choices label{{border:1px solid #b8aea0;border-radius:8px;padding:.65rem 1rem;text-transform:capitalize}}.notes{{display:block;margin-top:.8rem}}textarea{{display:block;width:100%;min-height:75px;margin-top:.3rem}}.micro{{font-size:.9rem;color:#4d5c55}}.status{{font-weight:750;color:var(--warn)}}.invalid{{outline:4px solid #d87618}}code{{word-break:break-word}}[hidden]{{display:none!important}}@media(max-width:700px){{header{{padding:1.3rem 1rem}}main{{padding:.6rem}}.toolbar{{position:static}}.contract{{grid-template-columns:1fr}}.choices{{display:grid;grid-template-columns:repeat(3,1fr)}}.choices label{{padding:.55rem .2rem;text-align:center}}}}
</style></head><body><header><p>BURNLENS / {escape(surface['milestone_id'])} / REVISION {surface['surface_revision']}</p><h1>{escape(surface['batch_manifest']['title'])}</h1><p>Review one disclosed, evidence-backed proposal at a time. Each answer remains candidate-specific.</p></header><main>
<p class="warning">{escape(WARNING)}</p><section class="contract"><div class="metric"><strong>{len(surface['candidates'])}</strong>exact candidates</div><div class="metric"><strong>{len(surface['review_groups'])}</strong>event groups</div><div><strong>Decision contract</strong><p>Yes is necessary, never sufficient. No and uncertain remain excluded.</p></div></section>
<section class="toolbar" aria-label="Review controls"><strong id="position">Candidate 1 of {len(surface['candidates'])}</strong> · <strong id="progress">0 of {len(surface['candidates'])} decisions</strong><span id="status" class="status" role="status" aria-live="polite"></span><br><button id="previous" class="secondary" type="button">Previous</button><button id="next" class="secondary" type="button">Next</button><button id="resume" class="secondary" type="button">Resume at first unanswered</button><button id="save-draft" class="secondary" type="button">Save hashed draft</button><label class="file-label secondary" for="load-response">Load draft or response</label><input id="load-response" type="file" accept="application/json"><button id="review-final" type="button">Review final decisions</button></section>
{''.join(cards)}<section class="attestation"><h2>Final attestation</h2><label><input id="attestation" type="checkbox"> I am the project owner, I reviewed every exact candidate, and I understand that yes does not establish ground truth or independently accept a label.</label><p>Trace: source <code>{surface['git_source_commit']}</code> · run <code>{escape(surface['run_id'])}</code> · ordered manifest <code>{surface['ordered_manifest_sha256']}</code>.</p></section>
<section id="final-review" class="final-review" hidden><h2>Final candidate-level review</h2><p>Confirm each explicit answer below. This is not a bulk approval.</p><ul id="final-list"></ul><button id="confirm-export" type="button" disabled>Export exact response and lock</button></section>
<script id="response-template" type="application/json">{embedded}</script><script>{script}</script></main></body></html>'''


def write_surface(surface: dict[str, Any], evidence_root: Path, output_directory: Path) -> list[dict[str, Any]]:
    """Write a blank no-overwrite surface and exact evidence copies."""
    surface = _reconstruct_surface(surface)
    _assert(not output_directory.exists(), "output directory already exists")
    evidence_root = evidence_root.resolve()
    evidence_payloads: dict[str, bytes] = {}
    for candidate in surface["candidates"]:
        for item in candidate["evidence_images"]:
            source = (evidence_root / Path(*PurePosixPath(item["path"]).parts)).resolve()
            try:
                source.relative_to(evidence_root)
            except ValueError as error:
                raise OwnerReviewBatchError("evidence path escapes its root") from error
            data = source.read_bytes()
            _assert(len(data) == item["bytes"], f"evidence byte count changed: {item['path']}")
            _assert(sha256(data).hexdigest() == item["sha256"], f"evidence SHA-256 changed: {item['path']}")
            evidence_payloads[item["path"]] = data

    output_directory.mkdir(parents=True)
    surface_id = surface["report_id"]
    manifest_path = output_directory / f"{surface_id}-BATCH-MANIFEST.json"
    template_path = output_directory / f"{surface_id}-RESPONSE-TEMPLATE.json"
    html_path = output_directory / f"{surface_id}.html"
    report_path = output_directory / f"{surface_id}.json"
    evidence_paths = [output_directory / Path(*PurePosixPath(relative).parts) for relative in evidence_payloads]
    manifest_document = {
        "ordered_manifest_sha256": surface["ordered_manifest_sha256"],
        "manifest": surface["batch_manifest"],
    }
    template = response_template(surface)
    created_paths: list[Path] = []

    def write(path: Path, data: bytes) -> None:
        _write_bytes(path, data)
        created_paths.append(path)

    try:
        write(manifest_path, (json.dumps(manifest_document, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
        write(template_path, (json.dumps(template, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
        write(html_path, _render_html(surface, template).encode("utf-8"))
        for relative, data in evidence_payloads.items():
            write(output_directory / Path(*PurePosixPath(relative).parts), data)
        outputs = [
            _binding(html_path, output_directory, media_type="text/html"),
            _binding(manifest_path, output_directory, media_type="application/json"),
            _binding(template_path, output_directory, media_type="application/json"),
            *[_binding(path, output_directory, media_type="image/png") for path in evidence_paths],
        ]
        report = deepcopy(surface)
        report["outputs"] = outputs
        write(report_path, (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
        bindings = [_binding(report_path, output_directory, media_type="application/json"), *outputs]
    except Exception:
        _rollback_surface_output(output_directory, created_paths)
        raise
    return bindings
