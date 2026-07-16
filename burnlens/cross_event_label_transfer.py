"""Transfer BurnLens's five-state proposal across the frozen Tepee/McKay pairs.

The output is proposal evidence for separate QA.  It is not a dataset, accepted
ground truth, trained artifact, accuracy result, or operational application.
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
    PACKAGE_ID as OPTICAL_PACKAGE_ID,
    TERMS_REVIEW_ID as OPTICAL_TERMS_REVIEW_ID,
    validate_cross_event_contracts,
)
from .cross_event_source_fitness import (
    EXPECTED_EVENTS,
    ROLE_PAIRS,
    _load_feasibility,
    _read_product,
)
from .label_proposal import (
    BOUNDARY_REVIEW_PX,
    BURN_DNBR_MIN,
    BURN_NDVI_LOSS_MIN,
    BURN_NIR_LOSS_MIN,
    BURN_NEIGHBOR_SUPPORT_MIN,
    BURN_SUPPORTING_SIGNALS_MIN,
    BURN_SWIR_GAIN_MIN,
    IGNORE_VALUE,
    LABEL_SCHEMA_VERSION,
    STABLE_ABS_DNBR_MAX,
    STABLE_ABS_NDVI_CHANGE_MAX,
    STABLE_ABS_NIR_CHANGE_MAX,
    STABLE_ABS_SWIR_CHANGE_MAX,
    STABLE_NEIGHBOR_SUPPORT_MIN,
    STATE_CODES,
    STATE_COLORS,
    STATE_NAMES,
    boundary_band,
    dilate_mask,
    erode_mask,
    neighbor_support,
    spectral_evidence,
)
from .mtbs_cross_event_reference import (
    ALLOWED_VALUES as MTBS_ALLOWED_VALUES,
    CONTRACT_VERSION as MTBS_CONTRACT_VERSION,
    CONTRACTS as MTBS_CONTRACTS,
    PACKAGE_ID as MTBS_PACKAGE_ID,
    SOURCE_RECORD_ID as MTBS_SOURCE_RECORD_ID,
    TERMS_REVIEW_ID as MTBS_TERMS_REVIEW_ID,
    verify_package as verify_mtbs_package,
)
from .optical_pair_evidence import (
    LABEL_PROTOCOL_VERSION,
    TARGET_VERSION,
    WARNING,
    _font,
    _write_utf8_lf,
    classify_pair_quality,
)
from .paired_intake import verify_registered_package


SOFTWARE_VERSION = "0.12.0"
REPORT_ID = "CROSS-EVENT-LABEL-TRANSFER-2026-001"
REPORT_SCHEMA_VERSION = "0.1.0"
REPORT_VERSION = "cross-event-five-state-label-transfer-evidence-v0.1.0"
TRANSFER_PROTOCOL_VERSION = "cross-event-five-state-transfer-v0.1.0"
LABEL_PROPOSAL_VERSION = "deschutes-cross-event-label-proposal-v0.1.0"
SOURCE_FITNESS_REPORT_ID = "CROSS-EVENT-SOURCE-FITNESS-2026-001"
SOURCE_FITNESS_SHA256 = "c9aa90894150e081a6df26b8ee16c502bd532b67d7ecd493e038a366a480b34f"
TASK_ISSUE = 367
MTBS_SUPPORT_VALUES = frozenset({2, 3, 4})
MTBS_AMBIGUOUS_VALUES = frozenset({1, 5})
MTBS_NONPROCESSING_VALUE = 6
MTBS_BACKGROUND_VALUE = 0
MTBS_UNCOVERED_VALUE = 255
STABILITY_FALLBACK_QUANTILE = 0.15
STABILITY_FALLBACK_MAX_NORMALIZED_SCORE = 6.0


class CrossEventLabelTransferError(RuntimeError):
    """A deterministic, secret-free transfer failure."""


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _load_source_fitness(path: Path) -> dict[str, Any]:
    if _sha256_file(path) != SOURCE_FITNESS_SHA256:
        raise CrossEventLabelTransferError("source-fitness checkpoint hash mismatch")
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CrossEventLabelTransferError("source-fitness checkpoint is unreadable") from error
    if report.get("report_id") != SOURCE_FITNESS_REPORT_ID:
        raise CrossEventLabelTransferError("source-fitness checkpoint identity mismatch")
    if report.get("label_protocol_version") != LABEL_PROTOCOL_VERSION:
        raise CrossEventLabelTransferError("source-fitness label protocol mismatch")
    if report.get("label_schema_version") != LABEL_SCHEMA_VERSION:
        raise CrossEventLabelTransferError("source-fitness label schema mismatch")
    decision = report.get("decision", {})
    if decision.get("machine") != "ACCEPT_CROSS_EVENT_SOURCE_FITNESS_WITH_EXCLUSIONS":
        raise CrossEventLabelTransferError("source-fitness machine decision is not transferable")
    if decision.get("visual_review") != "ACCEPT_CROSS_EVENT_SOURCE_FITNESS_WITH_EXCLUSIONS":
        raise CrossEventLabelTransferError("source-fitness visual decision is not transferable")
    events = report.get("events")
    if not isinstance(events, list) or tuple(item.get("event_group_id") for item in events) != EXPECTED_EVENTS:
        raise CrossEventLabelTransferError("source-fitness event order mismatch")
    return report


def _registration_state(shape: tuple[int, int], windows: list[dict[str, Any]]) -> np.ndarray:
    state = np.full(shape, MTBS_UNCOVERED_VALUE, dtype=np.uint8)
    rank = {"pass": 0, "review-needed": 1, "excluded": 2}
    for item in windows:
        if item.get("state") not in rank:
            raise CrossEventLabelTransferError("unsupported registration-window state")
        window = item.get("pixel_window") or {}
        row = int(window.get("row_offset", -1))
        column = int(window.get("column_offset", -1))
        height = int(window.get("height", 0))
        width = int(window.get("width", 0))
        if row < 0 or column < 0 or height <= 0 or width <= 0 or row + height > shape[0] or column + width > shape[1]:
            raise CrossEventLabelTransferError("registration window exceeds the proposal grid")
        view = state[row:row + height, column:column + width]
        value = rank[item["state"]]
        view[view == MTBS_UNCOVERED_VALUE] = value
        np.maximum(view, value, out=view)
    if np.any(state == MTBS_UNCOVERED_VALUE):
        raise CrossEventLabelTransferError("registration windows do not cover the proposal grid")
    return state


def _read_mtbs_on_sentinel_grid(
    package: Path,
    event_group_id: str,
    *,
    destination_shape: tuple[int, int],
    destination_transform: rasterio.Affine,
) -> tuple[np.ndarray, dict[str, Any]]:
    by_event = {item.event_group_id: item for item in MTBS_CONTRACTS}
    contract = by_event.get(event_group_id)
    if contract is None:
        raise CrossEventLabelTransferError("MTBS reference contract is missing")
    path = package / contract.filename
    output = np.full(destination_shape, MTBS_UNCOVERED_VALUE, dtype=np.uint8)
    provider_bytes = path.read_bytes()
    if len(provider_bytes) != contract.expected_size_bytes or sha256(provider_bytes).hexdigest() != contract.expected_sha256:
        raise CrossEventLabelTransferError("MTBS clip changed before transfer read")
    with MemoryFile(provider_bytes) as memory:
        with memory.open() as source:
            source_values = source.read(
                out=np.empty((1, source.height, source.width), dtype=np.uint8)
            )[0]
            reproject(
                source=source_values,
                destination=output,
                src_transform=source.transform,
                src_crs=source.crs,
                dst_transform=destination_transform,
                dst_crs="EPSG:32610",
                src_nodata=None,
                dst_nodata=MTBS_UNCOVERED_VALUE,
                resampling=Resampling.nearest,
                init_dest_nodata=True,
            )
            source_meta = {
                "filename": contract.filename,
                "sha256": contract.expected_sha256,
                "source_crs": source.crs.to_string(),
                "source_transform": [round(float(value), 9) for value in source.transform[:6]],
                "source_width": source.width,
                "source_height": source.height,
                "year_filter": contract.year,
                "read_contract": "one bounded byte read; SHA-256 and raster analysis use the same in-memory bytes",
            }
    observed = set(int(value) for value in np.unique(output))
    if not observed.issubset(set(MTBS_ALLOWED_VALUES) | {MTBS_UNCOVERED_VALUE}):
        raise CrossEventLabelTransferError("reprojected MTBS values exceed the documented domain")
    if MTBS_UNCOVERED_VALUE in observed:
        raise CrossEventLabelTransferError("registered MTBS clip does not cover the proposal grid")
    source_meta.update({
        "destination_crs": "EPSG:32610",
        "destination_transform": [round(float(value), 9) for value in destination_transform[:6]],
        "destination_width": destination_shape[1],
        "destination_height": destination_shape[0],
        "resampling": "nearest-neighbor categorical",
        "value_counts": {
            str(value): int((output == value).sum()) for value in sorted(observed)
        },
    })
    return output, source_meta


def classify_transfer_states(
    *,
    pair_quality: np.ndarray,
    registration_state: np.ndarray,
    reference_mask: np.ndarray,
    mtbs: np.ndarray,
    evidence: dict[str, np.ndarray],
    numeric_valid: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Apply the established spectral hypothesis with cross-event safeguards."""
    shape = pair_quality.shape
    arrays = (registration_state, reference_mask, mtbs, numeric_valid, *evidence.values())
    if any(item.shape != shape for item in arrays):
        raise CrossEventLabelTransferError("transfer inputs do not share one native grid")
    if set(int(value) for value in np.unique(pair_quality)) - {0, 1, 2}:
        raise CrossEventLabelTransferError("pair quality contains an unknown state")
    if set(int(value) for value in np.unique(registration_state)) - {0, 1, 2}:
        raise CrossEventLabelTransferError("registration evidence contains an unknown state")

    dnbr = evidence["dnbr"]
    ndvi_loss = evidence["ndvi_loss"]
    swir_gain = evidence["swir_gain"]
    nir_loss = evidence["nir_loss"]
    usable = (pair_quality == 0) & (registration_state == 0) & numeric_valid
    excluded = (
        (pair_quality == 2)
        | (registration_state == 2)
        | ~numeric_valid
        | (mtbs == MTBS_NONPROCESSING_VALUE)
        | (mtbs == MTBS_UNCOVERED_VALUE)
    )
    quality_review = ((pair_quality == 1) | (registration_state == 1)) & ~excluded

    support_count = (
        (ndvi_loss >= BURN_NDVI_LOSS_MIN).astype(np.uint8)
        + (swir_gain >= BURN_SWIR_GAIN_MIN).astype(np.uint8)
        + (nir_loss >= BURN_NIR_LOSS_MIN).astype(np.uint8)
    )
    burn_evidence = (dnbr >= BURN_DNBR_MIN) & (support_count >= BURN_SUPPORTING_SIGNALS_MIN)
    stable_primary = (
        (np.abs(dnbr) <= STABLE_ABS_DNBR_MAX)
        & (np.abs(ndvi_loss) <= STABLE_ABS_NDVI_CHANGE_MAX)
        & (np.abs(swir_gain) <= STABLE_ABS_SWIR_CHANGE_MAX)
        & (np.abs(nir_loss) <= STABLE_ABS_NIR_CHANGE_MAX)
    )
    burn_coherent = burn_evidence & (neighbor_support(burn_evidence) >= BURN_NEIGHBOR_SUPPORT_MIN)

    reference_core = erode_mask(reference_mask, BOUNDARY_REVIEW_PX)
    reference_outer = dilate_mask(reference_mask, BOUNDARY_REVIEW_PX)
    reference_boundary = reference_outer & ~reference_core
    mtbs_support = np.isin(mtbs, tuple(MTBS_SUPPORT_VALUES))
    mtbs_ambiguous = np.isin(mtbs, tuple(MTBS_AMBIGUOUS_VALUES))
    stability_score = np.sqrt(
        (np.abs(dnbr) / STABLE_ABS_DNBR_MAX) ** 2
        + (np.abs(ndvi_loss) / STABLE_ABS_NDVI_CHANGE_MAX) ** 2
        + (np.abs(swir_gain) / STABLE_ABS_SWIR_CHANGE_MAX) ** 2
        + (np.abs(nir_loss) / STABLE_ABS_NIR_CHANGE_MAX) ** 2
    )
    fallback_pool = (
        usable
        & ~reference_outer
        & (mtbs == MTBS_BACKGROUND_VALUE)
        & ~burn_evidence
        & np.isfinite(stability_score)
    )
    fallback_threshold: float | None = None
    stable_fallback = np.zeros(shape, dtype=bool)
    if np.any(fallback_pool):
        fallback_threshold = min(
            float(np.quantile(stability_score[fallback_pool], STABILITY_FALLBACK_QUANTILE, method="lower")),
            STABILITY_FALLBACK_MAX_NORMALIZED_SCORE,
        )
        stable_fallback = fallback_pool & (stability_score <= fallback_threshold)
    stable_primary_coherent = stable_primary & (neighbor_support(stable_primary) >= STABLE_NEIGHBOR_SUPPORT_MIN)
    stable_fallback_coherent = stable_fallback & (neighbor_support(stable_fallback) >= STABLE_NEIGHBOR_SUPPORT_MIN)
    stable_evidence = stable_primary | stable_fallback
    stable_coherent = stable_primary_coherent | stable_fallback_coherent
    burned_raw = usable & reference_core & mtbs_support & burn_coherent
    background_raw = usable & ~reference_outer & (mtbs == MTBS_BACKGROUND_VALUE) & stable_coherent
    source_conflict = usable & (
        (~reference_mask & burn_coherent)
        | (reference_mask & stable_coherent)
        | (reference_mask & (mtbs == MTBS_BACKGROUND_VALUE))
        | (~reference_mask & mtbs_support)
        | (mtbs_support & stable_coherent)
    )
    mtbs_ambiguity_review = usable & reference_mask & mtbs_ambiguous
    burned_boundary = usable & boundary_band(burned_raw)
    review = quality_review | reference_boundary | source_conflict | mtbs_ambiguity_review | burned_boundary

    states = np.full(shape, STATE_CODES["unknown"], dtype=np.uint8)
    states[excluded] = STATE_CODES["excluded"]
    states[review & ~excluded] = STATE_CODES["review-needed"]
    states[burned_raw & ~review & ~excluded] = STATE_CODES["burned"]
    states[background_raw & ~review & ~excluded] = STATE_CODES["background-candidate"]
    target = np.full(shape, IGNORE_VALUE, dtype=np.uint8)
    target[states == STATE_CODES["background-candidate"]] = 0
    target[states == STATE_CODES["burned"]] = 1
    if np.any((target != IGNORE_VALUE) & ~np.isin(states, [0, 1])):
        raise CrossEventLabelTransferError("ignored state entered the candidate target")
    return states, target, {
        "usable": usable,
        "excluded": excluded,
        "quality_review": quality_review,
        "burn_evidence": burn_evidence,
        "burn_coherent": burn_coherent,
        "stable_evidence": stable_evidence,
        "stable_coherent": stable_coherent,
        "stable_primary": stable_primary,
        "stable_primary_coherent": stable_primary_coherent,
        "stability_fallback_pool": fallback_pool,
        "stable_fallback": stable_fallback,
        "stable_fallback_coherent": stable_fallback_coherent,
        "stability_fallback_threshold_normalized": (
            None if fallback_threshold is None else round(fallback_threshold, 6)
        ),
        "reference_core": reference_core,
        "reference_boundary": reference_boundary,
        "mtbs_support": mtbs_support,
        "mtbs_ambiguous": mtbs_ambiguous,
        "source_conflict": source_conflict,
        "mtbs_ambiguity_review": mtbs_ambiguity_review,
        "burned_raw": burned_raw,
        "background_raw": background_raw,
        "burned_boundary": burned_boundary,
        "review": review,
    }


def summarize_states(states: np.ndarray) -> dict[str, Any]:
    counts = Counter(int(value) for value in states.reshape(-1))
    if set(counts) - set(STATE_NAMES):
        raise CrossEventLabelTransferError("state raster contains an unknown code")
    total = int(states.size)
    rows = [
        {
            "state": STATE_NAMES[code],
            "code": code,
            "pixels": counts.get(code, 0),
            "percent": round(100 * counts.get(code, 0) / total, 4),
            "target_value": code if code in {0, 1} else None,
        }
        for code in sorted(STATE_NAMES)
    ]
    candidate = counts.get(0, 0) + counts.get(1, 0)
    return {
        "pixel_count": total,
        "states": rows,
        "candidate_target_pixels": candidate,
        "candidate_target_percent": round(100 * candidate / total, 4),
        "ignored_pixels": total - candidate,
        "ignored_percent": round(100 * (total - candidate) / total, 4),
    }


def _threshold_contract() -> dict[str, float | int | str]:
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
        "stability_fallback_quantile": STABILITY_FALLBACK_QUANTILE,
        "stability_fallback_max_normalized_score": STABILITY_FALLBACK_MAX_NORMALIZED_SCORE,
        "boundary_review_px": BOUNDARY_REVIEW_PX,
        "threshold_scope": "transfer hypothesis inherited from the exact Darlene 3 proposal; not universal calibration",
    }


def _write_raster(
    path: Path,
    values: np.ndarray,
    transform: rasterio.Affine,
    *,
    event_group_id: str,
    kind: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=values.shape[1],
        height=values.shape[0],
        count=1,
        dtype="uint8",
        crs="EPSG:32610",
        transform=transform,
        nodata=IGNORE_VALUE if kind == "candidate-binary-target" else None,
        compress="deflate",
        predictor=2,
    ) as destination:
        destination.write(values, 1)
        destination.update_tags(
            repository="drwbkr1/burnlens-deschutes",
            task_issue=str(TASK_ISSUE),
            event_group_id=event_group_id,
            run_id=run_id,
            git_source_commit=git_source_commit,
            software_version=SOFTWARE_VERSION,
            label_protocol_version=LABEL_PROTOCOL_VERSION,
            label_schema_version=LABEL_SCHEMA_VERSION,
            label_proposal_version=LABEL_PROPOSAL_VERSION,
            raster_kind=kind,
            dataset_version="none",
            model_version="none",
        )
    return {
        "filename": path.name,
        "kind": kind,
        "size_bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
        "crs": "EPSG:32610",
        "transform": [round(float(value), 9) for value in transform[:6]],
        "width": values.shape[1],
        "height": values.shape[0],
        "dtype": "uint8",
        "nodata": IGNORE_VALUE if kind == "candidate-binary-target" else None,
    }


def _mask_counts(masks: dict[str, Any]) -> dict[str, int]:
    return {
        name: int(values.sum())
        for name, values in sorted(masks.items())
        if isinstance(values, np.ndarray) and values.dtype == bool
    }


def _method_diagnostics(masks: dict[str, Any]) -> dict[str, Any]:
    return {name: value for name, value in sorted(masks.items()) if not isinstance(value, np.ndarray)}


def build_report(
    *,
    optical_package: Path,
    mtbs_package: Path,
    feasibility_report_path: Path,
    source_fitness_report_path: Path,
    output_directory: Path,
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
        raise CrossEventLabelTransferError("registered optical package failed verification")
    mtbs_verification = verify_mtbs_package(mtbs_package)
    source_fitness = _load_source_fitness(source_fitness_report_path)
    feasibility, candidates = _load_feasibility(feasibility_report_path)
    contracts = {item.role: item for item in CROSS_EVENT_CONTRACTS}
    fitness_by_event = {item["event_group_id"]: item for item in source_fitness["events"]}

    events: list[dict[str, Any]] = []
    visuals: list[dict[str, Any]] = []
    for candidate in candidates:
        event_id = candidate["event_group_id"]
        fitness = fitness_by_event[event_id]
        pre_role, post_role = ROLE_PAIRS[event_id]
        pre_scene, pre = _read_product(optical_package, contracts[pre_role], candidate["source_geometry"])
        post_scene, post = _read_product(optical_package, contracts[post_role], candidate["source_geometry"])
        if pre["B04"].shape != post["B04"].shape or not np.array_equal(pre["MASK20"], post["MASK20"]):
            raise CrossEventLabelTransferError("pre/post proposal grids are not aligned")
        shape = pre["B04"].shape
        destination_transform = rasterio.Affine(*pre_scene["rasters"]["B04"]["crop_transform"])
        pair_quality, pair_quality_summary = classify_pair_quality(pre["SCL"], post["SCL"])
        registration_state = _registration_state(shape, fitness["registration"]["windows"])
        mtbs, mtbs_meta = _read_mtbs_on_sentinel_grid(
            mtbs_package,
            event_id,
            destination_shape=shape,
            destination_transform=destination_transform,
        )
        evidence, numeric_valid = spectral_evidence(pre_scene, pre, post_scene, post)
        states, target, masks = classify_transfer_states(
            pair_quality=pair_quality,
            registration_state=registration_state,
            reference_mask=pre["MASK20"],
            mtbs=mtbs,
            evidence=evidence,
            numeric_valid=numeric_valid,
        )
        summary = summarize_states(states)
        prefix = event_id.removeprefix("event-")
        state_output = _write_raster(
            output_directory / f"CROSS-EVENT-LABEL-TRANSFER-2026-001-{prefix}-state.tif",
            states,
            destination_transform,
            event_group_id=event_id,
            kind="five-state-companion-proposal",
            run_id=run_id,
            git_source_commit=git_source_commit,
        )
        target_output = _write_raster(
            output_directory / f"CROSS-EVENT-LABEL-TRANSFER-2026-001-{prefix}-target.tif",
            target,
            destination_transform,
            event_group_id=event_id,
            kind="candidate-binary-target",
            run_id=run_id,
            git_source_commit=git_source_commit,
        )
        mtbs_counts = Counter(int(value) for value in mtbs.reshape(-1))
        state_counts = {item["state"]: item["pixels"] for item in summary["states"]}
        if state_counts["burned"] == 0 or state_counts["background-candidate"] == 0:
            raise CrossEventLabelTransferError(f"{event_id} did not transfer both candidate target classes")
        events.append({
            "event_group_id": event_id,
            "fire_id": candidate["fire_id"],
            "fire_name": candidate["fire_name"],
            "ignition_date": candidate["ignition_date"],
            "geography_group_id": candidate["geography_group_id"],
            "scene_group_id": candidate["scene_pair"]["scene_group_id"],
            "time_group_id": candidate["time_group_id"],
            "source_geometry_sha256": fitness["source_geometry_sha256"],
            "grid": {
                "crs": "EPSG:32610",
                "transform": [round(float(value), 9) for value in destination_transform[:6]],
                "width": shape[1],
                "height": shape[0],
                "pixel_size_m": 20,
            },
            "inputs": {
                "pre": {"role": pre_scene["role"], "provider_id": pre_scene["provider_id"], "filename": pre_scene["filename"]},
                "post": {"role": post_scene["role"], "provider_id": post_scene["provider_id"], "filename": post_scene["filename"]},
                "mtbs": mtbs_meta,
            },
            "source_fitness_binding": {
                "registration_windows": [
                    {"window_id": item["window_id"], "state": item["state"], "reason_code": item["reason_code"], "pixel_window": item["pixel_window"]}
                    for item in fitness["registration"]["windows"]
                ],
                "pair_quality_summary": pair_quality_summary,
                "pair_quality_state_counts": {
                    "eligible-comparison": int((pair_quality == 0).sum()),
                    "review-needed": int((pair_quality == 1).sum()),
                    "excluded": int((pair_quality == 2).sum()),
                },
                "registration_state_counts": {
                    "pass": int((registration_state == 0).sum()),
                    "review-needed": int((registration_state == 1).sum()),
                    "excluded": int((registration_state == 2).sum()),
                },
            },
            "mtbs_destination_value_counts": {str(value): mtbs_counts[value] for value in sorted(mtbs_counts)},
            "method_mask_counts": _mask_counts(masks),
            "method_diagnostics": _method_diagnostics(masks),
            "summary": summary,
            "outputs": {"state": state_output, "target": target_output},
        })
        visuals.append({
            "event_group_id": event_id,
            "fire_name": candidate["fire_name"],
            "pre_tci": pre["TCI"],
            "post_tci": post["TCI"],
            "states": states,
            "target": target,
            "mtbs": mtbs,
        })

    aggregate_counts = Counter()
    for event in events:
        aggregate_counts.update({item["state"]: item["pixels"] for item in event["summary"]["states"]})
    if set(name for name, count in aggregate_counts.items() if count) != set(STATE_CODES):
        raise CrossEventLabelTransferError("aggregate transfer does not represent all five states")
    optical_registration = optical_verification.get("registration") or {}
    mtbs_registration = mtbs_verification.get("registration") or {}
    report = {
        "report_id": REPORT_ID,
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
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
            "feasibility_report_sha256": _sha256_file(feasibility_report_path),
            "source_fitness_report_sha256": SOURCE_FITNESS_SHA256,
            "optical_registration_manifest_sha256": optical_verification["registration_manifest_sha256"],
            "mtbs_registration_manifest_sha256": mtbs_verification["registration_manifest_sha256"],
        },
        "source_lineage": {
            "optical": {
                "package_id": OPTICAL_PACKAGE_ID,
                "contract_version": OPTICAL_CONTRACT_VERSION,
                "terms_review_id": OPTICAL_TERMS_REVIEW_ID,
                "acquisition_run_id": optical_registration.get("run_id"),
                "assets": optical_registration.get("assets"),
            },
            "mtbs": {
                "package_id": MTBS_PACKAGE_ID,
                "contract_version": MTBS_CONTRACT_VERSION,
                "source_record_id": MTBS_SOURCE_RECORD_ID,
                "terms_review_id": MTBS_TERMS_REVIEW_ID,
                "acquisition_run_id": mtbs_registration.get("run_id"),
                "source": mtbs_registration.get("source"),
                "registered_assets": mtbs_registration.get("assets"),
                "verified_current_assets": mtbs_verification["assets"],
                "registration_manifest_link_count": mtbs_verification["registration_manifest_link_count"],
            },
            "feasibility_source_snapshot_sha256": feasibility["input_hashes"]["source_snapshot_sha256"],
            "predecessor_run_id": source_fitness["run_id"],
            "predecessor_git_source_commit": source_fitness["git_source_commit"],
        },
        "method": {
            "thresholds": _threshold_contract(),
            "spectral": "Native 20 m B04/B8A/B12 changes reuse the established Darlene 3 proposal-screen hypothesis.",
            "quality": "Sentinel SCL and source-fitness registration states constrain eligibility; they never identify burn truth.",
            "mtbs": "Nearest-neighbor annual thematic severity supports classes 2-4, reserves classes 1/5 for review, excludes class 6, and never creates a burned candidate without coherent spectral evidence inside the frozen boundary.",
            "background": "Background candidates require affirmative stability outside the expanded event boundary and MTBS class 0. The fixed Darlene near-zero rule remains primary; the authorized binary-mask fallback admits only the lowest 15% normalized non-burn change tail, capped at score 6.0 and requiring 7-of-9 support. Boundary absence alone is insufficient.",
            "uncertainty": "Cross-source conflict, ambiguous MTBS evidence, boundary transition, quality review, and burned transitions stay review-needed; unsupported usable pixels stay unknown.",
        },
        "events": events,
        "aggregate": {
            "event_count": len(events),
            "state_counts": {name: aggregate_counts[name] for name in STATE_CODES},
            "all_five_states_represented": all(aggregate_counts[name] > 0 for name in STATE_CODES),
            "candidate_target_pixels": aggregate_counts["background-candidate"] + aggregate_counts["burned"],
            "ignored_pixels": sum(aggregate_counts[name] for name in ("unknown", "excluded", "review-needed")),
        },
        "decision": "PROPOSAL_READY_FOR_SEPARATE_QA",
        "decision_detail": "Both frozen events contain burned and background candidate pixels while preserving aggregate five-state uncertainty and all Tepee source-fitness exclusions. Separate software QA and rendered review remain required before proposal-level acceptance.",
        "claims": {
            "proven": [
                "The established five-state proposal hypothesis can be executed on both exact source-fit event pairs.",
                "Every candidate and ignored pixel is traceable to exact Sentinel, MTBS, boundary, quality, registration, protocol, schema, version, commit, and run evidence.",
            ],
            "not_proven": [
                "The proposal is accepted ground truth, field validated, universally calibrated, independently human labeled, or suitable for operational decisions.",
                "A dataset, split, baseline, trained model, accuracy result, deployed application, official status, or endorsement exists.",
            ],
        },
        "attribution": (
            "Contains modified Copernicus Sentinel-2 data (2017-2018), accessed through CDSE. "
            "MTBS reference: Monitoring Trends in Burn Severity Program, USGS and USDA Forest Service. No endorsement implied."
        ),
        "source_precedence": "Official emergency and incident sources govern public-safety decisions. Exact registered source bytes govern this bounded experiment; MTBS remains analyst-interpreted reference evidence.",
        "warning": WARNING,
    }
    return report, visuals


def _state_image(states: np.ndarray) -> Image.Image:
    rgb = np.zeros((*states.shape, 3), dtype=np.uint8)
    for code, color in STATE_COLORS.items():
        rgb[states == code] = color
    return Image.fromarray(rgb, mode="RGB")


def _target_image(target: np.ndarray) -> Image.Image:
    rgb = np.full((*target.shape, 3), (105, 108, 105), dtype=np.uint8)
    rgb[target == 0] = (0, 107, 100)
    rgb[target == 1] = (240, 90, 40)
    return Image.fromarray(rgb, mode="RGB")


def _mtbs_image(values: np.ndarray) -> Image.Image:
    colors = {
        0: (235, 232, 221),
        1: (222, 214, 151),
        2: (244, 183, 88),
        3: (224, 112, 52),
        4: (151, 48, 31),
        5: (85, 155, 89),
        6: (70, 70, 70),
    }
    rgb = np.zeros((*values.shape, 3), dtype=np.uint8)
    for code, color in colors.items():
        rgb[values == code] = color
    return Image.fromarray(rgb, mode="RGB")


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
    draw.rectangle((box[0], box[1], box[2], box[1] + 54), fill="#132a26")
    draw.text((box[0] + 12, box[1] + 7), title, fill="white", font=_font(15))
    draw.text((box[0] + 12, box[1] + 30), subtitle, fill="#b9d8cf", font=_font(11))


def render_png(report: dict[str, Any], visuals: list[dict[str, Any]], path: Path) -> None:
    canvas = Image.new("RGB", (1800, 1680), "#f4f0e8")
    draw = ImageDraw.Draw(canvas)
    ink, muted, teal, orange = "#15211d", "#5d6b64", "#006b64", "#f05a28"
    draw.rectangle((0, 0, 1800, 175), fill="#132a26")
    draw.text((58, 29), "BURNLENS / PHASE TWO / OBJECTIVE FOUR", fill="#b9d8cf", font=_font(20))
    draw.text((58, 68), "CROSS-EVENT FIVE-STATE TRANSFER", fill="white", font=_font(36))
    draw.text((58, 123), "Two exact Sentinel pairs + exact MTBS annual references / proposal evidence only", fill="#b9d8cf", font=_font(17))
    draw.text((1430, 45), "STATUS", fill="#b9d8cf", font=_font(15))
    draw.text((1430, 76), "SEPARATE QA", fill="#ffd166", font=_font(24))
    draw.text((1430, 116), "dataset / model: none", fill="white", font=_font(14))

    event_by_id = {item["event_group_id"]: item for item in report["events"]}
    for event_index, visual in enumerate(visuals):
        event = event_by_id[visual["event_group_id"]]
        top = 215 + event_index * 410
        draw.text((45, top - 27), f"{event['fire_name']}  /  {event['event_group_id']}", fill=teal, font=_font(18))
        boxes = [(45 + index * 342, top, 363 + index * 342, top + 245) for index in range(5)]
        _panel(canvas, draw, Image.fromarray(np.moveaxis(visual["pre_tci"], 0, 2), mode="RGB"), boxes[0], "PRE", "Sentinel-2 true color")
        _panel(canvas, draw, Image.fromarray(np.moveaxis(visual["post_tci"], 0, 2), mode="RGB"), boxes[1], "POST", "Sentinel-2 true color")
        _panel(canvas, draw, _mtbs_image(visual["mtbs"]), boxes[2], "MTBS REFERENCE", "0-6 thematic / nearest", nearest=True)
        _panel(canvas, draw, _state_image(visual["states"]), boxes[3], "COMPANION STATE", "five-state proposal", nearest=True)
        _panel(canvas, draw, _target_image(visual["target"]), boxes[4], "CANDIDATE TARGET", "0 / 1 / gray ignore", nearest=True)
        state_items = event["summary"]["states"]
        left = 45
        for item in state_items:
            color = "#%02x%02x%02x" % STATE_COLORS[item["code"]]
            draw.rounded_rectangle((left, top + 270, left + 320, top + 352), radius=12, fill="#fffdf8", outline="#d4cec1", width=2)
            draw.rectangle((left, top + 270, left + 10, top + 352), fill=color)
            draw.text((left + 24, top + 283), f"{item['percent']:.2f}%", fill=color, font=_font(20))
            draw.text((left + 24, top + 316), f"{item['state']} / {item['pixels']:,}", fill=ink, font=_font(12))
            left += 342
        draw.text(
            (45, top + 365),
            f"candidate {event['summary']['candidate_target_pixels']:,} / ignored {event['summary']['ignored_pixels']:,} / grid {event['grid']['width']} x {event['grid']['height']} @ 20 m / fallback threshold {event['method_diagnostics']['stability_fallback_threshold_normalized']:.6f} / coherent {event['method_mask_counts']['stable_fallback_coherent']:,}",
            fill=muted,
            font=_font(13),
        )

    box_top = 1055
    draw.rounded_rectangle((45, box_top, 1755, 1405), radius=18, fill="#e5efeb", outline="#aac8bf", width=2)
    draw.text((72, box_top + 25), "TRANSFER CONTRACT / WHAT THE EVIDENCE MEANS", fill=teal, font=_font(21))
    rules = [
        "Burned requires coherent multi-signal change inside the eroded event boundary and MTBS support class 2-4.",
        "Background uses fixed near-zero stability or capped lowest-15% fallback, outside expanded boundary + MTBS 0, with 7-of-9 support.",
        "MTBS class 1 or 5, cross-source conflict, SCL review, registration review, and transitions require review.",
        "SCL exclusion, Tepee W-01, invalid numeric evidence, MTBS class 6, or uncovered source evidence excludes.",
        "MTBS and Sentinel products are remotely sensed evidence, not comprehensive field validation or operational truth.",
        "A separate implementation must reopen exact sources and reproduce every state and target pixel before acceptance.",
    ]
    for index, rule in enumerate(rules):
        draw.text((88, box_top + 75 + index * 43), f"{index + 1}. {rule}", fill=ink, font=_font(14))
    aggregate = report["aggregate"]
    draw.text((72, box_top + 315), f"Aggregate candidate target: {aggregate['candidate_target_pixels']:,} / ignored: {aggregate['ignored_pixels']:,} / all five states: yes", fill=orange, font=_font(16))

    draw.text((45, 1445), report["attribution"], fill=muted, font=_font(13))
    trace = (
        f"run {report['run_id']} / source {report['git_source_commit'][:12]} / software {report['software_version']} / "
        f"protocol {report['label_protocol_version']} / schema {report['label_schema_version']} / proposal {report['label_proposal_version']}"
    )
    draw.text((45, 1482), trace, fill=muted, font=_font(12))
    draw.text((45, 1518), "app none / dataset none / split none / baseline none / model none / field validation none", fill=orange, font=_font(14))
    draw.text((45, 1555), report["warning"], fill="#33443e", font=_font(11))
    draw.text((45, 1605), "PRIMARY OUTPUT: PROPOSAL_READY_FOR_SEPARATE_QA", fill=teal, font=_font(18))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], png_name: str, path: Path) -> None:
    event_sections = []
    for event in report["events"]:
        state_rows = "".join(
            f"<tr><td>{escape(item['state'])}</td><td>{item['code']}</td><td>{'ignore' if item['target_value'] is None else item['target_value']}</td><td>{item['pixels']:,}</td><td>{item['percent']:.4f}%</td></tr>"
            for item in event["summary"]["states"]
        )
        mtbs_rows = "".join(
            f"<tr><td>{code}</td><td>{count:,}</td></tr>" for code, count in event["mtbs_destination_value_counts"].items()
        )
        windows = "".join(
            f"<li><code>{escape(item['window_id'])}</code>: {escape(item['state'])} / {escape(item['reason_code'])}</li>"
            for item in event["source_fitness_binding"]["registration_windows"]
        )
        event_sections.append(f"""
<section class="card"><h2>{escape(event['fire_name'])}</h2><p><code>{escape(event['event_group_id'])}</code><br>
Fire / geography / scene / time: <code>{escape(event['fire_id'])}</code> / <code>{escape(event['geography_group_id'])}</code> / <code>{escape(event['scene_group_id'])}</code> / <code>{escape(event['time_group_id'])}</code></p>
<div class="metrics"><div><strong>{event['summary']['candidate_target_pixels']:,}</strong><span>candidate pixels</span></div><div><strong>{event['summary']['ignored_pixels']:,}</strong><span>ignored pixels</span></div><div><strong>{event['grid']['width']} × {event['grid']['height']}</strong><span>native 20 m grid</span></div></div>
<div class="table-wrap"><table><thead><tr><th>State</th><th>Code</th><th>Target</th><th>Pixels</th><th>Share</th></tr></thead><tbody>{state_rows}</tbody></table></div>
<p>Authorized stability fallback: normalized threshold <code>{event['method_diagnostics']['stability_fallback_threshold_normalized']:.6f}</code>; {event['method_mask_counts']['stable_fallback_coherent']:,} coherent fallback pixels. This is an event-relative proposal screen, not universal calibration.</p>
<details><summary>MTBS values and registration bindings</summary><div class="columns"><table><thead><tr><th>MTBS code</th><th>Pixels</th></tr></thead><tbody>{mtbs_rows}</tbody></table><ul>{windows}</ul></div></details>
<p>Outputs: <a href="{escape(event['outputs']['state']['filename'])}">{escape(event['outputs']['state']['filename'])}</a> / <a href="{escape(event['outputs']['target']['filename'])}">{escape(event['outputs']['target']['filename'])}</a></p></section>""")
    thresholds = report["method"]["thresholds"]
    document = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens cross-event five-state transfer</title><style>
:root {{ --ink:#15211d; --muted:#5d6b64; --paper:#f4f0e8; --panel:#fffdf8; --teal:#006b64; --orange:#f05a28; }} * {{ box-sizing:border-box; }} body {{ margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif; }}
header {{ background:#132a26;color:white;padding:3rem max(5vw,2rem); }} header p {{ color:#b9d8cf; }} main {{ max-width:1300px;margin:auto;padding:2.5rem 1.5rem 5rem; }} .hero {{ width:100%;height:auto;border:1px solid #c8c0b2; }}
.warning {{ background:#fff1ca;border-left:6px solid #d87618;padding:1rem 1.2rem;font-weight:650; }} .card {{ background:var(--panel);border:1px solid #d9d1c4;border-radius:12px;padding:1.2rem;margin:1.2rem 0; }} .decision {{ border:2px solid var(--orange); }}
.metrics {{ display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:.8rem;margin:1rem 0; }} .metrics div {{ background:#e5efeb;padding:1rem;border-radius:10px; }} .metrics strong {{ display:block;color:var(--teal);font-size:1.6rem; }} .metrics span {{ color:var(--muted); }}
.table-wrap {{ overflow-x:auto; }} table {{ width:100%;border-collapse:collapse;background:var(--panel); }} th,td {{ padding:.65rem;border-bottom:1px solid #ddd5c9;text-align:left; }} code {{ overflow-wrap:anywhere; }} .columns {{ display:grid;grid-template-columns:minmax(220px,.45fr) 1fr;gap:1rem; }}
@media(max-width:700px) {{ .columns {{ grid-template-columns:1fr; }} }}
</style></head><body><header><p>BurnLens / Phase Two / Objective Four</p><h1>Cross-event five-state proposal transfer</h1><p>Two exact Sentinel pairs, two exact MTBS references, and explicit uncertainty. Proposal evidence only.</p></header><main>
<p class="warning">{escape(report['warning'])}</p><img class="hero" src="{escape(png_name)}" alt="Two event rows compare pre and post Sentinel imagery, MTBS reference, five-state companion proposal, and binary candidate target">
<section class="card decision"><h2>Decision</h2><p><strong>{escape(report['decision'])}</strong></p><p>{escape(report['decision_detail'])}</p><p>Aggregate: {report['aggregate']['candidate_target_pixels']:,} candidate target pixels and {report['aggregate']['ignored_pixels']:,} ignored pixels. All five states are represented. A separately invoked QA report is still required.</p></section>
{''.join(event_sections)}
<section class="card"><h2>Frozen transfer method</h2><p>{escape(report['method']['spectral'])}</p><ul><li>{escape(report['method']['quality'])}</li><li>{escape(report['method']['mtbs'])}</li><li>{escape(report['method']['background'])}</li><li>{escape(report['method']['uncertainty'])}</li></ul><p>Threshold scope: {escape(str(thresholds['threshold_scope']))}</p></section>
<section class="card"><h2>Traceability</h2><p><strong>Run:</strong> <code>{escape(report['run_id'])}</code><br><strong>Git source:</strong> <code>{escape(report['git_source_commit'])}</code><br><strong>Software / report:</strong> <code>{escape(report['software_version'])}</code> / <code>{escape(report['report_version'])}</code><br><strong>Label protocol / schema / proposal / transfer:</strong> <code>{escape(report['label_protocol_version'])}</code> / <code>{escape(report['label_schema_version'])}</code> / <code>{escape(report['label_proposal_version'])}</code> / <code>{escape(report['transfer_protocol_version'])}</code><br><strong>Application / dataset / baseline / model:</strong> none / none / none / none</p></section>
<section class="card"><h2>Boundaries and precedence</h2><p>{escape(report['source_precedence'])}</p><ul>{''.join(f'<li><strong>Not proven:</strong> {escape(item)}</li>' for item in report['claims']['not_proven'])}</ul><p>{escape(report['attribution'])}</p></section>
</main></body></html>"""
    _write_utf8_lf(path, document)


def write_report(
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
