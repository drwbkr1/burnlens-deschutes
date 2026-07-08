# Prompt Build Log Protocol

## Purpose

This protocol defines how BurnLens Deschutes records prompt-assisted repository work.

The prompt/build log is a traceability record. It shows what task was attempted, which repo standards governed the work, which prompts or task packets were used, which source checks were made, which files changed, what verification occurred, and what was handed off next.

The log must not become a transcript dump, private reasoning record, credential store, or replacement for GitHub issues, branches, pull requests, commits, artifacts, or release notes.

## Current status

| Field | Value |
|---|---|
| Protocol task issue | #126 |
| Parent issue | #119 |
| Protocol PR | #138 |
| Protocol status | merged |
| Protocol file | `records/PROMPT_BUILD_LOG.md` |
| Entry template | `templates/PROMPT_LOG_ENTRY.md` |
| Active entry directory | `records/prompt-build-log/` |

## Research basis

Fresh research was conducted after branch creation and before the protocol was written.

| Claim ID | Claim | Source authority | Evidence summary | Decision for this protocol |
|---|---|---|---|---|
| P1O4-T09-R01 | Codex reads `AGENTS.md` files before doing work and uses repository-level guidance. | OpenAI Codex docs: Custom instructions with AGENTS.md | OpenAI states Codex reads `AGENTS.md` before work and builds guidance from global and project files. | Each prompt log entry must record whether `AGENTS.md` and project standards were used. |
| P1O4-T09-R02 | Codex works from prompts and performs file reads, edits, and tool calls until the task is complete or cancelled. | OpenAI Codex docs: Prompting | OpenAI describes prompts as the user messages that tell Codex what to do and states Codex works through model output, file actions, and tool calls. | Each entry must record the task prompt, allowed files, actual files changed, and tool/verification evidence. |
| P1O4-T09-R03 | Codex outputs improve when verification steps are included. | OpenAI Codex docs: Prompting | OpenAI recommends including steps to reproduce, validate features, linting, and pre-commit checks. | Each entry must record intended verification and completed verification, including when tests were not run. |
| P1O4-T09-R04 | Codex handles complex work better when broken into smaller focused steps. | OpenAI Codex docs: Prompting | OpenAI recommends smaller, focused tasks because they are easier to test and review. | Each log entry maps to one task issue or clearly records an approved exception. |
| P1O4-T09-R05 | Codex threads should not modify the same files in parallel. | OpenAI Codex docs: Prompting | OpenAI notes multiple threads can run, but warns against two threads modifying the same files. | Each entry must record active file scope and any concurrency/dependency caveat. |
| P1O4-T09-R06 | Codex can audit instruction files loaded through logs/session files. | OpenAI Codex docs: Custom instructions with AGENTS.md | OpenAI describes checking logs/session records to inspect instruction files Codex loaded. | The protocol records instruction sources and prompt packet sources without requiring full private transcripts. |

## Source links

- OpenAI Codex docs: Custom instructions with AGENTS.md - https://developers.openai.com/codex/guides/agents-md
- OpenAI Codex docs: Prompting - https://developers.openai.com/codex/prompting

## Governing repository artifacts

Prompt/build log entries should reference the standards that governed the work:

- `AGENTS.md`
- `.github/ISSUE_TEMPLATE/task.yml`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `templates/CODEX_TASK_PACKET.md`
- `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md`
- `docs/phase-one/objective-four/ISSUE_ARCHITECTURE.md`
- `docs/phase-one/objective-four/ISSUE_TAXONOMY.md`
- `docs/phase-one/objective-four/PROJECT_BOARD_SPEC.md`
- `docs/phase-one/objective-four/OBJECTIVE_FOUR_TRACKER.md`
- `docs/phase-one/objective-four/OBJECTIVE_FOUR_CLOSEOUT.md`
- `docs/phase-one/objective-four/OBJECTIVE_FOUR_HANDOFF.md`
- `docs/phase-one/objective-four/OBJECTIVE_FOUR_RELEASE_NOTE.md`

## What the prompt/build log records

Record the durable facts needed to understand prompt-assisted work later.

| Field group | Record |
|---|---|
| Task identity | Phase, objective, task ID, task issue, parent issue, branch, PR, artifact paths. |
| Prompt packet | Whether `templates/CODEX_TASK_PACKET.md` was used and what task prompt or summary was given. |
| Instruction sources | Whether `AGENTS.md`, workflow docs, issue templates, PR templates, and task packet were consulted. |
| Research | Source links checked, research claims made, and whether official/primary sources were used. |
| File scope | Allowed files, actual files changed, and diff summary. |
| Decisions | Material decisions made by the prompt-assisted process. |
| Verification | Checks run, checks not run, and why. |
| Boundary review | Whether no-data/no-model/no-public-output rules were preserved. |
| Claims review | Safe claims and unsupported claims after the task. |
| Handoff | Next task, unresolved caveats, and dependencies. |

## What the log must not record

Do not record:

- secrets, access tokens, API keys, credentials, session cookies, private URLs, or environment variables;
- private chain-of-thought or hidden reasoning;
- raw full transcripts unless they are intentionally public and reviewed;
- personal information not needed for the artifact;
- unredacted proprietary or sensitive source material;
- unreviewed operational wildfire guidance;
- unsupported claims that BurnLens is official, validated, operational, emergency-ready, or agency-endorsed.

If a useful fact depends on private reasoning, summarize the decision and evidence instead of recording the reasoning process.

## Log location and naming

The protocol index is:

```text
records/PROMPT_BUILD_LOG.md
```

The reusable entry template is:

```text
templates/PROMPT_LOG_ENTRY.md
```

Individual entries should be stored under:

```text
records/prompt-build-log/YYYY-MM-DD-task-id.md
```

Use dated entry files once prompt/build logging is active. This keeps the protocol readable while preserving task-level traceability.

## Entry index

| Task | Entry path | Status | Notes |
|---|---|---|---|
| P1O4-T01 through P1O4-T08 | Not retroactively required | historical | Traceability exists through issues, PRs, and artifacts before this protocol existed. |
| P1O4-T09 | `records/PROMPT_BUILD_LOG.md` | merged via PR #138 | Protocol and template task. |
| P1O4-T10 | `records/prompt-build-log/2026-07-06-p1o4-t10.md` | merged via PR #139 | Phase Two intake template task. |
| P1O4-T11 | `records/prompt-build-log/2026-07-06-p1o4-t11.md` | merged via PR #140 | Closeout and handoff task. |
| P1O4-QA | `records/prompt-build-log/2026-07-06-p1o4-qa.md` | merged via PR #142 | Quality pass before P1O4-T12. |
| P1O4-T12 | `records/prompt-build-log/2026-07-06-p1o4-t12.md` | merged via PR #143 | Objective Four release note task. |
| P1O5-T01 | `records/prompt-build-log/2026-07-07-p1o5-t01.md` | merged via PR #147 | Objective Five tracker and artifact-contract baseline. |
| P1O5-T02 | `records/prompt-build-log/2026-07-08-p1o5-t02.md` | merged via PR #149 | Current status reconciliation and README handoff update. |
| P1O5-T03 | `records/prompt-build-log/2026-07-08-p1o5-t03.md` | merged via PR #152 | Expanded version taxonomy and VERSIONING.md protocol update. |
| P1O5-SYNC-03 | `records/prompt-build-log/2026-07-08-p1o5-sync-03.md` | merged via PR #154 | Status sync after P1O5-T03 merge. |
| P1O5-T04 | `records/prompt-build-log/2026-07-08-p1o5-t04.md` | merged via PR #156 | Release and tag control spec and release-note template. |
| P1O5-SYNC-04 | `records/prompt-build-log/2026-07-08-p1o5-sync-04.md` | merged via PR #158 | Status sync after P1O5-T04 merge. |
| P1O5-T05 | `records/prompt-build-log/2026-07-08-p1o5-t05.md` | merged via PR #160 | Provenance traceability spec and traceability record template. |
| P1O5-SYNC-05 | `records/prompt-build-log/2026-07-08-p1o5-sync-05.md` | merged via PR #162 | Status sync after P1O5-T05 merge. |
| P1O5-T06 | `records/prompt-build-log/2026-07-08-p1o5-t06.md` | drafted in branch | Run package contract and run manifest template. |

## Entry creation timing

Create or update a prompt/build log entry at these points:

| Workflow point | Required log action |
|---|---|
| Artifact contract | Record task identity, artifact target, and allowed file scope. |
| Branch creation | Record branch name and base. |
| Research complete | Record sources checked and claims validated. |
| Artifact drafted | Record files changed and material decisions. |
| Verification complete | Record checks run or not run. |
| PR opened | Record PR number and close-keyword behavior. |
| PR merged | Record merge method and handoff update when the log is updated in a later QA/closeout pass. |

For lightweight documentation tasks, a single complete entry before PR is acceptable if it covers the required fields. If a later QA pass reveals stale pending language, update the entry.

## Prompt summary rule

Record a useful prompt summary, not necessarily every word.

Good prompt summary:

> Create the Task 12 Objective Four release note using merged repo standards. Update adjacent tracker, closeout, handoff, and prompt-log index files. Do not create a tag or start data work.

Too thin:

> Create log.

Too much:

> Full unredacted transcript with all intermediate reasoning, credentials, and abandoned drafts.

## Research logging rule

For each source-backed claim, record:

- claim ID;
- source name;
- source URL or repo path;
- what the source supports;
- decision made from the source;
- date checked.

When source access fails, record the failure and whether the task can proceed without the source. Do not fabricate source support.

## Verification logging rule

Every entry must state what was verified.

Examples:

- Diff check: one expected file added.
- Markdown review: headings and checklists are readable.
- YAML check: issue form syntax reviewed.
- JSON review: manifest template remains valid JSON.
- Tests: not applicable because documentation only.
- Tests not run: no code changed.

Do not write that tests passed unless a named test or check was actually run.

## Boundary and claims logging rule

Every entry must include:

- current phase boundary;
- whether data/model/map/public-output work occurred;
- safe claim after the task;
- unsupported claims after the task.

For Objective Four, the expected result is documentation, template, workflow, release-note, or records work only.

## Entry approval rule

A prompt/build log entry is acceptable when a reviewer can answer:

1. What was Codex or the prompt assistant asked to do?
2. What repo standards governed the work?
3. Which files were allowed to change?
4. Which files actually changed?
5. What sources were checked?
6. What verification occurred?
7. Which claims are safe or unsupported?
8. What happens next?

## Acceptance checklist

| Check | Status | Notes |
|---|---|---|
| Protocol file exists. | Satisfied | `records/PROMPT_BUILD_LOG.md`. |
| Entry template exists. | Satisfied | `templates/PROMPT_LOG_ENTRY.md`. |
| Entry directory pattern is defined. | Satisfied | `records/prompt-build-log/YYYY-MM-DD-task-id.md`. |
| Protocol defines required log fields. | Satisfied | Field groups table included. |
| Protocol defines exclusions. | Satisfied | Sensitive/private material excluded. |
| Protocol defines timing. | Satisfied | Entry creation timing table included. |
| Protocol defines verification logging. | Satisfied | Verification logging rule included. |
| Protocol defines boundary and claims logging. | Satisfied | Boundary and claims rule included. |
| Documentation-only boundary is preserved. | Satisfied | No data/model/map/public output authorized. |

## Rejection and defer criteria

Revise or defer this protocol if:

- it requires recording private chain-of-thought;
- it allows secrets or credentials in logs;
- it permits vague prompt summaries with no file scope;
- it omits research/source checks;
- it omits verification results;
- it fails to distinguish allowed files from actual changed files;
- it allows unsupported official, operational, validation, or endorsement claims;
- it replaces issues or PRs instead of complementing them.

## Allowed uses

This protocol may be used to create prompt/build log entries for future Codex-assisted tasks, support closeout review, document source checks, and explain how prompt-built artifacts were produced.

## Forbidden uses

This protocol must not be used to publish private reasoning, expose credentials, bypass GitHub workflow, skip research, or claim that prompt-assisted outputs are official, operational, field-validated, emergency-ready, or agency-endorsed.

## Versioning and provenance implications

Each prompt/build log entry should preserve:

- task issue number;
- parent issue number;
- branch;
- PR number;
- artifact paths;
- source links;
- verification notes;
- merge method;
- handoff note.

## Claims-register check

Safe claim:

> BurnLens has a prompt/build log protocol, reusable entry template, and dated entry pattern for recording prompt-assisted repository work.

Unsupported claims:

- Prompt/build logging has been applied retroactively to every earlier task.
- Codex has been automated.
- Data, model, run, map, or public-demo work has begun.
- BurnLens outputs are official, operational, field-validated, emergency-ready, or agency-endorsed.

## Handoff note

After the P1O5-T06 PR is reviewed and merged, update parent issue #144 with the P1O5-T06 completion summary and proceed to P1O5-T07 / #163 from current `main`.
