"""Propose two deterministic Grandview regions without promoting labels."""

from __future__ import annotations

from html import escape
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw
import rasterio

from .grandview_background_evidence import WARNING, build_report as build_background_report
from .green_ridge_region_proposal import (
    PIXEL_AREA_HA,
    TARGET_PIXELS,
    GreenRidgeRegionProposalError,
    _aligned_tci,
    _evidence_image,
    _panel,
    select_region,
)
from .optical_pair_evidence import _font, _write_utf8_lf


SOFTWARE_VERSION = "0.42.0"
REPORT_ID = "GRANDVIEW-REGION-PROPOSAL-2026-001"
REPORT_VERSION = "grandview-no-promotion-region-proposal-v0.1.0"
GENERATOR_VERSION = "grandview-region-generator-v0.1.0"
TASK_ISSUE = 508


class GrandviewRegionProposalError(RuntimeError):
    """The Grandview proposal failed closed."""


def build_report(
    *,
    original_package: Path,
    extended_package: Path,
    plan_path: Path,
    reference_archive: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    source_report, previews = build_background_report(
        original_package=original_package,
        extended_package=extended_package,
        plan_path=plan_path,
        reference_archive=reference_archive,
        generated_at_utc=generated_at_utc,
        run_id=f"{run_id}-source-reverification",
        git_source_commit=git_source_commit,
    )
    burned_route = np.isin(previews["mtbs_dnbr6"], (2, 3, 4)) & np.isfinite(
        previews["pre_post_dnbr"]
    )
    background_route = previews["route"]
    try:
        selected = [
            select_region("burned", burned_route, previews["pre_post_dnbr"]),
            select_region("background", background_route, previews["dnbr"]),
        ]
    except GreenRidgeRegionProposalError as error:
        raise GrandviewRegionProposalError(str(error)) from error
    for index, item in enumerate(selected, start=1):
        item["candidate_id"] = f"GVP-{index:03d}"
    if np.any(
        (selected[0]["core"] | selected[0]["ring"])
        & (selected[1]["core"] | selected[1]["ring"])
    ):
        raise GrandviewRegionProposalError("candidate core/ring footprints overlap")
    public_candidates = [
        {
            "candidate_id": item["candidate_id"],
            "candidate_class": item["candidate_class"],
            "review_state": "unreviewed-no-promotion",
            "core_pixels": item["core_pixels"],
            "core_area_hectares": round(item["core_pixels"] * PIXEL_AREA_HA, 4),
            "unknown_ring_pixels": item["ring_pixels"],
            "bbox_rows_columns": item["bbox"],
            "dnbr_interval": item["dnbr_interval"],
            "dnbr_observed": item["dnbr_observed"],
            "eligible_component_count": item["eligible_component_count"],
            "evaluated_component_count": item["evaluated_component_count"],
            "selection_tie_sha256": item["selection_tie_sha256"],
            "candidate_raster": f"{REPORT_ID}-{item['candidate_id']}.tif",
            "owner_decision": None,
        }
        for item in selected
    ]
    report = {
        "report_id": REPORT_ID,
        "report_version": REPORT_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "event_group_id": source_report["event"]["event_group_id"],
        "event_id": source_report["event"]["event_id"],
        "target_version": source_report["trace"]["target_version"],
        "label_schema_version": source_report["trace"]["label_schema_version"],
        "input_label_set_version": source_report["trace"]["label_set_version"],
        "output_label_set_version": None,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "source_report": {
            "report_id": source_report["report_id"],
            "run_id": source_report["run_id"],
            "checkpoint": source_report["fitness_decision"]["checkpoint"],
        },
        "method": {
            "unit": "one intact 8-connected 20 m component",
            "partition": "fixed 0.05 dNBR bin from the established region-candidate protocol",
            "target_pixels": TARGET_PIXELS,
            "selection": "minimum absolute distance to 25 pixels, then SHA-256 of class, bin, and ordered native-grid coordinates",
            "burned_route": "MTBS dNBR6 classes 2-4 on the verified context grid and finite pre/post dNBR; RAVG classes are not used",
            "background_route": source_report["route_evidence"]["rule"],
            "unknown_ring": "one native 20 m pixel around the intact core; never promoted by this checkpoint",
        },
        "summary": {
            "candidate_count": 2,
            "class_counts": {"burned": 1, "background": 1},
            "core_pixels": sum(item["core_pixels"] for item in selected),
            "unknown_ring_pixels": sum(item["ring_pixels"] for item in selected),
            "owner_responses": 0,
            "labels_created": 0,
        },
        "candidates": public_candidates,
        "decision": "PROPOSE_TWO_GRANDVIEW_REGIONS_KEEP_OWNER_REVIEW_AND_PROMOTION_CLOSED",
        "next_gate": "Build a separately versioned blank owner yes/no/uncertain review surface bound to these exact raster bytes.",
        "limitations": [
            "The fixed dNBR partition is an evidence-coherence rule, not a universal burn or severity threshold.",
            "MTBS classes 2-4 and the multi-signal background route are candidate evidence, not independent ground truth.",
            "RAVG modeled classes are excluded from affirmative candidate logic under the delivered sparse/non-tree warning.",
            "Only one burned and one background proposal are created for one event; owner review remains absent.",
        ],
        "warning": WARNING,
    }
    return report, selected, previews


def render_png(
    report: dict[str, Any],
    selected: list[dict[str, Any]],
    previews: dict[str, Any],
    path: Path,
) -> None:
    canvas = Image.new("RGB", (1800, 900), "#07110f")
    draw = ImageDraw.Draw(canvas)
    draw.text((55, 35), "BURNLENS / GRANDVIEW REGION PROPOSAL", fill="#b9d8cf", font=_font(22))
    draw.text((55, 76), "Two intact review candidates; zero owner responses or labels.", fill="#eef7f3", font=_font(30))
    pre, post, extended = (
        _aligned_tci(previews, key) for key in ("pre_tci", "post_tci", "extended_tci")
    )
    for row, item in enumerate(selected):
        top = 145 + row * 330
        draw.rounded_rectangle((45, top, 1755, top + 300), radius=15, fill="#0e1d1a", outline="#315b50", width=2)
        draw.text(
            (65, top + 18),
            f"{item['candidate_id']} / proposed {item['candidate_class']} / core {item['core_pixels']} px / unknown ring {item['ring_pixels']} px",
            fill="#eef7f3",
            font=_font(18),
        )
        if item["candidate_class"] == "burned":
            values = previews["pre_post_dnbr"]
            sources = (pre, post, _evidence_image(values, "dnbr"), _evidence_image(previews["mtbs_dnbr6"], "reference"))
            labels = ("pre 2021", "post 2021", "fixed-bin pre/post dNBR", "MTBS classes 2-4")
        else:
            values = previews["dnbr"]
            sources = (pre, extended, _evidence_image(values, "dnbr"), _evidence_image(previews["route"].astype(np.uint8) * 2, "reference"))
            labels = ("pre 2021", "extended 2022", "fixed-bin anniversary dNBR", "affirmative background route")
        for column, (source, label) in enumerate(zip(sources, labels, strict=True)):
            left = 65 + column * 420
            canvas.paste(_panel(source, item, (380, 210)), (left, top + 62))
            draw.text((left, top + 274), label, fill="#b9d8cf", font=_font(14))
    draw.text((55, 825), report["warning"], fill="#ffd997", font=_font(14))
    draw.text((55, 858), f"TRACE {report['git_source_commit'][:12]} / {report['run_id']} / BurnLens {SOFTWARE_VERSION} / labels-dataset-model none", fill="#b9d8cf", font=_font(13))
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], path: Path) -> None:
    rows = "".join(
        f"<tr><td>{escape(item['candidate_id'])}</td><td>{escape(item['candidate_class'])}</td><td>{item['core_pixels']}</td><td>{item['unknown_ring_pixels']}</td><td><a href='{escape(item['candidate_raster'])}'>raster</a></td></tr>"
        for item in report["candidates"]
    )
    html = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Grandview region proposal</title><style>body{{margin:0;background:#07110f;color:#eef7f3;font:16px/1.5 system-ui}}main{{max-width:1200px;margin:auto;padding:30px}}img{{width:100%;height:auto}}.card{{background:#0e1d1a;border:1px solid #315b50;border-radius:14px;padding:18px;margin:18px 0}}.warn{{color:#ffd997}}table{{width:100%;border-collapse:collapse}}th,td{{padding:10px;border-bottom:1px solid #315b50;text-align:left}}a{{color:#78e0bd}}</style></head><body><main><p>BURNLENS / PHASE TWO / ISSUE #508</p><h1>Two Grandview regions are proposed; neither is a label.</h1><p class='card warn'>{escape(report['warning'])}</p><img src='{REPORT_ID}.png' width='1800' height='900' alt='Actual optical, dNBR, official-reference, candidate-core, and unknown-ring evidence'><div class='card'><strong>2</strong> unreviewed candidates · <strong>0</strong> owner responses · <strong>0</strong> labels</div><div class='card'><table><thead><tr><th>ID</th><th>Proposed class</th><th>Core pixels</th><th>Unknown ring</th><th>Output</th></tr></thead><tbody>{rows}</tbody></table></div><div class='card'><h2>Decision</h2><p>{escape(report['decision'])}</p><p>{escape(report['next_gate'])}</p></div><p>Trace: <code>{escape(report['git_source_commit'])}</code> · run <code>{escape(report['run_id'])}</code> · BurnLens {SOFTWARE_VERSION} · dataset/model none.</p></main></body></html>"""
    _write_utf8_lf(path, html)


def write_outputs(
    report: dict[str, Any],
    selected: list[dict[str, Any]],
    previews: dict[str, Any],
    directory: Path,
) -> list[Path]:
    if directory.exists():
        raise GrandviewRegionProposalError("output directory already exists")
    directory.mkdir(parents=True)
    outputs: list[Path] = []
    transform = previews["grid_transform"]
    for item in selected:
        path = directory / f"{REPORT_ID}-{item['candidate_id']}.tif"
        array = np.zeros(item["core"].shape, dtype=np.uint8)
        array[item["core"]] = 1
        array[item["ring"]] = 2
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
                candidate_id=item["candidate_id"],
                proposed_class=item["candidate_class"],
                kind="unreviewed-core-and-unknown-ring",
                generator_version=GENERATOR_VERSION,
                run_id=report["run_id"],
                git_source_commit=report["git_source_commit"],
                label_created="false",
            )
        outputs.append(path)
    png_path = directory / f"{REPORT_ID}.png"
    html_path = directory / f"{REPORT_ID}.html"
    json_path = directory / f"{REPORT_ID}.json"
    render_png(report, selected, previews, png_path)
    render_html(report, html_path)
    _write_utf8_lf(json_path, json.dumps(report, indent=2) + "\n")
    return [json_path, html_path, png_path, *outputs]
