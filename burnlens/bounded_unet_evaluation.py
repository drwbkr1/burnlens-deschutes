"""Open the frozen BurnLens model test once and retain exact evaluation evidence."""

from __future__ import annotations

from hashlib import sha256
from html import escape
import io
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Iterable

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import torch
import torch.nn.functional as functional

from burnlens.bounded_unet import (
    BoundedUNet,
    BoundedUNetError,
    ModelExample,
    configure_deterministic_execution,
    load_model_examples,
    require_finite,
)
from burnlens.bounded_unet_training import load_model_weights
from burnlens.unet_experiment import (
    DATASET_MANIFEST_PATH,
    TEST_AUTHORIZATION_DIRECTORY,
    TEST_AUTHORIZATION_VERSION,
    TEST_EVENT_IDS,
    TEST_OPENING_UNIT,
    _test_roster,
    load_test_access_grant,
)


EVALUATION_VERSION = "burnlens-bounded-unet-test-evaluation-v0.1.0"
EVALUATION_ID = "BOUNDED-UNET-TEST-EVALUATION-2026-001"
OPENING_RECEIPT_ID = "BOUNDED-UNET-TEST-OPENING-RECEIPT-2026-001"
MODEL_VERSION = "burnlens-unet-binary-v0.1.0"
DATASET_VERSION = "burnlens-dataset-v0.1.0"
SPLIT_VERSION = "burnlens-whole-event-split-v0.1.0"
BASELINE_VERSION = "burnlens-baseline-v0.1.0"
LABEL_SCHEMA_VERSION = "burn-scar-binary-region-label-schema-v0.3.0"
MODEL_DIRECTORY = Path("samples/models") / MODEL_VERSION
CONFIG_PATH = MODEL_DIRECTORY / "TRAINING-CONFIG-2026-001.json"
CONFIG_SHA256 = "1f939540e23a331a7814113a02f4ad7f148197dfa294990617ad62a01d1b003b"
WEIGHTS_PATH = MODEL_DIRECTORY / f"{MODEL_VERSION}.pt"
WEIGHTS_SHA256 = "703d92577e2b82a4cfdec0c5e43b8d7a064253483de4ccea909209f54b802334"
SELECTION_PATH = MODEL_DIRECTORY / "CHECKPOINT-SELECTION-2026-001.json"
SELECTION_SHA256 = "6dcae9af8d1a27c97a77ea90afaceaa8b0eee15cf3cfe207818380ef5e1db0c4"
TRAINING_REPORT_PATH = MODEL_DIRECTORY / "BOUNDED-UNET-TRAINING-2026-001.json"
TRAINING_REPORT_SHA256 = (
    "53a454bd082314c33e8249fdc98c62f89e7c0bb6ecc35d800dfa4f15df1fdf57"
)
ENVIRONMENT_CAPTURE_SHA256 = (
    "009effea6c4b17b884c8d4e66ad51b4981c18ebfa1aed1b332391b1be8524e36"
)
BASELINE_PATH = Path(
    "samples/baselines/burnlens-baseline-v0.1.0/"
    "BASELINE-EVALUATION-2026-001.json"
)
BASELINE_SHA256 = (
    "a8ba82f999a87a8114c7fc417126b96c1f031e7eb9e24311df20fe32d7edb221"
)
NORMALIZATION_PATH = Path(
    "records/phase-two/manifests/TRAIN-NORMALIZATION-2026-001.json"
)
ENVIRONMENT_CAPTURE_PATH = Path(
    "records/phase-three/environments/"
    "MODEL-ENVIRONMENT-CAPTURE-2026-001.json"
)
NORMALIZATION_SHA256 = (
    "6344861677753e9c96840f47e7a038a15f12a0c29759285c073f5cc6ea4bc255"
)
THRESHOLD = 0.5
DIAGNOSTIC_THRESHOLDS = (0.25, 0.5, 0.75)
PIXEL_AREA_M2 = 400.0
OUTPUT_DIRECTORY = Path(
    "samples/evaluation/phase-three/bounded-unet-test-v0.1.0"
)
RUN_DIRECTORY_ROOT = Path("runs/phase-three")
_COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class BoundedUNetEvaluationError(BoundedUNetError):
    """A frozen-candidate, opening, metric, render, or promotion failure."""


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BoundedUNetEvaluationError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise BoundedUNetEvaluationError(f"JSON object required: {path}")
    return value


def _identity(root: Path, relative: Path, expected_sha256: str) -> dict[str, Any]:
    path = root / relative
    if not path.is_file():
        raise BoundedUNetEvaluationError(f"bound input is absent: {relative}")
    digest = _sha256_file(path)
    if digest != expected_sha256:
        raise BoundedUNetEvaluationError(f"bound input drift: {relative}")
    return {
        "path": relative.as_posix(),
        "bytes": path.stat().st_size,
        "sha256": digest,
    }


def _write_new(path: Path, payload: bytes) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise BoundedUNetEvaluationError(f"refusing to overwrite: {path}")
    path.write_bytes(payload)
    if path.read_bytes() != payload:
        raise BoundedUNetEvaluationError(f"written bytes differ: {path}")
    return {
        "path": path.as_posix(),
        "bytes": len(payload),
        "sha256": sha256(payload).hexdigest(),
    }


def _npy_bytes(value: np.ndarray) -> bytes:
    buffer = io.BytesIO()
    np.save(buffer, value, allow_pickle=False)
    return buffer.getvalue()


def _ensure_finite(value: Any, label: str = "value") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            _ensure_finite(item, f"{label}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _ensure_finite(item, f"{label}[{index}]")
    elif isinstance(value, float) and not math.isfinite(value):
        raise BoundedUNetEvaluationError(f"nonfinite {label}")


def _require_exact_git_source(root: Path, git_source_commit: str) -> None:
    if not _COMMIT_PATTERN.fullmatch(git_source_commit):
        raise BoundedUNetEvaluationError("git source commit is invalid")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if head != git_source_commit:
        raise BoundedUNetEvaluationError("git source commit differs from HEAD")
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status:
        raise BoundedUNetEvaluationError(
            "working tree must be clean before the sealed-test opening"
        )


def _assert_opening_unused(root: Path, opening_id: str) -> None:
    for path in sorted((root / RUN_DIRECTORY_ROOT).glob("*/OPENING-CONSUMED.json")):
        value = _read_json(path)
        if value.get("opening_id") == opening_id:
            raise BoundedUNetEvaluationError(
                "test authorization was already consumed; retry is prohibited"
            )
    tracked_receipt = (
        root / OUTPUT_DIRECTORY / f"{OPENING_RECEIPT_ID}.json"
    )
    if tracked_receipt.is_file():
        value = _read_json(tracked_receipt)
        if value.get("opening", {}).get("opening_id") == opening_id:
            raise BoundedUNetEvaluationError(
                "test authorization was already consumed; retry is prohibited"
            )


def _candidate_bindings(root: Path) -> dict[str, dict[str, Any]]:
    bindings = {
        "config": _identity(root, CONFIG_PATH, CONFIG_SHA256),
        "weights": _identity(root, WEIGHTS_PATH, WEIGHTS_SHA256),
        "selection": _identity(root, SELECTION_PATH, SELECTION_SHA256),
        "training_report": _identity(
            root, TRAINING_REPORT_PATH, TRAINING_REPORT_SHA256
        ),
        "environment_capture": _identity(
            root, ENVIRONMENT_CAPTURE_PATH, ENVIRONMENT_CAPTURE_SHA256
        ),
        "baseline": _identity(root, BASELINE_PATH, BASELINE_SHA256),
        "normalization": _identity(
            root, NORMALIZATION_PATH, NORMALIZATION_SHA256
        ),
    }
    config = _read_json(root / CONFIG_PATH)
    selection = _read_json(root / SELECTION_PATH)
    report = _read_json(root / TRAINING_REPORT_PATH)
    if config.get("model_version_candidate") != MODEL_VERSION:
        raise BoundedUNetEvaluationError("candidate config model version drift")
    if config.get("boundaries", {}).get("test_arrays_opened") is not False:
        raise BoundedUNetEvaluationError("candidate config test boundary drift")
    if selection.get("selected_epoch") != 10:
        raise BoundedUNetEvaluationError("selected epoch drift")
    if selection.get("test_arrays_opened") is not False:
        raise BoundedUNetEvaluationError("selection test boundary drift")
    if selection.get("weights", {}).get("sha256") != WEIGHTS_SHA256:
        raise BoundedUNetEvaluationError("selection weights binding drift")
    if report.get("disposition") != "candidate-frozen-pending-one-test-opening":
        raise BoundedUNetEvaluationError("training candidate disposition drift")
    if report.get("boundaries", {}).get("test_open_count") != 0:
        raise BoundedUNetEvaluationError("training report test-open count drift")
    return bindings


def build_test_authorization(
    root: Path,
    output_path: Path,
    opening_id: str,
) -> dict[str, Any]:
    """Write the exact metadata-only U05 authorization without opening arrays."""

    bindings = _candidate_bindings(root)
    resolved = output_path.resolve()
    expected_parent = (root / TEST_AUTHORIZATION_DIRECTORY).resolve()
    if resolved.parent != expected_parent:
        raise BoundedUNetEvaluationError(
            "test authorization is outside the frozen directory"
        )
    if not opening_id.startswith("TEST-OPEN-"):
        raise BoundedUNetEvaluationError("test opening ID is invalid")
    manifest_identity = _identity(
        root,
        DATASET_MANIFEST_PATH,
        "e0b7ac666a70e96f979c386a9d503ad45ed0baea8f21e3838ba4530d5e3d2d16",
    )
    del manifest_identity
    roster = _test_roster(_read_json(root / DATASET_MANIFEST_PATH))
    authorization = {
        "authorization_version": TEST_AUTHORIZATION_VERSION,
        "opening_id": opening_id,
        "authorization_unit": TEST_OPENING_UNIT,
        "status": "AUTHORIZED_NOT_OPENED",
        "open_count_before": 0,
        "open_count_authorized": 1,
        "config_sha256": bindings["config"]["sha256"],
        "weights_sha256": bindings["weights"]["sha256"],
        "selection_sha256": bindings["selection"]["sha256"],
        "environment_capture_sha256": bindings["environment_capture"]["sha256"],
        "test_event_group_ids": list(TEST_EVENT_IDS),
        "test_patch_ids": [item["patch_id"] for item in roster],
    }
    return _write_new(resolved, _json_bytes(authorization))


def _class_metrics(
    truth: np.ndarray,
    predicted: np.ndarray,
    class_value: int,
) -> dict[str, Any]:
    truth_class = truth == class_value
    predicted_class = predicted == class_value
    tp = int(np.count_nonzero(truth_class & predicted_class))
    fp = int(np.count_nonzero(~truth_class & predicted_class))
    fn = int(np.count_nonzero(truth_class & ~predicted_class))
    support = int(np.count_nonzero(truth_class))
    predicted_count = int(np.count_nonzero(predicted_class))
    dice_denominator = 2 * tp + fp + fn
    iou_denominator = tp + fp + fn
    precision_denominator = tp + fp
    recall_denominator = tp + fn
    return {
        "class": "burned" if class_value == 1 else "background",
        "support": support,
        "predicted": predicted_count,
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "dice_denominator": dice_denominator,
        "iou_denominator": iou_denominator,
        "precision_denominator": precision_denominator,
        "recall_denominator": recall_denominator,
        "dice": 1.0 if dice_denominator == 0 else (2 * tp) / dice_denominator,
        "iou": 1.0 if iou_denominator == 0 else tp / iou_denominator,
        "precision": None if precision_denominator == 0 else tp / precision_denominator,
        "recall": None if recall_denominator == 0 else tp / recall_denominator,
    }


def _metric_block(
    logits: np.ndarray,
    probabilities: np.ndarray,
    truth: np.ndarray,
    threshold: float,
) -> dict[str, Any]:
    if (
        logits.ndim != 1
        or probabilities.shape != logits.shape
        or truth.shape != logits.shape
        or logits.size == 0
    ):
        raise BoundedUNetEvaluationError("metric vector schema drift")
    if not (
        np.isfinite(logits).all()
        and np.isfinite(probabilities).all()
        and np.isin(truth, np.array([0, 1], dtype=np.uint8)).all()
    ):
        raise BoundedUNetEvaluationError("metric vector is nonfinite or nonbinary")
    predicted = (probabilities >= threshold).astype(np.uint8)
    classes = [_class_metrics(truth, predicted, value) for value in (0, 1)]
    tensor_logits = torch.from_numpy(logits.astype(np.float32, copy=False))
    tensor_truth = torch.from_numpy(truth.astype(np.float32, copy=False))
    bce = float(
        functional.binary_cross_entropy_with_logits(
            tensor_logits, tensor_truth, reduction="mean"
        ).item()
    )
    true_burned = int(np.count_nonzero(truth == 1))
    predicted_burned = int(np.count_nonzero(predicted == 1))
    signed_difference = predicted_burned - true_burned
    return {
        "threshold": threshold,
        "core_pixels": int(truth.size),
        "true_burned_pixels": true_burned,
        "predicted_burned_pixels": predicted_burned,
        "masked_bce": bce,
        "classes": classes,
        "class_macro_dice": float(np.mean([item["dice"] for item in classes])),
        "class_macro_iou": float(np.mean([item["iou"] for item in classes])),
        "area_difference": {
            "scope": "selected prototype cores only",
            "pixel_area_m2": PIXEL_AREA_M2,
            "signed_pixels": signed_difference,
            "absolute_pixels": abs(signed_difference),
            "signed_m2": signed_difference * PIXEL_AREA_M2,
            "absolute_m2": abs(signed_difference) * PIXEL_AREA_M2,
            "relative_to_true_burned": (
                None
                if true_burned == 0
                else signed_difference / true_burned
            ),
        },
    }


def _calibration(probabilities: np.ndarray, truth: np.ndarray) -> dict[str, Any]:
    edges = np.linspace(0.0, 1.0, 11)
    assignments = np.digitize(probabilities, edges[1:-1], right=False)
    rows: list[dict[str, Any]] = []
    expected_calibration_error = 0.0
    for index in range(10):
        selected = assignments == index
        count = int(np.count_nonzero(selected))
        mean_probability = (
            None if count == 0 else float(np.mean(probabilities[selected]))
        )
        observed_fraction = (
            None if count == 0 else float(np.mean(truth[selected]))
        )
        if count:
            expected_calibration_error += (
                count
                / probabilities.size
                * abs(mean_probability - observed_fraction)
            )
        rows.append(
            {
                "lower_inclusive": float(edges[index]),
                "upper_inclusive_if_final_else_exclusive": float(edges[index + 1]),
                "count": count,
                "mean_probability": mean_probability,
                "observed_burned_fraction": observed_fraction,
            }
        )
    return {
        "status": "descriptive-only-not-calibrated",
        "method": "ten fixed-width bins over selected prototype cores",
        "core_pixels": int(probabilities.size),
        "brier_score": float(np.mean((probabilities - truth) ** 2)),
        "expected_calibration_error": float(expected_calibration_error),
        "bins": rows,
        "limitations": (
            "Two event groups and 89 prototype cores cannot support a calibrated "
            "probability or population-calibration claim."
        ),
    }


def evaluate_examples(
    model: BoundedUNet,
    examples: Iterable[ModelExample],
) -> tuple[dict[str, Any], dict[str, dict[str, np.ndarray]]]:
    """Evaluate an already authorized roster without changing frozen choices."""

    roster = list(examples)
    if not roster:
        raise BoundedUNetEvaluationError("evaluation roster is empty")
    model.eval()
    patch_arrays: dict[str, dict[str, np.ndarray]] = {}
    with torch.no_grad():
        for example in roster:
            inputs = example.inputs.unsqueeze(0)
            logits_tensor = model(inputs)
            require_finite(logits_tensor, f"logits[{example.patch_id}]")
            probabilities_tensor = torch.sigmoid(logits_tensor)
            require_finite(probabilities_tensor, f"probabilities[{example.patch_id}]")
            patch_arrays[example.patch_id] = {
                "logits": logits_tensor[0, 0].cpu().numpy().astype(np.float32),
                "probability": probabilities_tensor[0, 0]
                .cpu()
                .numpy()
                .astype(np.float32),
                "prediction": (
                    probabilities_tensor[0, 0].cpu().numpy() >= THRESHOLD
                ).astype(np.uint8),
                "truth": example.target[0].cpu().numpy().astype(np.uint8),
                "loss_mask": example.loss_mask[0].cpu().numpy().astype(bool),
                "input_valid": example.input_valid[0].cpu().numpy().astype(bool),
            }

    events: list[dict[str, Any]] = []
    pooled_logits: list[np.ndarray] = []
    pooled_probabilities: list[np.ndarray] = []
    pooled_truth: list[np.ndarray] = []
    for event_id in sorted({item.event_group_id for item in roster}):
        event_examples = [item for item in roster if item.event_group_id == event_id]
        event_logits: list[np.ndarray] = []
        event_probabilities: list[np.ndarray] = []
        event_truth: list[np.ndarray] = []
        for example in event_examples:
            arrays = patch_arrays[example.patch_id]
            mask = arrays["loss_mask"]
            event_logits.append(arrays["logits"][mask])
            event_probabilities.append(arrays["probability"][mask])
            event_truth.append(arrays["truth"][mask])
        logits = np.concatenate(event_logits)
        probabilities = np.concatenate(event_probabilities)
        truth = np.concatenate(event_truth)
        metrics = _metric_block(logits, probabilities, truth, THRESHOLD)
        events.append(
            {
                "event_group_id": event_id,
                "patch_count": len(event_examples),
                **metrics,
            }
        )
        pooled_logits.append(logits)
        pooled_probabilities.append(probabilities)
        pooled_truth.append(truth)

    all_logits = np.concatenate(pooled_logits)
    all_probabilities = np.concatenate(pooled_probabilities)
    all_truth = np.concatenate(pooled_truth)
    pooled = _metric_block(
        all_logits, all_probabilities, all_truth, THRESHOLD
    )
    event_class_rows = [
        item for event in events for item in event["classes"]
    ]
    threshold_sensitivity: list[dict[str, Any]] = []
    for diagnostic_threshold in DIAGNOSTIC_THRESHOLDS:
        block = _metric_block(
            all_logits,
            all_probabilities,
            all_truth,
            diagnostic_threshold,
        )
        threshold_sensitivity.append(
            {
                "threshold": diagnostic_threshold,
                "status": (
                    "frozen-operating-threshold"
                    if diagnostic_threshold == THRESHOLD
                    else "diagnostic-only-no-selection-or-retuning"
                ),
                "core_pixels": block["core_pixels"],
                "predicted_burned_pixels": block["predicted_burned_pixels"],
                "class_macro_dice": block["class_macro_dice"],
                "class_macro_iou": block["class_macro_iou"],
                "area_difference": block["area_difference"],
            }
        )
    result = {
        "event_count": len(events),
        "core_pixels": pooled["core_pixels"],
        "threshold": THRESHOLD,
        "masked_bce": pooled["masked_bce"],
        "true_burned_pixels": pooled["true_burned_pixels"],
        "predicted_burned_pixels": pooled["predicted_burned_pixels"],
        "event_class_macro_dice": float(
            np.mean([item["dice"] for item in event_class_rows])
        ),
        "event_class_macro_iou": float(
            np.mean([item["iou"] for item in event_class_rows])
        ),
        "worst_event_macro_dice": min(
            event["class_macro_dice"] for event in events
        ),
        "event_macro_dice_range": [
            min(event["class_macro_dice"] for event in events),
            max(event["class_macro_dice"] for event in events),
        ],
        "event_macro_iou_range": [
            min(event["class_macro_iou"] for event in events),
            max(event["class_macro_iou"] for event in events),
        ],
        "pooled_classes": pooled["classes"],
        "pooled_area_difference": pooled["area_difference"],
        "events": events,
        "threshold_sensitivity": threshold_sensitivity,
        "probability_calibration": _calibration(all_probabilities, all_truth),
    }
    _ensure_finite(result)
    return result, patch_arrays


def _patch_metadata(root: Path) -> dict[str, dict[str, Any]]:
    manifest = _read_json(root / DATASET_MANIFEST_PATH)
    metadata: dict[str, dict[str, Any]] = {}
    for item in manifest.get("patches", []):
        if item.get("split_role") != "test":
            continue
        transform = item.get("transform")
        if (
            not isinstance(transform, list)
            or len(transform) != 6
            or transform[0] != 20.0
            or transform[4] != -20.0
        ):
            raise BoundedUNetEvaluationError("test patch transform drift")
        metadata[item["patch_id"]] = {
            "patch_id": item["patch_id"],
            "event_group_id": item["event_group_id"],
            "candidate_id": item["candidate_id"],
            "proposed_class": item["class"],
            "crs": item["crs"],
            "transform": transform,
            "window": item["window"],
            "core_pixels": item["core_pixels"],
            "unknown_ring_pixels_in_patch": item["unknown_ring_pixels_in_patch"],
            "input_valid_pixels": item["input_valid_pixels"],
            "source_members": item["source_members"],
        }
    if len(metadata) != 4:
        raise BoundedUNetEvaluationError("test patch metadata roster drift")
    return metadata


def _normalization(root: Path) -> tuple[np.ndarray, np.ndarray]:
    value = _read_json(root / NORMALIZATION_PATH)
    channels = value.get("channels")
    if not isinstance(channels, list) or len(channels) != 6:
        raise BoundedUNetEvaluationError("normalization schema drift")
    means = np.array([item["mean"] for item in channels], dtype=np.float32)
    stds = np.array(
        [max(float(item["population_std"]), 1e-6) for item in channels],
        dtype=np.float32,
    )
    return means, stds


def _raw_features(
    example: ModelExample,
    means: np.ndarray,
    stds: np.ndarray,
) -> np.ndarray:
    normalized = example.inputs.cpu().numpy()
    raw = normalized * stds[:, None, None] + means[:, None, None]
    raw[:, ~example.input_valid[0].cpu().numpy().astype(bool)] = np.nan
    return raw


def _false_color(features: np.ndarray, start: int) -> Image.Image:
    rgb = np.stack(
        [features[start + 2], features[start + 1], features[start]], axis=-1
    )
    finite = np.isfinite(rgb).all(axis=-1)
    display = np.full((*finite.shape, 3), (218, 213, 201), dtype=np.uint8)
    display[finite] = (
        np.clip(rgb[finite] / 0.5, 0.0, 1.0) * 255.0
    ).astype(np.uint8)
    return Image.fromarray(display, mode="RGB").resize(
        (160, 160), resample=Image.Resampling.NEAREST
    )


def _probability_image(
    probabilities: np.ndarray,
    input_valid: np.ndarray,
) -> Image.Image:
    rgb = np.full((*probabilities.shape, 3), (218, 213, 201), dtype=np.uint8)
    valid = input_valid & np.isfinite(probabilities)
    values = np.clip(probabilities[valid], 0.0, 1.0)
    rgb[valid, 0] = (35 + 210 * values).astype(np.uint8)
    rgb[valid, 1] = (95 + 55 * (1.0 - np.abs(values - 0.5) * 2)).astype(
        np.uint8
    )
    rgb[valid, 2] = (220 - 185 * values).astype(np.uint8)
    return Image.fromarray(rgb, mode="RGB").resize(
        (160, 160), resample=Image.Resampling.NEAREST
    )


def _label_image(truth: np.ndarray, mask: np.ndarray) -> Image.Image:
    rgb = np.full((*truth.shape, 3), (218, 213, 201), dtype=np.uint8)
    rgb[mask & (truth == 0)] = (40, 120, 155)
    rgb[mask & (truth == 1)] = (215, 75, 45)
    return Image.fromarray(rgb, mode="RGB").resize(
        (160, 160), resample=Image.Resampling.NEAREST
    )


def _error_image(
    prediction: np.ndarray,
    truth: np.ndarray,
    mask: np.ndarray,
) -> Image.Image:
    rgb = np.full((*truth.shape, 3), (218, 213, 201), dtype=np.uint8)
    rgb[mask & (prediction == truth)] = (35, 145, 115)
    rgb[mask & (prediction != truth)] = (225, 65, 70)
    return Image.fromarray(rgb, mode="RGB").resize(
        (160, 160), resample=Image.Resampling.NEAREST
    )


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ):
        if path.is_file():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def render_evaluation_png(
    report: dict[str, Any],
    examples: list[ModelExample],
    patch_arrays: dict[str, dict[str, np.ndarray]],
    means: np.ndarray,
    stds: np.ndarray,
) -> bytes:
    preflight = report.get("role") == "validation-only-preflight"
    image = Image.new("RGB", (2100, 1540), "#f4f0e8")
    draw = ImageDraw.Draw(image)
    dark = "#17211d"
    muted = "#5e6962"
    green = "#23634c"
    red = "#9a3e32"
    draw.rounded_rectangle((55, 45, 2045, 245), 28, fill=dark)
    draw.text(
        (105, 82),
        (
            "BurnLens U-Net evaluation preflight"
            if preflight
            else "BurnLens bounded U-Net test"
        ),
        font=_font(52),
        fill="white",
    )
    draw.text(
        (108, 162),
        (
            "Validation only • sealed test unopened • renderer and metrics rehearsal"
            if preflight
            else "One frozen opening • prototype cores • model candidate, not ground truth"
        ),
        font=_font(27),
        fill="#d8e4dd",
    )
    metrics = report["test_metrics"]
    cards = [
        ("Core pixels", str(metrics["core_pixels"])),
        ("Event-class Dice", f"{metrics['event_class_macro_dice']:.3f}"),
        ("Event-class IoU", f"{metrics['event_class_macro_iou']:.3f}"),
        ("Worst event Dice", f"{metrics['worst_event_macro_dice']:.3f}"),
    ]
    for index, (label, value) in enumerate(cards):
        left = 55 + index * 505
        draw.rounded_rectangle((left, 275, left + 475, 420), 20, fill="white")
        draw.text((left + 28, 300), label, font=_font(22), fill=muted)
        draw.text((left + 28, 340), value, font=_font(39), fill=green)
    labels = ("pre SWIR/NIR/red", "post SWIR/NIR/red", "P(burned)", "prototype core", "correct / error")
    for index, label in enumerate(labels):
        draw.text((70 + index * 395, 450), label, font=_font(18), fill=muted)
    patch_meta = report["patches"]
    for row, example in enumerate(examples):
        arrays = patch_arrays[example.patch_id]
        meta = patch_meta[example.patch_id]
        raw = _raw_features(example, means, stds)
        y = 490 + row * 235
        draw.rounded_rectangle((55, y, 2045, y + 220), 18, fill="white")
        tiles = (
            _false_color(raw, 0),
            _false_color(raw, 3),
            _probability_image(arrays["probability"], arrays["input_valid"]),
            _label_image(arrays["truth"], arrays["loss_mask"]),
            _error_image(
                arrays["prediction"], arrays["truth"], arrays["loss_mask"]
            ),
        )
        for index, tile in enumerate(tiles):
            image.paste(tile, (70 + index * 395, y + 18))
        transform = meta["transform"]
        east = transform[2] + transform[0] * 64
        south = transform[5] + transform[4] * 64
        truth_burned = int(
            np.count_nonzero(arrays["truth"][arrays["loss_mask"]] == 1)
        )
        predicted_burned = int(
            np.count_nonzero(arrays["prediction"][arrays["loss_mask"]] == 1)
        )
        annotation = (
            f"{meta['candidate_id']} · {meta['event_group_id']} · {meta['crs']} · "
            f"20 m · {transform[2]:.0f},{transform[5]:.0f} to {east:.0f},{south:.0f} · "
            f"core burned true/pred {truth_burned}/{predicted_burned}"
        )
        draw.text((70, y + 188), annotation, font=_font(15), fill=dark)
    draw.text(
        (60, 1490),
        (
            "Gray is excluded. Red is error only on owner-approved prototype cores. "
            "No complete-scar area, field validation, generalization, or operational claim."
        ),
        font=_font(20),
        fill=red,
    )
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=False)
    return buffer.getvalue()


def render_evaluation_html(report: dict[str, Any], image_name: str) -> bytes:
    preflight = report.get("role") == "validation-only-preflight"
    metrics = report["test_metrics"]
    baseline = report["baseline_comparison"]
    headline = (
        "The evaluation renderer rehearses without the test."
        if preflight
        else "The first U-Net meets the sealed test once."
    )
    warning = (
        "Validation-only preflight. Ward Creek and Windigo remain sealed; "
        "test-open count is zero. No displayed metric is a test result."
        if preflight
        else (
            "Prototype evidence, not ground truth. Owner-approved cores from "
            "two events do not establish field validity, generalization, "
            "complete-scar area, or operational readiness. This result cannot "
            "be retried or tuned."
        )
    )
    comparison = (
        "<strong>Baseline comparison: not applicable.</strong><br>"
        "This validation-only preflight exercises the frozen renderer and "
        "metric schema without a test opening or RBR test comparison."
        if preflight
        else (
            f"<strong>Baseline comparison: {escape(baseline['status'])}</strong><br>"
            "Frozen RBR Dice/IoU/worst-event: 1.0000 / 1.0000 / 1.0000. Model: "
            f"{metrics['event_class_macro_dice']:.4f} / "
            f"{metrics['event_class_macro_iou']:.4f} / "
            f"{metrics['worst_event_macro_dice']:.4f}. "
            "A valid trained result is not automatically added value."
        )
    )
    boundary = (
        "<p>Analytical test-open count: 0. This surface uses validation only. "
        "Ward Creek and Windigo remain sealed.</p>"
        "<p>No test metric, model acceptance, release, inference, or model-value "
        "claim exists.</p>"
        if preflight
        else (
            "<p>Analytical test-open count: 1. Candidate config, weights, "
            "selection, environment, roster, threshold, and code were frozen "
            "before opening. No model, threshold, or code retry is authorized.</p>"
            "<p>This is an evaluated model candidate, not an accepted or "
            "released model. U06 must reproduce it exactly and decide whether "
            "to package or reject it.</p>"
        )
    )
    image_alt = (
        "Four validation patches rehearsing pre and post false color, burned "
        "probability, prototype cores, and model errors without opening the test"
        if preflight
        else (
            "Four Ward Creek and Windigo test patches showing pre and post "
            "false color, burned probability, prototype cores, and model errors "
            "with CRS and extent annotations"
        )
    )
    event_rows = "".join(
        (
            f"<tr><td>{escape(event['event_group_id'])}</td>"
            f"<td>{event['core_pixels']}</td>"
            f"<td>{event['masked_bce']:.4f}</td>"
            f"<td>{event['class_macro_dice']:.4f}</td>"
            f"<td>{event['class_macro_iou']:.4f}</td>"
            f"<td>{event['area_difference']['signed_pixels']}</td></tr>"
        )
        for event in metrics["events"]
    )
    class_rows = "".join(
        (
            f"<tr><td>{escape(event['event_group_id'])}</td>"
            f"<td>{escape(item['class'])}</td><td>{item['support']}</td>"
            f"<td>{item['predicted']}</td><td>{item['true_positive']}</td>"
            f"<td>{item['false_positive']}</td><td>{item['false_negative']}</td>"
            f"<td>{item['dice_denominator']}</td>"
            f"<td>{item['iou_denominator']}</td>"
            f"<td>{item['dice']:.4f}</td><td>{item['iou']:.4f}</td>"
            f"<td>{'undefined' if item['precision'] is None else f'{item['precision']:.4f}'}</td>"
            f"<td>{'undefined' if item['recall'] is None else f'{item['recall']:.4f}'}</td></tr>"
        )
        for event in metrics["events"]
        for item in event["classes"]
    )
    threshold_rows = "".join(
        (
            f"<tr><td>{item['threshold']:.2f}</td>"
            f"<td>{escape(item['status'])}</td>"
            f"<td>{item['predicted_burned_pixels']}</td>"
            f"<td>{item['class_macro_dice']:.4f}</td>"
            f"<td>{item['class_macro_iou']:.4f}</td></tr>"
        )
        for item in metrics["threshold_sensitivity"]
    )
    patch_rows = "".join(
        (
            f"<tr><td>{escape(item['candidate_id'])}</td>"
            f"<td>{escape(item['event_group_id'])}</td>"
            f"<td>{escape(item['proposed_class'])}</td>"
            f"<td>{escape(item['crs'])}</td>"
            f"<td>{escape(str(item['transform']))}</td>"
            f"<td>{escape(str(item['window']))}</td></tr>"
        )
        for item in report["patches"].values()
    )
    calibration = metrics["probability_calibration"]
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens bounded U-Net test evaluation</title>
<style>
:root{{--ink:#17211d;--paper:#f4f0e8;--card:#fff;--green:#23634c;--red:#9a3e32;--line:#d5d0c4}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 Arial,sans-serif;overflow-x:hidden}}
main{{max-width:1180px;margin:auto;padding:42px 24px 72px}}h1{{font-size:clamp(2.2rem,6vw,4.5rem);line-height:1.02;margin:.2em 0}}h2{{margin-top:2.2rem}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;margin:18px 0;overflow-wrap:anywhere}}.warn{{border-left:7px solid var(--red)}}
.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}}.metric strong{{display:block;font-size:1.7rem;color:var(--green)}}
img{{display:block;width:100%;height:auto;border:1px solid var(--line);border-radius:14px;background:#fff}}
.table-wrap{{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:#fff}}table{{border-collapse:collapse;width:100%;min-width:760px}}
th,td{{text-align:left;padding:10px;border-bottom:1px solid var(--line);white-space:nowrap}}code{{overflow-wrap:anywhere}}a:focus{{outline:3px solid var(--green);outline-offset:3px}}
@media(max-width:600px){{main{{padding:24px 14px 50px}}}}
</style></head><body><main id="main">
<p>BURNLENS / PHASE THREE / ISSUE #566 / U05</p>
<h1>{escape(headline)}</h1>
<div class="card warn">{escape(warning)}</div>
<div class="metrics">
<div class="card metric">Event-class Dice<strong>{metrics['event_class_macro_dice']:.4f}</strong></div>
<div class="card metric">Event-class IoU<strong>{metrics['event_class_macro_iou']:.4f}</strong></div>
<div class="card metric">Worst event Dice<strong>{metrics['worst_event_macro_dice']:.4f}</strong></div>
<div class="card metric">Masked BCE<strong>{metrics['masked_bce']:.4f}</strong></div>
</div>
<div class="card">{comparison}</div>
<h2>Geospatially bound prediction and error evidence</h2>
<img src="{escape(image_name)}" width="2100" height="1540" alt="{escape(image_alt)}">
<h2>Event results</h2><div class="table-wrap"><table><thead><tr><th>Event</th><th>Cores</th><th>BCE</th><th>Macro Dice</th><th>Macro IoU</th><th>Area difference, pixels</th></tr></thead><tbody>{event_rows}</tbody></table></div>
<h2>Event and class denominators</h2><div class="table-wrap"><table><thead><tr><th>Event</th><th>Class</th><th>Support</th><th>Predicted</th><th>TP</th><th>FP</th><th>FN</th><th>Dice denominator</th><th>IoU denominator</th><th>Dice</th><th>IoU</th><th>Precision</th><th>Recall</th></tr></thead><tbody>{class_rows}</tbody></table></div>
<h2>Frozen threshold sensitivity</h2><div class="card"><p>0.25 and 0.75 are diagnostics only. The operating threshold remains 0.50; no selection or retuning is permitted.</p></div>
<div class="table-wrap"><table><thead><tr><th>Threshold</th><th>Status</th><th>Predicted burned</th><th>Macro Dice</th><th>Macro IoU</th></tr></thead><tbody>{threshold_rows}</tbody></table></div>
<h2>Probability status</h2><div class="card"><strong>{escape(calibration['status'])}</strong><br>
Brier score {calibration['brier_score']:.4f}; fixed-bin descriptive ECE {calibration['expected_calibration_error']:.4f}. {escape(calibration['limitations'])}</div>
<h2>Patch lineage</h2><div class="table-wrap"><table><thead><tr><th>Candidate</th><th>Event</th><th>Proposed class</th><th>CRS</th><th>Transform</th><th>Window</th></tr></thead><tbody>{patch_rows}</tbody></table></div>
<h2>Boundary</h2><div class="card">{boundary}</div>
<p>Trace: commit <code>{escape(report['git_source_commit'])}</code> · run <code>{escape(report['run_id'])}</code> · model <code>{MODEL_VERSION}</code> · dataset <code>{DATASET_VERSION}</code> · split <code>{SPLIT_VERSION}</code>.</p>
</main></body></html>
""".encode("utf-8")


def _promote_tree(source: Path, destination: Path) -> None:
    if destination.exists() or destination.is_symlink():
        raise BoundedUNetEvaluationError(
            f"evaluation destination already exists: {destination}"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = destination.with_name(f".{destination.name}.staging")
    if staging.exists() or staging.is_symlink():
        raise BoundedUNetEvaluationError(
            f"evaluation staging path already exists: {staging}"
        )
    shutil.copytree(source, staging)
    for original in sorted(path for path in source.rglob("*") if path.is_file()):
        relative = original.relative_to(source)
        copied = staging / relative
        if (
            copied.stat().st_size != original.stat().st_size
            or _sha256_file(copied) != _sha256_file(original)
        ):
            raise BoundedUNetEvaluationError(
                f"evaluation staging copy drift: {relative}"
            )
    os.replace(staging, destination)


def _baseline_comparison(root: Path, metrics: dict[str, Any]) -> dict[str, Any]:
    baseline = _read_json(root / BASELINE_PATH)["selected_test_metrics"]
    model_tuple = (
        metrics["event_class_macro_dice"],
        metrics["event_class_macro_iou"],
        metrics["worst_event_macro_dice"],
    )
    baseline_tuple = (
        baseline["event_class_macro_dice"],
        baseline["event_class_macro_iou"],
        baseline["worst_event_macro_dice"],
    )
    if model_tuple == baseline_tuple:
        status = "MATCHES_RBR_WITHOUT_ADDED_VALUE"
    else:
        status = "BELOW_RBR_REJECT_AS_ANALYTICAL_WINNER"
    return {
        "baseline_version": BASELINE_VERSION,
        "baseline_family": baseline["family_id"],
        "baseline_threshold": baseline["threshold"],
        "baseline_metrics": {
            "event_class_macro_dice": baseline_tuple[0],
            "event_class_macro_iou": baseline_tuple[1],
            "worst_event_macro_dice": baseline_tuple[2],
        },
        "model_metrics": {
            "event_class_macro_dice": model_tuple[0],
            "event_class_macro_iou": model_tuple[1],
            "worst_event_macro_dice": model_tuple[2],
        },
        "analytical_winner": False,
        "status": status,
        "threshold_retuned": False,
    }


def run_validation_preflight(
    root: Path,
    output_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    """Exercise exact metrics/render/output code on validation only."""

    output_directory = output_directory.resolve()
    bindings = _candidate_bindings(root)
    if output_directory.exists() or output_directory.is_symlink():
        raise BoundedUNetEvaluationError("preflight output already exists")
    configure_deterministic_execution()
    model = BoundedUNet()
    load_model_weights(root / WEIGHTS_PATH, model)
    examples = load_model_examples(root, {"validation"})
    metrics, arrays = evaluate_examples(model, examples)
    means, stds = _normalization(root)
    report = {
        "evaluation_version": EVALUATION_VERSION,
        "evaluation_id": f"{EVALUATION_ID}-VALIDATION-PREFLIGHT",
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "role": "validation-only-preflight",
        "bindings": bindings,
        "test_arrays_opened": False,
        "test_open_count": 0,
        "test_metrics": metrics,
        "patches": {
            item.patch_id: {
                "candidate_id": item.patch_id,
                "event_group_id": item.event_group_id,
                "proposed_class": "validation-only",
                "crs": "validation-preflight",
                "transform": [20.0, 0.0, 0.0, 0.0, -20.0, 0.0],
                "window": {"row_offset": 0, "column_offset": 0, "height": 64, "width": 64},
            }
            for item in examples
        },
        "baseline_comparison": {
            "status": "NOT_APPLICABLE_VALIDATION_PREFLIGHT",
        },
    }
    output_directory.mkdir(parents=True)
    png_name = f"{EVALUATION_ID}-VALIDATION-PREFLIGHT.png"
    _write_new(
        output_directory / f"{EVALUATION_ID}-VALIDATION-PREFLIGHT.json",
        _json_bytes(report),
    )
    _write_new(
        output_directory / f"{EVALUATION_ID}-VALIDATION-PREFLIGHT.html",
        render_evaluation_html(report, png_name),
    )
    _write_new(
        output_directory / png_name,
        render_evaluation_png(report, examples, arrays, means, stds),
    )
    return report


def run_locked_test_evaluation(
    root: Path,
    authorization_path: Path,
    run_directory: Path,
    output_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, dict[str, Any]]:
    """Consume exactly one authorization and atomically freeze test evidence."""

    authorization_path = authorization_path.resolve()
    run_directory = run_directory.resolve()
    output_directory = output_directory.resolve()
    expected_run_parent = (root / RUN_DIRECTORY_ROOT).resolve()
    if run_directory.parent != expected_run_parent:
        raise BoundedUNetEvaluationError(
            "evaluation run directory is outside the frozen run root"
        )
    if output_directory != (root / OUTPUT_DIRECTORY).resolve():
        raise BoundedUNetEvaluationError("evaluation output path drift")
    _require_exact_git_source(root, git_source_commit)
    bindings = _candidate_bindings(root)
    metadata = _patch_metadata(root)
    means, stds = _normalization(root)
    if run_directory.exists() or run_directory.is_symlink():
        raise BoundedUNetEvaluationError("evaluation run directory already exists")
    if output_directory.exists() or output_directory.is_symlink():
        raise BoundedUNetEvaluationError("evaluation output already exists")
    grant = load_test_access_grant(
        root,
        authorization_path,
        config_sha256=CONFIG_SHA256,
        weights_sha256=WEIGHTS_SHA256,
        selection_sha256=SELECTION_SHA256,
        environment_capture_sha256=ENVIRONMENT_CAPTURE_SHA256,
    )
    _assert_opening_unused(root, grant.opening_id)
    configure_deterministic_execution()
    model = BoundedUNet()
    load_model_weights(root / WEIGHTS_PATH, model)
    run_directory.mkdir(parents=True)
    work = run_directory / "candidate"
    work.mkdir()
    started = {
        "opening_receipt_version": "burnlens-test-opening-start-v0.1.0",
        "opening_id": grant.opening_id,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "authorization_path": grant.authorization_path,
        "authorization_sha256": grant.authorization_sha256,
        "status": "OPENING_ATTEMPT_STARTED",
        "open_count_before": 0,
        "open_count_authorized": 1,
        "arrays_opened": False,
    }
    _write_new(run_directory / "OPENING-STARTED.json", _json_bytes(started))

    examples = load_model_examples(root, {"test"}, test_access_grant=grant)
    exact_patch_ids = [item.patch_id for item in examples]
    if exact_patch_ids != list(metadata):
        raise BoundedUNetEvaluationError("opened test roster order drift")
    consumed = {
        **started,
        "opening_receipt_version": "burnlens-test-opening-consumed-v0.1.0",
        "status": "OPENING_CONSUMED",
        "arrays_opened": True,
        "open_count_after": 1,
        "test_event_group_ids": list(TEST_EVENT_IDS),
        "test_patch_ids": exact_patch_ids,
    }
    _write_new(run_directory / "OPENING-CONSUMED.json", _json_bytes(consumed))

    metrics, arrays = evaluate_examples(model, examples)
    prediction_receipts: dict[str, dict[str, Any]] = {}
    for example in examples:
        patch = arrays[example.patch_id]
        patch_directory = work / "predictions" / example.patch_id
        probability = _write_new(
            patch_directory / "probability.npy",
            _npy_bytes(patch["probability"].astype(np.float32, copy=False)),
        )
        prediction = _write_new(
            patch_directory / "prediction.npy",
            _npy_bytes(patch["prediction"].astype(np.uint8, copy=False)),
        )
        prediction_receipts[example.patch_id] = {
            "probability": {
                **probability,
                "path": (
                    output_directory
                    / "predictions"
                    / example.patch_id
                    / "probability.npy"
                ).relative_to(root).as_posix(),
            },
            "prediction": {
                **prediction,
                "path": (
                    output_directory
                    / "predictions"
                    / example.patch_id
                    / "prediction.npy"
                ).relative_to(root).as_posix(),
            },
        }
    report = {
        "evaluation_version": EVALUATION_VERSION,
        "evaluation_id": EVALUATION_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "issue": 566,
        "unit_id": "P3O1-T01-U05",
        "git_source_commit": git_source_commit,
        "software_version": "0.52.0",
        "model_version_candidate": MODEL_VERSION,
        "dataset_version": DATASET_VERSION,
        "split_version": SPLIT_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "baseline_version": BASELINE_VERSION,
        "opening": {
            "opening_id": grant.opening_id,
            "authorization_path": grant.authorization_path,
            "authorization_sha256": grant.authorization_sha256,
            "open_count_before": 0,
            "open_count_after": 1,
            "test_event_group_ids": list(TEST_EVENT_IDS),
            "test_patch_ids": exact_patch_ids,
        },
        "bindings": bindings,
        "patches": metadata,
        "prediction_outputs": prediction_receipts,
        "test_metrics": metrics,
        "baseline_comparison": _baseline_comparison(root, metrics),
        "warnings": [
            "Owner-approved prototype labels are not independent ground truth or field validation.",
            "Two test event groups support no population or generalization inference.",
            "Area differences cover selected prototype cores only, not complete burn scars.",
            "Threshold sensitivity is diagnostic only; the frozen 0.5 threshold was not changed.",
            "The candidate is not accepted or released until exact U06 replay and decision.",
        ],
        "gates": {
            "candidate_bindings": "pass",
            "authorization_bindings": "pass",
            "exact_test_roster": "pass",
            "single_opening": "pass",
            "finite": "pass",
            "exact_loss_mask": "pass",
            "event_class_denominators": "pass",
            "threshold_not_retuned": "pass",
            "probability_status": "descriptive-only-not-calibrated",
            "render_required": "pass",
            "replay_required": "pending-u06",
        },
        "boundaries": {
            "test_arrays_opened": True,
            "test_open_count": 1,
            "test_tuning": False,
            "post_test_code_model_config_or_threshold_change": False,
            "accepted_model": False,
            "released_model": False,
            "model_value_claim": False,
            "independent_ground_truth": False,
            "field_validation": False,
            "generalization": False,
            "inference_or_deployment": False,
            "final_submission_ready": False,
        },
        "disposition": "test-evaluated-candidate-pending-u06-exact-replay-and-decision",
        "next_dependency": "P3O1-T01-U06 exact same-environment replay, package, model card, decision, and Phase Four handoff",
    }
    _ensure_finite(report)
    image_name = f"{EVALUATION_ID}.png"
    json_path = work / f"{EVALUATION_ID}.json"
    html_path = work / f"{EVALUATION_ID}.html"
    png_path = work / image_name
    _write_new(json_path, _json_bytes(report))
    _write_new(html_path, render_evaluation_html(report, image_name))
    _write_new(
        png_path,
        render_evaluation_png(report, examples, arrays, means, stds),
    )
    output_receipts: dict[str, dict[str, Any]] = {}
    for path in sorted(item for item in work.rglob("*") if item.is_file()):
        relative = path.relative_to(work)
        output_receipts[relative.as_posix()] = {
            "path": (output_directory / relative).relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
        }
    opening_receipt = {
        "opening_receipt_version": "burnlens-test-opening-receipt-v0.1.0",
        "opening_receipt_id": OPENING_RECEIPT_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "opening": consumed,
        "candidate_bindings": bindings,
        "outputs": output_receipts,
        "test_open_count_before": 0,
        "test_open_count_after": 1,
        "retry_authorized": False,
        "disposition": "consumed-and-frozen",
    }
    _write_new(
        work / f"{OPENING_RECEIPT_ID}.json",
        _json_bytes(opening_receipt),
    )
    _promote_tree(work, output_directory)
    receipts: dict[str, dict[str, Any]] = {}
    for path in sorted(item for item in output_directory.rglob("*") if item.is_file()):
        relative = path.relative_to(output_directory).as_posix()
        receipts[relative] = {
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
        }
    return receipts


def record_failed_evaluation(
    run_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    error: BaseException,
) -> None:
    run_directory.mkdir(parents=True, exist_ok=True)
    path = run_directory / "ATTEMPT-FAILED.json"
    if path.exists():
        return
    opening_consumed = (run_directory / "OPENING-CONSUMED.json").is_file()
    _write_new(
        path,
        _json_bytes(
            {
                "attempt_version": "burnlens-bounded-unet-test-attempt-v0.1.0",
                "generated_at_utc": generated_at_utc,
                "run_id": run_id,
                "git_source_commit": git_source_commit,
                "error_type": type(error).__name__,
                "error": str(error),
                "opening_consumed": opening_consumed,
                "retry_authorized": False if opening_consumed else None,
                "disposition": (
                    "stop-opening-consumed"
                    if opening_consumed
                    else "fail-closed-before-opening"
                ),
            }
        ),
    )
