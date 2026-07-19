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

The first task is experimental binary semantic segmentation for wildfire-relevant screening. Active-fire / hotspot-informed masking was the planned primary target, but P2O2-T04 proved it could not define defensible 10-20 m labels. The owner activated the established burn-scar binary-mask fallback on 2026-07-14. Active-fire observations remain complementary reference evidence only.

P2O4-T10B / issue #403 / PR #412 has shipped verified `v0.20.0-single-reviewer-reconciliation`, opening and reconciling one exact blinded response under the explicit reviewer-two waiver. Its 6 burned / 0 background / 50 ignored result remains immutable historical evidence, but the owner replaced that route on 2026-07-17 with `owner-confirmed-prototype-label-review-v0.1.0`. P2O4-T12 / issue #416 / PR #430 verified the exact current BAER/RAVG/MTBS bundles. P2O4-T14 / issue #432 / PR #434 now reopens all 56 original units as disclosed evidence-backed candidates and accepts only owner yes, no, or uncertain. A yes is necessary but not sufficient for an owner-approved prototype label; source, reproducibility, quality, and leakage gates must also pass. No and uncertain remain excluded. One reviewer remains one reviewer, and this route never supports independent-ground-truth, inter-rater, field-validation, official, endorsed, enterprise, or operational claims. Do not begin splits, baselines, or models early.

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

P2O4-T01 through P2O4-T19 ship verified proposal, source, review, custody, remediation, six-candidate, exact owner-review, and owner-response intake evidence through `v0.31.0-region-owner-response-intake`. Historical 6/0/50 exclusions are not inherited. Six regions pass as `owner-approved-prototype-region-labels-v0.1.0`: three burned, three background, 136 core pixels, and 246 excluded unknown-ring pixels across three events. P2O4-T20 freezes Green Ridge, Grandview, and Petes Lake as metadata-only groups. Verified P2O4-T21 / issue #472 / PR #475 passes Green Ridge exact optical custody, native pixels, quality, and registration only. Issue #477 owns official reference-pixel fitness. Green Ridge candidate classes/unknowns, owner review, labels, dataset, split, baseline, model, deployed analytical application, and independent scientific fitness remain absent. Never claim reviewer two, inter-rater agreement, consensus, field validation, official status, endorsement, or operational readiness.

- `aoi-darlene3-model-v0.2.0` is the accepted 12 km by 9 km final modeling AOI, derived reproducibly from one retained public NIFC reference feature.
- The repository has executable access-validation and AOI-evidence paths. `v0.3.0-intake-transaction-baseline` ships a fail-closed, exact three-asset transaction with temporary synthetic rehearsal and atomic all-or-none raw promotion.
- Issue #329 has now exercised both credentials through the secret-safe runtime wrapper. Three exact provider assets totaling 1,169,997,942 bytes are registered only in ignored local raw storage; no raw provider byte or secret material is committed.
- `SOURCE-INSPECTION-2026-001` renders real Sentinel AOI pixels, real VIIRS provider records, QA exclusions, scan-edge risk, and full lineage. Its decision is `ACCEPT_SOURCE_REFERENCE_DEFER_LABELS`.
- `OBSERVATION-GEOMETRY-2026-001` compares all 23 bounded NOAA-21 candidates. The selected `A2024179.2118` day observation materially improves qualified median view zenith from about 69 to 31 degrees with zero residual-bowtie exclusions, but its 2.48-hour offset and 375 m support still defer labels and a dataset.
- `TARGET-DECISION-2026-001` is the preserved pre-remediation run that exposed checkout-dependent input hashing after merge. Corrected run `TARGET-DECISION-2026-002` activates `target-burn-scar-v0.2.0`, retains the active-fire path as complementary reference only, and records that the current official MTBS occurrence layers expose no Darlene 3 feature in the frozen AOI. MTBS remains relevant methodology and potential cross-fire or future reference evidence, not current Darlene 3 truth.
- `OPTICAL-PAIR-2026-001` opens the exact real pre/post TCI, B04, B8A, B12, and SCL AOI pixels. Pairwise quality is 98.9137% eligible, 0.7641% review-needed, and 0.3222% excluded. Continuous dNBR is threshold-free change evidence; the later NIFC outline is context only.
- `CONTENT-REGISTRATION-2026-001` re-verifies that pair and measures independent B04/B8A/B12 gradient translation in twelve fixed windows. All pass; median residual is 0.0224 pixel and maximum is 0.0361 pixel / about 0.72 m. Product QC remains context and window passes never override SCL states.
- `LABEL-PROPOSAL-2026-001` implements `burn-scar-five-state-schema-v0.1.0`; `LABEL-QA-2026-001` independently recomputes the shared contract with zero disagreement. `CROSS-EVENT-FITNESS-2026-001` freezes acquisition groups; `CROSS-EVENT-SOURCE-FITNESS-2026-001` proves the exact pixels with exclusions. `CROSS-EVENT-LABEL-TRANSFER-2026-001` preserves five-state uncertainty across Tepee/McKay; its separate QA reproduces every state/target pixel. The shipped offline review workbench is a response-capture surface, not an analytical inference application. No accepted dataset, split, baseline output, trained model, analytical metric, deployment, independent human annotation, or field validation exists.
- Passing authentication or registration alone does not establish fire presence, label fitness, data fitness, or analytical value. Provider bytes and secrets must never be committed.

P2O2-T04 preserves active-fire reference semantics under `weak-reference-label-feasibility-v0.1.0`. P2O2-T06 preserves the five-state design; P2O3-T01 satisfies the local-translation prerequisite; P2O4-T01 implements one exact proposal and separate software QA; P2O4-T02 freezes two additional whole-event acquisition groups without calling them partitions; P2O4-T04 transfers proposal evidence without calling it accepted truth. Do not coerce 375 m points, non-detections, buffers, dNBR/SCL, product QC, registration windows, the later NIFC/MTBS boundaries, catalogue cloud metadata, software agreement, or an owner response into ground truth. Unknown, excluded, and review-needed pixels never become background silently. Explicit owner yes plus passed provenance, reproducibility, source/terms, quality, and event-level leakage gates must precede any prototype-label promotion; a dataset or split requires the resulting accepted set to satisfy the Phase Two class, coverage, and leakage outcomes.

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
