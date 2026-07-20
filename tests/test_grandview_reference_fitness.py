from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from burnlens.grandview_reference_fitness import (
    ARCHIVE_SHA256,
    GrandviewReferenceFitnessError,
    _dbf_records,
    build_report,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "downloads/phase-two/raw/grandview-s2-optical-pair-v0.1.0"
ARCHIVE = ROOT / "downloads/phase-two/quarantine/grandview-reference-delivery-r001/grandview-reference-delivery-r001.zip"
PLAN = ROOT / "samples/cross-event/phase-two/ADDITIONAL-EVENT-GROUP-PLAN-2026-001.json"


class GrandviewReferenceFitnessTests(unittest.TestCase):
    def test_dbf_parser_rejects_truncated_header(self) -> None:
        with self.assertRaisesRegex(GrandviewReferenceFitnessError, "header"):
            _dbf_records(b"short")

    @unittest.skipUnless(PACKAGE.is_dir() and ARCHIVE.is_file(), "ignored exact custody unavailable")
    def test_exact_delivery_and_optical_package_produce_expected_fitness(self) -> None:
        report, _ = build_report(
            package=PACKAGE, plan_path=PLAN, archive_path=ARCHIVE,
            generated_at_utc="2026-07-20T20:15:00Z",
            run_id="BL-TEST-GRANDVIEW-REFERENCE-FITNESS",
            git_source_commit="0" * 40,
        )
        self.assertEqual(report["archive"]["sha256"], ARCHIVE_SHA256)
        self.assertEqual(len(report["native_rasters"]), 20)
        self.assertTrue(all(item["all_bands_read"] for item in report["native_rasters"]))
        self.assertTrue(all(item["iso_metadata"]["access_and_use_language_present"] for item in report["metadata"]))
        self.assertEqual(report["evidence_comparison"]["mtbs_affirmative_pixels"], 58_438)
        self.assertEqual(report["evidence_comparison"]["mtbs_affirmative_and_optical_valid_pixels"], 56_943)
        self.assertEqual(report["evidence_comparison"]["mtbs_affirmative_with_ravg_modeled_effect_pixels"], 57_106)
        self.assertEqual(report["evidence_comparison"]["mtbs_reference_uncovered_pixels"], 793)
        self.assertIn("sparse", report["evidence_comparison"]["ravg_fitness_limit"])
        self.assertEqual(
            report["fitness_decision"]["reference_pixels"],
            "PASS_EXACT_GRANDVIEW_REFERENCE_SOURCE_FITNESS_WITH_RAVG_LIMIT",
        )
        self.assertIsNone(report["trace"]["dataset_version"])
        self.assertIsNone(report["trace"]["model_version"])


if __name__ == "__main__":
    unittest.main()
