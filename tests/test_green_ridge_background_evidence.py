from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import numpy as np
from rasterio.io import MemoryFile
from rasterio.transform import Affine

from burnlens.green_ridge_background_evidence import (
    _component_sizes,
    _sample_categorical_preserve_zero,
    build_report,
)


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "downloads/phase-two/raw/green-ridge-s2-optical-pair-v0.1.0"
EXTENDED = ROOT / "downloads/phase-two/raw/green-ridge-s2-background-extended-v0.1.0"
REFERENCE = ROOT / "downloads/phase-two/quarantine/BL-2026-07-19-green-ridge-reference-delivery-r001/usgs-delivery-20260719232840Z.zip"
PLAN = ROOT / "samples/cross-event/phase-two/ADDITIONAL-EVENT-GROUP-PLAN-2026-001.json"


class GreenRidgeBackgroundEvidenceTests(unittest.TestCase):
    def test_component_sizes_use_eight_neighbors(self) -> None:
        mask = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=bool)
        self.assertEqual(_component_sizes(mask), [3])

    def test_categorical_sampling_preserves_encoded_zero(self) -> None:
        values = np.array([[0, 1], [2, 0]], dtype=np.uint8)
        with MemoryFile() as memory:
            with memory.open(
                driver="GTiff", width=2, height=2, count=1, dtype="uint8",
                crs="EPSG:32610", transform=Affine(30, 0, 600000, 0, -30, 4900000), nodata=0,
            ) as target:
                target.write(values, 1)
            with memory.open() as source:
                runtime = {
                    "array": source.read(1).copy(), "transform": source.transform,
                    "crs": source.crs, "nodata": source.nodata,
                }
                sampled = _sample_categorical_preserve_zero(runtime, (3, 3), source.transform)
        self.assertEqual(sampled[0, 0], 0)
        self.assertEqual(sampled[0, 1], 1)
        self.assertEqual(sampled[1, 0], 2)

    @unittest.skipUnless(
        ORIGINAL.is_dir() and EXTENDED.is_dir() and REFERENCE.is_file(),
        "ignored exact custody unavailable",
    )
    def test_exact_custody_opens_background_evidence_route_without_candidates(self) -> None:
        report, _ = build_report(
            original_package=ORIGINAL,
            extended_package=EXTENDED,
            plan_path=PLAN,
            reference_archive=REFERENCE,
            generated_at_utc="2026-07-20T01:00:00Z",
            run_id="BL-TEST-GREEN-RIDGE-BACKGROUND-EVIDENCE",
            git_source_commit="0" * 40,
        )
        self.assertEqual(report["route_evidence"]["eligible_pixels"], 26_126)
        self.assertEqual(report["route_evidence"]["components_at_least_one_hectare"], 128)
        self.assertEqual(report["route_evidence"]["largest_component_pixels"], 3_703)
        self.assertEqual(report["route_evidence"]["candidate_regions_created"], 0)
        self.assertEqual(report["route_evidence"]["labels_created"], 0)
        self.assertEqual(
            report["fitness_decision"]["background_evidence_route"],
            "OPEN_BACKGROUND_EVIDENCE_ROUTE_FOR_SEPARATE_CANDIDATE_PROPOSAL",
        )
        self.assertIsNone(report["trace"]["dataset_version"])
        self.assertIsNone(report["trace"]["model_version"])


if __name__ == "__main__":
    unittest.main()
