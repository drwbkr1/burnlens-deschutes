from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import numpy as np

from burnlens.green_ridge_optical_contract import EVENT_GROUP_ID
from burnlens.green_ridge_source_fitness import (
    GreenRidgeSourceFitnessError,
    _load_candidate,
    build_report,
    summarize_spectral_change,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "downloads/phase-two/raw/green-ridge-s2-optical-pair-v0.1.0"
PLAN = ROOT / "samples/cross-event/phase-two/ADDITIONAL-EVENT-GROUP-PLAN-2026-001.json"


def plan_fixture() -> dict:
    return {
        "report_id": "ADDITIONAL-EVENT-GROUP-PLAN-2026-001",
        "selected_event_group_ids": [EVENT_GROUP_ID, "second", "third"],
        "candidate_assessments": [
            {
                "event_group_id": EVENT_GROUP_ID,
                "disposition": "FROZEN_FOR_BOUNDED_ACQUISITION",
                "fire_id": "OR4446712160520200817",
                "programs": ["BAER", "MTBS", "RAVG"],
            }
        ],
    }


class GreenRidgeSourceFitnessTests(unittest.TestCase):
    def test_plan_binding_requires_green_ridge_first(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            path.write_text(json.dumps(plan_fixture()), encoding="utf-8")
            _, candidate = _load_candidate(path)
            self.assertEqual(candidate["event_group_id"], EVENT_GROUP_ID)
            changed = plan_fixture()
            changed["selected_event_group_ids"] = ["second", EVENT_GROUP_ID, "third"]
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(GreenRidgeSourceFitnessError, "not first"):
                _load_candidate(path)

    def test_spectral_summary_is_continuous_and_assigns_no_class(self) -> None:
        mask = np.ones((2, 3), dtype=bool)
        pre = {"MASK20": mask, "SCL": np.full((2, 3), 4, dtype=np.uint8)}
        post = {"MASK20": mask.copy(), "SCL": np.full((2, 3), 5, dtype=np.uint8)}
        values = [
            (np.full((2, 3), 0.8, dtype=np.float32), mask),
            (np.full((2, 3), 0.2, dtype=np.float32), mask),
            (np.full((2, 3), 0.4, dtype=np.float32), mask),
            (np.full((2, 3), 0.4, dtype=np.float32), mask),
        ]
        with patch("burnlens.green_ridge_source_fitness._reflectance", side_effect=values):
            summary, dnbr, valid = summarize_spectral_change({}, pre, {}, post)
        self.assertEqual(summary["valid_pair_pixels"], 6)
        self.assertAlmostEqual(summary["dnbr_percentiles"]["p50"], 0.6)
        self.assertTrue(np.all(valid))
        self.assertTrue(np.allclose(dnbr[valid], 0.6))
        self.assertIn("no threshold", summary["interpretation"])

    @unittest.skipUnless(PACKAGE.is_dir(), "ignored Green Ridge provider package unavailable")
    def test_exact_registered_package_produces_expected_real_metrics(self) -> None:
        report, _ = build_report(
            package=PACKAGE,
            plan_path=PLAN,
            generated_at_utc="2026-07-19T22:30:00Z",
            run_id="BL-TEST-GREEN-RIDGE-FITNESS",
            git_source_commit="0" * 40,
        )
        self.assertEqual(
            report["fitness_decision"]["optical_source"],
            "PASS_EXACT_GREEN_RIDGE_OPTICAL_SOURCE_FITNESS",
        )
        self.assertEqual(
            report["pair_quality_inside_full_boundary"]["pixel_count_inside_full_boundary"], 44_110
        )
        self.assertEqual(report["registration"]["summary"]["state_counts"]["pass"], 9)
        self.assertIsNone(report["dataset_version"])
        self.assertIsNone(report["model_version"])


if __name__ == "__main__":
    unittest.main()
