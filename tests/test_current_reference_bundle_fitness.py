from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
from PIL import Image

import burnlens
from burnlens.current_reference_bundle_fitness import (
    DECISION,
    STATE_NAMES,
    _cross_tab,
    _safe_member,
    render_html,
    render_png,
)


class CurrentReferenceBundleFitnessTests(unittest.TestCase):
    def test_version_and_entrypoint_are_current(self) -> None:
        self.assertEqual(burnlens.__version__, "0.27.0")
        pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
        self.assertIn("burnlens-inspect-current-reference-bundles", pyproject)

    def test_archive_paths_fail_closed(self) -> None:
        self.assertTrue(_safe_member("mtbs/2017/product/file.tif"))
        self.assertFalse(_safe_member("../escape.tif"))
        self.assertFalse(_safe_member("/absolute.tif"))
        self.assertFalse(_safe_member("folder\\mixed.tif"))

    def test_cross_tab_preserves_all_five_states(self) -> None:
        proposal = np.array([[0, 1, 2], [3, 4, 1]], dtype=np.uint8)
        categories = {
            "affirmative": np.array([[False, True, False], [False, True, True]]),
            "outside": np.array([[True, False, True], [True, False, False]]),
        }
        result = _cross_tab(proposal, proposal, categories)
        self.assertEqual(set(result), set(STATE_NAMES.values()))
        self.assertEqual(result["burned"]["proposal_pixels"], 2)
        self.assertEqual(result["burned"]["evidence_counts"]["affirmative"], 2)

    def test_render_is_deterministic_and_semantic(self) -> None:
        report = {
            "decision": DECISION,
            "events": [
                {
                    "display_name": "Synthetic",
                    "products": [{"program": "RAVG"}],
                    "categorical_cross_program_confirmation_available": False,
                    "proposal": {"state_counts": {name: 1 for name in STATE_NAMES.values()}},
                    "cross_program_categorical_agreement": None,
                }
            ],
            "git_source_commit": "a" * 40,
            "software_version": "0.24.0",
            "run_id": "BL-TEST-CURRENT-REFERENCE-BUNDLE-FITNESS",
            "next_checkpoint": "Owner review next.",
            "provenance": {"label_schema_version": "burn-scar-five-state-schema-v0.1.0"},
        }
        previews = [{
            "display_name": "Synthetic",
            "proposal": np.zeros((20, 30), dtype=np.uint8),
            "mtbs": None,
            "ravg": np.ones((20, 30), dtype=np.float32),
            "baer": np.zeros((20, 30), dtype=np.float32),
        }]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, second, html = root / "first.png", root / "second.png", root / "report.html"
            render_png(report, previews, first)
            render_png(report, previews, second)
            render_html(report, first.name, html)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with Image.open(first) as image:
                self.assertEqual(image.size, (1800, 1580))
            page = html.read_text(encoding="utf-8")
            self.assertIn("Zero labels", page)
            self.assertIn("yes/no/uncertain", page)
            self.assertIn("Thresholded legacy Tepee BARC", page)
            self.assertNotIn(b"\r\n", html.read_bytes())

    def test_public_contract_keeps_analytical_versions_null(self) -> None:
        fixture = {
            "dataset_version": None,
            "split_version": None,
            "baseline_version": None,
            "model_version": None,
        }
        self.assertEqual(json.loads(json.dumps(fixture)), fixture)


if __name__ == "__main__":
    unittest.main()
