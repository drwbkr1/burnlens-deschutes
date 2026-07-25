from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

from burnlens.dataset_qa import (
    DATASET_MANIFEST_SHA256,
    _intersects,
    _normalization,
    _patch_bounds,
    build_report,
    render_html,
)
from burnlens.run_dataset_qa import verify_git_source_commit


ROOT = Path(__file__).resolve().parents[1]


class DatasetQaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report, cls.normalization, cls.render_arrays = build_report(
            ROOT,
            "2026-07-25T22:00:00Z",
            "BL-TEST-P2O5-T03-U04",
            "a" * 40,
        )

    def test_independent_reconstruction_passes_all_patches(self) -> None:
        self.assertEqual(
            self.report["inputs"]["dataset_manifest"]["sha256"],
            DATASET_MANIFEST_SHA256,
        )
        self.assertEqual(self.report["inventory"]["patches"], 12)
        self.assertEqual(self.report["inventory"]["reconstructed_patches"], 12)
        self.assertEqual(self.report["inventory"]["verified_patch_files"], 48)
        self.assertEqual(self.report["inventory"]["total_core_pixels"], 287)
        self.assertEqual(self.report["inventory"]["unknown_ring_pixels"], 531)

    def test_normalization_uses_train_only(self) -> None:
        self.assertFalse(self.normalization["validation_pixels_used"])
        self.assertFalse(self.normalization["test_pixels_used"])
        self.assertEqual(
            self.normalization["training_event_group_ids"],
            [
                "event-green-ridge-0684-cs-2020",
                "event-tepee-1144-ne-2018",
            ],
        )
        self.assertEqual(len(self.normalization["channels"]), 6)
        self.assertTrue(
            all(
                channel["eligible_pixel_count"] == 14723
                for channel in self.normalization["channels"]
            )
        )

    def test_test_is_reconstructed_for_integrity_but_not_rendered_or_summarized(self) -> None:
        self.assertFalse(self.report["inventory"]["test_rendered"])
        self.assertEqual(self.report["inventory"]["test_analytical_open_count"], 0)
        self.assertEqual(len(self.render_arrays), 8)
        self.assertTrue(
            all(not patch_id.startswith("test--") for patch_id in self.render_arrays)
        )
        self.assertFalse(self.report["boundaries"]["training_authorized"])

    def test_normalization_rejects_nonfinite_or_zero_variance_train_data(self) -> None:
        with self.assertRaisesRegex(Exception, "variance"):
            _normalization(
                [np.ones((6, 2, 2), dtype=np.float32)],
                [np.ones((2, 2), dtype=bool)],
                [f"c{i}" for i in range(6)],
            )

    def test_bounds_intersection_is_edge_exclusive(self) -> None:
        self.assertFalse(_intersects((0, 0, 1, 1), (1, 0, 2, 1)))
        self.assertTrue(_intersects((0, 0, 1.1, 1), (1, 0, 2, 1)))

    def test_html_preserves_claim_and_test_boundaries(self) -> None:
        html = render_html(self.report, "DATASET-QA-2026-001.png")
        self.assertIn("test analysis remains sealed", html)
        self.assertIn("Training remains unauthorized", html)
        self.assertIn("table{min-width:0;table-layout:fixed}", html)
        self.assertIn("body{overflow-x:hidden}", html)
        self.assertIn(".card strong{overflow-wrap:anywhere}", html)
        self.assertNotIn("ground truth achieved", html.lower())

    def test_runner_rejects_non_head_or_abbreviated_commit(self) -> None:
        with self.assertRaisesRegex(Exception, "full lowercase SHA-1"):
            verify_git_source_commit(ROOT, "d63c8a5")
        with self.assertRaisesRegex(Exception, "commit mismatch"):
            verify_git_source_commit(ROOT, "0" * 40)


if __name__ == "__main__":
    unittest.main()
