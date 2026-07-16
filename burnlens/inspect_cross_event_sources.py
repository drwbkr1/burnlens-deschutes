"""Verify and render native-pixel fitness for the frozen Tepee/McKay pairs."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .cross_event_source_fitness import (
    CrossEventSourceFitnessError,
    build_report,
    write_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--feasibility-report", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-html", type=Path, required=True)
    parser.add_argument("--output-png", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument(
        "--visual-review-decision",
        default="PENDING_VISUAL_REVIEW",
        choices=(
            "PENDING_VISUAL_REVIEW",
            "ACCEPT_CROSS_EVENT_SOURCE_FITNESS",
            "ACCEPT_CROSS_EVENT_SOURCE_FITNESS_WITH_EXCLUSIONS",
            "REJECT_CROSS_EVENT_SOURCE_FITNESS",
        ),
    )
    parser.add_argument("--visual-review-notes", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report, previews = build_report(
            package=args.package,
            feasibility_report_path=args.feasibility_report,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
            visual_review_decision=args.visual_review_decision,
            visual_review_notes=args.visual_review_notes,
        )
        write_report(report, previews, args.output_json, args.output_html, args.output_png)
        print(report["decision"]["machine"])
        return 0
    except (CrossEventSourceFitnessError, OSError, ValueError) as error:
        print(f"CROSS_EVENT_SOURCE_FITNESS_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
