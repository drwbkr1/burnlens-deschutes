"""Inspect registered Green Ridge pixels and render source-fitness evidence."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .green_ridge_source_fitness import GreenRidgeSourceFitnessError, build_report, write_outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report, previews = build_report(
            package=args.package,
            plan_path=args.plan,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        outputs = write_outputs(report, previews, args.output_directory)
        for name, path in outputs.items():
            print(f"{name}={path}")
        print(report["fitness_decision"]["event_status"])
        return 0
    except (GreenRidgeSourceFitnessError, OSError, ValueError) as error:
        print(f"GREEN_RIDGE_SOURCE_FITNESS_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
