"""Run independent P2O5-T03-U04 dataset QA."""

from __future__ import annotations

import argparse
from pathlib import Path

from .dataset_qa import DatasetQaError, write_outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--normalization-path", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args()
    try:
        outputs = write_outputs(
            args.repository_root.resolve(),
            args.output_directory.resolve(),
            args.normalization_path.resolve(),
            args.generated_at_utc,
            args.run_id,
            args.git_source_commit,
        )
    except (
        DatasetQaError,
        OSError,
        ValueError,
        TypeError,
        KeyError,
    ) as error:
        print(f"DATASET_QA_FAILED: {error}")
        return 2
    print("PASS_INDEPENDENT_DATASET_QA")
    for name, path in outputs.items():
        print(f"{name}={path}")
    print("test_analytical_open_count=0")
    print("training_authorized=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
