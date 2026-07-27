from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from burnlens.phase_six_portfolio_surface import (
    PhaseSixPortfolioSurfaceError,
    SURFACE_VERSION,
    build_surface,
    validate_surface,
    write_surface,
)


ROOT = Path(__file__).resolve().parents[1]
GENERATED = "2026-07-27T04:00:00Z"
RUN_ID = "BL-2026-07-27-p6o1-t01-u03-portfolio-surface-r999"
COMMIT = "a" * 40


class PhaseSixPortfolioSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.first = build_surface(
            repository_root=ROOT,
            generated_at_utc=GENERATED,
            run_id=RUN_ID,
            git_source_commit=COMMIT,
        )

    def test_build_is_deterministic_and_preserves_truth(self) -> None:
        second = build_surface(
            repository_root=ROOT,
            generated_at_utc=GENERATED,
            run_id=RUN_ID,
            git_source_commit=COMMIT,
        )
        self.assertEqual(self.first, second)
        manifest = self.first["manifest"]
        self.assertEqual(
            manifest["route"],
            "baseline-primary-with-rejected-model-diagnostic",
        )
        self.assertEqual(manifest["accepted_method"], "burnlens-baseline-v0.1.0")
        self.assertEqual(manifest["rejected_model"], "burnlens-unet-binary-v0.1.0")
        self.assertFalse(manifest["model_accepted"])
        self.assertFalse(manifest["model_outperformed_rbr"])
        self.assertFalse(manifest["public_action_authorized"])

    def test_written_surface_validates(self) -> None:
        with TemporaryDirectory(dir=ROOT / "downloads") as temporary:
            output_root = Path(temporary) / "surface"
            result = write_surface(
                repository_root=ROOT,
                output_root=output_root,
                generated_at_utc=GENERATED,
                run_id=RUN_ID,
                git_source_commit=COMMIT,
            )
            validation = validate_surface(
                output_root / SURFACE_VERSION,
                repository_root=ROOT,
            )
            self.assertEqual(
                result["result"],
                "PHASE_SIX_PORTFOLIO_SURFACE_WRITE_PASS",
            )
            self.assertEqual(
                validation["result"],
                "PHASE_SIX_PORTFOLIO_SURFACE_VALIDATION_PASS",
            )
            self.assertEqual(validation["external_links"], 0)
            self.assertEqual(validation["scripts"], 0)

    def test_surface_has_accessible_static_semantics(self) -> None:
        page = self.first["files"]["index.html"].decode("utf-8")
        self.assertIn('class="skip" href="#main"', page)
        self.assertIn('<main id="main" tabindex="-1">', page)
        self.assertIn('aria-labelledby="result-title"', page)
        self.assertIn("prefers-reduced-motion", page)
        self.assertIn("WCP-002", page)
        self.assertIn("66.76 ha", page)
        self.assertIn("did not outperform RBR", page)
        self.assertNotIn("<script", page.lower())
        self.assertNotIn("http://", page.lower())
        self.assertNotIn("https://", page.lower())
        self.assertNotIn("file://", page.lower())
        self.assertNotIn("c:\\users", page.lower())
        self.assertNotIn("c:\\projects", page.lower())

    def test_overwrite_and_tamper_fail_closed(self) -> None:
        with TemporaryDirectory(dir=ROOT / "downloads") as temporary:
            output_root = Path(temporary) / "surface"
            result = write_surface(
                repository_root=ROOT,
                output_root=output_root,
                generated_at_utc=GENERATED,
                run_id=RUN_ID,
                git_source_commit=COMMIT,
            )
            with self.assertRaisesRegex(
                PhaseSixPortfolioSurfaceError,
                "refusing to overwrite",
            ):
                write_surface(
                    repository_root=ROOT,
                    output_root=output_root,
                    generated_at_utc=GENERATED,
                    run_id=RUN_ID,
                    git_source_commit=COMMIT,
                )
            page = Path(result["index_path"])
            page.write_bytes(page.read_bytes() + b"tamper")
            with self.assertRaisesRegex(
                PhaseSixPortfolioSurfaceError,
                "output byte mismatch",
            ):
                validate_surface(
                    output_root / SURFACE_VERSION,
                    repository_root=ROOT,
                )

    def test_invalid_identity_fails(self) -> None:
        with self.assertRaisesRegex(
            PhaseSixPortfolioSurfaceError,
            "invalid U03 run ID",
        ):
            build_surface(
                repository_root=ROOT,
                generated_at_utc=GENERATED,
                run_id="bad",
                git_source_commit=COMMIT,
            )
        with self.assertRaisesRegex(
            PhaseSixPortfolioSurfaceError,
            "invalid git source commit",
        ):
            build_surface(
                repository_root=ROOT,
                generated_at_utc=GENERATED,
                run_id=RUN_ID,
                git_source_commit="bad",
            )


if __name__ == "__main__":
    unittest.main()
