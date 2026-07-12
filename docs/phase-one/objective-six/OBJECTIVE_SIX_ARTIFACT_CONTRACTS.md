# Phase One / Objective Six — Artifact Contracts

## Purpose

This file defines Objective Six artifact ownership, dependencies, canonical roles, task contracts, acceptance standards, and defer conditions.

It is an architecture record. It does not authorize a listed task or artifact by itself; authorization comes from the task issue.

## Objective contract

| Field | Requirement |
|---|---|
| Objective | Phase One / Objective Six — Prompt-Built Development Protocol |
| Parent issue | #195 |
| Objective owner | Human project owner |
| Operating unit | One issue, one bounded branch, one reviewable PR per task unless explicitly bundled |
| Default merge posture | Human-reviewed, task-scoped squash merge when permitted and authorized |
| Completion gate | All tasks merged or deliberately deferred; canonical roles stable; research and cohesion review passed; status synchronized |
| Prohibited default scope | Data, AOI, imagery, labels, masks, baselines, models, metrics, runs, maps, screenshots, public demos, public claims, tags, Releases, and repository-settings configuration |

## Canonical artifact map

| Artifact | Canonical responsibility | Routing or compatibility rule |
|---|---|---|
| `docs/workflows/PROMPT_TO_REPO_SOP.md` | Full prompt-to-repository workflow, context tiers, gates, and closeout rules | Other artifacts summarize or route to it and must not conflict |
| `templates/CODEX_TASK_PACKET.md` | Sole executable task capsule | `templates/CODEX_TASK_TEMPLATE.md` is a non-canonical wrapper |
| `records/PROMPT_BUILD_LOG.md` | Prompt/build-log protocol and dated-entry index | `PROMPT_LOG.md` is non-canonical navigation |
| `templates/PROMPT_LOG_ENTRY.md` | Detailed prompt/build-log entry structure | Routers link to it rather than duplicating fields |
| `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md` | Branch, PR, merge, and post-merge baseline | Objective Six adds stricter review and verification requirements through current controls |
| `.github/ISSUE_TEMPLATE/task.yml` | Structured issue-first task intake | It captures authorization inputs but does not replace the canonical packet |
| `.github/PULL_REQUEST_TEMPLATE.md` | Concise PR evidence surface | It routes detailed inspection to the standalone review checklist |
| `docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md` | Detailed human-review and merge-authorization record | AI review remains supplemental |

## Objective Six architecture artifacts

| Artifact | Responsibility | Owner task |
|---|---|---|
| `docs/phase-one/objective-six/OBJECTIVE_SIX_TRACKER.md` | Current objective state, dependencies, task status, gates, and handoff | P1O6-T01 |
| `docs/phase-one/objective-six/OBJECTIVE_SIX_ARTIFACT_CONTRACTS.md` | Artifact ownership and task contracts | P1O6-T01 |
| `docs/phase-one/objective-six/PROMPT_BUILT_DEVELOPMENT_PROTOCOL.md` | Coherent issue-to-merge architecture | P1O6-T01 |
| `PROMPT_LOG.md` | Merged non-canonical prompt-log router | P1O6-T02 |
| `templates/CODEX_TASK_TEMPLATE.md` | Merged non-canonical task-packet wrapper | P1O6-T03 |
| `AGENTS.md` | Repository prompt-assisted agent instructions | P1O6-T04 |
| `CONTRIBUTING.md` | Human-facing contributor guidance | P1O6-T05 |
| `docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md` | Detailed review record | P1O6-T06 |
| `.github/PULL_REQUEST_TEMPLATE.md` | Concise PR intake and evidence | P1O6-T06 |
| `.github/ISSUE_TEMPLATE/task.yml` | Structured task intake | P1O6-T07 |
| `docs/phase-one/objective-six/OBJECTIVE_SIX_RESEARCH_VALIDATION_LOG.md` | Current OpenAI/GitHub claim validation | P1O6-T08 |
| `docs/phase-one/objective-six/OBJECTIVE_SIX_COHESION_REVIEW.md` | Requirement coverage, findings, severity, and remediation disposition | P1O6-T08 |

## Compatibility rules

`PROMPT_LOG.md` and `templates/CODEX_TASK_TEMPLATE.md` are merged compatibility artifacts.

They may:

- identify the canonical file;
- explain when to use it;
- provide a minimal invocation sequence.

They must not become:

- a second protocol or index;
- a second task packet or field schema;
- a status register;
- a transcript archive;
- an independent workflow or approval mechanism.

## Research basis

The architecture was originally researched in P1O6-T01 using official OpenAI and GitHub sources. T08 revalidates current external claims. Later tasks must perform fresh research after branch creation when they depend on current external behavior.

## Task contracts

### P1O6-T01 — Define architecture and artifact contracts

| Field | Contract |
|---|---|
| Owner | Protocol architecture owner |
| Issue / branch | #196 / `p1o6t01b` |
| Primary artifacts | Tracker, artifact contracts, development protocol, README status, prompt log |
| Required decisions | Sequence, ownership, canonical naming, review separation, verification rule |
| Acceptance | Coherent architecture, no duplicate source, research and verification recorded |
| Status / handoff | Merged through PR #197; handoff T02 |

### P1O6-T02 — Create prompt-log entry point

| Field | Contract |
|---|---|
| Owner | Prompt-log navigation owner |
| Primary artifact | `PROMPT_LOG.md` |
| Canonical rule | Protocol/index remains `records/PROMPT_BUILD_LOG.md`; detailed template remains `templates/PROMPT_LOG_ENTRY.md` |
| Acceptance | Root router is concise, links resolve, no parallel protocol/index/transcript store |
| Status / handoff | Merged through PR #201; handoff T03 |

### P1O6-T03 — Create task-template entry point

| Field | Contract |
|---|---|
| Owner | Codex task-interface owner |
| Primary artifact | `templates/CODEX_TASK_TEMPLATE.md` |
| Canonical source | `templates/CODEX_TASK_PACKET.md` |
| Acceptance | Wrapper identifies canonical packet and does not fork its schema |
| Status / handoff | Merged through PR #206; handoff T04 |

### P1O6-T04 — Refresh repository agent instructions

| Field | Contract |
|---|---|
| Owner | Repository-instruction owner |
| Primary artifact | `AGENTS.md` |
| Acceptance | Current, concise, repository-wide, non-duplicative, boundary-preserving |
| Status / handoff | Merged through PR #209; handoff T05 |

### P1O6-T05 — Create contributor guidance

| Field | Contract |
|---|---|
| Owner | Contributor-guidance owner |
| Primary artifact | `CONTRIBUTING.md` |
| Acceptance | Routes humans to canonical controls without independent workflow or promises |
| Status / handoff | Merged through PR #213; handoff T06 |

### P1O6-T06 — Define human review and modernize PR intake

| Field | Contract |
|---|---|
| Owner | Human-review owner |
| Primary artifacts | `PR_REVIEW_CHECKLIST.md`; `.github/PULL_REQUEST_TEMPLATE.md` |
| Acceptance | Author, checks, AI, human outcome, and merge authorization remain distinct; no settings-enforcement claim |
| Status / handoff | Merged through PR #217; handoff T07 |

### P1O6-T07 — Modernize task issue intake

| Field | Contract |
|---|---|
| Owner | Issue-intake owner |
| Primary artifact | `.github/ISSUE_TEMPLATE/task.yml` |
| Acceptance | Valid bounded issue-form intake; no implementation authorized by default |
| Status / handoff | Merged through PR #221; handoff T08 |

### P1O6-T08 — Research validation and protocol cohesion review

| Field | Contract |
|---|---|
| Owner | Cohesion and research owner |
| Task issue / branch | #226 / `p1o6t08b` |
| Primary artifacts | `docs/phase-one/objective-six/OBJECTIVE_SIX_RESEARCH_VALIDATION_LOG.md`; `docs/phase-one/objective-six/OBJECTIVE_SIX_COHESION_REVIEW.md` |
| Dependencies | T01-T07 merged; required remediation merged and revalidated |
| Required decisions | Confirm current tooling claims, canonical links, rule coverage, severity, remediation, safe/unsupported claims |
| Acceptance | External claims source-backed; review surfaces align; no unresolved Critical or High contradiction |
| Defer/reject when | A material contradiction remains or a current claim cannot be verified |
| Handoff | P1O6-T09 only after T08 passes and merges |

### P1O6-T09 — Close out Objective Six

| Field | Contract |
|---|---|
| Owner | Closeout owner |
| Planned primary artifacts | `OBJECTIVE_SIX_CLOSEOUT.md`; `OBJECTIVE_SIX_HANDOFF.md` |
| Dependencies | T01-T08 merged or deliberately deferred with reasons |
| Required decisions | Final state, safe claims, limitations, next authorized workstream, parent close recommendation |
| Acceptance | README, tracker, logs, closeout, handoff, and parent summary agree; human closeout review recorded |
| Defer/reject when | Tasks or findings are unexplained, status conflicts, or evidence is incomplete |

## Cross-task mandatory rules

Every Objective Six task must:

- begin from a task issue;
- use a bounded branch from current `main` unless another base is explicitly authorized;
- preserve an allowed-file list;
- load Tier 0 and selective Tier 1 context;
- justify any Tier 2 use;
- perform fresh research after branch creation when current external claims are made;
- create or update a dated prompt/build log for prompt-assisted file changes;
- report named checks and actual results or task-specific non-applicability;
- diff-check against `main`;
- use a PR closing only its task issue;
- receive recorded human review before merge;
- treat AI review as supplemental;
- synchronize current-status records only when their truth changes;
- avoid rewriting completed-objective records for wording preference;
- preserve data, claims, source-precedence, version, tag, Release, and settings gates.

## No-duplicate-source gate

Reject an artifact when it independently restates canonical rules and can drift from the canonical source.

Routing and compatibility artifacts must remain concise and clearly non-canonical.

## Current handoff

T08 is active. REM-08A aligned canonical prompt-log controls. REM-08B reconciles stale contributor, contract, and architecture wording. After remediation and any required synchronization, T08 must rerun the affected checks.

Do not begin T09 until T08 passes, merges, and current-status truth is synchronized.
