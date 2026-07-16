from __future__ import annotations

from contextlib import redirect_stderr
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

from burnlens import acquire_cross_event_optical as acquire_cli
from burnlens.cross_event_optical_contract import (
    CROSS_EVENT_CONTRACTS,
    EXPECTED_METADATA,
    MAX_TRANSFER_ATTEMPTS,
    ROUTE_PRECEDENCE,
    REGISTRATION_MANIFEST_NAME,
    TEMPORARY_PREFIX,
    TEMPORARY_SUFFIX,
    CdseCredentials,
    _validate_working_entries,
    acquire_cross_event_package,
    refresh_cross_event_metadata,
    validate_cross_event_contracts,
    validate_cross_event_metadata,
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
    contract = next(item for item in CROSS_EVENT_CONTRACTS if item.role == role)
    expected = EXPECTED_METADATA[role]
    return {
        "Id": contract.provider_id,
        "Name": contract.native_id,
        "ContentLength": contract.expected_size_bytes,
        "Online": True,
        "ContentDate": {"Start": expected["acquisition_utc"], "End": expected["acquisition_utc"]},
        "PublicationDate": "2024-05-09T00:00:00Z",
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


class CrossEventOpticalContractTests(unittest.TestCase):
    def test_four_frozen_assets_form_two_exact_pairs(self) -> None:
        self.assertEqual(validate_cross_event_contracts(CROSS_EVENT_CONTRACTS), [])
        self.assertEqual(len(CROSS_EVENT_CONTRACTS), 4)
        self.assertEqual(len({item.provider_id for item in CROSS_EVENT_CONTRACTS}), 4)

    def test_contract_rejects_within_event_geometry_drift(self) -> None:
        changed = replace(
            CROSS_EVENT_CONTRACTS[1],
            native_id=CROSS_EVENT_CONTRACTS[1].native_id.replace("R013", "R113"),
        )
        reasons = validate_cross_event_contracts((CROSS_EVENT_CONTRACTS[0], changed, *CROSS_EVENT_CONTRACTS[2:]))
        self.assertIn("EVENT_PAIR_GEOMETRY_IDENTITY_MISMATCH", reasons)

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
        self.assertNotIn("example-password", repr(credentials))

    def test_public_metadata_refresh_accepts_only_frozen_odata_contract(self) -> None:
        payloads = {item.provider_id: metadata_payload(item.role) for item in CROSS_EVENT_CONTRACTS}

        def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
            self.assertIn("Attributes", request.full_url)
            self.assertIn("$expand=Attributes", request.full_url)
            provider_id = next(key for key in payloads if key in request.full_url)
            return FakeResponse(payloads[provider_id])

        snapshot = refresh_cross_event_metadata(
            observed_at_utc="2026-07-15T23:32:00Z",
            urlopen_fn=fake_urlopen,
        )
        self.assertEqual(len(snapshot["records"]), 4)
        self.assertEqual(snapshot["route_precedence"], ROUTE_PRECEDENCE)
        self.assertEqual(validate_cross_event_metadata(snapshot), [])
        self.assertNotIn("stable_route", json.dumps(snapshot))

    def test_route_specific_stac_packaging_difference_is_disclosed_not_coerced(self) -> None:
        contract = CROSS_EVENT_CONTRACTS[0]
        expected = EXPECTED_METADATA[contract.role]
        self.assertNotEqual(contract.expected_size_bytes, expected["stac_product_bytes"])
        self.assertIn("OData", ROUTE_PRECEDENCE["archive_authority"])
        self.assertIn("zipper", ROUTE_PRECEDENCE["stac_asset_role"])

    def test_cross_event_working_files_use_onedrive_ignored_tmp_suffix(self) -> None:
        self.assertEqual(TEMPORARY_SUFFIX, ".tmp")
        self.assertEqual(TEMPORARY_PREFIX, "~$")
        self.assertEqual(REGISTRATION_MANIFEST_NAME, ".burnlens-registration.json")
        with TemporaryDirectory() as directory:
            quarantine = Path(directory)
            accepted = quarantine / f"~${CROSS_EVENT_CONTRACTS[0].expected_filename}.tmp"
            accepted.write_bytes(b"")
            _validate_working_entries(quarantine)
            accepted.rename(quarantine / f"{CROSS_EVENT_CONTRACTS[0].expected_filename}.part")
            with self.assertRaisesRegex(AcquisitionError, "UNEXPECTED_ACQUISITION_WORKING_ENTRY"):
                _validate_working_entries(quarantine)

    def test_retryable_early_eof_gets_bounded_fresh_token_attempt(self) -> None:
        success = {"role": CROSS_EVENT_CONTRACTS[0].role, "status": "DOWNLOADED", "bytes": 1}
        with TemporaryDirectory() as directory, patch(
            "burnlens.cross_event_optical_contract.validate_cross_event_contracts", return_value=[]
        ), patch(
            "burnlens.cross_event_optical_contract.validate_cross_event_metadata", return_value=[]
        ), patch(
            "burnlens.cross_event_optical_contract.request_cdse_access_token", return_value="token"
        ) as token_request, patch(
            "burnlens.cross_event_optical_contract.stream_asset",
            side_effect=[
                AcquisitionError("DOWNLOAD_SIZE_MISMATCH", role=CROSS_EVENT_CONTRACTS[0].role),
                success,
                {**success, "role": CROSS_EVENT_CONTRACTS[1].role},
                {**success, "role": CROSS_EVENT_CONTRACTS[2].role},
                {**success, "role": CROSS_EVENT_CONTRACTS[3].role},
            ],
        ) as stream, patch(
            "burnlens.cross_event_optical_contract.promote_quarantine", return_value={"run_id": "test"}
        ), patch(
            "burnlens.cross_event_optical_contract.verify_registered_package",
            return_value={"accepted_as_unchanged_registered_package": True},
        ):
            result = acquire_cross_event_package(
                credentials=CdseCredentials("user", "secret"),
                quarantine=Path(directory) / "quarantine",
                raw_parent=Path(directory) / "raw",
                generated_at_utc="2026-07-16T00:30:00Z",
                run_id="BL-TEST-CROSS-EVENT-RETRY",
                metadata_snapshot={},
            )
        self.assertEqual(MAX_TRANSFER_ATTEMPTS, 5)
        self.assertEqual(token_request.call_count, 5)
        self.assertEqual(stream.call_count, 5)
        self.assertTrue(all(call.kwargs["part_suffix"] == ".tmp" for call in stream.call_args_list))
        self.assertTrue(all(call.kwargs["part_prefix"] == "~$" for call in stream.call_args_list))
        self.assertEqual(result["downloads"][0]["attempt_count"], 2)

    def test_public_odata_metadata_drift_fails_closed(self) -> None:
        payloads = {item.provider_id: metadata_payload(item.role) for item in CROSS_EVENT_CONTRACTS}
        payloads[CROSS_EVENT_CONTRACTS[1].provider_id]["ContentLength"] += 1

        def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
            provider_id = next(key for key in payloads if key in request.full_url)
            return FakeResponse(payloads[provider_id])

        with self.assertRaisesRegex(AcquisitionError, "PUBLIC_METADATA_DRIFT"):
            refresh_cross_event_metadata(
                observed_at_utc="2026-07-15T23:32:00Z",
                urlopen_fn=fake_urlopen,
            )

    def test_promotion_rejection_becomes_safe_acquisition_error(self) -> None:
        evaluation = {
            "reason_codes": ["INCOMPLETE_OR_INVALID_ASSET_SET"],
            "observations": [
                {"role": item.role, "reason_codes": ["ASSET_MULTILINK_NOT_ALLOWED"]}
                for item in CROSS_EVENT_CONTRACTS
            ],
        }
        with TemporaryDirectory() as directory, patch(
            "burnlens.cross_event_optical_contract.validate_cross_event_contracts", return_value=[]
        ), patch(
            "burnlens.cross_event_optical_contract.validate_cross_event_metadata", return_value=[]
        ), patch(
            "burnlens.cross_event_optical_contract.request_cdse_access_token", return_value="token"
        ), patch(
            "burnlens.cross_event_optical_contract.stream_asset", return_value={"status": "REUSED"}
        ), patch(
            "burnlens.cross_event_optical_contract.promote_quarantine", side_effect=ValueError("unsafe")
        ), patch(
            "burnlens.cross_event_optical_contract.evaluate_quarantine", return_value=evaluation
        ):
            with self.assertRaises(AcquisitionError) as context:
                acquire_cross_event_package(
                    credentials=CdseCredentials("user", "secret"),
                    quarantine=Path(directory) / "quarantine",
                    raw_parent=Path(directory) / "raw",
                    generated_at_utc="2026-07-15T23:32:00Z",
                    run_id="BL-TEST-CROSS-EVENT-OPTICAL",
                    metadata_snapshot={},
                )
        self.assertEqual(context.exception.reason_code, "QUARANTINE_PROMOTION_REJECTED")
        self.assertIn("tepee-2018-pre:ASSET_MULTILINK_NOT_ALLOWED", context.exception.detail)

    def test_cli_persists_safe_state_for_unexpected_local_failure(self) -> None:
        with TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            args = SimpleNamespace(
                quarantine=Path(directory) / "quarantine",
                raw_parent=Path(directory) / "raw",
                state_file=state,
                generated_at_utc="2026-07-15T23:32:00Z",
                run_id="BL-TEST-CROSS-EVENT-OPTICAL",
            )
            with patch.object(acquire_cli, "parse_args", return_value=args), patch.object(
                acquire_cli.CdseCredentials,
                "from_environment",
                return_value=CdseCredentials("user", "secret"),
            ), patch.object(acquire_cli, "refresh_cross_event_metadata", return_value={}), patch.object(
                acquire_cli,
                "acquire_cross_event_package",
                side_effect=ValueError("local path must not be exposed"),
            ):
                with redirect_stderr(io.StringIO()):
                    self.assertEqual(acquire_cli.main(), 2)
            failure = json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(failure["reason_code"], "LOCAL_TRANSACTION_FAILURE")
            self.assertEqual(failure["detail"], "ValueError")
            self.assertNotIn("local path", json.dumps(failure))


if __name__ == "__main__":
    unittest.main()
