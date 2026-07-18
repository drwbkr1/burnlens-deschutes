from __future__ import annotations

from hashlib import sha256
from html import escape
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


REPORT_ID = "LABEL-REGION-REMEDIATION-PLAN-2026-001"
REPORT_VERSION = "label-region-remediation-plan-v0.1.0"
PROTOCOL_VERSION = "owner-confirmed-contiguous-region-review-v0.1.0"
SOFTWARE_VERSION = "0.28.0"
DECISION = "ADOPT_REGION_FIRST_OWNER_REVIEW_REQUIRE_EVENT_DIVERSITY_BEFORE_DATASET"


class LabelRegionRemediationPlanError(RuntimeError):
    pass


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LabelRegionRemediationPlanError(f"invalid JSON input: {path.name}") from exc
    if not isinstance(value, dict):
        raise LabelRegionRemediationPlanError(f"JSON object required: {path.name}")
    return value


def _binding(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {"path": path.name, "bytes": len(payload), "sha256": sha256(payload).hexdigest()}


def _candidate(source: dict[str, Any], fire_id: str) -> dict[str, Any]:
    for item in source["candidates"]:
        if item["fire_id"] == fire_id:
            return item
    raise LabelRegionRemediationPlanError(f"required scout candidate missing: {fire_id}")


def build_report(
    sufficiency_path: Path,
    scout_report_path: Path,
    scout_source_path: Path,
    bundle_fitness_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    sufficiency = _read_json(sufficiency_path)
    scout = _read_json(scout_report_path)
    source = _read_json(scout_source_path)
    bundle = _read_json(bundle_fitness_path)
    if sufficiency.get("report_id") != "PROTOTYPE-LABEL-SUFFICIENCY-2026-001":
        raise LabelRegionRemediationPlanError("unexpected sufficiency report")
    if sufficiency.get("decision") != "REMEDIATE_LABEL_COVERAGE_BEFORE_DATASET_SPLIT_BASELINE_MODEL":
        raise LabelRegionRemediationPlanError("upstream sufficiency decision drift")
    if scout.get("report_id") != "OFFICIAL-SOURCE-SCOUT-2026-001":
        raise LabelRegionRemediationPlanError("unexpected scout report")
    if source.get("source_id") != "OFFICIAL-SOURCE-SCOUT-SOURCE-2026-001":
        raise LabelRegionRemediationPlanError("unexpected scout source capture")
    if bundle.get("report_id") != "CURRENT-REFERENCE-BUNDLE-FITNESS-2026-001":
        raise LabelRegionRemediationPlanError("unexpected bundle fitness report")
    if any(sufficiency["boundaries"].values()):
        raise LabelRegionRemediationPlanError("upstream analytical boundary drift")

    current_events = int(sufficiency["inventory"]["event_groups"])
    required_events = 6
    gw = _candidate(source, "OR4435412173920070830")
    milli = _candidate(source, "OR4425712174320170811")
    cache = _candidate(source, "OR4438412172820020723")
    two_bulls = _candidate(source, "OR4414212147220140607")
    report = {
        "report_id": REPORT_ID,
        "report_version": REPORT_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 449,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": SOFTWARE_VERSION,
        "bindings": {
            "sufficiency": _binding(sufficiency_path),
            "official_source_scout": _binding(scout_report_path),
            "official_source_capture": _binding(scout_source_path),
            "current_bundle_fitness": _binding(bundle_fitness_path),
        },
        "provenance": {
            "aoi_version": "aoi-darlene3-model-v0.2.0",
            "target_version": "target-burn-scar-v0.2.0",
            "label_schema_version": "burn-scar-five-state-schema-v0.1.0",
            "input_label_set_version": "owner-approved-prototype-labels-v0.1.0",
            "planned_region_protocol_version": PROTOCOL_VERSION,
            "dataset_version": None,
            "split_version": None,
            "baseline_version": None,
            "model_version": None,
            "source_record_id": "SOURCE-2026-018",
            "terms_record_id": "TERMS-2026-013",
            "source_precedence_id": "SOURCE-PRECEDENCE-2026-011",
        },
        "trigger": {
            "prototype_points": int(sufficiency["inventory"]["prototype_labels"]),
            "candidate_domain_pixels": int(sufficiency["inventory"]["candidate_domain_pixels"]),
            "point_coverage_percent": sufficiency["inventory"]["prototype_fraction_of_candidate_domain_percent"],
            "current_event_groups": current_events,
            "current_reference_regimes": int(sufficiency["partition_feasibility"]["source_regime_count"]),
            "highest_leverage_weakness": "reviewed center pixels do not define contiguous unknown-aware masks, and three events cannot replicate train/validation/test evidence",
        },
        "review_unit_contract": {
            "unit": "one contiguous evidence-coherent region on an event's frozen native optical grid",
            "not_a_unit": ["a center pixel expanded by radius", "an arbitrary square tile", "an entire connected proposal component without boundary review"],
            "candidate_generator": [
                "start only from an owner-approved prototype center with exact lineage",
                "grow only through same-class frozen proposal pixels that pass pair-quality and registration gates",
                "stop at proposal-state changes, invalid quality, reference disagreement, spectral discontinuity, or an existing region",
                "split oversized coherent components only on deterministic optical/reference boundaries, never on a tiling grid",
                "emit a one-native-pixel unknown ring around every proposed core and preserve all upstream unknown, excluded, and review-needed pixels",
            ],
            "owner_surface": "show pre/post optical evidence, quality state, permitted reference evidence, core outline, unknown ring, scale, and source limitations",
            "owner_decisions": {
                "yes": "may become an owner-approved prototype region only after all region/source/quality/leakage gates pass",
                "no": "exclude the proposed region and do not infer the opposite class",
                "uncertain": "retain the region and its boundary as unknown",
            },
            "partial_acceptance": "not permitted in v0.1.0; revise the deterministic candidate and present a new version instead",
        },
        "source_roles": [
            {"source": "Sentinel-2 L2A pre/post", "role": "primary native-grid optical evidence", "label_status": "not truth"},
            {"source": "MTBS", "role": "analyst-interpreted boundary/severity context", "label_status": "not automatic truth"},
            {"source": "RAVG", "role": "forest-calibrated vegetation-condition context with masks", "label_status": "limited outside forest; not automatic truth"},
            {"source": "BAER", "role": "public unthresholded dNBR context", "label_status": "preliminary; restricted thresholded BARC excluded"},
            {"source": "Landsat C2 L3 Burned Area", "role": "30 m algorithmic challenge/reference and sensor-shift evidence", "label_status": "not truth; QA and optical corroboration required"},
            {"source": "Annual NLCD", "role": "pre-fire land-cover stratification and applicability context", "label_status": "never burned/background evidence by itself"},
        ],
        "event_plan": {
            "minimum_event_groups_before_split_fitness": required_events,
            "additional_event_groups_required": required_events - current_events,
            "minimum_groups_per_eventual_role": 2,
            "requirements": [
                "every event must contribute separately reviewed burned, background, and unknown-boundary evidence",
                "whole event/geography/time groups must be frozen before acquisition and may enter only one eventual role",
                "the region generator must be frozen before reviewing at least two never-tuned transfer events",
                "no source program or exact evidence regime may occur in only one eventual split role",
                "no single event may provide a majority of accepted region pixels",
            ],
            "ranked_reconnaissance": [
                {"priority": 1, "fire": milli["fire_name"], "fire_id": milli["fire_id"], "year": milli["year"], "role": "Sentinel-era continuity candidate", "gate": "existing tile-seam exclusion must be solved by one deterministic multi-tile contract before acquisition"},
                {"priority": 2, "fire": gw["fire_name"], "fire_id": gw["fire_id"], "year": gw["year"], "role": "highest cross-program and temporal challenge evidence", "gate": "Landsat-only sensor shift; never mix into a Sentinel-native pool without a separately justified contract"},
                {"priority": 3, "fire": two_bulls["fire_name"], "fire_id": two_bulls["fire_id"], "year": two_bulls["year"], "role": "MTBS+RAVG regime replication candidate", "gate": "pre-Sentinel Landsat-only sensor shift"},
                {"priority": 4, "fire": cache["fire_name"], "fire_id": cache["fire_id"], "year": cache["year"], "role": "BAER+MTBS reference diversity", "gate": "older Landsat-only event; reference/challenge role first"},
            ],
            "next_acquisition_rule": "perform metadata-only Central Oregon Sentinel-era scouting first; acquire no event until at least three comparable candidates can satisfy one shared optical and region protocol",
        },
        "advancement_gates": [
            {"gate": "region reproducibility", "requirement": "exact source bytes, generator/version, grid, seed, parameters, core mask, unknown ring, and run hash reproduce"},
            {"gate": "owner confirmation", "requirement": "every accepted region has an exact yes response to the rendered region version; no/uncertain remain excluded"},
            {"gate": "class and uncertainty", "requirement": "every event has accepted burned/background regions and explicit unknown boundaries; no class is inferred from absence"},
            {"gate": "event diversity", "requirement": "at least six immutable event groups and at least two groups per eventual train/validation/test role"},
            {"gate": "regime leakage", "requirement": "source programs/regimes are replicated across events and not unique to one eventual role"},
            {"gate": "dominance", "requirement": "no single event supplies more than 50% of accepted region pixels; natural prevalence is reported separately from review sampling"},
            {"gate": "evaluation honesty", "requirement": "owner-confirmed regions remain prototype evidence, not independent ground truth; reserve never-tuned events and name agreement metrics honestly"},
            {"gate": "terms and publication", "requirement": "exact notices pass; restricted BARC and provider bytes remain private; public derivatives are explicitly permitted"},
        ],
        "phase_two_consequence": {
            "current_decision": "PLAN_ONLY_AND_DEFER_ACQUISITION_LABEL_REGIONS_DATASET_SPLIT_BASELINE_MODEL",
            "next_checkpoint": "implement and render a small deterministic region-candidate pilot on existing events, without promoting labels",
            "dataset_fitness_reopens_only_after": "region pilot, owner review, additional-event acquisition, and every advancement gate",
        },
        "boundaries": {
            "point_labels_expanded": False,
            "region_labels_created": False,
            "new_source_pixels_acquired": False,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
            "accuracy_or_ground_truth_claimed": False,
            "field_official_operational_or_endorsed_claimed": False,
        },
        "decision": DECISION,
        "warning": "Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Official sources govern.",
    }
    return report


def render_html(report: dict[str, Any]) -> str:
    trigger = report["trigger"]
    event_plan = report["event_plan"]
    source_rows = "".join(
        f"<tr><th>{escape(item['source'])}</th><td>{escape(item['role'])}</td><td>{escape(item['label_status'])}</td></tr>"
        for item in report["source_roles"]
    )
    gate_rows = "".join(
        f"<tr><th>{escape(item['gate'].title())}</th><td>{escape(item['requirement'])}</td></tr>"
        for item in report["advancement_gates"]
    )
    candidate_rows = "".join(
        f"<tr><td>{item['priority']}</td><th>{escape(item['fire'])} ({item['year']})</th><td>{escape(item['role'])}</td><td>{escape(item['gate'])}</td></tr>"
        for item in event_plan["ranked_reconnaissance"]
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens label-region remediation plan</title><style>
:root{{--ink:#123f3a;--paper:#f5f0e6;--card:#fff;--line:#b9ccc8;--accent:#d66b3d;--muted:#526763}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.48 system-ui,sans-serif}}header{{background:#103f39;color:#fff;padding:42px max(24px,5vw)}}main{{max-width:1180px;margin:auto;padding:32px 24px 56px}}h1{{margin:0 0 8px;font-size:clamp(2rem,5vw,3.2rem)}}.metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}}.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px}}.big{{font-size:2.35rem;font-weight:700}}table{{width:100%;border-collapse:collapse;background:#fff;margin:18px 0}}th,td{{text-align:left;padding:12px;border-bottom:1px solid #d8e1df;vertical-align:top}}.scroll{{overflow:auto}}.decision{{border-left:8px solid var(--accent)}}code{{overflow-wrap:anywhere}}@media(max-width:760px){{.metrics{{grid-template-columns:repeat(2,minmax(0,1fr))}}th,td{{min-width:170px}}}}@media(max-width:420px){{.metrics{{grid-template-columns:1fr}}}}
</style></head><body><header><h1>Label-region remediation plan</h1><p>Region-first owner review · whole-event leakage controls · no dataset created</p></header><main>
<section class="metrics"><div class="card"><div class="big">{trigger['prototype_points']}</div>reviewed points</div><div class="card"><div class="big">{trigger['current_event_groups']}</div>current events</div><div class="card"><div class="big">{event_plan['minimum_event_groups_before_split_fitness']}</div>minimum events</div><div class="card"><div class="big">+{event_plan['additional_event_groups_required']}</div>event gap</div></section>
<section class="card decision"><h2>Decision</h2><p><code>{escape(report['decision'])}</code></p><p>Replace point expansion and arbitrary tiles with deterministic evidence-coherent regions, a one-pixel unknown ring, exact owner yes/no/uncertain review, and at least six whole-event groups before split fitness can reopen.</p></section>
<h2>Source roles</h2><div class="scroll"><table><thead><tr><th>Source</th><th>Permitted role</th><th>Truth boundary</th></tr></thead><tbody>{source_rows}</tbody></table></div>
<h2>Event reconnaissance</h2><div class="scroll"><table><thead><tr><th>Priority</th><th>Fire</th><th>Role</th><th>Blocking gate</th></tr></thead><tbody>{candidate_rows}</tbody></table></div>
<h2>Advancement gates</h2><table>{gate_rows}</table>
<p>Trace: source <code>{escape(report['git_source_commit'])}</code> · BurnLens <code>{SOFTWARE_VERSION}</code> · protocol <code>{PROTOCOL_VERSION}</code> · run <code>{escape(report['run_id'])}</code> · dataset/split/baseline/model none.</p><p>{escape(report['warning'])}</p>
</main></body></html>"""


def render_png(report: dict[str, Any], path: Path) -> None:
    image = Image.new("RGB", (1800, 1280), "#f5f0e6")
    draw = ImageDraw.Draw(image)
    body = ImageFont.load_default(size=25)
    title = ImageFont.load_default(size=47)
    big = ImageFont.load_default(size=42)
    draw.rectangle((0, 0, 1800, 180), fill="#103f39")
    draw.text((70, 42), "BurnLens label-region remediation plan", fill="white", font=title)
    draw.text((70, 112), "Region-first owner review · whole-event controls · no dataset", fill="#c8ddd8", font=body)
    metrics = [("24", "reviewed points"), ("3", "current events"), ("6", "minimum events"), ("+3", "event gap")]
    for index, (value, label) in enumerate(metrics):
        x = 70 + index * 420
        draw.rounded_rectangle((x, 225, x + 360, 370), radius=16, fill="white", outline="#b9ccc8", width=2)
        draw.text((x + 24, 252), value, fill="#123f3a", font=big)
        draw.text((x + 24, 318), label, fill="#526763", font=body)
    draw.text((70, 420), "Region contract", fill="#123f3a", font=big)
    contract = [
        "Seed: exact owner-approved center with frozen lineage",
        "Grow: same-state, quality-valid, registered, evidence-coherent pixels",
        "Stop: state/quality/reference/spectral boundary or existing region",
        "Buffer: one native pixel remains unknown around every core",
        "Review: owner yes / no / uncertain on the exact rendered region version",
    ]
    y = 485
    for line in contract:
        draw.rounded_rectangle((70, y, 1730, y + 66), radius=12, fill="white", outline="#d1ddda", width=2)
        draw.ellipse((94, y + 22, 112, y + 40), fill="#d66b3d")
        draw.text((135, y + 17), line, fill="#123f3a", font=body)
        y += 78
    draw.text((70, 900), "Before dataset fitness can reopen", fill="#123f3a", font=big)
    gates = [
        ">=6 immutable event groups / >=2 per eventual role",
        "burned + background + unknown boundary in every event",
        "source regimes replicated across events and roles",
        "never-tuned transfer events reserved · no event majority",
    ]
    y = 970
    for line in gates:
        draw.text((92, y), "- " + line, fill="#7f3524", font=body)
        y += 55
    draw.text((70, 1215), "Decision: plan region review and event diversity; create no labels, dataset, split, baseline, or model.", fill="#7f3524", font=body)
    image.save(path, format="PNG", optimize=False)


def write_outputs(output_directory: Path, report: dict[str, Any]) -> list[dict[str, Any]]:
    output_directory.mkdir(parents=True, exist_ok=True)
    json_path = output_directory / f"{REPORT_ID}.json"
    html_path = output_directory / f"{REPORT_ID}.html"
    png_path = output_directory / f"{REPORT_ID}.png"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    html_path.write_text(render_html(report), encoding="utf-8", newline="\n")
    render_png(report, png_path)
    outputs = [_binding(path) for path in (html_path, png_path)]
    report["outputs"] = outputs
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return outputs
