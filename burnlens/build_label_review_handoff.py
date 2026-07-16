"""Build the exact BurnLens offline reviewer handoff from the shipped packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import zipfile

from .label_review_handoff import LabelReviewHandoffError, build_handoff


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--output-zip", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest, archive, _ = build_handoff(
            packet_path=args.packet,
            output_directory=args.output_directory,
            archive_path=args.output_zip,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        print(manifest["decision"])
        print(f"archive_bytes={archive['bytes']}")
        print(f"archive_sha256={archive['sha256']}")
        return 0
    except (LabelReviewHandoffError, OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        print(f"LABEL_REVIEW_HANDOFF_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
