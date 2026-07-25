from __future__ import annotations

import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

import rasterio

from burnlens.ward_creek_region_proposal import (
    BACKGROUND_REPORT_SHA256,
    EXPECTED_ROUTE_COUNTS,
    RUN_ID,
    SUFFICIENCY_REPORT_SHA256,
    WardCreekRegionProposalError,
    build_report,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
PRE = ROOT / "downloads/phase-two/raw/ward-creek-s2-optical-pre-v0.1.0"
POST = ROOT / "downloads/phase-two/raw/ward-creek-s2-optical-post-v0.1.0"
ARCHIVE = (
    ROOT
    / "downloads/phase-two/raw/ward-creek-mtbs-reference-v0.1.0/"
    "ward-creek-mtbs-reference-delivery-001.zip"
)
BACKGROUND = (
    ROOT
    / "samples/reference/phase-two/ward-creek/background-evidence-v0.1.0/"
    "WARD-CREEK-BACKGROUND-EVIDENCE-2026-001.json"
)
SUFFICIENCY = (
    ROOT
    / "samples/labels/readiness/phase-two/"
    "SIX-EVENT-DATASET-SUFFICIENCY-2026-001.json"
)


class WardCreekRegionProposalTests(unittest.TestCase):
    def test_frozen_bindings_and_route_counts(self) -> None:
        self.assertEqual(
            BACKGROUND_REPORT_SHA256,
            "acf5b02c314b7dfdee94d8709323117f24e1966042818c37ef7431085813933c",
        )
        self.assertEqual(
            SUFFICIENCY_REPORT_SHA256,
            "a3fa779669143333fbc2b9b27fb35d210d0847283ef754c9e7f1f39a0c30908b",
        )
        self.assertEqual(EXPECTED_ROUTE_COUNTS["burned_route"], 686)
        self.assertEqual(EXPECTED_ROUTE_COUNTS["background_route"], 21_266)

    @unittest.skipUnless(
        PRE.is_dir()
        and POST.is_dir()
        and ARCHIVE.is_file()
        and BACKGROUND.is_file()
        and SUFFICIENCY.is_file(),
        "ignored exact Ward Creek custody unavailable",
    )
    def test_exact_custody_proposes_two_intact_regions_without_labels(self) -> None:
        with TemporaryDirectory(
            dir=ROOT / "downloads/phase-two/runs/P2O4-T39-U05"
        ) as temporary:
            head = subprocess.run(
                ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            report, selected, _ = build_report(
                repository_root=ROOT,
                pre_package=PRE,
                post_package=POST,
                archive_path=ARCHIVE,
                extracted_root=Path(temporary) / "extracted",
                background_report_path=BACKGROUND,
                sufficiency_report_path=SUFFICIENCY,
                generated_at_utc="2026-07-24T23:45:00Z",
                run_id=RUN_ID,
                git_source_commit=head,
            )
            self.assertEqual(
                report["summary"]["class_counts"],
                {"burned": 1, "background": 1},
            )
            self.assertEqual(
                [item["core_pixels"] for item in selected],
                [14, 25],
            )
            self.assertEqual(report["summary"]["owner_responses"], 0)
            self.assertEqual(report["summary"]["labels_created"], 0)
            self.assertTrue(report["leakage_gate"]["ward_creek_event_group_absent"])
            self.assertIsNone(report["output_label_set_version"])
            self.assertIsNone(report["dataset_version"])
            self.assertIsNone(report["model_version"])

    @unittest.skipUnless(
        PRE.is_dir()
        and POST.is_dir()
        and ARCHIVE.is_file()
        and BACKGROUND.is_file()
        and SUFFICIENCY.is_file(),
        "ignored exact Ward Creek custody unavailable",
    )
    def test_outputs_bind_rasters_and_refuse_overwrite(self) -> None:
        with TemporaryDirectory(
            dir=ROOT / "downloads/phase-two/runs/P2O4-T39-U05"
        ) as temporary:
            temporary = Path(temporary)
            head = subprocess.run(
                ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            report, selected, previews = build_report(
                repository_root=ROOT,
                pre_package=PRE,
                post_package=POST,
                archive_path=ARCHIVE,
                extracted_root=temporary / "extracted",
                background_report_path=BACKGROUND,
                sufficiency_report_path=SUFFICIENCY,
                generated_at_utc="2026-07-24T23:45:00Z",
                run_id=RUN_ID,
                git_source_commit=head,
            )
            directory = temporary / "outputs"
            outputs = write_outputs(report, selected, previews, directory)
            self.assertEqual(len(outputs), 5)
            payload = json.loads((directory / f"{report['report_id']}.json").read_text())
            for candidate in payload["candidates"]:
                raster_path = directory / candidate["candidate_raster"]
                self.assertEqual(
                    raster_path.stat().st_size,
                    candidate["candidate_raster_bytes"],
                )
                with rasterio.open(raster_path) as raster:
                    self.assertEqual(
                        raster.tags()["proposal_binding_sha256"],
                        candidate["proposal_binding_sha256"],
                    )
                    self.assertEqual(raster.tags()["owner_decision"], "none")
                    self.assertEqual(raster.tags()["label_created"], "false")
            with self.assertRaisesRegex(
                WardCreekRegionProposalError,
                "already exists",
            ):
                write_outputs(report, selected, previews, directory)


if __name__ == "__main__":
    unittest.main()
