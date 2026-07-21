from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import burnlens
import burnlens.grandview_owner_response_intake as intake_module
from burnlens.grandview_owner_response_intake import (
    LABEL_SET_VERSION,
    PRIOR_LABEL_SET_VERSION,
    REPORT_ID,
    GrandviewOwnerResponseIntakeError,
    build_private_reconciliation,
    preserve_response,
    public_report,
    validate_response,
    write_private_no_overwrite,
    write_public_no_overwrite,
)


ROOT = Path(__file__).resolve().parents[1]
SURFACE = ROOT / "samples/labels/review/grandview/phase-two/GRANDVIEW-OWNER-REVIEW-SURFACE-2026-001.json"
TEMPLATE = ROOT / "samples/labels/review/grandview/phase-two/GRANDVIEW-OWNER-REVIEW-SURFACE-2026-001-RESPONSE-TEMPLATE.json"
PROPOSAL = ROOT / "samples/labels/pilot/grandview/phase-two/GRANDVIEW-REGION-PROPOSAL-2026-001.json"
PUBLIC_DIRECTORY = ROOT / "samples/labels/review/grandview/phase-two/intake"
PUBLIC_REPORT = PUBLIC_DIRECTORY / "GRANDVIEW-OWNER-RESPONSE-INTAKE-2026-001.json"


def _ignored_temporary_directory():
    downloads = ROOT / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    return TemporaryDirectory(dir=downloads)


def _tracked(path: Path) -> bool:
    return path.exists() and subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", str(path.relative_to(ROOT))],
        cwd=ROOT,
        check=False,
        capture_output=True,
    ).returncode == 0


class GrandviewOwnerResponseIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.surface = json.loads(SURFACE.read_text(encoding="utf-8"))
        cls.template = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    def _response(self, decisions: tuple[str, str] = ("yes", "yes")) -> dict:
        value = json.loads(json.dumps(self.template))
        value["completed"] = True
        value["review_started_at_utc"] = "2026-07-21T02:09:03.998Z"
        value["review_completed_at_utc"] = "2026-07-21T02:09:35.534Z"
        value["owner"]["attestation"] = True
        for item, decision in zip(value["responses"], decisions, strict=True):
            item["decision"] = decision
        return value

    @staticmethod
    def _bytes(value: dict) -> bytes:
        return (json.dumps(value, indent=2) + "\n").encode("utf-8")

    def _preserved(self, root: Path, response: dict) -> tuple[Path, Path]:
        root.mkdir(parents=True, exist_ok=True)
        payload = self._bytes(response)
        digest = hashlib.sha256(payload).hexdigest()
        source = root / f"GRANDVIEW-OWNER-REVIEW-SURFACE-2026-001-RESPONSE-{digest[:16]}.json"
        source.write_bytes(payload)
        exact, receipt, _ = preserve_response(
            repository_root=ROOT,
            surface_path=SURFACE,
            source_response_path=source,
            destination_directory=root / "custody",
            received_at_utc="2026-07-21T02:10:00Z",
            run_id="BL-TEST-GRANDVIEW-OWNER-RESPONSE-LOCK",
            git_source_commit="a" * 40,
        )
        return exact, receipt

    def _reconcile(self, root: Path, decisions: tuple[str, str] = ("yes", "yes"), proposal: Path = PROPOSAL) -> dict:
        exact, receipt = self._preserved(root, self._response(decisions))
        with patch.multiple(
            intake_module,
            EXPECTED_RESPONSE_BYTES=exact.stat().st_size,
            EXPECTED_RESPONSE_SHA256=hashlib.sha256(exact.read_bytes()).hexdigest(),
            EXPECTED_RECEIPT_BYTES=receipt.stat().st_size,
            EXPECTED_RECEIPT_SHA256=hashlib.sha256(receipt.read_bytes()).hexdigest(),
        ):
            return build_private_reconciliation(
                repository_root=ROOT,
                proposal_path=proposal,
                surface_path=SURFACE,
                response_path=exact,
                receipt_path=receipt,
                generated_at_utc="2026-07-21T02:11:00Z",
                run_id="BL-TEST-GRANDVIEW-OWNER-INTAKE",
                git_source_commit="b" * 40,
            )

    def test_version_and_entry_point(self) -> None:
        self.assertEqual(burnlens.__version__, "0.44.0")
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn("burnlens-build-grandview-owner-response-intake", pyproject)
        for extension in ("json", "html"):
            result = subprocess.run(
                ["git", "check-attr", "eol", "--", f"samples/labels/review/grandview/phase-two/intake/example.{extension}"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn(": eol: lf", result.stdout)

    def test_completed_response_contract(self) -> None:
        result = validate_response(self.surface, self._response(("yes", "uncertain")))
        self.assertEqual(result["decision_counts"], {"yes": 1, "no": 0, "uncertain": 1})
        self.assertEqual(len(result["candidate_bindings"]), 2)

    def test_production_custody_constants_are_exact(self) -> None:
        self.assertEqual(intake_module.EXPECTED_RESPONSE_BYTES, 887)
        self.assertEqual(
            intake_module.EXPECTED_RESPONSE_SHA256,
            "41fe9b3fa731a57d65def5d6952ef029a982ed26bcf62b9bf9cfa5d267018585",
        )
        self.assertEqual(intake_module.EXPECTED_RECEIPT_BYTES, 1_835)
        self.assertEqual(
            intake_module.EXPECTED_RECEIPT_SHA256,
            "0b2fa3360c5c54f39a5b2623ee0cf8acd0ab13ca76b2ef2ecd704c2a699dfa6a",
        )

    def test_partial_reordered_duplicate_and_altered_input_fail(self) -> None:
        for mutate, pattern in (
            (lambda value: value.update(completed=False), "incomplete"),
            (lambda value: value["responses"].reverse(), "order or identity"),
            (lambda value: value["responses"].__setitem__(1, dict(value["responses"][0])), "duplicate|order or identity"),
            (lambda value: value.update(unexpected_path="C:/private"), "fields changed"),
            (lambda value: value["responses"][0].update(decision="maybe"), "outside yes/no/uncertain"),
            (lambda value: value["responses"][0].update(notes="x" * 1001), "bounded string"),
            (
                lambda value: value.update(
                    review_started_at_utc="2026-07-21T02:10:00Z",
                    review_completed_at_utc="2026-07-21T02:09:00Z",
                ),
                "predates start",
            ),
        ):
            response = self._response()
            mutate(response)
            with self.assertRaisesRegex(GrandviewOwnerResponseIntakeError, pattern):
                validate_response(self.surface, response)

    def test_two_yes_advance_only_prototype_labels(self) -> None:
        with _ignored_temporary_directory() as temporary:
            private = self._reconcile(Path(temporary))
        self.assertEqual(private["label_set_version"], LABEL_SET_VERSION)
        self.assertEqual(private["decision_counts"], {"yes": 2, "no": 0, "uncertain": 0})
        self.assertEqual(private["outcome"]["grandview_owner_approved_region_labels"], 2)
        self.assertEqual(private["outcome"]["grandview_class_counts"], {"background": 1, "burned": 1})
        self.assertEqual(private["outcome"]["grandview_accepted_core_pixels"], 50)
        self.assertEqual(private["outcome"]["grandview_excluded_unknown_ring_pixels"], 98)
        self.assertTrue(private["outcome"]["grandview_event_complete"])
        self.assertEqual(private["outcome"]["cumulative_owner_approved_region_labels"], 10)
        self.assertEqual(private["outcome"]["cumulative_prototype_label_class_counts"], {"background": 5, "burned": 5})
        self.assertEqual(private["outcome"]["cumulative_accepted_core_pixels"], 236)
        self.assertEqual(private["outcome"]["cumulative_accepted_core_area_ha"], 9.44)
        self.assertEqual(private["outcome"]["cumulative_excluded_unknown_ring_pixels"], 431)
        self.assertEqual(private["outcome"]["event_group_count"], 5)
        self.assertFalse(private["outcome"]["minimum_event_group_gate_passed"])
        self.assertFalse(private["outcome"]["dataset_fitness_reopened"])
        for name in ("dataset_version", "split_version", "baseline_version", "model_version"):
            self.assertIsNone(private[name])

    def test_no_or_uncertain_retains_prior_label_set(self) -> None:
        with _ignored_temporary_directory() as temporary:
            private = self._reconcile(Path(temporary), ("no", "uncertain"))
        self.assertEqual(private["label_set_version"], PRIOR_LABEL_SET_VERSION)
        self.assertEqual(private["outcome"]["grandview_owner_approved_region_labels"], 0)
        self.assertEqual(private["outcome"]["grandview_excluded_unknown_ring_pixels"], 0)
        self.assertEqual(private["outcome"]["grandview_reviewed_unknown_ring_pixels"], 98)
        self.assertFalse(private["outcome"]["grandview_event_complete"])
        self.assertEqual(private["outcome"]["cumulative_owner_approved_region_labels"], 8)
        self.assertEqual(private["outcome"]["cumulative_excluded_unknown_ring_pixels"], 333)
        self.assertEqual(private["outcome"]["event_group_count"], 4)
        self.assertFalse(private["outcome"]["dataset_fitness_reopened"])

    def test_one_yes_does_not_complete_the_event(self) -> None:
        with _ignored_temporary_directory() as temporary:
            private = self._reconcile(Path(temporary), ("yes", "uncertain"))
        self.assertEqual(private["outcome"]["grandview_owner_approved_region_labels"], 1)
        self.assertFalse(private["outcome"]["grandview_event_complete"])
        self.assertEqual(private["outcome"]["event_group_count"], 4)
        self.assertEqual(private["outcome"]["cumulative_accepted_core_pixels"], 211)
        self.assertEqual(private["outcome"]["cumulative_excluded_unknown_ring_pixels"], 379)

    def test_raster_tamper_fails_closed(self) -> None:
        with _ignored_temporary_directory() as temporary:
            root = Path(temporary)
            proposal = root / PROPOSAL.name
            shutil.copyfile(PROPOSAL, proposal)
            for candidate in self.surface["candidates"]:
                source = PROPOSAL.parent / candidate["candidate_raster"]
                shutil.copyfile(source, root / source.name)
            raster = root / self.surface["candidates"][0]["candidate_raster"]
            tampered = bytearray(raster.read_bytes())
            tampered[-1] ^= 1
            raster.write_bytes(tampered)
            with self.assertRaisesRegex(GrandviewOwnerResponseIntakeError, "raster hash changed"):
                self._reconcile(root / "response", proposal=proposal)

    def test_receipt_pre_reveal_invariants_fail_closed(self) -> None:
        for field, value, pattern in (
            ("decisions_revealed", True, "pre-reveal"),
            ("qualifying_owner_response", True, "pre-qualifies"),
            ("origin_declared_by_operator", False, "origin declaration"),
            ("owner_yes_is_sufficient_without_other_gates", True, "promotion gates"),
        ):
            with self.subTest(field=field), _ignored_temporary_directory() as temporary:
                root = Path(temporary)
                exact, receipt = self._preserved(root, self._response())
                value_json = json.loads(receipt.read_text(encoding="utf-8"))
                value_json[field] = value
                receipt.write_text(json.dumps(value_json, indent=2) + "\n", encoding="utf-8", newline="\n")
                with (
                    patch.multiple(
                        intake_module,
                        EXPECTED_RESPONSE_BYTES=exact.stat().st_size,
                        EXPECTED_RESPONSE_SHA256=hashlib.sha256(exact.read_bytes()).hexdigest(),
                        EXPECTED_RECEIPT_BYTES=receipt.stat().st_size,
                        EXPECTED_RECEIPT_SHA256=hashlib.sha256(receipt.read_bytes()).hexdigest(),
                    ),
                    self.assertRaisesRegex(GrandviewOwnerResponseIntakeError, pattern),
                ):
                    build_private_reconciliation(
                        repository_root=ROOT,
                        proposal_path=PROPOSAL,
                        surface_path=SURFACE,
                        response_path=exact,
                        receipt_path=receipt,
                        generated_at_utc="2026-07-21T02:11:00Z",
                        run_id="BL-TEST-GRANDVIEW-RECEIPT-TAMPER",
                        git_source_commit="b" * 40,
                    )

    def test_private_and_public_writers_preserve_privacy(self) -> None:
        with _ignored_temporary_directory() as temporary:
            root = Path(temporary)
            private = self._reconcile(root / "response")
            private_path = root / "private.json"
            binding = write_private_no_overwrite(ROOT, private_path, private)
            report = public_report(private, binding)
            public_directory = root / "public"
            outputs = write_public_no_overwrite(report, public_directory)
            self.assertEqual(len(outputs), 3)
            serialized = (public_directory / f"{REPORT_ID}.json").read_text(encoding="utf-8").lower()
            for forbidden in ("candidate_id", "owner_decision", "note_present", "note_sha256", "c:\\users", "downloads"):
                self.assertNotIn(forbidden, serialized)
            html = (public_directory / f"{REPORT_ID}.html").read_text(encoding="utf-8")
            self.assertIn("&middot;", html)
            self.assertIn("Sources, roles, and attribution", html)
            self.assertIn("Burned Area Emergency Response", html)
            self.assertIn("USDA Forest Service and ESA", html)
            self.assertIn("count is necessary, not sufficient", html)
            self.assertNotIn("Ã", html)
            self.assertNotIn("Â", html)
            self.assertNotIn("�", html)
            with self.assertRaisesRegex(GrandviewOwnerResponseIntakeError, "refusing to overwrite"):
                write_private_no_overwrite(ROOT, private_path, private)

    @unittest.skipUnless(_tracked(PUBLIC_REPORT), "tracked Grandview owner intake not published yet")
    def test_tracked_public_report_is_aggregate_only_evidence(self) -> None:
        report_bytes = PUBLIC_REPORT.read_bytes()
        report = json.loads(report_bytes)
        self.assertEqual(report["input_bindings"]["response"], {
            "bytes": 887,
            "sha256": "41fe9b3fa731a57d65def5d6952ef029a982ed26bcf62b9bf9cfa5d267018585",
        })
        self.assertEqual(report["decision_counts"], {"yes": 2, "no": 0, "uncertain": 0})
        self.assertEqual(report["outcome"]["cumulative_owner_approved_region_labels"], 10)
        self.assertEqual(report["outcome"]["cumulative_prototype_label_class_counts"], {"background": 5, "burned": 5})
        self.assertEqual(report["outcome"]["cumulative_accepted_core_pixels"], 236)
        self.assertEqual(report["outcome"]["cumulative_excluded_unknown_ring_pixels"], 431)
        self.assertEqual(report["outcome"]["event_group_count"], 5)
        self.assertFalse(report["outcome"]["minimum_event_group_gate_passed"])
        self.assertFalse(report["outcome"]["dataset_fitness_reopened"])
        self.assertIsNone(report["dataset_version"])
        self.assertIsNone(report["split_version"])
        self.assertIsNone(report["baseline_version"])
        self.assertIsNone(report["model_version"])
        for output in report["outputs"]:
            output_path = PUBLIC_DIRECTORY / output["path"]
            output_bytes = output_path.read_bytes()
            self.assertEqual(len(output_bytes), output["bytes"])
            self.assertEqual(hashlib.sha256(output_bytes).hexdigest(), output["sha256"])
        serialized = report_bytes.decode("utf-8").lower()
        for forbidden in ("candidate_id", "owner_decision", "note_present", "note_sha256", "c:\\users", "downloads"):
            self.assertNotIn(forbidden, serialized)


if __name__ == "__main__":
    unittest.main()
