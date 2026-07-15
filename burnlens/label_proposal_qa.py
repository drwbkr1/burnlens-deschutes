"""Verify a BurnLens five-state label proposal through a separate code path.

The verifier deliberately does not import proposal classification code.  It
reopens immutable sources, independently recomputes the frozen rules, checks the
two GeoTIFFs, and creates a deterministic stratified audit.  This software-level
separation is not independent human inter-rater validation.
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

from .optical_pair_contract import (
    CONTRACT_VERSION,
    OPTICAL_CONTRACTS,
    PACKAGE_ID,
    validate_optical_contracts,
)
from .optical_pair_evidence import AOI_VERSION, TARGET_VERSION, WARNING, _read_scene
from .paired_intake import verify_registered_package


SOFTWARE_VERSION = "0.9.0"
REPORT_ID = "LABEL-QA-2026-001"
REPORT_SCHEMA_VERSION = "0.1.0"
REPORT_VERSION = "burn-scar-label-proposal-qa-v0.1.0"
PROPOSAL_REPORT_ID = "LABEL-PROPOSAL-2026-001"
LABEL_PROTOCOL_VERSION = "burn-scar-label-protocol-v0.1.0"
LABEL_SCHEMA_VERSION = "burn-scar-five-state-schema-v0.1.0"
LABEL_PROPOSAL_VERSION = "darlene3-burn-scar-label-proposal-v0.1.0"
QA_PROTOCOL_VERSION = "separate-label-proposal-qa-v0.1.0"
WIDTH = 600
HEIGHT = 450
PIXEL_SIZE_M = 20
IGNORE_VALUE = 255
AUDIT_PER_STATE = 20
AUDIT_BOUNDARY = 20

STATE_NAMES = {
    0: "background-candidate",
    1: "burned",
    2: "unknown",
    3: "excluded",
    4: "review-needed",
}
STATE_CODES = {name: code for code, name in STATE_NAMES.items()}
STATE_COLORS = {
    0: (0, 107, 100),
    1: (240, 90, 40),
    2: (233, 196, 106),
    3: (86, 95, 91),
    4: (126, 63, 143),
}

# Independently frozen copies of the proposal contract.  The verifier compares
# these to the report declaration and then evaluates them without importing the
# proposal module.
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


class LabelProposalQaError(RuntimeError):
    """A deterministic, secret-free QA failure."""


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return ImageFont.load_default(size=size)


def _write_utf8_lf(path: Path, text: str) -> None:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    path.write_bytes(normalized.encode("utf-8"))


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_lf_text(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", newline=None) as handle:
            return sha256(handle.read().encode("utf-8")).hexdigest()
    except (OSError, UnicodeError) as error:
        raise LabelProposalQaError(f"invalid UTF-8 input {path.name}") from error


def _qa_dilate(mask: np.ndarray, iterations: int = 1) -> np.ndarray:
    result = mask.astype(bool, copy=True)
    rows, columns = result.shape
    for _ in range(iterations):
        padded = np.pad(result, 1, mode="constant", constant_values=False)
        result = np.logical_or.reduce(
            [padded[row : row + rows, column : column + columns] for row in range(3) for column in range(3)]
        )
    return result


def _qa_erode(mask: np.ndarray, iterations: int = 1) -> np.ndarray:
    return ~_qa_dilate(~mask.astype(bool), iterations)


def _qa_boundary(mask: np.ndarray) -> np.ndarray:
    return _qa_dilate(mask, BOUNDARY_REVIEW_PX) & _qa_dilate(~mask, BOUNDARY_REVIEW_PX)


def _qa_neighbor_count(mask: np.ndarray) -> np.ndarray:
    rows, columns = mask.shape
    padded = np.pad(mask.astype(np.uint8), 1, mode="constant", constant_values=0)
    result = np.zeros((rows, columns), dtype=np.uint8)
    for row in range(3):
        for column in range(3):
            result += padded[row : row + rows, column : column + columns]
    return result


def _qa_reflectance(
    scene: dict[str, Any], arrays: dict[str, np.ndarray], band: str
) -> tuple[np.ndarray, np.ndarray]:
    metadata = scene["product_metadata"]
    digital = arrays[band]
    valid = (digital != metadata["nodata_dn"]) & (digital != metadata["saturated_dn"])
    values = np.full(digital.shape, np.nan, dtype=np.float32)
    values[valid] = (
        digital[valid].astype(np.float32) + float(metadata["boa_offsets"][band])
    ) / float(metadata["boa_quantification_value"])
    return values, valid


def _qa_index(
    scene: dict[str, Any], arrays: dict[str, np.ndarray], first: str, second: str
) -> tuple[np.ndarray, np.ndarray]:
    first_values, first_valid = _qa_reflectance(scene, arrays, first)
    second_values, second_valid = _qa_reflectance(scene, arrays, second)
    denominator = first_values + second_values
    valid = first_valid & second_valid & np.isfinite(denominator) & (np.abs(denominator) > 1e-6)
    result = np.full(first_values.shape, np.nan, dtype=np.float32)
    result[valid] = (first_values[valid] - second_values[valid]) / denominator[valid]
    return result, valid


def _qa_evidence(
    pre_scene: dict[str, Any],
    pre: dict[str, np.ndarray],
    post_scene: dict[str, Any],
    post: dict[str, np.ndarray],
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    pre_nbr, pre_nbr_valid = _qa_index(pre_scene, pre, "B8A", "B12")
    post_nbr, post_nbr_valid = _qa_index(post_scene, post, "B8A", "B12")
    pre_ndvi, pre_ndvi_valid = _qa_index(pre_scene, pre, "B8A", "B04")
    post_ndvi, post_ndvi_valid = _qa_index(post_scene, post, "B8A", "B04")
    pre_swir, pre_swir_valid = _qa_reflectance(pre_scene, pre, "B12")
    post_swir, post_swir_valid = _qa_reflectance(post_scene, post, "B12")
    pre_nir, pre_nir_valid = _qa_reflectance(pre_scene, pre, "B8A")
    post_nir, post_nir_valid = _qa_reflectance(post_scene, post, "B8A")
    evidence = {
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
        & np.logical_and.reduce([np.isfinite(item) for item in evidence.values()])
    )
    return evidence, valid


def _qa_pair_quality(pre_scl: np.ndarray, post_scl: np.ndarray) -> np.ndarray:
    if pre_scl.shape != (HEIGHT, WIDTH) or post_scl.shape != (HEIGHT, WIDTH):
        raise LabelProposalQaError("QA SCL arrays do not match the frozen grid")
    observed = set(int(value) for value in np.unique(np.concatenate([pre_scl.reshape(-1), post_scl.reshape(-1)])))
    if observed - set(range(12)):
        raise LabelProposalQaError("QA observed an unknown SCL class")
    excluded_scl = {0, 1, 2, 3, 6, 8, 9, 10, 11}
    excluded = np.isin(pre_scl, list(excluded_scl)) | np.isin(post_scl, list(excluded_scl))
    review = (~excluded) & ((pre_scl == 7) | (post_scl == 7))
    state = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)
    state[review] = 1
    state[excluded] = 2
    if np.any((state == 0) & ~np.isin(pre_scl, [4, 5])) or np.any((state == 0) & ~np.isin(post_scl, [4, 5])):
        raise LabelProposalQaError("QA pair quality left an unclassified eligible pixel")
    return state


def _qa_classify(
    pair_quality: np.ndarray,
    reference_mask: np.ndarray,
    evidence: dict[str, np.ndarray],
    numeric_valid: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray]]:
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
    burn_coherent = burn_evidence & (_qa_neighbor_count(burn_evidence) >= BURN_NEIGHBOR_SUPPORT_MIN)
    stable_coherent = stable_evidence & (_qa_neighbor_count(stable_evidence) >= STABLE_NEIGHBOR_SUPPORT_MIN)
    reference_core = _qa_erode(reference_mask, BOUNDARY_REVIEW_PX)
    reference_outer = _qa_dilate(reference_mask, BOUNDARY_REVIEW_PX)
    reference_boundary = reference_outer & ~reference_core
    burned_raw = usable & reference_core & burn_coherent
    background_raw = usable & ~reference_outer & stable_coherent
    source_conflict = usable & ((~reference_mask & burn_coherent) | (reference_mask & stable_coherent))
    burned_boundary = usable & _qa_boundary(burned_raw)
    review = quality_review | reference_boundary | source_conflict | burned_boundary

    states = np.full((HEIGHT, WIDTH), STATE_CODES["unknown"], dtype=np.uint8)
    states[excluded] = STATE_CODES["excluded"]
    states[review & ~excluded] = STATE_CODES["review-needed"]
    states[burned_raw & ~review & ~excluded] = STATE_CODES["burned"]
    states[background_raw & ~review & ~excluded] = STATE_CODES["background-candidate"]
    target = np.full((HEIGHT, WIDTH), IGNORE_VALUE, dtype=np.uint8)
    target[states == 0] = 0
    target[states == 1] = 1
    return states, target, {
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


def _read_proposal_raster(
    path: Path,
    *,
    expected_nodata: float | None,
    expected_transform: Affine,
    expected_kind: str,
    expected_run_id: str,
    expected_git_source_commit: str,
) -> tuple[np.ndarray, dict[str, Any]]:
    with rasterio.open(path) as source:
        if source.driver != "GTiff" or source.count != 1 or source.dtypes != ("uint8",):
            raise LabelProposalQaError(f"invalid proposal raster type: {path.name}")
        if source.width != WIDTH or source.height != HEIGHT or source.crs is None or source.crs.to_epsg() != 32610:
            raise LabelProposalQaError(f"invalid proposal raster grid: {path.name}")
        if source.transform != expected_transform or source.nodata != expected_nodata:
            raise LabelProposalQaError(f"proposal raster transform/nodata mismatch: {path.name}")
        tags = source.tags()
        required_tags = {
            "repository": "drwbkr1/burnlens-deschutes",
            "artifact_kind": expected_kind,
            "software_version": SOFTWARE_VERSION,
            "aoi_version": AOI_VERSION,
            "target_version": TARGET_VERSION,
            "label_protocol_version": LABEL_PROTOCOL_VERSION,
            "label_schema_version": LABEL_SCHEMA_VERSION,
            "label_proposal_version": LABEL_PROPOSAL_VERSION,
            "run_id": expected_run_id,
            "git_source_commit": expected_git_source_commit,
            "source_precedence": "official sources govern",
        }
        for key, value in required_tags.items():
            if tags.get(key) != value:
                raise LabelProposalQaError(f"proposal raster trace tag mismatch: {path.name}/{key}")
        values = source.read(1)
        metadata = {
            "filename": path.name,
            "bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
            "driver": source.driver,
            "width": source.width,
            "height": source.height,
            "dtype": source.dtypes[0],
            "crs": source.crs.to_string(),
            "transform": [round(float(value), 9) for value in source.transform[:6]],
            "nodata": source.nodata,
            "tags": required_tags,
        }
    return values, metadata


def _threshold_contract() -> dict[str, float | int]:
    return {
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
    }


def _select_coordinates(mask: np.ndarray, count: int, seed: str) -> list[tuple[int, int]]:
    coordinates = np.argwhere(mask)
    if coordinates.shape[0] < count:
        raise LabelProposalQaError(f"audit stratum {seed} has fewer than {count} pixels")
    ranked = sorted(
        ((sha256(f"{seed}:{int(row)}:{int(column)}".encode("utf-8")).digest(), int(row), int(column)) for row, column in coordinates),
        key=lambda item: item[0],
    )
    return [(row, column) for _, row, column in ranked[:count]]


def _audit_sample(
    *,
    proposal_states: np.ndarray,
    proposal_target: np.ndarray,
    expected_states: np.ndarray,
    expected_target: np.ndarray,
    evidence: dict[str, np.ndarray],
    masks: dict[str, np.ndarray],
    reference_mask: np.ndarray,
    pre_scl: np.ndarray,
    post_scl: np.ndarray,
    transform: Affine,
    proposal_run_id: str,
) -> list[dict[str, Any]]:
    strata: list[tuple[str, np.ndarray, int]] = [
        (f"state-{STATE_NAMES[code]}", proposal_states == code, AUDIT_PER_STATE) for code in sorted(STATE_NAMES)
    ]
    strata.append(("burned-transition-boundary", masks["burned_boundary"], AUDIT_BOUNDARY))
    rows: list[dict[str, Any]] = []
    for stratum, mask, count in strata:
        for row, column in _select_coordinates(mask, count, f"{proposal_run_id}:{stratum}"):
            x, y = transform * (column + 0.5, row + 0.5)
            state = int(proposal_states[row, column])
            expected = int(expected_states[row, column])
            rows.append(
                {
                    "stratum": stratum,
                    "row": row,
                    "column": column,
                    "x_utm10n": round(float(x), 3),
                    "y_utm10n": round(float(y), 3),
                    "proposal_state": STATE_NAMES[state],
                    "proposal_state_code": state,
                    "qa_state": STATE_NAMES[expected],
                    "qa_state_code": expected,
                    "proposal_target": None if int(proposal_target[row, column]) == IGNORE_VALUE else int(proposal_target[row, column]),
                    "qa_target": None if int(expected_target[row, column]) == IGNORE_VALUE else int(expected_target[row, column]),
                    "agree": state == expected and int(proposal_target[row, column]) == int(expected_target[row, column]),
                    "reference_context": bool(reference_mask[row, column]),
                    "pre_scl": int(pre_scl[row, column]),
                    "post_scl": int(post_scl[row, column]),
                    "dnbr": round(float(evidence["dnbr"][row, column]), 6) if np.isfinite(evidence["dnbr"][row, column]) else None,
                    "ndvi_loss": round(float(evidence["ndvi_loss"][row, column]), 6) if np.isfinite(evidence["ndvi_loss"][row, column]) else None,
                    "swir_gain": round(float(evidence["swir_gain"][row, column]), 6) if np.isfinite(evidence["swir_gain"][row, column]) else None,
                    "nir_loss": round(float(evidence["nir_loss"][row, column]), 6) if np.isfinite(evidence["nir_loss"][row, column]) else None,
                }
            )
    return rows


def _validate_visual_decision(machine_pass: bool, decision: str, notes: str) -> None:
    allowed = {
        "PENDING_QA_VISUAL_REVIEW",
        "ACCEPT_REVIEWABLE_LABEL_PROPOSAL_DEFER_DATASET",
        "ACCEPT_PROPOSAL_WITH_REVIEW_REMEDIATION",
        "REJECT_LABEL_PROPOSAL",
    }
    if decision not in allowed:
        raise LabelProposalQaError("invalid QA visual decision")
    if decision != "PENDING_QA_VISUAL_REVIEW" and not notes.strip():
        raise LabelProposalQaError("final QA visual decision requires notes")
    if not machine_pass and decision.startswith("ACCEPT_"):
        raise LabelProposalQaError("QA visual acceptance is incompatible with the machine gate")


def build_qa_report(
    *,
    package: Path,
    aoi_report_path: Path,
    reference_geojson_path: Path,
    optical_report_path: Path,
    registration_report_path: Path,
    proposal_report_path: Path,
    state_raster_path: Path,
    target_raster_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    visual_review_decision: str,
    visual_review_notes: str,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    proposal = json.loads(proposal_report_path.read_text(encoding="utf-8"))
    aoi = json.loads(aoi_report_path.read_text(encoding="utf-8"))
    reference = json.loads(reference_geojson_path.read_text(encoding="utf-8"))
    optical = json.loads(optical_report_path.read_text(encoding="utf-8"))
    registration = json.loads(registration_report_path.read_text(encoding="utf-8"))
    if proposal.get("report_id") != PROPOSAL_REPORT_ID or proposal.get("decision") != "PROPOSE_FIVE_STATE_LABELS_FOR_SEPARATE_QA":
        raise LabelProposalQaError("proposal report is not the expected QA candidate")
    if proposal.get("label_schema_version") != LABEL_SCHEMA_VERSION or proposal.get("label_proposal_version") != LABEL_PROPOSAL_VERSION:
        raise LabelProposalQaError("proposal label version mismatch")
    if proposal.get("software_version") != SOFTWARE_VERSION or proposal.get("git_source_commit") != git_source_commit:
        raise LabelProposalQaError("proposal source/software trace mismatch")
    if aoi.get("aoi_version") != AOI_VERSION or len(reference.get("features") or []) != 1:
        raise LabelProposalQaError("QA AOI/reference contract mismatch")
    if optical.get("decision") != "ACCEPT_OPTICAL_PAIR_FOR_PROTOCOL_DEFER_LABELS":
        raise LabelProposalQaError("QA optical predecessor is not accepted")
    if registration.get("decision") != "ACCEPT_LOCAL_CONTENT_REGISTRATION":
        raise LabelProposalQaError("QA registration predecessor is not accepted")
    declared_thresholds = dict(proposal.get("method", {}).get("thresholds", {}))
    declared_thresholds.pop("threshold_scope", None)
    if declared_thresholds != _threshold_contract():
        raise LabelProposalQaError("proposal and QA threshold contracts differ")

    verification = verify_registered_package(
        package,
        OPTICAL_CONTRACTS,
        contract_validator=validate_optical_contracts,
        contract_version=CONTRACT_VERSION,
    )
    if not verification["accepted_as_unchanged_registered_package"]:
        raise LabelProposalQaError("QA registered package verification failed")
    bounds = [float(value) for value in aoi["derivation"]["aoi_bbox_utm10n"]]
    transform = Affine(PIXEL_SIZE_M, 0.0, bounds[0], 0.0, -PIXEL_SIZE_M, bounds[3])
    proposal_states, state_metadata = _read_proposal_raster(
        state_raster_path,
        expected_nodata=None,
        expected_transform=transform,
        expected_kind="five-state companion proposal",
        expected_run_id=proposal["run_id"],
        expected_git_source_commit=proposal["git_source_commit"],
    )
    proposal_target, target_metadata = _read_proposal_raster(
        target_raster_path,
        expected_nodata=float(IGNORE_VALUE),
        expected_transform=transform,
        expected_kind="candidate binary target with explicit ignore",
        expected_run_id=proposal["run_id"],
        expected_git_source_commit=proposal["git_source_commit"],
    )
    if set(int(value) for value in np.unique(proposal_states)) != set(STATE_NAMES):
        raise LabelProposalQaError("proposal state raster does not contain exactly five states")
    if set(int(value) for value in np.unique(proposal_target)) - {0, 1, IGNORE_VALUE}:
        raise LabelProposalQaError("proposal target contains an invalid value")
    declared_outputs = proposal.get("output_rasters", {})
    if declared_outputs.get("state", {}).get("filename") != state_raster_path.name:
        raise LabelProposalQaError("proposal state raster filename mismatch")
    if declared_outputs.get("target", {}).get("filename") != target_raster_path.name:
        raise LabelProposalQaError("proposal target raster filename mismatch")
    if declared_outputs.get("state", {}).get("sha256") != state_metadata["sha256"]:
        raise LabelProposalQaError("proposal state raster hash mismatch")
    if declared_outputs.get("target", {}).get("sha256") != target_metadata["sha256"]:
        raise LabelProposalQaError("proposal target raster hash mismatch")

    pre_scene, pre = _read_scene(package, 0, bounds)
    post_scene, post = _read_scene(package, 1, bounds)
    pair_quality = _qa_pair_quality(pre["SCL"], post["SCL"])
    evidence, numeric_valid = _qa_evidence(pre_scene, pre, post_scene, post)
    reference_utm = transform_geom(
        "EPSG:4326", "EPSG:32610", reference["features"][0]["geometry"], precision=3
    )
    reference_mask = rasterize(
        [(reference_utm, 1)],
        out_shape=(HEIGHT, WIDTH),
        transform=transform,
        fill=0,
        all_touched=False,
        dtype="uint8",
    ).astype(bool)
    expected_states, expected_target, masks = _qa_classify(pair_quality, reference_mask, evidence, numeric_valid)
    state_disagreement = proposal_states != expected_states
    target_disagreement = proposal_target != expected_target
    audit = _audit_sample(
        proposal_states=proposal_states,
        proposal_target=proposal_target,
        expected_states=expected_states,
        expected_target=expected_target,
        evidence=evidence,
        masks=masks,
        reference_mask=reference_mask,
        pre_scl=pre["SCL"],
        post_scl=post["SCL"],
        transform=transform,
        proposal_run_id=proposal["run_id"],
    )
    state_counts = Counter(int(value) for value in proposal_states.reshape(-1))
    expected_counts = Counter(int(value) for value in expected_states.reshape(-1))
    per_state = [
        {
            "state": STATE_NAMES[code],
            "code": code,
            "proposal_pixels": state_counts[code],
            "qa_pixels": expected_counts[code],
            "matching_pixels": int(((proposal_states == code) & (expected_states == code)).sum()),
            "audit_samples": sum(1 for item in audit if item["stratum"] == f"state-{STATE_NAMES[code]}"),
        }
        for code in sorted(STATE_NAMES)
    ]
    state_mismatch_count = int(state_disagreement.sum())
    target_mismatch_count = int(target_disagreement.sum())
    audit_disagreement_count = sum(not item["agree"] for item in audit)
    machine_pass = (
        state_mismatch_count == 0
        and target_mismatch_count == 0
        and audit_disagreement_count == 0
        and all(item["audit_samples"] == AUDIT_PER_STATE for item in per_state)
        and len(audit) == AUDIT_PER_STATE * 5 + AUDIT_BOUNDARY
    )
    _validate_visual_decision(machine_pass, visual_review_decision, visual_review_notes)
    decision_detail = {
        "PENDING_QA_VISUAL_REVIEW": (
            "The separate implementation reproduces every proposal state and target pixel. Original-resolution "
            "proposal, agreement, boundary, and audit evidence still require rendered review."
        ),
        "ACCEPT_REVIEWABLE_LABEL_PROPOSAL_DEFER_DATASET": (
            "Accept this exact five-state proposal as reviewable evidence only. Separate software QA and rendered "
            "audit pass, while independent human inter-rater validation, dataset, split, baseline, and model remain absent."
        ),
        "ACCEPT_PROPOSAL_WITH_REVIEW_REMEDIATION": (
            "Retain the proposal and its passing machine evidence, but require the recorded review remediation before "
            "any label acceptance or dataset work."
        ),
        "REJECT_LABEL_PROPOSAL": (
            "Reject the proposal after QA review and preserve the exact disagreements or presentation failure for remediation."
        ),
    }[visual_review_decision]
    disagreement_examples = [
        {
            "row": int(row),
            "column": int(column),
            "proposal_state": STATE_NAMES[int(proposal_states[row, column])],
            "qa_state": STATE_NAMES[int(expected_states[row, column])],
        }
        for row, column in np.argwhere(state_disagreement)[:20]
    ]
    report: dict[str, Any] = {
        "report_id": REPORT_ID,
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
        "qa_protocol_version": QA_PROTOCOL_VERSION,
        "serialization": "UTF-8 JSON and HTML with LF line endings; deterministic PNG for fixed inputs",
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
        "label_proposal_run_id": proposal["run_id"],
        "baseline_version": None,
        "model_version": None,
        "package_id": PACKAGE_ID,
        "package_contract_version": CONTRACT_VERSION,
        "package_verification": verification,
        "input_hashes": {
            "aoi_report_sha256_lf_normalized": _sha256_lf_text(aoi_report_path),
            "reference_geojson_sha256_lf_normalized": _sha256_lf_text(reference_geojson_path),
            "optical_report_sha256_lf_normalized": _sha256_lf_text(optical_report_path),
            "registration_report_sha256_lf_normalized": _sha256_lf_text(registration_report_path),
            "proposal_report_sha256": _sha256_file(proposal_report_path),
        },
        "proposal_outputs": {
            "report": {"filename": proposal_report_path.name, "bytes": proposal_report_path.stat().st_size, "sha256": _sha256_file(proposal_report_path)},
            "state_raster": state_metadata,
            "target_raster": target_metadata,
        },
        "independence": {
            "separate_cli_invocation": True,
            "separate_module": "burnlens.label_proposal_qa",
            "proposal_classification_helpers_imported": False,
            "source_pixels_reopened": True,
            "quality_and_spectral_conditions_recomputed": True,
            "all_pixels_compared": True,
            "deterministic_stratified_audit": True,
            "same_codex_director": True,
            "independent_human_inter_rater_validation": False,
            "interpretation": "This is implementation-path independence and reproducibility QA, not a second human annotator or field validation.",
        },
        "threshold_contract": _threshold_contract(),
        "summary": {
            "pixel_count": int(proposal_states.size),
            "state_mismatch_pixels": state_mismatch_count,
            "state_agreement_percent": round(100 * (1 - state_mismatch_count / proposal_states.size), 6),
            "target_mismatch_pixels": target_mismatch_count,
            "target_agreement_percent": round(100 * (1 - target_mismatch_count / proposal_target.size), 6),
            "audit_sample_count": len(audit),
            "audit_disagreement_count": audit_disagreement_count,
            "per_state": per_state,
            "machine_decision": "PASS_SEPARATE_IMPLEMENTATION_QA" if machine_pass else "FAIL_SEPARATE_IMPLEMENTATION_QA",
        },
        "audit_sample": audit,
        "disagreement_examples": disagreement_examples,
        "visual_review": {
            "decision": visual_review_decision,
            "notes": visual_review_notes,
            "rendered_proposal_and_qa_reviewed": visual_review_decision != "PENDING_QA_VISUAL_REVIEW",
        },
        "decision": visual_review_decision,
        "decision_detail": decision_detail,
        "quality_gates": {
            "registered_pair_reverified": True,
            "source_pixels_reopened": True,
            "proposal_raster_hashes_reverified": True,
            "proposal_raster_georeferencing_reverified": True,
            "all_five_states_audited": all(item["audit_samples"] == AUDIT_PER_STATE for item in per_state),
            "burned_transition_boundary_audited": sum(item["stratum"] == "burned-transition-boundary" for item in audit) == AUDIT_BOUNDARY,
            "state_target_consistency": state_mismatch_count == 0 and target_mismatch_count == 0,
            "software_qa_passed": machine_pass,
            "independent_human_inter_rater_validation": False,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
        },
        "claims": {
            "permitted": [
                "A separately invoked implementation reproduced every state and target pixel for this exact proposal.",
                "A deterministic audit samples every state and the candidate burned transition boundary.",
                "The exact QA evidence records disagreements rather than hiding or collapsing them.",
            ],
            "prohibited": [
                "Software agreement is independent human annotation, field validation, accuracy, or ground truth.",
                "The proposal or QA is a fire perimeter, severity product, official result, or operational decision aid.",
                "The checkpoint establishes a dataset, split, baseline, model, performance metric, application, or deployment.",
            ],
        },
        "limitations": [
            "Both implementations apply the same frozen contract and may share conceptual assumptions despite separate code paths.",
            "The same Codex technical director authored and reviewed both paths; no independent human annotator participated.",
            "The proposal is bounded to one event and exact scene pair and cannot support leakage-resistant split evidence.",
            "Source and threshold limitations recorded by the proposal remain fully binding after software QA.",
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
        },
    }
    arrays = {
        "post_tci": post["TCI"],
        "proposal_states": proposal_states,
        "expected_states": expected_states,
        "state_disagreement": state_disagreement,
        "audit": audit,
    }
    return report, arrays


def _state_image(values: np.ndarray) -> Image.Image:
    palette = np.zeros((256, 3), dtype=np.uint8)
    for code, color in STATE_COLORS.items():
        palette[code] = color
    return Image.fromarray(palette[values], mode="RGB")


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
    canvas.paste(image.resize((box[2] - box[0], box[3] - box[1]), resampling), (box[0], box[1]))
    draw.rectangle(box, outline="#132a26", width=3)
    draw.rectangle((box[0], box[1], box[2], box[1] + 60), fill="#132a26")
    draw.text((box[0] + 14, box[1] + 8), title, fill="white", font=_font(17))
    draw.text((box[0] + 14, box[1] + 34), subtitle, fill="#b9d8cf", font=_font(13))


def _audit_image(post_tci: np.ndarray, audit: list[dict[str, Any]]) -> Image.Image:
    image = Image.fromarray(np.moveaxis(post_tci, 0, 2), mode="RGB").convert("RGBA")
    draw = ImageDraw.Draw(image)
    for item in audit:
        if item["stratum"] == "burned-transition-boundary":
            continue
        x = (item["column"] + 0.5) * image.width / WIDTH
        y = (item["row"] + 0.5) * image.height / HEIGHT
        code = item["proposal_state_code"]
        color = STATE_COLORS[code]
        draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill=(*color, 220), outline=(255, 255, 255, 255), width=2)
    return image.convert("RGB")


def render_png(report: dict[str, Any], arrays: dict[str, Any], path: Path) -> None:
    canvas = Image.new("RGB", (1800, 1250), "#f4f0e8")
    draw = ImageDraw.Draw(canvas)
    ink, muted, teal, orange = "#15211d", "#5d6b64", "#006b64", "#f05a28"
    draw.rectangle((0, 0, 1800, 170), fill="#132a26")
    draw.text((62, 33), "BURNLENS / SEPARATE LABEL QA", fill="#b9d8cf", font=_font(21))
    draw.text((62, 73), "FIVE-STATE PROPOSAL AUDIT", fill="white", font=_font(38))
    draw.text((1360, 43), "MACHINE GATE", fill="#b9d8cf", font=_font(17))
    gate = report["summary"]["machine_decision"]
    draw.text((1360, 79), "PASS" if gate.startswith("PASS") else "FAIL", fill="#ffd166", font=_font(28))
    draw.text((1360, 121), "human inter-rater: none", fill="white", font=_font(14))

    boxes = [
        (45, 215, 450, 520),
        (480, 215, 885, 520),
        (915, 215, 1320, 520),
        (1350, 215, 1755, 520),
    ]
    _panel(canvas, draw, _state_image(arrays["proposal_states"]), boxes[0], "PROPOSAL STATE", "input GeoTIFF / native 20 m", nearest=True)
    _panel(canvas, draw, _state_image(arrays["expected_states"]), boxes[1], "QA RECOMPUTATION", "separate implementation / native 20 m", nearest=True)
    disagreement_rgb = np.full((HEIGHT, WIDTH, 3), (222, 232, 228), dtype=np.uint8)
    disagreement_rgb[arrays["state_disagreement"]] = (240, 90, 40)
    _panel(canvas, draw, Image.fromarray(disagreement_rgb, mode="RGB"), boxes[2], "DISAGREEMENT", "orange = mismatch / pale = match", nearest=True)
    _panel(canvas, draw, _audit_image(arrays["post_tci"], arrays["audit"]), boxes[3], "STRATIFIED AUDIT", "20 markers per state on post pixels")

    metrics = [
        (f"{report['summary']['state_agreement_percent']:.2f}%", "state agreement", teal),
        (f"{report['summary']['target_agreement_percent']:.2f}%", "target agreement", teal),
        (str(report["summary"]["audit_sample_count"]), "audit samples", teal),
        (str(report["summary"]["audit_disagreement_count"]), "audit disagreements", orange),
    ]
    left = 45
    for value, label, color in metrics:
        draw.rounded_rectangle((left, 565, left + 405, 700), radius=15, fill="#fffdf8", outline="#d4cec1", width=2)
        draw.text((left + 24, 590), value, fill=color, font=_font(29))
        draw.text((left + 24, 646), label, fill=ink, font=_font(16))
        left += 435

    draw.rounded_rectangle((45, 745, 1755, 1055), radius=18, fill="#e5efeb", outline="#aac8bf", width=2)
    draw.text((72, 772), "WHAT THIS QA PROVES / DOES NOT PROVE", fill=teal, font=_font(22))
    lines = [
        "The verifier reopens exact source pixels, recomputes quality and four spectral signals, and re-rasterizes context.",
        "It imports no proposal-classification helper and compares every state and target pixel independently.",
        "The audit samples all five states plus the candidate burned transition boundary with stable coordinates.",
        "Zero software disagreement is reproducibility evidence, not independent human annotation or field validation.",
        "The proposal remains one-event candidate evidence; dataset, split, baseline, model, and metrics remain absent.",
        "Official sources govern; neither the proposal nor QA is a fire perimeter, severity product, or decision aid.",
    ]
    for index, line in enumerate(lines):
        draw.text((88, 822 + index * 35), f"{index + 1}. {line}", fill=ink, font=_font(15))
    draw.text((45, 1093), "Contains modified Copernicus Sentinel data 2024  |  NIFC geometry is context only", fill=muted, font=_font(15))
    trace = (
        f"qa run {report['run_id']} / proposal run {report['label_proposal_run_id']} / source {report['git_source_commit'][:12]} / "
        f"software {report['software_version']} / QA {report['qa_protocol_version']}"
    )
    draw.text((45, 1128), trace, fill=muted, font=_font(13))
    draw.text((45, 1162), "dataset none / split none / baseline none / model none / human inter-rater validation none", fill=orange, font=_font(14))
    draw.text((45, 1200), WARNING, fill="#33443e", font=_font(12))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], png_name: str, path: Path) -> None:
    state_rows = "".join(
        "<tr>"
        f"<td>{escape(item['state'])}</td><td>{item['proposal_pixels']:,}</td><td>{item['qa_pixels']:,}</td>"
        f"<td>{item['matching_pixels']:,}</td><td>{item['audit_samples']}</td></tr>"
        for item in report["summary"]["per_state"]
    )
    audit_rows = "".join(
        "<tr>"
        f"<td>{escape(item['stratum'])}</td><td>{item['row']}</td><td>{item['column']}</td>"
        f"<td>{escape(item['proposal_state'])}</td><td>{'pass' if item['agree'] else 'FAIL'}</td>"
        f"<td>{'n/a' if item['dnbr'] is None else f'{item['dnbr']:.4f}'}</td>"
        f"<td>{item['pre_scl']} / {item['post_scl']}</td></tr>"
        for item in report["audit_sample"]
    )
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens five-state proposal QA</title><style>
:root {{ color-scheme:light; --ink:#15211d; --muted:#5d6b64; --paper:#f4f0e8; --panel:#fffdf8; --teal:#006b64; --orange:#f05a28; }}
* {{ box-sizing:border-box; }} body {{ margin:0; background:var(--paper); color:var(--ink); font:16px/1.55 system-ui,sans-serif; }} header {{ background:#132a26; color:white; padding:3rem max(5vw,2rem); }} header p {{ color:#b9d8cf; }} main {{ max-width:1250px; margin:auto; padding:2.5rem 1.5rem 5rem; }}
.warning {{ background:#fff1ca; border-left:6px solid #d87618; padding:1rem 1.2rem; font-weight:650; }} .hero {{ display:block; width:100%; height:auto; border:1px solid #c8c0b2; margin:1.5rem 0; }} .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:1rem; }} .card {{ background:var(--panel); border:1px solid #d9d1c4; border-radius:12px; padding:1.2rem; }} .decision {{ border:2px solid var(--orange); }} .value {{ color:var(--teal); font-size:2rem; font-weight:800; }} .table-wrap {{ overflow:auto; max-height:34rem; }} table {{ width:100%; border-collapse:collapse; background:var(--panel); }} th,td {{ padding:.65rem; border-bottom:1px solid #ddd5c9; text-align:left; white-space:nowrap; }} code {{ overflow-wrap:anywhere; white-space:normal; }} h2 {{ margin-top:2.4rem; }}
</style></head><body><header><p>BurnLens / Phase Two / separate implementation QA</p><h1>Five-state proposal audit</h1><p>All-pixel comparison plus a deterministic state and boundary sample.</p></header><main>
<p class="warning">{escape(WARNING)}</p><img class="hero" src="{escape(png_name)}" alt="Proposal and independently recomputed state rasters with disagreement and audit maps">
<section class="card decision"><h2>Decision</h2><p><strong>{escape(report['decision'])}</strong></p><p>{escape(report['decision_detail'])}</p><p>Machine gate: <code>{escape(report['summary']['machine_decision'])}</code>.</p></section>
<div class="grid"><div class="card"><div class="value">{report['summary']['state_agreement_percent']:.2f}%</div><div>state agreement</div></div><div class="card"><div class="value">{report['summary']['target_agreement_percent']:.2f}%</div><div>target agreement</div></div><div class="card"><div class="value">{report['summary']['audit_sample_count']}</div><div>audit samples</div></div><div class="card"><div class="value">{report['summary']['audit_disagreement_count']}</div><div>audit disagreements</div></div></div>
<h2>Per-state comparison</h2><div class="table-wrap"><table><thead><tr><th>State</th><th>Proposal pixels</th><th>QA pixels</th><th>Exact matches</th><th>Audit samples</th></tr></thead><tbody>{state_rows}</tbody></table></div>
<h2>Independence boundary</h2><div class="card"><p>The verifier is separately invoked, imports no proposal classification helper, reopens source pixels, recomputes quality and spectral evidence, and compares every output pixel. The same Codex director authored both implementations. This is reproducibility and implementation-path QA, not independent human annotation, field validation, or accuracy evidence.</p></div>
<h2>Deterministic audit sample</h2><div class="table-wrap"><table><thead><tr><th>Stratum</th><th>Row</th><th>Column</th><th>State</th><th>Agreement</th><th>dNBR</th><th>Pre/post SCL</th></tr></thead><tbody>{audit_rows}</tbody></table></div>
<h2>Traceability</h2><div class="card"><p><strong>QA run:</strong> <code>{escape(report['run_id'])}</code><br><strong>Proposal run:</strong> <code>{escape(report['label_proposal_run_id'])}</code><br><strong>Git source:</strong> <code>{escape(report['git_source_commit'])}</code><br><strong>Software / report / QA:</strong> <code>{escape(report['software_version'])}</code> / <code>{escape(report['report_version'])}</code> / <code>{escape(report['qa_protocol_version'])}</code><br><strong>AOI / target / schema / proposal:</strong> <code>{escape(report['aoi_version'])}</code> / <code>{escape(report['target_version'])}</code> / <code>{escape(report['label_schema_version'])}</code> / <code>{escape(report['label_proposal_version'])}</code><br><strong>Application / dataset / split / baseline / model:</strong> none / none / none / none / none</p></div>
<h2>Boundaries</h2><ul><li>Software agreement does not make the proposal accepted ground truth.</li><li>No independent human inter-rater validation or field validation occurred.</li><li>No dataset, split, baseline, model, metric, application, deployment, operational result, official status, or endorsement exists.</li><li>Contains modified Copernicus Sentinel data 2024. NIFC geometry is context only. Official sources govern.</li></ul>
</main></body></html>"""
    _write_utf8_lf(path, document)


def write_qa_report(
    *, report: dict[str, Any], arrays: dict[str, Any], output_directory: Path
) -> dict[str, Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": output_directory / f"{REPORT_ID}.json",
        "html": output_directory / f"{REPORT_ID}.html",
        "png": output_directory / f"{REPORT_ID}.png",
    }
    _write_utf8_lf(paths["json"], json.dumps(report, indent=2) + "\n")
    render_png(report, arrays, paths["png"])
    render_html(report, paths["png"].name, paths["html"])
    return paths


def verify_label_proposal(
    *,
    package: Path,
    aoi_report_path: Path,
    reference_geojson_path: Path,
    optical_report_path: Path,
    registration_report_path: Path,
    proposal_report_path: Path,
    state_raster_path: Path,
    target_raster_path: Path,
    output_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    visual_review_decision: str,
    visual_review_notes: str,
) -> dict[str, Path]:
    report, arrays = build_qa_report(
        package=package,
        aoi_report_path=aoi_report_path,
        reference_geojson_path=reference_geojson_path,
        optical_report_path=optical_report_path,
        registration_report_path=registration_report_path,
        proposal_report_path=proposal_report_path,
        state_raster_path=state_raster_path,
        target_raster_path=target_raster_path,
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
        visual_review_decision=visual_review_decision,
        visual_review_notes=visual_review_notes,
    )
    return write_qa_report(report=report, arrays=arrays, output_directory=output_directory)
