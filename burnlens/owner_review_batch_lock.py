"""Pre-reveal exact-byte custody for manifest-driven owner-review batches."""

from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Iterable

import burnlens
from .owner_review_batch import (
    HARD_BATCH_MAX,
    OwnerReviewBatchError,
    RESPONSE_SCHEMA_VERSION,
    REVIEW_PROTOCOL_VERSION,
    SURFACE_VERSION,
    build_surface,
)


LOCK_VERSION = "owner-review-batch-exact-byte-lock-v0.1.0"
MAX_RESPONSE_BYTES = 1_000_000
MAX_SURFACE_BYTES = 5_000_000
REPOSITORY = "drwbkr1/burnlens-deschutes"
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_COMMIT = re.compile(r"[0-9a-fA-F]{40}\Z")
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{1,127}\Z")
_RESPONSE_FIELDS = {
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
_RESPONSE_ITEM_FIELDS = {
    "candidate_id",
    "event_group_id",
    "candidate_binding_sha256",
    "decision",
    "notes",
}


class OwnerReviewBatchLockError(RuntimeError):
    """Raised when batch-response custody cannot be proven without reveal."""


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise OwnerReviewBatchLockError(message)


def _sha256(data: bytes) -> str:
    return sha256(data).hexdigest()


def _json(data: bytes, name: str) -> dict[str, Any]:
    def reject_duplicate_fields(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            _assert(key not in value, f"duplicate JSON field: {key}")
            value[key] = item
        return value

    def reject_nonstandard_constant(value: str) -> None:
        raise OwnerReviewBatchLockError(f"non-standard JSON constant: {value}")

    try:
        value = json.loads(
            data.decode("utf-8"),
            object_pairs_hook=reject_duplicate_fields,
            parse_constant=reject_nonstandard_constant,
        )
    except (UnicodeError, json.JSONDecodeError) as error:
        raise OwnerReviewBatchLockError(f"invalid UTF-8 JSON: {name}") from error
    _assert(isinstance(value, dict), f"JSON is not an object: {name}")
    return value


def _read_bounded(path: Path, maximum: int, name: str) -> bytes:
    size = path.stat().st_size
    _assert(0 < size <= maximum, f"{name} exceeds bounded byte contract")
    data = path.read_bytes()
    _assert(len(data) == size, f"{name} changed while being read")
    return data


def _timestamp(value: Any, name: str) -> datetime:
    _assert(isinstance(value, str), f"{name} is not a timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise OwnerReviewBatchLockError(f"{name} is invalid") from error
    _assert(parsed.tzinfo is not None, f"{name} lacks timezone")
    return parsed


def _identity(value: Any, name: str) -> str:
    _assert(isinstance(value, str) and value.strip() == value and bool(value), f"{name} is invalid")
    return value


def _identifier(value: Any, name: str) -> str:
    value = _identity(value, name)
    _assert(_IDENTIFIER.fullmatch(value) is not None, f"{name} is invalid")
    return value


def _hash(value: Any, name: str) -> str:
    _assert(isinstance(value, str) and _SHA256.fullmatch(value) is not None, f"{name} is invalid")
    return value


def _exact_keys(value: dict[str, Any], keys: set[str], name: str) -> None:
    _assert(set(value) == keys, f"{name} fields changed")


def validate_surface(surface: dict[str, Any]) -> dict[str, Any]:
    """Validate the immutable batch fields needed by the pre-reveal lock."""
    _assert(isinstance(surface, dict), "surface is not an object")
    try:
        rebuilt = build_surface(surface.get("batch_manifest"))
    except OwnerReviewBatchError as error:
        raise OwnerReviewBatchLockError("surface batch manifest is invalid") from error

    allowed_fields = set(rebuilt)
    _assert(set(surface) in (allowed_fields, allowed_fields | {"outputs"}), "surface fields changed")
    for name in rebuilt:
        _assert(surface.get(name) == rebuilt[name], f"surface reconstruction mismatch: {name}")

    if "outputs" in surface:
        outputs = surface["outputs"]
        _assert(isinstance(outputs, list) and outputs, "surface outputs are invalid")
        output_paths: set[str] = set()
        for output in outputs:
            _assert(isinstance(output, dict), "surface output is not an object")
            _exact_keys(output, {"path", "bytes", "sha256", "media_type"}, "surface output")
            output_path = _identity(output["path"], "surface output path")
            _assert(output_path not in output_paths, "surface output path is duplicated")
            output_paths.add(output_path)
            _assert(
                isinstance(output["bytes"], int)
                and not isinstance(output["bytes"], bool)
                and output["bytes"] > 0,
                "surface output byte count is invalid",
            )
            _hash(output["sha256"], "surface output hash")
            _assert(
                output["media_type"] in {"application/json", "text/html", "image/png"},
                "surface output media type is invalid",
            )

    surface_revision = surface.get("surface_revision")
    _assert(
        isinstance(surface_revision, int) and not isinstance(surface_revision, bool) and surface_revision > 0,
        "surface revision is invalid",
    )
    task_issue = surface.get("task_issue")
    _assert(
        isinstance(task_issue, int) and not isinstance(task_issue, bool) and task_issue > 0,
        "surface task issue is invalid",
    )
    bindings = {
        "response_schema_version": _identity(surface.get("response_schema_version"), "surface response schema"),
        "surface_id": _identifier(surface.get("report_id"), "surface identity"),
        "surface_run_id": _identifier(surface.get("run_id"), "surface run identity"),
        "surface_revision": surface_revision,
        "milestone_id": _identifier(surface.get("milestone_id"), "surface milestone"),
        "ordered_manifest_sha256": _hash(
            surface.get("ordered_manifest_sha256"), "surface ordered manifest hash"
        ),
        "report_version": _identifier(surface.get("report_version"), "surface report version"),
        "review_protocol_version": _identifier(
            surface.get("review_protocol_version"), "surface review protocol version"
        ),
        "task_issue": task_issue,
    }
    _assert(bindings["response_schema_version"] == RESPONSE_SCHEMA_VERSION, "surface response schema changed")
    _assert(bindings["report_version"] == SURFACE_VERSION, "surface report version changed")
    _assert(
        bindings["review_protocol_version"] == REVIEW_PROTOCOL_VERSION,
        "surface review protocol version changed",
    )
    summary = surface.get("summary")
    _assert(isinstance(summary, dict), "surface summary is not an object")
    owner_responses = summary.get("owner_responses")
    labels_created = summary.get("labels_created")
    _assert(
        isinstance(owner_responses, int) and not isinstance(owner_responses, bool) and owner_responses == 0,
        "surface already contains owner responses",
    )
    _assert(
        isinstance(labels_created, int) and not isinstance(labels_created, bool) and labels_created == 0,
        "surface already contains labels",
    )
    candidates = surface.get("candidates")
    _assert(
        isinstance(candidates, list) and 1 <= len(candidates) <= HARD_BATCH_MAX,
        "surface candidates are invalid",
    )
    seen: set[str] = set()
    candidate_bindings: list[dict[str, str]] = []
    for candidate in candidates:
        _assert(isinstance(candidate, dict), "surface candidate is not an object")
        candidate_id = _identifier(candidate.get("candidate_id"), "surface candidate identity")
        _assert(candidate_id not in seen, "surface candidate identity is duplicated")
        seen.add(candidate_id)
        candidate_bindings.append(
            {
                "candidate_id": candidate_id,
                "event_group_id": _identifier(
                    candidate.get("event_group_id"), "surface event group identity"
                ),
                "candidate_binding_sha256": _hash(
                    candidate.get("candidate_binding_sha256"), "surface candidate binding hash"
                ),
            }
        )
    return {**bindings, "candidate_bindings": candidate_bindings}


def validate_completed_envelope_without_reveal(
    surface: dict[str, Any], response: dict[str, Any]
) -> dict[str, Any]:
    """Validate completion and immutable bindings without reading decisions or notes."""
    surface_binding = validate_surface(surface)
    _exact_keys(response, _RESPONSE_FIELDS, "response")
    for name in (
        "response_schema_version",
        "surface_id",
        "surface_run_id",
        "surface_revision",
        "milestone_id",
        "ordered_manifest_sha256",
    ):
        if name == "surface_revision":
            _assert(
                isinstance(response[name], int)
                and not isinstance(response[name], bool)
                and response[name] >= 1,
                "response surface revision is invalid",
            )
        _assert(response[name] == surface_binding[name], f"response binding mismatch: {name}")
    _assert(response["completed"] is True, "response is incomplete")

    owner = response["owner"]
    _assert(isinstance(owner, dict), "owner attestation is not an object")
    _exact_keys(owner, {"attestation"}, "owner attestation")
    _assert(owner["attestation"] is True, "owner attestation is incomplete")

    started = _timestamp(response["review_started_at_utc"], "review start")
    completed = _timestamp(response["review_completed_at_utc"], "review completion")
    _assert(completed >= started, "review completion predates start")

    items = response["responses"]
    expected = surface_binding["candidate_bindings"]
    _assert(isinstance(items, list) and len(items) == len(expected), "response candidate count changed")
    actual: list[dict[str, str]] = []
    for expected_candidate, item in zip(expected, items, strict=True):
        _assert(isinstance(item, dict), "response candidate is not an object")
        _exact_keys(item, _RESPONSE_ITEM_FIELDS, "response candidate")
        for name in ("candidate_id", "event_group_id", "candidate_binding_sha256"):
            _assert(item[name] == expected_candidate[name], f"response candidate binding mismatch: {name}")
        actual.append(dict(expected_candidate))

    return {
        "response_schema_version": surface_binding["response_schema_version"],
        "surface_id": surface_binding["surface_id"],
        "surface_run_id": surface_binding["surface_run_id"],
        "surface_revision": surface_binding["surface_revision"],
        "milestone_id": surface_binding["milestone_id"],
        "ordered_manifest_sha256": surface_binding["ordered_manifest_sha256"],
        "started_at_utc": response["review_started_at_utc"],
        "completed_at_utc": response["review_completed_at_utc"],
        "response_record_count": len(actual),
        "candidate_bindings": actual,
        "decision_values_read": False,
        "note_values_read": False,
    }


# Keep the shorter name available to task-specific adapters.
validate_envelope_without_reveal = validate_completed_envelope_without_reveal


def classify_completed_response_ambiguity(response_sha256s: Iterable[str]) -> dict[str, Any]:
    """Classify hashes already proven to be completed, envelope-valid exports."""
    hashes = list(response_sha256s)
    for value in hashes:
        _hash(value, "completed response hash")
    distinct = sorted(set(hashes))
    if not hashes:
        classification = "NO_VALID_COMPLETED_RESPONSE"
    elif len(distinct) > 1:
        classification = "AMBIGUOUS_DISTINCT_COMPLETED_RESPONSES"
    elif len(hashes) > 1:
        classification = "IDEMPOTENT_IDENTICAL_COMPLETED_RESPONSES"
    else:
        classification = "SINGLE_VALID_COMPLETED_RESPONSE"
    ambiguous = len(distinct) > 1
    return {
        "classification": classification,
        "completed_response_count": len(hashes),
        "distinct_response_count": len(distinct),
        "distinct_response_sha256s": distinct,
        "identical_exports_are_idempotent": len(hashes) > 1 and len(distinct) == 1,
        "ambiguous": ambiguous,
        "blocks_intake": not hashes or ambiguous,
    }


def require_unambiguous_completed_response(response_sha256s: Iterable[str]) -> dict[str, Any]:
    """Return the hash classification or fail when intake has no unique final bytes."""
    result = classify_completed_response_ambiguity(response_sha256s)
    _assert(not result["blocks_intake"], result["classification"])
    return result


def classify_completed_exports_without_reveal(
    *, surface_path: Path, response_paths: Iterable[Path]
) -> dict[str, Any]:
    """Validate completed envelopes and classify their exact hashes without reveal."""
    surface_bytes = _read_bounded(surface_path, MAX_SURFACE_BYTES, "surface")
    surface = _json(surface_bytes, surface_path.name)
    validate_surface(surface)
    response_sha256s: list[str] = []
    for path in response_paths:
        response_bytes = _read_bounded(path, MAX_RESPONSE_BYTES, "response")
        response = _json(response_bytes, path.name)
        validate_completed_envelope_without_reveal(surface, response)
        response_sha256 = _sha256(response_bytes)
        expected_name = f"{surface['report_id']}-RESPONSE-{response_sha256[:16]}.json"
        _assert(path.name == expected_name, "response filename does not match its exact byte hash")
        response_sha256s.append(response_sha256)
    result = classify_completed_response_ambiguity(response_sha256s)
    return {
        **result,
        "surface_sha256": _sha256(surface_bytes),
        "decision_values_read": False,
        "note_values_read": False,
    }


def _assert_ignored(repository_root: Path, path: Path) -> None:
    try:
        relative = path.relative_to(repository_root)
    except ValueError as error:
        raise OwnerReviewBatchLockError("custody destination is outside the repository") from error
    relative_text = relative.as_posix()
    tracked = subprocess.run(
        ["git", "-C", str(repository_root), "ls-files", "--error-unmatch", "--", relative_text],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    _assert(tracked.returncode != 0, "private custody output is already tracked")
    result = subprocess.run(
        ["git", "-C", str(repository_root), "check-ignore", "--quiet", "--no-index", "--", relative_text],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    _assert(result.returncode == 0, "private custody output is not ignored")


def _write_exact(path: Path, payload: bytes) -> None:
    created = False
    try:
        with path.open("xb") as handle:
            created = True
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        _assert(path.read_bytes() == payload, f"written custody bytes changed: {path.name}")
    except Exception:
        if created:
            try:
                path.unlink(missing_ok=True)
            except OSError as rollback_error:
                raise OwnerReviewBatchLockError(
                    f"failed to roll back partial custody write: {path.name}"
                ) from rollback_error
        raise


def _rollback(paths: Iterable[Path]) -> None:
    failures: list[str] = []
    for path in reversed(list(paths)):
        try:
            path.unlink(missing_ok=True)
        except OSError:
            failures.append(path.name)
    if failures:
        raise OwnerReviewBatchLockError(f"failed to roll back partial custody writes: {', '.join(failures)}")


def preserve_response_without_reveal(
    *,
    repository_root: Path,
    surface_path: Path,
    source_response_path: Path,
    destination_directory: Path,
    received_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> tuple[Path, Path, dict[str, Any]]:
    """Preserve exact response and receipt with no overwrite before decision access."""
    _assert(_COMMIT.fullmatch(git_source_commit) is not None, "git source commit must be a full SHA")
    _identifier(run_id, "lock run identity")

    repository_root = repository_root.resolve()
    destination_directory = destination_directory.resolve(strict=False)
    try:
        destination_directory.relative_to(repository_root)
    except ValueError as error:
        raise OwnerReviewBatchLockError("custody destination is outside the repository") from error

    surface_bytes = _read_bounded(surface_path, MAX_SURFACE_BYTES, "surface")
    surface = _json(surface_bytes, surface_path.name)
    surface_binding = validate_surface(surface)
    response_bytes = _read_bounded(source_response_path, MAX_RESPONSE_BYTES, "response")
    response = _json(response_bytes, source_response_path.name)
    envelope = validate_completed_envelope_without_reveal(surface, response)

    response_sha256 = _sha256(response_bytes)
    expected_name = f"{surface_binding['surface_id']}-RESPONSE-{response_sha256[:16]}.json"
    _assert(source_response_path.name == expected_name, "response filename does not match its exact byte hash")
    received = _timestamp(received_at_utc, "received time")
    completed = _timestamp(envelope["completed_at_utc"], "review completion")
    _assert(received >= completed, "received time predates review completion")

    destination_directory.mkdir(parents=True, exist_ok=True)
    exact_path = destination_directory / expected_name
    receipt_path = destination_directory / (
        f"{surface_binding['surface_id']}-RECEIPT-{response_sha256[:16]}.json"
    )
    _assert_ignored(repository_root, exact_path)
    _assert_ignored(repository_root, receipt_path)

    receipt = {
        "report_id": f"{surface_binding['surface_id']}-RECEIPT",
        "report_version": LOCK_VERSION,
        "received_at_utc": received_at_utc,
        "run_id": run_id,
        "repository": REPOSITORY,
        "task_issue": surface_binding["task_issue"],
        "git_source_commit": git_source_commit,
        "software_version": burnlens.__version__,
        "evidence_origin": "owner-returned-batch-response",
        "origin_declared_by_operator": True,
        "surface_binding": {
            **{name: surface_binding[name] for name in (
                "surface_id",
                "surface_run_id",
                "surface_revision",
                "milestone_id",
                "ordered_manifest_sha256",
            )},
            "report_version": surface_binding["report_version"],
            "response_schema_version": surface_binding["response_schema_version"],
            "review_protocol_version": surface_binding["review_protocol_version"],
            "task_issue": surface_binding["task_issue"],
            "bytes": len(surface_bytes),
            "sha256": _sha256(surface_bytes),
        },
        "response_binding": {
            "bytes": len(response_bytes),
            "sha256": response_sha256,
            **envelope,
        },
        "exact_response_preserved_without_overwrite": True,
        "decisions_revealed": False,
        "qualifying_owner_response": None,
        "owner_yes_is_sufficient_without_other_gates": False,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "decision": "PASS_EXACT_OWNER_REVIEW_BATCH_RESPONSE_LOCK_KEEP_DECISIONS_UNREVEALED",
    }
    receipt_bytes = (json.dumps(receipt, indent=2) + "\n").encode("utf-8")

    written: list[Path] = []
    try:
        _write_exact(exact_path, response_bytes)
        written.append(exact_path)
        _assert(source_response_path.read_bytes() == response_bytes, "response source changed during preservation")
        _assert(surface_path.read_bytes() == surface_bytes, "surface source changed during preservation")
        _write_exact(receipt_path, receipt_bytes)
        written.append(receipt_path)
        _assert(exact_path.read_bytes() == response_bytes, "preserved response changed after receipt write")
        _assert(receipt_path.read_bytes() == receipt_bytes, "preserved receipt changed after write")
        _assert(surface_path.read_bytes() == surface_bytes, "surface source changed during preservation")
    except FileExistsError as error:
        _rollback(written)
        raise OwnerReviewBatchLockError("refusing to overwrite exact response or receipt") from error
    except Exception:
        _rollback(written)
        raise
    return exact_path, receipt_path, receipt


# Task-specific adapters may use either verb while the generic contract settles.
lock_response_without_reveal = preserve_response_without_reveal
