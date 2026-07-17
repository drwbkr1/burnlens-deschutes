# BurnLens Controlling Execution Goal

## Goal

Direct BurnLens from its verified Phase One planning/control baseline to a defensible, reproducible, publicly coherent computer-vision-to-GEOINT portfolio release.

Codex acts as BurnLens's technical, product, and reliability director. It owns checkpoint selection, implementation, verification, versioning, repository maintenance, release execution, and continued prioritization within the authority and stop conditions below.

This document is the controlling source of truth for BurnLens execution. When repository instructions, historical controls, task restrictions, permission notes, roadmaps, handoffs, issues, PR bodies, or prior prompts conflict with it, follow this goal and update the active conflicting artifacts so the repository reflects the new authority. Do not use stale controls to narrow permissions this goal explicitly grants.

This precedence governs BurnLens project work. It does not override applicable law, platform safety requirements, spending limits, account ownership, or access controls outside the project.

## Repository boundary

All BurnLens work must occur in `drwbkr1/burnlens-deschutes`.

The separate `burnlens-site` repository must never be read, changed, published, used, or introduced as a dependency. BurnLens's analytical system, application, public website, case study, documentation, deployment configuration, and release evidence must live in and ship from `drwbkr1/burnlens-deschutes`.

## Preserved project spine

The following decisions are fixed unless the owner explicitly approves a change:

- **Portfolio thesis:** demonstrate depth, judgment, reproducibility, and transparent engineering through one bounded wildfire-related CV-to-GEOINT workflow rather than a broad collection of disconnected features.
- **Primary audience:** technical and technical-adjacent portfolio reviewers.
- **Reference user story:** a reviewer should be able to inspect and reproduce a workflow that combines imagery, public geospatial layers, and experimental CV outputs for a defined Deschutes County study area.
- **CV task:** experimental binary semantic segmentation for wildfire-relevant screening.
- **Planned primary target:** active-fire / hotspot-informed binary fire mask. P2O2-T04 rejected direct label promotion on observed temporal and spatial-support evidence; this source now remains complementary native-scale reference only.
- **Owner-approved active target path:** burn-scar binary mask. The owner activated the established fallback on 2026-07-14 through P2O2-T05 as `target-burn-scar-v0.2.0`; this does not change the binary semantic-segmentation task or authorize severity, recovery, or multiclass expansion.
- **Reference model family:** one bounded U-Net-style segmentation family, compared with the strongest relevant non-model baseline.
- **GEOINT workflow:** imagery → preprocessing → segmentation or baseline mask → georeferenced raster → vector polygons → transparent overlays → descriptive exposure-style summary → immutable run package → repository-owned evidence interface and case study.
- **Use boundaries:** experimental, non-operational, non-emergency, not field-validated, not agency-endorsed, and unsuitable for evacuation, routing, tactical, suppression, incident-command, property-level, insurance, legal, or regulatory decisions.
- **Source precedence:** official and authoritative sources always govern over BurnLens-derived output.
- **Design posture:** baseline-first, static-artifact-friendly, accessible, failure-visible, versioned, and traceable; prefer one deep system over parallel systems.
- **Transparency:** distinguish source/reference evidence, labels, baselines, models, integrated runs, and portfolio interpretation; expose uncertainty, exclusions, limitations, and failure cases.

Required warning for every future public-facing CV output:

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

The target-path decision is resolved. Future checkpoints must not silently reactivate active-fire label construction. They must first prove a legally usable and visually defensible pre/post optical pair plus a burn-scar protocol that preserves burned, background-candidate, unknown, excluded, and review-needed states before creating any label array.

## Current prototype-label governance

The owner replaced independent/blinded multi-reviewer acceptance as the prospective prototype-label gate on 2026-07-17. Codex must deterministically propose disclosed, evidence-backed burned/background candidates and present the appropriate optical, quality, and official/reference evidence to the owner. The owner answers yes, no, or uncertain.

An owner yes is necessary but not sufficient for an explicitly owner-approved prototype label. Exact provenance, reproducibility, source/terms, product fitness, quality, and event/geography/time leakage gates must also pass. No and uncertain remain excluded. The original 56 units must be reopened under this route; the prior single-response 6 burned / 0 background / 50 ignored reconciliation remains immutable historical evidence but is not a final exclusion decision.

This route must never be described as independent ground truth, inter-rater agreement, consensus, field validation, official or endorsed status, or enterprise/operational readiness. It does not relax uncertainty, source precedence, licensing, provenance, use boundaries, or dataset/split/model gates.

## Verified starting checkpoint

Execution resumes from the latest verified `main` baseline, `01df0632647224622b894511abaac5d48f2b6f6f`, not from ideation.

As of goal activation on 2026-07-13:

- the owner has recorded `APPROVE — PHASE TWO PLANNING ONLY` through P1O7-T08 / PR #294;
- Objectives One through Six exist as documented planning/control baselines;
- Objective Seven preserves the acceptance evidence and planning-only decision;
- an authenticated live tag inventory returns no tag refs;
- the repository has no accepted source data, final AOI, labels, dataset, executable pipeline, baseline output, trained model, metric, immutable run, raster, vector, map, application demonstration, or public analytical claim;
- therefore the first implementation obligation is to resolve Phase Two source/licensing/AOI readiness and then create the smallest defensible end-to-end vertical slice.

Planning maturity must never be represented as executed technical capability.

## Six required phase outcomes

The six phase objectives define what BurnLens must prove. Their listed tasks and sequence are a revisable planning hypothesis, not a rigid checklist.

### Phase One — scope and control baseline

Prove that the portfolio promise, target user, CV contract, source-feasibility posture, repository operating model, version/provenance/claims controls, prompt-assisted workflow, and acceptance evidence are coherent enough to govern implementation.

### Phase Two — data, labels, baselines, and dataset decision

Prove that one bounded Deschutes County experiment can be supported by legally usable sources, reproducible preprocessing, defensible positive/background/unknown labels, leakage-resistant splits, strong non-model baselines, dataset QA, and a clear train/fallback/baseline-only/remediate/stop decision.

### Phase Three — model evidence

Prove whether one bounded U-Net-style model adds measurable, inspectable, reproducible value beyond the strongest relevant baseline without hiding leakage, uncertainty, scene-level failure, or target limitations. A transparent baseline-only outcome is valid.

### Phase Four — CV-to-GEOINT product

Prove that the accepted model or baseline can become a reproducible inference-to-GEOINT workflow with valid georeferencing, raster/vector outputs, deterministic overlays and summaries, accessible evidence presentation, visible failure states, and immutable run packaging.

### Phase Five — reliability and release candidate

Prove that the integrated system can reproduce its evidence, detect and communicate failures, preserve lineage, meet declared accessibility/security/performance expectations, and roll back safely without expanding analytical scope.

### Phase Six — portfolio publication and closeout

Prove that a reviewer can understand, inspect, reproduce, evaluate, cite, and responsibly interpret one coherent release whose application, case study, repository, presentation, licensing, citation, archive, and maintenance posture all refer to the same accepted evidence and limitations.

Codex may reorder, split, merge, replace, or defer checkpoints when evidence supports a better route, provided these outcomes and the preserved project spine do not change.

## Operating cycle

Every cycle begins by running the current tool, repository-owned public surface, and relevant pipeline path on verified inputs. If none exists, confirm that fact and build the smallest end-to-end vertical slice permitted by resolved gates.

Then Codex must:

1. identify the highest-leverage user-visible or evidence-visible weakness;
2. implement one bounded, meaningful improvement;
3. validate the real rendered application and actual pipeline outputs, not only tests or code;
4. compare the result with the applicable requirements, reference outputs, phase objective, and portfolio narrative;
5. decide whether to accept, remediate, narrow, fall back, stop, or ship the checkpoint;
6. update the roadmap, phase status, changelog, version history, prompt/build log, and human-readable devlog;
7. version, commit, push, open and merge the PR, deploy when applicable, and verify the shipped result;
8. select and begin the next checkpoint without routine approval.

Only one bounded improvement is implemented at a time. Depth, reliability, reproducibility, transparency, and portfolio clarity take priority over parallel systems or checklist completion.

## Research and evidence policy

Use fresh primary sources whenever a checkpoint depends on current technical behavior, data access, licensing/terms, tooling, safety guidance, or public-facing claims. Record the URL or source identity, date checked, fact supported, decision adopted, and limitations.

Do not proceed with data access, retention, redistribution, or derived-output publication while source licensing or terms remain unresolved. Hotspot products must not be represented as exact perimeters or pixel-perfect labels without separate validation.

Evidence may support a narrower route: active-fire target, burn-scar fallback, baseline-only system, technical case study without interactive output, remediation, or stop. A narrower defensible result is better than unsupported breadth.

## Traceability standard

Every public output and claim must trace to all applicable identifiers:

- Git commit;
- application or objective-baseline version;
- AOI version;
- source record IDs and access dates;
- dataset version;
- label-schema version;
- baseline-method or model version;
- immutable run ID;
- report or interface version;
- processing timestamp and checksums;
- warning and degradation flags;
- limitations and source-precedence note.

If an identifier class does not yet exist, public status must say `not created`; it must not be omitted in a way that implies completion.

Traceability is necessary but not sufficient. Licensing, claims review, release QA, actual-output inspection, and production verification remain required.

## Standing authority

Within the preserved project spine and phase outcomes, Codex may:

- revise task order and planning documents;
- create, split, merge, supersede, close, or defer checkpoints and issues;
- create and manage branches;
- choose implementation details and already-bounded technical options;
- conduct fresh research and record decisions;
- add code, tests, fixtures, records, documentation, application surfaces, and deployment configuration;
- create versions, commits, tags, releases, and rollback records;
- push branches, open and update PRs, merge its own work after quality gates pass, and verify `main`;
- deploy previews and production checkpoints from this repository when access exists and the result is reversible and verifiable;
- update the repository-owned website and case study after every shipped checkpoint;
- accept, remediate, narrow, fall back, roll back, or stop a checkpoint based on evidence;
- continue choosing and shipping the next checkpoint without routine approval.

Historical requirements for separate human review, separate merge authorization, exact tag authorization, or routine phase activation do not narrow this standing authority.

## Stop and ask conditions

Stop and ask the owner only before:

- changing the core project promise, target user, CV task, any phase outcome, or the use boundaries;
- crossing an explicit no-go boundary;
- proceeding with unresolved source licensing or terms;
- spending money;
- adding a paid service or secret;
- changing access, ownership, or public-sharing status;
- taking an irreversible action;
- implying official, operational, emergency-ready, field-validated, agency-endorsed, or practitioner-endorsed status;
- shipping something BurnLens cannot verify.

Routine checkpoint selection, implementation, versioning, committing, pushing, PR creation, merging, reversible deployment, and continued execution do not require owner approval.

## Completion condition

This goal is complete only when BurnLens has shipped and verified the strongest defensible Phase Six outcome supported by evidence—model-centered, model-with-caveats, baseline-first, or technical-case-study-only—and the repository-owned application, case study, documentation, versions, licensing posture, traceability, reliability evidence, archive, and maintenance/closeout record all agree.

If the evidence cannot support a responsible release, completion may instead be a verified stopped or withdrawn outcome with the reasons, preserved evidence, and non-release decision fully documented.
