# Phase One Decision Memo

## Status

| Field | Current state |
|---|---|
| Task | P1O7-T08 — Create the Phase One decision memo |
| Task issue | #289 — closed through PR #294 |
| Parent issue | #246 — open and protected |
| Repository | `drwbkr1/burnlens-deschutes` |
| Branch / base | `p1o7t08b` / `main` at `8084cbed12046cee5424307c412e164bdd3d688d` |
| Evidence package | P1O7-T07 exit checklist, reviewed and merged through PR #284 at `69eea57597a27c58d3e9b8ffe2a1b07a8c4826ae` |
| Reviewed head | `71cdcdae7b987c497d39b002aae7a7b668cd6edd` |
| Pull request / merge | #294 / `69c0b7322f5c2a556f285ad639a8df467494979f` |
| Memo state | Human-owned decision reviewed and squash-merged |
| Human decision owner | Drew |
| Human decision date | 2026-07-13 |
| Full Phase One completion | Blocked by G10 |
| Phase Two data execution | Prohibited; blocked by F04-A and the before-data gate |
| Tag action | Not authorized or performed |
| GitHub Release action | Not authorized or performed |

## Decision

```text
APPROVE — PHASE TWO PLANNING ONLY
```

Drew reviewed the evidence-backed recommendation and recorded this human-owned Phase One decision on 2026-07-13. Drew approved exact head `71cdcdae7b987c497d39b002aae7a7b668cd6edd`, separately authorized squash merge for that exact head, and PR #294 merged at `69c0b7322f5c2a556f285ad639a8df467494979f`.

The decision authorizes a bounded planning lane only. It does not declare full Phase One complete, does not satisfy G10, and does not authorize source access, AOI creation, data download, data processing, labels, masks, baselines, models, runs, maps, public outputs, a tag, or a GitHub Release.

## Decision basis

The reviewed Phase One exit checklist preserves every original O1–O11 criterion and the required F04-A, F06-C, and F10-R distinctions. The evidence supports a coherent planning baseline:

- G01, G02, G03, G06-A, G07, and G11 meet their reviewed criteria;
- G04, G05, G06-B, G08, and G09 meet with recorded non-blocking limitations;
- no mandatory blocker applies to the narrow planning lane;
- G10 remains incomplete and blocks a full Phase One completion claim;
- F04-A remains incomplete and blocks every data-touch action;
- F06-C and F10-R remain supporting incomplete facts and are not promoted into new mandatory criteria.

The checklist therefore supports a bounded planning decision while requiring the project to preserve the difference between planning readiness, data-touch readiness, and executed technical readiness.

## Decision scope

### Work authorized by this decision

After P1O7-SYNC-08 makes current repository truth coherent, the following planning and control work may be proposed under separate issues:

1. complete P1O7-T09 closeout, handoff, and reviewed baseline-candidate preparation;
2. create the Phase Two planning parent issue and tracker;
3. define Phase Two objectives, task sequence, dependencies, acceptance gates, stop rules, and handoff conditions;
4. plan source/AOI intake tasks and the order in which required records would be instantiated;
5. prepare no-data repository documentation for future source, access, terms, AOI, CRS, provenance, registry, source-precedence, and use-boundary reviews;
6. create exact task issues, task capsules, branch names, file scopes, research plans, verification plans, and review gates for later work;
7. reconcile planning dependencies with the current Phase One closeout and release-control sequence.

Authorization is limited to issue-backed planning and control artifacts. Every future task remains subject to its own allowed-file contract, research requirement, verification plan, human review, and separate merge authorization.

### Immediate next repository task

```text
P1O7-T09 — Close out Objective Seven and prepare the reviewed baseline candidate
```

T09 may begin only under its own task issue after P1O7-SYNC-08 merges. This memo does not start T09 or Phase Two work.

## Work that remains prohibited

This decision does not authorize any of the following:

- accessing, querying for acquisition, downloading, retaining, or processing source data or imagery;
- selecting or creating an AOI geometry or AOI data file;
- creating source-derived records that imply an access, terms, format, CRS, provenance, or suitability review actually occurred;
- creating labels, masks, datasets, baselines, model inputs, model code, training runs, inference runs, metrics, maps, reports, screenshots, demos, deployments, or public outputs;
- changing repository settings, CI, Actions, branch protection, rulesets, Projects, labels, or milestones;
- approving a public claim or publishing public-facing release language;
- creating, moving, retargeting, annotating, signing, pushing, or deleting a tag;
- creating, editing, or publishing a GitHub Release or release asset;
- modifying, executing, closing, superseding, absorbing, or retargeting issue #194;
- claiming Phase One is complete, released, operational, official, field-validated, agency-endorsed, emergency-ready, production-ready, or suitable for evacuation, routing, tactical, or incident-command use.

A future task may authorize one exact controlled action only after its required records exist and its own issue names that action explicitly.

## Readiness-lane decision

| Readiness lane | Decision posture | Consequence |
|---|---|---|
| Phase Two planning | Authorized after status synchronization and separate issue authorization | Planning and control records may be created; no source or data action may occur. |
| Source/AOI intake planning | Authorized as documentation planning only | Future intake tasks and record requirements may be specified, but no source access, AOI geometry, download, or source-specific execution may occur. |
| Data touch | Not authorized | F04-A remains incomplete; the SOP before-data gate must be satisfied for one named action. |
| Labels, baselines, models, runs, metrics, maps, and outputs | Not authorized | No executed technical readiness exists. |
| Public claims | Not authorized | Claim evidence, use-boundary, source-precedence, and release-QA controls remain mandatory. |
| Objective baseline tag | Not authorized | G10 remains incomplete; later T09/T10, complete enumeration, QA, exact target authorization, creation, and verification remain required. |
| GitHub Release | Not authorized and not recommended for the current documentation/control candidate | T06 rejects this release class for the current candidate; F10-R remains a separate supporting fact. |

## Unresolved criteria, facts, and limitations

### G10 — first release tag exists

- **State:** `evidence incomplete`.
- **Class:** mandatory blocker to full Phase One completion and parent #246 closure.
- **Current evidence:** the exact Phase One candidate ref did not resolve during the T08 build recheck; complete tag enumeration remains `inaccessible/unresolved` through the connected GitHub action set.
- **Consequence:** the project must not claim Phase One complete or released.
- **Required future action:** after T09 closeout identifies the exact synchronized target, issue #292 may establish complete inventory and T10 readiness. A new exact T10 issue may create one tag only if the readiness record supports it and Drew explicitly authorizes the exact name, target SHA, method, and post-action verification.
- **Owner:** Drew as human decision and controlled-action owner; the future T10 issue must identify the executing agent and exact authorization.

Issue #292 is preparation only. It does not authorize tag creation.

### F04-A — authorization to touch data

- **State:** `evidence incomplete`.
- **Class:** mandatory blocker to data access, acquisition, AOI creation, preprocessing, and derived-data work.
- **Current evidence:** no exact data action and no complete source/access/terms/AOI/format/CRS/provenance/registry review package exists.
- **Consequence:** planning permission cannot be converted into data permission.
- **Required future action:** after an authorized Phase Two planning parent exists, issue #293 may instantiate the before-data intake package for one exact future Sentinel-2 metadata-only action. A separate exact action issue remains mandatory before any query or source access.
- **Owner:** the future Phase Two parent and exact intake-task owner, subject to Drew’s authorization.

Issue #293 is preparation only. It does not authorize a source query, AOI creation, download, or processing.

### F06-C — live GitHub Project state

- **State:** `evidence incomplete`; `inaccessible/unresolved`.
- **Class:** supporting fact only.
- **Current evidence:** the connected GitHub action catalog exposes no complete Project enumeration action.
- **Consequence:** no existence or absence claim is made. This does not block the planning lane.
- **Required future action:** reverify only when a later issue makes live Project state material. Do not create or change a Project without exact authorization.

### F10-R — GitHub Release exists

- **State:** `evidence incomplete`; complete inventory `inaccessible/unresolved`.
- **Class:** supporting controlled-action fact only.
- **Current evidence:** the connected GitHub action catalog exposes no complete GitHub Release enumeration action.
- **Consequence:** no existence or absence claim is made. A GitHub Release is not required for the current approved documentation/control release posture.
- **Required future action:** none for the present candidate. Reconsider only through a separately authorized T11 with new value justification.

### Non-blocking limitations carried from reviewed criteria

| Criterion | Limitation | Consequence and owner |
|---|---|---|
| G04 | No exact source, item, time window, access method, terms result, AOI, CRS result, or instantiated provenance record exists. | Future Phase Two intake issues must create and review those records before data touch. |
| G05 | Identified active-routing or navigation wording remains stale in some surfaces. | Navigation debt only; remediate under a separate exact-scope issue if it becomes material. |
| G06-B | The Project-board specification exists, but historical status wording and live configuration evidence remain limited. | Do not represent specification as configured enforcement; reverify only when material. |
| G08 | The prompt-built workflow is usable but some active-routing wording remains stale. | Continue using the current issue/capsule/branch/log/check/review/merge workflow; separate remediation may correct stale routing. |
| G09 | Core documentation classes exist, with navigation and historical-status limitations. | Recheck canonical navigation and status during T09 and any release QA. |

These limitations are not waived. They are carried with owners and consequences and may not be silently upgraded into passing evidence for a broader lane.

## Baseline-tag status

The approved conditional decision candidate remains:

```text
v0.0.7-objective-seven-phase-one-baseline
```

Its status is unchanged:

- it uses the existing objective-baseline identifier class;
- it is an approved decision candidate only;
- it is not a Git tag;
- it does not satisfy G10;
- its exact ref did not resolve during the T08 build recheck;
- that targeted failure does not prove the tag inventory is empty;
- complete tag enumeration remains `inaccessible/unresolved` through the connected action set;
- successful complete enumeration remains mandatory before T10, tag creation, and parent #246 closure;
- no alternate identifier may be silently substituted.

Issue #194 remains open, separate, unchanged, and limited to the Objective Five candidate `v0.0.5-objective-five-traceability` at its historical target. T08 does not execute, modify, close, absorb, supersede, or retarget that issue. The exact Objective Five ref also did not resolve during the T08 build recheck, but the targeted result is not a complete inventory.

## GitHub Release status

T06’s reviewed release-class decision remains controlling for the present documentation/control candidate:

- use a conditional objective-baseline tag plus a repository baseline-note or release-note document if later gates support it;
- do not publish a GitHub Release for this candidate;
- no deployable app, package, data, model, run, report, map, demo, or release asset exists in the Phase One baseline;
- complete GitHub Release inventory remains `inaccessible/unresolved` through the connected action set;
- no existence or absence claim is made;
- T11 remains conditional and is not recommended from the current evidence.

A repository note, tag, and GitHub Release are separate artifacts and must never be represented as interchangeable.

## Source-precedence and use-boundary posture

Official sources govern over every BurnLens-derived artifact. BurnLens remains an experimental computer-vision and GEOINT portfolio project for technical demonstration and planning-style screening only.

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

No BurnLens output may override county, state, federal, fire-service, emergency-management, hazard, evacuation, transportation, or incident information. No version, decision memo, tag candidate, future tag, repository note, or release object may be used as evidence of operational readiness, official authority, field validation, agency endorsement, emergency readiness, production stability, or decision authority.

## Required remediation and future controlled actions

| Action | Owner | Satisfaction evidence | Current state / consequence |
|---|---|---|---|
| Record the human decision and actual date for T08 | Drew | Decision record and PR review | **Complete:** planning-only decision recorded 2026-07-13. |
| Complete T08 review and separate merge authorization | Drew | Exact-head review and separate authorization | **Complete:** PR #294 reviewed and squash-merged. |
| Synchronize T08 lifecycle truth | P1O7-SYNC-08 / #296 | Reviewed six-file synchronization | Required before T09 starts. |
| Complete T09 closeout, handoff, and baseline-note preparation | Future T09 issue owner; Drew approves | Reviewed T09 artifacts, synchronized current status, exact included/excluded scope | No baseline target or T10 readiness until complete. |
| Complete tag enumeration and release/reproducibility QA | #292 and future T10 owner; Drew authorizes | Complete inventory, exact reviewed target, QA results, no collision, exact action authorization | G10 remains incomplete; no tag or parent closure. |
| Satisfy the before-data gate for one named action | #293 and future exact action owner; Drew authorizes | Source/access/terms/AOI/CRS/provenance/registry/boundary records and exact task authorization | No source access or data touch. |
| Reconcile stale routing only if material | Separate remediation owner | Exact-scope issue, corrected paths, review and merge evidence | Non-blocking navigation limitation remains visible. |

No remediation is hidden inside this memo. Every file or live-platform change requires its own authorization when it falls outside T08’s four-file scope.

## Human decision record

| Field | Final record |
|---|---|
| Decision owner | Drew |
| Decision date | 2026-07-13 |
| Review target | `71cdcdae7b987c497d39b002aae7a7b668cd6edd` |
| Human outcome | **Approve — Phase Two planning only** |
| Pull request | #294 |
| Merge authorization | Separate exact-head squash authorization recorded on PR #294 |
| Merge commit | `69c0b7322f5c2a556f285ad639a8df467494979f` |
| Blocking review item | None |

The author self-audit and any AI-assisted review are supplemental evidence only. They do not substitute for the recorded human decision or separate merge authorization.

## Handoff

After P1O7-SYNC-08 / #296 is reviewed and merged:

1. proceed to P1O7-T09 under its own issue;
2. preserve G10 as incomplete until a separately authorized tag action succeeds and is verified;
3. preserve F04-A as the data-touch blocker;
4. prepare the reviewed Phase One baseline candidate and exact included/excluded documentation scope;
5. create a separate Phase Two planning parent only within the planning lane authorized by this decision;
6. do not begin source access or data execution until a later exact task satisfies the before-data gate.

Parent #246 remains open. It cannot close through T08 or T09 alone while G10 remains incomplete and post-tag verification and explicit parent-close authorization remain outstanding.

## Do not carry forward

Do not carry forward:

- duplicate issue #295 as an active synchronization authorization;
- PR #258 or its wrong-repository findings;
- exact-ref failures as proof of an empty inventory;
- the conditional candidate as a created tag;
- the former pending human decision/date;
- the planning-only decision as data-touch or executed technical readiness;
- F06-C or F10-R as newly invented mandatory criteria;
- a repository baseline note as a GitHub Release;
- author or AI self-review as Drew’s decision;
- any implication that Phase One is complete, Phase Two data work has begun, or BurnLens is operational or official.
