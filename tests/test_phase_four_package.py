from __future__ import annotations

import io
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import zipfile

from burnlens.phase_four_package import (
    PACKAGE_VERSION,
    PhaseFourPackageError,
    build_package,
    validate_package,
)


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "BL-2026-07-26-p4o1-t01-u07-package-r999"
COMMIT = "a" * 40


class PhaseFourPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.first = build_package(
            repository_root=ROOT,
            generated_at_utc="2026-07-26T20:15:00Z",
            run_id=RUN_ID,
            git_source_commit=COMMIT,
        )

    def test_required_contents_and_boundaries(self) -> None:
        files = self.first["files"]
        for required in (
            "README.md",
            "REPORT.md",
            "WARNINGS.md",
            "REPLAY.md",
            "PACKAGE-MANIFEST.json",
            "CHECKSUMS.sha256",
            "config/MAP-CONFIG.json",
            "inventory/SOURCE-INVENTORY.json",
            "status/STATUS.json",
            "interface/index.html",
            "interface/interface-manifest.json",
            "evidence/u03-geospatial/run/vectors/rbr-accepted-polygons.gpkg",
            "evidence/u05-overlay/run/analysis/OVERLAY-SUMMARY.json",
        ):
            self.assertIn(required, files)
        serialized = b"".join(files.values()).lower()
        self.assertIn(b"model_accepted\": false", serialized)
        self.assertIn(b"model_outperformed_rbr\": false", serialized)
        self.assertIn(b"false-positive-risk", serialized)
        self.assertNotIn(b"c:\\users", serialized)
        self.assertNotIn(b"signed url", serialized)

    def test_archive_is_deterministic_safe_and_complete(self) -> None:
        second = build_package(
            repository_root=ROOT,
            generated_at_utc="2026-07-26T20:15:00Z",
            run_id=RUN_ID,
            git_source_commit=COMMIT,
        )
        self.assertEqual(self.first, second)
        with zipfile.ZipFile(io.BytesIO(self.first["archive"])) as archive:
            infos = archive.infolist()
            names = [item.filename for item in infos]
            self.assertEqual(len(names), len(set(names)))
            self.assertTrue(
                all(name.startswith(f"{PACKAGE_VERSION}/") for name in names)
            )
            self.assertFalse(any(".." in Path(name).parts for name in names))
            self.assertFalse(any(item.flag_bits & 0x1 for item in infos))
            self.assertIsNone(archive.testzip())

    def test_extracted_and_archive_validator(self) -> None:
        with TemporaryDirectory(dir=ROOT / "downloads") as temporary:
            base = Path(temporary)
            extracted = base / PACKAGE_VERSION
            for relative, payload in self.first["files"].items():
                path = extracted / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
            archive_path = base / "package.zip"
            archive_path.write_bytes(self.first["archive"])
            first = validate_package(extracted)
            second = validate_package(archive_path)
            self.assertEqual(first, second)
            self.assertEqual(first["result"], "PACKAGE_VALIDATION_PASS")
            self.assertEqual(first["geotiff_count"], 10)
            self.assertEqual(first["accepted_vector_feature_count"], 202)

    def test_bad_run_and_corrupt_archive_fail(self) -> None:
        with self.assertRaisesRegex(PhaseFourPackageError, "run ID"):
            build_package(
                repository_root=ROOT,
                generated_at_utc="2026-07-26T20:15:00Z",
                run_id="bad-run",
                git_source_commit=COMMIT,
            )
        with TemporaryDirectory(dir=ROOT / "downloads") as temporary:
            path = Path(temporary) / "bad.zip"
            path.write_bytes(b"not a zip")
            with self.assertRaises(zipfile.BadZipFile):
                validate_package(path)


if __name__ == "__main__":
    unittest.main()
