from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import rasterio

from burnlens.windigo_region_proposal import (
    LABEL_SET_VERSION,
    REPORT_ID,
    SOURCE_REPORT_SHA256,
    WindigoRegionProposalError,
    build_report,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
PRE = ROOT / "downloads/phase-two/raw/windigo-s2-optical-pre-v0.1.0"
POST = ROOT / "downloads/phase-two/raw/windigo-s2-optical-post-v0.1.0"
DELIVERY = (
    ROOT
    / "downloads/phase-two/quarantine/P2O4-T35-U03/"
    "windigo-reference-r001/windigo-reference-delivery.zip"
)
EXTRACTED = DELIVERY.parent / "extracted"
BOUNDARY = (
    ROOT
    / "downloads/phase-two/raw/BL-2026-07-23-windigo-entry-metadata-r001/"
    "official/windigo-mtbs-boundary.geojson"
)
SOURCE_REPORT = (
    ROOT
    / "samples/cross-event/phase-two/windigo/"
    "WINDIGO-SOURCE-FITNESS-2026-006.json"
)


class WindigoRegionProposalTests(unittest.TestCase):
    def test_source_report_hash_is_exact(self) -> None:
        self.assertEqual(
            SOURCE_REPORT_SHA256,
            "7e0ede49bcee692c130c6f04fe90898f6c393fb57f64191da1f16c1567b724b2",
        )
        self.assertEqual(LABEL_SET_VERSION, "owner-approved-prototype-region-labels-v0.3.0")

    @unittest.skipUnless(
        PRE.is_dir()
        and POST.is_dir()
        and DELIVERY.is_file()
        and EXTRACTED.is_dir()
        and BOUNDARY.is_file()
        and SOURCE_REPORT.is_file(),
        "ignored exact Windigo custody unavailable",
    )
    def test_exact_custody_proposes_two_regions_without_labels(self) -> None:
        report, selected, _ = build_report(
            pre_package=PRE,
            post_package=POST,
            archive_path=DELIVERY,
            extracted_root=EXTRACTED,
            boundary_path=BOUNDARY,
            source_report_path=SOURCE_REPORT,
            generated_at_utc="2026-07-23T22:00:00Z",
            run_id="BL-TEST-WINDIGO-REGION-PROPOSAL",
            git_source_commit="0" * 40,
        )
        self.assertEqual(report["report_id"], REPORT_ID)
        self.assertEqual(report["summary"]["class_counts"], {"burned": 1, "background": 1})
        self.assertEqual([item["core_pixels"] for item in selected], [25, 25])
        self.assertEqual(report["route_evidence"]["burned"]["pixels"], 8_606)
        self.assertEqual(report["route_evidence"]["background"]["pixels"], 182)
        self.assertEqual(report["summary"]["owner_responses"], 0)
        self.assertEqual(report["summary"]["labels_created"], 0)
        self.assertEqual(report["input_label_set_version"], LABEL_SET_VERSION)
        self.assertIsNone(report["output_label_set_version"])
        self.assertIsNone(report["dataset_version"])
        self.assertIsNone(report["model_version"])
        self.assertNotEqual(
            report["candidates"][0]["proposal_binding_sha256"],
            report["candidates"][1]["proposal_binding_sha256"],
        )

    @unittest.skipUnless(
        PRE.is_dir()
        and POST.is_dir()
        and DELIVERY.is_file()
        and EXTRACTED.is_dir()
        and BOUNDARY.is_file()
        and SOURCE_REPORT.is_file(),
        "ignored exact Windigo custody unavailable",
    )
    def test_exact_outputs_bind_candidate_rasters_and_refuse_overwrite(self) -> None:
        report, selected, previews = build_report(
            pre_package=PRE,
            post_package=POST,
            archive_path=DELIVERY,
            extracted_root=EXTRACTED,
            boundary_path=BOUNDARY,
            source_report_path=SOURCE_REPORT,
            generated_at_utc="2026-07-23T22:00:00Z",
            run_id="BL-TEST-WINDIGO-REGION-PROPOSAL",
            git_source_commit="0" * 40,
        )
        with TemporaryDirectory() as parent:
            directory = Path(parent) / "outputs"
            outputs = write_outputs(report, selected, previews, directory)
            self.assertEqual(len(outputs), 5)
            payload = json.loads((directory / f"{REPORT_ID}.json").read_text())
            self.assertEqual(len(payload["candidates"]), 2)
            for candidate in payload["candidates"]:
                raster = directory / candidate["candidate_raster"]
                self.assertEqual(raster.stat().st_size, candidate["candidate_raster_bytes"])
                with rasterio.open(raster) as dataset:
                    self.assertEqual(dataset.tags()["candidate_id"], candidate["candidate_id"])
                    self.assertEqual(dataset.tags()["owner_decision"], "none")
                    self.assertEqual(dataset.tags()["label_created"], "false")
            with self.assertRaisesRegex(WindigoRegionProposalError, "already exists"):
                write_outputs(report, selected, previews, directory)


if __name__ == "__main__":
    unittest.main()
