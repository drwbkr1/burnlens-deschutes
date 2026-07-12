# BurnLens Prompt-Built Development Protocol

## Status

| Field | Value |
|---|---|
| Objective | Phase One / Objective Six |
| Parent issue | #195 — open |
| Completed planned tasks | P1O6-T01 through P1O6-T08 |
| Last completed task | P1O6-T08 / #226 — merged through PR #235 |
| T08 synchronization | P1O6-SYNC-08 / #236 — merged through PR #237 |
| Next planned task | P1O6-T09 / #239 — after prerequisite remediation #238 |
| Data/model/map/public-output authorization | Not authorized |
| Tag or GitHub Release authorization | Not authorized |

## Purpose and scope

This protocol explains how BurnLens prompt-assisted repository work moves from authorization to merge and handoff.

It does not replace the full SOP, task issue, canonical task packet, prompt/build-log protocol, branch-and-PR baseline, contributor guidance, issue form, PR template, or PR review checklist. It defines how those controls work together and which source owns each rule.

The protocol can govern documentation, workflow, template, records, code, configuration, data, model, and public-output tasks only when a separate issue and the applicable phase controls explicitly authorize that work. Objective Six itself remains documentation, workflow, template, and records work.

## Governing source order

Use these sources according to their roles:

1. `docs/workflows/PROMPT_TO_REPO_SOP.md` — full workflow, context tiers, gates, and closeout rules.
2. `AGENTS.md` — repository-level prompt-assisted agent instructions.
3. GitHub task issue — task authorization and exact allowed scope.
4. `templates/CODEX_TASK_PACKET.md` — canonical executable task capsule.
5. `records/PROMPT_BUILD_LOG.md` — canonical prompt/build-log protocol and index.
6. `templates/PROMPT_LOG_ENTRY.md` — canonical detailed prompt/build-log entry template.
7. `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md` — branch, PR, merge, and post-merge baseline.
8. Objective- and workstream-specific controls selected through the SOP.
9. `docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md` — detailed human-review and merge-authorization record.

When sources conflict, stop before editing. Resolve the conflict through the issue or a separate control task. Do not silently choose the broader interpretation.

## Canonical and routing artifacts

### Task briefing

- `templates/CODEX_TASK_PACKET.md` is the sole canonical executable task capsule.
- `templates/CODEX_TASK_TEMPLATE.md` is a merged, non-canonical compatibility and discoverability wrapper.
- The wrapper must route to the packet and must not maintain a second required-field schema or workflow.

### Prompt logging

- `records/PROMPT_BUILD_LOG.md` is the sole canonical protocol and dated-entry index.
- `templates/PROMPT_LOG_ENTRY.md` is the sole canonical detailed entry template.
- `PROMPT_LOG.md` is a merged, non-canonical root router.
- The router must not become a second protocol, index, template, status register, or transcript archive.

### Issue and pull-request intake

- `.github/ISSUE_TEMPLATE/task.yml` is the structured task-authorization intake surface.
- `.github/PULL_REQUEST_TEMPLATE.md` is the concise PR evidence surface.
- `docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md` is the detailed reusable review record.
- Intake and review surfaces route to canonical controls; they do not replace them.

## Required workflow

```text
approved task issue
→ compact task capsule
→ branch from current main
→ Tier 0 plus selective Tier 1 context
→ justified Tier 2 only when needed
→ fresh research when required
→ edits within allowed files
→ dated prompt/build log
→ named checks and actual results
→ branch diff against main
→ task-scoped pull request
→ optional AI-assisted review
→ mandatory human review
→ separate merge authorization
→ authorized merge
→ parent update and conditional status synchronization
→ handoff
```

Skipping human review is never permitted. Any other skipped step requires a task-specific reason in the issue, log, or PR.

## Authorization and task capsule

Every meaningful task begins with its own issue or an explicitly approved bundled-task issue.

The issue identifies:

- task and parent;
- branch and base;
- dependencies;
- primary and supporting artifacts;
- allowed files;
- forbidden work;
- context requirements;
- research;
- verification;
- acceptance;
- human-review requirement;
- task-only close keyword;
- parent protection;
- handoff.

The task capsule is instantiated from `templates/CODEX_TASK_PACKET.md`. It may narrow the issue but may not add files, claims, or work the issue did not authorize.

## Branch and file-scope discipline

Create one compact task branch from current `main` unless the issue authorizes another base.

Prompt-assisted edits must not be made directly to `main`.

When another file becomes necessary:

1. stop before changing it;
2. explain why the current contract is insufficient;
3. revise the issue and capsule or create a separate task;
4. proceed only after human approval.

Connector friction does not authorize broader scope, temporary files on `main`, thinner artifacts, or bypassed review.

## Context loading

Load or summarize Tier 0 for every task. Select only the Tier 1 artifacts that match the work.

Tier 2 is historical or verification context only. Record every Tier 2 artifact and the specific reason current controls were insufficient. Historical drafts must not override current merged controls.

## Research

Fresh research is required after branch creation when the task depends on current technical, tooling, API, official, policy, legal, safety, source, dataset, model, or public-claim facts.

Prefer official or primary sources. Record:

- claim ID;
- source and URL or repository path;
- fact supported;
- affected artifact or decision;
- adopted wording or decision;
- date checked;
- support status or unresolved limitation.

When external research is not required, record why repository-internal verification is sufficient.

## Prompt/build logging

Prompt-assisted file changes require a dated entry under:

```text
records/prompt-build-log/YYYY-MM-DD-task-id.md
```

Use the canonical protocol and detailed template. Record identity, authorization, context, files, research, decisions, checks, boundaries, claims, review separation, merge state, synchronization, handoff, and `Do not carry forward`.

Do not record secrets, credentials, private reasoning, unnecessary transcripts, unnecessary personal information, or unreviewed operational guidance.

## Verification and diff review

Every task requires named verification.

For each applicable check, record the exact command or manual method, actual result, evidence, and limitation. A non-applicable check requires a task-specific reason.

Do not claim tests passed unless named tests or commands ran. Written policy does not create CI jobs, required checks, branch protection, rulesets, approvals, or other platform enforcement.

Before PR, compare the complete branch with its authorized base and confirm:

- every changed file is allowed;
- no scratch, generated, credential, or connector-test file exists;
- acceptance criteria are covered;
- research-backed statements have support;
- status language is accurate;
- boundaries and source precedence are preserved;
- unsupported claims are absent;
- the handoff is clear.

## Pull request, review, and merge

Every meaningful task reaches `main` through a task-scoped PR.

The PR targets `main` unless the issue authorizes another base, reports files/research/checks/boundaries, and uses:

```text
Closes #TASK_ISSUE
```

Ordinary task PRs do not close the parent objective issue.

Keep review stages distinct:

| Stage | Role | Satisfies human gate? |
|---|---|---:|
| Author self-audit | Author assertions about scope and evidence | No |
| Executable checks | Commands or manual methods with actual results | No |
| AI-assisted review | Supplemental defect and consistency findings | No |
| Human review | Inspection and `Approve`, `Request changes`, or `Defer or reject` outcome | Yes, when recorded |
| Merge authorization | Separate authorization after approval and resolved blockers | Required before merge |

For the solo-maintainer workflow, an explicit PR comment or completed checklist may record the human policy outcome. It is not formal GitHub author self-approval.

Merge only when:

- the human outcome is **Approve**;
- blocking findings are resolved;
- dependencies are resolved or explicitly accepted;
- the final diff remains in scope;
- checks are accurately reported;
- task-only closure and parent protection are correct;
- the merge method is permitted and authorized.

Prefer squash merge for bounded task branches when allowed and authorized.

## Post-merge synchronization

After merge:

- confirm the task issue closed;
- confirm the parent stayed open unless closeout explicitly authorized closure;
- comment on the parent with task, PR, artifacts, state, and next action;
- inspect README, the current tracker, canonical prompt-log index, and dated task log;
- create a separate sync task only when those records are stale;
- avoid rewriting completed-objective records.

## Data, claim, version, tag, and Release gates

This protocol does not authorize data, imagery, AOIs, labels, masks, baselines, models, metrics, runs, reports, maps, screenshots, public demos, public claims, repository settings, tags, or GitHub Releases.

Before controlled work, apply the matching SOP and Objective Five gates. Official sources govern. Version identifiers do not imply readiness. Tag creation and GitHub Release publication require separate explicit authorization.

## Stop conditions

Stop, narrow, or create a control task when:

- the issue or capsule is missing or conflicting;
- branch base or dependency state is unclear;
- required work is outside the allowed paths;
- current external claims cannot be verified;
- canonical sources conflict;
- a compatibility file would duplicate a canonical source;
- checks cannot be reported honestly;
- AI review is being substituted for human approval;
- controlled data, model, public-output, setting, tag, or Release work lacks explicit authorization;
- the work would imply official, operational, emergency, field-validated, or endorsed status.

## Current handoff

P1O6-T08 merged through PR #235 and was synchronized through PR #237. Its cohesion review records no unresolved Critical, High, or Medium contradiction.

P1O6-T09 / #239 is the next planned task. Before creating `p1o6t09b`, confirm prerequisite remediation #238 has merged and any required status synchronization is complete. T09 may document Objective Six completion only after its closeout and handoff receive separate human review and merge; parent #195 remains open until final `main` verification and explicit closure authorization.
