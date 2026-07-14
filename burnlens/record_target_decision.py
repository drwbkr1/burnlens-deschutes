"""Render the owner-approved BurnLens burn-scar target-path decision."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .target_decision import TargetDecisionError, run_target_decision


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observation-report", type=Path, required=True)
    parser.add_argument("--aoi-report", type=Path, required=True)
    parser.add_argument("--mtbs-record", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        paths = run_target_decision(
            observation_path=args.observation_report,
            aoi_path=args.aoi_report,
            mtbs_path=args.mtbs_record,
            output_directory=args.output_directory,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
    except (OSError, TargetDecisionError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    for kind, path in paths.items():
        print(f"{kind}={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
