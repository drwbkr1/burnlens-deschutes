from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from PIL import Image

import burnlens
from burnlens.owner_waiver_reveal_readiness import (
    OWNER_WAIVER_ID,
    RevealReadinessContract,
    authorize_owner_waiver_reveal,
)
from burnlens.single_reviewer_reconciliation import (
    DECISION,
    SingleReviewerReconciliationError,
    classify_unit,
    reconcile_single_reviewer,
)
from burnlens.single_reviewer_reconciliation_qa import (
    build_single_reviewer_reconciliation_qa,
    write_single_reviewer_reconciliation_qa,
)


class SingleReviewerReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / ".gitignore").write_text("downloads/\n", encoding="utf-8")
        self.inputs = self.root / "inputs"
        self.inputs.mkdir()
        self.packet = self.inputs / "packet.json"
        self.response = self.inputs / "response.json"
        self.receipt = self.inputs / "receipt.json"
        self.reveal = self.inputs / "reveal.html"
        self.authorization = self.root / "downloads" / "authorization.json"
        self.private_output = self.root / "downloads" / "reconciliation.json"
        self.units = [
            self._packet_unit("LRU-001", "event-a", "burned", 1),
            self._packet_unit("LRU-002", "event-a", "background-candidate", 0),
            self._packet_unit("LRU-003", "event-a", "background-candidate", 0),
            self._packet_unit("LRU-004", "event-b", "burned", 1),
            self._packet_unit("LRU-005", "event-b", "burned", 1),
            self._packet_unit("LRU-006", "event-b", "unknown", None),
        ]
        packet = {
            "report_id": "LABEL-REVIEW-PACKET-2026-001",
            "schema_version": "0.1.0",
            "run_id": "BL-SYNTHETIC-PACKET-r001",
            "aoi_version": "aoi-test-v0.1.0",
            "target_version": "target-test-v0.1.0",
            "label_schema_version": "label-test-v0.1.0",
            "response_schema_version": "burnlens-label-review-response-v0.1.0",
            "units": self.units,
        }
        self.packet.write_bytes((json.dumps(packet, indent=2) + "\n").encode())
        response_units = [
            self._response_unit("LRU-001", "burned", "sufficient", ["persistent-darkening"]),
            self._response_unit("LRU-002", "background", "sufficient", ["source-context-support"]),
            self._response_unit("LRU-003", "background", "sufficient", ["persistent-darkening"]),
            self._response_unit(
                "LRU-004",
                "burned",
                "limited",
                ["pre-post-change", "persistent-darkening"],
            ),
            self._response_unit("LRU-005", "uncertain", "sufficient", ["low-severity-ambiguity"]),
            self._response_unit("LRU-006", "burned", "sufficient", ["vegetation-loss"]),
        ]
        response = {
            "response_schema_version": "burnlens-label-review-response-v0.1.0",
            "packet_id": "LABEL-REVIEW-PACKET-2026-001",
            "packet_run_id": "BL-SYNTHETIC-PACKET-r001",
            "reviewer": {
                "reviewer_id": "reviewer-01",
                "independent_from_proposal_author": True,
                "burned_area_interpretation_experience": "withheld synthetic",
                "proposal_seen_before_first_pass": False,
                "attestation": "withheld synthetic",
            },
            "review_started_at_utc": "2026-07-16T20:00:00Z",
            "review_completed_at_utc": "2026-07-16T21:00:00Z",
            "responses": response_units,
            "completed": True,
        }
        self.response.write_bytes((json.dumps(response, indent=2) + "\n").encode())
        self.reveal.write_text(
            "<!doctype html><table>"
            + "".join(f"<tr><td>{unit['sample_id']}</td></tr>" for unit in self.units)
            + "</table>\n",
            encoding="utf-8",
        )
        receipt_value = {
            "report_id": "SYNTHETIC-RECEIPT",
            "report_version": "label-review-response-integrity-lock-v0.2.0",
            "repository": "drwbkr1/burnlens-deschutes",
            "task_issue": 384,
            "software_version": "0.15.0",
            "application_version": "label-review-handoff-workbench-v0.1.0",
            "evidence_origin": "returned-independent-response",
            "software_browser_fixture": False,
            "origin_declared_by_operator": True,
            "origin_verified_by_software": False,
            "software_contract_validation": "pass",
            "decision": "PASS_RESPONSE_CONTRACT_AND_HASH_LOCK_DEFER_SCIENTIFIC_USE",
            "scientific_label_fitness_established": False,
            "human_identity_verified_by_software": False,
            "reviewer_expertise_verified_by_software": False,
            "dataset_version": None,
            "split_version": None,
            "baseline_version": None,
            "model_version": None,
            "packet_binding": {"sha256": self._sha(self.packet)},
            "response_binding": {
                "bytes": self.response.stat().st_size,
                "sha256": self._sha(self.response),
                "opaque_reviewer_id": "reviewer-01",
                "unit_count": len(self.units),
            },
        }
        self.receipt.write_bytes((json.dumps(receipt_value, indent=2) + "\n").encode())
        self.contract = RevealReadinessContract(
            response_bytes=self.response.stat().st_size,
            response_sha256=self._sha(self.response),
            receipt_bytes=self.receipt.stat().st_size,
            receipt_sha256=self._sha(self.receipt),
            packet_bytes=self.packet.stat().st_size,
            packet_sha256=self._sha(self.packet),
            reveal_bytes=self.reveal.stat().st_size,
            reveal_sha256=self._sha(self.reveal),
            unit_count=len(self.units),
        )
        authorize_owner_waiver_reveal(
            repository_root=self.root,
            response_path=self.response,
            receipt_path=self.receipt,
            packet_path=self.packet,
            reveal_path=self.reveal,
            authorization_path=self.authorization,
            authorization_id=OWNER_WAIVER_ID,
            run_id="BL-SYNTHETIC-AUTHORIZATION-r001",
            authorized_at_utc="2026-07-16T21:30:00Z",
            git_source_commit="a" * 40,
            owner_waiver_confirmed=True,
            reduced_validation_acknowledged=True,
            operator_reveal_status="withheld-unopened-after-lock",
            contract=self.contract,
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @staticmethod
    def _sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _packet_unit(sample_id: str, event: str, state: str, target: int | None) -> dict:
        return {
            "sample_id": sample_id,
            "event_group_id": event,
            "row": 1,
            "column": 2,
            "pixel_center_utm10n": [3, 4],
            "reference_context_value": 1,
            "selection_hash": sample_id.lower() * 4,
            "presentation_hash": sample_id.lower() * 4,
            "proposal_state": state,
            "proposal_state_code": 1,
            "proposal_target_value": target,
            "dnbr_center": 0.2,
        }

    @staticmethod
    def _response_unit(
        sample_id: str,
        label: str,
        sufficiency: str,
        reasons: list[str],
    ) -> dict:
        return {
            "sample_id": sample_id,
            "first_pass_label": label,
            "evidence_sufficiency": sufficiency,
            "confidence": "high",
            "reason_codes": reasons,
            "notes": None,
        }

    def _run(self, **overrides: object) -> dict:
        values: dict[str, object] = {
            "repository_root": self.root,
            "authorization_path": self.authorization,
            "response_path": self.response,
            "receipt_path": self.receipt,
            "packet_path": self.packet,
            "reveal_path": self.reveal,
            "output_path": self.private_output,
            "opened_at_utc": "2026-07-16T22:40:00Z",
            "authorization_reverified_at_utc": "2026-07-16T22:40:40Z",
            "run_id": "BL-SYNTHETIC-RECONCILIATION-r001",
            "git_source_commit": "b" * 40,
            "operator_reveal_status_before_run": "opened-during-issue-403-reconciliation-preflight",
            "preflight_sequence_exception_acknowledged": True,
            "contract": self.contract,
        }
        values.update(overrides)
        return reconcile_single_reviewer(**values)

    def test_classification_rule_is_conservative_and_deterministic(self) -> None:
        results = [
            classify_unit(proposal, response)
            for proposal, response in zip(
                self.units,
                json.loads(self.response.read_text())["responses"],
                strict=True,
            )
        ]
        self.assertEqual(
            [item[1] for item in results],
            [
                "single-reviewer-supported-binary-match",
                "single-reviewer-supported-binary-match",
                "label-reason-semantic-conflict",
                "limited-or-insufficient-evidence",
                "reviewer-proposal-disagreement-or-nonbinary",
                "proposal-not-binary-candidate",
            ],
        )
        self.assertEqual([item[2] for item in results], [1, 0, None, None, None, None])

    def test_private_reconciliation_is_traceable_ignored_and_non_overwriting(self) -> None:
        report = self._run()
        self.assertEqual(report["decision"], DECISION)
        self.assertTrue(report["reveal_binding"]["opened_by_this_run"])
        self.assertFalse(
            report["reveal_binding"]["authorization_reverified_before_first_reveal_content_access"]
        )
        self.assertTrue(
            report["reveal_binding"]["authorization_reverified_before_unit_comparison"]
        )
        self.assertEqual(report["aggregate"]["accepted_candidate_units"], 2)
        self.assertEqual(report["aggregate"]["ignored_units"], 4)
        self.assertEqual(report["aggregate"]["accepted_label_counts"], {"background": 1, "burned": 1})
        self.assertEqual(len(report["decisions"]), 6)
        self.assertTrue(self.private_output.is_file())
        for item in report["decisions"]:
            self.assertIn("source_trace", item)
            self.assertIn("proposal_trace", item)
            self.assertIn("reviewer_trace", item)
        with self.assertRaisesRegex(SingleReviewerReconciliationError, "overwrite"):
            self._run()

    def test_exact_drift_and_reveal_coverage_fail_closed(self) -> None:
        original = self.reveal.read_bytes()
        self.reveal.write_bytes(original + b"drift")
        with self.assertRaisesRegex(Exception, "byte count differs"):
            self._run()
        self.reveal.write_bytes(original)
        wrong = self.reveal.read_text().replace("LRU-006", "LRU-099")
        self.reveal.write_text(wrong)
        drift_contract = RevealReadinessContract(
            **{
                **self.contract.__dict__,
                "reveal_bytes": self.reveal.stat().st_size,
                "reveal_sha256": self._sha(self.reveal),
            }
        )
        authorization = json.loads(self.authorization.read_text())
        authorization["reveal_binding"]["bytes"] = self.reveal.stat().st_size
        authorization["reveal_binding"]["sha256"] = self._sha(self.reveal)
        self.authorization.write_text(json.dumps(authorization, indent=2) + "\n")
        with self.assertRaisesRegex(SingleReviewerReconciliationError, "sample order"):
            self._run(contract=drift_contract)

    def test_public_qa_recomputes_aggregate_and_withholds_unit_content(self) -> None:
        self._run()
        report = build_single_reviewer_reconciliation_qa(
            private_reconciliation_path=self.private_output,
            generated_at_utc="2026-07-16T22:41:00Z",
            run_id="BL-SYNTHETIC-RECONCILIATION-QA-r001",
            git_source_commit="b" * 40,
        )
        serialized = json.dumps(report)
        self.assertNotIn("LRU-001", serialized)
        self.assertNotIn(self.private_output.name, serialized)
        self.assertEqual(report["aggregate"]["accepted_candidate_units"], 2)
        self.assertEqual(report["aggregate"]["ignored_units"], 4)
        output = self.root / "public"
        json_path = output / "report.json"
        html_path = output / "report.html"
        png_path = output / "report.png"
        write_single_reviewer_reconciliation_qa(
            report,
            json_path=json_path,
            html_path=html_path,
            png_path=png_path,
        )
        with Image.open(png_path) as image:
            self.assertEqual(image.size, (1800, 1280))
        self.assertIn("<main>", html_path.read_text())
        with self.assertRaisesRegex(Exception, "overwrite"):
            write_single_reviewer_reconciliation_qa(
                report,
                json_path=json_path,
                html_path=html_path,
                png_path=png_path,
            )

    def test_current_package_version_and_entry_points_are_explicit(self) -> None:
        self.assertEqual(burnlens.__version__, "0.25.0")
        pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
        self.assertIn("burnlens-run-single-reviewer-reconciliation =", pyproject)
        self.assertIn("burnlens-run-single-reviewer-reconciliation-qa =", pyproject)


if __name__ == "__main__":
    unittest.main()
