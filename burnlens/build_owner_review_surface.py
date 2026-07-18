"""Build the exact 56-unit BurnLens owner yes/no/uncertain surface."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .owner_review_surface import OwnerReviewSurfaceError, build_surface, write_surface


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path("."))
    parser.add_argument("--archive-dir", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--bundle-report", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--frozen-evidence-directory", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        report, previews = build_surface(
            repository_root=args.repository_root.resolve(),
            archive_dir=args.archive_dir.resolve(),
            packet_path=args.packet.resolve(),
            bundle_report_path=args.bundle_report.resolve(),
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        write_surface(
            report,
            previews,
            output_directory=args.output_directory.resolve(),
            frozen_evidence_directory=(
                args.frozen_evidence_directory.resolve()
                if args.frozen_evidence_directory
                else args.output_directory.resolve()
            ),
        )
    except (OwnerReviewSurfaceError, OSError, ValueError, KeyError) as error:
        print(f"OWNER_REVIEW_SURFACE_FAILED: {error}", file=sys.stderr)
        raise SystemExit(2) from error
    print(report["decision"])
    print(f"units={report['summary']['unit_count']}")
    print(f"owner_responses={report['review_contract']['owner_responses_recorded']}")
    print(f"labels_promoted={report['summary']['labels_promoted']}")


if __name__ == "__main__":
    main()
