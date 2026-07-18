# BurnLens Deschutes — Phase Two Objectives

## Document role

This document expands the Phase Two objective summarized in `docs/roadmap/BURNLENS_BUILD_ROADMAP.md`.

Its existence records the intended outcome and gate. It does not activate Phase Two or authorize data touch.

## Phase name

**Data Acquisition, Label Construction, Baseline Evidence, and Dataset Versioning**

## Canonical objective summary

Build a complete, traceable data foundation for one bounded Deschutes County experiment, including authorized sources and AOI, reproducible preprocessing, defensible positive/negative/unknown labels, leakage-resistant splits, non-model baselines, dataset QA, and a model-readiness decision.

## Current status

**Active - exact owner response reconciled; 24 prototype labels accepted; dataset not created.**

P2O1-T01 through P2O3-T01 establish metadata, route, terms, AOI, source transactions, source/observation evidence, the active burn-scar target, exact optical pairs, and verified registration. P2O4-T01 through P2O4-T14 ship proposal, cross-event, review/custody, historical single-response reconciliation, current catalog/request, source scout, exact bundle fitness, and the owner-confirmed surface. P2O4-T15 / issue #437 preserves the authoritative completed response and accepts 24 explicitly owner-approved prototype labels after all disclosed gates: 12 burned and 12 background, balanced across three event groups. Twenty-nine yes and three no/uncertain units remain excluded. The historical 6 burned / 0 background / 50 ignored counts are not inherited. No accepted dataset, split, baseline, model, or deployed analytical application exists.

Current objective posture: Objective One is satisfied for bounded acquisition actions. Objective Two has the accepted source/reference stack, observation comparison, approved target, exact pairs, and current official products. Objective Three has immutable preprocessing, reviewable proposal rasters, and 24 sparse owner-approved prototype units, but not an accepted dataset. Objective Four has completed the bounded owner-response gate without claiming independent truth, inter-rater agreement, or field validation. Objective Five has pre-tiling group identities but no accepted split, derived-pixel overlap audit, baselines, or untouched test set; issue #443 owns that sufficiency gate. Objective Six remains open. This ordering is evidence-responsive, not checklist completion.

## Phase purpose

Phase Two turns Phase One’s documentation-only feasibility decisions into controlled data evidence. It authorizes and records source access, selects one bounded AOI, acquires only approved assets, builds deterministic preprocessing and quality masks, constructs labels that preserve uncertainty, creates independent splits, evaluates simple baselines, and packages the result as a versioned dataset with a clear go/no-go decision for model training.

Phase Two does not train the U-Net model.

## Position in the six-phase build

| Phase One provides | Phase Two creates | Phase Three receives |
|---|---|---|
| CV task, target/fallback rules, source candidates, use boundaries, repository controls, provenance and version rules | AOI, source records, imagery, references, labels, exclusions, splits, preprocessing, baselines, manifests, QA, reproducibility evidence | A versioned training/evaluation package and active-fire, burn-scar, baseline-only, remediation, or stop decision |

## Locked technical context

The initial task remains experimental binary semantic segmentation for wildfire-relevant screening.

- Planned primary target: active-fire or hotspot-informed binary fire mask; P2O2-T04 rejected direct labels and retains this path as complementary reference only.
- Active target: owner-approved burn-scar binary mask under `target-burn-scar-v0.2.0`.
- Required label pathways: positive, negative/background, and unknown/exclude/review-needed.
- Unknown or invalid regions must not be silently converted to background or counted as ordinary negatives.
- FIRMS and similar products may serve as references, cues, sampling aids, weak-label sources, or baselines, not pixel-perfect ground truth.

## Required outcomes

Phase Two must produce:

1. one approved and versioned Deschutes County AOI;
2. approved source, access, terms, CRS, provenance, registry, precedence, and boundary records;
3. immutable raw-source registration and deterministic preprocessing;
4. explicit quality and exclusion masks;
5. a versioned image and label dataset;
6. a published positive/negative/unknown label schema;
7. train, validation, and test splits grouped before tiling by event, scene, geography, or time;
8. duplicate, overlap, and leakage audits;
9. at least one meaningful non-model baseline plus trivial reference baselines;
10. dataset QA and exclusion statistics;
11. a clean reproducibility dry run;
12. a documented Phase Three readiness decision.

## Objective set

### Objective One — Authorize and control Phase Two data work

**Purpose:** Create the parent tracker, task sequence, intake records, artifact boundaries, and review gates before any source asset is downloaded or retained.

**Required result:** Issue-backed authorization; AOI, source, access, terms, CRS, provenance, registry, precedence, use-boundary, and prompt-log records; explicit prohibition on model training and public performance claims.

**Acceptance gate:** The before-data record set is reviewed and sufficient for the exact proposed data action. Planning files alone do not authorize acquisition.

### Objective Two — Finalize the AOI and source stack

**Purpose:** Select one bounded AOI and technically defensible source roles for the primary and fallback targets.

**Required result:** Versioned AOI record; bounded access tests; accept/optional/defer/reject decisions for primary imagery, secondary imagery, harmonized imagery, reference products, local context, and metadata pattern.

**Acceptance gate:** The AOI and source stack are access-tested, versioned, terms-aware, and capable of supporting both the intended target and uncertainty handling.

### Objective Three — Build reproducible acquisition and preprocessing

**Purpose:** Convert authorized source assets into aligned, quality-controlled model inputs without contaminating future evaluation.

**Required result:** Immutable raw records; configuration-driven scaling, band selection, quality masking, reprojection, alignment, resampling, clipping, tiling, georeferencing, and preprocessing manifests.

**Acceptance gate:** A second run can regenerate equivalent processed assets from the same source records and configuration within documented tolerances.

### Objective Four — Construct and review the label dataset

**Purpose:** Create labels that are traceable, explicit about uncertainty, and defensible for a portfolio-scale experiment.

**Required result:** Versioned label schema; candidate weak/reference-derived labels; internal visual review; explicit temporal and spatial matching; confidence and disagreement handling; exclusions for ambiguous evidence.

**Acceptance gate:** Labels are reviewable and support active-fire segmentation or the approved fallback. Unreviewed point buffers alone are insufficient.

### Objective Five — Create independent splits, baselines, and dataset QA

**Purpose:** Prevent leakage and determine whether a future model has a meaningful baseline to beat.

**Required result:** Event/scene/place/time grouping before patching; duplicate and overlap audit; all-background and reference baselines; at least one nontrivial baseline where evidence supports it; untouched test set.

**Acceptance gate:** No known cross-split leakage remains; independent groups exist in every split; unknown coverage is reported; baseline errors are inspectable.

### Objective Six — Package, version, reproduce, and hand off

**Purpose:** Turn controlled working files into a traceable dataset release candidate and explicit model-readiness decision.

**Required result:** Dataset manifest, source references, AOI version, image and label inventories, label schema, split manifest, preprocessing config, quality masks, baseline version, checksums, terms references, known limitations, exclusion statistics, and clean dry-run evidence.

**Acceptance gate:** The project chooses one outcome: proceed with active-fire training, approve burn-scar fallback, remain baseline-only, remediate, or stop model work.

## Completion evidence

Phase Two is complete only when:

- the versioned dataset package can be reconstructed from its source records and configuration;
- split independence and leakage checks are documented;
- baseline evidence uses the same label and exclusion rules as future model evaluation;
- the test set remains locked and untouched by method selection;
- data terms and redistribution limits are known;
- the model-readiness decision is reviewed and merged;
- the handoff states exactly what Phase Three may train and evaluate.

## Dependencies

- reviewed Phase One acceptance outcome;
- task-specific before-data gate;
- current repository SOP, versioning, provenance, claims, and release controls;
- available and legally usable source access;
- sufficient positive and negative evidence for the selected target;
- storage and compute within approved limits.

## Non-goals

Phase Two does not:

- implement or train the U-Net model;
- tune model thresholds or publish model metrics;
- build the interactive map or public demo;
- claim field validation, local agency validation, operational accuracy, or emergency usefulness;
- expand to multiple AOIs or target classes merely to increase portfolio breadth;
- redistribute source data or derived artifacts before terms review.

## Fixed boundaries

- One bounded Deschutes County AOI at a time.
- One primary target and one documented fallback.
- Positive, background, and unknown/exclude remain separate.
- Raw source assets are immutable; corrections create new or superseding records.
- Splits occur before patch generation and preserve event/scene/geography/time independence.
- Official/reference, label, baseline, and future model artifacts remain distinct.
- No data action occurs outside an issue-backed contract and before-data gate.

## Known risks and assumptions

- Active-fire positives may be rare, obscured, temporally mismatched, or too coarse for defensible masks.
- Cloud, smoke, snow, glare, shadows, saturation, mixed pixels, and nodata may reduce usable coverage.
- Reference products may not align spatially or temporally with optical imagery.
- Near-duplicate remote-sensing samples can inflate evaluation if grouping and audits fail.
- Source access, API behavior, terms, and local-layer availability may change and require fresh primary-source validation.
- Resampling must not be described as creating genuine higher-resolution information.

## Authority delegated to Codex

Within issue-backed Phase Two checkpoints, Codex may:

- run bounded source access and format/CRS tests;
- propose AOI candidates and score them against approved criteria;
- implement deterministic acquisition, preprocessing, QA, and baseline code;
- create versioned records, manifests, checksums, and audits;
- exclude ambiguous or degraded evidence according to the label contract;
- recommend active-fire, fallback, baseline-only, remediation, or stop outcomes.

Codex must not silently change the target, proceed with unresolved data terms, unlock the test set, or treat weak labels as ground truth.

## Changes requiring owner approval

The stop conditions in `docs/governance/BURNLENS_EXECUTION_GOAL.md` control. Codex may plan Phase Two, select a bounded AOI under the established Deschutes County rationale, and begin data work once source terms/licensing and the before-data gate are resolved and recorded.

Owner approval is required before changing the CV task, primary target, controlled-fallback rule, phase outcome, or use boundaries; crossing a no-go boundary; proceeding with unresolved licensing/terms; spending money or adding a paid service/secret; changing access, ownership, or public-sharing status; taking an irreversible action; implying official/operational/emergency-ready/field-validated/endorsed status; or shipping something unverifiable.

## Expected handoff to Phase Three

The handoff must provide:

- target decision;
- dataset, AOI, source, and label versions;
- locked split manifest and checksum;
- quality and exclusion rules;
- baseline versions and results;
- known leakage and duplication findings;
- source and licensing limitations;
- training input contract;
- compute constraints;
- explicit authorization, remediation, baseline-only, or stop outcome.

## Source basis

This document consolidates the supplied Phase Two objective plan and current Phase One controls. Once merged, it is the canonical Phase Two objective definition; detailed tasks remain issue-generated and evidence-responsive.
