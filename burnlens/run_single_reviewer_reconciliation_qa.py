"""Publish aggregate-only QA for one private BurnLens single-reviewer reconciliation."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .single_reviewer_reconciliation_qa import (
    SingleReviewerReconciliationQaError,
    build_single_reviewer_reconciliation_qa,
    write_single_reviewer_reconciliation_qa,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-reconciliation", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-html", type=Path, required=True)
    parser.add_argument("--output-png", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = build_single_reviewer_reconciliation_qa(
            private_reconciliation_path=args.private_reconciliation,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        write_single_reviewer_reconciliation_qa(
            report,
            json_path=args.output_json,
            html_path=args.output_html,
            png_path=args.output_png,
        )
        print(report["decision"])
        print(f"accepted_candidate_units={report['aggregate']['accepted_candidate_units']}")
        print(f"ignored_units={report['aggregate']['ignored_units']}")
        return 0
    except (SingleReviewerReconciliationQaError, OSError, ValueError, KeyError) as error:
        print(f"SINGLE_REVIEWER_RECONCILIATION_QA_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
