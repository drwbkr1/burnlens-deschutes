from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from burnlens.phase_five_interface import (
    OUTPUT_HTML,
    PhaseFiveInterfaceError,
    build_interface,
    run_interface,
)


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "BL-2026-07-26-p5o1-t01-u03-reliability-interface-r999"
COMMIT = "c" * 40


class PhaseFiveInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.first = build_interface(
            repository_root=ROOT,
            generated_at_utc="2026-07-26T22:30:00Z",
            run_id=RUN_ID,
            git_source_commit=COMMIT,
        )

    def test_rejected_model_is_hidden_before_script(self) -> None:
        html = self.first["outputs"][OUTPUT_HTML].decode("utf-8")
        self.assertIn(
            'id="rejected-unet" data-layer="rejected-unet" hidden',
            html,
        )
        self.assertIn("<noscript>", html)
        self.assertIn(
            "The rejected U-Net stays hidden and is not promoted.",
            html,
        )

    def test_keyboard_text_reflow_and_offline_contract(self) -> None:
        checks = self.first["report"]["checks"]
        self.assertTrue(checks["skip_target_focusable"])
        self.assertTrue(checks["keyboard_native_controls"])
        self.assertTrue(checks["focus_visible"])
        self.assertTrue(checks["text_equivalent"])
        self.assertTrue(checks["non_color_failure_language"])
        self.assertTrue(checks["narrow_reflow"])
        self.assertTrue(checks["reduced_motion"])
        self.assertTrue(checks["offline_csp"])
        self.assertFalse(checks["external_runtime_reference"])

    def test_declared_contrast_pairs_pass(self) -> None:
        self.assertTrue(
            all(item["pass"] for item in self.first["report"]["contrast"])
        )
        self.assertGreaterEqual(
            min(item["ratio"] for item in self.first["report"]["contrast"]),
            3.0,
        )

    def test_exact_review_path_and_failure_evidence(self) -> None:
        html = self.first["outputs"][OUTPUT_HTML].decode("utf-8")
        self.assertIn("Four-step reviewer path", html)
        self.assertIn(
            "Five invalid packages fail before they can look accepted.",
            html,
        )
        self.assertIn("Retained pre-fix defects", html)
        self.assertIn("No claim that it outperformed", html)

    def test_determinism_and_no_overwrite(self) -> None:
        second = build_interface(
            repository_root=ROOT,
            generated_at_utc="2026-07-26T22:30:00Z",
            run_id=RUN_ID,
            git_source_commit=COMMIT,
        )
        self.assertEqual(self.first, second)
        with TemporaryDirectory(dir=ROOT / "downloads") as temporary:
            output = Path(temporary) / "interface"
            output.mkdir()
            (output / "keep.txt").write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(
                PhaseFiveInterfaceError,
                "refusing to overwrite",
            ):
                run_interface(
                    repository_root=ROOT,
                    output_directory=output,
                    generated_at_utc="2026-07-26T22:30:00Z",
                    run_id=RUN_ID,
                    git_source_commit=COMMIT,
                    require_clean=False,
                )


if __name__ == "__main__":
    unittest.main()
