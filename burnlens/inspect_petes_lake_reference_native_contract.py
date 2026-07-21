"""Inspect and record the exact terms-first Petes Lake MTBS native contract."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .petes_lake_reference_native_contract import (
    OUTPUT_PATH,
    PetesLakeReferenceNativeContractError,
    build_report,
    write_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.repository_root.resolve()
    output = (args.output or (root / OUTPUT_PATH)).resolve()
    try:
        if not output.is_relative_to(root):
            raise PetesLakeReferenceNativeContractError(
                "native-contract output must remain inside the repository"
            )
        report = build_report(
            repository_root=root,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        write_report(report, output)
        print(report["decision"]["code"])
        print(f"archive_sha256={report['native_contract']['archive']['sha256']}")
        print(f"native_rasters={len(report['native_contract']['native_rasters'])}")
        print("accepted_reference_pixels=0")
        return 0
    except (PetesLakeReferenceNativeContractError, OSError, ValueError) as error:
        print(f"PETES_LAKE_REFERENCE_NATIVE_CONTRACT_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
