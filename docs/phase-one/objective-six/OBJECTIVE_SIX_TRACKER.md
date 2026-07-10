# Phase One / Objective Six — Tracker

## Status

| Field | Current value |
|---|---|
| Objective | Phase One / Objective Six — Prompt-Built Development Protocol |
| Parent issue | #195 — open |
| Completed tasks | P1O6-T01 / #196 through PR #197; P1O6-T02 / #200 through PR #201 |
| Next task | P1O6-T03; issue and branch not yet created |
| Current state | T01 architecture and T02 prompt-log navigation are merged and synchronized; T03 is next |
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
| P1O6-T03 | Codex task-interface owner | Future `templates/CODEX_TASK_TEMPLATE.md`; compatibility relationship with `templates/CODEX_TASK_PACKET.md` | T01-T02 merged | Next; issue and branch not yet created |
| P1O6-T04 | Repository-instruction owner | Refresh `AGENTS.md` to reflect current phase and merged protocol | T01-T03 merged | Planned |
| P1O6-T05 | Contributor-guidance owner | Future `CONTRIBUTING.md` | T01-T04 merged | Planned |
| P1O6-T06 | Human-review owner | Future standalone review checklist and authorized PR-template modernization | T01-T05 merged | Planned |
| P1O6-T07 | Issue-intake owner | Authorized issue-form modernization and SOP integration | T01-T06 merged | Planned |
| P1O6-T08 | Cohesion and research owner | Objective Six research validation and protocol cohesion review | T01-T07 merged | Planned |
| P1O6-T09 | Closeout owner | Closeout, handoff, current-status synchronization, and parent summary | T01-T08 merged or deliberately deferred | Planned |

## Dependency rules

- T01 must merge before any later Objective Six deliverable is created.
- T02 and T03 implement the naming architecture decided in T01; they must not reopen canonical-role decisions without an explicit contract change.
- T04 follows T02 and T03 so `AGENTS.md` points to final canonical entry points.
- T05 follows the repository-instruction refresh so contributor guidance does not conflict with `AGENTS.md`.
- T06 defines the human-review surface after contributor and agent guidance are aligned.
- T07 modernizes issue intake only after the downstream task and review requirements are stable.
- T08 validates the complete protocol before closeout.
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
| Future `templates/CODEX_TASK_TEMPLATE.md` | Compatibility and discoverability entry point | May be created by T03 only as a concise wrapper that directs users to the canonical packet and explains how to instantiate it. It must not duplicate or diverge from packet fields. |

## Review model

### AI-assisted review

AI review may inspect a working-tree diff, identify omissions, recommend tests, flag possible defects, or review a GitHub pull request. Its findings are evidence for the human reviewer.

AI review does not approve its own work and cannot satisfy the human-review gate.

### Human review

Human review requires the project owner or another identified person to inspect the proposed branch or pull-request diff, compare it with the task issue and acceptance criteria, review verification evidence, and record one of these outcomes:

- approved for merge;
- changes requested;
- deferred or rejected.

For a personal repository, human review may be recorded in the PR checklist or a PR comment when GitHub does not provide a meaningful separate self-approval state. The record must still be distinct from AI review output.

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

## Safe claims

- Objective Six has a merged issue-backed architecture, tracker, artifact-contract map, and prompt-built development protocol.
- Root `PROMPT_LOG.md` is a merged non-canonical navigation entry point to the canonical prompt-log sources.
- `records/PROMPT_BUILD_LOG.md` remains the canonical prompt/build-log protocol and index.
- `templates/PROMPT_LOG_ENTRY.md` remains the canonical detailed entry template.
- P1O6-T01 merged through PR #197 and was synchronized through PR #199.
- P1O6-T02 merged through PR #201 and was synchronized through PR #203.
- No data, model, run, map, public-output, tag, Release, or repository-settings work was authorized by T01, T02, or their synchronization tasks.

## Unsupported claims

Do not claim that:

- Objective Six is complete;
- `templates/CODEX_TASK_TEMPLATE.md` or later Objective Six deliverables exist;
- AI review is equivalent to human approval;
- repository settings enforce this protocol;
- BurnLens has started data, model, run, map, or public-demo work;
- BurnLens is official, operational, field-validated, emergency-ready, or agency-endorsed.

## Rejection and defer criteria

Revise or defer work if:

- a later task lacks a merged dependency;
- a proposed compatibility artifact duplicates a canonical source;
- a task lacks an issue, branch, allowed-file scope, acceptance criteria, or handoff;
- research-backed tooling claims cannot be verified from official sources;
- verification is described without named commands or inspection methods;
- AI review is presented as human approval;
- the task would broaden into unauthorized implementation, public-output, release, or settings work.

## Handoff

Proceed to P1O6-T03. T03 must preserve `templates/CODEX_TASK_PACKET.md` as the canonical executable task capsule and may create `templates/CODEX_TASK_TEMPLATE.md` only as the compatibility and discoverability wrapper defined by the merged Objective Six architecture.
