"""Acquire the exact public MTBS clips for cross-event proposal transfer."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .mtbs_cross_event_reference import MtbsReferenceError, acquire_package


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = acquire_package(
            args.destination,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        print(result["registration_manifest_sha256"])
        return 0
    except (MtbsReferenceError, OSError, ValueError) as error:
        print(f"MTBS_CROSS_EVENT_REFERENCE_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
