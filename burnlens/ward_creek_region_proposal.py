"""Propose exact Ward Creek burned/background regions without creating labels."""

from __future__ import annotations

from hashlib import sha256
from html import escape
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw
import rasterio

from .green_ridge_region_proposal import (
    PIXEL_AREA_HA,
    TARGET_PIXELS,
    _evidence_image,
    _panel,
    select_region,
)
from .label_proposal import (
    BURN_DNBR_MIN,
    BURN_NDVI_LOSS_MIN,
    BURN_NIR_LOSS_MIN,
    BURN_SUPPORTING_SIGNALS_MIN,
    BURN_SWIR_GAIN_MIN,
    BURN_NEIGHBOR_SUPPORT_MIN,
    neighbor_support,
)
from .optical_pair_evidence import WARNING, _font, _write_utf8_lf
from .region_candidate_pilot import _align_tci_to_grid
from .replacement_event_optical_contract import (
    EVENT_GROUP_ID,
    EVENT_ID,
    SOFTWARE_VERSION,
)
from .ward_creek_background_evidence import (
    INPUT_LABEL_SET_VERSION,
    RUN_ID as BACKGROUND_RUN_ID,
    build_report as build_background_report,
)


REPORT_ID = "WARD-CREEK-REGION-PROPOSAL-2026-001"
REPORT_VERSION = "ward-creek-two-class-region-proposal-v0.1.0"
GENERATOR_VERSION = "ward-creek-region-proposal-generator-v0.1.0"
PROTOCOL_VERSION = "ward-creek-two-class-region-proposal-protocol-v0.1.0"
UNIT_ID = "P2O4-T39-U05"
TASK_ISSUE = 554
RUN_ID = "BL-2026-07-24-ward-creek-region-proposal-r001"
BACKGROUND_REPORT_ID = "WARD-CREEK-BACKGROUND-EVIDENCE-2026-001"
BACKGROUND_REPORT_SHA256 = (
    "acf5b02c314b7dfdee94d8709323117f24e1966042818c37ef7431085813933c"
)
SUFFICIENCY_REPORT_ID = "SIX-EVENT-DATASET-SUFFICIENCY-2026-001"
SUFFICIENCY_REPORT_SHA256 = (
    "a3fa779669143333fbc2b9b27fb35d210d0847283ef754c9e7f1f39a0c30908b"
)
LABEL_SCHEMA_VERSION = "burn-scar-binary-region-label-schema-v0.3.0"
TARGET_VERSION = "target-burn-scar-v0.2.0"
EXPECTED_ROUTE_COUNTS = {
    "burn_screen": 5_050,
    "burn_coherent": 3_208,
    "burned_route": 686,
    "background_route": 21_266,
}
EXPECTED_SELECTIONS = {
    "burned": {
        "core_pixels": 14,
        "ring_pixels": 26,
        "selection_tie_sha256": (
            "6c9480200d0db636a97aea5dbe2cc3f14011c21522779e6dfabc4de00ae9c72b"
        ),
    },
    "background": {
        "core_pixels": 25,
        "ring_pixels": 40,
        "selection_tie_sha256": (
            "01b368b6cb160e37334029294e492fbd1963eeb2634c96a58a3facf9458c5677"
        ),
    },
}


class WardCreekRegionProposalError(RuntimeError):
    """The exact Ward Creek U05 proposal failed closed."""


def _file_digest(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _read_bound_json(
    path: Path,
    *,
    expected_sha256: str,
    expected_report_id: str,
) -> dict[str, Any]:
    if not path.is_file() or _file_digest(path) != expected_sha256:
        raise WardCreekRegionProposalError(
            f"{expected_report_id} exact-byte binding mismatch"
        )
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise WardCreekRegionProposalError(
            f"{expected_report_id} is unreadable"
        ) from error
    if report.get("report_id") != expected_report_id:
        raise WardCreekRegionProposalError(
            f"{expected_report_id} semantic binding mismatch"
        )
    return report


def _candidate_binding(candidate: dict[str, Any]) -> str:
    core_rows, core_columns = np.where(candidate["core"])
    ring_rows, ring_columns = np.where(candidate["ring"])
    payload = {
        "event_group_id": EVENT_GROUP_ID,
        "event_id": EVENT_ID,
        "proposed_class": candidate["candidate_class"],
        "background_report_sha256": BACKGROUND_REPORT_SHA256,
        "sufficiency_report_sha256": SUFFICIENCY_REPORT_SHA256,
        "selection_tie_sha256": candidate["selection_tie_sha256"],
        "core_rows_columns": np.column_stack((core_rows, core_columns)).tolist(),
        "ring_rows_columns": np.column_stack((ring_rows, ring_columns)).tolist(),
    }
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _leakage_gate(sufficiency: dict[str, Any]) -> dict[str, Any]:
    if (
        sufficiency.get("label_set_version") != INPUT_LABEL_SET_VERSION
        or sufficiency.get("dataset_version") is not None
        or sufficiency.get("split_version") is not None
        or sufficiency.get("model_version") is not None
    ):
        raise WardCreekRegionProposalError("accepted sufficiency state drifted")
    groups = [item["event_group_id"] for item in sufficiency.get("events", [])]
    years = [item["year"] for item in sufficiency.get("events", [])]
    if EVENT_GROUP_ID in groups or 2019 in years:
        raise WardCreekRegionProposalError(
            "Ward Creek event group or year collides with accepted prototype evidence"
        )
    return {
        "status": "PASS",
        "accepted_sufficiency_report_sha256": SUFFICIENCY_REPORT_SHA256,
        "existing_event_group_count": len(groups),
        "existing_event_groups": groups,
        "ward_creek_event_group_absent": True,
        "ward_creek_year_absent": True,
        "candidate_pair_overlap_pixels": 0,
        "split_assignment_created": False,
        "note": (
            "This is a proposal-time collision gate. Whole-event split fitness is "
            "recomputed only after both classes pass owner and non-owner promotion gates."
        ),
    }


def build_report(
    *,
    repository_root: Path,
    pre_package: Path,
    post_package: Path,
    archive_path: Path,
    extracted_root: Path,
    background_report_path: Path,
    sufficiency_report_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    if run_id != RUN_ID:
        raise WardCreekRegionProposalError("run ID drifted")
    accepted_background = _read_bound_json(
        background_report_path,
        expected_sha256=BACKGROUND_REPORT_SHA256,
        expected_report_id=BACKGROUND_REPORT_ID,
    )
    if (
        accepted_background.get("run_id") != BACKGROUND_RUN_ID
        or accepted_background.get("fitness_decision", {}).get("next_dependency")
        != "P2O4-T39-U05_EXACT_TWO_CLASS_PROPOSAL"
        or accepted_background.get("output_label_set_version") is not None
    ):
        raise WardCreekRegionProposalError("accepted U04 semantics drifted")
    sufficiency = _read_bound_json(
        sufficiency_report_path,
        expected_sha256=SUFFICIENCY_REPORT_SHA256,
        expected_report_id=SUFFICIENCY_REPORT_ID,
    )
    leakage = _leakage_gate(sufficiency)
    fresh_background, previews = build_background_report(
        repository_root=repository_root,
        pre_package=pre_package,
        post_package=post_package,
        archive_path=archive_path,
        extracted_root=extracted_root,
        source_report_path=(
            repository_root
            / "samples/reference/phase-two/ward-creek/reference-fitness-v0.1.1/"
            "WARD-CREEK-REFERENCE-FITNESS-2026-002.json"
        ),
        generated_at_utc=generated_at_utc,
        run_id=BACKGROUND_RUN_ID,
        git_source_commit=git_source_commit,
    )
    for key in (
        "event",
        "accepted_u03_source",
        "custody_reverification",
        "terms_and_source_roles",
        "products",
        "mtbs_domain",
        "registration",
        "route_evidence",
        "fitness_decision",
    ):
        if fresh_background[key] != accepted_background[key]:
            raise WardCreekRegionProposalError(
                f"accepted U04 {key} failed exact scientific reverification"
            )

    support_count = (
        (previews["ndvi_loss"] >= BURN_NDVI_LOSS_MIN).astype(np.uint8)
        + (previews["swir_gain"] >= BURN_SWIR_GAIN_MIN).astype(np.uint8)
        + (previews["nir_loss"] >= BURN_NIR_LOSS_MIN).astype(np.uint8)
    )
    burn_screen = (
        (previews["dnbr"] >= BURN_DNBR_MIN)
        & (support_count >= BURN_SUPPORTING_SIGNALS_MIN)
    )
    burn_coherent = burn_screen & (
        neighbor_support(burn_screen) >= BURN_NEIGHBOR_SUPPORT_MIN
    )
    burned_route = (
        previews["usable"]
        & burn_coherent
        & np.isin(previews["sampled_mtbs"], (2, 3, 4))
    )
    background_route = previews["route"]
    route_counts = {
        "burn_screen": int(burn_screen.sum()),
        "burn_coherent": int(burn_coherent.sum()),
        "burned_route": int(burned_route.sum()),
        "background_route": int(background_route.sum()),
    }
    if route_counts != EXPECTED_ROUTE_COUNTS:
        raise WardCreekRegionProposalError(
            f"exact two-class routes drifted: {route_counts}"
        )
    selected = [
        select_region("burned", burned_route, previews["dnbr"]),
        select_region("background", background_route, previews["dnbr"]),
    ]
    for index, candidate in enumerate(selected, start=1):
        candidate["candidate_id"] = f"WCP-{index:03d}"
        expected = EXPECTED_SELECTIONS[candidate["candidate_class"]]
        observed = {
            key: candidate[key]
            for key in ("core_pixels", "ring_pixels", "selection_tie_sha256")
        }
        if observed != expected:
            raise WardCreekRegionProposalError(
                f"{candidate['candidate_class']} exact selection drifted"
            )
        candidate["proposal_binding_sha256"] = _candidate_binding(candidate)
    overlap = (
        (selected[0]["core"] | selected[0]["ring"])
        & (selected[1]["core"] | selected[1]["ring"])
    )
    if np.any(overlap):
        raise WardCreekRegionProposalError("candidate core/ring footprints overlap")

    candidates = [
        {
            "candidate_id": candidate["candidate_id"],
            "event_group_id": EVENT_GROUP_ID,
            "event_id": EVENT_ID,
            "proposed_class": candidate["candidate_class"],
            "review_state": "unreviewed-no-promotion",
            "core_pixels": candidate["core_pixels"],
            "core_area_hectares": round(
                candidate["core_pixels"] * PIXEL_AREA_HA,
                4,
            ),
            "target_pixels": TARGET_PIXELS,
            "target_gap_pixels": candidate["core_pixels"] - TARGET_PIXELS,
            "unknown_ring_pixels": candidate["ring_pixels"],
            "bbox_rows_columns": candidate["bbox"],
            "dnbr_interval": candidate["dnbr_interval"],
            "dnbr_observed": candidate["dnbr_observed"],
            "eligible_component_count": candidate["eligible_component_count"],
            "evaluated_component_count": candidate["evaluated_component_count"],
            "selection_tie_sha256": candidate["selection_tie_sha256"],
            "proposal_binding_sha256": candidate["proposal_binding_sha256"],
            "candidate_raster": (
                f"{REPORT_ID}-{candidate['candidate_id']}.tif"
            ),
            "candidate_raster_bytes": None,
            "candidate_raster_sha256": None,
            "owner_decision": None,
        }
        for candidate in selected
    ]
    report = {
        "report_id": REPORT_ID,
        "report_version": REPORT_VERSION,
        "generator_version": GENERATOR_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "unit_id": UNIT_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": None,
        "target_version": TARGET_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "input_label_set_version": INPUT_LABEL_SET_VERSION,
        "output_label_set_version": None,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "event": accepted_background["event"],
        "bindings": {
            "accepted_background_report": {
                "report_id": BACKGROUND_REPORT_ID,
                "run_id": BACKGROUND_RUN_ID,
                "bytes": background_report_path.stat().st_size,
                "sha256": BACKGROUND_REPORT_SHA256,
                "source_commit": accepted_background["git_source_commit"],
            },
            "accepted_sufficiency_report": {
                "report_id": SUFFICIENCY_REPORT_ID,
                "bytes": sufficiency_report_path.stat().st_size,
                "sha256": SUFFICIENCY_REPORT_SHA256,
                "source_commit": sufficiency["git_source_commit"],
            },
            "fresh_background_reverification_source_commit": git_source_commit,
        },
        "route_evidence": {
            "burned": {
                "pixels": route_counts["burned_route"],
                "area_hectares": round(
                    route_counts["burned_route"] * PIXEL_AREA_HA,
                    4,
                ),
                "burn_screen_pixels": route_counts["burn_screen"],
                "burn_coherent_pixels": route_counts["burn_coherent"],
                "rule": (
                    "Eligible exact-pair pixels; transferred coherent four-signal "
                    "burn screen; MTBS dNBR6 classes 2-4 corroboration."
                ),
            },
            "background": {
                "pixels": route_counts["background_route"],
                "area_hectares": round(
                    route_counts["background_route"] * PIXEL_AREA_HA,
                    4,
                ),
                "rule": accepted_background["route_evidence"]["rule"],
            },
        },
        "method": {
            "candidate_unit": "one intact 8-connected native 20 m component",
            "partition": "fixed 0.05 dNBR bin from the established region-candidate protocol",
            "target_pixels": TARGET_PIXELS,
            "selection": (
                "minimum absolute distance to 25 pixels, then SHA-256 of proposed "
                "class, fixed bin, and ordered native-grid coordinates"
            ),
            "intact_component_policy": (
                "Never clip, pad, merge, or expand a component to force the target. "
                "The burned core is 14 pixels because it is the nearest eligible intact component."
            ),
            "unknown_ring": (
                "one native 20 m pixel around each intact core; always excluded here"
            ),
        },
        "leakage_gate": leakage,
        "summary": {
            "candidate_count": 2,
            "class_counts": {"burned": 1, "background": 1},
            "core_pixels": sum(item["core_pixels"] for item in selected),
            "core_area_hectares": round(
                sum(item["core_pixels"] for item in selected) * PIXEL_AREA_HA,
                4,
            ),
            "unknown_ring_pixels": sum(item["ring_pixels"] for item in selected),
            "owner_responses": 0,
            "labels_created": 0,
        },
        "candidates": candidates,
        "decision": (
            "PROPOSE_EXACT_WARD_CREEK_TWO_CLASS_REGIONS_"
            "KEEP_OWNER_REVIEW_AND_PROMOTION_CLOSED"
        ),
        "next_gate": (
            "P2O4-T39-U06 must build one exact two-candidate owner "
            "yes/no/uncertain batch bound to these proposal and raster hashes."
        ),
        "limitations": [
            "The fixed spectral rules, dNBR bins, component target, and tie-break are evidence-coherence rules, not universal burn or severity thresholds.",
            "The burned core has 14 pixels / 0.56 hectares; BurnLens preserves that intact component instead of forcing the 25-pixel target.",
            "MTBS classes 2-4 and paired optical change are proposal evidence, not independent ground truth.",
            "The background proposal shows stability during the exact fire-window pair outside the conservative MTBS-domain buffer; it does not prove land was never burned.",
            "Only one burned and one background proposal are created; owner review and every non-owner promotion gate remain absent.",
        ],
        "claims": {
            "proven": [
                "Both exact proposal routes and their selected intact components reproduce from immutable custody.",
                "Ward Creek does not collide with an existing prototype event group or year.",
                "The two candidate core/ring footprints do not overlap.",
            ],
            "not_proven": [
                "No owner decision, label, dataset, split, baseline, model, metric, accuracy, independent validation, field validation, official status, endorsement, emergency suitability, or operational readiness exists."
            ],
        },
        "warning": WARNING,
    }
    previews = {
        **previews,
        "burn_screen": burn_screen,
        "burn_coherent": burn_coherent,
        "burned_route": burned_route,
        "background_route": background_route,
    }
    return report, selected, previews


def _aligned_tci(previews: dict[str, Any], key: str) -> Image.Image:
    transform = previews["grid_transform"]
    shape = previews["burned_route"].shape
    aligned = _align_tci_to_grid(
        previews[key],
        rasterio.Affine(
            transform.a / 2,
            0,
            transform.c,
            0,
            transform.e / 2,
            transform.f,
        ),
        transform,
        shape,
        "EPSG:32610",
    )
    return Image.fromarray(
        np.moveaxis(aligned, 0, 2).astype(np.uint8),
        mode="RGB",
    )


def _mask_image(mask: np.ndarray, color: tuple[int, int, int]) -> Image.Image:
    rgb = np.zeros((*mask.shape, 3), dtype=np.uint8)
    rgb[:] = (22, 31, 29)
    rgb[mask] = color
    return Image.fromarray(rgb, mode="RGB")


def render_png(
    report: dict[str, Any],
    selected: list[dict[str, Any]],
    previews: dict[str, Any],
    path: Path,
) -> None:
    canvas = Image.new("RGB", (1800, 1040), "#07110f")
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (55, 34),
        "BURNLENS / WARD CREEK TWO-CLASS PROPOSAL",
        fill="#b9d8cf",
        font=_font(22),
    )
    draw.text(
        (55, 72),
        "Two exact review candidates; zero owner decisions or labels.",
        fill="#eef7f3",
        font=_font(30),
    )
    draw.text(
        (55, 116),
        "Intact components are preserved; the burned core is 14 pixels, not forced to 25.",
        fill="#ffca73",
        font=_font(17),
    )
    pre = _aligned_tci(previews, "pre_tci")
    post = _aligned_tci(previews, "post_tci")
    for row, item in enumerate(selected):
        top = 158 + row * 370
        draw.rounded_rectangle(
            (45, top, 1755, top + 340),
            radius=15,
            fill="#0e1d1a",
            outline="#315b50",
            width=2,
        )
        draw.text(
            (65, top + 17),
            (
                f"{item['candidate_id']} / proposed {item['candidate_class']} / "
                f"core {item['core_pixels']} px / unknown ring {item['ring_pixels']} px"
            ),
            fill="#eef7f3",
            font=_font(18),
        )
        if item["candidate_class"] == "burned":
            sources = (
                pre,
                post,
                _evidence_image(previews["dnbr"], "dnbr"),
                _evidence_image(previews["sampled_mtbs"], "reference"),
                _mask_image(previews["burn_coherent"], (202, 109, 68)),
            )
            labels = (
                "pre 2019",
                "post 2019",
                "pre/post dNBR",
                "MTBS classes 2-4",
                "coherent burn screen",
            )
        else:
            sources = (
                pre,
                post,
                _evidence_image(previews["dnbr"], "dnbr"),
                _mask_image(previews["coherent"], (72, 150, 124)),
                _mask_image(previews["background_route"], (72, 150, 124)),
            )
            labels = (
                "pre 2019",
                "post 2019",
                "near-zero dNBR",
                "coherent stability",
                "outside MTBS buffer",
            )
        for column, (source, label) in enumerate(zip(sources, labels, strict=True)):
            left = 65 + column * 338
            canvas.paste(_panel(source, item, (300, 225)), (left, top + 58))
            draw.text(
                (left, top + 292),
                label,
                fill="#b9d8cf",
                font=_font(14),
            )
        draw.text(
            (65, top + 316),
            (
                f"binding {item['proposal_binding_sha256'][:24]}... / "
                f"fixed dNBR bin {item['dnbr_interval']}"
            ),
            fill="#78e0bd",
            font=_font(13),
        )
    draw.rounded_rectangle(
        (55, 914, 1745, 984),
        radius=14,
        fill="#261f12",
        outline="#be8a36",
        width=2,
    )
    draw.text((78, 927), WARNING, fill="#ffd997", font=_font(14))
    draw.text(
        (78, 955),
        "Both candidates remain unreviewed. MTBS is never affirmative background truth.",
        fill="#ffd997",
        font=_font(14),
    )
    draw.text(
        (55, 1002),
        (
            f"TRACE {report['git_source_commit'][:12]} / {report['run_id']} / "
            f"BurnLens {SOFTWARE_VERSION} / labels-dataset-model none"
        ),
        fill="#b9d8cf",
        font=_font(13),
    )
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], path: Path) -> None:
    rows = "".join(
        (
            f"<tr><td><code>{escape(item['candidate_id'])}</code></td>"
            f"<td>{escape(item['proposed_class'])}</td>"
            f"<td>{item['core_pixels']}</td>"
            f"<td>{item['target_gap_pixels']:+d}</td>"
            f"<td>{item['unknown_ring_pixels']}</td>"
            f"<td><code>{escape(item['proposal_binding_sha256'])}</code></td>"
            f"<td><a href='{escape(item['candidate_raster'])}'>raster</a></td></tr>"
        )
        for item in report["candidates"]
    )
    burned = report["route_evidence"]["burned"]
    background = report["route_evidence"]["background"]
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ward Creek region proposal</title><style>
html,body{{max-width:100%;overflow-x:hidden}}body{{margin:0;background:#07110f;color:#eef7f3;font:16px/1.55 system-ui,sans-serif}}main{{max-width:1200px;margin:auto;padding:32px;box-sizing:border-box}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.02}}.card{{max-width:100%;min-width:0;box-sizing:border-box;background:#0e1d1a;border:1px solid #315b50;border-radius:16px;padding:20px;margin:18px 0;overflow-wrap:anywhere}}.warn{{background:#261f12;border-color:#be8a36;color:#ffd997}}img{{display:block;max-width:100%;width:100%;height:auto;border-radius:16px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}.metric strong{{display:block;font-size:2rem;color:#78e0bd}}table{{width:100%;max-width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #315b50;vertical-align:top;overflow-wrap:anywhere}}code,strong{{overflow-wrap:anywhere}}a{{color:#78e0bd}}@media(max-width:700px){{main{{padding:18px}}.table-card{{overflow-x:auto}}.table-card table{{min-width:980px}}}}
</style></head><body><main><p>BURNLENS / PHASE TWO / ISSUE #554 / U05</p><h1>Two Ward Creek regions are proposed; neither is a label.</h1><div class="card warn">{escape(report['warning'])}</div><img src="{REPORT_ID}.png" width="1800" height="1040" alt="Actual Ward Creek burned and background proposal evidence with candidate cores and unknown rings"><div class="grid"><div class="card metric"><strong>2</strong>unreviewed candidates</div><div class="card metric"><strong>{burned['pixels']:,}</strong>burned-route pixels</div><div class="card metric"><strong>{background['pixels']:,}</strong>background-route pixels</div><div class="card metric"><strong>0</strong>owner decisions or labels</div></div><h2>Exact candidates</h2><div class="card table-card"><table><thead><tr><th>ID</th><th>Proposed class</th><th>Core pixels</th><th>Gap from 25</th><th>Unknown ring</th><th>Binding SHA-256</th><th>Raster</th></tr></thead><tbody>{rows}</tbody></table></div><h2>Why the burned core has 14 pixels</h2><div class="card"><p>{escape(report['method']['intact_component_policy'])}</p><p>The 25-pixel value is a selection target, not permission to alter evidence geometry.</p></div><h2>Conjunctive routes</h2><div class="card"><p><strong>Burned:</strong> {escape(burned['rule'])}</p><p><strong>Background:</strong> {escape(background['rule'])}</p></div><h2>Boundaries</h2><div class="card"><ul>{''.join(f'<li>{escape(item)}</li>' for item in report['limitations'])}</ul><p><strong>{escape(report['decision'])}</strong></p><p>{escape(report['next_gate'])}</p></div><div class="card warn"><p>No ground truth, owner decision, accepted label, dataset, split, baseline, model, metric, accuracy, field validation, official status, endorsement, emergency suitability, or operational readiness exists.</p></div><p>Trace: commit <code>{escape(report['git_source_commit'])}</code> / run <code>{escape(report['run_id'])}</code> / U04 <code>{BACKGROUND_REPORT_SHA256}</code> / BurnLens <code>{SOFTWARE_VERSION}</code>.</p></main></body></html>"""
    _write_utf8_lf(path, html)


def _write_candidate_raster(
    *,
    path: Path,
    candidate: dict[str, Any],
    transform: rasterio.Affine,
    report: dict[str, Any],
) -> None:
    array = np.zeros(candidate["core"].shape, dtype=np.uint8)
    array[candidate["core"]] = 1
    array[candidate["ring"]] = 2
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=array.shape[1],
        height=array.shape[0],
        count=1,
        dtype="uint8",
        crs="EPSG:32610",
        transform=transform,
        nodata=255,
        compress="DEFLATE",
        predictor=2,
    ) as dataset:
        dataset.write(array, 1)
        dataset.update_tags(
            candidate_id=candidate["candidate_id"],
            event_group_id=EVENT_GROUP_ID,
            event_id=EVENT_ID,
            proposed_class=candidate["candidate_class"],
            kind="unreviewed-core-and-unknown-ring",
            generator_version=GENERATOR_VERSION,
            run_id=report["run_id"],
            git_source_commit=report["git_source_commit"],
            background_report_sha256=BACKGROUND_REPORT_SHA256,
            sufficiency_report_sha256=SUFFICIENCY_REPORT_SHA256,
            proposal_binding_sha256=candidate["proposal_binding_sha256"],
            owner_decision="none",
            label_created="false",
        )


def write_outputs(
    report: dict[str, Any],
    selected: list[dict[str, Any]],
    previews: dict[str, Any],
    directory: Path,
) -> list[Path]:
    if directory.exists():
        raise WardCreekRegionProposalError("output directory already exists")
    directory.mkdir(parents=True)
    outputs: list[Path] = []
    by_id = {item["candidate_id"]: item for item in report["candidates"]}
    for candidate in selected:
        path = directory / f"{REPORT_ID}-{candidate['candidate_id']}.tif"
        _write_candidate_raster(
            path=path,
            candidate=candidate,
            transform=previews["grid_transform"],
            report=report,
        )
        public = by_id[candidate["candidate_id"]]
        public["candidate_raster_bytes"] = path.stat().st_size
        public["candidate_raster_sha256"] = _file_digest(path)
        outputs.append(path)
    png_path = directory / f"{REPORT_ID}.png"
    html_path = directory / f"{REPORT_ID}.html"
    json_path = directory / f"{REPORT_ID}.json"
    render_png(report, selected, previews, png_path)
    render_html(report, html_path)
    _write_utf8_lf(json_path, json.dumps(report, indent=2) + "\n")
    return [json_path, html_path, png_path, *outputs]
