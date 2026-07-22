"""Build preview or final Petes Lake U05 reference-fitness evidence."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys

from .petes_lake_reference_fitness import (
    BRANCH,
    FINAL_DIRECTORY,
    PREVIEW_DIRECTORY,
    PREVIEW_RUN_ID,
    REPORT_ID,
    RUN_ID,
    VISUAL_FAIL,
    VISUAL_FAIL_NOTE,
    VISUAL_PASS,
    VISUAL_PASS_NOTE,
    VISUAL_PENDING,
    PetesLakeReferenceFitnessError,
    build_report,
    write_outputs,
)


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=False
    )


def _preflight(root: Path) -> str:
    top = _git(root, "rev-parse", "--show-toplevel")
    branch = _git(root, "branch", "--show-current")
    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    head = _git(root, "rev-parse", "HEAD")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != root:
        raise PetesLakeReferenceFitnessError("repository root mismatch")
    if branch.returncode != 0 or branch.stdout.strip() != BRANCH:
        raise PetesLakeReferenceFitnessError("milestone branch mismatch")
    if status.returncode != 0 or status.stdout.strip():
        raise PetesLakeReferenceFitnessError("worktree must be clean")
    commit = head.stdout.strip()
    if head.returncode != 0 or len(commit) != 40:
        raise PetesLakeReferenceFitnessError("exact committed source HEAD required")
    remote = _git(
        root,
        "-c",
        "credential.interactive=never",
        "ls-remote",
        "--heads",
        "origin",
        BRANCH,
    )
    if remote.returncode != 0 or remote.stdout.split() != [commit, f"refs/heads/{BRANCH}"]:
        raise PetesLakeReferenceFitnessError("remote branch is not exactly equal to HEAD")
    return commit


def _timestamp(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise argparse.ArgumentTypeError("generated timestamp must be ISO-8601") from None
    if not value.endswith("Z") or parsed.tzinfo is None:
        raise argparse.ArgumentTypeError("generated timestamp must be UTC Z")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--generated-at-utc", type=_timestamp, required=True)
    parser.add_argument("--mode", choices=("preview", "final"), required=True)
    parser.add_argument("--visual-review-decision", choices=(VISUAL_PASS, VISUAL_FAIL))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        root = args.repository_root.resolve()
        commit = _preflight(root)
        if args.mode == "preview":
            if args.visual_review_decision:
                raise PetesLakeReferenceFitnessError("preview cannot contain a visual decision")
            decision = VISUAL_PENDING
            notes = ""
            run_id = PREVIEW_RUN_ID
            directory = root / PREVIEW_DIRECTORY
        else:
            if args.visual_review_decision is None:
                raise PetesLakeReferenceFitnessError("final requires a visual decision")
            decision = args.visual_review_decision
            notes = VISUAL_PASS_NOTE if decision == VISUAL_PASS else VISUAL_FAIL_NOTE
            run_id = RUN_ID
            directory = root / FINAL_DIRECTORY
        report, previews = build_report(
            repository_root=root,
            generated_at_utc=args.generated_at_utc,
            run_id=run_id,
            git_source_commit=commit,
            visual_review_decision=decision,
            visual_review_notes=notes,
        )
        outputs = write_outputs(report, previews, directory)
        print(
            json.dumps(
                {
                    "report_id": REPORT_ID,
                    "run_id": run_id,
                    "decision": report["fitness_decision"]["code"],
                    "accepted_reference_pixels": report["fitness_decision"][
                        "accepted_reference_pixels"
                    ],
                    "outputs": outputs,
                },
                sort_keys=True,
            )
        )
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print(f"PETES_LAKE_U05_REFERENCE_FITNESS_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
