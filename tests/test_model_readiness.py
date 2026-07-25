from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from burnlens.model_readiness import (
    INPUTS,
    ModelReadinessError,
    audit,
    render_html,
)


ROOT = Path(__file__).resolve().parents[1]
COMMIT = "a" * 40
GENERATED = "2026-07-25T20:40:03Z"
RUN_ID = "BL-TEST-P2O5-T03-U06"


class ModelReadinessTests(unittest.TestCase):
    def test_exact_package_authorizes_only_bounded_rejection_first_model(self) -> None:
        report, decision, contract = audit(
            ROOT, GENERATED, RUN_ID, COMMIT
        )
        self.assertTrue(report["boundaries"]["all_gates_passed"])
        self.assertEqual(decision["decision"], "AUTHORIZE_BOUNDED_UNET")
        self.assertEqual(
            decision["qualifier"], "REJECTION_FIRST_SINGLE_MODEL_EXPERIMENT"
        )
        self.assertTrue(decision["training_authorized"])
        self.assertFalse(decision["claims"]["model_exists"])
        self.assertFalse(decision["claims"]["model_adds_value"])
        self.assertEqual(contract["architecture"]["model_count"], 1)
        self.assertFalse(
            contract["authorization"]["architecture_search_authorized"]
        )
        self.assertFalse(
            contract["authorization"]["hyperparameter_search_authorized"]
        )
        self.assertEqual(
            contract["optimization"]["framework"], "torch==2.13.0"
        )
        self.assertEqual(contract["optimization"]["device"], "cpu")

    def test_contract_preserves_unknown_and_test_boundaries(self) -> None:
        _, _, contract = audit(ROOT, GENERATED, RUN_ID, COMMIT)
        self.assertEqual(
            contract["data_contract"]["excluded_states"],
            {"unknown": 2, "nodata": 255},
        )
        self.assertFalse(contract["authorization"]["test_tuning_authorized"])
        self.assertIn(
            "one model-evaluation opening",
            contract["checkpoint_selection"]["test_access"],
        )
        self.assertIn(
            "cannot become the analytical winner",
            contract["evaluation"]["analytical_winner_rule"],
        )

    def test_audit_fails_closed_on_any_bound_input_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for relative, _ in INPUTS.values():
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            relative = INPUTS["baseline_evaluation"][0]
            with (root / relative).open("ab") as handle:
                handle.write(b"\n")
            with self.assertRaisesRegex(
                ModelReadinessError, "baseline_evaluation input hash drift"
            ):
                audit(root, GENERATED, RUN_ID, COMMIT)

    def test_html_is_responsive_and_claim_bound(self) -> None:
        report, decision, _ = audit(ROOT, GENERATED, RUN_ID, COMMIT)
        html = render_html(report, decision, "decision.png")
        self.assertIn("width=device-width", html)
        self.assertIn("overflow-x:auto", html)
        self.assertIn("The baseline still leads", html)
        self.assertIn("not independent ground truth", html)
        self.assertIn("No model-value", html)
        self.assertNotIn("submission-ready", html.lower())


if __name__ == "__main__":
    unittest.main()
