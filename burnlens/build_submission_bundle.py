"""CLI for the deterministic offline BurnLens submission bundle."""

from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path

from burnlens.submission_bundle import (
    build_bundle_contents,
    write_bundle_no_overwrite,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the deterministic offline BurnLens portfolio submission ZIP."
    )
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args()

    contents = build_bundle_contents(
        repository_root=args.repository_root,
        generated_at_utc=args.generated_at_utc,
        run_id=args.run_id,
        git_source_commit=args.git_source_commit,
    )
    archive, receipt = write_bundle_no_overwrite(
        contents=contents,
        output_directory=args.output_directory,
        generated_at_utc=args.generated_at_utc,
        run_id=args.run_id,
        git_source_commit=args.git_source_commit,
    )
    for path in (archive, receipt):
        data = path.read_bytes()
        print(f"{path.name}={len(data)}:{sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
