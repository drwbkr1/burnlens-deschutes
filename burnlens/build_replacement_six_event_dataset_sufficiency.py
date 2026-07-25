"""Build the replacement six-event Phase Two sufficiency evidence."""

from __future__ import annotations

import argparse
from pathlib import Path

from .replacement_six_event_dataset_sufficiency import (
    DECISION,
    SixEventDatasetSufficiencyError,
    write_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
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
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        SixEventDatasetSufficiencyError,
    ) as error:
        print(
            f"REPLACEMENT_SIX_EVENT_DATASET_SUFFICIENCY_FAILED: {error}"
        )
        return 2
    print(DECISION)
    for name, path in outputs.items():
        print(f"{name}={path}")
    print("training_authorized=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
