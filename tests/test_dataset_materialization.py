from __future__ import annotations

import json
from pathlib import Path
import unittest

import numpy as np

from burnlens.dataset_materialization import (
    _event_state,
    _patch_window,
    _registration_index,
    _registration_pass_mask,
    _validate_inputs,
)


ROOT = Path(__file__).resolve().parents[1]


class DatasetMaterializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract, cls.split, cls.candidate = _validate_inputs(ROOT)

    def test_exact_registered_archive_roster_is_locally_available(self) -> None:
        index = _registration_index(ROOT)
        expected = {
            product["filename"]
            for event in self.contract["source_pairs"]
            for product in event["products"]
        }
        self.assertEqual(len(expected), 12)
        self.assertTrue(expected.issubset(index))
        for filename in expected:
            path, registration, asset = index[filename]
            self.assertTrue(path.is_file())
            self.assertFalse(registration["synthetic_fixture"])
            self.assertEqual(path.stat().st_size, asset["bytes"])

    def test_event_state_uses_only_owner_approved_cores(self) -> None:
        total_core = 0
        total_unknown = 0
        for event in self.candidate["events"]:
            state, arrays = _event_state(ROOT, event)
            self.assertEqual(len(arrays), 2)
            expected_core = event["core_pixels"]
            expected_unknown = event["unknown_ring_pixels"]
            self.assertEqual(
                int(np.count_nonzero(np.isin(state, (0, 1)))),
                expected_core,
            )
            self.assertEqual(int(np.count_nonzero(state == 2)), expected_unknown)
            total_core += expected_core
            total_unknown += expected_unknown
        self.assertEqual(total_core, 287)
        self.assertEqual(total_unknown, 531)

    def test_fixed_patch_contains_each_core_and_unknown_ring(self) -> None:
        for event in self.candidate["events"]:
            _, arrays = _event_state(ROOT, event)
            for candidate in event["candidates"]:
                values = arrays[candidate["candidate_id"]]
                row, column, height, width = _patch_window(values == 1)
                self.assertEqual((height, width), (64, 64))
                self.assertEqual(
                    int(
                        np.count_nonzero(
                            values[
                                row : row + height,
                                column : column + width,
                            ]
                            == 1
                        )
                    ),
                    candidate["core_pixels"],
                )
                self.assertEqual(
                    int(
                        np.count_nonzero(
                            values[
                                row : row + height,
                                column : column + width,
                            ]
                            == 2
                        )
                    ),
                    candidate["unknown_ring_pixels"],
                )

    def test_registration_mask_fails_closed_outside_windows(self) -> None:
        registration = {
            "windows": [
                {
                    "state": "pass",
                    "pixel_window": {
                        "row_offset": 1,
                        "column_offset": 1,
                        "height": 2,
                        "width": 2,
                    },
                }
            ]
        }
        passed, counts = _registration_pass_mask(registration, (4, 4))
        self.assertEqual(int(passed.sum()), 4)
        self.assertEqual(counts["uncovered"], 12)

    def test_locked_split_has_zero_test_open_count(self) -> None:
        self.assertEqual(self.split["sealed_test"]["open_count"], 0)
        self.assertFalse(self.split["sealed_test"]["pixel_values_opened"])
        self.assertFalse(self.split["boundaries"]["training_authorized"])


if __name__ == "__main__":
    unittest.main()
