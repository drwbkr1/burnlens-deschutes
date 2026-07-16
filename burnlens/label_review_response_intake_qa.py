"""Publish content-withheld QA for atomic reviewer-response intake."""

from __future__ import annotations

from html import escape
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from .label_review_response_intake import INTAKE_VERSION
from .lock_label_review_response import SOFTWARE_BROWSER_FIXTURE
from .optical_pair_evidence import WARNING, _font


REPORT_ID = "LABEL-REVIEW-RESPONSE-ATOMIC-INTAKE-QA-2026-001"
SCHEMA_VERSION = "0.1.0"
REPORT_VERSION = "label-review-response-atomic-intake-qa-v0.1.0"
SOFTWARE_VERSION = "0.18.0"
TASK_ISSUE = 402


class LabelReviewResponseIntakeQaError(RuntimeError):
    """A fail-closed atomic-intake QA failure."""


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise LabelReviewResponseIntakeQaError(message)


def build_response_intake_qa(
    *,
    intake_report: dict[str, Any],
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    """Convert a software-fixture intake rehearsal into bounded public evidence."""

    _assert(len(git_source_commit) == 40, "git source commit must be a full SHA")
    _assert(bool(generated_at_utc.strip()) and bool(run_id.strip()), "QA time and run are required")
    _assert(intake_report.get("intake_version") == INTAKE_VERSION, "intake version differs")
    _assert(intake_report.get("software_version") == SOFTWARE_VERSION, "intake software differs")
    _assert(intake_report.get("task_issue") == TASK_ISSUE, "intake task issue differs")
    _assert(
        intake_report.get("git_source_commit") == git_source_commit,
        "intake and QA source commits differ",
    )
    _assert(
        intake_report.get("evidence_origin") == SOFTWARE_BROWSER_FIXTURE,
        "QA requires an explicit software fixture",
    )
    _assert(intake_report.get("software_browser_fixture") is True, "fixture flag differs")
    _assert(
        intake_report.get("qualifying_independent_human_response") is False,
        "software fixture is misclassified as human evidence",
    )
    _assert(
        intake_report.get("decision")
        == "PASS_ATOMIC_SOFTWARE_FIXTURE_INTAKE_NO_HUMAN_EVIDENCE_NO_REVEAL",
        "intake decision differs",
    )
    _assert(
        intake_report.get("reveal_authorized_by_this_intake") is False,
        "intake improperly authorizes reveal",
    )
    _assert(
        all(
            intake_report.get(key) is None
            for key in ("dataset_version", "split_version", "baseline_version", "model_version")
        ),
        "intake advances a downstream analytical version",
    )
    source = intake_report.get("source_binding")
    preserved = intake_report.get("preserved_response_binding")
    receipt = intake_report.get("receipt_binding")
    checks = intake_report.get("checks")
    _assert(isinstance(source, dict), "source binding is missing")
    _assert(isinstance(preserved, dict), "preserved response binding is missing")
    _assert(isinstance(receipt, dict), "receipt binding is missing")
    _assert(isinstance(checks, dict), "intake checks are missing")
    _assert(source.get("bytes") == preserved.get("bytes"), "source and preserved bytes differ")
    _assert(source.get("sha256") == preserved.get("sha256"), "source and preserved hash differ")
    _assert(len(str(source.get("sha256", ""))) == 64, "response SHA-256 is invalid")
    _assert(len(str(receipt.get("sha256", ""))) == 64, "receipt SHA-256 is invalid")
    _assert(all(value == "pass" for value in checks.values()), "an intake check did not pass")
    serialized = json.dumps(intake_report)
    for forbidden in (
        "source_response_path",
        "custody_directory",
        "preserved_response_name",
        "receipt_name",
        "label_counts",
        "responses",
        "review_started_at_utc",
        "review_completed_at_utc",
    ):
        _assert(forbidden not in serialized, f"intake report exposes {forbidden}")

    return {
        "report_id": REPORT_ID,
        "schema_version": SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "parent_response_issue": 393,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "intake_version": INTAKE_VERSION,
        "application_version": intake_report["application_version"],
        "fixture_origin": SOFTWARE_BROWSER_FIXTURE,
        "source_binding": {
            "bytes": source["bytes"],
            "sha256": source["sha256"],
            "filename_withheld": True,
            "path_withheld": True,
        },
        "preserved_response_binding": {
            "bytes": preserved["bytes"],
            "sha256": preserved["sha256"],
            "opaque_reviewer_slot": preserved["opaque_reviewer_id"],
            "filename_withheld": True,
            "path_withheld": True,
        },
        "private_receipt_binding": {
            "bytes": receipt["bytes"],
            "sha256": receipt["sha256"],
            "report_version": receipt["report_version"],
            "software_version": receipt["software_version"],
            "filename_withheld": True,
            "path_withheld": True,
        },
        "checks": dict(checks),
        "custody_state": {
            "atomic_non_overwriting_intake_ready": True,
            "software_fixture_used": True,
            "independent_human_responses_added": 0,
            "project_returned_response_count": 1,
            "second_human_response_present": False,
            "reveal_status": "withheld-unopened-after-lock",
            "reveal_status_verified_by_software": False,
            "reveal_authorized_by_this_run": False,
            "response_comparison_performed": False,
            "adjudication_completed": False,
        },
        "content_withholding": {
            "withheld": [
                "response labels and distributions",
                "evidence-sufficiency and confidence values",
                "reason codes and notes",
                "reviewer experience and attestation text",
                "response timestamps",
                "private filenames and private paths",
            ]
        },
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "decision": "PASS_ATOMIC_RESPONSE_INTAKE_READINESS_FIXTURE_ONLY_NO_REVEAL",
        "claims": {
            "proven": [
                "The fixture source and preserved response are byte-identical after validation, copy, fsync, and no-overwrite promotion.",
                "The private receipt is built identically from the source and preserved copy.",
                "Duplicate hashes and reviewer slots, unignored destinations, overwrite, source drift, and partial failure are fail-closed.",
                "The rehearsal publishes no response content, private filename, or private path.",
            ],
            "not_proven": [
                "A software fixture is not a second qualifying independent human response.",
                "Software does not verify reviewer identity, expertise, independence, scientific fitness, or reveal history.",
                "No reveal, comparison, adjudication, accepted label, dataset, split, baseline, model, accuracy, field, official, endorsed, or operational claim is created.",
            ],
        },
        "research_basis": [
            "https://docs.python.org/3.12/library/tempfile.html",
            "https://docs.python.org/3.12/library/os.html#os.link",
            "https://docs.python.org/3.12/library/os.html#os.fsync",
        ],
        "warning": WARNING,
    }


def _write_utf8_lf(path: Path, text: str) -> None:
    if path.exists():
        raise LabelReviewResponseIntakeQaError(f"refusing to overwrite {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))


def _render_html(report: dict[str, Any]) -> str:
    checks = "".join(
        f"<li><code>{escape(name)}</code>: {escape(value)}</li>"
        for name, value in report["checks"].items()
    )
    proven = "".join(f"<li>{escape(item)}</li>" for item in report["claims"]["proven"])
    not_proven = "".join(
        f"<li>{escape(item)}</li>" for item in report["claims"]["not_proven"]
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens atomic response intake QA</title>
<style>
:root{{--ink:#17332e;--teal:#007c71;--paper:#f5f1e8;--card:#fffdf8;--line:#d7cebe;--warn:#f15a2a}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}
header{{background:#0e302a;color:white;padding:2.5rem max(5vw,1.25rem)}}main{{max-width:1120px;margin:auto;padding:2rem 1.25rem}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem}}section{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:1.3rem;margin-bottom:1rem}}
.metric{{font-size:2rem;color:var(--teal)}}code{{overflow-wrap:anywhere}}.decision{{color:var(--warn);font-weight:700}}
</style></head><body>
<header><p>BurnLens / Phase Two / Objective Four</p><h1>Atomic reviewer-response intake QA</h1><p>Exact-byte preservation / fail-closed custody / software fixture only / no reveal</p></header>
<main>
<div class="grid">
<section><div class="metric">{report['source_binding']['bytes']}</div><p>fixture source bytes</p></section>
<section><div class="metric">{report['preserved_response_binding']['bytes']}</div><p>preserved bytes</p></section>
<section><div class="metric">0</div><p>human responses added</p></section>
<section><div class="metric">0</div><p>reveal actions</p></section>
</div>
<section><h2>Exact bindings</h2><p>Response SHA-256: <code>{escape(report['source_binding']['sha256'])}</code></p>
<p>Receipt SHA-256: <code>{escape(report['private_receipt_binding']['sha256'])}</code></p>
<p>Opaque fixture slot: <code>{escape(report['preserved_response_binding']['opaque_reviewer_slot'])}</code></p></section>
<section><h2>Fail-closed checks</h2><ul>{checks}</ul></section>
<section><h2>What this proves</h2><ul>{proven}</ul><h2>What remains absent</h2><ul>{not_proven}</ul>
<p class="decision">{escape(report['decision'])}</p></section>
<section><h2>Traceability</h2><p>Run <code>{escape(report['run_id'])}</code><br>Git <code>{escape(report['git_source_commit'])}</code><br>
Software {escape(report['software_version'])} / intake {escape(report['intake_version'])}<br>Dataset / split / baseline / model: none / none / none / none</p></section>
<section><strong>{escape(report['warning'])}</strong></section>
</main></body></html>
"""


def _render_png(report: dict[str, Any], output_path: Path) -> None:
    if output_path.exists():
        raise LabelReviewResponseIntakeQaError(f"refusing to overwrite {output_path.name}")
    canvas = Image.new("RGB", (1800, 1280), "#f5f1e8")
    draw = ImageDraw.Draw(canvas)
    title = _font(42)
    heading = _font(27)
    body = _font(22)
    small = _font(17)
    draw.rectangle((0, 0, 1800, 190), fill="#0e302a")
    draw.text((55, 35), "BURNLENS / PHASE TWO / OBJECTIVE FOUR", font=small, fill="#c2dad4")
    draw.text((55, 80), "ATOMIC REVIEWER-RESPONSE INTAKE QA", font=title, fill="white")
    draw.text(
        (55, 140),
        "Exact-byte preservation / fail-closed custody / fixture only / no reveal",
        font=body,
        fill="#c2dad4",
    )
    metrics = [
        (str(report["source_binding"]["bytes"]), "fixture source bytes"),
        (str(report["preserved_response_binding"]["bytes"]), "preserved bytes"),
        ("0", "human responses added"),
        ("0", "reveal actions"),
    ]
    for index, (value, label) in enumerate(metrics):
        left = 45 + index * 430
        draw.rounded_rectangle((left, 225, left + 390, 345), radius=18, fill="#dfeeea")
        draw.text((left + 24, 245), value, font=heading, fill="#007c71")
        draw.text((left + 24, 300), label, font=small, fill="#51625e")
    draw.rounded_rectangle((45, 390, 1755, 850), radius=18, fill="#fffdf8", outline="#d7cebe")
    draw.text((75, 420), "WHAT THIS REHEARSAL PROVES", font=heading, fill="#007c71")
    lines = [
        "The exact fixture bytes pass the shipped response contract before custody mutation.",
        "A same-directory temporary copy is flushed, synced, re-hashed, and promoted without overwrite.",
        "The preserved response and source remain byte-identical; the receipt is built identically from both.",
        "Duplicate hashes and reviewer slots, source drift, unignored paths, and partial failure are rejected.",
        "No response content, filename, private path, comparison, adjudication, or reveal is published.",
    ]
    y = 485
    for line in lines:
        draw.ellipse((78, y + 8, 92, y + 22), fill="#f15a2a")
        draw.text((112, y), line, font=body, fill="#17332e")
        y += 68
    draw.text(
        (75, 810),
        f"response sha256  {report['source_binding']['sha256']}",
        font=small,
        fill="#51625e",
    )
    draw.rounded_rectangle((45, 890, 1755, 1160), radius=18, fill="#dfeeea")
    draw.text((75, 925), "BOUNDARY", font=heading, fill="#007c71")
    boundary = [
        "This run uses one software fixture and adds zero human evidence.",
        "The project remains at one returned response; reviewer two is still absent.",
        "Reveal, comparison, adjudication, accepted labels, dataset, split, baseline, and model remain deferred.",
    ]
    y = 985
    for line in boundary:
        draw.text((75, y), line, font=body, fill="#17332e")
        y += 48
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


def write_response_intake_qa(
    report: dict[str, Any],
    *,
    json_path: Path,
    html_path: Path,
    png_path: Path,
) -> None:
    for path in (json_path, html_path, png_path):
        if path.exists():
            raise LabelReviewResponseIntakeQaError(f"refusing to overwrite {path.name}")
    _write_utf8_lf(
        json_path,
        json.dumps(report, indent=2, ensure_ascii=True) + "\n",
    )
    _write_utf8_lf(html_path, _render_html(report))
    _render_png(report, png_path)
