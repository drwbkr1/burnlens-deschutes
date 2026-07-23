from __future__ import annotations

import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from burnlens.windigo_reference_request import (
    CUSTODY_PATHS,
    EVENT_ID,
    EXPECTED_PRODUCTS,
    MAPPING_PRODUCTS,
    WindigoReferenceRequestError,
    _validate_queue_response,
    acquire_request_receipt,
    build_public_request_report,
    normalize_metadata,
    request_payload,
)


def metadata_bytes() -> bytes:
    return json.dumps(
        {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": None,
                    "properties": {
                        "id": item["catalog_id"],
                        "map_id": item["map_id"],
                        "map_prog": item["program"],
                        "incid_name": item["incident_name"],
                        "event_id": item["event_id"],
                        "ig_date": f"{item['ignition_date']}Z",
                        "burnbndac": item["boundary_acres"],
                        "comment": item["provider_comment"],
                        "nonstandard": item["nonstandard"],
                    },
                }
                for item in reversed(EXPECTED_PRODUCTS)
            ],
        },
        separators=(",", ":"),
    ).encode()


class WindigoReferenceRequestTests(unittest.TestCase):
    def test_exact_three_program_payload_uses_all_eighteen_families(self):
        payload = request_payload()
        self.assertEqual(payload["mapping_ids"], [10022395, 10022960, 10029547])
        self.assertEqual(len(MAPPING_PRODUCTS), 18)
        self.assertEqual(payload["mapping_products"], list(MAPPING_PRODUCTS))
        self.assertEqual(payload["projection"], "UTM")

    def test_metadata_requires_exact_current_standard_roster(self):
        products = normalize_metadata(metadata_bytes())
        self.assertEqual(products, list(EXPECTED_PRODUCTS))
        drift = json.loads(metadata_bytes())
        drift["features"][0]["properties"]["nonstandard"] = True
        with self.assertRaisesRegex(WindigoReferenceRequestError, "drifted"):
            normalize_metadata(json.dumps(drift).encode())

    def test_queue_accepts_only_exact_success(self):
        _validate_queue_response(b'{"success":true}')
        for payload in (b'{"success":false}', b"{}", b"not-json"):
            with self.subTest(payload=payload):
                with self.assertRaises(WindigoReferenceRequestError):
                    _validate_queue_response(payload)

    def test_event_identity_is_frozen(self):
        self.assertEqual(EVENT_ID, "OR4336312205020220730")
        self.assertEqual(
            {item["program"] for item in EXPECTED_PRODUCTS},
            {"BAER", "RAVG", "MTBS"},
        )

    def test_accepted_request_preserves_private_custody_without_recipient(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / CUSTODY_PATHS["request_directory"]
            with patch(
                "burnlens.windigo_reference_request.verify_repository_preflight"
            ), patch(
                "burnlens.windigo_reference_request.fetch_metadata",
                return_value=metadata_bytes(),
            ), patch(
                "burnlens.windigo_reference_request._post_queue",
                return_value=b'{"success":true}',
            ):
                receipt = acquire_request_receipt(
                    output,
                    repository_root=root,
                    recipient="owner@example.com",
                    requested_at_utc="2026-07-23T21:00:00Z",
                    run_id="BL-2026-07-23-windigo-reference-request-r001",
                    git_source_commit="a" * 40,
                )
            self.assertEqual(receipt["request"]["state"], "ACCEPTED")
            self.assertEqual(receipt["request"]["recipient"], "WITHHELD_PRIVATE")
            self.assertTrue((output / "queue-attempt-started.json").is_file())
            self.assertTrue((output / "request-receipt.json").is_file())
            retained = b"".join(path.read_bytes() for path in output.iterdir())
            self.assertNotIn(b"owner@example.com", retained)
            with self.assertRaisesRegex(
                WindigoReferenceRequestError,
                "already exists",
            ):
                acquire_request_receipt(
                    output,
                    repository_root=root,
                    recipient="owner@example.com",
                    requested_at_utc="2026-07-23T21:00:00Z",
                    run_id="BL-2026-07-23-windigo-reference-request-r001",
                    git_source_commit="a" * 40,
                )

    def test_unknown_queue_outcome_is_retained_and_forbids_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / CUSTODY_PATHS["request_directory"]
            with patch(
                "burnlens.windigo_reference_request.verify_repository_preflight"
            ), patch(
                "burnlens.windigo_reference_request.fetch_metadata",
                return_value=metadata_bytes(),
            ), patch(
                "burnlens.windigo_reference_request._post_queue",
                side_effect=WindigoReferenceRequestError("unknown"),
            ):
                with self.assertRaisesRegex(WindigoReferenceRequestError, "unknown"):
                    acquire_request_receipt(
                        output,
                        repository_root=root,
                        recipient="owner@example.com",
                        requested_at_utc="2026-07-23T21:00:00Z",
                        run_id="BL-2026-07-23-windigo-reference-request-r001",
                        git_source_commit="a" * 40,
                    )
            self.assertTrue((output / "queue-outcome-unknown.json").is_file())
            state = json.loads(
                (output / "queue-outcome-unknown.json").read_text(encoding="utf-8")
            )
            self.assertEqual(state["state"], "QUEUE_OUTCOME_UNKNOWN_DO_NOT_RETRY")

    def test_public_reconciliation_withholds_recipient_and_binds_custody(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            private = root / CUSTODY_PATHS["request_directory"]
            private.mkdir(parents=True)
            payload = request_payload()
            receipt = {
                "contract_version": "windigo-reference-request-v0.1.0",
                "requested_at_utc": "2026-07-23T21:00:00Z",
                "run_id": "BL-2026-07-23-windigo-reference-request-r001",
                "git_source_commit": "3bd0062abfb90ec6b0bbb542c2c2413e69ceab56",
                "event_id": EVENT_ID,
                "request": {
                    "state": "ACCEPTED",
                    "recipient": "WITHHELD_PRIVATE",
                    "mapping_ids": payload["mapping_ids"],
                    "mapping_products": payload["mapping_products"],
                    "canonical_payload_sha256": "c" * 64,
                },
                "queue": {
                    "accepted": True,
                    "bytes": 16,
                    "sha256": "d" * 64,
                },
                "delivery": {"state": "PENDING_EMAIL_DELIVERY"},
            }
            files = {
                "metadata-response.json": metadata_bytes(),
                "queue-attempt-started.json": b"{}\n",
                "queue-response.json": b'{"success":true}',
                "request-prepared.json": b"{}\n",
                "request-receipt.json": (
                    json.dumps(receipt, indent=2) + "\n"
                ).encode(),
            }
            for name, data in files.items():
                (private / name).write_bytes(data)
            commit = "e" * 40

            def fake_git(_root, *arguments):
                values = {
                    ("rev-parse", "--show-toplevel"): str(root),
                    ("rev-parse", "HEAD"): commit,
                    ("branch", "--show-current"): (
                        "codex/p2o4-t35-windigo-deadline-gate"
                    ),
                    (
                        "rev-parse",
                        "origin/codex/p2o4-t35-windigo-deadline-gate",
                    ): commit,
                    ("status", "--porcelain=v1", "--untracked-files=all"): "",
                }
                return SimpleNamespace(
                    returncode=0,
                    stdout=values[arguments] + "\n",
                )

            with patch(
                "burnlens.windigo_reference_request._git",
                side_effect=fake_git,
            ):
                report = build_public_request_report(
                    repository_root=root,
                    reconciliation_commit=commit,
                )
            self.assertEqual(
                report["decision"],
                "ACCEPT_REQUEST_RECEIPT_PENDING_EXACT_DELIVERY",
            )
            self.assertEqual(report["request"]["recipient"], "WITHHELD_PRIVATE")
            self.assertEqual(len(report["private_custody_bindings"]), 5)


if __name__ == "__main__":
    unittest.main()
