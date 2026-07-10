# BurnLens Prompt-Built Development Protocol

## Purpose

This protocol defines the architecture for prompt-assisted repository work in BurnLens Deschutes.

It does not replace the full SOP, issue form, Codex task packet, prompt/build-log protocol, branch-and-PR workflow, or future contributor guidance. It defines how those artifacts work together and which source is canonical when names overlap.

## Scope

This protocol applies to prompt-assisted documentation, workflow, template, records, implementation, data, model, and public-output tasks only when the task is separately authorized by its issue and governing phase controls.

P1O6-T01 itself authorizes documentation and records work only. It does not authorize data, imagery, AOIs, labels, masks, baselines, models, metrics, runs, maps, screenshots, public demos, public claims, tags, GitHub Releases, or repository-settings changes.

## Governing source order

Use these sources without duplicating them:

1. `docs/workflows/PROMPT_TO_REPO_SOP.md` — full repository workflow reference.
2. `AGENTS.md` — repository-level instructions loaded by Codex and other agents when applicable.
3. `templates/CODEX_TASK_PACKET.md` — canonical executable task capsule.
4. Task issue and approved task-specific capsule — exact authorization and file scope.
5. `records/PROMPT_BUILD_LOG.md` — canonical prompt/build-log protocol and index.
6. `templates/PROMPT_LOG_ENTRY.md` — canonical detailed log-entry template.
7. `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md` — branch, PR, review, merge, and post-merge baseline.
8. Objective- and workstream-specific controls selected through the SOP tiers.

When two sources appear to conflict, stop before editing and resolve the conflict through the task issue or a new control task. Do not silently choose the broader interpretation.

## Canonical naming decisions

### Prompt logging

- `records/PROMPT_BUILD_LOG.md` remains the canonical logging protocol and entry index.
- `templates/PROMPT_LOG_ENTRY.md` remains the canonical detailed entry template.
- A future root `PROMPT_LOG.md` may exist only as a compatibility and navigation entry point. It must link to the canonical files and must not maintain a second protocol, second index, or transcript archive.

### Codex task briefing

- `templates/CODEX_TASK_PACKET.md` remains the canonical task capsule.
- A future `templates/CODEX_TASK_TEMPLATE.md` may exist only as a compatibility and discoverability wrapper. It must direct users to instantiate the canonical packet and must not duplicate or alter its required fields.

## Required workflow

Every meaningful prompt-assisted task follows this chain:

```text
approved task issue
→ compact task capsule
→ branch from current main
→ relevant Tier 0 and Tier 1 context
→ bounded research when required
→ prompt-assisted changes within allowed files
→ task prompt/build log
→ tests/checks or documented non-applicability
→ diff review against main
→ pull request closing only the task issue
→ AI-assisted review when useful
→ distinct human review
→ authorized merge
→ handoff and current-status synchronization
```

Skipping a step requires an explicit task-level reason recorded in the issue, prompt log, or PR. A skipped human-review step is not permitted.

## 1. Issue-first authorization

Every task begins from a GitHub task issue or an explicitly approved bundled-task issue.

The issue must identify:

- task ID and title;
- parent issue;
- recommended branch;
- primary and supporting artifacts;
- allowed file changes;
- forbidden work;
- dependencies;
- required research;
- acceptance criteria;
- verification expectations;
- expected PR close keyword;
- handoff target.

An issue describes authorized work. It does not prove that the work is complete.

## 2. Task capsule

The task capsule is the executable prompt derived from the issue and canonical `templates/CODEX_TASK_PACKET.md`.

The capsule must be compact enough to use operationally and complete enough to prevent scope drift. References to governing boundary files are preferred over copying large sections into every prompt.

The capsule cannot broaden the task issue. When the capsule conflicts with the issue, stop and revise the contract before editing.

## 3. Branch isolation

Create one compact task branch from current `main` unless the issue explicitly documents a dependency branch.

Prompt-assisted edits must not be made directly to `main`.

The branch name should preserve task identity, for example:

```text
p1o6t01b
p1o6t01fixb
p2o1t01b
```

Parallel branches must not edit the same files unless the dependency and merge order are explicit.

## 4. Context loading

Load Tier 0 for every task and only the Tier 1 artifacts that match the work.

Tier 2 historical artifacts are verification evidence, not default working context. When Tier 2 is used, the prompt/build log records the exact artifact and why current controls were insufficient.

This keeps task context small while preventing historical drafts from overriding merged controls.

## 5. Research gate

Fresh research is required when a task makes current technical, tooling, API, official, policy, legal, safety, source, model, or public-claim statements.

Research occurs after branch creation and before final research-backed language is written.

Use official or primary sources where available. Record:

- claim identifier;
- source name;
- source URL or repository path;
- what the source supports;
- decision adopted;
- date checked.

A source link without an adopted decision is incomplete. An adopted decision without verifiable support must be labeled as an internal design choice rather than a researched fact.

## 6. Allowed-file discipline

Prompt-assisted work may create or edit only the paths listed in the task contract.

When an additional file becomes necessary:

1. stop before changing it;
2. explain why the original contract is insufficient;
3. revise the issue and capsule or create a separate task;
4. proceed only after the human owner approves the scope change.

Connector friction does not authorize broader file scope or thinner artifacts.

## 7. Prompt/build logging

Prompt/build logs are administrative traceability records, not transcripts.

For each prompt-assisted task that changes files, create or update a dated entry under:

```text
records/prompt-build-log/YYYY-MM-DD-task-id.md
```

The entry records:

- task, issue, parent, branch, and future PR identity;
- prompt or task-packet summary;
- governing context used;
- allowed and actual files;
- research sources and adopted decisions;
- material architecture or debugging decisions;
- tests, checks, commands, inspection methods, and actual results;
- checks not run and reasons;
- boundary and claims review;
- sensitive-material exclusion;
- review-driven revisions;
- handoff.

Do not log credentials, tokens, cookies, secrets, private chain-of-thought, raw private transcripts, unnecessary personal data, or unreviewed emergency guidance.

## 8. Tests and verification

Verification is mandatory for every task.

### Applicable checks

Choose the smallest checks that can actually support the task claim, including:

- unit, integration, regression, or smoke tests;
- linting and formatting;
- type checking;
- schema or syntax validation;
- JSON, YAML, or manifest validation;
- link and path checks;
- rendered documentation review;
- diff inspection;
- UI or browser inspection;
- data, CRS, provenance, or run-package checks when later authorized.

### Reporting rule

For each check, record:

- exact command or manual inspection method;
- result: passed, failed, partial, blocked, or not applicable;
- relevant output or finding;
- unresolved limitation.

Do not write `tests passed` without naming the tests or commands that ran.

### Non-applicability rule

`Not applicable` must include a task-specific reason.

Acceptable example:

> Code tests were not applicable because this task changed Markdown documentation and administrative records only. Verification used branch diff inspection, path resolution, Markdown readability, research-source review, requirement coverage, and boundary checks.

Unacceptable example:

> Tests not needed.

## 9. Diff review

Before a PR, compare the task branch with `main` and confirm:

- every changed file is allowed;
- no scratch, generated, credential, or connector-test file is present;
- no unrelated completed-objective record changed;
- research claims have evidence;
- acceptance criteria are covered;
- current-status language is accurate;
- unsupported claims are absent;
- the handoff is clear.

A clean file list is necessary but not sufficient. Review the content of each changed file.

## 10. Pull request

Every meaningful task artifact reaches `main` through a pull request.

The PR must:

- target `main` unless explicitly authorized otherwise;
- use the task title pattern;
- summarize changed files and material decisions;
- report research and verification;
- state tests/checks not run and why;
- preserve boundary and source-precedence status;
- identify dependencies and next task;
- use `Closes #TASK_ISSUE` for the task issue only.

Ordinary task PRs must not close the parent objective issue.

GitHub closing keywords work when the PR targets the default branch and is merged. The issue link is workflow metadata, not proof that acceptance criteria were satisfied.

## 11. AI-assisted review

AI-assisted review is optional but encouraged for complex or high-risk diffs.

It may:

- inspect working-tree or PR changes;
- find missing requirements;
- flag defects, security concerns, inconsistent claims, or boundary violations;
- suggest focused tests;
- confirm whether identified findings were addressed.

AI review output must be labeled as AI-assisted. The authoring agent must not treat its own self-audit as independent approval.

## 12. Human review

Human review is mandatory before merge and is distinct from AI-assisted review.

The human reviewer must inspect:

1. the task issue and capsule;
2. the PR file list and diff;
3. research evidence where applicable;
4. tests/checks and actual results;
5. checks not run and reasons;
6. boundary and source-precedence status;
7. acceptance criteria;
8. handoff and close-keyword behavior.

The human records one outcome:

- **Approve** — ready for authorized merge;
- **Request changes** — findings must be addressed and re-reviewed;
- **Defer/reject** — task should not merge in its current form.

In a personal repository where the author cannot provide a meaningful separate GitHub self-approval, human review may be recorded through a completed PR checklist or explicit PR comment. It must name the human decision and remain separate from any AI review.

## 13. Merge

Merge only after:

- all required checks are accurately reported;
- blocking review findings are resolved;
- human approval is recorded;
- dependencies are merged or explicitly resolved;
- the diff contains only authorized files;
- the task issue close keyword is correct.

Prefer squash merge for bounded task branches when the repository allows it. GitHub documents that squash merging combines the topic-branch commits into one commit, which supports the BurnLens goal of one clear task-level history entry.

Merge method preference does not override repository settings or human authorization.

## 14. Post-merge handoff and synchronization

After merge:

- confirm the task issue closed as intended;
- comment on the parent objective issue with task, PR, artifact paths, status, and next task;
- update the current tracker, README, handoff, or prompt-log index only when their truth changed;
- avoid rewriting completed objective records;
- preserve merge commit and review evidence in later closeout records when applicable.

A separate sync task is appropriate when a merge leaves current-status records stale and those files were outside the original task scope.

## Review separation matrix

| Activity | AI may perform | Human must perform | Satisfies human gate? |
|---|---:|---:|---:|
| Draft files | Yes | Optional | No |
| Run named checks | Yes | May independently rerun | No |
| Inspect diff and flag issues | Yes | Yes | No when AI-only |
| Suggest changes | Yes | Yes | No |
| Confirm AI findings addressed | Yes | Human verifies material fixes | No |
| Approve merge | No | Yes | Yes |
| Authorize scope expansion | No | Yes | Yes |
| Authorize tag, Release, settings, or blocked work | No | Yes through a separate task | Yes only for that explicit authorization |

## Stop conditions

Stop, narrow, or create a control task when:

- the issue or capsule is missing;
- branch base or dependency state is unclear;
- a required file falls outside allowed scope;
- current tooling claims cannot be verified;
- canonical sources conflict;
- a compatibility file would duplicate a canonical source;
- tests or checks cannot be stated honestly;
- AI review is being substituted for human approval;
- data, model, public-output, release, or settings work lacks explicit authorization;
- the work would imply official, operational, emergency, field-validated, or endorsed status.

## Research validation summary

Research checked on 2026-07-09:

- OpenAI, Custom instructions with AGENTS.md: https://developers.openai.com/codex/guides/agents-md
- OpenAI, Prompting: https://developers.openai.com/codex/prompting
- GitHub, Linking a pull request to an issue: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue
- GitHub, About pull request reviews: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews
- GitHub, About merge methods: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github

The protocol adopts only architecture-level behavior from these sources. It does not configure Codex, GitHub reviews, protected branches, rulesets, Actions, or merge settings.

## Acceptance checklist

- [x] Issue-first and branch-scoped work is mandatory.
- [x] Canonical prompt-log and Codex task artifacts are identified.
- [x] Compatibility artifacts are constrained to routing roles.
- [x] Research timing and recording are explicit.
- [x] Allowed-file expansion requires human approval.
- [x] Prompt/build logging is mandatory for prompt-assisted file changes.
- [x] Tests/checks or documented non-applicability are mandatory.
- [x] AI-assisted review is separate from human approval.
- [x] Human review is mandatory before merge.
- [x] Task PRs close only task issues.
- [x] Post-merge synchronization is conditional on truth changing.
- [x] No settings or implementation work is authorized.

## Safe claim

BurnLens has drafted an Objective Six architecture for issue-backed, branch-scoped, prompt-logged, test-aware, human-reviewed repository work. The architecture becomes a merged repository control only after the P1O6-T01 PR receives human review and is merged.

## Unsupported claims

Do not claim that:

- repository settings enforce this protocol;
- AI review replaces human approval;
- all past work followed the Objective Six protocol;
- later Objective Six templates or guidance already exist;
- data, models, runs, maps, demos, tags, or Releases are authorized;
- BurnLens is official, operational, field-validated, emergency-ready, or agency-endorsed.

## Handoff

P1O6-T02 should use this protocol and `OBJECTIVE_SIX_ARTIFACT_CONTRACTS.md` to create a root prompt-log navigation entry point that routes to the existing canonical protocol, entry template, and dated entries without creating a parallel source of truth.