"""Run separate all-pixel QA for the cross-event five-state proposals."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .cross_event_label_transfer_qa import (
    CrossEventLabelTransferQaError,
    build_qa_report,
    write_qa_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--optical-package", type=Path, required=True)
    parser.add_argument("--mtbs-package", type=Path, required=True)
    parser.add_argument("--feasibility-report", type=Path, required=True)
    parser.add_argument("--source-fitness-report", type=Path, required=True)
    parser.add_argument("--proposal-report", type=Path, required=True)
    parser.add_argument("--proposal-output-directory", type=Path, required=True)
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
        report, visuals = build_qa_report(
            optical_package=args.optical_package,
            mtbs_package=args.mtbs_package,
            feasibility_report_path=args.feasibility_report,
            source_fitness_report_path=args.source_fitness_report,
            proposal_report_path=args.proposal_report,
            proposal_output_directory=args.proposal_output_directory,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        write_qa_report(report, visuals, args.output_json, args.output_html, args.output_png)
        print(report["decision"])
        return 0
    except (CrossEventLabelTransferQaError, OSError, ValueError) as error:
        print(f"CROSS_EVENT_LABEL_TRANSFER_QA_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
