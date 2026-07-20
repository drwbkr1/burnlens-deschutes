"""Validate and preserve one exact completed Green Ridge owner response."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .green_ridge_owner_response_intake import GreenRidgeOwnerResponseIntakeError, preserve_response


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--surface", type=Path, required=True)
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--destination-directory", type=Path, required=True)
    parser.add_argument("--received-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args()
    try:
        response_path, receipt_path, receipt = preserve_response(
            repository_root=args.repository_root.resolve(),
            surface_path=args.surface.resolve(),
            source_response_path=args.response.resolve(),
            destination_directory=args.destination_directory.resolve(),
            received_at_utc=args.received_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
    except (GreenRidgeOwnerResponseIntakeError, OSError, ValueError, KeyError) as error:
        print(f"GREEN_RIDGE_OWNER_RESPONSE_PRESERVATION_FAILED: {error}", file=sys.stderr)
        return 2
    print(receipt["decision"])
    print(f"exact_response={response_path}")
    print(f"receipt={receipt_path}")
    print(f"response_sha256={receipt['response_binding']['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
