# Phase 1 / Objective Two Final Handoff

## Objective status

**Objective Two is complete.**

Objective Two defined BurnLens Deschutes' first computer vision task tightly enough that later Phase One objectives and Phase Two data, label, baseline, and model work can proceed without ambiguity, scope creep, or operational overclaiming.

This handoff is documentation-only. It does not authorize data ingestion, imagery download, AOI tile selection, label creation, baseline generation, model training, inference, metric computation, model-card completion, website demo integration, or public performance claims.

## Objective Two purpose

Objective Two answers:

> What exactly is the first BurnLens computer vision task, what should it output, how should it be evaluated, what can go wrong, and what boundaries must govern future model or baseline outputs?

The result is a constrained, transparent, portfolio-safe CV task definition.

## Completed task index

| Task | Issue | PR | Artifact | Result |
|---|---:|---:|---|---|
| P1O2-T01 — Define CV task | #7 | #8 | `CV_TASK_DEFINITION.md` | Locked binary semantic segmentation as the first CV task type. |
| P1O2-T02 — Choose first segmentation target | #9 | #10 | `TARGET_CLASS_DECISION.md` | Selected active-fire / hotspot-informed binary fire mask as the first target. |
| P1O2-T03 — Define positive, negative, and ambiguous classes | #11 | #12 | `CLASS_DEFINITIONS.md` | Defined positive, negative/background, and unknown/exclude handling. |
| P1O2-T04 — Define model output contract | #15 | #16 | `CV_OUTPUT_CONTRACT.md` | Locked mask-first output contract and source/model/baseline separation. |
| P1O2-T05 — Define imagery assumptions | #17 | #18 | `IMAGERY_ASSUMPTIONS.md` | Kept imagery source, bands, AOI tiles, and preprocessing as Phase Two feasibility questions. |
| P1O2-T06 — Define label assumptions | #19 | #20 | `LABEL_ASSUMPTIONS.md` | Defined weak/reference/manual/baseline-derived label assumptions without treating active-fire products as pixel-perfect masks. |
| P1O2-T07 — Define baseline comparison plan | #23 | #44 | `BASELINE_COMPARISON_PLAN.md` | Required future models to be compared against simpler non-model baselines before value claims. |
| P1O2-T08 — Define first model family | #46 | #58 | `MODEL_FAMILY_DECISION.md` | Selected U-Net-style binary semantic segmentation as the first model family for future planning. |
| P1O2-T09 — Define evaluation metrics plan | #61 | #68 | `EVALUATION_METRICS_PLAN.md` | Selected IoU/Jaccard as the primary metric with supporting metrics and exclusion-mask rules. |
| P1O2-T10 — Define known failure modes | #70 | #77 | `FAILURE_MODES.md` | Defined imagery, label, model, geospatial, metric, and communication failure modes. |
| P1O2-T11 — Define CV-specific use boundaries | #79 | #81 | `CV_USE_BOUNDARIES.md` | Locked allowed/prohibited uses and required visible warning language. |
| P1O2-T12 — Create Objective Two final handoff | #83 | #84 | `OBJECTIVE_TWO_FINAL_HANDOFF.md` | Closed Objective Two and prepared transition to the next objective. |

## Locked CV task

BurnLens Deschutes' first computer vision task is:

> **Experimental binary semantic segmentation for wildfire-relevant screening.**

The task is image-to-mask, not scene classification, object detection, spread prediction, evacuation analysis, or incident support.

The locked technical chain remains:

```text
imagery → preprocessing → segmentation or baseline mask → raster output → vector polygons → map overlay → exposure-style summary → documented run package
```

## Locked target

Primary target:

> **Active-fire / hotspot-informed binary fire mask.**

Fallback target:

> **Burn-scar binary mask.**

The fallback may be used only if Phase Two shows active-fire / hotspot-informed labels are too weak, sparse, noisy, misaligned, or otherwise indefensible for a portfolio model. Changing to the fallback target requires a documented decision update.

## Locked class handling

Future label logic must preserve at least three pathways:

| Path | Meaning | Rule |
|---|---|---|
| Positive | Fire-relevant / target-positive | May be included as positive class. |
| Negative / background | Not target-positive under current label rules | May be included as background. |
| Unknown / exclude / review-needed | Ambiguous, invalid, obscured, low-confidence, nodata, or quality-masked region | Must not be silently treated as background. |

Unknown/exclude/review-needed regions must be masked out of metrics or reported separately with explicit rules.

## Locked output contract

Future CV or baseline output must be mask-first and traceable.

Expected future flow:

```text
input tile
→ predicted or baseline binary/probability mask
→ georeferenced raster output
→ optional vector polygons
→ map overlay
→ exposure-style summary
→ documented run package
```

Future outputs must distinguish official/reference sources, reference-derived labels, baseline outputs, model outputs, map overlays, and portfolio interpretations.

## Imagery and label assumptions

Imagery remains a Phase Two feasibility question. Candidate categories include Sentinel-2 MSI, Landsat Collection 2 Level-2, NASA FIRMS / MODIS / VIIRS active-fire products, harmonized Landsat/Sentinel sources, and public sample imagery if needed for prototype scaffolding.

No final imagery source, AOI tile, band set, cloud mask, preprocessing method, or data-access path has been selected by Objective Two.

Future labels may be reference-derived, weak, manually reviewed, baseline-derived, or excluded/unknown where evidence is insufficient. Active-fire/hotspot products may support reference, baseline, weak-label, sampling, or comparison logic, but must not be treated as pixel-perfect ground-truth segmentation masks unless separately validated.

## Baseline comparison requirement

Future model outputs must be compared against simpler non-model baselines before any model-value claim.

Candidate baselines include all-background, class-prior/random, FIRMS reference-display, FIRMS buffer/raster, simple spectral/threshold if supported by data feasibility, and burn-scar fallback baseline only if the target changes.

The baseline question is:

> Does a future BurnLens segmentation model add measurable, inspectable, portfolio-relevant value beyond simpler non-model approaches for the same AOI, source window, task definition, and label assumptions?

## Model family decision

The first model family is:

> **U-Net-style binary semantic segmentation.**

This is a future implementation-planning decision only. It does not authorize model code, architecture implementation, dependency selection, weights, training, inference, metric computation, model-card completion, or public performance claims.

Fallback families include DeepLabV3-style segmentation, FCN-style segmentation, lightweight encoder-decoder CNN, or a baseline-only path if data and labels are not defensible enough to train a model.

## Evaluation metrics plan

Future evaluation will use:

> **IoU / Jaccard as the primary segmentation metric.**

Supporting metrics and checks include Dice/F1, precision, recall, false-positive review, false-negative review, positive-area difference, per-scene or per-tile summaries, component/polygon quality once vectorization exists, and qualitative failure-mode review.

Every future model metric must be reported against at least one relevant baseline. Unknown, exclude, review-needed, nodata, or quality-masked regions must not be silently treated as background.

## Known failure modes

Future work must explicitly track imagery/source-quality, reference/label, baseline/model, geospatial-processing, evaluation/metric, and communication/use-boundary failure modes.

Required responses are:

| Response | Meaning |
|---|---|
| Flag | Keep the scene/output but mark the risk in manifest or report. |
| Review | Require qualitative inspection before interpretation. |
| Exclude | Remove affected pixels, areas, scenes, or runs from metrics when invalid. |
| Stop | Do not proceed until the issue is resolved. |

Example risks include cloud, cloud shadow, smoke/haze, bright bare ground, roads/rooftops, water/glare, snow/ice, sensor saturation, nodata, terrain occlusion, low spatial resolution, mixed pixels, stale imagery, hotspot point uncertainty, label noise, class imbalance, CRS mismatch, raster-grid mismatch, threshold sensitivity, and official-use confusion risk.

## CV-specific use boundaries

Future BurnLens CV outputs are experimental portfolio artifacts only.

Allowed uses include portfolio demonstration, methods explanation, reproducibility demonstration, non-operational screening examples, error analysis, and case-study storytelling.

Prohibited uses include emergency alerts, evacuation decisions, routing or road-closure guidance, tactical fire decisions, incident command, property-level hazard determinations, insurance/legal/regulatory decisions, official map replacement, and standalone public interpretation.

Required visible warning language:

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

Short warning for constrained UI surfaces:

```text
Experimental CV output — official sources govern.
```

## Persistent source-precedence rule

Official sources govern.

BurnLens outputs are experimental portfolio artifacts and must not override, replace, or appear equivalent to county, state, federal, fire-service, emergency-management, transportation, air-quality, or incident sources.

## Versioning and traceability expectations for later work

Future data, baseline, model, evaluation, run, map, or portfolio artifacts should remain traceable to repository commit, repo/app version, AOI version where relevant, dataset version where relevant, label schema version where relevant, baseline version where relevant, model version where relevant, source imagery/reference metadata, run ID, timestamp, warning flags, and limitations.

No public output should be portfolio-ready unless it can be traced.

## Phase boundary after Objective Two

Objective Two does not authorize data ingestion, final AOI tile selection, imagery download, label creation, dataset splitting, baseline generation, model code, model training, inference, metric computation, model-card completion, website demo integration, or public performance claims.

Those remain future work.

## Recommended next objective

The next objective should begin turning these scope decisions into data/source feasibility and research records, while still avoiding premature implementation.

Recommended next-objective focus:

> Determine which imagery, reference products, AOI constraints, and data-access paths are feasible for the locked binary segmentation task.

Recommended first next-objective tasks:

1. Create the next objective tracker issue.
2. Define candidate data/source feasibility criteria.
3. Inventory source access paths for Sentinel-2, Landsat, FIRMS, and allowed public sample imagery.
4. Define AOI tile-selection criteria without downloading imagery yet, unless the next objective explicitly authorizes source testing.
5. Update research validation logs and claims register.
6. Preserve all Objective Two boundaries in any future data decision.

## Objective Two completion checklist

- [x] CV task defined.
- [x] First target selected.
- [x] Class handling defined.
- [x] Output contract defined.
- [x] Imagery assumptions defined.
- [x] Label assumptions defined.
- [x] Baseline comparison plan defined.
- [x] First model family selected.
- [x] Evaluation metrics plan defined.
- [x] Known failure modes defined.
- [x] CV-specific use boundaries defined.
- [x] Final handoff created.

## Final closeout statement

Objective Two is complete.
