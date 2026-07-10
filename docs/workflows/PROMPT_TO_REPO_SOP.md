# BurnLens Prompt-to-Repo SOP

## Status

This SOP is the repo-level reference for prompt-assisted BurnLens work after Phase One / Objective Five.

It is not meant to be pasted in full into every ChatGPT chat. Each task chat should use the short quickstart and a compact task capsule, then load only the governing artifacts required for that task.

## Quickstart for a new task chat

1. Start from `OBJECTIVE_FIVE_HANDOFF.md` when beginning Phase Two, Objective Six, or baseline-tag QA.
2. Load Tier 0 governing artifacts.
3. Select only the Tier 1 artifacts relevant to the task.
4. Ignore Tier 2 historical context unless verification requires it.
5. Create or confirm the GitHub task issue.
6. Create one task branch from current `main`.
7. Preserve a task capsule before editing files.
8. Write only the allowed files.
9. Create or update a prompt/build log when prompt-assisted edits occur.
10. Diff-check the branch before PR.
11. Open a PR that closes only the task issue.
12. Run a status sync only when README, tracker, or prompt logs are stale after merge.

## Operating model

The full SOP is a reference manual. The task capsule is the executable prompt.

```text
Full SOP = stored repo reference.
Task capsule = compact task-specific operating prompt.
Chat handoff = compact context transfer.
New chat = optional context-management tool, not a GitHub workflow unit.
```

## Context tiers

### Tier 0: always governing context

Load or summarize these for every repository task:

```text
AGENTS.md
README.md
VERSIONING.md
docs/objective-one/TECHNICAL_DESCRIPTION.md
docs/objective-one/USE_BOUNDARIES.md
docs/objective-one/SOURCE_PRECEDENCE.md
docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_HANDOFF.md
records/PROMPT_BUILD_LOG.md
templates/PROMPT_LOG_ENTRY.md
```

### Tier 1: task-specific governing context

Load only the documents that match the work.

| Task type | Add these artifacts |
|---|---|
| CV task definition or model direction | `docs/phase-one/objective-two/`; `TECHNICAL_DESCRIPTION.md`; `REPRODUCIBILITY_CHECKLIST.md`; `RELEASE_QA_CHECKLIST.md` |
| Source, AOI, CRS, or provenance feasibility | `docs/phase-one/objective-three/`; `SOURCE_PRECEDENCE.md`; `PROVENANCE_TRACEABILITY_SPEC.md`; `ARTIFACT_REGISTRY_SPEC.md`; `RUN_PACKAGE_CONTRACT.md` |
| GitHub workflow, issues, PRs, or prompt logs | `BRANCH_AND_PR_WORKFLOW.md`; `templates/CODEX_TASK_PACKET.md`; `.github/ISSUE_TEMPLATE/task.yml`; `.github/PULL_REQUEST_TEMPLATE.md`; `records/PROMPT_BUILD_LOG.md` |
| Versioning, tags, releases, or baselines | `VERSIONING.md`; `VERSION_TAXONOMY.md`; `RELEASE_CONTROL.md`; `RELEASE_QA_CHECKLIST.md`; `OBJECTIVE_FIVE_RELEASE_NOTE.md`; `templates/RELEASE_NOTE_TEMPLATE.md` |
| Provenance, traceability, or run packages | `PROVENANCE_TRACEABILITY_SPEC.md`; `RUN_PACKAGE_CONTRACT.md`; `ARTIFACT_REGISTRY_SPEC.md`; `TRACEABILITY_RECORD_TEMPLATE.md`; `RUN_MANIFEST_TEMPLATE.json` |
| Claims, public copy, portfolio copy, or website language | `CLAIM_TRACEABILITY_PROTOCOL.md`; `CLAIM_EVIDENCE_LINK_TEMPLATE.md`; `OBJECTIVE_FIVE_CLAIMS_CHECK.md`; `SOURCE_PRECEDENCE_RELEASE_GATE.md`; `USE_BOUNDARIES.md`; `SOURCE_PRECEDENCE.md` |
| Reproducibility or release QA | `REPRODUCIBILITY_CHECKLIST.md`; `RELEASE_QA_CHECKLIST.md`; `RELEASE_CONTROL.md`; `OBJECTIVE_FIVE_RELEASE_NOTE.md` |
| Research-backed decisions | `OBJECTIVE_FIVE_RESEARCH_VALIDATION_LOG.md`; `OBJECTIVE_FIVE_CLAIMS_CHECK.md` |
| Phase Two or Objective Six handoff | `OBJECTIVE_FIVE_CLOSEOUT.md`; `OBJECTIVE_FIVE_HANDOFF.md`; README; tracker; relevant Tier 1 controls |

### Tier 2: historical or verification context

Use only when needed for audit or ambiguity:

```text
old prompt/build logs
old PR bodies
old issue comments
closed task issues
historical closeout notes
merged task branches
archived objective documents
prior current-status files
```

Do not load Tier 2 by default.

## Task capsule

Every task chat should start with a compact capsule:

```text
Task ID:
Parent issue:
Task issue:
Branch:
Primary artifacts:
Supporting artifacts:
Allowed file changes:
Forbidden work, by reference:
Tier 0 artifacts:
Tier 1 artifacts:
Tier 2 artifacts, if needed:
Research required:
Acceptance criteria:
PR close keyword:
Post-merge sync needed:
Parent issue close behavior:
```

Use references to governing boundary files instead of repeating long boundary language in every capsule.

## Chat handoff capsule

Every task chat should end with:

```text
Completed:
Merged PR:
Merge commit:
Files changed:
Status updates completed:
Safe claims:
Caveated claims:
Unsupported claims:
Next task:
Required context for next chat:
Do not carry forward:
```

The `Do not carry forward` line should explicitly discard drafting details that are no longer needed once merged artifacts exist.

## Objective Five control routing

Before starting work, answer these questions:

```text
Does this touch source data, AOI files, labels, models, runs, maps, reports, screenshots, or public demos?
Does this create or modify a source record, AOI record, data manifest, run manifest, or registry entry?
Does this make a public-facing claim?
Does this involve source precedence or official-source conflict?
Does this require reproducibility review or release QA?
Does this propose a tag or GitHub Release?
```

If yes, load the matching Tier 1 controls before writing files.

## Before-data gate

Before any future task touches data, imagery, AOI files, labels, masks, baselines, model inputs, or run outputs, the task must have reviewable records for:

```text
task issue explicitly authorizing the action
branch and PR scope
source candidate or source record
access method record
license or terms note
format and CRS precheck
AOI record and AOI identifier
provenance or traceability record
artifact registry classification
source-precedence review
use-boundary review
prompt/build log if prompt-assisted
README or tracker update if repo truth changes
```

If these records do not exist, stop before touching data and create a planning/control task instead.

## Public-claim gate

Before public-facing language is used, verify that the claim:

```text
has a claim type
has evidence
has limitations where needed
preserves source precedence where needed
does not exceed repo evidence
is allowed by OBJECTIVE_FIVE_CLAIMS_CHECK.md
```

If the claim touches fire, hazard, road, evacuation, incident, or public-safety context, apply the source-precedence gate and required boundary wording from the governing artifacts.

## Release/tag separation rule

```text
Proposed tag != created tag.
Release-note draft != GitHub Release.
Objective baseline != public release unless explicitly authorized.
GitHub tag creation requires explicit authorization.
GitHub Release publication requires separate explicit authorization.
```

Current proposed Objective Five baseline tag:

```text
v0.0.5-objective-five-traceability
```

Status: proposed only, not created, and not published as a GitHub Release.

## Prompt/build log compaction rule

Prompt/build logs are administrative traceability records. They should record:

```text
task identity
issue
branch
PR
merge commit when known
files changed
governing artifacts
research source summary
material decisions
verification
tag/release/data/public-output status where relevant
handoff
```

Do not repeat every governing boundary in full. Name the governing artifact instead.

## Connector-friction fallback

If a GitHub connector action blocks a long issue comment, PR body, or prompt log:

1. Retry once with concise administrative wording.
2. If still blocked, preserve the contract in the prompt log, PR body, or primary artifact.
3. Use artifact references instead of repeating long boundary lists.
4. Record the connector-friction note when useful.

A blocked comment does not invalidate the task if the contract remains preserved elsewhere and the PR remains reviewable.

## Issue, branch, PR, and merge rules

For each task:

```text
create or confirm task issue
create branch from current main
post or preserve artifact contract
write only allowed files
perform required research after branch creation
create/update prompt log when prompt-assisted
diff-check branch against main
open PR with close keyword for task issue only
avoid closing parent issue from ordinary task PR
squash merge if clean
update parent issue after merge
run status sync if current-status files are stale
```

## Post-merge sync rule

Run a sync task only when a merged PR leaves current-status files stale.

Sync tasks usually update only:

```text
README.md
objective tracker
records/PROMPT_BUILD_LOG.md
the task prompt log
the sync prompt log
```

## Closeout rule

A parent objective may close only when:

```text
planned tasks are closed or intentionally deferred
closeout artifact exists
handoff artifact exists
release-note draft exists if relevant
README reflects current status
tracker reflects current status
prompt-log index reflects current status
parent issue has final summary comment
unsupported claims remain blocked
no unauthorized data, model, public-output, tag, or release work occurred
```

## Success standard

This SOP succeeds when each task can be completed with:

```text
small context
clear branch scope
tight artifact contract
minimal repeated history
strong evidence links
clean PR
clean status sync
reusable chat handoff
```
