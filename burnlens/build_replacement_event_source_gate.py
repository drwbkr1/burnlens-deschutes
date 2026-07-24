"""CLI for the live P2O4-T39 Ward Creek metadata-only source gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .replacement_event_source_gate import capture_source_gate, write_outputs


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Re-query official Ward Creek metadata and write a fail-closed U01 source gate. "
            "This command never requests provider archive bytes."
        )
    )
    parser.add_argument("--accessed-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    source = capture_source_gate(
        accessed_at_utc=args.accessed_at_utc,
        run_id=args.run_id,
        git_source_commit=args.git_source_commit,
    )
    outputs = write_outputs(source=source, output_directory=args.output_directory)
    print(json.dumps({name: str(path) for name, path in outputs.items()}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
