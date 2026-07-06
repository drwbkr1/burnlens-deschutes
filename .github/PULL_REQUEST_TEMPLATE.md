# Pull request checklist

## Summary

- Adds or updates:
- Task issue:
- Parent issue:
- Branch:

## Required task linkage

- [ ] PR title uses the task pattern, for example `P1O4-T06 Add issue and PR templates`.
- [ ] PR body uses a close keyword for the task issue only.
- [ ] PR body does not close the objective parent issue unless this is an approved closeout task.
- [ ] Dependencies are named if this PR depends on another open PR or unmerged artifact.

## Artifact contract

- [ ] The task artifact contract was defined before artifact creation.
- [ ] Artifact path or paths are correct.
- [ ] The artifact explains purpose, scope, decisions, and handoff.
- [ ] The artifact includes acceptance and rejection or defer criteria where applicable.

## Research gate

- [ ] Fresh research was completed after branch creation and before artifact writing.
- [ ] Research-backed claims are documented in the artifact or task issue.
- [ ] Official or primary sources were preferred where available.
- [ ] Current or technical claims are not based on memory alone.

## Boundary gate

- [ ] This PR is documentation, template, workflow, or records work only, unless a later phase explicitly authorizes implementation.
- [ ] This PR does not create or process imagery, AOI data, labels, masks, baselines, model outputs, metrics, maps, or public demo artifacts.
- [ ] This PR does not claim operational reliability, official status, field validation, agency endorsement, or emergency-use readiness.
- [ ] If public-facing language is affected, official sources remain authoritative and BurnLens outputs remain experimental.

## Review gate

- [ ] Diff contains only intended files.
- [ ] No temporary connector test files are included.
- [ ] Branch naming follows `p1o4tXXb` or the later-phase equivalent.
- [ ] Commit history can be squash-merged cleanly.
- [ ] Handoff note identifies the next task or closeout action.

## Post-merge update

After merge:

- [ ] Task issue will be closed by the task-scoped close keyword.
- [ ] Parent issue will receive a comment with task, PR, artifact path, status, and next task.
- [ ] Tracker or handoff files will be updated if the current task requires it.
