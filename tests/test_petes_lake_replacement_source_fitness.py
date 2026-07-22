from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from burnlens.petes_lake_replacement_source_fitness import (
    CUSTODY_REPORT_BYTES,
    REPORT_ID,
    RUN_ID,
    VISUAL_PENDING,
    PetesLakeSourceFitnessError,
    _load_replacement_custody,
    _validate_prior_evidence,
    build_report,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "samples/cross-event/phase-two/ADDITIONAL-EVENT-GROUP-PLAN-2026-001.json"
CUSTODY = ROOT / "samples/cross-event/phase-two/petes-lake/PETES-LAKE-OPTICAL-REMEDIATION-CUSTODY-2026-001.json"
FAILED = ROOT / "samples/cross-event/phase-two/petes-lake/PETES-LAKE-SOURCE-FITNESS-2026-001.json"
SELECTION = ROOT / "samples/cross-event/phase-two/petes-lake/PETES-LAKE-SOURCE-REMEDIATION-2026-001.json"
PRE = ROOT / "downloads/phase-two/raw/petes-lake-s2-optical-pre-v0.1.0"
POST = ROOT / "downloads/phase-two/raw/petes-lake-s2-optical-post-remediation-v0.2.0"


class PetesLakeReplacementSourceFitnessTests(unittest.TestCase):
    def test_replacement_custody_is_exact_and_semantically_authorized(self) -> None:
        report = _load_replacement_custody(CUSTODY)
        self.assertEqual(CUSTODY.stat().st_size, CUSTODY_REPORT_BYTES)
        self.assertEqual(
            report["semantic_sha256"],
            "78c888b4a3b954c4038a3454773b1cd7c922bc5f71957524e803ee6534d71f75",
        )
        changed = json.loads(CUSTODY.read_text(encoding="utf-8"))
        changed["semantic_record"]["u04_authorized"] = True
        with TemporaryDirectory() as directory:
            path = Path(directory) / "changed.json"
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(PetesLakeSourceFitnessError, "byte identity"):
                _load_replacement_custody(path)

    def test_prior_failure_and_selection_are_immutable_inputs(self) -> None:
        failed, selection = _validate_prior_evidence(FAILED, SELECTION)
        self.assertFalse(failed["fitness_decision"]["u04_authorized"])
        self.assertEqual(
            selection["decision"],
            "SELECT_REPLACEMENT_POST_AUTHORIZE_CONTRACT_REVISION_ONLY",
        )

    def test_output_roster_is_separate_and_no_overwrite(self) -> None:
        with TemporaryDirectory() as directory, patch(
            "burnlens.petes_lake_replacement_source_fitness._render_png_bytes",
            return_value=b"replacement-png",
        ):
            output = write_outputs({"report_id": REPORT_ID}, {}, Path(directory))
            self.assertEqual(set(output), {"json", "png"})
            self.assertTrue((Path(directory) / f"{REPORT_ID}.json").is_file())
            with self.assertRaisesRegex(PetesLakeSourceFitnessError, "already exists"):
                write_outputs({"report_id": REPORT_ID}, {}, Path(directory))

    @unittest.skipUnless(
        PRE.is_dir() and POST.is_dir() and CUSTODY.is_file(),
        "ignored Petes Lake replacement provider packages unavailable",
    )
    def test_exact_replacement_pair_produces_native_evidence_without_labels(self) -> None:
        report, _ = build_report(
            repository_root=ROOT,
            plan_path=PLAN,
            custody_report_path=CUSTODY,
            failed_report_path=FAILED,
            selection_report_path=SELECTION,
            generated_at_utc="2026-07-21T22:00:00Z",
            run_id=RUN_ID,
            git_source_commit="0" * 40,
            visual_review_decision=VISUAL_PENDING,
            visual_review_notes="",
        )
        self.assertEqual(report["report_id"], REPORT_ID)
        self.assertEqual(
            report["fitness_decision"]["optical_source"],
            "PENDING_ACTUAL_PETES_LAKE_REPLACEMENT_RENDER_REVIEW",
        )
        self.assertFalse(report["fitness_decision"]["u04_authorized"])
        self.assertEqual(
            report["products"][1]["product_metadata"]["sensing_time_utc"],
            "2023-10-19T19:12:24.432471Z",
        )
        self.assertTrue(report["metadata_time_reconciliation"]["same_utc_date"])
        self.assertEqual(
            report["products"][1]["product_metadata"]["processing_baseline"],
            "05.10",
        )
        self.assertEqual(
            report["pair_quality_inside_full_boundary"]["pixel_count_inside_full_boundary"],
            34103,
        )
        self.assertEqual(
            report["pair_quality_inside_full_boundary"]["states"][0]["pixels"],
            33365,
        )
        self.assertEqual(report["registration"]["summary"]["state_counts"]["pass"], 5)
        self.assertEqual(
            report["registration"]["summary"]["state_counts"]["review-needed"], 3
        )
        self.assertEqual(report["registration"]["summary"]["p95_px"], 0.3732)
        self.assertEqual(report["spectral_change"]["valid_pair_pixels"], 33365)
        self.assertEqual(
            report["products"][1]["scl_summary_inside_full_boundary"]["classes"][11][
                "pixels"
            ],
            0,
        )
        self.assertEqual(
            report["products"][1]["quality_probabilities_inside_full_boundary"][
                "snow"
            ]["maximum_percent"],
            0,
        )
        self.assertEqual(report["temporal_fitness"]["post_days_after_ignition"], 55)
        self.assertIsNone(report["dataset_version"])
        self.assertIsNone(report["model_version"])


if __name__ == "__main__":
    unittest.main()
