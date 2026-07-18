"""Inspect exact current BAER/RAVG/MTBS bundles and render bounded fitness evidence."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .current_reference_bundle_fitness import (
    CurrentReferenceBundleFitnessError,
    build_report,
    write_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--archive-dir", type=Path, required=True)
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
        report, previews = build_report(
            repository_root=args.repository_root.resolve(),
            archive_dir=args.archive_dir.resolve(),
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        write_report(
            report,
            previews,
            json_path=args.output_json,
            html_path=args.output_html,
            png_path=args.output_png,
        )
        print(report["decision"])
        print(f"archives={report['source_controls']['archive_count']}")
        print(f"products={report['source_controls']['product_count']}")
        print("owner_responses=0")
        print("labels_promoted=false")
        return 0
    except (CurrentReferenceBundleFitnessError, OSError, ValueError, KeyError) as error:
        print(f"CURRENT_REFERENCE_BUNDLE_FITNESS_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
