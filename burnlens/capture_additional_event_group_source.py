"""Capture current official metadata for the additional-event-group plan."""

from __future__ import annotations

import argparse
from pathlib import Path

from .additional_event_group_plan import AdditionalEventGroupError, capture_source, write_source


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--accessed-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()
    try:
        write_source(
            capture_source(
                accessed_at_utc=args.accessed_at_utc,
                run_id=args.run_id,
                git_source_commit=args.git_source_commit,
            ),
            args.output_json,
        )
    except (AdditionalEventGroupError, OSError, ValueError, KeyError, TypeError) as error:
        print(f"ADDITIONAL_EVENT_GROUP_SOURCE_FAILED: {error}")
        return 2
    print(f"source={args.output_json}")
    print("provider_bytes_downloaded=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
