"""Operate the fail-closed Petes Lake NWI context intake state machine."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .petes_lake_wetland_custody import (
    PetesLakeWetlandCustodyError,
    authorize_contract,
    fetch_asset,
    finalize_contract,
    initialize_contract,
    promote_asset,
    start_asset,
    verify_asset,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    subparsers = parser.add_subparsers(dest="action", required=True)
    initialize = subparsers.add_parser("initialize")
    initialize.add_argument("--created-at-utc", required=True)
    initialize.add_argument("--git-source-commit", required=True)
    subparsers.add_parser("authorize")
    start = subparsers.add_parser("start")
    start.add_argument("--asset-id", required=True)
    start.add_argument("--started-at-utc", required=True)
    fetch = subparsers.add_parser("fetch")
    fetch.add_argument("--asset-id", required=True)
    fetch.add_argument("--request-dispatched-at-utc", required=True)
    verify = subparsers.add_parser("verify")
    verify.add_argument("--asset-id", required=True)
    promote = subparsers.add_parser("promote")
    promote.add_argument("--asset-id", required=True)
    finalize = subparsers.add_parser("finalize")
    finalize.add_argument("--completed-at-utc", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.action == "initialize":
            result = initialize_contract(
                args.repository_root,
                created_at_utc=args.created_at_utc,
                git_source_commit=args.git_source_commit,
            )
        elif args.action == "authorize":
            result = authorize_contract(args.repository_root)
        elif args.action == "start":
            result = start_asset(
                args.repository_root,
                asset_id=args.asset_id,
                started_at_utc=args.started_at_utc,
            )
        elif args.action == "fetch":
            result = fetch_asset(
                args.repository_root,
                asset_id=args.asset_id,
                request_dispatched_at_utc=args.request_dispatched_at_utc,
            )
        elif args.action == "verify":
            result = verify_asset(args.repository_root, asset_id=args.asset_id)
        elif args.action == "promote":
            result = promote_asset(args.repository_root, asset_id=args.asset_id)
        else:
            result = finalize_contract(
                args.repository_root, completed_at_utc=args.completed_at_utc
            )
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, ValueError, PetesLakeWetlandCustodyError) as error:
        print(f"PETES_LAKE_NWI_CUSTODY_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
