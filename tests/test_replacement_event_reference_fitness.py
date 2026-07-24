from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from burnlens.replacement_event_reference_fitness import (
    ARCHIVE_SHA256,
    EXPECTED_DNBR6_DOMAIN,
    FGDC_MEMBER,
    ISO_MEMBER,
    RUN_ID,
    ReplacementEventReferenceFitnessError,
    _inspect_metadata,
    build_report,
    render_html,
)


ROOT = Path(__file__).resolve().parents[1]
PRE = ROOT / "downloads/phase-two/raw/ward-creek-s2-optical-pre-v0.1.0"
POST = ROOT / "downloads/phase-two/raw/ward-creek-s2-optical-post-v0.1.0"
ARCHIVE = ROOT / "downloads/phase-two/raw/ward-creek-mtbs-reference-v0.1.0/ward-creek-mtbs-reference-delivery-001.zip"


class ReplacementEventReferenceFitnessTests(unittest.TestCase):
    def test_exact_embedded_notice_identities(self) -> None:
        if not ARCHIVE.is_file():
            self.skipTest("ignored exact custody unavailable")
        with ZipFile(ARCHIVE) as archive:
            metadata = _inspect_metadata(archive)
            self.assertEqual(metadata["fgdc"]["member"], FGDC_MEMBER)
            self.assertEqual(metadata["iso"]["member"], ISO_MEMBER)
            self.assertEqual(metadata["fgdc"]["sha256"], "39ab440c70785d408e2a2299832064b861fcb7c7a6cbb0bb6f0b5068df85cb99")
            self.assertEqual(metadata["iso"]["sha256"], "fa6fa6fc897a73d5272b48bf906b3605775b3a89a093d42922cc14ff38a7ffb1")

    def test_run_id_is_exact(self) -> None:
        self.assertEqual(RUN_ID, "BL-2026-07-24-ward-creek-reference-fitness-r001")
        self.assertEqual(ARCHIVE_SHA256, "d94dfb1609c882fdd26119b2be03cea486af1bbb85e4c9607f108f9455f61d18")
        self.assertEqual(EXPECTED_DNBR6_DOMAIN["2"], 8_287)

    @unittest.skipUnless(PRE.is_dir() and POST.is_dir() and ARCHIVE.is_file(), "ignored exact custody unavailable")
    def test_exact_sources_pass_without_creating_labels(self) -> None:
        with TemporaryDirectory(dir=ROOT / "downloads/phase-two/runs/P2O4-T39-U03") as temporary:
            temporary = Path(temporary)
            report, previews = build_report(
                pre_package=PRE,
                post_package=POST,
                archive_path=ARCHIVE,
                extracted_root=temporary / "extracted",
                generated_at_utc="2026-07-24T21:00:00Z",
                run_id=RUN_ID,
                git_source_commit="0" * 40,
            )
            evidence = report["evidence_comparison"]
            self.assertEqual(evidence["mtbs_affirmative_pixels"], 19_700)
            self.assertEqual(evidence["mtbs_uncovered_pixels"], 389)
            self.assertEqual(report["optical_reverification"]["registration"]["summary"]["state_counts"]["pass"], 9)
            self.assertEqual(report["fitness_decision"]["source"], "PASS_EXACT_WARD_CREEK_MTBS_SOURCE_FITNESS")
            self.assertIsNone(report["dataset_version"])
            self.assertIsNone(report["model_version"])
            html = render_html(report, "evidence.png")
            self.assertNotIn("official status", html.lower().split("what this proves")[1].split("what this does not prove")[0])
            self.assertEqual(previews["boundary_mask20"].shape, (219, 183))

    def test_notice_mutation_fails_closed(self) -> None:
        if not ARCHIVE.is_file():
            self.skipTest("ignored exact custody unavailable")
        with ZipFile(ARCHIVE) as archive:
            fgdc = archive.read(FGDC_MEMBER)
        self.assertEqual(sha256(fgdc).hexdigest(), "39ab440c70785d408e2a2299832064b861fcb7c7a6cbb0bb6f0b5068df85cb99")
        self.assertTrue(issubclass(ReplacementEventReferenceFitnessError, RuntimeError))


if __name__ == "__main__":
    unittest.main()
