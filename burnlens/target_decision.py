"""Build deterministic evidence for the owner-approved BurnLens target decision."""

from __future__ import annotations

from hashlib import sha256
from html import escape
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


REPORT_ID = "TARGET-DECISION-2026-001"
REPORT_SCHEMA_VERSION = "0.2.0"
REPORT_VERSION = "target-path-decision-v0.2.0"
SOFTWARE_VERSION = "0.6.0"
TARGET_DECISION_VERSION = "target-burn-scar-v0.2.0"
AOI_VERSION = "aoi-darlene3-model-v0.2.0"
WARNING = (
    "Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. "
    "Not evacuation, routing, tactical, or incident-command support. Official sources govern."
)


class TargetDecisionError(ValueError):
    """Raised when target-decision evidence is incomplete or contradictory."""


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return ImageFont.load_default(size=size)


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_lf_text(path: Path) -> str:
    """Hash UTF-8 text after universal-newline decoding and LF serialization."""
    try:
        with path.open("r", encoding="utf-8", newline=None) as handle:
            normalized = handle.read().encode("utf-8")
    except (OSError, UnicodeError) as error:
        raise TargetDecisionError(f"INPUT_TEXT_INVALID:{path.name}") from error
    return sha256(normalized).hexdigest()


def _write_utf8_lf(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise TargetDecisionError(f"INPUT_JSON_INVALID:{path.name}") from error
    if not isinstance(value, dict):
        raise TargetDecisionError(f"INPUT_JSON_OBJECT_REQUIRED:{path.name}")
    return value


def _validate_inputs(
    observation: dict[str, Any], aoi: dict[str, Any], mtbs: dict[str, Any]
) -> None:
    if observation.get("report_id") != "OBSERVATION-GEOMETRY-2026-001":
        raise TargetDecisionError("OBSERVATION_REPORT_ID_UNEXPECTED")
    if observation.get("decision") != "ACCEPT_COMPLEMENTARY_REFERENCE_GEOMETRY_DEFER_LABELS":
        raise TargetDecisionError("ACTIVE_FIRE_DECISION_UNEXPECTED")
    gates = observation.get("quality_gates") or {}
    if gates.get("label_array_created") is not False or gates.get("dataset_created") is not False:
        raise TargetDecisionError("ACTIVE_FIRE_OUTPUT_STATE_UNEXPECTED")
    if aoi.get("aoi_version") != AOI_VERSION:
        raise TargetDecisionError("AOI_VERSION_UNEXPECTED")
    findings = mtbs.get("findings") or {}
    required_zeroes = (
        "darlene_name_match_count_2024",
        "aoi_feature_count_2024",
        "aoi_feature_count_all_years",
    )
    if any(findings.get(key) != 0 for key in required_zeroes):
        raise TargetDecisionError("MTBS_DARLENE_ABSENCE_NOT_PROVEN")
    if findings.get("inventory_feature_count_2024") != 941:
        raise TargetDecisionError("MTBS_INVENTORY_COUNT_UNEXPECTED")
    if mtbs.get("rights_review", {}).get("metadata_use_status") != "RESOLVED_WITH_CITATION":
        raise TargetDecisionError("MTBS_METADATA_RIGHTS_UNRESOLVED")
    if mtbs.get("serialization") != "UTF-8 JSON with LF canonical line endings":
        raise TargetDecisionError("MTBS_SERIALIZATION_CONTRACT_UNEXPECTED")


def build_report(
    *,
    observation_path: Path,
    aoi_path: Path,
    mtbs_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    observation = _read_json(observation_path)
    aoi = _read_json(aoi_path)
    mtbs = _read_json(mtbs_path)
    _validate_inputs(observation, aoi, mtbs)

    selected = observation["candidate_summary"]["selected_native_id"]
    selected_candidate = next(
        item for item in observation["candidates"] if item["native_id"] == selected
    )
    inspection = selected_candidate["inspection"]
    offset_hours = abs(selected_candidate["seconds_from_sentinel_observation"]) / 3600
    median_view = inspection["aoi_reference_qualified_view_zenith_median_degrees"]

    return {
        "report_id": REPORT_ID,
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 337,
        "branch": "codex/p2o2-t05-burn-scar-target",
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": None,
        "aoi_version": AOI_VERSION,
        "target_decision_version": TARGET_DECISION_VERSION,
        "dataset_version": None,
        "label_schema_version": None,
        "baseline_version": None,
        "model_version": None,
        "input_evidence": {
            "observation_report": {
                "report_id": observation["report_id"],
                "run_id": observation["run_id"],
                "sha256_lf_normalized": _sha256_lf_text(observation_path),
            },
            "aoi_report": {
                "report_id": aoi["report_id"],
                "sha256_lf_normalized": _sha256_lf_text(aoi_path),
            },
            "mtbs_availability_record": {
                "record_id": mtbs["record_id"],
                "sha256_lf_normalized": _sha256_lf_text(mtbs_path),
            },
        },
        "owner_decision": {
            "recorded_date": "2026-07-14",
            "decision": "ACTIVATE_BURN_SCAR_BINARY_MASK_FALLBACK",
            "status": "ACTIVE",
            "scope": (
                "Change the active target path from active-fire/hotspot-informed labels to the already established "
                "burn-scar binary-mask fallback. The first CV task remains binary semantic segmentation."
            ),
            "unchanged": [
                "portfolio promise and technical/technical-adjacent reviewer",
                "binary semantic-segmentation task and mask-first GEOINT workflow",
                "use boundaries, official-source precedence, and transparency requirements",
                "six phase outcomes and baseline-first model decision",
            ],
        },
        "target_contract": {
            "active_target": "burn-scar binary mask",
            "former_primary_disposition": "COMPLEMENTARY_REFERENCE_ONLY",
            "former_primary": "active-fire / hotspot-informed binary fire mask",
            "positive_class": (
                "Burn-scar pixels supported by a future accepted, temporally appropriate, quality-screened optical-change "
                "and review protocol. No positive label exists yet."
            ),
            "background_candidate": (
                "Clear, observable pixels supported as unburned under the future accepted protocol; outside a perimeter "
                "or absence of a hotspot is not automatically background."
            ),
            "unknown": (
                "Cloud, smoke, haze, shadow, snow, temporal ambiguity, source disagreement, unobserved areas, and other "
                "insufficient evidence remain unknown and are never silently converted to background."
            ),
            "excluded": (
                "Invalid pixels, non-processing masks, failed georegistration, and quality states disallowed by the "
                "future accepted protocol are excluded."
            ),
            "severity_classes_used": False,
            "multiclass_expansion": False,
        },
        "active_fire_evidence": {
            "disposition": "REJECT_DIRECT_LABELS_RETAIN_REFERENCE",
            "selected_observation": selected,
            "support_m": 375,
            "sentinel_offset_hours": round(offset_hours, 6),
            "qualified_median_view_zenith_degrees": median_view,
            "qualified_record_count": inspection["aoi_reference_qualified_count"],
            "reason": (
                "The best bounded observation is useful complementary evidence, but its 375 m support and temporal "
                "offset cannot define 10-20 m pixel truth."
            ),
        },
        "mtbs_assessment": {
            "disposition": "NO_CURRENT_DARLENE3_RECORD_CONSIDER_METHODS_AND_CROSS_FIRE_REFERENCE",
            "accessed_at_utc": mtbs["accessed_at_utc"],
            "service_version": mtbs["service"]["current_version"],
            "inventory_feature_count_2024": mtbs["findings"]["inventory_feature_count_2024"],
            "darlene_name_match_count_2024": mtbs["findings"]["darlene_name_match_count_2024"],
            "aoi_feature_count_2024": mtbs["findings"]["aoi_feature_count_2024"],
            "aoi_feature_count_all_years": mtbs["findings"]["aoi_feature_count_all_years"],
            "interpretation": (
                "MTBS is scientifically relevant and publishes fire-level pre/post imagery, burn indices, boundaries, "
                "severity, and non-processing masks for mapped fires. Its current official vector services expose no "
                "Darlene 3 record in the frozen AOI, so it cannot supply the exact label for this experiment today."
            ),
            "future_rule": (
                "Re-query the current official inventory before any later MTBS use because releases are quarterly and "
                "revised fire products replace prior versions. Treat any future product as analyst-interpreted reference, "
                "not field truth; do not convert its six severity classes into a new multiclass target."
            ),
            "rights_status": mtbs["rights_review"],
        },
        "next_gate": {
            "decision": "PROCEED_TO_BURN_SCAR_SOURCE_AND_LABEL_PROTOCOL",
            "required_outcome": (
                "Select and visually validate one legally usable, temporally defensible pre/post optical source pair over "
                "the frozen AOI, then approve a binary burn-scar labeling protocol before creating any label array."
            ),
            "must_prove": [
                "exact source identity, terms, provenance, acquisition dates, CRS, grid, and AOI coverage",
                "pre/post optical quality and interpretable burn-change signal on real rendered pixels",
                "burned, background-candidate, unknown, excluded, and review-needed rules",
                "georegistration tolerance, non-processing masks, temporal leakage controls, and independent QA",
                "whether a reproducible non-model spectral baseline is defensible before any model work",
            ],
            "not_authorized_yet": [
                "label array or dataset creation",
                "train/validation/test split",
                "baseline mask, model training, inference, or performance claim",
                "severity, recovery, or multiclass target",
            ],
        },
        "quality_gates": {
            "owner_decision_recorded": True,
            "active_fire_direct_label_path_rejected": True,
            "mtbs_current_exact_fire_availability_checked": True,
            "mtbs_exact_darlene_record_available": False,
            "target_fallback_activated": True,
            "structured_input_hashes_lf_normalized": True,
            "label_array_created": False,
            "dataset_created": False,
            "baseline_created": False,
            "model_created": False,
        },
        "claims": {
            "permitted": [
                "BurnLens rejected direct active-fire labels and activated its controlled burn-scar binary-mask fallback.",
                "The current official MTBS occurrence services returned no Darlene 3 feature in the frozen AOI at the recorded access time.",
                "MTBS remains relevant as methodology and potential future or cross-fire reference evidence.",
            ],
            "prohibited": [
                "A burn-scar label, dataset, baseline, trained model, inference result, or analytical application exists.",
                "MTBS, NIFC geometry, severity classes, hotspots, or non-detections are pixel-perfect field truth.",
                "BurnLens is official, operational, emergency-ready, field-validated, or endorsed.",
            ],
        },
        "source_guidance": mtbs["source_guidance"],
        "attribution": [
            "MTBS Program (U.S. Geological Survey and USDA Forest Service), official services accessed 2026-07-14.",
            "NASA VIIRS/JPSS2 remains complementary native-scale thermal-anomaly reference evidence.",
            "NIFC WFIGS final-perimeter geometry remains an incident reference and AOI derivation source only.",
        ],
        "source_precedence": "Official sources govern over every BurnLens-derived artifact.",
        "warning": WARNING,
    }


def _wrapped_lines(draw: ImageDraw.ImageDraw, text: str, width: float, size: int) -> list[str]:
    font = _font(size)
    lines: list[str] = []
    current = ""
    for word in text.split():
        proposed = f"{current} {word}".strip()
        if current and draw.textlength(proposed, font=font) > width:
            lines.append(current)
            current = word
        else:
            current = proposed
    if current:
        lines.append(current)
    return lines


def _draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    *,
    width: int,
    size: int,
    fill: str,
    max_lines: int,
    line_height: int,
) -> None:
    for index, line in enumerate(_wrapped_lines(draw, text, width, size)[:max_lines]):
        draw.text((xy[0], xy[1] + index * line_height), line, fill=fill, font=_font(size))


def render_png(report: dict[str, Any], path: Path) -> None:
    canvas = Image.new("RGB", (1600, 1050), "#f4f0e8")
    draw = ImageDraw.Draw(canvas)
    ink = "#15211d"
    muted = "#5d6b64"
    teal = "#006b64"
    orange = "#f05a28"
    panel = "#fffdf8"

    draw.rectangle((0, 0, 1600, 185), fill="#132a26")
    draw.text((70, 36), "BURNLENS  /  TARGET PATH", fill="#b9d8cf", font=_font(22))
    draw.text((70, 78), "BURN-SCAR BINARY MASK FALLBACK", fill="white", font=_font(40))
    draw.text((70, 132), "OWNER-APPROVED  /  ACTIVE", fill="#ffd166", font=_font(25))
    draw.text((1210, 45), "TARGET VERSION", fill="#b9d8cf", font=_font(18))
    draw.text((1210, 80), TARGET_DECISION_VERSION, fill="white", font=_font(20))
    draw.text((1210, 122), "labels: not created", fill="#ffd166", font=_font(19))

    cards = (
        (
            "1  ACTIVE-FIRE PATH",
            "Direct labels rejected",
            f"Best reference: {report['active_fire_evidence']['support_m']} m support, "
            f"{report['active_fire_evidence']['sentinel_offset_hours']:.2f} h from Sentinel. Retained as complementary evidence only.",
            orange,
        ),
        (
            "2  MTBS EXACT FIRE",
            "No current Darlene 3 record",
            f"{report['mtbs_assessment']['inventory_feature_count_2024']} current 2024 inventory records; "
            "0 Darlene name matches and 0 AOI features in 2024 or all-years layers.",
            teal,
        ),
        (
            "3  NEXT EVIDENCE GATE",
            "Pre/post optical proof",
            "Validate one legally usable image pair and an uncertainty-preserving binary label protocol before creating labels, a dataset, or a baseline.",
            teal,
        ),
    )
    for index, (eyebrow, title, body, accent) in enumerate(cards):
        left = 60 + index * 510
        right = left + 470
        draw.rounded_rectangle((left, 220, right, 510), radius=22, fill=panel, outline="#d7d0c4", width=2)
        draw.rectangle((left, 220, left + 9, 510), fill=accent)
        draw.text((left + 32, 250), eyebrow, fill=accent, font=_font(18))
        _draw_wrapped(draw, (left + 32, 292), title, width=400, size=29, fill=ink, max_lines=2, line_height=38)
        _draw_wrapped(draw, (left + 32, 376), body, width=400, size=19, fill=muted, max_lines=5, line_height=28)

    draw.rounded_rectangle((60, 550, 1540, 835), radius=22, fill="#e6efeb", outline="#b8cbc3", width=2)
    draw.text((90, 580), "BINARY LABEL CONTRACT / DESIGN GATE, NOT AN IMPLEMENTED LABEL", fill=teal, font=_font(22))
    semantics = (
        ("BURNED", "Future positive pixels need accepted optical-change and review evidence."),
        ("BACKGROUND CANDIDATE", "Clear observable unburned evidence; outside a perimeter is not enough."),
        ("UNKNOWN", "Cloud, smoke, shadow, time ambiguity, and disagreement stay unknown."),
        ("EXCLUDED", "Invalid, non-processing, misregistered, or disallowed quality states."),
    )
    for index, (title, body) in enumerate(semantics):
        left = 90 + index * 360
        draw.text((left, 640), title, fill=ink, font=_font(19))
        _draw_wrapped(draw, (left, 680), body, width=320, size=18, fill=muted, max_lines=4, line_height=27)

    draw.rounded_rectangle((60, 865, 1540, 970), radius=18, fill=panel, outline="#d7d0c4", width=2)
    draw.text((90, 892), "TRACEABILITY", fill=teal, font=_font(18))
    trace = (
        f"run {report['run_id']}  /  source {report['git_source_commit'][:12]}  /  AOI {report['aoi_version']}  /  "
        "application none  /  dataset none  /  label schema none  /  baseline none  /  model none"
    )
    _draw_wrapped(draw, (90, 928), trace, width=1400, size=17, fill=ink, max_lines=2, line_height=25)

    draw.rectangle((0, 995, 1600, 1050), fill="#132a26")
    draw.text((55, 1013), WARNING, fill="white", font=_font(17))
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], image_name: str, path: Path) -> None:
    permitted = "".join(f"<li>{escape(item)}</li>" for item in report["claims"]["permitted"])
    prohibited = "".join(f"<li>{escape(item)}</li>" for item in report["claims"]["prohibited"])
    must_prove = "".join(f"<li>{escape(item)}</li>" for item in report["next_gate"]["must_prove"])
    sources = "".join(
        f'<li><a href="{escape(item["url"])}">{escape(item["organization"])}</a> — {escape(item["role"])}</li>'
        for item in report["source_guidance"]
    )
    target = report["target_contract"]
    mtbs = report["mtbs_assessment"]
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens burn-scar target decision</title>
<style>
:root{{--ink:#15211d;--muted:#5d6b64;--paper:#f4f0e8;--panel:#fffdf8;--teal:#006b64;--orange:#f05a28}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}
header{{background:#132a26;color:white;padding:2.4rem max(1rem,calc((100% - 1180px)/2))}} header p{{max-width:75ch;color:#c9ddd6}}
main{{max-width:1180px;margin:auto;padding:2rem 1rem 4rem}} section,.status,.card{{background:var(--panel);border:1px solid #d7d0c4;border-radius:14px;padding:1.25rem;margin:1rem 0}}
.status{{border-left:8px solid var(--orange)}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem}}
.metric{{display:block;color:var(--teal);font-size:2rem;font-weight:760}} img{{display:block;width:100%;height:auto;border:1px solid #d7d0c4;border-radius:14px}}
code{{overflow-wrap:anywhere}} a{{color:var(--teal)}} dt{{font-weight:750;margin-top:.7rem}} dd{{margin-left:0;color:var(--muted)}}
.warning{{background:#132a26;color:white;padding:1rem;border-radius:10px;font-weight:650}} .no{{color:var(--orange);font-weight:760}}
</style></head><body>
<header><h1>Burn-scar binary-mask fallback is active</h1><p>BurnLens records the owner-approved target change without creating a label, dataset, baseline, model, or analytical wildfire output.</p></header>
<main>
<div class="status"><h2>{escape(report['owner_decision']['decision'])}</h2><p>{escape(report['owner_decision']['scope'])}</p><p><strong>Target version:</strong> <code>{escape(report['target_decision_version'])}</code></p></div>
<div class="grid"><div class="card"><span class="metric">375 m</span>best active-fire reference support; direct labels rejected</div><div class="card"><span class="metric">0</span>current MTBS Darlene 3 / AOI records</div><div class="card"><span class="metric">0</span>label arrays, datasets, baselines, and models</div></div>
<figure><img src="{escape(image_name)}" width="1600" height="1050" alt="BurnLens target-path evidence showing the active burn-scar fallback, rejected direct active-fire labels, absent current MTBS Darlene record, and next optical evidence gate"><figcaption>Report <code>{escape(report['report_id'])}</code>; run <code>{escape(report['run_id'])}</code>; source commit <code>{escape(report['git_source_commit'])}</code>.</figcaption></figure>
<section><h2>Why the active-fire label path stopped</h2><p>{escape(report['active_fire_evidence']['reason'])}</p><p>Thermal-anomaly evidence remains complementary reference only. Non-detection is not background, and hotspots are not resized into optical pixel truth.</p></section>
<section><h2>MTBS: relevant, but no exact Darlene 3 product today</h2><p>{escape(mtbs['interpretation'])}</p><p>The official 2024 inventory returned <strong>{mtbs['inventory_feature_count_2024']}</strong> records, with <span class="no">zero</span> Darlene name matches and <span class="no">zero</span> features in the frozen AOI in both the 2024 and all-years occurrence layers.</p><p>{escape(mtbs['future_rule'])}</p></section>
<section><h2>Binary target semantics before implementation</h2><dl><dt>Burned</dt><dd>{escape(target['positive_class'])}</dd><dt>Background candidate</dt><dd>{escape(target['background_candidate'])}</dd><dt>Unknown</dt><dd>{escape(target['unknown'])}</dd><dt>Excluded</dt><dd>{escape(target['excluded'])}</dd></dl><p>Severity classes used: <strong>No.</strong> Multiclass expansion: <strong>No.</strong></p></section>
<section><h2>Next gate</h2><p>{escape(report['next_gate']['required_outcome'])}</p><ul>{must_prove}</ul></section>
<div class="grid"><section><h2>Permitted claims</h2><ul>{permitted}</ul></section><section><h2>Prohibited claims</h2><ul>{prohibited}</ul></section></div>
<section><h2>Traceability</h2><dl><dt>Repository</dt><dd>{escape(report['repository'])}</dd><dt>Software / target</dt><dd>{escape(report['software_version'])} / <code>{escape(report['target_decision_version'])}</code></dd><dt>AOI</dt><dd>{escape(report['aoi_version'])}</dd><dt>Application / dataset / label schema / baseline / model</dt><dd>Not created / not created / not created / not created / not created</dd><dt>Run</dt><dd><code>{escape(report['run_id'])}</code></dd><dt>Source commit</dt><dd><code>{escape(report['git_source_commit'])}</code></dd></dl></section>
<section><h2>Primary sources</h2><ul>{sources}</ul><p>{escape(report['source_precedence'])}</p></section>
<p class="warning">{escape(report['warning'])}</p>
</main></body></html>"""
    _write_utf8_lf(path, html)


def write_report(report: dict[str, Any], output_directory: Path) -> dict[str, Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": output_directory / f"{REPORT_ID}.json",
        "html": output_directory / f"{REPORT_ID}.html",
        "png": output_directory / f"{REPORT_ID}.png",
    }
    render_png(report, paths["png"])
    report["rendered_outputs"] = {
        "json": paths["json"].name,
        "html": paths["html"].name,
        "png": paths["png"].name,
        "png_sha256": _sha256(paths["png"]),
    }
    _write_utf8_lf(paths["json"], json.dumps(report, indent=2) + "\n")
    render_html(report, paths["png"].name, paths["html"])
    return paths


def run_target_decision(
    *,
    observation_path: Path,
    aoi_path: Path,
    mtbs_path: Path,
    output_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Path]:
    report = build_report(
        observation_path=observation_path,
        aoi_path=aoi_path,
        mtbs_path=mtbs_path,
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
    )
    return write_report(report, output_directory)
