"""Build a deterministic, proposal-safe BurnLens label-review handoff.

The handoff packages only the proposal-blinded review pages, an offline response
workbench, safe instructions, the blank response template, and a binding
manifest.  It deliberately excludes the proposal reveal, proposal-bearing
packet JSON, adjudication material, provider bytes, and any claim that a human
response exists.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from hashlib import sha256
from html import escape
import json
from pathlib import Path, PurePosixPath
from typing import Any
import zipfile

from PIL import Image, ImageDraw

from .optical_pair_evidence import WARNING, _font
from .verify_label_review_packet import (
    LabelReviewVerificationError,
    build_qa_report as verify_source_packet,
)


SOFTWARE_VERSION = "0.14.0"
HANDOFF_ID = "LABEL-REVIEW-HANDOFF-2026-001"
HANDOFF_SCHEMA_VERSION = "0.1.0"
HANDOFF_VERSION = "proposal-safe-offline-label-review-handoff-v0.1.0"
WORKBENCH_VERSION = "label-review-handoff-workbench-v0.1.0"
TASK_ISSUE = 379

EXPECTED_PACKET_ID = "LABEL-REVIEW-PACKET-2026-001"
EXPECTED_PACKET_RUN_ID = "BL-2026-07-16-label-review-packet-r001"
EXPECTED_PACKET_SHA256 = "77067063a769645af13886b6c87cc236a10e06199d091743908d63556e07637c"
EXPECTED_PACKET_DECISION = "READY_FOR_INDEPENDENT_REVIEW_DEFER_DATASET"
EXPECTED_RESPONSE_SCHEMA = "burnlens-label-review-response-v0.1.0"
EXPECTED_RESPONSE_TEMPLATE_SHA256 = (
    "8eb885be0f301cc1ef3eac8e718a12f96b624877267fd140b6b1a9eabc80627d"
)
EXPECTED_BLIND_PAGE_COUNT = 8
EXPECTED_UNIT_COUNT = 56

HANDOFF_HTML_NAME = f"{HANDOFF_ID}.html"
HANDOFF_JSON_NAME = f"{HANDOFF_ID}.json"
HANDOFF_PNG_NAME = f"{HANDOFF_ID}.png"
HANDOFF_README_NAME = f"{HANDOFF_ID}-README.txt"
RESPONSE_TEMPLATE_NAME = f"{EXPECTED_PACKET_ID}-RESPONSE-TEMPLATE.json"
ARCHIVE_ROOT = "BurnLens-Label-Review-Handoff-2026-001"
BLIND_PAGE_NAMES = tuple(
    f"{EXPECTED_PACKET_ID}-BLIND-{index:02d}.png"
    for index in range(1, EXPECTED_BLIND_PAGE_COUNT + 1)
)

FIRST_PASS_LABELS = (
    ("burned", "Burned"),
    ("background", "Background"),
    ("uncertain", "Uncertain"),
    ("unusable", "Unusable evidence"),
)
EVIDENCE_SUFFICIENCY = (
    ("sufficient", "Sufficient"),
    ("limited", "Limited"),
    ("insufficient", "Insufficient"),
)
CONFIDENCE_LEVELS = (
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
)
REASON_LABELS = {
    "pre-post-change": "Visible pre/post change",
    "persistent-darkening": "Persistent darkening",
    "vegetation-loss": "Vegetation loss",
    "source-context-support": "Official-source context supports interpretation",
    "source-context-conflict": "Official-source context conflicts",
    "cloud-smoke-shadow": "Cloud, smoke, or shadow",
    "registration-concern": "Registration concern",
    "boundary-ambiguity": "Boundary ambiguity",
    "low-severity-ambiguity": "Low-severity ambiguity",
    "non-fire-change-possible": "Non-fire change is possible",
    "other": "Other",
}

FORBIDDEN_ARCHIVE_NAMES = {
    f"{EXPECTED_PACKET_ID}.json",
    f"{EXPECTED_PACKET_ID}-REVEAL.html",
    f"{EXPECTED_PACKET_ID}-ADJUDICATION-TEMPLATE.json",
    "LABEL-REVIEW-PACKET-QA-2026-001.json",
    "LABEL-REVIEW-PACKET-QA-2026-001.html",
    "LABEL-REVIEW-PACKET-QA-2026-001.png",
}


class LabelReviewHandoffError(RuntimeError):
    """A deterministic, secret-free reviewer-handoff failure."""


def _write_utf8_lf(path: Path, text: str) -> None:
    if path.exists():
        raise LabelReviewHandoffError(f"refusing to overwrite existing output {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    path.write_bytes(normalized.encode("utf-8"))


def _write_new_bytes(path: Path, payload: bytes) -> None:
    if path.exists():
        raise LabelReviewHandoffError(f"refusing to overwrite existing output {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _sha256_bytes(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise LabelReviewHandoffError(f"invalid JSON input {path.name}") from error
    if not isinstance(value, dict):
        raise LabelReviewHandoffError(f"JSON input {path.name} is not an object")
    return value


def _member_name(name: str) -> str:
    return str(PurePosixPath(ARCHIVE_ROOT) / name)


def _media_type(name: str) -> str:
    suffix = Path(name).suffix.lower()
    return {
        ".html": "text/html",
        ".json": "application/json",
        ".png": "image/png",
        ".txt": "text/plain",
    }[suffix]


def _validate_timestamp(value: str) -> tuple[int, int, int, int, int, int]:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise LabelReviewHandoffError("generated timestamp is invalid") from error
    if parsed.tzinfo is None:
        raise LabelReviewHandoffError("generated timestamp must be timezone-aware")
    if parsed.year < 1980:
        raise LabelReviewHandoffError("generated timestamp predates ZIP support")
    return (parsed.year, parsed.month, parsed.day, parsed.hour, parsed.minute, parsed.second)


def _validate_source_packet(packet_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    if packet_path.name != f"{EXPECTED_PACKET_ID}.json":
        raise LabelReviewHandoffError("unexpected packet filename")
    if _sha256_file(packet_path) != EXPECTED_PACKET_SHA256:
        raise LabelReviewHandoffError("source packet SHA-256 differs from the shipped packet")
    packet = _load_json(packet_path)
    if packet.get("report_id") != EXPECTED_PACKET_ID:
        raise LabelReviewHandoffError("source packet identity is invalid")
    if packet.get("run_id") != EXPECTED_PACKET_RUN_ID:
        raise LabelReviewHandoffError("source packet run identity is invalid")
    if packet.get("decision") != EXPECTED_PACKET_DECISION:
        raise LabelReviewHandoffError("source packet decision is invalid")
    if len(packet.get("units", [])) != EXPECTED_UNIT_COUNT:
        raise LabelReviewHandoffError("source packet unit count is invalid")
    try:
        qa = verify_source_packet(
            packet_path=packet_path,
            response_paths=[],
            generated_at_utc="2026-07-16T16:20:00Z",
            run_id="BL-HANDOFF-SOURCE-VERIFY",
            git_source_commit="0" * 40,
        )
    except LabelReviewVerificationError as error:
        raise LabelReviewHandoffError(f"source packet verification failed: {error}") from error
    if qa["decision"] != "PASS_PACKET_INTEGRITY_READY_FOR_INDEPENDENT_REVIEW_DEFER_DATASET":
        raise LabelReviewHandoffError("source packet is not in the expected zero-response state")
    return packet, qa


def _output_binding(packet: dict[str, Any], name: str) -> dict[str, Any]:
    for item in packet.get("outputs", {}).get("files", []):
        if item.get("path") == name:
            return item
    raise LabelReviewHandoffError(f"packet output binding is missing for {name}")


def _validate_response_template(
    template_path: Path,
    packet: dict[str, Any],
) -> dict[str, Any]:
    binding = _output_binding(packet, RESPONSE_TEMPLATE_NAME)
    if _sha256_file(template_path) != binding.get("sha256"):
        raise LabelReviewHandoffError("response template differs from packet binding")
    if _sha256_file(template_path) != EXPECTED_RESPONSE_TEMPLATE_SHA256:
        raise LabelReviewHandoffError("response template differs from the shipped template")
    template = _load_json(template_path)
    if template.get("response_schema_version") != EXPECTED_RESPONSE_SCHEMA:
        raise LabelReviewHandoffError("response template schema is invalid")
    if template.get("packet_id") != EXPECTED_PACKET_ID:
        raise LabelReviewHandoffError("response template packet identity is invalid")
    if template.get("packet_run_id") != EXPECTED_PACKET_RUN_ID:
        raise LabelReviewHandoffError("response template run identity is invalid")
    expected_ids = [unit["sample_id"] for unit in packet["units"]]
    responses = template.get("responses")
    if not isinstance(responses, list):
        raise LabelReviewHandoffError("response template response list is invalid")
    if [item.get("sample_id") for item in responses] != expected_ids:
        raise LabelReviewHandoffError("response template unit order is invalid")
    return template


def _validate_blind_pages(packet_path: Path, packet: dict[str, Any]) -> list[Path]:
    paths: list[Path] = []
    for name in BLIND_PAGE_NAMES:
        path = packet_path.parent / name
        binding = _output_binding(packet, name)
        if not path.is_file():
            raise LabelReviewHandoffError(f"blind page is missing: {name}")
        if path.stat().st_size != binding.get("bytes"):
            raise LabelReviewHandoffError(f"blind page byte length differs: {name}")
        if _sha256_file(path) != binding.get("sha256"):
            raise LabelReviewHandoffError(f"blind page SHA-256 differs: {name}")
        paths.append(path)
    return paths


def _options(values: tuple[tuple[str, str], ...]) -> str:
    return '<option value="">Choose…</option>' + "".join(
        f'<option value="{escape(value)}">{escape(label)}</option>' for value, label in values
    )


def _render_reason_controls(sample_id: str) -> str:
    controls = []
    for reason, label in REASON_LABELS.items():
        control_id = f"{sample_id}-reason-{reason}"
        controls.append(
            f'<label class="check" for="{escape(control_id)}">'
            f'<input id="{escape(control_id)}" type="checkbox" '
            f'name="{escape(sample_id)}-reason" value="{escape(reason)}"> '
            f"{escape(label)}</label>"
        )
    return "".join(controls)


def _render_response_card(sample_id: str) -> str:
    return f"""<fieldset class="response-card" data-sample-id="{escape(sample_id)}">
<legend>{escape(sample_id)}</legend>
<div class="grid">
<label for="{escape(sample_id)}-label">First-pass label
<select id="{escape(sample_id)}-label" data-field="first_pass_label" required>{_options(FIRST_PASS_LABELS)}</select></label>
<label for="{escape(sample_id)}-sufficiency">Evidence sufficiency
<select id="{escape(sample_id)}-sufficiency" data-field="evidence_sufficiency" required>{_options(EVIDENCE_SUFFICIENCY)}</select></label>
<label for="{escape(sample_id)}-confidence">Confidence
<select id="{escape(sample_id)}-confidence" data-field="confidence" required>{_options(CONFIDENCE_LEVELS)}</select></label>
</div>
<fieldset class="reasons"><legend>Reason codes — choose at least one</legend>{_render_reason_controls(sample_id)}</fieldset>
<label for="{escape(sample_id)}-notes">Optional notes
<textarea id="{escape(sample_id)}-notes" data-field="notes" maxlength="1000" rows="2"></textarea></label>
<p class="field-error" id="{escape(sample_id)}-error" aria-live="polite"></p>
</fieldset>"""


def render_workbench_html(
    *,
    packet: dict[str, Any],
    response_template: dict[str, Any],
) -> str:
    units_by_page: dict[str, list[str]] = {name: [] for name in BLIND_PAGE_NAMES}
    for unit in packet["units"]:
        page = unit.get("blind_page")
        if page not in units_by_page:
            raise LabelReviewHandoffError("review unit has an unexpected blind-page binding")
        units_by_page[page].append(unit["sample_id"])
    if any(len(sample_ids) != 7 for sample_ids in units_by_page.values()):
        raise LabelReviewHandoffError("blind-page unit grouping is not seven-by-eight")

    sections = []
    for index, name in enumerate(BLIND_PAGE_NAMES, start=1):
        cards = "".join(_render_response_card(sample_id) for sample_id in units_by_page[name])
        sections.append(
            f"""<section class="page-block" aria-labelledby="page-{index:02d}-heading">
<h2 id="page-{index:02d}-heading">Review page {index:02d}</h2>
<img src="{escape(name)}" alt="Proposal-blinded review page {index:02d} with seven review units">
<div class="response-list">{cards}</div>
</section>"""
        )

    safe_template = json.dumps(
        response_template,
        separators=(",", ":"),
        ensure_ascii=True,
    ).replace("<", "\\u003c")
    page_sections = "".join(sections)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self' file: data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<title>BurnLens offline label-review workbench</title>
<style>
:root{{--ink:#15211d;--paper:#f4f0e8;--panel:#fffdf8;--teal:#006b64;--orange:#c74320;--muted:#5d6b64;--focus:#00a79d}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}
header{{background:#132a26;color:white;padding:2.5rem max(5vw,2rem)}}header p{{color:#b9d8cf;max-width:80ch}}
main{{max-width:1500px;margin:auto;padding:2rem 1.2rem 6rem}}.warning{{background:#fff1ca;border-left:6px solid #d87618;padding:1rem 1.2rem;font-weight:650}}
.card,.page-block,.response-card{{background:var(--panel);border:1px solid #d9d1c4;border-radius:12px;padding:1.2rem;margin:1.2rem 0}}
.page-block>img{{width:100%;height:auto;border:1px solid #c8c0b2}}.response-list{{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:1rem}}
.response-card{{margin:0;min-width:0}}legend{{font-weight:750;color:var(--teal)}}label{{display:block;font-weight:650;margin:.55rem 0}}
select,textarea,input[type=text]{{width:100%;font:inherit;padding:.6rem;border:1px solid #7f8b85;border-radius:6px;background:white;color:var(--ink)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:.7rem}}.reasons{{border:0;padding:.4rem 0;margin:.4rem 0}}
.check{{display:flex;gap:.45rem;align-items:flex-start;font-weight:450;margin:.3rem 0}}.check input{{margin-top:.35rem;accent-color:var(--teal)}}
button,.file-label{{display:inline-block;border:0;border-radius:7px;background:var(--teal);color:white;font:700 1rem/1.2 system-ui,sans-serif;padding:.75rem 1rem;margin:.3rem .4rem .3rem 0;cursor:pointer}}
button.secondary,.file-label.secondary{{background:#3e514a}}button:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible,.file-label:focus-within{{outline:4px solid var(--focus);outline-offset:2px}}
.file-label input{{position:absolute;inline-size:1px;block-size:1px;opacity:0}}.status{{position:sticky;top:0;z-index:3;background:#e5efeb;border:2px solid var(--teal);padding:1rem;margin:1rem 0;border-radius:10px}}
.error-summary{{display:none;background:#ffe5df;border-left:6px solid var(--orange);padding:1rem;margin:1rem 0}}.error-summary.show{{display:block}}.field-error{{min-height:1.4em;color:#9b2c12;font-weight:700}}
.response-card.invalid{{border:3px solid var(--orange)}}.review-summary{{background:#e5efeb;border-radius:10px;padding:1rem;margin:1rem 0}}code{{overflow-wrap:anywhere}}
@media (max-width:700px){{header{{padding:2rem 1.2rem}}main{{padding:1rem .7rem 4rem}}.response-list{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<header><p>BurnLens / Phase Two / independent review handoff</p><h1>Offline label-review workbench</h1>
<p>Complete all 56 proposal-blinded judgments here. This page does not transmit data, store browser state, or contain a reveal link.</p></header>
<main>
<p class="warning">{escape(WARNING)}</p>
<section class="card" aria-labelledby="instructions-heading"><h2 id="instructions-heading">Before you begin</h2>
<ol><li>Use an opaque reviewer ID. Do not enter credentials, secrets, or unnecessary personal data.</li>
<li>Inspect the pre/post Sentinel imagery, fixed-display continuous dNBR, and NIFC or MTBS context. Source context is not truth alone.</li>
<li>Choose one first-pass label, evidence-sufficiency level, confidence level, and at least one reason for every unit.</li>
<li>Save drafts as needed. Review and export the completed JSON before requesting any reveal material.</li>
<li>Return the JSON file to the BurnLens operator. The operator validates and SHA-256 locks the exact bytes before any reveal is released.</li></ol>
<p><strong>Packet:</strong> <code>{escape(EXPECTED_PACKET_ID)}</code> /
<strong>run:</strong> <code>{escape(EXPECTED_PACKET_RUN_ID)}</code> /
<strong>workbench:</strong> <code>{escape(WORKBENCH_VERSION)}</code></p></section>
<section class="card" aria-labelledby="guide-heading"><h2 id="guide-heading">Decision guide</h2>
<dl><dt><strong>Burned</strong></dt><dd>The center pixel has visible pre/post evidence consistent with a burn scar.</dd>
<dt><strong>Background</strong></dt><dd>The center pixel has usable evidence supporting no burn scar.</dd>
<dt><strong>Uncertain</strong></dt><dd>Burn and non-burn interpretations remain plausible or source evidence conflicts.</dd>
<dt><strong>Unusable evidence</strong></dt><dd>Cloud, smoke, shadow, missing support, registration, or another defect prevents a judgment.</dd>
<dt><strong>Sufficient</strong></dt><dd>The shown evidence supports the selected label without a material unresolved limitation.</dd>
<dt><strong>Limited</strong></dt><dd>A label is possible, but an explicit limitation reduces confidence.</dd>
<dt><strong>Insufficient</strong></dt><dd>The evidence does not support a label; use uncertain or unusable as appropriate.</dd></dl>
<p>Blank or uniform source-context panels can mean the sampled center is outside the displayed NIFC or MTBS class. Absence from source context is not proof of background.</p></section>
<noscript><p class="warning">JavaScript is required only to collect, validate, save, load, and export the local JSON response. No network request is made.</p></noscript>
<form id="review-form" novalidate>
<section class="card" aria-labelledby="reviewer-heading"><h2 id="reviewer-heading">Reviewer attestation</h2>
<div class="grid">
<label for="reviewer-id">Opaque reviewer ID
<input id="reviewer-id" type="text" maxlength="120" autocomplete="off" required></label>
<label for="reviewer-experience">Burned-area interpretation experience
<input id="reviewer-experience" type="text" maxlength="500" autocomplete="off" required></label>
</div>
<label class="check" for="independent"><input id="independent" type="checkbox" required> I did not author the BurnLens proposal or this review tooling.</label>
<label class="check" for="not-seen"><input id="not-seen" type="checkbox" required> I have not seen sample-specific BurnLens states or target values before this first pass.</label>
<label class="check" for="attestation"><input id="attestation" type="checkbox" required> I attest that these entries are my completed first-pass judgments.</label>
</section>
<div class="status" role="status" aria-live="polite"><strong id="progress">0 of {EXPECTED_UNIT_COUNT} units complete</strong>
<span id="started-status">Review timer starts with the first edit.</span></div>
<div id="error-summary" class="error-summary" role="alert" tabindex="-1"></div>
{page_sections}
<section class="card" aria-labelledby="finalize-heading"><h2 id="finalize-heading">Review, save, and export</h2>
<p>Draft files remain incomplete and cannot pass the BurnLens response verifier. Final export requires every field and attestation, then records the current client-clock completion time.</p>
<button id="review-button" type="button">Review response</button>
<button id="save-draft-button" class="secondary" type="button">Save draft JSON</button>
<label class="file-label secondary" for="load-draft">Load draft JSON<input id="load-draft" type="file" accept=".json,application/json"></label>
<button id="export-button" type="button">Export completed response JSON</button>
<div id="review-summary" class="review-summary" aria-live="polite">No response review has been run.</div>
</section>
</form>
<script id="response-template" type="application/json">{safe_template}</script>
<script>
"use strict";
const template = JSON.parse(document.getElementById("response-template").textContent);
const expectedIds = template.responses.map(item => item.sample_id);
const forbiddenKeys = new Set([
  "proposal" + "_state",
  "proposal" + "_state_code",
  "proposal" + "_target_value",
  "dnbr" + "_center"
]);
let startedAt = null;
const form = document.getElementById("review-form");
const progress = document.getElementById("progress");
const startedStatus = document.getElementById("started-status");
const errorSummary = document.getElementById("error-summary");
const reviewSummary = document.getElementById("review-summary");

function markStarted() {{
  if (!startedAt) {{
    startedAt = new Date().toISOString();
    startedStatus.textContent = "Started: " + startedAt + " (client clock)";
  }}
}}

function unitValue(sampleId) {{
  const card = document.querySelector('[data-sample-id="' + sampleId + '"]');
  const reasons = Array.from(card.querySelectorAll('input[type="checkbox"]:checked')).map(item => item.value);
  const notesValue = card.querySelector('[data-field="notes"]').value.trim();
  return {{
    sample_id: sampleId,
    first_pass_label: card.querySelector('[data-field="first_pass_label"]').value || null,
    evidence_sufficiency: card.querySelector('[data-field="evidence_sufficiency"]').value || null,
    confidence: card.querySelector('[data-field="confidence"]').value || null,
    reason_codes: reasons,
    notes: notesValue || null
  }};
}}

function unitComplete(item) {{
  return Boolean(item.first_pass_label && item.evidence_sufficiency && item.confidence && item.reason_codes.length);
}}

function updateProgress() {{
  const count = expectedIds.map(unitValue).filter(unitComplete).length;
  progress.textContent = count + " of {EXPECTED_UNIT_COUNT} units complete";
}}

function collectResponse(completed) {{
  const response = JSON.parse(JSON.stringify(template));
  response.reviewer = {{
    reviewer_id: document.getElementById("reviewer-id").value.trim() || null,
    independent_from_proposal_author: document.getElementById("independent").checked || null,
    burned_area_interpretation_experience: document.getElementById("reviewer-experience").value.trim() || null,
    proposal_seen_before_first_pass: document.getElementById("not-seen").checked ? false : null,
    attestation: document.getElementById("attestation").checked ? "I completed the first pass before reveal and attest that these are my judgments." : null
  }};
  response.review_started_at_utc = startedAt;
  response.review_completed_at_utc = completed ? new Date().toISOString() : null;
  response.responses = expectedIds.map(unitValue);
  response.completed = Boolean(completed);
  return response;
}}

function validateResponse(response) {{
  const errors = [];
  document.querySelectorAll(".response-card").forEach(card => {{
    card.classList.remove("invalid");
    card.querySelector(".field-error").textContent = "";
  }});
  if (!response.reviewer.reviewer_id) errors.push("Enter an opaque reviewer ID.");
  if (!response.reviewer.burned_area_interpretation_experience) errors.push("Describe burned-area interpretation experience.");
  if (response.reviewer.independent_from_proposal_author !== true) errors.push("Confirm independence from the proposal author.");
  if (response.reviewer.proposal_seen_before_first_pass !== false) errors.push("Confirm that sample-specific proposal values were not seen.");
  if (!response.reviewer.attestation) errors.push("Confirm the first-pass attestation.");
  response.responses.forEach(item => {{
    if (!unitComplete(item)) {{
      const card = document.querySelector('[data-sample-id="' + item.sample_id + '"]');
      card.classList.add("invalid");
      card.querySelector(".field-error").textContent = "Complete the label, sufficiency, confidence, and at least one reason.";
      errors.push(item.sample_id + " is incomplete.");
    }}
  }});
  if (errors.length) {{
    errorSummary.classList.add("show");
    errorSummary.innerHTML = "<strong>Response cannot be finalized.</strong><p>" + errors.length + " issue(s) remain. The first incomplete unit is highlighted.</p>";
  }} else {{
    errorSummary.classList.remove("show");
    errorSummary.textContent = "";
  }}
  return errors;
}}

function summarize(response) {{
  const labels = {{}};
  response.responses.forEach(item => {{ labels[item.first_pass_label] = (labels[item.first_pass_label] || 0) + 1; }});
  return Object.entries(labels).sort().map(item => item[0] + ": " + item[1]).join(" / ");
}}

function downloadJson(response, filename) {{
  const payload = JSON.stringify(response, null, 2) + "\\n";
  const blob = new Blob([payload], {{type:"application/json;charset=utf-8"}});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}}

function sanitizedReviewerId() {{
  const value = document.getElementById("reviewer-id").value.trim().replace(/[^A-Za-z0-9._-]+/g, "-").replace(/^-+|-+$/g, "");
  return value || "opaque-reviewer";
}}

function hasForbiddenKey(value) {{
  if (Array.isArray(value)) return value.some(hasForbiddenKey);
  if (value && typeof value === "object") return Object.entries(value).some(([key, child]) => forbiddenKeys.has(key) || hasForbiddenKey(child));
  return false;
}}

function loadDraft(response) {{
  if (!response || response.response_schema_version !== template.response_schema_version ||
      response.packet_id !== template.packet_id || response.packet_run_id !== template.packet_run_id ||
      !Array.isArray(response.responses) ||
      response.responses.map(item => item.sample_id).join("|") !== expectedIds.join("|") ||
      hasForbiddenKey(response)) {{
    throw new Error("The draft does not match this proposal-blinded response contract.");
  }}
  document.getElementById("reviewer-id").value = response.reviewer?.reviewer_id || "";
  document.getElementById("reviewer-experience").value = response.reviewer?.burned_area_interpretation_experience || "";
  document.getElementById("independent").checked = response.reviewer?.independent_from_proposal_author === true;
  document.getElementById("not-seen").checked = response.reviewer?.proposal_seen_before_first_pass === false;
  document.getElementById("attestation").checked = Boolean(response.reviewer?.attestation);
  startedAt = response.review_started_at_utc || null;
  startedStatus.textContent = startedAt ? "Started: " + startedAt + " (loaded client-clock value)" : "Review timer starts with the first edit.";
  response.responses.forEach(item => {{
    const card = document.querySelector('[data-sample-id="' + item.sample_id + '"]');
    card.querySelector('[data-field="first_pass_label"]').value = item.first_pass_label || "";
    card.querySelector('[data-field="evidence_sufficiency"]').value = item.evidence_sufficiency || "";
    card.querySelector('[data-field="confidence"]').value = item.confidence || "";
    card.querySelector('[data-field="notes"]').value = item.notes || "";
    const selected = new Set(item.reason_codes || []);
    card.querySelectorAll('input[type="checkbox"]').forEach(control => {{ control.checked = selected.has(control.value); }});
  }});
  updateProgress();
  reviewSummary.textContent = "Draft loaded. Run Review response before final export.";
}}

form.addEventListener("input", () => {{ markStarted(); updateProgress(); }});
form.addEventListener("change", () => {{ markStarted(); updateProgress(); }});
document.getElementById("review-button").addEventListener("click", () => {{
  const response = collectResponse(false);
  const errors = validateResponse(response);
  if (errors.length) {{
    reviewSummary.textContent = "Review found " + errors.length + " issue(s).";
    errorSummary.focus();
  }} else {{
    reviewSummary.textContent = "All {EXPECTED_UNIT_COUNT} units and attestations are complete. Label counts: " + summarize(response) + ". Confirm, then export.";
  }}
}});
document.getElementById("save-draft-button").addEventListener("click", () => {{
  markStarted();
  downloadJson(collectResponse(false), "{EXPECTED_PACKET_ID}-DRAFT-" + sanitizedReviewerId() + ".json");
  reviewSummary.textContent = "Draft saved locally. It is incomplete evidence and must not be submitted as a completed response.";
}});
document.getElementById("export-button").addEventListener("click", () => {{
  markStarted();
  const response = collectResponse(true);
  const errors = validateResponse(response);
  if (errors.length) {{
    reviewSummary.textContent = "Export blocked until all issues are corrected.";
    errorSummary.focus();
    return;
  }}
  reviewSummary.textContent = "Completed response reviewed. Label counts: " + summarize(response) + ". Exporting exact JSON for operator validation and SHA-256 locking.";
  downloadJson(response, "{EXPECTED_PACKET_ID}-RESPONSE-" + sanitizedReviewerId() + ".json");
}});
document.getElementById("load-draft").addEventListener("change", async event => {{
  const file = event.target.files[0];
  if (!file) return;
  try {{
    loadDraft(JSON.parse(await file.text()));
  }} catch (error) {{
    errorSummary.classList.add("show");
    errorSummary.textContent = error.message;
    errorSummary.focus();
  }} finally {{
    event.target.value = "";
  }}
}});
updateProgress();
</script>
</main>
</body>
</html>
"""


def render_readme() -> str:
    return f"""BurnLens independent label-review handoff
================================================

Packet: {EXPECTED_PACKET_ID}
Packet run: {EXPECTED_PACKET_RUN_ID}
Workbench: {WORKBENCH_VERSION}

1. Extract the complete ZIP into one directory.
2. Open {HANDOFF_HTML_NAME} in a current desktop browser.
3. Use an opaque reviewer ID and do not enter credentials, secrets, or unnecessary personal data.
4. Complete all {EXPECTED_UNIT_COUNT} first-pass units before requesting any reveal material.
5. Save drafts as needed. A draft is not a completed response.
6. Review and export the completed JSON.
7. Return the completed JSON to the BurnLens operator.
8. The operator validates and SHA-256 locks the exact response bytes before releasing any reveal.

This bundle contains no proposal-bearing packet JSON, proposal reveal, adjudication material,
provider archive, secret, network dependency, accepted label, dataset, split, baseline, or model.

{WARNING}
"""


def _payload_record(name: str, payload: bytes, role: str) -> dict[str, Any]:
    return {
        "path": name,
        "media_type": _media_type(name),
        "bytes": len(payload),
        "sha256": _sha256_bytes(payload),
        "role": role,
    }


def build_handoff_manifest(
    *,
    packet: dict[str, Any],
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    payloads: dict[str, bytes],
) -> dict[str, Any]:
    if len(git_source_commit) != 40:
        raise LabelReviewHandoffError("git source commit must be a full 40-character SHA")
    roles = {
        HANDOFF_HTML_NAME: "offline labelled response workbench; no network or reveal link",
        HANDOFF_README_NAME: "safe reviewer instructions",
        RESPONSE_TEMPLATE_NAME: "blank proposal-free response contract",
        **{
            name: f"proposal-blinded review image {index:02d}"
            for index, name in enumerate(BLIND_PAGE_NAMES, start=1)
        },
    }
    members = [_payload_record(name, payloads[name], roles[name]) for name in roles]
    output_map = {
        item["path"]: item
        for item in packet.get("outputs", {}).get("files", [])
        if item.get("path") in {RESPONSE_TEMPLATE_NAME, *BLIND_PAGE_NAMES}
    }
    if set(output_map) != {RESPONSE_TEMPLATE_NAME, *BLIND_PAGE_NAMES}:
        raise LabelReviewHandoffError("packet safe-output inventory is incomplete")
    for item in members:
        if item["path"] in output_map:
            source = output_map[item["path"]]
            if item["bytes"] != source["bytes"] or item["sha256"] != source["sha256"]:
                raise LabelReviewHandoffError(
                    f"handoff payload differs from packet binding: {item['path']}"
                )
    return {
        "report_id": HANDOFF_ID,
        "schema_version": HANDOFF_SCHEMA_VERSION,
        "report_version": HANDOFF_VERSION,
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
            "sha256": EXPECTED_PACKET_SHA256,
            "decision": packet["decision"],
            "response_schema_version": packet["response_schema_version"],
            "review_protocol_version": packet["review_protocol_version"],
            "label_schema_version": packet["label_schema_version"],
            "aoi_version": packet["aoi_version"],
        },
        "archive_contract": {
            "root_directory": ARCHIVE_ROOT,
            "format": "ZIP",
            "compression": "stored",
            "member_timestamp": generated_at_utc,
            "member_mode": "100644",
            "member_order": [HANDOFF_JSON_NAME, *[item["path"] for item in members]],
            "member_count": len(members) + 1,
            "path_links_allowed": False,
            "network_dependencies": 0,
        },
        "members": members,
        "review_contract": {
            "unit_count": EXPECTED_UNIT_COUNT,
            "blind_page_count": EXPECTED_BLIND_PAGE_COUNT,
            "first_pass_labels": [item[0] for item in FIRST_PASS_LABELS],
            "evidence_sufficiency": [item[0] for item in EVIDENCE_SUFFICIENCY],
            "confidence_levels": [item[0] for item in CONFIDENCE_LEVELS],
            "reason_codes": list(REASON_LABELS),
            "draft_roundtrip_available": True,
            "completed_response_export_available": True,
            "operator_hash_lock_required_before_reveal": True,
        },
        "exclusions": {
            "proposal_bearing_packet_json": True,
            "proposal_reveal": True,
            "adjudication_material": True,
            "qa_output": True,
            "provider_bytes": True,
            "secrets_or_credentials": True,
            "network_requests_or_analytics": True,
        },
        "completed_independent_responses": 0,
        "completed_adjudications": 0,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "decision": "READY_FOR_ISOLATED_INDEPENDENT_REVIEW_DEFER_DATASET",
        "decision_detail": (
            "The exact shipped blind pages now have a deterministic offline workbench and an "
            "allowlisted isolated handoff. No actual independent response is included."
        ),
        "claims": {
            "proven": [
                "The handoff is derived from the exact verified zero-response packet.",
                "The archive contract excludes reveal, proposal-bearing packet JSON, adjudication material, provider bytes, secrets, and network dependencies.",
                "The workbench exports the existing proposal-free response schema without transmitting data.",
            ],
            "not_proven": [
                "Software-generated handoff readiness is not independent human review, reviewer identity verification, label fitness, adjudication, field validation, or accuracy.",
                "No accepted label set, dataset, split, baseline, model, application deployment, official status, or endorsement exists.",
            ],
        },
        "warning": WARNING,
    }


def render_handoff_png(manifest: dict[str, Any], path: Path) -> None:
    canvas = Image.new("RGB", (1800, 1420), "#f4f0e8")
    draw = ImageDraw.Draw(canvas)
    ink, muted, teal, orange = "#15211d", "#5d6b64", "#006b64", "#f05a28"
    draw.rectangle((0, 0, 1800, 190), fill="#132a26")
    draw.text((55, 30), "BURNLENS / PHASE TWO / OBJECTIVE FOUR", fill="#b9d8cf", font=_font(19))
    draw.text((55, 72), "OFFLINE REVIEWER HANDOFF", fill="white", font=_font(38))
    draw.text(
        (55, 127),
        "Isolated proposal-blinded bundle / local response workbench / operator-side hash lock",
        fill="#b9d8cf",
        font=_font(16),
    )
    draw.text((1430, 48), "STATUS", fill="#b9d8cf", font=_font(14))
    draw.text((1430, 78), "HANDOFF READY", fill="#ffd166", font=_font(22))
    draw.text((1430, 119), "0 human responses", fill="white", font=_font(14))

    metrics = [
        (str(manifest["review_contract"]["unit_count"]), "review units"),
        (str(manifest["review_contract"]["blind_page_count"]), "blind pages"),
        (str(manifest["archive_contract"]["member_count"]), "allowlisted members"),
        ("0", "network dependencies"),
    ]
    for index, (value, label) in enumerate(metrics):
        left = 45 + index * 430
        draw.rounded_rectangle((left, 230, left + 390, 350), radius=15, fill="#e5efeb")
        draw.text((left + 24, 250), value, fill=teal, font=_font(31))
        draw.text((left + 24, 307), label, fill=muted, font=_font(14))

    draw.text((45, 405), "REVIEWER FLOW", fill=teal, font=_font(21))
    flow = [
        ("1", "EXTRACT", "Keep the complete bundle in one local directory."),
        ("2", "REVIEW", "Inspect eight blind pages and complete 56 labelled controls."),
        ("3", "CONFIRM", "Correct text-identified errors and review response counts."),
        ("4", "EXPORT", "Save exact response JSON locally; no data is transmitted."),
        ("5", "LOCK", "Operator validates and SHA-256 locks bytes before reveal."),
    ]
    for index, (number, title, detail) in enumerate(flow):
        top = 450 + index * 122
        draw.rounded_rectangle((45, top, 1755, top + 96), radius=15, fill="#fffdf8", outline="#d4cec1", width=2)
        draw.ellipse((72, top + 23, 120, top + 71), fill=teal)
        draw.text((88, top + 33), number, fill="white", font=_font(18))
        draw.text((150, top + 19), title, fill=teal, font=_font(19))
        draw.text((150, top + 52), detail, fill=ink, font=_font(15))

    box_top = 1085
    draw.rounded_rectangle((45, box_top, 1755, 1280), radius=16, fill="#fffdf8", outline="#d4cec1", width=2)
    draw.text((72, box_top + 22), "EVIDENCE BOUNDARY", fill=orange, font=_font(20))
    lines = [
        "No reveal, proposal-bearing packet JSON, adjudication material, provider byte, secret, or network dependency is included.",
        "The workbench can reduce transcription and accidental-reveal risk; it cannot prove reviewer identity, expertise, or independence.",
        "A synthetic software roundtrip may test the contract, but it can never count as a human response.",
        "Dataset, split, baseline, model, accuracy, field, official, and operational claims remain absent.",
    ]
    for index, line in enumerate(lines):
        draw.text((88, box_top + 61 + index * 31), f"{index + 1}. {line}", fill=ink, font=_font(13))
    trace = (
        f"run {manifest['run_id']} / source {manifest['git_source_commit'][:12]} / "
        f"software {manifest['software_version']} / app {manifest['application_version']}"
    )
    draw.text((45, 1320), trace, fill=muted, font=_font(12))
    draw.text((45, 1357), manifest["warning"], fill="#33443e", font=_font(10))
    if path.exists():
        raise LabelReviewHandoffError(f"refusing to overwrite existing output {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def _zip_info(name: str, timestamp: tuple[int, int, int, int, int, int]) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(_member_name(name), date_time=timestamp)
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    info.flag_bits = 0
    return info


def write_deterministic_archive(
    *,
    archive_path: Path,
    generated_at_utc: str,
    member_payloads: dict[str, bytes],
    member_order: list[str],
) -> dict[str, Any]:
    if archive_path.exists():
        raise LabelReviewHandoffError(f"refusing to overwrite existing archive {archive_path.name}")
    if set(member_payloads) != set(member_order) or len(member_order) != len(set(member_order)):
        raise LabelReviewHandoffError("archive member order does not match unique payloads")
    if FORBIDDEN_ARCHIVE_NAMES.intersection(member_payloads):
        raise LabelReviewHandoffError("forbidden proposal or QA material entered the archive")
    timestamp = _validate_timestamp(generated_at_utc)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path, mode="x", compression=zipfile.ZIP_STORED) as archive:
        for name in member_order:
            archive.writestr(_zip_info(name, timestamp), member_payloads[name])
    return {
        "path": archive_path.name,
        "bytes": archive_path.stat().st_size,
        "sha256": _sha256_file(archive_path),
        "member_count": len(member_order),
    }


def build_handoff(
    *,
    packet_path: Path,
    output_directory: Path,
    archive_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Path]]:
    packet, _ = _validate_source_packet(packet_path)
    response_template_path = packet_path.parent / RESPONSE_TEMPLATE_NAME
    response_template = _validate_response_template(response_template_path, packet)
    blind_paths = _validate_blind_pages(packet_path, packet)

    html_payload = render_workbench_html(
        packet=packet,
        response_template=deepcopy(response_template),
    ).replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    readme_payload = render_readme().replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    payloads = {
        HANDOFF_HTML_NAME: html_payload,
        HANDOFF_README_NAME: readme_payload,
        RESPONSE_TEMPLATE_NAME: response_template_path.read_bytes(),
        **{path.name: path.read_bytes() for path in blind_paths},
    }
    manifest = build_handoff_manifest(
        packet=packet,
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
        payloads=payloads,
    )
    manifest_payload = (
        json.dumps(manifest, indent=2, ensure_ascii=True).replace("\r\n", "\n").replace("\r", "\n")
        + "\n"
    ).encode("utf-8")

    paths = {
        "html": output_directory / HANDOFF_HTML_NAME,
        "json": output_directory / HANDOFF_JSON_NAME,
        "png": output_directory / HANDOFF_PNG_NAME,
        "readme": output_directory / HANDOFF_README_NAME,
        "archive": archive_path,
    }
    _write_new_bytes(paths["html"], html_payload)
    _write_new_bytes(paths["json"], manifest_payload)
    _write_new_bytes(paths["readme"], readme_payload)
    render_handoff_png(manifest, paths["png"])

    archive_payloads = {
        HANDOFF_JSON_NAME: manifest_payload,
        **payloads,
    }
    archive = write_deterministic_archive(
        archive_path=archive_path,
        generated_at_utc=generated_at_utc,
        member_payloads=archive_payloads,
        member_order=manifest["archive_contract"]["member_order"],
    )
    return manifest, archive, paths
