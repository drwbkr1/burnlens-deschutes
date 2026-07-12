# Phase One / Objective Six — Tracker

## Current status

| Field | Current value |
|---|---|
| Objective | Phase One / Objective Six — Prompt-Built Development Protocol |
| Parent issue | #195 — open |
| Completed planned tasks | P1O6-T01 through P1O6-T07 |
| Active task | P1O6-T08 / #226 — research validation and protocol cohesion review |
| T08 state | Revalidated and review-ready on `p1o6t08b`; PR not yet created |
| T08 remediation | REM-08A PR #228; SYNC-08A PR #230; REM-08B PR #232; SYNC-08B PR #234 — merged |
| Next planned task | P1O6-T09 — only after T08 review, merge, and required status sync |
| Objective complete | No |
| Data/model/map/public-output authorization | Not authorized |
| Tag or GitHub Release authorization | Not authorized |

## Purpose

Objective Six defines how prompt-assisted BurnLens repository work is authorized, scoped, executed, recorded, verified, reviewed, merged, synchronized, and handed off.

It integrates the existing SOP, task packet, prompt/build-log controls, issue intake, branch/PR workflow, contributor guidance, agent guidance, and human-review surfaces without creating duplicate sources of truth.

## Success gate

Objective Six is complete only when:

1. every planned task is merged or deliberately deferred with a reason;
2. canonical and compatibility roles are explicit;
3. prompt-assisted work begins from an issue and bounded task capsule;
4. changes occur on a task branch and reach `main` through a PR;
5. prompt logging records instructions, scope, research, decisions, verification, review, synchronization, and handoff;
6. applicable checks have names, methods, and actual results;
7. non-applicable checks have task-specific reasons;
8. human review is separate from author self-audit and AI-assisted review;
9. current-status records agree;
10. no unauthorized data, model, run, map, public-output, setting, tag, or Release work occurs;
11. T09 closeout and handoff are reviewed and merged.

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
| P1O6-T01 | #196 | Architecture, tracker, contracts, development protocol | Merged via PR #197; synchronized via PR #199 |
| P1O6-T02 | #200 | Root prompt-log navigation | Merged via PR #201; synchronized via PR #203 |
| P1O6-T03 | #204 | Task-packet compatibility wrapper | Merged via PR #206; synchronized via PR #208 |
| P1O6-T04 | #205 | Repository agent instructions | Merged via PR #209; synchronized via PR #211 |
| P1O6-T05 | #212 | Contributor guidance | Merged via PR #213; synchronized via PR #215 |
| P1O6-T06 | #216 | Human-review checklist and PR template | Merged via PR #217; synchronized via PR #219 |
| P1O6-T07 | #220 | Task issue form and SOP integration | Merged via PR #221; synchronized via PR #225 |
| P1O6-REM-08A | #227 | Canonical prompt-log controls | Merged via PR #228; synchronized via PR #230 |
| P1O6-REM-08B | #231 | Objective Six routing and path language | Merged via PR #232; synchronized via PR #234 |
| P1O6-T08 | #226 | Research validation and protocol cohesion review | Revalidated; review-ready on `p1o6t08b` |
| P1O6-T09 | pending | Closeout, handoff, final status, parent summary | Planned; blocked until T08 merges |

## Dependency rules

- T08 may proceed only after T01-T07 and required remediation are merged.
- T09 may proceed only after T08 merges and current status is synchronized where needed.
- A dependency override requires an explicit issue and recorded human approval.
- Parallel branches must not modify the same files without an explicit dependency and merge order.

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

## Review model

| Stage | Rule |
|---|---|
| Author self-audit | Assertions and evidence only; not independent approval |
| Executable/manual checks | Named methods with actual results and limitations |
| AI-assisted review | Optional supplemental findings; cannot approve or authorize scope |
| Human review | Mandatory inspection and one outcome: Approve, Request changes, or Defer/reject |
| Merge authorization | Separate authorization after approval and resolved blockers |

Written policy does not create CI, required checks, required approvals, branch protection, rulesets, CODEOWNERS, or other GitHub enforcement.

## T08 revalidation result

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
| T08 human review and merge | Pending |
| Parent closure avoided | Satisfied; #195 remains open |

## Safe claims

- Objective Six has a merged issue-backed prompt-to-repository architecture and current canonical-role map.
- T01-T07 and the two T08 remediation tasks are merged.
- T08 has been revalidated and is ready for human review.
- Human review remains distinct from AI-assisted review.
- Every task requires named checks and results or task-specific non-applicability.
- No data, model, run, map, public-output, repository-setting, tag, or GitHub Release work was authorized by Objective Six.

## Unsupported claims

Do not claim that:

- Objective Six is complete before T09;
- T08 is merged before its PR merges;
- T09 has started;
- author self-audit or AI review is human approval;
- repository settings enforce the written workflow;
- data, models, runs, maps, public outputs, tags, or GitHub Releases exist;
- BurnLens is official, operational, field-validated, emergency-ready, production-ready, or agency-endorsed.

## Handoff

Review and merge T08 only after the final five-file diff is confirmed clean and Drew records **Approve**. After merge, inspect README, this tracker, the canonical prompt-log index, and the dated T08 log. Synchronize stale status in a separate task, then proceed to P1O6-T09.
