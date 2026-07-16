"""Publish aggregate-only QA for the private BurnLens single-reviewer reconciliation."""

from __future__ import annotations

from hashlib import sha256
from html import escape
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from .optical_pair_evidence import WARNING, _font
from .single_reviewer_reconciliation import (
    DECISION as PRIVATE_DECISION,
    REPORT_ID as PRIVATE_REPORT_ID,
    REPORT_VERSION as PRIVATE_REPORT_VERSION,
    SOFTWARE_VERSION,
    TASK_ISSUE,
)


REPORT_ID = "LABEL-REVIEW-SINGLE-REVIEWER-RECONCILIATION-QA-2026-001"
SCHEMA_VERSION = "0.1.0"
REPORT_VERSION = "label-review-single-reviewer-reconciliation-qa-v0.1.0"
DECISION = "REMEDIATE_LABEL_EVIDENCE_DEFER_DATASET_SINGLE_REVIEWER"


class SingleReviewerReconciliationQaError(RuntimeError):
    """A fail-closed public reconciliation-QA failure."""


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise SingleReviewerReconciliationQaError(message)


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _load_private_report(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SingleReviewerReconciliationQaError(
            "private reconciliation is not valid UTF-8 JSON"
        ) from error
    _assert(isinstance(value, dict), "private reconciliation root must be an object")
    return value


def build_single_reviewer_reconciliation_qa(
    *,
    private_reconciliation_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    """Validate private reconciliation invariants and expose aggregate evidence only."""

    _assert(generated_at_utc.endswith("Z"), "QA time must end in Z")
    _assert(bool(run_id.strip()), "QA run ID is missing")
    _assert(
        len(git_source_commit) == 40
        and all(character in "0123456789abcdef" for character in git_source_commit),
        "QA source commit must be a full lowercase SHA",
    )
    private = _load_private_report(private_reconciliation_path)
    _assert(private.get("report_id") == PRIVATE_REPORT_ID, "private report identity differs")
    _assert(
        private.get("report_version") == PRIVATE_REPORT_VERSION,
        "private report version differs",
    )
    _assert(private.get("software_version") == SOFTWARE_VERSION, "private software differs")
    _assert(private.get("task_issue") == TASK_ISSUE, "private task issue differs")
    _assert(private.get("decision") == PRIVATE_DECISION, "private decision differs")
    reveal = private.get("reveal_binding")
    waiver = private.get("owner_waiver_state")
    aggregate = private.get("aggregate")
    decisions = private.get("decisions")
    _assert(isinstance(reveal, dict), "private reveal binding is missing")
    _assert(isinstance(waiver, dict), "private owner-waiver state is missing")
    _assert(isinstance(aggregate, dict), "private aggregate is missing")
    _assert(isinstance(decisions, list), "private decisions are missing")
    _assert(reveal.get("opened_by_this_run") is True, "private run did not record reveal access")
    _assert(
        reveal.get("authorization_reverified_before_first_reveal_content_access") is False,
        "preflight sequence exception is not preserved",
    )
    _assert(
        reveal.get("authorization_reverified_before_private_response_content_access") is True,
        "response-access authorization sequence differs",
    )
    _assert(
        reveal.get("authorization_reverified_before_unit_comparison") is True,
        "comparison authorization sequence differs",
    )
    _assert(
        reveal.get("preflight_sequence_exception_acknowledged") is True,
        "preflight sequence exception is unacknowledged",
    )
    _assert(waiver.get("returned_independent_responses") == 1, "response count differs")
    _assert(waiver.get("second_human_response_present") is False, "reviewer-two state differs")
    _assert(waiver.get("inter_rater_validation_available") is False, "inter-rater state differs")
    reviewed = aggregate.get("reviewed_units")
    accepted = aggregate.get("accepted_candidate_units")
    ignored = aggregate.get("ignored_units")
    _assert(
        all(isinstance(value, int) and value >= 0 for value in (reviewed, accepted, ignored)),
        "aggregate unit counts are invalid",
    )
    _assert(accepted + ignored == reviewed == len(decisions), "aggregate coverage differs")
    decision_counts: dict[str, int] = {}
    label_counts: dict[str, int] = {}
    event_counts: dict[str, dict[str, int]] = {}
    seen: set[str] = set()
    for item in decisions:
        _assert(isinstance(item, dict), "private unit decision is invalid")
        sample_id = item.get("sample_id")
        event_id = item.get("event_group_id")
        disposition = item.get("disposition")
        _assert(isinstance(sample_id, str) and sample_id not in seen, "private sample identity differs")
        _assert(isinstance(event_id, str) and event_id, "private event identity differs")
        _assert(disposition in {"accepted-candidate", "ignored"}, "private disposition differs")
        seen.add(sample_id)
        reason = item.get("disposition_reason")
        _assert(isinstance(reason, str) and reason, "private disposition reason is missing")
        decision_counts[reason] = decision_counts.get(reason, 0) + 1
        event_counts.setdefault(event_id, {"accepted-candidate": 0, "ignored": 0})[
            disposition
        ] += 1
        if disposition == "accepted-candidate":
            target = item.get("candidate_binary_target")
            _assert(target in {0, 1}, "accepted candidate target is invalid")
            label = "burned" if target == 1 else "background"
            label_counts[label] = label_counts.get(label, 0) + 1
        else:
            _assert(item.get("candidate_binary_target") is None, "ignored unit carries a target")
    _assert(decision_counts == aggregate.get("disposition_reason_counts"), "reason aggregate differs")
    _assert(label_counts == aggregate.get("accepted_label_counts"), "label aggregate differs")
    _assert(event_counts == aggregate.get("event_disposition_counts"), "event aggregate differs")
    _assert(
        all(
            private.get(key) is None
            for key in ("dataset_version", "split_version", "baseline_version", "model_version")
        ),
        "private reconciliation advances a downstream version",
    )

    public = {
        "report_id": REPORT_ID,
        "schema_version": SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "private_reconciliation_binding": {
            "bytes": private_reconciliation_path.stat().st_size,
            "sha256": _sha256_file(private_reconciliation_path),
            "report_id": PRIVATE_REPORT_ID,
            "report_version": PRIVATE_REPORT_VERSION,
            "filename_withheld": True,
            "path_withheld": True,
        },
        "authorization_binding": dict(private["authorization_binding"]),
        "response_binding": {
            **private["response_binding"],
            "filename_withheld": True,
            "path_withheld": True,
            "reviewer_free_text_withheld": True,
        },
        "receipt_binding": {
            **private["receipt_binding"],
            "filename_withheld": True,
            "path_withheld": True,
        },
        "packet_binding": dict(private["packet_binding"]),
        "reveal_binding": {
            **private["reveal_binding"],
            "content_republished": False,
        },
        "owner_waiver_state": dict(waiver),
        "rule": dict(private["rule"]),
        "aggregate": {
            "reviewed_units": reviewed,
            "accepted_candidate_units": accepted,
            "ignored_units": ignored,
            "accepted_label_counts": dict(sorted(label_counts.items())),
            "disposition_reason_counts": dict(sorted(decision_counts.items())),
            "event_disposition_counts": {
                event: dict(sorted(counts.items())) for event, counts in sorted(event_counts.items())
            },
        },
        "quality_gates": {
            "exact_private_report_binding": "pass",
            "all_units_have_unique_deterministic_dispositions": "pass",
            "aggregate_recomputed_from_private_units": "pass",
            "one_response_only_and_reviewer_two_absent": "pass",
            "inter_rater_consensus_adjudication_claims": "absent",
            "reviewer_free_text_private_paths_and_unit_details": "withheld",
            "original_response_receipt_packet_and_reveal_modified": False,
            "authorization_before_first_reveal_content_access": (
                "fail-disclosed: reveal HTML appeared in issue-403 preflight repository search"
            ),
            "authorization_before_private_response_access_and_unit_comparison": "pass",
        },
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "decision": DECISION,
        "decision_detail": (
            f"{label_counts.get('burned', 0)} candidate burned units and "
            f"{label_counts.get('background', 0)} candidate background units survive the conservative "
            "single-reviewer rule. This is useful proposal-diagnostic evidence, not a balanced or "
            "representative dataset."
        ),
        "next_gate": (
            "Remediate the reference-evidence route, prioritizing independently traceable burned and "
            "background evidence across every event; MTBS may support reference context but does not "
            "convert this bounded single-reviewer probe into validation or ground truth."
        ),
        "research_basis": [
            {
                "title": "MTBS Mapping Methods",
                "url": "https://www.mtbs.gov/mapping-methods",
                "use": (
                    "Current official methods confirm pre/post scene review, co-registration checks, "
                    "masking of clouds and shadows, analyst interpretation, and acknowledged uncertainty."
                ),
            },
            {
                "title": "CEOS LPV Burned Area Satellite Product Validation Protocol",
                "url": "https://lpvs.gsfc.nasa.gov/PDF/BurnedAreaValidationProtocol.pdf",
                "use": (
                    "The primary protocol separates burned, unburned, and unmapped areas and requires "
                    "independent, representative reference evidence for accuracy claims."
                ),
            },
            {
                "title": "CEOS LPV Fire Disturbance 2025",
                "url": "https://lpvs.gsfc.nasa.gov/PDF/LPV_Plenary_2025/LPV_Fire_202505_v3.pdf",
                "use": (
                    "The current fire-disturbance status notes unresolved sample-size and protocol "
                    "questions and treats limited independent samples as insufficient without QA."
                ),
            },
        ],
        "claims": {
            "proven": [
                "One exact blinded response was deterministically reconciled against the exact reveal.",
                "Every reviewed unit has one private traceable accepted-candidate or ignored disposition.",
                "Only aggregate evidence is public; reviewer free text and unit-level decisions remain withheld.",
                "The result identifies a bounded proposal-remediation need without creating a dataset.",
                "The preflight reveal-access sequence exception is disclosed rather than represented as a pass.",
            ],
            "not_proven": [
                "No second reviewer, inter-rater validation, consensus, or adjudication exists.",
                "Accepted-candidate units are not ground truth, a representative validation sample, or an accuracy estimate.",
                "No dataset, split, baseline, model, field validation, official status, endorsement, emergency readiness, or operational fitness exists.",
            ],
        },
        "warning": WARNING,
    }
    serialized = json.dumps(public, sort_keys=True)
    for forbidden in (
        str(private_reconciliation_path),
        private_reconciliation_path.name,
        '"sample_id"',
        '"decisions"',
        '"row"',
        '"column"',
        '"notes_sha256"',
        '"review_started_at_utc"',
        '"review_completed_at_utc"',
        '"attestation"',
        '"burned_area_interpretation_experience"',
    ):
        _assert(forbidden not in serialized, "private unit or reviewer content leaked into public QA")
    return public


def _write_utf8_lf(path: Path, text: str) -> None:
    if path.exists():
        raise SingleReviewerReconciliationQaError(f"refusing to overwrite {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))


def _render_html(report: dict[str, Any]) -> str:
    reasons = "".join(
        f"<li><code>{escape(name)}</code>: {count}</li>"
        for name, count in report["aggregate"]["disposition_reason_counts"].items()
    )
    events = "".join(
        f"<tr><td>{escape(event)}</td><td>{counts.get('accepted-candidate', 0)}</td>"
        f"<td>{counts.get('ignored', 0)}</td></tr>"
        for event, counts in report["aggregate"]["event_disposition_counts"].items()
    )
    proven = "".join(f"<li>{escape(item)}</li>" for item in report["claims"]["proven"])
    not_proven = "".join(f"<li>{escape(item)}</li>" for item in report["claims"]["not_proven"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens single-reviewer reconciliation QA</title><style>
:root{{--ink:#17332e;--teal:#007c71;--paper:#f5f1e8;--card:#fffdf8;--line:#d7cebe;--orange:#d94b20}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}
header{{background:#0e302a;color:white;padding:2.5rem max(5vw,1.25rem)}}main{{max-width:1120px;margin:auto;padding:2rem 1.25rem}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:1rem}}section{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:1.3rem;margin-bottom:1rem}}
.metric{{font-size:2rem;color:var(--teal)}}table{{width:100%;border-collapse:collapse}}th,td{{padding:.65rem;border-bottom:1px solid var(--line);text-align:left}}
code{{overflow-wrap:anywhere}}.decision{{color:var(--orange);font-weight:700}}
</style></head><body><header><p>BurnLens / Phase Two / Objective Four</p><h1>Single-reviewer reconciliation</h1>
<p>Owner waiver / reduced validation / aggregate-only evidence / dataset deferred</p></header><main>
<div class="grid"><section><div class="metric">{report['aggregate']['reviewed_units']}</div><p>reviewed units</p></section>
<section><div class="metric">{report['aggregate']['accepted_candidate_units']}</div><p>accepted candidate units</p></section>
<section><div class="metric">{report['aggregate']['ignored_units']}</div><p>ignored units</p></section>
<section><div class="metric">0</div><p>candidate background units</p></section></div>
<section><h2>Cross-event result</h2><table><thead><tr><th>Event</th><th>Accepted candidate</th><th>Ignored</th></tr></thead><tbody>{events}</tbody></table></section>
<section><h2>Why evidence was ignored</h2><ul>{reasons}</ul></section>
<section><h2>Decision</h2><p>{escape(report['decision_detail'])}</p><p><strong>Next gate:</strong> {escape(report['next_gate'])}</p>
<p class="decision">{escape(report['decision'])}</p></section>
<section><h2>What this proves</h2><ul>{proven}</ul><h2>What remains absent</h2><ul>{not_proven}</ul></section>
<section><h2>Traceability</h2><p>Run <code>{escape(report['run_id'])}</code><br>Git <code>{escape(report['git_source_commit'])}</code><br>
Software {escape(report['software_version'])} / issue #{report['task_issue']}<br>
Private reconciliation SHA-256 <code>{escape(report['private_reconciliation_binding']['sha256'])}</code><br>
Dataset / split / baseline / model: none / none / none / none</p></section>
<section><strong>{escape(report['warning'])}</strong></section></main></body></html>
"""


def _render_png(report: dict[str, Any], path: Path) -> None:
    if path.exists():
        raise SingleReviewerReconciliationQaError(f"refusing to overwrite {path.name}")
    canvas = Image.new("RGB", (1800, 1280), "#f5f1e8")
    draw = ImageDraw.Draw(canvas)
    title = _font(42)
    heading = _font(27)
    body = _font(22)
    small = _font(17)
    draw.rectangle((0, 0, 1800, 190), fill="#0e302a")
    draw.text((55, 35), "BURNLENS / PHASE TWO / OBJECTIVE FOUR", font=small, fill="#c2dad4")
    draw.text((55, 80), "SINGLE-REVIEWER RECONCILIATION", font=title, fill="white")
    draw.text((55, 140), "Reduced validation / aggregate-only evidence / dataset deferred", font=body, fill="#c2dad4")
    metrics = [
        (str(report["aggregate"]["reviewed_units"]), "reviewed units"),
        (str(report["aggregate"]["accepted_candidate_units"]), "accepted candidates"),
        (str(report["aggregate"]["ignored_units"]), "ignored units"),
        ("0", "background candidates"),
    ]
    for index, (value, label) in enumerate(metrics):
        left = 45 + index * 430
        draw.rounded_rectangle((left, 225, left + 390, 345), radius=18, fill="#dfeeea")
        draw.text((left + 24, 245), value, font=heading, fill="#007c71")
        draw.text((left + 24, 300), label, font=small, fill="#51625e")
    draw.rounded_rectangle((45, 390, 1755, 810), radius=18, fill="#fffdf8", outline="#d7cebe")
    draw.text((75, 420), "RESULT", font=heading, fill="#007c71")
    labels = report["aggregate"]["accepted_label_counts"]
    lines = [
        f"{labels.get('burned', 0)} burned candidate units survive the conservative rule.",
        f"{labels.get('background', 0)} background candidate units survive.",
    ]
    for event, counts in report["aggregate"]["event_disposition_counts"].items():
        lines.append(
            f"{event}: {counts.get('accepted-candidate', 0)} accepted / {counts.get('ignored', 0)} ignored."
        )
    lines.append(
        "One response remains one response: no inter-rater validation, consensus, or adjudication."
    )
    y = 475
    for line in lines:
        draw.text((85, y), f"- {line}", font=body, fill="#17332e")
        y += 48
    draw.rounded_rectangle((45, 855, 1755, 1105), radius=18, fill="#fde8df", outline="#d94b20")
    draw.text((75, 885), "DECISION", font=heading, fill="#d94b20")
    draw.text((75, 940), "REMEDIATE LABEL EVIDENCE / DEFER DATASET", font=heading, fill="#17332e")
    draw.text((75, 995), "Candidate units are diagnostic evidence, not ground truth or an accuracy sample.", font=body, fill="#17332e")
    draw.text((75, 1050), "Next: strengthen independently traceable burned and background evidence across every event.", font=body, fill="#17332e")
    draw.text((55, 1160), report["warning"], font=small, fill="#17332e")
    draw.text((55, 1205), f"Run {report['run_id']} / software {report['software_version']} / issue #{report['task_issue']}", font=small, fill="#51625e")
    canvas.save(path, format="PNG", optimize=False)


def write_single_reviewer_reconciliation_qa(
    report: dict[str, Any],
    *,
    json_path: Path,
    html_path: Path,
    png_path: Path,
) -> None:
    for path in (json_path, html_path, png_path):
        if path.exists():
            raise SingleReviewerReconciliationQaError(f"refusing to overwrite {path.name}")
    _write_utf8_lf(json_path, json.dumps(report, indent=2, ensure_ascii=True) + "\n")
    _write_utf8_lf(html_path, _render_html(report))
    png_path.parent.mkdir(parents=True, exist_ok=True)
    _render_png(report, png_path)
