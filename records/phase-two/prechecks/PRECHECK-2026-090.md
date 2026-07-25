# PRECHECK-2026-090 - P2O5-T03 U01 dataset contract

**Date:** 2026-07-25

**Issue:** #562

**Branch:** `codex/p2o5-t03-dataset-split-baselines`

**Exact base:** `1debea556a5fb2fc8eda87a234f106655cdc37db`

**Implementation source:** `0a1d5338a599b3cfa0a9932f12e6dbbc74b1dcd6`

**Run:** `BL-2026-07-25-p2o5-t03-u01-dataset-contract-r002`

**Disposition:** `pass-training-false`

## Exact entry

The candidate remains `DATASET-CANDIDATE-2026-002`, 30,504 bytes, SHA-256
`4a9646af493cdce81d0cd57405ebccf0dfecf5ca77c96930d0837c3b7d4e65f2`.
The accepted predecessor audit remains 6,601 bytes, SHA-256
`50e3b9f3c6c33a9f8cd36cf0952bf5033c039e68ffc864bf952ddec5442e6ed4`.

The builder rehashes every candidate-bound proposal, owner intake, source
record, terms record, and raster. It also binds the exact tracked optical
source-fitness reports for McKay, Tepee, Green Ridge, Grandview, Windigo, and
Ward Creek.

## Frozen contract

`DATASET-BUILD-CONTRACT-2026-001` freezes:

- six float32 Sentinel-2 L2A reflectance channels in order:
  pre B04, B8A, B12, then post B04, B8A, B12;
- metadata-derived band offsets and quantification;
- exact native EPSG:32610 20 m grids with no resampling, reprojection, or
  mosaicking;
- pair-valid SCL classes 4 and 5; class 7 and every excluded class remain out
  of loss and metrics;
- candidate-raster value 1 as the only core, value 2 as explicit unknown, and
  value 0 as unreviewed context rather than background;
- one 64 by 64 native-grid patch per candidate, split after no event and
  before every patch;
- train-only channel statistics and stored unstandardized reflectance;
- masked core-only Dice and IoU, per-event and per-class slices, exact
  denominators, macro-event aggregation, and one sealed test opening.

The contract selects no split and creates no dataset bytes.

## Exact outputs

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `DATASET-BUILD-CONTRACT-2026-001.json` | 29,653 | `f6106691d42692f39684ed43c35f7c097d51f08b13c3dc3bf1e030ca9687b67f` |
| `DATASET-READINESS-AUDIT-2026-003.json` | 7,750 | `f5af1b8bd8a103fd2b216e92cef02f57c3328b1524278275e94671d2a0724166` |
| `DATASET-READINESS-DECISION-2026-003.json` | 8,109 | `5295f932271655ab7b4a1956dbe4773920a6be68d121bfb3fa493c6bbc250558` |

The independent readiness utility reports `pass`, no blocking or deferred
gate, no failed count check, and `training_authorized=false`. Contract, audit,
and decision replay byte for byte.

Fourteen focused scientific tests pass with 36 retained NumPy warnings.
Five environment-profile tests pass in 121.12 seconds. Compilation and
`git diff --check` pass. A first combined environment command exceeded its
124-second time box without a result; the isolated rerun is the accepted
evidence.

## Boundary

This unit creates only the dataset/input/preprocessing/evaluation contract and
its audit evidence. Dataset, split, patch, normalization statistics, baseline,
model, metric result, training authorization, inference, deployment, and
external submission remain absent.

The next dependency is `P2O5-T03-U02`: predeclare a deterministic ranking over
all 54 valid whole-event assignments and lock exactly one split before
patching.
