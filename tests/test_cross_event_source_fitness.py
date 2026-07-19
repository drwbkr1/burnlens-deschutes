from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import numpy as np
from PIL import Image

import burnlens
from burnlens.cross_event_source_fitness import (
    CrossEventSourceFitnessError,
    _load_feasibility,
    _machine_decision,
    _validate_visual,
    measure_event_registration,
    registration_window_layout,
    render_html,
    render_png,
)


class CrossEventSourceFitnessTests(unittest.TestCase):
    def test_current_package_version_is_cross_event_source_fitness_version(self) -> None:
        self.assertEqual(burnlens.__version__, "0.33.0")

    def test_event_scaled_layout_covers_arbitrary_boundary_envelopes(self) -> None:
        mask = np.zeros((100, 220), dtype=bool)
        mask[15:85, 10:210] = True
        windows = registration_window_layout(mask)
        self.assertEqual(windows, [
            {"row_offset": 0, "column_offset": 0, "height": 100, "width": 100},
            {"row_offset": 0, "column_offset": 60, "height": 100, "width": 100},
            {"row_offset": 0, "column_offset": 120, "height": 100, "width": 100},
        ])
        self.assertTrue(all(mask[
            item["row_offset"]:item["row_offset"] + item["height"],
            item["column_offset"]:item["column_offset"] + item["width"],
        ].sum() >= 256 for item in windows))

    def test_registration_uses_native_context_but_counts_quality_only_inside_boundary(self) -> None:
        rng = np.random.default_rng(361)
        shape = (96, 180)
        mask = np.zeros(shape, dtype=bool)
        mask[20:80, 20:160] = True
        base = rng.integers(1200, 9000, size=shape, dtype=np.uint16)
        arrays = {
            "B04": base,
            "B8A": np.roll(base, 5, axis=1),
            "B12": np.roll(base, 7, axis=0),
            "SCL": np.where(mask, 4, 8).astype(np.uint8),
            "MASK20": mask,
        }
        scene = {
            "product_metadata": {
                "nodata_dn": 0,
                "saturated_dn": 65535,
                "boa_offsets": {"B04": -1000.0, "B8A": -1000.0, "B12": -1000.0},
                "boa_quantification_value": 10000.0,
            },
            "rasters": {
                "B04": {
                    "source_transform": [20.0, 0.0, 600000.0, 0.0, -20.0, 4850000.0],
                    "crop_transform": [20.0, 0.0, 620000.0, 0.0, -20.0, 4840000.0],
                }
            },
        }
        windows, quality = measure_event_registration(scene, arrays, scene, arrays)
        self.assertTrue(windows)
        self.assertTrue(all(item["state"] == "pass" for item in windows))
        states = {item["state"]: item["percent"] for item in quality["inside_boundary"]["states"]}
        self.assertEqual(states["eligible-comparison"], 100.0)
        self.assertEqual(states["excluded"], 0.0)
        self.assertTrue(all("never assigns burned" in item["label_effect"] for item in windows))

    def test_machine_and_visual_gates_fail_closed(self) -> None:
        event = {
            "registration": {
                "summary": {
                    "state_counts": {"pass": 2, "review-needed": 0, "excluded": 0, "fail-registration": 0}
                }
            }
        }
        self.assertEqual(_machine_decision([event]), "PASS_CROSS_EVENT_SOURCE_FITNESS_GATE")
        with self.assertRaisesRegex(CrossEventSourceFitnessError, "incompatible"):
            _validate_visual(
                "REJECT_CROSS_EVENT_SOURCE_FITNESS",
                "ACCEPT_CROSS_EVENT_SOURCE_FITNESS",
                "reviewed",
            )

    def test_frozen_feasibility_schema_drift_fails_closed(self) -> None:
        source = (
            Path(__file__).resolve().parents[1]
            / "samples/cross-event/phase-two/CROSS-EVENT-FITNESS-2026-001.json"
        )
        report = json.loads(source.read_text(encoding="utf-8"))
        report["label_schema_version"] = "burn-scar-label-protocol-v0.1.0"
        with TemporaryDirectory() as directory:
            path = Path(directory) / "feasibility.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(CrossEventSourceFitnessError, "label schema mismatch"):
                _load_feasibility(path)

    def test_render_is_deterministic_semantic_and_lf_only(self) -> None:
        summary = {
            "window_count": 1,
            "state_counts": {"pass": 1, "review-needed": 0, "excluded": 0, "fail-registration": 0},
            "p50_px": 0.0,
            "p95_px": 0.0,
            "max_px": 0.0,
            "max_m": 0.0,
            "machine_decision": "PASS_LOCAL_CONTENT_REGISTRATION_GATE",
        }
        product = {
            "role": "synthetic-pre",
            "product_metadata": {"sensing_time_utc": "2018-01-01T00:00:00Z"},
            "scl_summary_inside_full_boundary": {
                "eligible_land_percent": 100.0,
                "review_needed_percent": 0.0,
                "excluded_percent": 0.0,
            },
        }
        window = {
            "window_id": "W-01",
            "state": "pass",
            "reason_code": "CONTENT_REGISTRATION_PASS",
            "consensus": {"magnitude_px": 0.0},
        }
        report = {
            "events": [{
                "event_group_id": "synthetic-event",
                "fire_name": "SYNTHETIC EVENT",
                "scene_group_id": "synthetic-scenes",
                "products": [product, {**product, "role": "synthetic-post"}],
                "pair_quality": {"inside_boundary": {"states": [
                    {"state": "eligible-comparison", "percent": 100.0},
                    {"state": "review-needed", "percent": 0.0},
                    {"state": "excluded", "percent": 0.0},
                ]}},
                "registration": {"summary": summary, "windows": [window]},
            }],
            "decision": {
                "machine": "PASS_CROSS_EVENT_SOURCE_FITNESS_GATE",
                "visual_review": "PENDING_VISUAL_REVIEW",
                "visual_review_notes": "",
                "next_boundary": "No label pixels or dataset.",
            },
            "method": {
                "boundary": "Full synthetic boundary.",
                "native_pixels": "Native synthetic pixels.",
                "quality": "SCL is not truth.",
                "registration": "Independent gradients.",
                "registration_envelope": "Context is correlation-only.",
            },
            "git_source_commit": "a" * 40,
            "software_version": "0.11.0",
            "run_id": "BL-TEST-CROSS-EVENT-SOURCE-FITNESS",
            "label_protocol_version": "burn-scar-label-protocol-v0.1.0",
            "label_schema_version": "burn-scar-five-state-schema-v0.1.0",
            "registered_source_lineage": {
                "acquisition_run_id": "BL-TEST-ACQUISITION",
                "registration_manifest_name": ".burnlens-registration.json",
                "registration_manifest_link_count": 2,
            },
            "attribution": "Contains modified synthetic fixture data.",
        }
        preview = [{
            "event_group_id": "synthetic-event",
            "fire_name": "SYNTHETIC EVENT",
            "pre_tci": np.zeros((3, 70, 100), dtype=np.uint8),
            "post_tci": np.zeros((3, 70, 100), dtype=np.uint8),
            "pre_mask": np.ones((70, 100), dtype=bool),
            "post_mask": np.ones((70, 100), dtype=bool),
        }]
        with TemporaryDirectory() as directory:
            root = Path(directory)
            first, second, html = root / "first.png", root / "second.png", root / "report.html"
            render_png(report, preview, first)
            render_png(report, preview, second)
            render_html(report, first.name, html)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with Image.open(first) as image:
                self.assertEqual(image.size, (1800, 1450))
            page = html.read_text(encoding="utf-8")
            self.assertIn("4 exact archives", page)
            self.assertIn("0 labels", page)
            self.assertIn("acquisition run", page)
            self.assertIn("burn-scar-label-protocol-v0.1.0", page)
            self.assertIn("burn-scar-five-state-schema-v0.1.0", page)
            self.assertIn("OneDrive alias exception", page)
            self.assertIn("Contains modified synthetic fixture data", page)
            self.assertNotIn(b"\r\n", html.read_bytes())


if __name__ == "__main__":
    unittest.main()
