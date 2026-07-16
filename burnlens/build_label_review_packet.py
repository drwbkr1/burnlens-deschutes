"""Build the exact three-event BurnLens label-review readiness packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import zipfile

from .label_review_packet import (
    LabelReviewPacketError,
    build_packet,
    rebuild_exact_events,
    write_packet,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--darlene-optical-package", type=Path, required=True)
    parser.add_argument("--darlene-aoi-report", type=Path, required=True)
    parser.add_argument("--darlene-reference-geojson", type=Path, required=True)
    parser.add_argument("--darlene-optical-report", type=Path, required=True)
    parser.add_argument("--darlene-registration-report", type=Path, required=True)
    parser.add_argument("--darlene-proposal-report", type=Path, required=True)
    parser.add_argument("--darlene-proposal-directory", type=Path, required=True)
    parser.add_argument("--cross-event-optical-package", type=Path, required=True)
    parser.add_argument("--mtbs-package", type=Path, required=True)
    parser.add_argument("--cross-event-feasibility-report", type=Path, required=True)
    parser.add_argument("--cross-event-source-fitness-report", type=Path, required=True)
    parser.add_argument("--cross-event-proposal-report", type=Path, required=True)
    parser.add_argument("--cross-event-proposal-directory", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        events = rebuild_exact_events(
            darlene_optical_package=args.darlene_optical_package,
            darlene_aoi_report=args.darlene_aoi_report,
            darlene_reference_geojson=args.darlene_reference_geojson,
            darlene_optical_report=args.darlene_optical_report,
            darlene_registration_report=args.darlene_registration_report,
            darlene_proposal_report_path=args.darlene_proposal_report,
            darlene_proposal_directory=args.darlene_proposal_directory,
            cross_event_optical_package=args.cross_event_optical_package,
            mtbs_package=args.mtbs_package,
            cross_event_feasibility_report=args.cross_event_feasibility_report,
            cross_event_source_fitness_report=args.cross_event_source_fitness_report,
            cross_event_proposal_report_path=args.cross_event_proposal_report,
            cross_event_proposal_directory=args.cross_event_proposal_directory,
            git_source_commit=args.git_source_commit,
        )
        packet, units, response, adjudication = build_packet(
            events=events,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        write_packet(
            packet=packet,
            events=events,
            units=units,
            response=response,
            adjudication=adjudication,
            output_directory=args.output_directory,
        )
        print(packet["decision"])
        print(f"review_units={len(units)}")
        return 0
    except (
        LabelReviewPacketError,
        OSError,
        ValueError,
        KeyError,
        zipfile.BadZipFile,
    ) as error:
        print(f"LABEL_REVIEW_PACKET_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
