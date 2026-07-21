"""Build the blank Grandview owner review surface."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .grandview_owner_review_surface import (
    GrandviewOwnerReviewSurfaceError,
    build_surface,
    write_surface,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--original-package", type=Path, required=True)
    parser.add_argument("--extended-package", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--reference-archive", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args()
    try:
        report, selected, previews = build_surface(
            repository_root=args.repository_root.resolve(),
            original_package=args.original_package.resolve(),
            extended_package=args.extended_package.resolve(),
            plan_path=args.plan.resolve(),
            reference_archive=args.reference_archive.resolve(),
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        for binding in write_surface(report, selected, previews, args.output_directory.resolve()):
            print(f"{binding['path']} {binding['sha256']}")
        print(report["decision"])
        print("owner_responses=0")
        print("labels=0")
        return 0
    except (GrandviewOwnerReviewSurfaceError, OSError, ValueError, KeyError, TypeError) as error:
        print(f"GRANDVIEW_OWNER_REVIEW_SURFACE_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

