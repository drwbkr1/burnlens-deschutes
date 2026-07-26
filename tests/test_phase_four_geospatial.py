from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import sqlite3
import unittest
import warnings

import numpy as np
from rasterio.io import MemoryFile

from burnlens.phase_four_geospatial import (
    PhaseFourGeospatialError,
    build_geospatial_products,
)


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "BL-2026-07-26-p4o1-t01-u03-geospatial-r999"
COMMIT = "c" * 40


class PhaseFourGeospatialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.first = build_geospatial_products(
            repository_root=ROOT,
            generated_at_utc="2026-07-26T19:00:00Z",
            run_id=RUN_ID,
            git_source_commit=COMMIT,
        )

    def test_exact_raster_roster_and_native_georeferencing(self) -> None:
        self.assertEqual(len(self.first.manifest["rasters"]), 10)
        by_candidate = {
            "WCP-001": [20.0, 0.0, 667220.0, 0.0, -20.0, 4979800.0],
            "WCP-002": [20.0, 0.0, 670520.0, 0.0, -20.0, 4981800.0],
        }
        for item in self.first.manifest["rasters"]:
            with MemoryFile(self.first.outputs[item["path"]]) as memory:
                with memory.open() as dataset:
                    with warnings.catch_warnings():
                        warnings.filterwarnings(
                            "ignore",
                            message=(
                                r"Setting the shape on a NumPy array "
                                r"has been deprecated.*"
                            ),
                            category=DeprecationWarning,
                        )
                        first = dataset.read(1).copy()
                        second = dataset.read(1).copy()
                    self.assertEqual(dataset.crs.to_string(), "EPSG:32610")
                    self.assertEqual(
                        list(tuple(dataset.transform)[:6]),
                        by_candidate[item["candidate_id"]],
                    )
                    self.assertEqual(dataset.shape, (64, 64))
                    self.assertEqual(first.dtype, second.dtype)
                    self.assertEqual(
                        first.tobytes(order="C"), second.tobytes(order="C")
                    )

    def test_vectors_are_raw_valid_and_match_rbr_pixel_counts(self) -> None:
        validation = self.first.manifest["validation"]
        self.assertTrue(validation["all_geometries_valid"])
        self.assertTrue(validation["raw_binary_polygonization"])
        self.assertEqual(validation["simplification"], "none")
        self.assertEqual(
            validation["vector_summary"]["WCP-001"]["pixel_count"], 3536
        )
        self.assertEqual(
            validation["vector_summary"]["WCP-002"]["pixel_count"], 1669
        )
        connection = sqlite3.connect(":memory:")
        try:
            connection.deserialize(
                self.first.outputs["vectors/rbr-accepted-polygons.gpkg"]
            )
            self.assertEqual(
                connection.execute("PRAGMA integrity_check").fetchone(),
                ("ok",),
            )
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM rbr_accepted"
                ).fetchone()[0],
                validation["geometry_count"],
            )
        finally:
            connection.close()

    def test_output_build_is_byte_deterministic(self) -> None:
        second = build_geospatial_products(
            repository_root=ROOT,
            generated_at_utc="2026-07-26T19:00:00Z",
            run_id=RUN_ID,
            git_source_commit=COMMIT,
        )
        self.assertEqual(self.first.outputs, second.outputs)
        self.assertEqual(self.first.manifest, second.manifest)
        self.assertEqual(
            sha256(
                self.first.outputs["vectors/rbr-accepted-polygons.gpkg"]
            ).hexdigest(),
            sha256(
                second.outputs["vectors/rbr-accepted-polygons.gpkg"]
            ).hexdigest(),
        )

    def test_model_and_claim_boundaries_remain_false(self) -> None:
        diagnostic = self.first.manifest["rejected_diagnostic"]
        self.assertFalse(diagnostic["accepted"])
        self.assertFalse(diagnostic["outperformed_rbr"])
        boundaries = self.first.manifest["boundaries"]
        self.assertFalse(boundaries["phase_3b_created"])
        self.assertFalse(boundaries["second_experiment_planned"])
        self.assertFalse(boundaries["official_operational_or_emergency_claim"])

    def test_run_id_drift_fails_before_product_creation(self) -> None:
        with self.assertRaisesRegex(PhaseFourGeospatialError, "run ID"):
            build_geospatial_products(
                repository_root=ROOT,
                generated_at_utc="2026-07-26T19:00:00Z",
                run_id="bad-run",
                git_source_commit=COMMIT,
            )


if __name__ == "__main__":
    unittest.main()
