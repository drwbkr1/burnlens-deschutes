"""Publish content-withheld QA evidence for two exact private response locks."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .label_review_dual_lock_qa import (
    CURRENT_RECEIPT_SOFTWARE,
    CURRENT_RECEIPT_VERSION,
    LEGACY_RECEIPT_SOFTWARE,
    LEGACY_RECEIPT_VERSION,
    OPERATOR_REVEAL_STATUS,
    ORIGINS,
    LabelReviewDualLockQaError,
    LockSpec,
    build_dual_lock_qa,
    write_dual_lock_outputs,
)


def _add_lock_arguments(parser: argparse.ArgumentParser, number: int) -> None:
    prefix = f"lock-{number}"
    parser.add_argument(f"--{prefix}-response", type=Path, required=True)
    parser.add_argument(f"--{prefix}-receipt", type=Path, required=True)
    parser.add_argument(f"--{prefix}-response-sha256", required=True)
    parser.add_argument(f"--{prefix}-response-bytes", type=int, required=True)
    parser.add_argument(f"--{prefix}-receipt-sha256", required=True)
    parser.add_argument(f"--{prefix}-receipt-bytes", type=int, required=True)
    parser.add_argument(f"--{prefix}-reviewer-id", required=True)
    parser.add_argument(f"--{prefix}-task-issue", type=int, required=True)
    parser.add_argument(
        f"--{prefix}-receipt-version",
        choices=[LEGACY_RECEIPT_VERSION, CURRENT_RECEIPT_VERSION],
        required=True,
    )
    parser.add_argument(
        f"--{prefix}-receipt-software",
        choices=[LEGACY_RECEIPT_SOFTWARE, CURRENT_RECEIPT_SOFTWARE],
        required=True,
    )
    parser.add_argument(f"--{prefix}-origin", choices=sorted(ORIGINS), required=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    _add_lock_arguments(parser, 1)
    _add_lock_arguments(parser, 2)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-html", type=Path, required=True)
    parser.add_argument("--output-png", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument(
        "--operator-reveal-status",
        choices=[OPERATOR_REVEAL_STATUS],
        required=True,
        help="Operator declaration only; software cannot prove file-access history.",
    )
    return parser.parse_args()


def _spec(args: argparse.Namespace, number: int) -> LockSpec:
    key = f"lock_{number}"
    return LockSpec(
        response_path=getattr(args, f"{key}_response"),
        receipt_path=getattr(args, f"{key}_receipt"),
        expected_response_sha256=getattr(args, f"{key}_response_sha256"),
        expected_response_bytes=getattr(args, f"{key}_response_bytes"),
        expected_receipt_sha256=getattr(args, f"{key}_receipt_sha256"),
        expected_receipt_bytes=getattr(args, f"{key}_receipt_bytes"),
        expected_reviewer_id=getattr(args, f"{key}_reviewer_id"),
        expected_task_issue=getattr(args, f"{key}_task_issue"),
        expected_receipt_version=getattr(args, f"{key}_receipt_version"),
        expected_receipt_software=getattr(args, f"{key}_receipt_software"),
        expected_origin=getattr(args, f"{key}_origin"),
    )


def main() -> int:
    args = parse_args()
    try:
        report = build_dual_lock_qa(
            packet_path=args.packet,
            locks=[_spec(args, 1), _spec(args, 2)],
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
            operator_reveal_status=args.operator_reveal_status,
        )
        write_dual_lock_outputs(
            report,
            json_path=args.output_json,
            html_path=args.output_html,
            png_path=args.output_png,
        )
        print(report["decision"])
        print(
            "operator_declared_returned_responses="
            f"{report['origin_classification']['operator_declared_returned_responses']}"
        )
        print(f"software_fixtures={report['origin_classification']['software_browser_fixtures']}")
        return 0
    except (LabelReviewDualLockQaError, OSError, ValueError, KeyError) as error:
        print(f"LABEL_REVIEW_DUAL_LOCK_QA_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
