from __future__ import annotations

import json
from pathlib import Path
import tempfile

import pytest
import torch

from burnlens.bounded_unet import (
    BoundedUNet,
    ModelExample,
    configure_deterministic_execution,
)
from burnlens.bounded_unet_training import (
    BoundedUNetTrainingError,
    PROTOCOL_PATH,
    _run_training_loop,
    build_training_config,
    load_model_weights,
    record_failed_attempt,
    render_training_html,
    render_training_png,
    save_model_weights,
    validate_training_entry,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "1" * 40


def _example(
    patch_id: str,
    event_group_id: str,
    offset: float,
    split_role: str = "train",
) -> ModelExample:
    values = torch.linspace(0, 1, 6 * 64 * 64, dtype=torch.float32)
    features = (values.reshape(6, 64, 64) + offset).clone()
    target = torch.zeros((1, 64, 64), dtype=torch.float32)
    target[:, 31:33, 31:33] = 1
    mask = torch.zeros((1, 64, 64), dtype=torch.bool)
    mask[:, 30:34, 30:34] = True
    input_valid = torch.ones((1, 64, 64), dtype=torch.bool)
    return ModelExample(
        patch_id=patch_id,
        event_group_id=event_group_id,
        split_role=split_role,
        inputs=features,
        target=target,
        loss_mask=mask,
        input_valid=input_valid,
    )


def _synthetic_rosters() -> tuple[list[ModelExample], list[ModelExample]]:
    training = [
        _example("train-green", "event-green-ridge-0684-cs-2020", 0.0),
        _example("train-tepee", "event-tepee-1144-ne-2018", 0.1),
    ]
    validation = [
        _example(
            "val-grandview",
            "event-grandview-0558-od-2021",
            0.2,
            "validation",
        ),
        _example(
            "val-mckay",
            "event-mckay-1035-ne-2017",
            0.3,
            "validation",
        ),
    ]
    return training, validation


def test_exact_protocol_entry_and_config() -> None:
    protocol = validate_training_entry(ROOT, PROTOCOL_PATH, SOURCE_COMMIT)
    assert protocol["protocol_id"] == "BOUNDED-UNET-EXPERIMENT-PROTOCOL-2026-001"
    config = build_training_config(
        ROOT,
        PROTOCOL_PATH,
        "2026-07-26T01:00:00Z",
        "BL-TEST-U04",
        SOURCE_COMMIT,
    )
    assert config["boundaries"]["test_arrays_opened"] is False
    assert config["compute_budget"]["substantive_run_count"] == 1


def test_protocol_entry_rejects_wrong_commit_or_path() -> None:
    with pytest.raises(BoundedUNetTrainingError, match="source commit"):
        validate_training_entry(ROOT, PROTOCOL_PATH, "bad")
    with pytest.raises(BoundedUNetTrainingError, match="path drift"):
        validate_training_entry(ROOT, Path("other.json"), SOURCE_COMMIT)


def test_model_only_weights_are_exact_and_strict() -> None:
    configure_deterministic_execution()
    model = BoundedUNet()
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        first = save_model_weights(root / "first.pt", model)
        second = save_model_weights(root / "second.pt", model)
        assert first["bytes"] == second["bytes"]
        assert first["sha256"] == second["sha256"]
        assert (root / "first.pt").read_bytes() == (root / "second.pt").read_bytes()
        loaded = BoundedUNet()
        load_model_weights(root / "first.pt", loaded)
        for name, tensor in model.state_dict().items():
            assert torch.equal(tensor, loaded.state_dict()[name])
        with pytest.raises(BoundedUNetTrainingError, match="already exist"):
            save_model_weights(root / "first.pt", model)


def test_two_epoch_internal_loop_replays_exactly() -> None:
    training, validation = _synthetic_rosters()
    with tempfile.TemporaryDirectory() as first_directory:
        first_root = Path(first_directory)
        first = _run_training_loop(
            first_root,
            training,
            validation,
            maximum_epochs=2,
        )
        first_weights = Path(first["working_receipts"]["weights"]["path"]).read_bytes()
        first_history = json.dumps(first["history"], sort_keys=True)
    training, validation = _synthetic_rosters()
    with tempfile.TemporaryDirectory() as second_directory:
        second_root = Path(second_directory)
        second = _run_training_loop(
            second_root,
            training,
            validation,
            maximum_epochs=2,
        )
        second_weights = Path(second["working_receipts"]["weights"]["path"]).read_bytes()
        second_history = json.dumps(second["history"], sort_keys=True)
    assert first["epoch_count"] == second["epoch_count"] == 2
    assert first["selected_epoch"] == second["selected_epoch"]
    assert first_history == second_history
    assert first_weights == second_weights
    assert first["roster"]["test_patch_ids_opened"] == []


def test_internal_loop_rejects_wrong_event_roster() -> None:
    training, validation = _synthetic_rosters()
    object.__setattr__(training[0], "event_group_id", "wrong")
    with tempfile.TemporaryDirectory() as directory:
        with pytest.raises(BoundedUNetTrainingError, match="roster drift"):
            _run_training_loop(
                Path(directory),
                training,
                validation,
                maximum_epochs=1,
            )


def test_training_render_is_offline_and_explicit() -> None:
    report = {
        "training": {"epoch_count": 2},
        "selection": {
            "selected_epoch": 2,
            "validation": {
                "event_class_macro_dice": 0.4,
                "masked_bce": 0.6,
            },
            "weights": {"sha256": "a" * 64},
        },
        "warnings": ["Validation selection is not a test evaluation."],
        "run_id": "BL-TEST-U04",
        "git_source_commit": SOURCE_COMMIT,
        "protocol": {"sha256": "b" * 64},
        "disposition": "candidate-frozen-pending-one-test-opening",
    }
    history = [
        {
            "epoch": 1,
            "train_masked_bce": 0.7,
            "validation": {
                "masked_bce": 0.65,
                "event_class_macro_dice": 0.35,
                "event_class_macro_iou": 0.25,
                "worst_event_macro_dice": 0.3,
            },
            "checkpoint_improved": True,
        },
        {
            "epoch": 2,
            "train_masked_bce": 0.6,
            "validation": {
                "masked_bce": 0.6,
                "event_class_macro_dice": 0.4,
                "event_class_macro_iou": 0.3,
                "worst_event_macro_dice": 0.32,
            },
            "checkpoint_improved": True,
        },
    ]
    html = render_training_html(report, history, "plot.png").decode("utf-8")
    png = render_training_png(report, history)
    assert "Ward Creek and Windigo test arrays remain unopened" in html
    assert "not independent ground truth" in html
    assert "http://" not in html and "https://" not in html
    assert html.count("<tr>") == 3
    assert png.startswith(b"\x89PNG\r\n\x1a\n")


def test_completed_run_cannot_gain_a_false_failure_receipt() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        run_id = "BL-TEST-COMPLETE"
        run_directory = root / "runs" / "phase-three" / run_id
        run_directory.mkdir(parents=True)
        (run_directory / "ATTEMPT-COMPLETE.json").write_text(
            "{}\n",
            encoding="utf-8",
        )
        record_failed_attempt(
            root,
            Path("runs") / "phase-three" / run_id,
            "2026-07-26T01:00:00Z",
            run_id,
            SOURCE_COMMIT,
            RuntimeError("must not be recorded"),
        )
        assert not (run_directory / "ATTEMPT-FAILED.json").exists()
