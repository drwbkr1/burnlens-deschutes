"""CLI for the exact P2O1-T03 VIIRS access-integrity precheck."""

from __future__ import annotations

import argparse
from pathlib import Path

from .access_integrity import AssetSpec, build_report, inspect_payload, write_report


FIRE_SPEC = AssetSpec(
    role="active-fire",
    source_record_id="SOURCE-2026-005",
    collection="VJ214IMG.002",
    native_id="VJ214IMG.A2024179.1936.002.2025284191612",
    expected_filename="VJ214IMG.A2024179.1936.002.2025284191612.nc",
    stable_route="https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/VJ214IMG.002/VJ214IMG.A2024179.1936.002.2025284191612/VJ214IMG.A2024179.1936.002.2025284191612.nc",
    minimum_size_bytes=1_000_000,
)

GEO_SPEC = AssetSpec(
    role="terrain-corrected-geolocation",
    source_record_id="SOURCE-2026-006",
    collection="VJ203MODLL.021",
    native_id="VJ203MODLL.A2024179.1936.021.2024327213621",
    expected_filename="VJ203MODLL.A2024179.1936.021.2024327213621.h5",
    stable_route="https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/VJ203MODLL.021/VJ203MODLL.A2024179.1936.021.2024327213621/VJ203MODLL.A2024179.1936.021.2024327213621.h5",
    minimum_size_bytes=20_000_000,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fire-path", type=Path, required=True)
    parser.add_argument("--geolocation-path", type=Path, required=True)
    parser.add_argument("--fire-http-status", type=int, default=None)
    parser.add_argument("--geolocation-http-status", type=int, default=None)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-html", type=Path, required=True)
    parser.add_argument("--output-png", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    observations = [
        inspect_payload(args.fire_path, FIRE_SPEC, args.fire_http_status),
        inspect_payload(args.geolocation_path, GEO_SPEC, args.geolocation_http_status),
    ]
    report = build_report(
        observations,
        generated_at_utc=args.generated_at_utc,
        run_id=args.run_id,
    )
    write_report(report, args.output_json, args.output_html, args.output_png)
    return 0 if report["decision"] == "READY_FOR_FORMAT_INSPECTION" else 2


if __name__ == "__main__":
    raise SystemExit(main())
