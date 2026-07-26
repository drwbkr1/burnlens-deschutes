from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import unittest

from PIL import Image

from burnlens.phase_four_overlay import (
    PhaseFourOverlayError,
    build_overlay_products,
)


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "BL-2026-07-26-p4o1-t01-u05-overlay-r999"
COMMIT = "e" * 40


class PhaseFourOverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.first = build_overlay_products(
            repository_root=ROOT,
            generated_at_utc="2026-07-26T19:30:00Z",
            run_id=RUN_ID,
            git_source_commit=COMMIT,
        )

    def test_exact_measurements_and_failure_evidence(self) -> None:
        metrics = self.first["manifest"]["measurement_contract"]["patches"]
        self.assertEqual(metrics["WCP-001"]["accepted_rbr_area_ha"], 141.44)
        self.assertEqual(
            metrics["WCP-001"]["accepted_rbr_inside_mtbs_pct"], 94.19
        )
        self.assertEqual(metrics["WCP-002"]["accepted_rbr_area_ha"], 66.76)
        self.assertEqual(
            metrics["WCP-002"]["accepted_rbr_inside_mtbs_pct"], 0.0
        )
        self.assertEqual(metrics["WCP-001"]["blm_overlap_area_m2"], 0.0)
        self.assertEqual(metrics["WCP-002"]["blm_overlap_area_m2"], 0.0)

    def test_outputs_are_deterministic_and_geospatial(self) -> None:
        second = build_overlay_products(
            repository_root=ROOT,
            generated_at_utc="2026-07-26T19:30:00Z",
            run_id=RUN_ID,
            git_source_commit=COMMIT,
        )
        self.assertEqual(self.first["outputs"], second["outputs"])
        for path in (
            "context/roads.geojson",
            "context/facilities.geojson",
            "context/blm-boundary.geojson",
            "reference/mtbs-ward-creek-boundary.geojson",
        ):
            value = json.loads(self.first["outputs"][path])
            self.assertEqual(value["type"], "FeatureCollection")
            self.assertTrue(value["features"])
        self.assertEqual(
            sha256(self.first["outputs"]["OVERLAY-QUICKLOOK.png"]).hexdigest(),
            sha256(second["outputs"]["OVERLAY-QUICKLOOK.png"]).hexdigest(),
        )

    def test_quicklook_and_claim_boundaries(self) -> None:
        from io import BytesIO

        with Image.open(BytesIO(self.first["outputs"]["OVERLAY-QUICKLOOK.png"])) as image:
            self.assertEqual(image.size, (1600, 1000))
        boundaries = self.first["manifest"]["boundaries"]
        self.assertFalse(boundaries["model_accepted"])
        self.assertFalse(boundaries["model_outperformed_rbr"])
        self.assertFalse(boundaries["unet_used_for_measurement"])
        self.assertFalse(boundaries["second_experiment_planned"])
        summary = json.loads(
            self.first["outputs"]["analysis/OVERLAY-SUMMARY.json"]
        )
        self.assertEqual(len(summary["observations"]), 5)
        self.assertIn(
            "false-positive-risk",
            summary["observations"][1]["interpretation_boundary"],
        )

    def test_bad_run_id_fails(self) -> None:
        with self.assertRaisesRegex(PhaseFourOverlayError, "run ID"):
            build_overlay_products(
                repository_root=ROOT,
                generated_at_utc="2026-07-26T19:30:00Z",
                run_id="bad-run",
                git_source_commit=COMMIT,
            )


if __name__ == "__main__":
    unittest.main()
