# Phase One / Objective Six — Tracker

## Current status

| Field | Current value |
|---|---|
| Objective | Phase One / Objective Six — Prompt-Built Development Protocol |
| Parent issue | #195 — open; ready for manual closure only after Drew's separate explicit authorization |
| Completed planned tasks | P1O6-T01 through P1O6-T09 |
| Last completed task | P1O6-T09 / #239 — merged through PR #243 |
| Prerequisite closeout remediation | P1O6-REM-09A / #238 — merged through PR #240 |
| Prerequisite status synchronization | P1O6-SYNC-09A / #241 — merged through PR #242 |
| Final current-status synchronization | P1O6-SYNC-09 / #244 — this revision finalizes repository truth when merged |
| Objective complete | Yes — documented, reviewable repository-control baseline; executed implementation reliability is not claimed |
| Recommended next workstream | Phase Two data-intake preparation — planning/control records only |
| Phase Two data or implementation authorization | Not authorized |
| Tag or GitHub Release authorization | Not authorized |

## Purpose

Objective Six defines how prompt-assisted BurnLens repository work is authorized, scoped, executed, recorded, verified, reviewed, merged, synchronized, and handed off.

It integrates the SOP, task packet, prompt/build-log controls, issue intake, branch/PR workflow, contributor guidance, agent guidance, and human-review surfaces without creating duplicate sources of truth.

## Success gate

Objective Six is complete because:

1. every planned task is merged or deliberately deferred with a reason;
2. canonical and compatibility roles are explicit;
3. prompt-assisted work begins from an issue and bounded task capsule;
4. changes occur on a task branch and reach `main` through a PR;
5. prompt logging records instructions, scope, research, decisions, verification, review, synchronization, and handoff;
6. applicable checks have names, methods, and actual results;
7. non-applicable checks have task-specific reasons;
8. human review is separate from author self-audit and AI-assisted review;
9. current-status records agree through the final synchronization revision;
10. no unauthorized data, model, run, map, public-output, setting, tag, or Release work occurred;
11. T09 closeout and handoff were human-reviewed and merged;
12. final `main` status was rechecked after T09 merge.

Parent #195 closure is a separate administrative action and still requires Drew's explicit authorization.

## Governing boundaries

The following remain controlling:

- `docs/workflows/PROMPT_TO_REPO_SOP.md`;
- `AGENTS.md`;
- `docs/objective-one/USE_BOUNDARIES.md`;
- `docs/objective-one/SOURCE_PRECEDENCE.md`;
- `docs/phase-one/objective-five/OBJECTIVE_FIVE_HANDOFF.md`;
- `VERSIONING.md`.

Objective Six does not authorize imagery or data acquisition, AOI selection, labels, masks, baselines, models, metrics, runs, reports, maps, screenshots, public demos, public claims, repository settings, branch protection, rulesets, Actions, labels, milestones, Projects, tags, or GitHub Releases.

## Task sequence

| Task | Issue | Primary responsibility | Status |
|---|---:|---|---|
| P1O6-T01 | #196 | Architecture, tracker, contracts, development protocol | Merged via PR #197; synchronized by #198 / PR #199 |
| P1O6-T02 | #200 | Root prompt-log navigation | Merged via PR #201; synchronized by #202 / PR #203 |
| P1O6-T03 | #204 | Task-packet compatibility wrapper | Merged via PR #206; synchronized by #207 / PR #208 |
| P1O6-T04 | #205 | Repository agent instructions | Merged via PR #209; synchronized by #210 / PR #211 |
| P1O6-T05 | #212 | Contributor guidance | Merged via PR #213; synchronized by #214 / PR #215 |
| P1O6-T06 | #216 | Human-review checklist and PR template | Merged via PR #217; synchronized by #218 / PR #219 |
| P1O6-T07 | #220 | Task issue form and SOP integration | Merged via PR #221; synchronized by #224 / PR #225 |
| P1O6-REM-08A | #227 | Canonical prompt-log controls | Merged via PR #228; synchronized by #229 / PR #230 |
| P1O6-REM-08B | #231 | Objective Six routing and path language | Merged via PR #232; synchronized by #233 / PR #234 |
| P1O6-T08 | #226 | Research validation and protocol cohesion review | Merged via PR #235; synchronized by #236 / PR #237 |
| P1O6-REM-09A | #238 | Final stale Objective Six status controls | Merged via PR #240; synchronized by #241 / PR #242 |
| P1O6-T09 | #239 | Closeout, handoff, final status, and parent-close recommendation | Merged via PR #243; issue #239 closed |

No planned task or required remediation is deferred.

## Dependency and close rules

- T09 began only after T08, REM-09A, and SYNC-09A merged.
- A dependency override requires an explicit issue and recorded human approval.
- Parallel branches must not modify the same files without an explicit dependency and merge order.
- The T09 PR used `Closes #239` only.
- Parent #195 remained open through T09 merge.
- Parent #195 is ready for manual closure only after this final synchronization reaches `main`, the completion summary is posted, and Drew explicitly authorizes closure.

## Canonical artifact roles

| Artifact | Role |
|---|---|
| `docs/workflows/PROMPT_TO_REPO_SOP.md` | Full workflow, context tiers, gates, review/merge rules, and closeout rules |
| `AGENTS.md` | Repository-level prompt-assisted agent instructions |
| `CONTRIBUTING.md` | Human-facing workflow guidance |
| `.github/ISSUE_TEMPLATE/task.yml` | Structured issue-first authorization intake |
| `templates/CODEX_TASK_PACKET.md` | Sole canonical executable task capsule |
| `templates/CODEX_TASK_TEMPLATE.md` | Non-canonical compatibility wrapper |
| `records/PROMPT_BUILD_LOG.md` | Canonical prompt-log protocol and dated-entry index |
| `templates/PROMPT_LOG_ENTRY.md` | Canonical detailed prompt-log entry template |
| `PROMPT_LOG.md` | Non-canonical prompt-log navigation |
| `docs/phase-one/objective-six/PROMPT_BUILT_DEVELOPMENT_PROTOCOL.md` | Current issue-to-merge architecture |
| `docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md` | Detailed human-review and merge-authorization record |
| `.github/PULL_REQUEST_TEMPLATE.md` | Concise PR evidence and routing surface |
| `docs/phase-one/objective-six/OBJECTIVE_SIX_RESEARCH_VALIDATION_LOG.md` | Current OpenAI/GitHub claim validation |
| `docs/phase-one/objective-six/OBJECTIVE_SIX_COHESION_REVIEW.md` | Requirement coverage, findings, remediation, and cohesion decision |
| `docs/phase-one/objective-six/OBJECTIVE_SIX_CLOSEOUT.md` | Final objective decision, evidence inventory, limitations, and parent-close recommendation |
| `docs/phase-one/objective-six/OBJECTIVE_SIX_HANDOFF.md` | Completed baseline, next-workstream context, gates, and `Do not carry forward` guidance |

## Review model

| Stage | Rule |
|---|---|
| Author self-audit | Assertions and evidence only; not independent approval |
| Executable/manual checks | Named methods with actual results and limitations |
| AI-assisted review | Optional supplemental findings; cannot approve or authorize scope |
| Human review | Mandatory inspection and one outcome: Approve, Request changes, or Defer/reject |
| Merge authorization | Separate authorization after approval and resolved blockers |

Written policy does not create CI, required checks, required approvals, branch protection, rulesets, CODEOWNERS, or other GitHub enforcement.

## T08 final result

| Criterion | State |
|---|---|
| Official OpenAI/GitHub claims checked and caveated | Satisfied |
| Requirement-coverage matrix | Satisfied |
| Selected paths resolve | Satisfied after remediation |
| Issue-form YAML/schema evidence | Satisfied |
| One canonical prompt-log system | Satisfied after PR #228 |
| One canonical task packet | Satisfied |
| AGENTS and CONTRIBUTING agree | Satisfied after PR #232 |
| PR checklist and template agree | Satisfied |
| Issue form covers task-packet inputs | Satisfied |
| SOP points to controlling artifacts | Satisfied |
| Human review cannot be satisfied by AI | Satisfied |
| Named verification or task-specific N/A | Satisfied |
| Policy versus enforcement distinction | Satisfied |
| Controlled-work gates preserved | Satisfied |
| Critical findings open | 0 |
| High findings open | 0 |
| Medium findings open | 0 |
| Low findings open | 1 accepted historical-status caveat |
| Human approval and merge | Satisfied through PR #235 |
| Task issue closure | Satisfied; #226 closed |
| Parent closure avoided | Satisfied; #195 remains open |

## T09 closeout gate

| Criterion | Final state |
|---|---|
| Issue #239 was sole authorization | Satisfied |
| Prerequisite #238 / PR #240 | Merged |
| Required synchronization #241 / PR #242 | Merged |
| Branch created from current `main` | Satisfied; `p1o6t09b` from `f25c6b9d77b1a19900f27b8a85354d3b63466a60` |
| Six authorized paths only | Satisfied; PR #243 contained exactly six authorized paths |
| Closeout and handoff exist | Satisfied on `main` |
| README, tracker, and prompt-log agreement | Satisfied through P1O6-SYNC-09 |
| T08 cohesion passes | Satisfied |
| No material status contradiction | Satisfied |
| Human closeout review | Drew — Approve |
| Merge authorization | Drew — squash merge of reviewed head |
| T09 merge | PR #243 at `1a142633e8d91ad7451f3ac4cc3c86dc7ddd2640` |
| Task issue closure | Satisfied; #239 closed |
| Parent close readiness | Ready after this sync reaches `main`; explicit closure authorization still required |

## Controlled-work and release state

```text
Phase Two: not started
Data or imagery: not acquired or changed
AOI: not selected or created
Labels, masks, baselines, or models: not created
Metrics, runs, reports, maps, screenshots, demos, or public outputs: not created
Repository settings or CI: not configured or claimed by Objective Six
Proposed tag v0.0.5-objective-five-traceability: not created
GitHub Release: not created
```

## Safe claims

- Objective Six is complete as a documented, reviewable repository-control baseline.
- Objective Six has a merged issue-backed prompt-to-repository architecture and current canonical-role map.
- T01-T09, the T08 remediation tasks, REM-09A, and their required synchronizations are merged or represented in the final synchronization record.
- T08 provides a current research validation log and cohesion review with no unresolved Critical, High, or Medium contradiction.
- Human review remains distinct from AI-assisted review.
- Every task requires named checks and results or task-specific non-applicability.
- No data, model, run, map, public-output, repository-setting, tag, or GitHub Release work was authorized by Objective Six.

## Completion claim boundary

> BurnLens Deschutes has a documented, reviewable prompt-built development protocol connecting issue-backed authorization, bounded task capsules and branches, selective context loading, prompt/build logging, named verification, task-scoped pull requests, mandatory human review distinct from AI-assisted review, controlled merge authorization, conditional status synchronization, and handoff.

This claim does not mean the future data/model/run workflow was executed or proven reliable.

## Unsupported claims

Do not claim that:

- parent #195 is closed before explicit closure authorization;
- author self-audit or AI review is human approval;
- repository settings enforce the written workflow;
- Phase Two implementation has begun;
- data, models, runs, maps, public outputs, tags, or GitHub Releases exist;
- BurnLens is official, operational, field-validated, emergency-ready, production-ready, or agency-endorsed.

## Handoff

Use `OBJECTIVE_SIX_HANDOFF.md` for the next separately authorized workstream. The recommended next workstream is Phase Two data-intake preparation limited to a parent tracker and first source/AOI intake planning task. It must not touch data or begin implementation.

Parent #195 remains open until Drew explicitly authorizes manual closure after the final synchronization is confirmed on `main`.
