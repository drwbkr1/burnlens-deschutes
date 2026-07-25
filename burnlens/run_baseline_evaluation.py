"""Run the P2O5-T03-U05 baseline protocol, selection, or evaluation stage."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

from .baseline_evaluation import (
    BaselineEvaluationError,
    write_evaluation,
    write_protocol,
    write_selection,
)
from .run_dataset_qa import verify_git_source_commit


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    subparsers = parser.add_subparsers(dest="stage", required=True)
    protocol = subparsers.add_parser("protocol")
    protocol.add_argument("--output-path", type=Path, required=True)
    selection = subparsers.add_parser("selection")
    selection.add_argument("--protocol-path", type=Path, required=True)
    selection.add_argument("--output-path", type=Path, required=True)
    evaluation = subparsers.add_parser("evaluation")
    evaluation.add_argument("--protocol-path", type=Path, required=True)
    evaluation.add_argument("--selection-path", type=Path, required=True)
    evaluation.add_argument("--output-directory", type=Path, required=True)
    args = parser.parse_args()
    try:
        root = args.repository_root.resolve()
        commit = verify_git_source_commit(root, args.git_source_commit)
        if args.stage == "protocol":
            path = write_protocol(
                root,
                args.output_path.resolve(),
                args.generated_at_utc,
                args.run_id,
                commit,
            )
            print(f"PASS_BASELINE_PREREGISTRATION\nprotocol={path}")
        elif args.stage == "selection":
            path = write_selection(
                root,
                args.protocol_path.resolve(),
                args.output_path.resolve(),
                args.generated_at_utc,
                args.run_id,
                commit,
            )
            print(f"PASS_BASELINE_SELECTION_TEST_SEALED\nselection={path}")
        else:
            outputs = write_evaluation(
                root,
                args.protocol_path.resolve(),
                args.selection_path.resolve(),
                args.output_directory.resolve(),
                args.generated_at_utc,
                args.run_id,
                commit,
            )
            print("PASS_BASELINE_EVALUATION_TEST_OPEN_COUNT_1")
            for name, path in outputs.items():
                print(f"{name}={path}")
    except (
        BaselineEvaluationError,
        OSError,
        ValueError,
        TypeError,
        KeyError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"BASELINE_STAGE_FAILED: {error}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
