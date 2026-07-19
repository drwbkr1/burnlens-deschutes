from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

import numpy as np
from rasterio.io import MemoryFile
from rasterio.transform import Affine

from burnlens.green_ridge_reference_fitness import (
    ARCHIVE_SHA256,
    GreenRidgeReferenceFitnessError,
    _inspect_raster,
    _shapefile_record_count,
    build_report,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "downloads/phase-two/raw/green-ridge-s2-optical-pair-v0.1.0"
ARCHIVE = ROOT / "downloads/phase-two/quarantine/BL-2026-07-19-green-ridge-reference-delivery-r001/usgs-delivery-20260719232840Z.zip"
PLAN = ROOT / "samples/cross-event/phase-two/ADDITIONAL-EVENT-GROUP-PLAN-2026-001.json"


def raster_bytes(values: np.ndarray, nodata: int) -> bytes:
    with MemoryFile() as memory:
        with memory.open(
            driver="GTiff", width=values.shape[1], height=values.shape[0], count=1,
            dtype=values.dtype, crs="EPSG:32610", transform=Affine(30, 0, 600000, 0, -30, 4900000),
            nodata=nodata,
        ) as target:
            target.write(values, 1)
        return memory.read()


class GreenRidgeReferenceFitnessTests(unittest.TestCase):
    def test_categorical_inspection_preserves_encoded_nodata_class(self) -> None:
        values = np.array([[0, 1], [2, 4]], dtype=np.uint8)
        with TemporaryDirectory() as directory:
            path = Path(directory) / "test.zip"
            with ZipFile(path, "w") as archive:
                archive.writestr("test.tif", raster_bytes(values, 0))
            with ZipFile(path) as archive:
                profile, _ = _inspect_raster(archive, "test.tif")
        self.assertEqual(profile["native_value_domain"], {"0": 1, "1": 1, "2": 1, "4": 1})
        self.assertEqual(profile["nodata_pixels"], 1)

    def test_shapefile_parser_rejects_invalid_header(self) -> None:
        with self.assertRaisesRegex(GreenRidgeReferenceFitnessError, "header"):
            _shapefile_record_count(b"not a shapefile")

    @unittest.skipUnless(PACKAGE.is_dir() and ARCHIVE.is_file(), "ignored exact custody unavailable")
    def test_exact_delivery_and_optical_package_produce_expected_fitness(self) -> None:
        report, _ = build_report(
            package=PACKAGE, plan_path=PLAN, archive_path=ARCHIVE,
            generated_at_utc="2026-07-20T00:30:00Z", run_id="BL-TEST-GREEN-RIDGE-REFERENCE-FITNESS",
            git_source_commit="0" * 40,
        )
        self.assertEqual(report["archive"]["sha256"], ARCHIVE_SHA256)
        self.assertEqual(len(report["native_rasters"]), 20)
        self.assertEqual(report["evidence_comparison"]["both_programs_affirmative_pixels"], 41_642)
        self.assertEqual(report["evidence_comparison"]["either_program_affirmative_pixels"], 43_533)
        self.assertTrue(report["boundary_relationship"]["baer_mtbs_geometry_bytes_identical"])
        self.assertTrue(report["boundary_relationship"]["ravg_geometry_bytes_differ"])
        self.assertEqual(
            report["fitness_decision"]["reference_pixels"],
            "PASS_EXACT_GREEN_RIDGE_REFERENCE_SOURCE_FITNESS",
        )
        self.assertIsNone(report["trace"]["dataset_version"])
        self.assertIsNone(report["trace"]["model_version"])


if __name__ == "__main__":
    unittest.main()
