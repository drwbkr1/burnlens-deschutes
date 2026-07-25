from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import numpy as np

from burnlens.baseline_evaluation import (
    Example,
    _false_color,
    _selection_key,
    evaluate,
    fit_signal_family,
    predict,
    render_evaluation_html,
    score,
)


def _example(
    patch_id: str,
    event_id: str,
    role: str,
    burned_score: float,
    background_score: float,
) -> Example:
    features = np.zeros((6, 2, 2), dtype=np.float32)
    state = np.array([[0, 1], [0, 1]], dtype=np.uint8)
    loss = np.ones((2, 2), dtype=bool)
    pre_nbr = 0.5
    pre_b8a = (1 + pre_nbr) / 2
    pre_b12 = (1 - pre_nbr) / 2
    features[1] = pre_b8a
    features[2] = pre_b12
    target_dnbr = np.array(
        [
            [background_score, burned_score],
            [background_score, burned_score],
        ],
        dtype=np.float32,
    )
    post_nbr = pre_nbr - target_dnbr
    features[4] = (1 + post_nbr) / 2
    features[5] = (1 - post_nbr) / 2
    features[0] = 0.2
    features[3] = np.array([[0.2, 0.4], [0.2, 0.4]], dtype=np.float32)
    return Example(patch_id, event_id, role, features, state, loss)


class BaselineEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.examples = [
            _example("a", "event-a", "train", 0.6, 0.1),
            _example("b", "event-b", "train", 0.7, 0.2),
        ]

    def test_dnbr_and_rbr_scores_follow_preregistered_formulas(self) -> None:
        dnbr = score(self.examples[0].features, "dnbr-threshold")
        rbr = score(self.examples[0].features, "rbr-threshold")
        self.assertTrue(np.allclose(dnbr[0, 0], 0.1))
        self.assertTrue(np.allclose(dnbr[0, 1], 0.6))
        self.assertTrue(np.allclose(rbr, dnbr / 1.501))

    def test_threshold_fit_uses_midpoints_and_separates_synthetic_cores(self) -> None:
        fitted = fit_signal_family(self.examples, "dnbr-threshold")
        self.assertGreater(fitted["candidate_threshold_count"], 0)
        self.assertGreater(fitted["chosen_threshold"], 0.2)
        self.assertLess(fitted["chosen_threshold"], 0.6)
        self.assertEqual(
            fitted["training_metrics"]["event_class_macro_dice"], 1.0
        )

    def test_metrics_preserve_event_class_denominators(self) -> None:
        result = evaluate(self.examples, "dnbr-threshold", 0.4)
        self.assertEqual(result["event_count"], 2)
        self.assertEqual(result["core_pixels"], 8)
        self.assertEqual(result["event_class_macro_dice"], 1.0)
        self.assertEqual(
            result["events"][0]["classes"][1]["dice_denominator"], 4
        )

    def test_constant_references_are_eligible_and_explicit(self) -> None:
        background = evaluate(self.examples, "constant-background", None)
        burned = evaluate(self.examples, "constant-burned", None)
        self.assertEqual(background["predicted_burned_pixels"], 0)
        self.assertEqual(burned["predicted_burned_pixels"], 8)

    def test_selection_key_prefers_validation_before_training(self) -> None:
        weak_validation = {
            "family_id": "rbr-threshold",
            "validation_metrics": {
                "event_class_macro_dice": 0.4,
                "event_class_macro_iou": 0.3,
                "worst_event_macro_dice": 0.2,
            },
            "training_metrics": {"event_class_macro_dice": 1.0},
        }
        strong_validation = {
            "family_id": "dnbr-threshold",
            "validation_metrics": {
                "event_class_macro_dice": 0.5,
                "event_class_macro_iou": 0.4,
                "worst_event_macro_dice": 0.3,
            },
            "training_metrics": {"event_class_macro_dice": 0.6},
        }
        self.assertGreater(
            _selection_key(strong_validation), _selection_key(weak_validation)
        )

    def test_prediction_rejects_missing_signal_threshold(self) -> None:
        with self.assertRaisesRegex(Exception, "threshold"):
            predict(self.examples[0], "dnbr-threshold", None)

    def test_false_color_neutralizes_nonfinite_excluded_pixels(self) -> None:
        features = self.examples[0].features.copy()
        features[:, 0, 0] = np.nan
        image = _false_color(features, 0)
        self.assertEqual(image.getpixel((0, 0)), (218, 213, 201))

    def test_html_preserves_claim_and_training_boundaries(self) -> None:
        report = {
            "selected": {"family_id": "dnbr-threshold"},
            "selected_test_metrics": {
                "event_class_macro_dice": 0.5,
                "event_class_macro_iou": 0.4,
                "events": [
                    {
                        "event_group_id": "event-a",
                        "core_pixels": 4,
                        "macro_dice": 0.5,
                        "macro_iou": 0.4,
                    }
                ],
            },
            "test_family_metrics": [
                {
                    "family_id": "dnbr-threshold",
                    "event_class_macro_dice": 0.5,
                    "event_class_macro_iou": 0.4,
                    "event_macro_dice_range": [0.5, 0.5],
                }
            ],
            "limitations": [
                "Candidate construction may favor spectral separability."
            ],
            "git_source_commit": "a" * 40,
            "run_id": "BL-TEST",
        }
        html = render_evaluation_html(report, "test.png")
        self.assertIn("Training remains unauthorized", html)
        self.assertIn("not independent ground truth", html)
        self.assertIn("favor spectral separability", html)
        self.assertNotIn("generalizes", html.lower())


if __name__ == "__main__":
    unittest.main()
