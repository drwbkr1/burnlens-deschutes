from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

from burnlens.submission_bundle import (
    BOUND_ASSETS,
    BUNDLE_ID,
    INTERNAL_MANIFEST,
    START_PAGE,
    SubmissionBundleError,
    build_bundle_contents,
    validate_bundle_archive,
    write_bundle_no_overwrite,
)


ROOT = Path(__file__).resolve().parents[1]
STAMP = "2026-07-24T04:10:00Z"
RUN_ID = "BL-2026-07-24-august6-submission-bundle-r001"
COMMIT = "0" * 40
PRESERVED_BUNDLE = (
    ROOT
    / "portfolio"
    / "submission"
    / "BURNLENS-AUGUST-6-SUBMISSION-2026-001.zip"
)


class SubmissionBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._frozen_inputs = tempfile.TemporaryDirectory()
        cls.frozen_root = Path(cls._frozen_inputs.name)
        with zipfile.ZipFile(PRESERVED_BUNDLE) as archive:
            for item in BOUND_ASSETS:
                target = cls.frozen_root / item.path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(item.path))

    @classmethod
    def tearDownClass(cls) -> None:
        cls._frozen_inputs.cleanup()

    def test_real_roster_builds_with_explicit_null_versions(self) -> None:
        contents = build_bundle_contents(
            repository_root=self.frozen_root,
            generated_at_utc=STAMP,
            run_id=RUN_ID,
            git_source_commit=COMMIT,
        )
        manifest = json.loads(contents[INTERNAL_MANIFEST])
        self.assertEqual(manifest["start_page"], START_PAGE)
        self.assertIsNone(manifest["dataset_version"])
        self.assertIsNone(manifest["split_version"])
        self.assertIsNone(manifest["baseline_version"])
        self.assertIsNone(manifest["model_version"])
        self.assertNotIn(b"../", contents[START_PAGE])
        self.assertIn(b"Official sources govern", contents[START_PAGE])

    def test_two_archives_are_byte_identical_and_validate(self) -> None:
        contents = build_bundle_contents(
            repository_root=self.frozen_root,
            generated_at_utc=STAMP,
            run_id=RUN_ID,
            git_source_commit=COMMIT,
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first, _ = write_bundle_no_overwrite(
                contents=contents,
                output_directory=root / "a",
                generated_at_utc=STAMP,
                run_id=RUN_ID,
                git_source_commit=COMMIT,
            )
            second, _ = write_bundle_no_overwrite(
                contents=contents,
                output_directory=root / "b",
                generated_at_utc=STAMP,
                run_id=RUN_ID,
                git_source_commit=COMMIT,
            )
            self.assertEqual(first.read_bytes(), second.read_bytes())
            manifest = validate_bundle_archive(first)
            self.assertEqual(manifest["bundle_id"], BUNDLE_ID)

    def test_output_overwrite_is_rejected(self) -> None:
        contents = build_bundle_contents(
            repository_root=self.frozen_root,
            generated_at_utc=STAMP,
            run_id=RUN_ID,
            git_source_commit=COMMIT,
        )
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            write_bundle_no_overwrite(
                contents=contents,
                output_directory=output,
                generated_at_utc=STAMP,
                run_id=RUN_ID,
                git_source_commit=COMMIT,
            )
            with self.assertRaisesRegex(SubmissionBundleError, "overwrite"):
                write_bundle_no_overwrite(
                    contents=contents,
                    output_directory=output,
                    generated_at_utc=STAMP,
                    run_id=RUN_ID,
                    git_source_commit=COMMIT,
                )

    def test_changed_bound_asset_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fixture = Path(temp)
            for item in BOUND_ASSETS:
                target = fixture / item.path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(self.frozen_root / item.path, target)
            first = fixture / BOUND_ASSETS[0].path
            first.write_bytes(first.read_bytes() + b"drift")
            with self.assertRaisesRegex(SubmissionBundleError, "size changed"):
                build_bundle_contents(
                    repository_root=fixture,
                    generated_at_utc=STAMP,
                    run_id=RUN_ID,
                    git_source_commit=COMMIT,
                )

    def test_current_mutable_case_study_is_not_silently_rebundled(self) -> None:
        with self.assertRaisesRegex(
            SubmissionBundleError,
            "bound asset size changed: docs/case-study/BURNLENS_CASE_STUDY.md",
        ):
            build_bundle_contents(
                repository_root=ROOT,
                generated_at_utc=STAMP,
                run_id=RUN_ID,
                git_source_commit=COMMIT,
            )

    def test_preserved_bundle_still_validates(self) -> None:
        manifest = validate_bundle_archive(PRESERVED_BUNDLE)
        self.assertEqual(manifest["bundle_id"], BUNDLE_ID)

    def test_duplicate_or_unsafe_archive_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "unsafe.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("../escape.txt", b"no")
                archive.writestr(INTERNAL_MANIFEST, b"{}")
                archive.writestr(START_PAGE, b"<html></html>")
            with self.assertRaisesRegex(SubmissionBundleError, "unsafe"):
                validate_bundle_archive(path)


if __name__ == "__main__":
    unittest.main()
