from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import burnlens
from burnlens.official_source_scout import (
    DECISION,
    SOURCE_ID,
    OfficialSourceScoutError,
    _classify_asset_probe,
    _score_candidate,
    build_official_source_scout,
    finalize_source_capture,
    validate_source_capture,
    write_official_source_scout,
)


def candidate(
    fire_id: str,
    name: str,
    *,
    rank: int,
    year: int,
    programs: tuple[str, ...],
    distance: float,
) -> dict[str, object]:
    products = [
        {
            "catalog_id": index + 1,
            "map_id": 1000 + index,
            "program": program,
            "incident_name": name,
            "boundary_acres": 4200,
            "nonstandard": False,
        }
        for index, program in enumerate(programs)
    ]
    item: dict[str, object] = {
        "fire_id": fire_id,
        "fire_name": name,
        "ignition_date": f"{year}-08-01",
        "year": year,
        "latitude": 44.2,
        "longitude": -121.7,
        "acres": 4200.0,
        "occurrence_map_id": 1,
        "occurrence_program": "MTBS",
        "pre_image_id": "pre",
        "post_image_id": "post",
        "fire_type": "Wildfire",
        "assessment_type": "Extended",
        "products": products,
        "programs": list(programs),
        "minimum_current_event_distance_km": distance,
        "already_in_pending_seven_bundle_request": False,
        "known_context": None,
    }
    item["scores"] = _score_candidate(item, landsat_matched=12)
    item["landsat_burned_area"] = {
        "fire_id": fire_id,
        "point_window_only_not_full_boundary_coverage": True,
        "number_matched": 12,
        "number_returned": 10,
        "retained_items": [],
        "request_url": "https://landsatlook.usgs.gov/stac-server/search",
        "response_sha256": "a" * 64,
    }
    item["rank"] = rank
    return item


def source_capture() -> dict[str, object]:
    candidates = [
        candidate(
            "OR4435412173920070830",
            "GW FIRE",
            rank=1,
            year=2007,
            programs=("BAER", "MTBS", "RAVG"),
            distance=60.0,
        ),
        candidate(
            "OR4417812169920120909",
            "POLE CREEK",
            rank=2,
            year=2012,
            programs=("BAER", "MTBS"),
            distance=40.0,
        ),
    ]
    source = {
        "source_id": SOURCE_ID,
        "source_schema_version": "0.1.0",
        "captured_at_utc": "2026-07-17T16:30:00Z",
        "run_id": "BL-2026-07-17-official-source-scout-r001",
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 425,
        "parent_bundle_issue": 416,
        "git_source_commit": "a" * 40,
        "software_version": "0.23.0",
        "capture_scope": "metadata only",
        "source_response_evidence": {
            "one": {"response_sha256": "b" * 64},
            "two": {"response_sha256": "c" * 64},
        },
        "population": {
            "search_envelope_wgs84": [-122.2, 43.25, -120.75, 44.75],
            "county_geoid": "41017",
            "deschutes_mtbs_fire_count": 23,
            "portal_product_count": 37,
            "new_candidate_count": 20,
            "pending_bundle_event_ids": [
                "OR4364712147820240625",
                "OR4375212142520170829",
                "OR4383912111420180907",
            ],
        },
        "source_classes": [
            {
                "source_class": f"Source {index}",
                "live_identity": f"Identity {index}",
                "resolution_or_scale": "30 m",
                "temporal_relationship": "event-relative",
                "role": "reference evidence",
                "label_truth_status": "not truth",
                "terms_status": "resolved for metadata",
                "access_route": "https://example.usgs.gov/source",
            }
            for index in range(1, 8)
        ],
        "candidates": candidates,
        "landsat_checks": [item["landsat_burned_area"] for item in candidates],
        "capture_sha256": None,
    }
    return finalize_source_capture(source)


class OfficialSourceScoutTests(unittest.TestCase):
    def test_current_version_and_cli_are_registered(self) -> None:
        self.assertEqual(burnlens.__version__, "0.40.0")
        pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('version = "0.40.0"', pyproject)
        self.assertIn("burnlens-capture-official-source-scout", pyproject)
        self.assertIn("burnlens-acquire-green-ridge-background-optical", pyproject)
        self.assertIn("burnlens-inspect-green-ridge-background-evidence", pyproject)
        self.assertIn("burnlens-build-green-ridge-region-proposal", pyproject)

    def test_scoring_rewards_cross_program_landsat_and_diversity(self) -> None:
        strong = candidate(
            "OR4435412173920070830",
            "GW FIRE",
            rank=1,
            year=2007,
            programs=("BAER", "MTBS", "RAVG"),
            distance=60.0,
        )
        weak = candidate(
            "OR4395012085820070706",
            "MILLICAN EAST",
            rank=2,
            year=2014,
            programs=("MTBS",),
            distance=10.0,
        )
        strong_score = _score_candidate(strong, landsat_matched=8)
        weak_score = _score_candidate(weak, landsat_matched=0)
        self.assertGreater(strong_score["overall"], weak_score["overall"])
        self.assertEqual(strong_score["evidence_value"], 5)
        self.assertEqual(weak_score["owner_review_usefulness"], 1)

    def test_asset_probe_classifies_eros_login_without_credentials(self) -> None:
        self.assertEqual(
            _classify_asset_probe(
                final_url="https://ers.cr.usgs.gov/login?redirect=redacted",
                content_type="text/html",
                payload_prefix=b"<title>Login - EROS Registration System</title>",
            ),
            "AUTHENTICATION_REQUIRED",
        )
        self.assertEqual(
            _classify_asset_probe(
                final_url="https://landsatlook.usgs.gov/metadata.json",
                content_type="application/json",
                payload_prefix=b"{}",
            ),
            "PUBLIC_METADATA_ASSET_AVAILABLE",
        )

    def test_capture_hash_and_pending_queue_boundary_fail_closed(self) -> None:
        source = source_capture()
        validate_source_capture(source)
        source["candidates"][0]["already_in_pending_seven_bundle_request"] = True
        with self.assertRaisesRegex(OfficialSourceScoutError, "hash"):
            validate_source_capture(source)
        source = source_capture()
        source["candidates"][0]["already_in_pending_seven_bundle_request"] = True
        source = finalize_source_capture(source)
        with self.assertRaisesRegex(OfficialSourceScoutError, "duplicates"):
            validate_source_capture(source)

    def test_report_preserves_owner_review_and_no_label_claims(self) -> None:
        report = build_official_source_scout(source_capture())
        self.assertEqual(report["decision"], DECISION)
        self.assertEqual(report["findings"]["source_class_count"], 7)
        self.assertEqual(report["findings"]["top_candidates"][0]["fire_name"], "GW FIRE")
        self.assertFalse(report["queue_boundary"]["accepted_request_duplicated"])
        self.assertTrue(report["claim_boundaries"]["metadata_reconnaissance_only"])
        self.assertFalse(report["claim_boundaries"]["labels_promoted"])
        self.assertIsNone(report["dataset_version"])
        self.assertIn("yes/no/uncertain", report["owner_review_consequence"]["workflow"])

    def test_four_outputs_are_deterministic_and_rendered(self) -> None:
        source = source_capture()
        report = build_official_source_scout(source)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "first"
            second = root / "second"
            for output in (first, second):
                write_official_source_scout(
                    source,
                    report,
                    source_json_path=output / "source.json",
                    report_json_path=output / "report.json",
                    html_path=output / "report.html",
                    png_path=output / "report.png",
                )
            for name in ("source.json", "report.json", "report.html", "report.png"):
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())
            self.assertEqual(json.loads((first / "report.json").read_text())["decision"], DECISION)
            self.assertIn("Ranked new candidate fires", (first / "report.html").read_text())
            self.assertGreater((first / "report.png").stat().st_size, 20_000)

    def test_cli_failure_is_secret_free(self) -> None:
        from burnlens import capture_official_source_scout as cli

        with patch.object(
            cli,
            "capture_live_source_scout",
            side_effect=OfficialSourceScoutError("endpoint unavailable"),
        ), patch(
            "sys.argv",
            [
                "burnlens-capture-official-source-scout",
                "--captured-at-utc",
                "2026-07-17T16:30:00Z",
                "--run-id",
                "run",
                "--git-source-commit",
                "a" * 40,
                "--output-source-json",
                "source.json",
                "--output-report-json",
                "report.json",
                "--output-html",
                "report.html",
                "--output-png",
                "report.png",
            ],
        ):
            self.assertEqual(cli.main(), 2)


if __name__ == "__main__":
    unittest.main()
