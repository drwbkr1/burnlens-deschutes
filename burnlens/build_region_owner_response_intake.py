"""Build the private reconciliation and public-safe owner region intake report."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .region_owner_response_intake import (
    RegionOwnerResponseIntakeError,
    build_private_reconciliation,
    public_report,
    write_private_no_overwrite,
    write_public_no_overwrite,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--pilot", type=Path, required=True)
    parser.add_argument("--surface", type=Path, required=True)
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--private-output", type=Path, required=True)
    parser.add_argument("--public-output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        private = build_private_reconciliation(
            repository_root=args.repository_root.resolve(),
            pilot_path=args.pilot.resolve(),
            surface_path=args.surface.resolve(),
            response_path=args.response.resolve(),
            receipt_path=args.receipt.resolve(),
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        private_binding = write_private_no_overwrite(
            args.repository_root.resolve(), args.private_output.resolve(), private
        )
        report = public_report(private, private_binding)
        write_public_no_overwrite(report, args.public_output_directory.resolve())
    except (RegionOwnerResponseIntakeError, OSError, ValueError, KeyError) as error:
        print(f"REGION_OWNER_RESPONSE_INTAKE_FAILED: {error}", file=sys.stderr)
        return 2
    print(report["decision"])
    print(f"owner_region_responses={sum(report['decision_counts'].values())}")
    print(f"owner_approved_region_labels={report['outcome']['owner_approved_region_labels']}")
    print(f"accepted_core_pixels={report['outcome']['accepted_core_pixels']}")
    print("dataset_version=none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
