from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from burnlens.replacement_event_reference_request import (
    CROSS_PROGRAM_MAPPING_PRODUCTS,
    CUSTODY_PATHS,
    EVENT_ID,
    EXPECTED_PRODUCT,
    MAP_ID,
    MTBS_MAPPING_PRODUCTS,
    PUBLIC_REPORT_PATH,
    WardCreekReferenceRequestError,
    acquire_request_receipt,
    normalize_metadata,
    request_payload,
)


def metadata_bytes() -> bytes:
    properties = {
        "id": EXPECTED_PRODUCT["catalog_id"],
        "map_id": EXPECTED_PRODUCT["map_id"],
        "map_prog": EXPECTED_PRODUCT["program"],
        "incid_name": EXPECTED_PRODUCT["incident_name"],
        "event_id": EXPECTED_PRODUCT["event_id"],
        "ig_date": EXPECTED_PRODUCT["ignition_date"] + "Z",
        "burnbndac": EXPECTED_PRODUCT["boundary_acres"],
        "nonstandard": EXPECTED_PRODUCT["nonstandard"],
    }
    return json.dumps(
        {
            "type": "FeatureCollection",
            "features": [
                {"type": "Feature", "geometry": None, "properties": properties}
            ],
        }
    ).encode()


class ReplacementEventReferenceRequestTests(unittest.TestCase):
    def test_exact_metadata_and_mtbs_only_payload_pass(self):
        self.assertEqual(normalize_metadata(metadata_bytes()), EXPECTED_PRODUCT)
        payload = request_payload()
        self.assertEqual(payload["mapping_ids"], [MAP_ID])
        self.assertEqual(tuple(payload["mapping_products"]), MTBS_MAPPING_PRODUCTS)
        combined = " ".join(payload["mapping_products"]).casefold()
        for disallowed in ("soil burn", "basal area", "canopy cover", "composite burn"):
            self.assertNotIn(disallowed, combined)
        self.assertEqual(len(CROSS_PROGRAM_MAPPING_PRODUCTS), 8)

    def test_metadata_drift_fails_closed(self):
        changed = json.loads(metadata_bytes())
        changed["features"][0]["properties"]["map_id"] = 1
        with self.assertRaisesRegex(WardCreekReferenceRequestError, "drifted"):
            normalize_metadata(json.dumps(changed).encode())

    def test_receipt_withholds_recipient_and_is_no_overwrite(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            upstream = root / "samples/reference/phase-two/WARD-CREEK-OPTICAL-CUSTODY-2026-001.json"
            upstream.parent.mkdir(parents=True)
            upstream.write_text(
                json.dumps(
                    {
                        "decision": (
                            "PASS_WARD_CREEK_OPTICAL_CUSTODY_AUTHORIZE_U03_REFERENCE_INTAKE"
                        )
                    }
                )
            )
            with patch(
                "burnlens.replacement_event_reference_request.verify_repository_preflight"
            ), patch(
                "burnlens.replacement_event_reference_request.UPSTREAM_OPTICAL_REPORT",
                {
                    "path": upstream.relative_to(root).as_posix(),
                    "bytes": upstream.stat().st_size,
                    "sha256": __import__("hashlib").sha256(upstream.read_bytes()).hexdigest(),
                    "decision": (
                        "PASS_WARD_CREEK_OPTICAL_CUSTODY_AUTHORIZE_U03_REFERENCE_INTAKE"
                    ),
                },
            ):
                report = acquire_request_receipt(
                    repository_root=root,
                    recipient="owner@example.com",
                    requested_at_utc="2026-07-24T21:00:00Z",
                    run_id="BL-2026-07-24-ward-creek-reference-request-r001",
                    git_source_commit="a" * 40,
                    metadata_fetch_fn=metadata_bytes,
                    queue_post_fn=lambda _recipient: b'{"success":true}',
                )
                self.assertEqual(
                    report["decision"],
                    "ACCEPT_WARD_CREEK_REQUEST_RECEIPT_PENDING_EXACT_DELIVERY",
                )
                self.assertTrue((root / PUBLIC_REPORT_PATH).is_file())
                custody = root / CUSTODY_PATHS["request_directory"]
                combined = b"".join(path.read_bytes() for path in custody.iterdir())
                combined += (root / PUBLIC_REPORT_PATH).read_bytes()
                self.assertNotIn(b"owner@example.com", combined)
                with self.assertRaisesRegex(
                    WardCreekReferenceRequestError, "no overwrite"
                ):
                    acquire_request_receipt(
                        repository_root=root,
                        recipient="owner@example.com",
                        requested_at_utc="2026-07-24T21:00:00Z",
                        run_id="BL-2026-07-24-ward-creek-reference-request-r001",
                        git_source_commit="a" * 40,
                        metadata_fetch_fn=metadata_bytes,
                        queue_post_fn=lambda _recipient: b'{"success":true}',
                    )

    def test_ambiguous_queue_attempt_is_retained(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with patch(
                "burnlens.replacement_event_reference_request.verify_repository_preflight"
            ):
                def ambiguous(_recipient: str) -> bytes:
                    raise WardCreekReferenceRequestError(
                        "queue outcome is unknown; do not retry automatically"
                    )

                with self.assertRaisesRegex(
                    WardCreekReferenceRequestError, "do not retry"
                ):
                    acquire_request_receipt(
                        repository_root=root,
                        recipient="owner@example.com",
                        requested_at_utc="2026-07-24T21:00:00Z",
                        run_id="BL-2026-07-24-ward-creek-reference-request-r001",
                        git_source_commit="b" * 40,
                        metadata_fetch_fn=metadata_bytes,
                        queue_post_fn=ambiguous,
                    )
                state = json.loads(
                    (
                        root
                        / CUSTODY_PATHS["request_directory"]
                        / "queue-outcome-unknown.json"
                    ).read_text()
                )
                self.assertEqual(
                    state["state"], "QUEUE_OUTCOME_UNKNOWN_DO_NOT_RETRY"
                )
                self.assertFalse((root / PUBLIC_REPORT_PATH).exists())


if __name__ == "__main__":
    unittest.main()
