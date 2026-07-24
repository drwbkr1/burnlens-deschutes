from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from burnlens.ward_creek_background_evidence import (
    EXPECTED_COUNTS,
    RUN_ID,
    SOURCE_REPORT_SHA256,
    WardCreekBackgroundEvidenceError,
    _read_source_report,
    build_report,
    render_html,
)


ROOT = Path(__file__).resolve().parents[1]
PRE = ROOT / "downloads/phase-two/raw/ward-creek-s2-optical-pre-v0.1.0"
POST = ROOT / "downloads/phase-two/raw/ward-creek-s2-optical-post-v0.1.0"
ARCHIVE = (
    ROOT
    / "downloads/phase-two/raw/ward-creek-mtbs-reference-v0.1.0/"
    "ward-creek-mtbs-reference-delivery-001.zip"
)
SOURCE_REPORT = (
    ROOT
    / "samples/reference/phase-two/ward-creek/reference-fitness-v0.1.1/"
    "WARD-CREEK-REFERENCE-FITNESS-2026-002.json"
)


class WardCreekBackgroundEvidenceTests(unittest.TestCase):
    def test_frozen_contract(self) -> None:
        self.assertEqual(RUN_ID, "BL-2026-07-24-ward-creek-background-evidence-r001")
        self.assertEqual(EXPECTED_COUNTS["route"], 21_266)
        self.assertEqual(EXPECTED_COUNTS["components_at_least_one_hectare"], 167)
        self.assertEqual(
            SOURCE_REPORT_SHA256,
            "f31bc51c64dae60b5a419146f4183b960b8504044f79e7505018a630c47c466d",
        )

    def test_source_report_binding(self) -> None:
        report = _read_source_report(SOURCE_REPORT)
        self.assertEqual(report["fitness_decision"]["source"], "PASS_EXACT_WARD_CREEK_MTBS_SOURCE_FITNESS")

    @unittest.skipUnless(
        PRE.is_dir() and POST.is_dir() and ARCHIVE.is_file() and SOURCE_REPORT.is_file(),
        "ignored exact custody unavailable",
    )
    def test_exact_sources_open_background_route_without_candidate(self) -> None:
        with TemporaryDirectory(dir=ROOT / "downloads/phase-two/runs/P2O4-T39-U04") as temporary:
            temporary = Path(temporary)
            head = subprocess.run(
                ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            report, _ = build_report(
                repository_root=ROOT,
                pre_package=PRE,
                post_package=POST,
                archive_path=ARCHIVE,
                extracted_root=temporary / "extracted",
                source_report_path=SOURCE_REPORT,
                generated_at_utc="2026-07-24T22:00:00Z",
                run_id=RUN_ID,
                git_source_commit=head,
            )
            self.assertEqual(
                report["fitness_decision"]["background_evidence_route"],
                "OPEN_AFFIRMATIVE_BACKGROUND_EVIDENCE_ROUTE",
            )
            self.assertEqual(report["route_evidence"]["counts"], EXPECTED_COUNTS)
            self.assertEqual(report["route_evidence"]["candidate_regions_created"], 0)
            self.assertEqual(report["route_evidence"]["labels_created"], 0)
            self.assertIsNone(report["dataset_version"])
            self.assertIsNone(report["model_version"])
            html = render_html(report, "evidence.png")
            self.assertIn("no candidate or label", html.lower())
            self.assertIn("No MTBS class is affirmative background truth.", html)

    @unittest.skipUnless(
        PRE.is_dir() and POST.is_dir() and ARCHIVE.is_file() and SOURCE_REPORT.is_file(),
        "ignored exact custody unavailable",
    )
    def test_wrong_commit_fails_before_extraction(self) -> None:
        with TemporaryDirectory(dir=ROOT / "downloads/phase-two/runs/P2O4-T39-U04") as temporary:
            extracted = Path(temporary) / "never-created"
            with self.assertRaisesRegex(
                WardCreekBackgroundEvidenceError,
                "repository HEAD",
            ):
                build_report(
                    repository_root=ROOT,
                    pre_package=PRE,
                    post_package=POST,
                    archive_path=ARCHIVE,
                    extracted_root=extracted,
                    source_report_path=SOURCE_REPORT,
                    generated_at_utc="2026-07-24T22:00:00Z",
                    run_id=RUN_ID,
                    git_source_commit="0" * 40,
                )
            self.assertFalse(extracted.exists())

    def test_mutated_source_report_fails_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "source.json"
            data = SOURCE_REPORT.read_bytes()
            path.write_bytes(data + b" ")
            self.assertNotEqual(sha256(path.read_bytes()).hexdigest(), SOURCE_REPORT_SHA256)
            with self.assertRaisesRegex(
                WardCreekBackgroundEvidenceError,
                "binding mismatch",
            ):
                _read_source_report(path)


if __name__ == "__main__":
    unittest.main()
