"""Build the disclosed BurnLens owner yes/no/uncertain review surface.

The surface reopens the exact 56 units from the historical blinded packet.  It
does not accept labels: an owner ``yes`` remains necessary but insufficient
until later reproducibility, source, quality, and leakage gates pass.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from html import escape
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .current_reference_bundle_fitness import (
    EVENTS,
    WARNING,
    build_report as build_bundle_report,
)


SOFTWARE_VERSION = "0.25.0"
SURFACE_ID = "OWNER-REVIEW-SURFACE-2026-001"
REPORT_VERSION = "owner-confirmed-prototype-review-surface-v0.1.0"
PROTOCOL_VERSION = "owner-confirmed-prototype-label-review-v0.1.0"
RESPONSE_SCHEMA_VERSION = "burnlens-owner-review-response-v0.1.0"
TASK_ISSUE = 432
PACKET_ID = "LABEL-REVIEW-PACKET-2026-001"
PACKET_RUN_ID = "BL-2026-07-16-label-review-packet-r001"
PACKET_SHA256 = "77067063a769645af13886b6c87cc236a10e06199d091743908d63556e07637c"
BUNDLE_REPORT_ID = "CURRENT-REFERENCE-BUNDLE-FITNESS-2026-001"
BUNDLE_REPORT_SHA256 = "2d94aba62d735efede902aa9bbdc82ccabc987026acc118ff67c45d686a23eed"
SOURCE_PRECEDENCE_ID = "SOURCE_PRECEDENCE-2026-010"
TERMS_REVIEW_ID = "TERMS-2026-012"
UNITS_PER_PAGE = 7
CURRENT_ROW_HEIGHT = 300
CURRENT_PAGE_HEADER = 165
CURRENT_PAGE_FOOTER = 75
FROZEN_ROW_HEIGHT = 445
FROZEN_PAGE_HEADER = 175
ALLOWED_DECISIONS = ("yes", "no", "uncertain")


class OwnerReviewSurfaceError(RuntimeError):
    """A deterministic, secret-free owner-review surface failure."""


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _load_exact_json(path: Path, expected_sha256: str) -> dict[str, Any]:
    data = path.read_bytes()
    if _digest(data) != expected_sha256:
        raise OwnerReviewSurfaceError(f"exact input drift: {path.name}")
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise OwnerReviewSurfaceError(f"invalid JSON input: {path.name}") from error
    if not isinstance(value, dict):
        raise OwnerReviewSurfaceError(f"JSON input is not an object: {path.name}")
    return value


def _semantic(program: str, value: int | None) -> str:
    if value is None or value == 255:
        return "unavailable"
    if program == "MTBS":
        if value in (2, 3, 4):
            return "affirmative burn evidence"
        if value in (1, 5):
            return "ambiguous or unchanged"
        return "outside mask or no-data"
    if value in (2, 3, 4):
        return "affirmative burn evidence"
    if value == 1:
        return "ambiguous or unchanged"
    return "outside mask or no-data"


def _finite_number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return round(number, 3) if math.isfinite(number) else None


def _candidate_for_unit(unit: dict[str, Any], evidence: dict[str, Any]) -> tuple[str, str, str]:
    state = unit["proposal_state"]
    if state == "burned":
        return "burned", "frozen binary proposal", "bounded"
    if state == "background-candidate":
        return "background", "frozen binary proposal", "bounded"
    affirmative = [
        item["program"]
        for item in evidence["categorical"]
        if item["semantic"] == "affirmative burn evidence"
    ]
    if affirmative:
        return (
            "burned",
            f"current categorical direction ({' + '.join(affirmative)})",
            "quality-blocked",
        )
    if float(unit["dnbr_center"]) > 0:
        return "burned", "frozen Sentinel dNBR sign fallback", "quality-blocked"
    return "background", "frozen Sentinel dNBR sign fallback", "quality-blocked"


def _response_template(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "response_schema_version": RESPONSE_SCHEMA_VERSION,
        "surface_id": SURFACE_ID,
        "surface_run_id": report["run_id"],
        "packet_id": PACKET_ID,
        "packet_sha256": PACKET_SHA256,
        "owner_review_protocol_version": PROTOCOL_VERSION,
        "owner": {
            "owner_id": "project-owner",
            "attestation": None,
        },
        "review_started_at_utc": None,
        "review_completed_at_utc": None,
        "completed": False,
        "responses": [
            {
                "sample_id": unit["sample_id"],
                "candidate_label": unit["candidate_label"],
                "decision": None,
                "notes": None,
            }
            for unit in report["units"]
        ],
    }


def build_surface(
    *,
    repository_root: Path,
    archive_dir: Path,
    packet_path: Path,
    bundle_report_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> tuple[dict[str, Any], dict[str, dict[str, np.ndarray | None]]]:
    packet = _load_exact_json(packet_path, PACKET_SHA256)
    bundle_input = _load_exact_json(bundle_report_path, BUNDLE_REPORT_SHA256)
    if packet.get("report_id") != PACKET_ID or packet.get("run_id") != PACKET_RUN_ID:
        raise OwnerReviewSurfaceError("historical packet identity drift")
    units = packet.get("units")
    if not isinstance(units, list) or len(units) != 56:
        raise OwnerReviewSurfaceError("historical packet must contain exactly 56 units")
    sample_ids = [item.get("sample_id") for item in units]
    if sample_ids != [f"LRU-{index:03d}" for index in range(1, 57)]:
        raise OwnerReviewSurfaceError("historical unit identity or order drift")
    if bundle_input.get("report_id") != BUNDLE_REPORT_ID:
        raise OwnerReviewSurfaceError("bundle report identity drift")
    if len(git_source_commit) != 40:
        raise OwnerReviewSurfaceError("git source commit must be a full SHA")

    rebuilt_bundle, previews = build_bundle_report(
        repository_root=repository_root,
        archive_dir=archive_dir,
        generated_at_utc=bundle_input["generated_at_utc"],
        run_id=bundle_input["run_id"],
        git_source_commit=bundle_input["git_source_commit"],
    )
    rebuilt_bytes = (json.dumps(rebuilt_bundle, indent=2) + "\n").encode("utf-8")
    if _digest(rebuilt_bytes) != BUNDLE_REPORT_SHA256:
        raise OwnerReviewSurfaceError("current-reference bundle reconstruction drift")

    preview_by_event: dict[str, dict[str, np.ndarray | None]] = {}
    for contract, preview in zip(EVENTS, previews, strict=True):
        preview_by_event[contract.event_group_id] = {
            "mtbs": preview["mtbs"],
            "ravg": preview["ravg"],
            "baer": preview["baer"],
        }

    public_units: list[dict[str, Any]] = []
    for index, original in enumerate(units, start=1):
        event_id = original["event_group_id"]
        arrays = preview_by_event[event_id]
        row = int(original["row"])
        column = int(original["column"])
        categorical: list[dict[str, Any]] = []
        for program, key in (("MTBS", "mtbs"), ("RAVG", "ravg")):
            array = arrays[key]
            if array is None:
                continue
            value = int(array[row, column])
            categorical.append({
                "program": program,
                "value": None if value == 255 else value,
                "semantic": _semantic(program, value),
                "sampling": "nearest neighbor from 30 m source to frozen 20 m proposal grid; no resolution gain",
            })
        baer_value = None
        if arrays["baer"] is not None:
            baer_value = _finite_number(arrays["baer"][row, column])
        evidence = {
            "categorical": categorical,
            "baer_dnbr": {
                "value": baer_value,
                "semantic": "continuous change context only; positive change is not a burned threshold",
                "thresholded_barc_used": False,
            } if baer_value is not None else None,
        }
        candidate, basis, grade = _candidate_for_unit(original, evidence)
        page = math.ceil(index / UNITS_PER_PAGE)
        position = ((index - 1) % UNITS_PER_PAGE) + 1
        public_units.append({
            "sample_id": original["sample_id"],
            "event_group_id": event_id,
            "fire_name": original["fire_name"],
            "row": row,
            "column": column,
            "pixel_center_utm10n": original["pixel_center_utm10n"],
            "frozen_proposal_state": original["proposal_state"],
            "frozen_proposal_target": original["proposal_target_value"],
            "frozen_dnbr_center": original["dnbr_center"],
            "frozen_reference_context_value": original["reference_context_value"],
            "selection_hash": original["selection_hash"],
            "presentation_hash": original["presentation_hash"],
            "candidate_label": candidate,
            "candidate_basis": basis,
            "evidence_grade": grade,
            "question": f"Does the disclosed evidence support this unit as a {candidate} prototype candidate?",
            "current_reference_evidence": evidence,
            "frozen_evidence_page": original["blind_page"],
            "frozen_evidence_position": original["blind_page_position"],
            "current_evidence_page": f"{SURFACE_ID}-CURRENT-{page:02d}.png",
            "current_evidence_position": position,
            "promotion_status": "blocked pending owner response and later reproducibility/source/quality/leakage gates",
            "quality_blocker": None if original["proposal_state"] in ("burned", "background-candidate") else original["proposal_state"],
        })

    report = {
        "report_id": SURFACE_ID,
        "report_version": REPORT_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "response_schema_version": RESPONSE_SCHEMA_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": SOFTWARE_VERSION,
        "source_bindings": {
            "historical_packet": {"report_id": PACKET_ID, "run_id": PACKET_RUN_ID, "sha256": PACKET_SHA256},
            "current_bundle_fitness": {"report_id": BUNDLE_REPORT_ID, "run_id": bundle_input["run_id"], "sha256": BUNDLE_REPORT_SHA256},
            "source_precedence_id": SOURCE_PRECEDENCE_ID,
            "terms_review_id": TERMS_REVIEW_ID,
        },
        "provenance": {
            "aoi_version": "aoi-darlene3-model-v0.2.0",
            "target_version": "target-burn-scar-v0.2.0",
            "label_schema_version": "burn-scar-five-state-schema-v0.1.0",
            "dataset_version": None,
            "split_version": None,
            "baseline_version": None,
            "model_version": None,
        },
        "candidate_rule": {
            "order": [
                "preserve frozen burned/background candidate direction",
                "for frozen nonbinary states, prefer any permitted current categorical affirmative burn evidence",
                "otherwise use the sign of frozen Sentinel continuous dNBR only as a weak disclosed direction fallback",
            ],
            "nonbinary_origin_remains_quality_blocked": True,
            "positive_dnbr_is_not_a_burned_threshold": True,
            "creates_label": False,
        },
        "review_contract": {
            "allowed_decisions": list(ALLOWED_DECISIONS),
            "yes": "necessary but insufficient; later reproducibility, source, quality, and event-level leakage gates remain mandatory",
            "no": "excluded from prototype-label promotion",
            "uncertain": "excluded from prototype-label promotion with uncertainty preserved",
            "historical_response_inherited": False,
            "owner_responses_recorded": 0,
        },
        "units": public_units,
        "summary": {
            "unit_count": len(public_units),
            "candidate_counts": dict(sorted(Counter(item["candidate_label"] for item in public_units).items())),
            "frozen_state_counts": dict(sorted(Counter(item["frozen_proposal_state"] for item in public_units).items())),
            "quality_blocked_units": sum(item["quality_blocker"] is not None for item in public_units),
            "owner_yes": 0,
            "owner_no": 0,
            "owner_uncertain": 0,
            "labels_promoted": 0,
        },
        "boundaries": {
            "restricted_thresholded_tepee_barc": "excluded from all public pixels and candidate decisions",
            "darlene_categorical_cross_program_confirmation": False,
            "ravg": "forest-calibrated and timing-sensitive",
            "mtbs": "analyst interpreted; increased-greenness class 5 remains ambiguous",
            "not_claimed": [
                "independent ground truth",
                "inter-rater agreement or consensus",
                "field validation",
                "official or endorsed status",
                "operational, emergency-ready, or enterprise readiness",
                "accepted label set, dataset, split, baseline, model, or accuracy",
            ],
        },
        "decision": "READY_FOR_OWNER_YES_NO_UNCERTAIN_REVIEW_DEFER_LABELS_DATASET_MODEL",
        "warning": WARNING,
        "outputs": [],
    }
    return report, preview_by_event


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ("C:/Windows/Fonts/segoeui.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _crop(array: np.ndarray | None, row: int, column: int, radius: int = 6) -> np.ndarray | None:
    if array is None:
        return None
    result = np.full((radius * 2 + 1, radius * 2 + 1), np.nan, dtype=np.float32)
    y0, y1 = max(0, row - radius), min(array.shape[0], row + radius + 1)
    x0, x1 = max(0, column - radius), min(array.shape[1], column + radius + 1)
    result[(y0 - row + radius):(y1 - row + radius), (x0 - column + radius):(x1 - column + radius)] = array[y0:y1, x0:x1]
    return result


def _chip(array: np.ndarray | None, kind: str) -> Image.Image:
    if array is None:
        image = Image.new("RGB", (320, 190), "#e7e0d3")
        draw = ImageDraw.Draw(image)
        draw.text((87, 78), "NOT AVAILABLE", fill="#5d6b64", font=_font(18))
        return image
    rgb = np.zeros((*array.shape, 3), dtype=np.uint8)
    if kind == "mtbs":
        colors = {0: (239, 233, 219), 1: (242, 207, 94), 2: (236, 137, 45), 3: (202, 58, 31), 4: (132, 30, 23), 5: (82, 143, 87), 6: (120, 124, 122), 255: (90, 94, 92)}
        for value, color in colors.items():
            rgb[array == value] = color
        rgb[np.isnan(array)] = (90, 94, 92)
    elif kind == "ravg":
        colors = {0: (239, 233, 219), 1: (242, 207, 94), 2: (236, 137, 45), 3: (202, 58, 31), 4: (132, 30, 23), 9: (90, 94, 92), 255: (90, 94, 92)}
        for value, color in colors.items():
            rgb[array == value] = color
        rgb[np.isnan(array)] = (90, 94, 92)
    else:
        valid = np.isfinite(array)
        scaled = np.nan_to_num(np.clip((array + 250.0) / 750.0, 0, 1), nan=0.0)
        rgb[..., 0] = (70 + 185 * scaled).astype(np.uint8)
        rgb[..., 1] = (120 + 100 * (1 - np.abs(scaled - 0.5) * 2)).astype(np.uint8)
        rgb[..., 2] = (220 - 180 * scaled).astype(np.uint8)
        rgb[~valid] = (239, 233, 219)
    image = Image.fromarray(rgb, "RGB").resize((320, 190), Image.Resampling.NEAREST)
    draw = ImageDraw.Draw(image)
    draw.line((160, 80, 160, 110), fill="#00d6c9", width=4)
    draw.line((145, 95, 175, 95), fill="#00d6c9", width=4)
    draw.ellipse((153, 88, 167, 102), outline="#00d6c9", width=3)
    return image


def _draw_evidence_panel(canvas: Image.Image, x: int, top: int, title: str, subtitle: str, chip: Image.Image) -> None:
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((x, top, x + 340, top + 242), fill="#ffffff", outline="#173b35", width=2)
    draw.rectangle((x, top, x + 340, top + 52), fill="#173b35")
    draw.text((x + 12, top + 7), title, fill="white", font=_font(16))
    draw.text((x + 12, top + 30), subtitle, fill="#b9d8cf", font=_font(11))
    canvas.paste(chip, (x + 10, top + 52))


def render_current_pages(report: dict[str, Any], previews: dict[str, dict[str, np.ndarray | None]], output_directory: Path) -> list[Path]:
    paths: list[Path] = []
    for page_index in range(math.ceil(len(report["units"]) / UNITS_PER_PAGE)):
        units = report["units"][page_index * UNITS_PER_PAGE:(page_index + 1) * UNITS_PER_PAGE]
        height = CURRENT_PAGE_HEADER + len(units) * CURRENT_ROW_HEIGHT + CURRENT_PAGE_FOOTER
        canvas = Image.new("RGB", (1800, height), "#f4f0e8")
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((0, 0, 1800, 140), fill="#132a26")
        draw.text((48, 22), "BURNLENS / DISCLOSED OWNER REVIEW", fill="#b9d8cf", font=_font(18))
        draw.text((48, 56), f"CURRENT REFERENCE PAGE {page_index + 1:02d}", fill="white", font=_font(34))
        draw.text((48, 105), "Permitted current categorical evidence and unthresholded BAER dNBR context; none is truth alone.", fill="#b9d8cf", font=_font(14))
        for row_index, unit in enumerate(units):
            top = CURRENT_PAGE_HEADER + row_index * CURRENT_ROW_HEIGHT
            arrays = previews[unit["event_group_id"]]
            row, column = unit["row"], unit["column"]
            categorical = {
                item["program"]: item
                for item in unit["current_reference_evidence"]["categorical"]
            }
            def subtitle(program: str) -> str:
                item = categorical.get(program)
                if item is None or item["value"] is None:
                    return "not available"
                short = {
                    "affirmative burn evidence": "affirmative burn",
                    "ambiguous or unchanged": "ambiguous / unchanged",
                    "outside mask or no-data": "outside / no-data",
                }[item["semantic"]]
                return f"30 m value {item['value']} / {short}"
            baer = unit["current_reference_evidence"]["baer_dnbr"]
            baer_subtitle = "not available" if baer is None else f"dNBR {baer['value']} / continuous only"
            draw.text((45, top), f"{unit['sample_id']} / {unit['fire_name']} / center ({row}, {column})", fill="#006b64", font=_font(17))
            _draw_evidence_panel(canvas, 45, top + 34, "CURRENT MTBS dNBR6", subtitle("MTBS"), _chip(_crop(arrays["mtbs"], row, column), "mtbs"))
            _draw_evidence_panel(canvas, 420, top + 34, "CURRENT RAVG CBI4", subtitle("RAVG"), _chip(_crop(arrays["ravg"], row, column), "ravg"))
            _draw_evidence_panel(canvas, 795, top + 34, "BAER dNBR", baer_subtitle, _chip(_crop(arrays["baer"], row, column), "baer"))
            draw.rounded_rectangle((1170, top + 34, 1755, top + 276), radius=12, fill="#fffdf8", outline="#d0c5b5", width=2)
            draw.text((1192, top + 52), "DISCLOSED CODEX PROPOSITION", fill="#5b6a63", font=_font(14))
            draw.text((1192, top + 83), unit["candidate_label"].upper(), fill="#7a301e" if unit["candidate_label"] == "burned" else "#145a54", font=_font(34))
            draw.text((1192, top + 130), f"basis: {unit['candidate_basis']}", fill="#24332e", font=_font(15))
            draw.text((1192, top + 162), f"frozen state: {unit['frozen_proposal_state']}", fill="#24332e", font=_font(15))
            draw.text((1192, top + 194), f"evidence grade: {unit['evidence_grade']}", fill="#8a521c", font=_font(15))
            draw.text((1192, top + 225), "Owner yes is not label acceptance.", fill="#8a521c", font=_font(14))
        draw.text((45, height - 46), "Thresholded Tepee BARC is excluded. MTBS class 5 is ambiguous. Darlene has no categorical cross-program confirmation.", fill="#5d6b64", font=_font(13))
        path = output_directory / f"{SURFACE_ID}-CURRENT-{page_index + 1:02d}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(path, format="PNG", optimize=False)
        paths.append(path)
    return paths


def _crop_figure(image_name: str, position: int, *, row_height: int, header: int, page_height: int, alt: str) -> str:
    scaled_top = (header + (position - 1) * row_height) * 2 / 3
    scaled_page_height = page_height * 2 / 3
    return (
        '<div class="evidence-scroll"><div class="crop" '
        f'style="height:{row_height * 2 / 3:.3f}px"><img src="{escape(image_name)}" alt="{escape(alt)}" '
        f'style="width:1200px;height:{scaled_page_height:.3f}px;transform:translateY(-{scaled_top:.3f}px)"></div></div>'
    )


def render_html(report: dict[str, Any], response: dict[str, Any], path: Path, current_page_heights: dict[str, int], frozen_page_heights: dict[str, int]) -> None:
    cards: list[str] = []
    for unit in report["units"]:
        categorical = " / ".join(
            f"{item['program']} {item['value']}: {item['semantic']}"
            for item in unit["current_reference_evidence"]["categorical"]
        ) or "No MTBS layer; RAVG is the only current categorical program."
        baer = unit["current_reference_evidence"]["baer_dnbr"]
        baer_text = "not available" if baer is None else f"{baer['value']}; continuous context only"
        quality = "none from frozen binary state" if unit["quality_blocker"] is None else f"{unit['quality_blocker']} remains a promotion blocker"
        frozen_crop = _crop_figure(
            unit["frozen_evidence_page"], unit["frozen_evidence_position"],
            row_height=FROZEN_ROW_HEIGHT, header=FROZEN_PAGE_HEADER,
            page_height=frozen_page_heights[unit["frozen_evidence_page"]],
            alt=f"{unit['sample_id']} frozen pre/post optical, dNBR, and source context",
        )
        current_crop = _crop_figure(
            unit["current_evidence_page"], unit["current_evidence_position"],
            row_height=CURRENT_ROW_HEIGHT, header=CURRENT_PAGE_HEADER,
            page_height=current_page_heights[unit["current_evidence_page"]],
            alt=f"{unit['sample_id']} current permitted reference evidence and disclosed proposition",
        )
        decisions = "".join(
            f'<label><input type="radio" name="decision-{unit["sample_id"]}" value="{decision}"> {decision}</label>'
            for decision in ALLOWED_DECISIONS
        )
        cards.append(f'''<article class="unit" id="{unit['sample_id']}" data-sample="{unit['sample_id']}" data-candidate="{unit['candidate_label']}">
<div class="unit-head"><div><span>{unit['sample_id']} / {escape(unit['fire_name'])}</span><h2>Proposed {unit['candidate_label']}</h2></div><div class="badge {unit['evidence_grade']}">{unit['evidence_grade']}</div></div>
<p><strong>Frozen state:</strong> {escape(unit['frozen_proposal_state'])} · <strong>candidate basis:</strong> {escape(unit['candidate_basis'])} · <strong>quality:</strong> {escape(quality)}</p>
<details open><summary>Frozen optical and source evidence</summary>{frozen_crop}</details>
<details open><summary>Permitted current reference evidence</summary>{current_crop}<p class="micro">{escape(categorical)} · BAER dNBR: {escape(baer_text)}.</p></details>
<fieldset><legend>{escape(unit['question'])}</legend><div class="choices">{decisions}</div><label class="notes">Optional note <textarea data-notes maxlength="500"></textarea></label></fieldset>
</article>''')
    embedded = json.dumps(response, separators=(",", ":"), ensure_ascii=True).replace("<", "\\u003c")
    not_claimed = "".join(f"<li>{escape(item)}</li>" for item in report["boundaries"]["not_claimed"])
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens owner yes/no/uncertain review</title><style>
:root{{--ink:#17251f;--pine:#132a26;--teal:#006b64;--paper:#f4f0e8;--line:#d7cec1;--warn:#8a521c}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header{{background:var(--pine);color:white;padding:2.6rem max(5vw,1.25rem)}}header p{{max-width:900px;color:#c6ddd6}}main{{max-width:1320px;margin:auto;padding:1.25rem}}.warning,.contract,.toolbar,.unit{{background:#fffdf8;border:1px solid var(--line);border-radius:14px;padding:1.15rem;margin:1rem 0}}.warning{{border-left:7px solid #d87618;font-weight:650}}.contract{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem}}.metric strong{{display:block;font-size:2rem}}.toolbar{{position:sticky;top:0;z-index:3;box-shadow:0 5px 18px #132a2620}}button,.file-label{{border:0;border-radius:8px;padding:.75rem 1rem;background:var(--teal);color:white;font-weight:700;cursor:pointer;display:inline-block;margin:.25rem}}button.secondary,.file-label.secondary{{background:#53645d}}button:disabled{{opacity:.5;cursor:not-allowed}}input[type=file]{{position:absolute;left:-9999px}}.unit{{scroll-margin-top:120px}}.unit-head{{display:flex;justify-content:space-between;gap:1rem;align-items:start}}h1,h2{{line-height:1.15}}.unit h2{{margin:.2rem 0}}.badge{{padding:.35rem .65rem;border-radius:999px;font-weight:750;background:#e3eee9}}.badge.quality-blocked{{background:#fff0cf;color:#75420e}}details{{margin:.75rem 0;border-top:1px solid var(--line);padding-top:.6rem}}summary{{cursor:pointer;font-weight:750}}.evidence-scroll{{overflow-x:auto;border:1px solid var(--line);background:#ebe5da}}.crop{{width:1200px;overflow:hidden;position:relative}}.crop img{{display:block;max-width:none}}fieldset{{border:1px solid var(--line);border-radius:10px;padding:1rem}}legend{{font-weight:800;padding:0 .4rem}}.choices{{display:flex;flex-wrap:wrap;gap:.65rem}}.choices label{{border:1px solid #b8aea0;border-radius:8px;padding:.65rem 1rem;text-transform:capitalize}}.notes{{display:block;margin-top:.9rem}}textarea{{display:block;width:100%;min-height:70px;margin-top:.3rem}}.micro{{font-size:.9rem;color:#4d5c55}}.status{{font-weight:750;color:var(--warn);overflow-wrap:anywhere}}.invalid{{outline:4px solid #d87618}}.locked{{opacity:.92}}code{{overflow-wrap:anywhere}}@media(max-width:600px){{header{{padding:1.4rem 1rem}}main{{padding:.65rem}}.toolbar{{position:static}}.unit{{padding:.85rem}}.choices{{display:grid;grid-template-columns:1fr 1fr 1fr}}.choices label{{padding:.55rem .35rem;text-align:center}}}}
</style></head><body><header><p>BURNLENS / PHASE TWO / ISSUE #{TASK_ISSUE}</p><h1>Owner-confirmed prototype review</h1><p>Every original unit is reopened. Review the disclosed Codex proposition against frozen optical evidence and permitted current reference evidence, then answer yes, no, or uncertain.</p></header><main>
<p class="warning">{escape(report['warning'])}</p>
<section class="contract"><div class="metric"><strong>{report['summary']['unit_count']}</strong>original units reopened</div><div class="metric"><strong id="completed-count">0 / 56</strong>owner decisions</div><div class="metric"><strong>0</strong>labels promoted</div><div><strong>Decision contract</strong><p>Yes is necessary, not sufficient. No and uncertain remain excluded. Later reproducibility, source, quality, and event-level leakage gates remain mandatory.</p></div></section>
<section class="toolbar" aria-label="Review controls"><strong id="progress">0 of 56 decisions</strong><span id="status" class="status" role="status" aria-live="polite"></span><br><button id="save-draft" class="secondary" type="button">Save hashed draft</button><label class="file-label secondary" for="load-response">Load draft or response</label><input id="load-response" type="file" accept="application/json"><button id="review-complete" type="button">Review completion</button><button id="export-complete" type="button">Finalize and export exact response</button></section>
{''.join(cards)}
<section class="unit"><h2>Final attestation</h2><label><input id="attestation" type="checkbox"> I am the project owner, I reviewed every disclosed proposition, and I understand that yes does not establish ground truth or accept a label.</label><h3>Not claimed</h3><ul>{not_claimed}</ul><p>Trace: source commit <code>{escape(report['git_source_commit'])}</code> · BurnLens <code>{report['software_version']}</code> · run <code>{escape(report['run_id'])}</code> · dataset/split/baseline/model none.</p></section>
<script id="response-template" type="application/json">{embedded}</script><script>
const TEMPLATE=JSON.parse(document.getElementById('response-template').textContent);const ALLOWED=new Set(['yes','no','uncertain']);let startedAt=null;let loadedCompletedAt=null;let locked=false;
const cards=[...document.querySelectorAll('[data-sample]')];const status=document.getElementById('status');
function selected(card){{return card.querySelector('input[type=radio]:checked')?.value??null}}function update(){{const count=cards.filter(c=>selected(c)).length;document.getElementById('progress').textContent=`${{count}} of 56 decisions`;document.getElementById('completed-count').textContent=`${{count}} / 56`;if(count&&!startedAt)startedAt=new Date().toISOString();}}
function payload(completed){{return{{...TEMPLATE,owner:{{owner_id:'project-owner',attestation:document.getElementById('attestation').checked}},review_started_at_utc:startedAt,review_completed_at_utc:completed?(loadedCompletedAt??new Date().toISOString()):null,completed,responses:cards.map(card=>({{sample_id:card.dataset.sample,candidate_label:card.dataset.candidate,decision:selected(card),notes:card.querySelector('[data-notes]').value.trim()||null}}))}}}}
async function digest(bytes){{const value=await crypto.subtle.digest('SHA-256',bytes);return [...new Uint8Array(value)].map(x=>x.toString(16).padStart(2,'0')).join('')}}async function download(value,kind){{const text=JSON.stringify(value,null,2)+'\\n';const bytes=new TextEncoder().encode(text);const hash=await digest(bytes);const blob=new Blob([bytes],{{type:'application/json'}});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`{SURFACE_ID}-${{kind}}-${{hash.slice(0,16)}}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);status.textContent=` Exact ${{kind.toLowerCase()}} bytes prepared; SHA-256 ${{hash}}.`;return hash}}
function validateComplete(show){{let ok=true;cards.forEach(card=>{{card.classList.remove('invalid');if(!selected(card)){{ok=false;if(show)card.classList.add('invalid')}}}});if(!document.getElementById('attestation').checked)ok=false;status.textContent=ok?' Complete and ready for exact-byte export.':' Missing decisions or final attestation.';return ok}}
function lock(){{locked=true;document.body.classList.add('locked');document.querySelectorAll('input[type=radio],textarea,#attestation,#save-draft,#review-complete,#export-complete').forEach(x=>x.disabled=true);status.textContent+=' Response is locked in this browser session.'}}
document.addEventListener('change',update);document.getElementById('save-draft').addEventListener('click',()=>download(payload(false),'DRAFT'));document.getElementById('review-complete').addEventListener('click',()=>validateComplete(true));document.getElementById('export-complete').addEventListener('click',async()=>{{if(!validateComplete(true))return;await download(payload(true),'RESPONSE');lock()}});
document.getElementById('load-response').addEventListener('change',async event=>{{const file=event.target.files[0];if(!file)return;try{{const bytes=new Uint8Array(await file.arrayBuffer());const value=JSON.parse(new TextDecoder('utf-8',{{fatal:true}}).decode(bytes));if(value.response_schema_version!==TEMPLATE.response_schema_version||value.surface_id!==TEMPLATE.surface_id||value.surface_run_id!==TEMPLATE.surface_run_id||value.packet_sha256!==TEMPLATE.packet_sha256||!Array.isArray(value.responses)||value.responses.length!==56)throw new Error('binding mismatch');value.responses.forEach((item,index)=>{{const card=cards[index];if(item.sample_id!==card.dataset.sample||item.candidate_label!==card.dataset.candidate||!(item.decision===null||ALLOWED.has(item.decision)))throw new Error('unit or decision mismatch');if(item.decision)card.querySelector(`input[value="${{item.decision}}"]`).checked=true;card.querySelector('[data-notes]').value=item.notes??''}});startedAt=value.review_started_at_utc;loadedCompletedAt=value.review_completed_at_utc;document.getElementById('attestation').checked=value.owner?.attestation===true;update();const hash=await digest(bytes);status.textContent=` Loaded exact bytes; SHA-256 ${{hash}}.`;if(value.completed){{if(!validateComplete(false))throw new Error('completed response is incomplete');lock()}}}}catch(error){{status.textContent=` Load rejected: ${{error.message}}.`}}}});update();
</script></main></body></html>'''
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(html.replace("\r\n", "\n").encode("utf-8"))


def render_summary_png(report: dict[str, Any], path: Path) -> None:
    image = Image.new("RGB", (1800, 980), "#f4f0e8")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1800, 215), fill="#132a26")
    draw.text((70, 40), "BURNLENS / OWNER-CONFIRMED REVIEW", fill="#b9d8cf", font=_font(24))
    draw.text((70, 88), "All 56 original units are reopened.", fill="white", font=_font(48))
    draw.text((70, 158), "Disclosed evidence / yes-no-uncertain / zero labels promoted", fill="#b9d8cf", font=_font(24))
    metrics = (("56", "units"), (str(report["summary"]["candidate_counts"].get("burned", 0)), "burned propositions"), (str(report["summary"]["candidate_counts"].get("background", 0)), "background propositions"), ("0", "owner responses"))
    for index, (value, label) in enumerate(metrics):
        x = 70 + index * 420
        draw.rounded_rectangle((x, 280, x + 360, 455), radius=18, fill="#fffdf8", outline="#d7cec1", width=2)
        draw.text((x + 28, 305), value, fill="#006b64", font=_font(48))
        draw.text((x + 28, 390), label, fill="#33433c", font=_font(20))
    draw.rounded_rectangle((70, 520, 1730, 840), radius=18, fill="#fffdf8", outline="#d7cec1", width=2)
    draw.text((105, 558), "WHAT THE SURFACE DOES", fill="#006b64", font=_font(23))
    lines = [
        "Pairs every disclosed proposition with frozen optical/source evidence and permitted current reference evidence.",
        "Preserves unknown, excluded, and review-needed origins as quality blockers instead of erasing uncertainty.",
        "Excludes restricted thresholded Tepee BARC; treats MTBS class 5 as ambiguous and BAER dNBR as continuous context.",
        "Exports hash-named exact response bytes; yes still requires later reproducibility, source, quality, and leakage gates.",
        "Claims no independent truth, inter-rater agreement, field validation, official status, operational readiness, or accuracy.",
    ]
    for index, line in enumerate(lines):
        draw.text((110, 610 + index * 43), f"• {line}", fill="#283731", font=_font(19))
    draw.text((70, 900), f"Run {report['run_id']} / BurnLens {report['software_version']} / dataset, split, baseline, model: none", fill="#5d6b64", font=_font(18))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=False)


def write_surface(
    report: dict[str, Any],
    previews: dict[str, dict[str, np.ndarray | None]],
    *,
    output_directory: Path,
    frozen_evidence_directory: Path | None = None,
) -> dict[str, Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": output_directory / f"{SURFACE_ID}.json",
        "html": output_directory / f"{SURFACE_ID}.html",
        "png": output_directory / f"{SURFACE_ID}.png",
        "response_template": output_directory / f"{SURFACE_ID}-RESPONSE-TEMPLATE.json",
    }
    frozen_evidence_directory = frozen_evidence_directory or output_directory
    current_pages = render_current_pages(report, previews, output_directory)
    response = _response_template(report)
    paths["response_template"].write_bytes((json.dumps(response, indent=2) + "\n").encode("utf-8"))
    render_summary_png(report, paths["png"])
    current_heights = {item.name: Image.open(item).height for item in current_pages}
    frozen_heights: dict[str, int] = {}
    for unit in report["units"]:
        name = unit["frozen_evidence_page"]
        if name not in frozen_heights:
            with Image.open(frozen_evidence_directory / name) as image:
                frozen_heights[name] = image.height
    render_html(report, response, paths["html"], current_heights, frozen_heights)
    output_paths = [paths["html"], paths["png"], paths["response_template"], *current_pages]
    report["outputs"] = [
        {"path": item.name, "bytes": item.stat().st_size, "sha256": _digest(item.read_bytes())}
        for item in output_paths
    ]
    paths["json"].write_bytes((json.dumps(report, indent=2) + "\n").encode("utf-8"))
    paths["current_pages"] = current_pages[0].parent
    return paths
