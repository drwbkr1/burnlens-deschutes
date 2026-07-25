"""Build the exact P2O5-T03-U01 dataset and evaluation contract."""

from __future__ import annotations

import argparse
from pathlib import Path

from .dataset_build_contract import (
    DatasetBuildContractError,
    write_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args()
    try:
        outputs = write_outputs(
            args.repository_root.resolve(),
            args.generated_at_utc,
            args.run_id,
            args.git_source_commit,
        )
    except (
        DatasetBuildContractError,
        OSError,
        ValueError,
        TypeError,
        KeyError,
    ) as error:
        print(f"DATASET_BUILD_CONTRACT_FAILED: {error}")
        return 2
    print("PASS_DATASET_BUILD_CONTRACT")
    for name, path in outputs.items():
        print(f"{name}={path}")
    print("training_authorized=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
