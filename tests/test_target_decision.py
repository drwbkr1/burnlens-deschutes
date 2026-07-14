from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from PIL import Image

from burnlens.target_decision import TargetDecisionError, build_report, run_target_decision


ROOT = Path(__file__).resolve().parents[1]
OBSERVATION = ROOT / "samples/observation/phase-two/OBSERVATION-GEOMETRY-2026-001.json"
AOI = ROOT / "samples/aoi/phase-two/AOI-FINAL-2026-001.json"
MTBS = ROOT / "samples/target/phase-two/MTBS-DARLENE3-AVAILABILITY-2026-001.json"


class TargetDecisionTests(unittest.TestCase):
    def test_build_activates_fallback_without_creating_outputs(self) -> None:
        report = build_report(
            observation_path=OBSERVATION,
            aoi_path=AOI,
            mtbs_path=MTBS,
            generated_at_utc="2026-07-14T21:20:00Z",
            run_id="BL-TEST-TARGET-DECISION",
            git_source_commit="a" * 40,
        )
        self.assertEqual(report["owner_decision"]["status"], "ACTIVE")
        self.assertEqual(report["target_contract"]["active_target"], "burn-scar binary mask")
        self.assertEqual(report["target_contract"]["former_primary_disposition"], "COMPLEMENTARY_REFERENCE_ONLY")
        self.assertFalse(report["target_contract"]["severity_classes_used"])
        self.assertEqual(report["mtbs_assessment"]["inventory_feature_count_2024"], 941)
        self.assertEqual(report["mtbs_assessment"]["aoi_feature_count_all_years"], 0)
        self.assertFalse(report["quality_gates"]["label_array_created"])
        self.assertIsNone(report["dataset_version"])
        self.assertIsNone(report["label_schema_version"])
        self.assertIsNone(report["model_version"])

    def test_contradictory_mtbs_record_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "mtbs.json"
            record = json.loads(MTBS.read_text(encoding="utf-8"))
            record["findings"]["aoi_feature_count_2024"] = 1
            path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaisesRegex(TargetDecisionError, "MTBS_DARLENE_ABSENCE_NOT_PROVEN"):
                build_report(
                    observation_path=OBSERVATION,
                    aoi_path=AOI,
                    mtbs_path=path,
                    generated_at_utc="2026-07-14T21:20:00Z",
                    run_id="BL-TEST-TARGET-DECISION",
                    git_source_commit="a" * 40,
                )

    def test_rendered_outputs_are_traceable_and_real(self) -> None:
        with TemporaryDirectory() as directory:
            paths = run_target_decision(
                observation_path=OBSERVATION,
                aoi_path=AOI,
                mtbs_path=MTBS,
                output_directory=Path(directory),
                generated_at_utc="2026-07-14T21:20:00Z",
                run_id="BL-TEST-TARGET-DECISION",
                git_source_commit="a" * 40,
            )
            report = json.loads(paths["json"].read_text(encoding="utf-8"))
            html = paths["html"].read_text(encoding="utf-8")
            with Image.open(paths["png"]) as image:
                self.assertEqual(image.size, (1600, 1050))
            self.assertEqual(report["rendered_outputs"]["png"], paths["png"].name)
            self.assertIn("Burn-scar binary-mask fallback is active", html)
            self.assertIn("Not created / not created / not created / not created / not created", html)
            self.assertIn("Official sources govern", html)


if __name__ == "__main__":
    unittest.main()
