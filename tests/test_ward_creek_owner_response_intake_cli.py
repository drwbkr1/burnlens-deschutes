from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WardCreekOwnerResponseIntakeCliTests(unittest.TestCase):
    def _run_with_geo_imports_blocked(
        self,
        arguments: list[str],
    ) -> subprocess.CompletedProcess[str]:
        script = textwrap.dedent(
            """
            import builtins
            import sys

            original_import = builtins.__import__

            def blocked_import(name, *args, **kwargs):
                if name.split(".", 1)[0] in {"geopandas", "pyogrio", "pyproj", "shapely"}:
                    raise ModuleNotFoundError(
                        f"No module named {name!r}",
                        name=name.split(".", 1)[0],
                    )
                return original_import(name, *args, **kwargs)

            builtins.__import__ = blocked_import
            from burnlens.build_ward_creek_owner_response_intake import main
            raise SystemExit(main())
            """
        )
        return subprocess.run(
            [sys.executable, "-c", script, *arguments],
            cwd=ROOT,
            capture_output=True,
            check=False,
            text=True,
        )

    def test_help_does_not_require_geo_research_profile(self) -> None:
        completed = self._run_with_geo_imports_blocked(["--help"])
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("--response", completed.stdout)

    def test_execution_without_geo_profile_fails_with_setup_guidance(self) -> None:
        completed = self._run_with_geo_imports_blocked(
            [
                "--repository-root",
                ".",
                "--pre-package",
                "pre",
                "--post-package",
                "post",
                "--archive",
                "archive.zip",
                "--extracted-root",
                "extracted",
                "--background-report",
                "background.json",
                "--sufficiency-report",
                "sufficiency.json",
                "--proposal",
                "proposal.json",
                "--surface",
                "surface.json",
                "--response",
                "response.json",
                "--receipt",
                "receipt.json",
                "--private-output",
                "private.json",
                "--public-output-directory",
                "public",
                "--generated-at-utc",
                "2026-07-25T00:00:00Z",
                "--run-id",
                "test-run",
                "--git-source-commit",
                "0" * 40,
            ]
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("-Profile geo-research", completed.stderr)


if __name__ == "__main__":
    unittest.main()
