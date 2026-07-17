"""Capture and render the bounded BurnLens official-source scout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .official_source_scout import (
    OfficialSourceScoutError,
    build_official_source_scout,
    capture_live_source_scout,
    finalize_source_capture,
    validate_source_capture,
    write_official_source_scout,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--captured-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument("--input-source", type=Path)
    parser.add_argument("--output-source-json", type=Path, required=True)
    parser.add_argument("--output-report-json", type=Path, required=True)
    parser.add_argument("--output-html", type=Path, required=True)
    parser.add_argument("--output-png", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.input_source is None:
            source = finalize_source_capture(
                capture_live_source_scout(
                    captured_at_utc=args.captured_at_utc,
                    run_id=args.run_id,
                    git_source_commit=args.git_source_commit,
                )
            )
        else:
            source = json.loads(args.input_source.read_text(encoding="utf-8"))
            validate_source_capture(source)
            if source["captured_at_utc"] != args.captured_at_utc:
                raise OfficialSourceScoutError("input source timestamp differs from CLI")
            if source["run_id"] != args.run_id:
                raise OfficialSourceScoutError("input source run differs from CLI")
            if source["git_source_commit"] != args.git_source_commit:
                raise OfficialSourceScoutError("input source commit differs from CLI")
        report = build_official_source_scout(source)
        write_official_source_scout(
            source,
            report,
            source_json_path=args.output_source_json,
            report_json_path=args.output_report_json,
            html_path=args.output_html,
            png_path=args.output_png,
        )
        print(report["decision"])
        print(f"candidate_fires={report['findings']['new_candidate_count']}")
        print(f"source_classes={report['findings']['source_class_count']}")
        print("labels_promoted=false")
        return 0
    except (
        OfficialSourceScoutError,
        OSError,
        ValueError,
        KeyError,
        TypeError,
        json.JSONDecodeError,
    ) as error:
        print(f"OFFICIAL_SOURCE_SCOUT_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
