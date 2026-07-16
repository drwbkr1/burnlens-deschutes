"""Verify two private response locks without publishing review content."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from typing import Any, Sequence

from PIL import Image, ImageDraw

from .label_review_handoff import (
    EXPECTED_PACKET_ID,
    EXPECTED_PACKET_RUN_ID,
    EXPECTED_PACKET_SHA256,
    WORKBENCH_VERSION,
)
from .optical_pair_evidence import WARNING, _font
from .verify_label_review_packet import (
    LabelReviewVerificationError,
    validate_completed_response,
)


REPORT_ID = "LABEL-REVIEW-DUAL-LOCK-READINESS-QA-2026-001"
SCHEMA_VERSION = "0.1.0"
REPORT_VERSION = "label-review-dual-lock-readiness-qa-v0.1.0"
SOFTWARE_VERSION = "0.17.0"
TASK_ISSUE = 394
PARENT_RESPONSE_ISSUE = 393
OPERATOR_REVEAL_STATUS = "withheld-unopened-after-lock"
RETURNED_INDEPENDENT_RESPONSE = "returned-independent-response"
SOFTWARE_BROWSER_FIXTURE = "software-browser-fixture"
EXPECTED_RECEIPT_SCHEMA = "0.1.0"
LEGACY_RECEIPT_VERSION = "label-review-response-integrity-lock-v0.2.0"
CURRENT_RECEIPT_VERSION = "label-review-response-integrity-lock-v0.3.0"
LEGACY_RECEIPT_SOFTWARE = "0.15.0"
CURRENT_RECEIPT_SOFTWARE = "0.17.0"
SUPPORTED_RECEIPT_IDENTITIES = {
    (LEGACY_RECEIPT_VERSION, LEGACY_RECEIPT_SOFTWARE),
    (CURRENT_RECEIPT_VERSION, CURRENT_RECEIPT_SOFTWARE),
}
ORIGINS = {RETURNED_INDEPENDENT_RESPONSE, SOFTWARE_BROWSER_FIXTURE}
RETURNED_DECISION = "PASS_RESPONSE_CONTRACT_AND_HASH_LOCK_DEFER_SCIENTIFIC_USE"
FIXTURE_DECISION = "PASS_SOFTWARE_FIXTURE_CONTRACT_AND_HASH_LOCK_NO_REVEAL"
RETURNED_REVEAL_RULE = (
    "operator may release reveal only after preserving this receipt and exact response bytes"
)
FIXTURE_REVEAL_RULE = "prohibited: software fixture cannot authorize proposal reveal"


class LabelReviewDualLockQaError(RuntimeError):
    """A fail-closed dual-lock verification failure."""


@dataclass(frozen=True)
class LockSpec:
    """Expected exact identity for one private response and receipt pair."""

    response_path: Path
    receipt_path: Path
    expected_response_sha256: str
    expected_response_bytes: int
    expected_receipt_sha256: str
    expected_receipt_bytes: int
    expected_reviewer_id: str
    expected_task_issue: int
    expected_receipt_version: str
    expected_receipt_software: str
    expected_origin: str


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise LabelReviewDualLockQaError(message)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise LabelReviewDualLockQaError(f"invalid JSON input {path.name}") from error
    if not isinstance(value, dict):
        raise LabelReviewDualLockQaError(f"JSON input {path.name} is not an object")
    return value


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_timestamp(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise LabelReviewDualLockQaError(f"{label} is missing")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise LabelReviewDualLockQaError(f"{label} is invalid") from error
    if parsed.tzinfo is None:
        raise LabelReviewDualLockQaError(f"{label} must be timezone-aware")
    return parsed


def _write_utf8_lf(path: Path, text: str) -> None:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(normalized.encode("utf-8"))


def _sensitive_response_strings(response: dict[str, Any]) -> list[str]:
    values: list[str] = []
    reviewer = response.get("reviewer")
    if isinstance(reviewer, dict):
        for key in ("burned_area_interpretation_experience", "attestation"):
            value = reviewer.get(key)
            if isinstance(value, str) and value.strip():
                values.append(value)
    responses = response.get("responses")
    if isinstance(responses, list):
        for item in responses:
            if isinstance(item, dict):
                note = item.get("notes")
                if isinstance(note, str) and note.strip():
                    values.append(note)
    return values


def _validate_spec(spec: LockSpec, index: int) -> None:
    label = f"lock {index}"
    _assert(spec.response_path.is_file(), f"{label} private response is missing")
    _assert(spec.receipt_path.is_file(), f"{label} private receipt is missing")
    _assert(spec.expected_response_bytes > 0, f"{label} response byte count is invalid")
    _assert(spec.expected_receipt_bytes > 0, f"{label} receipt byte count is invalid")
    _assert(len(spec.expected_response_sha256) == 64, f"{label} response SHA-256 is invalid")
    _assert(len(spec.expected_receipt_sha256) == 64, f"{label} receipt SHA-256 is invalid")
    _assert(bool(spec.expected_reviewer_id.strip()), f"{label} reviewer slot is missing")
    _assert(
        isinstance(spec.expected_task_issue, int)
        and not isinstance(spec.expected_task_issue, bool)
        and spec.expected_task_issue > 0,
        f"{label} task issue is invalid",
    )
    _assert(
        (spec.expected_receipt_version, spec.expected_receipt_software)
        in SUPPORTED_RECEIPT_IDENTITIES,
        f"{label} receipt/software identity is unsupported",
    )
    _assert(spec.expected_origin in ORIGINS, f"{label} origin is invalid")


def _validate_private_lock(
    *,
    packet: dict[str, Any],
    spec: LockSpec,
    index: int,
) -> tuple[dict[str, Any], list[str]]:
    _validate_spec(spec, index)
    label = f"lock {index}"
    response = _load_json(spec.response_path)
    receipt = _load_json(spec.receipt_path)
    response_sha256 = _sha256_file(spec.response_path)
    receipt_sha256 = _sha256_file(spec.receipt_path)
    response_bytes = spec.response_path.stat().st_size
    receipt_bytes = spec.receipt_path.stat().st_size

    _assert(response_bytes == spec.expected_response_bytes, f"{label} response byte count differs")
    _assert(response_sha256 == spec.expected_response_sha256, f"{label} response SHA-256 differs")
    _assert(receipt_bytes == spec.expected_receipt_bytes, f"{label} receipt byte count differs")
    _assert(receipt_sha256 == spec.expected_receipt_sha256, f"{label} receipt SHA-256 differs")
    _assert(response_bytes <= 1_000_000, f"{label} response exceeds the bounded byte contract")

    try:
        summary = validate_completed_response(
            packet,
            response,
            response_sha256=response_sha256,
        )
    except LabelReviewVerificationError as error:
        raise LabelReviewDualLockQaError(f"{label} response validation failed: {error}") from error
    _assert(summary["reviewer_id"] == spec.expected_reviewer_id, f"{label} reviewer slot differs")
    _assert(summary["unit_count"] == 56, f"{label} unit count differs")

    _assert(receipt.get("schema_version") == EXPECTED_RECEIPT_SCHEMA, f"{label} receipt schema differs")
    _assert(
        receipt.get("report_version") == spec.expected_receipt_version,
        f"{label} receipt version differs",
    )
    _assert(receipt.get("repository") == "drwbkr1/burnlens-deschutes", f"{label} repository differs")
    _assert(receipt.get("task_issue") == spec.expected_task_issue, f"{label} task issue differs")
    _assert(
        receipt.get("software_version") == spec.expected_receipt_software,
        f"{label} receipt software differs",
    )
    _assert(receipt.get("application_version") == WORKBENCH_VERSION, f"{label} application differs")
    _assert(receipt.get("evidence_origin") == spec.expected_origin, f"{label} origin differs")
    _assert(receipt.get("origin_declared_by_operator") is True, f"{label} origin declaration is absent")
    _assert(receipt.get("origin_verified_by_software") is False, f"{label} origin boundary differs")
    _assert(receipt.get("software_contract_validation") == "pass", f"{label} contract did not pass")
    _assert(
        receipt.get("response_contents_include_independence_and_blinding_attestations") is True,
        f"{label} response attestations are absent",
    )
    _assert(receipt.get("human_identity_verified_by_software") is False, f"{label} identity boundary differs")
    _assert(
        receipt.get("reviewer_expertise_verified_by_software") is False,
        f"{label} expertise boundary differs",
    )
    _assert(
        receipt.get("scientific_label_fitness_established") is False,
        f"{label} scientific-fitness boundary differs",
    )
    _assert(
        all(receipt.get(key) is None for key in ("dataset_version", "split_version", "baseline_version", "model_version")),
        f"{label} advances a downstream analytical version",
    )

    if spec.expected_origin == SOFTWARE_BROWSER_FIXTURE:
        _assert(receipt.get("software_browser_fixture") is True, f"{label} fixture flag differs")
        _assert(
            receipt.get("qualifying_independent_human_response") is False,
            f"{label} fixture is misclassified as human evidence",
        )
        _assert(receipt.get("decision") == FIXTURE_DECISION, f"{label} fixture decision differs")
        _assert(receipt.get("reveal_release") == FIXTURE_REVEAL_RULE, f"{label} fixture reveal rule differs")
    else:
        _assert(receipt.get("software_browser_fixture") is False, f"{label} returned response is a fixture")
        _assert(
            receipt.get("qualifying_independent_human_response") is None,
            f"{label} lets software qualify a human response",
        )
        _assert(receipt.get("decision") == RETURNED_DECISION, f"{label} returned decision differs")
        _assert(receipt.get("reveal_release") == RETURNED_REVEAL_RULE, f"{label} reveal rule differs")

    packet_binding = receipt.get("packet_binding")
    _assert(isinstance(packet_binding, dict), f"{label} packet binding is missing")
    _assert(packet_binding.get("report_id") == packet["report_id"], f"{label} packet ID differs")
    _assert(packet_binding.get("run_id") == packet["run_id"], f"{label} packet run differs")
    _assert(
        packet_binding.get("git_source_commit") == packet["git_source_commit"],
        f"{label} packet source differs",
    )
    _assert(packet_binding.get("sha256") == EXPECTED_PACKET_SHA256, f"{label} packet hash differs")
    _assert(
        packet_binding.get("response_schema_version") == packet["response_schema_version"],
        f"{label} response schema differs",
    )

    response_binding = receipt.get("response_binding")
    _assert(isinstance(response_binding, dict), f"{label} response binding is missing")
    _assert(response_binding.get("bytes") == response_bytes, f"{label} receipt response bytes differ")
    _assert(response_binding.get("sha256") == response_sha256, f"{label} receipt response hash differs")
    _assert(
        response_binding.get("opaque_reviewer_id") == spec.expected_reviewer_id,
        f"{label} receipt reviewer slot differs",
    )
    _assert(response_binding.get("unit_count") == summary["unit_count"], f"{label} receipt unit count differs")
    _assert(response_binding.get("label_counts") == summary["label_counts"], f"{label} private label counts differ")
    _assert(
        response_binding.get("insufficient_evidence_units") == summary["insufficient_evidence_units"],
        f"{label} private sufficiency count differs",
    )
    _assert(
        response_binding.get("uncertain_or_unusable_units") == summary["uncertain_or_unusable_units"],
        f"{label} private uncertainty count differs",
    )
    _assert(response_binding.get("input_filename_retained") is False, f"{label} retained an input filename")

    completed_at = _parse_timestamp(response.get("review_completed_at_utc"), f"{label} completion time")
    received_at = _parse_timestamp(receipt.get("received_at_utc"), f"{label} receipt time")
    _assert(received_at >= completed_at, f"{label} receipt predates response completion")
    receipt_id = receipt.get("report_id")
    receipt_run_id = receipt.get("run_id")
    receipt_source = receipt.get("git_source_commit")
    _assert(isinstance(receipt_id, str) and receipt_id.strip(), f"{label} receipt ID is missing")
    _assert(isinstance(receipt_run_id, str) and receipt_run_id.strip(), f"{label} receipt run is missing")
    _assert(
        isinstance(receipt_source, str) and len(receipt_source) == 40,
        f"{label} receipt source commit is invalid",
    )

    public_binding = {
        "lock_slot": index,
        "response": {
            "bytes": response_bytes,
            "sha256": response_sha256,
            "opaque_reviewer_slot": spec.expected_reviewer_id,
            "unit_count": summary["unit_count"],
            "completed_contract": True,
            "input_filename_retained": False,
            "content_distribution_withheld": True,
            "free_text_withheld": True,
        },
        "receipt": {
            "report_id": receipt_id,
            "run_id": receipt_run_id,
            "git_source_commit": receipt_source,
            "bytes": receipt_bytes,
            "sha256": receipt_sha256,
            "report_version": spec.expected_receipt_version,
            "software_version": spec.expected_receipt_software,
            "task_issue": spec.expected_task_issue,
            "evidence_origin": spec.expected_origin,
            "input_filename_retained": False,
        },
    }
    return public_binding, _sensitive_response_strings(response)


def build_dual_lock_qa(
    *,
    packet_path: Path,
    locks: Sequence[LockSpec],
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    operator_reveal_status: str,
) -> dict[str, Any]:
    _assert(packet_path.is_file(), "packet is missing")
    _assert(len(locks) == 2, "exactly two lock specifications are required")
    _assert(len(git_source_commit) == 40, "git source commit must be a full 40-character SHA")
    _assert(bool(run_id.strip()), "run ID is missing")
    _parse_timestamp(generated_at_utc, "generation time")
    _assert(
        operator_reveal_status == OPERATOR_REVEAL_STATUS,
        "operator reveal status must preserve the unopened post-lock state",
    )

    packet = _load_json(packet_path)
    packet_sha256 = _sha256_file(packet_path)
    _assert(packet.get("report_id") == EXPECTED_PACKET_ID, "packet identity differs")
    _assert(packet.get("run_id") == EXPECTED_PACKET_RUN_ID, "packet run differs")
    _assert(packet_sha256 == EXPECTED_PACKET_SHA256, "packet hash differs")

    bindings: list[dict[str, Any]] = []
    sensitive_values: list[str] = []
    for index, spec in enumerate(locks, start=1):
        binding, sensitive = _validate_private_lock(packet=packet, spec=spec, index=index)
        bindings.append(binding)
        sensitive_values.extend(sensitive)

    response_hashes = [item["response"]["sha256"] for item in bindings]
    reviewer_slots = [item["response"]["opaque_reviewer_slot"] for item in bindings]
    receipt_hashes = [item["receipt"]["sha256"] for item in bindings]
    receipt_ids = [item["receipt"]["report_id"] for item in bindings]
    receipt_runs = [item["receipt"]["run_id"] for item in bindings]
    task_issues = [item["receipt"]["task_issue"] for item in bindings]
    _assert(len(set(response_hashes)) == 2, "dual locks reuse the same response SHA-256")
    _assert(len(set(reviewer_slots)) == 2, "dual locks reuse the same reviewer slot")
    _assert(len(set(receipt_hashes)) == 2, "dual locks reuse the same receipt SHA-256")
    _assert(len(set(receipt_ids)) == 2, "dual locks reuse the same receipt ID")
    _assert(len(set(receipt_runs)) == 2, "dual locks reuse the same receipt run ID")
    _assert(len(set(task_issues)) == 2, "dual locks reuse the same task issue")

    origins = [item["receipt"]["evidence_origin"] for item in bindings]
    returned_count = origins.count(RETURNED_INDEPENDENT_RESPONSE)
    fixture_count = origins.count(SOFTWARE_BROWSER_FIXTURE)
    _assert(returned_count in (1, 2), "dual-lock QA requires at least one returned-response origin")
    custody_minimum_met = returned_count == 2
    readiness_mode = fixture_count == 1
    _assert(
        (readiness_mode and returned_count == 1) or (fixture_count == 0 and returned_count == 2),
        "dual-lock origin combination is unsupported",
    )

    if readiness_mode:
        decision = "PASS_MIXED_VERSION_DUAL_LOCK_READINESS_ONE_RETURNED_ONE_FIXTURE_NO_REVEAL"
        detail = (
            "The exact legacy returned-response lock and one current-version software-fixture lock "
            "pass two-pair custody, compatibility, distinctness, chronology, and content-withholding "
            "checks. The fixture is not human evidence, so the project remains at one returned response "
            "and the reveal remains prohibited."
        )
    else:
        decision = "PASS_TWO_RETURNED_RESPONSE_CUSTODY_LOCKS_WITHHOLD_CONTENT_DEFER_REVEAL"
        detail = (
            "Two exact operator-declared returned-response locks pass custody, distinctness, chronology, "
            "and content-withholding checks. This run does not verify reviewer qualifications or authorize "
            "reveal, comparison, adjudication, or dataset creation."
        )

    report = {
        "report_id": REPORT_ID,
        "schema_version": SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "parent_response_issue": PARENT_RESPONSE_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": WORKBENCH_VERSION,
        "packet_binding": {
            "report_id": packet["report_id"],
            "run_id": packet["run_id"],
            "git_source_commit": packet["git_source_commit"],
            "sha256": packet_sha256,
            "response_schema_version": packet["response_schema_version"],
            "review_unit_count": 56,
        },
        "private_lock_bindings": bindings,
        "checks": {
            "two_exact_response_receipt_pairs": "pass",
            "packet_binding": "pass",
            "completed_response_contracts": "pass: 56 of 56 units in both pairs",
            "receipt_response_bindings": "pass",
            "receipt_chronology": "pass",
            "distinct_response_hashes": "pass",
            "distinct_reviewer_slots": "pass",
            "distinct_receipt_hashes": "pass",
            "distinct_receipt_ids": "pass",
            "distinct_receipt_runs": "pass",
            "distinct_task_issues": "pass",
            "mixed_receipt_version_compatibility": (
                "pass"
                if {item["receipt"]["report_version"] for item in bindings}
                == {LEGACY_RECEIPT_VERSION, CURRENT_RECEIPT_VERSION}
                else "not exercised"
            ),
            "public_content_withholding": "pass",
        },
        "origin_classification": {
            "operator_declared_returned_responses": returned_count,
            "software_browser_fixtures": fixture_count,
            "origin_verified_by_software": False,
            "human_identity_verified_by_software": False,
            "reviewer_expertise_verified_by_software": False,
            "scientific_label_fitness_established": False,
        },
        "custody_state": {
            "minimum_operator_declared_returned_responses": 2,
            "operator_declared_returned_responses_present": returned_count,
            "minimum_custody_count_met": custody_minimum_met,
            "second_qualifying_response_established_by_software": False,
            "reveal_status": operator_reveal_status,
            "reveal_status_verified_by_software": False,
            "reveal_authorized_by_this_run": False,
            "response_comparison_performed": False,
            "adjudication_ready": False,
            "adjudication_completed": False,
        },
        "content_withholding": {
            "withheld": [
                "first-pass label distributions",
                "evidence-sufficiency distributions",
                "confidence distributions",
                "reason-code distributions",
                "reviewer experience and attestation text",
                "response start and completion timestamps",
                "free-text notes",
                "private filenames and private paths",
            ],
            "reason": (
                "Preserve reviewer independence and keep review content private until a separate "
                "verified reveal/comparison checkpoint is authorized after two real locks exist."
            ),
        },
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "decision": decision,
        "decision_detail": detail,
        "claims": {
            "proven": [
                "Two exact response/receipt pairs can be validated together without publishing review content.",
                "Legacy first-lock and current second-lock receipt identities can be checked explicitly and fail closed on drift.",
                "The two response hashes, reviewer slots, receipt hashes, receipt IDs, receipt runs, and task issues are distinct.",
                "The current readiness run retains one software fixture as non-human evidence and prohibits reveal.",
            ],
            "not_proven": [
                "A software fixture is not a second qualifying independent human response.",
                "Operator-declared origins are not software verification of identity, expertise, independence, or scientific fitness.",
                "No reveal, response comparison, inter-rater agreement, adjudication, accepted label, dataset, split, baseline, model, accuracy, field validation, deployment, official status, endorsement, or operational readiness is established.",
            ],
        },
        "warning": WARNING,
    }

    serialized = json.dumps(report, ensure_ascii=True)
    forbidden_tokens = (
        '"label_counts"',
        '"responses"',
        '"reason_codes"',
        '"burned_area_interpretation_experience"',
        '"review_started_at_utc"',
        '"review_completed_at_utc"',
    )
    for token in forbidden_tokens:
        _assert(token not in serialized, f"public report retains forbidden response field {token}")
    for spec in locks:
        _assert(spec.response_path.name not in serialized, "public report retains a private response filename")
        _assert(spec.receipt_path.name not in serialized, "public report retains a private receipt filename")
    for value in sensitive_values:
        _assert(value not in serialized, "public report retains private reviewer text")
    return report


def render_dual_lock_png(report: dict[str, Any], output_path: Path) -> None:
    if output_path.exists():
        raise LabelReviewDualLockQaError(f"refusing to overwrite existing output {output_path.name}")
    canvas = Image.new("RGB", (1800, 1320), "#f4f0e8")
    draw = ImageDraw.Draw(canvas)
    ink, muted, teal, orange = "#15211d", "#5d6b64", "#006b64", "#f05a28"
    draw.rectangle((0, 0, 1800, 190), fill="#132a26")
    draw.text((55, 28), "BURNLENS / PHASE TWO / OBJECTIVE FOUR", fill="#b9d8cf", font=_font(19))
    draw.text((55, 70), "DUAL-LOCK CUSTODY READINESS", fill="white", font=_font(36))
    draw.text(
        (55, 125),
        "Legacy first lock + current fixture lock / review content withheld / no reveal",
        fill="#b9d8cf",
        font=_font(16),
    )
    state = report["origin_classification"]
    metrics = [
        (str(state["operator_declared_returned_responses"]), "operator-declared return"),
        (str(state["software_browser_fixtures"]), "software fixture"),
        ("2", "distinct exact locks"),
        ("0", "completed adjudications"),
    ]
    for index, (value, label) in enumerate(metrics):
        left = 45 + index * 430
        draw.rounded_rectangle((left, 225, left + 390, 345), radius=15, fill="#e5efeb")
        draw.text((left + 24, 246), value, fill=teal, font=_font(30))
        draw.text((left + 24, 302), label, fill=muted, font=_font(14))

    draw.rounded_rectangle((45, 395, 1755, 875), radius=18, fill="#fffdf8", outline="#d4cec1", width=2)
    draw.text((72, 425), "WHAT THIS RUN PROVES", fill=teal, font=_font(21))
    lines = [
        "The exact legacy first lock and a current-version software-fixture lock pass together.",
        "Both 56-unit response contracts, receipt bindings, packet bindings, and chronologies pass.",
        "Response hashes, reviewer slots, receipt hashes, IDs, runs, and task issues are distinct.",
        "No label, confidence, sufficiency, reason, note, experience, timestamp, filename, or path is published.",
        "The software fixture remains non-human and cannot satisfy the second-response gate.",
    ]
    y = 480
    for line in lines:
        draw.ellipse((75, y + 7, 87, y + 19), fill=orange)
        draw.text((105, y), line, fill=ink, font=_font(17))
        y += 62

    first, second = report["private_lock_bindings"]
    draw.text((72, 805), "LOCK 1 RESPONSE SHA-256", fill=muted, font=_font(13))
    draw.text((310, 805), first["response"]["sha256"], fill=ink, font=_font(13))
    draw.text((72, 842), "LOCK 2 RESPONSE SHA-256", fill=muted, font=_font(13))
    draw.text((310, 842), second["response"]["sha256"], fill=ink, font=_font(13))

    draw.rounded_rectangle((45, 925, 1755, 1160), radius=18, fill="#e7f1ed")
    draw.text((72, 955), "BOUNDARY", fill=teal, font=_font(19))
    draw.text(
        (72, 1000),
        "Project state remains one returned response. A second human response is absent.",
        fill=ink,
        font=_font(18),
    )
    draw.text(
        (72, 1045),
        "Reveal, comparison, adjudication, accepted labels, dataset, split, baseline, and model remain deferred.",
        fill=ink,
        font=_font(16),
    )
    draw.text((72, 1092), f"Decision: {report['decision']}", fill=orange, font=_font(14))
    draw.text((55, 1210), f"Run {report['run_id']} / Git {report['git_source_commit']}", fill=muted, font=_font(13))
    draw.text((55, 1252), report["warning"], fill=orange, font=_font(13))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, format="PNG", optimize=False, compress_level=9)


def render_dual_lock_html(report: dict[str, Any]) -> str:
    rows = []
    for binding in report["private_lock_bindings"]:
        response = binding["response"]
        receipt = binding["receipt"]
        rows.append(
            "<tr>"
            f"<td>{binding['lock_slot']}</td>"
            f"<td><code>{escape(receipt['evidence_origin'])}</code></td>"
            f"<td>{response['unit_count']} / 56</td>"
            f"<td><code>{escape(response['sha256'])}</code></td>"
            f"<td><code>{escape(receipt['report_version'])}</code><br>{escape(receipt['software_version'])}</td>"
            "</tr>"
        )
    proven = "".join(f"<li>{escape(item)}</li>" for item in report["claims"]["proven"])
    not_proven = "".join(f"<li>{escape(item)}</li>" for item in report["claims"]["not_proven"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens dual-lock custody readiness</title>
<style>
body{{margin:0;font-family:Segoe UI,Arial,sans-serif;background:#f4f0e8;color:#15211d}}header{{background:#132a26;color:white;padding:2rem}}main{{max-width:1120px;margin:auto;padding:1.5rem}}.card{{background:#fffdf8;border:1px solid #d4cec1;border-radius:14px;padding:1.25rem;margin-bottom:1rem}}table{{border-collapse:collapse;width:100%}}th,td{{border-bottom:1px solid #ddd;padding:.65rem;text-align:left;vertical-align:top}}code{{overflow-wrap:anywhere}}.warning{{color:#b13d18;font-weight:700}}h2{{color:#006b64}}
</style></head>
<body><header><p>BurnLens / Phase Two / Objective Four</p><h1>Dual-lock custody readiness</h1><p>Exact private bindings verified without publishing review content.</p></header>
<main>
<section class="card"><h2>Decision</h2><p><code>{escape(report['decision'])}</code></p><p>{escape(report['decision_detail'])}</p></section>
<section class="card"><h2>Exact lock bindings</h2><table><thead><tr><th>Lock</th><th>Origin classification</th><th>Contract</th><th>Response SHA-256</th><th>Receipt protocol / software</th></tr></thead><tbody>{''.join(rows)}</tbody></table><p>Response distributions, reviewer text, response timestamps, private filenames, and private paths are withheld.</p></section>
<section class="card"><h2>Custody state</h2><p><strong>Operator-declared returned responses:</strong> {report['origin_classification']['operator_declared_returned_responses']} of {report['custody_state']['minimum_operator_declared_returned_responses']} required.<br><strong>Software fixtures:</strong> {report['origin_classification']['software_browser_fixtures']}.<br><strong>Reveal authorized by this run:</strong> no.<br><strong>Adjudication ready:</strong> no.</p></section>
<section class="card"><h2>Proven</h2><ul>{proven}</ul><h2>Not proven</h2><ul>{not_proven}</ul></section>
<section class="card"><h2>Traceability</h2><p><strong>Run:</strong> <code>{escape(report['run_id'])}</code><br><strong>Git source:</strong> <code>{escape(report['git_source_commit'])}</code><br><strong>Software:</strong> {escape(report['software_version'])}<br><strong>Application:</strong> {escape(report['application_version'])}<br><strong>Packet:</strong> <code>{escape(report['packet_binding']['sha256'])}</code><br><strong>Dataset / split / baseline / model:</strong> none / none / none / none</p></section>
<p class="warning">{escape(report['warning'])}</p>
</main></body></html>
"""


def write_dual_lock_outputs(
    report: dict[str, Any],
    *,
    json_path: Path,
    html_path: Path,
    png_path: Path,
) -> None:
    for path in (json_path, html_path, png_path):
        if path.exists():
            raise LabelReviewDualLockQaError(f"refusing to overwrite existing output {path.name}")
    _write_utf8_lf(json_path, json.dumps(report, indent=2, ensure_ascii=True) + "\n")
    _write_utf8_lf(html_path, render_dual_lock_html(report))
    render_dual_lock_png(report, png_path)
