# BurnLens Deschutes — Build Roadmap

## Purpose

This document is the durable, repository-level roadmap for the six-phase BurnLens Deschutes build.

It gives Codex and reviewers enough whole-project context to choose the next bounded checkpoint without turning the project into a rigid feature checklist. It records the current best sequence, the outcome each phase must prove, the dependency gates between phases, and the owner's explicit stop conditions.

## Roadmap authority

This roadmap is a **versioned planning hypothesis**, not a rigid checklist. `docs/governance/BURNLENS_EXECUTION_GOAL.md` controls execution authority.

- The roadmap defines intended phase outcomes and dependencies.
- The phase objective documents expand those outcomes without changing their meaning.
- GitHub issues, branches, allowed-file contracts, and pull requests bound actual work.
- The execution goal overrides stale roadmap, issue, handoff, prompt, and repository-control language.
- `docs/governance/CHECKPOINT_POLICY.md` controls evidence-unit, milestone, exception, and release cadence.
- A later phase becomes active when its predecessor evidence and issue-backed gate are satisfied; routine activation does not require separate owner approval.

Codex may reorder, split, merge, defer, or replace tasks and checkpoints when verified evidence supports a better route. Codex must document the rationale and preserve the phase objective, project promise, use boundaries, source precedence, and traceability requirements.

A material change to a phase objective requires explicit human approval and a coordinated update to this roadmap and the affected phase document.

## Project promise

BurnLens Deschutes is an experimental, portfolio-first computer vision and GEOINT project that demonstrates how versioned wildfire-related imagery, a bounded segmentation model or justified baseline, and geospatial overlays can be turned into transparent planning-style screening artifacts.

The portfolio must prove:

1. a runnable analytical workflow;
2. transparent methods and provenance;
3. useful map-ready and planning-style outputs;
4. reproducibility, traceability, and graceful failure handling;
5. honest comparison between model and non-model evidence;
6. clear communication of limitations and prohibited uses;
7. prompt-assisted development that remains issue-backed, reviewable, and human-governed.

Every artifact should improve the tool, make the method more transparent, strengthen the evidence, or make the portfolio case more defensible.

## Non-negotiable boundaries

BurnLens is not official wildfire information and is not emergency guidance.

Use this warning, or a tighter equivalent, on future public-facing CV outputs:

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

BurnLens must not be presented as field-validated, agency-endorsed, operational, emergency-ready, production-stable, or suitable for evacuation, routing, tactical, suppression, incident-command, property-level, insurance, legal, or regulatory decisions.

Official and authoritative sources always govern over BurnLens-derived outputs.

## Global traceability rule

No public map, screenshot, summary, report, model output, application view, run artifact, website card, or portfolio claim is portfolio-ready unless it traces to the applicable repository commit, app or objective baseline version, AOI version, source records, dataset version, label schema version, baseline or model version, immutable run ID, processing timestamp, warning flags, limitations, and source-precedence note.

Traceability does not by itself make publication responsible. Claims review, release QA, resolved licensing, actual-output inspection, and production verification still apply.

## Status vocabulary

| Status | Meaning |
|---|---|
| `active — incomplete` | Authorized work exists, but the phase gate has not passed. |
| `proposed — blocked` | The phase objective is documented, but predecessor or authorization gates prevent execution. |
| `planning authorized — data blocked` | Planning may proceed, but data touch is blocked by unresolved before-data evidence. |
| `accepted for planning only` | The phase supports successor planning but does not claim an implementation or release baseline. |
| `accepted with caveats` | The phase gate passed with documented limitations that must carry forward. |
| `accepted` | The phase gate passed and the successor may be considered for authorization. |
| `remediate` | A correctable blocker prevents phase acceptance. |
| `stopped` | The phase cannot responsibly continue under the current objective. |

## Current phase overview

| Phase | Name | Canonical objective summary | Current status | Primary dependency | Detailed objectives |
|---|---|---|---|---|---|
| 1 | Scope, technical contracts, repository controls, and acceptance gate | Establish the documented project identity, bounded CV task, source-feasibility posture, repository operating system, version/provenance/claims controls, and prompt-built workflow, then make an evidence-backed Phase One acceptance decision before implementation begins. | **accepted and versioned for Phase Two planning; no analytical release** | P1O7-T08 / PR #294 records `APPROVE — PHASE TWO PLANNING ONLY`; #290 / PR #291 shipped the controlling goal and roadmap at `v0.0.8-execution-goal-baseline`. | [Phase One objectives](../phases/phase-01/PHASE_01_OBJECTIVES.md) |
| 2 | Data acquisition, labels, baselines, and dataset versioning | Build a complete, traceable data foundation for one bounded Deschutes County experiment, including authorized sources and AOI, reproducible preprocessing, defensible positive/negative/unknown labels, leakage-resistant splits, non-model baselines, dataset QA, and a model-readiness decision. | **active - incomplete; official fallback source-gate defer candidate** | Verified v0.45 retains five complete prototype-label events and Petes Lake's material defer. P2O4-T34 / issue #532 compares the official McKenzie HUC8 route with Milli, retains both as blocked/deferred, selects neither, and authorizes no provider bytes. BurnLens 0.46.0 is a release candidate pending one PR, fresh-main verification, and tag peel. The accepted label set does not change. | [Phase Two objectives](../phases/phase-02/PHASE_02_OBJECTIVES.md) |
| 3 | CV model development, controlled evaluation, and model versioning | Build and evaluate one bounded U-Net-style segmentation model against the accepted Phase Two baselines, then package either a defensible model or a transparent baseline-only decision with complete lineage, error analysis, and limitations. | **proposed — blocked** | Accepted Phase Two dataset package, locked split, baseline evidence, and target decision. | [Phase Three objectives](../phases/phase-03/PHASE_03_OBJECTIVES.md) |
| 4 | Inference, geospatial productization, interactive integration, and run versioning | Convert the accepted model or baseline into a reproducible inference-to-GEOINT workflow that preserves georeferencing, creates valid raster/vector artifacts, performs deterministic overlay analysis, presents an accessible evidence interface, and packages every execution as an immutable run. | **proposed — blocked** | Accepted Phase Three model package or approved Phase Two baseline-only path. | [Phase Four objectives](../phases/phase-04/PHASE_04_OBJECTIVES.md) |
| 5 | Reliability, QA, reproducibility, security, and release control | Harden the integrated workflow into a tested, reproducible, secure, accessible, performant, and reversible release candidate without expanding analytical scope. | **proposed — blocked** | Accepted Phase Four integrated run package and interface candidate. | [Phase Five objectives](../phases/phase-05/PHASE_05_OBJECTIVES.md) |
| 6 | Portfolio publication, public release, communication, and closeout | Publish one coherent, traceable portfolio release whose demo, case study, repository, presentation, licensing, citation, archive, and maintenance posture all refer to the same accepted evidence and limitations. | **proposed — blocked** | Accepted Phase Five release candidate, verified public claims, resolved licensing, and a repository-owned release surface. | [Phase Six objectives](../phases/phase-06/PHASE_06_OBJECTIVES.md) |

## Phase One — scope and control baseline

**Objective:** Establish the documented project identity, bounded CV task, source-feasibility posture, repository operating system, version/provenance/claims controls, and prompt-built workflow, then make an evidence-backed Phase One acceptance decision before implementation begins.

**What this phase must prove:** BurnLens can enter implementation with a coherent promise, bounded task, traceable operating rules, safe claims, and an explicit gate rather than relying on conversation context or informal assumptions.

**Current status:** Objectives One through Six are complete as documentation/control baselines. P1O7-T08 / PR #294 accepted the evidence for Phase Two planning only. PR #291 and `v0.0.8-execution-goal-baseline` version that control baseline. BL-GOV-002 / issue #400 / PR #401 has closed the obsolete Phase One GitHub backlog so old issue and PR restrictions remain historical evidence rather than apparently active authority. No Phase One analytical release exists. Phase Two metadata, route, access-integrity, final-AOI, intake-transaction, authenticated source/reference inspection, complete observation geometry, and burn-scar target-decision evidence are shipped through `v0.6.0-burn-scar-target-baseline`. Authorized credentials were exercised without committing raw source bytes or secret material.

## Phase Two — data foundation

**Objective:** Build a complete, traceable data foundation for one bounded Deschutes County experiment, including authorized sources and AOI, reproducible preprocessing, defensible positive/negative/unknown labels, leakage-resistant splits, non-model baselines, dataset QA, and a model-readiness decision.

**What this phase must prove:** The proposed CV task is supported by data and labels that are reproducible, independently split, honestly uncertain, and strong enough to justify—or reject—model training.

**Current status:** P2O1-T02 through P2O3-T01 ship exact route/access, AOI, source/reference, target, optical-pair, and registration evidence. Twenty-four original owner-approved prototype points remain immutable audit evidence. Verified P2O4-T19 through P2O4-T31 establish eight balanced prototype regions across Darlene, McKay, Tepee, and Green Ridge plus the complete pre-response Grandview path. Verified P2O4-T32 locks the exact Grandview response before reveal and admits one burned and one background core after every gate, yielding `owner-approved-prototype-region-labels-v0.3.0`: ten balanced regions, 236 core pixels / 9.44 ha, and 431 excluded unknown-ring pixels across five complete events. P2O4-T33 / issue #521 / PR #527 plus exception issue #528 / PR #529 ship verified BurnLens 0.45.0 while preserving that exact accepted set and Petes Lake's material-defer disposition. Restricted thresholded Tepee BARC remains private and unused. No accepted dataset, split, baseline, model, or deployed analytical application exists.

**Gate outcome:** Green Ridge and Grandview have passed their complete optical/reference/background/proposal/review/intake paths. P2O4-T33 / issue #521 / PR #527 groups the complete Petes Lake chain under `checkpoint-policy-v0.1.0`. U01/U02 pass; planned U03 retains a snow-dominated rendered failure; its exact 19 October replacement passes native quality with three spatial exclusions; and U04 passes exact MTBS request/delivery/custody/native-contract evidence while accepting zero reference pixels. U05 r001 retains a fixed local qualified-field validator failure. R002 and final authorized r003 each promote seven ordered NWI assets before the Data Source pre-count route fails at `PROVIDER_OPEN`; r002's cause is unknowable, while r003's bounded diagnostic records HTTP 500 without attributing cause. R003 is terminal and no r004 is authorized. U05 scientific fitness cannot run from a partial package, so production U06-U10 remain unexecuted/deferred and Petes Lake does not become event six. U11 execution is complete with disposition `defer`. Exception issue #528 / PR #529 passes U04; reviewed head `9cc07d1767c9912b18c459794dc541417b2b13d2` merges at verified checkpoint `d65c24f59ce0c854ba230aa977eaf718d881d952`, and annotated tag object `0b466402cdc36b0eacfff97d29dd16fe2a88868a` peels exactly to that merge. BurnLens 0.45.0 is verified; it changes software/tooling, not the accepted label set, and creates no GitHub Release or deployment. Objective Five's class/unknown completeness, source-regime replication, never-tuned transfer, dominance, leakage, baseline, and split gates remain authoritative and closed.

## Phase Three — model evidence

**Objective:** Build and evaluate one bounded U-Net-style segmentation model against the accepted Phase Two baselines, then package either a defensible model or a transparent baseline-only decision with complete lineage, error analysis, and limitations.

**What this phase must prove:** A model adds measurable, inspectable, reproducible value beyond the strongest relevant non-model baseline without hiding uncertainty, leakage, scene-level failures, or target limitations.

**Gate outcome:** integrate the frozen model, integrate with caveats, return for remediation, or proceed baseline-only.

## Phase Four — CV-to-GEOINT product

**Objective:** Convert the accepted model or baseline into a reproducible inference-to-GEOINT workflow that preserves georeferencing, creates valid raster/vector artifacts, performs deterministic overlay analysis, presents an accessible evidence interface, and packages every execution as an immutable run.

**What this phase must prove:** BurnLens can turn analytical output into a transparent, map-ready, planning-style screening package without blending model evidence with official information or converting descriptive spatial relationships into operational recommendations.

**Gate outcome:** accept an integrated model workflow, accept with caveats, accept a baseline-first interface, remediate, or stop integration.

## Phase Five — reliability and release candidate

**Objective:** Harden the integrated workflow into a tested, reproducible, secure, accessible, performant, and reversible release candidate without expanding analytical scope.

**What this phase must prove:** The complete system can reproduce its evidence, detect and communicate failures, preserve lineage, withstand expected defects, and roll back safely.

**Gate outcome:** accept a release candidate, accept with caveats, accept a baseline-first candidate, remediate, roll back, or stop release work.

## Phase Six — publication and closeout

**Objective:** Publish one coherent, traceable portfolio release whose demo, case study, repository, presentation, licensing, citation, archive, and maintenance posture all refer to the same accepted evidence and limitations.

**What this phase must prove:** A technical reviewer can understand, inspect, reproduce, evaluate, cite, and responsibly interpret BurnLens without relying on private project context or unsupported claims.

**Gate outcome:** publish a model-centered release, publish with caveats, publish a baseline-first release, publish a technical case study without interactive output, enter maintenance, archive, or withdraw.

## Dependency and gate chain

```text
Phase One accepted for Phase Two planning
→ source/licensing and before-data gate resolved
→ Phase Two data-ready
→ Phase Three model or baseline decision accepted
→ Phase Four integrated run accepted
→ Phase Five release candidate accepted
→ Phase Six publication verified
```

A predecessor gate may approve a narrower fallback path. The roadmap does not require a model-centered release when the evidence supports a stronger baseline-first portfolio story.

## Codex execution authority

Within the controlling goal and an issue-backed checkpoint, Codex may:

- inspect current repository and rendered outputs;
- choose the highest-leverage bounded weakness;
- propose and decompose issues and checkpoints;
- reorder task sequence when dependencies allow;
- select bounded implementation options;
- stop a run or phase when evidence fails a gate;
- recommend remediation, fallback, or scope reduction;
- maintain roadmap status, changelog, prompt/build logs, devlog, versions, and handoffs;
- create issues and branches; version, commit, push, open and merge pull requests; deploy; roll back; and verify checkpoints after quality gates pass.

Codex must not silently:

- change the project promise, target audience, core CV task, phase objective, use boundaries, source precedence, or traceability standard;
- touch data before the before-data gate is satisfied;
- change a locked test split, canonical run, model threshold, public metric, or analytical output after its controlling phase freezes it;
- proceed with unresolved source licensing or terms;
- spend money, add paid services or secrets, alter ownership, access, or public-sharing status, or take an irreversible action without explicit approval;
- imply official, operational, emergency-ready, field-validated, or endorsed status;
- publish anything it cannot verify.

## Roadmap revision protocol

A roadmap revision must identify:

1. the verified evidence that exposed the weakness;
2. the affected phase objective, dependency, or gate;
3. whether the change is task-level, checkpoint-level, or objective-level;
4. the artifacts and claims affected;
5. the proposed replacement route;
6. the boundaries preserved;
7. whether an owner stop condition is triggered.

Evidence-unit, milestone, exception, and other checkpoint-level changes may be made through issue-backed work under `docs/governance/CHECKPOINT_POLICY.md`. Objective-level changes require explicit owner approval and updates to both this roadmap and the affected phase objective document in the same pull request.

## Current next checkpoint

The controlling execution goal remains `v0.0.8-execution-goal-baseline` at `22a8d88435cb8d5b900a398b7482c3b7277d2ee6`, amended operationally by BL-GOV-003 and `checkpoint-policy-v0.1.0`. P2O4-T10B is immutable historical reconciliation, not the current acceptance route. Verified v0.31 through v0.45 establish ten balanced prototype regions across five events, complete the Green Ridge and Grandview paths, and close Petes Lake with disposition `defer` without treating it as event six. P2O4-T34 then proves that neither the McKenzie HUC8 route nor Milli currently clears the source gate.

The next prospective sequence is:

1. **Ship the bounded official-fallback defer:** Merge and verify P2O4-T34 without acquiring either route. Then register a fresh source route only after the unresolved rights and evidence failures can be addressed under a new issue contract.
2. **Dataset-fitness milestone:** rerun the full sufficiency evaluator across all accepted evidence and decide pass, remediation, fallback, deferral, or stop.
3. **Dataset-and-split milestone, conditional:** create a versioned dataset and leakage-resistant split only if fitness passes every class, unknown, regime, transfer, dominance, and separation gate.
4. **Baseline milestone, conditional:** establish the strongest justified non-model baseline only from the accepted locked dataset and split.

Do not create a dataset, split, or baseline merely when the sixth event arrives.

## Required reading order for long-running Codex work

1. `docs/governance/BURNLENS_EXECUTION_GOAL.md`
2. `docs/governance/CHECKPOINT_POLICY.md`
3. `AGENTS.md`
4. `docs/status/PHASE_STATUS.md`
5. this roadmap
6. the active phase objective document
7. the active issue and branch contract
8. only the workflow and archival evidence relevant to the next milestone or evidence unit

## Consistency rule

The roadmap contains the canonical short objective for each phase. Each phase document expands its objective without changing its meaning. Material changes must update both in the same reviewed pull request.
