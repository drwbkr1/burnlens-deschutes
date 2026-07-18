from __future__ import annotations

import argparse
from pathlib import Path

from .region_candidate_pilot import RegionCandidatePilotError, build_pilot_report, write_pilot_outputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the BurnLens no-promotion contiguous-region candidate pilot.")
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--private-intake", type=Path, required=True)
    parser.add_argument("--scratch-directory", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--private-mapping", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args()
    try:
        report, selected, _audit, events, private_mapping = build_pilot_report(
            repository_root=args.repository_root.resolve(),
            private_intake_path=args.private_intake.resolve(),
            scratch_directory=args.scratch_directory.resolve(),
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        write_pilot_outputs(
            report=report,
            selected=selected,
            events=events,
            private_mapping=private_mapping,
            output_directory=args.output_directory.resolve(),
            private_mapping_path=args.private_mapping.resolve(),
        )
    except (OSError, ValueError, KeyError, TypeError, RegionCandidatePilotError) as exc:
        print(f"REGION_CANDIDATE_PILOT_FAILED: {exc}")
        return 2
    print(report["decision"])
    print(f"candidate_count={report['summary']['candidate_count']}")
    print("owner_region_responses=0")
    print("region_labels=0")
    print("dataset_version=none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

