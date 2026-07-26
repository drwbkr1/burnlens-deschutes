from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

from burnlens.phase_four_runner import (
    BYTE_NODATA,
    FLOAT_NODATA,
    PhaseFourRunnerError,
    build_analysis,
)


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "BL-2026-07-26-p4o1-t01-u02-analysis-r999"
COMMIT = "a" * 40


class PhaseFourRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.first = build_analysis(
            repository_root=ROOT,
            generated_at_utc="2026-07-26T18:00:00Z",
            run_id=RUN_ID,
            git_source_commit=COMMIT,
        )

    def test_exact_roster_and_method_separation(self) -> None:
        self.assertEqual(self.first.manifest["state"], "accepted-baseline")
        self.assertEqual(
            [item["candidate_id"] for item in self.first.manifest["patches"]],
            ["WCP-001", "WCP-002"],
        )
        self.assertEqual(
            self.first.manifest["methods"]["accepted"]["version"],
            "burnlens-baseline-v0.1.0",
        )
        diagnostic = self.first.manifest["methods"]["rejected_diagnostic"]
        self.assertEqual(
            diagnostic["version"], "burnlens-unet-binary-v0.1.0"
        )
        self.assertFalse(diagnostic["accepted"])
        self.assertFalse(diagnostic["outperformed_rbr"])
        facts = {
            item["candidate_id"]: item["facts"]
            for item in self.first.manifest["patches"]
        }
        self.assertEqual(facts["WCP-001"]["rbr_positive_pixels"], 3536)
        self.assertEqual(
            facts["WCP-001"]["unet_diagnostic_positive_pixels"], 4095
        )
        self.assertEqual(facts["WCP-002"]["rbr_positive_pixels"], 1669)
        self.assertEqual(
            facts["WCP-002"]["unet_diagnostic_positive_pixels"], 3206
        )

    def test_outputs_have_exact_shapes_domains_and_exclusion_semantics(self) -> None:
        for candidate in ("WCP-001", "WCP-002"):
            arrays = {}
            for name in (
                "rbr-score.npy",
                "rbr-binary.npy",
                "exclusion.npy",
                "unet-probability-diagnostic.npy",
                "unet-binary-diagnostic.npy",
            ):
                path = f"patches/{candidate}/{name}"
                arrays[name] = np.load(
                    __import__("io").BytesIO(self.first.outputs[path]),
                    allow_pickle=False,
                )
                self.assertEqual(arrays[name].shape, (64, 64))
            self.assertEqual(arrays["rbr-score.npy"].dtype, np.float32)
            self.assertEqual(
                arrays["unet-probability-diagnostic.npy"].dtype, np.float32
            )
            self.assertTrue(
                np.isin(arrays["rbr-binary.npy"], [0, 1, BYTE_NODATA]).all()
            )
            self.assertTrue(
                np.isin(
                    arrays["unet-binary-diagnostic.npy"],
                    [0, 1, BYTE_NODATA],
                ).all()
            )
            valid = arrays["exclusion.npy"] == 0
            self.assertTrue(valid.all())
            self.assertFalse(
                np.any(arrays["rbr-score.npy"][valid] == FLOAT_NODATA)
            )

    def test_fixed_build_is_byte_deterministic(self) -> None:
        second = build_analysis(
            repository_root=ROOT,
            generated_at_utc="2026-07-26T18:00:00Z",
            run_id=RUN_ID,
            git_source_commit=COMMIT,
        )
        self.assertEqual(self.first.outputs, second.outputs)
        self.assertEqual(self.first.manifest, second.manifest)

    def test_run_id_drift_fails_before_array_loading(self) -> None:
        with self.assertRaisesRegex(PhaseFourRunnerError, "run ID"):
            build_analysis(
                repository_root=ROOT,
                generated_at_utc="2026-07-26T18:00:00Z",
                run_id="bad-run",
                git_source_commit=COMMIT,
            )


if __name__ == "__main__":
    unittest.main()
