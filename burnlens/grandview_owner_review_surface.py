"""Build a blank owner review surface for the exact Grandview proposals."""

from __future__ import annotations

from hashlib import sha256
from html import escape
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import numpy as np
from PIL import Image, ImageDraw
import rasterio

import burnlens
from .grandview_region_proposal import (
    REPORT_ID as PROPOSAL_ID,
    _aligned_tci,
    _evidence_image,
    _panel,
    build_report as build_proposal,
    write_outputs as write_proposal,
)
from .region_owner_review_surface import _binding, _font, _sha256, _write_text


SURFACE_ID = "GRANDVIEW-OWNER-REVIEW-SURFACE-2026-001"
SURFACE_VERSION = "grandview-owner-review-surface-v0.1.0"
RESPONSE_SCHEMA_VERSION = "burnlens-grandview-owner-review-response-v0.1.0"
TASK_ISSUE = 511
PROPOSAL_RUN_ID = "BL-2026-07-20-grandview-region-proposal-r001"
PROPOSAL_GENERATED_AT = "2026-07-20T22:40:00Z"
PROPOSAL_SOURCE_COMMIT = "78bb79eb04d76cff4ed183274de881557b176413"
ALLOWED_DECISIONS = ("yes", "no", "uncertain")
WARNING = (
    "Experimental BurnLens candidate review. Not a label, dataset, ground truth, "
    "official wildfire information, or emergency guidance. Official sources govern."
)
EXPECTED_PROPOSAL_OUTPUTS = {
    f"{PROPOSAL_ID}.json": (4620, "ee1259142c9069c4057366f21320c4e61cc6c9cd412038955938370397c3aaba"),
    f"{PROPOSAL_ID}.html": (2067, "cb4192b8dec17027ea28a0d745ebd80ff474a805b4e82c5661c14394baf0d4ac"),
    f"{PROPOSAL_ID}.png": (71701, "797dbacbaae24d43f9ed829ae0b9d64d417f3f812dc8a23ce2196ca0e6f73265"),
    f"{PROPOSAL_ID}-GVP-001.tif": (3958, "453adb2edafaf72569a60d98f93d923fe02352c9b0454930c8902b9b2b828933"),
    f"{PROPOSAL_ID}-GVP-002.tif": (3976, "2f83c1822da6a8e9aadbfcad097cc1b5ed1ea118277ea0e99784e7c97dc26e91"),
}


class GrandviewOwnerReviewSurfaceError(RuntimeError):
    """Raised when proposal or response-surface bindings fail closed."""


def _verify_proposal(
    repository_root: Path,
    original_package: Path,
    extended_package: Path,
    plan_path: Path,
    reference_archive: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any], dict[str, dict[str, Any]]]:
    report, selected, previews = build_proposal(
        original_package=original_package,
        extended_package=extended_package,
        plan_path=plan_path,
        reference_archive=reference_archive,
        generated_at_utc=PROPOSAL_GENERATED_AT,
        run_id=PROPOSAL_RUN_ID,
        git_source_commit=PROPOSAL_SOURCE_COMMIT,
    )
    published = repository_root / "samples/labels/pilot/grandview/phase-two"
    bindings: dict[str, dict[str, Any]] = {}
    with TemporaryDirectory(prefix="burnlens-grandview-proposal-") as temporary:
        rebuilt = Path(temporary) / "proposal"
        write_proposal(report, selected, previews, rebuilt)
        for name, (expected_bytes, expected_sha256) in EXPECTED_PROPOSAL_OUTPUTS.items():
            tracked_path = published / name
            rebuilt_path = rebuilt / name
            tracked = (tracked_path.stat().st_size, _sha256(tracked_path))
            regenerated = (rebuilt_path.stat().st_size, _sha256(rebuilt_path))
            expected = (expected_bytes, expected_sha256)
            if tracked != expected or regenerated != expected:
                raise GrandviewOwnerReviewSurfaceError(f"proposal binding changed: {name}")
            bindings[name] = {"path": str(tracked_path.relative_to(repository_root)).replace("\\", "/"), "bytes": expected_bytes, "sha256": expected_sha256}
    return report, selected, previews, bindings


def _verify_raster(path: Path, candidate: dict[str, Any]) -> dict[str, Any]:
    with rasterio.open(path) as dataset:
        values = dataset.read(1)
        tags = dataset.tags()
        domain = set(int(value) for value in np.unique(values))
        if dataset.crs is None or dataset.crs.to_epsg() != 32610:
            raise GrandviewOwnerReviewSurfaceError(f"{path.name} CRS changed")
        if domain - {0, 1, 2}:
            raise GrandviewOwnerReviewSurfaceError(f"{path.name} domain changed")
        if int((values == 1).sum()) != candidate["core_pixels"]:
            raise GrandviewOwnerReviewSurfaceError(f"{path.name} core count changed")
        if int((values == 2).sum()) != candidate["unknown_ring_pixels"]:
            raise GrandviewOwnerReviewSurfaceError(f"{path.name} ring count changed")
        if tags.get("label_created") != "false" or tags.get("run_id") != PROPOSAL_RUN_ID:
            raise GrandviewOwnerReviewSurfaceError(f"{path.name} promotion/run tags changed")
        return {
            "crs": "EPSG:32610",
            "shape": [dataset.height, dataset.width],
            "transform": list(dataset.transform)[:6],
            "nodata": dataset.nodata,
            "class_domain": {"0": "outside", "1": "unreviewed core", "2": "unknown ring"},
        }


def _response_template(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "response_schema_version": RESPONSE_SCHEMA_VERSION,
        "surface_id": SURFACE_ID,
        "surface_run_id": report["run_id"],
        "proposal_report_sha256": report["input_bindings"][f"{PROPOSAL_ID}.json"]["sha256"],
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


def build_surface(
    *, repository_root: Path, original_package: Path, extended_package: Path,
    plan_path: Path, reference_archive: Path, generated_at_utc: str,
    run_id: str, git_source_commit: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    proposal, selected, previews, bindings = _verify_proposal(
        repository_root, original_package, extended_package, plan_path, reference_archive
    )
    published = repository_root / "samples/labels/pilot/grandview/phase-two"
    candidates: list[dict[str, Any]] = []
    for item in proposal["candidates"]:
        raster_name = item["candidate_raster"]
        binding = bindings[raster_name]
        candidates.append({
            "candidate_id": item["candidate_id"],
            "event_group_id": proposal["event_group_id"],
            "event_id": proposal["event_id"],
            "fire_name": "Grandview 0558 OD",
            "proposed_class": item["candidate_class"],
            "core_pixels": item["core_pixels"],
            "core_area_hectares": item["core_area_hectares"],
            "unknown_ring_pixels": item["unknown_ring_pixels"],
            "dnbr_interval": item["dnbr_interval"],
            "dnbr_observed": item["dnbr_observed"],
            "selection_tie_sha256": item["selection_tie_sha256"],
            "candidate_raster": raster_name,
            "candidate_raster_bytes": binding["bytes"],
            "candidate_raster_sha256": binding["sha256"],
            "raster_contract": _verify_raster(published / raster_name, item),
            "evidence_image": f"{SURFACE_ID}-{item['candidate_id']}.png",
            "proposition_basis": proposal["method"][f"{item['candidate_class']}_route"],
            "limitations": proposal["limitations"][:3],
            "owner_decision": None,
            "promotion_status": "blocked pending exact owner response and later reproducibility/source/terms/quality/uncertainty/leakage gates",
        })
    report = {
        "report_id": SURFACE_ID,
        "report_version": SURFACE_VERSION,
        "response_schema_version": RESPONSE_SCHEMA_VERSION,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "software_version": burnlens.__version__,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "event_group_id": proposal["event_group_id"],
        "target_version": proposal["target_version"],
        "label_schema_version": proposal["label_schema_version"],
        "output_label_set_version": None,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "input_bindings": bindings,
        "source_records": ["MANIFEST-2026-041", "MANIFEST-2026-042", "MANIFEST-2026-043"],
        "proposal_records": ["REGISTRY-2026-042", "USE_BOUNDARY-2026-036", "MANIFEST-2026-044"],
        "candidates": candidates,
        "decision_contract": {
            "yes": "necessary but insufficient; later exact intake and reproducibility, source, terms, quality, uncertainty, and event-level leakage gates remain mandatory",
            "no": "excluded from prototype-label promotion",
            "uncertain": "excluded with uncertainty preserved",
        },
        "response_custody_contract": {
            "filename": f"{SURFACE_ID}-RESPONSE-<first-16-sha256>.json",
            "content_identity": "SHA-256 of the exact UTF-8 LF-terminated response bytes",
            "no_overwrite": True,
            "rename_or_edit_after_export": False,
            "authoritative_intake": "later separately versioned checkpoint only",
        },
        "summary": {"candidate_count": 2, "owner_responses": 0, "labels_created": 0, "dataset_count": 0, "model_count": 0},
        "claim_boundaries": {
            "owner_responses_collected": False,
            "labels_created": False,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
            "independent_ground_truth_inter_rater_field_official_or_operational_claimed": False,
        },
        "warning": WARNING,
        "decision": "SURFACE_READY_FOR_GRANDVIEW_OWNER_REVIEW_KEEP_RESPONSE_INTAKE_SEPARATE",
        "next_gate": "Preserve and intake one exact completed owner export in a separately versioned checkpoint before any label decision.",
    }
    return report, selected, previews


def _render_evidence_pages(selected: list[dict[str, Any]], previews: dict[str, Any], directory: Path) -> list[Path]:
    pre, post, extended = (_aligned_tci(previews, key) for key in ("pre_tci", "post_tci", "extended_tci"))
    paths: list[Path] = []
    for item in selected:
        canvas = Image.new("RGB", (1800, 430), "#f4f0e8")
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((0, 0, 1800, 92), fill="#132a26")
        draw.text((35, 18), f"{item['candidate_id']} / proposed {item['candidate_class']} / core {item['core_pixels']} px / unknown ring {item['ring_pixels']} px", fill="white", font=_font(24))
        draw.text((35, 55), "Red or teal = proposed core; gold = excluded unknown ring", fill="#c6ddd6", font=_font(16))
        if item["candidate_class"] == "burned":
            dnbr = previews["pre_post_dnbr"]
            reference = _evidence_image(previews["mtbs_dnbr6"], "reference")
            labels = ("pre-fire optical", "post-fire optical", "extended 2022 optical", "pre/post dNBR", "MTBS classes 2-4")
        else:
            dnbr = previews["dnbr"]
            reference = _evidence_image(previews["route"].astype(np.uint8) * 2, "reference")
            labels = ("pre-fire optical", "post-fire optical", "extended 2022 optical", "anniversary dNBR", "affirmative background route")
        sources = (pre, post, extended, _evidence_image(dnbr, "dnbr"), reference)
        for index, (source, label) in enumerate(zip(sources, labels, strict=True)):
            left = 35 + index * 350
            canvas.paste(_panel(source, item, (325, 260)), (left, 110))
            draw.text((left, 382), label, fill="#29463e", font=_font(16))
        path = directory / f"{SURFACE_ID}-{item['candidate_id']}.png"
        canvas.save(path, format="PNG", optimize=False)
        paths.append(path)
    return paths


def _render_overview(report: dict[str, Any], pages: list[Path], path: Path) -> None:
    canvas = Image.new("RGB", (1800, 1130), "#f4f0e8")
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 1800, 210), fill="#132a26")
    draw.text((55, 34), "BurnLens Grandview owner review", fill="white", font=_font(34))
    draw.text((55, 88), "2 exact candidates / 0 responses / 0 labels", fill="#c6ddd6", font=_font(22))
    draw.text((55, 137), WARNING, fill="#f2c48c", font=_font(17))
    for index, page in enumerate(pages):
        canvas.paste(Image.open(page).convert("RGB"), (0, 225 + index * 440))
    draw.text((55, 1095), "Yes is necessary but insufficient; later exact intake and evidence gates remain mandatory.", fill="#7f3524", font=_font(17))
    canvas.save(path, format="PNG", optimize=False)


def _render_html(report: dict[str, Any], template: dict[str, Any]) -> str:
    count = len(report["candidates"])
    cards: list[str] = []
    for item in report["candidates"]:
        choices = "".join(
            f'<label><input type="radio" name="decision-{escape(item["candidate_id"])}" value="{choice}"> {choice}</label>'
            for choice in ALLOWED_DECISIONS
        )
        limitations = "".join(f"<li>{escape(value)}</li>" for value in item["limitations"])
        cards.append(f'''<article class="candidate" data-candidate="{escape(item['candidate_id'])}" data-raster-hash="{item['candidate_raster_sha256']}">
<div class="candidate-head"><div><p class="eyebrow">{escape(item['candidate_id'])} / Grandview</p><h2>Is this exact region a usable prototype {escape(item['proposed_class'])} label candidate?</h2></div><span class="badge">unreviewed</span></div>
<div class="disclosure"><p><strong>Why proposed:</strong> {escape(item['proposition_basis'])}</p><p><strong>Exact unit:</strong> {item['core_pixels']} core pixels / {item['core_area_hectares']:.2f} ha; {item['unknown_ring_pixels']} excluded unknown-ring pixels; dNBR bin [{item['dnbr_interval'][0]:.2f}, {item['dnbr_interval'][1]:.2f}).</p><ul>{limitations}</ul></div>
<div class="evidence-scroll" tabindex="0" aria-label="Scrollable five-panel evidence for {escape(item['candidate_id'])}"><img src="{escape(item['evidence_image'])}" width="1800" height="430" alt="{escape(item['candidate_id'])}: pre, post, extended optical, class-specific dNBR, and MTBS or background-route evidence with core and unknown ring"></div>
<p class="micro">Exact raster SHA-256 <code>{item['candidate_raster_sha256']}</code>. Proposed class is derived evidence, not truth. Gold ring pixels stay unknown regardless of this answer.</p>
<fieldset><legend>Owner decision</legend><div class="choices">{choices}</div><label class="notes">Optional notes<textarea data-notes maxlength="1000"></textarea></label></fieldset></article>''')
    embedded = json.dumps(template).replace("</", "<\\/")
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BurnLens Grandview owner review</title><style>
:root{{--ink:#17251f;--pine:#132a26;--teal:#006b64;--paper:#f4f0e8;--line:#d7cec1;--warn:#8a521c}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif;overflow-wrap:anywhere}}header{{background:var(--pine);color:white;padding:2.4rem max(5vw,1rem)}}header p{{max-width:980px;color:#c6ddd6}}main{{max-width:1260px;margin:auto;padding:1.2rem}}.warning,.contract,.basis,.toolbar,.candidate,.attestation{{background:#fffdf8;border:1px solid var(--line);border-radius:14px;padding:1.1rem;margin:1rem 0}}.warning{{border-left:7px solid #d87618;font-weight:650}}.contract{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1rem}}.metric strong{{display:block;font-size:2rem}}.basis{{border-left:7px solid var(--teal)}}.toolbar{{position:sticky;top:0;z-index:3;box-shadow:0 5px 18px #132a2620}}button,.file-label{{border:0;border-radius:8px;padding:.75rem 1rem;background:var(--teal);color:white;font-weight:700;cursor:pointer;display:inline-block;margin:.25rem}}button.secondary,.file-label.secondary{{background:#53645d}}button:disabled{{opacity:.5;cursor:not-allowed}}input[type=file]{{position:absolute;left:-9999px}}.candidate{{scroll-margin-top:120px}}.candidate-head{{display:flex;justify-content:space-between;gap:1rem;align-items:start}}h1,h2{{line-height:1.15}}.eyebrow{{font-weight:800;color:var(--teal)}}.badge{{padding:.35rem .65rem;border-radius:999px;font-weight:750;background:#e3eee9}}.disclosure{{background:#f0f5f1;border-radius:10px;padding:.8rem 1rem;margin:.8rem 0}}.evidence-scroll{{overflow-x:auto;border:1px solid var(--line);background:#132a26}}.evidence-scroll img{{display:block;width:100%;min-width:1050px;height:auto}}fieldset{{border:1px solid var(--line);border-radius:10px;padding:1rem}}legend{{font-weight:800;padding:0 .4rem}}.choices{{display:flex;flex-wrap:wrap;gap:.65rem}}.choices label{{border:1px solid #b8aea0;border-radius:8px;padding:.65rem 1rem;text-transform:capitalize}}.notes{{display:block;margin-top:.9rem}}textarea{{display:block;width:100%;min-height:70px;margin-top:.3rem}}.micro{{font-size:.9rem;color:#4d5c55}}.status{{font-weight:750;color:var(--warn)}}.invalid{{outline:4px solid #d87618}}code{{word-break:break-word}}@media(max-width:700px){{header{{padding:1.4rem 1rem}}main{{padding:.65rem}}.toolbar{{position:static}}.contract{{grid-template-columns:1fr 1fr}}.candidate{{padding:.8rem}}.candidate-head{{display:block}}.choices{{display:grid;grid-template-columns:1fr 1fr 1fr}}.choices label{{padding:.55rem .3rem;text-align:center}}}}
</style></head><body><header><p>BURNLENS / PHASE TWO / ISSUE #511</p><h1>Grandview owner-confirmed region review</h1><p>Review each exact unreviewed core and its excluded unknown ring against actual pre-fire, post-fire, extended optical, class-specific dNBR, and MTBS/background-route evidence. Answer yes, no, or uncertain.</p></header><main>
<p class="warning">{escape(WARNING)}</p><section class="contract"><div class="metric"><strong>{count}</strong>exact candidates</div><div class="metric"><strong id="completed-count">0 / {count}</strong>decisions</div><div class="metric"><strong>0</strong>labels promoted</div><div><strong>Contract</strong><p>Yes is necessary, not sufficient. No and uncertain stay excluded.</p></div></section>
<section class="basis"><h2>Read before deciding</h2><p>The fixed dNBR bin is a coherence partition, not a universal burn threshold. MTBS classes 2-4 and the multi-signal background route are candidate evidence, not independent ground truth. RAVG modeled classes remain context-only under the delivered sparse/non-tree warning and are not affirmative evidence. Gold pixels are uncertainty rings and cannot be approved by this surface.</p><p><strong>Exact-byte custody:</strong> export once to the hash-named response file. Do not overwrite, rename, or edit it. A later checkpoint must preserve and verify those exact bytes before considering any label.</p></section>
<section class="toolbar" aria-label="Review controls"><strong id="progress">0 of {count} decisions</strong><span id="status" class="status" role="status" aria-live="polite"></span><br><button id="save-draft" class="secondary" type="button">Save hashed draft</button><label class="file-label secondary" for="load-response">Load draft or response</label><input id="load-response" type="file" accept="application/json"><button id="review-complete" type="button">Check completion</button><button id="export-complete" type="button">Finalize and export exact response</button></section>
{''.join(cards)}<section class="attestation"><h2>Final attestation</h2><label><input id="attestation" type="checkbox"> I am the project owner, I reviewed both exact regions, and I understand that yes does not establish ground truth or accept a label.</label><h3>Not claimed</h3><ul><li>independent ground truth or inter-rater agreement</li><li>field validation, official status, or endorsement</li><li>dataset, split, baseline, model, accuracy, operational, or emergency readiness</li></ul><p>Trace: source <code>{report['git_source_commit']}</code> | BurnLens <code>{report['software_version']}</code> | run <code>{report['run_id']}</code> | dataset/split/baseline/model none.</p></section>
<script id="response-template" type="application/json">{embedded}</script><script>
const TEMPLATE=JSON.parse(document.getElementById('response-template').textContent);const ALLOWED=new Set(['yes','no','uncertain']);let startedAt=null;let completedAt=null;const cards=[...document.querySelectorAll('[data-candidate]')];const status=document.getElementById('status');const TOTAL=cards.length;
function decision(card){{return card.querySelector('input[type=radio]:checked')?.value??null}}function update(){{const count=cards.filter(card=>decision(card)).length;document.getElementById('completed-count').textContent=`${{count}} / ${{TOTAL}}`;document.getElementById('progress').textContent=`${{count}} of ${{TOTAL}} decisions`;if(count&&!startedAt)startedAt=new Date().toISOString()}}
function payload(completed){{return {{...TEMPLATE,completed,review_started_at_utc:startedAt,review_completed_at_utc:completed?completedAt:null,owner:{{attestation:document.getElementById('attestation').checked}},responses:cards.map(card=>({{candidate_id:card.dataset.candidate,candidate_raster_sha256:card.dataset.rasterHash,decision:decision(card),notes:card.querySelector('[data-notes]').value}}))}}}}
function validateComplete(focus){{document.querySelectorAll('.invalid').forEach(x=>x.classList.remove('invalid'));const missing=cards.find(card=>!decision(card));if(missing){{missing.classList.add('invalid');status.textContent=' Every candidate requires yes, no, or uncertain.';if(focus)missing.scrollIntoView({{behavior:'smooth'}});return false}}if(!document.getElementById('attestation').checked){{status.textContent=' Final owner attestation is required.';return false}}completedAt=completedAt??new Date().toISOString();status.textContent=' Review is complete and ready for exact export.';return true}}
async function digest(bytes){{const value=await crypto.subtle.digest('SHA-256',bytes);return [...new Uint8Array(value)].map(x=>x.toString(16).padStart(2,'0')).join('')}}async function download(value,kind){{const bytes=new TextEncoder().encode(JSON.stringify(value,null,2)+'\\n');const hash=await digest(bytes);const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([bytes],{{type:'application/json'}}));a.download=`{SURFACE_ID}-${{kind}}-${{hash.slice(0,16)}}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);status.textContent=` Exact ${{kind.toLowerCase()}} bytes prepared; SHA-256 ${{hash}}.`}}
function lock(){{document.querySelectorAll('input[type=radio],textarea,#attestation,#save-draft,#load-response,#review-complete,#export-complete').forEach(x=>x.disabled=true);status.textContent+=' Response is locked in this browser session.'}}
document.addEventListener('change',update);document.getElementById('save-draft').addEventListener('click',()=>download(payload(false),'DRAFT'));document.getElementById('review-complete').addEventListener('click',()=>validateComplete(true));document.getElementById('export-complete').addEventListener('click',async()=>{{if(!validateComplete(true))return;await download(payload(true),'RESPONSE');lock()}});
document.getElementById('load-response').addEventListener('change',async event=>{{const file=event.target.files[0];if(!file)return;try{{const bytes=new Uint8Array(await file.arrayBuffer());const value=JSON.parse(new TextDecoder('utf-8',{{fatal:true}}).decode(bytes));if(value.response_schema_version!==TEMPLATE.response_schema_version||value.surface_id!==TEMPLATE.surface_id||value.surface_run_id!==TEMPLATE.surface_run_id||value.proposal_report_sha256!==TEMPLATE.proposal_report_sha256||typeof value.completed!=='boolean'||!Array.isArray(value.responses)||value.responses.length!==TOTAL)throw new Error('binding mismatch');const incoming=value.responses.map((item,index)=>{{const card=cards[index];if(item.candidate_id!==card.dataset.candidate||item.candidate_raster_sha256!==card.dataset.rasterHash||!(item.decision===null||ALLOWED.has(item.decision))||typeof item.notes!=='string'||item.notes.length>1000)throw new Error('candidate or decision mismatch');return item}});incoming.forEach((item,index)=>{{const card=cards[index];card.querySelectorAll('input[type=radio]').forEach(input=>input.checked=false);if(item.decision)card.querySelector(`input[value="${{item.decision}}"]`).checked=true;card.querySelector('[data-notes]').value=item.notes}});startedAt=value.review_started_at_utc;completedAt=value.review_completed_at_utc;document.getElementById('attestation').checked=value.owner?.attestation===true;update();status.textContent=` Loaded exact bytes; SHA-256 ${{await digest(bytes)}}.`;if(value.completed){{if(!validateComplete(false))throw new Error('completed response is incomplete');lock()}}}}catch(error){{status.textContent=` Load rejected: ${{error.message}}.`}}}});update();
</script></main></body></html>'''


def write_surface(report: dict[str, Any], selected: list[dict[str, Any]], previews: dict[str, Any], output_directory: Path) -> list[dict[str, Any]]:
    if output_directory.exists():
        raise GrandviewOwnerReviewSurfaceError("output directory already exists")
    output_directory.mkdir(parents=True)
    pages = _render_evidence_pages(selected, previews, output_directory)
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
        *[_binding(page, media_type="image/png") for page in pages],
    ]
    report["outputs"] = outputs
    _write_text(json_path, json.dumps(report, indent=2) + "\n")
    return [_binding(json_path, media_type="application/json"), *outputs]
