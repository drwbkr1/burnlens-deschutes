# BurnLens Deschutes

BurnLens Deschutes is a computer vision + GEOINT portfolio project focused on experimental wildfire-related screening in Deschutes County, Oregon.

The repository currently documents the controls and future workflow for turning wildfire-relevant imagery, public geospatial layers, and experimental segmentation or baseline outputs into traceable map-ready artifacts.

## Current status

**Phase One / Objective Six is complete as a documented, reviewable repository-control baseline, and parent issue #195 is closed. Phase One / Objective Seven is active but incomplete under parent issue #246. Drew approved `APPROVE — PHASE TWO PLANNING ONLY` on 2026-07-13 through P1O7-T08 / PR #294. Full Phase One completion remains blocked by G10, and data touch remains blocked by F04-A. Phase One has not been accepted as complete or released.**

Objective Five is complete and remains the control baseline for versioning, provenance, release control, future run-package planning, artifact registry planning, source-precedence gates, reproducibility QA, research validation, and claim traceability.

Objective Six defines how prompt-assisted repository work is issue-backed, branch-scoped, prompt-logged, test-aware, reviewed by a human, merged, synchronized, and handed off without creating duplicate sources of truth.

Objective Seven defines the evidence model, audits, decision records, remediation routing, exit checklist, and closeout sequence for the Phase One acceptance gate. P1O7-T01 established controls and artifact contracts. P1O7-T02 added the merged gate evidence matrix and defined how future tasks must evaluate evidence; it did not conduct the gate, mark a criterion passed, authorize data work, decide a release identifier or class, create a tag, or publish a GitHub Release.

P1O7-T03 / #257 completed the corrected `burnlens-deschutes`-only identity, boundary, and active-scope audit through PR #263 and squash merge commit `3d7e6d5a2de7fcc527803ae06d9b746143084207`. Drew reviewed and approved source head `ac39943396ba5ea1c4d28fcd1f9084d38a94cc21` and separately authorized the squash merge. Within the corrected repository-only scope, G01, G02, and G11 received reviewed `meets criterion` / `pass` results. These criterion findings do not make the final Phase One decision. The abandoned wrong-scope PR #258 remains closed unmerged and superseded; its findings are not current evidence.

P1O7-T04 / #269 completed the technical-readiness audit through PR #270 and squash merge commit `d3f05322eb0bf2c9802bba59bd6c3ad2484288f4`. Drew approved reviewed head `a8f84a7226e9bf059b805c2f9dbe0d6bdb8fb50b` and separately authorized squash merge. G03 received reviewed `meets criterion` / `pass`; G04 received reviewed `meets with limitation` / `pass with limitation`; F04-A remains `evidence incomplete` and continues to block data touch. These results support later gate synthesis only. They do not authorize Phase Two work or make the final Phase One decision.

P1O7-T05 / #273 completed the repository-control and live-state audit through PR #274 and squash merge commit `43a776f85ca84749d07d95afd71dda062b505e2c`. Drew approved exact head `e960b73dad99b8f6e7aecd759a3718c8e2b107c4` and separately authorized the squash merge. G06-A and G07 received reviewed `meets criterion`; G05, G06-B, G08, and G09 received reviewed `meets with limitation`; F06-C, G10, and F10-R remain `evidence incomplete`. Live Project status is `inaccessible/unresolved`; complete tag and GitHub Release inventories were inaccessible, and the known proposed Objective Five tag ref did not resolve. These findings do not make the final Phase One decision, authorize Phase Two work, create a Project, or create a tag or GitHub Release.

P1O7-T06 / #277 completed the baseline-identifier and release-class decision through PR #278 and squash merge commit `3f0e158c44e608267cfbba31d21103f99f584123`. Drew approved exact head `7d912920e09a22dff9b90a2104a2112b1a237cc1`, the conditional candidate `v0.0.7-objective-seven-phase-one-baseline`, and the rejection or historical-only treatment of the legacy candidates. P1O7-REM-06A / #279 then resolved T06-F01 through PR #280 and squash merge commit `5e6d0d111dc44eabfb056426c1d1c9bb868456c7`. T06-F01 is accepted with documented limitation for T07 sequencing; complete tag and GitHub Release inventories remain `inaccessible/unresolved`, G10 and F10-R remain incomplete and separate, and successful complete tag enumeration remains mandatory before T10 and parent #246 closure. No tag or GitHub Release was created.

P1O7-T07 / #283 completed the evidence-backed Phase One exit checklist through PR #284 and squash merge commit `69eea57597a27c58d3e9b8ffe2a1b07a8c4826ae`. Drew approved exact head `ce5466b5df97d7bb6f44c3050363b23f1ad448ea` and separately authorized squash merge. The checklist preserves all O1–O11 criteria and the required F04-A, F06-C, and F10-R distinctions. It records full Phase One completion as blocked by G10 and data touch as blocked by F04-A. It is eligible for P1O7-T08 evidence synthesis, but it does not make the Phase One decision or authorize Phase Two work, a tag, a GitHub Release, or public claims.

P1O7-T08 / #289 completed the Phase One decision memo through PR #294 and squash merge commit `69c0b7322f5c2a556f285ad639a8df467494979f`. Drew reviewed exact head `71cdcdae7b987c497d39b002aae7a7b668cd6edd`, recorded `APPROVE — PHASE TWO PLANNING ONLY` on 2026-07-13, and separately authorized squash merge. The decision authorizes bounded, separately issue-backed planning and control work only after synchronization. It does not authorize source access, AOI creation, data download or processing, labels, baselines, models, runs, maps, public claims, a tag, or a GitHub Release. G10 and F04-A remain unresolved blockers for their respective lanes.

Current Objective Six status:

```text
#195 - Phase 1 Objective Six parent — closed as completed
P1O6-T01 / #196 - merged through PR #197; synchronized through PR #199
P1O6-T02 / #200 - merged through PR #201; synchronized through PR #203
P1O6-T03 / #204 - merged through PR #206; synchronized through PR #208
P1O6-T04 / #205 - merged through PR #209; synchronized through PR #211
P1O6-T05 / #212 - merged through PR #213; synchronized through PR #215
P1O6-T06 / #216 - merged through PR #217; synchronized through PR #219
P1O6-T07 / #220 - merged through PR #221; synchronized through PR #225
P1O6-T08 / #226 - merged through PR #235; synchronized through PR #237
P1O6-REM-09A / #238 - merged through PR #240; synchronized through PR #242
P1O6-T09 / #239 - merged through PR #243; issue #239 closed
```

Current Objective Six records:

```text
AGENTS.md
CONTRIBUTING.md
docs/phase-one/objective-six/OBJECTIVE_SIX_TRACKER.md
docs/phase-one/objective-six/OBJECTIVE_SIX_ARTIFACT_CONTRACTS.md
docs/phase-one/objective-six/PROMPT_BUILT_DEVELOPMENT_PROTOCOL.md
docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md
docs/phase-one/objective-six/OBJECTIVE_SIX_RESEARCH_VALIDATION_LOG.md
docs/phase-one/objective-six/OBJECTIVE_SIX_COHESION_REVIEW.md
docs/phase-one/objective-six/OBJECTIVE_SIX_CLOSEOUT.md
docs/phase-one/objective-six/OBJECTIVE_SIX_HANDOFF.md
.github/ISSUE_TEMPLATE/task.yml
.github/PULL_REQUEST_TEMPLATE.md
```

Current Objective Seven status:

```text
#246 - Phase 1 Objective Seven parent — open and protected
P1O7-T01 / #247 - merged through PR #248; synchronized through P1O7-SYNC-01 / #249
P1O7-T02 / #251 - merged through PR #252; synchronized through P1O7-SYNC-02 / #253 and finalized through #255
P1O7-REM-03A / #259 - complete through PR #260; merge commit d1cb6cffa01402627c9e4b208139dc1a87c97552
P1O7-T03 / #257 - merged through PR #263; merge commit 3d7e6d5a2de7fcc527803ae06d9b746143084207; issue closed
P1O7-T04 / #269 - merged through PR #270; merge commit d3f05322eb0bf2c9802bba59bd6c3ad2484288f4; issue closed
P1O7-T05 / #273 - merged through PR #274; merge commit 43a776f85ca84749d07d95afd71dda062b505e2c; issue closed
P1O7-T06 / #277 - merged through PR #278; merge commit 3f0e158c44e608267cfbba31d21103f99f584123; issue closed
P1O7-REM-06A / #279 - merged through PR #280; merge commit 5e6d0d111dc44eabfb056426c1d1c9bb868456c7; issue closed
P1O7-SYNC-06A / #281 - merged through PR #282; final prior synchronization record
P1O7-T07 / #283 - merged through PR #284; merge commit 69eea57597a27c58d3e9b8ffe2a1b07a8c4826ae; issue closed
P1O7-SYNC-07 / #285 - final T07 status synchronization record
P1O7-T08 / #289 - reviewed and merged through PR #294; merge commit 69c0b7322f5c2a556f285ad639a8df467494979f; issue closed
P1O7-SYNC-08 / #296 - current bounded lifecycle synchronization
PR #258 - closed unmerged and superseded; wrong-scope findings are not current evidence
G01, G02, G03, G06-A, G07, and G11 - reviewed meets criterion / pass where applicable
G04, G05, G06-B, G08, and G09 - reviewed meets with limitation / pass with limitation where applicable
F04-A - evidence incomplete; mandatory blocker for data touch and supporting fact for planning-only evaluation
F06-C - evidence incomplete; live Project status inaccessible/unresolved
T06-F01 - accepted with documented limitation for sequencing; complete enumeration still mandatory before T10 and parent closure
G10 - evidence incomplete; mandatory blocker to claiming Phase One complete
F10-R - evidence incomplete; supporting fact only
Phase One decision - APPROVE — PHASE TWO PLANNING ONLY, Drew, 2026-07-13
P1O7-T09 - next task; not started by P1O7-SYNC-08
Release identifier and class - conditional objective-baseline candidate approved; no tag authorized or created
Objective Seven tag - not authorized or created; complete tag inventory remains inaccessible/unresolved
GitHub Release - not recommended for the current documentation/control candidate; complete inventory remains inaccessible/unresolved
```

Current Objective Seven records:

```text
docs/phase-one/objective-seven/OBJECTIVE_SEVEN_TRACKER.md
docs/phase-one/objective-seven/OBJECTIVE_SEVEN_ARTIFACT_CONTRACTS.md
docs/phase-one/objective-seven/PHASE_1_GATE_EVIDENCE_MATRIX.md
docs/phase-one/objective-seven/PHASE_1_SCOPE_AND_BOUNDARY_AUDIT.md
docs/phase-one/objective-seven/PHASE_1_TECHNICAL_READINESS_AUDIT.md
docs/phase-one/objective-seven/PHASE_1_REPOSITORY_CONTROL_AUDIT.md
docs/phase-one/objective-seven/PHASE_1_BASELINE_RELEASE_DECISION.md
docs/phase-one/objective-seven/remediation/P1O7-REM-06A_REMEDIATION_RECORD.md
docs/phase-one/objective-seven/PHASE_1_EXIT_CHECKLIST.md
docs/phase-one/objective-seven/PHASE_1_DECISION_MEMO.md
```

The Objective Five baseline tag action remains separate in open issue #194. Objective Seven does not execute, modify, supersede, or close that issue.

The Objective Five baseline identifier remains:

```text
v0.0.5-objective-five-traceability
```

During T05, that exact proposed tag ref did not resolve. Complete tag and GitHub Release inventories remain inaccessible, so the repository does not claim an empty inventory. The approved Objective Seven candidate is conditional and is not a tag. No Objective Seven tag or GitHub Release is authorized by the current workflow, and any later Phase One release path remains conditional and not guaranteed.

## Prompt-built development architecture

The controlling relationship is:

```text
full workflow reference: docs/workflows/PROMPT_TO_REPO_SOP.md
human contributor guidance: CONTRIBUTING.md
repository agent instructions: AGENTS.md
structured task issue intake: .github/ISSUE_TEMPLATE/task.yml
canonical task capsule: templates/CODEX_TASK_PACKET.md
task template entry point: templates/CODEX_TASK_TEMPLATE.md (non-canonical)
root prompt-log navigation: PROMPT_LOG.md (non-canonical)
canonical prompt-log protocol/index: records/PROMPT_BUILD_LOG.md
canonical prompt-log entry template: templates/PROMPT_LOG_ENTRY.md
Objective Six architecture: docs/phase-one/objective-six/PROMPT_BUILT_DEVELOPMENT_PROTOCOL.md
detailed PR review record: docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md
concise PR intake surface: .github/PULL_REQUEST_TEMPLATE.md
research validation: docs/phase-one/objective-six/OBJECTIVE_SIX_RESEARCH_VALIDATION_LOG.md
protocol cohesion review: docs/phase-one/objective-six/OBJECTIVE_SIX_COHESION_REVIEW.md
closeout decision: docs/phase-one/objective-six/OBJECTIVE_SIX_CLOSEOUT.md
next-workstream handoff: docs/phase-one/objective-six/OBJECTIVE_SIX_HANDOFF.md
current acceptance-gate tracker: docs/phase-one/objective-seven/OBJECTIVE_SEVEN_TRACKER.md
current acceptance-gate contracts: docs/phase-one/objective-seven/OBJECTIVE_SEVEN_ARTIFACT_CONTRACTS.md
current acceptance-gate evidence matrix: docs/phase-one/objective-seven/PHASE_1_GATE_EVIDENCE_MATRIX.md
current scope-and-boundary audit: docs/phase-one/objective-seven/PHASE_1_SCOPE_AND_BOUNDARY_AUDIT.md
current technical-readiness audit: docs/phase-one/objective-seven/PHASE_1_TECHNICAL_READINESS_AUDIT.md
current repository-control audit: docs/phase-one/objective-seven/PHASE_1_REPOSITORY_CONTROL_AUDIT.md
current baseline/release decision: docs/phase-one/objective-seven/PHASE_1_BASELINE_RELEASE_DECISION.md
current T06 inventory remediation: docs/phase-one/objective-seven/remediation/P1O7-REM-06A_REMEDIATION_RECORD.md
current Phase One exit checklist: docs/phase-one/objective-seven/PHASE_1_EXIT_CHECKLIST.md
current Phase One decision memo: docs/phase-one/objective-seven/PHASE_1_DECISION_MEMO.md
```

Root `CONTRIBUTING.md` provides the merged human-facing workflow for issue-first work, compact branches, allowed-file scope, prompt logging, verification, task-scoped pull requests, mandatory human review, solo-maintainer review evidence, policy-versus-enforcement distinctions, boundary escalation, and handoff.

Root `AGENTS.md` routes prompt-assisted agents to the merged issue-first workflow, the active Objective Seven workstream, current status controls, verification, human-review, boundary, and release controls while retaining completed Objective Six records as the documented repository-control baseline.

`.github/ISSUE_TEMPLATE/task.yml` provides the merged generic task-intake surface for bounded task identity, scope, selective context loading, research, prompt logging, verification, human review, task-only closure, parent protection, and handoff. It does not replace the canonical task capsule.

`docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md` provides the merged five-stage review record for author self-audit, actual checks, optional AI-assisted findings, mandatory human inspection, and separate merge authorization.

`.github/PULL_REQUEST_TEMPLATE.md` records concise linkage, scope, research, verification, security, boundary, review-separation, close-keyword, and handoff evidence while routing detailed inspection to the standalone checklist.

`templates/CODEX_TASK_TEMPLATE.md` is a compatibility and discoverability wrapper only. It directs users to instantiate `templates/CODEX_TASK_PACKET.md`, which remains the canonical executable task capsule.

Root `PROMPT_LOG.md` is a navigation and compatibility entry point only. It does not replace the canonical protocol, entry index, or detailed entry template.

The T08 research and cohesion records validate current OpenAI/GitHub claims, map the Objective Six rules to their controlling surfaces, and record resolved remediation and remaining limitations. T08 passed with zero unresolved Critical, High, or Medium findings.

The T09 closeout and handoff distinguish the documented repository-control protocol from future executed reliability. The closeout does not claim implementation, data, model, run, map, demo, operational, field-validation, platform-enforcement, tag, or Release status.

Human review is distinct from AI-assisted review. AI may draft, test, inspect, and recommend changes, but a human must inspect the proposed diff and record the merge decision.

Every task must report named tests or checks and actual results, or state a task-specific reason that a check does not apply.

## Objective Five governing records

```text
docs/phase-one/objective-five/CURRENT_STATUS_RECONCILIATION.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_TRACKER.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_ARTIFACT_CONTRACTS.md
docs/phase-one/objective-five/VERSION_TAXONOMY.md
docs/phase-one/objective-five/RELEASE_CONTROL.md
docs/phase-one/objective-five/PROVENANCE_TRACEABILITY_SPEC.md
docs/phase-one/objective-five/RUN_PACKAGE_CONTRACT.md
docs/phase-one/objective-five/ARTIFACT_REGISTRY_SPEC.md
docs/phase-one/objective-five/CLAIM_TRACEABILITY_PROTOCOL.md
docs/phase-one/objective-five/SOURCE_PRECEDENCE_RELEASE_GATE.md
docs/phase-one/objective-five/REPRODUCIBILITY_CHECKLIST.md
docs/phase-one/objective-five/RELEASE_QA_CHECKLIST.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_RESEARCH_VALIDATION_LOG.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_CLAIMS_CHECK.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_CLOSEOUT.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_HANDOFF.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_RELEASE_NOTE.md
VERSIONING.md
templates/RELEASE_NOTE_TEMPLATE.md
templates/TRACEABILITY_RECORD_TEMPLATE.md
templates/RUN_MANIFEST_TEMPLATE.json
templates/CLAIM_EVIDENCE_LINK_TEMPLATE.md
records/PROMPT_BUILD_LOG.md
```

## Current work boundary

BurnLens remains an experimental, non-operational portfolio project. Official sources govern. Future public-facing output must follow `docs/objective-one/USE_BOUNDARIES.md`, `docs/objective-one/SOURCE_PRECEDENCE.md`, and Objective Five release, source-precedence, reproducibility, QA, and claim-traceability controls.

Objective Seven is the active repository workstream. Drew's reviewed T08 decision authorizes bounded Phase Two planning and control work only under separate issues after synchronization. Objective Seven remains incomplete because G10 is unresolved, and F04-A continues to prohibit all source and data touch. No Phase One completion, release, implementation-readiness, public-claim, or data-execution claim is supported.

Phase Two data work has not begun. No AOI, source-data, label, model, run, map, public-demo, completed claim, Objective Seven tag, or GitHub Release artifact was created by P1O7-T01 through P1O7-T08.

Objective Seven does not authorize repository settings, branch protection, rulesets, Actions, labels, milestones, Projects, implementation work, or public-output work unless a later task explicitly allows the named change.

## Locked computer vision task

BurnLens Deschutes' first computer vision task is experimental binary semantic segmentation for wildfire-relevant screening.

The primary target is active-fire / hotspot-informed binary fire mask. The fallback target is burn-scar binary mask. The fallback may be used only if later feasibility work shows the primary target is not defensible for the portfolio model. Changing to the fallback requires a documented decision update.

## Core workflow

```text
imagery → preprocessing → segmentation or baseline mask → raster output → vector polygons → map overlay → exposure-style summary → documented run package
```

This chain is a future workflow contract. It does not mean those stages have already been implemented.

## Source separation rule

Future BurnLens artifacts must keep these categories separate:

- official/reference sources;
- reference-derived labels;
- baseline outputs;
- model outputs;
- map overlays;
- portfolio interpretations.

## Objective Six completion claim

> BurnLens Deschutes has a documented, reviewable prompt-built development protocol connecting issue-backed authorization, bounded task capsules and branches, selective context loading, prompt/build logging, named verification, task-scoped pull requests, mandatory human review distinct from AI-assisted review, controlled merge authorization, conditional status synchronization, and handoff.

This claim concerns documented repository controls. It does not mean the future CV/GEOINT workflow has been executed or proven reliable.

## Current bounded workstream

The active workstream is:

```text
Phase One / Objective Seven — Phase One acceptance gate
```

Current bounded work is:

```text
P1O7-T09 — Close out Objective Seven and prepare the reviewed baseline candidate (next; not started by P1O7-SYNC-08)
```

P1O7-T08 is reviewed and merged through PR #294, and P1O7-SYNC-08 / #296 synchronizes that repository truth. T09 must begin only under its own issue and task capsule. It must preserve the planning-only decision, keep G10 and F04-A unresolved, keep F06-C and F10-R as supporting facts, prepare an exact reviewed baseline candidate without creating a tag, and avoid authorizing source access, data touch, public claims, or a GitHub Release.

## Public site

The public website lives separately at `burnlensproject.org` and is backed by the `burnlens-site` repository.

This technical repository controls the scope, documentation, versioning, and future CV/GEOINT workflow artifacts. The public site should not make claims that are stronger than the artifacts in this repository support.
