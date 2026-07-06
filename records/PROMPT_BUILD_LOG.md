# Prompt Build Log Protocol

## Purpose

This protocol defines how BurnLens Deschutes records prompt-assisted repository work.

The prompt/build log is a traceability record. It should show what task was attempted, which repo standards governed the work, which prompts or task packets were used, which source checks were made, which files changed, what verification occurred, and what was handed off next.

The log must not become a transcript dump, private reasoning record, credential store, or replacement for GitHub issues, branches, pull requests, commits, artifacts, or release notes.

## Status

- Task issue: #126
- Parent issue: #119
- Branch: `p1o4t09b`
- Protocol file: `records/PROMPT_BUILD_LOG.md`
- Entry template: `templates/PROMPT_LOG_ENTRY.md`
- Current task: P1O4-T09 - Create prompt build log protocol

## Research basis

Fresh research was conducted after branch creation and before artifact writing.

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

The persistent index is:

```text
records/PROMPT_BUILD_LOG.md
```

The reusable entry template is:

```text
templates/PROMPT_LOG_ENTRY.md
```

For Objective Four, entries may be appended to `records/PROMPT_BUILD_LOG.md`. If the log becomes too long in a later phase, split entries into dated files under:

```text
records/prompt-build-log/YYYY-MM-DD-task-id.md
```

Do not split the log during Objective Four unless needed.

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
| PR merged | Record merge method and handoff update. |

For lightweight documentation tasks, a single complete entry before PR is acceptable if it covers the required fields.

## Prompt summary rule

Record a useful prompt summary, not necessarily every word.

Good prompt summary:

> Create the Task 9 prompt/build log protocol using merged repo standards and OpenAI Codex docs. Limit changes to `records/PROMPT_BUILD_LOG.md` and `templates/PROMPT_LOG_ENTRY.md`.

Too thin:

> Create log.

Too much:

> Full unredacted transcript with all intermediate reasoning, credentials, and abandoned drafts.

## Research logging rule

For each source-backed claim, record:

- claim ID;
- source name;
- source URL;
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
- Tests: not applicable because documentation only.
- Tests not run: no code changed.

Do not write that tests passed unless a named test or check was actually run.

## Boundary and claims logging rule

Every entry must include:

- current phase boundary;
- whether data/model/map/public-output work occurred;
- safe claim after the task;
- unsupported claims after the task.

For Objective Four, the expected result is usually documentation, template, workflow, or records work only.

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

## Initial Objective Four entries

Task 9 creates the protocol and template. Earlier Objective Four tasks were tracked through issues, PRs, and artifacts before this protocol existed. They do not require retroactive full entries unless requested during closeout.

| Task | Prompt log status | Notes |
|---|---|---|
| P1O4-T01 through P1O4-T08 | Not retroactively required | Traceability exists through issues, PRs, and artifacts. |
| P1O4-T09 | Required | This protocol and template establish logging rules going forward. |
| P1O4-T10 onward | Required | Use this protocol and `templates/PROMPT_LOG_ENTRY.md`. |

## P1O4-T09 log entry

Use `templates/PROMPT_LOG_ENTRY.md` as the source format. Fill this section after PR creation and before merge if a complete live entry is needed. Minimum entry for this task:

```text
Task ID: P1O4-T09
Task issue: #126
Parent issue: #119
Branch: p1o4t09b
Files changed: records/PROMPT_BUILD_LOG.md; templates/PROMPT_LOG_ENTRY.md
Research sources: OpenAI Codex AGENTS.md docs; OpenAI Codex prompting docs
Verification: diff check; file review; documentation-only boundary check
PR: pending until PR opened
Handoff: P1O4-T10 should use this protocol when creating Phase Two intake templates
```

## Acceptance checklist

| Check | Status | Notes |
|---|---|---|
| Task issue exists. | Satisfied | #126. |
| Parent issue is referenced. | Satisfied | #119. |
| Branch exists before artifact writing. | Satisfied | `p1o4t09b`. |
| Fresh research completed before artifact writing. | Satisfied | OpenAI Codex docs checked. |
| Protocol defines required log fields. | Satisfied | Field groups table included. |
| Protocol defines exclusions. | Satisfied | Sensitive/private material excluded. |
| Protocol defines timing. | Satisfied | Entry creation timing table included. |
| Protocol defines verification logging. | Satisfied | Verification logging rule included. |
| Protocol defines boundary and claims logging. | Satisfied | Boundary and claims rule included. |
| Template file is created. | Satisfied | `templates/PROMPT_LOG_ENTRY.md`. |
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

Safe claim after Task 9:

> BurnLens has a prompt/build log protocol and reusable entry template for recording prompt-assisted repository work.

Unsupported claims after Task 9:

- Prompt/build logging has been applied retroactively to every earlier task.
- Codex has been automated.
- Data, model, run, map, or public-demo work has begun.
- BurnLens outputs are official, operational, field-validated, emergency-ready, or agency-endorsed.

## Handoff note

Proceed to P1O4-T10 after this protocol and template are reviewed and merged. P1O4-T10 should use this protocol to record prompt-assisted creation of Phase Two intake templates, including source checks, file scope, boundary decisions, verification results, and handoff notes.
