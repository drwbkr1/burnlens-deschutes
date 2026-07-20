from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from PIL import Image

import burnlens
from burnlens.label_review_handoff import RESPONSE_TEMPLATE_NAME
from burnlens.label_review_response_lock_qa import (
    OPERATOR_REVEAL_STATUS,
    LabelReviewResponseLockQaError,
    build_public_response_lock_qa,
    write_public_response_lock_outputs,
)
from burnlens.lock_label_review_response import (
    LEGACY_LOCK_REPORT_VERSION,
    LEGACY_SOFTWARE_VERSION,
    RETURNED_INDEPENDENT_RESPONSE,
    build_response_lock,
    write_response_lock,
)


ROOT = Path(__file__).resolve().parents[1]
PACKET_DIRECTORY = ROOT / "samples" / "labels" / "review" / "phase-two"
PACKET_PATH = PACKET_DIRECTORY / "LABEL-REVIEW-PACKET-2026-001.json"
PRIVATE_TEXT = "PRIVATE REVIEWER TEXT MUST NEVER ENTER PUBLIC EVIDENCE"
REVIEWER_ID = "opaque-reviewer-test-only"


def _sha256_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _completed_response() -> dict:
    response = json.loads(
        (PACKET_DIRECTORY / RESPONSE_TEMPLATE_NAME).read_text(encoding="utf-8")
    )
    response["reviewer"] = {
        "reviewer_id": REVIEWER_ID,
        "independent_from_proposal_author": True,
        "burned_area_interpretation_experience": PRIVATE_TEXT,
        "proposal_seen_before_first_pass": False,
        "attestation": f"{PRIVATE_TEXT} / attestation",
    }
    response["review_started_at_utc"] = "2026-07-16T17:10:00Z"
    response["review_completed_at_utc"] = "2026-07-16T17:20:00Z"
    response["completed"] = True
    labels = ["burned", "background", "uncertain", "unusable"]
    for index, item in enumerate(response["responses"]):
        item.update(
            {
                "first_pass_label": labels[index % len(labels)],
                "evidence_sufficiency": "limited",
                "confidence": "medium",
                "reason_codes": ["low-severity-ambiguity"],
                "notes": PRIVATE_TEXT if index == 0 else None,
            }
        )
    return response


def _private_pair(root: Path) -> tuple[Path, Path]:
    root.mkdir(parents=True, exist_ok=True)
    response_path = root / "private-response.json"
    response_path.write_text(
        json.dumps(_completed_response(), indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    receipt = build_response_lock(
        packet_path=PACKET_PATH,
        response_path=response_path,
        receipt_id="LABEL-REVIEW-RESPONSE-LOCK-TEST-001",
        received_at_utc="2026-07-16T17:21:00Z",
        run_id="BL-TEST-RETURNED-RESPONSE-LOCK",
        git_source_commit="2" * 40,
        evidence_origin=RETURNED_INDEPENDENT_RESPONSE,
        task_issue=384,
        report_version=LEGACY_LOCK_REPORT_VERSION,
        software_version=LEGACY_SOFTWARE_VERSION,
    )
    receipt_path = root / "private-receipt.json"
    write_response_lock(receipt, receipt_path)
    return response_path, receipt_path


def _build(root: Path) -> dict:
    response_path, receipt_path = _private_pair(root)
    return build_public_response_lock_qa(
        packet_path=PACKET_PATH,
        response_path=response_path,
        receipt_path=receipt_path,
        generated_at_utc="2026-07-16T17:25:00Z",
        run_id="BL-TEST-PUBLIC-RESPONSE-LOCK-QA",
        git_source_commit="3" * 40,
        expected_response_sha256=_sha256_file(response_path),
        expected_response_bytes=response_path.stat().st_size,
        expected_receipt_sha256=_sha256_file(receipt_path),
        expected_receipt_bytes=receipt_path.stat().st_size,
        expected_reviewer_id=REVIEWER_ID,
        operator_reveal_status=OPERATOR_REVEAL_STATUS,
    )


class LabelReviewResponseLockQaTests(unittest.TestCase):
    def test_public_report_validates_exact_private_pair_without_content_leakage(self) -> None:
        with TemporaryDirectory() as temporary:
            report = _build(Path(temporary))
            self.assertEqual(
                report["decision"],
                "PASS_FIRST_RETURNED_RESPONSE_CONTRACT_AND_HASH_LOCK_WITHHOLD_CONTENT_DEFER_DATASET",
            )
            self.assertEqual(report["returned_response_count"], 1)
            self.assertFalse(report["adjudication_ready"])
            self.assertTrue(report["private_response_binding"]["content_distribution_withheld"])
            serialized = json.dumps(report)
            self.assertNotIn(PRIVATE_TEXT, serialized)
            self.assertNotIn('"label_counts"', serialized)
            self.assertNotIn('"responses"', serialized)
            self.assertNotIn("private-response.json", serialized)
            self.assertNotIn("private-receipt.json", serialized)

    def test_public_verifier_rejects_response_or_receipt_binding_drift(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            response_path, receipt_path = _private_pair(root)
            expected_response_hash = _sha256_file(response_path)
            expected_receipt_hash = _sha256_file(receipt_path)
            response = json.loads(response_path.read_text(encoding="utf-8"))
            response["responses"][0]["confidence"] = "high"
            response_path.write_text(json.dumps(response) + "\n", encoding="utf-8", newline="\n")
            with self.assertRaisesRegex(LabelReviewResponseLockQaError, "response SHA-256 differs"):
                build_public_response_lock_qa(
                    packet_path=PACKET_PATH,
                    response_path=response_path,
                    receipt_path=receipt_path,
                    generated_at_utc="2026-07-16T17:25:00Z",
                    run_id="BL-TEST-TAMPER",
                    git_source_commit="3" * 40,
                    expected_response_sha256=expected_response_hash,
                    expected_response_bytes=response_path.stat().st_size,
                    expected_receipt_sha256=expected_receipt_hash,
                    expected_receipt_bytes=receipt_path.stat().st_size,
                    expected_reviewer_id=REVIEWER_ID,
                    operator_reveal_status=OPERATOR_REVEAL_STATUS,
                )

            response_path, receipt_path = _private_pair(root / "second")
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["response_binding"]["sha256"] = "0" * 64
            receipt_path.write_text(json.dumps(receipt) + "\n", encoding="utf-8", newline="\n")
            with self.assertRaisesRegex(LabelReviewResponseLockQaError, "receipt response hash differs"):
                build_public_response_lock_qa(
                    packet_path=PACKET_PATH,
                    response_path=response_path,
                    receipt_path=receipt_path,
                    generated_at_utc="2026-07-16T17:25:00Z",
                    run_id="BL-TEST-RECEIPT-TAMPER",
                    git_source_commit="3" * 40,
                    expected_response_sha256=_sha256_file(response_path),
                    expected_response_bytes=response_path.stat().st_size,
                    expected_receipt_sha256=_sha256_file(receipt_path),
                    expected_receipt_bytes=receipt_path.stat().st_size,
                    expected_reviewer_id=REVIEWER_ID,
                    operator_reveal_status=OPERATOR_REVEAL_STATUS,
                )

    def test_public_outputs_are_semantic_rendered_and_content_withheld(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            report = _build(root)
            json_path = root / "public.json"
            html_path = root / "public.html"
            png_path = root / "public.png"
            write_public_response_lock_outputs(
                report,
                json_path=json_path,
                html_path=html_path,
                png_path=png_path,
            )
            with Image.open(png_path) as image:
                self.assertEqual(image.size, (1800, 1320))
            html = html_path.read_text(encoding="utf-8")
            self.assertIn("<main>", html)
            self.assertIn("Response distribution withheld", html)
            self.assertIn(report["private_response_binding"]["sha256"], html)
            self.assertNotIn(PRIVATE_TEXT, html)
            with self.assertRaisesRegex(LabelReviewResponseLockQaError, "overwrite"):
                write_public_response_lock_outputs(
                    report,
                    json_path=json_path,
                    html_path=html_path,
                    png_path=png_path,
                )

    def test_current_version_and_verifier_independence_are_explicit(self) -> None:
        self.assertEqual(burnlens.__version__, "0.35.0")
        source = (ROOT / "burnlens" / "label_review_response_lock_qa.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("lock_label_review_response", source)
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn(
            'burnlens-run-label-review-response-lock-qa = "burnlens.run_label_review_response_lock_qa:main"',
            pyproject,
        )


if __name__ == "__main__":
    unittest.main()
