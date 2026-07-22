from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

import burnlens
from burnlens.label_region_remediation_plan import DECISION, build_report


ROOT = Path(__file__).resolve().parents[1]
SUFFICIENCY = ROOT / "samples" / "labels" / "readiness" / "phase-two" / "PROTOTYPE-LABEL-SUFFICIENCY-2026-001.json"
SCOUT = ROOT / "samples" / "reference" / "phase-two" / "OFFICIAL-SOURCE-SCOUT-2026-001.json"
SOURCE = ROOT / "samples" / "reference" / "phase-two" / "OFFICIAL-SOURCE-SCOUT-SOURCE-2026-001.json"
BUNDLE = ROOT / "samples" / "reference" / "phase-two" / "CURRENT-REFERENCE-BUNDLE-FITNESS-2026-001.json"
PUBLIC = ROOT / "samples" / "labels" / "readiness" / "phase-two" / "LABEL-REGION-REMEDIATION-PLAN-2026-001.json"


class LabelRegionRemediationPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = build_report(SUFFICIENCY, SCOUT, SOURCE, BUNDLE, "2026-07-18T05:30:00Z", "BL-TEST-REGION-PLAN", "a" * 40)

    def test_version_decision_and_no_analytical_versions(self) -> None:
        self.assertEqual(burnlens.__version__, "0.45.0")
        self.assertEqual(self.report["decision"], DECISION)
        self.assertFalse(any(self.report["boundaries"].values()))

    def test_region_contract_rejects_point_expansion_and_tiles(self) -> None:
        contract = self.report["review_unit_contract"]
        self.assertIn("a center pixel expanded by radius", contract["not_a_unit"])
        self.assertIn("an arbitrary square tile", contract["not_a_unit"])
        self.assertIn("unknown ring", " ".join(contract["candidate_generator"]))

    def test_event_gate_requires_replication(self) -> None:
        plan = self.report["event_plan"]
        self.assertEqual(plan["minimum_event_groups_before_split_fitness"], 6)
        self.assertEqual(plan["additional_event_groups_required"], 3)
        self.assertEqual(plan["minimum_groups_per_eventual_role"], 2)
        self.assertEqual(len(plan["ranked_reconnaissance"]), 4)

    def test_source_truth_boundaries_are_explicit(self) -> None:
        serialized = json.dumps(self.report["source_roles"]).lower()
        self.assertIn("not automatic truth", serialized)
        self.assertIn("never burned/background evidence", serialized)
        self.assertIn("restricted thresholded barc excluded", serialized)


@unittest.skipUnless(PUBLIC.exists(), "tracked report not published yet")
class TrackedLabelRegionRemediationPlanTests(unittest.TestCase):
    def test_public_report_and_outputs(self) -> None:
        report = json.loads(PUBLIC.read_text(encoding="utf-8"))
        self.assertEqual(report["decision"], DECISION)
        self.assertFalse(any(report["boundaries"].values()))
        for output in report["outputs"]:
            path = PUBLIC.parent / output["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), output["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), output["sha256"])


if __name__ == "__main__":
    unittest.main()
