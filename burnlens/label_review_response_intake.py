"""Atomically preserve and receipt one BurnLens label-review response."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
from typing import Any, Iterable

from .label_review_handoff import WORKBENCH_VERSION
from .lock_label_review_response import (
    LOCK_REPORT_VERSION,
    RETURNED_INDEPENDENT_RESPONSE,
    SOFTWARE_BROWSER_FIXTURE,
    SOFTWARE_VERSION,
    build_response_lock,
)
from .optical_pair_evidence import WARNING


INTAKE_VERSION = "label-review-response-atomic-intake-v0.1.0"
MAX_RESPONSE_BYTES = 1_000_000
BUFFER_BYTES = 1024 * 1024


class LabelReviewResponseIntakeError(RuntimeError):
    """A fail-closed private response-intake failure."""


@dataclass(frozen=True)
class _SourceIdentity:
    device: int
    inode: int
    size: int
    modified_ns: int


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(BUFFER_BYTES):
            digest.update(chunk)
    return digest.hexdigest()


def _source_identity(path: Path) -> _SourceIdentity:
    metadata = path.stat(follow_symlinks=False)
    return _SourceIdentity(
        device=metadata.st_dev,
        inode=metadata.st_ino,
        size=metadata.st_size,
        modified_ns=metadata.st_mtime_ns,
    )


def _assert_regular_non_link_file(path: Path, label: str) -> None:
    try:
        metadata = path.stat(follow_symlinks=False)
    except OSError as error:
        raise LabelReviewResponseIntakeError(f"{label} is unavailable") from error
    if path.is_symlink() or not stat.S_ISREG(metadata.st_mode):
        raise LabelReviewResponseIntakeError(f"{label} must be a regular non-link file")
    if metadata.st_size <= 0 or metadata.st_size > MAX_RESPONSE_BYTES:
        raise LabelReviewResponseIntakeError(
            f"{label} must contain 1 to {MAX_RESPONSE_BYTES} bytes"
        )


def _validate_output_name(value: str, label: str) -> str:
    name = value.strip()
    if (
        not name
        or name in {".", ".."}
        or Path(name).name != name
        or "/" in name
        or "\\" in name
        or not name.lower().endswith(".json")
    ):
        raise LabelReviewResponseIntakeError(
            f"{label} must be one local JSON filename without path separators"
        )
    return name


def _normalize_hashes(values: Iterable[str]) -> set[str]:
    normalized: set[str] = set()
    for value in values:
        candidate = value.strip().lower()
        if len(candidate) != 64 or any(character not in "0123456789abcdef" for character in candidate):
            raise LabelReviewResponseIntakeError("a disallowed response SHA-256 is invalid")
        normalized.add(candidate)
    return normalized


def _git_path(repository_root: Path, path: Path) -> str:
    try:
        relative = path.relative_to(repository_root)
    except ValueError as error:
        raise LabelReviewResponseIntakeError(
            "custody outputs must stay inside the repository root"
        ) from error
    return relative.as_posix()


def _assert_ignored_untracked(repository_root: Path, path: Path) -> None:
    relative = _git_path(repository_root, path)
    ignored = subprocess.run(
        [
            "git",
            "-C",
            str(repository_root),
            "check-ignore",
            "--quiet",
            "--no-index",
            "--",
            relative,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if ignored.returncode != 0:
        if ignored.returncode == 1:
            raise LabelReviewResponseIntakeError(
                "custody output is not covered by repository ignore rules"
            )
        raise LabelReviewResponseIntakeError("git ignore verification failed")
    tracked = subprocess.run(
        [
            "git",
            "-C",
            str(repository_root),
            "ls-files",
            "--error-unmatch",
            "--",
            relative,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if tracked.returncode == 0:
        raise LabelReviewResponseIntakeError("custody output is already tracked")
    if tracked.returncode not in (1, 128):
        raise LabelReviewResponseIntakeError("git tracked-file verification failed")


def _write_temporary_response(source_path: Path, destination_directory: Path) -> tuple[Path, int, str]:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".burnlens-response-intake-",
        suffix=".tmp",
        dir=destination_directory,
    )
    temporary_path = Path(temporary_name)
    digest = sha256()
    byte_count = 0
    try:
        with source_path.open("rb") as source, os.fdopen(descriptor, "wb") as destination:
            while chunk := source.read(BUFFER_BYTES):
                byte_count += len(chunk)
                if byte_count > MAX_RESPONSE_BYTES:
                    raise LabelReviewResponseIntakeError(
                        f"response exceeds the {MAX_RESPONSE_BYTES}-byte intake limit"
                    )
                digest.update(chunk)
                destination.write(chunk)
            destination.flush()
            os.fsync(destination.fileno())
        return temporary_path, byte_count, digest.hexdigest()
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        temporary_path.unlink(missing_ok=True)
        raise


def _write_temporary_bytes(
    payload: bytes,
    destination_directory: Path,
    *,
    suffix: str,
) -> Path:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".burnlens-response-intake-",
        suffix=suffix,
        dir=destination_directory,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as destination:
            destination.write(payload)
            destination.flush()
            os.fsync(destination.fileno())
        return temporary_path
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        temporary_path.unlink(missing_ok=True)
        raise


def _promote_without_overwrite(temporary_path: Path, destination_path: Path) -> None:
    try:
        os.link(temporary_path, destination_path, follow_symlinks=False)
    except FileExistsError as error:
        raise LabelReviewResponseIntakeError(
            f"refusing to overwrite existing custody output {destination_path.name}"
        ) from error
    except OSError as error:
        raise LabelReviewResponseIntakeError(
            "same-directory no-overwrite custody promotion failed"
        ) from error
    temporary_path.unlink()


def intake_label_review_response(
    *,
    repository_root: Path,
    packet_path: Path,
    source_response_path: Path,
    custody_directory: Path,
    preserved_response_name: str,
    receipt_name: str,
    expected_reviewer_id: str,
    receipt_id: str,
    received_at_utc: str,
    run_id: str,
    git_source_commit: str,
    task_issue: int,
    disallowed_response_sha256: Iterable[str],
    disallowed_reviewer_ids: Iterable[str],
    evidence_origin: str = RETURNED_INDEPENDENT_RESPONSE,
) -> dict[str, Any]:
    """Validate, copy, revalidate, and receipt one exact response without overwrite."""

    if evidence_origin not in {RETURNED_INDEPENDENT_RESPONSE, SOFTWARE_BROWSER_FIXTURE}:
        raise LabelReviewResponseIntakeError("response evidence origin is invalid")
    reviewer_id = expected_reviewer_id.strip()
    if not reviewer_id or len(reviewer_id) > 120:
        raise LabelReviewResponseIntakeError("expected reviewer ID is missing or too long")
    response_name = _validate_output_name(preserved_response_name, "response output name")
    lock_name = _validate_output_name(receipt_name, "receipt output name")
    if response_name == lock_name:
        raise LabelReviewResponseIntakeError("response and receipt output names must differ")
    disallowed_hashes = _normalize_hashes(disallowed_response_sha256)
    disallowed_reviewers = {value.strip() for value in disallowed_reviewer_ids if value.strip()}
    if reviewer_id in disallowed_reviewers:
        raise LabelReviewResponseIntakeError("reviewer ID duplicates a disallowed custody slot")

    repository = repository_root.resolve(strict=True)
    if not (repository / ".git").exists():
        raise LabelReviewResponseIntakeError("repository root is not a Git worktree")
    unresolved_custody = custody_directory.absolute()
    if unresolved_custody.is_symlink():
        raise LabelReviewResponseIntakeError("custody directory must not be a symbolic link")
    custody = custody_directory.resolve(strict=False)
    _git_path(repository, custody)
    if custody == repository or custody == repository / ".git":
        raise LabelReviewResponseIntakeError("custody directory is not a valid ignored subdirectory")
    custody.mkdir(parents=True, exist_ok=True)
    if not custody.is_dir():
        raise LabelReviewResponseIntakeError("custody directory must be a real directory")
    custody = custody.resolve(strict=True)
    _git_path(repository, custody)

    source = source_response_path.resolve(strict=True)
    _assert_regular_non_link_file(source_response_path, "source response")
    try:
        source.relative_to(custody)
    except ValueError:
        pass
    else:
        raise LabelReviewResponseIntakeError(
            "source response must be outside the destination custody directory"
        )

    response_destination = custody / response_name
    receipt_destination = custody / lock_name
    if response_destination.exists() or receipt_destination.exists():
        raise LabelReviewResponseIntakeError("refusing to overwrite existing custody output")
    _assert_ignored_untracked(repository, response_destination)
    _assert_ignored_untracked(repository, receipt_destination)

    source_identity = _source_identity(source)
    source_receipt = build_response_lock(
        packet_path=packet_path,
        response_path=source,
        receipt_id=receipt_id,
        received_at_utc=received_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
        evidence_origin=evidence_origin,
        task_issue=task_issue,
        report_version=LOCK_REPORT_VERSION,
        software_version=SOFTWARE_VERSION,
    )
    if _source_identity(source) != source_identity:
        raise LabelReviewResponseIntakeError("source response changed during validation")
    source_hash = source_receipt["response_binding"]["sha256"]
    source_bytes = source_receipt["response_binding"]["bytes"]
    source_reviewer = source_receipt["response_binding"]["opaque_reviewer_id"]
    if source_hash in disallowed_hashes:
        raise LabelReviewResponseIntakeError("response duplicates disallowed custody evidence")
    if source_reviewer != reviewer_id:
        raise LabelReviewResponseIntakeError("response reviewer ID differs from the expected slot")
    if source_reviewer in disallowed_reviewers:
        raise LabelReviewResponseIntakeError("response reviewer ID duplicates existing custody")

    response_temporary: Path | None = None
    receipt_temporary: Path | None = None
    response_promoted = False
    receipt_promoted = False
    try:
        response_temporary, copied_bytes, copied_hash = _write_temporary_response(source, custody)
        if _source_identity(source) != source_identity:
            raise LabelReviewResponseIntakeError("source response changed during byte preservation")
        if _sha256_file(source) != source_hash or _source_identity(source) != source_identity:
            raise LabelReviewResponseIntakeError("source response changed during final source verification")
        if copied_bytes != source_bytes or copied_hash != source_hash:
            raise LabelReviewResponseIntakeError("preserved response differs from the validated source")
        if (
            response_temporary.stat().st_size != source_bytes
            or _sha256_file(response_temporary) != source_hash
        ):
            raise LabelReviewResponseIntakeError("temporary preserved response failed exact-byte verification")

        preserved_receipt = build_response_lock(
            packet_path=packet_path,
            response_path=response_temporary,
            receipt_id=receipt_id,
            received_at_utc=received_at_utc,
            run_id=run_id,
            git_source_commit=git_source_commit,
            evidence_origin=evidence_origin,
            task_issue=task_issue,
            report_version=LOCK_REPORT_VERSION,
            software_version=SOFTWARE_VERSION,
        )
        if preserved_receipt != source_receipt:
            raise LabelReviewResponseIntakeError(
                "preserved response receipt differs from the validated source receipt"
            )
        receipt_payload = (
            json.dumps(preserved_receipt, indent=2, ensure_ascii=True) + "\n"
        ).encode("utf-8")
        receipt_temporary = _write_temporary_bytes(
            receipt_payload,
            custody,
            suffix=".receipt.tmp",
        )

        _promote_without_overwrite(response_temporary, response_destination)
        response_temporary = None
        response_promoted = True
        _promote_without_overwrite(receipt_temporary, receipt_destination)
        receipt_temporary = None
        receipt_promoted = True

        preserved_hash = _sha256_file(response_destination)
        receipt_hash = _sha256_file(receipt_destination)
        if response_destination.stat().st_size != source_bytes or preserved_hash != source_hash:
            raise LabelReviewResponseIntakeError("promoted response failed exact-byte verification")
        if (
            receipt_destination.stat().st_size != len(receipt_payload)
            or receipt_destination.read_bytes() != receipt_payload
        ):
            raise LabelReviewResponseIntakeError("promoted receipt failed exact-byte verification")
        _assert_ignored_untracked(repository, response_destination)
        _assert_ignored_untracked(repository, receipt_destination)

        is_fixture = evidence_origin == SOFTWARE_BROWSER_FIXTURE
        decision = (
            "PASS_ATOMIC_SOFTWARE_FIXTURE_INTAKE_NO_HUMAN_EVIDENCE_NO_REVEAL"
            if is_fixture
            else "PASS_ATOMIC_RETURNED_RESPONSE_INTAKE_WITHHOLD_CONTENT_NO_REVEAL"
        )
        return {
            "intake_version": INTAKE_VERSION,
            "software_version": SOFTWARE_VERSION,
            "application_version": WORKBENCH_VERSION,
            "repository": "drwbkr1/burnlens-deschutes",
            "task_issue": task_issue,
            "git_source_commit": git_source_commit,
            "evidence_origin": evidence_origin,
            "origin_declared_by_operator": True,
            "origin_verified_by_software": False,
            "source_binding": {
                "bytes": source_bytes,
                "sha256": source_hash,
                "input_filename_retained": False,
                "input_path_retained": False,
            },
            "preserved_response_binding": {
                "bytes": response_destination.stat().st_size,
                "sha256": preserved_hash,
                "opaque_reviewer_id": reviewer_id,
                "input_filename_retained": False,
                "private_path_retained": False,
            },
            "receipt_binding": {
                "report_id": receipt_id,
                "run_id": run_id,
                "report_version": LOCK_REPORT_VERSION,
                "software_version": SOFTWARE_VERSION,
                "bytes": receipt_destination.stat().st_size,
                "sha256": receipt_hash,
                "private_filename_retained": False,
                "private_path_retained": False,
            },
            "checks": {
                "source_contract_validation": "pass",
                "source_stability_across_validation_copy_and_rehash": "pass",
                "same_directory_temporary_copy_fsync": "pass",
                "source_to_temporary_exact_bytes": "pass",
                "temporary_to_promoted_exact_bytes": "pass",
                "non_overwriting_link_promotion": "pass",
                "receipt_built_from_source_and_preserved_copy_identically": "pass",
                "ignored_untracked_private_storage": "pass",
                "duplicate_hash_and_reviewer_slot_rejection": "pass",
            },
            "qualifying_independent_human_response": False if is_fixture else None,
            "software_browser_fixture": is_fixture,
            "human_identity_verified_by_software": False,
            "reviewer_expertise_verified_by_software": False,
            "scientific_label_fitness_established": False,
            "reveal_authorized_by_this_intake": False,
            "response_comparison_performed": False,
            "adjudication_completed": False,
            "dataset_version": None,
            "split_version": None,
            "baseline_version": None,
            "model_version": None,
            "decision": decision,
            "warning": WARNING,
        }
    except BaseException:
        if receipt_promoted:
            receipt_destination.unlink(missing_ok=True)
        if response_promoted:
            response_destination.unlink(missing_ok=True)
        raise
    finally:
        if response_temporary is not None:
            response_temporary.unlink(missing_ok=True)
        if receipt_temporary is not None:
            receipt_temporary.unlink(missing_ok=True)
