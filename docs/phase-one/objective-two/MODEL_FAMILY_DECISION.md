# P1O2-T08 — First Model Family Decision

## Status

Phase 1 / Objective Two task artifact.

This document selects the first BurnLens Deschutes model family for future implementation planning. It does not create model code, implement an architecture, train weights, run inference, complete a model card, or approve a production model.

## Applies to

Current Objective Two decisions:

- CV task: experimental binary semantic segmentation for wildfire-relevant screening
- Primary target: active-fire / hotspot-informed binary fire mask
- Fallback target: burn-scar binary mask if active-fire label feasibility fails
- Output contract: mask-first, traceable output that can later become georeferenced raster, vector polygons, map overlay, exposure-style summary, and run package
- Baseline rule: future model outputs must be compared against simpler non-model baselines before any model-value claim

## Decision

BurnLens Deschutes will use a **U-Net-style binary semantic segmentation model family** as the first model family for future implementation planning.

This means the first model should be designed as an image-to-mask segmentation approach, where the expected output is a binary or probability-like raster aligned to an input tile. The model family is selected because it fits the current task shape: tile in, mask out, followed by geospatial processing.

## Why U-Net-style segmentation fits BurnLens

A U-Net-style family fits the project because:

- it is designed for dense image segmentation rather than scene-level classification
- it produces mask-like outputs that align with the locked BurnLens workflow
- it supports a binary positive/background output target
- it can be implemented with a relatively small, inspectable architecture
- it has a clear encoder/decoder structure that is explainable in a portfolio case study
- it can later support probability or confidence-style output before thresholding
- it can be compared against simple non-model mask baselines

The locked BurnLens workflow remains:

```text
imagery → preprocessing → segmentation or baseline mask → raster output → vector polygons → map overlay → exposure-style summary → documented run package
```

## Research basis

The original U-Net paper describes an architecture with a contracting path to capture context and a symmetric expanding path that enables precise localization. The paper also emphasizes efficient use of annotated samples through data augmentation, which is relevant because BurnLens may have limited or weak labels in early phases.

Torchvision documents semantic segmentation model families including FCN, DeepLabV3, and LRASPP. These are useful fallback/reference families for later implementation planning, but they are not selected as the first family in this task.

References:

- U-Net paper: https://arxiv.org/abs/1505.04597
- Torchvision semantic segmentation models: https://docs.pytorch.org/vision/main/models.html

## First-family requirements

A future first implementation should meet these requirements before training is allowed:

| Requirement | Meaning |
|---|---|
| Binary segmentation head | Output should support positive vs. background, with thresholding documented. |
| Mask-aligned output | Output dimensions or resize mapping must be documented against the input tile. |
| Unknown/exclude support | Unknown or excluded regions must be handled in loss/evaluation, not silently treated as negatives. |
| Versionable architecture | Architecture name, parameters, input bands, output classes, and code commit must be recordable. |
| Baseline comparison ready | Model output must be comparable against the baseline plan. |
| Geospatial handoff ready | Output must support later raster/vector conversion with metadata. |
| Small-data caution | Training plan must acknowledge limited labels, weak labels, class imbalance, and data leakage risk. |

## Input assumptions for future implementation

The selected model family does not decide the final imagery source or band set.

Future implementation may start with a simple input configuration such as RGB-like or selected multispectral bands, but the final band set must be justified during data feasibility and preprocessing work.

If multispectral imagery is used, the implementation must document:

- input band names
- band order
- spatial resolution and resampling method
- scaling/normalization method
- nodata handling
- cloud/smoke/quality mask handling
- whether pretrained weights are compatible with the band count

## Output assumptions for future implementation

A future U-Net-style model should support:

- binary mask output
- optional probability/confidence raster
- threshold documentation
- unknown/exclude treatment
- model version
- run ID
- source imagery ID
- dataset version
- label schema version
- baseline comparison reference

## Fallback model families

Fallbacks are allowed only if Phase Two or later implementation work shows that the first family is unsuitable.

| Fallback | When to consider | Constraint |
|---|---|---|
| DeepLabV3-style semantic segmentation | If stronger contextual modeling or pretrained encoder support is useful. | Must still support mask-first binary output and traceability. |
| FCN-style semantic segmentation | If a simpler reference architecture is needed for comparison. | Must not become the primary model without a documented decision update. |
| Lightweight encoder-decoder CNN | If compute or dependency constraints make U-Net-style implementation too heavy. | Must preserve output contract and baseline comparison requirements. |
| Baseline-only path | If labels, imagery, or alignment are too weak to justify model training. | Portfolio should state that the baseline path is more defensible than a trained model. |

## Model families not selected

The following are not selected for the first model family:

| Not selected | Reason |
|---|---|
| Object detection | The current task is pixel/region segmentation, not bounding boxes. |
| Image classification | Scene-level labels do not satisfy the mask-first GEOINT workflow. |
| Fire spread prediction | Out of scope and operationally sensitive. |
| Evacuation or routing models | Out of scope and not appropriate for this portfolio tool. |
| Multi-class wildfire platform | Too broad for the first model scope. |
| Real-time alerting model | Out of scope and could imply operational use. |

## Model-value dependency

The model family decision does not imply that a model should be trained no matter what.

A future model should proceed only if:

- data feasibility is adequate
- labels or reference-derived labels are defensible
- unknown/exclude handling is documented
- baseline comparison can be run
- evaluation metrics are defined
- limitations can be communicated clearly

If those conditions are not met, BurnLens should choose the baseline-only path rather than train an under-supported model.

## Versioning requirement

Future model versions should follow a clear identifier pattern such as:

```text
burnlens-unet-binary-v0.1.0
```

Minimum future model metadata:

| Field | Meaning |
|---|---|
| `model_family` | U-Net-style binary semantic segmentation. |
| `model_version` | Versioned model identifier. |
| `architecture_summary` | Encoder/decoder notes and major parameters. |
| `input_bands` | Bands and order used. |
| `output_classes` | Positive/background/exclude handling. |
| `dataset_version` | Dataset used for training/evaluation. |
| `label_schema_version` | Label schema used. |
| `training_commit` | Code commit used for training. |
| `training_run_id` | Run identifier if training occurs. |
| `baseline_versions` | Baselines used for comparison. |
| `known_limitations` | Data, label, model, and use limitations. |

## Phase boundary

This task does not authorize:

- model code
- architecture implementation
- dependency selection
- weights
- training
- inference
- metrics computation
- model card completion
- public demo claim

Those belong to later objectives or phases.

## Use boundary

Future BurnLens model outputs are experimental portfolio artifacts only. They are not official wildfire information, emergency guidance, evacuation routing, incident command support, or field-validated hazard assessment.

Official sources govern when information differs.

## Acceptance checklist

- [x] First model family selected.
- [x] U-Net-style binary semantic segmentation justified against the locked workflow.
- [x] Fallback model families defined without implementation.
- [x] Multispectral imagery, small data, class imbalance, and traceability constraints documented.
- [x] Baseline comparison dependency preserved.
- [x] Source precedence and non-operational boundaries preserved.
- [x] Phase boundary preserved: no code, model, weights, training, inference, or completed model card.
