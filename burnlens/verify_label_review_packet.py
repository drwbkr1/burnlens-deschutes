"""Independently verify a BurnLens label-review packet and supplied responses.

The verifier checks packet bindings, blind/reveal separation, blank templates,
and the domain/completeness of any actual reviewer responses.  It never converts
software QA into human label evidence or authorizes dataset candidacy.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from .optical_pair_evidence import WARNING, _font


SOFTWARE_VERSION = "0.13.0"
EXPECTED_PACKET_ID = "LABEL-REVIEW-PACKET-2026-001"
EXPECTED_PACKET_SCHEMA = "0.1.0"
EXPECTED_REVIEW_PROTOCOL = "proposal-blinded-label-review-readiness-v0.1.0"
EXPECTED_RESPONSE_SCHEMA = "burnlens-label-review-response-v0.1.0"
EXPECTED_ADJUDICATION_PROTOCOL = "burnlens-label-adjudication-v0.1.0"
EXPECTED_PACKET_DECISION = "READY_FOR_INDEPENDENT_REVIEW_DEFER_DATASET"
QA_REPORT_ID = "LABEL-REVIEW-PACKET-QA-2026-001"
QA_SCHEMA_VERSION = "0.1.0"
QA_REPORT_VERSION = "label-review-packet-integrity-qa-v0.1.0"
TASK_ISSUE = 375

STATE_TARGET = {
    "background-candidate": 0,
    "burned": 1,
    "unknown": None,
    "excluded": None,
    "review-needed": None,
}
FIRST_PASS_LABELS = {"burned", "background", "uncertain", "unusable"}
EVIDENCE_SUFFICIENCY = {"sufficient", "limited", "insufficient"}
CONFIDENCE_LEVELS = {"low", "medium", "high"}
REASON_CODES = {
    "pre-post-change",
    "persistent-darkening",
    "vegetation-loss",
    "source-context-support",
    "source-context-conflict",
    "cloud-smoke-shadow",
    "registration-concern",
    "boundary-ambiguity",
    "low-severity-ambiguity",
    "non-fire-change-possible",
    "other",
}


class LabelReviewVerificationError(RuntimeError):
    """A deterministic review-packet verification failure."""


def _write_utf8_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    path.write_bytes(normalized.encode("utf-8"))


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
        raise LabelReviewVerificationError(f"invalid JSON input {path.name}") from error
    if not isinstance(value, dict):
        raise LabelReviewVerificationError(f"JSON input {path.name} is not an object")
    return value


def _walk_keys(value: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            keys.append(str(key))
            keys.extend(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.extend(_walk_keys(child))
    return keys


def _verify_output_files(packet: dict[str, Any], directory: Path) -> list[dict[str, Any]]:
    files = packet.get("outputs", {}).get("files")
    if not isinstance(files, list) or not files:
        raise LabelReviewVerificationError("packet output inventory is missing")
    checked = []
    seen = set()
    for item in files:
        relative = item.get("path")
        if not isinstance(relative, str):
            raise LabelReviewVerificationError("packet output path is invalid")
        candidate = Path(relative)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise LabelReviewVerificationError("packet output path escapes its directory")
        if relative in seen:
            raise LabelReviewVerificationError("packet output path is duplicated")
        seen.add(relative)
        path = directory / candidate
        if not path.is_file():
            raise LabelReviewVerificationError(f"packet output is missing: {relative}")
        observed = {
            "path": relative,
            "bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
        }
        if observed != item:
            raise LabelReviewVerificationError(f"packet output binding changed: {relative}")
        checked.append(observed)
    return checked


def _verify_blind_boundary(packet: dict[str, Any], directory: Path) -> dict[str, Any]:
    blind_name = f"{EXPECTED_PACKET_ID}-BLIND.html"
    reveal_name = f"{EXPECTED_PACKET_ID}-REVEAL.html"
    blind_path = directory / blind_name
    reveal_path = directory / reveal_name
    blind = blind_path.read_text(encoding="utf-8")
    reveal = reveal_path.read_text(encoding="utf-8")
    forbidden_blind_tokens = (
        "proposal_state",
        "proposal_target",
        "proposed state</th>",
        f'href="{reveal_name}"',
        "background-candidate",
        "review-needed",
    )
    found = [token for token in forbidden_blind_tokens if token.lower() in blind.lower()]
    if found:
        raise LabelReviewVerificationError(
            f"blind first-pass document exposes reveal tokens: {', '.join(found)}"
        )
    if "Proposal reveal and adjudication key" not in reveal:
        raise LabelReviewVerificationError("reveal document identity is missing")
    if "Opening this page before first-pass completion disqualifies" not in reveal:
        raise LabelReviewVerificationError("reveal ordering warning is missing")
    page_count = int(packet["outputs"]["blind_page_count"])
    for page_index in range(1, page_count + 1):
        page_name = f"{EXPECTED_PACKET_ID}-BLIND-{page_index:02d}.png"
        if page_name not in blind:
            raise LabelReviewVerificationError(f"blind HTML omits page {page_index:02d}")
    return {
        "blind_html_sha256": _sha256_file(blind_path),
        "reveal_html_sha256": _sha256_file(reveal_path),
        "blind_page_count": page_count,
        "forbidden_reveal_tokens_found": [],
        "reveal_ordering_warning_present": True,
    }


def _verify_units(packet: dict[str, Any]) -> dict[str, Any]:
    events = packet.get("events")
    units = packet.get("units")
    coverage = packet.get("coverage")
    if not isinstance(events, list) or len(events) != 3:
        raise LabelReviewVerificationError("packet must bind exactly three events")
    if not isinstance(units, list) or not units:
        raise LabelReviewVerificationError("packet review units are missing")
    if not isinstance(coverage, list) or len(coverage) != 15:
        raise LabelReviewVerificationError("packet event/state coverage is incomplete")
    event_by_id = {item.get("event_group_id"): item for item in events}
    if len(event_by_id) != 3 or None in event_by_id:
        raise LabelReviewVerificationError("packet event identities are invalid")
    unit_ids = [item.get("sample_id") for item in units]
    expected_ids = [f"LRU-{index:03d}" for index in range(1, len(units) + 1)]
    if unit_ids != expected_ids:
        raise LabelReviewVerificationError("packet sample IDs are not exact and sequential")
    coordinate_keys = set()
    counted = Counter()
    for unit in units:
        event_id = unit.get("event_group_id")
        if event_id not in event_by_id:
            raise LabelReviewVerificationError("review unit references an unknown event")
        event = event_by_id[event_id]
        row, column = unit.get("row"), unit.get("column")
        if not isinstance(row, int) or not isinstance(column, int):
            raise LabelReviewVerificationError("review unit coordinates are invalid")
        if row < 0 or column < 0 or row >= event["grid"]["height"] or column >= event["grid"]["width"]:
            raise LabelReviewVerificationError("review unit falls outside its event grid")
        key = (event_id, row, column)
        if key in coordinate_keys:
            raise LabelReviewVerificationError("review unit pixel is duplicated")
        coordinate_keys.add(key)
        state = unit.get("proposal_state")
        if state not in STATE_TARGET:
            raise LabelReviewVerificationError("review unit proposal state is invalid")
        if unit.get("proposal_state_code") not in range(5):
            raise LabelReviewVerificationError("review unit proposal state code is invalid")
        if unit.get("proposal_target_value") != STATE_TARGET[state]:
            raise LabelReviewVerificationError("review unit target mapping is invalid")
        if not isinstance(unit.get("selection_hash"), str) or len(unit["selection_hash"]) != 64:
            raise LabelReviewVerificationError("review unit selection hash is invalid")
        counted[(event_id, state)] += 1
    coverage_counted = {
        (item["event_group_id"], item["proposal_state"]): item["selected_units"]
        for item in coverage
    }
    if dict(counted) != {key: value for key, value in coverage_counted.items() if value}:
        raise LabelReviewVerificationError("review units do not match coverage counts")
    summary = packet.get("coverage_summary", {})
    if summary.get("selected_units") != len(units):
        raise LabelReviewVerificationError("packet coverage total differs from review units")
    if packet.get("decision") != EXPECTED_PACKET_DECISION:
        raise LabelReviewVerificationError("packet overstates its review decision")
    gates = packet.get("quality_gates", {})
    forbidden_true = (
        "dataset_created",
        "split_created",
        "baseline_created",
        "model_created",
        "accuracy_claim_created",
        "field_validation_claim_created",
    )
    if any(gates.get(key) is not False for key in forbidden_true):
        raise LabelReviewVerificationError("packet quality gates overstate downstream evidence")
    if gates.get("completed_independent_responses") != 0 or gates.get("completed_adjudications") != 0:
        raise LabelReviewVerificationError("packet claims unprovided human evidence")
    return {
        "event_count": len(events),
        "unit_count": len(units),
        "unique_pixel_count": len(coordinate_keys),
        "coverage_strata": len(coverage),
        "structural_absences": summary.get("strata_structurally_absent"),
    }


def _verify_blank_response_template(
    packet: dict[str, Any],
    path: Path,
) -> dict[str, Any]:
    template = _load_json(path)
    if template.get("response_schema_version") != EXPECTED_RESPONSE_SCHEMA:
        raise LabelReviewVerificationError("response template schema changed")
    if template.get("packet_id") != EXPECTED_PACKET_ID or template.get("packet_run_id") != packet["run_id"]:
        raise LabelReviewVerificationError("response template packet binding changed")
    forbidden_keys = {"proposal_state", "proposal_state_code", "proposal_target_value", "dnbr_center"}
    if forbidden_keys.intersection(_walk_keys(template)):
        raise LabelReviewVerificationError("blank response template leaks proposal values")
    expected_ids = [unit["sample_id"] for unit in packet["units"]]
    responses = template.get("responses")
    if not isinstance(responses, list) or [item.get("sample_id") for item in responses] != expected_ids:
        raise LabelReviewVerificationError("response template sample bindings changed")
    if template.get("completed") is not False:
        raise LabelReviewVerificationError("blank response template is marked complete")
    reviewer = template.get("reviewer", {})
    if any(value is not None for value in reviewer.values()):
        raise LabelReviewVerificationError("blank response template contains reviewer data")
    for item in responses:
        if item.get("first_pass_label") is not None:
            raise LabelReviewVerificationError("blank response template contains a label")
        if item.get("evidence_sufficiency") is not None or item.get("confidence") is not None:
            raise LabelReviewVerificationError("blank response template contains a judgment")
        if item.get("reason_codes") != [] or item.get("notes") is not None:
            raise LabelReviewVerificationError("blank response template contains review content")
    return {
        "sha256": _sha256_file(path),
        "sample_count": len(responses),
        "proposal_value_keys_found": [],
        "blank": True,
    }


def _verify_blank_adjudication_template(
    packet: dict[str, Any],
    path: Path,
) -> dict[str, Any]:
    template = _load_json(path)
    if template.get("adjudication_protocol_version") != EXPECTED_ADJUDICATION_PROTOCOL:
        raise LabelReviewVerificationError("adjudication template protocol changed")
    if template.get("packet_id") != EXPECTED_PACKET_ID or template.get("packet_run_id") != packet["run_id"]:
        raise LabelReviewVerificationError("adjudication template packet binding changed")
    if template.get("completed") is not False or template.get("input_response_sha256") != []:
        raise LabelReviewVerificationError("blank adjudication template contains completed evidence")
    expected_ids = [unit["sample_id"] for unit in packet["units"]]
    decisions = template.get("decisions")
    if not isinstance(decisions, list) or [item.get("sample_id") for item in decisions] != expected_ids:
        raise LabelReviewVerificationError("adjudication template sample bindings changed")
    for item in decisions:
        if any(item.get(key) is not None for key in ("required", "final_label", "evidence_sufficiency", "reason")):
            raise LabelReviewVerificationError("blank adjudication template contains a decision")
    return {"sha256": _sha256_file(path), "sample_count": len(decisions), "blank": True}


def validate_completed_response(
    packet: dict[str, Any],
    response: dict[str, Any],
    *,
    response_sha256: str,
) -> dict[str, Any]:
    if response.get("response_schema_version") != EXPECTED_RESPONSE_SCHEMA:
        raise LabelReviewVerificationError("completed response schema is invalid")
    forbidden_keys = {"proposal_state", "proposal_state_code", "proposal_target_value", "dnbr_center"}
    if forbidden_keys.intersection(_walk_keys(response)):
        raise LabelReviewVerificationError("completed response includes proposal-value fields")
    if response.get("packet_id") != EXPECTED_PACKET_ID or response.get("packet_run_id") != packet["run_id"]:
        raise LabelReviewVerificationError("completed response packet binding is invalid")
    if response.get("completed") is not True:
        raise LabelReviewVerificationError("supplied response is not marked complete")
    reviewer = response.get("reviewer")
    if not isinstance(reviewer, dict):
        raise LabelReviewVerificationError("completed response reviewer block is missing")
    reviewer_id = reviewer.get("reviewer_id")
    if not isinstance(reviewer_id, str) or not reviewer_id.strip():
        raise LabelReviewVerificationError("completed response reviewer ID is missing")
    if reviewer.get("independent_from_proposal_author") is not True:
        raise LabelReviewVerificationError("completed response lacks independence attestation")
    if reviewer.get("proposal_seen_before_first_pass") is not False:
        raise LabelReviewVerificationError("completed response is not proposal-blinded")
    if not isinstance(reviewer.get("attestation"), str) or not reviewer["attestation"].strip():
        raise LabelReviewVerificationError("completed response attestation is missing")
    started = response.get("review_started_at_utc")
    completed = response.get("review_completed_at_utc")
    if not isinstance(started, str) or not isinstance(completed, str):
        raise LabelReviewVerificationError("completed response timestamps are missing")
    try:
        started_at = datetime.fromisoformat(started.replace("Z", "+00:00"))
        completed_at = datetime.fromisoformat(completed.replace("Z", "+00:00"))
    except ValueError as error:
        raise LabelReviewVerificationError("completed response timestamps are invalid") from error
    if started_at.tzinfo is None or completed_at.tzinfo is None or completed_at < started_at:
        raise LabelReviewVerificationError("completed response timestamp order is invalid")
    expected_ids = [unit["sample_id"] for unit in packet["units"]]
    responses = response.get("responses")
    if not isinstance(responses, list) or [item.get("sample_id") for item in responses] != expected_ids:
        raise LabelReviewVerificationError("completed response sample order or coverage is invalid")
    counts = Counter()
    for item in responses:
        label = item.get("first_pass_label")
        sufficiency = item.get("evidence_sufficiency")
        confidence = item.get("confidence")
        reasons = item.get("reason_codes")
        notes = item.get("notes")
        if label not in FIRST_PASS_LABELS:
            raise LabelReviewVerificationError("completed response label is out of domain")
        if sufficiency not in EVIDENCE_SUFFICIENCY:
            raise LabelReviewVerificationError("completed response evidence sufficiency is out of domain")
        if confidence not in CONFIDENCE_LEVELS:
            raise LabelReviewVerificationError("completed response confidence is out of domain")
        if not isinstance(reasons, list) or not reasons or len(reasons) != len(set(reasons)):
            raise LabelReviewVerificationError("completed response reason codes are missing or duplicated")
        if set(reasons) - REASON_CODES:
            raise LabelReviewVerificationError("completed response reason code is out of domain")
        if notes is not None and (not isinstance(notes, str) or len(notes) > 1000):
            raise LabelReviewVerificationError("completed response notes are invalid")
        counts[label] += 1
    return {
        "response_sha256": response_sha256,
        "reviewer_id": reviewer_id,
        "qualifying_independent_blinded_response": True,
        "unit_count": len(responses),
        "label_counts": dict(counts),
        "insufficient_evidence_units": sum(
            item["evidence_sufficiency"] == "insufficient" for item in responses
        ),
        "uncertain_or_unusable_units": sum(
            item["first_pass_label"] in {"uncertain", "unusable"} for item in responses
        ),
    }


def build_qa_report(
    *,
    packet_path: Path,
    response_paths: list[Path],
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    packet = _load_json(packet_path)
    if packet.get("report_id") != EXPECTED_PACKET_ID:
        raise LabelReviewVerificationError("packet identity is invalid")
    if packet.get("schema_version") != EXPECTED_PACKET_SCHEMA:
        raise LabelReviewVerificationError("packet schema is invalid")
    if packet.get("review_protocol_version") != EXPECTED_REVIEW_PROTOCOL:
        raise LabelReviewVerificationError("packet review protocol is invalid")
    directory = packet_path.parent
    output_checks = _verify_output_files(packet, directory)
    unit_checks = _verify_units(packet)
    blind_checks = _verify_blind_boundary(packet, directory)
    response_template_path = directory / f"{EXPECTED_PACKET_ID}-RESPONSE-TEMPLATE.json"
    adjudication_template_path = directory / f"{EXPECTED_PACKET_ID}-ADJUDICATION-TEMPLATE.json"
    response_template_checks = _verify_blank_response_template(packet, response_template_path)
    adjudication_template_checks = _verify_blank_adjudication_template(
        packet, adjudication_template_path
    )
    response_summaries = []
    reviewer_ids = set()
    for path in response_paths:
        response = _load_json(path)
        summary = validate_completed_response(
            packet, response, response_sha256=_sha256_file(path)
        )
        if summary["reviewer_id"] in reviewer_ids:
            raise LabelReviewVerificationError("qualifying reviewer ID is duplicated")
        reviewer_ids.add(summary["reviewer_id"])
        response_summaries.append(summary)
    if len(response_summaries) >= 2:
        decision = "PASS_PACKET_INTEGRITY_RESPONSES_READY_FOR_ADJUDICATION_DEFER_DATASET"
        detail = (
            "Packet integrity passed and at least two qualifying complete proposal-blinded responses "
            "were supplied. Adjudication and label-fitness evaluation remain separate required work."
        )
    elif response_summaries:
        decision = "PASS_PACKET_INTEGRITY_RESPONSES_PRESENT_DEFER_DATASET"
        detail = (
            "Packet integrity passed, but fewer than two qualifying complete independent responses "
            "were supplied. Dataset candidacy remains deferred."
        )
    else:
        decision = "PASS_PACKET_INTEGRITY_READY_FOR_INDEPENDENT_REVIEW_DEFER_DATASET"
        detail = (
            "Packet files, sample bindings, blind/reveal separation, and blank templates passed. "
            "No completed independent response was supplied, so dataset candidacy remains deferred."
        )
    return {
        "report_id": QA_REPORT_ID,
        "schema_version": QA_SCHEMA_VERSION,
        "report_version": QA_REPORT_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": None,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "packet_binding": {
            "report_id": packet["report_id"],
            "run_id": packet["run_id"],
            "git_source_commit": packet["git_source_commit"],
            "sha256": _sha256_file(packet_path),
            "decision": packet["decision"],
        },
        "checks": {
            "output_files": output_checks,
            "units": unit_checks,
            "blind_boundary": blind_checks,
            "response_template": response_template_checks,
            "adjudication_template": adjudication_template_checks,
        },
        "completed_response_count": len(response_summaries),
        "completed_responses": response_summaries,
        "independent_human_review_completed": len(response_summaries) >= 2,
        "adjudication_completed": False,
        "dataset_created": False,
        "accuracy_claim_created": False,
        "decision": decision,
        "decision_detail": detail,
        "claims": {
            "proven": [
                "The committed packet files and exact sample bindings pass an independently implemented structural verifier.",
                "The blank response and adjudication templates contain no proposal-value fields.",
                "Any supplied response summary is derived only from an actual validated response file.",
            ],
            "not_proven": [
                "Packet integrity is not human label fitness, inter-rater agreement, adjudication, field validation, or accuracy.",
                "No dataset, split, baseline, model, application, deployment, official status, or endorsement is established.",
            ],
        },
        "warning": WARNING,
    }


def render_qa_png(report: dict[str, Any], path: Path) -> None:
    canvas = Image.new("RGB", (1800, 1320), "#f4f0e8")
    draw = ImageDraw.Draw(canvas)
    ink, muted, teal, orange = "#15211d", "#5d6b64", "#006b64", "#f05a28"
    draw.rectangle((0, 0, 1800, 185), fill="#132a26")
    draw.text((55, 30), "BURNLENS / LABEL REVIEW PACKET", fill="#b9d8cf", font=_font(19))
    draw.text((55, 72), "INDEPENDENT INTEGRITY QA", fill="white", font=_font(37))
    draw.text(
        (55, 127),
        "File bindings + blind boundary + blank templates + actual-response validation",
        fill="#b9d8cf",
        font=_font(16),
    )
    metrics = [
        (str(report["checks"]["units"]["unit_count"]), "review units"),
        (str(report["checks"]["blind_boundary"]["blind_page_count"]), "blind pages"),
        (str(report["completed_response_count"]), "completed responses"),
        ("0", "completed adjudications"),
    ]
    for index, (value, label) in enumerate(metrics):
        left = 45 + index * 430
        draw.rounded_rectangle((left, 230, left + 390, 350), radius=15, fill="#e5efeb")
        draw.text((left + 24, 250), value, fill=teal, font=_font(31))
        draw.text((left + 24, 307), label, fill=muted, font=_font(14))
    draw.rounded_rectangle((45, 400, 1755, 930), radius=18, fill="#fffdf8", outline="#d4cec1", width=2)
    draw.text((72, 430), "VERIFIED CONTRACT", fill=teal, font=_font(21))
    lines = [
        f"{len(report['checks']['output_files'])} inventoried packet files match exact size and SHA-256 bindings.",
        "Every sample ID, pixel coordinate, event binding, proposal state, and binary-ignore mapping is valid.",
        "The first-pass HTML contains no reveal link or sample-specific proposal-value fields.",
        "Response and adjudication templates are blank, complete in sample coverage, and proposal-value free.",
        f"Actual qualifying response files supplied: {report['completed_response_count']}.",
        "Verifier output cannot authorize a dataset, accuracy result, model, or field-validation claim.",
    ]
    for index, line in enumerate(lines):
        draw.text((88, 485 + index * 58), f"{index + 1}. {line}", fill=ink, font=_font(15))
    draw.text((72, 845), report["decision"], fill=orange, font=_font(19))
    draw.text((45, 990), report["decision_detail"], fill=ink, font=_font(15))
    trace = (
        f"run {report['run_id']} / source {report['git_source_commit'][:12]} / software {report['software_version']} / "
        f"packet {report['packet_binding']['run_id']}"
    )
    draw.text((45, 1090), trace, fill=muted, font=_font(12))
    draw.text((45, 1130), "dataset none / split none / baseline none / model none / adjudication none", fill=orange, font=_font(14))
    draw.text((45, 1175), report["warning"], fill="#33443e", font=_font(10))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_qa_html(report: dict[str, Any], png_name: str, path: Path) -> None:
    response_rows = "".join(
        f"<tr><td>{escape(item['reviewer_id'])}</td><td><code>{escape(item['response_sha256'])}</code></td><td>{item['unit_count']}</td><td>{item['insufficient_evidence_units']}</td><td>{item['uncertain_or_unusable_units']}</td></tr>"
        for item in report["completed_responses"]
    )
    if not response_rows:
        response_rows = '<tr><td colspan="5">No completed response supplied.</td></tr>'
    document = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens label-review packet QA</title><style>
body{{margin:0;background:#f4f0e8;color:#15211d;font:16px/1.55 system-ui,sans-serif}}header{{background:#132a26;color:white;padding:3rem max(5vw,2rem)}}header p{{color:#b9d8cf}}main{{max-width:1300px;margin:auto;padding:2.5rem 1.5rem 5rem}}.hero{{width:100%;height:auto;border:1px solid #c8c0b2}}.warning{{background:#fff1ca;border-left:6px solid #d87618;padding:1rem;font-weight:650}}.card{{background:#fffdf8;border:1px solid #d9d1c4;border-radius:12px;padding:1.2rem;margin:1.2rem 0}}.decision{{border:2px solid #f05a28}}.table{{overflow-x:auto}}table{{width:100%;border-collapse:collapse}}th,td{{padding:.6rem;border-bottom:1px solid #ddd5c9;text-align:left}}code{{overflow-wrap:anywhere}}
</style></head><body><header><p>BurnLens / Phase Two / Objective Four</p><h1>Label-review packet integrity QA</h1><p>Independent structural verification. Not human label evidence.</p></header><main>
<p class="warning">{escape(report['warning'])}</p><img class="hero" src="{escape(png_name)}" alt="BurnLens label-review packet integrity QA">
<section class="card decision"><h2>Decision</h2><p><strong>{escape(report['decision'])}</strong></p><p>{escape(report['decision_detail'])}</p></section>
<section class="card"><h2>Packet checks</h2><p>{len(report['checks']['output_files'])} output files; {report['checks']['units']['unit_count']} unique units; {report['checks']['blind_boundary']['blind_page_count']} blind pages; blank response and adjudication templates passed.</p></section>
<section class="card"><h2>Actual completed responses</h2><div class="table"><table><thead><tr><th>Opaque reviewer ID</th><th>Response SHA-256</th><th>Units</th><th>Insufficient</th><th>Uncertain/unusable</th></tr></thead><tbody>{response_rows}</tbody></table></div></section>
<section class="card"><h2>Traceability and limits</h2><p><strong>Run:</strong> <code>{escape(report['run_id'])}</code><br><strong>Git source:</strong> <code>{escape(report['git_source_commit'])}</code><br><strong>Packet SHA-256:</strong> <code>{escape(report['packet_binding']['sha256'])}</code><br><strong>Dataset / split / baseline / model:</strong> none / none / none / none</p><ul>{''.join(f'<li><strong>Not proven:</strong> {escape(item)}</li>' for item in report['claims']['not_proven'])}</ul></section>
</main></body></html>"""
    _write_utf8_lf(path, document)


def write_qa_report(
    report: dict[str, Any],
    *,
    json_path: Path,
    html_path: Path,
    png_path: Path,
) -> None:
    _write_utf8_lf(json_path, json.dumps(report, indent=2) + "\n")
    render_qa_png(report, png_path)
    render_qa_html(report, png_path.name, html_path)
