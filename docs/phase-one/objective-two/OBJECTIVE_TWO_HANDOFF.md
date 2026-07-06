# Phase 1 / Objective Two Handoff

## Objective status

**Objective Two is complete.**

Objective Two defined the first BurnLens Deschutes computer vision task before Phase Two data, label, baseline, or model work begins.

The current focus remains documentation and scope control only.

## Repo use pattern

For P1O2 onward, each task used this loop:

```text
GitHub issue
→ task branch
→ repo artifact
→ commit
→ pull request
→ merge
→ objective handoff update
```

## Completed tasks

| Task | Issue | Branch | PR | Artifact | Status |
|---|---:|---|---:|---|---|
| P1O2-T01 — Define CV task | #7 | `p1o2/t01-cv-task-definition` | #8 | `docs/phase-one/objective-two/CV_TASK_DEFINITION.md` | Complete |
| P1O2-T02 — Choose first segmentation target | #9 | `p1o2/t02-segmentation-target` | #10 | `docs/phase-one/objective-two/TARGET_CLASS_DECISION.md` | Complete |
| P1O2-T03 — Define positive, negative, and ambiguous classes | #11 | `p1o2/t03-class-definitions` | #12 | `docs/phase-one/objective-two/CLASS_DEFINITIONS.md` | Complete |
| P1O2-T04 — Define model output contract | #15 | `p1o2/t04-output-contract` | #16 | `docs/phase-one/objective-two/CV_OUTPUT_CONTRACT.md` | Complete |
| P1O2-T05 — Define imagery assumptions | #17 | `p1o2/t05-imagery-assumptions` | #18 | `docs/phase-one/objective-two/IMAGERY_ASSUMPTIONS.md` | Complete |
| P1O2-T06 — Define label assumptions | #19 | `p1o2/t06-label-assumptions` | #20 | `docs/phase-one/objective-two/LABEL_ASSUMPTIONS.md` | Complete |
| P1O2-T07 — Define baseline comparison plan | #23 | `p1o2/t07-baseline-comparison` | #44 | `docs/phase-one/objective-two/BASELINE_COMPARISON_PLAN.md` | Complete |
| P1O2-T08 — Define first model family | #46 | `p1o2/t08-model-family-decision` | #58 | `docs/phase-one/objective-two/MODEL_FAMILY_DECISION.md` | Complete |
| P1O2-T09 — Define evaluation metrics plan | #61 | `p1o2/t09-evaluation-metrics` | #68 | `docs/phase-one/objective-two/EVALUATION_METRICS_PLAN.md` | Complete |
| P1O2-T10 — Define known failure modes | #70 | `p1o2/t10-failure-modes` | #77 | `docs/phase-one/objective-two/FAILURE_MODES.md` | Complete |
| P1O2-T11 — Define CV-specific use boundaries | #79 | `p1o2/t11-cv-use-boundaries` | #81 | `docs/phase-one/objective-two/CV_USE_BOUNDARIES.md` | Complete |
| P1O2-T12 — Create Objective Two final handoff | #83 | `p1o2/t12-objective-two-handoff` | #84 | `docs/phase-one/objective-two/OBJECTIVE_TWO_FINAL_HANDOFF.md` | Complete |

## Current locked decisions

### CV task

BurnLens Deschutes' first computer vision task is **experimental binary semantic segmentation for wildfire-relevant screening**.

### Primary target

The selected primary target is **active-fire / hotspot-informed binary fire mask**.

### Fallback target

The fallback target is **burn-scar binary mask**, only if Phase Two shows that active-fire / hotspot-informed labels are too weak, noisy, sparse, or misaligned for a defensible portfolio model.

### Class handling

Future label logic should preserve positive, negative/background, and unknown/exclude/review-needed pathways. Ambiguous pixels or regions should not be forced into positive or negative classes.

### Output contract

Future CV or baseline outputs must remain mask-first and traceable. Model outputs, baseline outputs, and official/reference source outputs must remain separated.

### Imagery assumptions

Imagery remains a Phase Two feasibility question. Candidate categories include Sentinel-2 MSI, Landsat Collection 2 Level-2, NASA FIRMS / MODIS / VIIRS active-fire products, harmonized Landsat/Sentinel sources, and public sample imagery if needed for prototype scaffolding.

No final imagery source, AOI tile, band set, cloud mask, preprocessing method, or data-access path has been selected yet.

### Label assumptions

Future labels may be reference-derived, weak, manually reviewed, or baseline-derived. Active-fire products may support reference, baseline, weak-label, sampling, or comparison logic, but must not be treated as pixel-perfect ground-truth segmentation masks.

### Baseline comparison plan

Future BurnLens model outputs must be compared against simpler non-model baselines before making any model-value claim.

Candidate baselines include all-background, class-prior/random, FIRMS reference-display, FIRMS buffer/raster, simple spectral/threshold if supported, and burn-scar fallback only if the target changes.

### Model family decision

The first model family is **U-Net-style binary semantic segmentation**.

This decision is documentation-only. It does not authorize model code, architecture implementation, weights, training, inference, metrics computation, model-card completion, or public demo claims.

Fallback families include DeepLabV3-style segmentation, FCN-style segmentation, lightweight encoder-decoder CNN, or a baseline-only path if Phase Two data and labels are not defensible enough to train a model.

### Evaluation metrics plan

Future evaluation will use **IoU / Jaccard** as the primary segmentation metric.

Supporting metrics include Dice / F1, precision, recall, false-positive review, false-negative review, positive-area difference, per-scene or per-tile summaries, and component or polygon quality once vectorization exists.

Unknown, exclude, review-needed, nodata, or quality-masked regions must not be silently treated as background. They must be excluded from metric computation or reported separately with an explicit ignore value or mask rule.

Every future model metric must be reported against at least one relevant baseline.

### Known failure modes

Future BurnLens work must explicitly track imagery/source-quality, reference/label, baseline/model, geospatial-processing, evaluation/metric, and communication/use-boundary failure modes.

Required responses include flag, review, exclude, or stop. Unknown or excluded areas must not be silently treated as background.

Examples include cloud, cloud shadow, smoke or haze, bright bare ground, roads or rooftops, water or glare, snow or ice, sensor saturation, nodata, terrain occlusion, low spatial resolution, mixed pixels, stale imagery, hotspot point uncertainty, label noise, class imbalance, CRS mismatch, raster-grid mismatch, threshold sensitivity, and official-use confusion risk.

### CV-specific use boundaries

Future BurnLens CV outputs are experimental portfolio artifacts only.

They may be used for portfolio demonstration, methods explanation, reproducibility demonstration, non-operational screening examples, error analysis, and case-study storytelling.

They must not be used for emergency alerts, evacuation decisions, routing or road-closure guidance, tactical fire decisions, incident command, property-level hazard determinations, insurance/legal/regulatory decisions, official map replacement, or standalone public interpretation.

Every future map, screenshot, report, model card, public site card, or run package must include visible warning language such as: **Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.**

## Final handoff artifact

The final Objective Two closeout artifact is:

```text
docs/phase-one/objective-two/OBJECTIVE_TWO_FINAL_HANDOFF.md
```

That artifact should be treated as the Objective Two transition record for the next objective.

## Still in scope for the next objective

The next objective should begin turning these scope decisions into data/source feasibility and research records, while preserving Objective Two boundaries.

Recommended next-objective focus:

> Determine which imagery, reference products, AOI constraints, and data-access paths are feasible for the locked binary segmentation task.

## Phase boundary

Do not start data ingestion, final AOI tile selection, imagery download, label creation, dataset splitting, baseline generation, model training, inference, or website demo integration until a later objective explicitly authorizes the relevant work.

## Persistent source-precedence rule

Official sources govern. BurnLens outputs are experimental portfolio artifacts.
