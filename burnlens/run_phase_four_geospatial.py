"""CLI for one immutable Phase Four U03 geospatial attempt."""

from __future__ import annotations

import argparse
from pathlib import Path

from burnlens.phase_four_geospatial import run_geospatial_products


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create native-grid BurnLens RBR rasters, rejected-U-Net "
            "diagnostic rasters, accepted RBR vectors, and validation evidence."
        )
    )
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    build = run_geospatial_products(
        repository_root=args.repository_root,
        generated_at_utc=args.generated_at_utc,
        run_id=args.run_id,
        git_source_commit=args.git_source_commit,
    )
    print(build.manifest["state"].upper().replace("-", "_"))
    print(f"RUN_ID={build.manifest['run_id']}")
    print(f"OUTPUT_COUNT={len(build.outputs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
