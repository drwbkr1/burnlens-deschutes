"""CLI validator for the Phase Five QA and release-control contract."""

from __future__ import annotations

import argparse
from pathlib import Path

from burnlens.phase_five_contract import load_contract


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the exact Phase Five release inputs, evidence-unit roster, "
            "failure injections, accessibility standard, budgets, and boundaries."
        )
    )
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path.cwd(),
        help="BurnLens repository root (defaults to the current directory).",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    contract = load_contract(args.repository_root)
    print("PHASE_FIVE_CONTRACT_VALIDATION_PASS")
    print(f"CONTRACT_ID={contract['contract_id']}")
    print(f"MILESTONE_ID={contract['milestone_id']}")
    print(f"EVIDENCE_UNIT_COUNT={len(contract['evidence_units'])}")
    print(
        "FAILURE_INJECTION_COUNT="
        f"{len(contract['failure_injection_standard']['required_injections'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
