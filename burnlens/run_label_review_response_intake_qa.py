"""Rehearse atomic response intake with a non-human software fixture."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .label_review_response_intake import (
    LabelReviewResponseIntakeError,
    intake_label_review_response,
)
from .label_review_response_intake_qa import (
    LabelReviewResponseIntakeQaError,
    build_response_intake_qa,
    write_response_intake_qa,
)
from .lock_label_review_response import SOFTWARE_BROWSER_FIXTURE


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--fixture-response", type=Path, required=True)
    parser.add_argument("--custody-directory", type=Path, required=True)
    parser.add_argument("--preserved-response-name", required=True)
    parser.add_argument("--receipt-name", required=True)
    parser.add_argument("--expected-reviewer-id", required=True)
    parser.add_argument("--receipt-id", required=True)
    parser.add_argument("--received-at-utc", required=True)
    parser.add_argument("--intake-run-id", required=True)
    parser.add_argument("--qa-run-id", required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument("--task-issue", type=int, default=402)
    parser.add_argument("--disallowed-response-sha256", action="append", default=[])
    parser.add_argument("--disallowed-reviewer-id", action="append", default=[])
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-html", type=Path, required=True)
    parser.add_argument("--output-png", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        intake = intake_label_review_response(
            repository_root=args.repository_root,
            packet_path=args.packet,
            source_response_path=args.fixture_response,
            custody_directory=args.custody_directory,
            preserved_response_name=args.preserved_response_name,
            receipt_name=args.receipt_name,
            expected_reviewer_id=args.expected_reviewer_id,
            receipt_id=args.receipt_id,
            received_at_utc=args.received_at_utc,
            run_id=args.intake_run_id,
            git_source_commit=args.git_source_commit,
            task_issue=args.task_issue,
            disallowed_response_sha256=args.disallowed_response_sha256,
            disallowed_reviewer_ids=args.disallowed_reviewer_id,
            evidence_origin=SOFTWARE_BROWSER_FIXTURE,
        )
        report = build_response_intake_qa(
            intake_report=intake,
            generated_at_utc=args.generated_at_utc,
            run_id=args.qa_run_id,
            git_source_commit=args.git_source_commit,
        )
        write_response_intake_qa(
            report,
            json_path=args.output_json,
            html_path=args.output_html,
            png_path=args.output_png,
        )
        print(report["decision"])
        print(f"response_sha256={report['preserved_response_binding']['sha256']}")
        print(f"receipt_sha256={report['private_receipt_binding']['sha256']}")
        return 0
    except (
        LabelReviewResponseIntakeError,
        LabelReviewResponseIntakeQaError,
        OSError,
        ValueError,
        KeyError,
    ) as error:
        print(f"LABEL_REVIEW_RESPONSE_INTAKE_QA_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
