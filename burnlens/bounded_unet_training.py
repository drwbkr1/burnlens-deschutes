"""Execute and freeze the one authorized BurnLens U-Net training run."""

from __future__ import annotations

import copy
from hashlib import sha256
from html import escape
import io
import json
import math
import os
from pathlib import Path
import re
import shutil
import time
from typing import Any, Iterable
import warnings

from PIL import Image, ImageDraw, ImageFont
import torch

from burnlens.bounded_unet import (
    BoundedUNet,
    BoundedUNetError,
    DATASET_VERSION,
    EARLY_STOPPING_PATIENCE,
    EarlyStoppingState,
    MODEL_VERSION,
    SEED,
    SPLIT_VERSION,
    architecture_record,
    configure_deterministic_execution,
    load_checkpoint,
    load_model_examples,
    make_optimizer,
    masked_bce_with_logits,
    require_finite_training_state,
    save_checkpoint,
    stack_examples,
)
from burnlens.unet_experiment import (
    PROTOCOL_ID,
    TEST_EVENT_IDS,
    TRAIN_EVENT_IDS,
    VALIDATION_EVENT_IDS,
    _event_metrics,
)


TRAINING_VERSION = "burnlens-bounded-unet-training-v0.1.0"
TRAINING_ID = "BOUNDED-UNET-TRAINING-2026-001"
TRAINING_CONFIG_VERSION = "burnlens-bounded-unet-training-config-v0.1.0"
TRAINING_HISTORY_VERSION = "burnlens-bounded-unet-training-history-v0.1.0"
SELECTION_VERSION = "burnlens-bounded-unet-checkpoint-selection-v0.1.0"
WEIGHTS_VERSION = "burnlens-bounded-unet-weights-v0.1.0"
PROTOCOL_PATH = Path(
    "records/phase-three/manifests/"
    "BOUNDED-UNET-EXPERIMENT-PROTOCOL-2026-001.json"
)
PROTOCOL_SHA256 = (
    "e2a0146ebcef4102b246f7a2117e09d21f441354eda0ceb4df764bbaebe940a6"
)
PROTOCOL_SOURCE_COMMIT = "fbb2e923ae7f9ca9ed7dbb317e4235a236ae2411"
ENVIRONMENT_CAPTURE_PATH = Path(
    "records/phase-three/environments/"
    "MODEL-ENVIRONMENT-CAPTURE-2026-001.json"
)
ENVIRONMENT_CAPTURE_SHA256 = (
    "009effea6c4b17b884c8d4e66ad51b4981c18ebfa1aed1b332391b1be8524e36"
)
CANDIDATE_DIRECTORY = Path(
    "samples/models/burnlens-unet-binary-v0.1.0"
)
RUN_DIRECTORY_ROOT = Path("runs/phase-three")
MAXIMUM_EPOCHS = 200
_COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class BoundedUNetTrainingError(BoundedUNetError):
    """A frozen substantive-training or candidate-promotion failure."""


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _write_new(path: Path, payload: bytes) -> dict[str, Any]:
    if path.exists():
        raise BoundedUNetTrainingError(f"output already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    return {
        "path": path.as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
    }


def _copy_new(source: Path, destination: Path) -> dict[str, Any]:
    if not source.is_file():
        raise BoundedUNetTrainingError(f"copy source is absent: {source}")
    if destination.exists():
        raise BoundedUNetTrainingError(
            f"copy destination already exists: {destination}"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as incoming, destination.open("xb") as outgoing:
        shutil.copyfileobj(incoming, outgoing, 8 * 1024 * 1024)
        outgoing.flush()
        os.fsync(outgoing.fileno())
    if _sha256_file(source) != _sha256_file(destination):
        raise BoundedUNetTrainingError("copy hash mismatch")
    return {
        "path": destination.as_posix(),
        "bytes": destination.stat().st_size,
        "sha256": _sha256_file(destination),
    }


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise BoundedUNetTrainingError(f"JSON root is not an object: {path}")
    return value


def _repo_relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise BoundedUNetTrainingError(
            f"path is outside repository root: {path}"
        ) from exc


def _final_receipt(
    root: Path,
    staged_path: Path,
    final_path: Path,
) -> dict[str, Any]:
    return {
        "path": _repo_relative(root, final_path),
        "bytes": staged_path.stat().st_size,
        "sha256": _sha256_file(staged_path),
    }


def _require_exact_path(root: Path, observed: Path, expected: Path) -> Path:
    resolved = observed if observed.is_absolute() else root / observed
    if resolved.resolve() != (root / expected).resolve():
        raise BoundedUNetTrainingError(
            f"path drift: expected {expected.as_posix()}, found {observed}"
        )
    return resolved.resolve()


def _require_finite_json(value: Any, label: str = "value") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            _require_finite_json(item, f"{label}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _require_finite_json(item, f"{label}[{index}]")
    elif isinstance(value, float) and not math.isfinite(value):
        raise BoundedUNetTrainingError(f"nonfinite {label}")


def validate_training_entry(
    root: Path,
    protocol_path: Path,
    git_source_commit: str,
) -> dict[str, Any]:
    """Validate every frozen U03 binding before a training step."""

    if not _COMMIT_PATTERN.fullmatch(git_source_commit):
        raise BoundedUNetTrainingError("training source commit is invalid")
    protocol_file = _require_exact_path(root, protocol_path, PROTOCOL_PATH)
    environment_file = root / ENVIRONMENT_CAPTURE_PATH
    if (
        not protocol_file.is_file()
        or _sha256_file(protocol_file) != PROTOCOL_SHA256
    ):
        raise BoundedUNetTrainingError("frozen protocol drift")
    if (
        not environment_file.is_file()
        or _sha256_file(environment_file) != ENVIRONMENT_CAPTURE_SHA256
    ):
        raise BoundedUNetTrainingError("environment capture drift")
    protocol = _read_json(protocol_file)
    if protocol.get("protocol_id") != PROTOCOL_ID:
        raise BoundedUNetTrainingError("protocol identity drift")
    if protocol.get("git_source_commit") != PROTOCOL_SOURCE_COMMIT:
        raise BoundedUNetTrainingError("protocol source drift")
    if protocol.get("unit_id") != "P3O1-T01-U03":
        raise BoundedUNetTrainingError("protocol unit drift")
    if protocol.get("model_version_candidate") != MODEL_VERSION:
        raise BoundedUNetTrainingError("model version drift")
    if protocol["compute_budget"] != {
        "device": "one local CPU",
        "substantive_run_count": 1,
        "batch_size": 4,
        "maximum_epochs": MAXIMUM_EPOCHS,
        "early_stopping_patience": EARLY_STOPPING_PATIENCE,
        "preflight_epochs": 2,
        "preflight_weights_retained": False,
        "architecture_or_hyperparameter_search": False,
    }:
        raise BoundedUNetTrainingError("compute budget drift")
    if tuple(protocol["data"]["train_events"]) != TRAIN_EVENT_IDS:
        raise BoundedUNetTrainingError("training event roster drift")
    if tuple(protocol["data"]["validation_events"]) != VALIDATION_EVENT_IDS:
        raise BoundedUNetTrainingError("validation event roster drift")
    if tuple(protocol["data"]["test_events"]) != TEST_EVENT_IDS:
        raise BoundedUNetTrainingError("test event roster drift")
    if protocol["optimization"]["seed"] != SEED:
        raise BoundedUNetTrainingError("seed drift")
    if protocol["optimization"]["batch_size"] != 4:
        raise BoundedUNetTrainingError("batch-size drift")
    if protocol["optimization"]["maximum_epochs"] != MAXIMUM_EPOCHS:
        raise BoundedUNetTrainingError("maximum-epoch drift")
    if protocol["optimization"]["device"] != "cpu":
        raise BoundedUNetTrainingError("device drift")
    if protocol["optimization"]["dtype"] != "float32":
        raise BoundedUNetTrainingError("dtype drift")
    if protocol["optimization"]["optimizer"] != "Adam":
        raise BoundedUNetTrainingError("optimizer drift")
    if protocol["optimization"]["learning_rate"] != 0.001:
        raise BoundedUNetTrainingError("learning-rate drift")
    if protocol["optimization"]["weight_decay"] != 0.0:
        raise BoundedUNetTrainingError("weight-decay drift")
    if protocol["optimization"]["gradient_clipping"] is not None:
        raise BoundedUNetTrainingError("gradient-clipping drift")
    if protocol["optimization"]["mixed_precision"] is not False:
        raise BoundedUNetTrainingError("mixed-precision drift")
    if protocol["data"]["shuffle"] is not False:
        raise BoundedUNetTrainingError("shuffle drift")
    if protocol["data"]["augmentation"] != "none":
        raise BoundedUNetTrainingError("augmentation drift")
    boundaries = protocol["boundaries"]
    if boundaries["test_arrays_opened"] is not False:
        raise BoundedUNetTrainingError("sealed-test boundary drift")
    if boundaries["test_open_count"] != 0:
        raise BoundedUNetTrainingError("sealed-test opening count drift")
    if boundaries["substantive_training_started"] is not False:
        raise BoundedUNetTrainingError("protocol start boundary drift")
    expected_architecture = architecture_record(BoundedUNet())
    for key, value in expected_architecture.items():
        protocol_value = (
            protocol["architecture"].get("model_version_candidate")
            if key == "model_version"
            else protocol["architecture"].get(key)
        )
        if key in {"input_shape", "output_channels", "trainable_parameter_count"}:
            continue
        if protocol_value is not None and protocol_value != value:
            raise BoundedUNetTrainingError(f"architecture drift: {key}")
    return protocol


def build_training_config(
    root: Path,
    protocol_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    protocol = validate_training_entry(root, protocol_path, git_source_commit)
    return {
        "training_config_version": TRAINING_CONFIG_VERSION,
        "training_config_id": "BOUNDED-UNET-TRAINING-CONFIG-2026-001",
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "issue": 566,
        "unit_id": "P3O1-T01-U04",
        "git_source_commit": git_source_commit,
        "software_version": "0.52.0",
        "dataset_version": DATASET_VERSION,
        "split_version": SPLIT_VERSION,
        "label_schema_version": "burn-scar-binary-region-label-schema-v0.3.0",
        "baseline_version": "burnlens-baseline-v0.1.0",
        "model_version_candidate": MODEL_VERSION,
        "protocol": {
            "path": PROTOCOL_PATH.as_posix(),
            "bytes": (root / PROTOCOL_PATH).stat().st_size,
            "sha256": PROTOCOL_SHA256,
            "source_commit": PROTOCOL_SOURCE_COMMIT,
        },
        "environment_capture": {
            "path": ENVIRONMENT_CAPTURE_PATH.as_posix(),
            "bytes": (root / ENVIRONMENT_CAPTURE_PATH).stat().st_size,
            "sha256": ENVIRONMENT_CAPTURE_SHA256,
        },
        "exact_inputs": protocol["exact_inputs"],
        "architecture": protocol["architecture"],
        "data": protocol["data"],
        "optimization": protocol["optimization"],
        "checkpoint_selection": protocol["checkpoint_selection"],
        "compute_budget": protocol["compute_budget"],
        "test_opening": protocol["test_opening"],
        "retention": protocol["retention"],
        "claims": protocol["claims"],
        "stop_conditions": protocol["stop_conditions"],
        "boundaries": {
            "substantive_run_count_authorized": 1,
            "test_arrays_opened": False,
            "test_open_count": 0,
            "test_access_authorized": False,
            "architecture_or_hyperparameter_search": False,
            "dataset_split_label_normalization_or_baseline_change": False,
        },
    }


def save_model_weights(path: Path, model: BoundedUNet) -> dict[str, Any]:
    """Save deterministic model-only weights with a strict safe-load schema."""

    if path.exists():
        raise BoundedUNetTrainingError(f"weights already exist: {path}")
    require_finite_training_state(model)
    payload = {
        "weights_version": WEIGHTS_VERSION,
        "model_version": MODEL_VERSION,
        "architecture": architecture_record(model),
        "model_state": model.state_dict(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        torch.save(payload, stream)
        stream.flush()
        os.fsync(stream.fileno())
    return {
        "path": path.as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
    }


def load_model_weights(path: Path, model: BoundedUNet) -> None:
    if not path.is_file():
        raise BoundedUNetTrainingError(f"weights are absent: {path}")
    payload = torch.load(path, map_location="cpu", weights_only=True)
    if not isinstance(payload, dict) or set(payload) != {
        "weights_version",
        "model_version",
        "architecture",
        "model_state",
    }:
        raise BoundedUNetTrainingError("weights schema drift")
    if payload["weights_version"] != WEIGHTS_VERSION:
        raise BoundedUNetTrainingError("weights version drift")
    if payload["model_version"] != MODEL_VERSION:
        raise BoundedUNetTrainingError("weights model version drift")
    if payload["architecture"] != architecture_record(model):
        raise BoundedUNetTrainingError("weights architecture drift")
    model.load_state_dict(payload["model_state"], strict=True)
    require_finite_training_state(model)


def _validate_role_roster(examples: Iterable[Any], expected: tuple[str, ...]) -> None:
    observed = tuple(sorted({item.event_group_id for item in examples}))
    if observed != tuple(sorted(expected)):
        raise BoundedUNetTrainingError(
            f"role event roster drift: expected {expected}, found {observed}"
        )


def _run_training_loop(
    run_directory: Path,
    training: list[Any],
    validation: list[Any],
    *,
    maximum_epochs: int = MAXIMUM_EPOCHS,
) -> dict[str, Any]:
    """Run one deterministic loop. Tests may lower epochs; production may not."""

    if maximum_epochs < 1 or maximum_epochs > MAXIMUM_EPOCHS:
        raise BoundedUNetTrainingError("training-loop epoch bound is invalid")
    _validate_role_roster(training, TRAIN_EVENT_IDS)
    _validate_role_roster(validation, VALIDATION_EVENT_IDS)
    settings = configure_deterministic_execution(SEED, 1)
    model = BoundedUNet()
    optimizer = make_optimizer(model)
    stopping = EarlyStoppingState()
    train_inputs, train_targets, train_masks = stack_examples(training)
    history: list[dict[str, Any]] = []
    best_model_state: dict[str, Any] | None = None
    best_optimizer_state: dict[str, Any] | None = None
    best_stopping_state: dict[str, Any] | None = None
    final_epoch = 0
    for epoch in range(1, maximum_epochs + 1):
        final_epoch = epoch
        model.train()
        optimizer.zero_grad(set_to_none=True)
        logits = model(train_inputs)
        train_loss = masked_bce_with_logits(logits, train_targets, train_masks)
        train_loss.backward()
        require_finite_training_state(model)
        optimizer.step()
        require_finite_training_state(model)
        model.eval()
        with torch.no_grad():
            validation_metrics = _event_metrics(model, validation)
        improved, would_stop = stopping.consider(
            epoch,
            validation_metrics["event_class_macro_dice"],
            validation_metrics["event_class_macro_iou"],
            validation_metrics["masked_bce"],
        )
        row = {
            "epoch": epoch,
            "train_masked_bce": float(train_loss.detach().item()),
            "validation": validation_metrics,
            "checkpoint_improved": improved,
            "early_stopping": stopping.to_dict(),
            "would_early_stop": would_stop,
            "finite_checks": {
                "input": True,
                "logits": True,
                "loss": True,
                "gradients": True,
                "weights": True,
                "validation_probabilities_and_metrics": True,
            },
        }
        _require_finite_json(row, f"epoch_{epoch}")
        history.append(row)
        _write_new(
            run_directory / "epochs" / f"epoch-{epoch:03d}.json",
            _json_bytes(row),
        )
        if improved:
            best_model_state = copy.deepcopy(model.state_dict())
            best_optimizer_state = copy.deepcopy(optimizer.state_dict())
            best_stopping_state = copy.deepcopy(stopping.to_dict())
        if would_stop:
            break
    if (
        not history
        or stopping.best_epoch is None
        or best_model_state is None
        or best_optimizer_state is None
        or best_stopping_state is None
    ):
        raise BoundedUNetTrainingError("training produced no selected checkpoint")

    final_checkpoint_path = run_directory / "checkpoints" / "final-checkpoint.pt"
    final_checkpoint = save_checkpoint(
        final_checkpoint_path,
        model,
        optimizer,
        final_epoch,
        stopping,
    )
    final_reload_model = BoundedUNet()
    final_reload_optimizer = make_optimizer(final_reload_model)
    loaded_final_epoch, _ = load_checkpoint(
        final_checkpoint_path,
        final_reload_model,
        final_reload_optimizer,
    )
    if loaded_final_epoch != final_epoch:
        raise BoundedUNetTrainingError("final checkpoint reload epoch drift")

    model.load_state_dict(best_model_state, strict=True)
    optimizer.load_state_dict(best_optimizer_state)
    selected_stopping = EarlyStoppingState.from_dict(best_stopping_state)
    require_finite_training_state(model)
    selected_checkpoint_path = (
        run_directory / "checkpoints" / "selected-checkpoint.pt"
    )
    selected_checkpoint = save_checkpoint(
        selected_checkpoint_path,
        model,
        optimizer,
        selected_stopping.best_epoch or 0,
        selected_stopping,
    )
    selected_reload_model = BoundedUNet()
    selected_reload_optimizer = make_optimizer(selected_reload_model)
    loaded_selected_epoch, loaded_selected_stopping = load_checkpoint(
        selected_checkpoint_path,
        selected_reload_model,
        selected_reload_optimizer,
    )
    if (
        loaded_selected_epoch != selected_stopping.best_epoch
        or loaded_selected_stopping.to_dict() != selected_stopping.to_dict()
    ):
        raise BoundedUNetTrainingError("selected checkpoint reload drift")
    weights_path = run_directory / "weights" / f"{MODEL_VERSION}.pt"
    weights = save_model_weights(weights_path, model)
    weight_reload = BoundedUNet()
    load_model_weights(weights_path, weight_reload)
    for name, tensor in model.state_dict().items():
        if not torch.equal(tensor, weight_reload.state_dict()[name]):
            raise BoundedUNetTrainingError(f"weights reload drift: {name}")

    selected_row = history[selected_stopping.best_epoch - 1]
    return {
        "environment": {
            "torch": torch.__version__,
            "device": "cpu",
            **settings,
        },
        "roster": {
            "train_patch_ids": [item.patch_id for item in training],
            "train_event_group_ids": list(TRAIN_EVENT_IDS),
            "train_core_pixels": sum(
                int(item.loss_mask.sum().item()) for item in training
            ),
            "validation_patch_ids": [item.patch_id for item in validation],
            "validation_event_group_ids": list(VALIDATION_EVENT_IDS),
            "validation_core_pixels": sum(
                int(item.loss_mask.sum().item()) for item in validation
            ),
            "test_patch_ids_opened": [],
            "test_event_group_ids_opened": [],
        },
        "history": history,
        "epoch_count": len(history),
        "final_epoch": final_epoch,
        "stopped_early": final_epoch < maximum_epochs,
        "selected_epoch": selected_stopping.best_epoch,
        "selected_validation": selected_row["validation"],
        "selected_train_masked_bce": selected_row["train_masked_bce"],
        "selected_early_stopping": selected_stopping.to_dict(),
        "final_early_stopping": stopping.to_dict(),
        "working_receipts": {
            "selected_checkpoint": selected_checkpoint,
            "final_checkpoint": final_checkpoint,
            "weights": weights,
        },
    }


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ):
        if path.is_file():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def render_training_png(report: dict[str, Any], history: list[dict[str, Any]]) -> bytes:
    image = Image.new("RGB", (1800, 1200), "#f4f0e8")
    draw = ImageDraw.Draw(image)
    dark = "#17211d"
    green = "#23634c"
    amber = "#9a5b19"
    red = "#9a3e32"
    muted = "#5e6962"
    draw.rounded_rectangle((60, 50, 1740, 250), 28, fill=dark)
    draw.text((105, 88), "BurnLens bounded U-Net training", font=_font(52), fill="white")
    draw.text(
        (108, 166),
        "One frozen CPU run • validation-only selection • sealed test unopened",
        font=_font(27),
        fill="#d8e4dd",
    )
    selection = report["selection"]
    cards = [
        ("Epochs", str(report["training"]["epoch_count"]), green),
        ("Selected epoch", str(selection["selected_epoch"]), green),
        (
            "Validation Dice",
            f"{selection['validation']['event_class_macro_dice']:.3f}",
            amber,
        ),
        (
            "Validation BCE",
            f"{selection['validation']['masked_bce']:.3f}",
            amber,
        ),
    ]
    for index, (label, value, color) in enumerate(cards):
        left = 60 + index * 420
        draw.rounded_rectangle((left, 290, left + 390, 455), 22, fill="white")
        draw.text((left + 28, 320), label, font=_font(23), fill=muted)
        draw.text((left + 28, 362), value, font=_font(44), fill=color)
    draw.text((70, 510), "Complete training trajectory", font=_font(34), fill=dark)
    chart = (100, 575, 1170, 1040)
    draw.rounded_rectangle(chart, 20, fill="white")
    x0, y0, x1, y1 = chart
    left = x0 + 90
    right = x1 - 45
    top = y0 + 45
    bottom = y1 - 75
    draw.line((left, bottom, right, bottom), fill="#bcc6bf", width=3)
    draw.line((left, top, left, bottom), fill="#bcc6bf", width=3)
    max_index = max(1, len(history) - 1)
    dice_points: list[tuple[float, float]] = []
    bce_points: list[tuple[float, float]] = []
    for index, row in enumerate(history):
        x = left + (right - left) * index / max_index
        dice = row["validation"]["event_class_macro_dice"]
        bce = min(1.0, row["validation"]["masked_bce"])
        dice_points.append((x, bottom - dice * (bottom - top)))
        bce_points.append((x, bottom - bce * (bottom - top)))
    if len(dice_points) == 1:
        draw.ellipse(
            (
                dice_points[0][0] - 5,
                dice_points[0][1] - 5,
                dice_points[0][0] + 5,
                dice_points[0][1] + 5,
            ),
            fill=green,
        )
    else:
        draw.line(dice_points, fill=green, width=6)
        draw.line(bce_points, fill=amber, width=6)
    draw.rectangle((160, 1070, 195, 1105), fill=green)
    draw.text((210, 1071), "validation event-class macro Dice", font=_font(21), fill=dark)
    draw.rectangle((655, 1070, 690, 1105), fill=amber)
    draw.text((705, 1071), "validation masked BCE", font=_font(21), fill=dark)
    draw.rounded_rectangle((1230, 510, 1740, 1060), 24, fill="#fffaf0")
    draw.text((1270, 550), "Frozen boundary", font=_font(32), fill=dark)
    bullets = [
        "Exactly one substantive model",
        "Train and validation only",
        "No threshold or seed search",
        "Every epoch retained",
        "Finite tensors and metrics",
        "Selected checkpoint reloaded",
        "Ward Creek/Windigo unopened",
        "Not a model-value claim",
    ]
    y = 625
    for bullet in bullets:
        draw.ellipse((1272, y + 8, 1288, y + 24), fill=red)
        draw.text((1305, y), bullet, font=_font(21), fill=dark)
        y += 53
    output = io.BytesIO()
    image.save(output, format="PNG", optimize=False, compress_level=9)
    return output.getvalue()


def render_training_html(
    report: dict[str, Any],
    history: list[dict[str, Any]],
    image_name: str,
) -> bytes:
    rows = "".join(
        "<tr>"
        f"<td>{row['epoch']}</td>"
        f"<td>{row['train_masked_bce']:.9f}</td>"
        f"<td>{row['validation']['masked_bce']:.9f}</td>"
        f"<td>{row['validation']['event_class_macro_dice']:.9f}</td>"
        f"<td>{row['validation']['event_class_macro_iou']:.9f}</td>"
        f"<td>{row['validation']['worst_event_macro_dice']:.9f}</td>"
        f"<td>{'yes' if row['checkpoint_improved'] else 'no'}</td>"
        "</tr>"
        for row in history
    )
    warning_rows = "".join(
        f"<li>{escape(item)}</li>" for item in report["warnings"]
    )
    selection = report["selection"]
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BurnLens bounded U-Net training</title>
<style>
:root{{--ink:#17211d;--muted:#5e6962;--paper:#f4f0e8;--card:#fff;--green:#23634c;--amber:#9a5b19}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,sans-serif}}
a{{color:var(--green)}} .skip{{position:absolute;left:-999px}} .skip:focus{{left:1rem;top:1rem;background:#fff;padding:.7rem;z-index:2}}
main{{width:min(1120px,calc(100% - 2rem));margin:2rem auto 4rem}} header,.card{{background:var(--card);border-radius:18px;padding:clamp(1.1rem,3vw,2.2rem);margin-bottom:1.2rem}}
h1{{margin:.2rem 0;font-size:clamp(2rem,6vw,3.8rem);line-height:1.05}} h2{{margin-top:0}} .eyebrow{{color:var(--green);font-weight:800;letter-spacing:.08em;text-transform:uppercase}}
.warning{{border-left:6px solid var(--amber);background:#fffaf0}} img{{display:block;width:100%;height:auto;border-radius:14px}}
.table-wrap{{overflow:auto;max-height:42rem}} table{{border-collapse:collapse;width:100%;min-width:860px}} th,td{{padding:.65rem;border-bottom:1px solid #d9ddd9;text-align:right}} th:first-child,td:first-child{{text-align:left}} thead th{{position:sticky;top:0;background:#fff}}
code{{overflow-wrap:anywhere}} @media(max-width:520px){{main{{width:min(100% - 1rem,1120px);margin-top:.5rem}} header,.card{{border-radius:12px}}}}
</style>
</head>
<body>
<a class="skip" href="#evidence">Skip to evidence</a>
<main>
<header>
<p class="eyebrow">P3O1-T01-U04 • one substantive run</p>
<h1>One frozen model, selected without test evidence</h1>
<p>The exact bounded U-Net trained for {report['training']['epoch_count']} epochs. Validation selected epoch {selection['selected_epoch']}. Ward Creek and Windigo test arrays remain unopened.</p>
</header>
<section class="card warning" aria-labelledby="boundary"><h2 id="boundary">Boundary</h2><p>This is a validation-selected candidate, not a test evaluation or evidence of model value. Owner-approved prototype labels are not independent ground truth or field validation.</p><ul>{warning_rows}</ul></section>
<section class="card" id="evidence" aria-labelledby="figure"><h2 id="figure">Rendered training evidence</h2><img src="{escape(image_name)}" alt="Complete BurnLens bounded U-Net training trajectory with epoch count, validation-selected epoch, validation Dice and masked BCE, and sealed-test boundary."></section>
<section class="card" aria-labelledby="history"><h2 id="history">Complete epoch history</h2><div class="table-wrap"><table><thead><tr><th>Epoch</th><th>Train BCE</th><th>Validation BCE</th><th>Event-class macro Dice</th><th>Event-class macro IoU</th><th>Worst-event macro Dice</th><th>Selected then</th></tr></thead><tbody>{rows}</tbody></table></div></section>
<section class="card" aria-labelledby="lineage"><h2 id="lineage">Frozen selection and lineage</h2><dl><dt>Run</dt><dd><code>{escape(report['run_id'])}</code></dd><dt>Source commit</dt><dd><code>{escape(report['git_source_commit'])}</code></dd><dt>Protocol SHA-256</dt><dd><code>{escape(report['protocol']['sha256'])}</code></dd><dt>Weights SHA-256</dt><dd><code>{escape(selection['weights']['sha256'])}</code></dd><dt>Disposition</dt><dd><code>{escape(report['disposition'])}</code></dd></dl></section>
</main>
</body>
</html>
"""
    return html.encode("utf-8")


def _promote_candidate(
    root: Path,
    run_directory: Path,
    candidate_directory: Path,
    config: dict[str, Any],
    loop: dict[str, Any],
    captured_warnings: list[str],
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    duration_seconds: float,
) -> dict[str, dict[str, Any]]:
    if candidate_directory.exists():
        raise BoundedUNetTrainingError(
            f"candidate output already exists: {candidate_directory}"
        )
    staging = run_directory / "candidate-staging"
    if staging.exists():
        raise BoundedUNetTrainingError(
            f"candidate staging already exists: {staging}"
        )
    staging.mkdir(parents=True)
    final_names = {
        "config": "TRAINING-CONFIG-2026-001.json",
        "history": "TRAINING-HISTORY-2026-001.json",
        "selection": "CHECKPOINT-SELECTION-2026-001.json",
        "selected_checkpoint": "selected-checkpoint.pt",
        "final_checkpoint": "final-checkpoint.pt",
        "weights": f"{MODEL_VERSION}.pt",
        "json": f"{TRAINING_ID}.json",
        "html": f"{TRAINING_ID}.html",
        "png": f"{TRAINING_ID}.png",
    }
    config_path = staging / final_names["config"]
    config_stage = _write_new(config_path, _json_bytes(config))
    history_value = {
        "training_history_version": TRAINING_HISTORY_VERSION,
        "training_history_id": "BOUNDED-UNET-TRAINING-HISTORY-2026-001",
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "epoch_count": loop["epoch_count"],
        "history": loop["history"],
    }
    history_path = staging / final_names["history"]
    history_stage = _write_new(history_path, _json_bytes(history_value))
    selected_stage_path = staging / final_names["selected_checkpoint"]
    selected_stage = _copy_new(
        Path(loop["working_receipts"]["selected_checkpoint"]["path"]),
        selected_stage_path,
    )
    final_stage_path = staging / final_names["final_checkpoint"]
    final_stage = _copy_new(
        Path(loop["working_receipts"]["final_checkpoint"]["path"]),
        final_stage_path,
    )
    weights_stage_path = staging / final_names["weights"]
    weights_stage = _copy_new(
        Path(loop["working_receipts"]["weights"]["path"]),
        weights_stage_path,
    )
    final = lambda name: candidate_directory / final_names[name]
    config_receipt = _final_receipt(root, config_path, final("config"))
    history_receipt = _final_receipt(root, history_path, final("history"))
    selected_receipt = _final_receipt(
        root, selected_stage_path, final("selected_checkpoint")
    )
    final_checkpoint_receipt = _final_receipt(
        root, final_stage_path, final("final_checkpoint")
    )
    weights_receipt = _final_receipt(root, weights_stage_path, final("weights"))
    selection = {
        "selection_version": SELECTION_VERSION,
        "selection_id": "BOUNDED-UNET-CHECKPOINT-SELECTION-2026-001",
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "rule": [
            "maximize validation event-class macro Dice",
            "maximize validation event-class macro IoU",
            "minimize validation masked BCE",
            "earliest epoch",
        ],
        "selected_epoch": loop["selected_epoch"],
        "selected_train_masked_bce": loop["selected_train_masked_bce"],
        "validation": loop["selected_validation"],
        "early_stopping": loop["selected_early_stopping"],
        "weights": weights_receipt,
        "selected_checkpoint": selected_receipt,
        "final_checkpoint": final_checkpoint_receipt,
        "test_arrays_opened": False,
        "test_open_count": 0,
    }
    _require_finite_json(selection, "selection")
    selection_path = staging / final_names["selection"]
    selection_stage = _write_new(selection_path, _json_bytes(selection))
    selection_receipt = _final_receipt(
        root, selection_path, final("selection")
    )
    report = {
        "training_version": TRAINING_VERSION,
        "training_id": TRAINING_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "issue": 566,
        "unit_id": "P3O1-T01-U04",
        "git_source_commit": git_source_commit,
        "software_version": "0.52.0",
        "dataset_version": DATASET_VERSION,
        "split_version": SPLIT_VERSION,
        "label_schema_version": "burn-scar-binary-region-label-schema-v0.3.0",
        "baseline_version": "burnlens-baseline-v0.1.0",
        "model_version_candidate": MODEL_VERSION,
        "protocol": config["protocol"],
        "environment_capture": config["environment_capture"],
        "architecture": architecture_record(BoundedUNet()),
        "optimization": config["optimization"],
        "training": {
            "substantive_run_count": 1,
            "epoch_count": loop["epoch_count"],
            "final_epoch": loop["final_epoch"],
            "stopped_early": loop["stopped_early"],
            "duration_seconds": duration_seconds,
            "history": history_receipt,
            "roster": loop["roster"],
            "environment": loop["environment"],
        },
        "selection": {
            **selection,
            "record": selection_receipt,
        },
        "config": config_receipt,
        "warnings": captured_warnings
        + [
            "Validation selection is not a locked-test evaluation.",
            "The frozen RBR baseline remains at the selected-core metric ceiling.",
            "Owner-approved prototype labels are not independent ground truth or field validation.",
        ],
        "gates": {
            "protocol_bound": True,
            "environment_bound": True,
            "one_substantive_run": True,
            "train_and_validation_only": True,
            "test_arrays_opened": False,
            "finite": True,
            "exact_loss_mask": True,
            "complete_epoch_history": True,
            "validation_only_selection": True,
            "selected_checkpoint_reload": True,
            "weights_reload": True,
            "atomic_candidate_promotion": True,
            "render_required": True,
        },
        "boundaries": {
            "test_arrays_opened": False,
            "test_open_count": 0,
            "test_metrics_created": False,
            "architecture_or_hyperparameter_search": False,
            "second_model": False,
            "dataset_split_label_normalization_or_baseline_changed": False,
            "model_value_claim": False,
            "inference_or_deployment": False,
            "final_submission_ready": False,
        },
        "disposition": "candidate-frozen-pending-one-test-opening",
        "next_dependency": (
            "P3O1-T01-U05 exact authorization-bound single test opening "
            "after U04 evidence is committed and pushed"
        ),
    }
    png_path = staging / final_names["png"]
    png_stage = _write_new(
        png_path,
        render_training_png(report, loop["history"]),
    )
    png_receipt = _final_receipt(root, png_path, final("png"))
    html_path = staging / final_names["html"]
    html_stage = _write_new(
        html_path,
        render_training_html(report, loop["history"], final_names["png"]),
    )
    html_receipt = _final_receipt(root, html_path, final("html"))
    report["outputs"] = {
        "config": config_receipt,
        "history": history_receipt,
        "selection": selection_receipt,
        "weights": weights_receipt,
        "selected_checkpoint": selected_receipt,
        "final_checkpoint": final_checkpoint_receipt,
        "html": html_receipt,
        "png": png_receipt,
    }
    _require_finite_json(report, "training_report")
    json_path = staging / final_names["json"]
    json_stage = _write_new(json_path, _json_bytes(report))
    json_receipt = _final_receipt(root, json_path, final("json"))
    candidate_directory.parent.mkdir(parents=True, exist_ok=True)
    if candidate_directory.exists():
        raise BoundedUNetTrainingError("candidate appeared before promotion")
    os.replace(staging, candidate_directory)
    receipts = {
        "config": config_receipt,
        "history": history_receipt,
        "selection": selection_receipt,
        "weights": weights_receipt,
        "selected_checkpoint": selected_receipt,
        "final_checkpoint": final_checkpoint_receipt,
        "html": html_receipt,
        "png": png_receipt,
        "json": json_receipt,
    }
    for receipt in receipts.values():
        path = root / receipt["path"]
        if (
            not path.is_file()
            or path.stat().st_size != receipt["bytes"]
            or _sha256_file(path) != receipt["sha256"]
        ):
            raise BoundedUNetTrainingError(
                f"promoted candidate verification failed: {receipt['path']}"
            )
    return receipts


def run_substantive_training(
    root: Path,
    protocol_path: Path,
    run_output_directory: Path,
    candidate_output_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, dict[str, Any]]:
    """Run and atomically promote exactly one frozen U04 candidate."""

    run_directory = _require_exact_path(
        root,
        run_output_directory,
        RUN_DIRECTORY_ROOT / run_id,
    )
    candidate_directory = _require_exact_path(
        root,
        candidate_output_directory,
        CANDIDATE_DIRECTORY,
    )
    if run_directory.exists():
        raise BoundedUNetTrainingError(
            f"substantive run directory already exists: {run_directory}"
        )
    if candidate_directory.exists():
        raise BoundedUNetTrainingError(
            f"candidate directory already exists: {candidate_directory}"
        )
    config = build_training_config(
        root,
        protocol_path,
        generated_at_utc,
        run_id,
        git_source_commit,
    )
    run_directory.mkdir(parents=True)
    _write_new(
        run_directory / "ATTEMPT-STARTED.json",
        _json_bytes(
            {
                "attempt_version": "burnlens-model-training-attempt-v0.1.0",
                "attempt_id": run_id,
                "generated_at_utc": generated_at_utc,
                "unit_id": "P3O1-T01-U04",
                "git_source_commit": git_source_commit,
                "protocol_sha256": PROTOCOL_SHA256,
                "test_access_requested": False,
                "substantive_run_count": 1,
            }
        ),
    )
    config_working = _write_new(
        run_directory / "TRAINING-CONFIG-2026-001.json",
        _json_bytes(config),
    )
    start = time.perf_counter()
    with warnings.catch_warnings(record=True) as observed_warnings:
        warnings.simplefilter("always")
        training = load_model_examples(root, {"train"})
        validation = load_model_examples(root, {"validation"})
        loop = _run_training_loop(
            run_directory,
            training,
            validation,
            maximum_epochs=MAXIMUM_EPOCHS,
        )
    captured_warnings = [
        f"{item.category.__name__}: {item.message}" for item in observed_warnings
    ]
    duration_seconds = time.perf_counter() - start
    working_history = _write_new(
        run_directory / "TRAINING-HISTORY-2026-001.json",
        _json_bytes(
            {
                "training_history_version": TRAINING_HISTORY_VERSION,
                "training_history_id": "BOUNDED-UNET-TRAINING-HISTORY-2026-001",
                "run_id": run_id,
                "git_source_commit": git_source_commit,
                "epoch_count": loop["epoch_count"],
                "history": loop["history"],
            }
        ),
    )
    working_result = {
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "duration_seconds": duration_seconds,
        "epoch_count": loop["epoch_count"],
        "final_epoch": loop["final_epoch"],
        "selected_epoch": loop["selected_epoch"],
        "selected_validation": loop["selected_validation"],
        "warnings": captured_warnings,
        "config": config_working,
        "history": working_history,
        "working_receipts": loop["working_receipts"],
        "test_arrays_opened": False,
        "test_open_count": 0,
        "disposition": "training-complete-pending-atomic-candidate-promotion",
    }
    _write_new(
        run_directory / "TRAINING-RESULT-2026-001.json",
        _json_bytes(working_result),
    )
    receipts = _promote_candidate(
        root,
        run_directory,
        candidate_directory,
        config,
        loop,
        captured_warnings,
        generated_at_utc,
        run_id,
        git_source_commit,
        duration_seconds,
    )
    _write_new(
        run_directory / "ATTEMPT-COMPLETE.json",
        _json_bytes(
            {
                "attempt_version": "burnlens-model-training-attempt-v0.1.0",
                "attempt_id": run_id,
                "unit_id": "P3O1-T01-U04",
                "git_source_commit": git_source_commit,
                "candidate_receipts": receipts,
                "test_arrays_opened": False,
                "test_open_count": 0,
                "disposition": "pass-candidate-frozen",
            }
        ),
    )
    return receipts


def record_failed_attempt(
    root: Path,
    run_output_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    error: Exception,
) -> None:
    """Retain a bounded failure without overwriting prior attempt evidence."""

    expected = RUN_DIRECTORY_ROOT / run_id
    run_directory = _require_exact_path(root, run_output_directory, expected)
    if not run_directory.is_dir():
        return
    if (run_directory / "ATTEMPT-COMPLETE.json").is_file():
        return
    failure = run_directory / "ATTEMPT-FAILED.json"
    if failure.exists():
        return
    _write_new(
        failure,
        _json_bytes(
            {
                "attempt_version": "burnlens-model-training-attempt-v0.1.0",
                "attempt_id": run_id,
                "generated_at_utc": generated_at_utc,
                "unit_id": "P3O1-T01-U04",
                "git_source_commit": git_source_commit,
                "error_type": type(error).__name__,
                "error": str(error),
                "automatic_retry_authorized": False,
                "test_access_requested": False,
                "disposition": "retained-failure",
            }
        ),
    )
