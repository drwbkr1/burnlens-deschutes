from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from PIL import Image

import burnlens
from burnlens.label_review_dual_lock_qa import (
    CURRENT_RECEIPT_SOFTWARE,
    CURRENT_RECEIPT_VERSION,
    LEGACY_RECEIPT_SOFTWARE,
    LEGACY_RECEIPT_VERSION,
    OPERATOR_REVEAL_STATUS,
    PREVIOUS_RECEIPT_SOFTWARE,
    PREVIOUS_RECEIPT_VERSION,
    RETURNED_INDEPENDENT_RESPONSE,
    SOFTWARE_BROWSER_FIXTURE,
    LabelReviewDualLockQaError,
    LockSpec,
    build_dual_lock_qa,
    write_dual_lock_outputs,
)
from burnlens.label_review_handoff import RESPONSE_TEMPLATE_NAME
from burnlens.lock_label_review_response import (
    build_response_lock,
    write_response_lock,
)


ROOT = Path(__file__).resolve().parents[1]
PACKET_DIRECTORY = ROOT / "samples" / "labels" / "review" / "phase-two"
PACKET_PATH = PACKET_DIRECTORY / "LABEL-REVIEW-PACKET-2026-001.json"
PRIVATE_ONE = "PRIVATE FIRST REVIEWER TEXT MUST NOT ENTER PUBLIC OUTPUT"
PRIVATE_TWO = "PRIVATE FIXTURE TEXT MUST NOT ENTER PUBLIC OUTPUT"


def _sha256_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _completed_response(
    *,
    reviewer_id: str,
    private_text: str,
    started_at: str,
    completed_at: str,
    offset: int,
) -> dict:
    response = json.loads(
        (PACKET_DIRECTORY / RESPONSE_TEMPLATE_NAME).read_text(encoding="utf-8")
    )
    response["reviewer"] = {
        "reviewer_id": reviewer_id,
        "independent_from_proposal_author": True,
        "burned_area_interpretation_experience": private_text,
        "proposal_seen_before_first_pass": False,
        "attestation": f"{private_text} / attestation",
    }
    response["review_started_at_utc"] = started_at
    response["review_completed_at_utc"] = completed_at
    response["completed"] = True
    labels = ["burned", "background", "uncertain", "unusable"]
    for index, item in enumerate(response["responses"]):
        item.update(
            {
                "first_pass_label": labels[(index + offset) % len(labels)],
                "evidence_sufficiency": "limited" if index % 2 else "sufficient",
                "confidence": "medium",
                "reason_codes": ["low-severity-ambiguity"],
                "notes": private_text if index == 0 else None,
            }
        )
    return response


def _private_pair(
    root: Path,
    *,
    name: str,
    reviewer_id: str,
    private_text: str,
    started_at: str,
    completed_at: str,
    received_at: str,
    offset: int,
    origin: str,
    task_issue: int,
    report_version: str,
    software_version: str,
) -> tuple[Path, Path]:
    root.mkdir(parents=True, exist_ok=True)
    response_path = root / f"{name}-response.json"
    response_path.write_text(
        json.dumps(
            _completed_response(
                reviewer_id=reviewer_id,
                private_text=private_text,
                started_at=started_at,
                completed_at=completed_at,
                offset=offset,
            ),
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    receipt = build_response_lock(
        packet_path=PACKET_PATH,
        response_path=response_path,
        receipt_id=f"LABEL-REVIEW-RESPONSE-LOCK-TEST-{name.upper()}",
        received_at_utc=received_at,
        run_id=f"BL-TEST-DUAL-LOCK-{name.upper()}",
        git_source_commit=("1" if name == "one" else "2") * 40,
        evidence_origin=origin,
        task_issue=task_issue,
        report_version=report_version,
        software_version=software_version,
    )
    receipt_path = root / f"{name}-receipt.json"
    write_response_lock(receipt, receipt_path)
    return response_path, receipt_path


def _spec(
    response_path: Path,
    receipt_path: Path,
    *,
    reviewer_id: str,
    task_issue: int,
    report_version: str,
    software_version: str,
    origin: str,
) -> LockSpec:
    return LockSpec(
        response_path=response_path,
        receipt_path=receipt_path,
        expected_response_sha256=_sha256_file(response_path),
        expected_response_bytes=response_path.stat().st_size,
        expected_receipt_sha256=_sha256_file(receipt_path),
        expected_receipt_bytes=receipt_path.stat().st_size,
        expected_reviewer_id=reviewer_id,
        expected_task_issue=task_issue,
        expected_receipt_version=report_version,
        expected_receipt_software=software_version,
        expected_origin=origin,
    )


def _readiness_specs(root: Path) -> list[LockSpec]:
    first_response, first_receipt = _private_pair(
        root,
        name="one",
        reviewer_id="reviewer-01",
        private_text=PRIVATE_ONE,
        started_at="2026-07-16T17:10:00Z",
        completed_at="2026-07-16T17:20:00Z",
        received_at="2026-07-16T17:21:00Z",
        offset=0,
        origin=RETURNED_INDEPENDENT_RESPONSE,
        task_issue=384,
        report_version=LEGACY_RECEIPT_VERSION,
        software_version=LEGACY_RECEIPT_SOFTWARE,
    )
    second_response, second_receipt = _private_pair(
        root,
        name="two",
        reviewer_id="browser-qa-fixture-not-human",
        private_text=PRIVATE_TWO,
        started_at="2026-07-16T18:04:09Z",
        completed_at="2026-07-16T18:04:10Z",
        received_at="2026-07-16T18:05:00Z",
        offset=1,
        origin=SOFTWARE_BROWSER_FIXTURE,
        task_issue=394,
        report_version=CURRENT_RECEIPT_VERSION,
        software_version=CURRENT_RECEIPT_SOFTWARE,
    )
    return [
        _spec(
            first_response,
            first_receipt,
            reviewer_id="reviewer-01",
            task_issue=384,
            report_version=LEGACY_RECEIPT_VERSION,
            software_version=LEGACY_RECEIPT_SOFTWARE,
            origin=RETURNED_INDEPENDENT_RESPONSE,
        ),
        _spec(
            second_response,
            second_receipt,
            reviewer_id="browser-qa-fixture-not-human",
            task_issue=394,
            report_version=CURRENT_RECEIPT_VERSION,
            software_version=CURRENT_RECEIPT_SOFTWARE,
            origin=SOFTWARE_BROWSER_FIXTURE,
        ),
    ]


def _build(root: Path, specs: list[LockSpec] | None = None) -> dict:
    return build_dual_lock_qa(
        packet_path=PACKET_PATH,
        locks=specs or _readiness_specs(root),
        generated_at_utc="2026-07-16T19:40:00Z",
        run_id="BL-TEST-DUAL-LOCK-READINESS-QA",
        git_source_commit="3" * 40,
        operator_reveal_status=OPERATOR_REVEAL_STATUS,
    )


class LabelReviewDualLockQaTests(unittest.TestCase):
    def test_mixed_legacy_current_readiness_is_content_withheld(self) -> None:
        with TemporaryDirectory() as temporary:
            report = _build(Path(temporary))
            self.assertEqual(
                report["decision"],
                "PASS_MIXED_VERSION_DUAL_LOCK_READINESS_ONE_RETURNED_ONE_FIXTURE_NO_REVEAL",
            )
            self.assertEqual(report["origin_classification"]["operator_declared_returned_responses"], 1)
            self.assertEqual(report["origin_classification"]["software_browser_fixtures"], 1)
            self.assertFalse(report["custody_state"]["minimum_custody_count_met"])
            self.assertFalse(report["custody_state"]["reveal_authorized_by_this_run"])
            self.assertFalse(report["custody_state"]["adjudication_ready"])
            self.assertEqual(
                report["checks"]["mixed_receipt_version_compatibility"],
                "pass",
            )
            serialized = json.dumps(report)
            self.assertNotIn(PRIVATE_ONE, serialized)
            self.assertNotIn(PRIVATE_TWO, serialized)
            self.assertNotIn('"label_counts"', serialized)
            self.assertNotIn('"responses"', serialized)
            self.assertNotIn("one-response.json", serialized)
            self.assertNotIn("two-receipt.json", serialized)

    def test_two_returned_origin_locks_still_do_not_authorize_reveal(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            specs = _readiness_specs(root)
            second = specs[1]
            second_response = json.loads(second.response_path.read_text(encoding="utf-8"))
            second_response["reviewer"]["burned_area_interpretation_experience"] = PRIVATE_TWO
            second.response_path.write_text(
                json.dumps(second_response, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            second.receipt_path.unlink()
            receipt = build_response_lock(
                packet_path=PACKET_PATH,
                response_path=second.response_path,
                receipt_id="LABEL-REVIEW-RESPONSE-LOCK-TEST-TWO-RETURNED",
                received_at_utc="2026-07-16T18:05:00Z",
                run_id="BL-TEST-DUAL-LOCK-TWO-RETURNED",
                git_source_commit="2" * 40,
                evidence_origin=RETURNED_INDEPENDENT_RESPONSE,
                task_issue=394,
            )
            write_response_lock(receipt, second.receipt_path)
            specs[1] = _spec(
                second.response_path,
                second.receipt_path,
                reviewer_id="browser-qa-fixture-not-human",
                task_issue=394,
                report_version=CURRENT_RECEIPT_VERSION,
                software_version=CURRENT_RECEIPT_SOFTWARE,
                origin=RETURNED_INDEPENDENT_RESPONSE,
            )
            report = _build(root, specs)
            self.assertEqual(
                report["decision"],
                "PASS_TWO_RETURNED_RESPONSE_CUSTODY_LOCKS_WITHHOLD_CONTENT_DEFER_REVEAL",
            )
            self.assertTrue(report["custody_state"]["minimum_custody_count_met"])
            self.assertFalse(report["custody_state"]["reveal_authorized_by_this_run"])
            self.assertFalse(report["custody_state"]["adjudication_ready"])

    def test_previous_receipt_identity_keeps_historical_report_identity(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            specs = _readiness_specs(root)
            previous_response, previous_receipt = _private_pair(
                root,
                name="previous",
                reviewer_id="browser-qa-fixture-not-human",
                private_text=PRIVATE_TWO,
                started_at="2026-07-16T18:04:09Z",
                completed_at="2026-07-16T18:04:10Z",
                received_at="2026-07-16T18:05:00Z",
                offset=1,
                origin=SOFTWARE_BROWSER_FIXTURE,
                task_issue=394,
                report_version=PREVIOUS_RECEIPT_VERSION,
                software_version=PREVIOUS_RECEIPT_SOFTWARE,
            )
            specs[1] = _spec(
                previous_response,
                previous_receipt,
                reviewer_id="browser-qa-fixture-not-human",
                task_issue=394,
                report_version=PREVIOUS_RECEIPT_VERSION,
                software_version=PREVIOUS_RECEIPT_SOFTWARE,
                origin=SOFTWARE_BROWSER_FIXTURE,
            )
            report = _build(root, specs)
            self.assertEqual(
                report["report_version"],
                "label-review-dual-lock-readiness-qa-v0.1.0",
            )
            self.assertEqual(report["software_version"], "0.17.0")
            self.assertEqual(report["checks"]["mixed_receipt_version_compatibility"], "pass")

    def test_invalid_public_task_issue_fails_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(LabelReviewDualLockQaError, "positive integer"):
                build_dual_lock_qa(
                    packet_path=PACKET_PATH,
                    locks=_readiness_specs(root),
                    generated_at_utc="2026-07-16T19:40:00Z",
                    run_id="BL-TEST-DUAL-LOCK-READINESS-QA",
                    git_source_commit="3" * 40,
                    operator_reveal_status=OPERATOR_REVEAL_STATUS,
                    task_issue=0,
                )

    def test_duplicate_and_receipt_drift_fail_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            specs = _readiness_specs(root)
            duplicate = deepcopy(specs[1])
            duplicate = LockSpec(
                response_path=specs[0].response_path,
                receipt_path=duplicate.receipt_path,
                expected_response_sha256=_sha256_file(specs[0].response_path),
                expected_response_bytes=specs[0].response_path.stat().st_size,
                expected_receipt_sha256=duplicate.expected_receipt_sha256,
                expected_receipt_bytes=duplicate.expected_receipt_bytes,
                expected_reviewer_id=specs[0].expected_reviewer_id,
                expected_task_issue=duplicate.expected_task_issue,
                expected_receipt_version=duplicate.expected_receipt_version,
                expected_receipt_software=duplicate.expected_receipt_software,
                expected_origin=duplicate.expected_origin,
            )
            with self.assertRaises(LabelReviewDualLockQaError):
                _build(root, [specs[0], duplicate])

            receipt = json.loads(specs[1].receipt_path.read_text(encoding="utf-8"))
            receipt["task_issue"] = 999
            specs[1].receipt_path.write_text(
                json.dumps(receipt) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            drifted = deepcopy(specs[1])
            drifted = LockSpec(
                **{
                    **drifted.__dict__,
                    "expected_receipt_sha256": _sha256_file(drifted.receipt_path),
                    "expected_receipt_bytes": drifted.receipt_path.stat().st_size,
                }
            )
            with self.assertRaisesRegex(LabelReviewDualLockQaError, "task issue differs"):
                _build(root, [specs[0], drifted])

    def test_outputs_are_semantic_rendered_and_non_overwriting(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            report = _build(root)
            json_path = root / "public.json"
            html_path = root / "public.html"
            png_path = root / "public.png"
            write_dual_lock_outputs(
                report,
                json_path=json_path,
                html_path=html_path,
                png_path=png_path,
            )
            with Image.open(png_path) as image:
                self.assertEqual(image.size, (1800, 1320))
            html = html_path.read_text(encoding="utf-8")
            self.assertIn("<main>", html)
            self.assertIn("Dual-lock custody readiness", html)
            self.assertIn("Software fixtures:</strong> 1", html)
            self.assertNotIn(PRIVATE_ONE, html)
            self.assertNotIn(PRIVATE_TWO, html)
            with self.assertRaisesRegex(LabelReviewDualLockQaError, "overwrite"):
                write_dual_lock_outputs(
                    report,
                    json_path=json_path,
                    html_path=html_path,
                    png_path=png_path,
                )

    def test_current_versions_and_verifier_independence_are_explicit(self) -> None:
        self.assertEqual(burnlens.__version__, "0.40.0")
        source = (ROOT / "burnlens" / "label_review_dual_lock_qa.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("lock_label_review_response", source)
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn(
            'burnlens-run-label-review-dual-lock-qa = "burnlens.run_label_review_dual_lock_qa:main"',
            pyproject,
        )


if __name__ == "__main__":
    unittest.main()
