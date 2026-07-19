from __future__ import annotations

from copy import deepcopy
from datetime import date, timedelta
import json
from pathlib import Path
import tempfile
import unittest

from burnlens.additional_event_group_plan import (
    AdditionalEventGroupError,
    CANDIDATE_IDS,
    SELECTED_EVENT_IDS,
    build_report,
    validate_source,
    write_report,
)


def _scene(event_id: str, day: date, *, window: str, post: bool) -> dict[str, object]:
    stamp = day.isoformat()
    side = "post" if post else "pre"
    return {
        "id": f"S2A_{event_id}_{side}",
        "window": window,
        "datetime": f"{stamp}T18:59:21.024Z",
        "platform": "sentinel-2a",
        "grid_code": f"MGRS-{event_id[-5:]}",
        "relative_orbit": 13,
        "processing_version": "05.00",
        "cloud_cover_percent": 1.0 if post else 0.5,
        "snow_cover_percent": 0.0,
        "bbox": [-123.0, 42.0, -119.0, 46.0],
        "product_href": f"https://download.dataspace.copernicus.eu/download/{event_id}-{side}",
        "product_bytes": 1_000_000_000,
        "provider_checksum": f"multihash:{event_id}-{side}",
        "product_filename": f"{event_id}-{side}.SAFE.zip",
    }


def _event(
    event_id: str,
    name: str,
    ignition: str,
    longitude: float,
    latitude: float,
    programs: list[str],
    index: int,
) -> dict[str, object]:
    ignition_day = date.fromisoformat(ignition)
    products = [
        {
            "catalog_id": index * 10 + offset,
            "map_id": index * 100 + offset,
            "program": program,
            "incident_name": name,
            "boundary_acres": 2000,
            "nonstandard": False,
        }
        for offset, program in enumerate(programs, 1)
    ]
    bbox = [longitude - 0.02, latitude - 0.02, longitude + 0.02, latitude + 0.02]
    geometry = {
        "type": "Polygon",
        "coordinates": [[
            [bbox[0], bbox[1]],
            [bbox[2], bbox[1]],
            [bbox[2], bbox[3]],
            [bbox[0], bbox[3]],
            [bbox[0], bbox[1]],
        ]],
    }
    pre = _scene(event_id, ignition_day - timedelta(days=15), window="pre", post=False)
    post = _scene(event_id, ignition_day + timedelta(days=25), window="post_initial", post=True)
    return {
        "fire_id": event_id,
        "fire_name": name,
        "ignition_date": ignition,
        "year": ignition_day.year,
        "latitude": latitude,
        "longitude": longitude,
        "acres": 2000.0 + index,
        "map_id": index,
        "map_program": "MTBS",
        "pre_id": f"pre-{index}",
        "post_id": f"post-{index}",
        "boundary": {
            "fire_id": event_id,
            "fire_name": name,
            "year": ignition_day.year,
            "fire_type": "Wildfire",
            "acres": 2000.0 + index,
            "assessment_type": "Extended",
            "ignition_date": ignition,
            "map_id": index,
            "map_program": "MTBS",
            "pre_id": f"pre-{index}",
            "post_id": f"post-{index}",
            "comments": None,
            "bbox": bbox,
            "geometry": geometry,
        },
        "portal_products": products,
        "programs": programs,
        "stac_search_bbox": bbox,
        "stac_windows": [
            {"window": "pre", "items": [pre]},
            {"window": "post_initial", "items": [post]},
            {"window": "post_extended", "items": []},
        ],
    }


def _source() -> dict[str, object]:
    specs = [
        (CANDIDATE_IDS[0], "WHYCHUS 0814 CS", "2017-08-11", -121.3764, 44.4122, ["MTBS"]),
        (CANDIDATE_IDS[1], "GREEN RIDGE 0684 CS", "2020-08-17", -121.5754, 44.4622, ["BAER", "MTBS", "RAVG"]),
        (CANDIDATE_IDS[2], "GRANDVIEW 0558 OD", "2021-07-11", -121.4237, 44.4257, ["BAER", "MTBS", "RAVG"]),
        (CANDIDATE_IDS[3], "PETES LAKE", "2023-08-25", -121.9125, 43.9670, ["MTBS"]),
        (CANDIDATE_IDS[4], "WHITEWATER", "2017-07-24", -121.8758, 44.6954, ["BAER", "MTBS", "RAVG"]),
    ]
    return {
        "source_id": "ADDITIONAL-EVENT-GROUP-SOURCE-2026-001",
        "source_schema_version": "0.1.0",
        "serialization": "UTF-8 JSON with LF canonical line endings",
        "accessed_at_utc": "2026-07-19T12:00:00Z",
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 466,
        "run_id": "BL-2026-07-19-additional-event-groups-test",
        "git_source_commit": "1" * 40,
        "software_version": "0.32.0",
        "purpose": "test",
        "rules": {},
        "request_urls": {
            "mtbs_occurrences": "https://apps.fs.usda.gov/occurrence",
            "mtbs_boundaries": "https://apps.fs.usda.gov/boundary",
            "burn_severity_portal": "https://edcintl.cr.usgs.gov/geoserver/wfs",
            "cdse_collection": "https://stac.dataspace.copernicus.eu/v1/collections/sentinel-2-l2a",
        },
        "cdse": {},
        "existing_events": [
            {"fire_id": "OR4364712147820240625", "event_group_id": "event-darlene3-or-2024", "year": 2024, "name": "Darlene 3", "programs": ["BAER", "MTBS", "RAVG"], "portal_products": []},
            {"fire_id": "OR4375212142520170829", "event_group_id": "event-mckay-1035-ne-2017", "year": 2017, "name": "McKay", "programs": ["MTBS", "RAVG"], "portal_products": []},
            {"fire_id": "OR4383912111420180907", "event_group_id": "event-tepee-1144-ne-2018", "year": 2018, "name": "Tepee", "programs": ["BAER", "MTBS", "RAVG"], "portal_products": []},
        ],
        "candidate_events": [
            _event(event_id, name, ignition, longitude, latitude, programs, index)
            for index, (event_id, name, ignition, longitude, latitude, programs) in enumerate(specs, 1)
        ],
        "source_guidance": [],
        "boundaries": {
            "provider_imagery_downloaded": False,
            "provider_bytes_retained": 0,
            "label_pixels_created": 0,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
        },
    }


class AdditionalEventGroupPlanTests(unittest.TestCase):
    def test_deterministic_selection_closes_new_years_first(self) -> None:
        report = build_report(
            _source(),
            source_sha256="2" * 64,
            generated_at_utc="2026-07-19T12:30:00Z",
            run_id="BL-2026-07-19-additional-event-groups-test-r001",
            git_source_commit="1" * 40,
        )
        selected = [
            item["fire_id"]
            for item in report["candidate_assessments"]
            if item["disposition"] == "FROZEN_FOR_BOUNDED_ACQUISITION"
        ]
        self.assertEqual(tuple(selected), SELECTED_EVENT_IDS)
        self.assertEqual(report["event_count_after_freeze"], 6)
        self.assertEqual(report["event_years_after_freeze"], [2017, 2018, 2020, 2021, 2023, 2024])
        self.assertEqual(report["acquisition_contract"]["selected_product_count"], 6)
        self.assertFalse(report["quality_gates"]["dataset_created"])

    def test_source_fails_closed_if_provider_bytes_advance(self) -> None:
        source = deepcopy(_source())
        source["boundaries"]["provider_bytes_retained"] = 1
        with self.assertRaisesRegex(AdditionalEventGroupError, "SOURCE_BOUNDARIES_INVALID"):
            validate_source(source)

    def test_report_outputs_are_byte_reproducible(self) -> None:
        report = build_report(
            _source(),
            source_sha256="2" * 64,
            generated_at_utc="2026-07-19T12:30:00Z",
            run_id="BL-2026-07-19-additional-event-groups-test-r001",
            git_source_commit="1" * 40,
        )
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_paths = write_report(deepcopy(report), Path(first))
            second_paths = write_report(deepcopy(report), Path(second))
            for key in ("json", "html", "png"):
                self.assertEqual(first_paths[key].read_bytes(), second_paths[key].read_bytes())
            parsed = json.loads(first_paths["json"].read_text(encoding="utf-8"))
            self.assertIsNone(parsed["dataset_version"])
            self.assertIn("Not official wildfire information", first_paths["html"].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
