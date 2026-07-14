from __future__ import annotations

from dataclasses import replace
import io
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from urllib.request import Request

from burnlens.paired_intake import EXACT_CONTRACTS, HDF5_MAGIC
from burnlens.provider_acquisition import (
    AcquisitionError,
    ProviderCredentials,
    SafeRedirectHandler,
    refresh_public_metadata,
    request_cdse_access_token,
    safe_endpoint,
    stream_asset,
    validate_metadata_snapshot,
)


class FakeResponse:
    def __init__(
        self,
        payload: bytes,
        *,
        status: int = 200,
        headers: dict[str, str] | None = None,
        final_url: str = "https://example.nasa.gov/file",
    ) -> None:
        self._stream = io.BytesIO(payload)
        self.status = status
        self.headers = headers or {}
        self._final_url = final_url

    def read(self, size: int = -1) -> bytes:
        return self._stream.read(size)

    def getcode(self) -> int:
        return self.status

    def geturl(self) -> str:
        return self._final_url

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None


class FakeOpener:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.requests: list[Request] = []

    def open(self, request: Request, timeout: float) -> FakeResponse:
        self.requests.append(request)
        return self.response


def metadata_payloads() -> dict[str, dict]:
    return {
        "cdse": {
            "Id": "58cebcf0-c417-4384-a93a-2d6b15344117",
            "Name": "S2B_MSIL2A_20240627T184919_N0510_R113_T10TFP_20240627T213644.SAFE",
            "ContentLength": 1_127_031_562,
            "Online": True,
            "Checksum": [
                {"Algorithm": "MD5", "Value": "3806a834a97ab2eb41f1edf5496b433c"},
                {
                    "Algorithm": "BLAKE3",
                    "Value": "546336e996586f4c276eb9ed3d9818f9574edbed24334dce74a394bd3759cb10",
                },
            ],
        },
        "fire": {
            "items": [
                {
                    "meta": {
                        "concept-id": "G3944882727-LPCLOUD",
                        "revision-date": "2026-01-03T01:53:50.819Z",
                    },
                    "umm": {
                        "GranuleUR": "VJ214IMG.A2024179.1936.002.2025284191612",
                        "DataGranule": {
                            "ArchiveAndDistributionInformation": [
                                {"Size": 2.5850448608398438, "SizeUnit": "MB"}
                            ]
                        },
                    },
                }
            ]
        },
        "geo": {
            "items": [
                {
                    "meta": {
                        "concept-id": "G4037038741-LPCLOUD",
                        "revision-date": "2026-04-30T04:50:17.152Z",
                    },
                    "umm": {
                        "GranuleUR": "VJ203MODLL.A2024179.1936.021.2024327213621",
                        "DataGranule": {
                            "ArchiveAndDistributionInformation": [
                                {"Size": 38.39088821411133, "SizeUnit": "MB"}
                            ]
                        },
                    },
                }
            ]
        },
    }


class ProviderAcquisitionTests(unittest.TestCase):
    def test_credentials_are_popped_and_repr_is_redacted(self) -> None:
        values = {
            "BURNLENS_CDSE_USERNAME": "cdse-user",
            "BURNLENS_CDSE_PASSWORD": "cdse-secret",
            "BURNLENS_EARTHDATA_USERNAME": "edl-user",
            "BURNLENS_EARTHDATA_PASSWORD": "edl-secret",
        }
        with patch.dict(os.environ, values, clear=False):
            credentials = ProviderCredentials.from_environment()
            for name in values:
                self.assertNotIn(name, os.environ)
        self.assertEqual(repr(credentials), "ProviderCredentials(<redacted>)")
        self.assertNotIn("secret", repr(credentials))

    def test_missing_credentials_fail_without_values(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(AcquisitionError, "CREDENTIAL_ENV_MISSING"):
                ProviderCredentials.from_environment()

    def test_exact_public_metadata_refresh_and_validation(self) -> None:
        payloads = metadata_payloads()

        def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
            url = request.full_url
            if "catalogue.dataspace" in url:
                payload = payloads["cdse"]
            elif "G3944882727" in url:
                payload = payloads["fire"]
            else:
                payload = payloads["geo"]
            return FakeResponse(json.dumps(payload).encode("utf-8"))

        snapshot = refresh_public_metadata(
            observed_at_utc="2026-07-14T17:45:00Z",
            urlopen_fn=fake_urlopen,
        )
        self.assertTrue(snapshot["live_refresh_performed"])
        self.assertEqual(len(snapshot["records"]), 3)
        self.assertEqual(validate_metadata_snapshot(snapshot), [])

    def test_public_metadata_drift_fails_closed(self) -> None:
        payloads = metadata_payloads()
        payloads["cdse"]["ContentLength"] += 1

        def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
            url = request.full_url
            if "catalogue.dataspace" in url:
                payload = payloads["cdse"]
            elif "G3944882727" in url:
                payload = payloads["fire"]
            else:
                payload = payloads["geo"]
            return FakeResponse(json.dumps(payload).encode("utf-8"))

        with self.assertRaisesRegex(AcquisitionError, "PUBLIC_METADATA_DRIFT"):
            refresh_public_metadata(
                observed_at_utc="2026-07-14T17:45:00Z",
                urlopen_fn=fake_urlopen,
            )

    def test_cmr_size_unit_must_be_megabytes(self) -> None:
        payloads = metadata_payloads()
        payloads["fire"]["items"][0]["umm"]["DataGranule"][
            "ArchiveAndDistributionInformation"
        ][0]["SizeUnit"] = "KB"

        def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
            url = request.full_url
            if "catalogue.dataspace" in url:
                payload = payloads["cdse"]
            elif "G3944882727" in url:
                payload = payloads["fire"]
            else:
                payload = payloads["geo"]
            return FakeResponse(json.dumps(payload).encode("utf-8"))

        with self.assertRaisesRegex(AcquisitionError, "CMR_SIZE_UNIT_UNEXPECTED"):
            refresh_public_metadata(
                observed_at_utc="2026-07-14T17:45:00Z",
                urlopen_fn=fake_urlopen,
            )

    def test_cdse_token_request_returns_only_access_token(self) -> None:
        observed_body = b""

        def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
            nonlocal observed_body
            observed_body = request.data or b""
            return FakeResponse(
                json.dumps({"access_token": "short-lived-token", "refresh_token": "never-retain"}).encode(
                    "utf-8"
                )
            )

        token = request_cdse_access_token("user", "password", urlopen_fn=fake_urlopen)
        self.assertEqual(token, "short-lived-token")
        self.assertIn(b"client_id=cdse-public", observed_body)
        self.assertNotIn(b"never-retain", observed_body)

    def test_safe_endpoint_strips_signed_query_and_fragment(self) -> None:
        result = safe_endpoint("https://bucket.s3.amazonaws.com/path/file.h5?X-Amz-Signature=secret#fragment")
        self.assertEqual(result, "https://bucket.s3.amazonaws.com/path/file.h5")
        self.assertNotIn("Signature", result)

    def test_redirect_handler_rejects_untrusted_or_insecure_host(self) -> None:
        handler = SafeRedirectHandler(allowed_host_suffixes=(".nasa.gov",))
        request = Request("https://data.nasa.gov/file")
        with self.assertRaisesRegex(AcquisitionError, "UNTRUSTED_REDIRECT_HOST"):
            handler.redirect_request(request, None, 302, "Found", {}, "https://example.com/file")
        with self.assertRaisesRegex(AcquisitionError, "UNTRUSTED_REDIRECT_HOST"):
            handler.redirect_request(request, None, 302, "Found", {}, "http://data.nasa.gov/file")

    def test_redirect_handler_does_not_suffix_match_exact_auth_host(self) -> None:
        self.assertTrue(
            SafeRedirectHandler._matches(
                "urs.earthdata.nasa.gov",
                ("urs.earthdata.nasa.gov",),
            )
        )
        self.assertFalse(
            SafeRedirectHandler._matches(
                "evilurs.earthdata.nasa.gov",
                ("urs.earthdata.nasa.gov",),
            )
        )

    def test_stream_asset_accepts_exact_binary_and_uses_part_then_rename(self) -> None:
        payload = HDF5_MAGIC + b"data"
        contract = replace(
            EXACT_CONTRACTS[1],
            expected_filename="test.h5",
            expected_size_bytes=len(payload),
            stable_route="https://data.nasa.gov/test.h5",
        )
        response = FakeResponse(
            payload,
            headers={"Content-Type": "application/octet-stream"},
            final_url="https://bucket.s3.amazonaws.com/test.h5?signature=private",
        )
        with TemporaryDirectory() as directory:
            quarantine = Path(directory) / "quarantine"
            result = stream_asset(contract, quarantine, opener=FakeOpener(response))
            self.assertEqual((quarantine / "test.h5").read_bytes(), payload)
            self.assertFalse((quarantine / "test.h5.part").exists())

        self.assertEqual(result["status"], "DOWNLOADED")
        self.assertEqual(result["safe_final_endpoint"], "https://bucket.s3.amazonaws.com/test.h5")

    def test_stream_asset_resumes_only_matching_content_range(self) -> None:
        full = HDF5_MAGIC + b"data"
        offset = 9
        contract = replace(
            EXACT_CONTRACTS[1],
            expected_filename="resume.h5",
            expected_size_bytes=len(full),
            stable_route="https://data.nasa.gov/resume.h5",
        )
        response = FakeResponse(
            full[offset:],
            status=206,
            headers={
                "Content-Type": "application/octet-stream",
                "Content-Range": f"bytes {offset}-{len(full) - 1}/{len(full)}",
            },
        )
        opener = FakeOpener(response)
        with TemporaryDirectory() as directory:
            quarantine = Path(directory) / "quarantine"
            quarantine.mkdir()
            (quarantine / "resume.h5.part").write_bytes(full[:offset])
            result = stream_asset(contract, quarantine, opener=opener)
            self.assertEqual((quarantine / "resume.h5").read_bytes(), full)

        self.assertEqual(result["resumed_from_bytes"], offset)
        self.assertEqual(opener.requests[0].get_header("Range"), f"bytes={offset}-")

    def test_stream_asset_rejects_html_without_registering_file(self) -> None:
        contract = replace(
            EXACT_CONTRACTS[1],
            expected_filename="login.nc",
            expected_size_bytes=12,
            stable_route="https://data.nasa.gov/login.nc",
        )
        response = FakeResponse(
            b"<html>login</html>",
            headers={"Content-Type": "text/html"},
        )
        with TemporaryDirectory() as directory:
            quarantine = Path(directory) / "quarantine"
            with self.assertRaisesRegex(AcquisitionError, "DOWNLOAD_TEXT_RESPONSE_REJECTED"):
                stream_asset(contract, quarantine, opener=FakeOpener(response))
            self.assertFalse((quarantine / "login.nc").exists())

    def test_stream_asset_removes_oversized_partial_file(self) -> None:
        expected = HDF5_MAGIC + b"data"
        contract = replace(
            EXACT_CONTRACTS[1],
            expected_filename="oversized.h5",
            expected_size_bytes=len(expected),
            stable_route="https://data.nasa.gov/oversized.h5",
        )
        response = FakeResponse(
            expected + b"extra",
            headers={"Content-Type": "application/octet-stream"},
        )
        with TemporaryDirectory() as directory:
            quarantine = Path(directory) / "quarantine"
            with self.assertRaisesRegex(AcquisitionError, "DOWNLOAD_EXCEEDS_EXPECTED_SIZE"):
                stream_asset(contract, quarantine, opener=FakeOpener(response))
            self.assertFalse((quarantine / "oversized.h5.part").exists())


if __name__ == "__main__":
    unittest.main()
