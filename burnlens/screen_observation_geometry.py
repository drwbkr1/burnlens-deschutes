"""Acquire, compare, and render the bounded NOAA-21 geometry screen."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .observation_geometry import ObservationGeometryError, run_observation_geometry_screen
from .provider_acquisition import AcquisitionError, ProviderCredentials


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quarantine", type=Path, required=True)
    parser.add_argument("--raw-parent", type=Path, required=True)
    parser.add_argument("--aoi-report", type=Path, required=True)
    parser.add_argument("--reference-geojson", type=Path, required=True)
    parser.add_argument("--baseline-report", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser.parse_args()


def _progress(role: str, observed: int, expected: int) -> None:
    percent = 100 * observed / expected if expected else 0
    print(f"{role}: {observed:,}/{expected:,} bytes ({percent:.1f}%)", flush=True)


def main() -> int:
    args = parse_args()
    credentials: ProviderCredentials | None = None
    try:
        try:
            credentials = ProviderCredentials.from_environment()
        except AcquisitionError as error:
            if error.reason_code != "CREDENTIAL_ENV_MISSING":
                raise
        paths = run_observation_geometry_screen(
            credentials=credentials,
            quarantine=args.quarantine,
            raw_parent=args.raw_parent,
            aoi_report_path=args.aoi_report,
            reference_geojson_path=args.reference_geojson,
            baseline_report_path=args.baseline_report,
            output_directory=args.output_directory,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
            progress=_progress,
        )
        for kind, path in paths.items():
            print(f"{kind}={path}")
        return 0
    except (AcquisitionError, ObservationGeometryError, OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    finally:
        credentials = None


if __name__ == "__main__":
    raise SystemExit(main())
