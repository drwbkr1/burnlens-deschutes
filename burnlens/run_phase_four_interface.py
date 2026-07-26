"""CLI for the self-contained Phase Four evidence interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from burnlens.phase_four_interface import run_interface


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build the local/offline Ward Creek RBR-primary Phase Four "
            "evidence interface."
        )
    )
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    build = run_interface(
        repository_root=args.repository_root,
        output_directory=args.output_directory,
        generated_at_utc=args.generated_at_utc,
        run_id=args.run_id,
        git_source_commit=args.git_source_commit,
    )
    print(build["report"]["disposition"].upper().replace("-", "_"))
    print(f"RUN_ID={build['report']['run_id']}")
    print(f"OUTPUT_COUNT={len(build['outputs'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
