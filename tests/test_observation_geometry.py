from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import h5py
import numpy as np

from burnlens.observation_geometry import (
    BASELINE_NATIVE_ID,
    PACKAGE_ID,
    _inspect_fire_product,
    _label_protocol,
    choose_geometry_candidate,
    normalize_inventory,
    render_html,
    render_png,
    validate_screen_contracts,
)
from burnlens.paired_intake import AssetContract


AOI_WGS84 = [-121.512668, 43.620281, -121.361791, 43.703322]
AOI_UTM = [620000.0, 4831000.0, 632000.0, 4840000.0]


def cmr_item(native_id: str, concept_id: str, begin: str, route_suffix: str) -> dict:
    return {
        "meta": {"concept-id": concept_id, "revision-date": "2026-07-14T00:00:00Z"},
        "umm": {
            "GranuleUR": native_id,
            "TemporalExtent": {
                "RangeDateTime": {
                    "BeginningDateTime": begin,
                    "EndingDateTime": begin.replace(":00.000Z", ":06.000Z"),
                }
            },
            "DataGranule": {
                "ArchiveAndDistributionInformation": [{"Size": 1.0, "SizeUnit": "MB"}]
            },
            "SpatialExtent": {
                "HorizontalSpatialDomain": {
                    "Geometry": {
                        "GPolygons": [
                            {
                                "Boundary": {
                                    "Points": [
                                        {"Longitude": -130.0, "Latitude": 50.0},
                                        {"Longitude": -110.0, "Latitude": 50.0},
                                        {"Longitude": -110.0, "Latitude": 35.0},
                                        {"Longitude": -130.0, "Latitude": 35.0},
                                        {"Longitude": -130.0, "Latitude": 50.0},
                                    ]
                                }
                            }
                        ]
                    }
                }
            },
            "RelatedUrls": [
                {
                    "Type": "GET DATA",
                    "URL": (
                        "https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/"
                        f"VJ214IMG.002/{native_id}/{route_suffix}"
                    ),
                }
            ],
        },
    }


class ObservationGeometryTests(unittest.TestCase):
    def test_inventory_is_sorted_ranked_and_preserves_pre_event_state(self) -> None:
        after = "VJ214IMG.A2024177.2012.002.2025284184449"
        before = "VJ214IMG.A2024177.0848.002.2025284184447"
        payload = {
            "items": [
                cmr_item(after, "G2-LPCLOUD", "2024-06-25T20:12:00.000Z", f"{after}.nc"),
                cmr_item(before, "G1-LPCLOUD", "2024-06-25T08:48:00.000Z", f"{before}.nc"),
            ]
        }
        inventory = normalize_inventory(payload, AOI_WGS84)

        self.assertEqual([item["native_id"] for item in inventory], [before, after])
        self.assertTrue(inventory[0]["pre_event_reference_only"])
        self.assertFalse(inventory[1]["pre_event_reference_only"])
        self.assertEqual(inventory[1]["metadata_rank"], 1)
        self.assertEqual(inventory[1]["size_bytes"], 1024 * 1024)

    def test_material_geometry_rule_is_relative_and_keeps_reasons(self) -> None:
        def candidate(native_id: str, view_max: float, bowtie: int = 0, pre_event: bool = False) -> dict:
            return {
                "native_id": native_id,
                "pre_event_reference_only": pre_event,
                "seconds_from_sentinel_observation": 100.0,
                "inspection": {
                    "aoi_fire_record_count": 2,
                    "aoi_residual_bowtie_count": bowtie,
                    "aoi_reference_qualified_count": 1,
                    "aoi_reference_qualified_view_zenith_range_degrees": [view_max - 1, view_max],
                    "aoi_reference_qualified_view_zenith_median_degrees": view_max - 0.5,
                },
            }

        candidates = [
            candidate(BASELINE_NATIVE_ID, 69.0),
            candidate("VJ214IMG.A2024180.2054.002.2025284193420", 45.0),
        ]
        selected = choose_geometry_candidate(
            candidates,
            baseline_view_range=[69.0, 69.1],
            baseline_residual_bowtie_share=0.375,
        )

        self.assertIsNotNone(selected)
        self.assertEqual(selected["native_id"], candidates[1]["native_id"])
        self.assertIn("VIEW_GEOMETRY_MARGIN_NOT_MET", candidates[0]["geometry_screen_reason_codes"])
        self.assertIn("MATERIAL_GEOMETRY_IMPROVEMENT", candidates[1]["geometry_screen_reason_codes"])

    def test_screen_contract_reuses_generic_exact_package_and_checks_pair(self) -> None:
        fire = AssetContract(
            role="viirs-active-fire:A2024180.2054",
            provider="NASA LP DAAC",
            source_record_id="SOURCE-2026-005",
            provider_id="G-FIRE",
            native_id="VJ214IMG.A2024180.2054.002.2025284193420",
            expected_filename="fire.nc",
            stable_route="https://data.nasa.gov/fire.nc",
            expected_size_bytes=10,
            container="hdf5",
            package_id=PACKAGE_ID,
            native_pair_token="A2024180.2054",
        )
        geo = AssetContract(
            role="viirs-geolocation:A2024180.2054",
            provider="NASA LP DAAC",
            source_record_id="SOURCE-2026-006",
            provider_id="G-GEO",
            native_id="VJ203MODLL.A2024180.2054.021.2025001000000",
            expected_filename="geo.h5",
            stable_route="https://data.nasa.gov/geo.h5",
            expected_size_bytes=10,
            container="hdf5",
            package_id=PACKAGE_ID,
            native_pair_token="A2024180.2054",
        )
        self.assertEqual(validate_screen_contracts((fire, geo)), [])

    def test_real_array_reader_preserves_native_reference_semantics(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.nc"
            with h5py.File(path, "w") as target:
                target.create_dataset("fire mask", shape=(6464, 6400), dtype="u1", chunks=(1, 6400))
                target.create_dataset("algorithm QA", shape=(6464, 6400), dtype="u4", chunks=(1, 6400))
                target["fire mask"][10, 20] = 8
                vectors = {
                    "FP_line": np.array([10], dtype="u2"),
                    "FP_sample": np.array([20], dtype="u2"),
                    "FP_latitude": np.array([43.66], dtype="f4"),
                    "FP_longitude": np.array([-121.43], dtype="f4"),
                    "FP_confidence": np.array([8], dtype="u1"),
                    "FP_power": np.array([1.5], dtype="f4"),
                    "FP_ViewZenAng": np.array([20.0], dtype="f4"),
                    "FP_SolZenAng": np.array([30.0], dtype="f4"),
                    "FP_AdjCloud": np.array([0], dtype="u2"),
                    "FP_AdjWater": np.array([0], dtype="u2"),
                }
                for name, values in vectors.items():
                    target.create_dataset(name, data=values)
                target.attrs["FirePix"] = 1
                target.attrs["InputPointer"] = "VJ203MOD.A2024180.2054.021.2025001000000.nc"
                for name, value in {
                    "LocalGranuleID": path.name,
                    "ShortName": "VJ214IMG",
                    "VersionID": "002",
                    "RangeBeginningDate": "2024-06-28",
                    "RangeBeginningTime": "20:54:00.000000",
                    "RangeEndingDate": "2024-06-28",
                    "RangeEndingTime": "21:00:00.000000",
                    "DayNightFlag": "Day",
                }.items():
                    target.attrs[name] = value
            reference = {
                "type": "Polygon",
                "coordinates": [[[620000, 4831000], [632000, 4831000], [632000, 4840000], [620000, 4840000], [620000, 4831000]]],
            }
            result = _inspect_fire_product(path, aoi_bbox_utm=AOI_UTM, reference_geometry_utm=reference)

        self.assertEqual(result["aoi_fire_record_count"], 1)
        self.assertEqual(result["aoi_reference_qualified_count"], 1)
        self.assertEqual(result["aoi_reference_qualified_view_zenith_median_degrees"], 20.0)
        self.assertTrue(result["aoi_records"][0]["inside_nifc_final_reference"])

    def test_protocol_and_render_make_no_label_claim(self) -> None:
        protocol = _label_protocol()
        self.assertEqual(protocol["implementation_status"], "FEASIBILITY_ONLY_NO_LABEL_ARRAY_CREATED")
        self.assertIn("not background truth", protocol["negative_candidate"])
        report = {
            "decision": "RETAIN_BASELINE_REFERENCE_DEFER_LABELS",
            "decision_detail": "Reference only.",
            "candidate_summary": {
                "selected_native_id": None,
                "inventory_count": 1,
                "aoi_detection_candidate_count": 0,
                "reference_qualified_candidate_count": 0,
            },
            "candidates": [
                {
                    "pair_token": "A2024177.0848",
                    "begin": "2024-06-25T08:48:00.000Z",
                    "native_id": "VJ214IMG.A2024177.0848.002.2025284184447",
                    "geometry_screen_reason_codes": ["PRE_APPROXIMATE_EVENT_START"],
                    "inspection": {
                        "aoi_fire_record_count": 0,
                        "aoi_reference_qualified_count": 0,
                        "aoi_reference_qualified_view_zenith_median_degrees": None,
                        "aoi_residual_bowtie_count": 0,
                    },
                }
            ],
            "label_feasibility_protocol": protocol,
            "claims": {"permitted": ["Bounded evidence."], "prohibited": ["Pixel-perfect truth."]},
            "screen_rule": {"material_improvement_rule": "Relative rule.", "rule_scope": "Evidence only."},
            "source_guidance": [{"url": "https://earthdata.nasa.gov", "organization": "NASA", "role": "Primary source"}],
            "report_id": "TEST",
            "run_id": "TEST-RUN",
            "git_source_commit": "a" * 40,
            "repository": "drwbkr1/burnlens-deschutes",
            "software_version": "0.5.0",
            "package_id": PACKAGE_ID,
            "aoi_version": "aoi-darlene3-model-v0.2.0",
            "source_precedence": "Official sources govern.",
            "warning": "Experimental evidence only.",
        }
        with TemporaryDirectory() as directory:
            root = Path(directory)
            png = root / "report.png"
            html = root / "report.html"
            render_png(report, png)
            render_html(report, png.name, html)
            self.assertEqual(ImageSize(png), (1600, 1100))
            html_text = html.read_text(encoding="utf-8")
        self.assertIn("unknown is never silently converted to background", html_text)
        self.assertIn("0</span>label arrays", html_text)


def ImageSize(path: Path) -> tuple[int, int]:
    from PIL import Image

    with Image.open(path) as image:
        return image.size


if __name__ == "__main__":
    unittest.main()
