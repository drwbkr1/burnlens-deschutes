from __future__ import annotations

import json
from pathlib import Path
import unittest

from burnlens.phase_four_context_intake import (
    PhaseFourContextIntakeError,
    _load_exact_plan,
    validate_feature_collection,
)


ROOT = Path(__file__).resolve().parents[1]


def _feature(object_id: int, geometry: dict, fields: set[str]) -> dict:
    properties = {field: None for field in fields}
    properties[next(field for field in fields if field == "objectid")] = object_id
    return {
        "type": "Feature",
        "geometry": geometry,
        "properties": properties,
    }


class PhaseFourContextIntakeTests(unittest.TestCase):
    def test_exact_authorized_plan_loads(self) -> None:
        plan = _load_exact_plan(ROOT)
        self.assertEqual(len(plan["assets"]), 8)
        self.assertTrue(
            all(asset["state"] == "authorized" for asset in plan["assets"])
        )

    def test_valid_line_feature_collection_passes(self) -> None:
        from burnlens.phase_four_context_intake import ASSET_RULES

        rule = ASSET_RULES["ntd-secondary-highways"]
        features = [
            _feature(
                index,
                {
                    "type": "LineString",
                    "coordinates": [
                        [-120.9, 44.9],
                        [-120.8, 45.0],
                    ],
                },
                rule["fields"],
            )
            for index in range(1, rule["count"] + 1)
        ]
        result = validate_feature_collection(
            json.dumps(
                {"type": "FeatureCollection", "features": features}
            ).encode(),
            asset_id="ntd-secondary-highways",
        )
        self.assertEqual(result["feature_count"], 28)
        self.assertTrue(result["object_ids_strictly_increasing"])

    def test_unexpected_field_fails(self) -> None:
        from burnlens.phase_four_context_intake import ASSET_RULES

        rule = ASSET_RULES["nsd-fire-ems"]
        fields = set(rule["fields"]) | {"address"}
        payload = json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    _feature(
                        1,
                        {"type": "Point", "coordinates": [-120.8, 44.9]},
                        fields,
                    )
                ],
            }
        ).encode()
        with self.assertRaisesRegex(
            PhaseFourContextIntakeError, "field roster"
        ):
            validate_feature_collection(payload, asset_id="nsd-fire-ems")

    def test_count_and_geometry_drift_fail(self) -> None:
        payload = json.dumps(
            {
                "type": "FeatureCollection",
                "features": [],
            }
        ).encode()
        with self.assertRaisesRegex(
            PhaseFourContextIntakeError, "feature count"
        ):
            validate_feature_collection(
                payload,
                asset_id="nbd-blm-boundary",
            )


if __name__ == "__main__":
    unittest.main()
