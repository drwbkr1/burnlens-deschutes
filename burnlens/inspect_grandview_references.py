"""Inspect and render exact Grandview official-reference source fitness."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .grandview_reference_fitness import GrandviewReferenceFitnessError, build_report, write_outputs
from .green_ridge_reference_fitness import GreenRidgeReferenceFitnessError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report, previews = build_report(
            package=args.package, plan_path=args.plan, archive_path=args.archive,
            generated_at_utc=args.generated_at_utc, run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        for name, path in write_outputs(report, previews, args.output_directory).items():
            print(f"{name}={path}")
        print(report["fitness_decision"]["checkpoint"])
        return 0
    except (GrandviewReferenceFitnessError, GreenRidgeReferenceFitnessError, OSError, ValueError) as error:
        print(f"GRANDVIEW_REFERENCE_FITNESS_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
