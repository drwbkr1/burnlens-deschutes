from __future__ import annotations

import argparse
from pathlib import Path

from .prototype_label_sufficiency import PrototypeLabelSufficiencyError, build_report, write_outputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Assess BurnLens prototype-label dataset and split sufficiency.")
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--surface", type=Path, required=True)
    parser.add_argument("--private-intake", type=Path, required=True)
    parser.add_argument("--darlene-proposal", type=Path, required=True)
    parser.add_argument("--cross-event-proposal", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args()
    try:
        report = build_report(
            args.repository_root.resolve(),
            args.surface.resolve(),
            args.private_intake.resolve(),
            args.darlene_proposal.resolve(),
            args.cross_event_proposal.resolve(),
            args.generated_at_utc,
            args.run_id,
            args.git_source_commit,
        )
        write_outputs(args.output_directory.resolve(), report)
    except (OSError, ValueError, KeyError, TypeError, PrototypeLabelSufficiencyError) as exc:
        print(f"PROTOTYPE_LABEL_SUFFICIENCY_FAILED: {exc}")
        return 2
    print(report["decision"])
    print(f"prototype_labels={report['inventory']['prototype_labels']}")
    print(f"candidate_domain_pixels={report['inventory']['candidate_domain_pixels']}")
    print(f"event_groups={report['inventory']['event_groups']}")
    print("dataset_version=none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
