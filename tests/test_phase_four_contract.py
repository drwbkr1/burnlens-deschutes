from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from burnlens.phase_four_contract import (
    ACCEPTED_METHOD,
    CONTRACT_PATH,
    MODEL_THRESHOLD,
    PhaseFourContractError,
    RBR_THRESHOLD,
    REJECTED_MODEL,
    load_contract,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]


class PhaseFourContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = load_contract(ROOT)

    def test_exact_contract_and_frozen_bytes_pass_without_array_loading(self) -> None:
        self.assertEqual(
            self.contract["contract_id"],
            "PHASE-FOUR-INTEGRATION-CONTRACT-2026-001",
        )
        self.assertEqual(len(self.contract["integration_roster"]), 2)
        self.assertTrue((ROOT / CONTRACT_PATH).is_file())

    def test_rbr_is_primary_and_unet_is_rejected_diagnostic(self) -> None:
        accepted = self.contract["analytical_methods"]["accepted"]
        diagnostic = self.contract["analytical_methods"]["rejected_diagnostic"]
        self.assertEqual(accepted["version"], ACCEPTED_METHOD)
        self.assertEqual(accepted["threshold"], RBR_THRESHOLD)
        self.assertEqual(diagnostic["version"], REJECTED_MODEL)
        self.assertEqual(diagnostic["threshold"], MODEL_THRESHOLD)
        self.assertFalse(diagnostic["accepted"])
        self.assertFalse(diagnostic["outperformed_rbr"])

    def test_states_outputs_and_no_phase_3b_boundary_are_explicit(self) -> None:
        self.assertEqual(
            set(self.contract["run_state_taxonomy"]),
            {
                "accepted-baseline",
                "degraded",
                "no-detection",
                "fallback-baseline",
                "failed",
                "withheld",
            },
        )
        self.assertFalse(self.contract["boundaries"]["phase_3b_created"])
        self.assertFalse(
            self.contract["boundaries"]["second_experiment_planned"]
        )
        self.assertFalse(
            self.contract["boundaries"]["second_experiment_implemented"]
        )

    def test_semantic_drift_fails_closed(self) -> None:
        changed = deepcopy(self.contract)
        changed["analytical_methods"]["accepted"]["threshold"] = 0.0
        with self.assertRaisesRegex(PhaseFourContractError, "RBR threshold drift"):
            validate_contract(changed, repository_root=ROOT)


if __name__ == "__main__":
    unittest.main()
