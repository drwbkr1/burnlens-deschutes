from __future__ import annotations

import json
from pathlib import Path
import unittest

from burnlens.dataset_build_contract import (
    CANDIDATE_SHA256,
    EXPECTED_EVENT_IDS,
    FEATURE_CHANNELS,
    build_audit,
    build_contract,
)


ROOT = Path(__file__).resolve().parents[1]


class DatasetBuildContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_contract(
            ROOT,
            "2026-07-25T20:00:00Z",
            "BL-TEST-P2O5-T03-U01",
            "a" * 40,
        )
        cls.audit = build_audit(ROOT, cls.contract, "b" * 64)

    def test_exact_candidate_and_event_roster_are_bound(self) -> None:
        self.assertEqual(
            self.contract["candidate"]["sha256"], CANDIDATE_SHA256
        )
        self.assertEqual(
            tuple(self.contract["eligible_event_group_ids"]),
            EXPECTED_EVENT_IDS,
        )
        self.assertEqual(len(self.contract["source_pairs"]), 6)

    def test_native_six_channel_contract_has_no_resampling(self) -> None:
        input_contract = self.contract["input_contract"]
        self.assertEqual(
            tuple(input_contract["channel_order"]), FEATURE_CHANNELS
        )
        self.assertEqual(
            input_contract["native_grid"],
            {
                "crs": "EPSG:32610",
                "resolution_m": 20,
                "resampling": "prohibited",
                "reprojection": "prohibited",
                "mosaicking": "prohibited",
            },
        )
        for event in self.contract["source_pairs"]:
            self.assertEqual(
                [item["temporal_role"] for item in event["products"]],
                ["pre", "post"],
            )
            for product in event["products"]:
                self.assertEqual(
                    set(product["members"]),
                    {"B04", "B8A", "B12", "SCL"},
                )

    def test_unreviewed_and_unknown_pixels_never_become_background(self) -> None:
        labels = self.contract["label_contract"]
        self.assertFalse(labels["unknown_is_background"])
        self.assertFalse(labels["outside_candidate_is_background"])
        self.assertIn("state is 0 or 1", labels["loss_mask"])
        self.assertEqual(labels["metric_mask"], "byte-identical to loss_mask")

    def test_split_and_test_boundaries_are_frozen_before_materialization(self) -> None:
        self.assertTrue(self.contract["patch_contract"]["split_before_patch"])
        self.assertTrue(self.contract["split_contract"]["group_before_patch"])
        self.assertEqual(
            self.contract["split_contract"]["valid_assignment_count"], 54
        )
        self.assertEqual(
            self.contract["evaluation_contract"]["test_open_count"], 1
        )
        self.assertEqual(
            self.contract["boundaries"],
            {
                "dataset_created": False,
                "split_created": False,
                "baseline_created": False,
                "model_created": False,
                "training_authorized": False,
                "independent_ground_truth_claimed": False,
                "generalization_claimed": False,
            },
        )

    def test_audit_is_non_count_only_and_never_authorizes_training(self) -> None:
        self.assertFalse(self.audit["template"])
        self.assertEqual(
            self.audit["candidate_manifest_sha256"], CANDIDATE_SHA256
        )
        self.assertGreaterEqual(len(self.audit["required_gate_ids"]), 8)
        self.assertTrue(all(gate["status"] == "pass" for gate in self.audit["gates"]))
        self.assertEqual(
            self.audit["training_authorization"],
            {
                "separate_approval_required": True,
                "authorized_by_this_audit": False,
            },
        )

    def test_generated_contract_is_json_serializable(self) -> None:
        encoded = json.dumps(self.contract, ensure_ascii=False)
        self.assertIn("burnlens-dataset-v0.1.0", encoded)


if __name__ == "__main__":
    unittest.main()
