"""CLI for the exact Phase Four U04 context intake."""

from __future__ import annotations

import argparse
from pathlib import Path

from burnlens.phase_four_context_intake import run_context_intake


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Acquire and no-overwrite promote the exact eight-response USGS "
            "Ward Creek context package."
        )
    )
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = run_context_intake(
        repository_root=args.repository_root,
        generated_at_utc=args.generated_at_utc,
        run_id=args.run_id,
        git_source_commit=args.git_source_commit,
    )
    print(result["state"])
    print(f"RUN_ID={result['run_id']}")
    print(f"ASSETS={result['total_assets']}")
    print(f"BYTES={result['total_bytes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
