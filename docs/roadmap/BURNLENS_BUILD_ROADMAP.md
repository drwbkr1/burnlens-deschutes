# BurnLens Deschutes — Working Build Roadmap

## Purpose

This document is the durable, repository-level roadmap for the six-phase BurnLens Deschutes build.

It gives Codex and human reviewers enough whole-project context to choose the next bounded checkpoint without turning the project into a rigid feature checklist. It records the current best sequence, the outcome each phase must prove, the dependency gates between phases, and the decisions that remain reserved for the human owner.

## Roadmap authority

This roadmap is a **versioned planning hypothesis**, not an automatic authorization to perform every listed activity.

- The roadmap defines intended phase outcomes and dependencies.
- The phase objective documents expand those outcomes without changing their meaning.
- GitHub issues, task capsules, branches, allowed-file contracts, and pull requests authorize actual work.
- Current merged repository controls override stale roadmap language.
- A later phase does not become active merely because its objective document exists.

Codex may reorder, split, merge, defer, or replace tasks and checkpoints inside an authorized phase when verified evidence supports a better route. Codex must document the rationale and preserve the phase objective, project promise, use boundaries, source precedence, and traceability requirements.

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

Traceability does not by itself authorize publication. Claims review, release QA, licensing, human review, and explicit release authorization still apply.

## Status vocabulary

| Status | Meaning |
|---|---|
| `active — incomplete` | Authorized work exists, but the phase gate has not passed. |
| `proposed — blocked` | The phase objective is documented, but predecessor or authorization gates prevent execution. |
| `ready for authorization` | Predecessor evidence is accepted, but issue-backed activation is still required. |
| `accepted with caveats` | The phase gate passed with documented limitations that must carry forward. |
| `accepted` | The phase gate passed and the successor may be considered for authorization. |
| `remediate` | A correctable blocker prevents phase acceptance. |
| `stopped` | The phase cannot responsibly continue under the current objective. |

## Current phase overview

| Phase | Name | Canonical objective summary | Current status | Primary dependency | Detailed objectives |
|---|---|---|---|---|---|
| 1 | Scope, technical contracts, repository controls, and acceptance gate | Establish the documented project identity, bounded CV task, source-feasibility posture, repository operating system, version/provenance/claims controls, and prompt-built workflow, then make an evidence-backed Phase One acceptance decision before implementation begins. | **active — incomplete** | P1O7-T08 decision and remaining Objective Seven closeout work; no final Phase One acceptance exists. | [Phase One objectives](../phases/phase-01/PHASE_01_OBJECTIVES.md) |
| 2 | Data acquisition, labels, baselines, and dataset versioning | Build a complete, traceable data foundation for one bounded Deschutes County experiment, including authorized sources and AOI, reproducible preprocessing, defensible positive/negative/unknown labels, leakage-resistant splits, non-model baselines, dataset QA, and a model-readiness decision. | **proposed — blocked** | Phase One acceptance plus the task-specific before-data gate. | [Phase Two objectives](../phases/phase-02/PHASE_02_OBJECTIVES.md) |
| 3 | CV model development, controlled evaluation, and model versioning | Build and evaluate one bounded U-Net-style segmentation model against the accepted Phase Two baselines, then package either a defensible model or a transparent baseline-only decision with complete lineage, error analysis, and limitations. | **proposed — blocked** | Accepted Phase Two dataset package, locked split, baseline evidence, and target decision. | [Phase Three objectives](../phases/phase-03/PHASE_03_OBJECTIVES.md) |
| 4 | Inference, geospatial productization, interactive integration, and run versioning | Convert the accepted model or baseline into a reproducible inference-to-GEOINT workflow that preserves georeferencing, creates valid raster/vector artifacts, performs deterministic overlay analysis, presents an accessible evidence interface, and packages every execution as an immutable run. | **proposed — blocked** | Accepted Phase Three model package or approved Phase Two baseline-only path. | [Phase Four objectives](../phases/phase-04/PHASE_04_OBJECTIVES.md) |
| 5 | Reliability, QA, reproducibility, security, and release control | Harden the integrated workflow into a tested, reproducible, secure, accessible, performant, and reversible release candidate without expanding analytical scope. | **proposed — blocked** | Accepted Phase Four integrated run package and interface candidate. | [Phase Five objectives](../phases/phase-05/PHASE_05_OBJECTIVES.md) |
| 6 | Portfolio publication, public release, communication, and closeout | Publish one coherent, traceable portfolio release whose demo, case study, repositories, presentation, licensing, citation, archive, and maintenance posture all refer to the same accepted evidence and limitations. | **proposed — blocked** | Accepted Phase Five release candidate, approved public claims, resolved licensing, and explicit release authorization. | [Phase Six objectives](../phases/phase-06/PHASE_06_OBJECTIVES.md) |

## Phase One — scope and control baseline

**Objective:** Establish the documented project identity, bounded CV task, source-feasibility posture, repository operating system, version/provenance/claims controls, and prompt-built workflow, then make an evidence-backed Phase One acceptance decision before implementation begins.

**What this phase must prove:** BurnLens can enter implementation with a coherent promise, bounded task, traceable operating rules, safe claims, and an explicit gate rather than relying on conversation context or informal assumptions.

**Current status:** Objectives One through Six are complete as documentation/control baselines. Objective Seven remains active and incomplete. The Phase One decision has not been made. Data touch remains blocked.

## Phase Two — data foundation

**Objective:** Build a complete, traceable data foundation for one bounded Deschutes County experiment, including authorized sources and AOI, reproducible preprocessing, defensible positive/negative/unknown labels, leakage-resistant splits, non-model baselines, dataset QA, and a model-readiness decision.

**What this phase must prove:** The proposed CV task is supported by data and labels that are reproducible, independently split, honestly uncertain, and strong enough to justify—or reject—model training.

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

**Objective:** Publish one coherent, traceable portfolio release whose demo, case study, repositories, presentation, licensing, citation, archive, and maintenance posture all refer to the same accepted evidence and limitations.

**What this phase must prove:** A technical reviewer can understand, inspect, reproduce, evaluate, cite, and responsibly interpret BurnLens without relying on private project context or unsupported claims.

**Gate outcome:** publish a model-centered release, publish with caveats, publish a baseline-first release, publish a technical case study without interactive output, enter maintenance, archive, or withdraw.

## Dependency and gate chain

```text
Phase One accepted
→ Phase Two authorized and data-ready
→ Phase Three model or baseline decision accepted
→ Phase Four integrated run accepted
→ Phase Five release candidate accepted
→ Phase Six publication explicitly authorized
```

A predecessor gate may approve a narrower fallback path. The roadmap does not require a model-centered release when the evidence supports a stronger baseline-first portfolio story.

## Codex execution authority

Within an active, issue-authorized phase, Codex may:

- inspect current repository and rendered outputs;
- choose the highest-leverage bounded weakness;
- propose and decompose issues and checkpoints;
- reorder task sequence when dependencies allow;
- select among already approved implementation options;
- stop a run or phase when evidence fails a gate;
- recommend remediation, fallback, or scope reduction;
- maintain roadmap status, changelog, prompt/build logs, devlog, versions, and handoffs when the task contract permits;
- commit, push, open pull requests, deploy previews, and verify authorized checkpoints when repository controls and quality gates permit.

Codex must not silently:

- change the project promise, target audience, core CV task, phase objective, use boundaries, source precedence, or traceability standard;
- activate a successor phase before its predecessor gate and task authorization;
- touch data before the before-data gate is satisfied;
- change a locked test split, canonical run, model threshold, public metric, or analytical output after its controlling phase freezes it;
- spend money, add paid services or secrets, alter ownership or access, publish a tag or GitHub Release, or take an irreversible action without explicit approval;
- merge its own work without the required human review and separate merge authorization;
- publish anything it cannot verify.

## Roadmap revision protocol

A roadmap revision must identify:

1. the verified evidence that exposed the weakness;
2. the affected phase objective, dependency, or gate;
3. whether the change is task-level, checkpoint-level, or objective-level;
4. the artifacts and claims affected;
5. the proposed replacement route;
6. the boundaries preserved;
7. the approval required.

Task-level and checkpoint-level changes may be made through ordinary issue-backed work. Objective-level changes require explicit human approval and updates to both this roadmap and the affected phase objective document in the same pull request.

## Current next checkpoint

The current repository truth places Phase One / Objective Seven at the acceptance-gate decision stage. P1O7-T08 is reserved for the Phase One decision memo. This roadmap does not make that decision and does not authorize Phase Two.

## Required reading order for long-running Codex work

1. `AGENTS.md`
2. `README.md`
3. `docs/workflows/PROMPT_TO_REPO_SOP.md`
4. this roadmap
5. the active phase objective document
6. current phase tracker, handoff, gate, and issue contract
7. only the workstream controls relevant to the next bounded checkpoint

## Consistency rule

The roadmap contains the canonical short objective for each phase. Each phase document expands its objective without changing its meaning. Material changes must update both in the same reviewed pull request.
