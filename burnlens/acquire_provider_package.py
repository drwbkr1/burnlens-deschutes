"""Acquire and register the exact owner-authorized BurnLens source package."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .provider_acquisition import (
    AcquisitionError,
    ProviderCredentials,
    acquire_exact_package,
    refresh_public_metadata,
    write_private_state,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quarantine", type=Path, required=True)
    parser.add_argument("--raw-parent", type=Path, required=True)
    parser.add_argument("--state-file", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    return parser.parse_args()


def _progress(role: str, observed: int, expected: int) -> None:
    percent = 100 * observed / expected if expected else 0
    print(f"{role}: {observed:,}/{expected:,} bytes ({percent:.1f}%)", flush=True)


def main() -> int:
    args = parse_args()
    credentials: ProviderCredentials | None = None
    try:
        credentials = ProviderCredentials.from_environment()
        metadata = refresh_public_metadata(observed_at_utc=args.generated_at_utc)
        result = acquire_exact_package(
            credentials=credentials,
            quarantine=args.quarantine,
            raw_parent=args.raw_parent,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            metadata_snapshot=metadata,
            progress=_progress,
        )
        write_private_state(args.state_file, result)
        print(result["decision"])
        return 0
    except AcquisitionError as error:
        safe_failure = {
            "decision": "ACQUISITION_FAILED",
            "reason_code": error.reason_code,
            "role": error.role,
            "detail": error.detail,
        }
        write_private_state(args.state_file, safe_failure)
        print(str(error), file=sys.stderr)
        return 2
    finally:
        credentials = None


if __name__ == "__main__":
    raise SystemExit(main())
