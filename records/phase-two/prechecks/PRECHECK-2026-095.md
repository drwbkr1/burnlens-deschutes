# PRECHECK-2026-095 - P2O5-T03 U06 model readiness

**Date:** 2026-07-25

**Issue:** #562

**Implementation source:** `d4d3e955ea9fe3afba682a4a96a8f80195c265c0`

**Accepted report source:** `4caf37e52591933c2c03ae050926d5123e47ed2f`

**Accepted run:** `BL-2026-07-25-p2o5-t03-u06-readiness-r002`

**Disposition:** `authorize-bounded-unet-rejection-first`

## Exact Phase Two package

U06 rehashes the exact dataset, candidate, split, independent QA,
normalization, baseline protocol, baseline selection, baseline evaluation,
model-family decision, Phase Two outcome, and current tooling-source record.
All ten input hashes match.

The audit passes nine substantive gates:

1. exact dataset and split identity;
2. six-event / twelve-patch / 287-core / 531-unknown scope;
3. locked whole-event 4/4/4 patch split;
4. passed independent dataset QA;
5. train-only normalization;
6. train/validation-only baseline selection;
7. one frozen, untuned baseline test opening;
8. explicit visibility of the RBR metric ceiling;
9. compatible CPU-only tooling feasibility without package installation.

The selected RBR baseline remains 1.0000 event-class macro Dice, IoU, and
worst-event macro Dice on 89 selected prototype test cores. This is a ceiling
on the frozen metric, not generalization.

## Fresh tooling and compute gate

| Source record | Bytes | SHA-256 |
|---|---:|---|
| `MODEL-TOOLING-SOURCES-2026-001.json` | 5,462 | `5e55f5fb5572a9ccfaef79d1c91f0b965771d1a99a047540598fc158ed190ffc` |

Current official PyTorch 2.13 documentation establishes the reproducibility,
numerical-accuracy, Windows/Python, CPU, and unreduced
`BCEWithLogitsLoss` boundaries. A local metadata-only
`uv pip install --dry-run torch setuptools==82.0.0` resolves
`torch==2.13.0` and preserves the repository's `setuptools>=82,<83`
constraint. It changes no installed package.

The observed machine has CPython 3.12.10, an Intel i7-1365U with ten physical
cores / twelve logical processors, 34,000,240,640 bytes of physical memory,
and no `nvidia-smi` route. CPU-only execution is selected. GPU, mixed
precision, cloud compute, distributed training, paid services, and secrets are
outside the first experiment.

## Decision and exact training contract

The accepted decision is:

`AUTHORIZE_BOUNDED_UNET`

with qualifier:

`REJECTION_FIRST_SINGLE_MODEL_EXPERIMENT`

The authorization becomes executable only after the coherent U07 milestone
release is merged, tagged, and verified. It permits exactly one small,
CPU-only, six-channel U-Net-style binary segmentation model. It does not permit
architecture search, hyperparameter search, augmentation, test tuning,
deployment, or a model-value claim.

The contract freezes:

- six native 20 m pre/post B04, B8A, and B12 channels;
- four train, four validation, and four test patches in canonical order;
- the train-only normalization and exact loss/metric mask;
- value 2 unknown and value 255 nodata exclusions;
- a 16 / 32 / 64 two-level U-Net with no batch normalization, dropout,
  pretrained weights, or second model;
- PyTorch 2.13.0, CPython 3.12.10, CPU, float32, seed 20260725, and strict
  deterministic algorithms;
- unreduced BCE-with-logits averaged only across exact loss-mask pixels;
- Adam at learning rate 0.001, batch size four, maximum 200 epochs, and
  validation-only early stopping;
- fixed probability threshold 0.5 and validation-only checkpoint selection;
- one final model test evaluation after code, environment, weights, and
  checkpoint are frozen;
- same-environment replay and finite-value gates.

Because RBR is already 1.0 on every primary frozen test metric, the U-Net
cannot become the analytical winner under the predeclared rule. A matching
model is a valid trained-model result but not added value. A lower, invalid,
contaminated, nonfinite, or irreproducible model is rejected and RBR remains
the accepted analytical method.

## Retained failures

R001 replays exactly and passes desktop rendering, but the long
machine-readable decision tokens widen the 390 by 844 document from 375 to
409 CSS pixels. Its five exact outputs remain under
`retained-failures/r001-narrow-token-overflow/`.

One post-r001 verification command uses system Python rather than the locked
environment and fails when `rasterio` is absent. The exact cause and valid
locked-environment rerun are retained in `FAILURE-LEDGER.md`.

Renderer source `4caf37e52591933c2c03ae050926d5123e47ed2f` permits card text to
wrap anywhere without changing any analytical or authorization value.

## Accepted exact outputs

| Output | Bytes | SHA-256 |
|---|---:|---|
| `MODEL-READINESS-AUDIT-2026-001.json` | 6,781 | `eebd08f25fca9b08b4f8408a768bf30eaa49e661e8aa858234da529a44b10cf4` |
| `MODEL-READINESS-DECISION-2026-001.json` | 1,967 | `74fd1c21e00cf75fb4a25eb3ca092b53033359a5dfbcd333eddf8a4b98c56769` |
| `BOUNDED-UNET-TRAINING-CONTRACT-2026-001.json` | 8,992 | `670dbb0712768dd0b8ef47a2c5305b736b21139029017a194e4ed747029c9166` |
| `MODEL-READINESS-DECISION-2026-001.html` | 6,184 | `6e80c26c29875c3a05249a4f226abcc1113df32c284ba2de2963741066de0557` |
| `MODEL-READINESS-DECISION-2026-001.png` | 71,508 | `6fc5d5b23ee89ccb01c052e2534f2ec42658a01ad6de0d51c73dc61bd57cee21` |

All five outputs replay byte for byte under the locked environment.

## Real rendered application

The accepted HTML and 1,800 by 1,040 PNG pass the in-app browser:

| Viewport | Document client / scroll width | Image client / natural size | Result |
|---|---:|---:|---|
| 1280 by 720 | 1,265 / 1,265 | 1,021 / 1,800 by 1,040 | pass |
| 390 by 844 | 375 / 375 | 296 / 1,800 by 1,040 | pass |

The narrow gate permits the readiness table to scroll inside its explicit
297-pixel container; no element outside that container overflows. Browser
diagnostics are empty.

Nineteen focused model-readiness, baseline, and dataset-QA tests pass under the
locked CPython 3.12.10 environment in 22.403 seconds with only the existing
NumPy deprecation warnings. Compilation and `git diff --check` pass.

After accepted outputs and records commit
`535e7f338a51dd5ceba65e3dd0d6cc2525f66b7b`, explicit `unittest` discovery
passes 692 tests with one expected skip in 540.969 seconds. The canonical
`pytest` suite then passes 695 tests, one expected skip, 228 retained NumPy
deprecation warnings, and 86 subtests in 582.05 seconds. A preceding bare
`unittest` invocation discovers zero tests and is rejected as evidence.

## Boundary and next dependency

No model, weights, training run, model evaluation, inference, deployment, or
final-submission-ready claim exists. U07 must ship and verify this coherent
Phase Two milestone before the separately issue-backed Phase Three experiment
may execute the exact contract.
