"""Propose two deterministic Green Ridge regions without promoting labels."""

from __future__ import annotations

from collections import deque
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from typing import Any, Iterator

import numpy as np
from PIL import Image, ImageDraw
import rasterio

from .green_ridge_background_evidence import WARNING, build_report as build_background_report
from .label_proposal import dilate_mask
from .optical_pair_evidence import _font, _write_utf8_lf
from .region_candidate_pilot import _align_tci_to_grid


SOFTWARE_VERSION = "0.36.0"
REPORT_ID = "GREEN-RIDGE-REGION-PROPOSAL-2026-001"
REPORT_VERSION = "green-ridge-no-promotion-region-proposal-v0.1.0"
GENERATOR_VERSION = "green-ridge-region-generator-v0.1.0"
TASK_ISSUE = 483
DNBR_BIN_WIDTH = 0.05
DNBR_OFFSET = 2.0
TARGET_PIXELS = 25
MIN_PIXELS = 2
MAX_PIXELS = 250
PIXEL_AREA_HA = 0.04


class GreenRidgeRegionProposalError(RuntimeError):
    """The Green Ridge proposal failed closed."""


def _components(mask: np.ndarray) -> Iterator[np.ndarray]:
    seen = np.zeros(mask.shape, dtype=bool)
    height, width = mask.shape
    for start_row, start_column in zip(*np.where(mask), strict=True):
        if seen[start_row, start_column]:
            continue
        component = np.zeros(mask.shape, dtype=bool)
        queue: deque[tuple[int, int]] = deque([(int(start_row), int(start_column))])
        seen[start_row, start_column] = True
        component[start_row, start_column] = True
        while queue:
            row, column = queue.popleft()
            for row_delta in (-1, 0, 1):
                for column_delta in (-1, 0, 1):
                    if row_delta == 0 and column_delta == 0:
                        continue
                    next_row, next_column = row + row_delta, column + column_delta
                    if (
                        0 <= next_row < height
                        and 0 <= next_column < width
                        and mask[next_row, next_column]
                        and not seen[next_row, next_column]
                    ):
                        seen[next_row, next_column] = True
                        component[next_row, next_column] = True
                        queue.append((next_row, next_column))
        yield component


def _bbox(mask: np.ndarray) -> list[int]:
    rows, columns = np.where(mask)
    if not len(rows):
        raise GreenRidgeRegionProposalError("empty candidate component")
    return [int(rows.min()), int(columns.min()), int(rows.max()) + 1, int(columns.max()) + 1]


def _tie_digest(candidate_class: str, bucket: int, component: np.ndarray) -> str:
    rows, columns = np.where(component)
    digest = sha256(f"{candidate_class}|{bucket}|".encode("ascii"))
    digest.update(np.column_stack((rows, columns)).astype("<i4").tobytes())
    return digest.hexdigest()


def select_region(candidate_class: str, route: np.ndarray, values: np.ndarray) -> dict[str, Any]:
    if route.shape != values.shape:
        raise GreenRidgeRegionProposalError("route/value grid mismatch")
    finite_route = route & np.isfinite(values)
    buckets = np.full(values.shape, -32768, dtype=np.int16)
    buckets[finite_route] = np.floor((values[finite_route] + DNBR_OFFSET) / DNBR_BIN_WIDTH).astype(np.int16)
    evaluated = 0
    eligible: list[tuple[tuple[int, str], int, np.ndarray]] = []
    for bucket in sorted(int(value) for value in np.unique(buckets[finite_route])):
        for component in _components(finite_route & (buckets == bucket)):
            evaluated += 1
            pixels = int(component.sum())
            if MIN_PIXELS <= pixels <= MAX_PIXELS:
                eligible.append(((abs(pixels - TARGET_PIXELS), _tie_digest(candidate_class, bucket, component)), bucket, component))
    if not eligible:
        raise GreenRidgeRegionProposalError(f"no eligible {candidate_class} component")
    _, bucket, core = min(eligible, key=lambda item: item[0])
    ring = dilate_mask(core, 1) & ~core
    if not ring.any():
        raise GreenRidgeRegionProposalError("candidate has no unknown ring")
    selected_values = values[core]
    return {
        "candidate_class": candidate_class,
        "core": core,
        "ring": ring,
        "bbox": _bbox(core | ring),
        "bucket": bucket,
        "core_pixels": int(core.sum()),
        "ring_pixels": int(ring.sum()),
        "dnbr_interval": [round(bucket * DNBR_BIN_WIDTH - DNBR_OFFSET, 6), round((bucket + 1) * DNBR_BIN_WIDTH - DNBR_OFFSET, 6)],
        "dnbr_observed": {"min": round(float(selected_values.min()), 6), "max": round(float(selected_values.max()), 6), "mean": round(float(selected_values.mean()), 6)},
        "eligible_component_count": len(eligible),
        "evaluated_component_count": evaluated,
        "selection_tie_sha256": _tie_digest(candidate_class, bucket, core),
    }


def build_report(
    *, original_package: Path, extended_package: Path, plan_path: Path,
    reference_archive: Path, generated_at_utc: str, run_id: str, git_source_commit: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    source_report, previews = build_background_report(
        original_package=original_package, extended_package=extended_package,
        plan_path=plan_path, reference_archive=reference_archive,
        generated_at_utc=generated_at_utc, run_id=f"{run_id}-source-reverification",
        git_source_commit=git_source_commit,
    )
    burned_route = (
        np.isin(previews["mtbs_dnbr6"], (2, 3, 4))
        & np.isin(previews["ravg_cbi4"], (2, 3, 4))
        & np.isfinite(previews["pre_post_dnbr"])
    )
    background_route = previews["route"]
    selected = [
        select_region("burned", burned_route, previews["pre_post_dnbr"]),
        select_region("background", background_route, previews["dnbr"]),
    ]
    for index, item in enumerate(selected, start=1):
        item["candidate_id"] = f"GRP-{index:03d}"
    if np.any((selected[0]["core"] | selected[0]["ring"]) & (selected[1]["core"] | selected[1]["ring"])):
        raise GreenRidgeRegionProposalError("candidate core/ring footprints overlap")
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
        "output_label_set_version": None,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "source_report": {"report_id": source_report["report_id"], "run_id": source_report["run_id"], "checkpoint": source_report["fitness_decision"]["checkpoint"]},
        "method": {
            "unit": "one intact 8-connected 20 m component",
            "partition": "fixed 0.05 dNBR bin from the established region-candidate protocol",
            "target_pixels": TARGET_PIXELS,
            "selection": "minimum absolute distance to 25 pixels, then SHA-256 of class, bin, and ordered native-grid coordinates",
            "burned_route": "MTBS dNBR6 classes 2-4 and RAVG CBI4 classes 2-4 agree; pre/post dNBR is finite",
            "background_route": source_report["route_evidence"]["rule"],
            "unknown_ring": "one native 20 m pixel around the intact core; never promoted by this checkpoint",
        },
        "summary": {"candidate_count": 2, "class_counts": {"burned": 1, "background": 1}, "core_pixels": sum(item["core_pixels"] for item in selected), "unknown_ring_pixels": sum(item["ring_pixels"] for item in selected), "owner_responses": 0, "labels_created": 0},
        "candidates": public_candidates,
        "decision": "PROPOSE_TWO_GREEN_RIDGE_REGIONS_KEEP_OWNER_REVIEW_AND_PROMOTION_CLOSED",
        "next_gate": "Build a separately versioned blank owner yes/no/uncertain review surface bound to these exact raster bytes.",
        "limitations": [
            "The fixed dNBR partition is an evidence-coherence rule, not a universal burn or severity threshold.",
            "MTBS/RAVG agreement and the multi-signal background route are candidate evidence, not independent ground truth.",
            "Only one burned and one background proposal are created for one event; owner review remains absent.",
        ],
        "warning": WARNING,
    }
    return report, selected, previews


def _aligned_tci(previews: dict[str, Any], key: str) -> Image.Image:
    transform = previews["grid_transform"]
    aligned = _align_tci_to_grid(
        previews[key],
        rasterio.Affine(transform.a / 2, 0, transform.c, 0, transform.e / 2, transform.f),
        transform, previews["route"].shape, "EPSG:32610",
    )
    return Image.fromarray(np.moveaxis(aligned, 0, 2).astype(np.uint8), mode="RGB")


def _evidence_image(values: np.ndarray, mode: str) -> Image.Image:
    if mode == "dnbr":
        normalized = np.nan_to_num(np.clip((values + 0.25) / 1.25, 0, 1), nan=0.0)
        rgb = np.dstack((255 * normalized, 120 * (1 - np.abs(normalized - 0.5) * 2), 255 * (1 - normalized))).astype(np.uint8)
    else:
        rgb = np.zeros((*values.shape, 3), dtype=np.uint8)
        rgb[:] = (55, 68, 63)
        rgb[np.isin(values, (2, 3, 4))] = (230, 91, 54)
        rgb[values == 0] = (72, 150, 124)
        rgb[values == 1] = (194, 175, 88)
    return Image.fromarray(rgb, mode="RGB")


def _panel(source: Image.Image, item: dict[str, Any], size: tuple[int, int]) -> Image.Image:
    core, ring = item["core"], item["ring"]
    rgba = source.convert("RGBA")
    layer = np.zeros((*core.shape, 4), dtype=np.uint8)
    layer[core] = (234, 76, 42, 165) if item["candidate_class"] == "burned" else (34, 190, 150, 165)
    layer[ring] = (242, 190, 70, 175)
    rgba = Image.alpha_composite(rgba, Image.fromarray(layer, mode="RGBA"))
    top, left, bottom, right = item["bbox"]
    padding = 8
    crop = rgba.crop((max(0, left-padding), max(0, top-padding), min(core.shape[1], right+padding), min(core.shape[0], bottom+padding)))
    return crop.resize(size, Image.Resampling.NEAREST).convert("RGB")


def render_png(report: dict[str, Any], selected: list[dict[str, Any]], previews: dict[str, Any], path: Path) -> None:
    canvas = Image.new("RGB", (1800, 900), "#07110f")
    draw = ImageDraw.Draw(canvas)
    draw.text((55, 35), "BURNLENS / GREEN RIDGE REGION PROPOSAL", fill="#b9d8cf", font=_font(22))
    draw.text((55, 76), "Two intact review candidates; zero owner responses or labels.", fill="#eef7f3", font=_font(30))
    pre, post, extended = (_aligned_tci(previews, key) for key in ("pre_tci", "post_tci", "extended_tci"))
    agreement = np.full(previews["route"].shape, 255, dtype=np.uint8)
    agreement[(previews["mtbs_dnbr6"] == 0) & (previews["ravg_cbi4"] == 0)] = 0
    agreement[
        np.isin(previews["mtbs_dnbr6"], (2, 3, 4))
        & np.isin(previews["ravg_cbi4"], (2, 3, 4))
    ] = 2
    for row, item in enumerate(selected):
        top = 145 + row * 330
        draw.rounded_rectangle((45, top, 1755, top + 300), radius=15, fill="#0e1d1a", outline="#315b50", width=2)
        draw.text((65, top + 18), f"{item['candidate_id']} / proposed {item['candidate_class']} / core {item['core_pixels']} px / unknown ring {item['ring_pixels']} px", fill="#eef7f3", font=_font(18))
        values = previews["pre_post_dnbr"] if item["candidate_class"] == "burned" else previews["dnbr"]
        sources = (pre, post if item["candidate_class"] == "burned" else extended, _evidence_image(values, "dnbr"), _evidence_image(agreement, "reference"))
        labels = ("pre 2020", "post 2020" if item["candidate_class"] == "burned" else "extended 2021", "fixed-bin dNBR", "MTBS + RAVG agreement")
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
    html = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Green Ridge region proposal</title><style>body{{margin:0;background:#07110f;color:#eef7f3;font:16px/1.5 system-ui}}main{{max-width:1200px;margin:auto;padding:30px}}img{{width:100%;height:auto}}.card{{background:#0e1d1a;border:1px solid #315b50;border-radius:14px;padding:18px;margin:18px 0}}.warn{{color:#ffd997}}table{{width:100%;border-collapse:collapse}}th,td{{padding:10px;border-bottom:1px solid #315b50;text-align:left}}a{{color:#78e0bd}}</style></head><body><main><p>BURNLENS / PHASE TWO / ISSUE #483</p><h1>Two Green Ridge regions are proposed; neither is a label.</h1><p class='card warn'>{escape(report['warning'])}</p><img src='{REPORT_ID}.png' width='1800' height='900' alt='Actual optical, dNBR, official-reference, candidate-core, and unknown-ring evidence'><div class='card'><strong>2</strong> unreviewed candidates · <strong>0</strong> owner responses · <strong>0</strong> labels</div><div class='card'><table><thead><tr><th>ID</th><th>Proposed class</th><th>Core pixels</th><th>Unknown ring</th><th>Output</th></tr></thead><tbody>{rows}</tbody></table></div><div class='card'><h2>Decision</h2><p>{escape(report['decision'])}</p><p>{escape(report['next_gate'])}</p></div><p>Trace: <code>{escape(report['git_source_commit'])}</code> · run <code>{escape(report['run_id'])}</code> · BurnLens {SOFTWARE_VERSION} · dataset/model none.</p></main></body></html>"""
    _write_utf8_lf(path, html)


def write_outputs(report: dict[str, Any], selected: list[dict[str, Any]], previews: dict[str, Any], directory: Path) -> list[Path]:
    if directory.exists():
        raise GreenRidgeRegionProposalError("output directory already exists")
    directory.mkdir(parents=True)
    outputs: list[Path] = []
    transform = previews["grid_transform"]
    for item in selected:
        path = directory / f"{REPORT_ID}-{item['candidate_id']}.tif"
        array = np.zeros(item["core"].shape, dtype=np.uint8)
        array[item["core"]] = 1
        array[item["ring"]] = 2
        with rasterio.open(path, "w", driver="GTiff", width=array.shape[1], height=array.shape[0], count=1, dtype="uint8", crs="EPSG:32610", transform=transform, nodata=255, compress="DEFLATE", predictor=2) as dataset:
            dataset.write(array, 1)
            dataset.update_tags(candidate_id=item["candidate_id"], proposed_class=item["candidate_class"], kind="unreviewed-core-and-unknown-ring", generator_version=GENERATOR_VERSION, run_id=report["run_id"], git_source_commit=report["git_source_commit"], label_created="false")
        outputs.append(path)
    png_path = directory / f"{REPORT_ID}.png"
    html_path = directory / f"{REPORT_ID}.html"
    json_path = directory / f"{REPORT_ID}.json"
    render_png(report, selected, previews, png_path)
    render_html(report, html_path)
    _write_utf8_lf(json_path, json.dumps(report, indent=2) + "\n")
    return [json_path, html_path, png_path, *outputs]
