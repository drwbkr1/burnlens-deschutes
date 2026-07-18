"""Build the exact BurnLens owner-response intake and gate assessment."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .owner_response_intake import (
    OwnerResponseIntakeError,
    build_private_reconciliation,
    public_report,
    write_private_no_overwrite,
    write_public_no_overwrite,
)
from .owner_review_surface import OwnerReviewSurfaceError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--archive-dir", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--bundle-report", type=Path, required=True)
    parser.add_argument("--surface", type=Path, required=True)
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--owner-confirmation", type=Path, required=True)
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
            archive_dir=args.archive_dir.resolve(),
            packet_path=args.packet.resolve(),
            bundle_report_path=args.bundle_report.resolve(),
            surface_path=args.surface.resolve(),
            response_path=args.response.resolve(),
            receipt_path=args.receipt.resolve(),
            confirmation_path=args.owner_confirmation.resolve(),
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        private_binding = write_private_no_overwrite(
            args.repository_root.resolve(),
            args.private_output.resolve(),
            private,
        )
        public = public_report(private, private_binding)
        write_public_no_overwrite(public, args.public_output_directory.resolve())
    except (OwnerResponseIntakeError, OwnerReviewSurfaceError, OSError, ValueError, KeyError) as error:
        print(f"OWNER_RESPONSE_INTAKE_FAILED: {error}", file=sys.stderr)
        return 2
    print(public["decision"])
    print(f"owner_decisions={sum(public['decision_counts'].values())}")
    print(f"prototype_labels={public['outcome']['owner_approved_prototype_labels']}")
    print(f"yes_quality_blocked={public['outcome']['yes_quality_blocked']}")
    print("dataset_version=none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
