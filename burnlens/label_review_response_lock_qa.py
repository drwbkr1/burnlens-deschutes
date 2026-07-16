"""Create public, content-withheld QA evidence for one private response lock."""

from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from typing import Any

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


PUBLIC_REPORT_ID = "LABEL-REVIEW-RESPONSE-LOCK-QA-2026-001"
PUBLIC_SCHEMA_VERSION = "0.1.0"
PUBLIC_REPORT_VERSION = "label-review-response-public-lock-qa-v0.1.0"
SOFTWARE_VERSION = "0.16.0"
TASK_ISSUE = 384
EXPECTED_PRIVATE_LOCK_SCHEMA = "0.1.0"
EXPECTED_PRIVATE_LOCK_VERSION = "label-review-response-integrity-lock-v0.2.0"
EXPECTED_PRIVATE_LOCK_SOFTWARE = "0.15.0"
EXPECTED_EVIDENCE_ORIGIN = "returned-independent-response"
EXPECTED_LOCK_DECISION = "PASS_RESPONSE_CONTRACT_AND_HASH_LOCK_DEFER_SCIENTIFIC_USE"
EXPECTED_REVEAL_RELEASE = (
    "operator may release reveal only after preserving this receipt and exact response bytes"
)
OPERATOR_REVEAL_STATUS = "withheld-unopened-after-lock"
MINIMUM_RESPONSES_FOR_ADJUDICATION = 2


class LabelReviewResponseLockQaError(RuntimeError):
    """A fail-closed public response-lock evidence failure."""


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise LabelReviewResponseLockQaError(message)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise LabelReviewResponseLockQaError(f"invalid JSON input {path.name}") from error
    if not isinstance(value, dict):
        raise LabelReviewResponseLockQaError(f"JSON input {path.name} is not an object")
    return value


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_timestamp(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise LabelReviewResponseLockQaError(f"{label} is missing")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise LabelReviewResponseLockQaError(f"{label} is invalid") from error
    if parsed.tzinfo is None:
        raise LabelReviewResponseLockQaError(f"{label} must be timezone-aware")
    return parsed


def _write_utf8_lf(path: Path, text: str) -> None:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(normalized.encode("utf-8"))


def _sensitive_response_strings(response: dict[str, Any]) -> list[str]:
    values: list[str] = []
    reviewer = response.get("reviewer")
    if isinstance(reviewer, dict):
        for key in (
            "burned_area_interpretation_experience",
            "attestation",
        ):
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


def _validate_private_receipt(
    *,
    receipt: dict[str, Any],
    packet: dict[str, Any],
    response_summary: dict[str, Any],
    response_bytes: int,
    response_sha256: str,
    expected_reviewer_id: str,
) -> None:
    _assert(receipt.get("schema_version") == EXPECTED_PRIVATE_LOCK_SCHEMA, "private receipt schema differs")
    _assert(receipt.get("report_version") == EXPECTED_PRIVATE_LOCK_VERSION, "private receipt version differs")
    _assert(receipt.get("repository") == "drwbkr1/burnlens-deschutes", "private receipt repository differs")
    _assert(receipt.get("task_issue") == TASK_ISSUE, "private receipt task issue differs")
    _assert(receipt.get("software_version") == EXPECTED_PRIVATE_LOCK_SOFTWARE, "private receipt software differs")
    _assert(receipt.get("application_version") == WORKBENCH_VERSION, "private receipt application differs")
    _assert(receipt.get("evidence_origin") == EXPECTED_EVIDENCE_ORIGIN, "private receipt origin differs")
    _assert(receipt.get("origin_declared_by_operator") is True, "operator origin declaration is absent")
    _assert(receipt.get("origin_verified_by_software") is False, "software origin boundary differs")
    _assert(receipt.get("software_contract_validation") == "pass", "private receipt contract did not pass")
    _assert(
        receipt.get("response_contents_include_independence_and_blinding_attestations") is True,
        "private receipt attestation state differs",
    )
    _assert(receipt.get("software_browser_fixture") is False, "returned response is misclassified as a fixture")
    _assert(
        receipt.get("qualifying_independent_human_response") is None,
        "private receipt must not let software qualify the reviewer",
    )
    _assert(receipt.get("human_identity_verified_by_software") is False, "identity boundary differs")
    _assert(receipt.get("reviewer_expertise_verified_by_software") is False, "expertise boundary differs")
    _assert(receipt.get("scientific_label_fitness_established") is False, "fitness boundary differs")
    _assert(receipt.get("reveal_release") == EXPECTED_REVEAL_RELEASE, "private receipt reveal rule differs")
    _assert(receipt.get("decision") == EXPECTED_LOCK_DECISION, "private receipt decision differs")
    _assert(
        all(receipt.get(key) is None for key in ("dataset_version", "split_version", "baseline_version", "model_version")),
        "private receipt advances a downstream analytical version",
    )

    packet_binding = receipt.get("packet_binding")
    _assert(isinstance(packet_binding, dict), "private receipt packet binding is missing")
    _assert(packet_binding.get("report_id") == packet["report_id"], "receipt packet ID differs")
    _assert(packet_binding.get("run_id") == packet["run_id"], "receipt packet run differs")
    _assert(packet_binding.get("git_source_commit") == packet["git_source_commit"], "receipt packet source differs")
    _assert(packet_binding.get("sha256") == EXPECTED_PACKET_SHA256, "receipt packet hash differs")
    _assert(
        packet_binding.get("response_schema_version") == packet["response_schema_version"],
        "receipt response schema differs",
    )

    response_binding = receipt.get("response_binding")
    _assert(isinstance(response_binding, dict), "private receipt response binding is missing")
    _assert(response_binding.get("bytes") == response_bytes, "receipt response byte count differs")
    _assert(response_binding.get("sha256") == response_sha256, "receipt response hash differs")
    _assert(response_binding.get("opaque_reviewer_id") == expected_reviewer_id, "receipt reviewer slot differs")
    _assert(response_binding.get("unit_count") == response_summary["unit_count"], "receipt unit count differs")
    _assert(response_binding.get("label_counts") == response_summary["label_counts"], "private label counts differ")
    _assert(
        response_binding.get("insufficient_evidence_units")
        == response_summary["insufficient_evidence_units"],
        "private evidence-sufficiency count differs",
    )
    _assert(
        response_binding.get("uncertain_or_unusable_units")
        == response_summary["uncertain_or_unusable_units"],
        "private uncertainty count differs",
    )
    _assert(response_binding.get("input_filename_retained") is False, "private receipt retained an input filename")


def build_public_response_lock_qa(
    *,
    packet_path: Path,
    response_path: Path,
    receipt_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    expected_response_sha256: str,
    expected_response_bytes: int,
    expected_receipt_sha256: str,
    expected_receipt_bytes: int,
    expected_reviewer_id: str,
    operator_reveal_status: str,
) -> dict[str, Any]:
    for path, label in (
        (packet_path, "packet"),
        (response_path, "private response"),
        (receipt_path, "private receipt"),
    ):
        _assert(path.is_file(), f"{label} is missing")
    _assert(len(git_source_commit) == 40, "git source commit must be a full 40-character SHA")
    _parse_timestamp(generated_at_utc, "public evidence generation time")
    _assert(bool(run_id.strip()), "run ID is missing")
    _assert(
        operator_reveal_status == OPERATOR_REVEAL_STATUS,
        "operator reveal status must preserve the unopened post-lock state",
    )
    _assert(expected_response_bytes > 0, "expected response byte count is invalid")
    _assert(expected_receipt_bytes > 0, "expected receipt byte count is invalid")
    _assert(len(expected_response_sha256) == 64, "expected response SHA-256 is invalid")
    _assert(len(expected_receipt_sha256) == 64, "expected receipt SHA-256 is invalid")
    _assert(bool(expected_reviewer_id.strip()), "expected reviewer slot is missing")

    packet = _load_json(packet_path)
    response = _load_json(response_path)
    receipt = _load_json(receipt_path)
    packet_sha256 = _sha256_file(packet_path)
    response_sha256 = _sha256_file(response_path)
    receipt_sha256 = _sha256_file(receipt_path)
    response_bytes = response_path.stat().st_size
    receipt_bytes = receipt_path.stat().st_size

    _assert(packet.get("report_id") == EXPECTED_PACKET_ID, "packet identity differs")
    _assert(packet.get("run_id") == EXPECTED_PACKET_RUN_ID, "packet run differs")
    _assert(packet_sha256 == EXPECTED_PACKET_SHA256, "packet hash differs")
    _assert(response_bytes == expected_response_bytes, "private response byte count differs")
    _assert(response_sha256 == expected_response_sha256, "private response SHA-256 differs")
    _assert(receipt_bytes == expected_receipt_bytes, "private receipt byte count differs")
    _assert(receipt_sha256 == expected_receipt_sha256, "private receipt SHA-256 differs")
    _assert(response_bytes <= 1_000_000, "private response exceeds the bounded byte contract")

    try:
        response_summary = validate_completed_response(
            packet,
            response,
            response_sha256=response_sha256,
        )
    except LabelReviewVerificationError as error:
        raise LabelReviewResponseLockQaError(f"private response validation failed: {error}") from error
    _assert(response_summary["reviewer_id"] == expected_reviewer_id, "private response reviewer slot differs")
    _assert(response_summary["unit_count"] == 56, "private response unit count differs")
    _validate_private_receipt(
        receipt=receipt,
        packet=packet,
        response_summary=response_summary,
        response_bytes=response_bytes,
        response_sha256=response_sha256,
        expected_reviewer_id=expected_reviewer_id,
    )

    received_at = _parse_timestamp(receipt.get("received_at_utc"), "private receipt time")
    completed_at = _parse_timestamp(response.get("review_completed_at_utc"), "private response completion time")
    _assert(received_at >= completed_at, "private receipt predates response completion")
    receipt_id = receipt.get("report_id")
    receipt_run_id = receipt.get("run_id")
    receipt_source_commit = receipt.get("git_source_commit")
    _assert(isinstance(receipt_id, str) and bool(receipt_id.strip()), "private receipt ID is missing")
    _assert(isinstance(receipt_run_id, str) and bool(receipt_run_id.strip()), "private receipt run is missing")
    _assert(
        isinstance(receipt_source_commit, str) and len(receipt_source_commit) == 40,
        "private receipt source commit is invalid",
    )

    report = {
        "report_id": PUBLIC_REPORT_ID,
        "schema_version": PUBLIC_SCHEMA_VERSION,
        "report_version": PUBLIC_REPORT_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": WORKBENCH_VERSION,
        "packet_binding": {
            "report_id": packet["report_id"],
            "run_id": packet["run_id"],
            "git_source_commit": packet["git_source_commit"],
            "sha256": packet_sha256,
            "response_schema_version": packet["response_schema_version"],
        },
        "private_response_binding": {
            "bytes": response_bytes,
            "sha256": response_sha256,
            "opaque_reviewer_slot": expected_reviewer_id,
            "unit_count": response_summary["unit_count"],
            "completed_contract": True,
            "input_filename_retained": False,
            "content_distribution_withheld": True,
            "free_text_withheld": True,
        },
        "private_receipt_binding": {
            "report_id": receipt_id,
            "run_id": receipt_run_id,
            "git_source_commit": receipt_source_commit,
            "received_at_utc": receipt["received_at_utc"],
            "bytes": receipt_bytes,
            "sha256": receipt_sha256,
            "decision": receipt["decision"],
            "evidence_origin": receipt["evidence_origin"],
            "input_filename_retained": False,
        },
        "checks": {
            "exact_response_bytes": "pass",
            "exact_private_receipt_bytes": "pass",
            "packet_binding": "pass",
            "completed_response_contract": "pass",
            "receipt_response_binding": "pass",
            "response_completed_before_receipt": True,
            "proposal_value_fields_absent": True,
            "independence_and_blinding_attestations_present": True,
            "public_content_withholding": "pass",
        },
        "content_withholding": {
            "withheld_until_second_response_lock": [
                "first-pass label distribution",
                "evidence-sufficiency distribution",
                "confidence distribution",
                "reason-code distribution",
                "free-text response notes",
                "reviewer experience statement",
                "response start and completion timestamps",
            ],
            "reason": (
                "Protect the independence of a subsequent reviewer and avoid unnecessary disclosure "
                "before the required second response is preserved and locked."
            ),
        },
        "operator_declarations": {
            "reveal_status": operator_reveal_status,
            "reveal_status_verified_by_software": False,
            "response_origin": EXPECTED_EVIDENCE_ORIGIN,
            "response_origin_verified_by_software": False,
        },
        "returned_response_count": 1,
        "minimum_responses_for_adjudication": MINIMUM_RESPONSES_FOR_ADJUDICATION,
        "adjudication_ready": False,
        "adjudication_completed": False,
        "scientific_label_fitness_established": False,
        "human_identity_verified_by_software": False,
        "reviewer_expertise_verified_by_software": False,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "decision": "PASS_FIRST_RETURNED_RESPONSE_CONTRACT_AND_HASH_LOCK_WITHHOLD_CONTENT_DEFER_DATASET",
        "decision_detail": (
            "One exact returned response and its pre-reveal operator receipt pass byte, packet, "
            "contract, binding, and chronology checks. Response distributions and free text remain "
            "withheld until the required second response is locked. Software does not verify the "
            "reviewer or establish scientific label fitness."
        ),
        "claims": {
            "proven": [
                "One exact 56-unit returned response passes the proposal-free completed-response contract.",
                "The preserved private response and private receipt match their recorded byte counts and SHA-256 digests.",
                "The receipt binds the exact response to the shipped packet and was recorded after response completion.",
                "The public artifact excludes response distributions, free text, experience text, response timestamps, and private filenames.",
            ],
            "not_proven": [
                "Operator-declared origin and reveal status are not software verification of reviewer identity, expertise, independence, or file-access history.",
                "One response is not adjudication readiness, label fitness, inter-rater agreement, field validation, or accuracy.",
                "No accepted label set, dataset, split, baseline, model, deployment, official status, endorsement, or operational readiness exists.",
            ],
        },
        "warning": WARNING,
    }

    serialized = json.dumps(report, ensure_ascii=True)
    forbidden_keys = (
        '"label_counts"',
        '"responses"',
        '"reason_codes"',
        '"burned_area_interpretation_experience"',
        '"review_started_at_utc"',
        '"review_completed_at_utc"',
    )
    for token in forbidden_keys:
        _assert(token not in serialized, f"public report retains forbidden response field {token}")
    _assert(response_path.name not in serialized, "public report retains the private response filename")
    _assert(receipt_path.name not in serialized, "public report retains the private receipt filename")
    for value in _sensitive_response_strings(response):
        _assert(value not in serialized, "public report retains private reviewer text")
    return report


def render_public_response_lock_png(report: dict[str, Any], output_path: Path) -> None:
    if output_path.exists():
        raise LabelReviewResponseLockQaError(f"refusing to overwrite existing output {output_path.name}")
    canvas = Image.new("RGB", (1800, 1320), "#f4f0e8")
    draw = ImageDraw.Draw(canvas)
    ink, muted, teal, orange = "#15211d", "#5d6b64", "#006b64", "#f05a28"
    draw.rectangle((0, 0, 1800, 190), fill="#132a26")
    draw.text((55, 28), "BURNLENS / PHASE TWO / OBJECTIVE FOUR", fill="#b9d8cf", font=_font(19))
    draw.text((55, 70), "FIRST RETURNED RESPONSE / HASH LOCK", fill="white", font=_font(36))
    draw.text(
        (55, 125),
        "Exact private bytes verified / public content withheld / reveal remains operator-withheld",
        fill="#b9d8cf",
        font=_font(16),
    )
    metrics = [
        ("56/56", "contract-complete units"),
        ("1", "returned response locked"),
        ("2", "responses required"),
        ("0", "completed adjudications"),
    ]
    for index, (value, label) in enumerate(metrics):
        left = 45 + index * 430
        draw.rounded_rectangle((left, 225, left + 390, 345), radius=15, fill="#e5efeb")
        draw.text((left + 24, 246), value, fill=teal, font=_font(30))
        draw.text((left + 24, 302), label, fill=muted, font=_font(14))

    draw.rounded_rectangle((45, 395, 1755, 870), radius=18, fill="#fffdf8", outline="#d4cec1", width=2)
    draw.text((72, 425), "VERIFIED WITHOUT PUBLISHING REVIEW CONTENT", fill=teal, font=_font(21))
    lines = [
        "The exact returned file matches the operator-supplied byte count and SHA-256 digest.",
        "All 56 response units, response domains, packet binding, and proposal-free contract pass.",
        "The private receipt matches its exact digest and binds the same response, packet, issue, and chronology.",
        "First-pass distributions, reasons, confidence, experience text, timestamps, and notes remain withheld.",
        "One response is preserved; a second qualifying response is required before adjudication.",
        "Software does not verify reviewer identity, expertise, independence, scientific fitness, or reveal history.",
    ]
    for index, line in enumerate(lines):
        draw.text((88, 485 + index * 58), f"{index + 1}. {line}", fill=ink, font=_font(15))
    draw.text((72, 825), report["decision"], fill=orange, font=_font(16))

    draw.rounded_rectangle((45, 925, 1755, 1120), radius=18, fill="#e5efeb")
    draw.text((72, 952), "CRYPTOGRAPHIC BINDINGS", fill=teal, font=_font(18))
    draw.text(
        (72, 1000),
        f"response sha256  {report['private_response_binding']['sha256']}",
        fill=ink,
        font=_font(12),
    )
    draw.text(
        (72, 1040),
        f"receipt sha256   {report['private_receipt_binding']['sha256']}",
        fill=ink,
        font=_font(12),
    )
    trace = (
        f"run {report['run_id']} / source {report['git_source_commit'][:12]} / "
        f"software {report['software_version']} / receipt {report['private_receipt_binding']['run_id']}"
    )
    draw.text((45, 1170), trace, fill=muted, font=_font(11))
    draw.text((45, 1210), "dataset none / split none / baseline none / model none / reveal withheld", fill=orange, font=_font(14))
    draw.text((45, 1260), report["warning"], fill="#33443e", font=_font(9))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, format="PNG", optimize=False)


def render_public_response_lock_html(report: dict[str, Any], output_path: Path) -> None:
    if output_path.exists():
        raise LabelReviewResponseLockQaError(f"refusing to overwrite existing output {output_path.name}")
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens first returned response hash lock</title>
<style>
body{{margin:0;background:#f4f0e8;color:#15211d;font:16px/1.55 system-ui,sans-serif}}header{{background:#132a26;color:white;padding:3rem max(5vw,2rem)}}header p{{color:#b9d8cf}}main{{max-width:1180px;margin:auto;padding:2.5rem 1.5rem 5rem}}.warning{{background:#fff1ca;border-left:6px solid #d87618;padding:1rem;font-weight:650}}.card{{background:#fffdf8;border:1px solid #d9d1c4;border-radius:12px;padding:1.2rem;margin:1.2rem 0}}.decision{{border:2px solid #f05a28}}code{{overflow-wrap:anywhere}}table{{width:100%;border-collapse:collapse}}th,td{{padding:.65rem;border-bottom:1px solid #ddd5c9;text-align:left}}
</style></head>
<body><header><p>BurnLens / Phase Two / Objective Four</p><h1>First returned response: public hash-lock evidence</h1><p>Exact private bytes verified. Review content withheld until a second response is locked.</p></header>
<main><p class="warning">{escape(report['warning'])}</p>
<section class="card decision"><h2>Decision</h2><p><strong>{escape(report['decision'])}</strong></p><p>{escape(report['decision_detail'])}</p></section>
<section class="card"><h2>Public proof</h2><table><tbody>
<tr><th>Returned responses preserved</th><td>{report['returned_response_count']} of {report['minimum_responses_for_adjudication']} required before adjudication</td></tr>
<tr><th>Completed response contract</th><td>{report['private_response_binding']['unit_count']} of 56 units</td></tr>
<tr><th>Private response SHA-256</th><td><code>{escape(report['private_response_binding']['sha256'])}</code></td></tr>
<tr><th>Private response bytes</th><td>{report['private_response_binding']['bytes']}</td></tr>
<tr><th>Private receipt SHA-256</th><td><code>{escape(report['private_receipt_binding']['sha256'])}</code></td></tr>
<tr><th>Private receipt bytes</th><td>{report['private_receipt_binding']['bytes']}</td></tr>
<tr><th>Operator-declared reveal state</th><td>{escape(report['operator_declarations']['reveal_status'])}; not software-verifiable</td></tr>
</tbody></table></section>
<section class="card"><h2>Response distribution withheld</h2><p>{escape(report['content_withholding']['reason'])}</p><ul>{''.join(f'<li>{escape(item)}</li>' for item in report['content_withholding']['withheld_until_second_response_lock'])}</ul></section>
<section class="card"><h2>Traceability and limits</h2><p><strong>Run:</strong> <code>{escape(report['run_id'])}</code><br><strong>Git source:</strong> <code>{escape(report['git_source_commit'])}</code><br><strong>Packet SHA-256:</strong> <code>{escape(report['packet_binding']['sha256'])}</code><br><strong>Private receipt run:</strong> <code>{escape(report['private_receipt_binding']['run_id'])}</code><br><strong>Dataset / split / baseline / model:</strong> none / none / none / none</p><ul>{''.join(f'<li><strong>Not proven:</strong> {escape(item)}</li>' for item in report['claims']['not_proven'])}</ul></section>
</main></body></html>"""
    _write_utf8_lf(output_path, document)


def write_public_response_lock_outputs(
    report: dict[str, Any],
    *,
    json_path: Path,
    html_path: Path,
    png_path: Path,
) -> None:
    for path in (json_path, html_path, png_path):
        if path.exists():
            raise LabelReviewResponseLockQaError(f"refusing to overwrite existing output {path.name}")
    _write_utf8_lf(json_path, json.dumps(report, indent=2, ensure_ascii=True) + "\n")
    render_public_response_lock_png(report, png_path)
    render_public_response_lock_html(report, html_path)
