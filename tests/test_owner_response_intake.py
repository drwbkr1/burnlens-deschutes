from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import burnlens
from burnlens.owner_response_intake import (
    CONFIRMATION_ID,
    EXPECTED_DECISIONS,
    LABEL_SET_VERSION,
    OwnerResponseIntakeError,
    _assert_source_direction,
    _validate_confirmation,
    write_private_no_overwrite,
)
from burnlens.promotion_gate_preflight import evaluate_units


ROOT = Path(__file__).resolve().parents[1]
SURFACE_PATH = ROOT / "samples" / "labels" / "review" / "phase-two" / "OWNER-REVIEW-SURFACE-2026-001.json"
TEMPLATE_PATH = ROOT / "samples" / "labels" / "review" / "phase-two" / "OWNER-REVIEW-SURFACE-2026-001-RESPONSE-TEMPLATE.json"
CONFIRMATION_PATH = ROOT / "records" / "phase-two" / "authorizations" / "OWNER-CONFIRMATION-2026-002.json"
PUBLIC_REPORT_PATH = ROOT / "samples" / "labels" / "review" / "phase-two" / "OWNER-RESPONSE-INTAKE-2026-001.json"


class OwnerResponseIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.surface = json.loads(SURFACE_PATH.read_text(encoding="utf-8"))
        cls.template = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))

    def _response(self, decision: str = "yes") -> dict:
        response = json.loads(json.dumps(self.template))
        response["owner"]["attestation"] = True
        response["review_started_at_utc"] = "2026-07-18T03:00:00.000Z"
        response["review_completed_at_utc"] = "2026-07-18T03:20:00.000Z"
        response["completed"] = True
        for item in response["responses"]:
            item["decision"] = decision
        return response

    def test_version_entry_point_and_contract(self) -> None:
        self.assertEqual(burnlens.__version__, "0.44.0")
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn("burnlens-build-owner-response-intake =", pyproject)
        self.assertEqual(LABEL_SET_VERSION, "owner-approved-prototype-labels-v0.1.0")

    def test_all_yes_exercises_exact_quality_and_source_gates(self) -> None:
        units, counts = evaluate_units(self.surface, self._response("yes"))
        self.assertEqual(counts["ELIGIBLE_OWNER_APPROVED_PROTOTYPE_LABEL"], 24)
        self.assertEqual(counts["EXCLUDED_QUALITY_BLOCKED_AFTER_YES"], 32)
        self.assertEqual(counts["POTENTIALLY_ELIGIBLE_AFTER_YES"], 24)
        self.assertEqual(counts["BLOCKED_EVEN_AFTER_YES"], 32)
        self.assertEqual(
            _assert_source_direction(units),
            {
                "background_without_affirmative_current_reference": 12,
                "burned_with_affirmative_current_reference": 12,
            },
        )
        approved = [unit for unit in units if unit["label_promoted"]]
        self.assertEqual({unit["candidate_label"] for unit in approved}, {"background", "burned"})
        self.assertTrue(all(unit["gates"]["event_leakage"]["partition_created"] is False for unit in approved))

    def test_no_and_uncertain_remain_excluded(self) -> None:
        units, counts = evaluate_units(self.surface, self._response("no"))
        self.assertEqual(counts["EXCLUDED_BY_OWNER_RESPONSE"], 56)
        self.assertFalse(any(unit["label_promoted"] for unit in units))
        units, counts = evaluate_units(self.surface, self._response("uncertain"))
        self.assertEqual(counts["EXCLUDED_BY_OWNER_RESPONSE"], 56)
        self.assertFalse(any(unit["label_promoted"] for unit in units))

    def test_confirmation_binds_only_authoritative_response(self) -> None:
        confirmation = _validate_confirmation(CONFIRMATION_PATH)
        self.assertEqual(confirmation["confirmation_id"], CONFIRMATION_ID)
        self.assertEqual(confirmation["authoritative_response"]["decision_counts"], EXPECTED_DECISIONS)
        self.assertTrue(confirmation["older_export_excluded"])
        serialized = CONFIRMATION_PATH.read_text(encoding="utf-8").lower()
        self.assertNotIn("c:\\users", serialized)
        self.assertNotIn("de25c0bd", serialized)

    def test_private_writer_is_ignored_exact_and_no_overwrite(self) -> None:
        downloads = ROOT / "downloads"
        downloads.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=downloads) as temporary:
            path = Path(temporary) / "private.json"
            report = {"report_id": "TEST", "decision_counts": EXPECTED_DECISIONS}
            binding = write_private_no_overwrite(ROOT, path, report)
            expected = (json.dumps(report, indent=2) + "\n").encode("utf-8")
            self.assertEqual(path.read_bytes(), expected)
            self.assertEqual(binding["bytes"], len(expected))
            self.assertTrue(binding["ignored"])
            with self.assertRaisesRegex(OwnerResponseIntakeError, "refusing to overwrite"):
                write_private_no_overwrite(ROOT, path, report)

    def test_tracked_public_report_is_content_safe_and_bounded(self) -> None:
        report = json.loads(PUBLIC_REPORT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(report["decision_counts"], EXPECTED_DECISIONS)
        self.assertEqual(report["outcome"]["owner_approved_prototype_labels"], 24)
        self.assertEqual(report["outcome"]["prototype_label_class_counts"], {"background": 12, "burned": 12})
        self.assertEqual(set(report["outcome"]["prototype_label_event_counts"].values()), {8})
        self.assertEqual(
            report["decision"],
            "ACCEPT_24_OWNER_APPROVED_PROTOTYPE_LABELS_DEFER_DATASET_SPLIT_BASELINE_MODEL",
        )
        self.assertFalse(any(report["boundaries"][key] for key in ("dataset_created", "split_created", "baseline_created", "model_created")))
        self.assertFalse(any(report["privacy"].values()))
        serialized = PUBLIC_REPORT_PATH.read_text(encoding="utf-8").lower()
        for forbidden in ("c:\\users", "downloads", "de25c0bd", "lru-", "sample_id"):
            self.assertNotIn(forbidden, serialized)

    def test_tracked_public_outputs_match_report_hashes(self) -> None:
        report = json.loads(PUBLIC_REPORT_PATH.read_text(encoding="utf-8"))
        output_root = PUBLIC_REPORT_PATH.parent
        for output in report["outputs"]:
            path = output_root / output["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), output["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), output["sha256"])


if __name__ == "__main__":
    unittest.main()
