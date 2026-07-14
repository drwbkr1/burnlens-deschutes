from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import numpy as np
from PIL import Image

from burnlens.source_inspection import (
    InspectionError,
    point_in_geometry,
    render_html,
    render_png,
    summarize_scl,
)


def minimal_report() -> dict:
    return {
        "run_id": "BL-test-source-inspection-r001",
        "software_version": "0.4.0",
        "git_source_commit": "a" * 40,
        "package_id": "darlene3-s2-viirs-pair-v0.1.0",
        "package_verification": {
            "registration": {"contract_version": "paired-intake-contract-v0.4.0"}
        },
        "aoi": {"bbox_utm10n": [620000, 4831000, 632000, 4840000]},
        "sentinel_2_l2a": {
            "scene_classification": {
                "summary": {"medium_high_cloud_percent": 9.0282}
            }
        },
        "viirs_active_fire": {
            "aoi_fire_record_count": 2,
            "aoi_non_bowtie_reference_count": 1,
            "aoi_view_zenith_range_degrees": [69.02, 69.07],
            "aoi_records": [
                {
                    "sparse_index": 1,
                    "utm10n_x": 626000,
                    "utm10n_y": 4835000,
                    "confidence_name": "nominal",
                    "view_zenith_degrees": 69.02,
                    "qa_residual_bowtie": False,
                    "inside_nifc_final_reference": True,
                },
                {
                    "sparse_index": 2,
                    "utm10n_x": 628000,
                    "utm10n_y": 4836000,
                    "confidence_name": "high",
                    "view_zenith_degrees": 69.07,
                    "qa_residual_bowtie": True,
                    "inside_nifc_final_reference": False,
                },
            ],
        },
    }


class SourceInspectionTests(unittest.TestCase):
    def test_scl_summary_preserves_classes_and_quality_counts(self) -> None:
        values = np.array([[0, 3, 8], [9, 4, 4]], dtype=np.uint8)
        result = summarize_scl(values)
        self.assertEqual(result["pixel_count"], 6)
        self.assertEqual(result["medium_high_cloud_pixels"], 2)
        self.assertEqual(result["medium_high_cloud_percent"], 33.3333)
        self.assertEqual(result["cloud_shadow_pixels"], 1)
        self.assertEqual(result["no_data_pixels"], 1)
        by_value = {item["value"]: item for item in result["classes"]}
        self.assertEqual(by_value[4]["pixels"], 2)
        self.assertEqual(by_value[11]["pixels"], 0)

    def test_scl_unknown_class_fails_closed(self) -> None:
        with self.assertRaisesRegex(InspectionError, "unknown class"):
            summarize_scl(np.array([[12]], dtype=np.uint8))

    def test_point_in_multipolygon_respects_holes(self) -> None:
        geometry = {
            "type": "MultiPolygon",
            "coordinates": [
                [
                    [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]],
                    [[4, 4], [6, 4], [6, 6], [4, 6], [4, 4]],
                ]
            ],
        }
        self.assertTrue(point_in_geometry(2, 2, geometry))
        self.assertFalse(point_in_geometry(5, 5, geometry))
        self.assertFalse(point_in_geometry(20, 20, geometry))

    def test_rendered_evidence_is_deterministic_and_expected_size(self) -> None:
        report = minimal_report()
        rgb = np.zeros((3, 900, 1200), dtype=np.uint8)
        rgb[0] = 80
        rgb[1] = 100
        rgb[2] = 120
        geometry = {
            "type": "Polygon",
            "coordinates": [
                [
                    [622000, 4832000],
                    [630000, 4832000],
                    [630000, 4838000],
                    [622000, 4838000],
                    [622000, 4832000],
                ]
            ],
        }
        with TemporaryDirectory() as directory:
            first = Path(directory) / "first.png"
            second = Path(directory) / "second.png"
            render_png(report, rgb, geometry, first)
            render_png(report, rgb, geometry, second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with Image.open(first) as rendered:
                self.assertEqual(rendered.size, (1600, 1100))

    def test_html_has_decision_trace_and_boundaries(self) -> None:
        report = minimal_report()
        with TemporaryDirectory() as directory:
            path = Path(directory) / "report.html"
            render_html(report, "report.png", path)
            text = path.read_text(encoding="utf-8")
        self.assertIn("Reference accepted; label and dataset readiness deferred", text)
        self.assertIn("Do not promote it to labels", text)
        self.assertIn(report["run_id"], text)
        self.assertIn(report["git_source_commit"], text)
        self.assertIn("Official sources govern", text)
        self.assertNotIn("is field-validated", text)


if __name__ == "__main__":
    unittest.main()
