from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
import unittest
from unittest.mock import patch

import burnlens.inspect_petes_lake_reference_fitness as command


class PetesLakeReferenceFitnessCliTests(unittest.TestCase):
    def test_help_does_not_probe_optional_geospatial_modules(self) -> None:
        with patch.object(command.importlib.util, "find_spec") as find_spec:
            with self.assertRaises(SystemExit) as raised:
                command.main(["--help"])
        self.assertEqual(raised.exception.code, 0)
        find_spec.assert_not_called()

    def test_real_execution_fails_bounded_when_geo_profile_is_absent(self) -> None:
        stderr = StringIO()
        arguments = [
            "--repository-root",
            str(Path.cwd()),
            "--generated-at-utc",
            "2026-07-22T00:00:00Z",
            "--mode",
            "preview",
        ]
        with (
            patch.object(command.importlib.util, "find_spec", return_value=None),
            patch.object(command, "_preflight") as preflight,
            redirect_stderr(stderr),
        ):
            return_code = command.main(arguments)

        self.assertEqual(return_code, 2)
        preflight.assert_not_called()
        message = stderr.getvalue()
        self.assertIn("PETES_LAKE_U05_REFERENCE_FITNESS_FAILED", message)
        self.assertIn("geo-research profile required", message)
        for module in command.GEO_RESEARCH_MODULES:
            self.assertIn(module, message)
        self.assertIn("-Profile geo-research", message)
        self.assertNotIn("Traceback", message)

    def test_broken_geo_profile_fails_bounded_without_preflight(self) -> None:
        arguments = [
            "--repository-root",
            str(Path.cwd()),
            "--generated-at-utc",
            "2026-07-22T00:00:00Z",
            "--mode",
            "preview",
        ]
        failures = (
            ImportError("simulated optional import failure"),
            OSError("simulated optional binary failure"),
            AttributeError("simulated optional initialization failure"),
        )
        for failure in failures:
            with self.subTest(error_type=type(failure).__name__):
                stderr = StringIO()
                with (
                    patch.object(
                        command.importlib.util, "find_spec", return_value=object()
                    ),
                    patch.object(
                        command.importlib,
                        "import_module",
                        side_effect=failure,
                    ),
                    patch.object(command, "_preflight") as preflight,
                    redirect_stderr(stderr),
                ):
                    return_code = command.main(arguments)

                self.assertEqual(return_code, 2)
                preflight.assert_not_called()
                message = stderr.getvalue()
                self.assertIn("geo-research profile incomplete or unusable", message)
                self.assertIn("-Profile geo-research", message)
                self.assertNotIn(str(failure), message)
                self.assertNotIn("Traceback", message)


if __name__ == "__main__":
    unittest.main()
