"""Run the one frozen BurnLens U-Net training experiment."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from burnlens.bounded_unet import BoundedUNetError
from burnlens.bounded_unet_training import (
    BoundedUNetTrainingError,
    record_failed_attempt,
    run_substantive_training,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-output-directory", type=Path, required=True)
    parser.add_argument("--candidate-output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args(argv)
    try:
        receipts = run_substantive_training(
            args.root.resolve(),
            args.protocol,
            args.run_output_directory,
            args.candidate_output_directory,
            args.generated_at_utc,
            args.run_id,
            args.git_source_commit,
        )
    except (OSError, ValueError, BoundedUNetError, BoundedUNetTrainingError) as exc:
        try:
            record_failed_attempt(
                args.root.resolve(),
                args.run_output_directory,
                args.generated_at_utc,
                args.run_id,
                args.git_source_commit,
                exc,
            )
        except (OSError, ValueError, BoundedUNetTrainingError):
            pass
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    for name in sorted(receipts):
        receipt = receipts[name]
        print(
            f"{name.upper()}; path={receipt['path']}; "
            f"bytes={receipt['bytes']}; sha256={receipt['sha256']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
