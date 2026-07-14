"""Create deterministic evidence for the exact paired-intake transaction contract."""

from __future__ import annotations

import argparse
from pathlib import Path

from .paired_intake import build_report, write_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        generated_at_utc=args.generated_at_utc,
        run_id=args.run_id,
        source_commit=args.source_commit,
    )
    write_report(report, args.output_dir)
    return 2 if report["decision"] == "BLOCKED_OWNER_CREDENTIAL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
