"""Frozen reference implementation for the bounded BurnLens U-Net."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import random
from typing import Any, Iterable

import numpy as np
import torch
from torch import Tensor, nn
import torch.nn.functional as functional


DATASET_MANIFEST_PATH = Path(
    "samples/datasets/burnlens-dataset-v0.1.0/DATASET-MANIFEST.json"
)
DATASET_MANIFEST_SHA256 = (
    "e0b7ac666a70e96f979c386a9d503ad45ed0baea8f21e3838ba4530d5e3d2d16"
)
NORMALIZATION_PATH = Path(
    "records/phase-two/manifests/TRAIN-NORMALIZATION-2026-001.json"
)
NORMALIZATION_SHA256 = (
    "6344861677753e9c96840f47e7a038a15f12a0c29759285c073f5cc6ea4bc255"
)
TRAINING_CONTRACT_PATH = Path(
    "records/phase-two/manifests/BOUNDED-UNET-TRAINING-CONTRACT-2026-001.json"
)
TRAINING_CONTRACT_SHA256 = (
    "670dbb0712768dd0b8ef47a2c5305b736b21139029017a194e4ed747029c9166"
)
DATASET_VERSION = "burnlens-dataset-v0.1.0"
SPLIT_VERSION = "burnlens-whole-event-split-v0.1.0"
MODEL_VERSION = "burnlens-unet-binary-v0.1.0"
CHANNEL_ORDER = (
    "pre_B04",
    "pre_B8A",
    "pre_B12",
    "post_B04",
    "post_B8A",
    "post_B12",
)
ALLOWED_DEVELOPMENT_ROLES = frozenset({"train", "validation"})
SEALED_TEST_ROLE = "test"
SEED = 20260725
LEARNING_RATE = 0.001
EARLY_STOPPING_PATIENCE = 25
EARLY_STOPPING_MIN_DELTA = 1e-6
CHECKPOINT_VERSION = "burnlens-bounded-unet-checkpoint-v0.1.0"


class BoundedUNetError(RuntimeError):
    """A frozen model-contract or execution failure."""


class SealedTestAccessError(BoundedUNetError):
    """The sealed test role was requested outside the one authorized opening."""


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _read_bound_json(root: Path, relative: Path, digest: str) -> dict[str, Any]:
    path = root / relative
    if not path.is_file():
        raise BoundedUNetError(f"required bound JSON is absent: {relative.as_posix()}")
    observed = _sha256_file(path)
    if observed != digest:
        raise BoundedUNetError(
            f"bound JSON hash drift for {relative.as_posix()}: {observed}"
        )
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise BoundedUNetError(f"bound JSON root is not an object: {relative.as_posix()}")
    return value


def _verified_array(path: Path, expected: dict[str, Any]) -> np.ndarray:
    if not path.is_file():
        raise BoundedUNetError(f"dataset array is absent: {path}")
    observed_bytes = path.stat().st_size
    if observed_bytes != expected.get("bytes"):
        raise BoundedUNetError(f"dataset array byte drift: {path}")
    observed_sha256 = _sha256_file(path)
    if observed_sha256 != expected.get("sha256"):
        raise BoundedUNetError(f"dataset array hash drift: {path}")
    value = np.load(path, allow_pickle=False)
    if not isinstance(value, np.ndarray):
        raise BoundedUNetError(f"dataset array is invalid: {path}")
    return value


@dataclass(frozen=True)
class ModelExample:
    """One manifest-bound, normalized model example."""

    patch_id: str
    event_group_id: str
    split_role: str
    inputs: Tensor
    target: Tensor
    loss_mask: Tensor
    input_valid: Tensor


def load_model_examples(root: Path, roles: Iterable[str]) -> list[ModelExample]:
    """Load only permitted development roles in canonical manifest order."""

    requested = frozenset(roles)
    if not requested:
        raise BoundedUNetError("at least one development role is required")
    if SEALED_TEST_ROLE in requested:
        raise SealedTestAccessError(
            "sealed test arrays require the frozen P3O1-T01-U05 opening mechanism"
        )
    if not requested.issubset(ALLOWED_DEVELOPMENT_ROLES):
        raise BoundedUNetError(f"invalid development roles: {sorted(requested)}")

    manifest = _read_bound_json(
        root, DATASET_MANIFEST_PATH, DATASET_MANIFEST_SHA256
    )
    normalization = _read_bound_json(
        root, NORMALIZATION_PATH, NORMALIZATION_SHA256
    )
    contract = _read_bound_json(
        root, TRAINING_CONTRACT_PATH, TRAINING_CONTRACT_SHA256
    )
    if manifest.get("dataset_version") != DATASET_VERSION:
        raise BoundedUNetError("dataset version drift")
    if contract.get("exact_inputs", {}).get("split_version") != SPLIT_VERSION:
        raise BoundedUNetError("split version drift")
    if tuple(normalization.get("channel_order", ())) != CHANNEL_ORDER:
        raise BoundedUNetError("normalization channel order drift")
    if normalization.get("statistics_owner") != "locked training events only":
        raise BoundedUNetError("normalization owner drift")
    if normalization.get("validation_pixels_used") is not False:
        raise BoundedUNetError("normalization used validation pixels")
    if normalization.get("test_pixels_used") is not False:
        raise BoundedUNetError("normalization used test pixels")
    channels = normalization.get("channels")
    if not isinstance(channels, list) or len(channels) != len(CHANNEL_ORDER):
        raise BoundedUNetError("normalization channel schema drift")
    means = np.array([item["mean"] for item in channels], dtype=np.float32)
    standard_deviations = np.array(
        [max(float(item["population_std"]), 1e-6) for item in channels],
        dtype=np.float32,
    )
    if (
        means.shape != (6,)
        or standard_deviations.shape != (6,)
        or not np.isfinite(means).all()
        or not np.isfinite(standard_deviations).all()
        or np.any(standard_deviations <= 0)
    ):
        raise BoundedUNetError("normalization statistics are invalid")

    dataset_root = root / "samples/datasets/burnlens-dataset-v0.1.0"
    examples: list[ModelExample] = []
    for patch in manifest.get("patches", []):
        role = patch.get("split_role")
        if role not in requested:
            continue
        files = {
            Path(item["path"]).name: item
            for item in patch.get("files", [])
            if isinstance(item, dict) and isinstance(item.get("path"), str)
        }
        if set(files) != {
            "features.npy",
            "input_valid.npy",
            "loss_mask.npy",
            "state.npy",
        }:
            raise BoundedUNetError(f"dataset file schema drift: {patch.get('patch_id')}")
        patch_root = dataset_root / "patches" / patch["patch_id"]
        features = _verified_array(
            patch_root / "features.npy", files["features.npy"]
        )
        input_valid = _verified_array(
            patch_root / "input_valid.npy", files["input_valid.npy"]
        ).astype(bool, copy=False)
        loss_mask = _verified_array(
            patch_root / "loss_mask.npy", files["loss_mask.npy"]
        ).astype(bool, copy=False)
        state = _verified_array(patch_root / "state.npy", files["state.npy"])

        if features.shape != (6, 64, 64) or features.dtype != np.float32:
            raise BoundedUNetError("feature tensor schema drift")
        if (
            input_valid.shape != (64, 64)
            or loss_mask.shape != (64, 64)
            or state.shape != (64, 64)
        ):
            raise BoundedUNetError("target/mask tensor schema drift")
        expected_loss_mask = input_valid & np.isin(state, np.array([0, 1]))
        if not np.array_equal(loss_mask, expected_loss_mask):
            raise BoundedUNetError("loss mask does not exactly match valid binary state")
        if not np.isfinite(features[:, input_valid]).all():
            raise BoundedUNetError("valid input pixel contains a nonfinite feature")

        normalized = (
            features - means[:, np.newaxis, np.newaxis]
        ) / standard_deviations[:, np.newaxis, np.newaxis]
        normalized[:, ~input_valid] = 0.0
        if not np.isfinite(normalized).all():
            raise BoundedUNetError("normalized input contains a nonfinite value")
        target = (state == 1).astype(np.float32, copy=False)
        examples.append(
            ModelExample(
                patch_id=patch["patch_id"],
                event_group_id=patch["event_group_id"],
                split_role=role,
                inputs=torch.from_numpy(normalized.copy()),
                target=torch.from_numpy(target[np.newaxis, ...].copy()),
                loss_mask=torch.from_numpy(loss_mask[np.newaxis, ...].copy()),
                input_valid=torch.from_numpy(input_valid[np.newaxis, ...].copy()),
            )
        )

    expected_count = 4 * len(requested)
    if len(examples) != expected_count:
        raise BoundedUNetError(
            f"expected {expected_count} examples for {sorted(requested)}, "
            f"found {len(examples)}"
        )
    if len({example.patch_id for example in examples}) != len(examples):
        raise BoundedUNetError("duplicate model example patch ID")
    return examples


def stack_examples(examples: Iterable[ModelExample]) -> tuple[Tensor, Tensor, Tensor]:
    """Stack examples without shuffling their manifest order."""

    ordered = list(examples)
    if not ordered:
        raise BoundedUNetError("cannot stack an empty example roster")
    inputs = torch.stack([example.inputs for example in ordered])
    targets = torch.stack([example.target for example in ordered])
    masks = torch.stack([example.loss_mask for example in ordered])
    if inputs.shape[1:] != (6, 64, 64):
        raise BoundedUNetError(f"stacked input shape drift: {tuple(inputs.shape)}")
    if targets.shape != masks.shape or targets.shape[1:] != (1, 64, 64):
        raise BoundedUNetError("stacked target/mask shape drift")
    return inputs, targets, masks


def require_finite(tensor: Tensor, name: str) -> None:
    if not bool(torch.isfinite(tensor).all().item()):
        raise BoundedUNetError(f"{name} contains a nonfinite value")


class _DoubleConv(nn.Module):
    def __init__(self, input_channels: int, output_channels: int) -> None:
        super().__init__()
        self.layers = nn.Sequential(
            nn.Conv2d(input_channels, output_channels, 3, padding=1),
            nn.ReLU(inplace=False),
            nn.Conv2d(output_channels, output_channels, 3, padding=1),
            nn.ReLU(inplace=False),
        )

    def forward(self, inputs: Tensor) -> Tensor:
        return self.layers(inputs)


class BoundedUNet(nn.Module):
    """The one architecture authorized by the frozen training contract."""

    def __init__(self) -> None:
        super().__init__()
        self.encoder_1 = _DoubleConv(6, 16)
        self.pool_1 = nn.MaxPool2d(2)
        self.encoder_2 = _DoubleConv(16, 32)
        self.pool_2 = nn.MaxPool2d(2)
        self.bottleneck = _DoubleConv(32, 64)
        self.up_2 = nn.ConvTranspose2d(64, 32, 2, stride=2)
        self.decoder_2 = _DoubleConv(64, 32)
        self.up_1 = nn.ConvTranspose2d(32, 16, 2, stride=2)
        self.decoder_1 = _DoubleConv(32, 16)
        self.output_head = nn.Conv2d(16, 1, 1)

    def forward(self, inputs: Tensor) -> Tensor:
        if inputs.device.type != "cpu":
            raise BoundedUNetError("the bounded U-Net accepts CPU tensors only")
        if inputs.dtype != torch.float32:
            raise BoundedUNetError("the bounded U-Net requires float32 inputs")
        if inputs.ndim != 4 or tuple(inputs.shape[1:]) != (6, 64, 64):
            raise BoundedUNetError(
                f"the bounded U-Net requires [N,6,64,64], found {tuple(inputs.shape)}"
            )
        require_finite(inputs, "model input")
        encoder_1 = self.encoder_1(inputs)
        encoder_2 = self.encoder_2(self.pool_1(encoder_1))
        bottleneck = self.bottleneck(self.pool_2(encoder_2))
        decoder_2 = self.decoder_2(
            torch.cat((self.up_2(bottleneck), encoder_2), dim=1)
        )
        decoder_1 = self.decoder_1(
            torch.cat((self.up_1(decoder_2), encoder_1), dim=1)
        )
        logits = self.output_head(decoder_1)
        require_finite(logits, "model logits")
        return logits


def architecture_record(model: BoundedUNet) -> dict[str, Any]:
    return {
        "model_version": MODEL_VERSION,
        "family": "U-Net-style binary semantic segmentation",
        "input_shape": [6, 64, 64],
        "encoder_channels": [16, 32],
        "bottleneck_channels": 64,
        "decoder_channels": [32, 16],
        "output_channels": 1,
        "batch_normalization": False,
        "dropout": False,
        "pretrained_weights": False,
        "trainable_parameter_count": sum(
            parameter.numel() for parameter in model.parameters()
            if parameter.requires_grad
        ),
    }


def masked_bce_with_logits(logits: Tensor, targets: Tensor, mask: Tensor) -> Tensor:
    """Mean unreduced BCE over exactly the bound binary loss mask."""

    if logits.shape != targets.shape or logits.shape != mask.shape:
        raise BoundedUNetError("logits, targets, and loss mask must have one shape")
    if logits.dtype != torch.float32 or targets.dtype != torch.float32:
        raise BoundedUNetError("logits and targets must be float32")
    if mask.dtype != torch.bool:
        raise BoundedUNetError("loss mask must be bool")
    require_finite(logits, "loss logits")
    require_finite(targets, "loss targets")
    if not bool(torch.all((targets == 0) | (targets == 1)).item()):
        raise BoundedUNetError("targets must be binary")
    selected = int(mask.sum().item())
    if selected <= 0:
        raise BoundedUNetError("loss mask selects zero pixels")
    unreduced = functional.binary_cross_entropy_with_logits(
        logits, targets, reduction="none"
    )
    require_finite(unreduced, "unreduced loss")
    loss = unreduced[mask].mean()
    require_finite(loss, "masked loss")
    return loss


def masked_binary_metrics(
    logits: Tensor,
    targets: Tensor,
    mask: Tensor,
    threshold: float = 0.5,
) -> dict[str, Any]:
    """Compute finite binary counts and class-symmetric Dice/IoU."""

    if not math.isfinite(threshold) or not 0 <= threshold <= 1:
        raise BoundedUNetError("probability threshold must be finite in [0,1]")
    if logits.shape != targets.shape or logits.shape != mask.shape:
        raise BoundedUNetError("metric tensor shape mismatch")
    probabilities = torch.sigmoid(logits)
    require_finite(probabilities, "probabilities")
    prediction = probabilities >= threshold
    truth = targets.to(dtype=torch.bool)
    classes: list[dict[str, Any]] = []
    for class_value, class_name in ((0, "background"), (1, "burned")):
        truth_class = truth == bool(class_value)
        predicted_class = prediction == bool(class_value)
        true_positive = int((truth_class & predicted_class & mask).sum().item())
        false_positive = int((~truth_class & predicted_class & mask).sum().item())
        false_negative = int((truth_class & ~predicted_class & mask).sum().item())
        support = int((truth_class & mask).sum().item())
        predicted_count = int((predicted_class & mask).sum().item())
        dice_denominator = 2 * true_positive + false_positive + false_negative
        iou_denominator = true_positive + false_positive + false_negative
        classes.append(
            {
                "class": class_name,
                "support": support,
                "predicted": predicted_count,
                "true_positive": true_positive,
                "false_positive": false_positive,
                "false_negative": false_negative,
                "dice_denominator": dice_denominator,
                "iou_denominator": iou_denominator,
                "dice": (
                    1.0
                    if dice_denominator == 0
                    else (2 * true_positive) / dice_denominator
                ),
                "iou": (
                    1.0
                    if iou_denominator == 0
                    else true_positive / iou_denominator
                ),
            }
        )
    return {
        "threshold": threshold,
        "core_pixels": int(mask.sum().item()),
        "classes": classes,
        "class_macro_dice": sum(item["dice"] for item in classes) / 2,
        "class_macro_iou": sum(item["iou"] for item in classes) / 2,
    }


def configure_deterministic_execution(
    seed: int = SEED,
    threads: int = 1,
) -> dict[str, Any]:
    """Apply the frozen same-host deterministic execution settings."""

    if seed != SEED:
        raise BoundedUNetError(f"seed drift: expected {SEED}, found {seed}")
    if threads != 1:
        raise BoundedUNetError("the frozen experiment requires one thread per pool")
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True, warn_only=False)
    if torch.get_num_threads() != threads:
        torch.set_num_threads(threads)
    if torch.get_num_interop_threads() != threads:
        torch.set_num_interop_threads(threads)
    return {
        "seed": seed,
        "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        "deterministic_warn_only": (
            torch.is_deterministic_algorithms_warn_only_enabled()
        ),
        "threads": torch.get_num_threads(),
        "interop_threads": torch.get_num_interop_threads(),
    }


def make_optimizer(model: BoundedUNet) -> torch.optim.Adam:
    if any(parameter.device.type != "cpu" for parameter in model.parameters()):
        raise BoundedUNetError("optimizer requires a CPU model")
    return torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=0.0,
    )


def require_finite_training_state(model: BoundedUNet) -> None:
    for name, parameter in model.named_parameters():
        require_finite(parameter, f"weight {name}")
        if parameter.grad is not None:
            require_finite(parameter.grad, f"gradient {name}")


@dataclass
class EarlyStoppingState:
    best_epoch: int | None = None
    best_event_class_macro_dice: float | None = None
    best_event_class_macro_iou: float | None = None
    best_masked_bce: float | None = None
    epochs_without_improvement: int = 0

    def selection_key(self) -> tuple[float, float, float, int] | None:
        if self.best_epoch is None:
            return None
        assert self.best_event_class_macro_dice is not None
        assert self.best_event_class_macro_iou is not None
        assert self.best_masked_bce is not None
        return (
            self.best_event_class_macro_dice,
            self.best_event_class_macro_iou,
            -self.best_masked_bce,
            -self.best_epoch,
        )

    def consider(
        self,
        epoch: int,
        event_class_macro_dice: float,
        event_class_macro_iou: float,
        masked_bce: float,
    ) -> tuple[bool, bool]:
        values = (
            event_class_macro_dice,
            event_class_macro_iou,
            masked_bce,
        )
        if epoch < 1 or not all(math.isfinite(value) for value in values):
            raise BoundedUNetError("early-stopping input is invalid")
        candidate = (
            event_class_macro_dice,
            event_class_macro_iou,
            -masked_bce,
            -epoch,
        )
        current = self.selection_key()
        improved = current is None or candidate > current
        if (
            current is not None
            and abs(event_class_macro_dice - current[0]) <= EARLY_STOPPING_MIN_DELTA
            and candidate[1:] <= current[1:]
        ):
            improved = False
        if improved:
            self.best_epoch = epoch
            self.best_event_class_macro_dice = event_class_macro_dice
            self.best_event_class_macro_iou = event_class_macro_iou
            self.best_masked_bce = masked_bce
            self.epochs_without_improvement = 0
        else:
            self.epochs_without_improvement += 1
        return improved, self.epochs_without_improvement >= EARLY_STOPPING_PATIENCE

    def to_dict(self) -> dict[str, Any]:
        return {
            "best_epoch": self.best_epoch,
            "best_event_class_macro_dice": self.best_event_class_macro_dice,
            "best_event_class_macro_iou": self.best_event_class_macro_iou,
            "best_masked_bce": self.best_masked_bce,
            "epochs_without_improvement": self.epochs_without_improvement,
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> EarlyStoppingState:
        expected = {
            "best_epoch",
            "best_event_class_macro_dice",
            "best_event_class_macro_iou",
            "best_masked_bce",
            "epochs_without_improvement",
        }
        if set(value) != expected:
            raise BoundedUNetError("checkpoint early-stopping schema drift")
        state = cls(**value)
        if state.best_epoch is not None:
            state.selection_key()
        if state.epochs_without_improvement < 0:
            raise BoundedUNetError("checkpoint patience state is invalid")
        return state


def save_checkpoint(
    path: Path,
    model: BoundedUNet,
    optimizer: torch.optim.Adam,
    epoch: int,
    early_stopping: EarlyStoppingState,
) -> dict[str, Any]:
    """Write one no-overwrite repository-local checkpoint."""

    if path.exists():
        raise BoundedUNetError(f"checkpoint already exists: {path}")
    if epoch < 0:
        raise BoundedUNetError("checkpoint epoch is invalid")
    require_finite_training_state(model)
    payload = {
        "checkpoint_version": CHECKPOINT_VERSION,
        "model_version": MODEL_VERSION,
        "architecture": architecture_record(model),
        "epoch": epoch,
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "early_stopping": early_stopping.to_dict(),
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


def load_checkpoint(
    path: Path,
    model: BoundedUNet,
    optimizer: torch.optim.Adam,
) -> tuple[int, EarlyStoppingState]:
    """Load only the repository's exact self-generated checkpoint schema."""

    if not path.is_file():
        raise BoundedUNetError(f"checkpoint is absent: {path}")
    payload = torch.load(path, map_location="cpu", weights_only=False)
    if not isinstance(payload, dict):
        raise BoundedUNetError("checkpoint root is invalid")
    expected = {
        "checkpoint_version",
        "model_version",
        "architecture",
        "epoch",
        "model_state",
        "optimizer_state",
        "early_stopping",
    }
    if set(payload) != expected:
        raise BoundedUNetError("checkpoint schema drift")
    if payload["checkpoint_version"] != CHECKPOINT_VERSION:
        raise BoundedUNetError("checkpoint version drift")
    if payload["model_version"] != MODEL_VERSION:
        raise BoundedUNetError("checkpoint model version drift")
    if payload["architecture"] != architecture_record(model):
        raise BoundedUNetError("checkpoint architecture drift")
    epoch = payload["epoch"]
    if not isinstance(epoch, int) or epoch < 0:
        raise BoundedUNetError("checkpoint epoch is invalid")
    model.load_state_dict(payload["model_state"], strict=True)
    optimizer.load_state_dict(payload["optimizer_state"])
    require_finite_training_state(model)
    return epoch, EarlyStoppingState.from_dict(payload["early_stopping"])
