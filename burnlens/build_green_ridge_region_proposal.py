"""Build the no-promotion Green Ridge region proposal."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .green_ridge_region_proposal import GreenRidgeRegionProposalError, build_report, write_outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-package", type=Path, required=True)
    parser.add_argument("--extended-package", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--reference-archive", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args()
    try:
        report, selected, previews = build_report(
            original_package=args.original_package, extended_package=args.extended_package,
            plan_path=args.plan, reference_archive=args.reference_archive,
            generated_at_utc=args.generated_at_utc, run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        for path in write_outputs(report, selected, previews, args.output_directory):
            print(path)
        print(report["decision"])
        return 0
    except (GreenRidgeRegionProposalError, OSError, ValueError, KeyError) as error:
        print(f"GREEN_RIDGE_REGION_PROPOSAL_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
