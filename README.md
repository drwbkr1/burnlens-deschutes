# BurnLens Deschutes

BurnLens Deschutes is a computer vision + GEOINT portfolio project focused on experimental wildfire-related screening in Deschutes County, Oregon.

The repository documents the controls and future workflow for turning wildfire-relevant imagery, public geospatial layers, and experimental segmentation or baseline outputs into traceable map-ready artifacts.

## Current status

**Phase One / Objective Six is complete as a documented, reviewable repository-control baseline, and parent issue #195 is closed. Phase One / Objective Seven remains active and incomplete under parent issue #246. Drew recorded `APPROVE — PHASE TWO PLANNING ONLY` on 2026-07-13 through P1O7-T08 / PR #294. Full Phase One completion remains blocked by G10, and every data-touch action remains blocked by F04-A. Phase One has not been accepted as complete or released.**

P1O7-T09 / issue #298 is active on branch `p1o7t09b`. The branch contains a review-ready Objective Seven closeout, handoff, Phase One documentation/control release-note candidate, reproducibility review, release-QA review, and synchronized status/log records.

T09 has no pull request, human outcome, merge authorization, or merge commit yet. The candidate’s exact eligible `main` target is therefore unresolved and must be recorded through a bounded post-merge synchronization after T09 is reviewed and merged.

The approved conditional candidate remains:

```text
v0.0.7-objective-seven-phase-one-baseline
```

It is not a Git tag. No Objective Seven tag is authorized or created. No GitHub Release is authorized or published, and a GitHub Release is not recommended for the current documentation/control candidate.

## Phase One decision and readiness lanes

| Lane | Current posture | Consequence |
|---|---|---|
| Phase Two planning | Authorized under separate issue-backed planning/control tasks | The first permitted Phase Two action is creation of a Phase Two planning parent and tracker. |
| Source/AOI intake planning | Documentation planning only | Future records and task order may be planned; no source access or AOI geometry may occur. |
| Data touch | Not authorized | F04-A remains `evidence incomplete`. |
| Labels, baselines, models, runs, metrics, maps, and outputs | Not authorized | No executed technical readiness exists. |
| Public claims and publication | Not authorized | Claim evidence, source-precedence review, and release QA remain mandatory. |
| Objective Seven tag | Not authorized | G10 remains incomplete; #292 is preparation only. |
| GitHub Release | Not authorized and not recommended | Documentation-only repository note is the selected release posture. |

## Objective Seven evidence summary

| Evidence class | Reviewed result |
|---|---|
| G01, G02, G03, G06-A, G07, G11 | `meets criterion` |
| G04, G05, G06-B, G08, G09 | `meets with limitation` |
| F04-A | `evidence incomplete`; blocks every data-touch action |
| F06-C | `evidence incomplete`; supporting live-Project fact only |
| G10 | `evidence incomplete`; blocks full Phase One completion and parent #246 closure |
| F10-R | `evidence incomplete`; supporting GitHub Release fact only |

Complete Project, tag, and GitHub Release inventories remain `inaccessible/unresolved` where stated in the reviewed records. Exact-ref failures are targeted observations and are not evidence of an empty inventory.

## Objective Seven lifecycle

```text
#246 - Phase 1 Objective Seven parent — open and protected
P1O7-T01 / #247 - merged through PR #248; synchronized through #249 / PR #250
P1O7-T02 / #251 - merged through PR #252; synchronized through #253 and finalization #255
P1O7-REM-03A / #259 - merged through PR #260
P1O7-T03 / #257 - merged through PR #263
P1O7-T04 / #269 - merged through PR #270
P1O7-T05 / #273 - merged through PR #274
P1O7-T06 / #277 - merged through PR #278
P1O7-REM-06A / #279 - merged through PR #280; synchronized through #281 / PR #282
P1O7-T07 / #283 - merged through PR #284; synchronized through #285 / PR #286 and #287 / PR #288
P1O7-T08 / #289 - reviewed and merged through PR #294 at 69c0b7322f5c2a556f285ad639a8df467494979f
P1O7-SYNC-08 / #296 - merged through PR #297 at 23d57ab96071e21068ab7c02ae970b2968e10c04
P1O7-T09 / #298 - review-ready branch build on p1o7t09b; PR, human review, and merge pending
P1O7-T10-PREP / #292 - open and blocked; complete tag inventory/readiness only; no tag authorization
P2O1-T01 / #293 - open and blocked; before-data intake preparation only; no source-access authorization
#194 - separate Objective Five tag action; open, unchanged, and outside Objective Seven
```

Duplicate issue #295 is not an active authorization. PR #258 is closed unmerged and superseded; its wrong-repository findings are not current evidence.

## Current Objective Seven records

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
docs/phase-one/objective-seven/OBJECTIVE_SEVEN_CLOSEOUT.md
docs/phase-one/objective-seven/OBJECTIVE_SEVEN_HANDOFF.md
docs/phase-one/objective-seven/PHASE_1_RELEASE_NOTE.md
docs/phase-one/objective-seven/OBJECTIVE_SEVEN_REPRODUCIBILITY_REVIEW.md
docs/phase-one/objective-seven/OBJECTIVE_SEVEN_RELEASE_QA_REVIEW.md
```

The five T09 primary artifacts are branch candidates until human review and merge. The T07 checklist and T08 decision memo retain their reviewed source-task roles and were not rewritten during the T09 build stage.

## T09 candidate and review posture

The T09 package prepares a conditional documentation/control objective-baseline candidate only.

| Item | Build-stage state |
|---|---|
| Closeout and handoff | Review-ready on `p1o7t09b` |
| Phase One release note | Review-ready repository candidate; not publication |
| Reproducibility review | Complete with decision `blocked` |
| Release-QA review | Complete with decision `blocked` |
| PR and reviewed head | Pending |
| Human review | Pending |
| Merge authorization | Pending |
| Eligible `main` target | Pending post-merge synchronization |
| Tag | Not created or authorized |
| GitHub Release | Not published, not authorized, not recommended |

The reviews are blocked from release action because the PR, human gate, merge, synchronized target, complete tag inventory, and exact tag authorization do not exist yet. The branch may proceed to human review without weakening those blockers.

## Required next sequence

1. Human-review the complete `p1o7t09b` diff under issue #298.
2. Open a task-scoped PR using `Closes #298` only.
3. Record one human outcome and separate exact-head merge authorization.
4. After merge, run a bounded synchronization that records the exact eligible `main` target.
5. Create the Phase Two planning parent/tracker as the first permitted Phase Two action.
6. Keep #293 blocked until that parent adopts the planning-only boundary.
7. Keep #292 blocked until T09 is merged and the exact synchronized target exists.
8. Permit a future exact T10 issue only if #292 establishes readiness and Drew authorizes the exact tag action.
9. Do not publish a GitHub Release for the current candidate.

Parent #246 cannot close through T09 alone. G10 resolution, post-tag verification, final synchronization, a parent summary, and explicit human parent-close authorization remain required.

## Prompt-built development architecture

```text
full workflow reference: docs/workflows/PROMPT_TO_REPO_SOP.md
human contributor guidance: CONTRIBUTING.md
repository agent instructions: AGENTS.md
structured task issue intake: .github/ISSUE_TEMPLATE/task.yml
canonical task capsule: templates/CODEX_TASK_PACKET.md
non-canonical task wrapper: templates/CODEX_TASK_TEMPLATE.md
root prompt-log navigation: PROMPT_LOG.md
canonical prompt-log protocol/index: records/PROMPT_BUILD_LOG.md
canonical prompt-log entry template: templates/PROMPT_LOG_ENTRY.md
Objective Six protocol: docs/phase-one/objective-six/PROMPT_BUILT_DEVELOPMENT_PROTOCOL.md
detailed human review record: docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md
concise PR intake: .github/PULL_REQUEST_TEMPLATE.md
```

Issue authorization, task capsule, branch scope, prompt logging, named checks, human review, and merge authorization remain distinct. Written policy does not prove that GitHub branch protection, rulesets, required approvals, CI, or other enforcement is configured.

## Objective Five governing controls

Objective Five remains the control baseline for future work:

```text
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
templates/RELEASE_NOTE_TEMPLATE.md
records/PROMPT_BUILD_LOG.md
```

## Current work boundary

BurnLens remains an experimental, non-operational portfolio project. Official sources govern.

Phase Two data work has not begun. No source query, AOI geometry, source data, label, baseline, model, run, metric, map, report, screenshot, demo, deployment, completed public claim, Objective Seven tag, or GitHub Release was created by Objective Seven or T09.

Required warning for future BurnLens-derived outputs:

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

## Locked computer-vision task

BurnLens Deschutes’ first computer-vision task remains experimental binary semantic segmentation for wildfire-relevant screening.

- Primary target: active-fire / hotspot-informed binary fire mask.
- Fallback target: burn-scar binary mask, only after a documented future feasibility decision.
- Required future chain:

```text
imagery → preprocessing → segmentation or baseline mask → raster output → vector polygons → map overlay → exposure-style summary → documented run package
```

This is a future workflow contract, not evidence that implementation or outputs exist.

Future artifacts must keep official/reference sources, reference-derived labels, baseline outputs, model outputs, map overlays, and portfolio interpretations separate.

## Known navigation limitation

`AGENTS.md` retains an obsolete T03-active sentence, and some completed-objective artifacts retain historical status headers. Current README, the Objective Seven tracker, the decision memo, and merged lifecycle records govern current truth. Those stale files were outside issue #298’s allowed scope and were not changed.

## Public site

The public website lives separately at `burnlensproject.org` and is backed by the `burnlens-site` repository.

This technical repository controls project scope, documentation, versioning, and future CV/GEOINT workflow artifacts. T09 does not publish or change the site, and public copy must never make claims stronger than the reviewed repository evidence supports.