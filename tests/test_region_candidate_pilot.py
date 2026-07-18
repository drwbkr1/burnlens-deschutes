from __future__ import annotations

import json
from pathlib import Path
import unittest

import numpy as np
from PIL import Image

import burnlens
from burnlens.region_candidate_pilot import (
    GENERATOR_VERSION,
    REPORT_ID,
    _candidate_from_seed,
    _panel,
    _tci_image,
    select_candidates,
)


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "samples" / "labels" / "pilot" / "phase-two" / f"{REPORT_ID}.json"


def _event(event_id: str) -> dict:
    shape = (24, 24)
    states = np.full(shape, 2, dtype=np.uint8)
    reference = np.zeros(shape, dtype=np.uint8)
    eligible = np.ones(shape, dtype=bool)
    dnbr = np.zeros(shape, dtype=np.float32)
    return {"event_group_id": event_id, "states": states, "reference": reference, "eligible": eligible, "dnbr": dnbr}


def _unit(sample_id: str, event_id: str, candidate_class: str, row: int, column: int) -> dict:
    return {
        "sample_id": sample_id,
        "event_group_id": event_id,
        "candidate_label": candidate_class,
        "row": row,
        "column": column,
        "selection_hash": (sample_id.lower().replace("-", "a") * 16)[:64],
    }


class RegionCandidatePilotTests(unittest.TestCase):
    def test_version_and_generator_are_frozen(self) -> None:
        self.assertEqual(burnlens.__version__, "0.29.0")
        self.assertEqual(GENERATOR_VERSION, "region-candidate-generator-v0.1.0")

    def test_component_is_intact_and_ring_is_one_pixel(self) -> None:
        event = _event("event-darlene3-or-2024")
        event["states"][8:11, 8:11] = 1
        event["reference"][8:11, 8:11] = 1
        event["dnbr"][8:11, 8:11] = 0.17
        candidate = _candidate_from_seed(event, _unit("LRU-001", event["event_group_id"], "burned", 9, 9))
        self.assertEqual(candidate["core_pixels"], 9)
        self.assertEqual(candidate["ring_pixels"], 16)
        self.assertFalse(candidate["touches_grid_edge"])

    def test_band_first_tci_is_normalized_for_rendering(self) -> None:
        image = _tci_image(np.zeros((3, 5, 7), dtype=np.uint8))
        self.assertEqual(image.size, (7, 5))

    def test_ten_meter_display_is_aligned_to_twenty_meter_candidate_grid(self) -> None:
        core = np.zeros((5, 7), dtype=bool)
        core[2, 3] = True
        ring = np.zeros_like(core)
        ring[1:4, 2:5] = True
        ring[2, 3] = False
        panel = _panel(Image.new("RGB", (14, 10)), core, ring, [2, 3, 3, 4], "burned", (70, 50))
        self.assertEqual(panel.size, (70, 50))

    def test_selection_never_clips_to_target(self) -> None:
        events = {event_id: _event(event_id) for event_id in (
            "event-darlene3-or-2024", "event-mckay-1035-ne-2017", "event-tepee-1144-ne-2018"
        )}
        units = []
        counter = 1
        for event_id, event in events.items():
            event["states"][3:7, 3:7] = 0
            event["dnbr"][3:7, 3:7] = 0.01
            units.append(_unit(f"LRU-{counter:03d}", event_id, "background", 4, 4)); counter += 1
            event["states"][14:18, 14:18] = 1
            event["reference"][14:18, 14:18] = 2
            event["dnbr"][14:18, 14:18] = 0.17
            units.append(_unit(f"LRU-{counter:03d}", event_id, "burned", 15, 15)); counter += 1
        selected, _ = select_candidates(units, events)
        self.assertEqual(len(selected), 6)
        self.assertTrue(all(item["core_pixels"] == 16 for item in selected))
        self.assertTrue(all(item["ring_pixels"] == 20 for item in selected))


@unittest.skipUnless(PUBLIC.exists(), "tracked pilot report not published yet")
class TrackedRegionCandidatePilotTests(unittest.TestCase):
    def test_public_report_is_no_promotion_and_private_safe(self) -> None:
        report = json.loads(PUBLIC.read_text(encoding="utf-8"))
        self.assertEqual(report["summary"]["candidate_count"], 6)
        self.assertEqual(report["summary"]["owner_region_responses"], 0)
        self.assertEqual(report["summary"]["owner_approved_region_labels"], 0)
        self.assertFalse(any(value for key, value in report["claim_boundaries"].items() if isinstance(value, bool)))
        serialized = PUBLIC.read_text(encoding="utf-8").lower()
        for forbidden in ("lru-", "sample_id", "owner_decision", "c:\\users", "private.json", "downloads\\"):
            self.assertNotIn(forbidden, serialized)

    def test_public_outputs_match_bindings(self) -> None:
        import hashlib
        report = json.loads(PUBLIC.read_text(encoding="utf-8"))
        for output in report["outputs"]:
            payload = (PUBLIC.parent / output["path"]).read_bytes()
            self.assertEqual(len(payload), output["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), output["sha256"])


if __name__ == "__main__":
    unittest.main()
