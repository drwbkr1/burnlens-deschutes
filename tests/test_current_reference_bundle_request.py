import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from burnlens.current_reference_bundle_request import (
    CAUTION_DETAILS,
    DECISION,
    EXPECTED_ASSESSMENT_FIELDS,
    MAX_METADATA_RESPONSE_BYTES,
    MAPPING_IDS,
    SOFTWARE_VERSION,
    CurrentReferenceBundleRequestError,
    build_bundle_request_evidence,
    fetch_full_inventory_response,
    full_inventory_request_url,
    normalize_assessment_metadata,
    request_payload,
    write_bundle_request_evidence,
)
from burnlens.current_reference_inventory import EXPECTED_PRODUCTS


ROOT = Path(__file__).resolve().parents[1]


def metadata_response() -> bytes:
    by_id = {int(item["catalog_id"]): item for item in EXPECTED_PRODUCTS}
    features = []
    for catalog_id, assessment in EXPECTED_ASSESSMENT_FIELDS.items():
        base = by_id[catalog_id]
        properties = {
            "id": catalog_id,
            "map_id": base["map_id"],
            "map_prog": base["program"],
            "incid_name": base["incident_name"],
            "event_id": base["event_id"],
            "ig_date": f"{base['ignition_date']}Z",
            "burnbndac": base["boundary_acres"],
            "nonstandard": base["nonstandard"],
            "asmt_type": assessment["assessment_type"],
            "post_id": assessment["post_id"],
            "postfire_date": (
                f"{assessment['postfire_date']}Z" if assessment["postfire_date"] else None
            ),
            "model": assessment["model"],
            "comment": assessment["comment"],
        }
        features.append(
            {
                "type": "Feature",
                "id": f"fire_polygons.{catalog_id}",
                "geometry": None,
                "properties": properties,
            }
        )
    return json.dumps({"type": "FeatureCollection", "features": features}).encode()


class CurrentReferenceBundleRequestTests(unittest.TestCase):
    def test_version_request_and_checkout_contract_are_exact(self) -> None:
        self.assertEqual(SOFTWARE_VERSION, "0.22.0")
        self.assertEqual(len(MAPPING_IDS), 6)
        self.assertEqual(len(request_payload()["mapping_products"]), 18)
        url = full_inventory_request_url()
        self.assertIn("propertyName=", url)
        self.assertIn("asmt_type", url)
        self.assertNotIn("geom", url)
        attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("samples/reference/phase-two/*.json text eol=lf", attributes)
        self.assertIn("samples/reference/phase-two/*.html text eol=lf", attributes)

    def test_request_report_preserves_pending_delivery_and_cautions(self) -> None:
        report = build_bundle_request_evidence(
            metadata_response(),
            b'{"success":true}',
            generated_at_utc="2026-07-17T02:00:00Z",
            run_id="BL-2026-07-17-current-reference-bundle-request-r001",
            git_source_commit="a" * 40,
        )
        self.assertEqual(report["decision"], DECISION)
        self.assertTrue(report["request"]["accepted"])
        self.assertEqual(report["assessment_metadata"]["product_count"], 7)
        self.assertEqual(report["assessment_metadata"]["caution_count"], 4)
        self.assertEqual(
            {
                item["caution"]["code"]
                for item in report["assessment_metadata"]["products"]
                if item["caution"]
            },
            {item["code"] for item in CAUTION_DETAILS.values()},
        )
        self.assertTrue(report["delivery_state"]["delivery_pending"])
        self.assertEqual(report["delivery_state"]["bundle_archives_received"], 0)
        self.assertEqual(report["label_state"]["labels_promoted_by_this_run"], 0)
        self.assertEqual(report["source"]["recipient"], "WITHHELD_PRIVATE")
        self.assertFalse(report["claim_boundaries"]["request_acceptance_is_delivery"])

    def test_metadata_and_queue_drift_fail_closed(self) -> None:
        payload = json.loads(metadata_response())
        payload["features"][0]["properties"]["comment"] = "changed"
        with self.assertRaisesRegex(CurrentReferenceBundleRequestError, "drifted"):
            build_bundle_request_evidence(
                json.dumps(payload).encode(),
                b'{"success":true}',
                generated_at_utc="2026-07-17T02:00:00Z",
                run_id="run",
                git_source_commit="a" * 40,
            )
        with self.assertRaisesRegex(CurrentReferenceBundleRequestError, "not accepted"):
            build_bundle_request_evidence(
                metadata_response(),
                b'{"success":false}',
                generated_at_utc="2026-07-17T02:00:00Z",
                run_id="run",
                git_source_commit="a" * 40,
            )

    def test_duplicate_metadata_identity_fails_closed(self) -> None:
        payload = json.loads(metadata_response())
        payload["features"].append(payload["features"][0])
        with self.assertRaisesRegex(
            CurrentReferenceBundleRequestError,
            "duplicate full-metadata catalog ID",
        ):
            normalize_assessment_metadata(json.dumps(payload).encode())

    def test_oversized_metadata_response_fails_closed(self) -> None:
        response = MagicMock()
        response.status = 200
        response.headers.get_content_type.return_value = "application/json"
        response.read.return_value = b"x" * (MAX_METADATA_RESPONSE_BYTES + 1)
        context = MagicMock()
        context.__enter__.return_value = response
        with patch(
            "burnlens.current_reference_bundle_request.urlopen",
            return_value=context,
        ), self.assertRaisesRegex(
            CurrentReferenceBundleRequestError,
            "exceeds bounded size",
        ):
            fetch_full_inventory_response()
        response.read.assert_called_once_with(MAX_METADATA_RESPONSE_BYTES + 1)

    def test_rendered_outputs_are_created_without_private_recipient(self) -> None:
        report = build_bundle_request_evidence(
            metadata_response(),
            b'{"success":true}',
            generated_at_utc="2026-07-17T02:00:00Z",
            run_id="BL-2026-07-17-current-reference-bundle-request-r001",
            git_source_commit="a" * 40,
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            json_path = root / "report.json"
            html_path = root / "report.html"
            png_path = root / "report.png"
            write_bundle_request_evidence(
                report,
                json_path=json_path,
                html_path=html_path,
                png_path=png_path,
            )
            self.assertEqual(json.loads(json_path.read_text())["decision"], DECISION)
            self.assertIn("Delivery remains pending", html_path.read_text())
            self.assertNotIn("gmail", json_path.read_text().lower())
            self.assertNotIn("gmail", html_path.read_text().lower())
            self.assertGreater(png_path.stat().st_size, 20_000)

    def test_cli_failure_is_secret_free(self) -> None:
        from burnlens import capture_current_reference_bundle_request as cli

        with patch.object(
            cli,
            "fetch_full_inventory_response",
            side_effect=CurrentReferenceBundleRequestError("endpoint unavailable"),
        ), patch(
            "sys.argv",
            [
                "burnlens-capture-current-reference-bundle-request",
                "--generated-at-utc",
                "2026-07-17T02:00:00Z",
                "--run-id",
                "run",
                "--git-source-commit",
                "a" * 40,
                "--input-queue-response",
                "queue.json",
                "--output-json",
                "x.json",
                "--output-html",
                "x.html",
                "--output-png",
                "x.png",
            ],
        ):
            self.assertEqual(cli.main(), 2)


if __name__ == "__main__":
    unittest.main()
