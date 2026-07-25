# PRECHECK-2026-094 - P2O5-T03 U05 non-model baseline

**Date:** 2026-07-25

**Issue:** #562

**Implementation source:** `b4720cabd26adf77859a4e0024428aa80fe9a119`

**Accepted report source:** `bfd5c6c9a137b0888d9678b176cf2412a1e18805`

**Accepted run:** `BL-2026-07-25-p2o5-t03-u05-evaluation-r003`

**Disposition:** `pass-reproducible-non-model-baseline-evaluation`

## Primary-source gate

Fresh research used public official and primary technical sources:

| Source record | Bytes | SHA-256 |
|---|---:|---|
| `BASELINE-PRIMARY-SOURCES-2026-001.json` | 5,813 | `88a3ac0bb98890e9a5c779b45223a3e9079b8fc2faa94c6f50f3a9560d43972b` |

USGS and MTBS sources justify NBR-change methods and caution that thematic
thresholds vary by fire and ecological setting. The USDA Forest Service primary
paper justifies RBR as an alternative to dNBR and RdNBR. The ESA handbook
confirms the relevant Sentinel-2 band identities.

U05 includes RBR, dNBR, and dNDVI threshold families plus all-background and
all-burned references. RdNBR is excluded because its published normalization is
singular at prefire NBR zero; U05 does not invent an epsilon or exclusion.

No third-party bytes, credentials, paid service, or private data are retained.

## Frozen preregistration

The protocol was committed before any train, validation, or test array opened:

| Artifact | Bytes | SHA-256 | Commit |
|---|---:|---|---|
| `BASELINE-PREREGISTRATION-2026-001.json` | 6,301 | `31eb08ae88ee0b4425dce8af3e47475e38a4d9adb9249af7381fc5d608799bb5` | `f48ef98e16841d8e255fb1ba96a2a5cf806361a1` |

The protocol freezes formulas, eligible families, train-only midpoint
threshold fitting, validation-only family selection, event/class macro Dice
and IoU, denominators, exact tie breaks, uncertainty limits, and a single
test-opening contract. It binds exact 4/4/4 train/validation/test patch rosters.

## Train and validation selection

Training-only fitting and validation-only selection replay exactly:

| Artifact | Bytes | SHA-256 | Commit |
|---|---:|---|---|
| `BASELINE-SELECTION-2026-001.json` | 37,091 | `061596f7df68844319cc3c5a5d8d0b19124cecc812e59c3a7eda9d5d3e68c1c3` | `220ce86cf056f81bf94a1c88141ca3082ab99b42` |

| Family | Frozen threshold | Train event-class Dice | Validation event-class Dice | Validation IoU |
|---|---:|---:|---:|---:|
| RBR | 0.041043221950531006 | 1.0000 | 0.8542 | 0.7758 |
| dNBR | 0.05970039591193199 | 1.0000 | 0.6622 | 0.6200 |
| dNDVI | 0.033301085233688354 | 1.0000 | 0.7997 | 0.7141 |
| all background | n/a | 0.3460 | 0.2428 | 0.1699 |
| all burned | n/a | 0.3196 | 0.3920 | 0.3301 |

The frozen validation objective selects RBR. Test analytical-open count remains
zero through this commit.

## Single sealed-test opening

The selected RBR and all four preregistered comparison families execute in one
logical analytical opening. No family, threshold, mask, metric, or selection
changes afterward.

The accepted RBR result uses 89 owner-approved prototype cores:

| Event | Background | Burned | Macro Dice | Macro IoU |
|---|---:|---:|---:|---:|
| Ward Creek 2019 | 25 | 14 | 1.0000 | 1.0000 |
| Windigo 2022 | 25 | 25 | 1.0000 | 1.0000 |

Pooled RBR denominators are exact:

- background: support 50, TP 50, FP 0, FN 0, Dice denominator 100;
- burned: support 39, TP 39, FP 0, FN 0, Dice denominator 78.

RBR, dNBR, and dNDVI each classify all 89 selected cores correctly. Constant
references remain much lower. This perfect selected-core result does not
measure unknown rings, unreviewed pixels, complete burn scars, or natural
prevalence.

Candidate construction used optical and official-reference evidence. It may
favor the spectral separability measured here. The result is not independent
ground truth, field validation, population inference, generalization,
operational readiness, or emergency suitability.

## Retained failures and accepted outputs

Run r001 fixes the exact metrics but is retained because excluded nonfinite
display pixels produce an invalid-cast warning. The display-only remediation
maps those pixels to a neutral color without changing any metric or prediction.

Run r002 passes exact replay and real rendering but is retained because the
report omits the candidate-selection-bias limitation. Run r003 adds that
limitation and preserves every r001 analytical value exactly.

| Accepted output | Bytes | SHA-256 |
|---|---:|---|
| `BASELINE-EVALUATION-2026-001.json` | 21,257 | `a8ba82f999a87a8114c7fc417126b96c1f031e7eb9e24311df20fe32d7edb221` |
| `BASELINE-EVALUATION-2026-001.html` | 3,921 | `109075ca31cb1c01137bdccff5786c862105eb15dc1cbe15c8603dcf3d15fd99` |
| `BASELINE-EVALUATION-2026-001.png` | 169,275 | `49bf3686fd7b109572fcbff8abb8e35d7d9054c7b2dd9e26e70cc26975700060` |

All three accepted outputs replay exactly.

## Real rendered application and verification

The exact accepted HTML and PNG pass the in-app browser:

| Viewport | Document client / scroll width | Image | Result |
|---|---:|---:|---|
| 1280 by 720 | 1,265 / 1,265 | 1800 by 1180 | pass |
| 390 by 844 | 375 / 375 | 1800 by 1180 | pass |

Both tables fit. All four limitations render. No overflowing element, browser
warning, or browser error exists.

Thirty-three focused dataset/baseline tests pass with 132 retained NumPy
deprecation warnings. Compilation and `git diff --check` pass.

After the accepted outputs and records commit at
`ca0e977046f3442ee03d5d178624ea525df8ee62`, the clean full repository suite
passes 691 tests, one expected skip, 228 retained warnings, and 86 subtests in
541.42 seconds.

## Boundary and handoff

The accepted decision is:

`PASS_REPRODUCIBLE_NON_MODEL_BASELINE_EVALUATION`

Test analytical-open count is one. Model and training authorization remain
false. U06 must decide whether a bounded U-Net is scientifically justified
when the strongest transparent baseline already classifies every selected test
core correctly.
