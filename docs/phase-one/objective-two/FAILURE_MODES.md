# P1O2-T10 — Known Failure Modes

## Status

Phase 1 / Objective Two task artifact.

This document defines known failure modes for future BurnLens Deschutes data, baseline, model, evaluation, and communication work. It does not ingest data, select imagery, create labels, train a model, run inference, compute metrics, or publish a map.

## Applies to

Current Objective Two decisions:

- CV task: experimental binary semantic segmentation for wildfire-relevant screening
- Primary target: active-fire / hotspot-informed binary fire mask
- Fallback target: burn-scar binary mask if active-fire label feasibility fails
- Output contract: mask-first, traceable output that can later become georeferenced raster, vector polygons, map overlay, exposure-style summary, and run package
- Baseline rule: future model outputs must be compared against simpler non-model baselines before any model-value claim
- Model family: U-Net-style binary semantic segmentation, documentation-only at this stage
- Evaluation primary metric: IoU / Jaccard, supported by Dice/F1, precision, recall, false-positive review, false-negative review, area difference, and qualitative review

## Purpose

The purpose of this document is to prevent BurnLens from treating future segmentation outputs as more reliable than the data, labels, model, and geospatial workflow can support.

Known failure modes should be tracked before implementation so that later phases can flag them in manifests, exclude them from evaluation when appropriate, and explain them clearly in portfolio materials.

## Failure-mode categories

BurnLens failure modes are grouped into six categories:

1. imagery and source-quality failure modes
2. reference and label failure modes
3. baseline and model failure modes
4. geospatial processing failure modes
5. evaluation and metric failure modes
6. communication and use-boundary failure modes

A future run may contain more than one failure mode at the same time.

## Imagery and source-quality failure modes

| Failure mode | How it can affect BurnLens | Required response |
|---|---|---|
| Cloud cover | Obscures surface evidence and may create false negatives or invalid labels. | Flag, mask, exclude, or document. |
| Cloud shadow | Can look like burned or darkened ground. | Flag, inspect, and avoid treating as target-positive without evidence. |
| Smoke or haze | Can obscure fire-relevant pixels or distort spectral values. | Flag and document as uncertain; exclude if severe. |
| Bright bare soil or rock | Can be confused with heat, flame-like brightness, or burn-related features. | Include in false-positive review. |
| Roads, rooftops, and built surfaces | May create bright or high-contrast artifacts that look fire-relevant. | Include in negative examples and false-positive review. |
| Water or glare | Can distort brightness and spectral signatures. | Flag where source QA supports it; inspect manually when needed. |
| Snow or ice | Can confuse thresholding, segmentation, or reference interpretation. | Mask or flag where source QA supports it. |
| Sensor saturation | Saturated pixels may hide useful signal or create false positives. | Flag and exclude if saturation affects target area. |
| Nodata, dropped pixels, or fill pixels | Missing pixels can create invalid masks or misleading evaluation. | Exclude from metrics and document. |
| Terrain occlusion or topographic shadow | Terrain can block or darken features. | Flag and avoid unsupported positive/negative assignment. |
| Low spatial resolution | Fire-relevant signals may be smaller than the pixel footprint. | Document source resolution and avoid pixel-perfect claims. |
| Mixed pixels | A single pixel may contain fire, vegetation, soil, smoke, or structures. | Treat as uncertain where label evidence is weak. |
| Stale imagery | Imagery and reference detections may describe different times. | Document source timestamps; stop comparison if incompatible. |

## Reference and label failure modes

| Failure mode | How it can affect BurnLens | Required response |
|---|---|---|
| Hotspot point is not a perimeter | A FIRMS-style point does not define a fire boundary or segmentation mask. | Do not treat points as ground-truth polygons. |
| Pixel-center mismatch | Active-fire point locations may represent pixel centers, not exact fire locations. | Preserve uncertainty when converting points to masks. |
| Weak-label circularity | A baseline created from a reference product may later be mistaken for independent ground truth. | Separate reference, baseline, and evaluation labels. |
| Label sparsity | Positive examples may be rare, especially for active-fire targets. | Track class imbalance and avoid accuracy-only claims. |
| Label noise | Reference-derived labels may include false detections or missed detections. | Use review flags and document label source quality. |
| Ambiguous regions | Some regions may be impossible to label confidently. | Use unknown/exclude handling, not forced positive or negative classes. |
| Timing mismatch | Labels and imagery may not represent the same fire state. | Document timestamps and stop evaluation if mismatch is too large. |
| Inconsistent label rules | Label criteria may change across scenes or runs. | Require label schema versioning. |
| Negative-label contamination | Background regions may actually contain unobserved target evidence. | Treat hard negatives cautiously and review samples. |
| Fallback-target drift | Burn-scar fallback could blur the original active-fire task. | Require a separate decision record if target changes. |

## Baseline and model failure modes

| Failure mode | How it can affect BurnLens | Required response |
|---|---|---|
| All-background collapse | Model predicts background everywhere due to class imbalance. | Compare against null baseline and report recall. |
| Overprediction | Model predicts too much target-positive area. | Report precision, false-positive area, and examples. |
| Underprediction | Model misses real or reference-supported positives. | Report recall, false-negative area, and examples. |
| Baseline imitation | Model simply reproduces a buffer/raster baseline without learning image evidence. | Compare outputs visually and quantitatively against baseline. |
| False confidence | Probability output appears authoritative without calibration or caveats. | Require threshold metadata and limitations. |
| Generalization failure | Model performs only on one source, AOI, season, or scene type. | Report per-scene and failure-mode subset results. |
| Pretrained-input mismatch | Pretrained encoders may expect RGB-style inputs while BurnLens may use multispectral bands. | Document band compatibility before implementation. |
| Class imbalance distortion | Sparse positives can make weak performance appear strong under some metrics. | Use IoU, Dice/F1, precision, recall, and false-positive/false-negative review. |
| Threshold sensitivity | Small threshold changes may produce very different masks. | Document threshold choice and do not tune on final evaluation. |
| Training/evaluation leakage | Adjacent tiles or derived labels may leak information. | Document splits and stop if leakage cannot be ruled out. |

## Geospatial processing failure modes

| Failure mode | How it can affect BurnLens | Required response |
|---|---|---|
| CRS mismatch | Outputs may not align with source imagery or reference layers. | Validate CRS before comparison or overlay. |
| Raster grid mismatch | Different resolution, transform, or extent can corrupt overlap metrics. | Require grid alignment checks. |
| Resampling artifacts | Resampling may blur, enlarge, shrink, or shift target masks. | Document resampling method. |
| Vectorization artifacts | Raster-to-vector conversion can create noisy fragments or over-smoothed polygons. | Report component/polygon counts once vectorization exists. |
| Nodata propagation failure | Nodata may become background or target-positive by mistake. | Preserve nodata/exclude masks. |
| AOI boundary clipping | Clipped outputs may hide false positives or false negatives. | Document AOI version and clipping logic. |
| Timestamp mismatch across layers | Different layers may represent different moments. | Record source dates and stop if incompatible. |
| Scale mismatch | A useful raster may become misleading when shown at an inappropriate map scale. | Include map-readability review. |

## Evaluation and metric failure modes

| Failure mode | How it can affect BurnLens | Required response |
|---|---|---|
| Accuracy-only reporting | Background dominance can make results look better than they are. | Do not use accuracy as the primary metric. |
| Single-score overclaiming | One aggregate score can hide local failures. | Report scene/tile summaries and qualitative examples. |
| Ignore-mask misuse | Unknown/exclude pixels could be treated as background. | Use explicit ignore value or mask rule. |
| Easy-case filtering | Removing hard scenes can inflate performance. | Document all exclusions and failure-mode subsets. |
| Baseline omission | Model may look useful without simpler comparison. | Require at least one relevant baseline comparison. |
| Unclear thresholding | Probability output may be binarized without explanation. | Document threshold and selection method. |
| Misaligned evaluation rasters | Metric output may be invalid if grids do not align. | Stop metric computation until aligned. |
| Weak labels treated as ground truth | Reference-derived labels may be overstated. | State label type and uncertainty. |

## Communication and use-boundary failure modes

| Failure mode | How it can affect BurnLens | Required response |
|---|---|---|
| Official-looking map output | Portfolio viewers may mistake experimental output for official wildfire information. | Include visible experimental-use language. |
| Emergency-use implication | Users may infer evacuation, routing, or incident guidance. | Repeat non-operational boundary. |
| Source-precedence confusion | BurnLens output may appear to override official information. | State that official sources govern. |
| Uncertainty hidden in polished visuals | Clean maps can hide weak labels, exclusions, or limitations. | Pair visuals with run report and limitation notes. |
| Performance overclaiming | Portfolio claims may imply operational accuracy. | Tie claims to versioned evaluation only. |
| Missing provenance | Outputs cannot be traced to source, commit, run, model, baseline, or label version. | Do not mark as portfolio-ready. |

## Warning flags for future manifests

Future run manifests should support warning flags such as:

```text
cloud_present
cloud_shadow_present
smoke_or_haze_present
bright_surface_risk
water_or_glare_present
snow_or_ice_present
sensor_saturation_present
nodata_present
terrain_occlusion_possible
source_time_mismatch
reference_resolution_limit
label_uncertainty_high
class_imbalance_high
baseline_circularity_risk
crs_mismatch
raster_grid_mismatch
threshold_sensitivity_high
official_use_confusion_risk
```

Flag names may change later, but the manifest must preserve the ability to record these risk types.

## Review and exclusion rules

BurnLens should use four responses to known failure modes:

| Response | Meaning |
|---|---|
| Flag | Keep the scene or output but mark the risk in the manifest or report. |
| Review | Require qualitative inspection before interpreting the output. |
| Exclude | Remove affected pixels, regions, scenes, or runs from metrics when they are invalid. |
| Stop | Do not proceed with comparison, training, inference, or portfolio claim until the issue is resolved. |

Unknown or excluded areas must not be silently treated as background.

## Minimum future reporting requirement

Any future run report should include:

- observed failure modes
- warning flags
- affected source IDs or tile IDs
- affected area or pixel count where possible
- review notes
- exclusion notes
- impact on metrics
- impact on map readability
- impact on portfolio claims

## Research basis

This plan is informed by current official source documentation:

- USGS Landsat Collection 2 QA documentation includes pixel-quality indicators for fill, dilated cloud, cirrus, cloud, cloud shadow, snow, water, confidence levels, radiometric saturation, dropped pixels, terrain occlusion, aerosol quality, and surface-temperature uncertainty.
- Sentinel-2 harmonized source documentation includes QA and scene-class concepts relevant to cloud, cirrus, cloud shadows, saturated/defective pixels, water, snow/ice, bare soils, and cloud probability.
- NASA FIRMS documentation describes active-fire / hotspot products, MODIS and VIIRS source characteristics, and data-use cautions that support treating active-fire references as uncertain inputs rather than pixel-perfect segmentation ground truth.

## Phase boundary

This task does not authorize:

- data ingestion
- imagery download
- source selection
- label creation
- baseline generation
- model training
- inference
- metric computation
- public map publication
- website demo integration

Those belong to later phases or later objectives.

## Use boundary

Future BurnLens outputs are experimental portfolio artifacts only. They are not official wildfire information, emergency guidance, evacuation routing, incident command support, or field-validated hazard assessment.

Official sources govern when information differs.

## Acceptance checklist

- [x] Imagery and source-quality failure modes defined.
- [x] Reference and label failure modes defined.
- [x] Baseline and model failure modes defined.
- [x] Geospatial processing failure modes defined.
- [x] Evaluation and metric failure modes defined.
- [x] Communication and use-boundary failure modes defined.
- [x] Review, exclusion, flag, and stop responses defined.
- [x] Baseline comparison and metrics-plan requirements preserved.
- [x] Source precedence and non-operational boundaries preserved.
- [x] Phase boundary preserved: no data, labels, model work, inference, metric computation, or site integration.
