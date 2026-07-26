"""CLI validator for extracted or archived Phase Four packages."""

from __future__ import annotations

import argparse
from pathlib import Path

from burnlens.phase_four_package import validate_package


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate exact Phase Four package checksums, structure, "
            "geospatial products, interface, and analytical status."
        )
    )
    parser.add_argument("--package-path", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = validate_package(args.package_path)
    print(result["result"])
    print(f"PACKAGE_VERSION={result['package_version']}")
    print(f"PAYLOAD_FILE_COUNT={result['payload_file_count']}")
    print(f"GEOTIFF_COUNT={result['geotiff_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
