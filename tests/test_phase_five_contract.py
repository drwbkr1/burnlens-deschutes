from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from burnlens.phase_five_contract import (
    ACCEPTED_METHOD,
    CONTRACT_ID,
    CONTRACT_PATH,
    PhaseFiveContractError,
    REJECTED_MODEL,
    UNITS,
    load_contract,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]


class PhaseFiveContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = load_contract(ROOT)

    def test_exact_contract_and_frozen_release_bytes_pass(self) -> None:
        self.assertEqual(self.contract["contract_id"], CONTRACT_ID)
        self.assertEqual(
            [item["unit_id"] for item in self.contract["evidence_units"]],
            UNITS,
        )
        self.assertTrue((ROOT / CONTRACT_PATH).is_file())

    def test_analytical_route_remains_baseline_primary(self) -> None:
        posture = self.contract["analytical_posture"]
        self.assertEqual(posture["accepted_method"], ACCEPTED_METHOD)
        self.assertEqual(posture["rejected_diagnostic_model"], REJECTED_MODEL)
        self.assertFalse(posture["rejected_model_accepted"])
        self.assertFalse(posture["rejected_model_outperformed_rbr"])

    def test_failure_accessibility_and_budget_standards_are_explicit(self) -> None:
        self.assertEqual(
            len(
                self.contract["failure_injection_standard"][
                    "required_injections"
                ]
            ),
            5,
        )
        self.assertTrue(
            self.contract["accessibility_standard"][
                "browser_policy_bypass_prohibited"
            ]
        )
        self.assertEqual(
            self.contract["performance_budgets"]["external_runtime_requests_max"],
            0,
        )

    def test_model_superiority_drift_fails_closed(self) -> None:
        changed = deepcopy(self.contract)
        changed["analytical_posture"]["rejected_model_outperformed_rbr"] = True
        with self.assertRaisesRegex(
            PhaseFiveContractError,
            "model-superiority claim is prohibited",
        ):
            validate_contract(changed, repository_root=ROOT)

    def test_failure_roster_drift_fails_closed(self) -> None:
        changed = deepcopy(self.contract)
        changed["failure_injection_standard"]["required_injections"].pop()
        with self.assertRaisesRegex(
            PhaseFiveContractError,
            "failure injection roster drift",
        ):
            validate_contract(changed, repository_root=ROOT)

    def test_browser_policy_bypass_fails_closed(self) -> None:
        changed = deepcopy(self.contract)
        changed["accessibility_standard"][
            "browser_policy_bypass_prohibited"
        ] = False
        with self.assertRaisesRegex(
            PhaseFiveContractError,
            "browser policy bypass must remain prohibited",
        ):
            validate_contract(changed, repository_root=ROOT)


if __name__ == "__main__":
    unittest.main()
