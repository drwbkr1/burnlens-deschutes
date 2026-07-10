# AGENTS.md

## Purpose

This file provides repository-level operating instructions for Codex, ChatGPT, and other prompt-assisted agents working in BurnLens Deschutes.

Use it together with the repository’s governing documents. A task-specific instruction may narrow this file, but it must not bypass BurnLens safety boundaries, source precedence, issue authorization, allowed-file scope, human review, or release controls.

## Project identity

BurnLens Deschutes is an experimental, portfolio-first computer vision and GEOINT wildfire screening project for Deschutes County, Oregon.

The project is intended to demonstrate technical capability, reproducibility, traceability, usefulness, and transparent limitations. It is not an official wildfire information source and is not emergency guidance.

## Non-negotiable boundary language

Use this warning, or a tighter equivalent, for future public-facing BurnLens CV outputs:

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

Do not describe BurnLens outputs as safe, official, validated, authoritative, emergency-ready, operational, field-confirmed, agency-endorsed, or suitable for evacuation, routing, tactical, or incident-command decisions.

## Source precedence

Official sources govern over BurnLens outputs.

BurnLens-derived outputs are lowest-priority experimental project artifacts. They must never override county, state, federal, fire-service, emergency-management, hazard, evacuation, transportation, or incident information.

If BurnLens output conflicts with official information, state that official sources govern. Do not reconcile the conflict as though BurnLens were authoritative.

## Governing workflow routes

Use these artifacts according to their roles:

1. `docs/workflows/PROMPT_TO_REPO_SOP.md` — full repository workflow reference and context-tier rules.
2. `templates/CODEX_TASK_PACKET.md` — canonical executable task capsule.
3. `templates/CODEX_TASK_TEMPLATE.md` — non-canonical compatibility and discoverability entry point only.
4. Task issue and approved task capsule — exact task authorization, branch, file scope, research, verification, and handoff.
5. `records/PROMPT_BUILD_LOG.md` — canonical prompt/build-log protocol and entry index.
6. `templates/PROMPT_LOG_ENTRY.md` — canonical detailed prompt/build-log entry template.
7. `PROMPT_LOG.md` — non-canonical root navigation for prompt logging.
8. `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md` — branch, PR, review, merge, and post-merge baseline.
9. Objective- and workstream-specific controls selected through the SOP.

Do not create a parallel task schema, prompt-log protocol, workflow, status register, verification checklist, or authorization mechanism.

## Current phase boundary

Phase One / Objective Six is the active repository-control workstream.

Objective Six work is limited to explicitly authorized documentation, workflow, template, and records changes. It does not authorize implementation, data acquisition, imagery download, AOI selection, labels, masks, baselines, models, metrics, runs, reports, maps, screenshots, demos, public claims, repository settings, tags, or GitHub Releases unless a later task issue names and authorizes the exact work.

Follow the current status and dependency order in:

- `README.md`
- `docs/phase-one/objective-six/OBJECTIVE_SIX_TRACKER.md`
- `docs/phase-one/objective-six/OBJECTIVE_SIX_ARTIFACT_CONTRACTS.md`
- `docs/phase-one/objective-six/PROMPT_BUILT_DEVELOPMENT_PROTOCOL.md`

Treat completed-objective trackers, handoffs, closeouts, old issues, old PR bodies, and historical logs as archival context unless a task explicitly requires verification or correction.

## Required task workflow

Every meaningful prompt-assisted task follows this chain:

```text
approved task issue
→ compact task capsule
→ branch from current main
→ Tier 0 plus relevant Tier 1 context
→ bounded research when required
→ edits within allowed files
→ dated prompt/build log
→ named checks or documented non-applicability
→ diff review against main
→ task-scoped pull request
→ optional AI-assisted review
→ mandatory human review
→ authorized merge
→ handoff and status synchronization when needed
```

Do not skip the issue, branch, allowed-file, prompt-log, PR, or human-review gates.

## Context loading

Use the SOP quickstart:

- load Tier 0 for every repository task;
- select only Tier 1 artifacts relevant to the task;
- use Tier 2 only when current controls are insufficient for a specific verification question;
- record any Tier 2 use and its reason in the prompt/build log.

Do not let historical drafts override current merged controls.

## Issue, branch, and PR rules

Every meaningful task must have its own task issue unless the human owner explicitly approves bundling.

Use compact task branches created from current `main`, unless the issue explicitly authorizes another base. Examples:

```text
p1o6t04b
p1o6t04fixb
p2o1t01b
```

Prompt-assisted edits must not be made directly to `main`.

Use task PR titles in this form:

```text
P#O#-T## Short task title
```

The PR must close only the task issue:

```text
Closes #TASK_ISSUE
```

Do not close a parent objective issue from an ordinary task PR. Prefer squash merge for bounded task branches when repository settings allow it and the human reviewer authorizes merge.

## Allowed-file discipline

Before editing, identify:

- task issue and parent issue;
- branch and base;
- primary and supporting artifacts;
- allowed file changes;
- forbidden work;
- required research;
- acceptance criteria;
- verification plan;
- intended PR close keyword;
- handoff target.

Edit only the paths named in the task contract.

If another path becomes necessary, stop before changing it. Explain why the contract is insufficient and obtain a human-approved scope revision or create a separate task.

Connector friction does not authorize broader scope, thinner artifacts, temporary files on `main`, or bypassing review.

## Research rule

Research must occur after branch creation and before final artifact language when a task depends on current technical, tooling, API, official, policy, legal, safety, source, dataset, model, or public-claim facts.

Prefer official or primary sources. Record the source, what it supports, the adopted decision, and the date checked.

When no fresh research is required, state why merged repository controls and repository-internal verification are sufficient. Do not introduce current external claims from memory.

## Prompt/build logging

Prompt-assisted tasks that materially change files must create or update a dated record under:

```text
records/prompt-build-log/YYYY-MM-DD-task-id.md
```

Use `records/PROMPT_BUILD_LOG.md` and `templates/PROMPT_LOG_ENTRY.md` as the canonical controls.

Record task identity, issue, branch, future or actual PR, governing context, allowed and actual files, research, material decisions, checks, results, checks not run, boundary review, claims review, review-driven revisions, and handoff.

Do not record secrets, credentials, tokens, cookies, private URLs, private chain-of-thought, raw private transcripts, unnecessary personal information, or unreviewed operational guidance.

## Verification and test reporting

Verification is mandatory for every task.

Report each applicable check by name, method or command, and actual result. Examples include:

- unit, integration, regression, or smoke tests;
- linting, formatting, and type checking;
- YAML, JSON, schema, or manifest validation;
- link and path checks;
- rendered-document or UI inspection;
- branch and PR diff inspection;
- data, CRS, provenance, or run-package checks when later authorized.

Do not write `tests passed` unless named tests or commands actually ran.

When a check does not apply, give a task-specific reason. For documentation-only work, code tests may be non-applicable while Markdown, path, link, scope, consistency, boundary, claims, and diff checks remain required.

## Review separation

AI-assisted review is supplemental. It may inspect diffs, identify omissions, flag defects or boundary violations, suggest checks, and confirm whether findings appear addressed.

AI-assisted review does not approve a merge. An authoring agent must not treat its own self-review as independent approval.

A human must inspect the task issue, capsule, changed-file list, diff, research where applicable, checks and results, acceptance criteria, boundary status, close keyword, and handoff. The human records one outcome:

- **Approve**;
- **Request changes**;
- **Defer or reject**.

Merge only after blocking findings are resolved and human approval is recorded.

## Data, claim, version, tag, and release gates

Before touching data, imagery, AOIs, labels, masks, baselines, model inputs, or run outputs, apply the before-data gate in `docs/workflows/PROMPT_TO_REPO_SOP.md` and the applicable Objective Three and Objective Five controls.

Before public-facing language or outputs, apply:

- `docs/objective-one/USE_BOUNDARIES.md`;
- `docs/objective-one/SOURCE_PRECEDENCE.md`;
- `docs/phase-one/objective-five/CLAIM_TRACEABILITY_PROTOCOL.md`;
- `docs/phase-one/objective-five/SOURCE_PRECEDENCE_RELEASE_GATE.md`;
- `docs/phase-one/objective-five/OBJECTIVE_FIVE_CLAIMS_CHECK.md`;
- applicable reproducibility and release-QA controls.

Follow `VERSIONING.md` for version and identifier rules. Update it only when the versioning protocol itself changes.

A proposed tag is not a created tag. A release-note draft is not a GitHub Release. Tag creation and GitHub Release publication require separate explicit authorization.

## Claims rules

Safe internal claims must be limited to evidence that exists in merged repository artifacts.

Do not claim operational reliability, field validation, emergency readiness, agency endorsement, official wildfire information status, live incident accuracy, completed data/model/map work, configured repository enforcement, or published releases unless the relevant evidence and explicit authorization exist.

## Future implementation caution

When later tasks authorize data or model work, add source records, provenance, versioning, run IDs, boundary records, and applicable checks before treating outputs as portfolio evidence.

The locked future technical chain remains:

```text
imagery → preprocessing → segmentation or baseline mask → raster output → vector polygons → map overlay → exposure-style summary → documented run package
```

Do not skip traceability or limitation steps to make the project appear more complete.

## Handoff rule

Every task must end with a compact handoff stating:

- what was completed;
- issue, branch, PR, and merge status;
- files changed;
- checks and results;
- safe, caveated, and unsupported claims;
- status synchronization completed or still needed;
- next task and required context;
- drafting details or historical context that should not carry forward.
