"""Validate, reconcile, and render the exact BurnLens owner response safely."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from hashlib import sha256
from html import escape
from io import BytesIO
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .lock_owner_review_response import validate_response
from .owner_review_surface import OwnerReviewSurfaceError
from .promotion_gate_preflight import (
    PROTOCOL_VERSION,
    SOURCE_PRECEDENCE_ID,
    SURFACE_SHA256,
    TERMS_REVIEW_ID,
    evaluate_units,
    verify_surface_reconstruction,
)


REPORT_ID = "OWNER-RESPONSE-INTAKE-2026-001"
PRIVATE_REPORT_ID = "OWNER-RESPONSE-INTAKE-PRIVATE-2026-001"
REPORT_VERSION = "owner-response-intake-v0.1.0"
PRIVATE_REPORT_VERSION = "owner-response-private-reconciliation-v0.1.0"
SOFTWARE_VERSION = "0.26.0"
TASK_ISSUE = 437
LABEL_SET_VERSION = "owner-approved-prototype-labels-v0.1.0"
CONFIRMATION_ID = "OWNER-CONFIRMATION-2026-002"
RESPONSE_BYTES = 7608
RESPONSE_SHA256 = "fd8ad8280ea066306da95936dca37ad02a3ee597bdba00203ce34d720ba877b8"
RECEIPT_BYTES = 1366
RECEIPT_SHA256 = "09533b0a261c01d5403f9728db45c29086fa4606ee655d45010e099ba1741ed9"
EXPECTED_DECISIONS = {"yes": 53, "no": 2, "uncertain": 1}
EXPECTED_EVENTS = {
    "event-darlene3-or-2024",
    "event-mckay-1035-ne-2017",
    "event-tepee-1144-ne-2018",
}
WARNING = (
    "Experimental BurnLens CV evidence. Not official wildfire information. "
    "Not emergency guidance. Official sources govern."
)


class OwnerResponseIntakeError(RuntimeError):
    """A fail-closed owner-response intake or reconciliation failure."""


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise OwnerResponseIntakeError(message)


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _regular_bytes(path: Path, label: str) -> bytes:
    try:
        metadata = path.stat(follow_symlinks=False)
    except OSError as error:
        raise OwnerResponseIntakeError(f"{label} is unavailable") from error
    _assert(not path.is_symlink() and stat.S_ISREG(metadata.st_mode), f"{label} must be a regular non-link file")
    _assert(metadata.st_size > 0, f"{label} is empty")
    return path.read_bytes()


def _json(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise OwnerResponseIntakeError(f"{label} is not valid UTF-8 JSON") from error
    _assert(isinstance(value, dict), f"{label} root must be an object")
    return value


def _utc(value: Any, label: str) -> datetime:
    _assert(isinstance(value, str) and value.endswith("Z"), f"{label} must be UTC with Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as error:
        raise OwnerResponseIntakeError(f"{label} is invalid") from error
    return parsed


def _validate_confirmation(path: Path) -> dict[str, Any]:
    value = _json(_regular_bytes(path, "owner confirmation record"), "owner confirmation record")
    _assert(value.get("confirmation_id") == CONFIRMATION_ID, "owner confirmation identity drift")
    _assert(value.get("authoritative_response", {}).get("bytes") == RESPONSE_BYTES, "owner confirmation byte drift")
    _assert(value.get("authoritative_response", {}).get("sha256") == RESPONSE_SHA256, "owner confirmation hash drift")
    _assert(value.get("authoritative_response", {}).get("decision_counts") == EXPECTED_DECISIONS, "owner confirmation count drift")
    _assert(value.get("older_export_excluded") is True, "older export exclusion is missing")
    _assert(value.get("controlled_intake_authorized") is True, "controlled intake is not authorized")
    return value


def _validate_receipt(receipt: dict[str, Any], response: dict[str, Any], response_bytes: bytes) -> None:
    _assert(receipt.get("report_id") == "OWNER-REVIEW-SURFACE-2026-001-RECEIPT", "receipt identity drift")
    _assert(receipt.get("evidence_origin") == "owner-returned-response", "receipt origin is not owner-returned")
    _assert(receipt.get("software_browser_fixture") is False, "receipt incorrectly marks a software fixture")
    _assert(receipt.get("exact_response_preserved_without_overwrite") is True, "receipt lacks no-overwrite custody")
    binding = receipt.get("response_binding", {})
    _assert(binding.get("bytes") == len(response_bytes) == RESPONSE_BYTES, "receipt response byte drift")
    _assert(binding.get("sha256") == _digest(response_bytes) == RESPONSE_SHA256, "receipt response hash drift")
    _assert(binding.get("decision_counts") == EXPECTED_DECISIONS, "receipt decision counts drift")
    _assert(receipt.get("surface_binding", {}).get("sha256") == SURFACE_SHA256, "receipt surface hash drift")
    _assert(receipt.get("decision") == "PASS_EXACT_OWNER_RESPONSE_LOCK_DEFER_LABEL_PROMOTION_GATES", "receipt decision drift")
    _assert(_utc(receipt.get("received_at_utc"), "received time") >= _utc(response.get("review_completed_at_utc"), "completed time"), "receipt predates completion")


def _assert_source_direction(units: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter()
    for unit in units:
        if unit["current_status"] != "ELIGIBLE_OWNER_APPROVED_PROTOTYPE_LABEL":
            continue
        categorical = unit["gates"]["source"]["categorical_evidence"]
        affirmative = any(item["semantic"] == "affirmative burn evidence" for item in categorical)
        if unit["candidate_label"] == "burned":
            _assert(affirmative, f"approved burned unit lacks current categorical affirmative support: {unit['sample_id']}")
            counts["burned_with_affirmative_current_reference"] += 1
        else:
            _assert(not affirmative, f"approved background unit conflicts with current categorical evidence: {unit['sample_id']}")
            counts["background_without_affirmative_current_reference"] += 1
    return dict(sorted(counts.items()))


def build_private_reconciliation(
    *,
    repository_root: Path,
    archive_dir: Path,
    packet_path: Path,
    bundle_report_path: Path,
    surface_path: Path,
    response_path: Path,
    receipt_path: Path,
    confirmation_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    _assert(len(git_source_commit) == 40 and all(char in "0123456789abcdef" for char in git_source_commit), "source commit is invalid")
    _utc(generated_at_utc, "generated time")
    confirmation = _validate_confirmation(confirmation_path)
    response_bytes = _regular_bytes(response_path, "preserved owner response")
    receipt_bytes = _regular_bytes(receipt_path, "preserved response receipt")
    _assert(len(response_bytes) == RESPONSE_BYTES and _digest(response_bytes) == RESPONSE_SHA256, "authoritative response bytes drift")
    _assert(len(receipt_bytes) == RECEIPT_BYTES and _digest(receipt_bytes) == RECEIPT_SHA256, "authoritative receipt bytes drift")
    response = _json(response_bytes, "preserved owner response")
    receipt = _json(receipt_bytes, "preserved response receipt")

    proof = verify_surface_reconstruction(
        repository_root=repository_root,
        archive_dir=archive_dir,
        packet_path=packet_path,
        bundle_report_path=bundle_report_path,
        surface_path=surface_path,
    )
    surface = proof.pop("surface")
    summary = validate_response(surface, response)
    _assert(summary["decision_counts"] == EXPECTED_DECISIONS, "validated decision counts drift")
    _validate_receipt(receipt, response, response_bytes)
    units, status_counts = evaluate_units(surface, response)
    _assert(status_counts.get("ELIGIBLE_OWNER_APPROVED_PROTOTYPE_LABEL") == 24, "eligible prototype label count drift")
    _assert(status_counts.get("EXCLUDED_QUALITY_BLOCKED_AFTER_YES") == 29, "quality-blocked yes count drift")
    _assert(status_counts.get("EXCLUDED_BY_OWNER_RESPONSE") == 3, "owner-excluded count drift")

    approved = [unit for unit in units if unit["current_status"] == "ELIGIBLE_OWNER_APPROVED_PROTOTYPE_LABEL"]
    _assert({unit["event_group_id"] for unit in approved} == EXPECTED_EVENTS, "approved event coverage drift")
    class_counts = dict(sorted(Counter(unit["candidate_label"] for unit in approved).items()))
    event_counts = dict(sorted(Counter(unit["event_group_id"] for unit in approved).items()))
    event_class_counts = dict(sorted(Counter(f"{unit['event_group_id']}::{unit['candidate_label']}" for unit in approved).items()))
    _assert(class_counts == {"background": 12, "burned": 12}, "approved class balance drift")
    _assert(all(value == 8 for value in event_counts.values()), "approved event balance drift")
    _assert(all(value == 4 for value in event_class_counts.values()), "approved event/class balance drift")
    source_direction = _assert_source_direction(units)
    _assert(source_direction == {
        "background_without_affirmative_current_reference": 12,
        "burned_with_affirmative_current_reference": 12,
    }, "approved source-direction inventory drift")

    private_units = [
        {
            "sample_id": unit["sample_id"],
            "event_group_id": unit["event_group_id"],
            "candidate_label": unit["candidate_label"],
            "frozen_proposal_state": unit["frozen_proposal_state"],
            "selection_hash": unit["selection_hash"],
            "presentation_hash": unit["presentation_hash"],
            "owner_decision": unit["owner_decision"],
            "gate_status": {name: gate["status"] for name, gate in unit["gates"].items()},
            "disposition": unit["current_status"],
            "prototype_target": (
                1 if unit["current_status"] == "ELIGIBLE_OWNER_APPROVED_PROTOTYPE_LABEL" and unit["candidate_label"] == "burned"
                else 0 if unit["current_status"] == "ELIGIBLE_OWNER_APPROVED_PROTOTYPE_LABEL"
                else None
            ),
        }
        for unit in units
    ]
    return {
        "report_id": PRIVATE_REPORT_ID,
        "report_version": PRIVATE_REPORT_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "owner_confirmation_id": confirmation["confirmation_id"],
        "response_binding": {"bytes": len(response_bytes), "sha256": RESPONSE_SHA256},
        "receipt_binding": {"bytes": len(receipt_bytes), "sha256": RECEIPT_SHA256},
        "surface_binding": {"bytes": proof["surface_bytes"], "sha256": proof["surface_sha256"]},
        "reconstruction": proof,
        "label_set_version": LABEL_SET_VERSION,
        "provenance": {
            "aoi_version": surface["provenance"]["aoi_version"],
            "target_version": surface["provenance"]["target_version"],
            "label_schema_version": surface["provenance"]["label_schema_version"],
            "dataset_version": None,
            "split_version": None,
            "baseline_version": None,
            "model_version": None,
            "source_precedence_id": SOURCE_PRECEDENCE_ID,
            "terms_review_id": TERMS_REVIEW_ID,
        },
        "decision_counts": EXPECTED_DECISIONS,
        "gate_counts": {
            "owner_approved_prototype_labels": len(approved),
            "yes_quality_blocked": status_counts["EXCLUDED_QUALITY_BLOCKED_AFTER_YES"],
            "no_or_uncertain_excluded": status_counts["EXCLUDED_BY_OWNER_RESPONSE"],
        },
        "approved_class_counts": class_counts,
        "approved_event_counts": event_counts,
        "approved_event_class_counts": event_class_counts,
        "source_direction_counts": source_direction,
        "units": private_units,
        "notes_copied": False,
        "historical_response_inherited": False,
        "dataset_created": False,
        "split_created": False,
        "baseline_created": False,
        "model_created": False,
        "decision": "ACCEPT_24_OWNER_APPROVED_PROTOTYPE_LABELS_DEFER_DATASET_SPLIT_BASELINE_MODEL",
        "warning": WARNING,
    }


def _git_relative(repository_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repository_root.resolve()).as_posix()
    except ValueError as error:
        raise OwnerResponseIntakeError("private output must stay inside the repository") from error


def write_private_no_overwrite(repository_root: Path, path: Path, report: dict[str, Any]) -> dict[str, Any]:
    relative = _git_relative(repository_root, path)
    ignored = subprocess.run(["git", "-C", str(repository_root), "check-ignore", "--quiet", "--no-index", "--", relative], check=False)
    _assert(ignored.returncode == 0, "private output is not ignored")
    tracked = subprocess.run(["git", "-C", str(repository_root), "ls-files", "--error-unmatch", "--", relative], check=False, capture_output=True)
    _assert(tracked.returncode != 0, "private output is tracked")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(report, indent=2) + "\n").encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(prefix=".owner-response-intake-", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    promoted = False
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path, follow_symlinks=False)
        except FileExistsError as error:
            raise OwnerResponseIntakeError("refusing to overwrite private reconciliation") from error
        promoted = True
        temporary.unlink()
        _assert(path.read_bytes() == payload, "private reconciliation promotion drift")
    except BaseException:
        if promoted:
            path.unlink(missing_ok=True)
        raise
    finally:
        temporary.unlink(missing_ok=True)
    return {"bytes": len(payload), "sha256": _digest(payload), "committed": False, "ignored": True}


def public_report(private: dict[str, Any], private_binding: dict[str, Any]) -> dict[str, Any]:
    return {
        "report_id": REPORT_ID,
        "report_version": REPORT_VERSION,
        "protocol_version": private["protocol_version"],
        "generated_at_utc": private["generated_at_utc"],
        "run_id": private["run_id"],
        "repository": private["repository"],
        "task_issue": TASK_ISSUE,
        "git_source_commit": private["git_source_commit"],
        "software_version": SOFTWARE_VERSION,
        "application_version": SOFTWARE_VERSION,
        "owner_confirmation_id": private["owner_confirmation_id"],
        "bindings": {
            "response": private["response_binding"],
            "receipt": private["receipt_binding"],
            "surface": private["surface_binding"],
            "private_reconciliation": private_binding,
        },
        "reconstruction": private["reconstruction"],
        "provenance": private["provenance"],
        "label_set_version": LABEL_SET_VERSION,
        "decision_counts": private["decision_counts"],
        "gate_results": {
            "reproducibility": "PASS_EXACT_SOURCE_BOUND_RECONSTRUCTION",
            "source": "PASS_24_DIRECTIONALLY_CONSISTENT_BOUNDED_SOURCE_ROLES",
            "quality": "PASS_24_FROZEN_BINARY_ORIGINS_BLOCK_32_NONBINARY_ORIGINS",
            "event_leakage": "PASS_3_IMMUTABLE_EVENT_GROUPS_NO_PARTITION",
            "owner_response": "PASS_EXACT_COMPLETED_OWNER_RESPONSE",
        },
        "outcome": {
            **private["gate_counts"],
            "prototype_label_class_counts": private["approved_class_counts"],
            "prototype_label_event_counts": private["approved_event_counts"],
            "source_direction_counts": private["source_direction_counts"],
        },
        "privacy": {
            "response_bytes_committed": False,
            "receipt_bytes_committed": False,
            "private_unit_reconciliation_committed": False,
            "owner_notes_published": False,
            "unit_decisions_published": False,
            "older_export_used": False,
        },
        "boundaries": {
            "historical_6_0_50_inherited": False,
            "restricted_thresholded_tepee_barc_used": False,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
            "not_claimed": [
                "independent ground truth or inter-rater agreement",
                "field validation, official status, endorsement, or operational readiness",
                "dataset readiness, model readiness, accuracy, or enterprise readiness",
            ],
        },
        "decision": private["decision"],
        "warning": private["warning"],
        "outputs": [],
    }


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ("C:/Windows/Fonts/segoeui.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _png_bytes(report: dict[str, Any]) -> bytes:
    image = Image.new("RGB", (1800, 1160), "#f6f1e7")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1800, 175), fill="#123f3b")
    draw.text((70, 45), "BurnLens owner response intake", fill="#f8f2e8", font=_font(46))
    draw.text((72, 112), "Exact 56-unit response · controlled prototype-label gate", fill="#b9d8cf", font=_font(21))
    metrics = [("53", "yes"), ("2", "no"), ("1", "uncertain"), ("24", "prototype labels")]
    for index, (value, label) in enumerate(metrics):
        x = 70 + index * 425
        draw.rounded_rectangle((x, 225, x + 365, 365), radius=18, fill="#fff", outline="#b8c9c3", width=2)
        draw.text((x + 25, 245), value, fill="#123f3b", font=_font(46))
        draw.text((x + 25, 315), label, fill="#52645e", font=_font(18))
    draw.text((70, 420), "Gate outcome", fill="#123f3b", font=_font(31))
    rows = [
        ("Exact custody", "PASS", "7,608 response bytes and no-overwrite receipt bind the shipped surface."),
        ("Reproducibility", "PASS", "Packet, seven-product analysis, surface, and 12 public outputs reconstruct."),
        ("Source", "PASS · BOUNDED", "12 burned agree with affirmative current reference; 12 backgrounds have no affirmative conflict."),
        ("Quality", "24 PASS / 32 BLOCK", "Twenty-nine owner yes decisions remain blocked by nonbinary origin."),
        ("Event leakage", "PASS · NO SPLIT", "Eight labels in each immutable event group; no dataset partition exists."),
    ]
    y = 480
    for name, status, explanation in rows:
        draw.rounded_rectangle((70, y, 1730, y + 92), radius=12, fill="#fff", outline="#d4d9d3")
        draw.text((95, y + 18), name, fill="#123f3b", font=_font(21))
        draw.text((390, y + 18), status, fill="#8b3d22" if "BLOCK" in status else "#145a54", font=_font(20))
        draw.text((680, y + 20), explanation, fill="#52645e", font=_font(15))
        y += 108
    draw.text((70, 1040), "12 burned + 12 background owner-approved prototype labels; dataset, split, baseline, and model remain absent.", fill="#6b3427", font=_font(18))
    draw.text((70, 1082), report["warning"], fill="#6b3427", font=_font(17))
    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=False)
    return buffer.getvalue()


def _html_bytes(report: dict[str, Any]) -> bytes:
    outcomes = report["outcome"]
    gate_rows = "".join(
        f"<tr><th>{escape(name.replace('_', ' ').title())}</th><td>{escape(value)}</td></tr>"
        for name, value in report["gate_results"].items()
    )
    event_rows = "".join(
        f"<tr><td>{escape(name)}</td><td>{value}</td></tr>"
        for name, value in outcomes["prototype_label_event_counts"].items()
    )
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BurnLens owner response intake</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f6f1e7;color:#173d39;font:16px/1.5 Segoe UI,Arial,sans-serif}}header{{background:#123f3b;color:#fff;padding:42px max(24px,5vw)}}main{{max-width:1250px;margin:auto;padding:32px 24px}}.metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}}.metric,.panel{{background:#fff;border:1px solid #cbd7d1;border-radius:14px;padding:20px}}.metric strong{{display:block;font-size:2.3rem}}.grid{{display:grid;grid-template-columns:1.2fr .8fr;gap:20px;margin-top:24px}}table{{border-collapse:collapse;width:100%}}th,td{{text-align:left;padding:12px;border-bottom:1px solid #e0e3df;vertical-align:top}}th{{width:35%;color:#123f3b}}code{{overflow-wrap:anywhere}}.warning{{border-left:5px solid #a64d2d;background:#fff4e8;padding:16px;margin-top:24px}}@media(max-width:760px){{.metrics,.grid{{grid-template-columns:1fr}}header{{padding:28px 20px}}main{{padding:20px 12px}}}}
</style></head><body><header><h1>BurnLens owner response intake</h1><p>Exact 56-unit response · content-safe aggregate · controlled prototype-label gate</p></header><main><section class="metrics"><div class="metric"><strong>53</strong>yes</div><div class="metric"><strong>2</strong>no</div><div class="metric"><strong>1</strong>uncertain</div><div class="metric"><strong>24</strong>prototype labels</div></section>
<section class="grid"><div class="panel"><h2>Promotion gates</h2><table>{gate_rows}</table></div><div class="panel"><h2>Bounded outcome</h2><p><strong>12 burned + 12 background</strong> become explicitly owner-approved prototype labels.</p><p>Twenty-nine yes decisions remain excluded because their frozen origin is unknown, excluded, or review-needed. Two no and one uncertain remain excluded.</p><table><thead><tr><th>Immutable event group</th><th>Labels</th></tr></thead><tbody>{event_rows}</tbody></table></div></section>
<p class="warning"><strong>Still absent:</strong> accepted dataset, split, baseline, model, accuracy, independent ground truth, inter-rater agreement, field validation, official status, endorsement, or operational/enterprise readiness. Unit decisions, notes, exact response bytes, receipt bytes, and the private reconciliation are not published. {escape(report['warning'])}</p>
<p>Trace: source commit <code>{escape(report['git_source_commit'])}</code> · BurnLens <code>{report['software_version']}</code> · label set <code>{escape(report['label_set_version'])}</code> · run <code>{escape(report['run_id'])}</code> · AOI <code>{escape(report['provenance']['aoi_version'])}</code> · schema <code>{escape(report['provenance']['label_schema_version'])}</code> · dataset/split/baseline/model none.</p></main></body></html>'''
    return html.encode("utf-8")


def write_public_no_overwrite(report: dict[str, Any], output_directory: Path) -> dict[str, Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": output_directory / f"{REPORT_ID}.json",
        "html": output_directory / f"{REPORT_ID}.html",
        "png": output_directory / f"{REPORT_ID}.png",
    }
    _assert(not any(path.exists() for path in paths.values()), "refusing to overwrite public intake output")
    html_bytes = _html_bytes(report)
    png_bytes = _png_bytes(report)
    report["outputs"] = [
        {"path": paths["html"].name, "bytes": len(html_bytes), "sha256": _digest(html_bytes)},
        {"path": paths["png"].name, "bytes": len(png_bytes), "sha256": _digest(png_bytes)},
    ]
    json_bytes = (json.dumps(report, indent=2) + "\n").encode("utf-8")
    written: list[Path] = []
    try:
        for path, payload in ((paths["html"], html_bytes), (paths["png"], png_bytes), (paths["json"], json_bytes)):
            with path.open("xb") as handle:
                handle.write(payload)
            written.append(path)
    except BaseException:
        for path in written:
            path.unlink(missing_ok=True)
        raise
    return paths
