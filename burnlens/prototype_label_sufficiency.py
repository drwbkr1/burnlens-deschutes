from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
from html import escape
import json
import math
from pathlib import Path
import statistics
import subprocess
from typing import Any

from PIL import Image, ImageDraw, ImageFont


REPORT_ID = "PROTOTYPE-LABEL-SUFFICIENCY-2026-001"
REPORT_VERSION = "prototype-label-sufficiency-v0.1.0"
PROTOCOL_VERSION = "prototype-label-dataset-readiness-v0.1.0"
SOFTWARE_VERSION = "0.27.0"
LABEL_SET_VERSION = "owner-approved-prototype-labels-v0.1.0"
EXPECTED_PRIVATE_REPORT = "OWNER-RESPONSE-INTAKE-PRIVATE-2026-001"
DECISION = "REMEDIATE_LABEL_COVERAGE_BEFORE_DATASET_SPLIT_BASELINE_MODEL"


class PrototypeLabelSufficiencyError(RuntimeError):
    pass


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PrototypeLabelSufficiencyError(f"invalid JSON input: {path.name}") from exc
    if not isinstance(value, dict):
        raise PrototypeLabelSufficiencyError(f"JSON object required: {path.name}")
    return value


def _binding(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {"path": path.name, "bytes": len(payload), "sha256": sha256(payload).hexdigest()}


def _assert_private_input(repository_root: Path, path: Path) -> None:
    try:
        relative = path.resolve().relative_to(repository_root.resolve()).as_posix()
    except ValueError as exc:
        raise PrototypeLabelSufficiencyError("private intake must stay repository-local") from exc
    ignored = subprocess.run(
        ["git", "-C", str(repository_root), "check-ignore", "--quiet", "--no-index", "--", relative],
        check=False,
    )
    if ignored.returncode != 0:
        raise PrototypeLabelSufficiencyError("private intake must be ignored")
    tracked = subprocess.run(
        ["git", "-C", str(repository_root), "ls-files", "--error-unmatch", "--", relative],
        check=False,
        capture_output=True,
    )
    if tracked.returncode == 0:
        raise PrototypeLabelSufficiencyError("private intake must remain untracked")


def _pair_distances(points: list[tuple[float, float]]) -> list[float]:
    return [math.dist(left, right) for index, left in enumerate(points) for right in points[index + 1 :]]


def _event_candidate_counts(darlene: dict[str, Any], cross_event: dict[str, Any]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    darlene_states = {item["state"]: int(item["pixels"]) for item in darlene["summary"]["states"]}
    result["event-darlene3-or-2024"] = {
        "background": darlene_states["background-candidate"],
        "burned": darlene_states["burned"],
    }
    for event in cross_event["events"]:
        states = {item["state"]: int(item["pixels"]) for item in event["summary"]["states"]}
        result[event["event_group_id"]] = {
            "background": states["background-candidate"],
            "burned": states["burned"],
        }
    return result


def _source_signature(unit: dict[str, Any]) -> str:
    evidence = unit["current_reference_evidence"]
    programs = sorted({item["program"] for item in evidence["categorical"]})
    if evidence.get("baer_dnbr") is not None:
        programs.append("BAER_DNBR_CONTEXT")
    return "+".join(programs)


def build_report(
    repository_root: Path,
    surface_path: Path,
    private_intake_path: Path,
    darlene_proposal_path: Path,
    cross_event_proposal_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    surface = _read_json(surface_path)
    private = _read_json(private_intake_path)
    darlene = _read_json(darlene_proposal_path)
    cross_event = _read_json(cross_event_proposal_path)

    if private.get("report_id") != EXPECTED_PRIVATE_REPORT:
        raise PrototypeLabelSufficiencyError("unexpected private intake report")
    if private.get("label_set_version") != LABEL_SET_VERSION:
        raise PrototypeLabelSufficiencyError("prototype label-set version mismatch")
    if not private.get("notes_copied") is False:
        raise PrototypeLabelSufficiencyError("private intake must not copy owner notes")
    if any(private.get(key) for key in ("dataset_created", "split_created", "baseline_created", "model_created")):
        raise PrototypeLabelSufficiencyError("upstream analytical versions must remain absent")
    _assert_private_input(repository_root, private_intake_path)

    surface_units = {unit["sample_id"]: unit for unit in surface["units"]}
    approved_private = [unit for unit in private["units"] if unit["prototype_target"] is not None]
    if len(approved_private) != 24:
        raise PrototypeLabelSufficiencyError("expected exactly 24 prototype labels")
    if len({unit["sample_id"] for unit in approved_private}) != 24:
        raise PrototypeLabelSufficiencyError("prototype unit identities must be unique")
    try:
        approved = [surface_units[unit["sample_id"]] for unit in approved_private]
    except KeyError as exc:
        raise PrototypeLabelSufficiencyError("prototype unit missing from surface") from exc

    candidate_counts = _event_candidate_counts(darlene, cross_event)
    event_units: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for unit in approved:
        event_units[unit["event_group_id"]].append(unit)
    if set(event_units) != set(candidate_counts):
        raise PrototypeLabelSufficiencyError("event binding mismatch")

    events: list[dict[str, Any]] = []
    for event_id in sorted(event_units):
        units = event_units[event_id]
        class_counts = Counter(unit["candidate_label"] for unit in units)
        if class_counts != {"background": 4, "burned": 4}:
            raise PrototypeLabelSufficiencyError("expected four prototype labels per event and class")
        geometry: dict[str, Any] = {}
        for label in ("background", "burned"):
            points = [tuple(map(float, unit["pixel_center_utm10n"])) for unit in units if unit["candidate_label"] == label]
            distances = _pair_distances(points)
            xs = [point[0] for point in points]
            ys = [point[1] for point in points]
            geometry[label] = {
                "minimum_pair_distance_m": round(min(distances), 3),
                "median_pair_distance_m": round(statistics.median(distances), 3),
                "maximum_pair_distance_m": round(max(distances), 3),
                "x_span_m": round(max(xs) - min(xs), 3),
                "y_span_m": round(max(ys) - min(ys), 3),
            }
        natural_total = sum(candidate_counts[event_id].values())
        reviewed_total = len(units)
        events.append(
            {
                "event_group_id": event_id,
                "prototype_label_counts": dict(sorted(class_counts.items())),
                "candidate_domain_counts": candidate_counts[event_id],
                "prototype_fraction_of_candidate_domain_percent": round(100 * reviewed_total / natural_total, 6),
                "candidate_domain_burn_share_percent": round(100 * candidate_counts[event_id]["burned"] / natural_total, 4),
                "prototype_burn_share_percent": 50.0,
                "source_regime": _source_signature(units[0]),
                "geometry": geometry,
            }
        )

    total_candidate = sum(sum(counts.values()) for counts in candidate_counts.values())
    source_regimes = {event["source_regime"] for event in events}
    if len(source_regimes) != 3:
        raise PrototypeLabelSufficiencyError("expected one distinct current-reference regime per event")

    private_binding = _binding(private_intake_path)
    private_binding.pop("path")
    report = {
        "report_id": REPORT_ID,
        "report_version": REPORT_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 443,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": SOFTWARE_VERSION,
        "bindings": {
            "owner_surface": _binding(surface_path),
            "private_owner_intake": {**private_binding, "committed": False, "ignored": True},
            "darlene_proposal": _binding(darlene_proposal_path),
            "cross_event_proposal": _binding(cross_event_proposal_path),
        },
        "provenance": {
            "aoi_version": "aoi-darlene3-model-v0.2.0",
            "target_version": "target-burn-scar-v0.2.0",
            "label_schema_version": "burn-scar-five-state-schema-v0.1.0",
            "label_set_version": LABEL_SET_VERSION,
            "dataset_version": None,
            "split_version": None,
            "baseline_version": None,
            "model_version": None,
            "source_precedence_id": "SOURCE-PRECEDENCE-2026-010",
            "terms_review_id": "TERMS-2026-012",
        },
        "inventory": {
            "prototype_labels": 24,
            "prototype_class_counts": {"background": 12, "burned": 12},
            "event_groups": 3,
            "labels_per_event": 8,
            "labels_per_event_class": 4,
            "candidate_domain_pixels": total_candidate,
            "prototype_fraction_of_candidate_domain_percent": round(100 * 24 / total_candidate, 6),
            "label_granularity": "reviewed center pixels only; no contiguous mask or accepted patch labels",
        },
        "events": events,
        "partition_feasibility": {
            "nonempty_train_validation_test_assignments": 6,
            "event_groups_per_role_in_every_assignment": {"train": 1, "validation": 1, "test": 1},
            "replicated_event_evidence_per_role": False,
            "source_regime_confounded_with_event": True,
            "source_regime_count": len(source_regimes),
        },
        "selection_and_evaluation": {
            "proposal_stratified_selection": True,
            "owner_saw_optical_and_current_reference_evidence": True,
            "independent_ground_truth": False,
            "prevalence_or_calibration_inference_supported": False,
            "per_pixel_segmentation_training_supported": False,
            "per_pixel_segmentation_evaluation_supported": False,
            "permitted_role": "prototype audit evidence and future labeling seed only",
        },
        "gate_results": {
            "exact_lineage": "PASS_EXACT_24_LABEL_LINEAGE",
            "spatial_dispersion": "PASS_DISTINCT_CENTERS_NOT_SUFFICIENCY",
            "label_granularity": "BLOCK_SINGLE_PIXELS_NO_CONTIGUOUS_MASKS",
            "coverage": "BLOCK_24_OF_189541_CANDIDATE_PIXELS",
            "partition": "BLOCK_3_EVENTS_ONE_PER_ROLE_NO_REPLICATION",
            "distribution": "BLOCK_BALANCED_AUDIT_SAMPLE_NOT_PREVALENCE",
            "evaluation_independence": "BLOCK_PROPOSAL_STRATIFIED_DISCLOSED_EVIDENCE",
        },
        "minimum_remediation": [
            "create reviewed contiguous burned/background/unknown regions rather than expanding point decisions",
            "add event and source-regime diversity so train, validation, and test each have replicated independent groups",
            "preserve natural prevalence and report a separate balanced audit sample",
            "reserve evidence not used for proposal selection or owner presentation for independent evaluation",
            "repeat overlap, duplication, leakage, terms, and uncertainty gates before dataset creation",
        ],
        "boundaries": {
            "prototype_points_expanded_to_masks": False,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
            "accuracy_claimed": False,
            "ground_truth_or_field_validation_claimed": False,
        },
        "decision": DECISION,
        "warning": "Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Official sources govern.",
    }
    return report


def render_html(report: dict[str, Any]) -> str:
    inventory = report["inventory"]
    gates = report["gate_results"]
    rows = "".join(
        f"<tr><th>{escape(name.replace('_', ' ').title())}</th><td class='{('pass' if value.startswith('PASS') else 'block')}'>{escape(value)}</td></tr>"
        for name, value in gates.items()
    )
    events = "".join(
        "<tr>"
        f"<td>{escape(event['event_group_id'])}</td>"
        f"<td>{event['candidate_domain_counts']['background']:,}</td>"
        f"<td>{event['candidate_domain_counts']['burned']:,}</td>"
        f"<td>{event['prototype_fraction_of_candidate_domain_percent']:.6f}%</td>"
        f"<td>{event['candidate_domain_burn_share_percent']:.4f}%</td>"
        f"<td>{escape(event['source_regime'])}</td>"
        "</tr>"
        for event in report["events"]
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens prototype-label sufficiency</title><style>
:root{{--ink:#123f3a;--muted:#526763;--paper:#f5f0e6;--card:#fff;--line:#b9ccc8;--block:#9b3f24;--pass:#14665d}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.45 system-ui,sans-serif}}header{{background:#103f39;color:white;padding:42px max(24px,5vw)}}main{{max-width:1180px;margin:auto;padding:32px 24px 56px}}h1{{margin:0 0 8px;font-size:clamp(2rem,5vw,3.2rem)}}.metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}}.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px}}.big{{font-size:2.4rem}}table{{width:100%;border-collapse:collapse;background:white;margin:18px 0}}th,td{{text-align:left;padding:12px;border-bottom:1px solid #d8e1df;vertical-align:top}}.pass{{color:var(--pass);font-weight:700}}.block{{color:var(--block);font-weight:700}}.scroll{{overflow:auto}}code{{overflow-wrap:anywhere}}@media(max-width:760px){{.metrics{{grid-template-columns:repeat(2,minmax(0,1fr))}}th,td{{min-width:150px}}}}@media(max-width:420px){{.metrics{{grid-template-columns:1fr}}}}
</style></head><body><header><h1>Prototype-label sufficiency</h1><p>24 owner-approved points · dataset and split readiness gate</p></header><main>
<section class="metrics"><div class="card"><div class="big">24</div>prototype labels</div><div class="card"><div class="big">3</div>event groups</div><div class="card"><div class="big">{inventory['candidate_domain_pixels']:,}</div>candidate pixels</div><div class="card"><div class="big">{inventory['prototype_fraction_of_candidate_domain_percent']:.6f}%</div>point coverage</div></section>
<h2>Gate result</h2><table>{rows}</table>
<h2>Event evidence</h2><div class="scroll"><table><thead><tr><th>Event</th><th>Candidate background</th><th>Candidate burned</th><th>Reviewed point fraction</th><th>Candidate burn share</th><th>Reference regime</th></tr></thead><tbody>{events}</tbody></table></div>
<div class="card"><h2>Decision</h2><p><code>{escape(report['decision'])}</code></p><p>Distinct reviewed centers are useful audit evidence, but single points, one event per split role, proposal-stratified selection, and source-regime confounding block a segmentation dataset and evaluation.</p></div>
<p>Trace: source <code>{escape(report['git_source_commit'])}</code> · BurnLens <code>{SOFTWARE_VERSION}</code> · label set <code>{LABEL_SET_VERSION}</code> · run <code>{escape(report['run_id'])}</code> · dataset/split/baseline/model none.</p><p>{escape(report['warning'])}</p>
</main></body></html>"""


def render_png(report: dict[str, Any], path: Path) -> None:
    image = Image.new("RGB", (1800, 1200), "#f5f0e6")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=28)
    title = ImageFont.load_default(size=48)
    big = ImageFont.load_default(size=44)
    draw.rectangle((0, 0, 1800, 180), fill="#103f39")
    draw.text((70, 45), "BurnLens prototype-label sufficiency", fill="white", font=title)
    draw.text((70, 112), "24 owner-approved points · dataset and split readiness gate", fill="#c8ddd8", font=font)
    metrics = [("24", "prototype labels"), ("3", "event groups"), ("189,541", "candidate pixels"), ("0.012662%", "point coverage")]
    for index, (value, label) in enumerate(metrics):
        x = 70 + index * 420
        draw.rounded_rectangle((x, 230, x + 360, 380), radius=16, fill="white", outline="#b9ccc8", width=2)
        draw.text((x + 24, 258), value, fill="#123f3a", font=big)
        draw.text((x + 24, 326), label, fill="#526763", font=font)
    draw.text((70, 430), "Readiness gates", fill="#123f3a", font=big)
    y = 500
    for name, value in report["gate_results"].items():
        passed = value.startswith("PASS")
        draw.rounded_rectangle((70, y, 1730, y + 72), radius=12, fill="white", outline="#d1ddda", width=2)
        draw.text((96, y + 20), name.replace("_", " ").title(), fill="#123f3a", font=font)
        draw.text((570, y + 20), value, fill="#14665d" if passed else "#9b3f24", font=font)
        y += 86
    draw.text((70, 1125), "Decision: remediate label coverage before dataset, split, baseline, or model work.", fill="#7f3524", font=font)
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
