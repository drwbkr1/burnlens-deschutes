"""Prepare or execute the one frozen BurnLens U-Net test opening."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from burnlens.bounded_unet import BoundedUNetError
from burnlens.bounded_unet_evaluation import (
    BoundedUNetEvaluationError,
    build_test_authorization,
    record_failed_evaluation,
    run_locked_test_evaluation,
    run_validation_preflight,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    authorization = subparsers.add_parser("prepare-authorization")
    authorization.add_argument("--root", type=Path, default=Path("."))
    authorization.add_argument("--output", type=Path, required=True)
    authorization.add_argument("--opening-id", required=True)

    preflight = subparsers.add_parser("validation-preflight")
    preflight.add_argument("--root", type=Path, default=Path("."))
    preflight.add_argument("--output-directory", type=Path, required=True)
    preflight.add_argument("--generated-at-utc", required=True)
    preflight.add_argument("--run-id", required=True)
    preflight.add_argument("--git-source-commit", required=True)

    evaluate = subparsers.add_parser("evaluate")
    evaluate.add_argument("--root", type=Path, default=Path("."))
    evaluate.add_argument("--authorization", type=Path, required=True)
    evaluate.add_argument("--run-directory", type=Path, required=True)
    evaluate.add_argument("--output-directory", type=Path, required=True)
    evaluate.add_argument("--generated-at-utc", required=True)
    evaluate.add_argument("--run-id", required=True)
    evaluate.add_argument("--git-source-commit", required=True)

    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "prepare-authorization":
            receipt = build_test_authorization(
                root, args.output, args.opening_id
            )
            print(
                f"AUTHORIZATION; path={receipt['path']}; "
                f"bytes={receipt['bytes']}; sha256={receipt['sha256']}"
            )
            return 0
        if args.command == "validation-preflight":
            report = run_validation_preflight(
                root,
                args.output_directory,
                args.generated_at_utc,
                args.run_id,
                args.git_source_commit,
            )
            print(
                "VALIDATION-PREFLIGHT; "
                f"core_pixels={report['test_metrics']['core_pixels']}; "
                "test_open_count=0"
            )
            return 0
        receipts = run_locked_test_evaluation(
            root,
            args.authorization,
            args.run_directory,
            args.output_directory,
            args.generated_at_utc,
            args.run_id,
            args.git_source_commit,
        )
    except (OSError, ValueError, BoundedUNetError, BoundedUNetEvaluationError) as exc:
        if args.command == "evaluate":
            try:
                record_failed_evaluation(
                    args.run_directory,
                    args.generated_at_utc,
                    args.run_id,
                    args.git_source_commit,
                    exc,
                )
            except (OSError, ValueError, BoundedUNetEvaluationError):
                pass
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    for name, receipt in receipts.items():
        print(
            f"OUTPUT; name={name}; path={receipt['path']}; "
            f"bytes={receipt['bytes']}; sha256={receipt['sha256']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
