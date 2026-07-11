# BurnLens Prompt-to-Repo SOP

## Status

This SOP is the repo-level reference for prompt-assisted BurnLens work after Phase One / Objective Five.

It is not meant to be pasted in full into every ChatGPT or Codex task. Each task should use the short quickstart, an authorized GitHub issue, and a compact task capsule, then load only the governing artifacts required for that work.

## Quickstart for a new task chat

1. Start from `docs/phase-one/objective-five/OBJECTIVE_FIVE_HANDOFF.md` when beginning Phase Two, Objective Six, or baseline-tag QA.
2. Load or summarize Tier 0 governing artifacts.
3. Select only the Tier 1 artifacts relevant to the task.
4. Ignore Tier 2 historical context unless a specific verification question requires it; record each Tier 2 artifact and reason when used.
5. Create or confirm the GitHub task issue through `.github/ISSUE_TEMPLATE/task.yml` or an equivalent explicitly approved issue contract.
6. Instantiate the canonical task capsule in `templates/CODEX_TASK_PACKET.md` without broadening the issue.
7. Create one compact task branch from current `main` unless the issue authorizes another base.
8. Preserve the approved task capsule before editing files.
9. Write only the allowed files and stop before any unapproved scope expansion.
10. Create or update a dated prompt/build log when prompt-assisted edits occur.
11. Run named checks with exact methods and actual results, or document a task-specific reason when a check does not apply.
12. Diff-check the complete branch against the authorized base before PR.
13. Open a PR that closes only the task issue and routes detailed inspection to `docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md`.
14. Treat AI-assisted review as supplemental; a human must inspect the task and record an outcome before merge.
15. Merge only after the human outcome is **Approve**, blocking findings are resolved, and merge authorization is recorded.
16. Run a status sync only when README, tracker, or prompt-log truth is stale after merge.

## Operating model

The full SOP is a reference manual. The GitHub issue is the authorization record. The task capsule is the executable prompt.

```text
Full SOP = stored repository reference.
Task issue = bounded authorization and intake record.
Task capsule = compact task-specific operating prompt.
Chat handoff = compact context transfer.
New chat = optional context-management tool, not a GitHub workflow unit.
```

## Canonical workflow artifact roles

Use these artifacts according to their roles. A routing or compatibility artifact must not become a second source of truth.

| Artifact | Role |
|---|---|
| `docs/workflows/PROMPT_TO_REPO_SOP.md` | Full repository workflow reference, context tiers, gates, and closeout rules. |
| `AGENTS.md` | Repository-level instructions for Codex, ChatGPT, and other prompt-assisted agents. |
| `CONTRIBUTING.md` | Human-facing contribution and solo-maintainer workflow guidance. |
| `.github/ISSUE_TEMPLATE/task.yml` | Structured issue-first intake surface for one bounded task contract. It does not replace the canonical task capsule. |
| `templates/CODEX_TASK_PACKET.md` | Canonical executable task capsule and source of truth for task-specific operating fields. |
| `templates/CODEX_TASK_TEMPLATE.md` | Non-canonical compatibility and discoverability entry point to the task packet. |
| `PROMPT_LOG.md` | Non-canonical root navigation for prompt/build logging. |
| `records/PROMPT_BUILD_LOG.md` | Canonical prompt/build-log protocol and dated-entry index. |
| `templates/PROMPT_LOG_ENTRY.md` | Canonical detailed prompt/build-log entry template. |
| `docs/phase-one/objective-six/PROMPT_BUILT_DEVELOPMENT_PROTOCOL.md` | Objective Six architecture showing how issue, capsule, branch, research, logging, verification, review, merge, and handoff fit together. |
| `docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md` | Detailed reusable review record separating author self-audit, executable checks, optional AI review, human inspection, and merge authorization. |
| `.github/PULL_REQUEST_TEMPLATE.md` | Concise PR intake and evidence surface that routes detailed review to the standalone checklist. |
| `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md` | Branch, PR, merge-method, and post-merge baseline retained by Objective Six. |

The task issue authorizes the work. The completed task capsule may narrow the issue but may not broaden it. The issue form, task packet, contributor guide, prompt-log controls, PR template, and review checklist must stay aligned without duplicating one another in full.

## Current GitHub and Codex integration notes

The following current platform behavior informs the workflow but does not create repository enforcement:

- GitHub issue forms are YAML files in `.github/ISSUE_TEMPLATE/` and currently remain a public-preview feature.
- Issue-form top-level metadata may include `name`, `description`, `body`, and optional `title`, `labels`, `assignees`, `projects`, and organization-defined `type`.
- Form input IDs must use supported characters and be unique. User-input labels must also be unique enough for GitHub validation.
- GitHub applies a configured default label only when that label already exists in the repository.
- Template-chooser behavior belongs in `.github/ISSUE_TEMPLATE/config.yml`; an issue-form task must not modify that file unless its issue explicitly allows it.
- Closing keywords link and close issues only when the PR targets the repository default branch and the change is merged.
- OpenAI Codex can provide a repository-guided GitHub review pass and can follow `AGENTS.md`; that review is supplemental evidence and is not BurnLens human approval or merge authorization.

Official-source references for current platform statements:

- GitHub Docs, Syntax for issue forms: `https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms`
- GitHub Docs, Syntax for GitHub's form schema: `https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-githubs-form-schema`
- GitHub Docs, Common validation errors when creating issue forms: `https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/common-validation-errors-when-creating-issue-forms`
- GitHub Docs, Configuring issue templates for your repository: `https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository`
- GitHub Docs, Linking a pull request to an issue: `https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue`
- OpenAI, Codex code review in GitHub: `https://developers.openai.com/codex/integrations/github`

Research-backed wording must still be rechecked after branch creation when a later task depends on current platform behavior.

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

Tier 0 establishes project identity, workflow, version posture, source precedence, boundaries, logging, and the latest safe handoff. The issue form should acknowledge Tier 0 but does not need to duplicate this list inside every submitted issue body.

### Tier 1: task-specific governing context

Load only the documents that match the work.

| Task type | Add these artifacts |
|---|---|
| CV task definition or model direction | `docs/phase-one/objective-two/`; `TECHNICAL_DESCRIPTION.md`; `REPRODUCIBILITY_CHECKLIST.md`; `RELEASE_QA_CHECKLIST.md` |
| Source, AOI, CRS, or provenance feasibility | `docs/phase-one/objective-three/`; `SOURCE_PRECEDENCE.md`; `PROVENANCE_TRACEABILITY_SPEC.md`; `ARTIFACT_REGISTRY_SPEC.md`; `RUN_PACKAGE_CONTRACT.md` |
| GitHub workflow, issues, PRs, review, or prompt logs | `CONTRIBUTING.md`; `BRANCH_AND_PR_WORKFLOW.md`; `PROMPT_BUILT_DEVELOPMENT_PROTOCOL.md`; `PR_REVIEW_CHECKLIST.md`; `.github/ISSUE_TEMPLATE/task.yml`; `.github/PULL_REQUEST_TEMPLATE.md`; `templates/CODEX_TASK_PACKET.md`; `records/PROMPT_BUILD_LOG.md` |
| Versioning, tags, releases, or baselines | `VERSIONING.md`; `VERSION_TAXONOMY.md`; `RELEASE_CONTROL.md`; `RELEASE_QA_CHECKLIST.md`; `OBJECTIVE_FIVE_RELEASE_NOTE.md`; `templates/RELEASE_NOTE_TEMPLATE.md` |
| Provenance, traceability, or run packages | `PROVENANCE_TRACEABILITY_SPEC.md`; `RUN_PACKAGE_CONTRACT.md`; `ARTIFACT_REGISTRY_SPEC.md`; `TRACEABILITY_RECORD_TEMPLATE.md`; `RUN_MANIFEST_TEMPLATE.json` |
| Claims, public copy, portfolio copy, or website language | `CLAIM_TRACEABILITY_PROTOCOL.md`; `CLAIM_EVIDENCE_LINK_TEMPLATE.md`; `OBJECTIVE_FIVE_CLAIMS_CHECK.md`; `SOURCE_PRECEDENCE_RELEASE_GATE.md`; `USE_BOUNDARIES.md`; `SOURCE_PRECEDENCE.md` |
| Reproducibility or release QA | `REPRODUCIBILITY_CHECKLIST.md`; `RELEASE_QA_CHECKLIST.md`; `RELEASE_CONTROL.md`; `OBJECTIVE_FIVE_RELEASE_NOTE.md` |
| Research-backed decisions | `OBJECTIVE_FIVE_RESEARCH_VALIDATION_LOG.md`; `OBJECTIVE_FIVE_CLAIMS_CHECK.md`; current official or primary sources named in the task issue |
| Phase Two or Objective Six handoff | `OBJECTIVE_FIVE_CLOSEOUT.md`; `OBJECTIVE_FIVE_HANDOFF.md`; README; current tracker; relevant Objective Six and workstream controls |

Record the exact Tier 1 files used in the task capsule and prompt/build log. Selecting a Tier 1 group does not authorize every artifact in that group to be edited.

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

When Tier 2 is used, record each exact artifact and why current Tier 0 and Tier 1 controls were insufficient. Historical drafts must never override current merged controls.

## Issue-first task contract

Every meaningful task starts from a GitHub task issue or an explicitly approved bundled-task issue.

Use `.github/ISSUE_TEMPLATE/task.yml` as the default intake path. The form should capture or require:

```text
generic task ID
parent issue
intended branch and base
dependencies
primary and supporting artifacts
allowed file changes
forbidden work and governing references
Tier 0 acknowledgement
relevant Tier 1 selection
Tier 2 use and justification
research requirement and plan
prompt-assisted status and prompt-log path
test/check plan and non-applicability reasons
human-review requirement
acceptance criteria
handoff
task-scoped PR close keyword
parent-issue protection
```

The issue is authorization, not evidence that acceptance criteria have been met. GitHub form validation improves intake completeness but does not replace human review or repository settings.

## Task capsule

Every task chat should preserve a compact capsule derived from the authorized issue and `templates/CODEX_TASK_PACKET.md`:

```text
Task ID:
Parent issue:
Task issue:
Branch and base:
Dependencies:
Primary artifacts:
Supporting artifacts:
Allowed file changes:
Forbidden work, by reference:
Tier 0 artifacts:
Tier 1 artifacts:
Tier 2 artifacts, if needed, and reason:
Research required:
Prompt/build-log path:
Verification plan:
Acceptance criteria:
PR close keyword:
Post-merge sync needed:
Parent issue close behavior:
Handoff target:
```

Use references to governing boundary files instead of repeating long boundary language in every capsule.

The issue form is the structured intake surface. `templates/CODEX_TASK_PACKET.md` remains the canonical executable task capsule. A capsule may narrow the issue but may not add files, claims, or work the issue did not authorize.

## Chat handoff capsule

Every completed task or review chat should end with:

```text
Completed:
Issue and branch:
Pull request:
Merge commit:
Files changed:
Verification completed:
Status updates completed:
Safe claims:
Caveated claims:
Unsupported claims:
Remaining issues:
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

If yes, load the matching Tier 1 controls before writing files. The task issue must explicitly authorize the named work; loading controls alone is not authorization.

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

If these records do not exist, stop before touching data and create a planning or control task instead.

## Public-claim and source-precedence gate

Before public-facing language is used, verify that the claim:

```text
has a claim type
has evidence
has limitations where needed
preserves source precedence where needed
does not exceed repository evidence
is allowed by OBJECTIVE_FIVE_CLAIMS_CHECK.md
```

If the claim touches fire, hazard, road, evacuation, incident, or public-safety context, apply the source-precedence gate and required boundary wording from the governing artifacts.

Official sources govern. BurnLens-derived data, model, map, summary, and portfolio interpretation artifacts remain lower-priority experimental outputs.

## Version, tag, and Release separation rule

```text
Version identifier != readiness claim.
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
issue, parent, branch, and base
future or actual PR
primary and supporting artifacts
allowed and actual files
governing Tier 0 and selected Tier 1 context
Tier 2 use and reason, when applicable
research sources, supported facts, and adopted decisions
material decisions
named verification methods and actual results
checks not run and task-specific reasons
human-review status
tag, Release, data, model, and public-output status where relevant
handoff
```

Do not repeat every governing boundary in full. Name the governing artifact instead.

Do not record secrets, credentials, tokens, cookies, private URLs, private chain-of-thought, raw private transcripts, unnecessary personal information, or unreviewed operational guidance.

## Connector-friction fallback

If a GitHub connector action blocks a long issue comment, PR body, or prompt log:

1. Retry once with concise administrative wording.
2. If still blocked, preserve the contract in the prompt log, PR body, or primary artifact.
3. Use artifact references instead of repeating long boundary lists.
4. Record the connector-friction note when useful.

A blocked comment does not invalidate the task if the contract remains preserved elsewhere and the PR remains reviewable. Connector friction never authorizes broader scope, thinner artifacts, temporary files on `main`, or bypassed review.

## Issue, branch, file, PR, and merge rules

For each task:

```text
create or confirm the task issue
preserve the issue-backed task capsule
create a compact branch from current main unless another base is authorized
load Tier 0 and only relevant Tier 1 context
perform required research after branch creation
write only allowed files
create or update the prompt/build log when prompt-assisted
run named checks and record actual results or task-specific non-applicability
diff-check all branch content against the authorized base
open a PR with the task title pattern and task-only close keyword `Closes #TASK_ISSUE`
avoid closing the parent issue from an ordinary task PR
use AI-assisted review only as supplemental evidence
obtain recorded human review
merge only after human approval and separate merge authorization
prefer squash merge for bounded task branches when permitted and authorized
update the parent issue after merge
run status sync only when current-status files are stale
```

Prompt-assisted edits must not be made directly to `main`.

If another file becomes necessary, stop before changing it. Explain why the task contract is insufficient and obtain a human-approved issue and capsule revision or create a separate task.

## Verification rule

Verification is mandatory for every task.

For each applicable check, record:

```text
check name
exact command or manual inspection method
actual result: passed, failed, partial, blocked, or not applicable
relevant output or evidence
limitation or unresolved finding
```

Do not write `tests passed` unless named tests or commands actually ran.

`Not applicable` requires a task-specific reason. Documentation and template work may still require Markdown, YAML, JSON, path, link, structure, requirement-coverage, consistency, scope, boundary, claims, sensitive-material, and diff checks even when code or runtime tests do not apply.

Templates and written policy do not create CI jobs, required status checks, branch protection, rulesets, required approvals, CODEOWNERS, or other GitHub enforcement.

## Review separation and merge authorization

Keep these stages distinct:

1. **Author self-audit** — author assertions about scope, research, checks, boundaries, and handoff.
2. **Automated or executable checks** — commands or manual methods with actual results.
3. **AI-assisted review, when used** — supplemental findings against the diff or PR.
4. **Human reviewer inspection** — mandatory inspection of issue, capsule, complete diff, research, verification, acceptance, boundaries, close behavior, and handoff.
5. **Merge authorization** — separate authorization after the human outcome is **Approve** and blocking findings are resolved.

Use `docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md` for the detailed reusable record.

AI-assisted review may inspect the diff, identify omissions, flag defects or boundary violations, recommend checks, and confirm whether findings appear addressed. It may not approve its own work, satisfy the human gate, authorize scope expansion, configure settings, create tags or Releases, or authorize merge.

The human records exactly one outcome:

- **Approve**;
- **Request changes**;
- **Defer or reject**.

For the current solo-maintainer workflow, human policy evidence may be an explicit PR comment or completed review checklist. It is not formal GitHub author self-approval and does not claim platform enforcement.

Merge only after:

```text
human outcome is Approve
all blocking findings are resolved
dependencies are resolved or explicitly accepted
final diff remains inside allowed scope
required checks are accurately reported
unresolved comments are resolved or explicitly accepted
task-only close keyword is correct
parent issue remains protected
merge method is permitted and authorized
```

## Post-merge sync rule

Run a sync task only when a merged PR leaves current-status files stale.

Sync tasks usually update only:

```text
README.md
current objective tracker
records/PROMPT_BUILD_LOG.md
the task prompt log
the sync prompt log
```

After every merge, inspect current-status truth before deciding whether a sync task is necessary. Do not create automatic synchronization churn when the original task already left the records accurate.

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
no unauthorized data, model, public-output, tag, Release, or settings work occurred
human closeout review and authorization are recorded
```

An ordinary task PR must not close its parent objective issue.

## Success standard

This SOP succeeds when each task can be completed with:

```text
issue-first authorization
small context
selective Tier 1 loading
Tier 2 exclusion by default
clear branch and file scope
tight artifact contract
minimal repeated history
current official research when needed
named verification with actual results
supplemental AI review when useful
mandatory human review
clean task-only PR closure
clean status synchronization
reusable chat handoff
preserved data, claim, version, tag, and Release gates
```
