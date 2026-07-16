"""Validate and SHA-256 lock one returned BurnLens label-review response."""

from __future__ import annotations

import argparse
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Any

from .label_review_handoff import (
    EXPECTED_PACKET_ID,
    EXPECTED_PACKET_RUN_ID,
    EXPECTED_PACKET_SHA256,
    WORKBENCH_VERSION,
)
from .optical_pair_evidence import WARNING
from .verify_label_review_packet import (
    LabelReviewVerificationError,
    validate_completed_response,
)


LOCK_SCHEMA_VERSION = "0.1.0"
LOCK_REPORT_VERSION = "label-review-response-integrity-lock-v0.2.0"
SOFTWARE_VERSION = "0.15.0"
RETURNED_INDEPENDENT_RESPONSE = "returned-independent-response"
SOFTWARE_BROWSER_FIXTURE = "software-browser-fixture"
EVIDENCE_ORIGINS = {
    RETURNED_INDEPENDENT_RESPONSE,
    SOFTWARE_BROWSER_FIXTURE,
}


class LabelReviewResponseLockError(RuntimeError):
    """A fail-closed response-locking failure."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise LabelReviewResponseLockError(f"invalid JSON input {path.name}") from error
    if not isinstance(value, dict):
        raise LabelReviewResponseLockError(f"JSON input {path.name} is not an object")
    return value


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def build_response_lock(
    *,
    packet_path: Path,
    response_path: Path,
    receipt_id: str,
    received_at_utc: str,
    run_id: str,
    git_source_commit: str,
    evidence_origin: str,
    task_issue: int,
) -> dict[str, Any]:
    packet = _load_json(packet_path)
    response = _load_json(response_path)
    if packet.get("report_id") != EXPECTED_PACKET_ID:
        raise LabelReviewResponseLockError("packet identity differs from the shipped packet")
    if packet.get("run_id") != EXPECTED_PACKET_RUN_ID:
        raise LabelReviewResponseLockError("packet run differs from the shipped packet")
    if _sha256_file(packet_path) != EXPECTED_PACKET_SHA256:
        raise LabelReviewResponseLockError("packet SHA-256 differs from the shipped packet")
    if response_path.stat().st_size > 1_000_000:
        raise LabelReviewResponseLockError("response exceeds the bounded byte contract")
    response_sha256 = _sha256_file(response_path)
    try:
        summary = validate_completed_response(
            packet,
            response,
            response_sha256=response_sha256,
        )
    except LabelReviewVerificationError as error:
        raise LabelReviewResponseLockError(f"response validation failed: {error}") from error
    if len(git_source_commit) != 40:
        raise LabelReviewResponseLockError("git source commit must be a full 40-character SHA")
    if evidence_origin not in EVIDENCE_ORIGINS:
        raise LabelReviewResponseLockError("response evidence origin is invalid")
    if not isinstance(task_issue, int) or isinstance(task_issue, bool) or task_issue <= 0:
        raise LabelReviewResponseLockError("task issue must be a positive integer")
    if not receipt_id.strip() or not run_id.strip() or not received_at_utc.strip():
        raise LabelReviewResponseLockError("receipt identity, run identity, and receive time are required")
    try:
        received = datetime.fromisoformat(received_at_utc.replace("Z", "+00:00"))
    except ValueError as error:
        raise LabelReviewResponseLockError("receive time is invalid") from error
    if received.tzinfo is None:
        raise LabelReviewResponseLockError("receive time must be timezone-aware")
    response_completed_text = response.get("review_completed_at_utc")
    try:
        response_completed = datetime.fromisoformat(
            response_completed_text.replace("Z", "+00:00")
        )
    except (AttributeError, ValueError) as error:
        raise LabelReviewResponseLockError(
            "response completion time is invalid"
        ) from error
    if response_completed.tzinfo is None or received < response_completed:
        raise LabelReviewResponseLockError(
            "response receive time predates response completion"
        )
    reviewer = response["reviewer"]
    reviewer_id = reviewer["reviewer_id"].strip()
    experience = reviewer.get("burned_area_interpretation_experience")
    if len(reviewer_id) > 120:
        raise LabelReviewResponseLockError("opaque reviewer ID exceeds the bounded length")
    if not isinstance(experience, str) or not experience.strip() or len(experience) > 500:
        raise LabelReviewResponseLockError(
            "burned-area interpretation experience is missing or exceeds the bounded length"
        )
    is_software_fixture = evidence_origin == SOFTWARE_BROWSER_FIXTURE
    if is_software_fixture:
        decision = "PASS_SOFTWARE_FIXTURE_CONTRACT_AND_HASH_LOCK_NO_REVEAL"
        detail = (
            "The exact browser-generated software-fixture bytes pass the proposal-free response "
            "contract and are bound to SHA-256. The fixture is not an independent human response, "
            "cannot authorize reveal, and cannot contribute to label fitness or dataset candidacy."
        )
        reveal_release = "prohibited: software fixture cannot authorize proposal reveal"
    else:
        decision = "PASS_RESPONSE_CONTRACT_AND_HASH_LOCK_DEFER_SCIENTIFIC_USE"
        detail = (
            "The exact returned-response bytes pass the proposal-free response contract and are "
            "bound to SHA-256. The operator-declared origin is not identity verification; software "
            "cannot prove reviewer expertise, independence, scientific correctness, or dataset fitness."
        )
        reveal_release = (
            "operator may release reveal only after preserving this receipt and exact response bytes"
        )
    return {
        "report_id": receipt_id,
        "schema_version": LOCK_SCHEMA_VERSION,
        "report_version": LOCK_REPORT_VERSION,
        "received_at_utc": received_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": task_issue,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": WORKBENCH_VERSION,
        "evidence_origin": evidence_origin,
        "origin_declared_by_operator": True,
        "origin_verified_by_software": False,
        "packet_binding": {
            "report_id": packet["report_id"],
            "run_id": packet["run_id"],
            "git_source_commit": packet["git_source_commit"],
            "sha256": _sha256_file(packet_path),
            "response_schema_version": packet["response_schema_version"],
        },
        "response_binding": {
            "bytes": response_path.stat().st_size,
            "sha256": response_sha256,
            "opaque_reviewer_id": summary["reviewer_id"],
            "unit_count": summary["unit_count"],
            "label_counts": summary["label_counts"],
            "insufficient_evidence_units": summary["insufficient_evidence_units"],
            "uncertain_or_unusable_units": summary["uncertain_or_unusable_units"],
            "input_filename_retained": False,
        },
        "software_contract_validation": "pass",
        "response_contents_include_independence_and_blinding_attestations": True,
        "qualifying_independent_human_response": False if is_software_fixture else None,
        "software_browser_fixture": is_software_fixture,
        "human_identity_verified_by_software": False,
        "reviewer_expertise_verified_by_software": False,
        "scientific_label_fitness_established": False,
        "reveal_release": reveal_release,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "decision": decision,
        "decision_detail": detail,
        "warning": WARNING,
    }


def write_response_lock(report: dict[str, Any], output_path: Path) -> None:
    if output_path.exists():
        raise LabelReviewResponseLockError(
            f"refusing to overwrite existing response lock {output_path.name}"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, indent=2, ensure_ascii=True) + "\n"
    output_path.write_bytes(payload.encode("utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--receipt-id", required=True)
    parser.add_argument("--received-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument("--task-issue", type=int, required=True)
    parser.add_argument(
        "--evidence-origin",
        choices=sorted(EVIDENCE_ORIGINS),
        required=True,
        help=(
            "Operator-declared origin. Use software-browser-fixture for automated QA; that mode "
            "cannot authorize reveal or count as human evidence."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = build_response_lock(
            packet_path=args.packet,
            response_path=args.response,
            receipt_id=args.receipt_id,
            received_at_utc=args.received_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
            evidence_origin=args.evidence_origin,
            task_issue=args.task_issue,
        )
        write_response_lock(report, args.output_json)
        print(report["decision"])
        print(f"response_sha256={report['response_binding']['sha256']}")
        return 0
    except (LabelReviewResponseLockError, OSError, ValueError, KeyError) as error:
        print(f"LABEL_REVIEW_RESPONSE_LOCK_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
