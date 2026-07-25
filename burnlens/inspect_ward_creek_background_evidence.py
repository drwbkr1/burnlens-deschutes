"""Inspect and render the exact Ward Creek affirmative-background route."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--pre-package", type=Path, required=True)
    parser.add_argument("--post-package", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--extracted-root", type=Path, required=True)
    parser.add_argument("--source-report", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser.parse_args()


def main() -> int:
    arguments = parse_args()
    try:
        from .ward_creek_background_evidence import (
            WardCreekBackgroundEvidenceError,
            build_report,
            write_outputs,
        )
    except ModuleNotFoundError as error:
        if error.name in {"geopandas", "pyogrio", "pyproj", "shapely"}:
            print(
                "WARD_CREEK_BACKGROUND_EVIDENCE_FAILED: "
                "optional geospatial dependencies are unavailable; "
                "run scripts/setup_worktree.ps1 -Profile geo-research",
                file=sys.stderr,
            )
            return 2
        raise

    try:
        report, previews = build_report(
            repository_root=arguments.repository_root,
            pre_package=arguments.pre_package,
            post_package=arguments.post_package,
            archive_path=arguments.archive,
            extracted_root=arguments.extracted_root,
            source_report_path=arguments.source_report,
            generated_at_utc=arguments.generated_at_utc,
            run_id=arguments.run_id,
            git_source_commit=arguments.git_source_commit,
        )
        for name, path in write_outputs(
            report,
            previews,
            arguments.output_directory,
        ).items():
            print(f"{name}={path}")
        print(report["fitness_decision"]["checkpoint"])
        return 0
    except (WardCreekBackgroundEvidenceError, OSError, ValueError) as error:
        print(f"WARD_CREEK_BACKGROUND_EVIDENCE_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
