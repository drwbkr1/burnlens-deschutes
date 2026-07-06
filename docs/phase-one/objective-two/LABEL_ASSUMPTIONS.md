# P1O2-T06 — Label Assumptions

## Status

Phase 1 / Objective Two task artifact.

This document defines label assumptions for the first BurnLens Deschutes CV task. It does not create labels, mask files, annotation files, train/validation/test splits, baseline outputs, model training runs, or inference outputs.

## Applies to

Current Objective Two decisions:

- CV task: experimental binary semantic segmentation for wildfire-relevant screening
- Primary target: active-fire / hotspot-informed binary fire mask
- Fallback target: burn-scar binary mask if active-fire label feasibility fails
- Class handling: positive, negative/background, and unknown/exclude/review-needed
- Output contract: mask-first output with future geospatial and run-package traceability

## Labeling principle

BurnLens labels should be treated as **documented training or evaluation artifacts**, not as official wildfire observations.

A future label can support portfolio modeling only if the source, conversion method, uncertainty, and limitations are documented. Ambiguity should be excluded or flagged rather than forced into positive or negative classes.

## Candidate label/reference sources

| Source category | Possible role | Main limitation |
|---|---|---|
| NASA FIRMS MODIS / VIIRS active-fire products | Reference evidence, baseline source, sampling aid, weak-label seed, or comparison source. | Active-fire detections identify hotspot pixel centers and are not exact segmentation masks. |
| Manually reviewed imagery masks | Human-created or human-reviewed training/evaluation labels. | Requires clear rules, review notes, and consistency checks. |
| Public burn-area or perimeter products | Fallback reference if burn-scar scope is activated. | Post-fire burned area is not the same as active-fire segmentation. |
| Threshold or rule-derived masks | Baseline or weak-label comparison. | Must be labeled as derived approximation, not ground truth. |
| Sample/demo labels | Pipeline development or tutorial use only. | Must not be presented as Deschutes operational evidence. |

## Research basis

NASA FIRMS provides near-real-time satellite imagery, active fire/hotspots, and related products. FIRMS documentation states that MODIS active fire/thermal hotspot locations represent the center of a 1 km pixel and VIIRS locations represent the center of a 375 m pixel. That supports using FIRMS for reference, weak-label, baseline, or sampling logic, but not as exact pixel-perfect ground truth for segmentation masks.

Research reference:

- NASA FIRMS documentation: https://www.earthdata.nasa.gov/data/tools/firms

## Primary label assumption

For the selected active-fire / hotspot-informed target, Phase Two should assume that initial labels may be **reference-derived** rather than fully ground-truth masks.

This means labels may be created from public reference evidence using documented rules such as:

- rasterizing hotspot points to a target grid
- buffering hotspot points with a stated radius
- intersecting reference evidence with usable imagery tiles
- manually reviewing or excluding questionable regions
- marking cloud/smoke/low-quality regions as unknown or excluded

The exact rule must be decided later in a labeling guide. This document only defines the assumption that the conversion must be explicit.

## Positive label assumption

A future positive label means:

> This pixel or region is associated with active-fire or hotspot-informed fire-relevant evidence under the documented BurnLens label rule.

Positive labels should record:

- source product
- source date/time
- source sensor/platform, if available
- confidence or quality field, if available
- conversion method
- reviewer status, if manually reviewed
- known caveats

## Negative/background label assumption

A future negative/background label means:

> This pixel or region is not associated with the selected positive class under the documented BurnLens label rule and is not flagged as unknown/exclude/review-needed.

Negative/background labels should not be created only from random easy background pixels. Phase Two should intentionally include confusing background examples where feasible, such as bright soil, roads, rooftops, water glare, shadows, clouds, or other features likely to cause false positives.

## Unknown / exclude / review-needed assumption

A future unknown/exclude/review-needed label means:

> This pixel or region should not be used as a confident positive or negative example because the evidence is incomplete, ambiguous, degraded, source-conflicted, or outside the current label rule.

Examples include:

- cloud-covered imagery
- smoke-obscured imagery
- missing or inconsistent QA flags
- geolocation mismatch between imagery and reference evidence
- active-fire reference point that does not align cleanly with image evidence
- stale imagery relative to reference source timing
- mixed pixels at coarse resolution
- low-confidence reference evidence, if not otherwise handled
- source conflict with official/public information
- areas outside the chosen AOI or label scope

## Minimum label metadata required later

Every future label record should include at least:

| Field | Meaning |
|---|---|
| `label_id` | Unique label or mask identifier. |
| `label_schema_version` | Version of the labeling rules. |
| `class_value` | Numeric class value. |
| `class_name` | Human-readable class name. |
| `source_name` | Source product or imagery used. |
| `source_url` | Documentation or access URL. |
| `source_datetime` | Source acquisition or detection time/date if available. |
| `source_sensor` | Sensor/instrument if applicable. |
| `source_resolution` | Spatial resolution if applicable. |
| `conversion_method` | Buffer, rasterization, manual mask, threshold, or other method. |
| `conversion_parameters` | Radius, threshold, grid size, CRS, or other relevant parameters. |
| `review_status` | Unreviewed, manually reviewed, excluded, or needs review. |
| `quality_flags` | Cloud, smoke, stale, low-confidence, alignment issue, or other flags. |
| `created_at` | Label creation timestamp. |
| `created_by` | Human, script, or process that created the label. |
| `notes` | Caveats or interpretation notes. |

## Required label-quality checks for Phase Two

Before labels can support model training, Phase Two should check:

- image-mask alignment
- CRS and transform alignment
- source date/time compatibility
- class balance
- positive label sparsity
- negative/background sampling strategy
- ambiguity/exclusion coverage
- cloud/smoke/quality flags
- duplicates or overlapping reference products
- whether labels are appropriate for training, validation, testing, or baseline comparison only

## Ground-truth language restriction

BurnLens should avoid calling reference-derived labels **ground truth** unless a later document justifies that term for a specific source and use.

Preferred terms:

- reference-derived label
- weak label
- manually reviewed label
- baseline-derived mask
- experimental training label
- evaluation reference

Avoid:

- official fire perimeter
- emergency-ready label
- field-validated observation
- authoritative active-fire boundary
- ground-truth mask, unless separately justified

## Fallback label assumption

If the project switches to burn-scar segmentation, it must create a new or revised label assumption document before data work begins.

The fallback may not automatically expand into burn severity, recovery analysis, multi-class burned-area mapping, or incident assessment.

## Source-precedence rule

Official sources govern.

BurnLens labels and model outputs are experimental portfolio artifacts and must never override county, state, federal, fire-service, emergency-management, transportation, evacuation, hazard, or incident information.

## Use boundary

Future labels should be described as:

> Experimental BurnLens labels derived from public/open reference information and documented review rules for portfolio segmentation research.

Future labels should not be described as:

> Official wildfire observations or emergency-ready ground truth.

## Acceptance checklist

- [x] Candidate label/reference sources defined without creating labels.
- [x] FIRMS and other active-fire products are treated as reference/weak-label/baseline/sampling aids, not perfect masks.
- [x] Ambiguity, exclusion, quality, and source-alignment assumptions defined.
- [x] Minimum label metadata fields defined.
- [x] Source-precedence and non-operational use boundaries preserved.
- [x] Phase boundary preserved: no labels, mask files, labeling guide implementation, dataset split, or model training.
