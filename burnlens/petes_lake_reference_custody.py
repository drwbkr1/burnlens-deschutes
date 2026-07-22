"""Acquire one exact USGS Petes Lake MTBS delivery into ignored custody."""

from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
from typing import Any, Callable
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from uuid import uuid4

from .petes_lake_reference_delivery import (
    PetesLakeReferenceDeliveryError,
    inspect_delivery,
)
from .petes_lake_reference_request import CUSTODY_PATHS, EVENT_ID, MAP_ID
from .provider_acquisition import USER_AGENT


CONTRACT_VERSION = "petes-lake-reference-custody-v0.1.0"
REQUEST_RUN_ID = "BL-2026-07-21-petes-lake-reference-request-r001"
REQUEST_RECEIPT_BYTES = 4_775
REQUEST_RECEIPT_SHA256 = "8f29336c5c9f79a0ceb90b65f97f9434b71bbad8087b6dda36abf188a92aa595"
REQUEST_SOURCE_COMMIT = "a9e7b3fce9a06b5781fd84e2f5d4cf474523e16e"
ALLOWED_HOST = "edcintl.cr.usgs.gov"
DELIVERY_SENDER_DOMAIN = "usgs.gov"
DELIVERY_SUBJECT = "MTBS Web Viewer Order Complete"
CANONICAL_ARCHIVE_NAME = "petes-lake-mtbs-reference-delivery-001.zip"
MAX_ARCHIVE_BYTES = 1024 * 1024 * 1024


class PetesLakeReferenceCustodyError(RuntimeError):
    """The exact Petes Lake delivery transaction failed closed."""


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _file_digest(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _write_json_no_overwrite(path: Path, payload: dict[str, Any]) -> None:
    if path.exists():
        raise PetesLakeReferenceCustodyError(f"state exists; no overwrite allowed: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{uuid4().hex}")
    try:
        with temporary.open("xb") as handle:
            handle.write((json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
        temporary.rename(path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


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
        raise PetesLakeReferenceCustodyError("private retrieval route failed the exact HTTPS host contract")


def _validate_request_receipt(
    path: Path,
    *,
    expected_bytes: int = REQUEST_RECEIPT_BYTES,
    expected_sha256: str = REQUEST_RECEIPT_SHA256,
) -> dict[str, Any]:
    if not path.is_file():
        raise PetesLakeReferenceCustodyError("accepted request receipt is absent")
    raw = path.read_bytes()
    if len(raw) != expected_bytes or _digest(raw) != expected_sha256:
        raise PetesLakeReferenceCustodyError("accepted request receipt identity mismatch")
    try:
        receipt = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PetesLakeReferenceCustodyError("accepted request receipt is not JSON") from error
    if (
        receipt.get("run_id") != REQUEST_RUN_ID
        or receipt.get("git_source_commit") != REQUEST_SOURCE_COMMIT
        or receipt.get("event_id") != EVENT_ID
        or receipt.get("map_id") != MAP_ID
        or receipt.get("request", {}).get("state") != "ACCEPTED"
        or receipt.get("request", {}).get("mapping_ids") != [MAP_ID]
        or receipt.get("delivery", {}).get("state") != "PENDING_EMAIL_DELIVERY"
    ):
        raise PetesLakeReferenceCustodyError("accepted request receipt semantics mismatch")
    return receipt


def _paths(repository_root: Path) -> dict[str, Path]:
    quarantine = repository_root / CUSTODY_PATHS["delivery_quarantine"]
    raw = repository_root / CUSTODY_PATHS["raw_package"]
    final_state = repository_root / CUSTODY_PATHS["run_state"]
    stem = final_state.with_suffix("")
    return {
        "quarantine": quarantine,
        "quarantine_partial": quarantine / (CANONICAL_ARCHIVE_NAME + ".partial"),
        "quarantine_archive": quarantine / CANONICAL_ARCHIVE_NAME,
        "raw": raw,
        "raw_archive": raw / CANONICAL_ARCHIVE_NAME,
        "attempt_state": stem.with_name(stem.name + "-attempt-started.json"),
        "failure_state": stem.with_name(stem.name + "-failure.json"),
        "final_state": final_state,
    }


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
    expected_request_receipt_bytes: int = REQUEST_RECEIPT_BYTES,
    expected_request_receipt_sha256: str = REQUEST_RECEIPT_SHA256,
) -> dict[str, Any]:
    root = repository_root.resolve()
    if not (root / ".git").exists() or not (root / "pyproject.toml").is_file():
        raise PetesLakeReferenceCustodyError("repository root is not a BurnLens checkout")
    if not re.fullmatch(r"[0-9a-f]{40}", git_source_commit):
        raise PetesLakeReferenceCustodyError("git source commit must be an exact lowercase SHA-1")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z", message_received_at_utc):
        raise PetesLakeReferenceCustodyError("message received timestamp must be exact UTC")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z", captured_at_utc):
        raise PetesLakeReferenceCustodyError("capture timestamp must be exact UTC")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", delivery_expiry_text):
        raise PetesLakeReferenceCustodyError("delivery expiry must preserve the exact message text")
    _validate_retrieval_url(retrieval_url)
    request_receipt = root / CUSTODY_PATHS["request_directory"] / "request-receipt.json"
    _validate_request_receipt(
        request_receipt,
        expected_bytes=expected_request_receipt_bytes,
        expected_sha256=expected_request_receipt_sha256,
    )
    paths = _paths(root)
    if any(path.exists() for path in paths.values()):
        raise PetesLakeReferenceCustodyError("delivery custody target exists; no overwrite allowed")

    attempt = {
        "contract_version": CONTRACT_VERSION,
        "unit_id": "P2O4-T33-U04",
        "run_id": run_id,
        "message": {
            "sender_domain": DELIVERY_SENDER_DOMAIN,
            "subject": DELIVERY_SUBJECT,
            "received_at_utc": message_received_at_utc,
            "delivery_expiry_text": delivery_expiry_text,
            "delivery_expiry_timezone_stated": False,
            "exact_product_identity_present": True,
            "mailbox_read_only": True,
            "private_message_id_retained": False,
            "recipient_retained": False,
        },
        "captured_at_utc": captured_at_utc,
        "git_source_commit": git_source_commit,
        "event_id": EVENT_ID,
        "map_id": MAP_ID,
        "request_receipt": {
            "run_id": REQUEST_RUN_ID,
            "bytes": expected_request_receipt_bytes,
            "sha256": expected_request_receipt_sha256,
        },
        "retrieval": {
            "scheme": "https",
            "provider_host": ALLOWED_HOST,
            "private_path_retained": False,
            "private_url_retained": False,
            "automatic_retry": False,
            "attempts": 1,
        },
        "state": "DELIVERY_GET_ATTEMPT_STARTED_NO_AUTOMATIC_RETRY",
    }
    _write_json_no_overwrite(paths["attempt_state"], attempt)
    paths["quarantine"].mkdir(parents=True)
    try:
        request = Request(
            retrieval_url,
            headers={"User-Agent": USER_AGENT, "Accept": "application/zip, application/octet-stream"},
        )
        try:
            response_context = urlopen_fn(request, timeout=180)
            with response_context as response, paths["quarantine_partial"].open("xb") as handle:
                status = int(getattr(response, "status", 200))
                if status != 200:
                    raise PetesLakeReferenceCustodyError("delivery endpoint returned a non-success status")
                final_url = str(getattr(response, "geturl", lambda: retrieval_url)())
                _validate_retrieval_url(final_url)
                if final_url != retrieval_url:
                    raise PetesLakeReferenceCustodyError("delivery endpoint redirected from the exact private route")
                content_length_raw = response.headers.get("Content-Length")
                content_length = int(content_length_raw) if content_length_raw else None
                if content_length is not None and not 0 < content_length <= MAX_ARCHIVE_BYTES:
                    raise PetesLakeReferenceCustodyError("delivery content length is outside the bounded contract")
                digest = sha256()
                total = 0
                while block := response.read(1024 * 1024):
                    total += len(block)
                    if total > MAX_ARCHIVE_BYTES:
                        raise PetesLakeReferenceCustodyError("delivery exceeds the bounded archive size")
                    handle.write(block)
                    digest.update(block)
                handle.flush()
                os.fsync(handle.fileno())
        except PetesLakeReferenceCustodyError:
            raise
        except (OSError, ValueError) as error:
            raise PetesLakeReferenceCustodyError(
                "delivery transfer failed; private route withheld and no retry performed"
            ) from error
        if total <= 0 or (content_length is not None and total != content_length):
            raise PetesLakeReferenceCustodyError("delivery byte count does not match the exact response")
        with paths["quarantine_partial"].open("rb") as source:
            magic = source.read(4)
        if magic != b"PK\x03\x04":
            raise PetesLakeReferenceCustodyError("delivery is not a ZIP archive")
        paths["quarantine_partial"].rename(paths["quarantine_archive"])
        try:
            preflight = inspect_delivery([paths["quarantine_archive"]])
        except PetesLakeReferenceDeliveryError as error:
            raise PetesLakeReferenceCustodyError("delivery failed safe archive preflight") from error
        archive_hash = digest.hexdigest()
        observed = preflight["archives"][0]
        if observed["bytes"] != total or observed["sha256"] != archive_hash:
            raise PetesLakeReferenceCustodyError("delivery preflight identity mismatch")

        temporary_raw = paths["raw"].with_name(f".{paths['raw'].name}.tmp-{uuid4().hex}")
        temporary_raw.mkdir(parents=True)
        try:
            paths["quarantine_archive"].rename(temporary_raw / CANONICAL_ARCHIVE_NAME)
            temporary_raw.rename(paths["raw"])
        except Exception:
            shutil.rmtree(temporary_raw, ignore_errors=True)
            raise
        paths["quarantine"].rmdir()
        final_archive = paths["raw_archive"]
        if (
            not final_archive.is_file()
            or final_archive.stat().st_size != total
            or _file_digest(final_archive) != archive_hash
            or final_archive.stat().st_nlink != 1
        ):
            raise PetesLakeReferenceCustodyError("promoted delivery failed exact readback or link-count verification")
        report = {
            **attempt,
            "state": "PASS_EXACT_PETES_LAKE_MTBS_DELIVERY_CUSTODY",
            "completed_at_utc": captured_at_utc,
            "retrieval": {**attempt["retrieval"], "http_status": 200},
            "archive": {
                "canonical_filename": CANONICAL_ARCHIVE_NAME,
                "bytes": total,
                "sha256": archive_hash,
                "content_length": content_length,
                "single_link": True,
                "ignored_repository_local": True,
                "provider_filename_retained": False,
                "provider_route_retained": False,
            },
            "safe_delivery_preflight": preflight,
            "terms_and_native_pixels": "NOT_OPENED_PENDING_TERMS_FIRST_NATIVE_CONTRACT",
            "claim_boundaries": {
                "queue_acceptance_is_delivery": False,
                "custody_is_reference_fitness": False,
                "reference_pixels_accepted": False,
                "candidate_or_label_created": False,
                "dataset_split_baseline_model_created": False,
            },
            "next_dependency": "P2O4-T33-U04_TERMS_FIRST_NATIVE_CONTRACT",
        }
        _write_json_no_overwrite(paths["final_state"], report)
        return report
    except Exception as error:
        failure = {
            **attempt,
            "state": "DELIVERY_CUSTODY_FAILED_NO_AUTOMATIC_RETRY",
            "failure_code": (
                str(error)
                if isinstance(error, PetesLakeReferenceCustodyError)
                else "unexpected local custody failure"
            ),
            "private_route_retained": False,
            "retained_bytes": next(
                (
                    path.stat().st_size
                    for path in (
                        paths["quarantine_partial"],
                        paths["quarantine_archive"],
                        paths["raw_archive"],
                    )
                    if path.exists()
                ),
                None,
            ),
            "next_dependency": "retain and disposition this exact attempt before any new retrieval",
        }
        try:
            _write_json_no_overwrite(paths["failure_state"], failure)
        except Exception:
            pass
        raise
