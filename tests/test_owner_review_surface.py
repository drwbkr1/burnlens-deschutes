from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import burnlens
from burnlens.lock_owner_review_response import lock_response, validate_response
from burnlens.owner_review_surface import (
    ALLOWED_DECISIONS,
    BUNDLE_REPORT_SHA256,
    PACKET_SHA256,
    RESPONSE_SCHEMA_VERSION,
    SURFACE_ID,
    OwnerReviewSurfaceError,
)


ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "samples" / "labels" / "review" / "phase-two"
SURFACE_PATH = DIRECTORY / f"{SURFACE_ID}.json"
HTML_PATH = DIRECTORY / f"{SURFACE_ID}.html"
TEMPLATE_PATH = DIRECTORY / f"{SURFACE_ID}-RESPONSE-TEMPLATE.json"


class OwnerReviewSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.surface = json.loads(SURFACE_PATH.read_text(encoding="utf-8"))
        cls.template = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))

    def test_version_and_entry_points(self) -> None:
        self.assertEqual(burnlens.__version__, "0.41.0")
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('burnlens-build-owner-review-surface =', pyproject)
        self.assertIn('burnlens-lock-owner-review-response =', pyproject)

    def test_all_original_units_are_reopened_without_owner_decisions(self) -> None:
        report = self.surface
        self.assertEqual(report["report_id"], SURFACE_ID)
        self.assertEqual(report["task_issue"], 432)
        self.assertEqual(report["summary"]["unit_count"], 56)
        self.assertEqual(
            [item["sample_id"] for item in report["units"]],
            [f"LRU-{index:03d}" for index in range(1, 57)],
        )
        self.assertEqual(report["summary"]["candidate_counts"], {"background": 21, "burned": 35})
        self.assertEqual(report["summary"]["quality_blocked_units"], 32)
        self.assertEqual(report["review_contract"]["owner_responses_recorded"], 0)
        self.assertEqual(report["summary"]["labels_promoted"], 0)
        self.assertFalse(report["review_contract"]["historical_response_inherited"])
        self.assertEqual(
            report["source_bindings"]["historical_packet"]["sha256"],
            PACKET_SHA256,
        )
        self.assertEqual(
            report["source_bindings"]["current_bundle_fitness"]["sha256"],
            BUNDLE_REPORT_SHA256,
        )

    def test_public_surface_excludes_restricted_barc_and_preserves_cautions(self) -> None:
        serialized = json.dumps(self.surface).lower()
        self.assertEqual(
            self.surface["boundaries"]["restricted_thresholded_tepee_barc"],
            "excluded from all public pixels and candidate decisions",
        )
        self.assertIn("increased-greenness class 5 remains ambiguous", serialized)
        self.assertIn("forest-calibrated and timing-sensitive", serialized)
        for unit in self.surface["units"]:
            evidence = unit["current_reference_evidence"]
            if evidence["baer_dnbr"] is not None:
                self.assertFalse(evidence["baer_dnbr"]["thresholded_barc_used"])
            self.assertIn(unit["candidate_label"], {"burned", "background"})
            if unit["frozen_proposal_state"] not in {"burned", "background-candidate"}:
                self.assertIsNotNone(unit["quality_blocker"])
                self.assertEqual(unit["evidence_grade"], "quality-blocked")

    def test_exact_outputs_and_interactive_contract_are_present(self) -> None:
        for output in self.surface["outputs"]:
            path = DIRECTORY / output["path"]
            data = path.read_bytes()
            self.assertEqual(len(data), output["bytes"])
            self.assertEqual(sha256(data).hexdigest(), output["sha256"])
        html = HTML_PATH.read_text(encoding="utf-8")
        self.assertEqual(html.count('data-sample="LRU-'), 56)
        self.assertEqual(html.count('value="yes"'), 56)
        self.assertEqual(html.count('value="no"'), 56)
        self.assertEqual(html.count('value="uncertain"'), 56)
        self.assertIn("Finalize and export exact response", html)
        self.assertNotIn("localStorage", html)
        self.assertNotIn("burnlens-site", html.lower())
        node = shutil.which("node")
        self.assertIsNotNone(node)
        controller = html.rsplit("<script>", 1)[1].split("</script>", 1)[0]
        with tempfile.TemporaryDirectory() as temporary:
            script = Path(temporary) / "owner-review-controller.js"
            script.write_text(controller, encoding="utf-8", newline="\n")
            result = subprocess.run(
                [node, "--check", str(script)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_blank_template_contains_no_owner_decisions(self) -> None:
        template = self.template
        self.assertEqual(template["response_schema_version"], RESPONSE_SCHEMA_VERSION)
        self.assertFalse(template["completed"])
        self.assertFalse(template["owner"]["attestation"])
        self.assertEqual(len(template["responses"]), 56)
        self.assertTrue(all(item["decision"] is None for item in template["responses"]))

    def _completed_response(self) -> dict:
        response = json.loads(json.dumps(self.template))
        response["owner"]["attestation"] = True
        response["review_started_at_utc"] = "2026-07-18T04:00:00Z"
        response["review_completed_at_utc"] = "2026-07-18T04:20:00Z"
        response["completed"] = True
        for index, item in enumerate(response["responses"]):
            item["decision"] = ALLOWED_DECISIONS[index % len(ALLOWED_DECISIONS)]
        return response

    def test_completed_response_validates_and_exact_bytes_lock_without_overwrite(self) -> None:
        response = self._completed_response()
        summary = validate_response(self.surface, response)
        self.assertEqual(summary["decision_counts"], {"yes": 19, "no": 19, "uncertain": 18})
        response_bytes = (json.dumps(response, indent=2) + "\n").encode("utf-8")
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            response_path = directory / "response.json"
            response_path.write_bytes(response_bytes)
            locked = directory / "locked"
            exact, receipt, report = lock_response(
                surface_path=SURFACE_PATH,
                response_path=response_path,
                destination_directory=locked,
                received_at_utc="2026-07-18T04:21:00Z",
                run_id="BL-2026-07-18-owner-review-response-lock-test-r001",
                git_source_commit="a" * 40,
                evidence_origin="software-browser-fixture",
            )
            self.assertEqual(exact.read_bytes(), response_bytes)
            self.assertTrue(receipt.is_file())
            self.assertFalse(report["owner_yes_is_label_acceptance"])
            self.assertTrue(report["software_browser_fixture"])
            self.assertFalse(report["qualifying_owner_response"])
            with self.assertRaisesRegex(OwnerReviewSurfaceError, "refusing to overwrite"):
                lock_response(
                    surface_path=SURFACE_PATH,
                    response_path=response_path,
                    destination_directory=locked,
                    received_at_utc="2026-07-18T04:21:00Z",
                    run_id="BL-2026-07-18-owner-review-response-lock-test-r002",
                    git_source_commit="b" * 40,
                    evidence_origin="software-browser-fixture",
                )
            self.assertEqual(exact.read_bytes(), response_bytes)
            self.assertTrue(receipt.is_file())

    def test_response_validation_fails_closed(self) -> None:
        response = self._completed_response()
        response["responses"][0]["decision"] = "maybe"
        with self.assertRaisesRegex(OwnerReviewSurfaceError, "outside yes/no/uncertain"):
            validate_response(self.surface, response)
        response = self._completed_response()
        response["responses"][0]["candidate_label"] = "background" if response["responses"][0]["candidate_label"] == "burned" else "burned"
        with self.assertRaisesRegex(OwnerReviewSurfaceError, "identity or proposition drift"):
            validate_response(self.surface, response)


if __name__ == "__main__":
    unittest.main()
