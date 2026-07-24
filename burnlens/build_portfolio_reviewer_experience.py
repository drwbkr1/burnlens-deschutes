"""CLI for the repository-owned BurnLens portfolio reviewer experience."""

from __future__ import annotations

import argparse
from pathlib import Path

from burnlens.portfolio_reviewer_experience import (
    build_report,
    write_outputs_no_overwrite,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the deterministic local/offline BurnLens reviewer experience."
    )
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args()

    report = build_report(
        repository_root=args.repository_root,
        generated_at_utc=args.generated_at_utc,
        run_id=args.run_id,
        git_source_commit=args.git_source_commit,
    )
    outputs = write_outputs_no_overwrite(
        report=report,
        output_directory=args.output_directory,
    )
    print(report["decision"])
    for output in outputs:
        print(f'{output["path"]}={output["bytes"]}:{output["sha256"]}')


if __name__ == "__main__":
    main()
