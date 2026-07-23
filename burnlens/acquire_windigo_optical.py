"""Acquire or verify the exact Windigo Sentinel-2 pair."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .provider_acquisition import AcquisitionError
from .windigo_optical_contract import (
    CdseCredentials,
    WindigoOpticalRun,
    acquire_windigo_optical_pair,
    refresh_windigo_metadata,
    verify_windigo_completed,
    verify_windigo_repository_preflight,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    gate = parser.add_mutually_exclusive_group()
    gate.add_argument("--preflight-only", action="store_true")
    gate.add_argument("--verify-only", action="store_true")
    return parser.parse_args()


def _progress(role: str, observed: int, expected: int) -> None:
    percent = 100 * observed / expected if expected else 0
    try:
        print(f"{role}: {observed:,}/{expected:,} bytes ({percent:.1f}%)", flush=True)
    except (BrokenPipeError, OSError):
        # A detached or closed display channel must not be misclassified as an
        # archive write failure or interrupt exact-byte custody.
        return


def main() -> int:
    args = parse_args()
    credentials: CdseCredentials | None = None
    try:
        run = WindigoOpticalRun.create(
            repository_root=args.repository_root,
            generated_at_utc=args.generated_at_utc,
        )
        trace = verify_windigo_repository_preflight(
            run,
            existing_success_outputs=bool(args.verify_only),
        )
        if args.preflight_only:
            snapshot = refresh_windigo_metadata(observed_at_utc=args.generated_at_utc)
            print(
                "PASS_WINDIGO_U02_PREFLIGHT_NO_CREDENTIALS "
                f"products={len(snapshot['records'])}"
            )
            return 0
        if args.verify_only:
            reasons = verify_windigo_completed(run)
            if reasons:
                raise AcquisitionError("WINDIGO_U02_VERIFY_FAILED", detail=",".join(reasons))
            print("PASS_WINDIGO_U02_VERIFY_ONLY_NO_CREDENTIALS")
            return 0
        metadata = refresh_windigo_metadata(observed_at_utc=args.generated_at_utc)
        credentials = CdseCredentials.from_environment()
        result = acquire_windigo_optical_pair(
            run=run,
            trace=trace,
            credentials=credentials,
            metadata_snapshot=metadata,
            progress=_progress,
        )
        print(result["decision"])
        return 0
    except (AcquisitionError, OSError, ValueError, json.JSONDecodeError) as error:
        if isinstance(error, AcquisitionError):
            print(str(error), file=sys.stderr)
        else:
            print(f"WINDIGO_LOCAL_TRANSACTION_FAILURE; detail={type(error).__name__}", file=sys.stderr)
        return 2
    finally:
        credentials = None


if __name__ == "__main__":
    raise SystemExit(main())
