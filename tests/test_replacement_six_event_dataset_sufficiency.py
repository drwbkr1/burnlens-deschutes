from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from burnlens.replacement_six_event_dataset_sufficiency import (
    DECISION,
    EVENTS,
    LABEL_SET_VERSION,
    REPORT_ID,
    SixEventDatasetSufficiencyError,
    build_audit_contract,
    build_audit_decision,
    build_candidate_manifest,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_REPORT = (
    ROOT
    / "samples/labels/readiness/phase-two/"
    f"{REPORT_ID}.json"
)


class ReplacementSixEventDatasetSufficiencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candidate = build_candidate_manifest(
            ROOT,
            "2026-07-25T05:30:00Z",
            "BL-TEST-REPLACEMENT-SIX-EVENT-SUFFICIENCY",
            "a" * 40,
        )
        candidate_bytes = (
            json.dumps(cls.candidate, indent=2, ensure_ascii=False) + "\n"
        ).encode("utf-8")
        cls.contract = build_audit_contract(
            cls.candidate,
            hashlib.sha256(candidate_bytes).hexdigest(),
        )
        contract_bytes = (
            json.dumps(cls.contract, indent=2, ensure_ascii=False) + "\n"
        ).encode("utf-8")
        cls.decision = build_audit_decision(
            cls.contract,
            hashlib.sha256(contract_bytes).hexdigest(),
        )

    def test_exact_replacement_roster_excludes_darlene(self) -> None:
        event_ids = [
            event["event_group_id"]
            for event in self.candidate["events"]
        ]
        self.assertEqual(
            event_ids,
            [
                "event-mckay-1035-ne-2017",
                "event-tepee-1144-ne-2018",
                "event-green-ridge-0684-cs-2020",
                "event-grandview-0558-od-2021",
                "event-windigo-2022",
                "event-ward-creek-2019",
            ],
        )
        self.assertNotIn("event-darlene3-or-2024", event_ids)
        self.assertEqual(
            self.candidate["excluded_event_groups"],
            [
                {
                    "event_group_id": "event-darlene3-or-2024",
                    "reason": (
                        "Unique NIFC context regime excluded under issue #554; "
                        "historical evidence remains immutable."
                    ),
                }
            ],
        )

    def test_exact_inventory_and_source_regime_replication(self) -> None:
        inventory = self.candidate["inventory"]
        self.assertEqual(inventory["event_groups"], 6)
        self.assertEqual(inventory["owner_approved_regions"], 12)
        self.assertEqual(
            inventory["class_counts"],
            {"background": 6, "burned": 6},
        )
        self.assertEqual(inventory["accepted_core_pixels"], 287)
        self.assertEqual(inventory["accepted_core_area_hectares"], 11.48)
        self.assertEqual(inventory["excluded_unknown_ring_pixels"], 531)
        self.assertAlmostEqual(
            inventory["maximum_event_core_share_percent"],
            20.5575,
        )
        self.assertEqual(
            self.candidate["source_regime_counts"],
            {
                "sentinel2-baer-mtbs-ravg-current-v1": 3,
                "sentinel2-mtbs-current-v1": 3,
            },
        )
        self.assertEqual(
            self.candidate["source_program_counts"],
            {
                "BAER": 3,
                "COPERNICUS_SENTINEL_2": 6,
                "MTBS": 6,
                "RAVG": 3,
            },
        )

    def test_every_raster_is_exact_contiguous_and_unknown_aware(self) -> None:
        rasters = [
            candidate
            for event in self.candidate["events"]
            for candidate in event["candidates"]
        ]
        self.assertEqual(len(rasters), 12)
        self.assertEqual(
            len({item["raster"]["sha256"] for item in rasters}),
            12,
        )
        for candidate in rasters:
            contract = candidate["raster_contract"]
            self.assertEqual(contract["crs"], "EPSG:32610")
            self.assertEqual(contract["nodata"], 255)
            self.assertIn(1, contract["class_domain"])
            self.assertIn(2, contract["class_domain"])
            self.assertTrue(contract["core_is_one_8_connected_component"])
            self.assertGreater(contract["unknown_ring_pixels"], 0)

    def test_frozen_partition_logic_has_54_valid_assignments(self) -> None:
        partition = self.candidate["partition_feasibility"]
        self.assertEqual(partition["total_2_2_2_assignments"], 90)
        self.assertEqual(partition["valid_assignments"], 54)
        self.assertEqual(
            partition["closest_assignment"]["violations"],
            [],
        )
        self.assertTrue(
            any(
                event["never_tuned_transfer"]
                for event in self.candidate["events"]
            )
        )

    def test_all_required_audit_gates_pass_without_training(self) -> None:
        self.assertEqual(
            {gate["status"] for gate in self.contract["gates"]},
            {"pass"},
        )
        self.assertEqual(self.decision["decision"], "pass")
        self.assertEqual(
            self.decision["blocking_required_gate_ids"],
            [],
        )
        self.assertEqual(
            self.decision["deferred_required_gate_ids"],
            [],
        )
        self.assertEqual(
            self.decision["failed_blocking_count_checks"],
            [],
        )
        self.assertTrue(
            all(
                result["satisfied"]
                for result in self.decision["count_results"]
            )
        )
        self.assertFalse(self.decision["training_authorized"])
        self.assertFalse(
            self.contract["training_authorization"][
                "authorized_by_this_audit"
            ]
        )

    def test_production_outputs_are_complete_safe_and_no_overwrite(
        self,
    ) -> None:
        test_root = (
            ROOT
            / "downloads/phase-two/runs/P2O4-T39-U08-TEST"
        )
        test_root.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(dir=test_root) as temporary:
            root = Path(temporary)
            outputs = write_outputs(
                ROOT,
                root / "records",
                root / "public",
                "2026-07-25T05:30:00Z",
                "BL-TEST-REPLACEMENT-SIX-EVENT-SUFFICIENCY",
                "a" * 40,
            )
            report = json.loads(
                outputs["json"].read_text(encoding="utf-8")
            )
            self.assertEqual(report["decision"], DECISION)
            self.assertEqual(report["audit_decision"], "pass")
            self.assertEqual(
                report["partition_feasibility"]["valid_assignments"],
                54,
            )
            self.assertFalse(
                report["next_checkpoint"]["training_authorized"]
            )
            self.assertTrue(
                all(
                    value is False
                    for value in report["boundaries"].values()
                )
            )
            serialized = outputs["json"].read_text(
                encoding="utf-8"
            ).lower()
            for forbidden in (
                "c:\\users",
                "owner_decision",
                "private_reconciliation",
                "response-aadd",
                "receipt-aadd",
            ):
                self.assertNotIn(forbidden, serialized)
            outputs_by_name = {
                path.name: path for path in outputs.values()
            }
            for output in report["outputs"]:
                path = outputs_by_name[Path(output["path"]).name]
                payload = path.read_bytes()
                self.assertEqual(len(payload), output["bytes"])
                self.assertEqual(
                    hashlib.sha256(payload).hexdigest(),
                    output["sha256"],
                )
            with self.assertRaisesRegex(
                SixEventDatasetSufficiencyError,
                "output already exists",
            ):
                write_outputs(
                    ROOT,
                    root / "records",
                    root / "public",
                    "2026-07-25T05:30:00Z",
                    "BL-TEST-REPLACEMENT-SIX-EVENT-SUFFICIENCY",
                    "a" * 40,
                )

    @unittest.skipUnless(
        PUBLIC_REPORT.is_file(),
        "tracked replacement sufficiency report is unavailable",
    )
    def test_tracked_public_report_is_self_bound(self) -> None:
        report = json.loads(PUBLIC_REPORT.read_text(encoding="utf-8"))
        self.assertEqual(
            report["label_set_version"],
            LABEL_SET_VERSION,
        )
        self.assertEqual(report["audit_decision"], "pass")
        self.assertEqual(
            report["partition_feasibility"]["valid_assignments"],
            54,
        )
        self.assertFalse(report["boundaries"]["training_authorized"])
        for output in report["outputs"]:
            path = ROOT / output["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), output["bytes"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                output["sha256"],
            )

    def test_roster_is_stable(self) -> None:
        self.assertEqual(len(EVENTS), 6)
        self.assertEqual(
            sum(bool(item["never_tuned_transfer"]) for item in EVENTS),
            3,
        )


if __name__ == "__main__":
    unittest.main()
