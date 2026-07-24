from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from burnlens.six_event_dataset_sufficiency import (
    DECISION,
    EVENTS,
    build_audit_contract,
    build_audit_decision,
    build_candidate_manifest,
    prospective_partitions,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]


class SixEventDatasetSufficiencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candidate = build_candidate_manifest(
            ROOT,
            "2026-07-24T18:00:00Z",
            "BL-TEST-SIX-EVENT-DATASET-SUFFICIENCY",
            "a" * 40,
        )
        candidate_bytes = (json.dumps(cls.candidate, indent=2) + "\n").encode("utf-8")
        cls.contract = build_audit_contract(cls.candidate, hashlib.sha256(candidate_bytes).hexdigest())
        contract_bytes = (json.dumps(cls.contract, indent=2) + "\n").encode("utf-8")
        cls.decision = build_audit_decision(cls.contract, hashlib.sha256(contract_bytes).hexdigest())

    def test_exact_six_event_region_inventory(self) -> None:
        inventory = self.candidate["inventory"]
        self.assertEqual(inventory["event_groups"], 6)
        self.assertEqual(inventory["owner_approved_regions"], 12)
        self.assertEqual(inventory["class_counts"], {"background": 6, "burned": 6})
        self.assertEqual(inventory["accepted_core_pixels"], 286)
        self.assertEqual(inventory["excluded_unknown_ring_pixels"], 533)
        self.assertLess(inventory["maximum_event_core_share_percent"], 50)

    def test_every_raster_is_exact_contiguous_and_unknown_aware(self) -> None:
        rasters = [
            candidate
            for event in self.candidate["events"]
            for candidate in event["candidates"]
        ]
        self.assertEqual(len(rasters), 12)
        self.assertEqual(len({item["raster"]["sha256"] for item in rasters}), 12)
        for candidate in rasters:
            contract = candidate["raster_contract"]
            self.assertEqual(contract["crs"], "EPSG:32610")
            self.assertEqual(contract["nodata"], 255)
            self.assertIn(1, contract["class_domain"])
            self.assertIn(2, contract["class_domain"])
            self.assertTrue(contract["core_is_one_8_connected_component"])
            self.assertGreater(contract["unknown_ring_pixels"], 0)

    def test_regime_replication_blocks_every_2_2_2_assignment(self) -> None:
        partition = self.candidate["partition_feasibility"]
        self.assertEqual(partition["total_2_2_2_assignments"], 90)
        self.assertEqual(partition["valid_assignments"], 0)
        self.assertIn(
            "regime_unique_to_one_role:sentinel2-nifc-incident-context-v1",
            partition["closest_assignment"]["violations"],
        )
        self.assertIn(
            "program_unique_to_one_role:NIFC_WFIGS",
            partition["closest_assignment"]["violations"],
        )
        self.assertEqual(
            self.candidate["source_regime_counts"],
            {
                "sentinel2-baer-mtbs-ravg-current-v1": 3,
                "sentinel2-mtbs-current-v1": 2,
                "sentinel2-nifc-incident-context-v1": 1,
            },
        )

    def test_partition_logic_can_pass_when_regimes_are_replicated(self) -> None:
        synthetic = []
        for index in range(6):
            synthetic.append(
                {
                    "event_group_id": f"event-{index}",
                    "source_regime": f"regime-{index % 3}",
                    "source_programs": ["shared-program"],
                    "never_tuned_transfer": index >= 2,
                }
            )
        self.assertGreater(prospective_partitions(synthetic)["valid_assignments"], 0)

    def test_audit_blocks_without_authorizing_training(self) -> None:
        self.assertEqual(self.decision["decision"], "block")
        self.assertFalse(self.decision["training_authorized"])
        self.assertEqual(
            self.decision["blocking_required_gate_ids"],
            ["evaluation-design", "leakage-and-split-fitness"],
        )
        self.assertIn("valid-2-2-2-assignments", self.decision["failed_blocking_count_checks"])
        self.assertIn("unique-exact-source-regimes", self.decision["failed_blocking_count_checks"])
        self.assertIn("unique-source-programs", self.decision["failed_blocking_count_checks"])
        self.assertEqual(self.contract["template"], False)
        self.assertFalse(self.contract["training_authorization"]["authorized_by_this_audit"])

    def test_production_outputs_are_complete_and_content_safe(self) -> None:
        test_root = ROOT / "downloads" / "phase-two" / "runs" / "P2O5-T02-TEST"
        test_root.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(dir=test_root) as temporary:
            root = Path(temporary)
            records = root / "records"
            public = root / "public"
            outputs = write_outputs(
                ROOT,
                records,
                public,
                "2026-07-24T18:00:00Z",
                "BL-TEST-SIX-EVENT-DATASET-SUFFICIENCY",
                "a" * 40,
            )
            report = json.loads(outputs["json"].read_text(encoding="utf-8"))
            self.assertEqual(report["decision"], DECISION)
            self.assertEqual(report["audit_decision"], "block")
            self.assertFalse(report["minimum_remediation"]["terminal_fallback_activated"])
            self.assertTrue(all(value is False for value in report["boundaries"].values()))
            serialized = outputs["json"].read_text(encoding="utf-8").lower()
            for forbidden in ("c:\\users", "owner_decision", "private_reconciliation"):
                self.assertNotIn(forbidden, serialized)
            for output in report["outputs"]:
                path = ROOT / output["path"]
                payload = path.read_bytes()
                self.assertEqual(len(payload), output["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), output["sha256"])

    def test_roster_is_stable(self) -> None:
        self.assertEqual(len(EVENTS), 6)
        self.assertEqual(sum(bool(item["never_tuned_transfer"]) for item in EVENTS), 3)


if __name__ == "__main__":
    unittest.main()
