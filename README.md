# BurnLens Deschutes

BurnLens Deschutes is a computer vision + GEOINT portfolio project focused on experimental wildfire-related screening in Deschutes County, Oregon.

The repository documents the controls and future workflow for turning wildfire-relevant imagery, public geospatial layers, and experimental segmentation or baseline outputs into traceable map-ready artifacts.

## Current status

**Phase One / Objective Six is complete as a documented, reviewable repository-control baseline, and parent issue #195 is closed. Phase One / Objective Seven remains active and incomplete under parent issue #246. Drew recorded `APPROVE — PHASE TWO PLANNING ONLY` on 2026-07-13 through P1O7-T08 / PR #294. Full Phase One completion remains blocked by G10, and every data-touch action remains blocked by F04-A. Phase One has not been accepted as complete or released.**

P1O7-T09 / issue #298 was human-reviewed and squash-merged through PR #299 at `d7ad8f063239a61e9212e6eac562deffa50a7a88`. P1O7-SYNC-09 / issue #300 then synchronized T09 lifecycle truth through PR #301 at:

```text
10caebb3d61ff622dc6dfe8809a63886089eba4e
```

P1O7-SYNC-09F / issue #302 designates that reviewed synchronization merge as the exact eligible synchronized `main` target for the conditional Phase One documentation/control baseline candidate. The designation becomes final when the #302 record is reviewed and merged.

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
| Objective Seven tag | Not authorized | G10 remains incomplete; #292 is readiness preparation only. |
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
P1O7-T09 / #298 - reviewed and merged through PR #299 at d7ad8f063239a61e9212e6eac562deffa50a7a88
P1O7-SYNC-09 / #300 - reviewed and merged through PR #301 at 10caebb3d61ff622dc6dfe8809a63886089eba4e
P1O7-SYNC-09F / #302 - exact-target finalization record
P1O7-T10-PREP / #292 - complete tag inventory/readiness only; no tag authorization
P2O1-T01 / #293 - blocked before-data intake preparation only; no source-access authorization
#194 - separate Objective Five tag action; open, unchanged, and outside Objective Seven
```

Duplicate issue #295 is not an active authorization. PR #258 is closed unmerged and superseded; its wrong-repository findings are not current evidence.

## Candidate target and remaining tag gate

The exact eligible synchronized `main` target is:

```text
10caebb3d61ff622dc6dfe8809a63886089eba4e
```

This target contains the reviewed T09 closeout package and the merged SYNC-09 lifecycle/status corrections. Recording the target does not create a tag, satisfy G10, prove an empty or collision-free tag inventory, or authorize tag creation.

After P1O7-SYNC-09F merges, issue #292 may begin its complete authenticated tag inventory and readiness review. #292 cannot create a tag. A future exact P1O7-T10 issue may be considered only if #292 records readiness and Drew separately authorizes the exact tag name, target, method, and verification.

The T09 reproducibility and release-QA decisions remain `blocked` for tag or release action until complete inventory/readiness evidence and exact T10 authorization exist.

## Required next sequence

1. Review and merge P1O7-SYNC-09F / #302.
2. Allow #292 to begin complete authenticated tag inventory and readiness review; no tag creation.
3. Create the Phase Two planning parent/tracker as the first permitted Phase Two action.
4. Keep #293 blocked until that parent adopts the planning-only boundary.
5. Permit a future exact T10 issue only if #292 establishes readiness and Drew authorizes the exact tag action.
6. Do not publish a GitHub Release for the current candidate.

Parent #246 remains open. G10 resolution, authorized tag creation if supported, post-tag verification, final status synchronization, a parent summary, and explicit human parent-close authorization remain required.

## Prompt-built development architecture

```text
full workflow reference: docs/workflows/PROMPT_TO_REPO_SOP.md
human contributor guidance: CONTRIBUTING.md
repository agent instructions: AGENTS.md
structured task issue intake: .github/ISSUE_TEMPLATE/task.yml
canonical task capsule: templates/CODEX_TASK_PACKET.md
root prompt-log navigation: PROMPT_LOG.md
canonical prompt-log protocol/index: records/PROMPT_BUILD_LOG.md
canonical prompt-log entry template: templates/PROMPT_LOG_ENTRY.md
Objective Six protocol: docs/phase-one/objective-six/PROMPT_BUILT_DEVELOPMENT_PROTOCOL.md
detailed human review record: docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md
concise PR intake: .github/PULL_REQUEST_TEMPLATE.md
```

## Current work boundary

BurnLens remains an experimental, non-operational portfolio project. Official sources govern. Future public-facing output must follow `docs/objective-one/USE_BOUNDARIES.md`, `docs/objective-one/SOURCE_PRECEDENCE.md`, and Objective Five release, source-precedence, reproducibility, QA, and claim-traceability controls.

Phase Two data work has not begun. No source query, AOI geometry, source data, label, model, run, map, public demo, completed public claim, Objective Seven tag, or GitHub Release artifact has been created by Objective Seven work.

Objective Seven does not authorize repository settings, branch protection, rulesets, Actions, labels, milestones, Projects, implementation work, or public-output work unless a later task explicitly allows the named change.

## Public site

The public website lives separately at `burnlensproject.org` and is backed by the `burnlens-site` repository.

This technical repository controls the scope, documentation, versioning, and future CV/GEOINT workflow artifacts. The public site should not make claims stronger than the artifacts in this repository support.