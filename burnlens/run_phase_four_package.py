"""CLI for the immutable Phase Four run package."""

from __future__ import annotations

import argparse
from pathlib import Path

from burnlens.phase_four_package import run_package


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the deterministic Ward Creek Phase Four run package."
    )
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--extracted-directory", type=Path, required=True)
    parser.add_argument("--archive-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    build = run_package(
        repository_root=args.repository_root,
        extracted_directory=args.extracted_directory,
        archive_directory=args.archive_directory,
        generated_at_utc=args.generated_at_utc,
        run_id=args.run_id,
        git_source_commit=args.git_source_commit,
    )
    print("PACKAGE_CANDIDATE_PENDING_CLEAN_REPRODUCTION")
    print(f"RUN_ID={build['receipt']['run_id']}")
    print(f"FILE_COUNT={len(build['files'])}")
    print(f"ARCHIVE_BYTES={len(build['archive'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
