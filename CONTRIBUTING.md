# Contributing to BurnLens Deschutes

## Purpose

This guide explains the human-facing workflow for contributing to BurnLens Deschutes.

BurnLens is an experimental, portfolio-first computer vision and GEOINT wildfire-screening project. It is not an official wildfire information source, emergency system, field-validated product, or operational decision tool. Official sources govern.

This guide documents repository policy. It does not promise that outside contributions will be accepted, reviewed within a particular time, maintained, or supported. It also does not authorize implementation, data acquisition, public outputs, repository-setting changes, tags, or GitHub Releases.

## Canonical workflow sources

Use this guide as a concise human entry point. The following files remain authoritative for their specific roles:

- `docs/workflows/PROMPT_TO_REPO_SOP.md` — full prompt-to-repository workflow and context tiers.
- `AGENTS.md` — repository-level instructions for prompt-assisted agents.
- `templates/CODEX_TASK_PACKET.md` — canonical executable task capsule.
- `templates/CODEX_TASK_TEMPLATE.md` — non-canonical compatibility and discoverability entry point.
- `records/PROMPT_BUILD_LOG.md` — canonical prompt/build-log protocol and index.
- `templates/PROMPT_LOG_ENTRY.md` — canonical detailed prompt/build-log entry template.
- `PROMPT_LOG.md` — non-canonical prompt-log navigation.
- `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md` — branch, pull-request, review, merge, and post-merge baseline.
- `docs/phase-one/objective-six/OBJECTIVE_SIX_TRACKER.md` — current Objective Six task and dependency state.
- `docs/phase-one/objective-six/OBJECTIVE_SIX_ARTIFACT_CONTRACTS.md` — task artifact contracts.
- `docs/phase-one/objective-six/PROMPT_BUILT_DEVELOPMENT_PROTOCOL.md` — how the workflow components operate together.

Do not use this file to create a second task packet, prompt-log schema, context-tier table, pull-request checklist, review checklist, or independent workflow.

## Start from an authorized issue

Meaningful repository work begins with a GitHub task issue or an explicitly approved bundled-task issue.

Before changing files, confirm that the issue identifies:

- the task and parent issue;
- dependencies;
- branch and base;
- primary and supporting artifacts;
- allowed file changes;
- forbidden work;
- required research;
- acceptance criteria;
- verification expectations;
- intended pull-request close keyword;
- handoff target.

The issue authorizes work; it does not prove that the work is complete.

Use `templates/CODEX_TASK_PACKET.md` to turn the issue into the compact operating capsule. A task capsule may narrow the issue but may not broaden it.

## Use a task branch

Create one compact task branch from current `main` unless the issue explicitly authorizes another base. Use the project pattern, such as:

```text
p1o6t05b
p1o6t05fixb
p2o1t01b
```

Do not make meaningful or prompt-assisted changes directly to `main`.

Keep changes inside the issue's allowed file list. If another path becomes necessary, stop before editing it. Explain why the existing contract is insufficient, then revise the issue and capsule or create a separate task with human approval.

## Load only the required context

Follow the SOP quickstart:

1. Load or summarize Tier 0.
2. Select only the Tier 1 artifacts relevant to the task.
3. Use Tier 2 historical material only when current controls cannot resolve a specific verification question.
4. Record any Tier 2 use and its reason in the prompt/build log.

Historical drafts, old issues, and old pull-request text must not override current merged controls.

## Research current claims

Perform fresh research after branch creation when a task depends on current technical, tooling, API, official, policy, legal, safety, source, dataset, model, or public-claim facts.

Prefer official or primary sources. Record what each source supports, the wording or decision adopted, and the date checked. When repository-internal verification is sufficient, record why no fresh external research was needed.

## Log prompt-assisted changes

Prompt-assisted file changes require a dated record under:

```text
records/prompt-build-log/YYYY-MM-DD-task-id.md
```

Use `records/PROMPT_BUILD_LOG.md` and `templates/PROMPT_LOG_ENTRY.md` as the canonical logging controls.

Record the task identity, issue, branch, files, governing context, research, material decisions, checks and actual results, checks not run and reasons, boundary and claims review, review-driven changes, and handoff.

Do not record secrets, credentials, tokens, cookies, private URLs, private chain-of-thought, raw private transcripts, unnecessary personal information, or unreviewed operational wildfire guidance.

## Run and report checks honestly

Every task requires verification.

For each applicable check, record:

- the check name;
- the command or manual inspection method;
- the actual result;
- any failure, limitation, or unresolved issue.

Do not write `tests passed` unless named tests or commands actually ran.

When a check does not apply, give a task-specific reason. Documentation-only work may mark code, model, data, application, CI, lint, or executable tests as not applicable, while still performing Markdown, path, link, requirement-coverage, consistency, scope, boundary, claims, sensitive-material, and branch-diff checks.

Do not invent or require CI jobs, status checks, or other automated gates that do not exist.

## Open a task-scoped pull request

Every meaningful task reaches `main` through a pull request.

The pull request should:

- target `main` unless the issue explicitly authorizes another base;
- use the task title pattern;
- summarize the changed files and material decisions;
- report research and verification;
- list checks not run and explain why;
- preserve boundary and source-precedence status;
- identify dependencies and the next task;
- use `Closes #TASK_ISSUE` for the task issue only.

Do not use a closing keyword for an objective parent issue in an ordinary task pull request.

## Human review is mandatory

AI-assisted review is supplemental. It may inspect a diff, flag omissions or defects, suggest focused checks, and confirm whether findings appear addressed. It cannot approve a merge, authorize scope expansion, or satisfy the human-review requirement.

Before merge, a human must inspect:

1. the task issue and capsule;
2. the changed-file list and diff;
3. research evidence where applicable;
4. checks, methods, and actual results;
5. checks not run and reasons;
6. acceptance criteria;
7. boundaries and source precedence;
8. the task-only close keyword and handoff.

The recorded human outcome must be one of:

```text
Approve
Request changes
Defer or reject
```

### Solo-maintainer review evidence

GitHub provides `Comment`, `Approve`, and `Request changes` review states, but pull-request authors cannot formally approve their own pull requests.

For the current solo-maintainer workflow, Drew records human review through either:

- an explicit pull-request comment naming the human outcome; or
- a completed pull-request checklist that names the outcome and states that the diff and verification evidence were reviewed.

This is BurnLens policy evidence. It is not a GitHub approval review and does not claim platform enforcement.

When another eligible human reviewer is available, request their review and use GitHub's formal review state where possible. This guide does not imply that another reviewer currently exists.

## Documented policy versus GitHub enforcement

`CONTRIBUTING.md`, the SOP, and `AGENTS.md` define project policy. GitHub branch protection and rulesets are separate repository settings that can enforce selected requirements when they are configured and active.

GitHub documents controls such as requiring pull requests, approving reviews, status checks, conversation resolution, and linear history. Rulesets can be active or disabled. Written policy alone does not activate those controls.

This task does not inspect, enable, or modify branch protection, rulesets, required approvals, required checks, CI, CODEOWNERS, conversation-resolution gates, linear-history rules, or other settings. Do not claim that any of them are configured without separate verification and authorization.

## Stop and escalate scope

Stop before proceeding when:

- the issue or task capsule is missing or conflicting;
- a dependency or branch base is unclear;
- required work falls outside the allowed paths;
- current tooling or external claims cannot be verified;
- checks cannot be reported honestly;
- canonical controls conflict;
- AI review is being substituted for human approval;
- the task would broaden into unauthorized data, model, public-output, settings, tag, Release, or other blocked work.

Revise the task contract or create a separate issue before continuing.

## BurnLens boundaries

Follow `docs/objective-one/USE_BOUNDARIES.md`, `docs/objective-one/SOURCE_PRECEDENCE.md`, `VERSIONING.md`, the Objective Five handoff, and the matching controls selected through the SOP.

A task issue or contribution guide does not authorize imagery, AOIs, labels, masks, baselines, models, metrics, runs, reports, maps, screenshots, public demos, public claims, repository settings, tags, or GitHub Releases unless an explicit later task authorizes the exact work and its required gates are satisfied.

## Post-merge handoff

After an authorized merge:

- confirm the task issue closed as intended;
- update the parent issue with the task, pull request, artifacts, status, and next task;
- synchronize README, tracker, or prompt-log records only when their truth changed;
- avoid rewriting completed objective records.

For Objective Six, complete P1O6-T05 review, merge, and any required synchronization before proceeding to P1O6-T06 — Define the human review checklist and modernize pull-request intake.

## GitHub research basis

The review and enforcement distinctions above were checked against current official GitHub documentation on 2026-07-11:

- About pull request reviews: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews
- Reviewing proposed changes in a pull request: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/reviewing-proposed-changes-in-a-pull-request
- About protected branches: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- About rulesets: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets
- Available rules for rulesets: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
