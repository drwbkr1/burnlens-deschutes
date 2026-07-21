from __future__ import annotations

from dataclasses import replace
import errno
import io
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.request import Request

from burnlens.paired_intake import EXACT_CONTRACTS, HDF5_MAGIC
from burnlens.provider_acquisition import (
    AcquisitionError,
    MAX_BOUNDED_TRANSFER_ATTEMPTS,
    ProviderCredentials,
    SafeRedirectHandler,
    classify_transfer_failure,
    promote_quarantine_no_overwrite,
    refresh_public_metadata,
    request_cdse_access_token,
    safe_endpoint,
    stream_asset,
    stream_cdse_asset_with_retries,
    validate_metadata_snapshot,
    write_private_state,
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


class SequenceOpener:
    def __init__(self, outcomes: list[FakeResponse | BaseException]) -> None:
        self.outcomes = list(outcomes)
        self.requests: list[Request] = []

    def open(self, request: Request, timeout: float) -> FakeResponse:
        self.requests.append(request)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


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

    def test_stream_asset_rejects_multilink_partial_before_request(self) -> None:
        full = HDF5_MAGIC + b"data"
        contract = replace(
            EXACT_CONTRACTS[1],
            expected_filename="linked-resume.h5",
            expected_size_bytes=len(full),
            stable_route="https://data.nasa.gov/linked-resume.h5",
        )
        with TemporaryDirectory() as directory:
            quarantine = Path(directory) / "quarantine"
            quarantine.mkdir()
            part = quarantine / "linked-resume.h5.part"
            part.write_bytes(full[:9])
            alias = Path(directory) / "upload-staging-alias"
            os.link(part, alias)
            opener = FakeOpener(
                FakeResponse(
                    full[9:],
                    status=206,
                    headers={
                        "Content-Type": "application/octet-stream",
                        "Content-Range": f"bytes 9-{len(full) - 1}/{len(full)}",
                    },
                )
            )
            with self.assertRaisesRegex(AcquisitionError, "PART_FILE_MULTILINK_NOT_ALLOWED"):
                stream_asset(contract, quarantine, opener=opener)
            self.assertEqual(opener.requests, [])
            self.assertTrue(part.exists())

    def test_stream_asset_rejects_partial_symlink_before_request(self) -> None:
        full = HDF5_MAGIC + b"data"
        contract = replace(
            EXACT_CONTRACTS[1],
            expected_filename="symlink-resume.h5",
            expected_size_bytes=len(full),
            stable_route="https://data.nasa.gov/symlink-resume.h5",
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            quarantine = root / "quarantine"
            quarantine.mkdir()
            external = root / "external-part"
            external.write_bytes(full[:9])
            try:
                os.symlink(external, quarantine / "symlink-resume.h5.part")
            except OSError as error:
                self.skipTest(f"file symlink unavailable: {type(error).__name__}")
            opener = FakeOpener(FakeResponse(full[9:], status=206))
            with self.assertRaisesRegex(AcquisitionError, "PART_FILE_LINK_NOT_ALLOWED"):
                stream_asset(contract, quarantine, opener=opener)
            self.assertEqual(opener.requests, [])
            self.assertEqual(external.read_bytes(), full[:9])

    def test_stream_asset_rejects_dangling_final_symlink_before_request(self) -> None:
        full = HDF5_MAGIC + b"data"
        contract = replace(
            EXACT_CONTRACTS[1],
            expected_filename="dangling-final.h5",
            expected_size_bytes=len(full),
            stable_route="https://data.nasa.gov/dangling-final.h5",
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            quarantine = root / "quarantine"
            quarantine.mkdir()
            try:
                os.symlink(root / "missing-external", quarantine / contract.expected_filename)
            except OSError as error:
                self.skipTest(f"file symlink unavailable: {type(error).__name__}")
            opener = FakeOpener(FakeResponse(full))
            with self.assertRaisesRegex(
                AcquisitionError,
                "EXISTING_QUARANTINE_ASSET_LINK_NOT_ALLOWED",
            ):
                stream_asset(contract, quarantine, opener=opener)
            self.assertEqual(opener.requests, [])

    def test_stream_asset_finalization_never_replaces_race_created_target(self) -> None:
        full = HDF5_MAGIC + b"data"
        contract = replace(
            EXACT_CONTRACTS[1],
            expected_filename="final-race.h5",
            expected_size_bytes=len(full),
            stable_route="https://data.nasa.gov/final-race.h5",
        )
        response = FakeResponse(full, final_url=contract.stable_route)
        with TemporaryDirectory() as directory:
            quarantine = Path(directory) / "quarantine"
            target = quarantine / contract.expected_filename
            part = quarantine / f"{contract.expected_filename}.part"
            from burnlens import provider_acquisition

            real_rename = provider_acquisition._rename_path_no_overwrite

            def race_then_rename(source: Path, destination: Path) -> None:
                destination.write_bytes(b"race-created")
                real_rename(source, destination)

            with patch(
                "burnlens.provider_acquisition._rename_path_no_overwrite",
                side_effect=race_then_rename,
            ), self.assertRaisesRegex(AcquisitionError, "FINAL_ASSET_RACE_CREATED"):
                stream_asset(contract, quarantine, opener=FakeOpener(response))
            self.assertEqual(target.read_bytes(), b"race-created")
            self.assertEqual(part.read_bytes(), full)

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

    def test_http_status_classification_is_fail_closed(self) -> None:
        for status in (401, 403, 404, 429):
            error = AcquisitionError("DOWNLOAD_HTTP_STATUS_REJECTED", detail=str(status))
            self.assertEqual(classify_transfer_failure(error), "NONRETRYABLE_HTTP_STATUS")
        for status in (408, 500, 503, 599):
            error = AcquisitionError("DOWNLOAD_HTTP_STATUS_REJECTED", detail=str(status))
            self.assertEqual(classify_transfer_failure(error), "RETRYABLE_HTTP_STATUS")
        for status in (301, 400, 409, 600):
            error = AcquisitionError("DOWNLOAD_HTTP_STATUS_REJECTED", detail=str(status))
            self.assertEqual(classify_transfer_failure(error), "NONRETRYABLE_HTTP_STATUS")
        self.assertEqual(
            classify_transfer_failure(AcquisitionError("DOWNLOAD_REQUEST_FAILED")),
            "RETRYABLE_TRANSPORT",
        )
        self.assertEqual(
            classify_transfer_failure(AcquisitionError("DOWNLOAD_EARLY_EOF")),
            "RETRYABLE_TRANSPORT",
        )
        self.assertEqual(
            classify_transfer_failure(AcquisitionError("DOWNLOAD_WRITE_FAILED")),
            "NONRETRYABLE",
        )
        self.assertEqual(
            classify_transfer_failure(AcquisitionError("DOWNLOAD_SIZE_MISMATCH")),
            "NONRETRYABLE",
        )
        self.assertEqual(
            classify_transfer_failure(AcquisitionError("DOWNLOAD_EXCEEDS_EXPECTED_SIZE")),
            "NONRETRYABLE",
        )

    def test_stream_asset_preserves_http_status_for_retry_policy(self) -> None:
        contract = replace(
            EXACT_CONTRACTS[1],
            expected_filename="status.h5",
            expected_size_bytes=9,
            stable_route="https://data.nasa.gov/status.h5",
        )
        error = HTTPError(contract.stable_route, 403, "Forbidden", {}, None)
        with TemporaryDirectory() as directory, self.assertRaises(AcquisitionError) as context:
            stream_asset(contract, Path(directory), opener=SequenceOpener([error]))
        self.assertEqual(context.exception.reason_code, "DOWNLOAD_HTTP_STATUS_REJECTED")
        self.assertEqual(context.exception.detail, "403")

    def test_cdse_retry_uses_fresh_token_for_retryable_http_status(self) -> None:
        payload = HDF5_MAGIC + b"data"
        contract = replace(
            EXACT_CONTRACTS[1],
            expected_filename="retry-http.h5",
            expected_size_bytes=len(payload),
            stable_route="https://download.dataspace.copernicus.eu/retry-http.h5",
        )
        opener = SequenceOpener(
            [
                HTTPError(contract.stable_route, 503, "Unavailable", {}, None),
                FakeResponse(payload, final_url=contract.stable_route),
            ]
        )
        tokens = iter(("token-one", "token-two"))
        requested: list[tuple[str, str]] = []

        def token_request(username: str, password: str) -> str:
            requested.append((username, password))
            return next(tokens)

        with TemporaryDirectory() as directory:
            result = stream_cdse_asset_with_retries(
                contract,
                Path(directory),
                username="user",
                password="secret",
                token_request_fn=token_request,
                opener_factory=lambda: opener,
            )
        self.assertEqual(result["attempt_count"], 2)
        self.assertEqual(len(requested), 2)
        self.assertEqual(
            [request.get_header("Authorization") for request in opener.requests],
            ["Bearer token-one", "Bearer token-two"],
        )

    def test_cdse_retry_does_not_retry_terminal_http_status(self) -> None:
        contract = replace(
            EXACT_CONTRACTS[1],
            expected_filename="terminal.h5",
            expected_size_bytes=9,
            stable_route="https://download.dataspace.copernicus.eu/terminal.h5",
        )
        opener = SequenceOpener(
            [HTTPError(contract.stable_route, 429, "Quota", {}, None)]
        )
        token_calls = 0

        def token_request(username: str, password: str) -> str:
            nonlocal token_calls
            token_calls += 1
            return "token"

        with TemporaryDirectory() as directory, self.assertRaises(AcquisitionError) as context:
            stream_cdse_asset_with_retries(
                contract,
                Path(directory),
                username="user",
                password="secret",
                token_request_fn=token_request,
                opener_factory=lambda: opener,
            )
        self.assertEqual(context.exception.reason_code, "DOWNLOAD_HTTP_STATUS_REJECTED")
        self.assertEqual(context.exception.detail, "429")
        self.assertEqual(token_calls, 1)

    def test_cdse_retry_retries_transport_failure_with_fresh_token(self) -> None:
        payload = HDF5_MAGIC + b"data"
        contract = replace(
            EXACT_CONTRACTS[1],
            expected_filename="retry-transport.h5",
            expected_size_bytes=len(payload),
            stable_route="https://download.dataspace.copernicus.eu/retry-transport.h5",
        )
        opener = SequenceOpener(
            [
                URLError("temporary transport failure"),
                FakeResponse(payload, final_url=contract.stable_route),
            ]
        )
        token_calls = 0

        def token_request(username: str, password: str) -> str:
            nonlocal token_calls
            token_calls += 1
            return f"token-{token_calls}"

        with TemporaryDirectory() as directory:
            result = stream_cdse_asset_with_retries(
                contract,
                Path(directory),
                username="user",
                password="secret",
                token_request_fn=token_request,
                opener_factory=lambda: opener,
            )
        self.assertEqual(result["attempt_count"], 2)
        self.assertEqual(token_calls, 2)

    def test_cdse_retry_treats_only_short_eof_as_retryable_size_failure(self) -> None:
        payload = HDF5_MAGIC + b"data"
        first = payload[: len(HDF5_MAGIC)]
        remainder = payload[len(first) :]
        contract = replace(
            EXACT_CONTRACTS[1],
            expected_filename="retry-short-eof.h5",
            expected_size_bytes=len(payload),
            stable_route="https://download.dataspace.copernicus.eu/retry-short-eof.h5",
        )
        opener = SequenceOpener(
            [
                FakeResponse(first, final_url=contract.stable_route),
                FakeResponse(
                    remainder,
                    status=206,
                    headers={"Content-Range": f"bytes {len(first)}-{len(payload) - 1}/{len(payload)}"},
                    final_url=contract.stable_route,
                ),
            ]
        )
        token_calls = 0

        def token_request(username: str, password: str) -> str:
            nonlocal token_calls
            token_calls += 1
            return f"token-{token_calls}"

        with TemporaryDirectory() as directory:
            result = stream_cdse_asset_with_retries(
                contract,
                Path(directory),
                username="user",
                password="secret",
                token_request_fn=token_request,
                opener_factory=lambda: opener,
            )
        self.assertEqual(result["attempt_count"], 2)
        self.assertEqual(token_calls, 2)
        self.assertEqual(
            [request.get_header("Range") for request in opener.requests],
            [None, f"bytes={len(first)}-"],
        )

    def test_cdse_retry_attempt_limit_is_hard_bounded(self) -> None:
        self.assertEqual(MAX_BOUNDED_TRANSFER_ATTEMPTS, 5)
        with TemporaryDirectory() as directory, self.assertRaisesRegex(
            AcquisitionError, "TRANSFER_ATTEMPT_LIMIT_INVALID"
        ):
            stream_cdse_asset_with_retries(
                EXACT_CONTRACTS[1],
                Path(directory),
                username="user",
                password="secret",
                max_attempts=6,
            )

    def test_cdse_retry_rejects_completed_prior_invocation_asset(self) -> None:
        payload = HDF5_MAGIC + b"data"
        contract = replace(
            EXACT_CONTRACTS[1],
            expected_filename="already-complete.h5",
            expected_size_bytes=len(payload),
            stable_route="https://download.dataspace.copernicus.eu/already-complete.h5",
        )
        token_calls = 0

        def token_request(username: str, password: str) -> str:
            nonlocal token_calls
            token_calls += 1
            return "token"

        with TemporaryDirectory() as directory:
            quarantine = Path(directory)
            (quarantine / contract.expected_filename).write_bytes(payload)
            with self.assertRaisesRegex(
                AcquisitionError, "PRIOR_COMPLETED_QUARANTINE_ASSET_NOT_ALLOWED"
            ):
                stream_cdse_asset_with_retries(
                    contract,
                    quarantine,
                    username="user",
                    password="secret",
                    token_request_fn=token_request,
                )
        self.assertEqual(token_calls, 0)

    def test_no_overwrite_promotion_rejects_race_created_destination(self) -> None:
        payload = HDF5_MAGIC + b"data"
        contract = replace(
            EXACT_CONTRACTS[1],
            expected_filename="asset.h5",
            expected_size_bytes=len(payload),
            package_id="test-no-overwrite-package",
            provider_md5=None,
            provider_blake3=None,
            native_pair_token=None,
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            quarantine = root / "quarantine"
            quarantine.mkdir()
            (quarantine / contract.expected_filename).write_bytes(payload)
            destination = root / "raw" / contract.package_id

            from burnlens import provider_acquisition

            real_rename = provider_acquisition._rename_path_no_overwrite

            def race_then_rename(source: Path, target: Path) -> None:
                target.mkdir(parents=True)
                real_rename(source, target)

            with patch(
                "burnlens.provider_acquisition._rename_path_no_overwrite",
                side_effect=race_then_rename,
            ), self.assertRaises(FileExistsError):
                promote_quarantine_no_overwrite(
                    quarantine,
                    destination,
                    (contract,),
                    generated_at_utc="2026-07-21T16:00:00Z",
                    run_id="BL-TEST-NO-OVERWRITE-RACE",
                    synthetic_fixture=True,
                    contract_validator=lambda contracts: [],
                    contract_version="test-contract-v0.1.0",
                )
            self.assertTrue(destination.is_dir())
            self.assertTrue(quarantine.is_dir())
            self.assertTrue((quarantine / contract.expected_filename).is_file())
            self.assertFalse((quarantine / ".burnlens-registration.json").exists())

    def test_no_overwrite_promotion_moves_complete_package_and_manifest(self) -> None:
        payload = HDF5_MAGIC + b"data"
        contract = replace(
            EXACT_CONTRACTS[1],
            expected_filename="asset.h5",
            expected_size_bytes=len(payload),
            package_id="test-no-overwrite-package",
            provider_md5=None,
            provider_blake3=None,
            native_pair_token=None,
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            quarantine = root / "quarantine"
            quarantine.mkdir()
            (quarantine / contract.expected_filename).write_bytes(payload)
            destination = root / "raw" / contract.package_id
            registration = promote_quarantine_no_overwrite(
                quarantine,
                destination,
                (contract,),
                generated_at_utc="2026-07-21T16:00:00Z",
                run_id="BL-TEST-NO-OVERWRITE-SUCCESS",
                synthetic_fixture=True,
                contract_validator=lambda contracts: [],
                contract_version="test-contract-v0.1.0",
            )
            self.assertFalse(quarantine.exists())
            self.assertEqual((destination / contract.expected_filename).read_bytes(), payload)
            self.assertEqual(
                json.loads(
                    (destination / ".burnlens-registration.json").read_text(encoding="utf-8")
                ),
                registration,
            )

    def test_linux_no_replace_rename_uses_encoded_paths_and_flag(self) -> None:
        from burnlens import provider_acquisition

        observed: list[tuple[object, ...]] = []

        class FakeRenameAt2:
            argtypes = None
            restype = None

            def __call__(self, *args):
                observed.append(args)
                return 0

        class FakeLibc:
            renameat2 = FakeRenameAt2()

        source = Path("source-é")
        destination = Path("destination-é")
        with patch.object(provider_acquisition.os, "name", "posix"), patch.object(
            provider_acquisition.sys, "platform", "linux"
        ), patch.object(provider_acquisition.ctypes, "CDLL", return_value=FakeLibc()):
            provider_acquisition._rename_path_no_overwrite(source, destination)
        self.assertEqual(len(observed), 1)
        self.assertEqual(observed[0][0], -100)
        self.assertEqual(observed[0][1], os.fsencode(source))
        self.assertEqual(observed[0][2], -100)
        self.assertEqual(observed[0][3], os.fsencode(destination))
        self.assertEqual(observed[0][4], 1)

    def test_no_replace_rename_fails_closed_on_unsupported_platform(self) -> None:
        from burnlens import provider_acquisition

        source = Path("source")
        destination = Path("destination")
        with patch.object(provider_acquisition.os, "name", "posix"), patch.object(
            provider_acquisition.sys, "platform", "freebsd"
        ), self.assertRaises(OSError) as context:
            provider_acquisition._rename_path_no_overwrite(source, destination)
        self.assertEqual(context.exception.errno, errno.ENOTSUP)

    def test_private_state_is_ignored_untracked_file_fsynced_and_no_overwrite(self) -> None:
        with TemporaryDirectory() as directory:
            repository = Path(directory)
            subprocess.run(["git", "init", "--quiet", str(repository)], check=True)
            (repository / ".gitignore").write_text("private/\n", encoding="utf-8")
            state_path = repository / "private" / "state.json"
            expected = b'{\n  "decision": "PASS"\n}\n'
            real_fsync = os.fsync
            with patch(
                "burnlens.provider_acquisition.os.fsync", wraps=real_fsync
            ) as fsync:
                write_private_state(
                    state_path,
                    {"decision": "PASS"},
                    repo_root=repository,
                )
            self.assertEqual(state_path.read_bytes(), expected)
            self.assertEqual(state_path.stat().st_nlink, 1)
            self.assertGreaterEqual(fsync.call_count, 1)
            with self.assertRaisesRegex(AcquisitionError, "PRIVATE_STATE_OVERWRITE_REFUSED"):
                write_private_state(
                    state_path,
                    {"decision": "CHANGED"},
                    repo_root=repository,
                )
            self.assertEqual(state_path.read_bytes(), expected)

    def test_private_state_rejects_repo_local_nonignored_or_tracked_path(self) -> None:
        with TemporaryDirectory() as directory:
            repository = Path(directory)
            subprocess.run(["git", "init", "--quiet", str(repository)], check=True)
            (repository / ".gitignore").write_text("private/\n", encoding="utf-8")
            with self.assertRaisesRegex(AcquisitionError, "PRIVATE_STATE_NOT_IGNORED"):
                write_private_state(
                    repository / "public" / "state.json",
                    {},
                    repo_root=repository,
                )

            tracked_path = repository / "private" / "tracked.json"
            tracked_path.parent.mkdir()
            tracked_path.write_text("tracked\n", encoding="utf-8")
            subprocess.run(
                ["git", "-C", str(repository), "add", "--force", "--", "private/tracked.json"],
                check=True,
            )
            tracked_path.unlink()
            with self.assertRaisesRegex(AcquisitionError, "PRIVATE_STATE_TRACKED"):
                write_private_state(tracked_path, {}, repo_root=repository)

    def test_private_state_rejects_repo_link_that_escapes_to_outside_target(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repository = root / "repository"
            outside = root / "outside"
            repository.mkdir()
            outside.mkdir()
            subprocess.run(["git", "init", "--quiet", str(repository)], check=True)
            (repository / ".gitignore").write_text("private/\n", encoding="utf-8")
            link = repository / "private"
            try:
                os.symlink(outside, link, target_is_directory=True)
            except OSError as error:
                self.skipTest(f"directory symlink unavailable: {type(error).__name__}")

            with self.assertRaisesRegex(AcquisitionError, "PRIVATE_STATE_LINK_NOT_ALLOWED"):
                write_private_state(link / "state.json", {"status": "SAFE"})
            self.assertFalse((outside / "state.json").exists())

    def test_private_state_rejects_repo_link_to_ignored_directory_within_repo(self) -> None:
        with TemporaryDirectory() as directory:
            repository = Path(directory) / "repository"
            repository.mkdir()
            actual = repository / "actual"
            actual.mkdir()
            subprocess.run(["git", "init", "--quiet", str(repository)], check=True)
            (repository / ".gitignore").write_text(
                "actual/\nprivate/\n",
                encoding="utf-8",
            )
            link = repository / "private"
            try:
                os.symlink(actual, link, target_is_directory=True)
            except OSError as error:
                self.skipTest(f"directory symlink unavailable: {type(error).__name__}")

            with self.assertRaisesRegex(AcquisitionError, "PRIVATE_STATE_LINK_NOT_ALLOWED"):
                write_private_state(link / "state.json", {"status": "SAFE"})
            self.assertFalse((actual / "state.json").exists())

    def test_private_state_outside_git_preserves_isolated_test_compatibility(self) -> None:
        with TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            write_private_state(state_path, {"status": "SAFE"})
            self.assertEqual(json.loads(state_path.read_text(encoding="utf-8")), {"status": "SAFE"})

    def test_private_state_rejects_multilink_without_manifest_exception(self) -> None:
        with TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            original_lstat = Path.lstat

            def two_link_lstat(path: Path):
                observed = original_lstat(path)
                values = list(observed)
                values[3] = 2
                return os.stat_result(values)

            with patch(
                "burnlens.provider_acquisition.Path.lstat",
                autospec=True,
                side_effect=two_link_lstat,
            ), self.assertRaisesRegex(AcquisitionError, "PRIVATE_STATE_MULTILINK_NOT_ALLOWED"):
                write_private_state(state_path, {"status": "SAFE"})
            self.assertFalse(state_path.exists())

    def test_private_state_removes_failed_readback(self) -> None:
        with TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            with patch(
                "burnlens.provider_acquisition._read_private_state_from_handle",
                return_value=b"changed",
            ), self.assertRaisesRegex(AcquisitionError, "PRIVATE_STATE_READBACK_MISMATCH"):
                write_private_state(state_path, {"status": "SAFE"})
            self.assertFalse(state_path.exists())


if __name__ == "__main__":
    unittest.main()
