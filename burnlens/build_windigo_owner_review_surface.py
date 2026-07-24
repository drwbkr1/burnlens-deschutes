"""CLI for the exact blank Windigo owner-review surface."""

from __future__ import annotations

import argparse
from pathlib import Path

from .owner_review_batch import OwnerReviewBatchError
from .windigo_owner_review_surface import write_windigo_surface


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build one exact blank two-card Windigo owner-review surface."
    )
    parser.add_argument("--proposal-directory", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        bindings = write_windigo_surface(
            args.proposal_directory,
            args.output_directory,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
    except (OSError, OwnerReviewBatchError) as error:
        raise SystemExit(f"Windigo owner-review surface failed: {error}") from error
    for binding in bindings:
        print(
            f"{binding['path']} bytes={binding['bytes']} sha256={binding['sha256']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
