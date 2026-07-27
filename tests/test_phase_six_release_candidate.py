from __future__ import annotations

import io
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import zipfile

from burnlens.phase_six_release_candidate import (
    CANONICAL_ENTRYPOINT,
    PACKAGE_VERSION,
    PhaseSixCandidateError,
    build_candidate,
    validate_candidate,
    write_candidate,
)


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "BL-2026-07-27-p6o1-t01-u05-pre-publication-package-r999"
COMMIT = "a" * 40
GENERATED = "2026-07-27T05:00:00Z"


class PhaseSixReleaseCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.first = build_candidate(
            repository_root=ROOT,
            generated_at_utc=GENERATED,
            run_id=RUN_ID,
            git_source_commit=COMMIT,
        )

    def test_candidate_is_deterministic_and_preserves_frozen_truth(self) -> None:
        second = build_candidate(
            repository_root=ROOT,
            generated_at_utc=GENERATED,
            run_id=RUN_ID,
            git_source_commit=COMMIT,
        )
        self.assertEqual(self.first, second)
        self.assertEqual(
            self.first["files"][CANONICAL_ENTRYPOINT],
            (ROOT / CANONICAL_ENTRYPOINT).read_bytes(),
        )
        self.assertEqual(
            self.first["files"][
                "portfolio/phase-four/"
                "BURNLENS-WARD-CREEK-RBR-RUN-2026-001.zip"
            ],
            (
                ROOT
                / "portfolio/phase-four/"
                "BURNLENS-WARD-CREEK-RBR-RUN-2026-001.zip"
            ).read_bytes(),
        )
        manifest = self.first["manifest"]
        self.assertEqual(manifest["state"], "local-pre-publication-candidate")
        self.assertFalse(manifest["model_accepted"])
        self.assertFalse(manifest["model_outperformed_rbr"])
        self.assertFalse(manifest["public_action_authorized"])
        self.assertTrue(manifest["closure"]["complete_local_link_closure"])
        self.assertTrue(manifest["closure"]["complete_phase_five_directory"])

    def test_archive_is_safe_complete_and_fixed(self) -> None:
        with zipfile.ZipFile(io.BytesIO(self.first["archive"])) as archive:
            infos = archive.infolist()
            names = [item.filename for item in infos]
            self.assertEqual(len(names), len(set(names)))
            self.assertTrue(
                all(name.startswith(f"{PACKAGE_VERSION}/") for name in names)
            )
            self.assertFalse(any(".." in Path(name).parts for name in names))
            self.assertFalse(any(item.flag_bits & 0x1 for item in infos))
            self.assertTrue(
                all(item.date_time == (2026, 1, 1, 0, 0, 0) for item in infos)
            )
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
                "PHASE_SIX_CANDIDATE_VALIDATION_PASS",
            )
            self.assertEqual(directory["file_count"], archive["file_count"])
            self.assertEqual(
                directory["extracted_bytes"],
                archive["extracted_bytes"],
            )
            self.assertGreater(directory["local_links"], 100)
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
                PhaseSixCandidateError,
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
                PhaseSixCandidateError,
                "manifest byte mismatch",
            ):
                validate_candidate(package_root)

    def test_traversal_archive_and_invalid_bindings_fail(self) -> None:
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as archive:
            archive.writestr(
                f"{PACKAGE_VERSION}/../escape.txt",
                b"escape",
            )
        with TemporaryDirectory(dir=ROOT / "downloads") as temporary:
            archive_path = Path(temporary) / "bad.zip"
            archive_path.write_bytes(stream.getvalue())
            with self.assertRaisesRegex(
                PhaseSixCandidateError,
                "unsafe archive member",
            ):
                validate_candidate(archive_path)
        with self.assertRaisesRegex(
            PhaseSixCandidateError,
            "invalid U05 run ID",
        ):
            build_candidate(
                repository_root=ROOT,
                generated_at_utc=GENERATED,
                run_id="bad",
                git_source_commit=COMMIT,
            )

    def test_package_excludes_private_custody_and_model_weights(self) -> None:
        names = {name.lower() for name in self.first["files"]}
        self.assertFalse(
            any(
                Path(name).suffix
                in {".pt", ".pth", ".onnx", ".ckpt", ".safetensors"}
                for name in names
            )
        )
        self.assertFalse(
            any(
                part in {"raw", "quarantine", "custody", "downloads"}
                for name in names
                for part in Path(name).parts
            )
        )
        serialized = b"\n".join(self.first["files"].values()).lower()
        self.assertNotIn(b"c:\\users", serialized)
        self.assertNotIn(b"c:\\projects", serialized)
        self.assertNotIn(b"owner-review-surface-2026-001-response", serialized)

    def test_checksum_roster_has_checkout_stable_lf_bytes(self) -> None:
        attributes = (ROOT / ".gitattributes").read_text(
            encoding="utf-8"
        ).splitlines()
        self.assertIn(
            "samples/runs/phase-six/**/*.sha256 text eol=lf",
            attributes,
        )


if __name__ == "__main__":
    unittest.main()
