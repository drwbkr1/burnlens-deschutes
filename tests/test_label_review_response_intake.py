from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from PIL import Image

import burnlens
from burnlens.label_review_handoff import RESPONSE_TEMPLATE_NAME
from burnlens.label_review_response_intake import (
    LabelReviewResponseIntakeError,
    _promote_without_overwrite,
    _write_temporary_response,
    intake_label_review_response,
)
from burnlens.label_review_response_intake_qa import (
    LabelReviewResponseIntakeQaError,
    build_response_intake_qa,
    write_response_intake_qa,
)
from burnlens.lock_label_review_response import (
    LOCK_REPORT_VERSION,
    RETURNED_INDEPENDENT_RESPONSE,
    SOFTWARE_BROWSER_FIXTURE,
    SOFTWARE_VERSION,
)


ROOT = Path(__file__).resolve().parents[1]
PACKET_DIRECTORY = ROOT / "samples" / "labels" / "review" / "phase-two"
PACKET_PATH = PACKET_DIRECTORY / "LABEL-REVIEW-PACKET-2026-001.json"
SOURCE_COMMIT = "4" * 40
FIRST_RESPONSE_SHA256 = "485e80f2563f8b723c16daa8b5e5a1172dd88e8f2a28a7dd8608c933fa64eed9"


def _completed_response(reviewer_id: str = "reviewer-02") -> dict:
    response = json.loads(
        (PACKET_DIRECTORY / RESPONSE_TEMPLATE_NAME).read_text(encoding="utf-8")
    )
    response["reviewer"] = {
        "reviewer_id": reviewer_id,
        "independent_from_proposal_author": True,
        "burned_area_interpretation_experience": "software fixture experience",
        "proposal_seen_before_first_pass": False,
        "attestation": "software fixture attestation",
    }
    response["review_started_at_utc"] = "2026-07-16T21:00:00Z"
    response["review_completed_at_utc"] = "2026-07-16T21:05:00Z"
    response["completed"] = True
    labels = ["burned", "background", "uncertain", "unusable"]
    for index, item in enumerate(response["responses"]):
        item.update(
            {
                "first_pass_label": labels[index % len(labels)],
                "evidence_sufficiency": "limited",
                "confidence": "medium",
                "reason_codes": ["low-severity-ambiguity"],
                "notes": None,
            }
        )
    return response


def _initialize_repository(root: Path, *, ignored: bool = True) -> None:
    subprocess.run(["git", "init", "--quiet", str(root)], check=True)
    if ignored:
        (root / ".gitignore").write_text("downloads/\n", encoding="utf-8", newline="\n")


def _source(root: Path, reviewer_id: str = "reviewer-02") -> Path:
    path = root / "inbound" / "response.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_completed_response(reviewer_id), indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def _intake(
    repository: Path,
    source: Path,
    *,
    reviewer_id: str = "reviewer-02",
    disallowed_hashes: list[str] | None = None,
    disallowed_reviewers: list[str] | None = None,
    evidence_origin: str = SOFTWARE_BROWSER_FIXTURE,
) -> dict:
    return intake_label_review_response(
        repository_root=repository,
        packet_path=PACKET_PATH,
        source_response_path=source,
        custody_directory=repository / "downloads" / "phase-two" / "reviewer-responses" / "test",
        preserved_response_name="PRESERVED-RESPONSE.json",
        receipt_name="PRIVATE-RECEIPT.json",
        expected_reviewer_id=reviewer_id,
        receipt_id="LABEL-REVIEW-RESPONSE-LOCK-TEST-ATOMIC",
        received_at_utc="2026-07-16T21:06:00Z",
        run_id="BL-TEST-ATOMIC-RESPONSE-INTAKE",
        git_source_commit=SOURCE_COMMIT,
        task_issue=402,
        disallowed_response_sha256=disallowed_hashes or [FIRST_RESPONSE_SHA256],
        disallowed_reviewer_ids=disallowed_reviewers or ["reviewer-01"],
        evidence_origin=evidence_origin,
    )


class LabelReviewResponseIntakeTests(unittest.TestCase):
    def test_atomic_intake_preserves_exact_bytes_and_current_receipt(self) -> None:
        with TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repo"
            repository.mkdir()
            _initialize_repository(repository)
            source = _source(repository)
            source_bytes = source.read_bytes()
            report = _intake(
                repository,
                source,
                evidence_origin=RETURNED_INDEPENDENT_RESPONSE,
            )
            custody = repository / "downloads" / "phase-two" / "reviewer-responses" / "test"
            preserved = custody / "PRESERVED-RESPONSE.json"
            receipt_path = custody / "PRIVATE-RECEIPT.json"

            self.assertEqual(preserved.read_bytes(), source_bytes)
            self.assertEqual(report["source_binding"]["sha256"], sha256(source_bytes).hexdigest())
            self.assertEqual(
                report["source_binding"]["sha256"],
                report["preserved_response_binding"]["sha256"],
            )
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(receipt["report_version"], LOCK_REPORT_VERSION)
            self.assertEqual(receipt["software_version"], SOFTWARE_VERSION)
            self.assertEqual(
                receipt["reveal_release"],
                "prohibited until a separate public owner-waiver and reveal-readiness "
                "checkpoint authorizes reveal",
            )
            self.assertFalse(report["reveal_authorized_by_this_intake"])
            self.assertIsNone(report["qualifying_independent_human_response"])
            self.assertFalse(report["software_browser_fixture"])
            self.assertNotIn(str(source), json.dumps(report))
            self.assertNotIn("PRESERVED-RESPONSE.json", json.dumps(report))
            ignored = subprocess.run(
                ["git", "-C", str(repository), "check-ignore", "--quiet", str(preserved)],
                check=False,
            )
            self.assertEqual(ignored.returncode, 0)

    def test_overwrite_duplicate_reviewer_and_unignored_destinations_fail_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repo"
            repository.mkdir()
            _initialize_repository(repository)
            source = _source(repository)
            report = _intake(repository, source)
            with self.assertRaisesRegex(LabelReviewResponseIntakeError, "overwrite"):
                _intake(repository, source)

            second_repository = Path(temporary) / "second"
            second_repository.mkdir()
            _initialize_repository(second_repository)
            duplicate_source = _source(second_repository)
            with self.assertRaisesRegex(LabelReviewResponseIntakeError, "duplicates disallowed"):
                _intake(
                    second_repository,
                    duplicate_source,
                    disallowed_hashes=[report["source_binding"]["sha256"]],
                )

            third_repository = Path(temporary) / "third"
            third_repository.mkdir()
            _initialize_repository(third_repository)
            third_source = _source(third_repository)
            with self.assertRaisesRegex(LabelReviewResponseIntakeError, "reviewer ID duplicates"):
                _intake(
                    third_repository,
                    third_source,
                    disallowed_reviewers=["reviewer-01", "reviewer-02"],
                )

            unignored_repository = Path(temporary) / "unignored"
            unignored_repository.mkdir()
            _initialize_repository(unignored_repository, ignored=False)
            unignored_source = _source(unignored_repository)
            with self.assertRaisesRegex(LabelReviewResponseIntakeError, "not covered"):
                _intake(unignored_repository, unignored_source)

            symlink_repository = Path(temporary) / "symlink"
            symlink_repository.mkdir()
            _initialize_repository(symlink_repository)
            symlink_source = _source(symlink_repository)
            real_custody = symlink_repository / "downloads" / "real-custody"
            real_custody.mkdir(parents=True)
            linked_custody = symlink_repository / "downloads" / "linked-custody"
            try:
                linked_custody.symlink_to(real_custody, target_is_directory=True)
            except OSError:
                pass
            else:
                with self.assertRaisesRegex(LabelReviewResponseIntakeError, "symbolic link"):
                    intake_label_review_response(
                        repository_root=symlink_repository,
                        packet_path=PACKET_PATH,
                        source_response_path=symlink_source,
                        custody_directory=linked_custody,
                        preserved_response_name="PRESERVED-RESPONSE.json",
                        receipt_name="PRIVATE-RECEIPT.json",
                        expected_reviewer_id="reviewer-02",
                        receipt_id="LABEL-REVIEW-RESPONSE-LOCK-TEST-ATOMIC",
                        received_at_utc="2026-07-16T21:06:00Z",
                        run_id="BL-TEST-ATOMIC-RESPONSE-INTAKE",
                        git_source_commit=SOURCE_COMMIT,
                        task_issue=402,
                        disallowed_response_sha256=[FIRST_RESPONSE_SHA256],
                        disallowed_reviewer_ids=["reviewer-01"],
                        evidence_origin=SOFTWARE_BROWSER_FIXTURE,
                    )

    def test_source_drift_and_receipt_promotion_failure_roll_back_outputs(self) -> None:
        with TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repo"
            repository.mkdir()
            _initialize_repository(repository)
            source = _source(repository)

            def copy_then_mutate(source_path: Path, destination: Path):
                result = _write_temporary_response(source_path, destination)
                source_path.write_bytes(source_path.read_bytes() + b" ")
                return result

            with patch(
                "burnlens.label_review_response_intake._write_temporary_response",
                side_effect=copy_then_mutate,
            ):
                with self.assertRaisesRegex(LabelReviewResponseIntakeError, "changed during"):
                    _intake(repository, source)
            custody = repository / "downloads" / "phase-two" / "reviewer-responses" / "test"
            self.assertFalse((custody / "PRESERVED-RESPONSE.json").exists())
            self.assertFalse((custody / "PRIVATE-RECEIPT.json").exists())
            self.assertEqual(list(custody.glob(".burnlens-response-intake-*")), [])

            source = _source(repository)
            call_count = 0

            def first_promotes_second_fails(temporary_path: Path, destination_path: Path) -> None:
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    _promote_without_overwrite(temporary_path, destination_path)
                    return
                raise LabelReviewResponseIntakeError("injected receipt promotion failure")

            with patch(
                "burnlens.label_review_response_intake._promote_without_overwrite",
                side_effect=first_promotes_second_fails,
            ):
                with self.assertRaisesRegex(
                    LabelReviewResponseIntakeError,
                    "injected receipt promotion failure",
                ):
                    _intake(repository, source)
            self.assertFalse((custody / "PRESERVED-RESPONSE.json").exists())
            self.assertFalse((custody / "PRIVATE-RECEIPT.json").exists())
            self.assertEqual(list(custody.glob(".burnlens-response-intake-*")), [])

    def test_special_source_and_wrong_reviewer_fail_before_custody_write(self) -> None:
        with TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repo"
            repository.mkdir()
            _initialize_repository(repository)
            directory_source = repository / "inbound" / "directory.json"
            directory_source.mkdir(parents=True)
            with self.assertRaisesRegex(LabelReviewResponseIntakeError, "regular non-link"):
                _intake(repository, directory_source)

            source = _source(repository, reviewer_id="another-slot")
            with self.assertRaisesRegex(LabelReviewResponseIntakeError, "differs"):
                _intake(repository, source)

    def test_public_qa_is_rendered_content_withheld_and_non_overwriting(self) -> None:
        with TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repo"
            repository.mkdir()
            _initialize_repository(repository)
            intake = _intake(repository, _source(repository))
            report = build_response_intake_qa(
                intake_report=intake,
                generated_at_utc="2026-07-16T21:07:00Z",
                run_id="BL-TEST-ATOMIC-RESPONSE-INTAKE-QA",
                git_source_commit=SOURCE_COMMIT,
            )
            output = Path(temporary) / "public"
            json_path = output / "qa.json"
            html_path = output / "qa.html"
            png_path = output / "qa.png"
            write_response_intake_qa(
                report,
                json_path=json_path,
                html_path=html_path,
                png_path=png_path,
            )
            with Image.open(png_path) as image:
                self.assertEqual(image.size, (1800, 1280))
            serialized = json_path.read_text(encoding="utf-8")
            self.assertNotIn("software fixture experience", serialized)
            self.assertNotIn("response.json", serialized)
            self.assertNotIn(str(repository), serialized)
            self.assertIn("<main>", html_path.read_text(encoding="utf-8"))
            with self.assertRaisesRegex(LabelReviewResponseIntakeQaError, "overwrite"):
                write_response_intake_qa(
                    report,
                    json_path=json_path,
                    html_path=html_path,
                    png_path=png_path,
                )
            drifted = dict(intake)
            drifted["git_source_commit"] = "5" * 40
            with self.assertRaisesRegex(
                LabelReviewResponseIntakeQaError,
                "source commits differ",
            ):
                build_response_intake_qa(
                    intake_report=drifted,
                    generated_at_utc="2026-07-16T21:07:00Z",
                    run_id="BL-TEST-ATOMIC-RESPONSE-INTAKE-QA",
                    git_source_commit=SOURCE_COMMIT,
                )

    def test_current_versions_and_entry_points_are_explicit(self) -> None:
        self.assertEqual(burnlens.__version__, "0.46.0")
        self.assertEqual(SOFTWARE_VERSION, "0.18.0")
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn(
            'burnlens-intake-label-review-response = "burnlens.intake_label_review_response:main"',
            pyproject,
        )
        self.assertIn(
            'burnlens-run-label-review-response-intake-qa = '
            '"burnlens.run_label_review_response_intake_qa:main"',
            pyproject,
        )


if __name__ == "__main__":
    unittest.main()
