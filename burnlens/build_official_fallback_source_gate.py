"""Build the deterministic P2O4-T34 official-fallback comparison report."""

from __future__ import annotations

import argparse
from pathlib import Path

from .official_fallback_source_gate import OfficialFallbackGateError, run_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    args = parser.parse_args()
    try:
        paths = run_report(
            repository_root=args.repository_root,
            output_directory=args.output_directory,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
    except (OfficialFallbackGateError, OSError, ValueError, KeyError, TypeError) as error:
        print(f"OFFICIAL_FALLBACK_SOURCE_GATE_FAILED: {error}")
        return 2
    for name, path in paths.items():
        print(f"{name}={path}")
    print("decision=DEFER_BOTH_OFFICIAL_FALLBACK_CANDIDATES_SELECT_NEITHER_NO_PROVIDER_BYTES_AUTHORIZED")
    print("provider_bytes_authorized=false")
    print("provider_bytes_acquired=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
