"""Authorize a later BurnLens proposal reveal after an explicit owner waiver."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
from typing import Any

from .label_review_handoff import WORKBENCH_VERSION
from .optical_pair_evidence import WARNING


AUTHORIZATION_SCHEMA_VERSION = "0.1.0"
AUTHORIZATION_VERSION = "label-review-owner-waiver-reveal-authorization-v0.1.0"
SOFTWARE_VERSION = "0.19.0"
TASK_ISSUE = 407
PARENT_RECONCILIATION_ISSUE = 403
SUPERSEDED_SECOND_RESPONSE_ISSUE = 393
OWNER_WAIVER_ID = "OWNER-WAIVER-2026-001"
OWNER_WAIVER_DATE = "2026-07-16"
UNOPENED_REVEAL_STATUS = "withheld-unopened-after-lock"
DECISION = "PASS_OWNER_WAIVER_REVEAL_READINESS_SINGLE_REVIEWER_REDUCED_VALIDATION"
REPOSITORY = "drwbkr1/burnlens-deschutes"
BUFFER_BYTES = 1024 * 1024


@dataclass(frozen=True)
class RevealReadinessContract:
    response_bytes: int
    response_sha256: str
    receipt_bytes: int
    receipt_sha256: str
    packet_bytes: int
    packet_sha256: str
    reveal_bytes: int
    reveal_sha256: str
    opaque_reviewer_id: str = "reviewer-01"
    unit_count: int = 56


PRODUCTION_CONTRACT = RevealReadinessContract(
    response_bytes=16_443,
    response_sha256="485e80f2563f8b723c16daa8b5e5a1172dd88e8f2a28a7dd8608c933fa64eed9",
    receipt_bytes=2_508,
    receipt_sha256="67599f794a1310e9523cded095787c918ed47d88c439e240a0b41ea6e5eb9835",
    packet_bytes=61_599,
    packet_sha256="77067063a769645af13886b6c87cc236a10e06199d091743908d63556e07637c",
    reveal_bytes=9_433,
    reveal_sha256="27bc0ccd0ab113f852ebc9ce80c537b8e6166c37d390785670fd7e0fedbb35af",
)


class OwnerWaiverRevealReadinessError(RuntimeError):
    """A fail-closed owner-waiver or reveal-readiness failure."""


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise OwnerWaiverRevealReadinessError(message)


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
        raise OwnerWaiverRevealReadinessError(f"{label} is unavailable") from error
    if path.is_symlink() or not stat.S_ISREG(metadata.st_mode):
        raise OwnerWaiverRevealReadinessError(f"{label} must be a regular non-link file")
    if metadata.st_size <= 0:
        raise OwnerWaiverRevealReadinessError(f"{label} is empty")


def _verify_exact_file(
    path: Path,
    *,
    label: str,
    expected_bytes: int,
    expected_sha256: str,
) -> dict[str, Any]:
    _assert_regular_non_link_file(path, label)
    byte_count = path.stat(follow_symlinks=False).st_size
    digest = _sha256_file(path)
    _assert(byte_count == expected_bytes, f"{label} byte count differs")
    _assert(digest == expected_sha256, f"{label} SHA-256 differs")
    return {"bytes": byte_count, "sha256": digest}


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OwnerWaiverRevealReadinessError(f"{label} is not valid UTF-8 JSON") from error
    _assert(isinstance(value, dict), f"{label} root must be an object")
    return value


def _parse_utc(value: str, label: str) -> datetime:
    _assert(isinstance(value, str) and value.endswith("Z"), f"{label} must end in Z")
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as error:
        raise OwnerWaiverRevealReadinessError(f"{label} is invalid") from error


def _validate_full_sha(value: str, label: str) -> None:
    _assert(
        isinstance(value, str)
        and len(value) == 40
        and all(character in "0123456789abcdef" for character in value),
        f"{label} must be a full lowercase Git SHA",
    )


def _validate_receipt(
    receipt: dict[str, Any],
    *,
    contract: RevealReadinessContract,
) -> None:
    _assert(receipt.get("repository") == REPOSITORY, "receipt repository differs")
    _assert(
        receipt.get("evidence_origin") == "returned-independent-response",
        "receipt does not bind a returned independent response",
    )
    _assert(receipt.get("software_browser_fixture") is False, "receipt binds a software fixture")
    _assert(receipt.get("origin_declared_by_operator") is True, "receipt origin is undeclared")
    _assert(receipt.get("origin_verified_by_software") is False, "receipt origin boundary differs")
    _assert(receipt.get("software_contract_validation") == "pass", "receipt contract did not pass")
    _assert(
        receipt.get("decision") == "PASS_RESPONSE_CONTRACT_AND_HASH_LOCK_DEFER_SCIENTIFIC_USE",
        "receipt decision differs",
    )
    _assert(receipt.get("scientific_label_fitness_established") is False, "receipt overclaims fitness")
    _assert(receipt.get("human_identity_verified_by_software") is False, "receipt overclaims identity")
    _assert(
        receipt.get("reviewer_expertise_verified_by_software") is False,
        "receipt overclaims reviewer expertise",
    )
    _assert(
        all(
            receipt.get(key) is None
            for key in ("dataset_version", "split_version", "baseline_version", "model_version")
        ),
        "receipt advances a downstream analytical version",
    )
    packet = receipt.get("packet_binding")
    response = receipt.get("response_binding")
    _assert(isinstance(packet, dict), "receipt packet binding is missing")
    _assert(isinstance(response, dict), "receipt response binding is missing")
    _assert(packet.get("sha256") == contract.packet_sha256, "receipt packet hash differs")
    _assert(response.get("bytes") == contract.response_bytes, "receipt response bytes differ")
    _assert(response.get("sha256") == contract.response_sha256, "receipt response hash differs")
    _assert(
        response.get("opaque_reviewer_id") == contract.opaque_reviewer_id,
        "receipt reviewer slot differs",
    )
    _assert(response.get("unit_count") == contract.unit_count, "receipt unit count differs")


def _relative_git_path(repository_root: Path, path: Path) -> str:
    try:
        return path.relative_to(repository_root).as_posix()
    except ValueError as error:
        raise OwnerWaiverRevealReadinessError(
            "authorization output must stay inside the repository root"
        ) from error


def _assert_ignored_untracked(repository_root: Path, path: Path) -> None:
    relative = _relative_git_path(repository_root, path)
    ignored = subprocess.run(
        ["git", "-C", str(repository_root), "check-ignore", "--quiet", "--no-index", "--", relative],
        check=False,
        capture_output=True,
        text=True,
    )
    if ignored.returncode != 0:
        if ignored.returncode == 1:
            raise OwnerWaiverRevealReadinessError(
                "authorization output is not covered by repository ignore rules"
            )
        raise OwnerWaiverRevealReadinessError("git ignore verification failed")
    tracked = subprocess.run(
        ["git", "-C", str(repository_root), "ls-files", "--error-unmatch", "--", relative],
        check=False,
        capture_output=True,
        text=True,
    )
    _assert(tracked.returncode != 0, "authorization output is already tracked")


def _write_private_authorization(path: Path, payload: bytes) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".burnlens-reveal-authorization-",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary_path = Path(temporary_name)
    promoted = False
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary_path, path, follow_symlinks=False)
        except FileExistsError as error:
            raise OwnerWaiverRevealReadinessError(
                "refusing to overwrite an existing reveal authorization"
            ) from error
        except OSError as error:
            raise OwnerWaiverRevealReadinessError(
                "same-directory no-overwrite authorization promotion failed"
            ) from error
        promoted = True
        temporary_path.unlink()
        _assert(path.read_bytes() == payload, "promoted authorization bytes differ")
    except BaseException:
        if promoted:
            path.unlink(missing_ok=True)
        raise
    finally:
        temporary_path.unlink(missing_ok=True)


def authorize_owner_waiver_reveal(
    *,
    repository_root: Path,
    response_path: Path,
    receipt_path: Path,
    packet_path: Path,
    reveal_path: Path,
    authorization_path: Path,
    authorization_id: str,
    run_id: str,
    authorized_at_utc: str,
    git_source_commit: str,
    owner_waiver_confirmed: bool,
    reduced_validation_acknowledged: bool,
    operator_reveal_status: str,
    task_issue: int = TASK_ISSUE,
    parent_reconciliation_issue: int = PARENT_RECONCILIATION_ISSUE,
    contract: RevealReadinessContract = PRODUCTION_CONTRACT,
) -> dict[str, Any]:
    """Verify exact custody and authorize only a later controlled reconciliation reveal."""

    repository = repository_root.resolve(strict=True)
    _assert((repository / ".git").exists(), "repository root is not a Git worktree")
    _assert(task_issue == TASK_ISSUE, "task issue differs")
    _assert(
        parent_reconciliation_issue == PARENT_RECONCILIATION_ISSUE,
        "parent reconciliation issue differs",
    )
    _assert(authorization_id == OWNER_WAIVER_ID, "owner-waiver authorization ID differs")
    _assert(bool(run_id.strip()), "authorization run ID is missing")
    _parse_utc(authorized_at_utc, "authorization time")
    _validate_full_sha(git_source_commit, "git source commit")
    _assert(owner_waiver_confirmed is True, "explicit owner waiver is required")
    _assert(
        reduced_validation_acknowledged is True,
        "single-reviewer reduced-validation risk must be acknowledged",
    )
    _assert(
        operator_reveal_status == UNOPENED_REVEAL_STATUS,
        "reveal must remain operator-declared unopened before authorization",
    )

    response = _verify_exact_file(
        response_path,
        label="preserved first response",
        expected_bytes=contract.response_bytes,
        expected_sha256=contract.response_sha256,
    )
    receipt_binding = _verify_exact_file(
        receipt_path,
        label="first-response receipt",
        expected_bytes=contract.receipt_bytes,
        expected_sha256=contract.receipt_sha256,
    )
    packet = _verify_exact_file(
        packet_path,
        label="review packet",
        expected_bytes=contract.packet_bytes,
        expected_sha256=contract.packet_sha256,
    )
    reveal = _verify_exact_file(
        reveal_path,
        label="proposal reveal",
        expected_bytes=contract.reveal_bytes,
        expected_sha256=contract.reveal_sha256,
    )
    receipt = _load_json(receipt_path, "first-response receipt")
    _validate_receipt(receipt, contract=contract)

    output = authorization_path.absolute()
    _relative_git_path(repository, output)
    _assert(not output.exists(), "refusing to overwrite an existing reveal authorization")
    _assert(not output.is_symlink(), "authorization output must not be a symbolic link")
    output.parent.mkdir(parents=True, exist_ok=True)
    output_parent = output.parent.resolve(strict=True)
    _relative_git_path(repository, output_parent)
    output = output_parent / output.name
    _assert_ignored_untracked(repository, output)

    report: dict[str, Any] = {
        "report_id": authorization_id,
        "schema_version": AUTHORIZATION_SCHEMA_VERSION,
        "report_version": AUTHORIZATION_VERSION,
        "authorized_at_utc": authorized_at_utc,
        "run_id": run_id,
        "repository": REPOSITORY,
        "task_issue": task_issue,
        "parent_reconciliation_issue": parent_reconciliation_issue,
        "superseded_second_response_issue": SUPERSEDED_SECOND_RESPONSE_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": WORKBENCH_VERSION,
        "owner_waiver": {
            "waiver_id": OWNER_WAIVER_ID,
            "decision_date": OWNER_WAIVER_DATE,
            "reviewer_two_requirement_waived": True,
            "second_human_response_present": False,
            "single_reviewer_reduced_validation_acknowledged": True,
            "waiver_verified_by_software": False,
            "source": "explicit interactive repository-owner directive",
        },
        "response_binding": {
            **response,
            "opaque_reviewer_id": contract.opaque_reviewer_id,
            "unit_count": contract.unit_count,
            "filename_retained": False,
            "private_path_retained": False,
            "contents_interpreted_by_this_run": False,
        },
        "receipt_binding": {
            **receipt_binding,
            "report_id": receipt["report_id"],
            "report_version": receipt["report_version"],
            "software_version": receipt["software_version"],
            "filename_retained": False,
            "private_path_retained": False,
        },
        "packet_binding": {**packet, "report_id": "LABEL-REVIEW-PACKET-2026-001"},
        "reveal_binding": {
            **reveal,
            "report_id": "LABEL-REVIEW-PACKET-2026-001-REVEAL",
            "contents_interpreted_by_this_run": False,
        },
        "checks": {
            "exact_preserved_response": "pass",
            "exact_first_response_receipt": "pass",
            "receipt_response_binding": "pass",
            "receipt_packet_binding": "pass",
            "returned_response_not_fixture": "pass",
            "exact_review_packet": "pass",
            "exact_unopened_reveal": "pass",
            "owner_waiver_declared": "pass",
            "reduced_validation_acknowledged": "pass",
            "ignored_untracked_authorization_storage": "pass",
            "no_overwrite_authorization_promotion": "pass",
        },
        "evidence_state": {
            "returned_independent_responses": 1,
            "second_human_response_present": False,
            "inter_rater_validation_available": False,
            "consensus_available": False,
            "adjudication_available": False,
            "operator_reveal_status_before_run": UNOPENED_REVEAL_STATUS,
            "reveal_opened_by_this_run": False,
            "response_comparison_performed": False,
        },
        "authorization_scope": {
            "reveal_authorized_for_later_private_reconciliation": True,
            "authorized_reconciliation_issue": PARENT_RECONCILIATION_ISSUE,
            "authorized_response_count": 1,
            "must_preserve_original_response_and_proposal": True,
            "must_retain_disagreement_uncertainty_exclusions_and_weak_evidence_as_ignored": True,
            "public_reviewer_free_text_prohibited": True,
        },
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "decision": DECISION,
        "warning": WARNING,
    }
    payload = (json.dumps(report, indent=2, ensure_ascii=True) + "\n").encode("utf-8")
    _write_private_authorization(output, payload)
    _assert_ignored_untracked(repository, output)
    return report


def verify_owner_waiver_reveal_authorization(
    *,
    authorization_path: Path,
    response_path: Path,
    receipt_path: Path,
    packet_path: Path,
    reveal_path: Path,
    contract: RevealReadinessContract = PRODUCTION_CONTRACT,
) -> dict[str, Any]:
    """Reverify one private authorization and every exact pre-reveal binding."""

    _assert_regular_non_link_file(authorization_path, "owner-waiver authorization")
    report = _load_json(authorization_path, "owner-waiver authorization")
    _assert(report.get("report_id") == OWNER_WAIVER_ID, "authorization ID differs")
    _assert(report.get("report_version") == AUTHORIZATION_VERSION, "authorization version differs")
    _assert(report.get("software_version") == SOFTWARE_VERSION, "authorization software differs")
    _assert(report.get("repository") == REPOSITORY, "authorization repository differs")
    _assert(report.get("task_issue") == TASK_ISSUE, "authorization issue differs")
    _assert(
        report.get("parent_reconciliation_issue") == PARENT_RECONCILIATION_ISSUE,
        "authorization parent issue differs",
    )
    _assert(report.get("decision") == DECISION, "authorization decision differs")
    _parse_utc(report.get("authorized_at_utc"), "authorization time")
    _validate_full_sha(report.get("git_source_commit"), "authorization source commit")
    waiver = report.get("owner_waiver")
    evidence = report.get("evidence_state")
    scope = report.get("authorization_scope")
    checks = report.get("checks")
    _assert(isinstance(waiver, dict), "owner waiver is missing")
    _assert(isinstance(evidence, dict), "authorization evidence state is missing")
    _assert(isinstance(scope, dict), "authorization scope is missing")
    _assert(isinstance(checks, dict), "authorization checks are missing")
    _assert(waiver.get("reviewer_two_requirement_waived") is True, "owner waiver is absent")
    _assert(waiver.get("second_human_response_present") is False, "second-response state differs")
    _assert(
        waiver.get("single_reviewer_reduced_validation_acknowledged") is True,
        "reduced-validation acknowledgement is absent",
    )
    _assert(all(value == "pass" for value in checks.values()), "an authorization check did not pass")
    _assert(evidence.get("returned_independent_responses") == 1, "response count differs")
    _assert(evidence.get("second_human_response_present") is False, "reviewer-two state differs")
    _assert(evidence.get("reveal_opened_by_this_run") is False, "authorization claims reveal access")
    _assert(
        scope.get("reveal_authorized_for_later_private_reconciliation") is True,
        "later reconciliation reveal is not authorized",
    )
    _assert(scope.get("authorized_response_count") == 1, "authorized response count differs")
    _assert(
        all(
            report.get(key) is None
            for key in ("dataset_version", "split_version", "baseline_version", "model_version")
        ),
        "authorization advances a downstream analytical version",
    )

    response = _verify_exact_file(
        response_path,
        label="preserved first response",
        expected_bytes=contract.response_bytes,
        expected_sha256=contract.response_sha256,
    )
    receipt_binding = _verify_exact_file(
        receipt_path,
        label="first-response receipt",
        expected_bytes=contract.receipt_bytes,
        expected_sha256=contract.receipt_sha256,
    )
    packet = _verify_exact_file(
        packet_path,
        label="review packet",
        expected_bytes=contract.packet_bytes,
        expected_sha256=contract.packet_sha256,
    )
    reveal = _verify_exact_file(
        reveal_path,
        label="proposal reveal",
        expected_bytes=contract.reveal_bytes,
        expected_sha256=contract.reveal_sha256,
    )
    receipt = _load_json(receipt_path, "first-response receipt")
    _validate_receipt(receipt, contract=contract)
    _assert(report.get("response_binding", {}).get("sha256") == response["sha256"], "authorization response hash differs")
    _assert(report.get("receipt_binding", {}).get("sha256") == receipt_binding["sha256"], "authorization receipt hash differs")
    _assert(report.get("packet_binding", {}).get("sha256") == packet["sha256"], "authorization packet hash differs")
    _assert(report.get("reveal_binding", {}).get("sha256") == reveal["sha256"], "authorization reveal hash differs")
    return report
