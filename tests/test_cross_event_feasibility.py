from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import burnlens
from burnlens.cross_event_feasibility import (
    CrossEventFeasibilityError,
    build_report,
    write_report,
)
from burnlens.cross_event_source import _inside_geometry


COMMIT = "1" * 40


def scene(
    scene_id: str,
    acquired: str,
    *,
    platform: str = "sentinel-2a",
    orbit: int = 13,
    cloud: float = 1.0,
) -> dict[str, object]:
    return {
        "id": scene_id,
        "window": "test",
        "datetime": acquired,
        "platform": platform,
        "grid_code": "MGRS-10TFP",
        "relative_orbit": orbit,
        "processing_version": "05.00",
        "cloud_cover_percent": cloud,
        "snow_cover_percent": 0.0,
        "bbox": [-122.0, 43.0, -120.0, 45.0],
        "product_href": f"https://zipper.dataspace.copernicus.eu/odata/v1/Products({scene_id})/$value",
        "product_bytes": 100,
        "provider_checksum": "multihash:abc",
        "product_filename": f"{scene_id}.SAFE.zip",
    }


def event(
    fire_id: str,
    fire_name: str,
    ignition: str,
    point: tuple[float, float],
    bbox: list[float],
    *,
    covered: bool = True,
) -> dict[str, object]:
    ring = [
        [bbox[0], bbox[1]],
        [bbox[2], bbox[1]],
        [bbox[2], bbox[3]],
        [bbox[0], bbox[3]],
        [bbox[0], bbox[1]],
    ]
    year = int(ignition[:4])
    windows = [
        {
            "window": "pre",
            "items": [scene(f"{fire_id}-pre", f"{year}-07-01T19:00:00Z")]
            if covered
            else [],
        },
        {
            "window": "post_initial",
            "items": [scene(f"{fire_id}-post", f"{year}-09-20T19:00:00Z")]
            if covered
            else [],
        },
        {"window": "post_extended", "items": []},
    ]
    return {
        "fire_id": fire_id,
        "fire_name": fire_name,
        "ignition_date": ignition,
        "year": year,
        "latitude": point[1],
        "longitude": point[0],
        "acres": 2000.0,
        "boundary_available": True,
        "pre_stac_eligible": True,
        "boundary": {
            "bbox": bbox,
            "assessment_type": "Extended",
            "geometry": {"type": "Polygon", "coordinates": [ring]},
        },
        "stac_windows": windows,
    }


def inputs() -> tuple[dict, dict, dict, dict]:
    source = {
        "record_id": "CROSS-EVENT-SOURCE-2026-001",
        "schema_version": "0.1.0",
        "accessed_at_utc": "2026-07-15T23:00:00Z",
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 357,
        "rules": {
            "search_envelope_wgs84": [-122.2, 43.25, -120.75, 44.75],
            "county_membership_method": "representative point test",
            "minimum_year": 2017,
            "fire_type": "Wildfire",
            "minimum_acres": 1000.0,
            "maximum_acres": 30000.0,
        },
        "mtbs": {
            "search_envelope_feature_count": 3,
            "deschutes_county_feature_count": 3,
        },
        "events": [
            event("OR-A", "Alpha", "2018-08-15", (-121.0, 43.9), [-121.03, 43.87, -120.97, 43.93]),
            event("OR-B", "Bravo", "2017-08-15", (-121.7, 44.1), [-121.73, 44.07, -121.67, 44.13]),
            event("OR-C", "Seam", "2019-08-15", (-121.8, 44.3), [-121.9, 44.2, -121.7, 44.4], covered=False),
        ],
        "boundaries": {
            "provider_imagery_downloaded": False,
            "raw_provider_bytes_retained": 0,
            "label_pixels_created": 0,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
        },
        "source_guidance": [],
    }
    aoi = {
        "report_id": "AOI-FINAL-2026-001",
        "decision": "ACCEPT_FINAL_MODELING_AOI",
        "aoi_version": "aoi-darlene3-model-v0.2.0",
        "derivation": {"aoi_bbox_wgs84": [-121.51, 43.62, -121.36, 43.70]},
    }
    optical = {
        "report_id": "OPTICAL-PAIR-2026-001",
        "decision": "ACCEPT_OPTICAL_PAIR_FOR_PROTOCOL_DEFER_LABELS",
        "target_version": "target-burn-scar-v0.2.0",
        "pre_scene": {"native_id": "DARLENE-PRE.SAFE"},
        "post_scene": {"native_id": "DARLENE-POST.SAFE"},
    }
    label_qa = {
        "report_id": "LABEL-QA-2026-001",
        "decision": "ACCEPT_REVIEWABLE_LABEL_PROPOSAL_DEFER_DATASET",
        "label_schema_version": "burn-scar-five-state-schema-v0.1.0",
    }
    return source, aoi, optical, label_qa


def report() -> dict:
    source, aoi, optical, label_qa = inputs()
    return build_report(
        source=source,
        aoi=aoi,
        optical=optical,
        label_qa=label_qa,
        input_hashes={"fixture": "2" * 64},
        generated_at_utc="2026-07-15T23:01:00Z",
        run_id="RUN-TEST-CROSS-EVENT",
        git_source_commit=COMMIT,
        visual_review_decision="PENDING_VISUAL_REVIEW",
        visual_review_notes="Synthetic test fixture.",
    )


class CrossEventFeasibilityTests(unittest.TestCase):
    def test_package_version(self) -> None:
        self.assertEqual(burnlens.__version__, "0.16.0")

    def test_selects_two_groups_and_excludes_uncovered_event(self) -> None:
        value = report()
        self.assertEqual(value["decision"], "SELECT_CROSS_EVENT_ACQUISITION_CANDIDATES")
        self.assertEqual(value["inventory"]["selected_candidate_count"], 2)
        self.assertEqual(value["group_contract"]["status"], "GROUPS_FROZEN_PARTITIONS_NOT_CREATED")
        excluded = next(item for item in value["candidate_assessments"] if item["fire_id"] == "OR-C")
        self.assertEqual(excluded["disposition"], "EXCLUDED_FROM_ACQUISITION")
        self.assertIn("NO_COMPATIBLE_LOW_CLOUD_SINGLE_TILE_PAIR", excluded["reasons"])
        self.assertFalse(value["quality_gates"]["dataset_created"])
        self.assertFalse(value["quality_gates"]["partition_created"])

    def test_source_boundary_violation_fails_closed(self) -> None:
        source, aoi, optical, label_qa = inputs()
        source["boundaries"]["provider_imagery_downloaded"] = True
        with self.assertRaisesRegex(CrossEventFeasibilityError, "SOURCE_SNAPSHOT_BOUNDARY_UNEXPECTED"):
            build_report(
                source=source,
                aoi=aoi,
                optical=optical,
                label_qa=label_qa,
                input_hashes={},
                generated_at_utc="2026-07-15T23:01:00Z",
                run_id="RUN-TEST-CROSS-EVENT",
                git_source_commit=COMMIT,
                visual_review_decision="PENDING_VISUAL_REVIEW",
                visual_review_notes="",
            )

    def test_point_on_polygon_boundary_is_inclusive(self) -> None:
        geometry = {
            "type": "Polygon",
            "coordinates": [[[0.0, 0.0], [2.0, 0.0], [2.0, 2.0], [0.0, 2.0], [0.0, 0.0]]],
        }
        self.assertTrue(_inside_geometry(0.0, 1.0, geometry))
        self.assertTrue(_inside_geometry(1.0, 1.0, geometry))
        self.assertFalse(_inside_geometry(3.0, 1.0, geometry))

    def test_rendered_outputs_are_byte_deterministic(self) -> None:
        first = report()
        second = deepcopy(first)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            first_paths = write_report(first, root / "first")
            second_paths = write_report(second, root / "second")
            for kind in ("json", "html", "png"):
                self.assertEqual(first_paths[kind].read_bytes(), second_paths[kind].read_bytes())
            parsed = json.loads(first_paths["json"].read_text(encoding="utf-8"))
            self.assertEqual(parsed["rendered_outputs"]["png_sha256"], first["rendered_outputs"]["png_sha256"])


if __name__ == "__main__":
    unittest.main()
