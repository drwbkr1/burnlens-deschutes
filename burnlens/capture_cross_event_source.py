"""CLI for a normalized current cross-event source capture."""

from __future__ import annotations

import argparse
from pathlib import Path

from .cross_event_source import CrossEventSourceError, write_cross_event_source


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture current official MTBS, Census, and CDSE metadata for cross-event feasibility."
    )
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--accessed-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args()
    try:
        path = write_cross_event_source(
            output_path=args.output_json,
            accessed_at_utc=args.accessed_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
    except CrossEventSourceError as error:
        print(f"error={error}")
        return 2
    print(f"json={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
