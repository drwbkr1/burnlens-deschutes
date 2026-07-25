"""Acquire one exact USGS Ward Creek MTBS delivery into ignored custody."""

from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
from typing import Any, Callable
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from uuid import uuid4
import zipfile

from .provider_acquisition import USER_AGENT
from .replacement_event_reference_request import (
    BRANCH,
    CUSTODY_PATHS,
    EVENT_ID,
    MAP_ID,
    PUBLIC_REPORT_PATH as REQUEST_REPORT_PATH,
    REPOSITORY,
)


CONTRACT_VERSION = "ward-creek-reference-custody-v0.1.0"
UNIT_ID = "P2O4-T39-U03"
TASK_ISSUE = 554
REQUEST_RUN_ID = "BL-2026-07-24-ward-creek-reference-request-r001"
REQUEST_RECEIPT_BYTES = 3_433
REQUEST_RECEIPT_SHA256 = (
    "5f2949fecbd8b8a79de0d573b4fb1c04705ff69e0683901c776251b0cf1c5d98"
)
REQUEST_SOURCE_COMMIT = "21eff8dd85cbf795bef68e0f0113fe5272eb286e"
REQUEST_REPORT_BYTES = 3_413
REQUEST_REPORT_SHA256 = (
    "ad8f70ee3cbda8fcff77755486d0cb400a3a5b3c2bc09b99813e8a95abd3d54f"
)
ALLOWED_HOST = "edcintl.cr.usgs.gov"
DELIVERY_SENDER = "no-reply@usgs.gov"
DELIVERY_SUBJECT = "MTBS Web Viewer Order Complete"
CANONICAL_ARCHIVE_NAME = "ward-creek-mtbs-reference-delivery-001.zip"
DELIVERY_REPORT_PATH = (
    "samples/reference/phase-two/WARD-CREEK-REFERENCE-CUSTODY-2026-001.json"
)
MAX_ARCHIVE_BYTES = 1024 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 4 * 1024 * 1024 * 1024
CHUNK_BYTES = 1024 * 1024


class WardCreekReferenceCustodyError(RuntimeError):
    """The exact Ward Creek delivery transaction failed closed."""


def _file_digest(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(CHUNK_BYTES), b""):
            digest.update(block)
    return digest.hexdigest()


def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def _path_present(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.exists() or path.is_symlink() or bool(is_junction and is_junction())


def _validate_retrieval_url(value: str) -> None:
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or parsed.hostname != ALLOWED_HOST
        or parsed.port not in (None, 443)
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or not parsed.path.lower().endswith(".zip")
    ):
        raise WardCreekReferenceCustodyError(
            "private retrieval route failed the exact HTTPS host contract"
        )


def _safe_member(name: str) -> bool:
    path = PurePosixPath(name)
    return (
        bool(path.parts)
        and not path.is_absolute()
        and ".." not in path.parts
        and ":" not in path.parts[0]
        and "\\" not in name
    )


def inspect_archive(path: Path) -> dict[str, Any]:
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            names = [item.filename for item in infos]
            if not infos:
                raise WardCreekReferenceCustodyError("delivery ZIP is empty")
            if len(names) != len(set(names)):
                raise WardCreekReferenceCustodyError(
                    "delivery ZIP has duplicate members"
                )
            if any(not _safe_member(name) for name in names):
                raise WardCreekReferenceCustodyError(
                    "delivery ZIP has an unsafe member path"
                )
            if any(item.flag_bits & 0x1 for item in infos):
                raise WardCreekReferenceCustodyError(
                    "delivery ZIP has encrypted members"
                )
            if any(stat.S_ISLNK((item.external_attr >> 16) & 0xFFFF) for item in infos):
                raise WardCreekReferenceCustodyError(
                    "delivery ZIP has symbolic-link members"
                )
            uncompressed = sum(item.file_size for item in infos)
            if uncompressed > MAX_UNCOMPRESSED_BYTES:
                raise WardCreekReferenceCustodyError(
                    "delivery ZIP exceeds the uncompressed-byte limit"
                )
            if archive.testzip() is not None:
                raise WardCreekReferenceCustodyError(
                    "delivery ZIP failed its full CRC test"
                )
    except zipfile.BadZipFile as error:
        raise WardCreekReferenceCustodyError(
            "delivery is not a valid ZIP"
        ) from error
    lower_names = [name.casefold() for name in names]
    event_token = EVENT_ID.casefold()
    map_token = str(MAP_ID)
    if not any(event_token in name for name in lower_names):
        raise WardCreekReferenceCustodyError(
            "delivery ZIP lacks the exact event identity"
        )
    if not any(map_token in name for name in lower_names):
        raise WardCreekReferenceCustodyError(
            "delivery ZIP lacks the exact map identity"
        )
    notice_candidates = [
        name
        for name in names
        if any(
            token in PurePosixPath(name).name.casefold()
            for token in ("readme", "license", "copyright", "metadata", "notice")
        )
    ]
    return {
        "member_count": len(names),
        "file_count": sum(not item.is_dir() for item in infos),
        "directory_count": sum(item.is_dir() for item in infos),
        "uncompressed_bytes": uncompressed,
        "unique_safe_paths": True,
        "encrypted_members": 0,
        "symlink_members": 0,
        "crc_test_passed": True,
        "event_identity_present": True,
        "map_identity_present": True,
        "notice_candidate_count": len(notice_candidates),
        "notice_candidate_names": notice_candidates,
    }


def verify_repository_preflight(root: Path, git_source_commit: str) -> None:
    root = root.resolve()
    if re.fullmatch(r"[0-9a-f]{40}", git_source_commit) is None:
        raise WardCreekReferenceCustodyError("git source commit is invalid")
    checks = (
        (("rev-parse", "--show-toplevel"), root.as_posix(), "repository root mismatch"),
        (("rev-parse", "HEAD"), git_source_commit, "git source commit mismatch"),
        (("branch", "--show-current"), BRANCH, "branch mismatch"),
        (
            ("rev-parse", f"origin/{BRANCH}"),
            git_source_commit,
            "remote checkpoint mismatch",
        ),
    )
    for arguments, expected, reason in checks:
        result = _git(root, *arguments)
        observed = result.stdout.strip().replace("\\", "/")
        if result.returncode != 0 or observed != expected:
            raise WardCreekReferenceCustodyError(reason)
    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if status.returncode != 0 or status.stdout.strip():
        raise WardCreekReferenceCustodyError("worktree must be clean")
    receipt = root / CUSTODY_PATHS["request_directory"] / "request-receipt.json"
    if (
        not receipt.is_file()
        or receipt.stat().st_size != REQUEST_RECEIPT_BYTES
        or _file_digest(receipt) != REQUEST_RECEIPT_SHA256
    ):
        raise WardCreekReferenceCustodyError("request receipt binding mismatch")
    request = json.loads(receipt.read_text(encoding="utf-8"))
    if (
        request.get("run_id") != REQUEST_RUN_ID
        or request.get("git_source_commit") != REQUEST_SOURCE_COMMIT
        or request.get("event_id") != EVENT_ID
        or request.get("map_id") != MAP_ID
        or request.get("request", {}).get("state") != "ACCEPTED"
        or request.get("delivery", {}).get("state") != "PENDING_EMAIL_DELIVERY"
    ):
        raise WardCreekReferenceCustodyError("request receipt semantics mismatch")
    report = root / REQUEST_REPORT_PATH
    if (
        not report.is_file()
        or report.stat().st_size != REQUEST_REPORT_BYTES
        or _file_digest(report) != REQUEST_REPORT_SHA256
    ):
        raise WardCreekReferenceCustodyError("public request report binding mismatch")
    private_paths = (
        root / CUSTODY_PATHS["delivery_quarantine"],
        root / CUSTODY_PATHS["raw_package"],
        root / CUSTODY_PATHS["run_state"],
    )
    for path in private_paths:
        relative = path.relative_to(root).as_posix()
        if _git(root, "check-ignore", "--quiet", "--no-index", "--", relative).returncode != 0:
            raise WardCreekReferenceCustodyError(
                f"delivery custody path is not ignored: {relative}"
            )
        if _path_present(path):
            raise WardCreekReferenceCustodyError(
                "delivery custody target already exists; no retry or overwrite"
            )
    public = root / DELIVERY_REPORT_PATH
    if _path_present(public):
        raise WardCreekReferenceCustodyError(
            "delivery public report already exists; no retry or overwrite"
        )
    if _git(root, "check-ignore", "--quiet", "--no-index", "--", DELIVERY_REPORT_PATH).returncode != 1:
        raise WardCreekReferenceCustodyError("delivery public report is ignored")


def _write_json_no_overwrite(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(payload, indent=2) + "\n").encode("utf-8")
    try:
        with path.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError:
        raise WardCreekReferenceCustodyError(
            f"state exists; no overwrite allowed: {path.name}"
        ) from None


def acquire_delivery(
    *,
    repository_root: Path,
    retrieval_url: str,
    message_received_at_utc: str,
    captured_at_utc: str,
    delivery_expiry_text: str,
    run_id: str,
    git_source_commit: str,
    urlopen_fn: Callable[..., Any] = urlopen,
) -> dict[str, Any]:
    root = repository_root.resolve()
    _validate_retrieval_url(retrieval_url)
    verify_repository_preflight(root, git_source_commit)
    if not message_received_at_utc.endswith("Z") or not captured_at_utc.endswith("Z"):
        raise WardCreekReferenceCustodyError(
            "message and capture times must be explicit UTC"
        )
    if run_id != "BL-2026-07-24-ward-creek-reference-delivery-r001":
        raise WardCreekReferenceCustodyError("delivery run ID mismatch")
    quarantine = root / CUSTODY_PATHS["delivery_quarantine"]
    destination = root / CUSTODY_PATHS["raw_package"]
    state_path = root / CUSTODY_PATHS["run_state"]
    partial = quarantine / f"{CANONICAL_ARCHIVE_NAME}.partial"
    final = quarantine / CANONICAL_ARCHIVE_NAME
    quarantine.mkdir(parents=True)
    request = Request(
        retrieval_url,
        headers={"Accept": "application/zip", "User-Agent": USER_AGENT},
    )
    observed = 0
    digest = sha256()
    try:
        with urlopen_fn(request, timeout=600) as response:
            status_code = int(getattr(response, "status", response.getcode()))
            if status_code != 200:
                raise WardCreekReferenceCustodyError(
                    f"delivery returned HTTP {status_code}; no retry"
                )
            effective_url = response.geturl()
            _validate_retrieval_url(effective_url)
            if effective_url != retrieval_url:
                raise WardCreekReferenceCustodyError(
                    "delivery redirect or route substitution is not allowed"
                )
            content_length = response.headers.get("Content-Length")
            if content_length is not None and int(content_length) > MAX_ARCHIVE_BYTES:
                raise WardCreekReferenceCustodyError(
                    "delivery exceeds the archive-byte limit"
                )
            with partial.open("xb") as handle:
                while True:
                    block = response.read(CHUNK_BYTES)
                    if not block:
                        break
                    observed += len(block)
                    if observed > MAX_ARCHIVE_BYTES:
                        raise WardCreekReferenceCustodyError(
                            "delivery exceeds the archive-byte limit"
                        )
                    handle.write(block)
                    digest.update(block)
                handle.flush()
                os.fsync(handle.fileno())
        if content_length is not None and observed != int(content_length):
            raise WardCreekReferenceCustodyError(
                "delivery content length mismatch; no retry"
            )
        if observed == 0:
            raise WardCreekReferenceCustodyError("delivery is empty; no retry")
        partial.rename(final)
        inspection = inspect_archive(final)
        archive_sha256 = digest.hexdigest()
        registration = {
            "registration_schema_version": "0.1.0",
            "contract_version": CONTRACT_VERSION,
            "run_id": run_id,
            "captured_at_utc": captured_at_utc,
            "event_id": EVENT_ID,
            "map_id": MAP_ID,
            "filename": CANONICAL_ARCHIVE_NAME,
            "bytes": observed,
            "sha256": archive_sha256,
            "provider_route_retained": False,
            "inspection": inspection,
        }
        _write_json_no_overwrite(
            quarantine / ".burnlens-registration.json", registration
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        quarantine.rename(destination)
    except Exception as error:
        failure = {
            "contract_version": CONTRACT_VERSION,
            "unit_id": UNIT_ID,
            "run_id": run_id,
            "captured_at_utc": captured_at_utc,
            "event_id": EVENT_ID,
            "map_id": MAP_ID,
            "state": "DELIVERY_CUSTODY_FAILED_NO_AUTOMATIC_RETRY",
            "observed_partial_bytes": observed,
            "failure_type": type(error).__name__,
            "provider_route_retained": False,
        }
        _write_json_no_overwrite(
            state_path.with_name(f"{state_path.stem}-failure.json"),
            failure,
        )
        raise
    state = {
        "contract_version": CONTRACT_VERSION,
        "unit_id": UNIT_ID,
        "run_id": run_id,
        "captured_at_utc": captured_at_utc,
        "git_source_commit": git_source_commit,
        "event_id": EVENT_ID,
        "map_id": MAP_ID,
        "delivery_message": {
            "sender": DELIVERY_SENDER,
            "subject": DELIVERY_SUBJECT,
            "received_at_utc": message_received_at_utc,
            "expiry_text": delivery_expiry_text,
            "recipient": "WITHHELD_PRIVATE",
            "message_id": "WITHHELD_PRIVATE",
        },
        "archive": {
            "filename": CANONICAL_ARCHIVE_NAME,
            "bytes": observed,
            "sha256": archive_sha256,
            "provider_route_retained": False,
            "inspection": inspection,
        },
        "request_receipt": {
            "bytes": REQUEST_RECEIPT_BYTES,
            "sha256": REQUEST_RECEIPT_SHA256,
            "run_id": REQUEST_RUN_ID,
            "git_source_commit": REQUEST_SOURCE_COMMIT,
        },
        "state": "REGISTERED_EXACT_WARD_CREEK_MTBS_DELIVERY_TERMS_NOT_OPENED",
        "warning": (
            "Exact archive custody is not source fitness, label truth, official "
            "status, field validation, operational readiness, or emergency guidance."
        ),
    }
    _write_json_no_overwrite(state_path, state)
    public = {
        "report_id": "WARD-CREEK-REFERENCE-CUSTODY-2026-001",
        "report_schema_version": "0.1.0",
        "unit_id": UNIT_ID,
        "run_id": run_id,
        "captured_at_utc": captured_at_utc,
        "event_id": EVENT_ID,
        "map_id": MAP_ID,
        "trace": {
            "repository": REPOSITORY,
            "branch": BRANCH,
            "issue": TASK_ISSUE,
            "git_source_commit": git_source_commit,
            "request_report": {
                "path": REQUEST_REPORT_PATH,
                "bytes": REQUEST_REPORT_BYTES,
                "sha256": REQUEST_REPORT_SHA256,
            },
        },
        "delivery_message": {
            "sender_domain": "usgs.gov",
            "subject": DELIVERY_SUBJECT,
            "received_at_utc": message_received_at_utc,
            "expiry_text": delivery_expiry_text,
            "recipient": "WITHHELD_PRIVATE",
            "message_id": "WITHHELD_PRIVATE",
        },
        "archive": {
            "bytes": observed,
            "sha256": archive_sha256,
            "provider_route_retained": False,
            "inspection": inspection,
        },
        "gate_results": {
            "exact_request_binding": "pass",
            "exact_message_identity": "pass",
            "https_provider_host_no_substitution": "pass",
            "single_bounded_get": "pass",
            "safe_unique_unencrypted_no_symlink_zip": "pass",
            "full_crc": "pass",
            "event_and_map_identity": "pass",
            "terms_notices_and_native_pixels": "not executed",
            "candidate_label_dataset_split_baseline_model": "not created",
        },
        "decision": "PASS_WARD_CREEK_REFERENCE_CUSTODY_OPEN_EXACT_NOTICES_NEXT",
        "warning": state["warning"],
    }
    _write_json_no_overwrite(root / DELIVERY_REPORT_PATH, public)
    return public
