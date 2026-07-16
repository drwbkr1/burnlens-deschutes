"""Publish content-withheld QA for the BurnLens owner-waiver reveal gate."""

from __future__ import annotations

from hashlib import sha256
from html import escape
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from .optical_pair_evidence import WARNING, _font
from .owner_waiver_reveal_readiness import (
    AUTHORIZATION_VERSION,
    DECISION as AUTHORIZATION_DECISION,
    OWNER_WAIVER_ID,
    PARENT_RECONCILIATION_ISSUE,
    PRODUCTION_CONTRACT,
    SOFTWARE_VERSION,
    TASK_ISSUE,
    RevealReadinessContract,
    verify_owner_waiver_reveal_authorization,
)


REPORT_ID = "LABEL-REVIEW-OWNER-WAIVER-REVEAL-READINESS-QA-2026-001"
SCHEMA_VERSION = "0.1.0"
REPORT_VERSION = "label-review-owner-waiver-reveal-readiness-qa-v0.1.0"
DECISION = "PASS_OWNER_WAIVER_REVEAL_READINESS_CONTENT_WITHHELD"


class OwnerWaiverRevealReadinessQaError(RuntimeError):
    """A fail-closed public reveal-readiness QA failure."""


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise OwnerWaiverRevealReadinessQaError(message)


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def build_owner_waiver_reveal_readiness_qa(
    *,
    authorization_path: Path,
    response_path: Path,
    receipt_path: Path,
    packet_path: Path,
    reveal_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    contract: RevealReadinessContract = PRODUCTION_CONTRACT,
) -> dict[str, Any]:
    """Reverify the private gate and expose only bounded readiness evidence."""

    _assert(bool(generated_at_utc.strip()) and generated_at_utc.endswith("Z"), "QA time is invalid")
    _assert(bool(run_id.strip()), "QA run ID is missing")
    _assert(
        len(git_source_commit) == 40
        and all(character in "0123456789abcdef" for character in git_source_commit),
        "QA source commit must be a full lowercase SHA",
    )
    authorization = verify_owner_waiver_reveal_authorization(
        authorization_path=authorization_path,
        response_path=response_path,
        receipt_path=receipt_path,
        packet_path=packet_path,
        reveal_path=reveal_path,
        contract=contract,
    )
    _assert(
        authorization.get("git_source_commit") == git_source_commit,
        "authorization and QA source commits differ",
    )
    serialized = json.dumps(authorization, sort_keys=True)
    for forbidden in (
        str(response_path),
        str(receipt_path),
        str(authorization_path),
        response_path.name,
        receipt_path.name,
        authorization_path.name,
        '"label_counts"',
        '"responses"',
        '"review_started_at_utc"',
        '"review_completed_at_utc"',
        '"reviewer_experience"',
        '"attestation"',
    ):
        _assert(forbidden not in serialized, "private response or reviewer content leaked into authorization")

    authorization_binding = {
        "bytes": authorization_path.stat().st_size,
        "sha256": _sha256_file(authorization_path),
        "report_id": OWNER_WAIVER_ID,
        "report_version": AUTHORIZATION_VERSION,
        "filename_withheld": True,
        "path_withheld": True,
    }
    return {
        "report_id": REPORT_ID,
        "schema_version": SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "parent_reconciliation_issue": PARENT_RECONCILIATION_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "authorization_binding": authorization_binding,
        "response_binding": {
            "bytes": contract.response_bytes,
            "sha256": contract.response_sha256,
            "opaque_reviewer_id": contract.opaque_reviewer_id,
            "unit_count": contract.unit_count,
            "filename_withheld": True,
            "path_withheld": True,
            "contents_withheld": True,
        },
        "receipt_binding": {
            "bytes": contract.receipt_bytes,
            "sha256": contract.receipt_sha256,
            "filename_withheld": True,
            "path_withheld": True,
        },
        "packet_binding": {
            "bytes": contract.packet_bytes,
            "sha256": contract.packet_sha256,
            "report_id": "LABEL-REVIEW-PACKET-2026-001",
        },
        "reveal_binding": {
            "bytes": contract.reveal_bytes,
            "sha256": contract.reveal_sha256,
            "report_id": "LABEL-REVIEW-PACKET-2026-001-REVEAL",
            "contents_withheld": True,
        },
        "checks": dict(authorization["checks"]),
        "owner_waiver_state": {
            "explicit_owner_waiver_recorded": True,
            "reviewer_two_requirement_waived": True,
            "returned_independent_responses": 1,
            "second_human_response_present": False,
            "single_reviewer_reduced_validation_acknowledged": True,
            "inter_rater_validation_available": False,
            "consensus_available": False,
            "adjudication_available": False,
        },
        "reveal_state": {
            "operator_status_before_authorization": "withheld-unopened-after-lock",
            "reveal_opened_by_authorization_run": False,
            "reveal_opened_by_qa_run": False,
            "reveal_authorized_for_later_private_reconciliation": True,
            "authorized_reconciliation_issue": PARENT_RECONCILIATION_ISSUE,
        },
        "content_withholding": {
            "response_labels_distributions_confidence_reasons_notes_and_timestamps": "withheld",
            "reviewer_experience_attestations_and_free_text": "withheld",
            "private_filenames_and_paths": "withheld",
            "proposal_reveal_contents": "withheld",
        },
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "authorization_decision": AUTHORIZATION_DECISION,
        "decision": DECISION,
        "claims": {
            "proven": [
                "The exact preserved first response and exact private receipt still match their shipped bindings.",
                "The exact packet and proposal-reveal artifact still match the immutable review inventory.",
                "The owner explicitly waived reviewer two and acknowledged the permanently reduced single-reviewer validation route.",
                "A later private deterministic reconciliation run under issue #403 may now open the exact reveal.",
            ],
            "not_proven": [
                "The waiver does not create a second reviewer, inter-rater validation, consensus, or adjudication.",
                "Authorization does not accept any label, create a dataset or split, train a baseline or model, or establish accuracy.",
                "Software does not verify reviewer identity, expertise, independence, field validity, official status, endorsement, emergency readiness, or operational fitness.",
            ],
        },
        "warning": WARNING,
    }


def _write_utf8_lf(path: Path, text: str) -> None:
    if path.exists():
        raise OwnerWaiverRevealReadinessQaError(f"refusing to overwrite {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))


def _render_html(report: dict[str, Any]) -> str:
    checks = "".join(
        f"<li><code>{escape(name)}</code>: {escape(value)}</li>"
        for name, value in report["checks"].items()
    )
    proven = "".join(f"<li>{escape(item)}</li>" for item in report["claims"]["proven"])
    not_proven = "".join(f"<li>{escape(item)}</li>" for item in report["claims"]["not_proven"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens owner-waiver reveal readiness</title><style>
:root{{--ink:#17332e;--teal:#007c71;--paper:#f5f1e8;--card:#fffdf8;--line:#d7cebe;--warn:#f15a2a}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}
header{{background:#0e302a;color:white;padding:2.5rem max(5vw,1.25rem)}}main{{max-width:1120px;margin:auto;padding:2rem 1.25rem}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:1rem}}section{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:1.3rem;margin-bottom:1rem}}
.metric{{font-size:2rem;color:var(--teal)}}code{{overflow-wrap:anywhere}}.decision{{color:var(--warn);font-weight:700}}
</style></head><body><header><p>BurnLens / Phase Two / Objective Four</p><h1>Owner-waiver reveal readiness</h1>
<p>One exact independent response / reviewer two waived / content withheld / later reconciliation only</p></header><main>
<div class="grid"><section><div class="metric">1</div><p>returned independent response</p></section>
<section><div class="metric">0</div><p>second reviewers</p></section><section><div class="metric">0</div><p>reveal actions in this run</p></section>
<section><div class="metric">0</div><p>accepted labels</p></section></div>
<section><h2>Exact pre-reveal bindings</h2><p>Response SHA-256: <code>{escape(report['response_binding']['sha256'])}</code></p>
<p>Receipt SHA-256: <code>{escape(report['receipt_binding']['sha256'])}</code></p>
<p>Packet SHA-256: <code>{escape(report['packet_binding']['sha256'])}</code></p>
<p>Reveal SHA-256: <code>{escape(report['reveal_binding']['sha256'])}</code></p></section>
<section><h2>Fail-closed checks</h2><ul>{checks}</ul></section>
<section><h2>What this proves</h2><ul>{proven}</ul><h2>What remains absent</h2><ul>{not_proven}</ul>
<p class="decision">{escape(report['decision'])}</p></section>
<section><h2>Traceability</h2><p>Run <code>{escape(report['run_id'])}</code><br>Git <code>{escape(report['git_source_commit'])}</code><br>
Software {escape(report['software_version'])} / issue #{report['task_issue']} / reconciliation #{report['parent_reconciliation_issue']}<br>
Dataset / split / baseline / model: none / none / none / none</p></section>
<section><strong>{escape(report['warning'])}</strong></section></main></body></html>
"""


def _render_png(report: dict[str, Any], output_path: Path) -> None:
    if output_path.exists():
        raise OwnerWaiverRevealReadinessQaError(f"refusing to overwrite {output_path.name}")
    canvas = Image.new("RGB", (1800, 1280), "#f5f1e8")
    draw = ImageDraw.Draw(canvas)
    title = _font(42)
    heading = _font(27)
    body = _font(22)
    small = _font(17)
    draw.rectangle((0, 0, 1800, 190), fill="#0e302a")
    draw.text((55, 35), "BURNLENS / PHASE TWO / OBJECTIVE FOUR", font=small, fill="#c2dad4")
    draw.text((55, 80), "OWNER-WAIVER REVEAL READINESS", font=title, fill="white")
    draw.text((55, 140), "Single reviewer / reduced validation / content withheld", font=body, fill="#c2dad4")
    metrics = [
        ("1", "returned response"),
        ("0", "second reviewers"),
        ("0", "reveal actions"),
        ("0", "accepted labels"),
    ]
    for index, (value, label) in enumerate(metrics):
        left = 45 + index * 430
        draw.rounded_rectangle((left, 225, left + 390, 345), radius=18, fill="#dfeeea")
        draw.text((left + 24, 245), value, font=heading, fill="#007c71")
        draw.text((left + 24, 300), label, font=small, fill="#51625e")
    draw.rounded_rectangle((45, 390, 1755, 830), radius=18, fill="#fffdf8", outline="#d7cebe")
    draw.text((75, 420), "AUTHORIZED SCOPE", font=heading, fill="#007c71")
    lines = [
        "Exact response, receipt, packet, and reveal bindings pass without proposal-content interpretation.",
        "The owner explicitly waived reviewer two and acknowledged reduced single-reviewer validation.",
        "A later deterministic private reconciliation under issue #403 may open the exact reveal.",
        "Original response and proposal artifacts remain immutable; weak or conflicting evidence stays ignored.",
        "No inter-rater validation, consensus, adjudication, accepted label, dataset, split, baseline, or model exists.",
    ]
    y = 485
    for line in lines:
        draw.ellipse((78, y + 8, 92, y + 22), fill="#f15a2a")
        draw.text((112, y), line, font=body, fill="#17332e")
        y += 68
    draw.text((75, 790), f"reveal sha256  {report['reveal_binding']['sha256']}", font=small, fill="#51625e")
    draw.rounded_rectangle((45, 870, 1755, 1160), radius=18, fill="#dfeeea")
    draw.text((75, 905), "BOUNDARY", font=heading, fill="#007c71")
    boundary = [
        "The waiver changes the route; it does not add reviewer evidence.",
        "Response labels, reviewer text, timestamps, private paths, and reveal content remain withheld here.",
        "The next run must preserve permanently that inter-rater validation and adjudication are absent.",
    ]
    y = 965
    for line in boundary:
        draw.text((75, y), line, font=body, fill="#17332e")
        y += 50
    draw.text((75, 1120), report["decision"], font=small, fill="#f15a2a")
    draw.text(
        (55, 1200),
        f"run {report['run_id']} / Git {report['git_source_commit']} / software {report['software_version']}",
        font=small,
        fill="#51625e",
    )
    draw.text((55, 1240), report["warning"], font=small, fill="#f15a2a")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, format="PNG", optimize=False)


def write_owner_waiver_reveal_readiness_qa(
    report: dict[str, Any],
    *,
    json_path: Path,
    html_path: Path,
    png_path: Path,
) -> None:
    for path in (json_path, html_path, png_path):
        if path.exists():
            raise OwnerWaiverRevealReadinessQaError(f"refusing to overwrite {path.name}")
    _write_utf8_lf(json_path, json.dumps(report, indent=2, ensure_ascii=True) + "\n")
    _write_utf8_lf(html_path, _render_html(report))
    _render_png(report, png_path)
