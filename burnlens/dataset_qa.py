"""Independently audit and render the exact BurnLens prototype dataset."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from html import escape
import json
import math
import os
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import rasterio
from rasterio.transform import array_bounds
from rasterio.windows import Window, from_bounds

from . import __version__


REPORT_ID = "DATASET-QA-2026-001"
REPORT_VERSION = "burnlens-dataset-qa-v0.1.0"
NORMALIZATION_ID = "TRAIN-NORMALIZATION-2026-001"
NORMALIZATION_VERSION = "burnlens-train-normalization-v0.1.0"
TASK_ISSUE = 562
UNIT_ID = "P2O5-T03-U04"
DATASET_ROOT = Path("samples/datasets/burnlens-dataset-v0.1.0")
DATASET_MANIFEST_PATH = DATASET_ROOT / "DATASET-MANIFEST.json"
DATASET_MANIFEST_SHA256 = (
    "e0b7ac666a70e96f979c386a9d503ad45ed0baea8f21e3838ba4530d5e3d2d16"
)
CONTRACT_PATH = Path(
    "records/phase-two/manifests/DATASET-BUILD-CONTRACT-2026-001.json"
)
CONTRACT_SHA256 = (
    "f6106691d42692f39684ed43c35f7c097d51f08b13c3dc3bf1e030ca9687b67f"
)
SPLIT_PATH = Path(
    "records/phase-two/manifests/WHOLE-EVENT-SPLIT-2026-001.json"
)
SPLIT_SHA256 = (
    "a62e66f4f81a95a56a727b29bb382cb87369306f11e2f2a4527d1c7fb68d0b99"
)
CANDIDATE_PATH = Path(
    "records/phase-two/readiness/DATASET-CANDIDATE-2026-002.json"
)
CANDIDATE_SHA256 = (
    "4a9646af493cdce81d0cd57405ebccf0dfecf5ca77c96930d0837c3b7d4e65f2"
)
FEATURE_BANDS = ("B04", "B8A", "B12")
ELIGIBLE_SCL = (4, 5)
WARNING = (
    "Owner-approved prototype evidence, not independent ground truth or "
    "field validation. Official sources govern."
)


class DatasetQaError(RuntimeError):
    """A deterministic independent dataset-QA failure."""


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _binding(root: Path, relative: Path) -> dict[str, Any]:
    path = root / relative
    if not path.is_file():
        raise DatasetQaError(
            f"required input is absent: {relative.as_posix()}"
        )
    return {
        "path": relative.as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
    }


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise DatasetQaError(f"JSON root is not an object: {path}")
    return value


def _load_inputs(
    root: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    bindings = {
        "dataset": _binding(root, DATASET_MANIFEST_PATH),
        "contract": _binding(root, CONTRACT_PATH),
        "split": _binding(root, SPLIT_PATH),
        "candidate": _binding(root, CANDIDATE_PATH),
    }
    expected = {
        "dataset": DATASET_MANIFEST_SHA256,
        "contract": CONTRACT_SHA256,
        "split": SPLIT_SHA256,
        "candidate": CANDIDATE_SHA256,
    }
    for name, digest in expected.items():
        if bindings[name]["sha256"] != digest:
            raise DatasetQaError(f"{name} input hash drift")
    dataset = _read_json(root / DATASET_MANIFEST_PATH)
    contract = _read_json(root / CONTRACT_PATH)
    split = _read_json(root / SPLIT_PATH)
    candidate = _read_json(root / CANDIDATE_PATH)
    if dataset["inventory"]["test_open_count"] != 0:
        raise DatasetQaError("test open count is not zero")
    if dataset["boundaries"]["dataset_qa_passed"] is not False:
        raise DatasetQaError("input dataset already claims QA")
    return dataset, contract, split, candidate


def _archive_index(
    root: Path,
) -> dict[str, tuple[Path, dict[str, Any], dict[str, Any]]]:
    output: dict[str, tuple[Path, dict[str, Any], dict[str, Any]]] = {}
    for registration_path in (
        root / "downloads/phase-two/raw"
    ).rglob(".burnlens-registration.json"):
        registration = _read_json(registration_path)
        if registration.get("synthetic_fixture") is not False:
            continue
        for asset in registration.get("assets", []):
            filename = asset.get("filename")
            if not isinstance(filename, str):
                continue
            if filename in output:
                raise DatasetQaError(
                    f"duplicate archive registration: {filename}"
                )
            output[filename] = (
                registration_path.parent / filename,
                registration,
                asset,
            )
    return output


def _verify_archives(
    root: Path, contract: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    index = _archive_index(root)
    output: dict[str, dict[str, Any]] = {}
    for pair in contract["source_pairs"]:
        for product in pair["products"]:
            filename = product["filename"]
            if filename not in index:
                raise DatasetQaError(f"archive is absent: {filename}")
            path, registration, asset = index[filename]
            observed = {
                "bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
                "links": path.stat().st_nlink,
            }
            if (
                observed["bytes"] != asset["bytes"]
                or observed["sha256"] != asset["sha256"]
                or observed["links"] != 1
                or asset["native_id"] != product["native_id"]
            ):
                raise DatasetQaError(f"archive custody drift: {filename}")
            output[product["role"]] = {
                "path": path,
                "package_id": registration["package_id"],
                "filename": filename,
                "bytes": observed["bytes"],
                "sha256": observed["sha256"],
            }
    if len(output) != 12:
        raise DatasetQaError("archive roster is not exactly twelve")
    return output


def _candidate_event_state(
    root: Path, event: dict[str, Any]
) -> tuple[np.ndarray, dict[str, np.ndarray], rasterio.Affine]:
    arrays: dict[str, np.ndarray] = {}
    transform: rasterio.Affine | None = None
    shape: tuple[int, int] | None = None
    for candidate in event["candidates"]:
        path = root / candidate["raster"]["path"]
        with rasterio.open(path) as source:
            values = source.read(1)
            observed_transform = source.transform
            if str(source.crs) != "EPSG:32610" or source.nodata != 255:
                raise DatasetQaError(
                    f"candidate raster metadata drift: {candidate['candidate_id']}"
                )
        if transform is None:
            transform = observed_transform
            shape = values.shape
        elif transform != observed_transform or shape != values.shape:
            raise DatasetQaError("event candidate grids differ")
        if set(int(value) for value in np.unique(values)) - {0, 1, 2, 255}:
            raise DatasetQaError("candidate raster domain drift")
        arrays[candidate["candidate_id"]] = values
    if transform is None or shape is None:
        raise DatasetQaError("candidate event is empty")
    state = np.full(shape, 255, dtype=np.uint8)
    state[
        np.logical_or.reduce([values == 2 for values in arrays.values()])
    ] = 2
    occupied = np.zeros(shape, dtype=bool)
    for candidate in event["candidates"]:
        core = arrays[candidate["candidate_id"]] == 1
        if np.any(core & occupied):
            raise DatasetQaError("candidate cores overlap")
        state[core] = 0 if candidate["class"] == "background" else 1
        occupied |= core
    return state, arrays, transform


def _source_window(
    source: rasterio.DatasetReader,
    target_transform: rasterio.Affine,
    shape: tuple[int, int],
) -> Window:
    bounds = array_bounds(*shape, target_transform)
    candidate = from_bounds(*bounds, transform=source.transform)
    rounded = Window(
        round(float(candidate.col_off)),
        round(float(candidate.row_off)),
        round(float(candidate.width)),
        round(float(candidate.height)),
    )
    if max(
        abs(float(candidate.col_off) - rounded.col_off),
        abs(float(candidate.row_off) - rounded.row_off),
        abs(float(candidate.width) - rounded.width),
        abs(float(candidate.height) - rounded.height),
    ) > 1e-7:
        raise DatasetQaError("patch is not integer-aligned to source")
    if source.window_transform(rounded) != target_transform:
        raise DatasetQaError("patch transform differs from source window")
    return rounded


def _read_source_patch(
    archive: Path,
    member: str,
    transform: rasterio.Affine,
    dtype: str,
) -> np.ndarray:
    uri = archive.resolve().as_posix()
    with rasterio.open(f"zip://{uri}!{member}") as source:
        if (
            source.driver != "JP2OpenJPEG"
            or source.crs is None
            or source.crs.to_epsg() != 32610
            or source.count != 1
            or source.dtypes != (dtype,)
            or abs(source.transform.a - 20.0) > 1e-9
            or abs(source.transform.e + 20.0) > 1e-9
        ):
            raise DatasetQaError(f"source raster contract drift: {member}")
        values = source.read(
            1, window=_source_window(source, transform, (64, 64))
        )
    if values.shape != (64, 64):
        raise DatasetQaError("source patch shape drift")
    return values


def _registration_for_event(
    report: dict[str, Any], event_id: str
) -> dict[str, Any]:
    if isinstance(report.get("events"), list):
        matching = [
            event
            for event in report["events"]
            if event.get("event_group_id") == event_id
        ]
        if len(matching) != 1:
            raise DatasetQaError("source report event is not unique")
        registration = matching[0]["registration"]
    elif isinstance(report.get("registration"), dict):
        registration = report["registration"]
    else:
        registration = report["optical_reverification"]["registration"]
    return registration


def _registration_patch(
    registration: dict[str, Any],
    event_shape: tuple[int, int],
    patch_window: dict[str, int],
) -> np.ndarray:
    summary = registration.get("summary", {})
    counts = summary.get("state_counts", {})
    if (
        counts
        and counts.get("pass", 0) > 0
        and counts.get("review-needed", 0) == 0
        and counts.get("excluded", 0) == 0
        and counts.get("fail-registration", 0) == 0
        and str(summary.get("machine_decision", "")).startswith("PASS_")
    ):
        return np.ones((64, 64), dtype=bool)
    state = np.full(event_shape, 3, dtype=np.uint8)
    covered = np.zeros(event_shape, dtype=bool)
    rank = {"pass": 0, "review-needed": 1, "excluded": 2}
    for item in registration["windows"]:
        value = rank[item["state"]]
        window = item["pixel_window"]
        row, column = window["row_offset"], window["column_offset"]
        height, width = window["height"], window["width"]
        view = state[row : row + height, column : column + width]
        seen = covered[row : row + height, column : column + width]
        view[~seen] = value
        view[seen] = np.maximum(view[seen], value)
        seen[:] = True
    row = patch_window["row_offset"]
    column = patch_window["column_offset"]
    return state[row : row + 64, column : column + 64] == 0


def _load_array(path: Path, shape: tuple[int, ...], dtype: str) -> np.ndarray:
    value = np.load(path, allow_pickle=False)
    if value.shape != shape or value.dtype != np.dtype(dtype):
        raise DatasetQaError(f"array schema drift: {path}")
    return value


def _patch_bounds(patch: dict[str, Any]) -> tuple[float, float, float, float]:
    transform = rasterio.Affine(*patch["transform"])
    return array_bounds(64, 64, transform)


def _intersects(
    first: tuple[float, float, float, float],
    second: tuple[float, float, float, float],
) -> bool:
    return not (
        first[2] <= second[0]
        or second[2] <= first[0]
        or first[3] <= second[1]
        or second[3] <= first[1]
    )


def _normalization(
    train_features: list[np.ndarray],
    train_valid: list[np.ndarray],
    channel_order: list[str],
) -> dict[str, Any]:
    channels = []
    for index, channel in enumerate(channel_order):
        values = np.concatenate(
            [
                features[index][valid].astype(np.float64)
                for features, valid in zip(train_features, train_valid)
            ]
        )
        if not len(values) or not np.all(np.isfinite(values)):
            raise DatasetQaError(f"train statistics are invalid: {channel}")
        mean = float(np.mean(values, dtype=np.float64))
        std = float(np.std(values, dtype=np.float64))
        if std <= 1e-6:
            raise DatasetQaError(f"train channel variance is too small: {channel}")
        channels.append(
            {
                "channel": channel,
                "eligible_pixel_count": int(len(values)),
                "mean": mean,
                "population_std": std,
                "minimum": float(values.min()),
                "maximum": float(values.max()),
            }
        )
    return {
        "normalization_version": NORMALIZATION_VERSION,
        "normalization_id": NORMALIZATION_ID,
        "statistics_owner": "locked training events only",
        "channel_order": channel_order,
        "method": "per-channel global mean and population standard deviation",
        "standardization": "(value - train_mean) / max(train_std, 1e-6)",
        "validation_pixels_used": False,
        "test_pixels_used": False,
        "channels": channels,
    }


def build_report(
    root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, dict[str, np.ndarray]]]:
    dataset, contract, split, candidate = _load_inputs(root)
    archives = _verify_archives(root, contract)
    pair_by_event = {
        pair["event_group_id"]: pair for pair in contract["source_pairs"]
    }
    event_by_id = {
        event["event_group_id"]: event for event in candidate["events"]
    }
    candidate_by_id = {
        region["candidate_id"]: region
        for event in candidate["events"]
        for region in event["candidates"]
    }
    event_state_cache: dict[
        str, tuple[np.ndarray, dict[str, np.ndarray], rasterio.Affine]
    ] = {}
    reconstructed = 0
    file_bindings = 0
    core_counts: Counter[str] = Counter()
    unknown_pixels = 0
    train_features: list[np.ndarray] = []
    train_valid: list[np.ndarray] = []
    render_arrays: dict[str, dict[str, np.ndarray]] = {}
    feature_hashes: set[str] = set()
    patch_bounds: list[tuple[str, str, tuple[float, float, float, float]]] = []
    source_ids_by_role: dict[str, set[str]] = {
        "train": set(),
        "validation": set(),
        "test": set(),
    }
    for patch in dataset["patches"]:
        patch_root = root / DATASET_ROOT / "patches" / patch["patch_id"]
        for binding in patch["files"]:
            path = root / DATASET_ROOT / binding["path"]
            if (
                path.stat().st_size != binding["bytes"]
                or _sha256_file(path) != binding["sha256"]
            ):
                raise DatasetQaError(
                    f"dataset file binding drift: {binding['path']}"
                )
            file_bindings += 1
        features = _load_array(
            patch_root / "features.npy", (6, 64, 64), "float32"
        )
        state = _load_array(patch_root / "state.npy", (64, 64), "uint8")
        valid = _load_array(
            patch_root / "input_valid.npy", (64, 64), "uint8"
        ).astype(bool)
        loss = _load_array(
            patch_root / "loss_mask.npy", (64, 64), "uint8"
        ).astype(bool)
        if set(int(value) for value in np.unique(state)) - {0, 1, 2, 255}:
            raise DatasetQaError(f"state domain drift: {patch['patch_id']}")
        if not np.array_equal(loss, np.isin(state, (0, 1)) & valid):
            raise DatasetQaError(f"loss-mask drift: {patch['patch_id']}")
        if not np.all(np.isnan(features[:, ~valid])):
            raise DatasetQaError(
                f"invalid features are not NaN: {patch['patch_id']}"
            )
        if not np.all(np.isfinite(features[:, valid])):
            raise DatasetQaError(
                f"valid features are not finite: {patch['patch_id']}"
            )

        event_id = patch["event_group_id"]
        if event_id not in event_state_cache:
            event_state_cache[event_id] = _candidate_event_state(
                root, event_by_id[event_id]
            )
        event_state, candidate_arrays, event_transform = event_state_cache[
            event_id
        ]
        window = patch["window"]
        row, column = window["row_offset"], window["column_offset"]
        expected_state = event_state[row : row + 64, column : column + 64]
        if not np.array_equal(state, expected_state):
            raise DatasetQaError(
                f"candidate-to-state reconstruction drift: {patch['patch_id']}"
            )
        own = candidate_arrays[patch["candidate_id"]]
        if int(
            np.count_nonzero(
                own[row : row + 64, column : column + 64] == 1
            )
        ) != candidate_by_id[patch["candidate_id"]]["core_pixels"]:
            raise DatasetQaError(
                f"candidate core reconstruction drift: {patch['patch_id']}"
            )

        pair = pair_by_event[event_id]
        report = _read_json(root / pair["source_report"]["path"])
        patch_transform = rasterio.Affine(*patch["transform"])
        reconstructed_features = []
        numeric_valid = np.ones((64, 64), dtype=bool)
        scl_arrays = []
        for product in pair["products"]:
            source_ids_by_role[patch["split_role"]].add(product["native_id"])
            archive = archives[product["role"]]["path"]
            for band in FEATURE_BANDS:
                dn = _read_source_patch(
                    archive,
                    product["members"][band],
                    patch_transform,
                    "uint16",
                )
                numeric_valid &= (dn != product["nodata_dn"]) & (
                    dn != product["saturated_dn"]
                )
                reconstructed_features.append(
                    (
                        dn.astype(np.float32)
                        + np.float32(product["boa_offsets"][band])
                    )
                    / np.float32(product["boa_quantification_value"])
                )
            scl_arrays.append(
                _read_source_patch(
                    archive,
                    product["members"]["SCL"],
                    patch_transform,
                    "uint8",
                )
            )
        expected_valid = (
            numeric_valid
            & np.logical_and.reduce(
                [np.isin(scl, ELIGIBLE_SCL) for scl in scl_arrays]
            )
            & _registration_patch(
                _registration_for_event(report, event_id),
                event_state.shape,
                window,
            )
        )
        expected_features = np.stack(reconstructed_features).astype(np.float32)
        expected_features[:, ~expected_valid] = np.nan
        if not np.array_equal(valid, expected_valid):
            raise DatasetQaError(
                f"input-valid reconstruction drift: {patch['patch_id']}"
            )
        if not np.array_equal(features, expected_features, equal_nan=True):
            raise DatasetQaError(
                f"feature reconstruction drift: {patch['patch_id']}"
            )
        reconstructed += 1
        core_counts[patch["class"]] += int(loss.sum())
        unknown_pixels += int(np.count_nonzero(state == 2))
        feature_digest = _sha256_file(patch_root / "features.npy")
        if feature_digest in feature_hashes:
            raise DatasetQaError("exact duplicate feature array")
        feature_hashes.add(feature_digest)
        patch_bounds.append(
            (patch["patch_id"], patch["split_role"], _patch_bounds(patch))
        )
        if patch["split_role"] == "train":
            train_features.append(features)
            train_valid.append(valid)
        if patch["split_role"] in {"train", "validation"}:
            render_arrays[patch["patch_id"]] = {
                "features": features,
                "state": state,
                "valid": valid,
            }
    cross_role_overlaps = []
    for index, first in enumerate(patch_bounds):
        for second in patch_bounds[index + 1 :]:
            if first[1] != second[1] and _intersects(first[2], second[2]):
                cross_role_overlaps.append([first[0], second[0]])
    if cross_role_overlaps:
        raise DatasetQaError("cross-role patch footprint overlap")
    for first_role, first_ids in source_ids_by_role.items():
        for second_role, second_ids in source_ids_by_role.items():
            if first_role < second_role and first_ids & second_ids:
                raise DatasetQaError("source product crosses split roles")
    if (
        reconstructed != 12
        or file_bindings != 48
        or core_counts != {"background": 140, "burned": 147}
        or unknown_pixels != 531
        or len(render_arrays) != 8
    ):
        raise DatasetQaError("independent dataset inventory drift")
    normalization = _normalization(
        train_features,
        train_valid,
        contract["input_contract"]["channel_order"],
    )
    report = {
        "report_version": REPORT_VERSION,
        "report_id": REPORT_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "unit_id": UNIT_ID,
        "git_source_commit": git_source_commit,
        "software_version": __version__,
        "inputs": {
            "dataset_manifest": _binding(root, DATASET_MANIFEST_PATH),
            "dataset_contract": _binding(root, CONTRACT_PATH),
            "whole_event_split": _binding(root, SPLIT_PATH),
            "dataset_candidate": _binding(root, CANDIDATE_PATH),
        },
        "independence": (
            "This QA does not import the materializer. It independently "
            "reopens registrations, provider archives, candidate rasters, "
            "dataset arrays, and split metadata."
        ),
        "gates": {
            "exact_dataset_file_bindings": "pass: 48 of 48 patch files",
            "archive_custody": (
                "pass: 12 single-link archives / 13,633,040,965 bytes"
            ),
            "source_to_patch_reconstruction": "pass: 12 of 12 patches",
            "array_schema_and_domains": "pass",
            "core_and_unknown_counts": "pass: 287 core / 531 unknown",
            "exact_duplicate_features": "pass: zero",
            "cross_role_spatial_overlap": "pass: zero",
            "cross_role_source_product_overlap": "pass: zero",
            "train_only_normalization": "pass",
            "render_scope": "pass: train and validation only; test not rendered",
        },
        "inventory": {
            "event_groups": 6,
            "patches": 12,
            "reconstructed_patches": reconstructed,
            "verified_patch_files": file_bindings,
            "core_pixels": dict(sorted(core_counts.items())),
            "total_core_pixels": sum(core_counts.values()),
            "unknown_ring_pixels": unknown_pixels,
            "train_normalization_pixels_per_channel": normalization["channels"][
                0
            ]["eligible_pixel_count"],
            "rendered_patches": len(render_arrays),
            "rendered_roles": ["train", "validation"],
            "test_rendered": False,
            "test_analytical_open_count": 0,
        },
        "normalization": normalization,
        "limitations": [
            "Only two events and 109 labeled core pixels are available for training.",
            "Validation and test each contain only two event groups.",
            "Integrity-only test reconstruction emitted no test statistics or images and does not count as an analytical test opening.",
            "Exact source/group separation cannot establish geographic or population representativeness.",
            "Owner-approved prototype labels are not independent ground truth.",
        ],
        "decision": "PASS_INDEPENDENT_DATASET_QA_AUTHORIZE_BASELINE_PREREGISTRATION_ONLY",
        "boundaries": {
            "dataset_qa_passed": True,
            "normalization_statistics_created": True,
            "test_analytical_open_count": 0,
            "baseline_created": False,
            "model_created": False,
            "metric_result_created": False,
            "training_authorized": False,
            "independent_ground_truth_claimed": False,
            "generalization_claimed": False,
        },
        "next_dependency": "P2O5-T03-U05",
        "warning": WARNING,
    }
    normalization_output = {
        **normalization,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "unit_id": UNIT_ID,
        "git_source_commit": git_source_commit,
        "software_version": __version__,
        "dataset_manifest_sha256": DATASET_MANIFEST_SHA256,
        "split_manifest_sha256": SPLIT_SHA256,
        "training_event_group_ids": split["selection"]["roles"]["train"][
            "event_group_ids"
        ],
        "boundaries": {
            "validation_pixels_used": False,
            "test_pixels_used": False,
            "baseline_created": False,
            "model_created": False,
            "training_authorized": False,
        },
    }
    return report, normalization_output, render_arrays


def _font(size: int) -> ImageFont.ImageFont:
    candidates = (
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
    )
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def _false_color(features: np.ndarray, offset: int) -> Image.Image:
    rgb = np.stack(
        [features[offset + 2], features[offset + 1], features[offset]],
        axis=-1,
    )
    rgb = np.nan_to_num(rgb, nan=0.0, posinf=0.5, neginf=0.0)
    rgb = np.clip(rgb / 0.5, 0.0, 1.0)
    return Image.fromarray((rgb * 255).astype(np.uint8), mode="RGB").resize(
        (160, 160), Image.Resampling.NEAREST
    )


def _state_image(state: np.ndarray) -> Image.Image:
    colors = np.zeros((64, 64, 3), dtype=np.uint8)
    colors[state == 0] = (20, 160, 145)
    colors[state == 1] = (240, 90, 40)
    colors[state == 2] = (235, 190, 80)
    colors[state == 255] = (28, 34, 40)
    return Image.fromarray(colors, mode="RGB").resize(
        (160, 160), Image.Resampling.NEAREST
    )


def _valid_image(valid: np.ndarray) -> Image.Image:
    values = np.where(valid, 220, 25).astype(np.uint8)
    return Image.fromarray(values, mode="L").convert("RGB").resize(
        (160, 160), Image.Resampling.NEAREST
    )


def render_png(
    report: dict[str, Any],
    render_arrays: dict[str, dict[str, np.ndarray]],
    path: Path,
) -> None:
    width, height = 1800, 1240
    image = Image.new("RGB", (width, height), (244, 241, 232))
    draw = ImageDraw.Draw(image)
    title_font = _font(42)
    section_font = _font(25)
    body_font = _font(17)
    small_font = _font(14)
    draw.text((50, 35), "BurnLens dataset QA", fill=(20, 35, 46), font=title_font)
    draw.text(
        (50, 92),
        "Independent reconstruction · train-only statistics · test not rendered",
        fill=(65, 75, 82),
        font=section_font,
    )
    metrics = (
        ("12", "patches reconstructed"),
        ("287", "core pixels"),
        ("531", "unknown pixels"),
        ("0", "test analytical opens"),
    )
    for index, (value, label) in enumerate(metrics):
        x = 50 + index * 430
        draw.rounded_rectangle(
            (x, 140, x + 390, 220), radius=12, fill=(255, 255, 255)
        )
        draw.text((x + 18, 150), value, fill=(20, 115, 105), font=section_font)
        draw.text((x + 105, 158), label, fill=(48, 58, 64), font=body_font)
    items = sorted(render_arrays.items())
    for index, (patch_id, arrays) in enumerate(items):
        row, column = divmod(index, 2)
        x = 50 + column * 875
        y = 250 + row * 235
        draw.rounded_rectangle(
            (x, y, x + 825, y + 210), radius=12, fill=(255, 255, 255)
        )
        label = patch_id.replace("--", " · ")
        draw.text((x + 14, y + 10), label, fill=(28, 40, 48), font=small_font)
        tiles = (
            ("pre false color", _false_color(arrays["features"], 0)),
            ("post false color", _false_color(arrays["features"], 3)),
            ("state", _state_image(arrays["state"])),
            ("valid", _valid_image(arrays["valid"])),
        )
        for tile_index, (tile_label, tile) in enumerate(tiles):
            tile_x = x + 14 + tile_index * 200
            image.paste(tile, (tile_x, y + 38))
            draw.text(
                (tile_x, y + 180),
                tile_label,
                fill=(65, 75, 82),
                font=small_font,
            )
    draw.text(
        (50, 1200),
        (
            "Fixed display only: B12/B8A/B04 false color at 0–0.5 reflectance. "
            "Not model preprocessing. Test patches are excluded from this render."
        ),
        fill=(80, 70, 62),
        font=body_font,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], png_name: str) -> str:
    channels = "".join(
        (
            f"<tr><td>{escape(item['channel'])}</td>"
            f"<td>{item['eligible_pixel_count']:,}</td>"
            f"<td>{item['mean']:.6f}</td>"
            f"<td>{item['population_std']:.6f}</td></tr>"
        )
        for item in report["normalization"]["channels"]
    )
    gates = "".join(
        f"<tr><th scope='row'>{escape(key.replace('_', ' '))}</th>"
        f"<td>{escape(value)}</td></tr>"
        for key, value in report["gates"].items()
    )
    limits = "".join(
        f"<li>{escape(item)}</li>" for item in report["limitations"]
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens dataset QA</title>
<style>
:root{{--ink:#17242c;--muted:#58636a;--paper:#f4f1e8;--card:#fff;--teal:#147f75;--orange:#df5f32;--line:#d6d0c2}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 Arial,sans-serif}}
main{{max-width:1180px;margin:auto;padding:42px 24px 72px}}h1{{font-size:clamp(2rem,5vw,4.2rem);line-height:1;margin:.2em 0}}h2{{margin-top:2.2rem}}
.warn,.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;margin:18px 0}}.warn{{border-left:7px solid var(--orange)}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}}.metric strong{{display:block;font-size:2.2rem;color:var(--teal)}}img{{display:block;width:100%;height:auto;border:1px solid var(--line);border-radius:14px;background:#fff}}
.table{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;min-width:650px}}th,td{{text-align:left;padding:10px;border-bottom:1px solid var(--line)}}code{{overflow-wrap:anywhere}}
@media(max-width:760px){{.grid{{grid-template-columns:repeat(2,1fr)}}main{{padding:24px 14px 50px}}}}
</style></head><body><main>
<p>BURNLENS / PHASE TWO / ISSUE #{TASK_ISSUE} / U04</p>
<h1>Every dataset patch reconstructs; test analysis remains sealed.</h1>
<div class="warn">{escape(report['warning'])}</div>
<div class="grid">
<div class="card metric"><strong>12/12</strong>patches reconstructed</div>
<div class="card metric"><strong>287</strong>accepted core pixels</div>
<div class="card metric"><strong>531</strong>unknown-ring pixels</div>
<div class="card metric"><strong>0</strong>test analytical opens</div>
</div>
<h2>Rendered train and validation evidence</h2>
<p>The figure uses fixed false-color display scaling. It is not preprocessing. Test patches are not rendered.</p>
<img src="{escape(png_name)}" width="1800" height="1240" alt="Eight BurnLens train and validation patches showing pre and post false color, label states, and input-valid masks">
<h2>Independent gates</h2><div class="card table"><table>{gates}</table></div>
<h2>Train-only normalization</h2><div class="card table"><table><thead><tr><th>Channel</th><th>Pixels</th><th>Mean</th><th>Population std</th></tr></thead><tbody>{channels}</tbody></table></div>
<h2>Limits and next gate</h2><div class="card"><ul>{limits}</ul>
<p><strong>{escape(report['decision'])}</strong></p>
<p>Only baseline preregistration may follow. Training remains unauthorized.</p></div>
<p>Trace: commit <code>{escape(report['git_source_commit'])}</code> · run <code>{escape(report['run_id'])}</code> · dataset <code>burnlens-dataset-v0.1.0</code> · split <code>burnlens-whole-event-split-v0.1.0</code> · model none.</p>
</main></body></html>
"""


def _write_new(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with path.open("xb") as handle:
            created = True
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        if path.read_bytes() != data:
            raise DatasetQaError(f"exact output readback failed: {path}")
    except Exception:
        if created and path.exists():
            path.unlink()
        raise


def write_outputs(
    root: Path,
    output_directory: Path,
    normalization_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Path]:
    report, normalization, render_arrays = build_report(
        root, generated_at_utc, run_id, git_source_commit
    )
    outputs = {
        "json": output_directory / f"{REPORT_ID}.json",
        "html": output_directory / f"{REPORT_ID}.html",
        "png": output_directory / f"{REPORT_ID}.png",
        "normalization": normalization_path,
    }
    _write_new(outputs["json"], _json_bytes(report))
    _write_new(
        outputs["html"],
        render_html(report, outputs["png"].name).encode("utf-8"),
    )
    if outputs["png"].exists():
        raise DatasetQaError("PNG output already exists")
    render_png(report, render_arrays, outputs["png"])
    _write_new(outputs["normalization"], _json_bytes(normalization))
    return outputs
