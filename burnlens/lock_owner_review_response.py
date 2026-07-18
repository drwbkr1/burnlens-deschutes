"""Validate and no-overwrite lock exact BurnLens owner-review response bytes."""

from __future__ import annotations

import argparse
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Any

from .owner_review_surface import (
    ALLOWED_DECISIONS,
    PACKET_ID,
    PACKET_SHA256,
    PROTOCOL_VERSION,
    RESPONSE_SCHEMA_VERSION,
    SOFTWARE_VERSION,
    SURFACE_ID,
    OwnerReviewSurfaceError,
)


LOCK_VERSION = "owner-review-exact-byte-lock-v0.1.0"
OWNER_RETURNED_RESPONSE = "owner-returned-response"
SOFTWARE_BROWSER_FIXTURE = "software-browser-fixture"
EVIDENCE_ORIGINS = {OWNER_RETURNED_RESPONSE, SOFTWARE_BROWSER_FIXTURE}


def _json(data: bytes, name: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise OwnerReviewSurfaceError(f"invalid UTF-8 JSON: {name}") from error
    if not isinstance(value, dict):
        raise OwnerReviewSurfaceError(f"JSON is not an object: {name}")
    return value


def validate_response(surface: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    expected = {
        "response_schema_version": RESPONSE_SCHEMA_VERSION,
        "surface_id": SURFACE_ID,
        "surface_run_id": surface["run_id"],
        "packet_id": PACKET_ID,
        "packet_sha256": PACKET_SHA256,
        "owner_review_protocol_version": PROTOCOL_VERSION,
    }
    for key, value in expected.items():
        if response.get(key) != value:
            raise OwnerReviewSurfaceError(f"response binding mismatch: {key}")
    if response.get("completed") is not True:
        raise OwnerReviewSurfaceError("response is not completed")
    owner = response.get("owner")
    if not isinstance(owner, dict) or owner.get("owner_id") != "project-owner" or owner.get("attestation") is not True:
        raise OwnerReviewSurfaceError("owner attestation is incomplete")
    try:
        started = datetime.fromisoformat(response["review_started_at_utc"].replace("Z", "+00:00"))
        completed = datetime.fromisoformat(response["review_completed_at_utc"].replace("Z", "+00:00"))
    except (AttributeError, KeyError, ValueError) as error:
        raise OwnerReviewSurfaceError("review timestamps are invalid") from error
    if started.tzinfo is None or completed.tzinfo is None or completed < started:
        raise OwnerReviewSurfaceError("review timestamp order is invalid")
    responses = response.get("responses")
    units = surface.get("units")
    if not isinstance(responses, list) or not isinstance(units, list) or len(responses) != 56 or len(units) != 56:
        raise OwnerReviewSurfaceError("response must bind all 56 units")
    counts = {decision: 0 for decision in ALLOWED_DECISIONS}
    for expected_unit, item in zip(units, responses, strict=True):
        if not isinstance(item, dict):
            raise OwnerReviewSurfaceError("response unit is not an object")
        if item.get("sample_id") != expected_unit["sample_id"] or item.get("candidate_label") != expected_unit["candidate_label"]:
            raise OwnerReviewSurfaceError("response unit identity or proposition drift")
        decision = item.get("decision")
        if decision not in ALLOWED_DECISIONS:
            raise OwnerReviewSurfaceError("response decision is outside yes/no/uncertain")
        counts[decision] += 1
        notes = item.get("notes")
        if notes is not None and (not isinstance(notes, str) or len(notes) > 500):
            raise OwnerReviewSurfaceError("response note is invalid or too long")
    return {"decision_counts": counts, "started_at_utc": response["review_started_at_utc"], "completed_at_utc": response["review_completed_at_utc"]}


def lock_response(
    *,
    surface_path: Path,
    response_path: Path,
    destination_directory: Path,
    received_at_utc: str,
    run_id: str,
    git_source_commit: str,
    evidence_origin: str,
) -> tuple[Path, Path, dict[str, Any]]:
    surface_bytes = surface_path.read_bytes()
    response_bytes = response_path.read_bytes()
    if len(response_bytes) > 1_000_000:
        raise OwnerReviewSurfaceError("response exceeds bounded byte contract")
    surface = _json(surface_bytes, surface_path.name)
    response = _json(response_bytes, response_path.name)
    if surface.get("report_id") != SURFACE_ID or surface.get("task_issue") != 432:
        raise OwnerReviewSurfaceError("surface identity drift")
    summary = validate_response(surface, response)
    if evidence_origin not in EVIDENCE_ORIGINS:
        raise OwnerReviewSurfaceError("response evidence origin is invalid")
    if len(git_source_commit) != 40:
        raise OwnerReviewSurfaceError("git source commit must be a full SHA")
    try:
        received = datetime.fromisoformat(received_at_utc.replace("Z", "+00:00"))
        completed = datetime.fromisoformat(summary["completed_at_utc"].replace("Z", "+00:00"))
    except ValueError as error:
        raise OwnerReviewSurfaceError("receive time is invalid") from error
    if received.tzinfo is None or received < completed:
        raise OwnerReviewSurfaceError("receive time predates completion")
    response_sha = sha256(response_bytes).hexdigest()
    destination_directory.mkdir(parents=True, exist_ok=True)
    exact_path = destination_directory / f"{SURFACE_ID}-RESPONSE-{response_sha[:16]}.json"
    receipt_path = destination_directory / f"{SURFACE_ID}-RECEIPT-{response_sha[:16]}.json"
    receipt = {
        "report_id": f"{SURFACE_ID}-RECEIPT",
        "report_version": LOCK_VERSION,
        "received_at_utc": received_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 432,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "evidence_origin": evidence_origin,
        "origin_declared_by_operator": True,
        "software_browser_fixture": evidence_origin == SOFTWARE_BROWSER_FIXTURE,
        "qualifying_owner_response": None if evidence_origin == OWNER_RETURNED_RESPONSE else False,
        "surface_binding": {"report_id": SURFACE_ID, "run_id": surface["run_id"], "sha256": sha256(surface_bytes).hexdigest()},
        "response_binding": {"bytes": len(response_bytes), "sha256": response_sha, **summary},
        "exact_response_preserved_without_overwrite": True,
        "owner_yes_is_label_acceptance": False,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "decision": (
            "PASS_SOFTWARE_FIXTURE_EXACT_BYTE_LOCK_NO_OWNER_EVIDENCE"
            if evidence_origin == SOFTWARE_BROWSER_FIXTURE
            else "PASS_EXACT_OWNER_RESPONSE_LOCK_DEFER_LABEL_PROMOTION_GATES"
        ),
    }
    receipt_bytes = (json.dumps(receipt, indent=2) + "\n").encode("utf-8")
    wrote_exact = False
    try:
        with exact_path.open("xb") as handle:
            handle.write(response_bytes)
        wrote_exact = True
        with receipt_path.open("xb") as handle:
            handle.write(receipt_bytes)
    except FileExistsError as error:
        if wrote_exact:
            exact_path.unlink()
        raise OwnerReviewSurfaceError("refusing to overwrite an existing exact response or receipt") from error
    return exact_path, receipt_path, receipt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--surface", type=Path, required=True)
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--destination-directory", type=Path, required=True)
    parser.add_argument("--received-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument("--evidence-origin", choices=sorted(EVIDENCE_ORIGINS), required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        exact, receipt, report = lock_response(
            surface_path=args.surface.resolve(),
            response_path=args.response.resolve(),
            destination_directory=args.destination_directory.resolve(),
            received_at_utc=args.received_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
            evidence_origin=args.evidence_origin,
        )
    except (OwnerReviewSurfaceError, OSError, ValueError, KeyError) as error:
        print(f"OWNER_REVIEW_RESPONSE_LOCK_FAILED: {error}", file=sys.stderr)
        raise SystemExit(2) from error
    print(report["decision"])
    print(f"exact_response={exact}")
    print(f"receipt={receipt}")


if __name__ == "__main__":
    main()
