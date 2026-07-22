"""Build the exact Petes Lake U03 source-fitness preview or final evidence."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys

from .petes_lake_source_fitness import (
    REPORT_ID,
    VISUAL_FAIL,
    VISUAL_PASS,
    VISUAL_PENDING,
    PetesLakeSourceFitnessError,
    build_report,
    write_outputs,
)


BRANCH = "codex/p2o4-t33-petes-lake-milestone"
U02_EVIDENCE_COMMIT = "11580b28e5b8dd4be0b68420d0baf096c95b7e9b"
PLAN_PATH = Path("samples/cross-event/phase-two/ADDITIONAL-EVENT-GROUP-PLAN-2026-001.json")
CUSTODY_REPORT_PATH = Path(
    "samples/cross-event/phase-two/petes-lake/PETES-LAKE-OPTICAL-CUSTODY-2026-001.json"
)
PREVIEW_DIRECTORY = Path(
    "downloads/phase-two/runs/P2O4-T33-U03/petes-lake-source-fitness-preview-r002"
)
FINAL_DIRECTORY = Path("samples/cross-event/phase-two/petes-lake")


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=False
    )


def _preflight(root: Path) -> str:
    top = _git(root, "rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != root:
        raise PetesLakeSourceFitnessError("repository root mismatch")
    branch = _git(root, "branch", "--show-current")
    if branch.returncode != 0 or branch.stdout.strip() != BRANCH:
        raise PetesLakeSourceFitnessError("branch mismatch")
    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if status.returncode != 0 or status.stdout.strip():
        raise PetesLakeSourceFitnessError("worktree is not clean")
    head = _git(root, "rev-parse", "HEAD")
    commit = head.stdout.strip()
    if head.returncode != 0 or len(commit) != 40:
        raise PetesLakeSourceFitnessError("committed source HEAD required")
    ancestor = _git(root, "merge-base", "--is-ancestor", U02_EVIDENCE_COMMIT, commit)
    if ancestor.returncode != 0:
        raise PetesLakeSourceFitnessError("U02 evidence is not an ancestor")
    return commit


def _timestamp(value: str) -> str:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise argparse.ArgumentTypeError("generated timestamp must be ISO-8601") from None
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--generated-at-utc", type=_timestamp, required=True)
    parser.add_argument("--mode", choices=("preview", "final"), required=True)
    parser.add_argument(
        "--visual-review-decision",
        choices=(VISUAL_PASS, VISUAL_FAIL),
    )
    parser.add_argument("--visual-review-notes", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        root = args.repository_root.resolve()
        commit = _preflight(root)
        if args.mode == "preview":
            if args.visual_review_decision or args.visual_review_notes:
                raise PetesLakeSourceFitnessError("preview cannot contain a visual decision")
            decision = VISUAL_PENDING
            notes = ""
            run_id = "BL-2026-07-21-petes-lake-source-fitness-preview-r002"
            directory = root / PREVIEW_DIRECTORY
        else:
            if args.visual_review_decision is None:
                raise PetesLakeSourceFitnessError("final output requires a visual decision")
            decision = args.visual_review_decision
            notes = args.visual_review_notes
            run_id = "BL-2026-07-21-petes-lake-source-fitness-r001"
            directory = root / FINAL_DIRECTORY
        report, previews = build_report(
            repository_root=root,
            plan_path=root / PLAN_PATH,
            custody_report_path=root / CUSTODY_REPORT_PATH,
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
                    "decision": report["fitness_decision"]["optical_source"],
                    "outputs": outputs,
                },
                sort_keys=True,
            )
        )
        return 0
    except (OSError, ValueError, PetesLakeSourceFitnessError) as error:
        print(f"PETES_LAKE_U03_FAILURE; reason={error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
