"""Pre-reveal exact-byte custody for one completed Grandview owner response."""

from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
from typing import Any

import burnlens
from .grandview_owner_review_surface import RESPONSE_SCHEMA_VERSION, SURFACE_ID, SURFACE_VERSION
from .grandview_region_proposal import REPORT_ID as PROPOSAL_ID


LOCK_VERSION = "grandview-owner-response-exact-byte-lock-v0.1.0"
TASK_ISSUE = 517
EXPECTED_SURFACE_SHA256 = "7576ab36e97d026f9f706e67c75e3482b718818a3697e704a17ce7dc4c54369c"
EVIDENCE_ORIGIN = "owner-returned-grandview-response"


class GrandviewOwnerResponseLockError(RuntimeError):
    """Raised when exact response custody cannot be proven without reveal."""


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise GrandviewOwnerResponseLockError(message)


def _sha256(data: bytes) -> str:
    return sha256(data).hexdigest()


def _json(data: bytes, name: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise GrandviewOwnerResponseLockError(f"invalid UTF-8 JSON: {name}") from error
    _assert(isinstance(value, dict), f"JSON is not an object: {name}")
    return value


def _timestamp(value: Any, name: str) -> datetime:
    _assert(isinstance(value, str), f"{name} is not a timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise GrandviewOwnerResponseLockError(f"{name} is invalid") from error
    _assert(parsed.tzinfo is not None, f"{name} lacks timezone")
    return parsed


def _exact_keys(value: dict[str, Any], keys: set[str], name: str) -> None:
    _assert(set(value) == keys, f"{name} fields changed")


def _surface(surface_path: Path) -> tuple[dict[str, Any], bytes]:
    data = surface_path.read_bytes()
    _assert(_sha256(data) == EXPECTED_SURFACE_SHA256, "surface bytes changed")
    surface = _json(data, surface_path.name)
    _assert(surface.get("report_id") == SURFACE_ID, "surface identity changed")
    _assert(surface.get("report_version") == SURFACE_VERSION, "surface version changed")
    _assert(surface.get("response_schema_version") == RESPONSE_SCHEMA_VERSION, "surface schema changed")
    _assert(surface.get("summary", {}).get("owner_responses") == 0, "tracked surface contains responses")
    _assert(surface.get("summary", {}).get("labels_created") == 0, "tracked surface contains labels")
    return surface, data


def validate_envelope_without_reveal(surface: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    """Validate completion and immutable bindings without reading decision or note values."""
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
    _assert(isinstance(items, list) and len(items) == 2, "response must contain two records")
    bindings: list[dict[str, str]] = []
    for candidate, item in zip(candidates, items, strict=True):
        _assert(isinstance(item, dict), "response item is not an object")
        _exact_keys(item, {"candidate_id", "candidate_raster_sha256", "decision", "notes"}, "response item")
        _assert(item["candidate_id"] == candidate["candidate_id"], "candidate order or identity changed")
        _assert(item["candidate_raster_sha256"] == candidate["candidate_raster_sha256"], "candidate raster binding changed")
        bindings.append(
            {
                "candidate_id": item["candidate_id"],
                "candidate_raster_sha256": item["candidate_raster_sha256"],
            }
        )
    return {
        "started_at_utc": response["review_started_at_utc"],
        "completed_at_utc": response["review_completed_at_utc"],
        "response_record_count": len(items),
        "candidate_bindings": bindings,
        "decision_values_read": False,
        "note_values_read": False,
    }


def _assert_ignored(repository_root: Path, path: Path) -> None:
    try:
        relative = path.relative_to(repository_root)
    except ValueError as error:
        raise GrandviewOwnerResponseLockError("custody destination is outside the repository") from error
    result = subprocess.run(
        ["git", "-C", str(repository_root), "check-ignore", "--quiet", "--no-index", "--", str(relative)],
        check=False,
    )
    _assert(result.returncode == 0, "private output is not ignored")


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
    """Atomically preserve exact response and receipt before decision access."""
    _assert(len(git_source_commit) == 40, "git source commit must be a full SHA")
    surface, surface_bytes = _surface(surface_path)
    before = source_response_path.read_bytes()
    _assert(len(before) <= 1_000_000, "response exceeds bounded byte contract")
    response = _json(before, source_response_path.name)
    envelope = validate_envelope_without_reveal(surface, response)
    response_sha = _sha256(before)
    expected_name = f"{SURFACE_ID}-RESPONSE-{response_sha[:16]}.json"
    _assert(source_response_path.name == expected_name, "response filename does not match its exact byte hash")
    received = _timestamp(received_at_utc, "received time")
    completed = _timestamp(envelope["completed_at_utc"], "review completion")
    _assert(received >= completed, "received time predates review completion")

    try:
        destination_directory.relative_to(repository_root)
    except ValueError as error:
        raise GrandviewOwnerResponseLockError("custody destination is outside the repository") from error
    destination_directory.mkdir(parents=True, exist_ok=True)
    exact_path = destination_directory / expected_name
    receipt_path = destination_directory / f"{SURFACE_ID}-RECEIPT-{response_sha[:16]}.json"
    _assert_ignored(repository_root, exact_path)
    _assert_ignored(repository_root, receipt_path)
    receipt = {
        "report_id": f"{SURFACE_ID}-RECEIPT",
        "report_version": LOCK_VERSION,
        "received_at_utc": received_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": burnlens.__version__,
        "evidence_origin": EVIDENCE_ORIGIN,
        "origin_declared_by_operator": True,
        "surface_binding": {
            "report_id": SURFACE_ID,
            "run_id": surface["run_id"],
            "bytes": len(surface_bytes),
            "sha256": _sha256(surface_bytes),
        },
        "response_binding": {"bytes": len(before), "sha256": response_sha, **envelope},
        "exact_response_preserved_without_overwrite": True,
        "decisions_revealed": False,
        "qualifying_owner_response": None,
        "owner_yes_is_sufficient_without_other_gates": False,
        "label_set_version": None,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "decision": "PASS_EXACT_GRANDVIEW_OWNER_RESPONSE_LOCK_KEEP_DECISIONS_UNREVEALED",
    }
    receipt_bytes = (json.dumps(receipt, indent=2) + "\n").encode("utf-8")
    wrote_response = False
    wrote_receipt = False
    try:
        with exact_path.open("xb") as handle:
            handle.write(before)
            handle.flush()
            os.fsync(handle.fileno())
        wrote_response = True
        _assert(source_response_path.read_bytes() == before, "response source changed during preservation")
        _assert(exact_path.read_bytes() == before, "preserved response differs from source")
        with receipt_path.open("xb") as handle:
            wrote_receipt = True
            handle.write(receipt_bytes)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        if wrote_response and exact_path.exists():
            exact_path.unlink()
        raise GrandviewOwnerResponseLockError("refusing to overwrite exact response or receipt") from error
    except Exception:
        if wrote_response and exact_path.exists():
            exact_path.unlink()
        if wrote_receipt and receipt_path.exists():
            receipt_path.unlink()
        raise
    return exact_path, receipt_path, receipt
