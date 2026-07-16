"""Publish content-withheld QA evidence for one exact private response lock."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .label_review_response_lock_qa import (
    OPERATOR_REVEAL_STATUS,
    LabelReviewResponseLockQaError,
    build_public_response_lock_qa,
    write_public_response_lock_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-html", type=Path, required=True)
    parser.add_argument("--output-png", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument("--expected-response-sha256", required=True)
    parser.add_argument("--expected-response-bytes", type=int, required=True)
    parser.add_argument("--expected-receipt-sha256", required=True)
    parser.add_argument("--expected-receipt-bytes", type=int, required=True)
    parser.add_argument("--expected-reviewer-id", required=True)
    parser.add_argument(
        "--operator-reveal-status",
        choices=[OPERATOR_REVEAL_STATUS],
        required=True,
        help="Operator declaration only; software cannot prove file-access history.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = build_public_response_lock_qa(
            packet_path=args.packet,
            response_path=args.response,
            receipt_path=args.receipt,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
            expected_response_sha256=args.expected_response_sha256,
            expected_response_bytes=args.expected_response_bytes,
            expected_receipt_sha256=args.expected_receipt_sha256,
            expected_receipt_bytes=args.expected_receipt_bytes,
            expected_reviewer_id=args.expected_reviewer_id,
            operator_reveal_status=args.operator_reveal_status,
        )
        write_public_response_lock_outputs(
            report,
            json_path=args.output_json,
            html_path=args.output_html,
            png_path=args.output_png,
        )
        print(report["decision"])
        print(f"response_sha256={report['private_response_binding']['sha256']}")
        print(f"receipt_sha256={report['private_receipt_binding']['sha256']}")
        return 0
    except (LabelReviewResponseLockQaError, OSError, ValueError, KeyError) as error:
        print(f"LABEL_REVIEW_RESPONSE_LOCK_QA_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
