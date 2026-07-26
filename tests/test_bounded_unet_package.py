from __future__ import annotations

from pathlib import Path

import numpy as np

from burnlens.bounded_unet_package import (
    WEIGHTS_SHA256,
    build_decision,
    build_inference_contract,
    build_model_card,
    render_decision_html,
    render_decision_png,
    verify_immutable_evaluation,
)


ROOT = Path(__file__).resolve().parents[1]


def _replay() -> dict[str, object]:
    return {
        "history_exact": True,
        "weights_bytes_exact": True,
        "selected_epoch": 10,
        "final_epoch": 35,
    }


def _evaluation() -> dict[str, object]:
    return {
        "test_source_arrays_reopened": False,
        "baseline_decision": "BELOW_RBR_REJECT_AS_ANALYTICAL_WINNER",
    }


def test_immutable_evaluation_rechecks_outputs_without_dataset_arrays(
    monkeypatch,
) -> None:
    original = np.load
    opened: list[str] = []

    def guarded(path: object, *args: object, **kwargs: object) -> np.ndarray:
        normalized = str(path).replace("\\", "/").lower()
        assert "/samples/datasets/" not in normalized
        opened.append(normalized)
        return original(path, *args, **kwargs)

    monkeypatch.setattr(np, "load", guarded)
    result = verify_immutable_evaluation(ROOT)
    assert result["prediction_arrays_checked"] == 8
    assert result["test_source_arrays_reopened"] is False
    assert result["test_open_count"] == 1
    assert len(opened) == 8


def test_decision_retains_baseline_and_model_as_rejected_diagnostic() -> None:
    decision = build_decision(_replay(), _evaluation())
    assert decision["decision"] == "reject-model-retain-baseline"
    assert decision["model_accepted"] is False
    assert (
        decision["phase_four_recommendation"]["route"]
        == "baseline-primary-with-rejected-model-diagnostic"
    )
    assert decision["claims"]["valid_trained_model_artifact"] is True
    assert decision["claims"]["model_added_value"] is False


def test_inference_contract_is_bounded_and_preserves_model_status() -> None:
    contract = build_inference_contract()
    assert contract["inputs"]["shape"] == [6, 64, 64]
    assert contract["outputs"]["binary_diagnostic"] == "probability >= 0.5"
    assert contract["analytical_status"] == "rejected-as-analytical-winner"
    assert "use as the accepted analytical perimeter" in contract["prohibited"]


def test_model_card_and_decision_render_are_offline_and_explicit() -> None:
    decision = build_decision(_replay(), _evaluation())
    card = build_model_card("a" * 40, "BL-TEST-U06", decision).decode("utf-8")
    html = render_decision_html(
        decision,
        _replay(),
        "decision.png",
        "a" * 40,
        "BL-TEST-U06",
    ).decode("utf-8")
    png = render_decision_png(decision)
    assert "rejected as the analytical winner" in card
    assert WEIGHTS_SHA256 in card
    assert "The model is reproducible. It is not the winner." in html
    assert "No second test opening" in html
    assert "http://" not in html and "https://" not in html
    assert "<script" not in html
    assert png.startswith(b"\x89PNG\r\n\x1a\n")
