from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from PIL import Image

from burnlens.access_integrity import AssetSpec, HDF5_MAGIC, build_report, inspect_payload, render_html, render_png


SPEC = AssetSpec(
    role="test",
    source_record_id="SOURCE-TEST",
    collection="TEST.001",
    native_id="TEST.NATIVE",
    expected_filename="test.nc",
    stable_route="https://example.invalid/test.nc",
    minimum_size_bytes=16,
)


class AccessIntegrityTests(unittest.TestCase):
    def test_rejects_login_html_even_with_success_status_and_data_suffix(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "test.nc"
            path.write_text("<!doctype html><html><title>Earthdata Login</title></html>", encoding="utf-8")

            result = inspect_payload(path, SPEC, 200)

        self.assertFalse(result["accepted_as_source_asset"])
        self.assertEqual(result["observed_media_hint"], "html")
        self.assertEqual(result["response_title"], "Earthdata Login")
        self.assertIsNone(result["sha256"])
        self.assertIn("HTML_LOGIN_OR_ERROR_RESPONSE", result["reason_codes"])

    def test_accepts_hdf5_signature_and_minimum_size(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "test.nc"
            path.write_bytes(HDF5_MAGIC + b"\0" * 8)

            result = inspect_payload(path, SPEC, 200)

        self.assertTrue(result["accepted_as_source_asset"])
        self.assertEqual(result["observed_magic_hex"], HDF5_MAGIC.hex())
        self.assertEqual(len(result["sha256"]), 64)
        self.assertEqual(result["reason_codes"], ["SOURCE_ASSET_ACCEPTED"])

    def test_rejects_signature_only_payload_below_minimum(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "test.nc"
            path.write_bytes(HDF5_MAGIC)

            result = inspect_payload(path, SPEC, 200)

        self.assertFalse(result["accepted_as_source_asset"])
        self.assertIn("PAYLOAD_BELOW_EXPECTED_MINIMUM", result["reason_codes"])

    def test_report_is_deterministic_for_fixed_inputs(self) -> None:
        observation = {
            "accepted_as_source_asset": False,
            "observed_bytes": 100,
            "role": "test",
            "response_title": "Earthdata Login",
            "reason_codes": ["HTML_LOGIN_OR_ERROR_RESPONSE"],
        }
        first = build_report([observation], generated_at_utc="2026-07-14T00:30:00Z", run_id="TEST-RUN")
        second = build_report([observation], generated_at_utc="2026-07-14T00:30:00Z", run_id="TEST-RUN")
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))
        self.assertEqual(first["retention"]["provider_source_asset_count"], 0)
        self.assertEqual(first["decision"], "BLOCKED_OWNER_CREDENTIAL")

    def test_non_login_failure_is_not_mislabeled_as_credential_block(self) -> None:
        observation = {
            "accepted_as_source_asset": False,
            "observed_bytes": 8,
            "role": "test",
            "response_title": None,
            "reason_codes": ["PAYLOAD_BELOW_EXPECTED_MINIMUM"],
        }
        report = build_report([observation], generated_at_utc="2026-07-14T00:30:00Z", run_id="TEST-RUN")
        self.assertEqual(report["decision"], "BLOCKED_PAYLOAD_INTEGRITY")
        self.assertIn("failed identity or integrity", report["decision_detail"])

    def test_ready_report_renders_accepted_state(self) -> None:
        observation = {
            "role": "test",
            "source_record_id": "SOURCE-TEST",
            "collection": "TEST.001",
            "native_id": "TEST.NATIVE",
            "expected_filename": "test.nc",
            "stable_route": "https://example.invalid/test.nc",
            "http_status": 200,
            "observed_bytes": 16,
            "observed_magic_hex": HDF5_MAGIC.hex(),
            "observed_media_hint": "hdf5",
            "response_title": None,
            "expected_signature": "HDF5/NetCDF-4",
            "minimum_size_bytes": 16,
            "accepted_as_source_asset": True,
            "sha256": "0" * 64,
            "reason_codes": ["SOURCE_ASSET_ACCEPTED"],
        }
        report = build_report([observation], generated_at_utc="2026-07-14T00:30:00Z", run_id="TEST-RUN")
        html = render_html(report)
        self.assertEqual(report["decision"], "READY_FOR_FORMAT_INSPECTION")
        self.assertIn("Provider bytes passed precheck", html)
        self.assertIn("Payloads accepted", html)

    def test_rendered_report_has_warning_and_no_operational_claim(self) -> None:
        observation = {
            "role": "test",
            "source_record_id": "SOURCE-TEST",
            "collection": "TEST.001",
            "native_id": "TEST.NATIVE",
            "expected_filename": "test.nc",
            "stable_route": "https://example.invalid/test.nc",
            "http_status": 200,
            "observed_bytes": 100,
            "observed_magic_hex": "3c21646f63747970",
            "observed_media_hint": "html",
            "response_title": "Earthdata Login",
            "expected_signature": "HDF5/NetCDF-4",
            "minimum_size_bytes": 16,
            "accepted_as_source_asset": False,
            "sha256": None,
            "reason_codes": ["HTML_LOGIN_OR_ERROR_RESPONSE"],
        }
        report = build_report([observation], generated_at_utc="2026-07-14T00:30:00Z", run_id="TEST-RUN")
        html = render_html(report)
        self.assertIn("Not official wildfire information", html)
        self.assertIn("Provider bytes did not pass", html)
        self.assertIn("No mask, QA field, geolocation array", html)
        self.assertNotIn("operational wildfire", html.lower())

    def test_visual_evidence_render_has_expected_canvas(self) -> None:
        observation = {
            "role": "test",
            "source_record_id": "SOURCE-TEST",
            "collection": "TEST.001",
            "native_id": "TEST.NATIVE",
            "expected_filename": "test.nc",
            "stable_route": "https://example.invalid/test.nc",
            "http_status": 200,
            "observed_bytes": 100,
            "observed_magic_hex": "3c21646f63747970",
            "observed_media_hint": "html",
            "response_title": "Earthdata Login",
            "expected_signature": "HDF5/NetCDF-4",
            "minimum_size_bytes": 16,
            "accepted_as_source_asset": False,
            "sha256": None,
            "reason_codes": ["HTML_LOGIN_OR_ERROR_RESPONSE"],
        }
        report = build_report([observation], generated_at_utc="2026-07-14T00:30:00Z", run_id="TEST-RUN")
        with TemporaryDirectory() as directory:
            path = Path(directory) / "report.png"
            render_png(report, path)
            with Image.open(path) as image:
                self.assertEqual(image.size, (1600, 1200))
                self.assertEqual(image.mode, "RGB")


if __name__ == "__main__":
    unittest.main()
