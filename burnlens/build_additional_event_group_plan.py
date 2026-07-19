"""Build the rendered additional whole-event group plan from a frozen source."""

from __future__ import annotations

import argparse
from pathlib import Path

from .additional_event_group_plan import AdditionalEventGroupError, run_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-json", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args()
    try:
        paths = run_report(
            source_path=args.source_json,
            output_directory=args.output_directory,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
    except (AdditionalEventGroupError, OSError, ValueError, KeyError, TypeError) as error:
        print(f"ADDITIONAL_EVENT_GROUP_PLAN_FAILED: {error}")
        return 2
    for key, path in paths.items():
        print(f"{key}={path}")
    print("decision=SIX_WHOLE_EVENT_GROUPS_FROZEN_NO_DATASET")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
