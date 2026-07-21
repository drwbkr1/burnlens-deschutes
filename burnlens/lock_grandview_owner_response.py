"""Operator-lock one exact Grandview owner response before decision reveal."""

from __future__ import annotations

import argparse
from pathlib import Path

from .grandview_owner_response_lock import GrandviewOwnerResponseLockError, preserve_response_without_reveal


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--surface", type=Path, required=True)
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--destination-directory", type=Path, required=True)
    parser.add_argument("--received-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args()
    try:
        exact, receipt, report = preserve_response_without_reveal(
            repository_root=args.repository_root.resolve(),
            surface_path=args.surface.resolve(),
            source_response_path=args.response.resolve(),
            destination_directory=args.destination_directory.resolve(),
            received_at_utc=args.received_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
    except (GrandviewOwnerResponseLockError, OSError, ValueError, KeyError, TypeError) as error:
        print(f"GRANDVIEW_OWNER_RESPONSE_LOCK_FAILED: {error}")
        return 2
    print(report["decision"])
    print(f"exact_response={exact}")
    print(f"receipt={receipt}")
    print(f"response_bytes={report['response_binding']['bytes']}")
    print(f"response_sha256={report['response_binding']['sha256']}")
    print("decision_values_read=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
