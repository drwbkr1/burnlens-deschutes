"""Acquire the exact Petes Lake Sentinel pair as ordered singleton transactions."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .petes_lake_optical_contract import (
    CdseCredentials,
    PetesLakeOpticalRun,
    acquire_petes_lake_optical_pair,
    finalize_petes_lake_aggregate_only,
    resume_petes_lake_post_only,
    validate_u03_prerequisite,
    verify_petes_lake_repository_preflight,
)
from .provider_acquisition import AcquisitionError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--revision", required=True, help="Immutable run revision, for example r001")
    parser.add_argument(
        "--mode",
        choices=("full", "full-remediation", "post-only", "aggregate-only"),
        default="full",
        help=(
            "Full r001 acquisition, a new full transaction after an unpromoted r001 "
            "failure, or a no-reacquisition post/aggregate remediation"
        ),
    )
    gate = parser.add_mutually_exclusive_group()
    gate.add_argument(
        "--preflight-only",
        action="store_true",
        help="Run exact repository/path gates and exit before reading credentials",
    )
    gate.add_argument(
        "--verify-only",
        action="store_true",
        help="Credential-free validation of completed full r001 outputs",
    )
    return parser.parse_args()


def _progress(role: str, observed: int, expected: int) -> None:
    percent = 100 * observed / expected if expected else 0
    print(f"{role}: {observed:,}/{expected:,} bytes ({percent:.1f}%)", flush=True)


def main() -> int:
    args = parse_args()
    credentials: CdseCredentials | None = None
    try:
        run = PetesLakeOpticalRun.create(
            repository_root=args.repository_root,
            generated_at_utc=args.generated_at_utc,
            revision=args.revision,
            mode=args.mode,
        )
        # Repository, branch, committed HEAD, U01 ancestry, exact entry bytes,
        # ignore rules, and no-overwrite destinations all pass before a
        # credential is read from the environment.
        verify_only = bool(getattr(args, "verify_only", False))
        preflight_only = bool(getattr(args, "preflight_only", False))
        if verify_only and (run.mode != "full" or run.revision != "r001"):
            raise AcquisitionError("VERIFY_ONLY_REQUIRES_FULL_R001")
        trace = verify_petes_lake_repository_preflight(
            run,
            existing_success_outputs=verify_only,
        )
        if preflight_only:
            print("PASS_PETES_LAKE_U02_PREFLIGHT_NO_CREDENTIALS")
            return 0
        if verify_only:
            reasons = validate_u03_prerequisite(run)
            if reasons:
                raise AcquisitionError(
                    "PETES_LAKE_U02_VERIFY_ONLY_FAILED",
                    detail=",".join(reasons),
                )
            print("PASS_PETES_LAKE_U02_VERIFY_ONLY_NO_CREDENTIALS")
            return 0
        if run.mode == "aggregate-only":
            result = finalize_petes_lake_aggregate_only(run=run, trace=trace)
        else:
            credentials = CdseCredentials.from_environment()
            if run.mode == "post-only":
                result = resume_petes_lake_post_only(
                    credentials=credentials,
                    run=run,
                    trace=trace,
                    progress=_progress,
                )
            else:
                result = acquire_petes_lake_optical_pair(
                    credentials=credentials,
                    run=run,
                    trace=trace,
                    progress=_progress,
                )
        print(result["decision"])
        return 0
    except (AcquisitionError, OSError, ValueError) as error:
        if isinstance(error, AcquisitionError):
            print(str(error), file=sys.stderr)
        else:
            print(f"LOCAL_TRANSACTION_FAILURE; detail={type(error).__name__}", file=sys.stderr)
        return 2
    finally:
        credentials = None


if __name__ == "__main__":
    raise SystemExit(main())
