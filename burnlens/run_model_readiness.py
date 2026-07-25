"""Run P2O5-T03-U06 model-readiness audit."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess

from .model_readiness import ModelReadinessError, write_outputs


def verify_git_source_commit(repository_root: Path, supplied_commit: str) -> str:
    if re.fullmatch(r"[0-9a-f]{40}", supplied_commit) is None:
        raise ModelReadinessError(
            "git source commit must be a full lowercase SHA-1"
        )
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository_root,
        check=True,
        capture_output=True,
        text=True,
    )
    head = result.stdout.strip()
    if supplied_commit != head:
        raise ModelReadinessError(
            f"git source commit mismatch: supplied {supplied_commit}, HEAD {head}"
        )
    return head


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--readiness-directory", type=Path, required=True)
    parser.add_argument("--contract-path", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args()
    try:
        root = args.repository_root.resolve()
        commit = verify_git_source_commit(root, args.git_source_commit)
        outputs = write_outputs(
            root,
            args.output_directory.resolve(),
            args.readiness_directory.resolve(),
            args.contract_path.resolve(),
            args.generated_at_utc,
            args.run_id,
            commit,
        )
    except (
        ModelReadinessError,
        OSError,
        subprocess.CalledProcessError,
        ValueError,
        TypeError,
        KeyError,
    ) as error:
        print(f"MODEL_READINESS_FAILED: {error}")
        return 2
    print("AUTHORIZE_BOUNDED_UNET")
    print("qualifier=REJECTION_FIRST_SINGLE_MODEL_EXPERIMENT")
    for name, path in outputs.items():
        print(f"{name}={path}")
    print("model_created=false")
    print("training_authorized_after_verified_u07_release=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
