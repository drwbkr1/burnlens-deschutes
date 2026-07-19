from __future__ import annotations

from dataclasses import replace
import io
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.request import Request

from burnlens import acquire_green_ridge_optical as acquire_cli
from burnlens.green_ridge_optical_contract import (
    GREEN_RIDGE_CONTRACTS,
    EXPECTED_METADATA,
    ROUTE_PRECEDENCE,
    CdseCredentials,
    _validate_working_entries,
    refresh_green_ridge_metadata,
    validate_green_ridge_contracts,
    validate_green_ridge_metadata,
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
    contract = next(item for item in GREEN_RIDGE_CONTRACTS if item.role == role)
    expected = EXPECTED_METADATA[role]
    return {
        "Id": contract.provider_id,
        "Name": contract.native_id,
        "ContentLength": contract.expected_size_bytes,
        "Online": True,
        "ContentDate": {"Start": expected["acquisition_utc"], "End": expected["acquisition_utc"]},
        "PublicationDate": "2026-07-19T00:00:00Z",
        "S3Path": f"/eodata/Sentinel-2/MSI/L2A/{contract.native_id}",
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


class GreenRidgeOpticalContractTests(unittest.TestCase):
    def test_two_assets_form_one_exact_green_ridge_pair(self) -> None:
        self.assertEqual(validate_green_ridge_contracts(GREEN_RIDGE_CONTRACTS), [])
        self.assertEqual(len(GREEN_RIDGE_CONTRACTS), 2)
        self.assertEqual(sum(item.expected_size_bytes for item in GREEN_RIDGE_CONTRACTS), 2_388_456_138)

    def test_pair_geometry_drift_fails_closed(self) -> None:
        changed = replace(
            GREEN_RIDGE_CONTRACTS[1],
            native_id=GREEN_RIDGE_CONTRACTS[1].native_id.replace("T10TFQ", "T10TFP"),
        )
        self.assertIn(
            "GREEN_RIDGE_PAIR_GEOMETRY_IDENTITY_MISMATCH",
            validate_green_ridge_contracts((GREEN_RIDGE_CONTRACTS[0], changed)),
        )

    def test_live_metadata_shape_accepts_only_exact_odata_contract(self) -> None:
        payloads = {item.provider_id: metadata_payload(item.role) for item in GREEN_RIDGE_CONTRACTS}

        def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
            provider_id = next(key for key in payloads if key in request.full_url)
            return FakeResponse(payloads[provider_id])

        snapshot = refresh_green_ridge_metadata(
            observed_at_utc="2026-07-19T22:10:00Z", urlopen_fn=fake_urlopen
        )
        self.assertEqual(validate_green_ridge_metadata(snapshot), [])
        self.assertEqual(snapshot["route_precedence"], ROUTE_PRECEDENCE)
        self.assertNotIn("stable_route", json.dumps(snapshot))

    def test_metadata_checksum_drift_fails_closed(self) -> None:
        payloads = {item.provider_id: metadata_payload(item.role) for item in GREEN_RIDGE_CONTRACTS}
        payloads[GREEN_RIDGE_CONTRACTS[0].provider_id]["Checksum"][0]["Value"] = "0" * 32

        def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
            provider_id = next(key for key in payloads if key in request.full_url)
            return FakeResponse(payloads[provider_id])

        with self.assertRaisesRegex(AcquisitionError, "PUBLIC_METADATA_DRIFT"):
            refresh_green_ridge_metadata(
                observed_at_utc="2026-07-19T22:10:00Z", urlopen_fn=fake_urlopen
            )

    def test_credentials_are_popped_and_redacted(self) -> None:
        values = {
            "BURNLENS_CDSE_USERNAME": "example-user",
            "BURNLENS_CDSE_PASSWORD": "example-password",
        }
        with patch.dict(os.environ, values, clear=False):
            credentials = CdseCredentials.from_environment()
            self.assertNotIn("BURNLENS_CDSE_USERNAME", os.environ)
            self.assertNotIn("BURNLENS_CDSE_PASSWORD", os.environ)
        self.assertNotIn("example-password", repr(credentials))

    def test_working_directory_rejects_unexpected_entries(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory)
            accepted = path / f"~${GREEN_RIDGE_CONTRACTS[0].expected_filename}.tmp"
            accepted.write_bytes(b"")
            _validate_working_entries(path)
            (path / "unexpected.txt").write_text("no", encoding="utf-8")
            with self.assertRaisesRegex(AcquisitionError, "UNEXPECTED_ACQUISITION_WORKING_ENTRY"):
                _validate_working_entries(path)

    def test_cli_persists_secret_free_failure_state(self) -> None:
        with TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            args = SimpleNamespace(
                quarantine=Path(directory) / "quarantine",
                raw_parent=Path(directory) / "raw",
                state_file=state,
                generated_at_utc="2026-07-19T22:10:00Z",
                run_id="BL-TEST-GREEN-RIDGE",
            )
            with patch.object(acquire_cli, "parse_args", return_value=args), patch.object(
                acquire_cli.CdseCredentials,
                "from_environment",
                return_value=CdseCredentials("user", "secret"),
            ), patch.object(
                acquire_cli, "refresh_green_ridge_metadata", return_value={}
            ), patch.object(
                acquire_cli,
                "acquire_green_ridge_package",
                side_effect=AcquisitionError("PUBLIC_METADATA_DRIFT", detail="SIZE"),
            ):
                self.assertEqual(acquire_cli.main(), 2)
            failure = json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(failure["reason_code"], "PUBLIC_METADATA_DRIFT")
            self.assertNotIn("secret", json.dumps(failure))


if __name__ == "__main__":
    unittest.main()
