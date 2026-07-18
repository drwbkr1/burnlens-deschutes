from __future__ import annotations

import argparse
from pathlib import Path

from .region_owner_review_surface import RegionOwnerReviewSurfaceError, build_surface, write_surface


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the exact six-candidate BurnLens owner region review surface.")
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args()
    try:
        report, pilot_png = build_surface(
            args.repository_root.resolve(), args.generated_at_utc, args.run_id, args.git_source_commit
        )
        write_surface(report, pilot_png, args.output_directory.resolve())
    except (OSError, ValueError, KeyError, TypeError, RegionOwnerReviewSurfaceError) as exc:
        print(f"REGION_OWNER_REVIEW_SURFACE_FAILED: {exc}")
        return 2
    print(report["decision"])
    print("candidate_count=6")
    print("owner_region_responses=0")
    print("region_labels=0")
    print("dataset_version=none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
