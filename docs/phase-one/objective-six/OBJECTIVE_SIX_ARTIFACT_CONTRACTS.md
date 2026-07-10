# Phase One / Objective Six — Artifact Contracts

## Purpose

This file defines the planned Objective Six task artifacts, ownership, dependencies, canonical roles, allowed change classes, acceptance standards, and defer conditions.

It is an architecture record. It does not create or authorize the later deliverables listed as future paths.

## Objective contract

| Field | Requirement |
|---|---|
| Objective | Phase One / Objective Six — Prompt-Built Development Protocol |
| Parent issue | #195 |
| First task | P1O6-T01 / #196 |
| Objective owner | Human project owner |
| Operating unit | One task issue, one bounded branch, one reviewable PR per task unless explicitly bundled |
| Default merge posture | Human-reviewed, task-scoped squash merge when repository settings allow it |
| Completion gate | All tasks merged or deliberately deferred; canonical roles stable; human-review and test-reporting rules implemented; current status synchronized |
| Prohibited scope | Data, AOI, imagery, labels, masks, baselines, models, metrics, runs, maps, screenshots, public demos, public claims, tags, Releases, and repository-settings configuration |

## Canonical artifact map

### Existing canonical sources

| Artifact | Canonical responsibility | Compatibility rule |
|---|---|---|
| `docs/workflows/PROMPT_TO_REPO_SOP.md` | Full prompt-to-repository reference workflow | Later docs may summarize or route to it, but must not restate a conflicting workflow. |
| `templates/CODEX_TASK_PACKET.md` | Executable task capsule for prompt-assisted work | Future `templates/CODEX_TASK_TEMPLATE.md` is a thin entry point only. |
| `records/PROMPT_BUILD_LOG.md` | Prompt/build-log protocol and entry index | Future root `PROMPT_LOG.md` is navigation only. |
| `templates/PROMPT_LOG_ENTRY.md` | Detailed task-level prompt/build-log entry structure | Compatibility artifacts link to it instead of duplicating fields. |
| `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md` | Branch, PR, review, merge, and post-merge workflow baseline | Objective Six may add stricter human-review and test-reporting rules but must state the relationship. |
| `.github/ISSUE_TEMPLATE/task.yml` | Current task issue intake form | T07 may modernize it after the Objective Six protocol is stable. |
| `.github/PULL_REQUEST_TEMPLATE.md` | Current PR checklist | T06 may modernize it after contributor and agent guidance are aligned. |

### Objective Six current artifacts

| Artifact | Responsibility | Owner task |
|---|---|---|
| `docs/phase-one/objective-six/OBJECTIVE_SIX_TRACKER.md` | Current objective status, dependencies, task states, gates, and handoff | P1O6-T01 |
| `docs/phase-one/objective-six/OBJECTIVE_SIX_ARTIFACT_CONTRACTS.md` | Planned artifact map and task-level contracts | P1O6-T01 |
| `docs/phase-one/objective-six/PROMPT_BUILT_DEVELOPMENT_PROTOCOL.md` | Coherent issue-to-merge prompt-assisted development architecture | P1O6-T01 |
| `records/prompt-build-log/2026-07-09-p1o6-t01.md` | Task-level traceability record | P1O6-T01 |

### Future compatibility artifacts

| Future artifact | Planned role | Must not become |
|---|---|---|
| `PROMPT_LOG.md` | Root-level navigation entry point to `records/PROMPT_BUILD_LOG.md`, `templates/PROMPT_LOG_ENTRY.md`, and dated entries | A second protocol, a second entry index, or a transcript store |
| `templates/CODEX_TASK_TEMPLATE.md` | Discoverability wrapper that directs users to instantiate `templates/CODEX_TASK_PACKET.md` | A divergent task schema or replacement packet |

## Research basis for the architecture

Research was performed after branch creation on 2026-07-09 using official sources.

| Claim ID | Official source | Support | Architecture decision |
|---|---|---|---|
| P1O6-T01-R01 | OpenAI, Custom instructions with AGENTS.md — https://developers.openai.com/codex/guides/agents-md | Codex builds a layered instruction chain from global and project `AGENTS.md` or override files, with more specific directory guidance later in the chain. | Keep repository instructions centralized and avoid duplicating operating rules across competing files. |
| P1O6-T01-R02 | OpenAI, Prompting — https://developers.openai.com/codex/prompting | OpenAI examples attach explicit constraints and verification, ask for commands and results, support local or PR review, and require human iteration after drafts. | Require bounded prompts, named verification, actual results, and explicit human review after AI-assisted work. |
| P1O6-T01-R03 | GitHub, Linking a pull request to an issue — https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue | Supported keywords in a PR targeting the default branch can link and close issues on merge. | Use `Closes #TASK_ISSUE` for the task issue only and never the parent from ordinary task PRs. |
| P1O6-T01-R04 | GitHub, About pull request reviews — https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews | GitHub reviews support comment, approve, and request-changes outcomes; administrators may require approvals. | Record a human review outcome distinct from AI review, without claiming settings enforce it unless configured later. |
| P1O6-T01-R05 | GitHub, About merge methods — https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github | Squash and merge combines topic-branch commits into one commit when enabled. | Preserve squash merge as the preferred clean-history method, subject to repository settings and human authorization. |

## Task contracts

### P1O6-T01 — Define architecture and artifact contracts

| Field | Contract |
|---|---|
| Owner | Protocol architecture owner |
| Issue | #196 |
| Branch | `p1o6t01b` |
| Current artifacts | `OBJECTIVE_SIX_TRACKER.md`; `OBJECTIVE_SIX_ARTIFACT_CONTRACTS.md`; `PROMPT_BUILT_DEVELOPMENT_PROTOCOL.md`; `README.md`; task prompt log; prompt-log index |
| Dependencies | Merged SOP, Objective Five handoff, existing workflow and logging artifacts |
| Required research | Current OpenAI Codex instruction/prompting behavior and current GitHub issue/PR/review/merge behavior |
| Required decisions | Task sequence, artifact ownership, canonical naming, human-versus-AI review, tests-or-non-applicability rule, README status |
| Acceptance | Architecture is complete, no duplicate source is planned, only allowed files change, research and verification are recorded, human review remains pending until Prompt 3 |
| Defer/reject when | Research cannot support a tooling claim; a proposed path duplicates an existing canonical source; scope expands into later deliverables or implementation |
| Handoff | P1O6-T02 |

### P1O6-T02 — Create prompt-log entry point and strengthen traceability

| Field | Contract |
|---|---|
| Owner | Prompt-log navigation owner |
| Future primary artifact | `PROMPT_LOG.md` |
| Potential adjacent artifacts | `records/PROMPT_BUILD_LOG.md`; task prompt log; README only if repository navigation truth changes |
| Dependency | P1O6-T01 merged |
| Canonical rule | `records/PROMPT_BUILD_LOG.md` remains the protocol/index; `templates/PROMPT_LOG_ENTRY.md` remains the detailed entry template |
| Required decision | Define the smallest useful root navigation surface without copying the protocol or entry index |
| Acceptance | Root file clearly routes users to canonical records; no parallel log or transcript store exists; links resolve |
| Defer/reject when | The proposed root file repeats the index, creates different required fields, or invites raw transcript storage |
| Handoff | P1O6-T03 |

### P1O6-T03 — Create Codex task template entry point

| Field | Contract |
|---|---|
| Owner | Codex task-interface owner |
| Future primary artifact | `templates/CODEX_TASK_TEMPLATE.md` |
| Canonical source | `templates/CODEX_TASK_PACKET.md` |
| Dependency | P1O6-T01 merged; T02 naming relationships available |
| Required decision | Define a concise compatibility wrapper and instantiation guidance without forking packet fields |
| Acceptance | The template points to the packet, explains canonical status, preserves task issue/branch/scope/research/verification/handoff fields, and introduces no conflicting workflow |
| Defer/reject when | It becomes a second full packet or omits required SOP gates |
| Handoff | P1O6-T04 |

### P1O6-T04 — Refresh repository agent instructions

| Field | Contract |
|---|---|
| Owner | Repository-instruction owner |
| Future primary artifact | `AGENTS.md` |
| Dependencies | T01-T03 merged |
| Required research | Recheck current OpenAI `AGENTS.md` discovery behavior if the official documentation changed materially |
| Required decisions | Replace stale current-phase language; route to canonical SOP, task packet, prompt-log sources, human-review rule, and tests rule |
| Acceptance | Instructions are current, concise, repository-wide, non-duplicative, and preserve all BurnLens boundaries |
| Defer/reject when | The edit conflicts with nested instruction precedence, repeats whole protocols, or authorizes implementation |
| Handoff | P1O6-T05 |

### P1O6-T05 — Create contributor guidance

| Field | Contract |
|---|---|
| Owner | Contributor-guidance owner |
| Future primary artifact | `CONTRIBUTING.md` |
| Dependencies | T01-T04 merged |
| Required decisions | Explain issue intake, branch use, allowed scope, tests/checks, prompt logging, PR review, human approval, and boundary escalation for human contributors |
| Acceptance | Guidance routes to canonical sources and does not restate them inconsistently |
| Defer/reject when | It implies outside contribution rights, support commitments, or implementation authorization not present in the repo |
| Handoff | P1O6-T06 |

### P1O6-T06 — Define human review checklist and modernize PR intake

| Field | Contract |
|---|---|
| Owner | Human-review owner |
| Future primary artifacts | `docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md`; `.github/PULL_REQUEST_TEMPLATE.md` |
| Dependencies | T01-T05 merged |
| Required research | Revalidate GitHub review states and PR-template behavior only as needed |
| Required decisions | Record AI review separately; require human diff inspection; require tests/checks or non-applicability; preserve task-only close keyword |
| Acceptance | PR template and checklist agree; human review outcome is explicit; no settings enforcement is claimed |
| Defer/reject when | AI approval can satisfy the gate, the parent issue can be auto-closed, or verification evidence is optional |
| Handoff | P1O6-T07 |

### P1O6-T07 — Modernize task issue intake

| Field | Contract |
|---|---|
| Owner | Issue-intake owner |
| Future primary artifact | `.github/ISSUE_TEMPLATE/task.yml` |
| Dependencies | T01-T06 merged |
| Required research | Revalidate GitHub issue-form syntax and supported fields before editing |
| Required decisions | Integrate SOP tiering, allowed files, forbidden work, research, tests/checks, human review, close keyword, and handoff fields |
| Acceptance | Valid YAML; issue form creates one bounded task contract; no implementation is authorized by default |
| Defer/reject when | Syntax cannot be validated or fields create conflicting canonical rules |
| Handoff | P1O6-T08 |

### P1O6-T08 — Research validation and protocol cohesion review

| Field | Contract |
|---|---|
| Owner | Cohesion and research owner |
| Future primary artifacts | `docs/phase-one/objective-six/OBJECTIVE_SIX_RESEARCH_VALIDATION.md`; `docs/phase-one/objective-six/OBJECTIVE_SIX_COHESION_REVIEW.md` |
| Dependencies | T01-T07 merged |
| Required decisions | Confirm every current tooling claim, resolve contradictions, verify canonical links, and classify safe/caveated/unsupported protocol claims |
| Acceptance | No unresolved source-of-truth conflict; all official-source claims are current; review surfaces align |
| Defer/reject when | A material contradiction remains or a current claim cannot be verified |
| Handoff | P1O6-T09 |

### P1O6-T09 — Close out Objective Six and synchronize status

| Field | Contract |
|---|---|
| Owner | Closeout owner |
| Future primary artifacts | `docs/phase-one/objective-six/OBJECTIVE_SIX_CLOSEOUT.md`; `docs/phase-one/objective-six/OBJECTIVE_SIX_HANDOFF.md` |
| Potential adjacent artifacts | `OBJECTIVE_SIX_TRACKER.md`; `README.md`; `records/PROMPT_BUILD_LOG.md`; task prompt log; parent issue comment |
| Dependencies | T01-T08 merged or deliberately deferred with reasons |
| Required decisions | Final objective state, safe claims, unresolved limitations, next authorized workstream, parent close recommendation |
| Acceptance | Current status is consistent; parent summary exists; no unsupported claim or unauthorized work occurred; human closeout review is recorded |
| Defer/reject when | Any task is unexplained, current-status records conflict, or acceptance evidence is incomplete |
| Handoff | Next objective or Phase Two task explicitly selected by the human owner |

## Cross-task mandatory rules

Every Objective Six task must:

- begin from a task issue;
- use a compact branch from current `main` unless an explicit dependency requires otherwise;
- preserve an allowed-file list;
- perform fresh research after branch creation when current tooling claims are made;
- create or update a task prompt/build log for prompt-assisted file changes;
- report named tests/checks and actual results, or document task-specific non-applicability;
- diff-check against `main`;
- use a PR that closes only its task issue;
- receive recorded human review before merge;
- treat AI review as supplemental;
- update current-status artifacts only when their truth changes;
- avoid rewriting completed objective records.

## No-duplicate-source gate

A future artifact is rejected when it independently restates canonical rules and can drift from the canonical source.

Compatibility artifacts must be concise routers. They may identify the canonical path, explain when to use it, and provide a minimal invocation example. They may not maintain separate required-field lists, task indexes, status registers, or workflow definitions.

## Handoff

P1O6-T02 should implement only the prompt-log navigation relationship defined here. It must not modify the Codex template relationship, `AGENTS.md`, issue or PR templates, contributor guidance, repository settings, or any implementation/public-output artifact.