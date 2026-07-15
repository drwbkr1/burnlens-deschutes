"""Inspect the exact Sentinel-2 pair and render non-label protocol evidence."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import zipfile

from .optical_pair_evidence import OpticalPairEvidenceError, inspect_optical_pair


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--aoi-report", type=Path, required=True)
    parser.add_argument("--reference-geojson", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument(
        "--visual-review-decision",
        required=True,
        choices=(
            "PENDING_VISUAL_REVIEW",
            "ACCEPT_OPTICAL_PAIR_FOR_PROTOCOL_DEFER_LABELS",
            "REJECT_OPTICAL_PAIR_REMEDIATE",
        ),
    )
    parser.add_argument("--visual-review-notes", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        paths = inspect_optical_pair(
            package=args.package,
            aoi_report_path=args.aoi_report,
            reference_geojson_path=args.reference_geojson,
            output_directory=args.output_directory,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
            visual_review_decision=args.visual_review_decision,
            visual_review_notes=args.visual_review_notes,
        )
    except (OSError, OpticalPairEvidenceError, ValueError, zipfile.BadZipFile) as error:
        print(str(error), file=sys.stderr)
        return 2
    for kind, path in paths.items():
        print(f"{kind}={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
