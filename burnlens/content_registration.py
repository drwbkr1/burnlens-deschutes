"""Measure and render pair-local Sentinel-2 content registration evidence.

This module measures translation residuals on independent per-scene spectral
gradient signals. It does not resample source imagery, create label pixels, or
turn registration windows into burn/background evidence.
"""

from __future__ import annotations

from hashlib import sha256
from html import escape
import json
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from PIL import Image, ImageDraw

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
    SELECTED_BANDS,
    TARGET_VERSION,
    WARNING,
    OpticalPairEvidenceError,
    _font,
    _local_name,
    _read_scene,
    _reflectance,
    _sha256_lf_text,
    _write_utf8_lf,
    classify_pair_quality,
)
from .paired_intake import verify_registered_package


SOFTWARE_VERSION = "0.8.0"
REPORT_ID = "CONTENT-REGISTRATION-2026-001"
REPORT_SCHEMA_VERSION = "0.1.0"
REPORT_VERSION = "content-registration-evidence-v0.1.0"
REGISTRATION_PROTOCOL_VERSION = "local-content-registration-v0.1.0"
OPTICAL_REPORT_ID = "OPTICAL-PAIR-2026-001"
WINDOW_SIZE_PX = 150
PIXEL_SIZE_M = 20
UPSAMPLE_FACTOR = 100
MIN_USABLE_FRACTION = 0.90
MIN_CONFIDENT_BANDS = 2
MIN_PEAK_RATIO = 2.0
MAX_BAND_DEVIATION_PX = 0.15
MAX_RESIDUAL_PX = 0.50
PRIMARY_SOURCES = (
    {
        "title": "Efficient subpixel image registration algorithms",
        "publisher": "Optica Publishing Group",
        "doi": "10.1364/OL.33.000156",
        "url": "https://doi.org/10.1364/OL.33.000156",
        "use": "Localized upsampled-DFT cross-correlation method basis.",
    },
    {
        "title": "Sentinel-2 Products Specification",
        "publisher": "Copernicus Sentinel Online",
        "url": "https://sentiwiki.copernicus.eu/web/s2-products",
        "use": "Product-level geometric context; not pair-local proof.",
    },
    {
        "title": "Sentinel-2 MSI L2A Data Quality Report, January 2026",
        "publisher": "Copernicus Sentinel Online",
        "url": (
            "https://sentiwiki.copernicus.eu/__attachments/1692737/"
            "OMPC.CS.DQR.002.12-2025-Sentinel-2-MSI-L2A-DQR-January2026.pdf"
        ),
        "use": "Current Collection-1 and PB05.10 geometric-quality context; not pair-local proof.",
    },
)


class ContentRegistrationError(OpticalPairEvidenceError):
    """A deterministic, secret-free registration evidence failure."""


def _upsampled_dft(
    data: np.ndarray,
    region_size: tuple[int, int],
    upsample_factor: int,
    axis_offsets: tuple[float, float],
) -> np.ndarray:
    """Evaluate a small upsampled DFT region using matrix multiplication."""

    if data.ndim != 2 or len(region_size) != 2 or len(axis_offsets) != 2:
        raise ContentRegistrationError("upsampled DFT requires two-dimensional inputs")
    if upsample_factor < 1 or any(size < 1 for size in region_size):
        raise ContentRegistrationError("invalid upsampled DFT dimensions")
    output = data
    axes = list(zip(data.shape, region_size, axis_offsets))
    for source_size, requested_size, offset in axes[::-1]:
        kernel = (
            (np.arange(requested_size, dtype=np.float64)[:, None] - offset)
            * np.fft.fftfreq(source_size, d=float(upsample_factor))
        )
        output = np.tensordot(
            np.exp(-2j * np.pi * kernel),
            output,
            axes=(1, -1),
        )
    return output


def _coarse_peak_ratio(correlation: np.ndarray, peak: tuple[int, int]) -> float:
    magnitude = np.abs(correlation)
    rows, columns = np.indices(magnitude.shape)
    row_distance = np.minimum(
        np.abs(rows - peak[0]), magnitude.shape[0] - np.abs(rows - peak[0])
    )
    column_distance = np.minimum(
        np.abs(columns - peak[1]), magnitude.shape[1] - np.abs(columns - peak[1])
    )
    outside = (row_distance > 2) | (column_distance > 2)
    second = float(np.max(magnitude[outside])) if np.any(outside) else 0.0
    first = float(magnitude[peak])
    if second <= np.finfo(np.float64).eps:
        return first / np.finfo(np.float64).eps if first > 0 else 0.0
    return first / second


def estimate_subpixel_shift(
    reference: np.ndarray,
    moving: np.ndarray,
    *,
    upsample_factor: int = UPSAMPLE_FACTOR,
) -> dict[str, float]:
    """Estimate the row/column shift to apply to ``moving`` to match ``reference``.

    Inputs must already be comparable scalar signals. A separable Hann taper
    limits edge discontinuities; phase-only correlation limits gain effects;
    and a localized upsampled DFT refines the integer peak.
    """

    if reference.ndim != 2 or reference.shape != moving.shape:
        raise ContentRegistrationError("registration signals must be aligned 2D arrays")
    if min(reference.shape) < 32:
        raise ContentRegistrationError("registration signals are too small")
    if upsample_factor < 1:
        raise ContentRegistrationError("upsample factor must be positive")
    if not np.all(np.isfinite(reference)) or not np.all(np.isfinite(moving)):
        raise ContentRegistrationError("registration signals must be finite")

    taper = np.outer(np.hanning(reference.shape[0]), np.hanning(reference.shape[1]))
    reference_signal = (reference.astype(np.float64) - float(np.mean(reference))) * taper
    moving_signal = (moving.astype(np.float64) - float(np.mean(moving))) * taper
    reference_energy = float(np.linalg.norm(reference_signal))
    moving_energy = float(np.linalg.norm(moving_signal))
    if min(reference_energy, moving_energy) <= 1e-9:
        raise ContentRegistrationError("registration signal has insufficient texture")

    reference_frequency = np.fft.fftn(reference_signal)
    moving_frequency = np.fft.fftn(moving_signal)
    cross_power = reference_frequency * moving_frequency.conj()
    magnitude = np.abs(cross_power)
    valid = magnitude > np.finfo(np.float64).eps
    if int(valid.sum()) < 16:
        raise ContentRegistrationError("registration spectrum is ambiguous")
    phase = np.zeros_like(cross_power)
    phase[valid] = cross_power[valid] / magnitude[valid]

    coarse = np.fft.ifftn(phase)
    coarse_peak = tuple(int(value) for value in np.unravel_index(np.argmax(np.abs(coarse)), coarse.shape))
    peak_ratio = _coarse_peak_ratio(coarse, coarse_peak)
    shifts = np.array(coarse_peak, dtype=np.float64)
    midpoints = np.trunc(np.array(reference.shape, dtype=np.float64) / 2.0)
    shape = np.array(reference.shape, dtype=np.float64)
    shifts[shifts > midpoints] -= shape[shifts > midpoints]

    if upsample_factor > 1:
        shifts = np.round(shifts * upsample_factor) / upsample_factor
        region_extent = int(np.ceil(upsample_factor * 1.5))
        region_center = float(np.trunc(region_extent / 2.0))
        offsets = tuple(region_center - shifts * upsample_factor)
        refined = _upsampled_dft(
            phase.conj(),
            (region_extent, region_extent),
            upsample_factor,
            offsets,
        ).conj()
        refined_peak = np.array(
            np.unravel_index(np.argmax(np.abs(refined)), refined.shape),
            dtype=np.float64,
        )
        refined_peak -= region_center
        shifts += refined_peak / upsample_factor

    row_shift, column_shift = (float(value) for value in shifts)
    return {
        "row_shift_to_apply_px": round(row_shift, 4),
        "column_shift_to_apply_px": round(column_shift, 4),
        "magnitude_px": round(float(np.hypot(row_shift, column_shift)), 4),
        "coarse_peak_ratio": round(float(peak_ratio), 4),
        "sample_resolution_px": round(1.0 / upsample_factor, 6),
        "reference_energy": round(reference_energy, 6),
        "moving_energy": round(moving_energy, 6),
    }


def _gradient_signal(reflectance: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    if reflectance.ndim != 2 or reflectance.size == 0:
        raise ContentRegistrationError("reflectance signal must be a non-empty 2D array")
    finite = np.isfinite(reflectance)
    if int(finite.sum()) < int(reflectance.size * MIN_USABLE_FRACTION):
        raise ContentRegistrationError("reflectance signal has insufficient finite coverage")
    median = float(np.median(reflectance[finite]))
    filled = np.where(finite, reflectance, median).astype(np.float64)
    row_gradient, column_gradient = np.gradient(filled)
    gradient = np.hypot(row_gradient, column_gradient)
    low, high = (float(value) for value in np.percentile(gradient[finite], [1, 99]))
    if not np.isfinite(low) or not np.isfinite(high) or high - low <= 1e-9:
        raise ContentRegistrationError("reflectance gradient has insufficient texture")
    clipped = np.clip(gradient, low, high)
    return clipped, {
        "finite_fraction": round(float(finite.mean()), 6),
        "fill_value": round(median, 8),
        "gradient_clip_percentiles": [1, 99],
        "gradient_clip_values": [round(low, 8), round(high, 8)],
    }


def _window_bounds(
    aoi_bounds: list[float], row_offset: int, column_offset: int
) -> list[float]:
    west, _south, _east, north = aoi_bounds
    return [
        round(west + column_offset * PIXEL_SIZE_M, 3),
        round(north - (row_offset + WINDOW_SIZE_PX) * PIXEL_SIZE_M, 3),
        round(west + (column_offset + WINDOW_SIZE_PX) * PIXEL_SIZE_M, 3),
        round(north - row_offset * PIXEL_SIZE_M, 3),
    ]


def measure_registration_windows(
    pre_signals: dict[str, np.ndarray],
    post_signals: dict[str, np.ndarray],
    pair_state: np.ndarray,
    aoi_bounds: list[float],
) -> list[dict[str, Any]]:
    """Measure all 12 fixed non-overlapping AOI windows and classify the gate."""

    if pair_state.shape != (450, 600):
        raise ContentRegistrationError("pair-quality grid is not 450 x 600")
    if np.any(~np.isin(pair_state, [0, 1, 2])):
        raise ContentRegistrationError("pair-quality grid contains an unknown state")
    for band in SELECTED_BANDS:
        if pre_signals.get(band) is None or post_signals.get(band) is None:
            raise ContentRegistrationError(f"missing registration signal for {band}")
        if pre_signals[band].shape != pair_state.shape or post_signals[band].shape != pair_state.shape:
            raise ContentRegistrationError(f"registration signal grid mismatch for {band}")

    windows: list[dict[str, Any]] = []
    for row_number, row_offset in enumerate(range(0, 450, WINDOW_SIZE_PX), start=1):
        for column_number, column_offset in enumerate(range(0, 600, WINDOW_SIZE_PX), start=1):
            row_slice = slice(row_offset, row_offset + WINDOW_SIZE_PX)
            column_slice = slice(column_offset, column_offset + WINDOW_SIZE_PX)
            quality = pair_state[row_slice, column_slice]
            eligible_fraction = float(np.mean(quality == 0))
            review_fraction = float(np.mean(quality == 1))
            excluded_fraction = float(np.mean(quality == 2))
            band_results: dict[str, Any] = {}
            confident_vectors: list[list[float]] = []
            for band in SELECTED_BANDS:
                try:
                    result = estimate_subpixel_shift(
                        pre_signals[band][row_slice, column_slice],
                        post_signals[band][row_slice, column_slice],
                    )
                except ContentRegistrationError as error:
                    band_results[band] = {
                        "confident": False,
                        "reason": str(error),
                    }
                    continue
                result["confident"] = result["coarse_peak_ratio"] >= MIN_PEAK_RATIO
                result["reason"] = (
                    "PEAK_RATIO_PASS" if result["confident"] else "PEAK_RATIO_BELOW_GATE"
                )
                band_results[band] = result
                if result["confident"]:
                    confident_vectors.append(
                        [result["row_shift_to_apply_px"], result["column_shift_to_apply_px"]]
                    )

            consensus: dict[str, Any] | None = None
            if len(confident_vectors) >= MIN_CONFIDENT_BANDS:
                vectors = np.asarray(confident_vectors, dtype=np.float64)
                median_vector = np.median(vectors, axis=0)
                deviations = np.linalg.norm(vectors - median_vector, axis=1)
                consensus = {
                    "row_shift_to_apply_px": round(float(median_vector[0]), 4),
                    "column_shift_to_apply_px": round(float(median_vector[1]), 4),
                    "magnitude_px": round(float(np.linalg.norm(median_vector)), 4),
                    "magnitude_m": round(float(np.linalg.norm(median_vector)) * PIXEL_SIZE_M, 3),
                    "max_band_deviation_px": round(float(np.max(deviations)), 4),
                    "confident_band_count": len(confident_vectors),
                }

            if eligible_fraction < MIN_USABLE_FRACTION:
                state = "excluded"
                reason = "ELIGIBLE_FRACTION_BELOW_GATE"
            elif consensus is None:
                state = "review-needed"
                reason = "INSUFFICIENT_CONFIDENT_BANDS"
            elif consensus["max_band_deviation_px"] > MAX_BAND_DEVIATION_PX:
                state = "review-needed"
                reason = "BAND_CONSENSUS_EXCEEDS_GATE"
            elif consensus["magnitude_px"] > MAX_RESIDUAL_PX:
                state = "fail-registration"
                reason = "CONTENT_RESIDUAL_EXCEEDS_GATE"
            else:
                state = "pass"
                reason = "CONTENT_REGISTRATION_PASS"

            windows.append(
                {
                    "window_id": f"W-R{row_number:02d}-C{column_number:02d}",
                    "grid_row": row_number,
                    "grid_column": column_number,
                    "pixel_window": {
                        "row_offset": row_offset,
                        "column_offset": column_offset,
                        "height": WINDOW_SIZE_PX,
                        "width": WINDOW_SIZE_PX,
                    },
                    "bounds_utm10n": _window_bounds(aoi_bounds, row_offset, column_offset),
                    "pair_quality": {
                        "eligible_fraction": round(eligible_fraction, 6),
                        "review_needed_fraction": round(review_fraction, 6),
                        "excluded_fraction": round(excluded_fraction, 6),
                    },
                    "band_measurements": band_results,
                    "consensus": consensus,
                    "state": state,
                    "reason_code": reason,
                    "label_effect": (
                        "none; this window result never assigns burned or background and never overrides pixel quality"
                    ),
                }
            )
    return windows


def _geometric_quality_metadata(archive_path: Path) -> dict[str, Any]:
    """Read the bounded datastrip geometric report, including its cautions."""

    with zipfile.ZipFile(archive_path) as archive:
        matches = [
            name
            for name in archive.namelist()
            if "/DATASTRIP/" in name and name.endswith("/QI_DATA/GEOMETRIC_QUALITY.xml")
        ]
        if len(matches) != 1:
            raise ContentRegistrationError("expected one datastrip geometric-quality report")
        try:
            member_bytes = archive.read(matches[0])
            root = ET.fromstring(member_bytes)
        except (KeyError, ET.ParseError, UnicodeError):
            raise ContentRegistrationError("invalid datastrip geometric-quality report") from None
    reports = [item for item in root.iter() if _local_name(item.tag) == "report"]
    if len(reports) != 1:
        raise ContentRegistrationError("geometric-quality report root is ambiguous")
    inspections: dict[str, Any] = {}
    selected = {
        "Geometric_Refining_Image_Refining",
        "Geometric_Refining_Spatio_Residual_Histograms",
        "Geometric_Refining_Vnir_Swir_Registration",
        "Absolute_Location_Value",
        "Planimetric_Stability",
        "Ephemeris_Quality",
    }
    checks = [item for item in root.iter() if _local_name(item.tag) == "check"]
    for check in checks:
        candidates = [item for item in check if _local_name(item.tag) == "inspection"]
        if len(candidates) != 1:
            raise ContentRegistrationError("geometric-quality check has ambiguous inspection metadata")
        inspection = candidates[0]
        identifier = inspection.attrib.get("id", "")
        if identifier not in selected:
            continue
        messages = [
            (item.text or "").strip()
            for item in check.iter()
            if _local_name(item.tag) == "message"
        ]
        values = {
            item.attrib.get("name", ""): (item.text or "").strip()
            for item in check.iter()
            if _local_name(item.tag) == "value"
        }
        inspections[identifier] = {
            "status": inspection.attrib.get("status"),
            "processing_status": inspection.attrib.get("processingStatus"),
            "message": messages[0] if messages else "",
            "values": values,
        }
    return {
        "member": matches[0],
        "member_sha256": sha256(member_bytes).hexdigest(),
        "report_global_status": reports[0].attrib.get("globalStatus"),
        "report_date": reports[0].attrib.get("date"),
        "inspections": inspections,
        "interpretation": (
            "Product QC is contextual provenance only. It does not prove pair-local content registration; "
            "the packaged report says VNIR/SWIR bands have not been registered and spatio-residual histograms were not computed."
        ),
    }


def _summary(windows: list[dict[str, Any]]) -> dict[str, Any]:
    states = {name: sum(item["state"] == name for item in windows) for name in (
        "pass", "review-needed", "excluded", "fail-registration"
    )}
    magnitudes = np.array(
        [item["consensus"]["magnitude_px"] for item in windows if item["consensus"] is not None],
        dtype=np.float64,
    )
    if magnitudes.size == 0:
        percentiles = {"p50_px": None, "p95_px": None, "max_px": None, "max_m": None}
    else:
        p50, p95, maximum = (float(value) for value in np.percentile(magnitudes, [50, 95, 100]))
        percentiles = {
            "p50_px": round(p50, 4),
            "p95_px": round(p95, 4),
            "max_px": round(maximum, 4),
            "max_m": round(maximum * PIXEL_SIZE_M, 3),
        }
    if states["fail-registration"]:
        machine_decision = "REJECT_REGISTRATION_REMEDIATE"
    elif states["review-needed"] or states["excluded"]:
        machine_decision = "ACCEPT_REGISTRATION_WITH_SPATIAL_EXCLUSIONS"
    else:
        machine_decision = "PASS_LOCAL_CONTENT_REGISTRATION_GATE"
    return {
        "window_count": len(windows),
        "state_counts": states,
        **percentiles,
        "machine_decision": machine_decision,
    }


def _validate_visual_decision(machine_decision: str, decision: str, notes: str) -> None:
    allowed = {
        "PENDING_VISUAL_REVIEW",
        "ACCEPT_LOCAL_CONTENT_REGISTRATION",
        "ACCEPT_REGISTRATION_WITH_SPATIAL_EXCLUSIONS",
        "REJECT_REGISTRATION_REMEDIATE",
    }
    if decision not in allowed:
        raise ContentRegistrationError("invalid visual review decision")
    if decision != "PENDING_VISUAL_REVIEW" and not notes.strip():
        raise ContentRegistrationError("final visual review requires notes")
    compatible = {
        "PASS_LOCAL_CONTENT_REGISTRATION_GATE": {"ACCEPT_LOCAL_CONTENT_REGISTRATION"},
        "ACCEPT_REGISTRATION_WITH_SPATIAL_EXCLUSIONS": {
            "ACCEPT_REGISTRATION_WITH_SPATIAL_EXCLUSIONS",
            "REJECT_REGISTRATION_REMEDIATE",
        },
        "REJECT_REGISTRATION_REMEDIATE": {"REJECT_REGISTRATION_REMEDIATE"},
    }
    if decision != "PENDING_VISUAL_REVIEW" and decision not in compatible[machine_decision]:
        raise ContentRegistrationError("visual decision is incompatible with the machine gate")


def build_report(
    *,
    package: Path,
    aoi_report_path: Path,
    optical_report_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    visual_review_decision: str,
    visual_review_notes: str,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    verification = verify_registered_package(
        package,
        OPTICAL_CONTRACTS,
        contract_validator=validate_optical_contracts,
        contract_version=CONTRACT_VERSION,
    )
    if not verification["accepted_as_unchanged_registered_package"]:
        raise ContentRegistrationError("registered optical pair verification failed")
    aoi = json.loads(aoi_report_path.read_text(encoding="utf-8"))
    optical = json.loads(optical_report_path.read_text(encoding="utf-8"))
    if aoi.get("aoi_version") != AOI_VERSION:
        raise ContentRegistrationError("unexpected AOI version")
    if optical.get("report_id") != OPTICAL_REPORT_ID or optical.get("decision") != "ACCEPT_OPTICAL_PAIR_FOR_PROTOCOL_DEFER_LABELS":
        raise ContentRegistrationError("optical predecessor is not the accepted checkpoint")
    if optical.get("package_id") != PACKAGE_ID or optical.get("label_schema_version") != LABEL_PROTOCOL_VERSION:
        raise ContentRegistrationError("optical predecessor contract mismatch")

    aoi_bounds = [float(value) for value in aoi["derivation"]["aoi_bbox_utm10n"]]
    pre_scene, pre_arrays = _read_scene(package, 0, aoi_bounds)
    post_scene, post_arrays = _read_scene(package, 1, aoi_bounds)
    for band in (*SELECTED_BANDS, "SCL"):
        if pre_scene["rasters"][band]["source_transform"] != post_scene["rasters"][band]["source_transform"]:
            raise ContentRegistrationError(f"pre/post {band} transforms differ")
        if pre_scene["rasters"][band]["aoi_bounds_utm10n"] != post_scene["rasters"][band]["aoi_bounds_utm10n"]:
            raise ContentRegistrationError(f"pre/post {band} bounds differ")

    pair_state, pair_quality = classify_pair_quality(pre_arrays["SCL"], post_arrays["SCL"])
    pre_signals: dict[str, np.ndarray] = {}
    post_signals: dict[str, np.ndarray] = {}
    signal_contract: dict[str, Any] = {}
    for band in SELECTED_BANDS:
        pre_reflectance, _ = _reflectance(pre_scene, pre_arrays, band)
        post_reflectance, _ = _reflectance(post_scene, post_arrays, band)
        pre_signals[band], pre_stats = _gradient_signal(pre_reflectance)
        post_signals[band], post_stats = _gradient_signal(post_reflectance)
        signal_contract[band] = {"pre": pre_stats, "post": post_stats}

    windows = measure_registration_windows(pre_signals, post_signals, pair_state, aoi_bounds)
    summary = _summary(windows)
    _validate_visual_decision(summary["machine_decision"], visual_review_decision, visual_review_notes)
    decision_detail = {
        "PENDING_VISUAL_REVIEW": (
            "The deterministic local measurements are complete; rendered pre/post content, window states, "
            "residuals, and trace evidence still require visual review."
        ),
        "ACCEPT_LOCAL_CONTENT_REGISTRATION": (
            "Accept the exact pair's measured local content registration for the frozen AOI. Every fixed window "
            "passes the residual, confidence, band-consensus, and usable-coverage gates. Pixel-level review and "
            "exclusion states remain unchanged, and no label has been created."
        ),
        "ACCEPT_REGISTRATION_WITH_SPATIAL_EXCLUSIONS": (
            "Accept only the passing registration windows and preserve every review/excluded window as spatially "
            "ineligible for later label construction until separately resolved."
        ),
        "REJECT_REGISTRATION_REMEDIATE": (
            "Reject the pair-local registration gate and remediate or replace the affected source evidence before "
            "any label proposal."
        ),
    }[visual_review_decision]

    quality_metadata = {
        contract.role: _geometric_quality_metadata(package / contract.expected_filename)
        for contract in OPTICAL_CONTRACTS
    }
    report: dict[str, Any] = {
        "report_id": REPORT_ID,
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
        "serialization": "UTF-8 JSON and HTML with LF line endings; deterministic PNG for fixed inputs",
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 347,
        "branch": "codex/p2o3-t01-content-registration",
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": None,
        "aoi_version": AOI_VERSION,
        "target_version": TARGET_VERSION,
        "dataset_version": None,
        "label_schema_version": LABEL_PROTOCOL_VERSION,
        "label_schema_implemented": False,
        "baseline_version": None,
        "model_version": None,
        "registration_protocol_version": REGISTRATION_PROTOCOL_VERSION,
        "package_id": PACKAGE_ID,
        "package_contract_version": CONTRACT_VERSION,
        "package_verification": verification,
        "terms_review_id": TERMS_REVIEW_ID,
        "input_hashes": {
            "aoi_report_sha256_lf_normalized": _sha256_lf_text(aoi_report_path),
            "optical_report_sha256_lf_normalized": _sha256_lf_text(optical_report_path),
        },
        "predecessor": {
            "report_id": optical["report_id"],
            "report_version": optical["report_version"],
            "run_id": optical["run_id"],
            "git_source_commit": optical["git_source_commit"],
            "decision": optical["decision"],
        },
        "aoi": {
            "bbox_utm10n": aoi_bounds,
            "width_px_at_20m": 600,
            "height_px_at_20m": 450,
            "pixel_size_m": PIXEL_SIZE_M,
        },
        "pair_identity": {
            "pre_native_id": pre_scene["native_id"],
            "post_native_id": post_scene["native_id"],
            "native_20m_grid_equal": True,
            "reprojection_performed": False,
            "source_resampling_performed": False,
        },
        "product_geometric_quality": quality_metadata,
        "pair_quality": pair_quality,
        "method": {
            "protocol_version": REGISTRATION_PROTOCOL_VERSION,
            "quantity": "translation shift to apply to post/moving content to align with pre/reference content",
            "signals": (
                "Independent pre and post native-20m B04, B8A, and B12 reflectance gradient magnitudes; "
                "each gradient is clipped at its own AOI 1st/99th percentiles."
            ),
            "shared_mask_applied_to_correlation": False,
            "shared_mask_rationale": (
                "A shared stable/quality mask can manufacture a zero-shift correlation peak. Pair quality is used "
                "only to classify window usability and never multiplied into either correlation signal."
            ),
            "taper": "separable Hann taper inside each window",
            "estimator": "phase-only cross-power spectrum with localized upsampled DFT refinement",
            "upsample_factor": UPSAMPLE_FACTOR,
            "sample_resolution_px": 1 / UPSAMPLE_FACTOR,
            "window_grid": "4 columns x 3 rows; 12 non-overlapping 150 x 150 native-20m windows covering the AOI",
            "gates": {
                "minimum_eligible_fraction": MIN_USABLE_FRACTION,
                "minimum_confident_bands": MIN_CONFIDENT_BANDS,
                "minimum_coarse_peak_ratio": MIN_PEAK_RATIO,
                "maximum_band_deviation_px": MAX_BAND_DEVIATION_PX,
                "maximum_residual_px": MAX_RESIDUAL_PX,
                "maximum_residual_m": MAX_RESIDUAL_PX * PIXEL_SIZE_M,
            },
            "selection_boundaries": (
                "NIFC geometry, dNBR, VIIRS observations, burn/background assumptions, and label thresholds do not "
                "select pixels, windows, peaks, or decisions."
            ),
            "signal_details": signal_contract,
            "primary_sources": list(PRIMARY_SOURCES),
        },
        "windows": windows,
        "summary": summary,
        "visual_review": {
            "decision": visual_review_decision,
            "notes": visual_review_notes,
            "rendered_source_pixels_reviewed": visual_review_decision != "PENDING_VISUAL_REVIEW",
        },
        "decision": visual_review_decision,
        "decision_detail": decision_detail,
        "quality_gates": {
            "registered_pair_reverified": True,
            "accepted_optical_predecessor_reverified": True,
            "native_grid_identity_reverified": True,
            "real_b04_b8a_b12_pixels_measured": True,
            "all_windows_cover_aoi_once": len(windows) == 12,
            "source_pixels_resampled": False,
            "shared_mask_used_in_estimator": False,
            "label_array_created": False,
            "dataset_created": False,
            "baseline_created": False,
            "model_created": False,
        },
        "claims": {
            "permitted": [
                "BurnLens measured pair-local translation residuals on the exact native-grid Sentinel-2 pair.",
                "Window decisions preserve confidence, band-consensus, usable-coverage, and residual evidence.",
                "Registration evidence is inspectable and traceable to the exact source package and predecessor run.",
            ],
            "prohibited": [
                "A passing registration window is burned, unburned, background, or independently validated truth.",
                "Product-level Sentinel QC alone proves pair-local registration.",
                "The evidence establishes a label set, dataset, baseline, model, operational result, or field validation.",
            ],
        },
        "limitations": [
            "The estimator tests local translation, not all deformation, parallax, atmosphere, spectral, or temporal differences.",
            "Gradient structure can change between dates; cross-band consensus and peak-ratio gates reduce but do not eliminate ambiguity.",
            "The 0.5-pixel residual gate is a BurnLens label-readiness requirement, not a provider guarantee or accuracy claim.",
            "Pixel-level SCL review and exclusions remain independently binding after any window-level pass.",
            "One event cannot support leakage-resistant train, validation, and test groups.",
        ],
        "attribution": ["Contains modified Copernicus Sentinel data 2024."],
        "source_precedence": "Official sources govern over every BurnLens-derived artifact.",
        "warning": WARNING,
        "rendered_outputs": {
            "json": f"{REPORT_ID}.json",
            "html": f"{REPORT_ID}.html",
            "png": f"{REPORT_ID}.png",
        },
    }
    return report, {"pre_tci": pre_arrays["TCI"], "post_tci": post_arrays["TCI"]}


def _render_scene_panel(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    rgb: np.ndarray,
    box: tuple[int, int, int, int],
    title: str,
    subtitle: str,
) -> None:
    image = Image.fromarray(np.moveaxis(rgb, 0, 2), mode="RGB")
    image = image.resize((box[2] - box[0], box[3] - box[1]), Image.Resampling.LANCZOS)
    canvas.paste(image, (box[0], box[1]))
    draw.rectangle(box, outline="#132a26", width=3)
    draw.rectangle((box[0], box[1], box[2], box[1] + 62), fill="#132a26")
    draw.text((box[0] + 16, box[1] + 9), title, fill="white", font=_font(18))
    draw.text((box[0] + 16, box[1] + 36), subtitle, fill="#b9d8cf", font=_font(14))


def render_png(report: dict[str, Any], pre_rgb: np.ndarray, post_rgb: np.ndarray, path: Path) -> None:
    canvas = Image.new("RGB", (1800, 1250), "#f4f0e8")
    draw = ImageDraw.Draw(canvas)
    ink, muted, teal, orange = "#15211d", "#5d6b64", "#006b64", "#f05a28"
    draw.rectangle((0, 0, 1800, 170), fill="#132a26")
    draw.text((65, 35), "BURNLENS / PAIR-LOCAL REGISTRATION", fill="#b9d8cf", font=_font(22))
    draw.text((65, 75), "CONTENT RESIDUAL EVIDENCE", fill="white", font=_font(38))
    draw.text((1330, 42), "DECISION", fill="#b9d8cf", font=_font(18))
    label = {
        "PENDING_VISUAL_REVIEW": "REVIEW PENDING",
        "ACCEPT_LOCAL_CONTENT_REGISTRATION": "GATE ACCEPTED",
        "ACCEPT_REGISTRATION_WITH_SPATIAL_EXCLUSIONS": "PARTIAL ACCEPT",
        "REJECT_REGISTRATION_REMEDIATE": "REMEDIATE",
    }[report["decision"]]
    draw.text((1330, 78), label, fill="#ffd166", font=_font(28))
    draw.text((1330, 121), "no labels created", fill="white", font=_font(17))

    pre_box = (55, 220, 575, 610)
    post_box = (640, 220, 1160, 610)
    grid_box = (1225, 220, 1745, 610)
    _render_scene_panel(canvas, draw, pre_rgb, pre_box, "PRE / REFERENCE", "Sentinel-2A true color / 10 m")
    _render_scene_panel(canvas, draw, post_rgb, post_box, "POST / MOVING", "Sentinel-2A true color / 10 m")
    grid_image = Image.fromarray(np.moveaxis(pre_rgb, 0, 2), mode="RGB")
    grid_image = grid_image.resize((grid_box[2] - grid_box[0], grid_box[3] - grid_box[1]), Image.Resampling.LANCZOS)
    overlay = Image.new("RGBA", grid_image.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    state_colors = {
        "pass": (0, 107, 100, 104),
        "review-needed": (126, 63, 143, 130),
        "excluded": (94, 100, 96, 145),
        "fail-registration": (240, 90, 40, 145),
    }
    cell_width = overlay.width / 4
    cell_height = overlay.height / 3
    for item in report["windows"]:
        left = int(round((item["grid_column"] - 1) * cell_width))
        top = int(round((item["grid_row"] - 1) * cell_height))
        right = int(round(item["grid_column"] * cell_width))
        bottom = int(round(item["grid_row"] * cell_height))
        overlay_draw.rectangle((left, top, right, bottom), fill=state_colors[item["state"]], outline="white", width=2)
        value = "n/a" if item["consensus"] is None else f"{item['consensus']['magnitude_px']:.3f} px"
        text_top = top + (76 if item["grid_row"] == 1 else 42)
        overlay_draw.text((left + 10, text_top), value, fill="white", font=_font(15), stroke_width=2, stroke_fill="#15211d")
    grid_image = Image.alpha_composite(grid_image.convert("RGBA"), overlay).convert("RGB")
    canvas.paste(grid_image, (grid_box[0], grid_box[1]))
    draw.rectangle(grid_box, outline="#132a26", width=3)
    draw.rectangle((grid_box[0], grid_box[1], grid_box[2], grid_box[1] + 62), fill="#132a26")
    draw.text((grid_box[0] + 16, grid_box[1] + 9), "12-WINDOW RESIDUAL GRID", fill="white", font=_font(18))
    draw.text((grid_box[0] + 16, grid_box[1] + 36), "consensus shift magnitude / native 20 m px", fill="#b9d8cf", font=_font(14))

    summary = report["summary"]
    cards = [
        (str(summary["state_counts"]["pass"]), "windows pass", teal),
        (f"{summary['p50_px']:.3f} px", "median residual", teal),
        (f"{summary['p95_px']:.3f} px", "p95 residual", teal),
        (f"{summary['max_px']:.3f} px", f"maximum / {summary['max_m']:.2f} m", orange),
    ]
    left = 55
    for value, text_value, color in cards:
        draw.rounded_rectangle((left, 650, left + 400, 780), radius=16, fill="#fffdf8", outline="#d4cec1", width=2)
        draw.text((left + 24, 675), value, fill=color, font=_font(30))
        draw.text((left + 24, 727), text_value, fill=muted, font=_font(17))
        left += 430

    draw.rounded_rectangle((55, 820, 1745, 1085), radius=18, fill="#e5efeb", outline="#aac8bf", width=2)
    draw.text((82, 846), "METHOD + FAIL-CLOSED GATES", fill=teal, font=_font(22))
    method_lines = [
        "B04 + B8A + B12 independent reflectance gradients / no shared correlation mask",
        "Hann taper + phase-only cross-power + localized 100x DFT refinement (0.01 px samples)",
        "Gate: eligible >= 90% / >= 2 confident bands / peak ratio >= 2 / band deviation <= 0.15 px",
        "Residual <= 0.50 native pixel (10 m); otherwise remediate or spatially exclude",
        "Window pass never overrides SCL review/excluded pixels and never assigns burned/background",
    ]
    for index, line in enumerate(method_lines):
        draw.text((100, 894 + index * 35), f"{index + 1}. {line}", fill=ink, font=_font(17))

    draw.text((55, 1115), "Contains modified Copernicus Sentinel data 2024  |  official sources govern", fill=muted, font=_font(16))
    trace = (
        f"run {report['run_id']} / source {report['git_source_commit'][:12]} / software {report['software_version']} / "
        f"registration {report['registration_protocol_version']} / labels unimplemented / dataset none / baseline none / model none"
    )
    draw.text((55, 1150), trace, fill=muted, font=_font(14))
    draw.text((55, 1180), "Product QC is context only; pair-local evidence above controls this gate.", fill=orange, font=_font(15))
    draw.text((55, 1216), WARNING, fill="#33443e", font=_font(13))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], png_name: str, path: Path) -> None:
    row_fragments: list[str] = []
    for item in report["windows"]:
        consensus = item["consensus"]
        row_shift = "n/a" if consensus is None else f"{consensus['row_shift_to_apply_px']:.4f}"
        column_shift = "n/a" if consensus is None else f"{consensus['column_shift_to_apply_px']:.4f}"
        magnitude = "n/a" if consensus is None else f"{consensus['magnitude_px']:.4f}"
        row_fragments.append(
            "<tr>"
            f"<td><code>{escape(item['window_id'])}</code></td>"
            f"<td>{escape(item['state'])}</td>"
            f"<td>{row_shift}</td>"
            f"<td>{column_shift}</td>"
            f"<td>{magnitude}</td>"
            f"<td>{item['pair_quality']['eligible_fraction'] * 100:.2f}%</td>"
            f"<td>{escape(item['reason_code'])}</td>"
            "</tr>"
        )
    rows = "".join(row_fragments)
    summary = report["summary"]
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens pair-local content registration</title><style>
:root {{ color-scheme:light; --ink:#15211d; --muted:#5d6b64; --paper:#f4f0e8; --panel:#fffdf8; --teal:#006b64; --orange:#f05a28; }}
* {{ box-sizing:border-box; }} body {{ margin:0; background:var(--paper); color:var(--ink); font:16px/1.55 system-ui,sans-serif; }}
header {{ background:#132a26; color:white; padding:3rem max(5vw,2rem); }} header p {{ color:#b9d8cf; }} main {{ max-width:1250px; margin:auto; padding:2.5rem 1.5rem 5rem; }}
.warning {{ background:#fff1ca; border-left:6px solid #d87618; padding:1rem 1.2rem; font-weight:650; }} .hero {{ display:block; width:100%; height:auto; border:1px solid #c8c0b2; margin:1.5rem 0; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:1rem; }} .card {{ background:var(--panel); border:1px solid #d9d1c4; border-radius:12px; padding:1.2rem; }}
.decision {{ border:2px solid var(--orange); }} .value {{ color:var(--teal); font-size:2rem; font-weight:800; }} .table-wrap {{ overflow-x:auto; }} table {{ width:100%; border-collapse:collapse; background:var(--panel); }}
th,td {{ padding:.7rem; border-bottom:1px solid #ddd5c9; text-align:left; vertical-align:top; white-space:nowrap; }} code {{ overflow-wrap:anywhere; white-space:normal; }} h2 {{ margin-top:2.4rem; }}
</style></head><body><header><p>BurnLens / Phase Two / Objective Three</p><h1>Pair-local content registration</h1><p>Measured evidence before any burn-scar label proposal.</p></header><main>
<p class="warning">{escape(WARNING)}</p><img class="hero" src="{escape(png_name)}" alt="Pre and post Sentinel-2 images with a twelve-window local registration residual grid">
<section class="card decision"><h2>Decision</h2><p><strong>{escape(report['decision'])}</strong></p><p>{escape(report['decision_detail'])}</p><p>Machine gate: <code>{escape(summary['machine_decision'])}</code>.</p></section>
<div class="grid"><div class="card"><div class="value">{summary['state_counts']['pass']} / 12</div><div>windows pass</div></div><div class="card"><div class="value">{summary['p95_px']:.3f} px</div><div>p95 content residual</div></div><div class="card"><div class="value">{summary['max_px']:.3f} px</div><div>maximum residual / {summary['max_m']:.2f} m</div></div><div class="card"><div class="value">0 labels</div><div>dataset, baseline, and model remain absent</div></div></div>
<h2>What was measured</h2><div class="card"><p>{escape(report['method']['signals'])}</p><ul><li>{escape(report['method']['estimator'])}; {report['method']['upsample_factor']}x refinement.</li><li>{escape(report['method']['window_grid'])}.</li><li>{escape(report['method']['shared_mask_rationale'])}</li><li>{escape(report['method']['selection_boundaries'])}</li></ul></div>
<h2>Window evidence</h2><div class="table-wrap"><table><thead><tr><th>Window</th><th>State</th><th>Row shift to apply (px)</th><th>Column shift to apply (px)</th><th>Magnitude (px)</th><th>Eligible pixels</th><th>Reason</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Product QC caveat</h2><div class="card"><p>Both packaged datastrip reports have global status PASSED. They also state that VNIR/SWIR bands have not been registered and that spatio-residual histograms were not computed. Product QC is provenance context, not this pair-local gate.</p></div>
<h2>Traceability</h2><div class="card"><p><strong>Run:</strong> <code>{escape(report['run_id'])}</code><br><strong>Git source:</strong> <code>{escape(report['git_source_commit'])}</code><br><strong>Software / report / method:</strong> <code>{escape(report['software_version'])}</code> / <code>{escape(report['report_version'])}</code> / <code>{escape(report['registration_protocol_version'])}</code><br><strong>AOI / target / label protocol:</strong> <code>{escape(report['aoi_version'])}</code> / <code>{escape(report['target_version'])}</code> / <code>{escape(report['label_schema_version'])}</code> (unimplemented)<br><strong>Package / contract:</strong> <code>{escape(report['package_id'])}</code> / <code>{escape(report['package_contract_version'])}</code><br><strong>Application / dataset / baseline / model:</strong> none / none / none / none</p></div>
<h2>Boundaries</h2><ul><li>A pass is registration evidence, never burned/background truth.</li><li>Pixel-level review and exclusion states remain binding.</li><li>No label array, dataset, split, baseline, model, metric, application, deployment, operational result, or field validation was created.</li><li>Contains modified Copernicus Sentinel data 2024. Official sources govern.</li></ul>
</main></body></html>"""
    _write_utf8_lf(path, document)


def write_report(
    *, report: dict[str, Any], arrays: dict[str, np.ndarray], output_directory: Path
) -> dict[str, Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    json_path = output_directory / f"{REPORT_ID}.json"
    html_path = output_directory / f"{REPORT_ID}.html"
    png_path = output_directory / f"{REPORT_ID}.png"
    _write_utf8_lf(json_path, json.dumps(report, indent=2) + "\n")
    render_png(report, arrays["pre_tci"], arrays["post_tci"], png_path)
    render_html(report, png_path.name, html_path)
    return {"json": json_path, "html": html_path, "png": png_path}


def measure_content_registration(
    *,
    package: Path,
    aoi_report_path: Path,
    optical_report_path: Path,
    output_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    visual_review_decision: str,
    visual_review_notes: str,
) -> dict[str, Path]:
    report, arrays = build_report(
        package=package,
        aoi_report_path=aoi_report_path,
        optical_report_path=optical_report_path,
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
        visual_review_decision=visual_review_decision,
        visual_review_notes=visual_review_notes,
    )
    return write_report(report=report, arrays=arrays, output_directory=output_directory)
