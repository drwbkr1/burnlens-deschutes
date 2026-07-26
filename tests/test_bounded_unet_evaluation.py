from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
from unittest import mock

import numpy as np
import pytest
import torch

from burnlens.bounded_unet import BoundedUNet, ModelExample
from burnlens.bounded_unet_evaluation import (
    BASELINE_PATH,
    CONFIG_PATH,
    DATASET_MANIFEST_PATH,
    ENVIRONMENT_CAPTURE_PATH,
    MODEL_VERSION,
    NORMALIZATION_PATH,
    SELECTION_PATH,
    TRAINING_REPORT_PATH,
    WEIGHTS_PATH,
    BoundedUNetEvaluationError,
    _assert_opening_unused,
    _baseline_comparison,
    build_test_authorization,
    evaluate_examples,
    render_evaluation_html,
    render_evaluation_png,
)


ROOT = Path(__file__).resolve().parents[1]


def _example(
    patch_id: str,
    event_id: str,
    truth_values: tuple[int, int],
) -> ModelExample:
    inputs = torch.zeros((6, 64, 64), dtype=torch.float32)
    target = torch.zeros((1, 64, 64), dtype=torch.float32)
    mask = torch.zeros((1, 64, 64), dtype=torch.bool)
    target[0, 0, 0] = truth_values[0]
    target[0, 0, 1] = truth_values[1]
    mask[0, 0, :2] = True
    return ModelExample(
        patch_id=patch_id,
        event_group_id=event_id,
        split_role="validation",
        inputs=inputs,
        target=target,
        loss_mask=mask,
        input_valid=torch.ones((1, 64, 64), dtype=torch.bool),
    )


def _zero_model() -> BoundedUNet:
    model = BoundedUNet()
    with torch.no_grad():
        for parameter in model.parameters():
            parameter.zero_()
    return model


def test_metrics_include_exact_denominators_thresholds_and_calibration() -> None:
    examples = [
        _example("patch-a", "event-a", (0, 1)),
        _example("patch-b", "event-b", (0, 1)),
    ]
    metrics, arrays = evaluate_examples(_zero_model(), examples)
    assert metrics["core_pixels"] == 4
    assert metrics["true_burned_pixels"] == 2
    assert metrics["predicted_burned_pixels"] == 4
    assert metrics["event_class_macro_dice"] == pytest.approx(1 / 3)
    assert metrics["event_class_macro_iou"] == pytest.approx(0.25)
    assert metrics["worst_event_macro_dice"] == pytest.approx(1 / 3)
    assert [item["threshold"] for item in metrics["threshold_sensitivity"]] == [
        0.25,
        0.5,
        0.75,
    ]
    assert (
        metrics["probability_calibration"]["status"]
        == "descriptive-only-not-calibrated"
    )
    assert metrics["probability_calibration"]["brier_score"] == pytest.approx(0.25)
    assert set(arrays) == {"patch-a", "patch-b"}
    background = metrics["events"][0]["classes"][0]
    assert background["support"] == 1
    assert background["predicted"] == 0
    assert background["precision"] is None
    assert background["recall"] == 0.0


def test_authorization_is_exact_metadata_only_and_no_overwrite() -> None:
    with tempfile.TemporaryDirectory(prefix="burnlens-u05-auth-") as directory:
        root = Path(directory)
        for relative in (
            CONFIG_PATH,
            WEIGHTS_PATH,
            SELECTION_PATH,
            TRAINING_REPORT_PATH,
            ENVIRONMENT_CAPTURE_PATH,
            BASELINE_PATH,
            NORMALIZATION_PATH,
            DATASET_MANIFEST_PATH,
        ):
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, destination)
        output = (
            root
            / "records/phase-three/test-openings/"
            "BOUNDED-UNET-TEST-AUTHORIZATION-2026-001.json"
        )
        with mock.patch("numpy.load") as array_load:
            receipt = build_test_authorization(
                root, output, "TEST-OPEN-P3O1-T01-U05-2026-001"
            )
        array_load.assert_not_called()
        value = json.loads(output.read_text(encoding="utf-8"))
        assert receipt["sha256"]
        assert value["status"] == "AUTHORIZED_NOT_OPENED"
        assert value["open_count_before"] == 0
        assert value["open_count_authorized"] == 1
        assert len(value["test_patch_ids"]) == 4
        assert value["test_event_group_ids"] == [
            "event-ward-creek-2019",
            "event-windigo-2022",
        ]
        with pytest.raises(BoundedUNetEvaluationError, match="overwrite"):
            build_test_authorization(
                root, output, "TEST-OPEN-P3O1-T01-U05-2026-001"
            )


def test_render_is_offline_explicit_and_geospatially_bound() -> None:
    examples = [
        _example("patch-a", "event-a", (0, 1)),
        _example("patch-b", "event-b", (0, 1)),
    ]
    model = _zero_model()
    metrics, arrays = evaluate_examples(model, examples)
    patches = {
        item.patch_id: {
            "candidate_id": item.patch_id,
            "event_group_id": item.event_group_id,
            "proposed_class": "synthetic",
            "crs": "EPSG:32610",
            "transform": [20.0, 0.0, 600000.0, 0.0, -20.0, 4900000.0],
            "window": {
                "row_offset": 0,
                "column_offset": 0,
                "height": 64,
                "width": 64,
            },
        }
        for item in examples
    }
    report = {
        "test_metrics": metrics,
        "baseline_comparison": {
            **_baseline_comparison(ROOT, metrics),
            "status": "BELOW_RBR_REJECT_AS_ANALYTICAL_WINNER",
        },
        "patches": patches,
        "git_source_commit": "a" * 40,
        "run_id": "BL-TEST-U05",
    }
    html = render_evaluation_html(report, "evaluation.png").decode("utf-8")
    png = render_evaluation_png(
        report,
        examples,
        arrays,
        np.zeros(6, dtype=np.float32),
        np.ones(6, dtype=np.float32),
    )
    assert "prototype cores" in html
    assert "Analytical test-open count: 1" in html
    assert "No model, threshold, or code retry is authorized" in html
    assert "EPSG:32610" in html
    assert "http://" not in html and "https://" not in html
    assert "<script" not in html
    assert png.startswith(b"\x89PNG\r\n\x1a\n")


def test_consumed_opening_blocks_any_retry() -> None:
    with tempfile.TemporaryDirectory(prefix="burnlens-u05-consumed-") as directory:
        root = Path(directory)
        receipt = root / "runs/phase-three/run-one/OPENING-CONSUMED.json"
        receipt.parent.mkdir(parents=True)
        receipt.write_text(
            json.dumps(
                {
                    "opening_id": "TEST-OPEN-P3O1-T01-U05-2026-001",
                    "status": "OPENING_CONSUMED",
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        with pytest.raises(
            BoundedUNetEvaluationError, match="already consumed"
        ):
            _assert_opening_unused(
                root, "TEST-OPEN-P3O1-T01-U05-2026-001"
            )
