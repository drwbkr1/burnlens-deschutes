"""Finalize and render the issue #321 Darlene 3 modeling AOI evidence."""

from __future__ import annotations

import argparse
from pathlib import Path

from .aoi_finalizer import build_aoi_evidence, write_outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--source-commit", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report, polygons = build_aoi_evidence(
        args.source,
        generated_at_utc=args.generated_at_utc,
        run_id=args.run_id,
        source_commit=args.source_commit,
    )
    stem = "AOI-FINAL-2026-001"
    write_outputs(
        report,
        polygons,
        json_path=args.output_dir / f"{stem}.json",
        html_path=args.output_dir / f"{stem}.html",
        png_path=args.output_dir / f"{stem}.png",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
