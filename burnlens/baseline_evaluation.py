"""Preregister, select, and evaluate transparent BurnLens baselines."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from html import escape
import io
import json
import math
import os
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from PIL import Image, ImageDraw, ImageFont


TASK_ISSUE = 562
UNIT_ID = "P2O5-T03-U05"
SOFTWARE_VERSION = "0.51.0"
DATASET_ID = "burnlens-dataset-v0.1.0"
SPLIT_ID = "burnlens-whole-event-split-v0.1.0"
BASELINE_VERSION = "burnlens-baseline-v0.1.0"
PROTOCOL_ID = "BASELINE-PREREGISTRATION-2026-001"
SELECTION_ID = "BASELINE-SELECTION-2026-001"
EVALUATION_ID = "BASELINE-EVALUATION-2026-001"
DATASET_MANIFEST_PATH = Path(
    "samples/datasets/burnlens-dataset-v0.1.0/DATASET-MANIFEST.json"
)
SPLIT_PATH = Path("records/phase-two/manifests/WHOLE-EVENT-SPLIT-2026-001.json")
NORMALIZATION_PATH = Path(
    "records/phase-two/manifests/TRAIN-NORMALIZATION-2026-001.json"
)
SOURCE_RECORD_PATH = Path(
    "records/phase-two/sources/BASELINE-PRIMARY-SOURCES-2026-001.json"
)
DATASET_MANIFEST_SHA256 = (
    "e0b7ac666a70e96f979c386a9d503ad45ed0baea8f21e3838ba4530d5e3d2d16"
)
SPLIT_SHA256 = (
    "a62e66f4f81a95a56a727b29bb382cb87369306f11e2f2a4527d1c7fb68d0b99"
)
NORMALIZATION_SHA256 = (
    "6344861677753e9c96840f47e7a038a15f12a0c29759285c073f5cc6ea4bc255"
)
FAMILY_ORDER = (
    "rbr-threshold",
    "dnbr-threshold",
    "dndvi-threshold",
    "constant-background",
    "constant-burned",
)
SIGNAL_FAMILIES = FAMILY_ORDER[:3]


class BaselineEvaluationError(RuntimeError):
    """Raised when a baseline gate fails closed."""


@dataclass(frozen=True)
class Example:
    patch_id: str
    event_group_id: str
    split_role: str
    features: np.ndarray
    state: np.ndarray
    loss_mask: np.ndarray


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _identity(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise BaselineEvaluationError(f"expected JSON object: {path}")
    return value


def _json_bytes(value: dict[str, Any]) -> bytes:
    return (
        json.dumps(value, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
    )


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
            raise BaselineEvaluationError(f"exact output readback failed: {path}")
    except Exception:
        if created and path.exists():
            path.unlink()
        raise


def _verify_fixed_inputs(root: Path) -> dict[str, dict[str, Any]]:
    paths = {
        "dataset_manifest": root / DATASET_MANIFEST_PATH,
        "whole_event_split": root / SPLIT_PATH,
        "train_normalization": root / NORMALIZATION_PATH,
        "primary_source_record": root / SOURCE_RECORD_PATH,
    }
    expected = {
        "dataset_manifest": DATASET_MANIFEST_SHA256,
        "whole_event_split": SPLIT_SHA256,
        "train_normalization": NORMALIZATION_SHA256,
    }
    identities = {name: _identity(path, root) for name, path in paths.items()}
    for name, digest in expected.items():
        if identities[name]["sha256"] != digest:
            raise BaselineEvaluationError(f"{name} SHA-256 drift")
    return identities


def build_protocol(
    root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    identities = _verify_fixed_inputs(root)
    manifest = _load_json(root / DATASET_MANIFEST_PATH)
    if manifest.get("dataset_version") != DATASET_ID:
        raise BaselineEvaluationError("dataset identity drift")
    role_rosters = {
        role: sorted(
            patch["patch_id"]
            for patch in manifest["patches"]
            if patch["split_role"] == role
        )
        for role in ("train", "validation", "test")
    }
    if {role: len(roster) for role, roster in role_rosters.items()} != {
        "train": 4,
        "validation": 4,
        "test": 4,
    }:
        raise BaselineEvaluationError("patch role roster drift")
    return {
        "protocol_version": "burnlens-baseline-preregistration-v0.1.0",
        "protocol_id": PROTOCOL_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "unit_id": UNIT_ID,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "dataset_id": DATASET_ID,
        "split_id": SPLIT_ID,
        "baseline_version": BASELINE_VERSION,
        "inputs": identities,
        "role_rosters": role_rosters,
        "channel_contract": {
            "order": [
                "pre_B04",
                "pre_B8A",
                "pre_B12",
                "post_B04",
                "post_B8A",
                "post_B12",
            ],
            "units": "unitless bottom-of-atmosphere reflectance",
            "local_resampling": "none",
        },
        "families": [
            {
                "family_id": "rbr-threshold",
                "eligible_for_selection": True,
                "score": "dNBR / (prefire_NBR + 1.001)",
                "prediction": "burned when score >= fitted threshold",
                "source_ids": [
                    "burn-severity-portal-glossary",
                    "parks-dillon-miller-2014-rbr",
                ],
            },
            {
                "family_id": "dnbr-threshold",
                "eligible_for_selection": True,
                "score": "prefire_NBR - postfire_NBR",
                "prediction": "burned when score >= fitted threshold",
                "source_ids": [
                    "burn-severity-portal-glossary",
                    "mtbs-mapping-method",
                ],
            },
            {
                "family_id": "dndvi-threshold",
                "eligible_for_selection": True,
                "score": "prefire_NDVI - postfire_NDVI",
                "prediction": "burned when score >= fitted threshold",
                "source_ids": ["burn-severity-portal-glossary"],
            },
            {
                "family_id": "constant-background",
                "eligible_for_selection": True,
                "score": "none",
                "prediction": "background for every metric-mask pixel",
                "source_ids": [],
            },
            {
                "family_id": "constant-burned",
                "eligible_for_selection": True,
                "score": "none",
                "prediction": "burned for every metric-mask pixel",
                "source_ids": [],
            },
        ],
        "excluded_families": [
            {
                "family_id": "rdnbr-threshold",
                "reason": (
                    "Published scale-dependent denominator is singular at "
                    "prefire NBR zero; no new epsilon or exclusion is permitted."
                ),
            },
            {
                "family_id": "learned-classifier",
                "reason": "U05 is restricted to non-model baselines.",
            },
        ],
        "fit_contract": {
            "threshold_source": "training core pixels only",
            "candidate_thresholds": (
                "midpoints between sorted unique finite training-core scores"
            ),
            "prediction_comparator": "score >= threshold",
            "training_objective_order": [
                "maximize event-class macro Dice",
                "maximize event-class macro IoU",
                "maximize worst-event macro Dice",
                "minimize absolute burned-count error",
                "prefer higher threshold",
            ],
            "validation_family_selection_order": [
                "maximize event-class macro Dice",
                "maximize event-class macro IoU",
                "maximize worst-event macro Dice",
                "maximize fixed-method training event-class macro Dice",
                "prefer family order rbr, dnbr, dndvi, constant-background, constant-burned",
            ],
        },
        "metric_contract": {
            "mask": "loss_mask only; state 0 background and 1 burned",
            "primary": [
                "event-class macro Dice",
                "event-class macro IoU",
            ],
            "required_detail": [
                "per-event and per-class confusion counts",
                "per-event and per-class Dice and IoU",
                "pooled core-only class Dice and IoU",
                "exact denominators",
            ],
            "uncertainty": (
                "report the exact two-test-event range; no confidence interval "
                "or population inference is permitted"
            ),
        },
        "test_open_contract": {
            "analytical_open_count_before": 0,
            "selection_must_be_committed_before_open": True,
            "open_count_authorized": 1,
            "evaluate_all_frozen_families_in_one_process": True,
            "selection_after_test": "prohibited",
            "test_tuning": "prohibited",
            "test_render_before_open": "prohibited",
        },
        "claims": {
            "prototype_labels_only": True,
            "independent_ground_truth": False,
            "field_validation": False,
            "generalization": False,
            "operational_or_emergency_use": False,
        },
        "boundaries": {
            "test_pixels_read": False,
            "threshold_fitted": False,
            "baseline_selected": False,
            "metric_result_created": False,
            "model_created": False,
            "training_authorized": False,
        },
        "next_dependency": "fit thresholds on train and select family on validation",
    }


def write_protocol(
    root: Path,
    output_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> Path:
    protocol = build_protocol(
        root, generated_at_utc, run_id, git_source_commit
    )
    _write_new(output_path, _json_bytes(protocol))
    return output_path


def _verified_array(path: Path, expected: dict[str, Any]) -> np.ndarray:
    if path.stat().st_size != expected["bytes"] or _sha256(path) != expected["sha256"]:
        raise BaselineEvaluationError(f"dataset array binding drift: {path}")
    value = np.load(path, allow_pickle=False)
    if not isinstance(value, np.ndarray):
        raise BaselineEvaluationError(f"invalid array: {path}")
    return value


def load_examples(root: Path, roles: set[str]) -> list[Example]:
    if not roles or not roles.issubset({"train", "validation", "test"}):
        raise BaselineEvaluationError("invalid role request")
    manifest = _load_json(root / DATASET_MANIFEST_PATH)
    if _sha256(root / DATASET_MANIFEST_PATH) != DATASET_MANIFEST_SHA256:
        raise BaselineEvaluationError("dataset manifest drift")
    dataset_root = root / "samples/datasets/burnlens-dataset-v0.1.0"
    examples: list[Example] = []
    for patch in manifest["patches"]:
        if patch["split_role"] not in roles:
            continue
        files = {Path(item["path"]).name: item for item in patch["files"]}
        patch_root = dataset_root / "patches" / patch["patch_id"]
        features = _verified_array(patch_root / "features.npy", files["features.npy"])
        state = _verified_array(patch_root / "state.npy", files["state.npy"])
        loss_mask = _verified_array(
            patch_root / "loss_mask.npy", files["loss_mask.npy"]
        ).astype(bool, copy=False)
        if features.shape != (6, 64, 64):
            raise BaselineEvaluationError("feature schema drift")
        if state.shape != (64, 64) or loss_mask.shape != (64, 64):
            raise BaselineEvaluationError("mask schema drift")
        if not np.isin(state[loss_mask], np.array([0, 1], dtype=state.dtype)).all():
            raise BaselineEvaluationError("metric mask includes non-core state")
        if not np.isfinite(features[:, loss_mask]).all():
            raise BaselineEvaluationError("metric features include nonfinite value")
        examples.append(
            Example(
                patch_id=patch["patch_id"],
                event_group_id=patch["event_group_id"],
                split_role=patch["split_role"],
                features=features,
                state=state,
                loss_mask=loss_mask,
            )
        )
    expected = 4 * len(roles)
    if len(examples) != expected:
        raise BaselineEvaluationError(
            f"expected {expected} examples for {sorted(roles)}, found {len(examples)}"
        )
    return sorted(examples, key=lambda item: item.patch_id)


def _ratio(numerator: np.ndarray, denominator: np.ndarray, name: str) -> np.ndarray:
    if np.any(np.abs(denominator) <= 1e-12):
        raise BaselineEvaluationError(f"{name} denominator is zero")
    return numerator / denominator


def score(features: np.ndarray, family_id: str) -> np.ndarray:
    pre_b04, pre_b8a, pre_b12, post_b04, post_b8a, post_b12 = features
    pre_nbr = _ratio(pre_b8a - pre_b12, pre_b8a + pre_b12, "prefire NBR")
    post_nbr = _ratio(
        post_b8a - post_b12, post_b8a + post_b12, "postfire NBR"
    )
    dnbr = pre_nbr - post_nbr
    if family_id == "dnbr-threshold":
        return dnbr
    if family_id == "rbr-threshold":
        return _ratio(dnbr, pre_nbr + 1.001, "RBR")
    if family_id == "dndvi-threshold":
        pre_ndvi = _ratio(
            pre_b8a - pre_b04, pre_b8a + pre_b04, "prefire NDVI"
        )
        post_ndvi = _ratio(
            post_b8a - post_b04, post_b8a + post_b04, "postfire NDVI"
        )
        return pre_ndvi - post_ndvi
    raise BaselineEvaluationError(f"unknown signal family: {family_id}")


def predict(
    example: Example, family_id: str, threshold: float | None
) -> np.ndarray:
    if family_id == "constant-background":
        return np.zeros(example.state.shape, dtype=np.uint8)
    if family_id == "constant-burned":
        return np.ones(example.state.shape, dtype=np.uint8)
    if threshold is None or not math.isfinite(threshold):
        raise BaselineEvaluationError("signal family threshold is not finite")
    values = score(example.features, family_id)
    return (values >= threshold).astype(np.uint8)


def _class_metrics(
    truth: np.ndarray, predicted: np.ndarray, class_value: int
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
    return {
        "class": "burned" if class_value == 1 else "background",
        "support": support,
        "predicted": predicted_count,
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "dice_denominator": dice_denominator,
        "iou_denominator": iou_denominator,
        "dice": 1.0 if dice_denominator == 0 else (2 * tp) / dice_denominator,
        "iou": 1.0 if iou_denominator == 0 else tp / iou_denominator,
    }


def evaluate(
    examples: Iterable[Example],
    family_id: str,
    threshold: float | None,
) -> dict[str, Any]:
    examples = list(examples)
    if not examples:
        raise BaselineEvaluationError("no examples to evaluate")
    events: list[dict[str, Any]] = []
    pooled_truth: list[np.ndarray] = []
    pooled_prediction: list[np.ndarray] = []
    for event_id in sorted({item.event_group_id for item in examples}):
        event_examples = [item for item in examples if item.event_group_id == event_id]
        truth = np.concatenate(
            [item.state[item.loss_mask].astype(np.uint8) for item in event_examples]
        )
        predicted = np.concatenate(
            [predict(item, family_id, threshold)[item.loss_mask] for item in event_examples]
        )
        classes = [_class_metrics(truth, predicted, value) for value in (0, 1)]
        events.append(
            {
                "event_group_id": event_id,
                "core_pixels": int(truth.size),
                "classes": classes,
                "macro_dice": float(np.mean([item["dice"] for item in classes])),
                "macro_iou": float(np.mean([item["iou"] for item in classes])),
            }
        )
        pooled_truth.append(truth)
        pooled_prediction.append(predicted)
    all_truth = np.concatenate(pooled_truth)
    all_prediction = np.concatenate(pooled_prediction)
    pooled_classes = [
        _class_metrics(all_truth, all_prediction, value) for value in (0, 1)
    ]
    event_macro_dice = [item["macro_dice"] for item in events]
    event_macro_iou = [item["macro_iou"] for item in events]
    return {
        "family_id": family_id,
        "threshold": threshold,
        "event_count": len(events),
        "core_pixels": int(all_truth.size),
        "true_burned_pixels": int(np.count_nonzero(all_truth == 1)),
        "predicted_burned_pixels": int(np.count_nonzero(all_prediction == 1)),
        "event_class_macro_dice": float(
            np.mean(
                [
                    item["dice"]
                    for event in events
                    for item in event["classes"]
                ]
            )
        ),
        "event_class_macro_iou": float(
            np.mean(
                [item["iou"] for event in events for item in event["classes"]]
            )
        ),
        "worst_event_macro_dice": float(min(event_macro_dice)),
        "event_macro_dice_range": [
            float(min(event_macro_dice)),
            float(max(event_macro_dice)),
        ],
        "event_macro_iou_range": [
            float(min(event_macro_iou)),
            float(max(event_macro_iou)),
        ],
        "pooled_classes": pooled_classes,
        "events": events,
    }


def _threshold_candidates(examples: Iterable[Example], family_id: str) -> list[float]:
    values = np.concatenate(
        [score(item.features, family_id)[item.loss_mask] for item in examples]
    )
    unique = np.unique(values.astype(np.float64))
    if unique.size < 2:
        raise BaselineEvaluationError(f"{family_id} has fewer than two unique scores")
    midpoints = unique[:-1] + (unique[1:] - unique[:-1]) / 2.0
    finite = [float(item) for item in midpoints if math.isfinite(float(item))]
    if not finite:
        raise BaselineEvaluationError(f"{family_id} has no finite threshold")
    return finite


def _fit_key(result: dict[str, Any]) -> tuple[float, ...]:
    burned_error = abs(
        result["predicted_burned_pixels"] - result["true_burned_pixels"]
    )
    return (
        result["event_class_macro_dice"],
        result["event_class_macro_iou"],
        result["worst_event_macro_dice"],
        -float(burned_error),
        float(result["threshold"]),
    )


def fit_signal_family(
    train_examples: Iterable[Example], family_id: str
) -> dict[str, Any]:
    examples = list(train_examples)
    candidates = _threshold_candidates(examples, family_id)
    results = [evaluate(examples, family_id, threshold) for threshold in candidates]
    chosen = max(results, key=_fit_key)
    return {
        "family_id": family_id,
        "candidate_threshold_count": len(candidates),
        "candidate_threshold_sha256": sha256(
            _json_bytes({"thresholds": candidates})
        ).hexdigest(),
        "chosen_threshold": chosen["threshold"],
        "training_metrics": chosen,
        "fit_objective": list(_fit_key(chosen)),
    }


def _selection_key(item: dict[str, Any]) -> tuple[float, ...]:
    validation = item["validation_metrics"]
    training = item["training_metrics"]
    priority = len(FAMILY_ORDER) - FAMILY_ORDER.index(item["family_id"])
    return (
        validation["event_class_macro_dice"],
        validation["event_class_macro_iou"],
        validation["worst_event_macro_dice"],
        training["event_class_macro_dice"],
        float(priority),
    )


def build_selection(
    root: Path,
    protocol_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    protocol = _load_json(protocol_path)
    if protocol.get("protocol_id") != PROTOCOL_ID:
        raise BaselineEvaluationError("baseline protocol identity drift")
    if protocol["boundaries"]["test_pixels_read"]:
        raise BaselineEvaluationError("protocol indicates prior test read")
    train = load_examples(root, {"train"})
    validation = load_examples(root, {"validation"})
    attempted: list[dict[str, Any]] = []
    for family_id in SIGNAL_FAMILIES:
        fitted = fit_signal_family(train, family_id)
        fitted["validation_metrics"] = evaluate(
            validation, family_id, fitted["chosen_threshold"]
        )
        attempted.append(fitted)
    for family_id in ("constant-background", "constant-burned"):
        attempted.append(
            {
                "family_id": family_id,
                "candidate_threshold_count": 0,
                "candidate_threshold_sha256": None,
                "chosen_threshold": None,
                "training_metrics": evaluate(train, family_id, None),
                "validation_metrics": evaluate(validation, family_id, None),
            }
        )
    chosen = max(attempted, key=_selection_key)
    return {
        "selection_version": "burnlens-baseline-selection-v0.1.0",
        "selection_id": SELECTION_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "unit_id": UNIT_ID,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "dataset_id": DATASET_ID,
        "split_id": SPLIT_ID,
        "baseline_version": BASELINE_VERSION,
        "inputs": {
            "protocol": _identity(protocol_path, root),
            **_verify_fixed_inputs(root),
        },
        "attempted_families": attempted,
        "selected": {
            "family_id": chosen["family_id"],
            "threshold": chosen["chosen_threshold"],
            "selection_key": list(_selection_key(chosen)),
            "selection_source": "validation events only after train-only fitting",
        },
        "boundaries": {
            "train_pixels_read": True,
            "validation_pixels_read": True,
            "test_pixels_read": False,
            "test_analytical_open_count": 0,
            "selection_frozen": True,
            "metric_result_created": False,
            "model_created": False,
            "training_authorized": False,
        },
        "next_dependency": (
            "commit exact selection, then perform the one authorized test open"
        ),
    }


def write_selection(
    root: Path,
    protocol_path: Path,
    output_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> Path:
    selection = build_selection(
        root, protocol_path, generated_at_utc, run_id, git_source_commit
    )
    _write_new(output_path, _json_bytes(selection))
    return output_path


def _false_color(features: np.ndarray, start: int) -> Image.Image:
    rgb = np.stack(
        [features[start + 2], features[start + 1], features[start]], axis=-1
    )
    rgb = np.clip(rgb / 0.5, 0.0, 1.0)
    return Image.fromarray((rgb * 255.0).astype(np.uint8), mode="RGB").resize(
        (128, 128), resample=Image.Resampling.NEAREST
    )


def _label_image(state: np.ndarray, loss: np.ndarray) -> Image.Image:
    rgb = np.full((*state.shape, 3), (218, 213, 201), dtype=np.uint8)
    rgb[loss & (state == 0)] = (40, 120, 155)
    rgb[loss & (state == 1)] = (215, 75, 45)
    return Image.fromarray(rgb, mode="RGB").resize(
        (128, 128), resample=Image.Resampling.NEAREST
    )


def _prediction_image(
    prediction: np.ndarray, state: np.ndarray, loss: np.ndarray
) -> Image.Image:
    rgb = np.full((*state.shape, 3), (218, 213, 201), dtype=np.uint8)
    correct = loss & (prediction == state)
    wrong = loss & (prediction != state)
    rgb[correct] = (35, 145, 115)
    rgb[wrong] = (225, 65, 70)
    return Image.fromarray(rgb, mode="RGB").resize(
        (128, 128), resample=Image.Resampling.NEAREST
    )


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
    ):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def render_evaluation_png(
    report: dict[str, Any], examples: list[Example], predictions: dict[str, np.ndarray]
) -> bytes:
    width, height = 1800, 1180
    image = Image.new("RGB", (width, height), (244, 241, 232))
    draw = ImageDraw.Draw(image)
    title = _font(42)
    section = _font(24)
    body = _font(17)
    small = _font(14)
    draw.text((50, 35), "BurnLens non-model baseline", fill=(20, 35, 46), font=title)
    draw.text(
        (50, 92),
        "One sealed-test opening · prototype labels · no generalization claim",
        fill=(65, 75, 82),
        font=section,
    )
    selected = report["selected_test_metrics"]
    draw.text(
        (50, 145),
        (
            f"{report['selected']['family_id']}  |  "
            f"event-class Dice {selected['event_class_macro_dice']:.3f}  |  "
            f"IoU {selected['event_class_macro_iou']:.3f}"
        ),
        fill=(20, 115, 105),
        font=section,
    )
    for index, example in enumerate(examples):
        row = index
        y = 205 + row * 225
        draw.rounded_rectangle((50, y, 1750, y + 195), radius=12, fill=(255, 255, 255))
        draw.text(
            (68, y + 10),
            example.patch_id.replace("--", " · "),
            fill=(28, 40, 48),
            font=small,
        )
        tiles = (
            ("pre false color", _false_color(example.features, 0)),
            ("post false color", _false_color(example.features, 3)),
            ("prototype core", _label_image(example.state, example.loss_mask)),
            (
                "correct / error",
                _prediction_image(
                    predictions[example.patch_id], example.state, example.loss_mask
                ),
            ),
        )
        for tile_index, (label, tile) in enumerate(tiles):
            x = 68 + tile_index * 405
            image.paste(tile, (x, y + 38))
            draw.text((x + 140, y + 85), label, fill=(65, 75, 82), font=body)
    draw.text(
        (50, 1128),
        (
            "Red marks errors only on owner-approved prototype cores. Gray is "
            "excluded. Test evidence has two events and supports no population claim."
        ),
        fill=(80, 70, 62),
        font=body,
    )
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=False)
    return buffer.getvalue()


def render_evaluation_html(report: dict[str, Any], png_name: str) -> str:
    rows = "".join(
        (
            f"<tr><td>{escape(item['family_id'])}</td>"
            f"<td>{item['event_class_macro_dice']:.4f}</td>"
            f"<td>{item['event_class_macro_iou']:.4f}</td>"
            f"<td>{item['event_macro_dice_range'][0]:.4f}–"
            f"{item['event_macro_dice_range'][1]:.4f}</td></tr>"
        )
        for item in report["test_family_metrics"]
    )
    events = "".join(
        (
            f"<tr><td>{escape(item['event_group_id'])}</td>"
            f"<td>{item['core_pixels']}</td>"
            f"<td>{item['macro_dice']:.4f}</td>"
            f"<td>{item['macro_iou']:.4f}</td></tr>"
        )
        for item in report["selected_test_metrics"]["events"]
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens baseline evaluation</title>
<style>
:root{{--ink:#17242c;--paper:#f4f1e8;--card:#fff;--teal:#147f75;--orange:#df5f32;--line:#d6d0c2}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 Arial,sans-serif;overflow-x:hidden}}
main{{max-width:1180px;margin:auto;padding:42px 24px 72px}}h1{{font-size:clamp(2rem,5vw,4.1rem);line-height:1;margin:.2em 0}}h2{{margin-top:2.2rem}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;margin:18px 0}}.card strong{{overflow-wrap:anywhere}}
.warn{{border-left:7px solid var(--orange)}}img{{display:block;width:100%;height:auto;border:1px solid var(--line);border-radius:14px;background:#fff}}
table{{border-collapse:collapse;width:100%}}th,td{{text-align:left;padding:10px;border-bottom:1px solid var(--line);overflow-wrap:anywhere}}code{{overflow-wrap:anywhere}}
@media(max-width:760px){{main{{padding:24px 14px 50px}}table{{table-layout:fixed}}}}
</style></head><body><main>
<p>BURNLENS / PHASE TWO / ISSUE #{TASK_ISSUE} / U05</p>
<h1>A transparent baseline meets the sealed test once.</h1>
<div class="card warn">Owner-approved prototype labels, not independent ground truth or field validation. Two test events support no generalization claim.</div>
<div class="card"><strong>{escape(report['selected']['family_id'])}</strong><br>
Validation selected this frozen family before the test opened. Test event-class macro Dice:
<strong>{report['selected_test_metrics']['event_class_macro_dice']:.4f}</strong>.
IoU: <strong>{report['selected_test_metrics']['event_class_macro_iou']:.4f}</strong>.</div>
<h2>Inspectable test evidence</h2>
<img src="{escape(png_name)}" width="1800" height="1180" alt="Four sealed-test BurnLens patches with pre and post imagery, prototype cores, and selected-baseline errors">
<h2>Frozen family comparison</h2><div class="card"><table><thead><tr><th>Family</th><th>Dice</th><th>IoU</th><th>Event Dice range</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Selected family by event</h2><div class="card"><table><thead><tr><th>Event</th><th>Cores</th><th>Macro Dice</th><th>Macro IoU</th></tr></thead><tbody>{events}</tbody></table></div>
<h2>Boundary</h2><div class="card"><p>Test analytical-open count: 1. No threshold or family changed after opening. No confidence interval is reported because two event groups cannot support population inference.</p>
<p>Training remains unauthorized pending U06. Model none. Operational and emergency use prohibited.</p></div>
<p>Trace: commit <code>{escape(report['git_source_commit'])}</code> · run <code>{escape(report['run_id'])}</code> · dataset <code>{DATASET_ID}</code> · split <code>{SPLIT_ID}</code> · baseline <code>{BASELINE_VERSION}</code>.</p>
</main></body></html>
"""


def build_evaluation(
    root: Path,
    protocol_path: Path,
    selection_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> tuple[dict[str, Any], list[Example], dict[str, np.ndarray]]:
    protocol = _load_json(protocol_path)
    selection = _load_json(selection_path)
    if protocol.get("protocol_id") != PROTOCOL_ID:
        raise BaselineEvaluationError("protocol identity drift")
    if selection.get("selection_id") != SELECTION_ID:
        raise BaselineEvaluationError("selection identity drift")
    if not selection["boundaries"]["selection_frozen"]:
        raise BaselineEvaluationError("selection is not frozen")
    if selection["boundaries"]["test_pixels_read"]:
        raise BaselineEvaluationError("selection indicates prior test read")
    test = load_examples(root, {"test"})
    attempted_by_id = {
        item["family_id"]: item for item in selection["attempted_families"]
    }
    family_metrics: list[dict[str, Any]] = []
    for family_id in FAMILY_ORDER:
        item = attempted_by_id[family_id]
        family_metrics.append(evaluate(test, family_id, item["chosen_threshold"]))
    selected_family = selection["selected"]["family_id"]
    selected_threshold = selection["selected"]["threshold"]
    selected_metrics = next(
        item for item in family_metrics if item["family_id"] == selected_family
    )
    predictions = {
        item.patch_id: predict(item, selected_family, selected_threshold)
        for item in test
    }
    report = {
        "evaluation_version": "burnlens-baseline-evaluation-v0.1.0",
        "evaluation_id": EVALUATION_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "unit_id": UNIT_ID,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "dataset_id": DATASET_ID,
        "split_id": SPLIT_ID,
        "baseline_version": BASELINE_VERSION,
        "inputs": {
            "protocol": _identity(protocol_path, root),
            "selection": _identity(selection_path, root),
            **_verify_fixed_inputs(root),
        },
        "selected": selection["selected"],
        "test_family_metrics": family_metrics,
        "selected_test_metrics": selected_metrics,
        "uncertainty": {
            "test_event_groups": 2,
            "reporting": "exact event range only",
            "confidence_interval": None,
            "population_inference": False,
        },
        "claims": {
            "prototype_labels_only": True,
            "independent_ground_truth": False,
            "field_validation": False,
            "generalization": False,
            "operational_or_emergency_use": False,
        },
        "boundaries": {
            "test_analytical_open_count_before": 0,
            "test_analytical_open_count_after": 1,
            "test_tuning": False,
            "selection_changed_after_test": False,
            "metric_result_created": True,
            "model_created": False,
            "training_authorized": False,
        },
        "decision": "PASS_REPRODUCIBLE_NON_MODEL_BASELINE_EVALUATION",
        "next_dependency": "P2O5-T03-U06 model-readiness audit",
    }
    return report, test, predictions


def write_evaluation(
    root: Path,
    protocol_path: Path,
    selection_path: Path,
    output_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Path]:
    report, examples, predictions = build_evaluation(
        root,
        protocol_path,
        selection_path,
        generated_at_utc,
        run_id,
        git_source_commit,
    )
    outputs = {
        "json": output_directory / f"{EVALUATION_ID}.json",
        "html": output_directory / f"{EVALUATION_ID}.html",
        "png": output_directory / f"{EVALUATION_ID}.png",
    }
    png = render_evaluation_png(report, examples, predictions)
    _write_new(outputs["json"], _json_bytes(report))
    _write_new(
        outputs["html"],
        render_evaluation_html(report, outputs["png"].name).encode("utf-8"),
    )
    _write_new(outputs["png"], png)
    return outputs
