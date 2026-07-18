"""Build an offline owner review surface for the six exact region candidates.

This surface collects no response while it is built. It binds immutable public
pilot evidence and exports yes/no/uncertain response bytes for later intake.
"""

from __future__ import annotations

from hashlib import sha256
from html import escape
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont
import rasterio

import burnlens


SURFACE_ID = "REGION-OWNER-REVIEW-SURFACE-2026-001"
SURFACE_VERSION = "region-owner-review-surface-v0.1.0"
RESPONSE_SCHEMA_VERSION = "burnlens-region-owner-review-response-v0.1.0"
PILOT_ID = "REGION-CANDIDATE-PILOT-2026-001"
PILOT_REPORT_VERSION = "no-promotion-region-candidate-pilot-v0.1.0"
EXPECTED_PILOT_RUN = "BL-2026-07-18-region-candidate-pilot-r006"
EXPECTED_PILOT_SHA256 = "1db602a721373f29f31f9d720ea9871b99d6e391e598236681a9cb438a51b55f"
ALLOWED_DECISIONS = ("yes", "no", "uncertain")
WARNING = (
    "Experimental BurnLens candidate review. Not a label, dataset, ground truth, "
    "official wildfire information, or emergency guidance. Official sources govern."
)


class RegionOwnerReviewSurfaceError(RuntimeError):
    """Raised when a frozen binding or output contract fails."""


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _binding(path: Path, **extra: Any) -> dict[str, Any]:
    value = {"path": path.name, "bytes": path.stat().st_size, "sha256": _sha256(path)}
    value.update(extra)
    return value


def _write_text(path: Path, text: str) -> None:
    if path.exists():
        raise RegionOwnerReviewSurfaceError(f"refusing to overwrite {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def _verify_raster(path: Path, candidate: dict[str, Any]) -> dict[str, Any]:
    with rasterio.open(path) as dataset:
        values = dataset.read()[0]
        tags = dataset.tags()
        if dataset.crs is None or dataset.crs.to_epsg() != 32610:
            raise RegionOwnerReviewSurfaceError(f"{path.name} CRS changed")
        if set(int(value) for value in set(values.ravel())) - {0, 1, 2}:
            raise RegionOwnerReviewSurfaceError(f"{path.name} class domain changed")
        if int((values == 1).sum()) != candidate["core_pixels"]:
            raise RegionOwnerReviewSurfaceError(f"{path.name} core count changed")
        if int((values == 2).sum()) != candidate["unknown_ring_pixels"]:
            raise RegionOwnerReviewSurfaceError(f"{path.name} ring count changed")
        if tags.get("region_label_created") != "false" or tags.get("dataset_created") != "false":
            raise RegionOwnerReviewSurfaceError(f"{path.name} no-promotion tags changed")
        return {
            "crs": "EPSG:32610",
            "width": dataset.width,
            "height": dataset.height,
            "transform": list(dataset.transform)[:6],
            "nodata": dataset.nodata,
            "class_domain": {"0": "outside candidate", "1": "candidate core", "2": "unknown ring"},
        }


def _response_template(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "response_schema_version": RESPONSE_SCHEMA_VERSION,
        "surface_id": SURFACE_ID,
        "surface_run_id": report["run_id"],
        "pilot_report_sha256": report["input_bindings"]["pilot_report"]["sha256"],
        "completed": False,
        "review_started_at_utc": None,
        "review_completed_at_utc": None,
        "owner": {"attestation": False},
        "responses": [
            {
                "candidate_id": item["candidate_id"],
                "candidate_raster_sha256": item["candidate_raster_sha256"],
                "decision": None,
                "notes": "",
            }
            for item in report["candidates"]
        ],
    }


def build_surface(repository_root: Path, generated_at_utc: str, run_id: str, git_source_commit: str) -> tuple[dict[str, Any], Path]:
    pilot_path = repository_root / "samples/labels/pilot/phase-two" / f"{PILOT_ID}.json"
    pilot_png = pilot_path.with_suffix(".png")
    if _sha256(pilot_path) != EXPECTED_PILOT_SHA256:
        raise RegionOwnerReviewSurfaceError("pilot report bytes changed")
    pilot = json.loads(pilot_path.read_text(encoding="utf-8"))
    if pilot.get("report_id") != PILOT_ID or pilot.get("report_version") != PILOT_REPORT_VERSION:
        raise RegionOwnerReviewSurfaceError("pilot identity changed")
    if pilot.get("run_id") != EXPECTED_PILOT_RUN or pilot.get("summary", {}).get("candidate_count") != 6:
        raise RegionOwnerReviewSurfaceError("pilot run or candidate count changed")
    if pilot.get("summary", {}).get("owner_region_responses") != 0 or pilot.get("summary", {}).get("owner_approved_region_labels") != 0:
        raise RegionOwnerReviewSurfaceError("pilot no-promotion state changed")
    outputs = {item["path"]: item for item in pilot.get("outputs", [])}
    candidates: list[dict[str, Any]] = []
    for index, item in enumerate(pilot["candidates"], start=1):
        expected_id = f"RCP-{index:03d}"
        if item.get("candidate_id") != expected_id:
            raise RegionOwnerReviewSurfaceError("candidate order changed")
        raster_name = item["candidate_raster"]
        raster_path = pilot_path.parent / raster_name
        binding = outputs.get(raster_name)
        if binding is None or binding["bytes"] != raster_path.stat().st_size or binding["sha256"] != _sha256(raster_path):
            raise RegionOwnerReviewSurfaceError(f"{raster_name} binding changed")
        raster_contract = _verify_raster(raster_path, item)
        candidates.append({
            "candidate_id": expected_id,
            "event_group_id": item["event_group_id"],
            "fire_name": item["fire_name"],
            "proposed_class": item["candidate_class"],
            "core_pixels": item["core_pixels"],
            "core_area_ha": item["core_area_ha"],
            "unknown_ring_pixels": item["unknown_ring_pixels"],
            "dnbr_interval": item["dnbr_interval"],
            "reference_kind": item["reference_context"]["kind"],
            "candidate_raster": raster_name,
            "candidate_raster_bytes": binding["bytes"],
            "candidate_raster_sha256": binding["sha256"],
            "raster_contract": raster_contract,
            "evidence_image": f"{SURFACE_ID}-{expected_id}.png",
            "owner_decision": None,
            "promotion_status": "blocked pending exact owner response and later reproducibility/source/quality/leakage gates",
        })
    if _sha256(pilot_png) != outputs[pilot_png.name]["sha256"]:
        raise RegionOwnerReviewSurfaceError("pilot evidence image changed")
    report = {
        "report_id": SURFACE_ID,
        "report_version": SURFACE_VERSION,
        "response_schema_version": RESPONSE_SCHEMA_VERSION,
        "software_version": burnlens.__version__,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "input_bindings": {
            "pilot_report": {"report_id": PILOT_ID, "run_id": pilot["run_id"], "bytes": pilot_path.stat().st_size, "sha256": _sha256(pilot_path)},
            "pilot_evidence_png": {"bytes": pilot_png.stat().st_size, "sha256": _sha256(pilot_png)},
        },
        "source_records": pilot["source_records"],
        "terms_records": pilot["terms_records"],
        "review_records": ["PRECHECK-2026-028", "SOURCE-PRECEDENCE-2026-012", "USE_BOUNDARY-2026-026"],
        "candidates": candidates,
        "decision_contract": {
            "yes": "necessary but insufficient; later reproducibility, source, quality, terms, and event-level leakage gates remain mandatory",
            "no": "excluded from region-label promotion",
            "uncertain": "excluded with uncertainty preserved",
            "prior_point_decisions_inherited": False,
        },
        "summary": {"candidate_count": 6, "owner_region_responses": 0, "owner_approved_region_labels": 0, "dataset_count": 0, "model_count": 0},
        "claim_boundaries": {
            "owner_region_responses_collected": False,
            "region_labels_created": False,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
            "independent_ground_truth_inter_rater_field_official_or_operational_claimed": False,
        },
        "warning": WARNING,
        "decision": "SURFACE_READY_FOR_OWNER_REGION_REVIEW_KEEP_RESPONSE_INTAKE_SEPARATE",
        "next_gate": "Validate exact reconstruction and real browser interaction; collect an actual owner response only through a later controlled workflow.",
    }
    return report, pilot_png


def _render_evidence_pages(report: dict[str, Any], pilot_png: Path, output_directory: Path) -> list[Path]:
    source = Image.open(pilot_png).convert("RGB")
    if source.size != (1800, 1960):
        raise RegionOwnerReviewSurfaceError("pilot evidence dimensions changed")
    paths: list[Path] = []
    for index, candidate in enumerate(report["candidates"]):
        top = 230 + index * 285
        crop = source.crop((45, top, 1755, top + 270))
        path = output_directory / candidate["evidence_image"]
        crop.save(path, format="PNG", optimize=False)
        paths.append(path)
    return paths


def _render_overview(report: dict[str, Any], pages: list[Path], path: Path) -> None:
    canvas = Image.new("RGB", (1800, 2050), "#f4f0e8")
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 1800, 220), fill="#132a26")
    draw.text((60, 38), "BurnLens owner region review surface", fill="white", font=_font(34))
    draw.text((60, 92), "6 exact candidates / yes-no-uncertain / 0 responses / 0 labels", fill="#c6ddd6", font=_font(22))
    draw.text((60, 142), WARNING, fill="#f2c48c", font=_font(17))
    for index, page in enumerate(pages):
        canvas.paste(Image.open(page).convert("RGB"), (45, 245 + index * 295))
    draw.text((60, 2020), "A later exact response-intake checkpoint must validate any completed export.", fill="#7f3524", font=_font(16))
    canvas.save(path, format="PNG", optimize=False)


def _render_html(report: dict[str, Any], template: dict[str, Any]) -> str:
    cards = []
    for item in report["candidates"]:
        choices = "".join(
            f'<label><input type="radio" name="decision-{escape(item["candidate_id"])}" value="{value}"> {value}</label>'
            for value in ALLOWED_DECISIONS
        )
        cards.append(f'''<article class="candidate" data-candidate="{escape(item['candidate_id'])}" data-raster-hash="{item['candidate_raster_sha256']}">
<div class="candidate-head"><div><p class="eyebrow">{escape(item['candidate_id'])} / {escape(item['fire_name'])}</p><h2>Is this exact region a usable prototype {escape(item['proposed_class'])} label candidate?</h2></div><span class="badge">unreviewed</span></div>
<p><strong>Core:</strong> {item['core_pixels']} px / {item['core_area_ha']:.2f} ha · <strong>unknown ring:</strong> {item['unknown_ring_pixels']} px · <strong>dNBR bin:</strong> [{item['dnbr_interval'][0]:.2f}, {item['dnbr_interval'][1]:.2f}) · <strong>reference:</strong> {escape(item['reference_kind'])}</p>
<img src="{escape(item['evidence_image'])}" alt="{escape(item['candidate_id'])} pre and post optical, dNBR, official reference context, candidate core, and unknown ring">
<p class="micro">Exact raster SHA-256 <code>{item['candidate_raster_sha256']}</code>. Proposed class is derived evidence, not truth. Review the core and ring together.</p>
<fieldset><legend>Owner decision</legend><div class="choices">{choices}</div><label class="notes">Optional notes<textarea data-notes maxlength="1000"></textarea></label></fieldset></article>''')
    embedded = json.dumps(template).replace("</", "<\\/")
    not_claimed = "".join(f"<li>{escape(item)}</li>" for item in (
        "independent ground truth or inter-rater agreement", "field validation or official endorsement",
        "dataset, split, baseline, model, accuracy, operational, or emergency readiness"))
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BurnLens owner region review</title><style>
:root{{--ink:#17251f;--pine:#132a26;--teal:#006b64;--paper:#f4f0e8;--line:#d7cec1;--warn:#8a521c}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif;overflow-wrap:anywhere}}header{{background:var(--pine);color:white;padding:2.4rem max(5vw,1rem)}}header p{{max-width:900px;color:#c6ddd6}}main{{max-width:1260px;margin:auto;padding:1.2rem}}.warning,.contract,.toolbar,.candidate,.attestation{{background:#fffdf8;border:1px solid var(--line);border-radius:14px;padding:1.1rem;margin:1rem 0}}.warning{{border-left:7px solid #d87618;font-weight:650}}.contract{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1rem}}.metric strong{{display:block;font-size:2rem}}.toolbar{{position:sticky;top:0;z-index:3;box-shadow:0 5px 18px #132a2620}}button,.file-label{{border:0;border-radius:8px;padding:.75rem 1rem;background:var(--teal);color:white;font-weight:700;cursor:pointer;display:inline-block;margin:.25rem}}button.secondary,.file-label.secondary{{background:#53645d}}button:disabled{{opacity:.5;cursor:not-allowed}}input[type=file]{{position:absolute;left:-9999px}}.candidate{{scroll-margin-top:120px}}.candidate-head{{display:flex;justify-content:space-between;gap:1rem;align-items:start}}h1,h2{{line-height:1.15}}.eyebrow{{font-weight:800;color:var(--teal)}}.badge{{padding:.35rem .65rem;border-radius:999px;font-weight:750;background:#e3eee9}}.candidate img{{display:block;width:100%;height:auto;border:1px solid var(--line)}}fieldset{{border:1px solid var(--line);border-radius:10px;padding:1rem}}legend{{font-weight:800;padding:0 .4rem}}.choices{{display:flex;flex-wrap:wrap;gap:.65rem}}.choices label{{border:1px solid #b8aea0;border-radius:8px;padding:.65rem 1rem;text-transform:capitalize}}.notes{{display:block;margin-top:.9rem}}textarea{{display:block;width:100%;min-height:70px;margin-top:.3rem}}.micro{{font-size:.9rem;color:#4d5c55}}.status{{font-weight:750;color:var(--warn)}}.invalid{{outline:4px solid #d87618}}code{{word-break:break-word}}@media(max-width:700px){{header{{padding:1.4rem 1rem}}main{{padding:.65rem}}.toolbar{{position:static}}.contract{{grid-template-columns:1fr 1fr}}.candidate{{padding:.8rem}}.candidate-head{{display:block}}.choices{{display:grid;grid-template-columns:1fr 1fr 1fr}}.choices label{{padding:.55rem .3rem;text-align:center}}}}
</style></head><body><header><p>BURNLENS / PHASE TWO / ISSUE #457</p><h1>Owner-confirmed region review</h1><p>Review each exact shipped region against actual optical and permitted official reference evidence, then answer yes, no, or uncertain.</p></header><main>
<p class="warning">{escape(WARNING)}</p><section class="contract"><div class="metric"><strong>6</strong>exact candidates</div><div class="metric"><strong id="completed-count">0 / 6</strong>decisions</div><div class="metric"><strong>0</strong>labels promoted</div><div><strong>Contract</strong><p>Yes is necessary, not sufficient. No and uncertain stay excluded.</p></div></section>
<section class="toolbar" aria-label="Review controls"><strong id="progress">0 of 6 decisions</strong><span id="status" class="status" role="status" aria-live="polite"></span><br><button id="save-draft" class="secondary" type="button">Save hashed draft</button><label class="file-label secondary" for="load-response">Load draft or response</label><input id="load-response" type="file" accept="application/json"><button id="review-complete" type="button">Check completion</button><button id="export-complete" type="button">Finalize and export exact response</button></section>
{''.join(cards)}<section class="attestation"><h2>Final attestation</h2><label><input id="attestation" type="checkbox"> I am the project owner, I reviewed every exact region, and I understand that yes does not establish ground truth or accept a label.</label><h3>Not claimed</h3><ul>{not_claimed}</ul><p>Trace: source <code>{report['git_source_commit']}</code> · BurnLens <code>{report['software_version']}</code> · run <code>{report['run_id']}</code> · dataset/split/baseline/model none.</p></section>
<script id="response-template" type="application/json">{embedded}</script><script>
const TEMPLATE=JSON.parse(document.getElementById('response-template').textContent);const ALLOWED=new Set(['yes','no','uncertain']);let startedAt=null;let completedAt=null;let locked=false;const cards=[...document.querySelectorAll('[data-candidate]')];const status=document.getElementById('status');
function decision(card){{return card.querySelector('input[type=radio]:checked')?.value??null}}function update(){{const count=cards.filter(card=>decision(card)).length;document.getElementById('completed-count').textContent=`${{count}} / 6`;document.getElementById('progress').textContent=`${{count}} of 6 decisions`;if(count&&!startedAt)startedAt=new Date().toISOString()}}
function payload(completed){{return {{...TEMPLATE,completed,review_started_at_utc:startedAt,review_completed_at_utc:completed?completedAt:null,owner:{{attestation:document.getElementById('attestation').checked}},responses:cards.map(card=>({{candidate_id:card.dataset.candidate,candidate_raster_sha256:card.dataset.rasterHash,decision:decision(card),notes:card.querySelector('[data-notes]').value}}))}}}}
function validateComplete(focus){{document.querySelectorAll('.invalid').forEach(x=>x.classList.remove('invalid'));const missing=cards.find(card=>!decision(card));if(missing){{missing.classList.add('invalid');status.textContent=' Every candidate requires yes, no, or uncertain.';if(focus)missing.scrollIntoView({{behavior:'smooth'}});return false}}if(!document.getElementById('attestation').checked){{status.textContent=' Final owner attestation is required.';return false}}completedAt=completedAt??new Date().toISOString();status.textContent=' Review is complete and ready for exact export.';return true}}
async function digest(bytes){{const value=await crypto.subtle.digest('SHA-256',bytes);return [...new Uint8Array(value)].map(x=>x.toString(16).padStart(2,'0')).join('')}}async function download(value,kind){{const bytes=new TextEncoder().encode(JSON.stringify(value,null,2)+'\\n');const hash=await digest(bytes);const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([bytes],{{type:'application/json'}}));a.download=`{SURFACE_ID}-${{kind}}-${{hash.slice(0,16)}}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);status.textContent=` Exact ${{kind.toLowerCase()}} bytes prepared; SHA-256 ${{hash}}.`}}
function lock(){{locked=true;document.querySelectorAll('input[type=radio],textarea,#attestation,#save-draft,#review-complete,#export-complete').forEach(x=>x.disabled=true);status.textContent+=' Response is locked in this browser session.'}}
document.addEventListener('change',update);document.getElementById('save-draft').addEventListener('click',()=>download(payload(false),'DRAFT'));document.getElementById('review-complete').addEventListener('click',()=>validateComplete(true));document.getElementById('export-complete').addEventListener('click',async()=>{{if(!validateComplete(true))return;await download(payload(true),'RESPONSE');lock()}});
document.getElementById('load-response').addEventListener('change',async event=>{{const file=event.target.files[0];if(!file)return;try{{const bytes=new Uint8Array(await file.arrayBuffer());const value=JSON.parse(new TextDecoder('utf-8',{{fatal:true}}).decode(bytes));if(value.response_schema_version!==TEMPLATE.response_schema_version||value.surface_id!==TEMPLATE.surface_id||value.surface_run_id!==TEMPLATE.surface_run_id||value.pilot_report_sha256!==TEMPLATE.pilot_report_sha256||!Array.isArray(value.responses)||value.responses.length!==6)throw new Error('binding mismatch');value.responses.forEach((item,index)=>{{const card=cards[index];if(item.candidate_id!==card.dataset.candidate||item.candidate_raster_sha256!==card.dataset.rasterHash||!(item.decision===null||ALLOWED.has(item.decision)))throw new Error('candidate or decision mismatch');if(item.decision)card.querySelector(`input[value="${{item.decision}}"]`).checked=true;card.querySelector('[data-notes]').value=item.notes??''}});startedAt=value.review_started_at_utc;completedAt=value.review_completed_at_utc;document.getElementById('attestation').checked=value.owner?.attestation===true;update();status.textContent=` Loaded exact bytes; SHA-256 ${{await digest(bytes)}}.`;if(value.completed){{if(!validateComplete(false))throw new Error('completed response is incomplete');lock()}}}}catch(error){{status.textContent=` Load rejected: ${{error.message}}.`}}}});update();
</script></main></body></html>'''


def write_surface(report: dict[str, Any], pilot_png: Path, output_directory: Path) -> list[dict[str, Any]]:
    if output_directory.exists():
        raise RegionOwnerReviewSurfaceError("output directory already exists")
    output_directory.mkdir(parents=True)
    pages = _render_evidence_pages(report, pilot_png, output_directory)
    overview = output_directory / f"{SURFACE_ID}.png"
    template_path = output_directory / f"{SURFACE_ID}-RESPONSE-TEMPLATE.json"
    html_path = output_directory / f"{SURFACE_ID}.html"
    json_path = output_directory / f"{SURFACE_ID}.json"
    _render_overview(report, pages, overview)
    template = _response_template(report)
    _write_text(template_path, json.dumps(template, indent=2) + "\n")
    _write_text(html_path, _render_html(report, template))
    outputs = [
        _binding(html_path, media_type="text/html"),
        _binding(overview, media_type="image/png"),
        _binding(template_path, media_type="application/json"),
        *[_binding(path, media_type="image/png") for path in pages],
    ]
    report["outputs"] = outputs
    _write_text(json_path, json.dumps(report, indent=2) + "\n")
    return [_binding(json_path, media_type="application/json"), *outputs]
