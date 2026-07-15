"""Build a bounded five-state burn-scar label proposal from the exact optical pair.

This module creates candidate labels for review, not a dataset or accepted ground
truth.  It preserves uncertainty in a companion state raster and requires a
separately invoked QA implementation before any proposal-level acceptance.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import rasterio
from rasterio.features import rasterize
from rasterio.transform import Affine
from rasterio.warp import transform_geom

from .content_registration import REGISTRATION_PROTOCOL_VERSION
from .optical_pair_contract import (
    CONTRACT_VERSION,
    OPTICAL_CONTRACTS,
    PACKAGE_ID,
    TERMS_REVIEW_ID,
    validate_optical_contracts,
)
from .optical_pair_evidence import (
    AOI_VERSION,
    LABEL_PROTOCOL_VERSION,
    TARGET_VERSION,
    WARNING,
    _read_scene,
    _reflectance,
)
from .paired_intake import verify_registered_package


SOFTWARE_VERSION = "0.9.0"
REPORT_ID = "LABEL-PROPOSAL-2026-001"
REPORT_SCHEMA_VERSION = "0.1.0"
REPORT_VERSION = "burn-scar-label-proposal-evidence-v0.1.0"
LABEL_SCHEMA_VERSION = "burn-scar-five-state-schema-v0.1.0"
LABEL_PROPOSAL_VERSION = "darlene3-burn-scar-label-proposal-v0.1.0"
PIXEL_SIZE_M = 20
WIDTH = 600
HEIGHT = 450
IGNORE_VALUE = 255

STATE_CODES = {
    "background-candidate": 0,
    "burned": 1,
    "unknown": 2,
    "excluded": 3,
    "review-needed": 4,
}
STATE_NAMES = {value: key for key, value in STATE_CODES.items()}
STATE_COLORS = {
    0: (0, 107, 100),
    1: (240, 90, 40),
    2: (233, 196, 106),
    3: (86, 95, 91),
    4: (126, 63, 143),
}

# Frozen proposal-screen thresholds for this exact pair.  They are conservative
# evidence rules, not universal fire/severity thresholds or field calibration.
BURN_DNBR_MIN = 0.10
BURN_NDVI_LOSS_MIN = 0.05
BURN_SWIR_GAIN_MIN = 0.02
BURN_NIR_LOSS_MIN = 0.02
BURN_SUPPORTING_SIGNALS_MIN = 2
BURN_NEIGHBOR_SUPPORT_MIN = 5
STABLE_ABS_DNBR_MAX = 0.03
STABLE_ABS_NDVI_CHANGE_MAX = 0.03
STABLE_ABS_SWIR_CHANGE_MAX = 0.01
STABLE_ABS_NIR_CHANGE_MAX = 0.01
STABLE_NEIGHBOR_SUPPORT_MIN = 7
BOUNDARY_REVIEW_PX = 1

PRIMARY_SOURCES = (
    "https://sentiwiki.copernicus.eu/web/s2-processing",
    "https://sentiwiki.copernicus.eu/__attachments/1672112/OMPC.CS.DQR.002.02-2026-i95r0-MSI-L2A-DQR-March-2026.pdf",
    "https://www.mtbs.gov/mapping-methods",
    "https://www.mtbs.gov/faqs",
    "https://www.fs.usda.gov/rm/pubs_series/rmrs/gtr/rmrs_gtr164.pdf",
    "https://cds.climate.copernicus.eu/licences/ec-sentinel",
)


class LabelProposalError(RuntimeError):
    """A deterministic, secret-free proposal failure."""


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return ImageFont.load_default(size=size)


def _write_utf8_lf(path: Path, text: str) -> None:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    path.write_bytes(normalized.encode("utf-8"))


def _sha256_lf_text(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", newline=None) as handle:
            return sha256(handle.read().encode("utf-8")).hexdigest()
    except (OSError, UnicodeError) as error:
        raise LabelProposalError(f"invalid UTF-8 input {path.name}") from error


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def dilate_mask(mask: np.ndarray, iterations: int = 1) -> np.ndarray:
    """Eight-neighbor binary dilation without an additional dependency."""
    if mask.ndim != 2 or iterations < 0:
        raise LabelProposalError("invalid mask dilation request")
    output = mask.astype(bool, copy=True)
    rows, columns = output.shape
    for _ in range(iterations):
        padded = np.pad(output, 1, mode="constant", constant_values=False)
        output = np.logical_or.reduce(
            [padded[row : row + rows, column : column + columns] for row in range(3) for column in range(3)]
        )
    return output


def erode_mask(mask: np.ndarray, iterations: int = 1) -> np.ndarray:
    """Eight-neighbor binary erosion paired with :func:`dilate_mask`."""
    if mask.ndim != 2 or iterations < 0:
        raise LabelProposalError("invalid mask erosion request")
    return ~dilate_mask(~mask.astype(bool), iterations)


def boundary_band(mask: np.ndarray) -> np.ndarray:
    """Return a one-pixel two-sided transition band."""
    return dilate_mask(mask, BOUNDARY_REVIEW_PX) & dilate_mask(~mask, BOUNDARY_REVIEW_PX)


def neighbor_support(mask: np.ndarray) -> np.ndarray:
    """Count supporting pixels in each clipped 3 by 3 neighborhood."""
    if mask.ndim != 2:
        raise LabelProposalError("invalid neighborhood-support mask")
    rows, columns = mask.shape
    padded = np.pad(mask.astype(np.uint8), 1, mode="constant", constant_values=0)
    return sum(
        (padded[row : row + rows, column : column + columns] for row in range(3) for column in range(3)),
        start=np.zeros((rows, columns), dtype=np.uint8),
    )


def _normalized_difference(
    scene: dict[str, Any], arrays: dict[str, np.ndarray], first: str, second: str
) -> tuple[np.ndarray, np.ndarray]:
    first_values, first_valid = _reflectance(scene, arrays, first)
    second_values, second_valid = _reflectance(scene, arrays, second)
    denominator = first_values + second_values
    valid = first_valid & second_valid & np.isfinite(denominator) & (np.abs(denominator) > 1e-6)
    result = np.full(first_values.shape, np.nan, dtype=np.float32)
    result[valid] = (first_values[valid] - second_values[valid]) / denominator[valid]
    return result, valid


def spectral_evidence(
    pre_scene: dict[str, Any],
    pre: dict[str, np.ndarray],
    post_scene: dict[str, Any],
    post: dict[str, np.ndarray],
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Compute four independent, native-grid change signals."""
    pre_nbr, pre_nbr_valid = _normalized_difference(pre_scene, pre, "B8A", "B12")
    post_nbr, post_nbr_valid = _normalized_difference(post_scene, post, "B8A", "B12")
    pre_ndvi, pre_ndvi_valid = _normalized_difference(pre_scene, pre, "B8A", "B04")
    post_ndvi, post_ndvi_valid = _normalized_difference(post_scene, post, "B8A", "B04")
    pre_swir, pre_swir_valid = _reflectance(pre_scene, pre, "B12")
    post_swir, post_swir_valid = _reflectance(post_scene, post, "B12")
    pre_nir, pre_nir_valid = _reflectance(pre_scene, pre, "B8A")
    post_nir, post_nir_valid = _reflectance(post_scene, post, "B8A")
    values = {
        "dnbr": pre_nbr - post_nbr,
        "ndvi_loss": pre_ndvi - post_ndvi,
        "swir_gain": post_swir - pre_swir,
        "nir_loss": pre_nir - post_nir,
    }
    valid = (
        pre_nbr_valid
        & post_nbr_valid
        & pre_ndvi_valid
        & post_ndvi_valid
        & pre_swir_valid
        & post_swir_valid
        & pre_nir_valid
        & post_nir_valid
    )
    valid &= np.logical_and.reduce([np.isfinite(item) for item in values.values()])
    return values, valid


def classify_label_states(
    *,
    pair_quality: np.ndarray,
    reference_mask: np.ndarray,
    evidence: dict[str, np.ndarray],
    numeric_valid: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    """Apply the frozen proposal rules while preserving all uncertainty states."""
    expected_shape = (HEIGHT, WIDTH)
    if pair_quality.shape != expected_shape or reference_mask.shape != expected_shape:
        raise LabelProposalError("proposal inputs do not match the frozen native 20 m grid")
    if numeric_valid.shape != expected_shape or any(value.shape != expected_shape for value in evidence.values()):
        raise LabelProposalError("spectral evidence does not match the frozen grid")
    if set(int(value) for value in np.unique(pair_quality)) - {0, 1, 2}:
        raise LabelProposalError("pair quality contains an unknown state")

    dnbr = evidence["dnbr"]
    ndvi_loss = evidence["ndvi_loss"]
    swir_gain = evidence["swir_gain"]
    nir_loss = evidence["nir_loss"]
    usable = (pair_quality == 0) & numeric_valid
    excluded = (pair_quality == 2) | ~numeric_valid
    quality_review = (pair_quality == 1) & numeric_valid

    support_count = (
        (ndvi_loss >= BURN_NDVI_LOSS_MIN).astype(np.uint8)
        + (swir_gain >= BURN_SWIR_GAIN_MIN).astype(np.uint8)
        + (nir_loss >= BURN_NIR_LOSS_MIN).astype(np.uint8)
    )
    burn_evidence = (dnbr >= BURN_DNBR_MIN) & (support_count >= BURN_SUPPORTING_SIGNALS_MIN)
    stable_evidence = (
        (np.abs(dnbr) <= STABLE_ABS_DNBR_MAX)
        & (np.abs(ndvi_loss) <= STABLE_ABS_NDVI_CHANGE_MAX)
        & (np.abs(swir_gain) <= STABLE_ABS_SWIR_CHANGE_MAX)
        & (np.abs(nir_loss) <= STABLE_ABS_NIR_CHANGE_MAX)
    )
    burn_coherent = burn_evidence & (neighbor_support(burn_evidence) >= BURN_NEIGHBOR_SUPPORT_MIN)
    stable_coherent = stable_evidence & (neighbor_support(stable_evidence) >= STABLE_NEIGHBOR_SUPPORT_MIN)

    reference_core = erode_mask(reference_mask, BOUNDARY_REVIEW_PX)
    reference_outer = dilate_mask(reference_mask, BOUNDARY_REVIEW_PX)
    reference_boundary = reference_outer & ~reference_core
    burned_raw = usable & reference_core & burn_coherent
    background_raw = usable & ~reference_outer & stable_coherent
    source_conflict = usable & ((~reference_mask & burn_coherent) | (reference_mask & stable_coherent))
    burned_boundary = usable & boundary_band(burned_raw)
    review = quality_review | reference_boundary | source_conflict | burned_boundary

    states = np.full(expected_shape, STATE_CODES["unknown"], dtype=np.uint8)
    states[excluded] = STATE_CODES["excluded"]
    states[review & ~excluded] = STATE_CODES["review-needed"]
    states[burned_raw & ~review & ~excluded] = STATE_CODES["burned"]
    states[background_raw & ~review & ~excluded] = STATE_CODES["background-candidate"]

    target = np.full(expected_shape, IGNORE_VALUE, dtype=np.uint8)
    target[states == STATE_CODES["background-candidate"]] = 0
    target[states == STATE_CODES["burned"]] = 1
    if np.any((target != IGNORE_VALUE) & ~np.isin(states, [0, 1])):
        raise LabelProposalError("ignored state entered the candidate target")
    if np.any((states == 0) & (target != 0)) or np.any((states == 1) & (target != 1)):
        raise LabelProposalError("state and target rasters disagree")

    masks = {
        "usable": usable,
        "excluded": excluded,
        "quality_review": quality_review,
        "burn_evidence": burn_evidence,
        "burn_coherent": burn_coherent,
        "stable_evidence": stable_evidence,
        "stable_coherent": stable_coherent,
        "reference_core": reference_core,
        "reference_boundary": reference_boundary,
        "burned_raw": burned_raw,
        "background_raw": background_raw,
        "source_conflict": source_conflict,
        "burned_boundary": burned_boundary,
        "review": review,
    }
    return states, target, masks


def summarize_states(states: np.ndarray) -> dict[str, Any]:
    if states.shape != (HEIGHT, WIDTH):
        raise LabelProposalError("state summary received an invalid raster")
    counts = Counter(int(value) for value in states.reshape(-1))
    if set(counts) != set(STATE_NAMES):
        missing = sorted(set(STATE_NAMES) - set(counts))
        raise LabelProposalError(f"proposal does not represent every required state: {missing}")
    total = int(states.size)
    rows = [
        {
            "state": STATE_NAMES[code],
            "code": code,
            "pixels": counts[code],
            "percent": round(100 * counts[code] / total, 4),
            "target_value": code if code in {0, 1} else None,
        }
        for code in sorted(STATE_NAMES)
    ]
    labeled = counts[0] + counts[1]
    return {
        "pixel_count": total,
        "states": rows,
        "candidate_target_pixels": labeled,
        "candidate_target_percent": round(100 * labeled / total, 4),
        "ignored_pixels": total - labeled,
        "ignored_percent": round(100 * (total - labeled) / total, 4),
        "machine_decision": "PROPOSAL_READY_FOR_SEPARATE_QA",
    }


def _write_raster(
    path: Path,
    values: np.ndarray,
    transform: Affine,
    *,
    nodata: int | None,
    kind: str,
    run_id: str,
    git_source_commit: str,
) -> None:
    profile: dict[str, Any] = {
        "driver": "GTiff",
        "width": WIDTH,
        "height": HEIGHT,
        "count": 1,
        "dtype": "uint8",
        "crs": "EPSG:32610",
        "transform": transform,
        "compress": "DEFLATE",
        "predictor": 2,
        "zlevel": 9,
        "tiled": True,
        "blockxsize": 256,
        "blockysize": 256,
    }
    if nodata is not None:
        profile["nodata"] = nodata
    with rasterio.open(path, "w", **profile) as target:
        target.write(values, 1)
        target.update_tags(
            repository="drwbkr1/burnlens-deschutes",
            artifact_kind=kind,
            software_version=SOFTWARE_VERSION,
            aoi_version=AOI_VERSION,
            target_version=TARGET_VERSION,
            label_protocol_version=LABEL_PROTOCOL_VERSION,
            label_schema_version=LABEL_SCHEMA_VERSION,
            label_proposal_version=LABEL_PROPOSAL_VERSION,
            run_id=run_id,
            git_source_commit=git_source_commit,
            source_precedence="official sources govern",
        )


def _raster_metadata(path: Path, *, nodata: int | None) -> dict[str, Any]:
    with rasterio.open(path) as source:
        if (
            source.count != 1
            or source.width != WIDTH
            or source.height != HEIGHT
            or source.dtypes != ("uint8",)
            or source.crs is None
            or source.crs.to_epsg() != 32610
            or source.nodata != nodata
        ):
            raise LabelProposalError(f"invalid output raster contract: {path.name}")
        return {
            "filename": path.name,
            "bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
            "width": source.width,
            "height": source.height,
            "count": source.count,
            "dtype": source.dtypes[0],
            "crs": source.crs.to_string(),
            "transform": [round(float(value), 9) for value in source.transform[:6]],
            "nodata": source.nodata,
        }


def _state_image(states: np.ndarray) -> Image.Image:
    palette = np.zeros((256, 3), dtype=np.uint8)
    for code, color in STATE_COLORS.items():
        palette[code] = color
    return Image.fromarray(palette[states], mode="RGB")


def _target_image(target: np.ndarray) -> Image.Image:
    palette = np.zeros((256, 3), dtype=np.uint8)
    palette[0] = STATE_COLORS[0]
    palette[1] = STATE_COLORS[1]
    palette[IGNORE_VALUE] = (226, 222, 212)
    return Image.fromarray(palette[target], mode="RGB")


def _panel(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    image: Image.Image,
    box: tuple[int, int, int, int],
    title: str,
    subtitle: str,
    *,
    nearest: bool = False,
) -> None:
    resampling = Image.Resampling.NEAREST if nearest else Image.Resampling.LANCZOS
    resized = image.resize((box[2] - box[0], box[3] - box[1]), resampling)
    canvas.paste(resized, (box[0], box[1]))
    draw.rectangle(box, outline="#132a26", width=3)
    draw.rectangle((box[0], box[1], box[2], box[1] + 60), fill="#132a26")
    draw.text((box[0] + 14, box[1] + 8), title, fill="white", font=_font(17))
    draw.text((box[0] + 14, box[1] + 34), subtitle, fill="#b9d8cf", font=_font(13))


def render_png(
    report: dict[str, Any],
    pre_tci: np.ndarray,
    post_tci: np.ndarray,
    states: np.ndarray,
    target: np.ndarray,
    path: Path,
) -> None:
    canvas = Image.new("RGB", (1800, 1250), "#f4f0e8")
    draw = ImageDraw.Draw(canvas)
    ink, muted, teal, orange = "#15211d", "#5d6b64", "#006b64", "#f05a28"
    draw.rectangle((0, 0, 1800, 170), fill="#132a26")
    draw.text((62, 33), "BURNLENS / PHASE TWO / OBJECTIVE FOUR", fill="#b9d8cf", font=_font(21))
    draw.text((62, 73), "FIVE-STATE LABEL PROPOSAL", fill="white", font=_font(38))
    draw.text((1370, 43), "STATUS", fill="#b9d8cf", font=_font(17))
    draw.text((1370, 79), "SEPARATE QA REQUIRED", fill="#ffd166", font=_font(23))
    draw.text((1370, 120), "dataset not created", fill="white", font=_font(15))

    boxes = [
        (45, 215, 450, 520),
        (480, 215, 885, 520),
        (915, 215, 1320, 520),
        (1350, 215, 1755, 520),
    ]
    _panel(
        canvas,
        draw,
        Image.fromarray(np.moveaxis(pre_tci, 0, 2), mode="RGB"),
        boxes[0],
        "PRE / REFERENCE",
        "Sentinel-2A true color / native 10 m",
    )
    _panel(
        canvas,
        draw,
        Image.fromarray(np.moveaxis(post_tci, 0, 2), mode="RGB"),
        boxes[1],
        "POST / OBSERVED",
        "Sentinel-2A true color / native 10 m",
    )
    _panel(canvas, draw, _state_image(states), boxes[2], "COMPANION STATE", "five states / native 20 m", nearest=True)
    _panel(canvas, draw, _target_image(target), boxes[3], "CANDIDATE TARGET", "burned 1 / background 0 / gray ignore", nearest=True)

    state_rows = report["summary"]["states"]
    left = 45
    for item in state_rows:
        color = "#%02x%02x%02x" % STATE_COLORS[item["code"]]
        draw.rounded_rectangle((left, 565, left + 320, 700), radius=15, fill="#fffdf8", outline="#d4cec1", width=2)
        draw.rectangle((left, 565, left + 12, 700), fill=color)
        draw.text((left + 28, 587), f"{item['percent']:.2f}%", fill=color, font=_font(28))
        draw.text((left + 28, 634), item["state"], fill=ink, font=_font(16))
        draw.text((left + 28, 664), f"{item['pixels']:,} pixels", fill=muted, font=_font(13))
        left += 342

    draw.rounded_rectangle((45, 745, 1755, 1055), radius=18, fill="#e5efeb", outline="#aac8bf", width=2)
    draw.text((72, 772), "PROPOSAL RULES / NOT GROUND TRUTH", fill=teal, font=_font(22))
    rules = [
        "Burned candidate: eroded NIFC context + multi-signal change + support in at least 5 of 9 neighbors.",
        "Background candidate: outside expanded context + multi-signal stability in at least 7 of 9 neighbors.",
        "Review-needed: SCL review, reference boundary, burned-transition boundary, or source/spectral disagreement.",
        "Unknown remains unknown; excluded follows pair quality or invalid numeric evidence; both stay outside target use.",
        "NIFC, SCL, VIIRS, MTBS, dNBR, and visual appearance never act as sufficient truth alone.",
        "A separately invoked verifier must reopen sources, reproduce state logic, and audit every state before acceptance.",
    ]
    for index, rule in enumerate(rules):
        draw.text((88, 822 + index * 35), f"{index + 1}. {rule}", fill=ink, font=_font(15))

    draw.text((45, 1093), "Contains modified Copernicus Sentinel data 2024  |  NIFC geometry is context only", fill=muted, font=_font(15))
    trace = (
        f"run {report['run_id']} / source {report['git_source_commit'][:12]} / software {report['software_version']} / "
        f"schema {report['label_schema_version']} / proposal {report['label_proposal_version']}"
    )
    draw.text((45, 1128), trace, fill=muted, font=_font(13))
    draw.text((45, 1162), "dataset none / split none / baseline none / model none / human inter-rater validation none", fill=orange, font=_font(14))
    draw.text((45, 1200), WARNING, fill="#33443e", font=_font(12))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], png_name: str, path: Path) -> None:
    rows = "".join(
        "<tr>"
        f"<td><span class=\"swatch\" style=\"background:rgb{STATE_COLORS[item['code']]}\"></span>{escape(item['state'])}</td>"
        f"<td>{item['code']}</td><td>{'ignore' if item['target_value'] is None else item['target_value']}</td>"
        f"<td>{item['pixels']:,}</td><td>{item['percent']:.4f}%</td></tr>"
        for item in report["summary"]["states"]
    )
    thresholds = report["method"]["thresholds"]
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens five-state label proposal</title><style>
:root {{ color-scheme:light; --ink:#15211d; --muted:#5d6b64; --paper:#f4f0e8; --panel:#fffdf8; --teal:#006b64; --orange:#f05a28; }}
* {{ box-sizing:border-box; }} body {{ margin:0; background:var(--paper); color:var(--ink); font:16px/1.55 system-ui,sans-serif; }}
header {{ background:#132a26; color:white; padding:3rem max(5vw,2rem); }} header p {{ color:#b9d8cf; }} main {{ max-width:1250px; margin:auto; padding:2.5rem 1.5rem 5rem; }}
.warning {{ background:#fff1ca; border-left:6px solid #d87618; padding:1rem 1.2rem; font-weight:650; }} .hero {{ display:block; width:100%; height:auto; border:1px solid #c8c0b2; margin:1.5rem 0; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:1rem; }} .card {{ background:var(--panel); border:1px solid #d9d1c4; border-radius:12px; padding:1.2rem; }}
.decision {{ border:2px solid var(--orange); }} .value {{ color:var(--teal); font-size:2rem; font-weight:800; }} .table-wrap {{ overflow-x:auto; }} table {{ width:100%; border-collapse:collapse; background:var(--panel); }}
th,td {{ padding:.7rem; border-bottom:1px solid #ddd5c9; text-align:left; }} code {{ overflow-wrap:anywhere; }} h2 {{ margin-top:2.4rem; }} .swatch {{ display:inline-block; width:.9rem; height:.9rem; margin-right:.5rem; border:1px solid #333; }}
</style></head><body><header><p>BurnLens / Phase Two / Objective Four</p><h1>Five-state burn-scar label proposal</h1><p>Candidate pixels with explicit uncertainty; separate QA is required.</p></header><main>
<p class="warning">{escape(WARNING)}</p><img class="hero" src="{escape(png_name)}" alt="Pre and post Sentinel images beside a five-state label proposal and binary target with ignored pixels">
<section class="card decision"><h2>Proposal status</h2><p><strong>{escape(report['decision'])}</strong></p><p>{escape(report['decision_detail'])}</p><p>Machine gate: <code>{escape(report['summary']['machine_decision'])}</code>.</p></section>
<div class="grid"><div class="card"><div class="value">{report['summary']['candidate_target_percent']:.2f}%</div><div>candidate target domain</div></div><div class="card"><div class="value">{report['summary']['ignored_percent']:.2f}%</div><div>explicitly ignored</div></div><div class="card"><div class="value">5 / 5</div><div>states represented</div></div><div class="card"><div class="value">0</div><div>datasets, splits, baselines, models</div></div></div>
<h2>State inventory</h2><div class="table-wrap"><table><thead><tr><th>State</th><th>Code</th><th>Target</th><th>Pixels</th><th>Share</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Frozen proposal method</h2><div class="card"><p>Burned candidates require incident-reference context plus multiple independent spectral changes. Background candidates require affirmative multi-signal stability away from the reference. Candidate evidence must also be locally coherent. These are proposal-screen rules for this exact pair, not universal burn/severity thresholds or field calibration.</p><ul><li>dNBR minimum: {thresholds['burn_dnbr_min']:.2f}; at least {thresholds['burn_supporting_signals_min']} of NDVI loss ≥ {thresholds['burn_ndvi_loss_min']:.2f}, SWIR gain ≥ {thresholds['burn_swir_gain_min']:.2f}, and NIR loss ≥ {thresholds['burn_nir_loss_min']:.2f}; at least {thresholds['burn_neighbor_support_min']} of 9 neighborhood pixels must support the burn screen.</li><li>Stable evidence requires |dNBR| ≤ {thresholds['stable_abs_dnbr_max']:.2f}, |NDVI change| ≤ {thresholds['stable_abs_ndvi_change_max']:.2f}, |SWIR change| ≤ {thresholds['stable_abs_swir_change_max']:.2f}, and |NIR change| ≤ {thresholds['stable_abs_nir_change_max']:.2f}; at least {thresholds['stable_neighbor_support_min']} of 9 neighborhood pixels must be stable.</li><li>One native 20 m pixel is reserved around the incident-reference boundary and candidate burned transitions.</li></ul></div>
<h2>Traceability</h2><div class="card"><p><strong>Run:</strong> <code>{escape(report['run_id'])}</code><br><strong>Git source:</strong> <code>{escape(report['git_source_commit'])}</code><br><strong>Software / report:</strong> <code>{escape(report['software_version'])}</code> / <code>{escape(report['report_version'])}</code><br><strong>AOI / target:</strong> <code>{escape(report['aoi_version'])}</code> / <code>{escape(report['target_version'])}</code><br><strong>Protocol / schema / proposal:</strong> <code>{escape(report['label_protocol_version'])}</code> / <code>{escape(report['label_schema_version'])}</code> / <code>{escape(report['label_proposal_version'])}</code><br><strong>Application / dataset / split / baseline / model:</strong> none / none / none / none / none</p></div>
<h2>Boundaries</h2><ul><li>This is a proposal for separate QA, not accepted ground truth.</li><li>The NIFC geometry is mixed-method incident-reference context, not a pixel-perfect perimeter.</li><li>SCL and continuous spectral change have known limitations and never become sufficient truth alone.</li><li>The separate deterministic QA path is not independent human inter-rater validation.</li><li>No dataset, split, baseline, model, metric, application, deployment, operational result, official status, endorsement, or field-validation claim exists.</li><li>Contains modified Copernicus Sentinel data 2024. Official sources govern.</li></ul>
</main></body></html>"""
    _write_utf8_lf(path, document)


def build_proposal(
    *,
    package: Path,
    aoi_report_path: Path,
    reference_geojson_path: Path,
    optical_report_path: Path,
    registration_report_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> tuple[dict[str, Any], dict[str, np.ndarray], Affine]:
    verification = verify_registered_package(
        package,
        OPTICAL_CONTRACTS,
        contract_validator=validate_optical_contracts,
        contract_version=CONTRACT_VERSION,
    )
    if not verification["accepted_as_unchanged_registered_package"]:
        raise LabelProposalError("registered optical pair verification failed")
    aoi = json.loads(aoi_report_path.read_text(encoding="utf-8"))
    reference = json.loads(reference_geojson_path.read_text(encoding="utf-8"))
    optical = json.loads(optical_report_path.read_text(encoding="utf-8"))
    registration = json.loads(registration_report_path.read_text(encoding="utf-8"))
    if aoi.get("aoi_version") != AOI_VERSION:
        raise LabelProposalError("unexpected AOI version")
    if len(reference.get("features") or []) != 1:
        raise LabelProposalError("expected exactly one NIFC reference feature")
    if optical.get("decision") != "ACCEPT_OPTICAL_PAIR_FOR_PROTOCOL_DEFER_LABELS":
        raise LabelProposalError("optical predecessor is not accepted")
    if registration.get("decision") != "ACCEPT_LOCAL_CONTENT_REGISTRATION":
        raise LabelProposalError("registration predecessor is not accepted")
    if registration.get("summary", {}).get("machine_decision") != "PASS_LOCAL_CONTENT_REGISTRATION_GATE":
        raise LabelProposalError("registration machine gate did not pass")
    if registration.get("label_schema_implemented") is not False:
        raise LabelProposalError("registration predecessor unexpectedly implemented labels")

    bounds = [float(value) for value in aoi["derivation"]["aoi_bbox_utm10n"]]
    if bounds != [620000.0, 4831000.0, 632000.0, 4840000.0]:
        raise LabelProposalError("AOI bounds changed")
    pre_scene, pre = _read_scene(package, 0, bounds)
    post_scene, post = _read_scene(package, 1, bounds)
    for band in ("B04", "B8A", "B12", "SCL"):
        if pre_scene["rasters"][band]["source_transform"] != post_scene["rasters"][band]["source_transform"]:
            raise LabelProposalError(f"pre/post {band} transforms differ")
        if pre_scene["rasters"][band]["aoi_bounds_utm10n"] != post_scene["rasters"][band]["aoi_bounds_utm10n"]:
            raise LabelProposalError(f"pre/post {band} bounds differ")

    pre_scl, post_scl = pre["SCL"], post["SCL"]
    known = set(int(value) for value in np.unique(np.concatenate([pre_scl.reshape(-1), post_scl.reshape(-1)])))
    if known - set(range(12)):
        raise LabelProposalError("source SCL contains an unknown class")
    excluded_scl = {0, 1, 2, 3, 6, 8, 9, 10, 11}
    review_scl = {7}
    excluded = np.isin(pre_scl, list(excluded_scl)) | np.isin(post_scl, list(excluded_scl))
    review = (~excluded) & (np.isin(pre_scl, list(review_scl)) | np.isin(post_scl, list(review_scl)))
    pair_quality = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)
    pair_quality[review] = 1
    pair_quality[excluded] = 2

    evidence, numeric_valid = spectral_evidence(pre_scene, pre, post_scene, post)
    reference_utm = transform_geom(
        "EPSG:4326", "EPSG:32610", reference["features"][0]["geometry"], precision=3
    )
    transform = Affine(PIXEL_SIZE_M, 0.0, bounds[0], 0.0, -PIXEL_SIZE_M, bounds[3])
    reference_mask = rasterize(
        [(reference_utm, 1)],
        out_shape=(HEIGHT, WIDTH),
        transform=transform,
        fill=0,
        all_touched=False,
        dtype="uint8",
    ).astype(bool)
    states, target, masks = classify_label_states(
        pair_quality=pair_quality,
        reference_mask=reference_mask,
        evidence=evidence,
        numeric_valid=numeric_valid,
    )
    summary = summarize_states(states)
    total = int(states.size)
    report: dict[str, Any] = {
        "report_id": REPORT_ID,
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
        "serialization": "UTF-8 JSON and HTML with LF line endings; deterministic GeoTIFF and PNG for fixed inputs",
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 353,
        "branch": "codex/p2o4-t01-label-proposal",
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": None,
        "aoi_version": AOI_VERSION,
        "target_version": TARGET_VERSION,
        "dataset_version": None,
        "split_version": None,
        "label_protocol_version": LABEL_PROTOCOL_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "label_schema_implemented": True,
        "label_proposal_version": LABEL_PROPOSAL_VERSION,
        "label_proposal_status": "candidate-for-separate-qa",
        "baseline_version": None,
        "model_version": None,
        "registration_protocol_version": REGISTRATION_PROTOCOL_VERSION,
        "package_id": PACKAGE_ID,
        "package_contract_version": CONTRACT_VERSION,
        "package_verification": verification,
        "terms_review_ids": [TERMS_REVIEW_ID, "TERMS-2026-003", "TERMS-2026-005"],
        "input_hashes": {
            "aoi_report_sha256_lf_normalized": _sha256_lf_text(aoi_report_path),
            "reference_geojson_sha256_lf_normalized": _sha256_lf_text(reference_geojson_path),
            "optical_report_sha256_lf_normalized": _sha256_lf_text(optical_report_path),
            "registration_report_sha256_lf_normalized": _sha256_lf_text(registration_report_path),
        },
        "predecessors": {
            "optical": {
                "report_id": optical["report_id"],
                "run_id": optical["run_id"],
                "decision": optical["decision"],
                "git_source_commit": optical["git_source_commit"],
            },
            "registration": {
                "report_id": registration["report_id"],
                "run_id": registration["run_id"],
                "decision": registration["decision"],
                "git_source_commit": registration["git_source_commit"],
                "maximum_residual_px": registration["summary"]["max_px"],
            },
        },
        "aoi": {
            "bbox_utm10n": bounds,
            "width_px": WIDTH,
            "height_px": HEIGHT,
            "pixel_size_m": PIXEL_SIZE_M,
            "crs": "EPSG:32610",
            "transform": [round(float(value), 9) for value in transform[:6]],
        },
        "source_roles": {
            "sentinel_pair": "native-grid optical and quality evidence; not truth alone",
            "nifc_reference": "later mixed-method incident-reference context; not pixel-perfect truth",
            "viirs": "complementary native-scale thermal-anomaly reference; not used to assign proposal pixels",
            "mtbs": "methodology and future/cross-fire reference only; current Darlene AOI evidence absent",
        },
        "method": {
            "resolution": "native 20 m; no source reprojection or resampling",
            "reference_rasterization": "pixel-center rule (all_touched=false); one-pixel eroded core and expanded boundary",
            "burned_rule": "reference core plus dNBR minimum, at least two of three independent supporting changes, and local neighborhood coherence",
            "background_rule": "outside expanded reference plus affirmative stability in dNBR, NDVI, SWIR, and NIR with local neighborhood coherence",
            "review_rule": "SCL 7, incident-reference boundary, candidate-burn transition, or reference/spectral disagreement",
            "unknown_rule": "valid evidence that satisfies neither conservative candidate class nor a review trigger",
            "excluded_rule": "excluded pair quality or invalid reflectance/index arithmetic",
            "thresholds": {
                "burn_dnbr_min": BURN_DNBR_MIN,
                "burn_ndvi_loss_min": BURN_NDVI_LOSS_MIN,
                "burn_swir_gain_min": BURN_SWIR_GAIN_MIN,
                "burn_nir_loss_min": BURN_NIR_LOSS_MIN,
                "burn_supporting_signals_min": BURN_SUPPORTING_SIGNALS_MIN,
                "burn_neighbor_support_min": BURN_NEIGHBOR_SUPPORT_MIN,
                "stable_abs_dnbr_max": STABLE_ABS_DNBR_MAX,
                "stable_abs_ndvi_change_max": STABLE_ABS_NDVI_CHANGE_MAX,
                "stable_abs_swir_change_max": STABLE_ABS_SWIR_CHANGE_MAX,
                "stable_abs_nir_change_max": STABLE_ABS_NIR_CHANGE_MAX,
                "stable_neighbor_support_min": STABLE_NEIGHBOR_SUPPORT_MIN,
                "boundary_review_px": BOUNDARY_REVIEW_PX,
                "threshold_scope": "frozen conservative proposal screen for this exact pair; not universal severity calibration",
            },
            "primary_sources": list(PRIMARY_SOURCES),
        },
        "evidence_counts": {
            key: {"pixels": int(mask.sum()), "percent": round(100 * int(mask.sum()) / total, 4)}
            for key, mask in masks.items()
        },
        "summary": summary,
        "decision": "PROPOSE_FIVE_STATE_LABELS_FOR_SEPARATE_QA",
        "decision_detail": (
            "Create a deterministic native-grid candidate target and five-state companion raster for separate QA. "
            "No candidate pixel is accepted ground truth, and no dataset, split, baseline, or model is created."
        ),
        "quality_gates": {
            "registered_pair_reverified": True,
            "accepted_optical_predecessor_reverified": True,
            "accepted_registration_predecessor_reverified": True,
            "native_grid_identity_reverified": True,
            "real_b04_b8a_b12_scl_pixels_read": True,
            "source_pixels_resampled": False,
            "all_five_states_represented": len(summary["states"]) == 5,
            "companion_state_raster_created": True,
            "candidate_target_raster_created": True,
            "independent_qa_completed": False,
            "independent_human_inter_rater_validation": False,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
        },
        "claims": {
            "permitted": [
                "BurnLens produced a traceable five-state candidate proposal for separate QA on one exact native-grid pair.",
                "Every non-binary state remains ignored in the candidate target raster.",
                "The proposal exposes its source roles, thresholds, state shares, uncertainty, and decision boundary.",
            ],
            "prohibited": [
                "The proposal is accepted ground truth, field validation, a fire perimeter, burn severity, or a detection.",
                "NIFC, SCL, VIIRS, MTBS, dNBR, or visual appearance is sufficient truth alone.",
                "The proposal establishes a dataset, split, baseline, model, metric, application, deployment, or operational result.",
            ],
        },
        "limitations": [
            "The approximate incident start does not prove every pre-scene pixel is unburned.",
            "The approximately ten-day interval permits non-fire vegetation, moisture, atmosphere, soil, and land-surface change.",
            "The NIFC final perimeter is later mixed-method context and cannot supply pixel-perfect boundaries.",
            "The proposal thresholds are transparent conservative screens for this exact pair, not universal or field-calibrated severity thresholds.",
            "A separately implemented software verifier is not independent human inter-rater validation.",
            "One event cannot support leakage-resistant train, validation, and test groups.",
        ],
        "attribution": [
            "Contains modified Copernicus Sentinel data 2024.",
            "NIFC WFIGS final incident-reference feature SOURCE-2026-007.",
        ],
        "source_precedence": "Official sources govern over every BurnLens-derived artifact.",
        "warning": WARNING,
        "rendered_outputs": {
            "json": f"{REPORT_ID}.json",
            "html": f"{REPORT_ID}.html",
            "png": f"{REPORT_ID}.png",
            "state_raster": f"{REPORT_ID}-state.tif",
            "target_raster": f"{REPORT_ID}-target.tif",
        },
    }
    arrays = {
        "pre_tci": pre["TCI"],
        "post_tci": post["TCI"],
        "states": states,
        "target": target,
        "reference_mask": reference_mask,
        **evidence,
    }
    return report, arrays, transform


def write_proposal(
    *,
    report: dict[str, Any],
    arrays: dict[str, np.ndarray],
    transform: Affine,
    output_directory: Path,
) -> dict[str, Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": output_directory / f"{REPORT_ID}.json",
        "html": output_directory / f"{REPORT_ID}.html",
        "png": output_directory / f"{REPORT_ID}.png",
        "state_raster": output_directory / f"{REPORT_ID}-state.tif",
        "target_raster": output_directory / f"{REPORT_ID}-target.tif",
    }
    _write_raster(
        paths["state_raster"],
        arrays["states"],
        transform,
        nodata=None,
        kind="five-state companion proposal",
        run_id=report["run_id"],
        git_source_commit=report["git_source_commit"],
    )
    _write_raster(
        paths["target_raster"],
        arrays["target"],
        transform,
        nodata=IGNORE_VALUE,
        kind="candidate binary target with explicit ignore",
        run_id=report["run_id"],
        git_source_commit=report["git_source_commit"],
    )
    report["output_rasters"] = {
        "state": _raster_metadata(paths["state_raster"], nodata=None),
        "target": _raster_metadata(paths["target_raster"], nodata=float(IGNORE_VALUE)),
    }
    _write_utf8_lf(paths["json"], json.dumps(report, indent=2) + "\n")
    render_png(
        report,
        arrays["pre_tci"],
        arrays["post_tci"],
        arrays["states"],
        arrays["target"],
        paths["png"],
    )
    render_html(report, paths["png"].name, paths["html"])
    return paths


def propose_burn_scar_labels(
    *,
    package: Path,
    aoi_report_path: Path,
    reference_geojson_path: Path,
    optical_report_path: Path,
    registration_report_path: Path,
    output_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Path]:
    report, arrays, transform = build_proposal(
        package=package,
        aoi_report_path=aoi_report_path,
        reference_geojson_path=reference_geojson_path,
        optical_report_path=optical_report_path,
        registration_report_path=registration_report_path,
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
    )
    return write_proposal(
        report=report,
        arrays=arrays,
        transform=transform,
        output_directory=output_directory,
    )
