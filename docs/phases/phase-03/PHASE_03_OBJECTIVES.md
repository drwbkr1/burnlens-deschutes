# BurnLens Deschutes — Phase Three Objectives

## Document role

This document expands the Phase Three objective summarized in `docs/roadmap/BURNLENS_BUILD_ROADMAP.md`.

It defines the evidence Phase Three must produce. It does not authorize training before Phase Two acceptance and an issue-backed model-work contract.

## Phase name

**Computer Vision Model Development, Controlled Evaluation, and Model Versioning**

## Canonical objective summary

Build and evaluate one bounded U-Net-style segmentation model against the accepted Phase Two baselines, then package either a defensible model or a transparent baseline-only decision with complete lineage, error analysis, and limitations.

## Current status

**Proposed — blocked.**

Phase Three depends on an accepted Phase Two package, target decision, locked split, baseline evidence, and explicit model-work authorization.

## Phase purpose

Phase Three answers one central question:

> Does one bounded U-Net-style segmentation model add measurable, inspectable, and reproducible value beyond the simpler Phase Two baselines?

The phase is not an architecture competition. It creates one understandable training system, a small predeclared experiment matrix, one frozen candidate or baseline-only decision, one final locked-test evaluation, a model card, and a versioned handoff for geospatial integration.

## Position in the six-phase build

| Phase Two provides | Phase Three creates | Phase Four receives |
|---|---|---|
| Approved AOI, dataset, labels, exclusions, splits, baselines, manifests, and target decision | Training system, controlled experiments, selected candidate, locked-test evidence, error analysis, model package or baseline-only decision | Frozen analytical package, inference contract, threshold/calibration status, limitations, and fallback rules |

## Locked context

- Task: experimental binary semantic segmentation for wildfire-relevant screening.
- Primary target: active-fire or hotspot-informed mask unless Phase Two formally approved the fallback.
- Reference family: U-Net-style encoder-decoder.
- Unknown and excluded pixels remain masked from loss and metrics according to the label contract.
- The Phase Two test set remains locked until one final evaluation.
- Model evidence must be compared with the strongest relevant non-model baseline.

## Required outcomes

Phase Three must produce:

1. one reproducible PyTorch training and evaluation system;
2. one U-Net-style reference implementation;
3. a small predeclared experiment matrix and compute budget;
4. masked loss and metrics that preserve exclusion semantics;
5. tracked configs, seeds, environments, checkpoints, warnings, and commits;
6. a selected frozen candidate or documented baseline-only decision;
7. one final locked-test evaluation;
8. aggregate and per-scene metrics;
9. qualitative successes, failures, and source/label/model error categorization;
10. model-versus-baseline evidence;
11. calibration analysis if probabilities will be exposed as confidence-like output;
12. a versioned model package, model card, reproducibility run, and Phase Four recommendation.

## Objective set

### Objective One — Authorize and control model work

**Purpose:** Lock the accepted Phase Two lineage, model family, experiment budget, test-set rules, file scope, and Phase Four handoff before implementation.

**Acceptance gate:** Every model task can proceed through issue-backed repository work without changing data, labels, splits, or public claims silently.

### Objective Two — Implement the reference model and training system

**Purpose:** Build one configuration-driven training system with clear separation among imagery, labels, exclusions, logits, probabilities, thresholded masks, baselines, and metrics.

**Required result:** Dataloader integration; U-Net-style model; masked loss; optimizer and scheduler; train/validation loops; checkpoint recovery; environment capture; deterministic or best-effort reproducibility mode; smoke-test mode; clear failure messages.

**Acceptance gate:** The system completes forward/backward passes, masks exclusions correctly, saves and reloads checkpoints, reproduces a small run within documented tolerance, and rejects incompatible inputs.

### Objective Three — Define the controlled experiment protocol

**Purpose:** Predeclare training, selection, loss, augmentation, threshold, seed, compute, and stopping rules before substantive experiments.

**Required result:** Modest experiment matrix; scientifically plausible training-only augmentation; limited imbalance strategies; validation-based threshold selection; no test-set use for tuning.

**Acceptance gate:** Every permitted experiment has a distinct purpose and configuration, and the test set remains locked.

### Objective Four — Train, compare, and freeze the candidate

**Purpose:** Run the approved experiments and select one candidate through predeclared evidence rather than headline metrics or visual preference.

**Required result:** Traceable runs; validation metrics; false-positive/false-negative behavior; baseline comparison; scene stability; model size and inference practicality; resumable and selected checkpoints.

**Acceptance gate:** One candidate is frozen for evaluation, a correctable problem is routed to remediation, or the model path stops transparently.

### Objective Five — Evaluate, calibrate, and analyze failures

**Purpose:** Determine whether the frozen candidate adds meaningful value beyond the Phase Two baselines.

**Required result:** One locked-test evaluation; IoU primary metric; Dice/F1, precision, recall, area difference, per-scene and empty-scene evidence; hard-case review; threshold sensitivity; calibration evidence where applicable; error attribution.

**Acceptance gate:** The project makes a clear integrate, integrate-with-caveats, remediate, or baseline-only decision without test-set tuning.

### Objective Six — Package, version, reproduce, and hand off

**Purpose:** Convert the selected analytical result into a traceable Phase Four input.

**Required result:** Versioned weights or baseline reference; inference and training configs; architecture record; metrics; evaluation summary; model card; environment lock; commit; dataset lineage; checksums; sample predictions; clean reproduction evidence.

**Acceptance gate:** Phase Four receives one immutable analytical package and a clear inference/output contract, or a documented decision not to integrate a model.

## Completion evidence

Phase Three is complete only when:

- the experiment protocol was fixed before substantive training;
- the selected threshold was chosen without test-set evidence;
- final test evaluation occurred once against the locked split;
- baseline comparison and failure cases are preserved;
- every metric traces to dataset, label, split, model, threshold, environment, and commit;
- the model card states intended and prohibited uses;
- a clean environment can reproduce the accepted inference behavior within documented tolerance;
- the Phase Four decision is reviewed and merged.

## Dependencies

- accepted Phase Two dataset and target decision;
- locked test split and baseline versions;
- approved compute, storage, dependency, and environment posture;
- complete label and exclusion semantics;
- issue-backed model authorization.

## Non-goals

Phase Three does not:

- search broadly across unrelated architectures;
- modify the accepted dataset, labels, AOI, or split without a new Phase Two decision;
- build the interactive map or final geospatial product;
- publish the final case study or public demo;
- claim real-time, operational, field-validated, agency-endorsed, or emergency capability;
- advance a model merely because it trains successfully.

## Fixed boundaries

- One target and one reference model family.
- Small, predeclared experiment budget.
- Test set locked until final evaluation.
- Unknown and excluded pixels remain excluded.
- Baseline comparison is mandatory.
- Raw probabilities are not automatically called confidence.
- Model versions do not imply operational readiness.

## Known risks and assumptions

- Foreground scarcity and label uncertainty may dominate architecture choice.
- Small datasets may produce unstable metrics and seed sensitivity.
- Exact PyTorch reproducibility may vary by platform, release, hardware, or nondeterministic operation.
- Class imbalance can inflate accuracy while failing on positive pixels.
- Scene-level aggregation may hide local failures.
- Calibration may be poor even when segmentation metrics improve.
- Model value may be negative or too small to justify integration; baseline-only remains a valid portfolio outcome.

## Authority delegated to Codex

After the Phase Two evidence gate and within an issue-backed experiment contract, Codex may:

- implement the reference training system;
- select among approved loss, augmentation, regularization, and capacity options;
- run the bounded experiment matrix;
- checkpoint, compare, and recommend a candidate;
- identify implementation defects and propose remediation;
- stop model work when no candidate adds credible value;
- package the selected model and evidence.

Codex must not expand the architecture search without evidence, unlock the test set, alter labels after the split is frozen, reinterpret metrics, or publish performance claims outside evaluated evidence.

## Changes requiring owner approval

The stop conditions in `docs/governance/BURNLENS_EXECUTION_GOAL.md` control. Model training and bounded experiment selection do not require routine approval once Phase Two's gate passes and the issue contract records the frozen evidence.

Owner approval is required before changing the core CV task or phase outcome; crossing a no-go boundary; proceeding with unresolved licensing/terms; spending money or adding a paid service/secret; changing access, ownership, or public-sharing status; taking an irreversible action; implying official/operational/emergency-ready/field-validated/endorsed status; or shipping something unverifiable. Restricted assets may not be published while terms remain unresolved.

## Expected handoff to Phase Four

The handoff must provide:

- selected model version or baseline-only decision;
- weights/checksums where applicable;
- exact input band, normalization, tile, and exclusion contract;
- frozen threshold and calibration status;
- dataset, label, split, and baseline lineage;
- aggregate and per-scene metrics;
- known failure modes and withheld conditions;
- expected raster/probability output semantics;
- inference environment and reproducibility evidence;
- explicit integrate, caveated, baseline-only, remediate, or stop outcome.

## Source basis

This document consolidates the supplied Phase Three objective plan and current BurnLens CV, versioning, use-boundary, and repository-control documents. Detailed experiment tasks remain issue-generated and evidence-responsive.
