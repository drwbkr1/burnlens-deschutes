"""Submit one exact Petes Lake MTBS request and preserve its private receipt."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

from .petes_lake_reference_request import (
    PetesLakeReferenceRequestError,
    acquire_request_receipt,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--requested-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument(
        "--recipient-environment-variable",
        default="BURNLENS_REFERENCE_REQUEST_EMAIL",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    recipient = os.environ.pop(args.recipient_environment_variable, "")
    try:
        receipt = acquire_request_receipt(
            args.output_directory,
            repository_root=args.repository_root,
            recipient=recipient,
            requested_at_utc=args.requested_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        print("PETES_LAKE_REFERENCE_REQUEST_ACCEPTED")
        print(f"mapping_ids={len(receipt['request']['mapping_ids'])}")
        print("delivery=PENDING_EMAIL_DELIVERY")
        return 0
    except (PetesLakeReferenceRequestError, OSError, ValueError) as error:
        print(f"PETES_LAKE_REFERENCE_REQUEST_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
