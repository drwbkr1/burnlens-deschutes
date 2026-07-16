"""Publish public QA for one private BurnLens owner-waiver reveal authorization."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .owner_waiver_reveal_readiness import OwnerWaiverRevealReadinessError
from .owner_waiver_reveal_readiness_qa import (
    OwnerWaiverRevealReadinessQaError,
    build_owner_waiver_reveal_readiness_qa,
    write_owner_waiver_reveal_readiness_qa,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--reveal", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-html", type=Path, required=True)
    parser.add_argument("--output-png", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = build_owner_waiver_reveal_readiness_qa(
            authorization_path=args.authorization,
            response_path=args.response,
            receipt_path=args.receipt,
            packet_path=args.packet,
            reveal_path=args.reveal,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        write_owner_waiver_reveal_readiness_qa(
            report,
            json_path=args.output_json,
            html_path=args.output_html,
            png_path=args.output_png,
        )
        print(report["decision"])
        print(f"authorization_sha256={report['authorization_binding']['sha256']}")
        print(f"reveal_sha256={report['reveal_binding']['sha256']}")
        print("reveal_opened_by_this_run=false")
        return 0
    except (
        OwnerWaiverRevealReadinessError,
        OwnerWaiverRevealReadinessQaError,
        OSError,
        ValueError,
        KeyError,
    ) as error:
        print(f"OWNER_WAIVER_REVEAL_READINESS_QA_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
