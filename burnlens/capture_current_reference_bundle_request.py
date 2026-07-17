"""Capture exact current-reference bundle-request evidence."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .current_reference_bundle_request import (
    CurrentReferenceBundleRequestError,
    build_bundle_request_evidence,
    fetch_full_inventory_response,
    write_bundle_request_evidence,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument("--input-metadata-response", type=Path)
    parser.add_argument("--input-queue-response", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-html", type=Path, required=True)
    parser.add_argument("--output-png", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        metadata = (
            args.input_metadata_response.read_bytes()
            if args.input_metadata_response is not None
            else fetch_full_inventory_response()
        )
        queue = args.input_queue_response.read_bytes()
        report = build_bundle_request_evidence(
            metadata,
            queue,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        write_bundle_request_evidence(
            report,
            json_path=args.output_json,
            html_path=args.output_html,
            png_path=args.output_png,
        )
        print(report["decision"])
        print(f"products={report['assessment_metadata']['product_count']}")
        print(f"cautions={report['assessment_metadata']['caution_count']}")
        print("bundles_received=0")
        print("labels_promoted=0")
        return 0
    except (CurrentReferenceBundleRequestError, OSError, ValueError, KeyError) as error:
        print(f"CURRENT_REFERENCE_BUNDLE_REQUEST_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
