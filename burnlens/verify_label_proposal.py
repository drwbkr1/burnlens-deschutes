"""Independently verify and render a BurnLens label proposal audit."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import zipfile

from .label_proposal_qa import LabelProposalQaError, verify_label_proposal


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--aoi-report", type=Path, required=True)
    parser.add_argument("--reference-geojson", type=Path, required=True)
    parser.add_argument("--optical-report", type=Path, required=True)
    parser.add_argument("--registration-report", type=Path, required=True)
    parser.add_argument("--proposal-report", type=Path, required=True)
    parser.add_argument("--state-raster", type=Path, required=True)
    parser.add_argument("--target-raster", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument(
        "--visual-review-decision",
        required=True,
        choices=(
            "PENDING_QA_VISUAL_REVIEW",
            "ACCEPT_REVIEWABLE_LABEL_PROPOSAL_DEFER_DATASET",
            "ACCEPT_PROPOSAL_WITH_REVIEW_REMEDIATION",
            "REJECT_LABEL_PROPOSAL",
        ),
    )
    parser.add_argument("--visual-review-notes", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        paths = verify_label_proposal(
            package=args.package,
            aoi_report_path=args.aoi_report,
            reference_geojson_path=args.reference_geojson,
            optical_report_path=args.optical_report,
            registration_report_path=args.registration_report,
            proposal_report_path=args.proposal_report,
            state_raster_path=args.state_raster,
            target_raster_path=args.target_raster,
            output_directory=args.output_directory,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
            visual_review_decision=args.visual_review_decision,
            visual_review_notes=args.visual_review_notes,
        )
    except (OSError, LabelProposalQaError, ValueError, zipfile.BadZipFile) as error:
        print(str(error), file=sys.stderr)
        return 2
    for kind, path in paths.items():
        print(f"{kind}={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
