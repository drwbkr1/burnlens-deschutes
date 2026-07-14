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
| 2 | Data acquisition, labels, baselines, and dataset versioning | Build a complete, traceable data foundation for one bounded Deschutes County experiment, including authorized sources and AOI, reproducible preprocessing, defensible positive/negative/unknown labels, leakage-resistant splits, non-model baselines, dataset QA, and a model-readiness decision. | **active — incomplete; final AOI shipped; paired imagery intake blocked on owner-approved CDSE and Earthdata credentials** | P2O2-T01 / #321 / PR #322 ships a 108 km2 final modeling AOI from one cited public NIFC reference at `v0.2.0-aoi-baseline` and verifies county/source metadata coverage. Pixel-level source fitness remains blocked. | [Phase Two objectives](../phases/phase-02/PHASE_02_OBJECTIVES.md) |
| 3 | CV model development, controlled evaluation, and model versioning | Build and evaluate one bounded U-Net-style segmentation model against the accepted Phase Two baselines, then package either a defensible model or a transparent baseline-only decision with complete lineage, error analysis, and limitations. | **proposed — blocked** | Accepted Phase Two dataset package, locked split, baseline evidence, and target decision. | [Phase Three objectives](../phases/phase-03/PHASE_03_OBJECTIVES.md) |
| 4 | Inference, geospatial productization, interactive integration, and run versioning | Convert the accepted model or baseline into a reproducible inference-to-GEOINT workflow that preserves georeferencing, creates valid raster/vector artifacts, performs deterministic overlay analysis, presents an accessible evidence interface, and packages every execution as an immutable run. | **proposed — blocked** | Accepted Phase Three model package or approved Phase Two baseline-only path. | [Phase Four objectives](../phases/phase-04/PHASE_04_OBJECTIVES.md) |
| 5 | Reliability, QA, reproducibility, security, and release control | Harden the integrated workflow into a tested, reproducible, secure, accessible, performant, and reversible release candidate without expanding analytical scope. | **proposed — blocked** | Accepted Phase Four integrated run package and interface candidate. | [Phase Five objectives](../phases/phase-05/PHASE_05_OBJECTIVES.md) |
| 6 | Portfolio publication, public release, communication, and closeout | Publish one coherent, traceable portfolio release whose demo, case study, repository, presentation, licensing, citation, archive, and maintenance posture all refer to the same accepted evidence and limitations. | **proposed — blocked** | Accepted Phase Five release candidate, verified public claims, resolved licensing, and a repository-owned release surface. | [Phase Six objectives](../phases/phase-06/PHASE_06_OBJECTIVES.md) |

## Phase One — scope and control baseline

**Objective:** Establish the documented project identity, bounded CV task, source-feasibility posture, repository operating system, version/provenance/claims controls, and prompt-built workflow, then make an evidence-backed Phase One acceptance decision before implementation begins.

**What this phase must prove:** BurnLens can enter implementation with a coherent promise, bounded task, traceable operating rules, safe claims, and an explicit gate rather than relying on conversation context or informal assumptions.

**Current status:** Objectives One through Six are complete as documentation/control baselines. P1O7-T08 / PR #294 accepted the evidence for Phase Two planning only. PR #291 and `v0.0.8-execution-goal-baseline` version that control baseline. No analytical release exists. Phase Two metadata, route, access-integrity, and final-AOI evidence is shipped through P2O2-T01 / `v0.2.0-aoi-baseline`, while provider imagery access remains blocked.

## Phase Two — data foundation

**Objective:** Build a complete, traceable data foundation for one bounded Deschutes County experiment, including authorized sources and AOI, reproducible preprocessing, defensible positive/negative/unknown labels, leakage-resistant splits, non-model baselines, dataset QA, and a model-readiness decision.

**What this phase must prove:** The proposed CV task is supported by data and labels that are reproducible, independently split, honestly uncertain, and strong enough to justify—or reject—model training.

**Current status:** P2O1-T02 / issue #312 narrows the discovery set to one exact Sentinel-2 L2A product and the closest same-day NOAA-21 VIIRS active-fire/geolocation pair. P2O1-T03 / issue #317 proves that unauthenticated LP DAAC responses are Earthdata Login HTML rather than source assets. P2O2-T01 / issue #321 / PR #322 ships `aoi-darlene3-model-v0.2.0`, a deterministic 12 km by 9 km modeling boundary derived from one public NIFC final-perimeter reference, at `v0.2.0-aoi-baseline`. County and selected-source metadata coverage pass, but BurnLens still has zero provider imagery assets, pixel arrays, labels, datasets, baselines, or models. Paired intake requires owner approval for both credential boundaries.

**Gate outcome:** proceed with active-fire segmentation, approve a documented burn-scar fallback, remain baseline-only, remediate, or stop model work.

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

Task-level and checkpoint-level changes may be made through ordinary issue-backed work. Objective-level changes require explicit owner approval and updates to both this roadmap and the affected phase objective document in the same pull request.

## Current next checkpoint

The controlling execution goal remains `v0.0.8-execution-goal-baseline` at `22a8d88435cb8d5b900a398b7482c3b7277d2ee6`. P2O1-T01 through P2O2-T01 are shipped and tagged through `v0.2.0-aoi-baseline` at `fffd3dda123d7c43fe678dca9adfd8feb73de158`; `aoi-darlene3-model-v0.2.0` is frozen for modeling. The highest-leverage checkpoint is exact paired asset intake and visual inspection, but it must not begin until the owner explicitly authorizes both CDSE and Earthdata credentials. Geometry and metadata coverage remain evidence of scope, never a detection.

## Required reading order for long-running Codex work

1. `docs/governance/BURNLENS_EXECUTION_GOAL.md`
2. `AGENTS.md`
3. `docs/status/PHASE_STATUS.md`
4. this roadmap
5. the active phase objective document
6. the active issue and branch contract
7. only the workflow and archival evidence relevant to the next bounded checkpoint

## Consistency rule

The roadmap contains the canonical short objective for each phase. Each phase document expands its objective without changing its meaning. Material changes must update both in the same reviewed pull request.
