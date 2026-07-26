"""CLI validator for tracked Phase Five failure-injection evidence."""

from __future__ import annotations

import argparse
from pathlib import Path

from burnlens.phase_five_failure_injection import validate_failure_record


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Rebuild the five invalid fixtures, verify tracked evidence, "
            "and revalidate canonical Phase Four recovery."
        )
    )
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = validate_failure_record(args.repository_root)
    print(result["result"])
    print(f"FIXTURE_COUNT={result['fixture_count']}")
    print(f"PUBLIC_OUTPUT_COUNT={result['public_output_count']}")
    print(
        "CANONICAL_ARCHIVE_SHA256="
        f"{result['canonical_archive_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
