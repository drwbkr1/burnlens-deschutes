from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from burnlens.grandview_optical_contract import EVENT_GROUP_ID
from burnlens.grandview_source_fitness import GrandviewSourceFitnessError, _load_candidate, build_report


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "downloads/phase-two/raw/grandview-s2-optical-pair-v0.1.0"
PLAN = ROOT / "samples/cross-event/phase-two/ADDITIONAL-EVENT-GROUP-PLAN-2026-001.json"


def plan_fixture() -> dict:
    return {
        "report_id": "ADDITIONAL-EVENT-GROUP-PLAN-2026-001",
        "selected_event_group_ids": ["first", EVENT_GROUP_ID, "third"],
        "candidate_assessments": [
            {
                "event_group_id": EVENT_GROUP_ID,
                "disposition": "FROZEN_FOR_BOUNDED_ACQUISITION",
                "fire_id": "OR4446612140020210711",
                "programs": ["BAER", "MTBS", "RAVG"],
            }
        ],
    }


class GrandviewSourceFitnessTests(unittest.TestCase):
    def test_plan_binding_requires_grandview_second(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            path.write_text(json.dumps(plan_fixture()), encoding="utf-8")
            _, candidate = _load_candidate(path)
            self.assertEqual(candidate["event_group_id"], EVENT_GROUP_ID)
            changed = plan_fixture()
            changed["selected_event_group_ids"] = [EVENT_GROUP_ID, "second", "third"]
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(GrandviewSourceFitnessError, "not second"):
                _load_candidate(path)

    @unittest.skipUnless(PACKAGE.is_dir(), "ignored Grandview provider package unavailable")
    def test_exact_registered_package_produces_expected_real_metrics(self) -> None:
        report, _ = build_report(
            package=PACKAGE,
            plan_path=PLAN,
            generated_at_utc="2026-07-20T19:00:00Z",
            run_id="BL-TEST-GRANDVIEW-FITNESS",
            git_source_commit="0" * 40,
        )
        self.assertEqual(report["fitness_decision"]["optical_source"], "PASS_EXACT_GRANDVIEW_OPTICAL_SOURCE_FITNESS")
        self.assertEqual(report["pair_quality_inside_full_boundary"]["pixel_count_inside_full_boundary"], 62_588)
        self.assertEqual(report["spectral_change"]["valid_pair_pixels"], 61_073)
        self.assertEqual(report["registration"]["summary"]["state_counts"]["pass"], 9)
        self.assertIsNone(report["dataset_version"])
        self.assertIsNone(report["model_version"])


if __name__ == "__main__":
    unittest.main()
