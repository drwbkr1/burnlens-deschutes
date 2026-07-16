"""Run the authorized private BurnLens single-reviewer reconciliation."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .owner_waiver_reveal_readiness import OwnerWaiverRevealReadinessError
from .single_reviewer_reconciliation import (
    SingleReviewerReconciliationError,
    reconcile_single_reviewer,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--reveal", type=Path, required=True)
    parser.add_argument("--private-output", type=Path, required=True)
    parser.add_argument("--opened-at-utc", required=True)
    parser.add_argument("--authorization-reverified-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument("--operator-reveal-status-before-run", required=True)
    parser.add_argument("--acknowledge-preflight-sequence-exception", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = reconcile_single_reviewer(
            repository_root=args.repository_root,
            authorization_path=args.authorization,
            response_path=args.response,
            receipt_path=args.receipt,
            packet_path=args.packet,
            reveal_path=args.reveal,
            output_path=args.private_output,
            opened_at_utc=args.opened_at_utc,
            authorization_reverified_at_utc=args.authorization_reverified_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
            operator_reveal_status_before_run=args.operator_reveal_status_before_run,
            preflight_sequence_exception_acknowledged=args.acknowledge_preflight_sequence_exception,
        )
        print(report["decision"])
        print(f"accepted_candidate_units={report['aggregate']['accepted_candidate_units']}")
        print(f"ignored_units={report['aggregate']['ignored_units']}")
        print("reveal_opened_by_this_run=true")
        return 0
    except (
        OwnerWaiverRevealReadinessError,
        SingleReviewerReconciliationError,
        OSError,
        ValueError,
        KeyError,
    ) as error:
        print(f"SINGLE_REVIEWER_RECONCILIATION_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
