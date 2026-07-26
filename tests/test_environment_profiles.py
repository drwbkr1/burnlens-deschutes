import importlib.util
import json
import subprocess
import sys
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFY_SCRIPT = ROOT / "scripts" / "verify_environment.py"
GEO_MODULES = (
    "boto3",
    "geopandas",
    "pyogrio",
    "pyproj",
    "pystac_client",
    "rioxarray",
    "shapely",
    "xarray",
)
MODEL_MODULES = ("torch",)


def _run_smoke(profile: str) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
    completed = subprocess.run(
        [sys.executable, str(VERIFY_SCRIPT), "--profile", profile],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    payload = json.loads(completed.stdout)
    return completed, payload


class EnvironmentProfileTests(unittest.TestCase):
    def test_environment_dependencies_are_exactly_pinned(self) -> None:
        with (ROOT / "pyproject.toml").open("rb") as stream:
            project = tomllib.load(stream)["project"]

        self.assertEqual(project["requires-python"], ">=3.12")
        self.assertEqual(project["license"], "MIT")
        self.assertEqual(project["license-files"], ["LICENSE"])
        requirements = list(project["dependencies"])
        requirements.extend(project["optional-dependencies"]["dev"])
        requirements.extend(project["optional-dependencies"]["geo-research"])
        requirements.extend(project["optional-dependencies"]["model"])

        self.assertEqual(len(requirements), len(set(requirements)))
        for requirement in requirements:
            self.assertEqual(requirement.count("=="), 1, requirement)
            self.assertNotIn("*", requirement)
            self.assertNotIn(";", requirement)

    def test_lock_file_has_checkout_stable_lf_bytes(self) -> None:
        attributes = subprocess.run(
            ["git", "check-attr", "text", "eol", "--", "uv.lock"],
            cwd=ROOT,
            capture_output=True,
            check=True,
            text=True,
        )
        self.assertEqual(
            attributes.stdout.splitlines(),
            ["uv.lock: text: set", "uv.lock: eol: lf"],
        )

    def test_codex_environment_selects_locked_geo_profile(self) -> None:
        with (ROOT / ".codex" / "environments" / "geospatial.toml").open(
            "rb"
        ) as stream:
            environment = tomllib.load(stream)
        setup = (ROOT / "scripts" / "setup_worktree.ps1").read_text(encoding="utf-8")

        self.assertEqual(set(environment), {"version", "name", "setup", "actions"})
        self.assertEqual(environment["version"], 1)
        self.assertEqual(environment["name"], "BurnLens geospatial research (Windows)")
        self.assertEqual(
            environment["setup"],
            {
                "script": (
                    "powershell.exe -NoProfile -ExecutionPolicy Bypass "
                    "-File scripts/setup_worktree.ps1 -Profile geo-research"
                )
            },
        )
        self.assertEqual(
            environment["actions"],
            [
                {
                    "name": "Verify geospatial environment",
                    "icon": "run",
                    "command": (
                        ".\\.venv\\Scripts\\python.exe "
                        "scripts\\verify_environment.py --profile geo-research"
                    ),
                },
                {
                    "name": "Run BurnLens tests",
                    "icon": "run",
                    "command": ".\\.venv\\Scripts\\python.exe -m pytest -q",
                },
            ],
        )
        self.assertIn("uv.lock", setup)
        self.assertIn("'--locked'", setup)
        self.assertNotIn("'--frozen'", setup)
        self.assertIn("pip check --python", setup)
        self.assertIn("Move it aside explicitly before setup", setup)
        self.assertIn("Another BurnLens environment setup is already running", setup)
        self.assertNotIn("credentials\\", setup.lower())
        self.assertTrue((ROOT / "uv.lock").is_file())

    def test_codex_environment_selects_locked_model_profile(self) -> None:
        with (ROOT / ".codex" / "environments" / "model.toml").open("rb") as stream:
            environment = tomllib.load(stream)
        setup = (ROOT / "scripts" / "setup_worktree.ps1").read_text(encoding="utf-8")

        self.assertEqual(set(environment), {"version", "name", "setup", "actions"})
        self.assertEqual(environment["version"], 1)
        self.assertEqual(
            environment["name"], "BurnLens bounded U-Net research (Windows CPU)"
        )
        self.assertEqual(
            environment["setup"],
            {
                "script": (
                    "powershell.exe -NoProfile -ExecutionPolicy Bypass "
                    "-File scripts/setup_worktree.ps1 -Profile model-research"
                )
            },
        )
        self.assertEqual(
            environment["actions"],
            [
                {
                    "name": "Verify model environment",
                    "icon": "run",
                    "command": (
                        ".\\.venv\\Scripts\\python.exe "
                        "scripts\\verify_environment.py --profile model-research"
                    ),
                },
                {
                    "name": "Run BurnLens tests",
                    "icon": "run",
                    "command": ".\\.venv\\Scripts\\python.exe -m pytest -q",
                },
            ],
        )
        self.assertIn("'model-research'", setup)
        self.assertIn("'--extra', 'model'", setup)

    def test_runtime_profile_smoke(self) -> None:
        completed, payload = _run_smoke("runtime")
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["profile"], "runtime")
        self.assertEqual(payload["checks"]["runtime"]["raster_sum"], 120)
        self.assertEqual(payload["checks"]["console_entry_points"]["count"], 106)
        self.assertEqual(payload["checks"]["console_entry_points"]["help_count"], 106)
        self.assertEqual(
            len(payload["checks"]["console_entry_points"]["names"]), 106
        )

    @unittest.skipUnless(
        all(importlib.util.find_spec(module) is not None for module in GEO_MODULES),
        "geo-research optional dependencies are not installed",
    )
    def test_geo_research_profile_smoke(self) -> None:
        completed, payload = _run_smoke("geo-research")
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["profile"], "geo-research")
        self.assertEqual(payload["checks"]["geo_research"]["geopackage_rows"], 1)
        self.assertEqual(payload["checks"]["geo_research"]["overlap_area_m2"], 800.0)
        self.assertEqual(payload["checks"]["geo_research"]["projected_area_m2"], 1600.0)

    @unittest.skipUnless(
        all(importlib.util.find_spec(module) is not None for module in MODEL_MODULES),
        "model optional dependencies are not installed",
    )
    def test_model_research_profile_smoke(self) -> None:
        completed, payload = _run_smoke("model-research")
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["profile"], "model-research")
        model = payload["checks"]["model_research"]
        self.assertEqual(model["torch"].split("+", 1)[0], "2.13.0")
        self.assertFalse(model["cuda_available"])
        self.assertIsNone(model["cuda_build"])
        self.assertTrue(model["deterministic_algorithms"])
        self.assertFalse(model["deterministic_warn_only"])
        self.assertEqual(model["threads"], 1)
        self.assertEqual(model["interop_threads"], 1)


if __name__ == "__main__":
    unittest.main()
