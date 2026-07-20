from __future__ import annotations

from dataclasses import replace
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from urllib.request import Request

from burnlens.green_ridge_background_optical_contract import (
    BACKGROUND_OPTICAL_CONTRACTS,
    EVENT_GROUP_ID,
    EXPECTED_METADATA,
    EXTENDED_CONTRACT,
    ROUTE_PRECEDENCE,
    _validate_working_entries,
    refresh_background_optical_metadata,
    validate_background_optical_contracts,
    validate_background_optical_metadata,
)
from burnlens.provider_acquisition import AcquisitionError


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._stream = io.BytesIO(json.dumps(payload).encode("utf-8"))
        self.status = 200

    def read(self, size: int = -1) -> bytes:
        return self._stream.read(size)

    def getcode(self) -> int:
        return self.status

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None


def metadata_payload() -> dict:
    return {
        "Id": EXTENDED_CONTRACT.provider_id,
        "Name": EXTENDED_CONTRACT.native_id,
        "ContentLength": EXTENDED_CONTRACT.expected_size_bytes,
        "Online": True,
        "ContentDate": {"Start": EXPECTED_METADATA["acquisition_utc"]},
        "PublicationDate": "2023-03-11T21:04:16.033401Z",
        "S3Path": f"/eodata/Sentinel-2/MSI/L2A/{EXTENDED_CONTRACT.native_id}",
        "Checksum": [
            {"Algorithm": "MD5", "Value": EXTENDED_CONTRACT.provider_md5},
            {"Algorithm": "BLAKE3", "Value": EXTENDED_CONTRACT.provider_blake3},
        ],
        "Attributes": [
            {"Name": "platformSerialIdentifier", "Value": EXPECTED_METADATA["platform_serial_identifier"]},
            {"Name": "tileId", "Value": EXPECTED_METADATA["tile_id"]},
            {"Name": "relativeOrbitNumber", "Value": EXPECTED_METADATA["relative_orbit_number"]},
            {"Name": "processorVersion", "Value": EXPECTED_METADATA["processor_version"]},
            {"Name": "productType", "Value": EXPECTED_METADATA["product_type"]},
            {"Name": "cloudCover", "Value": EXPECTED_METADATA["cloud_cover_percent"]},
        ],
    }


class GreenRidgeBackgroundOpticalContractTests(unittest.TestCase):
    def test_exact_extended_asset_contract_passes(self) -> None:
        self.assertEqual(validate_background_optical_contracts(BACKGROUND_OPTICAL_CONTRACTS), [])
        self.assertEqual(len(BACKGROUND_OPTICAL_CONTRACTS), 1)
        self.assertEqual(EXTENDED_CONTRACT.expected_size_bytes, 1_193_992_663)

    def test_scene_identity_drift_fails_closed(self) -> None:
        changed = replace(EXTENDED_CONTRACT, native_id=EXTENDED_CONTRACT.native_id.replace("T10TFQ", "T10TFP"))
        self.assertIn(
            "CONTRACT_REQUIRES_EXACT_EXTENDED_ASSET",
            validate_background_optical_contracts((changed,)),
        )

    def test_live_metadata_shape_is_exact_and_private_route_absent(self) -> None:
        def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
            self.assertIn(EXTENDED_CONTRACT.provider_id, request.full_url)
            return FakeResponse(metadata_payload())

        snapshot = refresh_background_optical_metadata(
            observed_at_utc="2026-07-20T00:30:00Z", urlopen_fn=fake_urlopen
        )
        self.assertEqual(validate_background_optical_metadata(snapshot), [])
        self.assertEqual(snapshot["records"][0]["event_group_id"], EVENT_GROUP_ID)
        self.assertEqual(snapshot["route_precedence"], ROUTE_PRECEDENCE)
        self.assertNotIn("stable_route", json.dumps(snapshot))

    def test_checksum_drift_fails_closed(self) -> None:
        payload = metadata_payload()
        payload["Checksum"][0]["Value"] = "0" * 32

        with self.assertRaisesRegex(AcquisitionError, "PUBLIC_METADATA_DRIFT"):
            refresh_background_optical_metadata(
                observed_at_utc="2026-07-20T00:30:00Z",
                urlopen_fn=lambda request, timeout: FakeResponse(payload),
            )

    def test_working_directory_rejects_unexpected_entries(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory)
            (path / f"~${EXTENDED_CONTRACT.expected_filename}.tmp").write_bytes(b"")
            _validate_working_entries(path)
            (path / "unexpected.txt").write_text("no", encoding="utf-8")
            with self.assertRaisesRegex(AcquisitionError, "UNEXPECTED_ACQUISITION_WORKING_ENTRY"):
                _validate_working_entries(path)


if __name__ == "__main__":
    unittest.main()
