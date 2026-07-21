"""Preflight exact Petes Lake MTBS archives without extraction or raster access."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .petes_lake_reference_delivery import (
    PetesLakeReferenceDeliveryError,
    inspect_delivery,
    write_receipt,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = inspect_delivery(args.archive)
        write_receipt(report, args.output)
        print(report["decision"])
        print(f"archives={report['archive_count']}")
        print(f"map_ids={len(report['observed_map_ids'])}")
        return 0
    except (PetesLakeReferenceDeliveryError, OSError, ValueError) as error:
        print(f"PETES_LAKE_REFERENCE_DELIVERY_PREFLIGHT_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

