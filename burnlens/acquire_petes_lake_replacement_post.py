"""Acquire or verify the exact Petes Lake October 19 replacement post archive."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .petes_lake_replacement_optical_contract import (
    CdseCredentials,
    ReplacementOpticalRun,
    acquire_replacement_post,
    finalize_replacement_custody,
    verify_replacement_custody,
    verify_replacement_repository_preflight,
)
from .provider_acquisition import AcquisitionError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--revision", required=True, help="Immutable revision r001-r999")
    parser.add_argument(
        "--mode",
        choices=("acquire", "finalize"),
        default="acquire",
        help="Acquire r001, or finish from an already registered archive at r002+",
    )
    gate = parser.add_mutually_exclusive_group()
    gate.add_argument(
        "--preflight-only",
        action="store_true",
        help="Run every credential-free gate and exit before reading credentials",
    )
    gate.add_argument(
        "--verify-only",
        action="store_true",
        help="Credential-free recomputation of completed custody outputs",
    )
    return parser.parse_args()


def _progress(role: str, observed: int, expected: int) -> None:
    percent = 100 * observed / expected if expected else 0
    print(f"{role}: {observed:,}/{expected:,} bytes ({percent:.1f}%)", flush=True)


def main() -> int:
    args = parse_args()
    credentials: CdseCredentials | None = None
    try:
        run = ReplacementOpticalRun.create(
            repository_root=args.repository_root,
            generated_at_utc=args.generated_at_utc,
            revision=args.revision,
            mode=args.mode,
        )
        verify_only = bool(getattr(args, "verify_only", False))
        preflight_only = bool(getattr(args, "preflight_only", False))
        preflight = verify_replacement_repository_preflight(
            run,
            existing_success_outputs=verify_only,
        )
        if preflight_only:
            print("PASS_PETES_LAKE_REPLACEMENT_PREFLIGHT_NO_CREDENTIALS")
            return 0
        if verify_only:
            reasons = verify_replacement_custody(run=run, preflight=preflight)
            if reasons:
                raise AcquisitionError(
                    "PETES_LAKE_REPLACEMENT_VERIFY_ONLY_FAILED",
                    detail=",".join(reasons),
                )
            print("PASS_PETES_LAKE_REPLACEMENT_VERIFY_ONLY_NO_CREDENTIALS")
            return 0
        if run.mode == "finalize":
            result = finalize_replacement_custody(run=run, preflight=preflight)
        else:
            credentials = CdseCredentials.from_environment()
            result = acquire_replacement_post(
                credentials=credentials,
                run=run,
                preflight=preflight,
                progress=_progress,
            )
        decision = (result.get("semantic_record") or {}).get("decision")
        if not isinstance(decision, str) or not decision:
            raise AcquisitionError("PETES_LAKE_REPLACEMENT_RESULT_DECISION_MISSING")
        print(decision)
        return 0
    except (AcquisitionError, OSError, ValueError) as error:
        if isinstance(error, AcquisitionError):
            print(str(error), file=sys.stderr)
        else:
            print(
                f"PETES_LAKE_REPLACEMENT_LOCAL_FAILURE; detail={type(error).__name__}",
                file=sys.stderr,
            )
        return 2
    finally:
        credentials = None


if __name__ == "__main__":
    raise SystemExit(main())
