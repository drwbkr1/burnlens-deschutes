from __future__ import annotations

import argparse
from pathlib import Path

from .label_region_remediation_plan import LabelRegionRemediationPlanError, build_report, write_outputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the BurnLens contiguous-region and event-diversity remediation plan.")
    parser.add_argument("--sufficiency", type=Path, required=True)
    parser.add_argument("--source-scout", type=Path, required=True)
    parser.add_argument("--source-capture", type=Path, required=True)
    parser.add_argument("--bundle-fitness", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args()
    try:
        report = build_report(
            args.sufficiency.resolve(),
            args.source_scout.resolve(),
            args.source_capture.resolve(),
            args.bundle_fitness.resolve(),
            args.generated_at_utc,
            args.run_id,
            args.git_source_commit,
        )
        write_outputs(args.output_directory.resolve(), report)
    except (OSError, ValueError, KeyError, TypeError, LabelRegionRemediationPlanError) as exc:
        print(f"LABEL_REGION_REMEDIATION_PLAN_FAILED: {exc}")
        return 2
    print(report["decision"])
    print(f"current_events={report['trigger']['current_event_groups']}")
    print(f"minimum_events={report['event_plan']['minimum_event_groups_before_split_fitness']}")
    print("dataset_version=none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
