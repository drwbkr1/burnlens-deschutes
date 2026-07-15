from __future__ import annotations

from dataclasses import replace
import io
import json
import os
import unittest
from unittest.mock import patch
from urllib.request import Request

from burnlens.optical_pair_contract import (
    EXPECTED_METADATA,
    OPTICAL_CONTRACTS,
    CdseCredentials,
    refresh_optical_metadata,
    validate_optical_contracts,
    validate_optical_metadata,
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


def metadata_payload(role: str) -> dict:
    contract = next(item for item in OPTICAL_CONTRACTS if item.role == role)
    expected = EXPECTED_METADATA[role]
    return {
        "Id": contract.provider_id,
        "Name": contract.native_id,
        "ContentLength": contract.expected_size_bytes,
        "Online": True,
        "ContentDate": {
            "Start": expected["acquisition_utc"],
            "End": expected["acquisition_utc"],
        },
        "PublicationDate": "2024-07-06T03:08:53Z",
        "S3Path": f"/eodata/Sentinel-2/MSI/L2A/2024/{contract.native_id}",
        "Checksum": [
            {"Algorithm": "MD5", "Value": contract.provider_md5},
            {"Algorithm": "BLAKE3", "Value": contract.provider_blake3},
        ],
        "Attributes": [
            {"Name": "platformSerialIdentifier", "Value": expected["platform_serial_identifier"]},
            {"Name": "tileId", "Value": expected["tile_id"]},
            {"Name": "relativeOrbitNumber", "Value": expected["relative_orbit_number"]},
            {"Name": "processorVersion", "Value": expected["processor_version"]},
            {"Name": "productType", "Value": expected["product_type"]},
            {"Name": "cloudCover", "Value": expected["cloud_cover_percent"]},
        ],
    }


class OpticalPairContractTests(unittest.TestCase):
    def test_frozen_pair_is_same_platform_baseline_orbit_and_tile(self) -> None:
        self.assertEqual(validate_optical_contracts(OPTICAL_CONTRACTS), [])

    def test_contract_rejects_geometry_identity_drift(self) -> None:
        changed = replace(
            OPTICAL_CONTRACTS[1],
            native_id=OPTICAL_CONTRACTS[1].native_id.replace("R013", "R113"),
        )
        reasons = validate_optical_contracts((OPTICAL_CONTRACTS[0], changed))
        self.assertIn("OPTICAL_PAIR_GEOMETRY_IDENTITY_MISMATCH", reasons)

    def test_cdse_credentials_are_popped_and_redacted(self) -> None:
        values = {
            "BURNLENS_CDSE_USERNAME": "example-user",
            "BURNLENS_CDSE_PASSWORD": "example-password",
        }
        with patch.dict(os.environ, values, clear=False):
            credentials = CdseCredentials.from_environment()
            for name in values:
                self.assertNotIn(name, os.environ)
        self.assertEqual(repr(credentials), "CdseCredentials(<redacted>)")
        self.assertNotIn("password", repr(credentials))

    def test_missing_cdse_environment_fails_without_secret_value(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(AcquisitionError, "CREDENTIAL_ENV_MISSING"):
                CdseCredentials.from_environment()

    def test_public_metadata_refresh_accepts_only_the_frozen_pair(self) -> None:
        payloads = {
            item.provider_id: metadata_payload(item.role) for item in OPTICAL_CONTRACTS
        }

        def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
            self.assertIn("Attributes", request.full_url)
            self.assertIn("$expand=Attributes", request.full_url)
            provider_id = next(key for key in payloads if key in request.full_url)
            return FakeResponse(payloads[provider_id])

        snapshot = refresh_optical_metadata(
            observed_at_utc="2026-07-15T16:00:59Z",
            urlopen_fn=fake_urlopen,
        )
        self.assertTrue(snapshot["live_refresh_performed"])
        self.assertEqual(len(snapshot["records"]), 2)
        self.assertEqual(validate_optical_metadata(snapshot), [])
        self.assertNotIn("stable_route", json.dumps(snapshot))

    def test_public_metadata_drift_fails_closed(self) -> None:
        payloads = {
            item.provider_id: metadata_payload(item.role) for item in OPTICAL_CONTRACTS
        }
        payloads[OPTICAL_CONTRACTS[1].provider_id]["Attributes"][-1]["Value"] = 1.0

        def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
            provider_id = next(key for key in payloads if key in request.full_url)
            return FakeResponse(payloads[provider_id])

        with self.assertRaisesRegex(AcquisitionError, "PUBLIC_METADATA_DRIFT"):
            refresh_optical_metadata(
                observed_at_utc="2026-07-15T16:00:59Z",
                urlopen_fn=fake_urlopen,
            )


if __name__ == "__main__":
    unittest.main()
