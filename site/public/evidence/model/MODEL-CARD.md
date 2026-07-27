# BurnLens U-Net binary v0.1.0

## Status

Valid trained and evaluated prototype; **rejected as the analytical winner**.
The accepted analytical method remains `burnlens-baseline-v0.1.0`
relative-burn-ratio thresholding.

## Intended portfolio role

Demonstrate a reproducible six-channel U-Net training/evaluation path and make
its failure visible beside the accepted baseline. It may appear in the Phase
Four application only as a clearly labeled rejected-model diagnostic.

## Architecture and inputs

- 117,473-parameter U-Net-style binary segmentation model
- six 20-metre Sentinel-2 channels: pre/post B04, B8A, and B12
- 64-by-64 float32 patches
- train-only normalization `burnlens-train-normalization-v0.1.0`
- exact loss mask excludes unknown, invalid, nodata, and non-binary pixels
- CPU, seed 20260725, Adam 0.001, batch four, threshold 0.5

## Data and labels

Dataset `burnlens-dataset-v0.1.0`, whole-event split
`burnlens-whole-event-split-v0.1.0`, and label schema
`burn-scar-binary-region-label-schema-v0.3.0`. Labels are owner-approved
prototype cores, not independent ground truth or field validation.

## Evaluation

One Ward Creek/Windigo opening is consumed. The model predicts all 89 selected
cores as burned:

- event-class macro Dice: 0.29874213836477986
- event-class macro IoU: 0.21474358974358976
- worst-event macro Dice: 0.2641509433962264
- masked BCE: 0.7280717492103577
- RBR baseline Dice/IoU/worst-event: 1.0 / 1.0 / 1.0

Decision: `reject-model-retain-baseline`.

## Reproducibility

The U06 train/validation replay reproduces all 35 history rows, selected epoch
10, final epoch 35, and the exact 479,573-byte model weights SHA-256
`703d92577e2b82a4cfdec0c5e43b8d7a064253483de4ccea909209f54b802334`. U05 probabilities, predictions, denominators, and decision
are independently reverified from immutable outputs without a second source
test-array opening.

## Limitations and prohibited claims

Six events, 12 patches, and 287 selected prototype cores do not establish
population performance. The test has two events and 89 selected cores. The
result does not measure full burn scars, natural prevalence, field validity,
generalization, official status, operational readiness, or emergency fitness.
The model must not be used as the accepted perimeter or area estimator.

## Trace

- source commit: `90ab4ab42d6ceb11c2987efb0b737c016712cea8`
- replay run: `BL-2026-07-25-p3o1-t01-u06-replay-r003`
- software at execution: `0.52.0`
- rejected-model package: `burnlens-unet-rejected-package-v0.1.1`
- AOI: `aoi-darlene3-model-v0.2.0`
- model: `burnlens-unet-binary-v0.1.0`
- dataset: `burnlens-dataset-v0.1.0`
- split: `burnlens-whole-event-split-v0.1.0`
- label schema: `burn-scar-binary-region-label-schema-v0.3.0`
- baseline: `burnlens-baseline-v0.1.0`
