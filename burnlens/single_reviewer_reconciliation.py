"""Reconcile one exact blinded response with the BurnLens proposal under an owner waiver."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile
from typing import Any

from .label_review_packet import LABEL_SCHEMA_VERSION, RESPONSE_SCHEMA_VERSION
from .optical_pair_evidence import AOI_VERSION, TARGET_VERSION, WARNING
from .owner_waiver_reveal_readiness import (
    AUTHORIZATION_VERSION,
    OWNER_WAIVER_ID,
    PRODUCTION_CONTRACT,
    RevealReadinessContract,
    verify_owner_waiver_reveal_authorization,
)
from .verify_label_review_packet import validate_completed_response


REPORT_ID = "LABEL-REVIEW-SINGLE-REVIEWER-RECONCILIATION-2026-001"
SCHEMA_VERSION = "0.1.0"
REPORT_VERSION = "label-review-single-reviewer-reconciliation-v0.1.0"
SOFTWARE_VERSION = "0.20.0"
TASK_ISSUE = 403
DECISION = "REMEDIATE_LABEL_EVIDENCE_DEFER_DATASET_SINGLE_REVIEWER"
REVEAL_STATUS_BEFORE_RUN = "opened-during-issue-403-reconciliation-preflight"
BUFFER_BYTES = 1024 * 1024

BINARY_PROPOSAL_TO_REVIEW_LABEL = {
    "burned": "burned",
    "background-candidate": "background",
}
WEAK_OR_CONFLICTING_REASON_CODES = frozenset(
    {
        "source-context-conflict",
        "cloud-smoke-shadow",
        "registration-concern",
        "boundary-ambiguity",
        "low-severity-ambiguity",
        "non-fire-change-possible",
        "other",
    }
)
BURN_DIRECTIONAL_REASON_CODES = frozenset({"persistent-darkening", "vegetation-loss"})


class SingleReviewerReconciliationError(RuntimeError):
    """A fail-closed private reconciliation failure."""


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise SingleReviewerReconciliationError(message)


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(BUFFER_BYTES):
            digest.update(chunk)
    return digest.hexdigest()


def _assert_regular_non_link_file(path: Path, label: str) -> None:
    try:
        metadata = path.stat(follow_symlinks=False)
    except OSError as error:
        raise SingleReviewerReconciliationError(f"{label} is unavailable") from error
    _assert(not path.is_symlink() and stat.S_ISREG(metadata.st_mode), f"{label} must be a regular non-link file")
    _assert(metadata.st_size > 0, f"{label} is empty")


def _load_json(path: Path, label: str) -> dict[str, Any]:
    _assert_regular_non_link_file(path, label)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SingleReviewerReconciliationError(f"{label} is not valid UTF-8 JSON") from error
    _assert(isinstance(value, dict), f"{label} root must be an object")
    return value


def _parse_utc(value: str, label: str) -> None:
    _assert(isinstance(value, str) and value.endswith("Z"), f"{label} must end in Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as error:
        raise SingleReviewerReconciliationError(f"{label} is invalid") from error
    _assert(parsed.tzinfo is not None, f"{label} must be timezone-aware")


def _validate_git_sha(value: str, label: str) -> None:
    _assert(
        isinstance(value, str)
        and len(value) == 40
        and all(character in "0123456789abcdef" for character in value),
        f"{label} must be a full lowercase Git SHA",
    )


def _git_relative(repository_root: Path, path: Path) -> str:
    try:
        return path.relative_to(repository_root).as_posix()
    except ValueError as error:
        raise SingleReviewerReconciliationError("private output must stay inside the repository") from error


def _assert_ignored_untracked(repository_root: Path, path: Path) -> None:
    relative = _git_relative(repository_root, path)
    ignored = subprocess.run(
        ["git", "-C", str(repository_root), "check-ignore", "--quiet", "--no-index", "--", relative],
        check=False,
        capture_output=True,
        text=True,
    )
    _assert(ignored.returncode == 0, "private output is not covered by repository ignore rules")
    tracked = subprocess.run(
        ["git", "-C", str(repository_root), "ls-files", "--error-unmatch", "--", relative],
        check=False,
        capture_output=True,
        text=True,
    )
    _assert(tracked.returncode != 0, "private output is already tracked")


def classify_unit(
    proposal_unit: dict[str, Any],
    reviewer_unit: dict[str, Any],
) -> tuple[str, str, int | None]:
    """Return the deterministic disposition, reason, and optional binary target."""

    proposal_state = proposal_unit.get("proposal_state")
    reviewer_label = reviewer_unit.get("first_pass_label")
    expected_label = BINARY_PROPOSAL_TO_REVIEW_LABEL.get(proposal_state)
    if expected_label is None:
        return "ignored", "proposal-not-binary-candidate", None
    if reviewer_label != expected_label:
        return "ignored", "reviewer-proposal-disagreement-or-nonbinary", None
    if reviewer_unit.get("evidence_sufficiency") != "sufficient":
        return "ignored", "limited-or-insufficient-evidence", None
    reason_codes = set(reviewer_unit.get("reason_codes", []))
    if reason_codes & WEAK_OR_CONFLICTING_REASON_CODES:
        return "ignored", "weak-or-conflicting-evidence-code", None
    if expected_label == "background" and reason_codes & BURN_DIRECTIONAL_REASON_CODES:
        return "ignored", "label-reason-semantic-conflict", None
    if expected_label == "burned" and not reason_codes & BURN_DIRECTIONAL_REASON_CODES:
        return "ignored", "label-reason-semantic-conflict", None
    target = 1 if expected_label == "burned" else 0
    return "accepted-candidate", "single-reviewer-supported-binary-match", target


def _validate_reveal_contents(reveal_path: Path, expected_ids: list[str]) -> None:
    _assert_regular_non_link_file(reveal_path, "proposal reveal")
    try:
        reveal = reveal_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise SingleReviewerReconciliationError("proposal reveal is not valid UTF-8") from error
    observed = re.findall(r"LRU-\d{3}", reveal)
    _assert(observed == expected_ids, "proposal reveal sample order or coverage differs")


def _write_private_output(path: Path, payload: bytes) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".burnlens-single-reviewer-reconciliation-",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    promoted = False
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path, follow_symlinks=False)
        except FileExistsError as error:
            raise SingleReviewerReconciliationError("refusing to overwrite private reconciliation") from error
        except OSError as error:
            raise SingleReviewerReconciliationError("no-overwrite private reconciliation promotion failed") from error
        promoted = True
        temporary.unlink()
        _assert(path.read_bytes() == payload, "promoted private reconciliation bytes differ")
    except BaseException:
        if promoted:
            path.unlink(missing_ok=True)
        raise
    finally:
        temporary.unlink(missing_ok=True)


def reconcile_single_reviewer(
    *,
    repository_root: Path,
    authorization_path: Path,
    response_path: Path,
    receipt_path: Path,
    packet_path: Path,
    reveal_path: Path,
    output_path: Path,
    opened_at_utc: str,
    authorization_reverified_at_utc: str,
    run_id: str,
    git_source_commit: str,
    operator_reveal_status_before_run: str,
    preflight_sequence_exception_acknowledged: bool,
    contract: RevealReadinessContract = PRODUCTION_CONTRACT,
) -> dict[str, Any]:
    """Open the exact reveal, reconcile all units, and atomically preserve a private report."""

    repository = repository_root.resolve(strict=True)
    _assert((repository / ".git").exists(), "repository root is not a Git worktree")
    _parse_utc(opened_at_utc, "reveal-opened time")
    _parse_utc(authorization_reverified_at_utc, "authorization-reverified time")
    _assert(
        authorization_reverified_at_utc >= opened_at_utc,
        "authorization-reverified time precedes the recorded reveal access",
    )
    _assert(bool(run_id.strip()), "reconciliation run ID is missing")
    _validate_git_sha(git_source_commit, "reconciliation source commit")
    _assert(
        operator_reveal_status_before_run == REVEAL_STATUS_BEFORE_RUN,
        "pre-run reveal status differs",
    )
    _assert(
        preflight_sequence_exception_acknowledged is True,
        "the issue-403 preflight sequence exception must be acknowledged",
    )
    authorization = verify_owner_waiver_reveal_authorization(
        authorization_path=authorization_path,
        response_path=response_path,
        receipt_path=receipt_path,
        packet_path=packet_path,
        reveal_path=reveal_path,
        contract=contract,
    )
    packet = _load_json(packet_path, "review packet")
    response = _load_json(response_path, "preserved first response")
    response_summary = validate_completed_response(
        packet,
        response,
        response_sha256=contract.response_sha256,
    )
    _assert(response_summary["unit_count"] == contract.unit_count, "validated response unit count differs")
    packet_units = packet.get("units")
    response_units = response.get("responses")
    _assert(isinstance(packet_units, list), "packet units are missing")
    _assert(isinstance(response_units, list), "response units are missing")
    expected_ids = [item.get("sample_id") for item in packet_units]
    _assert(
        all(isinstance(sample_id, str) for sample_id in expected_ids)
        and len(expected_ids) == len(set(expected_ids)) == contract.unit_count,
        "packet sample identities differ",
    )
    _validate_reveal_contents(reveal_path, expected_ids)

    decisions: list[dict[str, Any]] = []
    disposition_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    accepted_label_counts: Counter[str] = Counter()
    event_counts: dict[str, Counter[str]] = {}
    for proposal_unit, reviewer_unit in zip(packet_units, response_units, strict=True):
        _assert(proposal_unit["sample_id"] == reviewer_unit["sample_id"], "unit binding differs")
        disposition, reason, target = classify_unit(proposal_unit, reviewer_unit)
        event_id = proposal_unit.get("event_group_id")
        _assert(isinstance(event_id, str) and event_id, "unit event identity is missing")
        disposition_counts[disposition] += 1
        reason_counts[reason] += 1
        event_counts.setdefault(event_id, Counter())[disposition] += 1
        if disposition == "accepted-candidate":
            accepted_label_counts[reviewer_unit["first_pass_label"]] += 1
        notes = reviewer_unit.get("notes")
        decisions.append(
            {
                "sample_id": proposal_unit["sample_id"],
                "event_group_id": event_id,
                "source_trace": {
                    "row": proposal_unit.get("row"),
                    "column": proposal_unit.get("column"),
                    "pixel_center_utm10n": proposal_unit.get("pixel_center_utm10n"),
                    "reference_context_value": proposal_unit.get("reference_context_value"),
                    "selection_hash": proposal_unit.get("selection_hash"),
                    "presentation_hash": proposal_unit.get("presentation_hash"),
                },
                "proposal_trace": {
                    "proposal_state": proposal_unit.get("proposal_state"),
                    "proposal_state_code": proposal_unit.get("proposal_state_code"),
                    "proposal_target_value": proposal_unit.get("proposal_target_value"),
                    "dnbr_center": proposal_unit.get("dnbr_center"),
                },
                "reviewer_trace": {
                    "response_sha256": contract.response_sha256,
                    "first_pass_label": reviewer_unit.get("first_pass_label"),
                    "evidence_sufficiency": reviewer_unit.get("evidence_sufficiency"),
                    "confidence": reviewer_unit.get("confidence"),
                    "reason_codes": list(reviewer_unit.get("reason_codes", [])),
                    "notes_present": isinstance(notes, str) and bool(notes),
                    "notes_sha256": sha256(notes.encode("utf-8")).hexdigest()
                    if isinstance(notes, str) and notes
                    else None,
                },
                "disposition": disposition,
                "disposition_reason": reason,
                "candidate_binary_target": target,
            }
        )

    accepted = disposition_counts["accepted-candidate"]
    ignored = disposition_counts["ignored"]
    _assert(accepted + ignored == contract.unit_count, "reconciliation coverage differs")
    _assert(ignored > 0, "production reconciliation unexpectedly has no ignored evidence")
    output = output_path.absolute()
    _git_relative(repository, output)
    _assert(not output.exists(), "refusing to overwrite private reconciliation")
    output.parent.mkdir(parents=True, exist_ok=True)
    output_parent = output.parent.resolve(strict=True)
    _git_relative(repository, output_parent)
    output = output_parent / output.name
    _assert_ignored_untracked(repository, output)

    report: dict[str, Any] = {
        "report_id": REPORT_ID,
        "schema_version": SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
        "generated_at_utc": opened_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "aoi_version": packet.get("aoi_version", AOI_VERSION),
        "target_version": packet.get("target_version", TARGET_VERSION),
        "label_schema_version": packet.get("label_schema_version", LABEL_SCHEMA_VERSION),
        "response_schema_version": packet.get("response_schema_version", RESPONSE_SCHEMA_VERSION),
        "authorization_binding": {
            "bytes": authorization_path.stat().st_size,
            "sha256": _sha256_file(authorization_path),
            "report_id": OWNER_WAIVER_ID,
            "report_version": AUTHORIZATION_VERSION,
        },
        "response_binding": {
            "bytes": contract.response_bytes,
            "sha256": contract.response_sha256,
            "opaque_reviewer_id": contract.opaque_reviewer_id,
            "unit_count": contract.unit_count,
        },
        "receipt_binding": {"bytes": contract.receipt_bytes, "sha256": contract.receipt_sha256},
        "packet_binding": {"bytes": contract.packet_bytes, "sha256": contract.packet_sha256},
        "reveal_binding": {
            "bytes": contract.reveal_bytes,
            "sha256": contract.reveal_sha256,
            "operator_status_before_run": REVEAL_STATUS_BEFORE_RUN,
            "opened_by_this_run": True,
            "first_access_context": "issue-403-reconciliation-preflight",
            "first_access_recorded_at_utc": opened_at_utc,
            "authorization_reverified_at_utc": authorization_reverified_at_utc,
            "authorization_reverified_before_first_reveal_content_access": False,
            "authorization_reverified_before_private_response_content_access": True,
            "authorization_reverified_before_unit_comparison": True,
            "preflight_sequence_exception_acknowledged": True,
            "sequence_exception_detail": (
                "A repository search displayed exact reveal HTML during issue-403 preflight before "
                "the explicit authorization verifier invocation. The verifier passed immediately "
                "afterward and before private response content access or unit comparison. Reviewer "
                "blindness, response custody, and all exact source bytes were already locked."
            ),
        },
        "owner_waiver_state": {
            "returned_independent_responses": 1,
            "second_human_response_present": False,
            "reviewer_two_requirement_waived": True,
            "inter_rater_validation_available": False,
            "consensus_available": False,
            "adjudication_available": False,
        },
        "rule": {
            "version": REPORT_VERSION,
            "binary_proposal_to_review_label": dict(BINARY_PROPOSAL_TO_REVIEW_LABEL),
            "requires_evidence_sufficiency": "sufficient",
            "weak_or_conflicting_reason_codes": sorted(WEAK_OR_CONFLICTING_REASON_CODES),
            "burn_directional_reason_codes": sorted(BURN_DIRECTIONAL_REASON_CODES),
            "background_with_burn_directional_reason": "ignored-label-reason-semantic-conflict",
            "burned_without_burn_directional_reason": "ignored-label-reason-semantic-conflict",
            "uncertain_unusable_disagreement_nonbinary_and_noncandidate_proposals": "ignored",
        },
        "aggregate": {
            "reviewed_units": contract.unit_count,
            "accepted_candidate_units": accepted,
            "ignored_units": ignored,
            "accepted_label_counts": dict(sorted(accepted_label_counts.items())),
            "disposition_reason_counts": dict(sorted(reason_counts.items())),
            "event_disposition_counts": {
                event: {
                    "accepted-candidate": counts["accepted-candidate"],
                    "ignored": counts["ignored"],
                }
                for event, counts in sorted(event_counts.items())
            },
        },
        "decisions": decisions,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "decision": DECISION,
        "decision_detail": (
            "The single-reviewer route yields too little balanced, cross-event binary evidence for "
            "dataset candidacy. Preserve supported units as candidate evidence, retain every other "
            "unit as ignored, and remediate source/reference evidence before any dataset or baseline."
        ),
        "warning": WARNING,
    }
    payload = (json.dumps(report, indent=2, ensure_ascii=True) + "\n").encode("utf-8")
    _write_private_output(output, payload)
    _assert_ignored_untracked(repository, output)
    return report
