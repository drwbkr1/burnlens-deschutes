"""Inspect and render Green Ridge affirmative background-route evidence."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .green_ridge_background_evidence import (
    GreenRidgeBackgroundEvidenceError,
    build_report,
    write_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-package", type=Path, required=True)
    parser.add_argument("--extended-package", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--reference-archive", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report, previews = build_report(
            original_package=args.original_package,
            extended_package=args.extended_package,
            plan_path=args.plan,
            reference_archive=args.reference_archive,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        for name, path in write_outputs(report, previews, args.output_directory).items():
            print(f"{name}={path}")
        print(report["fitness_decision"]["checkpoint"])
        return 0
    except (GreenRidgeBackgroundEvidenceError, OSError, ValueError, KeyError) as error:
        print(f"GREEN_RIDGE_BACKGROUND_EVIDENCE_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
