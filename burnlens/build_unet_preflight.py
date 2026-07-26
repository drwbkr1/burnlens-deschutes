"""Freeze the bounded U-Net protocol and run its sealed-test preflight."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from burnlens.unet_experiment import (
    UNetExperimentError,
    write_preflight_outputs,
    write_protocol,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--protocol-output", type=Path, required=True)
    parser.add_argument("--preflight-output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve()
        write_protocol(
            root,
            args.protocol_output,
            args.generated_at_utc,
            args.run_id,
            args.git_source_commit,
        )
        receipts = write_preflight_outputs(
            root,
            args.protocol_output,
            args.preflight_output_directory,
            args.generated_at_utc,
            args.run_id,
            args.git_source_commit,
        )
    except (OSError, ValueError, UNetExperimentError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    for name in ("json", "html", "png"):
        receipt = receipts[name]
        print(
            f"{name.upper()}; path={receipt['path']}; "
            f"bytes={receipt['bytes']}; sha256={receipt['sha256']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
