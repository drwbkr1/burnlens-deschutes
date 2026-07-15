"""Create the bounded BurnLens five-state burn-scar label proposal."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import zipfile

from .label_proposal import LabelProposalError, propose_burn_scar_labels


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--aoi-report", type=Path, required=True)
    parser.add_argument("--reference-geojson", type=Path, required=True)
    parser.add_argument("--optical-report", type=Path, required=True)
    parser.add_argument("--registration-report", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        paths = propose_burn_scar_labels(
            package=args.package,
            aoi_report_path=args.aoi_report,
            reference_geojson_path=args.reference_geojson,
            optical_report_path=args.optical_report,
            registration_report_path=args.registration_report,
            output_directory=args.output_directory,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
    except (OSError, LabelProposalError, ValueError, zipfile.BadZipFile) as error:
        print(str(error), file=sys.stderr)
        return 2
    for kind, path in paths.items():
        print(f"{kind}={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
