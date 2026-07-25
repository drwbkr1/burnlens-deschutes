"""Build the repository-owned BurnLens portfolio reviewer experience."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from typing import Any


REPORT_ID = "BURNLENS-PORTFOLIO-REVIEWER-EXPERIENCE-2026-001"
REPORT_VERSION = "portfolio-reviewer-experience-v0.2.0"
SOFTWARE_VERSION = "0.51.0"
TASK_ISSUE = 560


class PortfolioReviewerExperienceError(ValueError):
    """Raised when portfolio inputs or output custody fail closed."""


@dataclass(frozen=True)
class BoundInput:
    path: str
    bytes: int
    sha256: str
    role: str


BOUND_INPUTS = (
    BoundInput(
        path=(
            "samples/labels/readiness/phase-two/"
            "SIX-EVENT-DATASET-SUFFICIENCY-2026-002.json"
        ),
        bytes=9429,
        sha256="88cbe6ae01af322d7f80ff8a76b3dce698c08b53394a7e68faec2f5cb198ef0a",
        role="verified replacement six-event sufficiency result and trace source",
    ),
    BoundInput(
        path=(
            "samples/labels/readiness/phase-two/"
            "SIX-EVENT-DATASET-SUFFICIENCY-2026-002.html"
        ),
        bytes=6357,
        sha256="0fbdfd85a8055b2b560c7aac4d35424693ee60761a5f00f6f1b2f804e894c326",
        role="verified replacement six-event sufficiency detail",
    ),
    BoundInput(
        path=(
            "samples/labels/readiness/phase-two/"
            "SIX-EVENT-DATASET-SUFFICIENCY-2026-002.png"
        ),
        bytes=101221,
        sha256="b20b3852d23185c2e0aa0f9b6cfd462b22eb98dbdbdaad5b8bb9bdeb43977761",
        role="verified replacement six-event sufficiency preview",
    ),
    BoundInput(
        path=(
            "samples/cross-event/phase-two/petes-lake/"
            "PETES-LAKE-SOURCE-FITNESS-2026-001.png"
        ),
        bytes=626846,
        sha256="4ed3870e37bf68db24805540f00614c5050c064b621ca3fc5e3c0ef244bf0d42",
        role="retained snow-dominated failure preview",
    ),
    BoundInput(
        path=(
            "docs/phase-two/objective-four/"
            "PETES_LAKE_MATERIAL_DEFER_DECISION.md"
        ),
        bytes=6050,
        sha256="6e0cb457261cc0ef48b86b15e8b21a83ec21c4b880990d83b0c79834a26c31e7",
        role="verified material-defer decision",
    ),
)


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _validate_bound_inputs(repository_root: Path) -> dict[str, Path]:
    resolved: dict[str, Path] = {}
    for item in BOUND_INPUTS:
        path = repository_root / item.path
        if not path.is_file():
            raise PortfolioReviewerExperienceError(f"bound input missing: {item.path}")
        if path.stat().st_size != item.bytes:
            raise PortfolioReviewerExperienceError(f"bound input size changed: {item.path}")
        if _digest(path) != item.sha256:
            raise PortfolioReviewerExperienceError(f"bound input hash changed: {item.path}")
        resolved[item.path] = path
    return resolved


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PortfolioReviewerExperienceError(f"invalid JSON input: {path}") from error
    if not isinstance(payload, dict):
        raise PortfolioReviewerExperienceError(f"JSON input must be an object: {path}")
    return payload


def build_report(
    *,
    repository_root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    """Validate exact evidence and build the public portfolio manifest."""
    repository_root = repository_root.resolve()
    inputs = _validate_bound_inputs(repository_root)
    readiness_path = inputs[BOUND_INPUTS[0].path]
    readiness = _load_json(readiness_path)

    expected = {
        "software_version": "0.50.0",
        "label_set_version": "owner-approved-prototype-region-labels-v0.5.0",
        "label_schema_version": "burn-scar-binary-region-label-schema-v0.3.0",
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "decision": (
            "PASS_SIX_EVENT_DATASET_SUFFICIENCY_"
            "AUTHORIZE_DATASET_SPLIT_QA_BASELINE_CHECKPOINT"
        ),
    }
    for key, value in expected.items():
        if readiness.get(key) != value:
            raise PortfolioReviewerExperienceError(f"readiness trace changed: {key}")

    inventory = readiness.get("inventory")
    if not isinstance(inventory, dict):
        raise PortfolioReviewerExperienceError("readiness inventory is missing")
    required_inventory = {
        "event_groups": 6,
        "owner_approved_regions": 12,
        "class_counts": {"background": 6, "burned": 6},
        "accepted_core_pixels": 287,
        "accepted_core_area_hectares": 11.48,
        "excluded_unknown_ring_pixels": 531,
        "balanced_review_roster_is_natural_prevalence": False,
    }
    for key, value in required_inventory.items():
        if inventory.get(key) != value:
            raise PortfolioReviewerExperienceError(f"readiness inventory changed: {key}")

    partition = readiness.get("partition_feasibility")
    if not isinstance(partition, dict) or partition.get("valid_assignments") != 54:
        raise PortfolioReviewerExperienceError("readiness split feasibility changed")
    gates = readiness.get("gate_results")
    if not isinstance(gates, dict) or len(gates) != 10:
        raise PortfolioReviewerExperienceError("readiness gate roster changed")
    if any(item.get("status") != "pass" for item in gates.values()):
        raise PortfolioReviewerExperienceError("a readiness gate is no longer passing")
    boundaries = readiness.get("boundaries")
    required_boundaries = {
        "dataset_created": False,
        "split_created": False,
        "baseline_created": False,
        "model_created": False,
        "training_authorized": False,
        "independent_ground_truth_claimed": False,
    }
    if not isinstance(boundaries, dict) or any(
        boundaries.get(key) != value for key, value in required_boundaries.items()
    ):
        raise PortfolioReviewerExperienceError("readiness boundary changed")

    if len(git_source_commit) != 40:
        raise PortfolioReviewerExperienceError("git source commit must be a full 40-character ID")
    if not run_id.strip():
        raise PortfolioReviewerExperienceError("run ID is required")

    return {
        "report_id": REPORT_ID,
        "report_version": REPORT_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "audience": "technical and technical-adjacent portfolio reviewers",
        "promise": (
            "Show how versioned wildfire imagery can move through a bounded "
            "computer-vision-to-GEOINT evidence workflow without hiding uncertainty."
        ),
        "target_version": readiness["target_version"],
        "aoi_version": readiness["aoi_version"],
        "label_schema_version": readiness["label_schema_version"],
        "label_set_version": readiness["label_set_version"],
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "review_path": [
            {
                "step": 1,
                "label": "See the strongest verified result",
                "target": "#result",
                "time": "45 seconds",
            },
            {
                "step": 2,
                "label": "Inspect a retained stop decision",
                "target": "#failure",
                "time": "45 seconds",
            },
            {
                "step": 3,
                "label": "Verify lineage and limitations",
                "target": "#trace",
                "time": "30 seconds",
            },
        ],
        "metrics": {
            "event_groups": inventory["event_groups"],
            "prototype_regions": inventory["owner_approved_regions"],
            "prototype_regions_by_class": inventory["class_counts"],
            "accepted_core_pixels": inventory["accepted_core_pixels"],
            "accepted_core_area_ha": inventory["accepted_core_area_hectares"],
            "excluded_unknown_ring_pixels": inventory[
                "excluded_unknown_ring_pixels"
            ],
            "valid_whole_event_assignments": partition["valid_assignments"],
            "readiness_gates_passed": len(gates),
        },
        "accepted_events": [
            event["fire_name"] for event in readiness["events"]
        ],
        "strongest_result": {
            "title": "Replacement six-event sufficiency passes",
            "decision": readiness["decision"],
            "run_id": readiness["run_id"],
            "git_source_commit": readiness["git_source_commit"],
            "software_version": readiness["software_version"],
            "detail_path": BOUND_INPUTS[1].path,
            "preview_path": BOUND_INPUTS[2].path,
        },
        "retained_failure": {
            "title": "Petes Lake stops before candidate generation",
            "decision": "DEFER_PETES_LAKE_DO_NOT_PROMOTE_SIXTH_EVENT",
            "run_id": "BL-2026-07-22-petes-lake-milestone-closeout-r001",
            "terminal_run_id": "BL-2026-07-22-petes-lake-nwi-context-r003",
            "git_checkpoint": "52310531ad0b8e6d07800fc752f7bf65b5fdea9a",
            "software_version": "0.45.0",
            "detail_path": BOUND_INPUTS[4].path,
            "preview_path": BOUND_INPUTS[3].path,
        },
        "source_roles": [
            "Sentinel-2 supplies optical evidence under recorded Copernicus attribution.",
            "BAER supplies field-informed preliminary prototype-positive evidence with program cautions.",
            "MTBS corroborates burned evidence under program-specific limits.",
            "RAVG modeled effects remain context and conservative exclusion only.",
            "No source product is treated as affirmative background truth without a separate route.",
        ],
        "limitations": [
            "Owner-approved prototype regions are not independent ground truth.",
            "The sufficiency pass authorizes only a separate dataset, split, QA, and baseline checkpoint.",
            "The accepted cores contain only 287 native 20-meter pixels.",
            "The balanced review roster does not estimate natural class prevalence.",
            "No dataset, split, baseline, model, accuracy, or inference output exists.",
            "BurnLens is not official, endorsed, field-validated, operational, or emergency-ready.",
        ],
        "bound_inputs": [
            {
                "path": item.path,
                "bytes": item.bytes,
                "sha256": item.sha256,
                "role": item.role,
            }
            for item in BOUND_INPUTS
        ],
        "warning": (
            "Experimental owner-approved prototype evidence. Not ground truth, "
            "official wildfire information, emergency guidance, field validation, "
            "a dataset, or a model. Official sources govern."
        ),
        "decision": (
            "PRESENT_VERIFIED_SIX_EVENT_SUFFICIENCY_"
            "KEEP_DATASET_MODEL_CLOSED"
        ),
    }


def _repo_href(path: str) -> str:
    return "../" + path.replace("\\", "/")


def render_html(report: dict[str, Any]) -> str:
    """Render the deterministic, dependency-free reviewer landing page."""
    metrics = report["metrics"]
    result = report["strongest_result"]
    failure = report["retained_failure"]
    review_steps = "".join(
        (
            f'<a class="step" href="{escape(step["target"])}">'
            f'<span>{step["step"]}</span><strong>{escape(step["label"])}</strong>'
            f'<small>{escape(step["time"])}</small></a>'
        )
        for step in report["review_path"]
    )
    source_items = "".join(f"<li>{escape(item)}</li>" for item in report["source_roles"])
    limitation_items = "".join(
        f"<li>{escape(item)}</li>" for item in report["limitations"]
    )
    events = "".join(f"<li>{escape(event)}</li>" for event in report["accepted_events"])
    trace_rows = "".join(
        (
            "<tr>"
            f"<th scope=\"row\">{escape(label)}</th>"
            f"<td><code>{escape(str(value if value is not None else 'null'))}</code></td>"
            "</tr>"
        )
        for label, value in (
            ("Repository commit", report["git_source_commit"]),
            ("Application version", report["software_version"]),
            ("Target version", report["target_version"]),
            ("AOI version", report["aoi_version"]),
            ("Label schema", report["label_schema_version"]),
            ("Prototype label set", report["label_set_version"]),
            ("Dataset version", report["dataset_version"]),
            ("Split version", report["split_version"]),
            ("Baseline version", report["baseline_version"]),
            ("Model version", report["model_version"]),
            ("Portfolio run", report["run_id"]),
        )
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="BurnLens verified CV-to-GEOINT portfolio evidence and limitations.">
<link rel="icon" href="data:,">
<title>BurnLens — evidence before claims</title>
<style>
:root{{--ink:#15221d;--muted:#52615a;--paper:#f5f0e7;--card:#fffdf8;--forest:#102c27;--teal:#08776d;--ember:#dc6d22;--line:#d8cec0;--focus:#ffbf47}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.58 system-ui,-apple-system,"Segoe UI",sans-serif}}a{{color:inherit}}a:focus-visible,summary:focus-visible{{outline:4px solid var(--focus);outline-offset:4px}}.skip{{position:absolute;left:-999px;top:1rem;background:white;padding:.7rem;z-index:9}}.skip:focus{{left:1rem}}header{{background:var(--forest);color:white}}nav{{max-width:1180px;margin:auto;display:flex;justify-content:space-between;align-items:center;gap:1rem;padding:1rem 1.25rem;border-bottom:1px solid #ffffff24}}nav a{{text-decoration:none}}nav ul{{display:flex;gap:1rem;list-style:none;margin:0;padding:0;font-size:.92rem}}.brand{{font-weight:800;letter-spacing:.08em}}.hero{{max-width:1180px;margin:auto;display:grid;grid-template-columns:1.35fr .65fr;gap:2rem;padding:5rem 1.25rem 4rem}}.eyebrow{{color:#9fd6ce;font-weight:750;letter-spacing:.09em;text-transform:uppercase}}h1{{font-size:clamp(2.7rem,6vw,5.8rem);line-height:.95;letter-spacing:-.055em;margin:.5rem 0 1.4rem;max-width:840px}}.lede{{font-size:1.2rem;color:#d8e8e3;max-width:750px}}.hero-note{{align-self:end;background:#ffffff10;border:1px solid #ffffff2b;border-radius:18px;padding:1.25rem}}.hero-note strong{{display:block;font-size:1.35rem;margin-bottom:.35rem}}main{{max-width:1180px;margin:auto;padding:0 1.25rem 5rem}}.warning{{margin:-1.6rem 0 2rem;background:#fff6e9;border-left:8px solid var(--ember);border-radius:14px;padding:1.1rem 1.2rem;font-weight:700}}.review-path{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:2rem 0 4rem}}.step{{display:grid;grid-template-columns:auto 1fr;gap:.25rem .8rem;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:1rem;text-decoration:none}}.step span{{grid-row:1/3;display:grid;place-items:center;width:2.3rem;height:2.3rem;border-radius:50%;background:var(--teal);color:white;font-weight:800}}.step small{{color:var(--muted)}}section{{scroll-margin-top:1rem;margin:4.5rem 0}}.section-head{{max-width:760px;margin-bottom:1.5rem}}.section-head p{{color:var(--muted)}}h2{{font-size:clamp(2rem,4vw,3.6rem);line-height:1.05;letter-spacing:-.035em;margin:.3rem 0}}h3{{font-size:1.35rem;margin:.25rem 0}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}}.metric{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:1.15rem}}.metric strong{{display:block;font-size:2.2rem;color:var(--teal);line-height:1}}.evidence{{display:grid;grid-template-columns:1.2fr .8fr;gap:1.4rem;background:var(--card);border:1px solid var(--line);border-radius:22px;overflow:hidden}}.evidence img{{width:100%;height:100%;min-height:360px;object-fit:cover;object-position:top;border-right:1px solid var(--line)}}.evidence-copy{{padding:1.4rem 1.4rem 1.4rem 0}}.pill{{display:inline-block;background:#e5f2ee;color:#075b54;border-radius:99px;padding:.25rem .65rem;font-size:.82rem;font-weight:800;text-transform:uppercase;letter-spacing:.04em}}.pill.stop{{background:#fbe6d8;color:#8a3d0d}}.button-row{{display:flex;flex-wrap:wrap;gap:.7rem;margin-top:1.2rem}}.button{{display:inline-block;background:var(--forest);color:white;border-radius:10px;padding:.7rem 1rem;text-decoration:none;font-weight:750}}.button.secondary{{background:transparent;color:var(--forest);border:1px solid var(--forest)}}.events{{display:grid;grid-template-columns:repeat(6,1fr);gap:.6rem;list-style:none;padding:0}}.events li{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:.75rem;text-align:center;font-weight:750}}.split{{display:grid;grid-template-columns:1fr 1fr;gap:1.4rem}}.panel{{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:1.3rem}}li+li{{margin-top:.45rem}}table{{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line)}}th,td{{padding:.8rem;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}}th{{width:32%}}code{{font:0.88rem/1.45 ui-monospace,SFMono-Regular,Consolas,monospace;overflow-wrap:anywhere}}details{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:1rem;margin-top:1rem}}summary{{cursor:pointer;font-weight:800}}footer{{background:#e9e1d5;padding:2rem 1.25rem}}footer div{{max-width:1180px;margin:auto}}@media(max-width:820px){{nav ul{{display:none}}.hero,.evidence,.split{{grid-template-columns:1fr}}.hero{{padding-top:3.2rem}}.evidence img{{border-right:0;border-bottom:1px solid var(--line);min-height:auto}}.evidence-copy{{padding:1.2rem}}.metrics{{grid-template-columns:1fr 1fr}}.review-path{{grid-template-columns:1fr}}.events{{grid-template-columns:repeat(3,1fr)}}th{{width:38%}}}}@media(max-width:430px){{main,nav,.hero{{padding-left:.8rem;padding-right:.8rem}}.metrics{{grid-template-columns:1fr 1fr}}.metric strong{{font-size:1.75rem}}.events{{grid-template-columns:1fr 1fr}}th,td{{display:block;width:100%}}th{{border-bottom:0;padding-bottom:.1rem}}td{{padding-top:.1rem}}}}@media(prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}@media print{{nav,.review-path,.button-row{{display:none}}body{{background:white}}section{{break-inside:avoid}}}}
</style>
</head>
<body>
<a class="skip" href="#main">Skip to evidence</a>
<header>
<nav aria-label="Primary"><a class="brand" href="#top">BURNLENS</a><ul><li><a href="#result">Result</a></li><li><a href="#failure">Failure</a></li><li><a href="#method">Method</a></li><li><a href="#trace">Trace</a></li></ul></nav>
<div class="hero" id="top"><div><p class="eyebrow">Experimental CV-to-GEOINT evidence</p><h1>Evidence before claims.</h1><p class="lede">{escape(report["promise"])}</p></div><aside class="hero-note" aria-label="Current posture"><strong>Phase Two evidence</strong>Six-event sufficiency passes. Dataset and model gates remain closed.</aside></div>
</header>
<main id="main">
<p class="warning">{escape(report["warning"])}</p>
<div class="review-path" aria-label="Two-minute reviewer path">{review_steps}</div>
<section aria-labelledby="proof-heading"><div class="section-head"><p class="eyebrow">What is actually proven</p><h2 id="proof-heading">A complete evidence chain, with restraint.</h2><p>BurnLens preserves source roles, uncertainty, owner decisions, and failure states. Every readiness gate passes, while training remains unauthorized.</p></div><div class="metrics"><div class="metric"><strong>{metrics["event_groups"]}</strong>complete event groups</div><div class="metric"><strong>{metrics["prototype_regions"]}</strong>prototype regions</div><div class="metric"><strong>{metrics["valid_whole_event_assignments"]}</strong>valid whole-event splits</div><div class="metric"><strong>0</strong>datasets or models</div></div><ol class="events" aria-label="Accepted event groups">{events}</ol></section>
<section id="result" aria-labelledby="result-heading"><div class="section-head"><p class="eyebrow">Strongest verified result</p><h2 id="result-heading">{escape(result["title"])}</h2><p>The exact candidate passes all {metrics["readiness_gates_passed"]} source, custody, schema, quality, uncertainty, leakage, reproducibility, evaluation, review, claims, and privacy gates.</p></div><article class="evidence"><a href="{_repo_href(result["preview_path"])}"><img src="{_repo_href(result["preview_path"])}" alt="Replacement six-event sufficiency evidence showing all ten passing readiness gates"></a><div class="evidence-copy"><span class="pill">Verified result</span><h3>Candidate ready for the next data checkpoint</h3><p>Six burned and six background regions span six events. All 531 unknown-ring pixels remain excluded. The pass authorizes dataset, split, QA, and baseline work, not training.</p><p><code>{escape(result["run_id"])}</code></p><div class="button-row"><a class="button" href="{_repo_href(result["detail_path"])}">Open detailed result</a><a class="button secondary" href="../docs/phase-two/objective-five/REPLACEMENT_SIX_EVENT_DATASET_SUFFICIENCY_DECISION.md">Read decision</a></div></div></article></section>
<section id="failure" aria-labelledby="failure-heading"><div class="section-head"><p class="eyebrow">Reliability is visible</p><h2 id="failure-heading">{escape(failure["title"])}</h2><p>BurnLens keeps a snow-dominated source failure and a terminal partial-custody stop instead of manufacturing a sixth event from incomplete evidence.</p></div><article class="evidence"><a href="{_repo_href(failure["preview_path"])}"><img src="{_repo_href(failure["preview_path"])}" alt="Petes Lake snow-dominated source-fitness failure evidence"></a><div class="evidence-copy"><span class="pill stop">Retained stop</span><h3>Defer is a product decision</h3><p>Seven valid assets remain evidence. One failed asset and four unexecuted assets cannot become a complete scientific package. Candidate generation never starts.</p><p><code>{escape(failure["terminal_run_id"])}</code></p><div class="button-row"><a class="button" href="{_repo_href(failure["detail_path"])}">Read material-defer decision</a><a class="button secondary" href="../records/prompt-build-log/2026-07-21-p2o4-t33.md">Inspect milestone log</a></div></div></article></section>
<section id="method" aria-labelledby="method-heading"><div class="section-head"><p class="eyebrow">Method and boundaries</p><h2 id="method-heading">Different sources have different jobs.</h2><p>Source precedence is part of the product. Context is not relabeled as truth, and ambiguous pixels stay unknown.</p></div><div class="split"><div class="panel"><h3>Source roles</h3><ul>{source_items}</ul></div><div class="panel"><h3>What remains unproven</h3><ul>{limitation_items}</ul></div></div></section>
<section id="trace" aria-labelledby="trace-heading"><div class="section-head"><p class="eyebrow">Lineage</p><h2 id="trace-heading">Null is a valid version.</h2><p>Every displayed claim binds to the current portfolio build and the evidence-bearing run. Missing analytical stages stay explicit.</p></div><table><tbody>{trace_rows}</tbody></table><details><summary>Exact bound inputs</summary><ul>{''.join(f'<li><code>{escape(item["path"])}</code> — {item["bytes"]:,} bytes — <code>{escape(item["sha256"])}</code></li>' for item in report["bound_inputs"])}</ul></details><div class="button-row"><a class="button" href="{REPORT_ID}.json">Open machine-readable manifest</a><a class="button secondary" href="../docs/case-study/BURNLENS_CASE_STUDY.md">Read full case study</a><a class="button secondary" href="README.md">Reviewer quickstart</a></div></section>
</main>
<footer><div><strong>BurnLens {escape(report["software_version"])}</strong><p>Run <code>{escape(report["run_id"])}</code> · commit <code>{escape(report["git_source_commit"])}</code> · issue #{report["task_issue"]}. Local/offline repository evidence; no deployed application.</p></div></footer>
</body>
</html>
"""
    return html


def write_outputs_no_overwrite(
    *,
    report: dict[str, Any],
    output_directory: Path,
) -> list[dict[str, Any]]:
    """Write JSON and HTML atomically enough for no-overwrite local generation."""
    output_directory = output_directory.resolve()
    output_directory.mkdir(parents=True, exist_ok=True)
    json_path = output_directory / f"{REPORT_ID}.json"
    html_path = output_directory / f"{REPORT_ID}.html"
    for path in (json_path, html_path):
        if path.exists():
            raise PortfolioReviewerExperienceError(f"refusing to overwrite: {path}")

    html_bytes = render_html(report).encode("utf-8")
    public_report = dict(report)
    public_report["outputs"] = [
        {
            "path": html_path.name,
            "bytes": len(html_bytes),
            "sha256": sha256(html_bytes).hexdigest(),
            "media_type": "text/html",
        }
    ]
    json_bytes = (
        json.dumps(public_report, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")

    json_path.write_bytes(json_bytes)
    html_path.write_bytes(html_bytes)
    return [
        {
            "path": json_path.name,
            "bytes": len(json_bytes),
            "sha256": sha256(json_bytes).hexdigest(),
        },
        {
            "path": html_path.name,
            "bytes": len(html_bytes),
            "sha256": sha256(html_bytes).hexdigest(),
        },
    ]
