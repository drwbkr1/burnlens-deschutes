# BurnLens Deschutes

BurnLens Deschutes is a computer vision + GEOINT portfolio project focused on experimental wildfire-related screening in Deschutes County, Oregon.

The repository currently documents the controls and future workflow for turning wildfire-relevant imagery, public geospatial layers, and experimental segmentation or baseline outputs into traceable map-ready artifacts.

## Current status

**Phase One / Objective Six is complete as a documented, reviewable repository-control baseline, and parent issue #195 is closed. Phase One / Objective Seven is active but incomplete under parent issue #246. The Phase One acceptance gate has not been completed, and Phase One has not been accepted or released.**

Objective Five is complete and remains the control baseline for versioning, provenance, release control, future run-package planning, artifact registry planning, source-precedence gates, reproducibility QA, research validation, and claim traceability.

Objective Six defines how prompt-assisted repository work is issue-backed, branch-scoped, prompt-logged, test-aware, reviewed by a human, merged, synchronized, and handed off without creating duplicate sources of truth.

Objective Seven defines the evidence model, audits, decision records, remediation routing, exit checklist, and closeout sequence for the Phase One acceptance gate. P1O7-T01 established controls and artifact contracts. P1O7-T02 added the merged gate evidence matrix and defined how future tasks must evaluate evidence; it did not conduct the gate, mark a criterion passed, authorize data work, decide a release identifier or class, create a tag, or publish a GitHub Release.

P1O7-T03 / #257 is active and is being rebuilt under a corrected `burnlens-deschutes`-only scope. P1O7-REM-03A / #259 is the bounded status-routing remediation that must complete before the corrected T03 audit is rebuilt. The abandoned wrong-scope PR #258 is closed unmerged and superseded; its findings are not current evidence.

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
P1O7-T03 / #257 - active; corrected burnlens-deschutes-only audit rebuild pending P1O7-REM-03A
P1O7-REM-03A / #259 - active status-routing remediation on p1o7rem03a
PR #258 - closed unmerged and superseded; wrong-scope findings are not current evidence
Phase One acceptance - not evaluated; no final gate conclusion exists
G01, G02, and G11 - pending corrected P1O7-T03 audit; no verdict assigned by #259
Release identifier and class - not decided
Objective Seven tag - not authorized or created
GitHub Release - not authorized or published
```

Current Objective Seven records:

```text
docs/phase-one/objective-seven/OBJECTIVE_SEVEN_TRACKER.md
docs/phase-one/objective-seven/OBJECTIVE_SEVEN_ARTIFACT_CONTRACTS.md
docs/phase-one/objective-seven/PHASE_1_GATE_EVIDENCE_MATRIX.md
```

The Objective Five baseline tag action remains separate in open issue #194. Objective Seven does not execute, modify, supersede, or close that issue.

The Objective Five baseline identifier remains:

```text
v0.0.5-objective-five-traceability
```

At this status snapshot, that tag has not been created. No GitHub Release has been published. Any later Phase One release path is conditional and not guaranteed.

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

Objective Seven is the active repository workstream. It is evaluating the documented Phase One control baseline through separately authorized evidence, audit, decision, remediation, and closeout tasks. Objective Seven is incomplete, and no Phase One pass, release, implementation-readiness, or Phase Two data authorization claim is currently supported.

Phase Two data work has not begun. No AOI, source-data, label, model, run, map, public-demo, completed claim, Objective Seven tag, or GitHub Release artifact has been created by P1O7-T01, P1O7-T02, or P1O7-REM-03A.

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
P1O7-REM-03A / #259 — Correct Objective Seven active-status routing
```

After #259 is reviewed and merged, P1O7-T03 / #257 must be rebuilt from current `main` under the corrected `burnlens-deschutes`-only scope. G01, G02, and G11 remain pending that corrected audit. PR #258 is superseded and must not be used as evidence.

T03 may inspect and record evidence-backed findings only within its own issue scope. It must not silently remediate evaluated files, conduct later technical or repository-state audits, declare the final Phase One decision, begin Phase Two data work, choose or create a tag, or publish a GitHub Release.

## Public site

The public website lives separately at `burnlensproject.org` and is backed by the `burnlens-site` repository.

This technical repository controls the scope, documentation, versioning, and future CV/GEOINT workflow artifacts. The public site should not make claims that are stronger than the artifacts in this repository support.