# Phase One / Objective Six — Tracker

## Status

| Field | Current value |
|---|---|
| Objective | Phase One / Objective Six — Prompt-Built Development Protocol |
| Parent issue | #195 — open |
| Completed tasks | P1O6-T01 / #196 through PR #197; P1O6-T02 / #200 through PR #201; P1O6-T03 / #204 through PR #206; P1O6-T04 / #205 through PR #209; P1O6-T05 / #212 through PR #213; P1O6-T06 / #216 through PR #217; P1O6-T07 / #220 through PR #221 |
| Next task | P1O6-T08 — research validation and protocol cohesion review |
| Current state | T01-T07 are merged; T07 current-status records are synchronized through PR #225; T08 is next |
| Data/model/map/public-output authorization | Not authorized |
| Tag or GitHub Release authorization | Not authorized |

## Purpose

Objective Six defines how prompt-assisted BurnLens repository work is authorized, scoped, executed, recorded, verified, reviewed, merged, and handed off.

The objective converts the existing prompt-to-repo SOP, Codex task packet, prompt/build-log protocol, issue workflow, and pull-request workflow into one coherent operating architecture without creating duplicate sources of truth.

## Success gate

Objective Six is complete only when all of the following are true:

1. Every planned task is merged or deliberately deferred with a recorded reason.
2. Canonical and compatibility artifact roles are explicit.
3. Prompt-assisted work begins from a task issue and a bounded task capsule.
4. Work occurs on a task branch and reaches `main` only through a pull request.
5. Prompt/build logging records material instructions, files, decisions, research, verification, and review-driven changes.
6. Named tests or checks and their actual results are mandatory when applicable.
7. A documented reason is mandatory when a test or check does not apply.
8. Human review is recorded separately from AI-assisted review.
9. AI review is treated as supplemental and cannot satisfy human approval.
10. Current-status records are synchronized without rewriting completed objective records.
11. No unauthorized data, model, run, map, public-output, tag, Release, or repository-settings work occurs.

## Governing boundaries

This objective is documentation, workflow, template, and records work only unless a later task explicitly authorizes a narrower change.

The following remain controlling:

- `docs/workflows/PROMPT_TO_REPO_SOP.md`
- `AGENTS.md`
- `docs/objective-one/USE_BOUNDARIES.md`
- `docs/objective-one/SOURCE_PRECEDENCE.md`
- `docs/phase-one/objective-five/OBJECTIVE_FIVE_HANDOFF.md`
- `VERSIONING.md`

Objective Six does not authorize imagery or data acquisition, AOI selection, labels, masks, baselines, models, metrics, runs, reports, maps, screenshots, public demos, public claims, tags, GitHub Releases, repository settings, branch protection, rulesets, Actions, labels, milestones, or Projects.

## Task sequence and dependencies

| Task | Owner / responsibility | Primary deliverable(s) | Dependency | Status |
|---|---|---|---|---|
| P1O6-T01 | Protocol architecture owner | `OBJECTIVE_SIX_TRACKER.md`; `OBJECTIVE_SIX_ARTIFACT_CONTRACTS.md`; `PROMPT_BUILT_DEVELOPMENT_PROTOCOL.md`; README status update | Objective Five handoff and SOP | Merged via PR #197; status synchronized via PR #199 |
| P1O6-T02 | Prompt-log navigation owner | Root `PROMPT_LOG.md`; prompt-log protocol/index acknowledgement; README navigation update | T01 merged | Merged via PR #201; status synchronized via PR #203 |
| P1O6-T03 | Codex task-interface owner | `templates/CODEX_TASK_TEMPLATE.md`; compatibility relationship with `templates/CODEX_TASK_PACKET.md` | T01-T02 merged | Merged via PR #206; status synchronized via PR #208 |
| P1O6-T04 | Repository-instruction owner | Refresh `AGENTS.md` to reflect current phase and merged protocol | T01-T03 merged | Merged via PR #209; status synchronized through P1O6-SYNC-04 |
| P1O6-T05 | Contributor-guidance owner | `CONTRIBUTING.md` | T01-T04 merged | Merged via PR #213; status synchronized via PR #215 |
| P1O6-T06 | Human-review owner | `docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md`; `.github/PULL_REQUEST_TEMPLATE.md` | T01-T05 merged | Merged via PR #217; status synchronized via PR #219 |
| P1O6-T07 | Issue-intake owner | `.github/ISSUE_TEMPLATE/task.yml`; SOP integration; tracker and prompt-log records | T01-T06 merged | Merged via PR #221; status synchronized via PR #225 |
| P1O6-T08 | Cohesion and research owner | Objective Six research validation and protocol cohesion review | T01-T07 merged | Next |
| P1O6-T09 | Closeout owner | Closeout, handoff, current-status synchronization, and parent summary | T01-T08 merged or deliberately deferred | Planned |

## Dependency rules

- T01 must merge before any later Objective Six deliverable is created.
- T02 and T03 implement the naming architecture decided in T01; they must not reopen canonical-role decisions without an explicit contract change.
- T04 follows T02 and T03 so `AGENTS.md` points to final canonical entry points.
- T05 follows the repository-instruction refresh so contributor guidance does not conflict with `AGENTS.md`.
- T06 defines the human-review surface after contributor and agent guidance are aligned.
- T07 modernizes issue intake only after the downstream task and review requirements are stable.
- T08 validates the complete protocol only after T07 is merged and current-status truth is synchronized when needed.
- T09 closes the objective only after the tracker, README, prompt-log index, closeout, and handoff all describe the same state.

No blocked task is authorized to proceed around an unmet dependency. A dependency override requires an explicit issue and PR note from the human project owner.

## Canonical naming decisions

### Prompt-log artifacts

| Path | Role | Decision |
|---|---|---|
| `records/PROMPT_BUILD_LOG.md` | Canonical protocol and index | Remains the source of truth for prompt/build logging rules and entry indexing. |
| `templates/PROMPT_LOG_ENTRY.md` | Canonical detailed entry template | Remains the source of truth for task-level prompt/build-log content. |
| Root `PROMPT_LOG.md` | Compatibility and navigation entry point | Exists as a concise router to the canonical protocol, template, and dated entries. It does not contain a parallel log index or restate the protocol in full. |

### Codex task artifacts

| Path | Role | Decision |
|---|---|---|
| `templates/CODEX_TASK_PACKET.md` | Canonical executable task capsule | Remains the source of truth for task identity, context tiers, scope, research, verification, PR requirements, and handoff. |
| `templates/CODEX_TASK_TEMPLATE.md` | Compatibility and discoverability entry point | Exists as a concise wrapper that directs users to instantiate the canonical packet. It does not duplicate or diverge from packet fields. |

### Repository agent instructions

| Path | Role | Decision |
|---|---|---|
| `AGENTS.md` | Repository-level agent instructions | Routes prompt-assisted agents to the canonical SOP, task packet, prompt-log controls, verification rules, human-review gate, and boundary/release controls without reproducing them in full. |

### Contributor guidance

| Path | Role | Decision |
|---|---|---|
| `CONTRIBUTING.md` | Human-facing repository workflow | Routes human contributors and the solo maintainer to canonical controls, mandatory human review, honest verification, policy-versus-enforcement distinctions, scope escalation, and handoff without duplicating the full SOP or T06 checklist. |

### Pull-request review artifacts

| Path | Role | Decision |
|---|---|---|
| `docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md` | Detailed reusable human-review record | Owns the five-stage review evidence: author self-audit, actual checks, optional AI-assisted findings, human inspection, and merge authorization. Merged through PR #217. |
| `.github/PULL_REQUEST_TEMPLATE.md` | Concise PR intake and evidence surface | Routes to the standalone checklist and captures generic task linkage, scope, research, verification, security, boundaries, review separation, close behavior, and handoff without duplicating the checklist in full. Modernized through PR #217. |

### Issue-intake and SOP artifacts

| Path | Role | Current state |
|---|---|---|
| `.github/ISSUE_TEMPLATE/task.yml` | Structured issue-first intake surface for a bounded task contract. It captures authorization inputs but does not replace the canonical task packet. | Modernized and merged through PR #221. |
| `docs/workflows/PROMPT_TO_REPO_SOP.md` | Full repository workflow reference and context/gate authority. | Integrated with stable Objective Six artifact roles and merged through PR #221. |

## Review model

### Author self-audit

The author may verify task linkage, scope, research, checks, boundaries, claims, and handoff before requesting review. Author checkboxes are self-reported evidence only. They are not independent review or formal GitHub approval.

### Automated or executable checks

Each task reports the commands or inspection methods that actually apply and their actual results. Templates and written policy do not create CI jobs or required status checks.

### AI-assisted review

AI review may inspect a working-tree or branch diff, identify omissions, recommend tests, flag possible defects, or review a GitHub pull request. Its findings are evidence for the human reviewer.

AI review does not approve its own work and cannot satisfy the human-review gate.

### Human review

Human review requires the project owner or another identified person to inspect the proposed branch or pull-request diff, compare it with the task issue and acceptance criteria, review verification evidence, and record one of these outcomes:

- **Approve**;
- **Request changes**;
- **Defer or reject**.

For a personal repository, human review may be recorded in the PR checklist or a PR comment when GitHub does not provide a meaningful separate self-approval state. The record must still be distinct from AI review output and must not be described as formal author self-approval.

### Merge authorization

Merge authorization is recorded only after the human outcome is **Approve**, blocking findings are resolved, the final diff remains in scope, checks are accurately reported, and the task-only close keyword is correct.

## Tests and checks rule

Every task must record:

1. the named automated tests, linters, type checks, schema checks, link checks, rendering checks, smoke tests, or manual inspections that apply;
2. the exact command or inspection method;
3. the actual result;
4. any failure or limitation;
5. every expected check not run and the reason.

`Not applicable` is acceptable only with a task-specific reason. A task may not claim that tests passed unless a named check was actually executed.

## Final acceptance state for P1O6-T01

| Criterion | State |
|---|---|
| Objective purpose and success gate defined | Satisfied on `main` |
| Planned tasks, dependencies, paths, and owners listed | Satisfied on `main` |
| Prompt-log canonical and compatibility roles decided | Satisfied on `main` |
| Codex-template canonical and compatibility roles decided | Satisfied on `main` |
| Human review distinct from AI review | Satisfied; human merge authorization and AI-assisted review were recorded separately in PR #197 |
| Tests-or-documented-non-applicability rule defined | Satisfied on `main` |
| Duplicate source of truth prevented | Satisfied on `main` |
| README Objective Six status updated | Satisfied and synchronized |
| Required research recorded | Satisfied on `main` |
| Human review and merge | Satisfied through PR #197 |
| Task issue closure | Satisfied; #196 closed |
| Parent issue closure avoided | Satisfied; #195 remains open |

## Final acceptance state for P1O6-T02

| Criterion | State |
|---|---|
| Root `PROMPT_LOG.md` exists | Satisfied on `main` |
| Root file is navigation and compatibility only | Satisfied on `main` |
| Canonical protocol/index preserved | Satisfied; `records/PROMPT_BUILD_LOG.md` remains canonical |
| Canonical detailed entry template preserved | Satisfied; `templates/PROMPT_LOG_ENTRY.md` remains canonical |
| Dated-entry directory linked | Satisfied; `records/prompt-build-log/` is routed from the root file |
| Parallel protocol, index, schema, or transcript store avoided | Satisfied through content and diff review |
| Repository paths and links reviewed | Satisfied through PR #201 review |
| Tests/checks or non-applicability recorded | Satisfied in the T02 dated log and PR #201 |
| Human review distinct from AI review | Satisfied; human merge authorization and AI-assisted review were recorded separately in PR #201 |
| Human review and merge | Satisfied through PR #201 |
| Task issue closure | Satisfied; #200 closed |
| Parent issue closure avoided | Satisfied; #195 remains open |

## Final acceptance state for P1O6-T03

| Criterion | State |
|---|---|
| Compatibility wrapper exists | Satisfied; `templates/CODEX_TASK_TEMPLATE.md` is on `main` |
| Canonical packet preserved | Satisfied; `templates/CODEX_TASK_PACKET.md` remains unchanged and canonical |
| Correct relative link | Satisfied through T03 review |
| Concise instantiation guidance and bounded example | Satisfied through PR #206 |
| Parallel packet, schema, tier tables, or workflow avoided | Satisfied through diff and content review |
| README and prompt-log records updated | Satisfied and synchronized through PR #208 |
| Tests/checks or non-applicability recorded | Satisfied in the T03 dated log and PR #206 |
| Human review distinct from AI review | Satisfied; the human outcome was Approve and was recorded separately from AI-assisted findings |
| Human review and merge | Satisfied through PR #206 |
| Task issue closure | Satisfied; #204 closed |
| Parent issue closure avoided | Satisfied; #195 remains open |

## Final acceptance state for P1O6-T04

| Criterion | State |
|---|---|
| Root agent instructions refreshed | Satisfied; `AGENTS.md` reflects Objective Six on `main` |
| Stale Objective Four authorization language removed | Satisfied through PR #209 review |
| Canonical workflow and task-capsule roles routed correctly | Satisfied through PR #209 |
| Prompt-log roles routed correctly | Satisfied through PR #209 |
| Issue, branch, allowed-file, PR, and task-only close rules present | Satisfied on `main` |
| Human review distinct from AI review | Satisfied; Drew approved and AI-assisted findings were recorded separately |
| Tests/checks or task-specific non-applicability required | Satisfied on `main` |
| Before-data, claim, source-precedence, version, tag, and Release gates preserved | Satisfied through content and boundary review |
| Duplicate packet, schema, tier table, or checklist avoided | Satisfied through diff and content review |
| Human review and merge | Satisfied through PR #209 |
| Task issue closure | Satisfied; #205 closed |
| Parent issue closure avoided | Satisfied; #195 remains open |

## Final acceptance state for P1O6-T05

| Criterion | State |
|---|---|
| Root contributor guidance exists | Satisfied; `CONTRIBUTING.md` is on `main` |
| Human-facing workflow routes to canonical sources | Satisfied through PR #213 review |
| Issue-first and compact-branch requirements | Satisfied on `main` |
| Prompt logging and honest verification rules | Satisfied on `main` |
| Human review distinct from AI-assisted review | Satisfied; Drew's `Approve` outcome was recorded separately from AI findings |
| Solo-maintainer evidence defined without formal self-approval claim | Satisfied on `main` |
| Documented policy separated from GitHub enforcement | Satisfied; no configured-settings claim was introduced |
| Outside-contribution and support promises avoided | Satisfied through content review |
| Duplicate SOP, packet, schema, or future review checklist avoided | Satisfied through content and diff review |
| Human review and merge | Satisfied through PR #213 |
| Task issue closure | Satisfied; #212 closed |
| Parent issue closure avoided | Satisfied; #195 remains open |

## Final acceptance state for P1O6-T06

| Criterion | State |
|---|---|
| Task issue and branch | Satisfied; issue #216 closed after PR #217 merged from `p1o6t06b` |
| Canonical checklist path | Satisfied; `docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md` is on `main` and no competing `docs/workflows/` checklist was created |
| Standalone checklist | Satisfied through PR #217 review and merge |
| PR template modernization | Satisfied through PR #217; generic patterns replace Objective Four-specific examples |
| Five-stage review separation | Satisfied; author, checks, AI, human, and merge authorization are distinct |
| Tests/checks and non-applicability | Satisfied with exact-method, actual-result, and task-specific N/A requirements |
| Human review distinct from AI-assisted review | Satisfied; Drew's `Approve` outcome was recorded in PR #217 separately from AI findings |
| Solo-maintainer evidence | Satisfied without claiming formal author self-approval |
| Settings-enforcement distinction | Satisfied; no configured-settings or invented-CI claim was introduced |
| Prompt/build logging | Satisfied; dated T06 record and canonical index updated |
| Human review and merge | Satisfied through squash merge PR #217 at `c6db812af8887bf7c6718f9e38aaaf130923e7b4` |
| Task issue closure | Satisfied; #216 closed |
| Parent issue closure avoided | Satisfied; #195 remains open |
| Status synchronization | Satisfied through P1O6-SYNC-06 / PR #219 |
| Handoff | P1O6-T07 |

## Final acceptance state for P1O6-T07

| Criterion | State |
|---|---|
| Task issue and branch | Satisfied; issue #220 closed after PR #221 merged from `p1o6t07b` |
| Allowed-file scope | Satisfied; PR #221 changed exactly the five paths authorized by issue #220 |
| Issue-form modernization | Satisfied; `.github/ISSUE_TEMPLATE/task.yml` is on `main` with generic task patterns and bounded intake fields |
| SOP integration | Satisfied; `docs/workflows/PROMPT_TO_REPO_SOP.md` is on `main` with stable Objective Six routing and gates |
| Tier behavior | Satisfied; Tier 0 is required, Tier 1 remains selective, and Tier 2 remains excluded by default with justification when used |
| Research | Satisfied; current official GitHub and OpenAI sources were checked after branch creation and recorded in the dated log |
| Verification | Satisfied; YAML, schema, ID/label, requirement, path, consistency, boundary, claims, and branch-diff checks were recorded |
| Prompt/build logging | Satisfied; dated T07 record and canonical index updated |
| Human review distinct from AI-assisted review | Satisfied; Drew's `Approve` outcome was recorded separately from AI-assisted review in PR #221 |
| Human review and merge | Satisfied through squash merge PR #221 at `6225d9c9a90404f4730bd54727dbf01f56884842` |
| Task issue closure | Satisfied; #220 closed |
| Parent issue closure avoided | Satisfied; #195 remains open |
| Status synchronization | Satisfied through P1O6-SYNC-07 / PR #225 |
| Handoff | P1O6-T08 |

## Safe claims

- Objective Six has a merged issue-backed architecture, tracker, artifact-contract map, and prompt-built development protocol.
- Root `PROMPT_LOG.md` is a merged non-canonical navigation entry point to the canonical prompt-log sources.
- `records/PROMPT_BUILD_LOG.md` remains the canonical prompt/build-log protocol and index.
- `templates/PROMPT_LOG_ENTRY.md` remains the canonical detailed entry template.
- `templates/CODEX_TASK_PACKET.md` remains the canonical executable task capsule.
- `templates/CODEX_TASK_TEMPLATE.md` is a merged non-canonical compatibility and discoverability wrapper.
- Root `AGENTS.md` contains merged repository-level prompt-assisted work instructions aligned with Objective Six.
- Root `CONTRIBUTING.md` contains merged human-facing workflow guidance aligned with Objective Six.
- P1O6-T01 merged through PR #197 and was synchronized through PR #199.
- P1O6-T02 merged through PR #201 and was synchronized through PR #203.
- P1O6-T03 merged through PR #206 and was synchronized through PR #208.
- P1O6-T04 merged through PR #209 and was synchronized through P1O6-SYNC-04.
- P1O6-T05 merged through PR #213 and was synchronized through PR #215.
- P1O6-T06 merged through PR #217 and was synchronized through PR #219.
- P1O6-T07 merged through PR #221 and was synchronized through PR #225.
- BurnLens has a merged generic task issue form and integrated SOP routing that capture bounded task scope, selective context loading, prompt logging, verification, mandatory human review, task-scoped issue closure, parent protection, and handoff without claiming repository-settings enforcement.
- BurnLens has a merged reusable human PR review checklist and generic PR template that separate author self-audit, actual checks, optional AI-assisted findings, human inspection, and merge authorization without claiming repository-settings enforcement.
- No data, model, run, map, public-output, tag, Release, or repository-settings work was authorized by T01-T07 or their synchronization tasks.

## Unsupported claims

Do not claim that:

- Objective Six is complete;
- P1O6-T08 or later Objective Six deliverables exist or have started;
- author self-audit or AI review is equivalent to human approval;
- repository settings enforce this protocol;
- another eligible human reviewer currently exists;
- BurnLens has started data, model, run, map, or public-demo work;
- a tag or GitHub Release exists;
- BurnLens is official, operational, field-validated, emergency-ready, or agency-endorsed.

## Rejection and defer criteria

Revise or defer work if:

- a later task lacks a merged dependency;
- a proposed compatibility artifact duplicates a canonical source;
- a task lacks an issue, branch, allowed-file scope, acceptance criteria, or handoff;
- research-backed tooling claims cannot be verified from official sources;
- verification is described without named commands or inspection methods;
- author self-audit or AI review is presented as human approval;
- merge authorization is recorded before human approval or while blocking findings remain;
- the task would broaden into unauthorized implementation, public-output, release, or settings work.

## Handoff

P1O6-T07 / #220 merged through PR #221 at `6225d9c9a90404f4730bd54727dbf01f56884842` and was synchronized through P1O6-SYNC-07 / PR #225. Proceed to P1O6-T08 — Research validation and protocol cohesion review. T08 must use current `main`, the merged Objective Six artifacts, the current SOP, the canonical prompt-log controls, and current official GitHub/OpenAI sources. It must not begin implementation, data, model, public-output, repository-setting, tag, or GitHub Release work.
