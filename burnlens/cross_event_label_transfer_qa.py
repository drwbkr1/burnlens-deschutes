"""Separately reproduce and audit the cross-event five-state proposals.

This module intentionally does not import the proposal transfer module or its
classification helpers.  It reopens the exact sources and independently
recomputes every state and target pixel.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw
import rasterio
from rasterio.io import MemoryFile
from rasterio.warp import Resampling, reproject

from .cross_event_optical_contract import (
    CONTRACT_VERSION as OPTICAL_CONTRACT_VERSION,
    CROSS_EVENT_CONTRACTS,
    validate_cross_event_contracts,
)
from .cross_event_source_fitness import EXPECTED_EVENTS, ROLE_PAIRS, _load_feasibility, _read_product
from .mtbs_cross_event_reference import (
    ALLOWED_VALUES as MTBS_ALLOWED_VALUES,
    CONTRACTS as MTBS_CONTRACTS,
    verify_package as verify_mtbs_package,
)
from .optical_pair_evidence import LABEL_PROTOCOL_VERSION, TARGET_VERSION, WARNING, _font, _reflectance, _write_utf8_lf
from .paired_intake import verify_registered_package


SOFTWARE_VERSION = "0.12.1"
REPORT_ID = "CROSS-EVENT-LABEL-TRANSFER-QA-2026-002"
REPORT_SCHEMA_VERSION = "0.1.1"
REPORT_VERSION = "separate-cross-event-label-transfer-qa-v0.1.1"
QA_PROTOCOL_VERSION = "separate-cross-event-five-state-qa-v0.1.0"
PROPOSAL_REPORT_ID = "CROSS-EVENT-LABEL-TRANSFER-2026-002"
PROPOSAL_REPORT_VERSION = "cross-event-five-state-label-transfer-evidence-v0.1.1"
TRANSFER_PROTOCOL_VERSION = "cross-event-five-state-transfer-v0.1.0"
LABEL_SCHEMA_VERSION = "burn-scar-five-state-schema-v0.1.0"
LABEL_PROPOSAL_VERSION = "deschutes-cross-event-label-proposal-v0.1.0"
SOURCE_FITNESS_SHA256 = "c9aa90894150e081a6df26b8ee16c502bd532b67d7ecd493e038a366a480b34f"
SOURCE_FITNESS_REPORT_ID = "CROSS-EVENT-SOURCE-FITNESS-2026-001"
SOURCE_FITNESS_REPORT_VERSION = "cross-event-source-fitness-v0.1.0"
SOURCE_FITNESS_RUN_ID = "BL-2026-07-16-cross-event-source-fitness-r006"
SOURCE_FITNESS_GIT_SOURCE_COMMIT = "cf1d9101e2760bf7d779b6fae68e605bb8809c1c"
SOURCE_FITNESS_DECISION = "ACCEPT_CROSS_EVENT_SOURCE_FITNESS_WITH_EXCLUSIONS"
TASK_ISSUE = 371
IGNORE_VALUE = 255
STATE_CODES = {"background-candidate": 0, "burned": 1, "unknown": 2, "excluded": 3, "review-needed": 4}
STATE_NAMES = {value: key for key, value in STATE_CODES.items()}
STATE_COLORS = {0: (0, 107, 100), 1: (240, 90, 40), 2: (233, 196, 106), 3: (86, 95, 91), 4: (126, 63, 143)}
ELIGIBLE_SCL = frozenset({4, 5})
REVIEW_SCL = frozenset({7})
KNOWN_SCL = frozenset(range(12))
MTBS_SUPPORT = frozenset({2, 3, 4})
MTBS_AMBIGUOUS = frozenset({1, 5})
MTBS_UNCOVERED = 255
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
STABILITY_FALLBACK_QUANTILE = 0.15
STABILITY_FALLBACK_MAX_NORMALIZED_SCORE = 6.0
AUDIT_PER_PRESENT_STATE = 5


class CrossEventLabelTransferQaError(RuntimeError):
    """A deterministic, secret-free QA failure."""


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _qa_dilate(mask: np.ndarray, iterations: int = 1) -> np.ndarray:
    output = mask.astype(bool, copy=True)
    rows, columns = output.shape
    for _ in range(iterations):
        padded = np.pad(output, 1, mode="constant", constant_values=False)
        output = np.logical_or.reduce(
            [padded[row:row + rows, column:column + columns] for row in range(3) for column in range(3)]
        )
    return output


def _qa_erode(mask: np.ndarray, iterations: int = 1) -> np.ndarray:
    return ~_qa_dilate(~mask.astype(bool), iterations)


def _qa_boundary(mask: np.ndarray) -> np.ndarray:
    return _qa_dilate(mask, 1) & _qa_dilate(~mask, 1)


def _qa_neighbor_count(mask: np.ndarray) -> np.ndarray:
    rows, columns = mask.shape
    padded = np.pad(mask.astype(np.uint8), 1, mode="constant", constant_values=0)
    result = np.zeros((rows, columns), dtype=np.uint8)
    for row in range(3):
        for column in range(3):
            result += padded[row:row + rows, column:column + columns]
    return result


def _qa_index(
    scene: dict[str, Any], arrays: dict[str, np.ndarray], first: str, second: str
) -> tuple[np.ndarray, np.ndarray]:
    first_values, first_valid = _reflectance(scene, arrays, first)
    second_values, second_valid = _reflectance(scene, arrays, second)
    denominator = first_values + second_values
    valid = first_valid & second_valid & np.isfinite(denominator) & (np.abs(denominator) > 1e-6)
    output = np.full(first_values.shape, np.nan, dtype=np.float32)
    output[valid] = (first_values[valid] - second_values[valid]) / denominator[valid]
    return output, valid


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
        pre_nbr_valid & post_nbr_valid & pre_ndvi_valid & post_ndvi_valid
        & pre_swir_valid & post_swir_valid & pre_nir_valid & post_nir_valid
    )
    valid &= np.logical_and.reduce([np.isfinite(item) for item in values.values()])
    return values, valid


def _qa_pair_quality(pre_scl: np.ndarray, post_scl: np.ndarray) -> np.ndarray:
    if pre_scl.shape != post_scl.shape:
        raise CrossEventLabelTransferQaError("QA SCL grids are not aligned")
    if set(int(value) for value in np.unique(pre_scl)) - set(KNOWN_SCL):
        raise CrossEventLabelTransferQaError("QA pre SCL has an unknown value")
    if set(int(value) for value in np.unique(post_scl)) - set(KNOWN_SCL):
        raise CrossEventLabelTransferQaError("QA post SCL has an unknown value")
    excluded = ~(
        np.isin(pre_scl, tuple(ELIGIBLE_SCL | REVIEW_SCL))
        & np.isin(post_scl, tuple(ELIGIBLE_SCL | REVIEW_SCL))
    )
    review = ~excluded & (np.isin(pre_scl, tuple(REVIEW_SCL)) | np.isin(post_scl, tuple(REVIEW_SCL)))
    state = np.zeros(pre_scl.shape, dtype=np.uint8)
    state[review] = 1
    state[excluded] = 2
    return state


def _qa_registration_state(shape: tuple[int, int], windows: list[dict[str, Any]]) -> np.ndarray:
    output = np.full(shape, MTBS_UNCOVERED, dtype=np.uint8)
    rank = {"pass": 0, "review-needed": 1, "excluded": 2}
    for item in windows:
        value = rank.get(item.get("state"))
        if value is None:
            raise CrossEventLabelTransferQaError("QA registration state is unsupported")
        window = item.get("pixel_window") or {}
        row, column = int(window.get("row_offset", -1)), int(window.get("column_offset", -1))
        height, width = int(window.get("height", 0)), int(window.get("width", 0))
        if row < 0 or column < 0 or height <= 0 or width <= 0 or row + height > shape[0] or column + width > shape[1]:
            raise CrossEventLabelTransferQaError("QA registration window exceeds the grid")
        view = output[row:row + height, column:column + width]
        view[view == MTBS_UNCOVERED] = value
        np.maximum(view, value, out=view)
    if np.any(output == MTBS_UNCOVERED):
        raise CrossEventLabelTransferQaError("QA registration windows do not cover the grid")
    return output


def _qa_mtbs(
    package: Path,
    event_group_id: str,
    shape: tuple[int, int],
    transform: rasterio.Affine,
) -> np.ndarray:
    contract = {item.event_group_id: item for item in MTBS_CONTRACTS}[event_group_id]
    output = np.full(shape, MTBS_UNCOVERED, dtype=np.uint8)
    provider_bytes = (package / contract.filename).read_bytes()
    if len(provider_bytes) != contract.expected_size_bytes or sha256(provider_bytes).hexdigest() != contract.expected_sha256:
        raise CrossEventLabelTransferQaError("QA MTBS clip changed before read")
    with MemoryFile(provider_bytes) as memory:
        with memory.open() as source:
            reproject(
                source=source.read(
                    out=np.empty((1, source.height, source.width), dtype=np.uint8)
                )[0],
                destination=output,
                src_transform=source.transform,
                src_crs=source.crs,
                dst_transform=transform,
                dst_crs="EPSG:32610",
                src_nodata=None,
                dst_nodata=MTBS_UNCOVERED,
                resampling=Resampling.nearest,
                init_dest_nodata=True,
            )
    if set(int(value) for value in np.unique(output)) - set(MTBS_ALLOWED_VALUES):
        raise CrossEventLabelTransferQaError("QA MTBS clip coverage/domain mismatch")
    return output


def _qa_classify(
    pair_quality: np.ndarray,
    registration_state: np.ndarray,
    reference_mask: np.ndarray,
    mtbs: np.ndarray,
    evidence: dict[str, np.ndarray],
    numeric_valid: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    usable = (pair_quality == 0) & (registration_state == 0) & numeric_valid
    excluded = (pair_quality == 2) | (registration_state == 2) | ~numeric_valid | (mtbs == 6) | (mtbs == 255)
    quality_review = ((pair_quality == 1) | (registration_state == 1)) & ~excluded
    dnbr, ndvi_loss = evidence["dnbr"], evidence["ndvi_loss"]
    swir_gain, nir_loss = evidence["swir_gain"], evidence["nir_loss"]
    support = (
        (ndvi_loss >= BURN_NDVI_LOSS_MIN).astype(np.uint8)
        + (swir_gain >= BURN_SWIR_GAIN_MIN).astype(np.uint8)
        + (nir_loss >= BURN_NIR_LOSS_MIN).astype(np.uint8)
    )
    burn = (dnbr >= BURN_DNBR_MIN) & (support >= BURN_SUPPORTING_SIGNALS_MIN)
    stable_primary = (
        (np.abs(dnbr) <= STABLE_ABS_DNBR_MAX)
        & (np.abs(ndvi_loss) <= STABLE_ABS_NDVI_CHANGE_MAX)
        & (np.abs(swir_gain) <= STABLE_ABS_SWIR_CHANGE_MAX)
        & (np.abs(nir_loss) <= STABLE_ABS_NIR_CHANGE_MAX)
    )
    burn_coherent = burn & (_qa_neighbor_count(burn) >= BURN_NEIGHBOR_SUPPORT_MIN)
    core = _qa_erode(reference_mask, BOUNDARY_REVIEW_PX)
    outer = _qa_dilate(reference_mask, BOUNDARY_REVIEW_PX)
    reference_boundary = outer & ~core
    mtbs_support = np.isin(mtbs, tuple(MTBS_SUPPORT))
    mtbs_ambiguous = np.isin(mtbs, tuple(MTBS_AMBIGUOUS))
    stability_score = np.sqrt(
        (np.abs(dnbr) / STABLE_ABS_DNBR_MAX) ** 2
        + (np.abs(ndvi_loss) / STABLE_ABS_NDVI_CHANGE_MAX) ** 2
        + (np.abs(swir_gain) / STABLE_ABS_SWIR_CHANGE_MAX) ** 2
        + (np.abs(nir_loss) / STABLE_ABS_NIR_CHANGE_MAX) ** 2
    )
    fallback_pool = usable & ~outer & (mtbs == 0) & ~burn & np.isfinite(stability_score)
    stable_fallback = np.zeros(pair_quality.shape, dtype=bool)
    if np.any(fallback_pool):
        threshold = min(
            float(np.quantile(stability_score[fallback_pool], STABILITY_FALLBACK_QUANTILE, method="lower")),
            STABILITY_FALLBACK_MAX_NORMALIZED_SCORE,
        )
        stable_fallback = fallback_pool & (stability_score <= threshold)
    stable_coherent = (
        (stable_primary & (_qa_neighbor_count(stable_primary) >= STABLE_NEIGHBOR_SUPPORT_MIN))
        | (stable_fallback & (_qa_neighbor_count(stable_fallback) >= STABLE_NEIGHBOR_SUPPORT_MIN))
    )
    burned_raw = usable & core & mtbs_support & burn_coherent
    background_raw = usable & ~outer & (mtbs == 0) & stable_coherent
    conflict = usable & (
        (~reference_mask & burn_coherent)
        | (reference_mask & stable_coherent)
        | (reference_mask & (mtbs == 0))
        | (~reference_mask & mtbs_support)
        | (mtbs_support & stable_coherent)
    )
    ambiguity = usable & reference_mask & mtbs_ambiguous
    burned_boundary = usable & _qa_boundary(burned_raw)
    review = quality_review | reference_boundary | conflict | ambiguity | burned_boundary
    states = np.full(pair_quality.shape, STATE_CODES["unknown"], dtype=np.uint8)
    states[excluded] = STATE_CODES["excluded"]
    states[review & ~excluded] = STATE_CODES["review-needed"]
    states[burned_raw & ~review & ~excluded] = STATE_CODES["burned"]
    states[background_raw & ~review & ~excluded] = STATE_CODES["background-candidate"]
    target = np.full(pair_quality.shape, IGNORE_VALUE, dtype=np.uint8)
    target[states == 0] = 0
    target[states == 1] = 1
    return states, target


def _read_output_raster(
    path: Path,
    *,
    expected_hash: str,
    expected_shape: tuple[int, int],
    expected_transform: rasterio.Affine,
    expected_kind: str,
    event_group_id: str,
    proposal_run_id: str,
    proposal_commit: str,
) -> np.ndarray:
    if _sha256_file(path) != expected_hash:
        raise CrossEventLabelTransferQaError("proposal output hash mismatch")
    with rasterio.open(path) as source:
        if source.driver != "GTiff" or source.crs is None or source.crs.to_epsg() != 32610:
            raise CrossEventLabelTransferQaError("proposal output format/CRS mismatch")
        if source.count != 1 or source.dtypes != ("uint8",) or (source.height, source.width) != expected_shape:
            raise CrossEventLabelTransferQaError("proposal output grid mismatch")
        if any(abs(float(a) - float(b)) > 1e-9 for a, b in zip(source.transform[:6], expected_transform[:6])):
            raise CrossEventLabelTransferQaError("proposal output transform mismatch")
        tags = source.tags()
        required = {
            "repository": "drwbkr1/burnlens-deschutes",
            "task_issue": str(TASK_ISSUE),
            "event_group_id": event_group_id,
            "run_id": proposal_run_id,
            "git_source_commit": proposal_commit,
            "software_version": SOFTWARE_VERSION,
            "label_protocol_version": LABEL_PROTOCOL_VERSION,
            "label_schema_version": LABEL_SCHEMA_VERSION,
            "label_proposal_version": LABEL_PROPOSAL_VERSION,
            "raster_kind": expected_kind,
            "dataset_version": "none",
            "model_version": "none",
        }
        if any(tags.get(key) != value for key, value in required.items()):
            raise CrossEventLabelTransferQaError("proposal output trace tags mismatch")
        return source.read(
            out=np.empty((1, source.height, source.width), dtype=np.uint8)
        )[0]


def _select_coordinates(mask: np.ndarray, count: int, seed: str) -> list[tuple[int, int]]:
    coordinates = np.argwhere(mask)
    if len(coordinates) == 0:
        return []
    seed_value = int.from_bytes(sha256(seed.encode("utf-8")).digest()[:8], "big")
    rng = np.random.default_rng(seed_value)
    indexes = rng.choice(len(coordinates), size=min(count, len(coordinates)), replace=False)
    return sorted((int(coordinates[index, 0]), int(coordinates[index, 1])) for index in indexes)


def _audit_event(
    event_group_id: str,
    proposal_states: np.ndarray,
    proposal_target: np.ndarray,
    expected_states: np.ndarray,
    expected_target: np.ndarray,
    reference_mask: np.ndarray,
    mtbs: np.ndarray,
    pair_quality: np.ndarray,
    registration_state: np.ndarray,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    audit: list[dict[str, Any]] = []
    coverage: list[dict[str, Any]] = []
    for code in sorted(STATE_NAMES):
        mask = proposal_states == code
        coordinates = _select_coordinates(mask, AUDIT_PER_PRESENT_STATE, f"{event_group_id}:{code}")
        coverage.append({
            "state": STATE_NAMES[code],
            "state_code": code,
            "available_pixels": int(mask.sum()),
            "sample_count": len(coordinates),
            "absence_verified": len(coordinates) == 0 and int(mask.sum()) == 0,
        })
        for row, column in coordinates:
            audit.append({
                "event_group_id": event_group_id,
                "state": STATE_NAMES[code],
                "state_code": code,
                "row": row,
                "column": column,
                "proposal_state": STATE_NAMES[int(proposal_states[row, column])],
                "qa_state": STATE_NAMES[int(expected_states[row, column])],
                "proposal_target": int(proposal_target[row, column]),
                "qa_target": int(expected_target[row, column]),
                "reference_context": bool(reference_mask[row, column]),
                "mtbs_value": int(mtbs[row, column]),
                "pair_quality_state": int(pair_quality[row, column]),
                "registration_state": int(registration_state[row, column]),
                "agree": bool(
                    proposal_states[row, column] == expected_states[row, column]
                    and proposal_target[row, column] == expected_target[row, column]
                ),
            })
    return audit, coverage


def _load_proposal(path: Path) -> dict[str, Any]:
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CrossEventLabelTransferQaError("proposal report is unreadable") from error
    if report.get("report_id") != PROPOSAL_REPORT_ID or report.get("report_version") != PROPOSAL_REPORT_VERSION:
        raise CrossEventLabelTransferQaError("proposal report identity mismatch")
    if report.get("software_version") != SOFTWARE_VERSION:
        raise CrossEventLabelTransferQaError("proposal software version mismatch")
    if report.get("label_protocol_version") != LABEL_PROTOCOL_VERSION:
        raise CrossEventLabelTransferQaError("proposal label protocol mismatch")
    if report.get("label_schema_version") != LABEL_SCHEMA_VERSION:
        raise CrossEventLabelTransferQaError("proposal label schema mismatch")
    if report.get("label_proposal_version") != LABEL_PROPOSAL_VERSION:
        raise CrossEventLabelTransferQaError("proposal version mismatch")
    if report.get("transfer_protocol_version") != TRANSFER_PROTOCOL_VERSION:
        raise CrossEventLabelTransferQaError("proposal transfer protocol mismatch")
    if report.get("decision") != "PROPOSAL_READY_FOR_SEPARATE_QA":
        raise CrossEventLabelTransferQaError("proposal is not ready for separate QA")
    if report.get("dataset_version") is not None or report.get("model_version") is not None:
        raise CrossEventLabelTransferQaError("proposal overstates dataset/model status")
    return report


def build_qa_report(
    *,
    optical_package: Path,
    mtbs_package: Path,
    feasibility_report_path: Path,
    source_fitness_report_path: Path,
    proposal_report_path: Path,
    proposal_output_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    optical_verification = verify_registered_package(
        optical_package,
        CROSS_EVENT_CONTRACTS,
        contract_validator=validate_cross_event_contracts,
        contract_version=OPTICAL_CONTRACT_VERSION,
        allow_multilink_registration_manifest=True,
    )
    if not optical_verification["accepted_as_unchanged_registered_package"]:
        raise CrossEventLabelTransferQaError("QA optical package verification failed")
    mtbs_verification = verify_mtbs_package(mtbs_package)
    proposal = _load_proposal(proposal_report_path)
    if _sha256_file(source_fitness_report_path) != SOURCE_FITNESS_SHA256:
        raise CrossEventLabelTransferQaError("QA source-fitness checkpoint hash mismatch")
    try:
        source_fitness = json.loads(source_fitness_report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CrossEventLabelTransferQaError("QA source-fitness checkpoint is unreadable") from error
    source_fitness_identity = (
        source_fitness.get("report_id"),
        source_fitness.get("report_version"),
        source_fitness.get("run_id"),
        source_fitness.get("git_source_commit"),
        source_fitness.get("label_protocol_version"),
        source_fitness.get("label_schema_version"),
        source_fitness.get("decision", {}).get("machine"),
    )
    if source_fitness_identity != (
        SOURCE_FITNESS_REPORT_ID,
        SOURCE_FITNESS_REPORT_VERSION,
        SOURCE_FITNESS_RUN_ID,
        SOURCE_FITNESS_GIT_SOURCE_COMMIT,
        LABEL_PROTOCOL_VERSION,
        LABEL_SCHEMA_VERSION,
        SOURCE_FITNESS_DECISION,
    ):
        raise CrossEventLabelTransferQaError("QA source-fitness identity or decision drifted")
    if proposal.get("git_source_commit") != git_source_commit:
        raise CrossEventLabelTransferQaError("proposal and QA source commits differ")
    feasibility, candidates = _load_feasibility(feasibility_report_path)
    fitness_by_event = {item["event_group_id"]: item for item in source_fitness["events"]}
    proposal_by_event = {item["event_group_id"]: item for item in proposal["events"]}
    contracts = {item.role: item for item in CROSS_EVENT_CONTRACTS}
    if tuple(proposal_by_event) != EXPECTED_EVENTS:
        raise CrossEventLabelTransferQaError("proposal event order mismatch")

    events: list[dict[str, Any]] = []
    visuals: list[dict[str, Any]] = []
    total_state_mismatches = 0
    total_target_mismatches = 0
    all_audit: list[dict[str, Any]] = []
    for candidate in candidates:
        event_id = candidate["event_group_id"]
        proposal_event = proposal_by_event[event_id]
        fitness_event = fitness_by_event[event_id]
        if any(
            proposal_event.get(key) != candidate.get(key)
            for key in ("fire_id", "fire_name", "geography_group_id", "time_group_id")
        ):
            raise CrossEventLabelTransferQaError("proposal event grouping mismatch")
        pre_role, post_role = ROLE_PAIRS[event_id]
        pre_scene, pre = _read_product(optical_package, contracts[pre_role], candidate["source_geometry"])
        post_scene, post = _read_product(optical_package, contracts[post_role], candidate["source_geometry"])
        shape = pre["B04"].shape
        transform = rasterio.Affine(*pre_scene["rasters"]["B04"]["crop_transform"])
        pair_quality = _qa_pair_quality(pre["SCL"], post["SCL"])
        registration_state = _qa_registration_state(shape, fitness_event["registration"]["windows"])
        mtbs = _qa_mtbs(mtbs_package, event_id, shape, transform)
        evidence, numeric_valid = _qa_evidence(pre_scene, pre, post_scene, post)
        expected_states, expected_target = _qa_classify(
            pair_quality, registration_state, pre["MASK20"], mtbs, evidence, numeric_valid
        )
        state_meta = proposal_event["outputs"]["state"]
        target_meta = proposal_event["outputs"]["target"]
        proposal_states = _read_output_raster(
            proposal_output_directory / state_meta["filename"],
            expected_hash=state_meta["sha256"],
            expected_shape=shape,
            expected_transform=transform,
            expected_kind="five-state-companion-proposal",
            event_group_id=event_id,
            proposal_run_id=proposal["run_id"],
            proposal_commit=proposal["git_source_commit"],
        )
        proposal_target = _read_output_raster(
            proposal_output_directory / target_meta["filename"],
            expected_hash=target_meta["sha256"],
            expected_shape=shape,
            expected_transform=transform,
            expected_kind="candidate-binary-target",
            event_group_id=event_id,
            proposal_run_id=proposal["run_id"],
            proposal_commit=proposal["git_source_commit"],
        )
        state_mismatch = proposal_states != expected_states
        target_mismatch = proposal_target != expected_target
        state_count = int(state_mismatch.sum())
        target_count = int(target_mismatch.sum())
        total_state_mismatches += state_count
        total_target_mismatches += target_count
        audit, coverage = _audit_event(
            event_id,
            proposal_states,
            proposal_target,
            expected_states,
            expected_target,
            pre["MASK20"],
            mtbs,
            pair_quality,
            registration_state,
        )
        all_audit.extend(audit)
        if any(not item["agree"] for item in audit):
            raise CrossEventLabelTransferQaError("deterministic audit contains disagreement")
        per_state = []
        for code in sorted(STATE_NAMES):
            proposal_count = int((proposal_states == code).sum())
            expected_count = int((expected_states == code).sum())
            per_state.append({
                "state": STATE_NAMES[code],
                "code": code,
                "proposal_pixels": proposal_count,
                "qa_pixels": expected_count,
                "matching_pixels": int(((proposal_states == code) & (expected_states == code)).sum()),
                "sample_count": next(item["sample_count"] for item in coverage if item["state_code"] == code),
                "absence_verified": next(item["absence_verified"] for item in coverage if item["state_code"] == code),
            })
        events.append({
            "event_group_id": event_id,
            "fire_name": candidate["fire_name"],
            "pixel_count": int(proposal_states.size),
            "state_mismatch_pixels": state_count,
            "target_mismatch_pixels": target_count,
            "state_agreement_percent": round(100 * (1 - state_count / proposal_states.size), 6),
            "target_agreement_percent": round(100 * (1 - target_count / proposal_target.size), 6),
            "per_state": per_state,
            "audit_coverage": coverage,
            "audit": audit,
        })
        visuals.append({
            "event_group_id": event_id,
            "fire_name": candidate["fire_name"],
            "proposal_states": proposal_states,
            "expected_states": expected_states,
            "difference": state_mismatch | target_mismatch,
        })

    machine_pass = (
        total_state_mismatches == 0
        and total_target_mismatches == 0
        and all(item["agree"] for item in all_audit)
        and all(
            row["sample_count"] == min(AUDIT_PER_PRESENT_STATE, row["proposal_pixels"])
            if row["proposal_pixels"] > 0 else row["absence_verified"]
            for event in events for row in event["per_state"]
        )
    )
    if not machine_pass:
        raise CrossEventLabelTransferQaError("separate QA gate failed")
    report = {
        "report_id": REPORT_ID,
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
        "qa_protocol_version": QA_PROTOCOL_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": None,
        "target_version": TARGET_VERSION,
        "dataset_version": None,
        "label_protocol_version": LABEL_PROTOCOL_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "label_proposal_version": LABEL_PROPOSAL_VERSION,
        "transfer_protocol_version": TRANSFER_PROTOCOL_VERSION,
        "baseline_version": None,
        "model_version": None,
        "input_hashes": {
            "proposal_report_sha256": _sha256_file(proposal_report_path),
            "feasibility_report_sha256": _sha256_file(feasibility_report_path),
            "source_fitness_report_sha256": SOURCE_FITNESS_SHA256,
            "optical_registration_manifest_sha256": optical_verification["registration_manifest_sha256"],
            "mtbs_registration_manifest_sha256": mtbs_verification["registration_manifest_sha256"],
        },
        "proposal_trace": {
            "proposal_run_id": proposal["run_id"],
            "proposal_git_source_commit": proposal["git_source_commit"],
            "proposal_software_version": proposal["software_version"],
            "proposal_report_version": proposal["report_version"],
        },
        "independence": {
            "separately_invoked": True,
            "imports_transfer_module": False,
            "imports_transfer_classifier": False,
            "reopens_exact_sources": True,
            "recomputes_spectral_quality_registration_mtbs_and_state_logic": True,
            "human_inter_rater_validation": False,
        },
        "events": events,
        "aggregate": {
            "event_count": len(events),
            "pixel_count": sum(item["pixel_count"] for item in events),
            "state_mismatch_pixels": total_state_mismatches,
            "target_mismatch_pixels": total_target_mismatches,
            "audit_sample_count": len(all_audit),
            "all_audit_samples_agree": all(item["agree"] for item in all_audit),
            "all_present_states_sampled_and_absent_states_verified": True,
        },
        "decision": "ACCEPT_CROSS_EVENT_LABEL_TRANSFER_PROPOSAL",
        "decision_detail": "The separately invoked implementation reopened all six exact registered source assets, reproduced every proposal state and target pixel across Tepee and McKay, and completed deterministic per-state audits. Accept this exact proposal as reviewable evidence only; no dataset, model, accuracy, field-validation, operational, or official claim follows.",
        "claims": {
            "proven": [
                "Every proposal state and target pixel is reproducible from the exact registered sources under a separately implemented software path.",
                "Both event groups preserve their frozen grouping and Tepee source-fitness exclusions.",
            ],
            "not_proven": [
                "Independent human inter-rater agreement, field validity, universal calibration, dataset fitness, model performance, or operational readiness.",
            ],
        },
        "source_snapshot_sha256": feasibility["input_hashes"]["source_snapshot_sha256"],
        "warning": WARNING,
    }
    return report, visuals


def _state_image(states: np.ndarray) -> Image.Image:
    rgb = np.zeros((*states.shape, 3), dtype=np.uint8)
    for code, color in STATE_COLORS.items():
        rgb[states == code] = color
    return Image.fromarray(rgb, mode="RGB")


def render_png(report: dict[str, Any], visuals: list[dict[str, Any]], path: Path) -> None:
    canvas = Image.new("RGB", (1800, 1320), "#f4f0e8")
    draw = ImageDraw.Draw(canvas)
    ink, muted, teal, orange = "#15211d", "#5d6b64", "#006b64", "#f05a28"
    draw.rectangle((0, 0, 1800, 170), fill="#132a26")
    draw.text((58, 30), "BURNLENS / SEPARATE SOFTWARE QA", fill="#b9d8cf", font=_font(20))
    draw.text((58, 70), "CROSS-EVENT LABEL TRANSFER VERIFIED", fill="white", font=_font(34))
    draw.text((58, 122), "Every state and target pixel independently reproduced / human validation still absent", fill="#b9d8cf", font=_font(16))
    draw.text((1450, 54), "DECISION", fill="#b9d8cf", font=_font(14))
    draw.text((1450, 86), "ACCEPT", fill="#72d6b1", font=_font(27))

    for index, visual in enumerate(visuals):
        top = 225 + index * 340
        draw.text((55, top - 31), f"{visual['fire_name']} / {visual['event_group_id']}", fill=teal, font=_font(18))
        boxes = [(55, top, 550, top + 245), (650, top, 1145, top + 245), (1245, top, 1745, top + 245)]
        images = [
            (_state_image(visual["proposal_states"]), "PROPOSAL", "five-state output"),
            (_state_image(visual["expected_states"]), "SEPARATE QA", "recomputed states"),
            (Image.fromarray(np.where(visual["difference"][..., None], np.array([210, 50, 40]), np.array([49, 145, 109])).astype(np.uint8), mode="RGB"), "PIXEL AGREEMENT", "green = exact / red = mismatch"),
        ]
        for box, (image, title, subtitle) in zip(boxes, images):
            canvas.paste(image.resize((box[2] - box[0], box[3] - box[1]), Image.Resampling.NEAREST), (box[0], box[1]))
            draw.rectangle(box, outline="#132a26", width=3)
            draw.rectangle((box[0], box[1], box[2], box[1] + 54), fill="#132a26")
            draw.text((box[0] + 13, box[1] + 7), title, fill="white", font=_font(15))
            draw.text((box[0] + 13, box[1] + 31), subtitle, fill="#b9d8cf", font=_font(11))
        event = report["events"][index]
        draw.text((55, top + 267), f"state mismatch {event['state_mismatch_pixels']} / target mismatch {event['target_mismatch_pixels']} / agreement {event['state_agreement_percent']:.6f}% / five states audited (zero-count absence allowed)", fill=ink, font=_font(14))

    box_top = 915
    draw.rounded_rectangle((55, box_top, 1745, 1125), radius=18, fill="#e5efeb", outline="#aac8bf", width=2)
    draw.text((82, box_top + 24), "INDEPENDENCE AND SCOPE", fill=teal, font=_font(20))
    notes = [
        "Separate invocation; transfer module and classifier are not imported.",
        "All four Sentinel archives and both MTBS clips were reopened and reprojected from exact registered bytes.",
        "SCL, registration windows, spectral changes, MTBS rules, state logic, targets, tags, hashes, and grids were recomputed.",
        "Deterministic samples cover every present state per event; zero-count states are explicitly verified absent.",
        "This is reproducibility QA, not independent human inter-rater agreement or field validation.",
    ]
    for index, note in enumerate(notes):
        draw.text((98, box_top + 65 + index * 28), f"{index + 1}. {note}", fill=ink, font=_font(13))

    draw.text((55, 1160), f"run {report['run_id']} / source {report['git_source_commit'][:12]} / software {report['software_version']} / QA {report['qa_protocol_version']}", fill=muted, font=_font(12))
    draw.text((55, 1194), f"proposal run {report['proposal_trace']['proposal_run_id']} / proposal source {report['proposal_trace']['proposal_git_source_commit'][:12]} / schema {report['label_schema_version']}", fill=muted, font=_font(12))
    draw.text((55, 1228), "app none / dataset none / split none / baseline none / model none / field validation none", fill=orange, font=_font(14))
    draw.text((55, 1265), report["warning"], fill="#33443e", font=_font(11))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], png_name: str, path: Path) -> None:
    sections = []
    for event in report["events"]:
        rows = "".join(
            f"<tr><td>{escape(item['state'])}</td><td>{item['proposal_pixels']:,}</td><td>{item['qa_pixels']:,}</td><td>{item['matching_pixels']:,}</td><td>{item['sample_count']}</td><td>{'yes' if item['absence_verified'] else 'n/a'}</td></tr>"
            for item in event["per_state"]
        )
        sections.append(f"""<section class="card"><h2>{escape(event['fire_name'])}</h2><div class="metrics"><div><strong>{event['pixel_count']:,}</strong><span>pixels</span></div><div><strong>{event['state_mismatch_pixels']}</strong><span>state mismatches</span></div><div><strong>{event['target_mismatch_pixels']}</strong><span>target mismatches</span></div><div><strong>{event['state_agreement_percent']:.6f}%</strong><span>agreement</span></div></div><div class="table-wrap"><table><thead><tr><th>State</th><th>Proposal</th><th>QA</th><th>Matching</th><th>Samples</th><th>Absent verified</th></tr></thead><tbody>{rows}</tbody></table></div></section>""")
    document = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BurnLens separate cross-event label QA</title><style>
:root {{ --ink:#15211d;--paper:#f4f0e8;--panel:#fffdf8;--teal:#006b64;--orange:#f05a28; }} * {{ box-sizing:border-box; }} body {{ margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif; }} header {{ background:#132a26;color:white;padding:3rem max(5vw,2rem); }} header p {{ color:#b9d8cf; }} main {{ max-width:1300px;margin:auto;padding:2.5rem 1.5rem 5rem; }} .warning {{ background:#fff1ca;border-left:6px solid #d87618;padding:1rem 1.2rem;font-weight:650; }} .hero {{ width:100%;height:auto;border:1px solid #c8c0b2; }} .card {{ background:var(--panel);border:1px solid #d9d1c4;border-radius:12px;padding:1.2rem;margin:1.2rem 0; }} .decision {{ border:2px solid var(--teal); }} .metrics {{ display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:.8rem;margin:1rem 0; }} .metrics div {{ background:#e5efeb;padding:1rem;border-radius:10px; }} .metrics strong {{ display:block;color:var(--teal);font-size:1.5rem; }} .metrics span {{ color:#5d6b64; }} .table-wrap {{ overflow-x:auto; }} table {{ width:100%;border-collapse:collapse; }} th,td {{ padding:.65rem;border-bottom:1px solid #ddd5c9;text-align:left; }} code {{ overflow-wrap:anywhere; }}
</style></head><body><header><p>BurnLens / Phase Two / Objective Four</p><h1>Separate cross-event label-transfer QA</h1><p>Exact pixel reproduction from reopened registered sources.</p></header><main><p class="warning">{escape(report['warning'])}</p><img class="hero" src="{escape(png_name)}" alt="Proposal and independent QA state maps with green all-pixel agreement maps for Tepee and McKay">
<section class="card decision"><h2>Decision</h2><p><strong>{escape(report['decision'])}</strong></p><p>{escape(report['decision_detail'])}</p><p>{report['aggregate']['state_mismatch_pixels']} state mismatches; {report['aggregate']['target_mismatch_pixels']} target mismatches; {report['aggregate']['audit_sample_count']} deterministic audit samples.</p></section>{''.join(sections)}
<section class="card"><h2>Independence</h2><ul><li>Separately invoked: yes.</li><li>Imports transfer module/classifier: no / no.</li><li>Reopens exact sources and recomputes source logic: yes.</li><li>Independent human inter-rater validation: no.</li></ul></section>
<section class="card"><h2>Traceability</h2><p><strong>QA run / source:</strong> <code>{escape(report['run_id'])}</code> / <code>{escape(report['git_source_commit'])}</code><br><strong>Proposal run / source:</strong> <code>{escape(report['proposal_trace']['proposal_run_id'])}</code> / <code>{escape(report['proposal_trace']['proposal_git_source_commit'])}</code><br><strong>Software / QA protocol:</strong> <code>{escape(report['software_version'])}</code> / <code>{escape(report['qa_protocol_version'])}</code><br><strong>Label protocol / schema / proposal:</strong> <code>{escape(report['label_protocol_version'])}</code> / <code>{escape(report['label_schema_version'])}</code> / <code>{escape(report['label_proposal_version'])}</code><br><strong>Application / dataset / baseline / model:</strong> none / none / none / none</p></section>
<section class="card"><h2>Boundary</h2><ul>{''.join(f'<li><strong>Not proven:</strong> {escape(item)}</li>' for item in report['claims']['not_proven'])}</ul></section></main></body></html>"""
    _write_utf8_lf(path, document)


def write_qa_report(
    report: dict[str, Any],
    visuals: list[dict[str, Any]],
    json_path: Path,
    html_path: Path,
    png_path: Path,
) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    _write_utf8_lf(json_path, json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    render_png(report, visuals, png_path)
    render_html(report, png_path.name, html_path)
