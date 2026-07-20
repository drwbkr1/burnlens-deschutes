from __future__ import annotations

from copy import deepcopy
import unittest

import numpy as np

import burnlens
from burnlens.label_review_packet import (
    DARLENE_EVENT_ID,
    EVENT_ORDER,
    RESPONSE_SCHEMA_VERSION,
    adjudication_template,
    build_packet,
    response_template,
    select_sample_units,
)
from burnlens.verify_label_review_packet import (
    LabelReviewVerificationError,
    _verify_units,
    validate_completed_response,
)


def _event(event_id: str, *, omit_excluded: bool = False) -> dict:
    height, width = 50, 70
    states = np.zeros((height, width), dtype=np.uint8)
    states[:, 14:28] = 1
    states[:, 28:42] = 2
    states[:, 42:56] = 3
    states[:, 56:] = 4
    if omit_excluded:
        states[states == 3] = 2
    target = np.full(states.shape, 255, dtype=np.uint8)
    target[states == 0] = 0
    target[states == 1] = 1
    return {
        "event_group_id": event_id,
        "fire_name": event_id,
        "grid": {
            "crs": "EPSG:32610",
            "transform": [20.0, 0.0, 600000.0, 0.0, -20.0, 4800000.0],
            "width": width,
            "height": height,
            "pixel_size_m": 20,
        },
        "proposal": {
            "report_id": "TEST",
            "run_id": "BL-TEST",
            "git_source_commit": "a" * 40,
            "label_proposal_version": "test-proposal-v0",
            "report_sha256": "1" * 64,
            "state_raster_sha256": "2" * 64,
            "target_raster_sha256": "3" * 64,
            "state_counts": {},
        },
        "reference_context": {
            "kind": "MTBS annual thematic burn-severity reference",
            "detail": "test",
            "role": "review context; never sufficient truth alone",
        },
        "source_trace": {"test": True},
        "_arrays": {
            "states": states,
            "target": target,
            "pre_tci": np.zeros((3, height * 2, width * 2), dtype=np.uint8),
            "post_tci": np.zeros((3, height * 2, width * 2), dtype=np.uint8),
            "dnbr": np.zeros((height, width), dtype=np.float32),
            "reference": np.zeros((height, width), dtype=np.uint8),
        },
    }


def _events() -> list[dict]:
    return [
        _event(DARLENE_EVENT_ID),
        _event(EVENT_ORDER[1]),
        _event(EVENT_ORDER[2], omit_excluded=True),
    ]


def _walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


class LabelReviewPacketTests(unittest.TestCase):
    def test_current_package_version_is_label_review_readiness_version(self) -> None:
        self.assertEqual(burnlens.__version__, "0.35.0")

    def test_deterministic_stratified_selection_reports_structural_absence(self) -> None:
        first_units, first_coverage = select_sample_units(
            _events(), selection_seed="a" * 64
        )
        second_units, second_coverage = select_sample_units(
            _events(), selection_seed="a" * 64
        )
        self.assertEqual(first_units, second_units)
        self.assertEqual(first_coverage, second_coverage)
        self.assertEqual(len(first_units), 56)
        self.assertEqual(
            [item["sample_id"] for item in first_units],
            [f"LRU-{index:03d}" for index in range(1, 57)],
        )
        self.assertEqual(
            [item["presentation_hash"] for item in first_units],
            sorted(item["presentation_hash"] for item in first_units),
        )
        absent = [item for item in first_coverage if item["structural_absence"]]
        self.assertEqual(
            [(item["event_group_id"], item["proposal_state"]) for item in absent],
            [(EVENT_ORDER[2], "excluded")],
        )
        self.assertTrue(
            all(
                item["selected_units"] == 4
                for item in first_coverage
                if not item["structural_absence"]
            )
        )

    def test_blank_templates_never_contain_proposal_value_fields(self) -> None:
        units, _ = select_sample_units(_events(), selection_seed="b" * 64)
        response = response_template("PACKET", "RUN", units)
        adjudication = adjudication_template("PACKET", "RUN", units)
        forbidden = {
            "proposal_state",
            "proposal_state_code",
            "proposal_target_value",
            "dnbr_center",
        }
        self.assertFalse(forbidden.intersection(_walk_keys(response)))
        self.assertFalse(forbidden.intersection(_walk_keys(adjudication)))
        self.assertFalse(response["completed"])
        self.assertFalse(adjudication["completed"])
        self.assertTrue(
            all(item["first_pass_label"] is None for item in response["responses"])
        )

    def test_packet_never_advances_dataset_or_human_evidence(self) -> None:
        packet, units, _, _ = build_packet(
            events=_events(),
            generated_at_utc="2026-07-16T00:00:00Z",
            run_id="BL-TEST-LABEL-REVIEW",
            git_source_commit="a" * 40,
        )
        self.assertEqual(packet["decision"], "READY_FOR_INDEPENDENT_REVIEW_DEFER_DATASET")
        self.assertEqual(len(units), 56)
        self.assertEqual(packet["quality_gates"]["completed_independent_responses"], 0)
        self.assertEqual(packet["quality_gates"]["completed_adjudications"], 0)
        self.assertFalse(packet["quality_gates"]["dataset_created"])
        self.assertFalse(packet["quality_gates"]["accuracy_claim_created"])
        verified = _verify_units(packet)
        self.assertEqual(verified["unit_count"], 56)
        self.assertEqual(verified["unique_pixel_count"], 56)

    def test_completed_response_validator_accepts_only_full_blinded_domain(self) -> None:
        packet, units, template, _ = build_packet(
            events=_events(),
            generated_at_utc="2026-07-16T00:00:00Z",
            run_id="BL-TEST-LABEL-REVIEW",
            git_source_commit="a" * 40,
        )
        response = deepcopy(template)
        response["reviewer"] = {
            "reviewer_id": "reviewer-opaque-01",
            "independent_from_proposal_author": True,
            "burned_area_interpretation_experience": "documented-separately",
            "proposal_seen_before_first_pass": False,
            "attestation": "I completed the first pass before reveal.",
        }
        response["review_started_at_utc"] = "2026-07-16T01:00:00Z"
        response["review_completed_at_utc"] = "2026-07-16T02:00:00Z"
        response["completed"] = True
        for item in response["responses"]:
            item.update(
                {
                    "first_pass_label": "uncertain",
                    "evidence_sufficiency": "limited",
                    "confidence": "low",
                    "reason_codes": ["low-severity-ambiguity"],
                    "notes": None,
                }
            )
        summary = validate_completed_response(
            packet, response, response_sha256="f" * 64
        )
        self.assertTrue(summary["qualifying_independent_blinded_response"])
        self.assertEqual(summary["unit_count"], len(units))
        self.assertEqual(summary["uncertain_or_unusable_units"], len(units))

        response["responses"][0]["first_pass_label"] = "proposal-agrees"
        with self.assertRaisesRegex(LabelReviewVerificationError, "label is out of domain"):
            validate_completed_response(packet, response, response_sha256="f" * 64)

        response["responses"][0]["first_pass_label"] = "uncertain"
        response["responses"][0]["proposal_state"] = "unknown"
        with self.assertRaisesRegex(LabelReviewVerificationError, "proposal-value fields"):
            validate_completed_response(packet, response, response_sha256="f" * 64)

    def test_packet_verifier_rejects_target_promotion_of_ignored_state(self) -> None:
        packet, _, _, _ = build_packet(
            events=_events(),
            generated_at_utc="2026-07-16T00:00:00Z",
            run_id="BL-TEST-LABEL-REVIEW",
            git_source_commit="a" * 40,
        )
        ignored = next(
            item for item in packet["units"] if item["proposal_state"] == "unknown"
        )
        ignored["proposal_target_value"] = 0
        with self.assertRaisesRegex(LabelReviewVerificationError, "target mapping"):
            _verify_units(packet)

    def test_response_schema_is_explicit_and_versioned(self) -> None:
        units, _ = select_sample_units(_events(), selection_seed="c" * 64)
        response = response_template("PACKET", "RUN", units)
        self.assertEqual(response["response_schema_version"], RESPONSE_SCHEMA_VERSION)
        self.assertIn("privacy", response["instructions"])


if __name__ == "__main__":
    unittest.main()
