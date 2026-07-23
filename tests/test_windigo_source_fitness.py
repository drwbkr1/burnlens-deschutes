from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import numpy as np

from burnlens.windigo_source_fitness import (
    ARCHIVE_SHA256,
    REPORT_ID,
    WindigoSourceFitnessError,
    _counts,
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


class WindigoSourceFitnessTests(unittest.TestCase):
    def test_counts_respects_mask(self) -> None:
        values = np.array([[1, 2], [2, 4]], dtype=np.uint8)
        mask = np.array([[True, False], [True, True]])
        self.assertEqual(_counts(values, mask), {"1": 1, "2": 1, "4": 1})

    def test_pdf_review_fails_closed(self) -> None:
        with self.assertRaisesRegex(WindigoSourceFitnessError, "PDF"):
            build_report(
                pre_package=Path("missing"),
                post_package=Path("missing"),
                archive_path=Path("missing"),
                extracted_root=Path("missing"),
                boundary_path=Path("missing"),
                generated_at_utc="2026-07-23T21:00:00Z",
                run_id="BL-TEST",
                git_source_commit="0" * 40,
                pdf_visual_review="PENDING",
            )

    @unittest.skipUnless(
        PRE.is_dir()
        and POST.is_dir()
        and DELIVERY.is_file()
        and EXTRACTED.is_dir()
        and BOUNDARY.is_file(),
        "ignored exact Windigo custody unavailable",
    )
    def test_exact_custody_produces_expected_source_fitness(self) -> None:
        report, previews = build_report(
            pre_package=PRE,
            post_package=POST,
            archive_path=DELIVERY,
            extracted_root=EXTRACTED,
            boundary_path=BOUNDARY,
            generated_at_utc="2026-07-23T21:00:00Z",
            run_id="BL-TEST-WINDIGO-SOURCE-FITNESS",
            git_source_commit="0" * 40,
            pdf_visual_review="PASS_EXACT_FOUR_PROVIDER_MAP_PDFS",
        )
        self.assertEqual(report["report_id"], REPORT_ID)
        self.assertEqual(report["archive"]["sha256"], ARCHIVE_SHA256)
        self.assertEqual(len(report["native_rasters"]), 21)
        self.assertEqual(
            report["fitness_decision"]["source"],
            "PASS_EXACT_WINDIGO_SOURCE_FITNESS_WITH_VECTOR_EXCLUSIONS",
        )
        self.assertEqual(
            report["evidence_comparison"][
                "baer_mtbs_agreement_and_optical_valid_pixels"
            ],
            9_789,
        )
        vectors = {
            item["program"]: item for item in report["boundary_vectors"]
        }
        self.assertFalse(vectors["BAER"]["valid"])
        self.assertFalse(vectors["RAVG"]["valid"])
        self.assertTrue(vectors["MTBS"]["valid"])
        self.assertTrue(
            all(not item["repair_performed"] for item in vectors.values())
        )
        self.assertIsNone(report["dataset_version"])
        self.assertIsNone(report["model_version"])
        self.assertEqual(previews["boundary_mask20"].shape, (153, 158))

    @unittest.skipUnless(
        PRE.is_dir()
        and POST.is_dir()
        and DELIVERY.is_file()
        and EXTRACTED.is_dir()
        and BOUNDARY.is_file(),
        "ignored exact Windigo custody unavailable",
    )
    def test_exact_outputs_refuse_overwrite(self) -> None:
        report, previews = build_report(
            pre_package=PRE,
            post_package=POST,
            archive_path=DELIVERY,
            extracted_root=EXTRACTED,
            boundary_path=BOUNDARY,
            generated_at_utc="2026-07-23T21:00:00Z",
            run_id="BL-TEST-WINDIGO-SOURCE-FITNESS",
            git_source_commit="0" * 40,
            pdf_visual_review="PASS_EXACT_FOUR_PROVIDER_MAP_PDFS",
        )
        with TemporaryDirectory() as directory:
            outputs = write_outputs(report, previews, Path(directory))
            self.assertEqual(set(outputs), {"json", "html", "png"})
            with self.assertRaisesRegex(
                WindigoSourceFitnessError, "already exists"
            ):
                write_outputs(report, previews, Path(directory))


if __name__ == "__main__":
    unittest.main()
