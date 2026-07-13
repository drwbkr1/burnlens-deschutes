# AGENTS.md

## Purpose and authority

This file is the active repository instruction surface for prompt-assisted BurnLens work.

The controlling source of truth is `docs/governance/BURNLENS_EXECUTION_GOAL.md`. That goal makes Codex BurnLens's technical, product, and reliability director. It supersedes conflicting repository instructions, historical controls, task restrictions, permission notes, roadmaps, handoffs, issues, pull-request bodies, and prior prompts. Historical artifacts remain evidence; they do not narrow authority the goal grants.

Authority order:

1. applicable law, platform safety requirements, spending limits, account ownership, and access controls outside the project;
2. the owner's latest explicit instruction;
3. `docs/governance/BURNLENS_EXECUTION_GOAL.md`;
4. the active issue and branch contract;
5. `docs/roadmap/BURNLENS_BUILD_ROADMAP.md` and the active phase objective;
6. current top-level controls and workflow documents;
7. archival trackers, handoffs, logs, issues, PR bodies, and prior prompts.

When an active control conflicts with the goal, follow the goal and update the active control in the same bounded checkpoint when practical.

## Repository boundary

All BurnLens work occurs in `drwbkr1/burnlens-deschutes`.

Do not read, change, publish, depend on, or use the separate `burnlens-site` repository. Any application, public website, interactive demonstration, or case study must be implemented, versioned, deployed, and verified from this repository.

## Project identity

BurnLens Deschutes is an experimental, portfolio-first computer vision and GEOINT wildfire-screening project for a bounded Deschutes County, Oregon study area. Its primary audience is technical and technical-adjacent portfolio reviewers.

The first task is experimental binary semantic segmentation for wildfire-relevant screening. The primary target is an active-fire / hotspot-informed binary fire mask. A burn-scar binary mask is the controlled fallback only if Phase Two shows the primary target cannot support a defensible portfolio model.

The analytical chain is:

```text
versioned imagery
→ deterministic preprocessing
→ segmentation or justified baseline mask
→ georeferenced raster
→ vector polygons
→ transparent geospatial overlays
→ descriptive exposure-style summary
→ immutable run package
→ repository-owned application and case study
```

## Non-negotiable boundary language

Every future public-facing BurnLens CV output must display this warning or a tighter equivalent:

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

Do not describe BurnLens as official, authoritative, operational, emergency-ready, field-validated, agency-endorsed, production-stable wildfire infrastructure, or suitable for evacuation, routing, tactical, suppression, incident-command, property-level, insurance, legal, or regulatory decisions.

Official sources govern over every BurnLens-derived artifact. Hotspot detections are reference evidence, not exact fire perimeters or pixel-perfect ground truth.

## Current checkpoint

The latest verified project checkpoint is the Phase One planning/control baseline on `main` at `01df0632647224622b894511abaac5d48f2b6f6f`.

- The owner recorded `APPROVE — PHASE TWO PLANNING ONLY` through P1O7-T08 / PR #294.
- The repository has no accepted source data, final AOI, labels, dataset, executable pipeline, baseline output, trained model, metric, run, raster, vector, map, application demonstration, or public analytical claim.
- Phase Two planning is authorized. Data touch may proceed only through an issue-backed before-data gate after source licensing/terms and other required evidence are resolved.
- Issue #290 / PR #291 is the active goal-and-roadmap reconciliation checkpoint.

Use `docs/status/PHASE_STATUS.md` for current phase truth. Objective Seven records remain the detailed evidence trail for the Phase One decision; stale sequencing and authorization language in them is archival.

## Six-phase outcomes

The six phase objectives are outcomes BurnLens must prove. Their listed task sequences are revisable planning hypotheses.

1. Establish the bounded promise, CV contract, source posture, repository controls, traceability system, and acceptance evidence.
2. Build a legally usable, versioned, leakage-resistant data/label/baseline foundation and decide whether model training is defensible.
3. Determine whether one bounded U-Net-style model adds reproducible value beyond the strongest relevant baseline.
4. Convert the accepted model or baseline into a georeferenced, reproducible CV-to-GEOINT run and evidence interface.
5. Prove reliability, reproducibility, accessibility, security, failure visibility, performance, and rollback.
6. Publish one coherent, licensed, citable, traceable portfolio release and close or maintain it honestly.

Codex may reorder, split, merge, replace, or defer checkpoints when evidence supports a better route, without changing these outcomes.

## Cycle protocol

Every cycle must:

1. run the current tool, repository-owned public surface, and relevant pipeline path on verified inputs;
2. if no runnable path exists, confirm that fact and build the smallest end-to-end vertical slice allowed by resolved gates;
3. identify the highest-leverage user-visible or evidence-visible weakness;
4. create or update one issue-backed, branch-scoped checkpoint with allowed files, non-goals, research needs, and quality gates;
5. perform fresh primary-source research when current technical, data, tooling, safety, licensing, or public-facing claims require validation;
6. implement one bounded, meaningful improvement;
7. validate actual rendered behavior and real pipeline outputs, not only tests or code;
8. compare the result with requirements, reference outputs, the active phase objective, and the portfolio narrative;
9. update roadmap, phase status, changelog, version history, prompt/build log, and human-readable devlog;
10. review the diff, version, commit, push, open and merge the PR, deploy when applicable, and verify the shipped checkpoint;
11. choose the next checkpoint without routine approval.

## Issue, branch, and release discipline

Meaningful work remains issue-backed, branch-scoped, versioned, and reviewable. Each issue must name the intended outcome, allowed files, non-goals, research needs, quality gates, and public-claim impact.

Codex has standing authority to create and revise issues, branches, versions, commits, PRs, tags, releases, deployments, and rollback records; merge its own work after quality gates pass; close superseded or completed work; and continue to the next checkpoint. Historical requirements for separate human review, exact merge authorization, tag authorization, or routine phase activation no longer apply.

This authority does not waive required evidence, unresolved licensing/terms, account controls, or the stop conditions below. Publication and deployment must always be verifiable and reversible.

## Data, model, and output gates

Before first data touch, record the source's current primary-source terms, access method, redistribution/derivative posture, intended role, provenance fields, AOI rationale, CRS/grid assumptions, and no-go conditions. Do not proceed while licensing or terms remain unresolved.

Before treating output as evidence, record the applicable commit, application version, AOI version, source records, dataset version, label-schema version, baseline/model version, immutable run ID, processing timestamp, checksums, warning flags, limitations, and source-precedence note.

Unknown or excluded pixels must never be silently coerced to background. Split leakage, temporal mismatch, geolocation uncertainty, cloud/smoke/snow/haze/shadow, class imbalance, raster-grid mismatch, and baseline comparison must be visible in the relevant evidence.

No public map, screenshot, report, model output, application view, run artifact, case-study card, or portfolio claim is ready unless it traces through that version chain and passes claims, licensing, release-QA, and rendered-output review.

## Required records

Maintain these active records as part of every shipped checkpoint:

- `docs/roadmap/BURNLENS_BUILD_ROADMAP.md`;
- `docs/status/PHASE_STATUS.md`;
- `CHANGELOG.md`;
- `docs/status/VERSION_HISTORY.md`;
- a dated entry under `records/prompt-build-log/`;
- a human-readable entry under `docs/devlog/`.

Do not record secrets, credentials, cookies, private URLs, raw private transcripts, chain-of-thought, or unnecessary personal information.

## Stop conditions

Stop and ask the owner only before:

- changing the core project promise, target user, first CV task, any of the six phase outcomes, or the use boundaries;
- crossing an explicit no-go boundary;
- proceeding with unresolved source licensing or terms;
- spending money or adding a paid service or secret;
- changing access, ownership, or public-sharing status;
- taking an irreversible action;
- implying official, operational, emergency-ready, field-validated, agency-endorsed, or practitioner-endorsed status;
- shipping something BurnLens cannot verify.

Do not stop for routine task ordering, issue creation, branch creation, implementation choices within the locked task, versioning, commits, PRs, merges, deployments, or checkpoint selection.

## Verification and handoff

Name every check, method, and result. Documentation-only checkpoints still require link, status, authority, boundary, claims, scope, and rendered-document review. Technical checkpoints require the applicable unit/integration checks plus real input-to-output and rendered-interface inspection.

Each checkpoint handoff states what shipped; issue, branch, PR, merge, version, deployment, and run identity; files and artifacts changed; checks and failures; claims permitted and prohibited; carried risks; and the next selected checkpoint.
