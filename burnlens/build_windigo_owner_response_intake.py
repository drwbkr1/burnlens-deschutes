"""Build private reconciliation and public-safe Windigo intake evidence."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .windigo_owner_response_intake import (
    WindigoOwnerResponseIntakeError,
    build_private_reconciliation,
    public_report,
    write_private_no_overwrite,
    write_public_no_overwrite,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--pre-package", type=Path, required=True)
    parser.add_argument("--post-package", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--extracted-root", type=Path, required=True)
    parser.add_argument("--boundary", type=Path, required=True)
    parser.add_argument("--source-report", type=Path, required=True)
    parser.add_argument("--proposal", type=Path, required=True)
    parser.add_argument("--surface", type=Path, required=True)
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--private-output", type=Path, required=True)
    parser.add_argument("--public-output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args()
    try:
        repository_root = args.repository_root.resolve()
        private = build_private_reconciliation(
            repository_root=repository_root,
            pre_package=args.pre_package.resolve(),
            post_package=args.post_package.resolve(),
            archive_path=args.archive.resolve(),
            extracted_root=args.extracted_root.resolve(),
            boundary_path=args.boundary.resolve(),
            source_report_path=args.source_report.resolve(),
            proposal_path=args.proposal.resolve(),
            surface_path=args.surface.resolve(),
            response_path=args.response.resolve(),
            receipt_path=args.receipt.resolve(),
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        private_binding = write_private_no_overwrite(
            repository_root,
            args.private_output.resolve(),
            private,
        )
        report = public_report(private, private_binding)
        write_public_no_overwrite(report, args.public_output_directory.resolve())
    except (WindigoOwnerResponseIntakeError, OSError, ValueError, KeyError) as error:
        print(f"WINDIGO_OWNER_RESPONSE_INTAKE_FAILED: {error}", file=sys.stderr)
        return 2
    print(report["decision"])
    print(f"windigo_owner_responses={sum(report['decision_counts'].values())}")
    print(
        "windigo_owner_approved_region_labels="
        f"{report['outcome']['windigo_owner_approved_region_labels']}"
    )
    print(
        "cumulative_owner_approved_region_labels="
        f"{report['outcome']['cumulative_owner_approved_region_labels']}"
    )
    print("dataset_version=none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
