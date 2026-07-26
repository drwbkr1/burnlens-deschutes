from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from burnlens.phase_five_failure_injection import (
    CANONICAL_ARCHIVE,
    EXPECTED_ERRORS,
    PhaseFiveFailureInjectionError,
    build_injection_archives,
    run_failure_injections,
)


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "BL-2026-07-26-p5o1-t01-u02-failure-injection-r999"
COMMIT = "b" * 40


class PhaseFiveFailureInjectionTests(unittest.TestCase):
    def test_fixture_bytes_are_deterministic_and_complete(self) -> None:
        first = build_injection_archives(ROOT / CANONICAL_ARCHIVE)
        second = build_injection_archives(ROOT / CANONICAL_ARCHIVE)
        self.assertEqual(first, second)
        self.assertEqual(set(first), set(EXPECTED_ERRORS))
        self.assertTrue(all(first.values()))

    def test_full_injection_and_recovery_run(self) -> None:
        with TemporaryDirectory(dir=ROOT / "downloads") as temporary:
            base = Path(temporary)
            build = run_failure_injections(
                repository_root=ROOT,
                output_directory=base / "run",
                report_directory=base / "report",
                generated_at_utc="2026-07-26T22:00:00Z",
                run_id=RUN_ID,
                git_source_commit=COMMIT,
                require_clean=False,
            )
            result = build["result"]
            self.assertEqual(len(result["injections"]), 5)
            self.assertTrue(
                result["checks"]["all_invalid_fixtures_rejected"]
            )
            self.assertTrue(
                result["checks"][
                    "canonical_validated_after_every_injection"
                ]
            )
            self.assertFalse(result["checks"]["accepted_output_created"])
            self.assertIn(
                b"Failure is rejected before it can look accepted.",
                build["html_bytes"],
            )
            self.assertIn(
                b"rejected diagnostic",
                build["html_bytes"],
            )

    def test_no_overwrite(self) -> None:
        with TemporaryDirectory(dir=ROOT / "downloads") as temporary:
            base = Path(temporary)
            output = base / "run"
            output.mkdir()
            (output / "existing.txt").write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(
                PhaseFiveFailureInjectionError,
                "refusing to overwrite",
            ):
                run_failure_injections(
                    repository_root=ROOT,
                    output_directory=output,
                    report_directory=base / "report",
                    generated_at_utc="2026-07-26T22:00:00Z",
                    run_id=RUN_ID,
                    git_source_commit=COMMIT,
                    require_clean=False,
                )


if __name__ == "__main__":
    unittest.main()
