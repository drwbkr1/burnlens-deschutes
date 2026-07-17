"""Capture and render the current official BurnLens reference inventory."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .current_reference_inventory import (
    CurrentReferenceInventoryError,
    build_current_reference_inventory,
    fetch_inventory_response,
    write_current_reference_inventory,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument("--input-response", type=Path)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-html", type=Path, required=True)
    parser.add_argument("--output-png", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        raw_response = (
            args.input_response.read_bytes()
            if args.input_response is not None
            else fetch_inventory_response()
        )
        report = build_current_reference_inventory(
            raw_response,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        write_current_reference_inventory(
            report,
            json_path=args.output_json,
            html_path=args.output_html,
            png_path=args.output_png,
        )
        print(report["decision"])
        print(f"products={report['inventory']['product_count']}")
        print(
            "normalized_products_sha256="
            f"{report['source']['normalized_products_sha256']}"
        )
        print("labels_promoted=false")
        return 0
    except (CurrentReferenceInventoryError, OSError, ValueError, KeyError) as error:
        print(f"CURRENT_REFERENCE_INVENTORY_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

