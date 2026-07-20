from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs

from burnlens.green_ridge_reference_request import (
    EVENT_ID,
    EXPECTED_PRODUCTS,
    GreenRidgeReferenceRequestError,
    acquire_request_receipt,
    normalize_metadata,
    request_payload,
)


def metadata_bytes() -> bytes:
    features = []
    names = {
        "catalog_id": "id",
        "map_id": "map_id",
        "program": "map_prog",
        "incident_name": "incid_name",
        "event_id": "event_id",
        "assessment_type": "asmt_type",
        "boundary_acres": "burnbndac",
        "post_id": "post_id",
        "model": "model",
        "dnbr_offset": "dnbr_offst",
        "dnbr_stddev": "dnbr_stddv",
        "nodata_threshold": "nodata_t",
        "increased_greenness_threshold": "incgreen_t",
        "low_threshold": "low_t",
        "moderate_threshold": "mod_t",
        "high_threshold": "high_t",
        "provider_comment": "comment",
        "nonstandard": "nonstandard",
    }
    for expected in EXPECTED_PRODUCTS:
        properties = {target: expected[source] for source, target in names.items()}
        properties["ig_date"] = expected["ignition_date"] + "Z"
        properties["postfire_date"] = expected["postfire_date"] + "Z"
        features.append({"type": "Feature", "geometry": None, "properties": properties})
    return json.dumps({"type": "FeatureCollection", "features": features}).encode()


class Response:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.status = 200

    def __enter__(self) -> "Response":
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self, maximum: int) -> bytes:
        return self.data[:maximum]


class GreenRidgeReferenceRequestTests(unittest.TestCase):
    def test_exact_metadata_normalizes_and_payload_is_native_utm(self) -> None:
        observed = normalize_metadata(metadata_bytes())
        self.assertEqual({item["map_id"] for item in observed}, {10015623, 10021333, 10016049})
        payload = request_payload()
        self.assertEqual(payload["projection"], "UTM")
        self.assertEqual(payload["mapping_bundles"], [])
        self.assertEqual(len(payload["mapping_products"]), 18)

    def test_metadata_drift_fails_closed(self) -> None:
        changed = json.loads(metadata_bytes())
        changed["features"][0]["properties"]["map_id"] = 1
        with self.assertRaisesRegex(GreenRidgeReferenceRequestError, "drifted"):
            normalize_metadata(json.dumps(changed).encode())

    def test_receipt_is_atomic_private_and_no_overwrite(self) -> None:
        queue = b'{"success":true}'
        captured = []

        def open_response(request: object, **_: object) -> Response:
            captured.append(request)
            return Response(metadata_bytes() if len(captured) == 1 else queue)

        with TemporaryDirectory() as directory, patch(
            "burnlens.green_ridge_reference_request.urlopen", side_effect=open_response
        ):
            output = Path(directory) / "receipt"
            receipt = acquire_request_receipt(
                output,
                recipient="owner@example.com",
                requested_at_utc="2026-07-19T23:30:00Z",
                run_id="BL-TEST-GREEN-RIDGE-REFERENCE-REQUEST",
            )
            self.assertEqual(receipt["event_id"], EVENT_ID)
            self.assertEqual(receipt["request"]["recipient"], "WITHHELD_PRIVATE")
            body = parse_qs(captured[1].data.decode())
            self.assertEqual(body["email"], ["owner@example.com"])
            combined = b"".join(path.read_bytes() for path in output.iterdir())
            self.assertNotIn(b"owner@example.com", combined)
            with self.assertRaisesRegex(GreenRidgeReferenceRequestError, "no overwrite"):
                acquire_request_receipt(
                    output,
                    recipient="owner@example.com",
                    requested_at_utc="2026-07-19T23:30:00Z",
                    run_id="BL-TEST-GREEN-RIDGE-REFERENCE-REQUEST",
                )


if __name__ == "__main__":
    unittest.main()
