from __future__ import annotations

import io
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import zipfile

from burnlens.phase_five_release_candidate import (
    CANDIDATE_VERSION,
    PhaseFiveCandidateError,
    build_candidate,
    validate_candidate,
    write_candidate,
)


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "BL-2026-07-26-p5o1-t01-u06-release-candidate-r999"
COMMIT = "a" * 40
GENERATED = "2026-07-27T01:30:00Z"


class PhaseFiveReleaseCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.first = build_candidate(
            repository_root=ROOT,
            generated_at_utc=GENERATED,
            run_id=RUN_ID,
            git_source_commit=COMMIT,
        )

    def test_candidate_is_deterministic_and_preserves_truth(self) -> None:
        second = build_candidate(
            repository_root=ROOT,
            generated_at_utc=GENERATED,
            run_id=RUN_ID,
            git_source_commit=COMMIT,
        )
        self.assertEqual(self.first, second)
        self.assertEqual(
            self.first["files"][
                "phase-four/BURNLENS-WARD-CREEK-RBR-RUN-2026-001.zip"
            ],
            (
                ROOT
                / "portfolio/phase-four/"
                "BURNLENS-WARD-CREEK-RBR-RUN-2026-001.zip"
            ).read_bytes(),
        )
        manifest = self.first["manifest"]
        self.assertEqual(manifest["state"], "accepted-baseline-first-candidate")
        self.assertFalse(manifest["model_accepted"])
        self.assertFalse(manifest["model_outperformed_rbr"])
        self.assertEqual(manifest["open_findings"]["medium"], 2)
        self.assertEqual(manifest["open_findings"]["critical"], 0)
        self.assertEqual(manifest["open_findings"]["high"], 0)

    def test_archive_is_safe_and_complete(self) -> None:
        with zipfile.ZipFile(io.BytesIO(self.first["archive"])) as archive:
            infos = archive.infolist()
            names = [item.filename for item in infos]
            self.assertEqual(len(names), len(set(names)))
            self.assertTrue(
                all(name.startswith(f"{CANDIDATE_VERSION}/") for name in names)
            )
            self.assertFalse(any(".." in Path(name).parts for name in names))
            self.assertFalse(any(item.flag_bits & 0x1 for item in infos))
            self.assertIsNone(archive.testzip())

    def test_written_directory_and_archive_validate(self) -> None:
        with TemporaryDirectory(dir=ROOT / "downloads") as temporary:
            base = Path(temporary)
            result = write_candidate(
                repository_root=ROOT,
                output_root=base / "samples",
                archive_root=base / "portfolio",
                generated_at_utc=GENERATED,
                run_id=RUN_ID,
                git_source_commit=COMMIT,
            )
            directory = validate_candidate(Path(result["package_root"]))
            archive = validate_candidate(Path(result["archive_path"]))
            self.assertEqual(
                directory["result"],
                "PHASE_FIVE_CANDIDATE_VALIDATION_PASS",
            )
            self.assertEqual(directory["file_count"], archive["file_count"])
            self.assertEqual(
                directory["extracted_bytes"],
                archive["extracted_bytes"],
            )
            receipt = Path(result["receipt_path"]).read_bytes().lower()
            self.assertNotIn(b"c:\\users", receipt)
            self.assertNotIn(b"c:\\projects", receipt)

    def test_tamper_and_overwrite_fail_closed(self) -> None:
        with TemporaryDirectory(dir=ROOT / "downloads") as temporary:
            base = Path(temporary)
            result = write_candidate(
                repository_root=ROOT,
                output_root=base / "samples",
                archive_root=base / "portfolio",
                generated_at_utc=GENERATED,
                run_id=RUN_ID,
                git_source_commit=COMMIT,
            )
            with self.assertRaisesRegex(
                PhaseFiveCandidateError,
                "refusing to overwrite",
            ):
                write_candidate(
                    repository_root=ROOT,
                    output_root=base / "samples",
                    archive_root=base / "portfolio",
                    generated_at_utc=GENERATED,
                    run_id=RUN_ID,
                    git_source_commit=COMMIT,
                )
            package_root = Path(result["package_root"])
            readme = package_root / "README.md"
            readme.write_bytes(readme.read_bytes() + b"tamper")
            with self.assertRaisesRegex(
                PhaseFiveCandidateError,
                "manifest byte mismatch",
            ):
                validate_candidate(package_root)

    def test_traversal_archive_and_invalid_bindings_fail(self) -> None:
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as archive:
            archive.writestr(
                f"{CANDIDATE_VERSION}/../escape.txt",
                b"escape",
            )
        with TemporaryDirectory(dir=ROOT / "downloads") as temporary:
            archive_path = Path(temporary) / "bad.zip"
            archive_path.write_bytes(stream.getvalue())
            with self.assertRaisesRegex(
                PhaseFiveCandidateError,
                "unsafe archive member",
            ):
                validate_candidate(archive_path)
        with self.assertRaisesRegex(
            PhaseFiveCandidateError,
            "invalid U06 run ID",
        ):
            build_candidate(
                repository_root=ROOT,
                generated_at_utc=GENERATED,
                run_id="bad",
                git_source_commit=COMMIT,
            )


if __name__ == "__main__":
    unittest.main()
