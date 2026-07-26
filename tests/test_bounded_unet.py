from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import numpy as np
import torch

from burnlens.bounded_unet import (
    BoundedUNet,
    BoundedUNetError,
    EarlyStoppingState,
    LEARNING_RATE,
    ModelExample,
    SealedTestAccessError,
    architecture_record,
    configure_deterministic_execution,
    load_checkpoint,
    load_model_examples,
    make_optimizer,
    masked_bce_with_logits,
    masked_binary_metrics,
    require_finite_training_state,
    save_checkpoint,
    stack_examples,
)


ROOT = Path(__file__).resolve().parents[1]


def _synthetic_example(patch_id: str, role: str = "train") -> ModelExample:
    generator = torch.Generator().manual_seed(17)
    inputs = torch.randn((6, 64, 64), generator=generator, dtype=torch.float32)
    target = torch.zeros((1, 64, 64), dtype=torch.float32)
    target[:, 20:44, 20:44] = 1
    loss_mask = torch.zeros((1, 64, 64), dtype=torch.bool)
    loss_mask[:, 16:48, 16:48] = True
    input_valid = torch.ones((1, 64, 64), dtype=torch.bool)
    return ModelExample(
        patch_id=patch_id,
        event_group_id=f"event-{patch_id}",
        split_role=role,
        inputs=inputs,
        target=target,
        loss_mask=loss_mask,
        input_valid=input_valid,
    )


def _state_digest(model: BoundedUNet) -> str:
    digest = sha256()
    for name, tensor in sorted(model.state_dict().items()):
        digest.update(name.encode("utf-8"))
        digest.update(tensor.detach().cpu().numpy().tobytes(order="C"))
    return digest.hexdigest()


def _tiny_step() -> tuple[str, float]:
    configure_deterministic_execution()
    model = BoundedUNet()
    optimizer = make_optimizer(model)
    inputs, targets, masks = stack_examples(
        [_synthetic_example("a"), _synthetic_example("b")]
    )
    optimizer.zero_grad(set_to_none=True)
    logits = model(inputs)
    loss = masked_bce_with_logits(logits, targets, masks)
    loss.backward()
    require_finite_training_state(model)
    optimizer.step()
    require_finite_training_state(model)
    return _state_digest(model), float(loss.detach().item())


class BoundedUNetTests(unittest.TestCase):
    def test_architecture_matches_the_frozen_contract(self) -> None:
        configure_deterministic_execution()
        model = BoundedUNet()
        record = architecture_record(model)
        self.assertEqual(record["input_shape"], [6, 64, 64])
        self.assertEqual(record["encoder_channels"], [16, 32])
        self.assertEqual(record["bottleneck_channels"], 64)
        self.assertEqual(record["decoder_channels"], [32, 16])
        self.assertFalse(record["batch_normalization"])
        self.assertFalse(record["dropout"])
        self.assertFalse(record["pretrained_weights"])
        self.assertEqual(record["trainable_parameter_count"], 117473)
        self.assertEqual(
            sum(isinstance(item, torch.nn.Conv2d) for item in model.modules()),
            11,
        )
        self.assertEqual(
            sum(
                isinstance(item, torch.nn.ConvTranspose2d)
                for item in model.modules()
            ),
            2,
        )
        self.assertEqual(
            sum(isinstance(item, torch.nn.MaxPool2d) for item in model.modules()),
            2,
        )
        self.assertFalse(any(isinstance(item, torch.nn.BatchNorm2d) for item in model.modules()))
        self.assertFalse(any(isinstance(item, torch.nn.Dropout) for item in model.modules()))

    def test_forward_backward_and_masked_loss_are_finite(self) -> None:
        configure_deterministic_execution()
        model = BoundedUNet()
        optimizer = make_optimizer(model)
        self.assertEqual(optimizer.param_groups[0]["lr"], LEARNING_RATE)
        inputs, targets, masks = stack_examples([_synthetic_example("a")])
        logits = model(inputs)
        self.assertEqual(tuple(logits.shape), (1, 1, 64, 64))
        loss = masked_bce_with_logits(logits, targets, masks)
        loss.backward()
        require_finite_training_state(model)

    def test_masked_loss_excludes_every_unselected_pixel(self) -> None:
        logits = torch.tensor([[[[100.0, 0.0], [0.0, -100.0]]]])
        targets = torch.tensor([[[[0.0, 0.0], [1.0, 1.0]]]])
        mask = torch.tensor([[[[False, True], [True, False]]]])
        observed = masked_bce_with_logits(logits, targets, mask)
        expected = torch.nn.functional.binary_cross_entropy_with_logits(
            torch.tensor([0.0, 0.0]),
            torch.tensor([0.0, 1.0]),
        )
        self.assertTrue(torch.equal(observed, expected))

    def test_metrics_ignore_excluded_predictions_and_preserve_denominators(self) -> None:
        logits = torch.tensor([[[[-100.0, -100.0], [100.0, 100.0]]]])
        targets = torch.tensor([[[[0.0, 1.0], [1.0, 0.0]]]])
        mask = torch.tensor([[[[True, False], [True, False]]]])
        metrics = masked_binary_metrics(logits, targets, mask)
        self.assertEqual(metrics["core_pixels"], 2)
        self.assertEqual(metrics["class_macro_dice"], 1.0)
        self.assertEqual(metrics["class_macro_iou"], 1.0)
        self.assertEqual(metrics["classes"][0]["dice_denominator"], 2)
        self.assertEqual(metrics["classes"][1]["iou_denominator"], 1)

    def test_incompatible_inputs_fail_closed(self) -> None:
        model = BoundedUNet()
        with self.assertRaisesRegex(BoundedUNetError, "float32"):
            model(torch.zeros((1, 6, 64, 64), dtype=torch.float64))
        with self.assertRaisesRegex(BoundedUNetError, "N,6,64,64"):
            model(torch.zeros((1, 6, 32, 32), dtype=torch.float32))
        values = torch.zeros((1, 6, 64, 64), dtype=torch.float32)
        values[0, 0, 0, 0] = torch.nan
        with self.assertRaisesRegex(BoundedUNetError, "nonfinite"):
            model(values)

    def test_sealed_test_role_is_rejected_before_array_access(self) -> None:
        with mock.patch("numpy.load") as load:
            with self.assertRaisesRegex(SealedTestAccessError, "U05"):
                load_model_examples(ROOT, {"test"})
            load.assert_not_called()

    def test_manifest_loader_uses_only_train_normalization_and_exact_masks(self) -> None:
        examples = load_model_examples(ROOT, {"train", "validation"})
        self.assertEqual(len(examples), 8)
        self.assertEqual([item.split_role for item in examples[:4]], ["train"] * 4)
        self.assertEqual(
            [item.split_role for item in examples[4:]], ["validation"] * 4
        )
        self.assertEqual(len({item.event_group_id for item in examples}), 4)
        for example in examples:
            self.assertEqual(tuple(example.inputs.shape), (6, 64, 64))
            self.assertEqual(example.inputs.dtype, torch.float32)
            self.assertTrue(torch.isfinite(example.inputs).all())
            self.assertTrue(torch.all(example.loss_mask <= example.input_valid))
            self.assertTrue(
                torch.all(
                    (example.target[example.loss_mask] == 0)
                    | (example.target[example.loss_mask] == 1)
                )
            )

    def test_bound_train_validation_smoke_runs_one_train_step_only(self) -> None:
        configure_deterministic_execution()
        training = load_model_examples(ROOT, {"train"})
        validation = load_model_examples(ROOT, {"validation"})
        self.assertEqual(sum(int(item.loss_mask.sum()) for item in training), 109)
        self.assertEqual(sum(int(item.loss_mask.sum()) for item in validation), 89)

        model = BoundedUNet()
        optimizer = make_optimizer(model)
        train_inputs, train_targets, train_masks = stack_examples(training)
        optimizer.zero_grad(set_to_none=True)
        train_loss = masked_bce_with_logits(
            model(train_inputs), train_targets, train_masks
        )
        train_loss.backward()
        require_finite_training_state(model)
        optimizer.step()
        require_finite_training_state(model)

        validation_inputs, validation_targets, validation_masks = stack_examples(
            validation
        )
        model.eval()
        with torch.no_grad():
            validation_logits = model(validation_inputs)
            validation_loss = masked_bce_with_logits(
                validation_logits, validation_targets, validation_masks
            )
            validation_metrics = masked_binary_metrics(
                validation_logits, validation_targets, validation_masks
            )
        self.assertTrue(torch.isfinite(train_loss))
        self.assertTrue(torch.isfinite(validation_loss))
        self.assertEqual(validation_metrics["core_pixels"], 89)

    def test_deterministic_tiny_step_replays_exactly(self) -> None:
        first_digest, first_loss = _tiny_step()
        second_digest, second_loss = _tiny_step()
        self.assertEqual(first_digest, second_digest)
        self.assertEqual(first_loss, second_loss)

    def test_early_stopping_uses_frozen_tie_break_order_and_patience(self) -> None:
        state = EarlyStoppingState()
        improved, stopped = state.consider(1, 0.5, 0.4, 0.7)
        self.assertTrue(improved)
        self.assertFalse(stopped)
        improved, _ = state.consider(2, 0.5, 0.5, 0.8)
        self.assertTrue(improved)
        improved, _ = state.consider(3, 0.5, 0.5, 0.7)
        self.assertTrue(improved)
        improved, _ = state.consider(4, 0.5, 0.5, 0.7)
        self.assertFalse(improved)
        self.assertEqual(state.best_epoch, 3)
        for epoch in range(5, 29):
            _, stopped = state.consider(epoch, 0.4, 0.4, 0.8)
        self.assertTrue(stopped)

    def test_checkpoint_round_trip_and_no_overwrite(self) -> None:
        configure_deterministic_execution()
        model = BoundedUNet()
        optimizer = make_optimizer(model)
        inputs, targets, masks = stack_examples([_synthetic_example("a")])
        loss = masked_bce_with_logits(model(inputs), targets, masks)
        loss.backward()
        optimizer.step()
        expected_digest = _state_digest(model)
        stopping = EarlyStoppingState()
        stopping.consider(1, 0.5, 0.4, float(loss.detach().item()))
        with tempfile.TemporaryDirectory(prefix="burnlens-unet-test-") as directory:
            path = Path(directory) / "checkpoint.pt"
            receipt = save_checkpoint(path, model, optimizer, 1, stopping)
            self.assertEqual(receipt["bytes"], path.stat().st_size)
            self.assertEqual(receipt["sha256"], sha256(path.read_bytes()).hexdigest())
            with self.assertRaisesRegex(BoundedUNetError, "already exists"):
                save_checkpoint(path, model, optimizer, 1, stopping)
            restored = BoundedUNet()
            restored_optimizer = make_optimizer(restored)
            epoch, restored_stopping = load_checkpoint(
                path, restored, restored_optimizer
            )
            self.assertEqual(epoch, 1)
            self.assertEqual(restored_stopping.to_dict(), stopping.to_dict())
            self.assertEqual(_state_digest(restored), expected_digest)

    def test_loss_rejects_empty_mask_and_nonfinite_values(self) -> None:
        logits = torch.zeros((1, 1, 2, 2), dtype=torch.float32)
        targets = torch.zeros_like(logits)
        with self.assertRaisesRegex(BoundedUNetError, "zero pixels"):
            masked_bce_with_logits(
                logits, targets, torch.zeros_like(logits, dtype=torch.bool)
            )
        logits[0, 0, 0, 0] = np.inf
        with self.assertRaisesRegex(BoundedUNetError, "nonfinite"):
            masked_bce_with_logits(
                logits, targets, torch.ones_like(logits, dtype=torch.bool)
            )


if __name__ == "__main__":
    unittest.main()
