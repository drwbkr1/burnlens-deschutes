"""Build the public Windigo request receipt from exact private custody."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .windigo_reference_request import (
    WindigoReferenceRequestError,
    build_public_request_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--reconciliation-commit", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = build_public_request_report(
            repository_root=args.repository_root,
            reconciliation_commit=args.reconciliation_commit,
        )
        print(report["decision"])
        print("delivery=PENDING_EMAIL_DELIVERY")
        return 0
    except (WindigoReferenceRequestError, OSError, ValueError) as error:
        print(f"WINDIGO_REFERENCE_RECONCILIATION_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
