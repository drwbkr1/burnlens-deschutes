"""Materialize the exact P2O5-T03-U03 BurnLens dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

from .dataset_materialization import (
    DatasetMaterializationError,
    write_dataset,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args()
    try:
        destination = write_dataset(
            args.repository_root.resolve(),
            args.generated_at_utc,
            args.run_id,
            args.git_source_commit,
        )
    except (
        DatasetMaterializationError,
        OSError,
        ValueError,
        TypeError,
        KeyError,
    ) as error:
        print(f"DATASET_MATERIALIZATION_FAILED: {error}")
        return 2
    print("PASS_MATERIALIZE_BURNLENS_DATASET")
    print(f"dataset={destination}")
    print("test_pixels_opened=false")
    print("training_authorized=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
