from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from burnlens.owner_review_batch import (
    MANIFEST_SCHEMA_VERSION,
    OwnerReviewBatchError,
    build_surface,
    response_template,
    validate_completed_response,
)
from burnlens.owner_review_batch_lock import (
    MAX_RESPONSE_BYTES,
    OwnerReviewBatchLockError,
    _assert_ignored,
    _json,
    classify_completed_exports_without_reveal,
    classify_completed_response_ambiguity,
    preserve_response_without_reveal,
    require_unambiguous_completed_response,
    validate_completed_envelope_without_reveal,
)


ROOT = Path(__file__).resolve().parents[1]
SURFACE_ID = "OWNER-REVIEW-BATCH-TEST-001"


def _ignored_temporary_directory():
    downloads = ROOT / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    return TemporaryDirectory(dir=downloads)


class OwnerReviewBatchLockTests(unittest.TestCase):
    @staticmethod
    def _manifest() -> dict:
        return {
            "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
            "surface_id": SURFACE_ID,
            "surface_revision": 1,
            "surface_run_id": "BL-TEST-OWNER-REVIEW-BATCH-SURFACE-R001",
            "milestone_id": "P2O4-T33",
            "task_issue": 521,
            "generated_at_utc": "2026-07-21T13:59:00Z",
            "git_source_commit": "a" * 40,
            "title": "Synthetic Petes Lake owner-review pair",
            "review_groups": [
                {
                    "event_group_id": "event-petes-lake-2020",
                    "event_label": "Petes Lake 2020",
                    "context": "Synthetic event context for the generic custody contract only.",
                    "candidate_ids": ["PLP-001", "PLP-002"],
                }
            ],
            "candidates": [
                {
                    "candidate_id": "PLP-001",
                    "event_group_id": "event-petes-lake-2020",
                    "proposed_class": "burned",
                    "question": "Is this exact region a usable prototype burned candidate?",
                    "proposition_basis": "Synthetic deterministic fixture basis for custody testing only.",
                    "limitations": ["Synthetic fixture; not owner evidence or a label."],
                    "facts": [{"label": "Core", "value": "25 native-grid pixels"}],
                    "proposal_binding": {
                        "record_id": "PETES-PROPOSAL-001",
                        "bytes": 101,
                        "sha256": sha256(b"proposal-1").hexdigest(),
                    },
                    "candidate_raster_binding": {
                        "path": "candidate-001.tif",
                        "bytes": 201,
                        "sha256": sha256(b"raster-1").hexdigest(),
                    },
                    "evidence_images": [
                        {
                            "path": "evidence-001.png",
                            "bytes": 301,
                            "sha256": sha256(b"evidence-1").hexdigest(),
                            "alt": "Synthetic burned-candidate evidence.",
                        }
                    ],
                },
                {
                    "candidate_id": "PLP-002",
                    "event_group_id": "event-petes-lake-2020",
                    "proposed_class": "background",
                    "question": "Is this exact region a usable prototype background candidate?",
                    "proposition_basis": "Synthetic deterministic fixture basis for custody testing only.",
                    "limitations": ["Synthetic fixture; not owner evidence or a label."],
                    "facts": [{"label": "Core", "value": "25 native-grid pixels"}],
                    "proposal_binding": {
                        "record_id": "PETES-PROPOSAL-002",
                        "bytes": 102,
                        "sha256": sha256(b"proposal-2").hexdigest(),
                    },
                    "candidate_raster_binding": {
                        "path": "candidate-002.tif",
                        "bytes": 202,
                        "sha256": sha256(b"raster-2").hexdigest(),
                    },
                    "evidence_images": [
                        {
                            "path": "evidence-002.png",
                            "bytes": 302,
                            "sha256": sha256(b"evidence-2").hexdigest(),
                            "alt": "Synthetic background-candidate evidence.",
                        }
                    ],
                },
            ],
            "batch_size_exception": "single-event-pair",
            "supersedes_surface_id": None,
        }

    @classmethod
    def _surface(cls) -> dict:
        return build_surface(cls._manifest())

    @classmethod
    def _response(cls, decisions: tuple[object, object] = ("yes", "uncertain")) -> dict:
        surface = cls._surface()
        value = response_template(surface)
        value.update(
            completed=True,
            review_started_at_utc="2026-07-21T14:00:00Z",
            review_completed_at_utc="2026-07-21T14:02:00Z",
        )
        value["owner"]["attestation"] = True
        for item, decision in zip(value["responses"], decisions, strict=True):
            item["decision"] = decision
        return value

    @staticmethod
    def _bytes(value: dict) -> bytes:
        return (json.dumps(value, indent=2) + "\n").encode("utf-8")

    def _paths(self, root: Path, response: dict | None = None) -> tuple[Path, Path]:
        root.mkdir(parents=True, exist_ok=True)
        surface_path = root / "surface.json"
        surface_path.write_bytes(self._bytes(self._surface()))
        response_bytes = self._bytes(response or self._response())
        response_hash = sha256(response_bytes).hexdigest()
        response_path = root / f"{SURFACE_ID}-RESPONSE-{response_hash[:16]}.json"
        response_path.write_bytes(response_bytes)
        return surface_path, response_path

    def _preserve(self, root: Path, response: dict | None = None):
        surface_path, response_path = self._paths(root, response)
        return preserve_response_without_reveal(
            repository_root=ROOT,
            surface_path=surface_path,
            source_response_path=response_path,
            destination_directory=root / "custody",
            received_at_utc="2026-07-21T14:03:00Z",
            run_id="BL-TEST-OWNER-REVIEW-BATCH-LOCK-R001",
            git_source_commit="d" * 40,
        )

    def test_preserves_exact_bytes_and_pre_reveal_receipt(self) -> None:
        with _ignored_temporary_directory() as temporary:
            root = Path(temporary)
            surface_path, source = self._paths(root)
            exact, receipt_path, receipt = preserve_response_without_reveal(
                repository_root=ROOT,
                surface_path=surface_path,
                source_response_path=source,
                destination_directory=root / "custody",
                received_at_utc="2026-07-21T14:03:00Z",
                run_id="BL-TEST-OWNER-REVIEW-BATCH-LOCK-R001",
                git_source_commit="d" * 40,
            )
            self.assertEqual(exact.read_bytes(), source.read_bytes())
            self.assertEqual(json.loads(receipt_path.read_bytes()), receipt)
            self.assertFalse(receipt["decisions_revealed"])
            self.assertFalse(receipt["response_binding"]["decision_values_read"])
            self.assertFalse(receipt["response_binding"]["note_values_read"])
            self.assertNotIn("decision_counts", receipt["response_binding"])
            self.assertEqual(receipt["surface_binding"]["surface_revision"], 1)
            self.assertEqual(receipt["surface_binding"]["milestone_id"], "P2O4-T33")

    def test_rejects_hash_filename_drift(self) -> None:
        with _ignored_temporary_directory() as temporary:
            root = Path(temporary)
            surface_path, source = self._paths(root)
            wrong = source.with_name(f"{SURFACE_ID}-RESPONSE-0000000000000000.json")
            source.replace(wrong)
            with self.assertRaisesRegex(OwnerReviewBatchLockError, "filename"):
                preserve_response_without_reveal(
                    repository_root=ROOT,
                    surface_path=surface_path,
                    source_response_path=wrong,
                    destination_directory=root / "custody",
                    received_at_utc="2026-07-21T14:03:00Z",
                    run_id="test",
                    git_source_commit="d" * 40,
                )

    def test_rejects_binding_and_attestation_failures(self) -> None:
        mutations = (
            (lambda value: value["owner"].update(attestation=False), "attestation"),
            (lambda value: value.update(surface_revision=2), "surface_revision"),
            (lambda value: value.update(surface_revision=True), "surface revision"),
            (lambda value: value.update(milestone_id="P2O4-X"), "milestone_id"),
            (lambda value: value.update(ordered_manifest_sha256="e" * 64), "ordered_manifest_sha256"),
            (
                lambda value: value["responses"][0].update(candidate_binding_sha256="f" * 64),
                "candidate_binding_sha256",
            ),
            (lambda value: value["responses"].reverse(), "candidate_id"),
        )
        for mutation, message in mutations:
            with self.subTest(message=message):
                response = self._response()
                mutation(response)
                with self.assertRaisesRegex(OwnerReviewBatchLockError, message):
                    validate_completed_envelope_without_reveal(self._surface(), response)

    def test_surface_must_reconstruct_from_its_embedded_manifest(self) -> None:
        candidate_drift = json.loads(json.dumps(self._surface()))
        candidate_drift["candidates"][0]["candidate_binding_sha256"] = "f" * 64
        with self.assertRaisesRegex(OwnerReviewBatchLockError, "reconstruction mismatch: candidates"):
            validate_completed_envelope_without_reveal(candidate_drift, self._response())

        manifest_drift = json.loads(json.dumps(self._surface()))
        manifest_drift["batch_manifest"]["candidates"][0]["evidence_images"][0]["sha256"] = "e" * 64
        with self.assertRaisesRegex(OwnerReviewBatchLockError, "batch manifest is invalid"):
            validate_completed_envelope_without_reveal(manifest_drift, self._response())

        contract_drift = json.loads(json.dumps(self._surface()))
        contract_drift["decision_contract"]["yes"] = "tampered meaning"
        with self.assertRaisesRegex(OwnerReviewBatchLockError, "decision_contract"):
            validate_completed_envelope_without_reveal(contract_drift, self._response())

    def test_refuses_overwrite(self) -> None:
        with _ignored_temporary_directory() as temporary:
            root = Path(temporary)
            surface_path, source = self._paths(root)
            arguments = dict(
                repository_root=ROOT,
                surface_path=surface_path,
                source_response_path=source,
                destination_directory=root / "custody",
                received_at_utc="2026-07-21T14:03:00Z",
                run_id="test",
                git_source_commit="d" * 40,
            )
            exact, receipt, _ = preserve_response_without_reveal(**arguments)
            exact_bytes = exact.read_bytes()
            receipt_bytes = receipt.read_bytes()
            with self.assertRaisesRegex(OwnerReviewBatchLockError, "overwrite"):
                preserve_response_without_reveal(**arguments)
            self.assertEqual(exact.read_bytes(), exact_bytes)
            self.assertEqual(receipt.read_bytes(), receipt_bytes)

    def test_rolls_back_response_when_receipt_write_collides(self) -> None:
        with _ignored_temporary_directory() as temporary:
            root = Path(temporary)
            surface_path, source = self._paths(root)
            response_hash = sha256(source.read_bytes()).hexdigest()
            custody = root / "custody"
            custody.mkdir()
            receipt = custody / f"{SURFACE_ID}-RECEIPT-{response_hash[:16]}.json"
            receipt.write_bytes(b"existing receipt")
            exact = custody / source.name
            with self.assertRaisesRegex(OwnerReviewBatchLockError, "overwrite"):
                preserve_response_without_reveal(
                    repository_root=ROOT,
                    surface_path=surface_path,
                    source_response_path=source,
                    destination_directory=custody,
                    received_at_utc="2026-07-21T14:03:00Z",
                    run_id="test",
                    git_source_commit="d" * 40,
                )
            self.assertFalse(exact.exists())
            self.assertEqual(receipt.read_bytes(), b"existing receipt")

    def test_malformed_decision_is_preserved_before_full_validation(self) -> None:
        valid_summary = validate_completed_response(self._surface(), self._response(("yes", "no")))
        self.assertEqual(valid_summary["answered_count"], 2)
        response = self._response(decisions=({"not": "a decision"}, "yes"))
        envelope = validate_completed_envelope_without_reveal(self._surface(), response)
        self.assertFalse(envelope["decision_values_read"])
        with _ignored_temporary_directory() as temporary:
            root = Path(temporary)
            exact, _, _ = self._preserve(root, response)
            self.assertEqual(json.loads(exact.read_bytes())["responses"][0]["decision"], {"not": "a decision"})
        with self.assertRaisesRegex(OwnerReviewBatchError, "decision"):
            validate_completed_response(self._surface(), response)

    def test_ambiguity_classifier_is_hash_based_and_fail_closed(self) -> None:
        first = "1" * 64
        second = "2" * 64
        identical = classify_completed_response_ambiguity([first, first])
        self.assertTrue(identical["identical_exports_are_idempotent"])
        self.assertFalse(identical["ambiguous"])
        self.assertFalse(identical["blocks_intake"])
        ambiguous = classify_completed_response_ambiguity([first, second, first])
        self.assertTrue(ambiguous["ambiguous"])
        self.assertTrue(ambiguous["blocks_intake"])
        self.assertEqual(ambiguous["distinct_response_count"], 2)
        with self.assertRaisesRegex(OwnerReviewBatchLockError, "AMBIGUOUS"):
            require_unambiguous_completed_response([first, second])

    def test_export_classifier_validates_envelopes_without_reveal(self) -> None:
        with _ignored_temporary_directory() as temporary:
            root = Path(temporary)
            surface_path, first = self._paths(root / "first")
            duplicate_root = root / "duplicate"
            duplicate_root.mkdir()
            duplicate = duplicate_root / first.name
            duplicate.write_bytes(first.read_bytes())
            result = classify_completed_exports_without_reveal(
                surface_path=surface_path, response_paths=[first, duplicate]
            )
            self.assertEqual(result["classification"], "IDEMPOTENT_IDENTICAL_COMPLETED_RESPONSES")
            self.assertFalse(result["decision_values_read"])

            _, distinct = self._paths(root / "distinct", self._response(("no", "yes")))
            ambiguous = classify_completed_exports_without_reveal(
                surface_path=surface_path, response_paths=[first, distinct]
            )
            self.assertEqual(ambiguous["classification"], "AMBIGUOUS_DISTINCT_COMPLETED_RESPONSES")
            self.assertTrue(ambiguous["blocks_intake"])

    def test_duplicate_json_fields_and_oversized_response_fail_before_intake(self) -> None:
        with self.assertRaisesRegex(OwnerReviewBatchLockError, "duplicate JSON field"):
            _json(b'{"completed":true,"completed":false}', "duplicate.json")
        with self.assertRaisesRegex(OwnerReviewBatchLockError, "non-standard JSON constant"):
            _json(b'{"decision":NaN}', "nonstandard.json")

        with _ignored_temporary_directory() as temporary:
            root = Path(temporary)
            surface_path = root / "surface.json"
            surface_path.write_bytes(self._bytes(self._surface()))
            oversized = root / "oversized.json"
            oversized.write_bytes(b" " * (MAX_RESPONSE_BYTES + 1))
            with self.assertRaisesRegex(OwnerReviewBatchLockError, "bounded byte contract"):
                classify_completed_exports_without_reveal(
                    surface_path=surface_path,
                    response_paths=[oversized],
                )

    def test_private_custody_guard_rejects_a_tracked_destination(self) -> None:
        tracked = subprocess.CompletedProcess(args=[], returncode=0)
        with patch("burnlens.owner_review_batch_lock.subprocess.run", return_value=tracked):
            with self.assertRaisesRegex(OwnerReviewBatchLockError, "already tracked"):
                _assert_ignored(ROOT, ROOT / "downloads" / "synthetic-private-response.json")


if __name__ == "__main__":
    unittest.main()
