from __future__ import annotations

from pathlib import Path
import unittest

from burnlens.grandview_region_proposal import build_report


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "downloads/phase-two/raw/grandview-s2-optical-pair-v0.1.0"
EXTENDED = ROOT / "downloads/phase-two/raw/grandview-s2-background-extended-v0.1.0"
REFERENCE = ROOT / "downloads/phase-two/quarantine/grandview-reference-delivery-r001/grandview-reference-delivery-r001.zip"
PLAN = ROOT / "samples/cross-event/phase-two/ADDITIONAL-EVENT-GROUP-PLAN-2026-001.json"


class GrandviewRegionProposalTests(unittest.TestCase):
    @unittest.skipUnless(
        ORIGINAL.is_dir() and EXTENDED.is_dir() and REFERENCE.is_file(),
        "ignored exact custody unavailable",
    )
    def test_exact_custody_proposes_two_regions_without_labels(self) -> None:
        report, selected, _ = build_report(
            original_package=ORIGINAL,
            extended_package=EXTENDED,
            plan_path=PLAN,
            reference_archive=REFERENCE,
            generated_at_utc="2026-07-20T23:55:00Z",
            run_id="BL-TEST-GRANDVIEW-REGION-PROPOSAL",
            git_source_commit="0" * 40,
        )
        self.assertEqual(report["summary"]["candidate_count"], 2)
        self.assertEqual(report["summary"]["class_counts"], {"burned": 1, "background": 1})
        self.assertEqual([item["core_pixels"] for item in selected], [25, 25])
        self.assertEqual(report["summary"]["owner_responses"], 0)
        self.assertEqual(report["summary"]["labels_created"], 0)
        self.assertIsNone(report["output_label_set_version"])
        self.assertIsNone(report["dataset_version"])
        self.assertIsNone(report["model_version"])
        self.assertIn("RAVG classes are not used", report["method"]["burned_route"])


if __name__ == "__main__":
    unittest.main()
