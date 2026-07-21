from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import numpy as np

from burnlens.petes_lake_optical_contract import EVENT_GROUP_ID
from burnlens.petes_lake_source_fitness import (
    PetesLakeSourceFitnessError,
    VISUAL_PENDING,
    _load_candidate,
    _write_bytes_no_overwrite,
    build_report,
    summarize_probability,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "samples/cross-event/phase-two/ADDITIONAL-EVENT-GROUP-PLAN-2026-001.json"
CUSTODY = (
    ROOT
    / "samples/cross-event/phase-two/petes-lake/PETES-LAKE-OPTICAL-CUSTODY-2026-001.json"
)
PRE = ROOT / "downloads/phase-two/raw/petes-lake-s2-optical-pre-v0.1.0"
POST = ROOT / "downloads/phase-two/raw/petes-lake-s2-optical-post-v0.1.0"


def plan_fixture() -> dict:
    return {
        "report_id": "ADDITIONAL-EVENT-GROUP-PLAN-2026-001",
        "selected_event_group_ids": ["first", "second", EVENT_GROUP_ID],
        "candidate_assessments": [
            {
                "event_group_id": EVENT_GROUP_ID,
                "disposition": "FROZEN_FOR_BOUNDED_ACQUISITION",
                "fire_id": "OR4396912190120230825",
                "programs": ["MTBS"],
            }
        ],
    }


class PetesLakeSourceFitnessTests(unittest.TestCase):
    def test_plan_binding_requires_petes_lake_third(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            path.write_text(json.dumps(plan_fixture()), encoding="utf-8")
            _, candidate = _load_candidate(path)
            self.assertEqual(candidate["event_group_id"], EVENT_GROUP_ID)
            changed = plan_fixture()
            changed["selected_event_group_ids"] = [EVENT_GROUP_ID, "second", "third"]
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(PetesLakeSourceFitnessError, "not third"):
                _load_candidate(path)

    def test_probability_summary_preserves_native_range_without_threshold(self) -> None:
        values = np.array([[0, 10, 50], [90, 100, 25]], dtype=np.uint8)
        mask = np.array([[True, True, False], [True, True, False]])
        summary = summarize_probability(values, mask)
        self.assertEqual(summary["pixel_count"], 4)
        self.assertEqual(summary["maximum_percent"], 100)
        self.assertFalse(summary["threshold_applied"])
        changed = values.copy()
        changed[0, 0] = 101
        with self.assertRaisesRegex(PetesLakeSourceFitnessError, "0-100"):
            summarize_probability(changed, mask)

    def test_output_writer_is_exact_and_no_overwrite(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.bin"
            _write_bytes_no_overwrite(path, b"exact\n")
            self.assertEqual(path.read_bytes(), b"exact\n")
            with self.assertRaisesRegex(PetesLakeSourceFitnessError, "already exists"):
                _write_bytes_no_overwrite(path, b"changed\n")

    @unittest.skipUnless(
        PRE.is_dir() and POST.is_dir() and CUSTODY.is_file(),
        "ignored Petes Lake provider packages unavailable",
    )
    def test_exact_registered_pair_produces_native_quality_and_registration(self) -> None:
        report, _ = build_report(
            repository_root=ROOT,
            plan_path=PLAN,
            custody_report_path=CUSTODY,
            generated_at_utc="2026-07-21T20:00:00Z",
            run_id="BL-TEST-PETES-LAKE-SOURCE-FITNESS",
            git_source_commit="0" * 40,
            visual_review_decision=VISUAL_PENDING,
            visual_review_notes="",
        )
        self.assertEqual(report["fitness_decision"]["optical_source"], VISUAL_PENDING)
        self.assertEqual(
            report["fitness_decision"]["machine_source_gate"],
            "REJECT_EXACT_PETES_LAKE_OPTICAL_SOURCE_FITNESS",
        )
        self.assertFalse(report["fitness_decision"]["u04_authorized"])
        self.assertEqual(report["products"][0]["product_metadata"]["processing_baseline"], "05.10")
        self.assertEqual(
            report["products"][0]["scl_summary_inside_full_boundary"]["eligible_land_pixels"],
            33763,
        )
        self.assertEqual(
            report["products"][1]["scl_summary_inside_full_boundary"]["classes"][11]["pixels"],
            26627,
        )
        self.assertEqual(
            report["products"][1]["quality_probabilities_inside_full_boundary"]["snow"][
                "range_contract_percent"
            ],
            [0, 100],
        )
        self.assertEqual(report["pair_quality_inside_full_boundary"]["pixel_count_inside_full_boundary"], 34103)
        self.assertEqual(report["pair_quality_inside_full_boundary"]["states"][0]["pixels"], 7439)
        self.assertEqual(report["registration"]["summary"]["state_counts"]["pass"], 0)
        self.assertEqual(report["registration"]["summary"]["state_counts"]["excluded"], 8)
        self.assertEqual(report["registration"]["summary"]["p95_px"], 0.6199)
        self.assertEqual(report["spectral_change"]["valid_pair_pixels"], 7439)
        self.assertEqual(report["temporal_fitness"]["pre_days_before_ignition"], 35)
        self.assertEqual(report["temporal_fitness"]["post_days_after_ignition"], 65)
        self.assertIsNone(report["dataset_version"])
        self.assertIsNone(report["model_version"])


if __name__ == "__main__":
    unittest.main()
