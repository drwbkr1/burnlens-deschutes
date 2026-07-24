from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

import burnlens
from burnlens.windigo_owner_response_intake import (
    EXPECTED_RECEIPT_BYTES,
    EXPECTED_RECEIPT_SHA256,
    EXPECTED_RESPONSE_BYTES,
    EXPECTED_RESPONSE_SHA256,
    LABEL_SET_VERSION,
    REPORT_ID,
    WindigoOwnerResponseIntakeError,
    build_private_reconciliation,
    public_report,
    write_private_no_overwrite,
    write_public_no_overwrite,
)


ROOT = Path(__file__).resolve().parents[1]
PRE = ROOT / "downloads/phase-two/raw/windigo-s2-optical-pre-v0.1.0"
POST = ROOT / "downloads/phase-two/raw/windigo-s2-optical-post-v0.1.0"
ARCHIVE = ROOT / (
    "downloads/phase-two/quarantine/P2O4-T35-U03/windigo-reference-r001/"
    "windigo-reference-delivery.zip"
)
EXTRACTED = ARCHIVE.parent / "extracted"
BOUNDARY = ROOT / (
    "downloads/phase-two/raw/BL-2026-07-23-windigo-entry-metadata-r001/"
    "official/windigo-mtbs-boundary.geojson"
)
SOURCE_REPORT = ROOT / "samples/cross-event/phase-two/windigo/WINDIGO-SOURCE-FITNESS-2026-006.json"
PROPOSAL = ROOT / "samples/labels/pilot/windigo/phase-two/WINDIGO-REGION-PROPOSAL-2026-001.json"
SURFACE = ROOT / (
    "samples/labels/review/windigo/phase-two/"
    "WINDIGO-OWNER-REVIEW-SURFACE-2026-001.json"
)
LOCKED = ROOT / "downloads/phase-two/review-responses/P2O4-T35-U05/locked"
RESPONSE = LOCKED / "WINDIGO-OWNER-REVIEW-SURFACE-2026-001-RESPONSE-d1f77a9cf575f668.json"
RECEIPT = LOCKED / "WINDIGO-OWNER-REVIEW-SURFACE-2026-001-RECEIPT-d1f77a9cf575f668.json"
PUBLIC_DIRECTORY = ROOT / "samples/labels/review/windigo/phase-two/intake"
PUBLIC_REPORT = PUBLIC_DIRECTORY / f"{REPORT_ID}.json"
PRIVATE_AVAILABLE = all(
    path.exists()
    for path in (PRE, POST, ARCHIVE, EXTRACTED, BOUNDARY, RESPONSE, RECEIPT)
)
BOUND_RECORD_PATHS = (
    "records/phase-two/sources/SOURCE-2026-036.md",
    "records/phase-two/sources/SOURCE-2026-037.md",
    "records/phase-two/terms/TERMS-2026-031.md",
    "records/phase-two/terms/TERMS-2026-032.md",
    "records/phase-two/prechecks/PRECHECK-2026-059.md",
    "records/phase-two/prechecks/PRECHECK-2026-060.md",
    "records/phase-two/prechecks/PRECHECK-2026-061.md",
    "records/phase-two/prechecks/PRECHECK-2026-062.md",
    "records/phase-two/prechecks/PRECHECK-2026-063.md",
)


def _ignored_temporary_directory():
    downloads = ROOT / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    return TemporaryDirectory(dir=downloads)


class WindigoOwnerResponseCheckoutContractTests(unittest.TestCase):
    def test_every_exact_record_binding_has_an_explicit_lf_checkout_contract(self) -> None:
        for path in BOUND_RECORD_PATHS:
            completed = subprocess.run(
                ["git", "check-attr", "text", "eol", "--", path],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn(f"{path}: text: set", completed.stdout)
            self.assertIn(f"{path}: eol: lf", completed.stdout)

    def test_public_intake_outputs_have_explicit_checkout_contracts(self) -> None:
        public_directory = PUBLIC_DIRECTORY.relative_to(ROOT).as_posix()
        expected = {
            f"{public_directory}/{REPORT_ID}.json": ("set", "lf"),
            f"{public_directory}/{REPORT_ID}.html": ("set", "lf"),
            f"{public_directory}/{REPORT_ID}.png": ("unset", "unspecified"),
        }
        for path, (text_value, eol_value) in expected.items():
            completed = subprocess.run(
                ["git", "check-attr", "text", "eol", "--", path],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn(f"{path}: text: {text_value}", completed.stdout)
            self.assertIn(f"{path}: eol: {eol_value}", completed.stdout)


@unittest.skipUnless(PRIVATE_AVAILABLE, "exact ignored Windigo custody is unavailable")
class WindigoOwnerResponseIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.private = build_private_reconciliation(
            repository_root=ROOT,
            pre_package=PRE,
            post_package=POST,
            archive_path=ARCHIVE,
            extracted_root=EXTRACTED,
            boundary_path=BOUNDARY,
            source_report_path=SOURCE_REPORT,
            proposal_path=PROPOSAL,
            surface_path=SURFACE,
            response_path=RESPONSE,
            receipt_path=RECEIPT,
            generated_at_utc="2026-07-24T00:15:00Z",
            run_id="BL-TEST-WINDIGO-OWNER-RESPONSE-INTAKE",
            git_source_commit="a" * 40,
        )

    def test_version_entry_point_and_exact_custody_constants(self) -> None:
        self.assertEqual(burnlens.__version__, "0.49.0")
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn("burnlens-build-windigo-owner-response-intake", pyproject)
        self.assertEqual(EXPECTED_RESPONSE_BYTES, RESPONSE.stat().st_size)
        self.assertEqual(EXPECTED_RESPONSE_SHA256, hashlib.sha256(RESPONSE.read_bytes()).hexdigest())
        self.assertEqual(EXPECTED_RECEIPT_BYTES, RECEIPT.stat().st_size)
        self.assertEqual(EXPECTED_RECEIPT_SHA256, hashlib.sha256(RECEIPT.read_bytes()).hexdigest())

    def test_two_yes_and_all_non_owner_gates_accept_only_prototype_event(self) -> None:
        private = self.private
        self.assertEqual(private["decision_counts"], {"yes": 2, "no": 0, "uncertain": 0})
        self.assertEqual(private["label_set_version"], LABEL_SET_VERSION)
        self.assertTrue(private["outcome"]["windigo_event_complete"])
        self.assertTrue(private["outcome"]["no_partial_event_promotion"])
        self.assertEqual(private["outcome"]["windigo_owner_approved_region_labels"], 2)
        self.assertEqual(private["outcome"]["windigo_class_counts"], {"background": 1, "burned": 1})
        self.assertEqual(private["outcome"]["windigo_accepted_core_pixels"], 50)
        self.assertEqual(private["outcome"]["windigo_excluded_unknown_ring_pixels"], 102)
        self.assertEqual(private["outcome"]["cumulative_owner_approved_region_labels"], 12)
        self.assertEqual(
            private["outcome"]["cumulative_prototype_label_class_counts"],
            {"background": 6, "burned": 6},
        )
        self.assertEqual(private["outcome"]["cumulative_accepted_core_pixels"], 286)
        self.assertEqual(private["outcome"]["cumulative_accepted_core_area_ha"], 11.44)
        self.assertEqual(private["outcome"]["cumulative_excluded_unknown_ring_pixels"], 533)
        self.assertEqual(private["outcome"]["event_group_count"], 6)
        self.assertTrue(private["outcome"]["minimum_event_group_gate_passed"])
        self.assertFalse(private["outcome"]["separate_sufficiency_evaluator_passed"])
        self.assertFalse(private["outcome"]["dataset_fitness_reopened"])
        self.assertTrue(all(private["promotion_gates"].values()))
        for name in ("dataset_version", "split_version", "baseline_version", "model_version"):
            self.assertIsNone(private[name])

    def test_every_candidate_reconstructs_from_exact_source_pixels(self) -> None:
        units = self.private["private_units"]
        self.assertEqual([unit["candidate_id"] for unit in units], ["WDP-001", "WDP-002"])
        self.assertEqual([unit["proposed_class"] for unit in units], ["burned", "background"])
        for unit in units:
            self.assertTrue(unit["candidate_gate_passed"])
            self.assertTrue(all(unit["gates"].values()))
            self.assertEqual(unit["core_pixels"], 25)
            self.assertEqual(unit["unknown_ring_pixels"], 51)
            self.assertEqual(unit["disposition"], "OWNER_APPROVED_PROTOTYPE_REGION_LABEL")

    def test_public_report_is_aggregate_only_and_no_overwrite(self) -> None:
        with _ignored_temporary_directory() as temporary:
            root = Path(temporary)
            private_path = root / "private.json"
            binding = write_private_no_overwrite(ROOT, private_path, self.private)
            report = public_report(self.private, binding)
            public_directory = root / "public"
            outputs = write_public_no_overwrite(report, public_directory)
            self.assertEqual(len(outputs), 3)
            serialized = (public_directory / f"{REPORT_ID}.json").read_text(encoding="utf-8").lower()
            for forbidden in (
                "candidate_id",
                "owner_decision",
                "note_present",
                "note_sha256",
                "c:\\users",
                "downloads",
            ):
                self.assertNotIn(forbidden, serialized)
            html = (public_directory / f"{REPORT_ID}.html").read_text(encoding="utf-8")
            self.assertIn("Six complete event groups meet only the frozen count minimum", html)
            self.assertIn("Notes and unit decisions remain private", html)
            self.assertNotIn("Ã", html)
            with self.assertRaisesRegex(WindigoOwnerResponseIntakeError, "refusing to overwrite"):
                write_private_no_overwrite(ROOT, private_path, self.private)

    def test_exact_private_paths_are_ignored(self) -> None:
        for path in (PRE, POST, ARCHIVE, EXTRACTED, BOUNDARY, RESPONSE, RECEIPT):
            result = subprocess.run(
                ["git", "check-ignore", "--quiet", "--no-index", "--", str(path.relative_to(ROOT))],
                cwd=ROOT,
                check=False,
            )
            self.assertEqual(result.returncode, 0, str(path))

    @unittest.skipUnless(PUBLIC_REPORT.is_file(), "tracked Windigo intake is unavailable")
    def test_public_candidate_is_aggregate_only_and_self_bound(self) -> None:
        report_bytes = PUBLIC_REPORT.read_bytes()
        report = json.loads(report_bytes)
        self.assertEqual(report["software_version"], "0.47.0")
        self.assertEqual(report["label_set_version"], LABEL_SET_VERSION)
        self.assertEqual(report["decision_counts"], {"yes": 2, "no": 0, "uncertain": 0})
        self.assertEqual(report["outcome"]["cumulative_owner_approved_region_labels"], 12)
        self.assertEqual(report["outcome"]["event_group_count"], 6)
        self.assertFalse(report["outcome"]["dataset_fitness_reopened"])
        for output in report["outputs"]:
            path = PUBLIC_DIRECTORY / output["path"]
            self.assertEqual(path.stat().st_size, output["bytes"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), output["sha256"])
        serialized = report_bytes.decode("utf-8").lower()
        for forbidden in (
            "candidate_id",
            "owner_decision",
            "note_present",
            "note_sha256",
            "c:\\users",
            "downloads",
        ):
            self.assertNotIn(forbidden, serialized)


if __name__ == "__main__":
    unittest.main()
