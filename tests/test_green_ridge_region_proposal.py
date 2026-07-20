from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

from burnlens.green_ridge_region_proposal import build_report, select_region


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "downloads/phase-two/raw/green-ridge-s2-optical-pair-v0.1.0"
EXTENDED = ROOT / "downloads/phase-two/raw/green-ridge-s2-background-extended-v0.1.0"
REFERENCE = ROOT / "downloads/phase-two/quarantine/BL-2026-07-19-green-ridge-reference-delivery-r001/usgs-delivery-20260719232840Z.zip"
PLAN = ROOT / "samples/cross-event/phase-two/ADDITIONAL-EVENT-GROUP-PLAN-2026-001.json"


class GreenRidgeRegionProposalTests(unittest.TestCase):
    def test_select_region_keeps_intact_component_and_unknown_ring(self) -> None:
        route = np.zeros((9, 9), dtype=bool)
        route[3:6, 3:6] = True
        values = np.full((9, 9), np.nan, dtype=np.float32)
        values[route] = 0.2
        selected = select_region("background", route, values)
        self.assertEqual(selected["core_pixels"], 9)
        self.assertEqual(selected["ring_pixels"], 16)
        self.assertFalse(np.any(selected["core"] & selected["ring"]))

    def test_hash_tie_break_is_deterministic(self) -> None:
        route = np.zeros((12, 12), dtype=bool)
        route[2:4, 2:4] = True
        route[8:10, 8:10] = True
        values = np.full(route.shape, np.nan, dtype=np.float32)
        values[route] = 0.1
        first = select_region("burned", route, values)
        second = select_region("burned", route, values)
        self.assertEqual(first["selection_tie_sha256"], second["selection_tie_sha256"])
        self.assertTrue(np.array_equal(first["core"], second["core"]))

    @unittest.skipUnless(ORIGINAL.is_dir() and EXTENDED.is_dir() and REFERENCE.is_file(), "ignored exact custody unavailable")
    def test_exact_custody_proposes_two_regions_without_labels(self) -> None:
        report, selected, _ = build_report(
            original_package=ORIGINAL, extended_package=EXTENDED, plan_path=PLAN,
            reference_archive=REFERENCE, generated_at_utc="2026-07-20T01:25:00Z",
            run_id="BL-TEST-GREEN-RIDGE-REGION-PROPOSAL", git_source_commit="0" * 40,
        )
        self.assertEqual(report["summary"]["candidate_count"], 2)
        self.assertEqual(report["summary"]["class_counts"], {"burned": 1, "background": 1})
        self.assertEqual([item["core_pixels"] for item in selected], [25, 25])
        self.assertEqual(report["summary"]["owner_responses"], 0)
        self.assertEqual(report["summary"]["labels_created"], 0)
        self.assertIsNone(report["dataset_version"])
        self.assertIsNone(report["model_version"])


if __name__ == "__main__":
    unittest.main()
