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
    DECISION,
    OWNER_WAIVER_ID,
    OwnerWaiverRevealReadinessError,
    RevealReadinessContract,
    authorize_owner_waiver_reveal,
    verify_owner_waiver_reveal_authorization,
)
from burnlens.owner_waiver_reveal_readiness_qa import (
    build_owner_waiver_reveal_readiness_qa,
    write_owner_waiver_reveal_readiness_qa,
)


class OwnerWaiverRevealReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / ".gitignore").write_text("downloads/\n", encoding="utf-8")
        self.response = self.root / "inputs" / "response.json"
        self.receipt = self.root / "inputs" / "receipt.json"
        self.packet = self.root / "inputs" / "packet.json"
        self.reveal = self.root / "inputs" / "reveal.html"
        self.response.parent.mkdir(parents=True)
        self.response.write_bytes(b'{"synthetic":"response-bytes-only"}\n')
        self.packet.write_bytes(b'{"synthetic":"packet-bytes-only"}\n')
        self.reveal.write_bytes(b"<!doctype html><title>synthetic reveal bytes</title>\n")
        response_sha = self._sha(self.response)
        packet_sha = self._sha(self.packet)
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
            "packet_binding": {"sha256": packet_sha},
            "response_binding": {
                "bytes": self.response.stat().st_size,
                "sha256": response_sha,
                "opaque_reviewer_id": "reviewer-01",
                "unit_count": 56,
            },
        }
        self.receipt.write_bytes(
            (json.dumps(receipt_value, indent=2, ensure_ascii=True) + "\n").encode("utf-8")
        )
        self.contract = RevealReadinessContract(
            response_bytes=self.response.stat().st_size,
            response_sha256=response_sha,
            receipt_bytes=self.receipt.stat().st_size,
            receipt_sha256=self._sha(self.receipt),
            packet_bytes=self.packet.stat().st_size,
            packet_sha256=packet_sha,
            reveal_bytes=self.reveal.stat().st_size,
            reveal_sha256=self._sha(self.reveal),
        )
        self.authorization = self.root / "downloads" / "private" / "authorization.json"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @staticmethod
    def _sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _authorize(self, **overrides: object) -> dict:
        values: dict[str, object] = {
            "repository_root": self.root,
            "response_path": self.response,
            "receipt_path": self.receipt,
            "packet_path": self.packet,
            "reveal_path": self.reveal,
            "authorization_path": self.authorization,
            "authorization_id": OWNER_WAIVER_ID,
            "run_id": "BL-SYNTHETIC-OWNER-WAIVER-r001",
            "authorized_at_utc": "2026-07-16T22:30:00Z",
            "git_source_commit": "a" * 40,
            "owner_waiver_confirmed": True,
            "reduced_validation_acknowledged": True,
            "operator_reveal_status": "withheld-unopened-after-lock",
            "contract": self.contract,
        }
        values.update(overrides)
        return authorize_owner_waiver_reveal(**values)

    def test_exact_gate_authorizes_only_later_reconciliation(self) -> None:
        report = self._authorize()
        self.assertEqual(report["decision"], DECISION)
        self.assertTrue(self.authorization.is_file())
        self.assertFalse(report["evidence_state"]["reveal_opened_by_this_run"])
        self.assertTrue(
            report["authorization_scope"]["reveal_authorized_for_later_private_reconciliation"]
        )
        self.assertEqual(report["evidence_state"]["returned_independent_responses"], 1)
        self.assertFalse(report["evidence_state"]["second_human_response_present"])
        verified = verify_owner_waiver_reveal_authorization(
            authorization_path=self.authorization,
            response_path=self.response,
            receipt_path=self.receipt,
            packet_path=self.packet,
            reveal_path=self.reveal,
            contract=self.contract,
        )
        self.assertEqual(verified, report)

    def test_missing_waiver_risk_acknowledgement_and_wrong_status_fail(self) -> None:
        with self.assertRaisesRegex(OwnerWaiverRevealReadinessError, "owner waiver"):
            self._authorize(owner_waiver_confirmed=False)
        with self.assertRaisesRegex(OwnerWaiverRevealReadinessError, "reduced-validation"):
            self._authorize(reduced_validation_acknowledged=False)
        with self.assertRaisesRegex(OwnerWaiverRevealReadinessError, "unopened"):
            self._authorize(operator_reveal_status="opened")
        self.assertFalse(self.authorization.exists())

    def test_drift_fixture_receipt_and_overwrite_fail_closed(self) -> None:
        original = self.reveal.read_bytes()
        self.reveal.write_bytes(original + b"drift")
        with self.assertRaisesRegex(OwnerWaiverRevealReadinessError, "byte count differs"):
            self._authorize()
        self.reveal.write_bytes(original)
        receipt = json.loads(self.receipt.read_text(encoding="utf-8"))
        receipt["software_browser_fixture"] = True
        self.receipt.write_bytes(
            (json.dumps(receipt, indent=2, ensure_ascii=True) + "\n").encode("utf-8")
        )
        fixture_contract = RevealReadinessContract(
            **{
                **self.contract.__dict__,
                "receipt_bytes": self.receipt.stat().st_size,
                "receipt_sha256": self._sha(self.receipt),
            }
        )
        with self.assertRaisesRegex(OwnerWaiverRevealReadinessError, "software fixture"):
            self._authorize(contract=fixture_contract)
        self.receipt.unlink()
        self.setUp_receipt_again()
        self._authorize()
        with self.assertRaisesRegex(OwnerWaiverRevealReadinessError, "overwrite"):
            self._authorize()

    def setUp_receipt_again(self) -> None:
        response_sha = self._sha(self.response)
        packet_sha = self._sha(self.packet)
        value = {
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
            "packet_binding": {"sha256": packet_sha},
            "response_binding": {
                "bytes": self.response.stat().st_size,
                "sha256": response_sha,
                "opaque_reviewer_id": "reviewer-01",
                "unit_count": 56,
            },
        }
        self.receipt.write_bytes((json.dumps(value, indent=2) + "\n").encode())
        self.contract = RevealReadinessContract(
            response_bytes=self.response.stat().st_size,
            response_sha256=response_sha,
            receipt_bytes=self.receipt.stat().st_size,
            receipt_sha256=self._sha(self.receipt),
            packet_bytes=self.packet.stat().st_size,
            packet_sha256=packet_sha,
            reveal_bytes=self.reveal.stat().st_size,
            reveal_sha256=self._sha(self.reveal),
        )

    def test_public_qa_is_content_withheld_rendered_and_non_overwriting(self) -> None:
        self._authorize()
        report = build_owner_waiver_reveal_readiness_qa(
            authorization_path=self.authorization,
            response_path=self.response,
            receipt_path=self.receipt,
            packet_path=self.packet,
            reveal_path=self.reveal,
            generated_at_utc="2026-07-16T22:31:00Z",
            run_id="BL-SYNTHETIC-OWNER-WAIVER-QA-r001",
            git_source_commit="a" * 40,
            contract=self.contract,
        )
        serialized = json.dumps(report)
        self.assertNotIn(self.response.name, serialized)
        self.assertNotIn(self.receipt.name, serialized)
        self.assertNotIn("label_counts", serialized)
        self.assertFalse(report["reveal_state"]["reveal_opened_by_qa_run"])
        self.assertFalse(report["owner_waiver_state"]["inter_rater_validation_available"])
        output = self.root / "public"
        json_path = output / "report.json"
        html_path = output / "report.html"
        png_path = output / "report.png"
        write_owner_waiver_reveal_readiness_qa(
            report,
            json_path=json_path,
            html_path=html_path,
            png_path=png_path,
        )
        with Image.open(png_path) as image:
            self.assertEqual(image.size, (1800, 1280))
        self.assertIn("<main>", html_path.read_text(encoding="utf-8"))
        with self.assertRaisesRegex(Exception, "overwrite"):
            write_owner_waiver_reveal_readiness_qa(
                report,
                json_path=json_path,
                html_path=html_path,
                png_path=png_path,
            )

    def test_current_package_version_and_entry_points_are_explicit(self) -> None:
        self.assertEqual(burnlens.__version__, "0.33.0")
        pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('burnlens-authorize-label-review-reveal =', pyproject)
        self.assertIn('burnlens-run-owner-waiver-reveal-readiness-qa =', pyproject)


if __name__ == "__main__":
    unittest.main()
