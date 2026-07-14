"""Render real-source fitness evidence for the registered BurnLens package."""

from __future__ import annotations

import argparse
from pathlib import Path

from .source_inspection import inspect_source_package


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--aoi-report", type=Path, required=True)
    parser.add_argument("--reference-geojson", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = inspect_source_package(
        package=args.package,
        aoi_report_path=args.aoi_report,
        reference_geojson_path=args.reference_geojson,
        output_directory=args.output_directory,
        generated_at_utc=args.generated_at_utc,
        run_id=args.run_id,
        git_source_commit=args.git_source_commit,
    )
    for name, path in paths.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
