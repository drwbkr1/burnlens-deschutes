from __future__ import annotations

import argparse
from pathlib import Path

from .six_event_dataset_sufficiency import (
    SixEventDatasetSufficiencyError,
    write_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit six-event owner-approved prototype-region dataset sufficiency."
    )
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--records-directory", type=Path, required=True)
    parser.add_argument("--public-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args()
    try:
        outputs = write_outputs(
            args.repository_root.resolve(),
            args.records_directory.resolve(),
            args.public_directory.resolve(),
            args.generated_at_utc,
            args.run_id,
            args.git_source_commit,
        )
    except (OSError, ValueError, KeyError, TypeError, SixEventDatasetSufficiencyError) as exc:
        print(f"SIX_EVENT_DATASET_SUFFICIENCY_FAILED: {exc}")
        return 2
    print("BLOCK_DATASET_CANDIDATE_REMEDIATE_SOURCE_REGIME_SPLIT_FITNESS")
    for name, path in outputs.items():
        print(f"{name}={path}")
    print("training_authorized=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
