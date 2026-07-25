from __future__ import annotations

from pathlib import Path
import unittest

from burnlens.whole_event_split import (
    RANKING_CRITERIA,
    SPLIT_VERSION,
    _all_assignments,
    _validate_inputs,
    build_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ROLES = {
    "train": [
        "event-green-ridge-0684-cs-2020",
        "event-tepee-1144-ne-2018",
    ],
    "validation": [
        "event-grandview-0558-od-2021",
        "event-mckay-1035-ne-2017",
    ],
    "test": [
        "event-ward-creek-2019",
        "event-windigo-2022",
    ],
}


class WholeEventSplitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ranking, cls.split = build_outputs(
            ROOT,
            "2026-07-25T21:00:00Z",
            "BL-TEST-P2O5-T03-U02",
            "a" * 40,
        )

    def test_all_54_valid_assignments_are_ranked_once(self) -> None:
        assignments = self.ranking["ranked_valid_assignments"]
        self.assertEqual(len(assignments), 54)
        self.assertEqual(
            [assignment["rank"] for assignment in assignments],
            list(range(1, 55)),
        )
        canonical = [
            assignment["score_components"]["canonical_role_event_ids"]
            for assignment in assignments
        ]
        self.assertEqual(len(set(canonical)), 54)

    def test_predeclared_ranking_selects_exact_split(self) -> None:
        self.assertEqual(
            tuple(
                self.ranking["ranking_predeclaration"]["criteria_in_order"]
            ),
            RANKING_CRITERIA,
        )
        self.assertEqual(self.ranking["selected_roles"], EXPECTED_ROLES)
        self.assertEqual(self.split["selection"]["rank"], 1)
        self.assertEqual(
            {
                role: summary["event_group_ids"]
                for role, summary in self.split["selection"]["roles"].items()
            },
            EXPECTED_ROLES,
        )

    def test_each_role_has_one_regime_and_one_transfer_event(self) -> None:
        for summary in self.split["selection"]["roles"].values():
            self.assertEqual(
                sorted(summary["source_regime_counts"].values()), [1, 1]
            )
            self.assertEqual(summary["never_tuned_transfer_events"], 1)
        self.assertEqual(
            self.split["selection"]["roles"]["train"]["core_pixels"], 109
        )
        self.assertEqual(
            self.split["selection"]["roles"]["validation"]["core_pixels"], 89
        )
        self.assertEqual(
            self.split["selection"]["roles"]["test"]["core_pixels"], 89
        )

    def test_ranking_is_independent_of_candidate_event_order(self) -> None:
        _, _, by_id = _validate_inputs(ROOT)
        assignments, _ = _all_assignments(dict(reversed(list(by_id.items()))))
        self.assertEqual(assignments[0]["roles"], EXPECTED_ROLES)
        self.assertEqual(
            assignments,
            self.ranking["ranked_valid_assignments"],
        )

    def test_group_ids_and_candidates_are_role_atomic(self) -> None:
        groups = self.split["group_bindings"]
        self.assertEqual(len(groups), 6)
        for field in (
            "scene_group_id",
            "geography_group_id",
            "time_group_id",
            "source_regime_group_id",
        ):
            self.assertEqual(
                len({groups[event_id][field] for event_id in groups}), 6
                if field != "source_regime_group_id"
                else 2,
            )
        self.assertEqual(
            sum(len(items) for items in self.split["candidate_bindings"].values()),
            12,
        )

    def test_test_and_training_boundaries_remain_closed(self) -> None:
        self.assertEqual(self.split["split_version"], SPLIT_VERSION)
        self.assertFalse(self.split["dataset_created"])
        self.assertEqual(self.split["sealed_test"]["open_count"], 0)
        self.assertFalse(self.split["sealed_test"]["pixel_values_opened"])
        self.assertFalse(self.split["boundaries"]["training_authorized"])
        self.assertFalse(self.split["boundaries"]["metric_result_created"])
        self.assertFalse(
            self.ranking["ranking_predeclaration"]["pixel_values_opened"]
        )


if __name__ == "__main__":
    unittest.main()
