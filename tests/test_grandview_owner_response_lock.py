from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from burnlens.grandview_owner_response_lock import (
    GrandviewOwnerResponseLockError,
    preserve_response_without_reveal,
)


ROOT = Path(__file__).resolve().parents[1]
SURFACE = ROOT / "samples/labels/review/grandview/phase-two/GRANDVIEW-OWNER-REVIEW-SURFACE-2026-001.json"


def _ignored_temporary_directory():
    downloads = ROOT / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    return TemporaryDirectory(dir=downloads)


class GrandviewOwnerResponseLockTests(unittest.TestCase):
    def _response(self) -> dict:
        return {
            "response_schema_version": "burnlens-grandview-owner-review-response-v0.1.0",
            "surface_id": "GRANDVIEW-OWNER-REVIEW-SURFACE-2026-001",
            "surface_run_id": "BL-2026-07-21-grandview-owner-review-surface-r001",
            "proposal_report_sha256": "ee1259142c9069c4057366f21320c4e61cc6c9cd412038955938370397c3aaba",
            "completed": True,
            "review_started_at_utc": "2026-07-21T02:00:00Z",
            "review_completed_at_utc": "2026-07-21T02:01:00Z",
            "owner": {"attestation": True},
            "responses": [
                {
                    "candidate_id": "GVP-001",
                    "candidate_raster_sha256": "453adb2edafaf72569a60d98f93d923fe02352c9b0454930c8902b9b2b828933",
                    "decision": "yes",
                    "notes": "",
                },
                {
                    "candidate_id": "GVP-002",
                    "candidate_raster_sha256": "2f83c1822da6a8e9aadbfcad097cc1b5ed1ea118277ea0e99784e7c97dc26e91",
                    "decision": "uncertain",
                    "notes": "bounded fixture",
                },
            ],
        }

    def _source(self, root: Path, response: dict | None = None) -> Path:
        payload = (json.dumps(response or self._response(), indent=2) + "\n").encode()
        digest = sha256(payload).hexdigest()
        path = root / f"GRANDVIEW-OWNER-REVIEW-SURFACE-2026-001-RESPONSE-{digest[:16]}.json"
        path.write_bytes(payload)
        return path

    def test_preserves_exact_bytes_and_pre_reveal_receipt(self) -> None:
        with _ignored_temporary_directory() as temporary:
            root = Path(temporary)
            source = self._source(root)
            exact, receipt_path, receipt = preserve_response_without_reveal(
                repository_root=ROOT,
                surface_path=SURFACE,
                source_response_path=source,
                destination_directory=root / "custody",
                received_at_utc="2026-07-21T02:02:00Z",
                run_id="BL-2026-07-21-grandview-owner-response-intake-test-r001",
                git_source_commit="a" * 40,
            )
            self.assertEqual(exact.read_bytes(), source.read_bytes())
            self.assertTrue(receipt_path.is_file())
            self.assertFalse(receipt["decisions_revealed"])
            self.assertFalse(receipt["response_binding"]["decision_values_read"])
            self.assertIsNone(receipt["qualifying_owner_response"])
            self.assertNotIn("decision_counts", receipt["response_binding"])

    def test_rejects_hash_filename_drift(self) -> None:
        with _ignored_temporary_directory() as temporary:
            root = Path(temporary)
            source = self._source(root)
            wrong = source.with_name("GRANDVIEW-OWNER-REVIEW-SURFACE-2026-001-RESPONSE-0000000000000000.json")
            source.replace(wrong)
            with self.assertRaisesRegex(GrandviewOwnerResponseLockError, "filename"):
                preserve_response_without_reveal(
                    repository_root=ROOT,
                    surface_path=SURFACE,
                    source_response_path=wrong,
                    destination_directory=root / "custody",
                    received_at_utc="2026-07-21T02:02:00Z",
                    run_id="test",
                    git_source_commit="a" * 40,
                )

    def test_rejects_incomplete_attestation_and_binding_drift(self) -> None:
        for mutation, message in (
            (lambda value: value["owner"].update(attestation=False), "attestation"),
            (lambda value: value["responses"][1].update(candidate_id="GVP-X"), "identity"),
        ):
            with self.subTest(message=message), _ignored_temporary_directory() as temporary:
                root = Path(temporary)
                response = self._response()
                mutation(response)
                source = self._source(root, response)
                with self.assertRaisesRegex(GrandviewOwnerResponseLockError, message):
                    preserve_response_without_reveal(
                        repository_root=ROOT,
                        surface_path=SURFACE,
                        source_response_path=source,
                        destination_directory=root / "custody",
                        received_at_utc="2026-07-21T02:02:00Z",
                        run_id="test",
                        git_source_commit="a" * 40,
                    )

    def test_refuses_overwrite(self) -> None:
        with _ignored_temporary_directory() as temporary:
            root = Path(temporary)
            source = self._source(root)
            arguments = dict(
                repository_root=ROOT,
                surface_path=SURFACE,
                source_response_path=source,
                destination_directory=root / "custody",
                received_at_utc="2026-07-21T02:02:00Z",
                run_id="test",
                git_source_commit="a" * 40,
            )
            preserve_response_without_reveal(**arguments)
            with self.assertRaisesRegex(GrandviewOwnerResponseLockError, "overwrite"):
                preserve_response_without_reveal(**arguments)


if __name__ == "__main__":
    unittest.main()
