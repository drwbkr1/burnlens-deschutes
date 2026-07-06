# P1O2-T07 — Baseline Comparison Plan

## Status

Phase 1 / Objective Two task artifact.

This document defines how BurnLens Deschutes will compare future model outputs against non-model baselines. It does not generate a baseline, ingest data, train a model, run inference, or build an evaluation dataset.

## Applies to

Current Objective Two decisions:

- CV task: experimental binary semantic segmentation for wildfire-relevant screening
- Primary target: active-fire / hotspot-informed binary fire mask
- Fallback target: burn-scar binary mask if active-fire label feasibility fails
- Class handling: positive, negative/background, and unknown/exclude/review-needed
- Output contract: mask-first, traceable output that can later become georeferenced raster, polygons, map overlay, exposure-style summary, and run package
- Imagery and labels: still Phase Two feasibility questions

## Baseline comparison purpose

The baseline comparison exists to answer one question:

> Does a future BurnLens segmentation model add measurable, inspectable, and portfolio-relevant value beyond simpler non-model approaches for the same AOI, source window, task definition, and label assumptions?

A model should not be considered useful just because it produces a visually interesting mask. It should be compared against simple alternatives that are cheaper, more transparent, or closer to public reference information.

## What counts as a baseline

A baseline is a non-model or minimally learned comparison method used to contextualize future model performance. It is not an official source and not ground truth unless separately justified.

BurnLens should keep three categories separate:

| Category | Description | Example |
|---|---|---|
| Reference product | Public or official source used for context, sampling, or comparison. | NASA FIRMS active-fire detections. |
| Baseline output | Derived non-model layer created from a documented rule. | Buffered or rasterized FIRMS points. |
| Model output | Future output from a trained BurnLens segmentation model. | U-Net-style predicted binary mask. |

A reference product can be used to create a baseline, but once transformed, the result must be labeled as a BurnLens-derived baseline output.

## Candidate baselines

Phase Two or Phase Three should evaluate these baselines in order, only where the data supports them.

| Baseline | Description | Why it matters | Phase status |
|---|---|---|---|
| All-background sanity baseline | Predict every pixel as negative/background. | Detects whether class imbalance makes a naive result look deceptively strong. | Define now; compute later. |
| Class-prior/random sanity baseline | Predict positives according to observed label prevalence or a simple random strategy. | Provides a low-information reference point. | Define now; compute later if useful. |
| FIRMS reference-display baseline | Display active-fire/hotspot points directly as reference context without model inference. | Tests whether the portfolio could simply show public fire detections rather than building CV. | Define now; execute later. |
| FIRMS buffer/raster baseline | Buffer or rasterize FIRMS detections into a mask-like output with documented parameters. | Gives the model a practical non-ML mask baseline to beat or clarify. | Define now; execute later. |
| Simple spectral/threshold baseline | Use a documented threshold or rule from selected imagery bands, only if Phase Two source feasibility supports it. | Tests whether simple image rules outperform or explain the model. | Conditional. |
| Burn-scar fallback baseline | If target changes to burn scar, compare against simple burned-area or index-derived mask logic. | Prevents fallback scope from becoming model-first. | Conditional fallback only. |

## Baselines not allowed in Objective Two

Objective Two does not authorize:

- downloading FIRMS data
- rasterizing points
- buffering hotspots
- selecting imagery bands
- creating threshold masks
- creating evaluation labels
- computing metrics
- training or testing a model

This document only defines the comparison plan.

## Research basis

Scikit-learn documents `DummyClassifier` as a classifier that makes predictions using simple rules and ignores input features. This supports including all-background, class-prior, or random sanity baselines before interpreting future model performance.

Scikit-learn defines Jaccard score as the size of the intersection divided by the size of the union of label sets, which aligns with IoU-style segmentation comparison. Scikit-learn also documents precision, recall, F-score, and support as classification metrics for evaluating binary prediction tradeoffs.

NASA FIRMS provides active-fire/hotspot information from MODIS and VIIRS, including near-real-time products. FIRMS documentation also notes that MODIS detections represent the center of a 1 km pixel and VIIRS detections represent the center of a 375 m pixel, which supports using FIRMS as reference or baseline evidence but not treating it as a pixel-perfect segmentation mask.

Research references:

- Scikit-learn DummyClassifier: https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html
- Scikit-learn Jaccard score: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.jaccard_score.html
- Scikit-learn precision/recall/F-score support: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html
- NASA FIRMS documentation: https://www.earthdata.nasa.gov/data/tools/firms

## Minimum future comparison metrics

Future comparison should include both quantitative and qualitative review.

Minimum quantitative metrics:

| Metric | Purpose |
|---|---|
| IoU / Jaccard | Measures overlap between predicted positive regions and reference/evaluation mask. |
| Dice / F1 | Measures overlap with sensitivity to class imbalance. |
| Precision | Measures how often predicted positive regions are actually positive under the evaluation rule. |
| Recall | Measures how much of the positive reference/evaluation area is recovered. |
| False positives | Documents over-detection, especially bright ground, roofs, roads, glare, or non-fire heat-like features. |
| False negatives | Documents missed positive regions, especially small or partially obscured fire-relevant areas. |
| Positive area difference | Compares predicted positive area against baseline/reference-derived positive area. |
| Component/polygon count difference | Flags fragmented, noisy, or over-smoothed outputs after vectorization. |

Metrics should not be reported without the data version, label schema version, baseline version, model version, run ID, and exclusion rules.

## Minimum qualitative checks

Future comparison should also include qualitative inspection:

- Does the model merely reproduce the baseline buffer shape?
- Does the model hallucinate positives where no plausible reference or image evidence exists?
- Does the model miss obvious reference-supported positives?
- Are errors concentrated around clouds, smoke, shadows, glare, roads, roofs, water, or bright soil?
- Does the output remain map-readable after raster-to-vector conversion?
- Does the output improve the eventual portfolio case study beyond simply showing public reference data?
- Are uncertainty and limitations clear enough for a viewer to understand what the output is not?

## Model-value test

A future model provides value only if at least one of these is true and documented:

1. It improves quantitative overlap metrics over the selected baseline without creating unacceptable false positives.
2. It produces map-ready masks that are more spatially useful than a direct reference-display or buffer/raster baseline.
3. It identifies interpretable image patterns that a simple baseline misses, while preserving uncertainty and caveats.
4. It supports a clearer portfolio demonstration of CV-to-GEOINT workflow than a baseline alone.
5. It exposes useful failure modes that demonstrate technical honesty and responsible limitation handling.

If none of these are true, the portfolio should state that the baseline is sufficient for the current scope and should not overstate the model.

## Baseline-version requirements

Every future baseline output should have a version and manifest entry.

Recommended baseline version pattern:

```text
burnlens-baseline-firms-buffer-v0.1.0
burnlens-baseline-all-background-v0.1.0
burnlens-baseline-spectral-threshold-v0.1.0
```

Minimum baseline metadata:

| Field | Meaning |
|---|---|
| `baseline_version` | Versioned baseline identifier. |
| `baseline_type` | all-background, class-prior, FIRMS-display, FIRMS-buffer, spectral-threshold, or fallback. |
| `source_name` | Source product used, if any. |
| `source_datetime` | Source time/date, if available. |
| `parameters` | Buffer radius, threshold, class prior, random seed, CRS, grid size, or other rule parameters. |
| `aoi_version` | AOI version used. |
| `dataset_version` | Dataset version, if applicable. |
| `label_schema_version` | Label schema version, if applicable. |
| `created_at` | Processing timestamp. |
| `source_commit` | Git commit used to create it. |
| `warning_flags` | Stale source, cloud/smoke issue, low confidence, alignment issue, or similar. |

## Stop conditions

Do not compare model and baseline outputs if:

- labels are not versioned
- source dates are incompatible
- CRS/georeferencing does not align
- unknown/exclude regions are silently treated as negatives
- baseline parameters are missing
- model version or baseline version is missing
- run ID is missing
- evaluation set contains leakage from training data
- metrics exclude difficult cases without documenting why

## Portfolio language

Allowed:

> BurnLens compares a future segmentation model against simple reference-derived and non-model baselines to test whether model outputs add value beyond public fire detections or simple mask rules.

Not allowed:

> BurnLens proves model outputs are more accurate than official wildfire data.

> BurnLens replaces FIRMS, county wildfire information, emergency management data, or incident products.

> BurnLens provides emergency-ready active-fire detection.

## Use boundary

Baseline and model outputs are experimental portfolio artifacts. They are not official wildfire information, not emergency guidance, not evacuation routing, not incident command support, and not field-validated hazard assessments.

Official sources govern when information differs.

## Acceptance checklist

- [x] Purpose of baseline comparison defined.
- [x] Candidate baselines identified without generating them.
- [x] Reference products, baseline outputs, and model outputs separated.
- [x] Evidence threshold for future model value defined.
- [x] Minimum metrics and qualitative checks defined.
- [x] Baseline versioning and metadata requirements defined.
- [x] Source precedence and non-operational boundaries preserved.
- [x] Phase boundary preserved: no baseline generation, data ingestion, model training, inference, or evaluation dataset build.
