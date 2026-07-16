"""Authorize a later BurnLens proposal reveal under the explicit owner waiver."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .owner_waiver_reveal_readiness import (
    OwnerWaiverRevealReadinessError,
    authorize_owner_waiver_reveal,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--reveal", type=Path, required=True)
    parser.add_argument("--authorization-output", type=Path, required=True)
    parser.add_argument("--authorization-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--authorized-at-utc", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument("--task-issue", type=int, default=407)
    parser.add_argument("--parent-reconciliation-issue", type=int, default=403)
    parser.add_argument("--operator-reveal-status", required=True)
    parser.add_argument("--confirm-owner-waiver", action="store_true")
    parser.add_argument("--acknowledge-reduced-validation", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = authorize_owner_waiver_reveal(
            repository_root=args.repository_root,
            response_path=args.response,
            receipt_path=args.receipt,
            packet_path=args.packet,
            reveal_path=args.reveal,
            authorization_path=args.authorization_output,
            authorization_id=args.authorization_id,
            run_id=args.run_id,
            authorized_at_utc=args.authorized_at_utc,
            git_source_commit=args.git_source_commit,
            owner_waiver_confirmed=args.confirm_owner_waiver,
            reduced_validation_acknowledged=args.acknowledge_reduced_validation,
            operator_reveal_status=args.operator_reveal_status,
            task_issue=args.task_issue,
            parent_reconciliation_issue=args.parent_reconciliation_issue,
        )
        print(report["decision"])
        print(f"response_sha256={report['response_binding']['sha256']}")
        print(f"receipt_sha256={report['receipt_binding']['sha256']}")
        print(f"reveal_sha256={report['reveal_binding']['sha256']}")
        print("reveal_opened_by_this_run=false")
        return 0
    except (OwnerWaiverRevealReadinessError, OSError, ValueError, KeyError) as error:
        print(f"LABEL_REVIEW_REVEAL_AUTHORIZATION_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
