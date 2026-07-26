"""Replay and package the BurnLens U-Net rejection decision."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from burnlens.bounded_unet_package import (
    BoundedUNetPackageError,
    record_failed_package,
    run_replay_and_package,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--run-directory", type=Path, required=True)
    parser.add_argument("--package-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args(argv)
    try:
        receipts = run_replay_and_package(
            args.root.resolve(),
            args.run_directory,
            args.package_directory,
            args.generated_at_utc,
            args.run_id,
            args.git_source_commit,
        )
    except (OSError, ValueError, BoundedUNetPackageError) as exc:
        try:
            record_failed_package(
                args.run_directory,
                args.generated_at_utc,
                args.run_id,
                args.git_source_commit,
                exc,
            )
        except (OSError, ValueError, BoundedUNetPackageError):
            pass
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    for name, receipt in receipts.items():
        print(
            f"PACKAGE; name={name}; path={receipt['path']}; "
            f"bytes={receipt['bytes']}; sha256={receipt['sha256']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
