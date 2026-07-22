"""Capture one exact private Petes Lake MTBS delivery without retaining its URL."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

from .petes_lake_reference_custody import (
    PetesLakeReferenceCustodyError,
    acquire_delivery,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--message-received-at-utc", required=True)
    parser.add_argument("--captured-at-utc", required=True)
    parser.add_argument("--delivery-expiry-text", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument(
        "--retrieval-url-environment-variable",
        default="BURNLENS_REFERENCE_DELIVERY_URL",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    retrieval_url = os.environ.pop(args.retrieval_url_environment_variable, "")
    try:
        report = acquire_delivery(
            repository_root=args.repository_root,
            retrieval_url=retrieval_url,
            message_received_at_utc=args.message_received_at_utc,
            captured_at_utc=args.captured_at_utc,
            delivery_expiry_text=args.delivery_expiry_text,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        print(report["state"])
        print(f"archive_bytes={report['archive']['bytes']}")
        print(f"archive_sha256={report['archive']['sha256']}")
        print("terms_and_native_pixels=NOT_OPENED")
        return 0
    except (PetesLakeReferenceCustodyError, OSError, ValueError) as error:
        print(f"PETES_LAKE_REFERENCE_CUSTODY_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
