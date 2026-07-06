# P1O2-T09 — Evaluation Metrics Plan

## Status

Phase 1 / Objective Two task artifact.

This document defines the future evaluation metrics plan for BurnLens Deschutes. It does not compute metrics, build an evaluation dataset, train a model, run inference, complete a model card, or approve a public performance claim.

## Applies to

Current Objective Two decisions:

- CV task: experimental binary semantic segmentation for wildfire-relevant screening
- Primary target: active-fire / hotspot-informed binary fire mask
- Fallback target: burn-scar binary mask if active-fire label feasibility fails
- Output contract: mask-first, traceable output that can later become georeferenced raster, vector polygons, map overlay, exposure-style summary, and run package
- Baseline rule: future model outputs must be compared against simpler non-model baselines before any model-value claim
- Model family: U-Net-style binary semantic segmentation, documentation-only at this stage

## Evaluation question

The evaluation plan answers:

> Does a future BurnLens segmentation model produce a defensible binary mask that improves on simpler baselines without hiding uncertainty, unknown regions, label weakness, or operational limitations?

This is not a plan to prove that the model is operationally accurate. It is a plan to evaluate whether a portfolio model is honest, inspectable, and useful enough to demonstrate the CV-to-GEOINT workflow.

## Primary metric

### IoU / Jaccard

**IoU / Jaccard** is the primary quantitative segmentation metric.

Reason:

- It directly measures overlap between predicted positive regions and evaluation/reference positive regions.
- It penalizes both false positives and false negatives.
- It fits a binary mask task better than plain accuracy, especially when positive pixels are sparse.
- It provides a simple comparison point against non-model mask baselines.

Minimum reporting requirement:

```text
primary_metric: IoU / Jaccard
positive_class: fire-relevant / target-positive
average: binary or positive-class only
threshold: documented if probability output is used
exclude_value: documented if unknown/exclude mask exists
zero_division_policy: documented
```

## Supporting quantitative metrics

| Metric | Required? | Purpose |
|---|---:|---|
| Dice / F1 | Yes | Complements IoU and helps communicate positive-class overlap under class imbalance. |
| Precision | Yes | Measures how much predicted positive area is actually supported by the evaluation reference. Useful for overprediction review. |
| Recall | Yes | Measures how much reference positive area is recovered. Useful for missed-positive review. |
| False-positive count or area | Yes | Documents over-detection and likely misleading positives. |
| False-negative count or area | Yes | Documents missed positive regions. |
| Positive-area difference | Yes | Compares predicted positive area with baseline/reference positive area. |
| Component or polygon count | Conditional | Required once raster-to-vector conversion exists. Helps identify noisy fragmentation or over-smoothing. |
| Calibration or confidence summary | Conditional | Required only if probability/confidence rasters are produced. |
| Per-scene/per-tile summary | Yes | Prevents aggregate metrics from hiding failures on difficult scenes. |

## Metrics not sufficient by themselves

These metrics must not be used alone:

| Metric | Why insufficient |
|---|---|
| Accuracy | Can be misleading when most pixels are background. |
| Overall positive area only | Does not show whether the model found the right locations. |
| Visual quality only | Can hide false positives, false negatives, and label leakage. |
| Single aggregate score only | Can hide poor performance on clouds, smoke, shadows, bright surfaces, or low-confidence labels. |

## Unknown and exclude handling

BurnLens must preserve the label pathway defined earlier:

| Value | Class | Metric handling |
|---:|---|---|
| 1 | Positive / fire-relevant | Included as the positive class. |
| 0 | Negative / background | Included as background. |
| 255 or null | Unknown / exclude / review needed | Excluded from metric computation or reported separately. |

Unknown or excluded regions must never be silently treated as background.

Before any metric is computed, the evaluation run must document:

- exclude value or mask path
- number or area of excluded pixels
- reason for exclusion
- whether exclusions came from labels, source quality, cloud/smoke masks, georegistration issues, nodata, or manual review
- whether baseline and model outputs used the same exclusion rules

## Threshold policy

If a future model outputs probabilities or logits, the threshold used to convert probability to binary mask must be documented.

Minimum threshold metadata:

```text
probability_output: true_or_false
threshold: numeric_value
threshold_selection_method: fixed_default | validation_selected | baseline_matched | other_documented_reason
threshold_scope: global | per_model | per_dataset | other_documented_scope
```

Do not tune a threshold on the final evaluation set and then present the result as held-out performance.

## Baseline comparison requirement

Every future model metric must be reported beside at least one relevant baseline from `BASELINE_COMPARISON_PLAN.md`.

Minimum comparison table:

| Run | Output type | IoU/Jaccard | Dice/F1 | Precision | Recall | FP area | FN area | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---|
| baseline | non-model | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| model | U-Net-style segmentation | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

The model should not be described as adding value unless it improves quantitative or qualitative evidence over the baseline without creating misleading artifacts.

## Qualitative review requirements

Future evaluation reports must include qualitative review, not just metrics.

Required qualitative checks:

- side-by-side input imagery, reference/evaluation mask, baseline output, and model output
- false-positive examples
- false-negative examples
- ambiguous or excluded-region examples
- cloud, smoke, shadow, glare, bare ground, water, road, rooftop, and bright-soil failure cases when present
- map-readability review after georeferencing or vectorization exists
- explanation of whether model output improves clarity or only adds complexity

## Spatial and geospatial checks

When georeferenced outputs exist, evaluation must include spatial checks:

- CRS and transform consistency
- pixel grid alignment
- raster dimensions
- nodata handling
- resampling method
- source timestamp compatibility
- AOI version
- vectorization tolerance if polygons are generated

Do not compute model-vs-reference overlap if rasters are misaligned or source dates are incompatible.

## Split and leakage rules

Future evaluation must document how data were split.

Minimum split metadata:

- train/validation/test split method
- scene IDs or tile IDs in each split
- source dates in each split
- AOI version
- whether adjacent tiles could leak information
- whether weak labels were derived from the same baseline being compared
- whether baseline parameters were tuned on the evaluation set

Stop if the evaluation split is not documented.

## Reporting levels

Metrics should be reported at three levels when data allows:

| Level | Purpose |
|---|---|
| Dataset-level | Overall comparison across the evaluation set. |
| Scene/tile-level | Reveals difficult cases hidden by aggregate scores. |
| Failure-mode subset | Shows performance under clouds, smoke, shadows, bright surfaces, low confidence, or other known issues. |

## Minimum future run report fields

A future evaluation run report should include:

| Field | Meaning |
|---|---|
| `run_id` | Evaluation run identifier. |
| `model_version` | Model version, if evaluating a model. |
| `baseline_version` | Baseline version being compared. |
| `dataset_version` | Dataset version. |
| `label_schema_version` | Label schema version. |
| `aoi_version` | AOI version. |
| `source_commit` | Code commit used for evaluation. |
| `threshold` | Threshold used for probability-to-mask conversion. |
| `ignore_index` | Exclude value, if used. |
| `metric_versions` | Library or metric implementation versions. |
| `source_dates` | Imagery/reference dates. |
| `limitations` | Evaluation caveats. |

## Research basis

This plan is informed by current metric documentation:

- scikit-learn defines Jaccard similarity as intersection divided by union of label sets.
- scikit-learn defines precision as true positives divided by true positives plus false positives, recall as true positives divided by true positives plus false negatives, and F-score as a weighted harmonic mean of precision and recall.
- TorchMetrics provides binary Jaccard support with thresholding and `ignore_index`, which maps well to probability-to-mask conversion and unknown/exclude handling.

## Model-value interpretation

A future model adds value only if:

- it is compared against a relevant baseline
- IoU/Jaccard and supporting metrics improve or reveal a useful tradeoff
- false positives and false negatives are documented
- unknown/exclude areas are handled transparently
- the output remains map-readable and source-precedence compliant
- limitations are clear enough for a portfolio viewer to understand what the model is not

If the baseline is stronger, clearer, or more defensible than the model, BurnLens should say so.

## Stop conditions

Do not report model performance if:

- label schema version is missing
- dataset version is missing
- evaluation split is missing
- baseline comparison is missing
- unknown/exclude regions are silently treated as background
- threshold is undocumented
- source dates are incompatible
- raster grids are misaligned
- evaluation labels are circularly derived from the baseline being tested without disclosure
- metrics are computed only on easy cases
- a single score is used to imply operational reliability

## Phase boundary

This task does not authorize:

- metric computation
- evaluation dataset creation
- data ingestion
- label creation
- model training
- inference
- model card completion
- public performance claims

Those belong to later objectives or phases.

## Use boundary

Future BurnLens evaluation outputs are experimental portfolio artifacts only. They are not official wildfire information, emergency guidance, evacuation routing, incident command support, or field-validated hazard assessment.

Official sources govern when information differs.

## Acceptance checklist

- [x] Primary metric defined.
- [x] Supporting metrics defined.
- [x] Metrics tied to binary semantic segmentation.
- [x] Unknown/exclude handling preserved.
- [x] Threshold policy documented.
- [x] Baseline comparison requirement preserved.
- [x] Qualitative review expectations defined.
- [x] Stop conditions documented.
- [x] Source precedence and non-operational boundaries preserved.
- [x] Phase boundary preserved: no metrics computed, no evaluation set built, no training, no inference, no model card completion.
