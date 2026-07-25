"""Run independent P2O5-T03-U04 dataset QA."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess

from .dataset_qa import DatasetQaError, write_outputs


def verify_git_source_commit(repository_root: Path, supplied_commit: str) -> str:
    if re.fullmatch(r"[0-9a-f]{40}", supplied_commit) is None:
        raise DatasetQaError("git source commit must be a full lowercase SHA-1")
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository_root,
        check=True,
        capture_output=True,
        text=True,
    )
    head = result.stdout.strip()
    if supplied_commit != head:
        raise DatasetQaError(
            f"git source commit mismatch: supplied {supplied_commit}, HEAD {head}"
        )
    return head


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
        repository_root = args.repository_root.resolve()
        verified_commit = verify_git_source_commit(
            repository_root, args.git_source_commit
        )
        outputs = write_outputs(
            repository_root,
            args.output_directory.resolve(),
            args.normalization_path.resolve(),
            args.generated_at_utc,
            args.run_id,
            verified_commit,
        )
    except (
        DatasetQaError,
        OSError,
        subprocess.CalledProcessError,
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
