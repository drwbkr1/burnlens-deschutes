from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import burnlens
from burnlens.current_reference_inventory import (
    DECISION,
    EXPECTED_PRODUCTS,
    CurrentReferenceInventoryError,
    build_current_reference_inventory,
    inventory_request_url,
    normalize_inventory,
    write_current_reference_inventory,
)


def response_bytes(products: tuple[dict[str, object], ...] = EXPECTED_PRODUCTS) -> bytes:
    features = []
    for index, product in enumerate(reversed(products)):
        features.append(
            {
                "type": "Feature",
                "id": f"synthetic-{index}",
                "geometry": None,
                "properties": {
                    "id": product["catalog_id"],
                    "map_id": product["map_id"],
                    "map_prog": product["program"],
                    "incid_name": product["incident_name"],
                    "event_id": product["event_id"],
                    "ig_date": f"{product['ignition_date']}Z",
                    "burnbndac": product["boundary_acres"],
                    "nonstandard": product["nonstandard"],
                },
            }
        )
    return json.dumps(
        {"type": "FeatureCollection", "features": features},
        separators=(",", ":"),
    ).encode()


class CurrentReferenceInventoryTests(unittest.TestCase):
    def test_version_and_request_are_exact(self) -> None:
        self.assertEqual(burnlens.__version__, "0.38.0")
        attributes = Path(".gitattributes").read_text(encoding="utf-8")
        self.assertIn("samples/reference/phase-two/*.json text eol=lf", attributes)
        self.assertIn("samples/reference/phase-two/*.html text eol=lf", attributes)
        url = inventory_request_url()
        self.assertIn("mtbs%3Afire_polygons", url)
        self.assertIn("propertyName=id%2Cmap_id%2Cmap_prog", url)
        for event_id in (
            "OR4364712147820240625",
            "OR4375212142520170829",
            "OR4383912111420180907",
        ):
            self.assertIn(event_id, url)

    def test_normalization_is_order_independent_and_exact(self) -> None:
        products = normalize_inventory(response_bytes())
        self.assertEqual(len(products), 7)
        self.assertEqual(
            [(item["event_id"], item["program"]) for item in products],
            sorted((item["event_id"], item["program"]) for item in EXPECTED_PRODUCTS),
        )
        self.assertTrue(any(item["nonstandard"] for item in products))
        self.assertEqual(
            next(
                item["event_group_id"]
                for item in products
                if item["event_id"] == "OR4364712147820240625"
            ),
            "event-darlene3-or-2024",
        )

    def test_catalog_drift_fails_closed(self) -> None:
        drifted = [dict(item) for item in EXPECTED_PRODUCTS]
        drifted[0]["map_id"] = 999
        with self.assertRaisesRegex(CurrentReferenceInventoryError, "differ"):
            normalize_inventory(response_bytes(tuple(drifted)))

    def test_geometry_or_unexpected_program_fails_closed(self) -> None:
        payload = json.loads(response_bytes())
        payload["features"][0]["geometry"] = {"type": "Point", "coordinates": [0, 0]}
        with self.assertRaisesRegex(CurrentReferenceInventoryError, "property-only"):
            normalize_inventory(json.dumps(payload).encode())
        payload = json.loads(response_bytes())
        payload["features"][0]["properties"]["map_prog"] = "UNKNOWN"
        with self.assertRaisesRegex(CurrentReferenceInventoryError, "unexpected program"):
            normalize_inventory(json.dumps(payload).encode())

    def test_report_defers_all_promotion_and_model_claims(self) -> None:
        report = build_current_reference_inventory(
            response_bytes(),
            generated_at_utc="2026-07-17T00:30:00Z",
            run_id="BL-2026-07-17-current-reference-inventory-r001",
            git_source_commit="a" * 40,
        )
        self.assertEqual(report["decision"], DECISION)
        self.assertEqual(report["inventory"]["program_counts"], {"BAER": 2, "MTBS": 2, "RAVG": 3})
        self.assertTrue(report["inventory"]["all_events_have_cross_program_reference"])
        self.assertEqual(report["provenance"]["dataset_version"], None)
        self.assertEqual(report["provenance"]["model_version"], None)
        self.assertTrue(report["claim_boundaries"]["inventory_only"])
        self.assertFalse(report["claim_boundaries"]["labels_promoted_by_this_run"])
        self.assertFalse(report["claim_boundaries"]["scientific_validation_claimed"])

    def test_three_rendered_outputs_are_created(self) -> None:
        report = build_current_reference_inventory(
            response_bytes(),
            generated_at_utc="2026-07-17T00:30:00Z",
            run_id="BL-2026-07-17-current-reference-inventory-r001",
            git_source_commit="a" * 40,
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            json_path = root / "report.json"
            html_path = root / "report.html"
            png_path = root / "report.png"
            write_current_reference_inventory(
                report,
                json_path=json_path,
                html_path=html_path,
                png_path=png_path,
            )
            self.assertEqual(json.loads(json_path.read_text())["decision"], DECISION)
            self.assertIn("Cross-program reference exists", html_path.read_text())
            self.assertGreater(png_path.stat().st_size, 20_000)

    def test_cli_failure_is_secret_free(self) -> None:
        from burnlens import capture_current_reference_inventory as cli

        with patch.object(
            cli,
            "fetch_inventory_response",
            side_effect=CurrentReferenceInventoryError("endpoint unavailable"),
        ), patch(
            "sys.argv",
            [
                "burnlens-capture-current-reference-inventory",
                "--generated-at-utc",
                "2026-07-17T00:30:00Z",
                "--run-id",
                "run",
                "--git-source-commit",
                "a" * 40,
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
