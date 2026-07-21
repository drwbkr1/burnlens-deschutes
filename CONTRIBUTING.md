# Contributing to BurnLens Deschutes

## Purpose

This guide explains the human-facing workflow for contributing to BurnLens Deschutes.

BurnLens is an experimental, portfolio-first computer vision and GEOINT wildfire-screening project. It is not an official wildfire information source, emergency system, field-validated product, or operational decision tool. Official sources govern.

This guide documents repository policy. It does not promise that outside contributions will be accepted, reviewed within a particular time, maintained, or supported. It also does not authorize implementation, data acquisition, public outputs, repository-setting changes, tags, or GitHub Releases.

## Canonical workflow sources

Use this guide as a concise human entry point. The following files remain authoritative for their specific roles:

- `docs/governance/BURNLENS_EXECUTION_GOAL.md` — controlling execution authority and stop conditions.
- `docs/governance/CHECKPOINT_POLICY.md` — evidence-unit, milestone, exception, batching, and shipping cadence.
- `docs/workflows/PROMPT_TO_REPO_SOP.md` — full prompt-to-repository workflow and context tiers.
- `AGENTS.md` — repository-level instructions for prompt-assisted agents.
- `templates/CODEX_TASK_PACKET.md` — canonical executable task capsule.
- `templates/CODEX_TASK_TEMPLATE.md` — non-canonical compatibility and discoverability entry point.
- `records/PROMPT_BUILD_LOG.md` — canonical prompt/build-log protocol and index.
- `templates/PROMPT_LOG_ENTRY.md` — canonical detailed prompt/build-log entry template.
- `PROMPT_LOG.md` — non-canonical prompt-log navigation.
- `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md` and `docs/phase-one/objective-six/` — historical workflow evidence and optional inspection aids; they do not override the execution goal, checkpoint policy, or current live milestone issue.

Do not use this file to create a second task packet, prompt-log schema, context-tier table, pull-request checklist, review checklist, or independent workflow.

## Start from an authorized checkpoint issue

Milestone and exception work begins with a GitHub checkpoint issue. Related evidence units may accumulate inside one milestone issue and branch under `docs/governance/CHECKPOINT_POLICY.md`; they do not require separate issues or PRs merely to record progress.

Before changing files, confirm that the issue identifies:

- the task and parent issue;
- the checkpoint class, milestone outcome, and exit condition;
- the evidence-unit roster or registration rule;
- failure-retention rules or the exception trigger;
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

The issue authorizes the checkpoint outcome; it does not prove that an evidence unit or milestone is complete.

Use `templates/CODEX_TASK_PACKET.md` to turn the issue into the compact operating capsule. A task capsule may narrow the issue but may not broaden it.

## Use a checkpoint branch

Create one compact milestone or exception branch from current `main` unless the issue explicitly authorizes another base. Evidence units remain on that branch until the milestone ships. Use the project pattern, such as:

```text
p1o6t05b
p1o6t05fixb
p2o1t01b
```

Do not make meaningful or prompt-assisted changes directly to `main`.

Keep changes inside the issue's allowed path families. Register each unit before editing and preserve its immutable identifiers, hashes, gates, disposition, and failures. If work changes the authorized outcome, phase result, use boundary, or high-risk source/data scope, stop before editing and revise the issue or create a separate checkpoint.

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

## Open a checkpoint-scoped pull request

Every milestone or exception reaches `main` through a pull request. Evidence units may remain on the authorized milestone branch until its exit condition is met.

The pull request should:

- target `main` unless the issue explicitly authorizes another base;
- use the task title pattern;
- summarize the changed files and material decisions;
- report research and verification;
- enumerate every evidence unit and its pass, remediate, exclude, defer, or stop disposition;
- retain failed and superseded units instead of presenting only favorable evidence;
- list checks not run and explain why;
- preserve boundary and source-precedence status;
- identify dependencies and the next task;
- use `Closes #TASK_ISSUE` for the task issue only.

Do not use a closing keyword for an objective parent issue in an ordinary task pull request.

## Review and owner decisions

Author self-audit, executable checks, AI-assisted review, owner evidence decisions, and merge decisions are distinct.

AI-assisted review may inspect a diff, flag omissions or defects, suggest focused checks, and confirm whether findings appear addressed. It cannot be described as independent approval, fabricate an owner decision, authorize work outside the issue, or waive evidence gates.

The owner must act when the exact workflow requires yes/no/uncertain candidate review or when an execution-goal stop condition is reached. Routine issue, branch, implementation, PR, merge, tag, reversible deployment, and checkpoint-selection decisions do not require separate owner approval under the controlling goal.

Before merge, verify:

1. the checkpoint issue, class, capsule, and complete unit ledger;
2. the changed-file list and diff;
3. research evidence where applicable;
4. checks, methods, actual results, and retained failures;
5. acceptance and milestone exit criteria;
6. boundaries, source precedence, and required owner decisions;
7. the checkpoint-only close keyword and handoff.

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
- AI review is being represented as independent approval or an owner decision;
- the task would broaden into unauthorized data, model, public-output, settings, tag, Release, or other blocked work.

Revise the task contract or create a separate issue before continuing.

## BurnLens boundaries

Follow `docs/objective-one/USE_BOUNDARIES.md`, `docs/objective-one/SOURCE_PRECEDENCE.md`, `VERSIONING.md`, the Objective Five handoff, and the matching controls selected through the SOP.

A task issue or contribution guide does not authorize imagery, AOIs, labels, masks, baselines, models, metrics, runs, reports, maps, screenshots, public demos, public claims, repository settings, tags, or GitHub Releases unless an explicit later task authorizes the exact work and its required gates are satisfied.

## Post-merge handoff

After a milestone or exception merge:

- confirm the task issue closed as intended;
- update the parent issue with the task, pull request, artifacts, status, and next task;
- synchronize README, tracker, or prompt-log records only when their truth is materially stale and the milestone closeout cannot state it accurately;
- avoid rewriting completed objective records.

Use `README.md`, the roadmap, phase status, and the live GitHub milestone issue to identify current work and dependencies. Do not use the historical Objective Six tracker or task-specific handoffs as current authority after later checkpoints have merged.

## GitHub research basis

The review and enforcement distinctions above were checked against current official GitHub documentation on 2026-07-11:

- About pull request reviews: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews
- Reviewing proposed changes in a pull request: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/reviewing-proposed-changes-in-a-pull-request
- About protected branches: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- About rulesets: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets
- Available rules for rulesets: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
