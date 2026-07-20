from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import burnlens
from burnlens.green_ridge_owner_response_intake import (
    LABEL_SET_VERSION,
    PRIOR_LABEL_SET_VERSION,
    REPORT_ID,
    GreenRidgeOwnerResponseIntakeError,
    build_private_reconciliation,
    preserve_response,
    public_report,
    validate_response,
    write_private_no_overwrite,
    write_public_no_overwrite,
)


ROOT = Path(__file__).resolve().parents[1]
SURFACE = ROOT / "samples/labels/review/green-ridge/phase-two/GREEN-RIDGE-OWNER-REVIEW-SURFACE-2026-001.json"
TEMPLATE = ROOT / "samples/labels/review/green-ridge/phase-two/GREEN-RIDGE-OWNER-REVIEW-SURFACE-2026-001-RESPONSE-TEMPLATE.json"
PROPOSAL = ROOT / "samples/labels/pilot/green-ridge/phase-two/GREEN-RIDGE-REGION-PROPOSAL-2026-001.json"


class GreenRidgeOwnerResponseIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.surface = json.loads(SURFACE.read_text(encoding="utf-8"))
        cls.template = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    def _response(self, decisions: tuple[str, str] = ("yes", "yes")) -> dict:
        value = json.loads(json.dumps(self.template))
        value["completed"] = True
        value["review_started_at_utc"] = "2026-07-20T16:32:00Z"
        value["review_completed_at_utc"] = "2026-07-20T16:33:00Z"
        value["owner"]["attestation"] = True
        for item, decision in zip(value["responses"], decisions, strict=True):
            item["decision"] = decision
        return value

    @staticmethod
    def _bytes(value: dict) -> bytes:
        return (json.dumps(value, indent=2) + "\n").encode("utf-8")

    def _preserved(self, root: Path, response: dict) -> tuple[Path, Path]:
        payload = self._bytes(response)
        digest = hashlib.sha256(payload).hexdigest()
        source = root / f"GREEN-RIDGE-OWNER-REVIEW-SURFACE-2026-001-RESPONSE-{digest[:16]}.json"
        source.write_bytes(payload)
        exact, receipt, _ = preserve_response(
            repository_root=ROOT,
            surface_path=SURFACE,
            source_response_path=source,
            destination_directory=root / "custody",
            received_at_utc="2026-07-20T16:34:00Z",
            run_id="BL-TEST-GREEN-RIDGE-OWNER-RESPONSE-LOCK",
            git_source_commit="a" * 40,
        )
        return exact, receipt

    def test_version_and_entry_points(self) -> None:
        self.assertEqual(burnlens.__version__, "0.38.0")
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn("burnlens-intake-green-ridge-owner-response", pyproject)
        self.assertIn("burnlens-build-green-ridge-owner-response-intake", pyproject)

    def test_completed_response_contract(self) -> None:
        result = validate_response(self.surface, self._response(("yes", "uncertain")))
        self.assertEqual(result["decision_counts"], {"yes": 1, "no": 0, "uncertain": 1})
        self.assertEqual(len(result["candidate_bindings"]), 2)

    def test_partial_reordered_duplicate_and_altered_input_fail(self) -> None:
        for mutate, pattern in (
            (lambda value: value.update(completed=False), "incomplete"),
            (lambda value: value["responses"].reverse(), "order or identity"),
            (lambda value: value["responses"].__setitem__(1, dict(value["responses"][0])), "duplicate|order or identity"),
            (lambda value: value.update(unexpected_path="C:/private"), "fields changed"),
        ):
            response = self._response()
            mutate(response)
            with self.assertRaisesRegex(GreenRidgeOwnerResponseIntakeError, pattern):
                validate_response(self.surface, response)

    def test_preservation_rejects_overwrite_and_wrong_filename(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "downloads") as temporary:
            root = Path(temporary)
            exact, receipt = self._preserved(root, self._response())
            self.assertEqual(exact.read_bytes(), self._bytes(self._response()))
            self.assertTrue(receipt.is_file())
            payload = self._bytes(self._response())
            wrong = root / "wrong.json"
            wrong.write_bytes(payload)
            with self.assertRaisesRegex(GreenRidgeOwnerResponseIntakeError, "filename"):
                preserve_response(
                    repository_root=ROOT,
                    surface_path=SURFACE,
                    source_response_path=wrong,
                    destination_directory=root / "other",
                    received_at_utc="2026-07-20T16:34:00Z",
                    run_id="BL-TEST-WRONG",
                    git_source_commit="a" * 40,
                )
            source = root / exact.name
            source.write_bytes(exact.read_bytes())
            with self.assertRaisesRegex(GreenRidgeOwnerResponseIntakeError, "refusing to overwrite"):
                preserve_response(
                    repository_root=ROOT,
                    surface_path=SURFACE,
                    source_response_path=source,
                    destination_directory=exact.parent,
                    received_at_utc="2026-07-20T16:34:00Z",
                    run_id="BL-TEST-DUPLICATE",
                    git_source_commit="a" * 40,
                )

    def test_yes_and_exclusions_preserve_unknowns_and_cumulative_state(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "downloads") as temporary:
            root = Path(temporary)
            exact, receipt = self._preserved(root, self._response(("yes", "uncertain")))
            private = build_private_reconciliation(
                repository_root=ROOT,
                proposal_path=PROPOSAL,
                surface_path=SURFACE,
                response_path=exact,
                receipt_path=receipt,
                generated_at_utc="2026-07-20T16:35:00Z",
                run_id="BL-TEST-GREEN-RIDGE-OWNER-INTAKE",
                git_source_commit="b" * 40,
            )
            self.assertEqual(private["label_set_version"], LABEL_SET_VERSION)
            self.assertEqual(private["outcome"]["green_ridge_owner_approved_region_labels"], 1)
            self.assertEqual(private["outcome"]["green_ridge_accepted_core_pixels"], 25)
            self.assertEqual(private["outcome"]["green_ridge_excluded_unknown_ring_pixels"], 87)
            self.assertEqual(private["outcome"]["cumulative_owner_approved_region_labels"], 7)
            self.assertEqual(private["outcome"]["event_group_count"], 4)
            self.assertFalse(private["outcome"]["dataset_fitness_reopened"])

    def test_no_new_yes_retains_prior_label_set(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "downloads") as temporary:
            root = Path(temporary)
            exact, receipt = self._preserved(root, self._response(("no", "uncertain")))
            private = build_private_reconciliation(
                repository_root=ROOT,
                proposal_path=PROPOSAL,
                surface_path=SURFACE,
                response_path=exact,
                receipt_path=receipt,
                generated_at_utc="2026-07-20T16:35:00Z",
                run_id="BL-TEST-GREEN-RIDGE-NO-NEW-LABELS",
                git_source_commit="c" * 40,
            )
            self.assertEqual(private["label_set_version"], PRIOR_LABEL_SET_VERSION)
            self.assertEqual(private["outcome"]["green_ridge_owner_approved_region_labels"], 0)
            self.assertEqual(private["outcome"]["event_group_count"], 3)

    def test_private_and_public_writers_preserve_privacy(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "downloads") as temporary:
            root = Path(temporary)
            exact, receipt = self._preserved(root, self._response())
            private = build_private_reconciliation(
                repository_root=ROOT,
                proposal_path=PROPOSAL,
                surface_path=SURFACE,
                response_path=exact,
                receipt_path=receipt,
                generated_at_utc="2026-07-20T16:35:00Z",
                run_id="BL-TEST-GREEN-RIDGE-WRITERS",
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
            with self.assertRaisesRegex(GreenRidgeOwnerResponseIntakeError, "refusing to overwrite"):
                write_private_no_overwrite(ROOT, private_path, private)


if __name__ == "__main__":
    unittest.main()
