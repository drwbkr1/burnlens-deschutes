from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

import burnlens
from burnlens.prototype_label_sufficiency import DECISION, build_report


ROOT = Path(__file__).resolve().parents[1]
SURFACE = ROOT / "samples" / "labels" / "review" / "phase-two" / "OWNER-REVIEW-SURFACE-2026-001.json"
PRIVATE = ROOT / "downloads" / "phase-two" / "runs" / "BL-2026-07-18-prototype-label-sufficiency-cycle-r001" / "private.json"
DARLENE = ROOT / "samples" / "labels" / "phase-two" / "LABEL-PROPOSAL-2026-001.json"
CROSS_EVENT = ROOT / "samples" / "labels" / "cross-event" / "phase-two" / "CROSS-EVENT-LABEL-TRANSFER-2026-002.json"
PUBLIC = ROOT / "samples" / "labels" / "readiness" / "phase-two" / "PROTOTYPE-LABEL-SUFFICIENCY-2026-001.json"


@unittest.skipUnless(PRIVATE.exists(), "exact private owner intake is local and ignored")
class PrototypeLabelSufficiencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = build_report(
            ROOT,
            SURFACE,
            PRIVATE,
            DARLENE,
            CROSS_EVENT,
            "2026-07-18T05:00:00Z",
            "BL-TEST-PROTOTYPE-SUFFICIENCY",
            "a" * 40,
        )

    def test_version_and_decision(self) -> None:
        self.assertEqual(burnlens.__version__, "0.27.0")
        self.assertEqual(self.report["decision"], DECISION)

    def test_inventory_blocks_dataset_expansion(self) -> None:
        inventory = self.report["inventory"]
        self.assertEqual(inventory["prototype_labels"], 24)
        self.assertEqual(inventory["prototype_class_counts"], {"background": 12, "burned": 12})
        self.assertEqual(inventory["candidate_domain_pixels"], 189541)
        self.assertEqual(inventory["prototype_fraction_of_candidate_domain_percent"], 0.012662)
        self.assertIn("center pixels only", inventory["label_granularity"])
        self.assertFalse(self.report["selection_and_evaluation"]["per_pixel_segmentation_training_supported"])

    def test_event_partition_has_no_replication(self) -> None:
        partition = self.report["partition_feasibility"]
        self.assertEqual(partition["nonempty_train_validation_test_assignments"], 6)
        self.assertEqual(partition["event_groups_per_role_in_every_assignment"], {"train": 1, "validation": 1, "test": 1})
        self.assertFalse(partition["replicated_event_evidence_per_role"])
        self.assertTrue(partition["source_regime_confounded_with_event"])
        self.assertEqual(partition["source_regime_count"], 3)

    def test_public_report_contains_no_unit_decisions(self) -> None:
        serialized = json.dumps(self.report).lower()
        for forbidden in ("sample_id", "owner_decision", "lru-", "pixel_center_utm10n", "c:\\users"):
            self.assertNotIn(forbidden, serialized)
        self.assertFalse(any(self.report["boundaries"].values()))


class TrackedPrototypeLabelSufficiencyTests(unittest.TestCase):
    def test_readiness_outputs_have_checkout_stable_text_bytes(self) -> None:
        attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("samples/labels/readiness/phase-two/*.json text eol=lf", attributes)
        self.assertIn("samples/labels/readiness/phase-two/*.html text eol=lf", attributes)

    def test_public_report_is_bounded_and_content_safe(self) -> None:
        report = json.loads(PUBLIC.read_text(encoding="utf-8"))
        self.assertEqual(report["decision"], DECISION)
        self.assertEqual(report["inventory"]["prototype_labels"], 24)
        self.assertEqual(report["inventory"]["candidate_domain_pixels"], 189541)
        self.assertFalse(any(report["boundaries"].values()))
        serialized = PUBLIC.read_text(encoding="utf-8").lower()
        for forbidden in ("sample_id", "owner_decision", "lru-", "pixel_center_utm10n", "c:\\users", "downloads"):
            self.assertNotIn(forbidden, serialized)

    def test_public_rendered_outputs_match_report(self) -> None:
        report = json.loads(PUBLIC.read_text(encoding="utf-8"))
        for output in report["outputs"]:
            path = PUBLIC.parent / output["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), output["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), output["sha256"])


if __name__ == "__main__":
    unittest.main()
