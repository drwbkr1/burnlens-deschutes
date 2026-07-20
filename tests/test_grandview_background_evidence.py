from __future__ import annotations

import unittest

import numpy as np
import rasterio

from burnlens.grandview_background_evidence import (
    GrandviewBackgroundEvidenceError,
    _registration_exclusion_mask,
    _reference_route_masks,
)


class GrandviewBackgroundEvidenceTests(unittest.TestCase):
    def test_outside_all_requires_baer_nodata_and_both_encoded_zeros(self) -> None:
        baer = np.array([[np.nan, 0.2], [np.nan, np.nan]], dtype=np.float32)
        mtbs = np.array([[0, 0], [2, 0]], dtype=np.uint8)
        ravg = np.array([[0, 0], [0, 3]], dtype=np.uint8)
        masks = _reference_route_masks(baer, mtbs, ravg)
        self.assertEqual(masks["outside_all"].tolist(), [[True, False], [False, False]])

    def test_ravg_modeled_value_only_excludes_and_never_affirms(self) -> None:
        baer = np.full((7, 7), np.nan, dtype=np.float32)
        mtbs = np.zeros((7, 7), dtype=np.uint8)
        ravg = np.zeros((7, 7), dtype=np.uint8)
        ravg[3, 3] = 4
        masks = _reference_route_masks(baer, mtbs, ravg)
        self.assertTrue(masks["ravg_footprint"][3, 3])
        self.assertFalse(masks["outside_all"][3, 3])
        self.assertEqual(int(masks["boundary_buffer"].sum()), 49)

    def test_grid_mismatch_fails_closed(self) -> None:
        with self.assertRaisesRegex(GrandviewBackgroundEvidenceError, "grids differ"):
            _reference_route_masks(
                np.zeros((2, 2), dtype=np.float32),
                np.zeros((2, 3), dtype=np.uint8),
                np.zeros((2, 2), dtype=np.uint8),
            )

    def test_registration_review_window_becomes_spatial_exclusion(self) -> None:
        transform = rasterio.Affine(20, 0, 0, 0, -20, 200)
        windows = [
            {"state": "pass", "bounds_utm10n": [0, 0, 20, 20]},
            {"state": "review-needed", "bounds_utm10n": [40, 40, 80, 80]},
        ]
        mask = _registration_exclusion_mask(windows, (10, 10), transform)
        self.assertEqual(int(mask.sum()), 4)
        self.assertTrue(mask[6:8, 2:4].all())


if __name__ == "__main__":
    unittest.main()
