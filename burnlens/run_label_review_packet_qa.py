"""Verify a BurnLens label-review packet and any actual completed responses."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .verify_label_review_packet import (
    LabelReviewVerificationError,
    build_qa_report,
    write_qa_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--response", type=Path, action="append", default=[])
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-html", type=Path, required=True)
    parser.add_argument("--output-png", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = build_qa_report(
            packet_path=args.packet,
            response_paths=args.response,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        write_qa_report(
            report,
            json_path=args.output_json,
            html_path=args.output_html,
            png_path=args.output_png,
        )
        print(report["decision"])
        return 0
    except (LabelReviewVerificationError, OSError, ValueError, KeyError) as error:
        print(f"LABEL_REVIEW_PACKET_QA_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
