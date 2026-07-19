from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import burnlens
from burnlens.region_owner_response_intake import (
    LABEL_SET_VERSION,
    REPORT_ID,
    RegionOwnerResponseIntakeError,
    build_private_reconciliation,
    preserve_response,
    public_report,
    validate_response,
    write_private_no_overwrite,
    write_public_no_overwrite,
)


ROOT = Path(__file__).resolve().parents[1]
SURFACE_PATH = ROOT / "samples/labels/review/regions/phase-two/REGION-OWNER-REVIEW-SURFACE-2026-001.json"
TEMPLATE_PATH = ROOT / "samples/labels/review/regions/phase-two/REGION-OWNER-REVIEW-SURFACE-2026-001-RESPONSE-TEMPLATE.json"
PILOT_PATH = ROOT / "samples/labels/pilot/phase-two/REGION-CANDIDATE-PILOT-2026-001.json"


class RegionOwnerResponseIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.surface = json.loads(SURFACE_PATH.read_text(encoding="utf-8"))
        cls.template = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))

    def _response(self, decision: str = "yes") -> dict:
        response = json.loads(json.dumps(self.template))
        response["completed"] = True
        response["review_started_at_utc"] = "2026-07-19T17:29:13.738Z"
        response["review_completed_at_utc"] = "2026-07-19T17:29:35.496Z"
        response["owner"]["attestation"] = True
        for item in response["responses"]:
            item["decision"] = decision
        return response

    @staticmethod
    def _bytes(value: dict) -> bytes:
        return (json.dumps(value, indent=2) + "\n").encode("utf-8")

    def _preserved_pair(self, directory: Path, response: dict) -> tuple[Path, Path]:
        payload = self._bytes(response)
        digest = hashlib.sha256(payload).hexdigest()
        source = directory / f"REGION-OWNER-REVIEW-SURFACE-2026-001-RESPONSE-{digest[:16]}.json"
        source.write_bytes(payload)
        destination = directory / "custody"
        exact, receipt, _ = preserve_response(
            repository_root=ROOT,
            surface_path=SURFACE_PATH,
            source_response_path=source,
            destination_directory=destination,
            received_at_utc="2026-07-19T17:30:00Z",
            run_id="BL-2026-07-19-region-owner-response-lock-test",
            git_source_commit="a" * 40,
        )
        return exact, receipt

    def test_version_and_entry_points(self) -> None:
        self.assertEqual(burnlens.__version__, "0.31.0")
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn("burnlens-intake-region-owner-response =", pyproject)
        self.assertIn("burnlens-build-region-owner-response-intake =", pyproject)
        self.assertEqual(LABEL_SET_VERSION, "owner-approved-prototype-region-labels-v0.1.0")

    def test_exact_completed_response_contract(self) -> None:
        result = validate_response(self.surface, self._response())
        self.assertEqual(result["decision_counts"], {"yes": 6, "no": 0, "uncertain": 0})
        self.assertEqual(len(result["candidate_bindings"]), 6)

    def test_partial_reordered_duplicate_and_altered_input_fail(self) -> None:
        for mutate, pattern in (
            (lambda value: value.update(completed=False), "incomplete"),
            (lambda value: value["responses"].reverse(), "order or identity"),
            (lambda value: value["responses"].__setitem__(1, dict(value["responses"][0])), "duplicate|order or identity"),
            (lambda value: value.update(unexpected_path="C:/private"), "fields changed"),
        ):
            response = self._response()
            mutate(response)
            with self.assertRaisesRegex(RegionOwnerResponseIntakeError, pattern):
                validate_response(self.surface, response)

    def test_no_and_uncertain_remain_excluded(self) -> None:
        for decision in ("no", "uncertain"):
            with tempfile.TemporaryDirectory(dir=ROOT / "downloads") as temporary:
                root = Path(temporary)
                exact, receipt = self._preserved_pair(root, self._response(decision))
                private = build_private_reconciliation(
                    repository_root=ROOT,
                    pilot_path=PILOT_PATH,
                    surface_path=SURFACE_PATH,
                    response_path=exact,
                    receipt_path=receipt,
                    generated_at_utc="2026-07-19T17:31:00Z",
                    run_id=f"BL-2026-07-19-region-intake-{decision}-test",
                    git_source_commit="b" * 40,
                )
                self.assertEqual(private["outcome"]["owner_approved_region_labels"], 0)
                self.assertIsNone(private["label_set_version"])

    def test_all_yes_passes_raster_uncertainty_and_leakage_gates(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "downloads") as temporary:
            root = Path(temporary)
            exact, receipt = self._preserved_pair(root, self._response())
            private = build_private_reconciliation(
                repository_root=ROOT,
                pilot_path=PILOT_PATH,
                surface_path=SURFACE_PATH,
                response_path=exact,
                receipt_path=receipt,
                generated_at_utc="2026-07-19T17:31:00Z",
                run_id="BL-2026-07-19-region-intake-all-yes-test",
                git_source_commit="c" * 40,
            )
            self.assertEqual(private["outcome"]["owner_approved_region_labels"], 6)
            self.assertEqual(private["outcome"]["prototype_label_class_counts"], {"background": 3, "burned": 3})
            self.assertEqual(private["outcome"]["accepted_core_pixels"], 136)
            self.assertEqual(private["outcome"]["excluded_unknown_ring_pixels"], 246)
            self.assertFalse(private["outcome"]["dataset_fitness_reopened"])
            self.assertTrue(all(all(unit["gates"].values()) for unit in private["units"]))

    def test_private_and_public_writers_preserve_privacy(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "downloads") as temporary:
            root = Path(temporary)
            exact, receipt = self._preserved_pair(root, self._response())
            private = build_private_reconciliation(
                repository_root=ROOT,
                pilot_path=PILOT_PATH,
                surface_path=SURFACE_PATH,
                response_path=exact,
                receipt_path=receipt,
                generated_at_utc="2026-07-19T17:31:00Z",
                run_id="BL-2026-07-19-region-intake-writer-test",
                git_source_commit="d" * 40,
            )
            private_path = root / "private.json"
            binding = write_private_no_overwrite(ROOT, private_path, private)
            report = public_report(private, binding)
            public_directory = root / "public"
            outputs = write_public_no_overwrite(report, public_directory)
            self.assertEqual(len(outputs), 3)
            serialized = (public_directory / f"{REPORT_ID}.json").read_text(encoding="utf-8").lower()
            for forbidden in ("candidate_id", "owner_decision", "note_present", "note_sha256", "c:\\users", "downloads"):
                self.assertNotIn(forbidden, serialized)
            with self.assertRaisesRegex(RegionOwnerResponseIntakeError, "refusing to overwrite"):
                write_private_no_overwrite(ROOT, private_path, private)


if __name__ == "__main__":
    unittest.main()
