# PRECHECK-2026-091 - P2O5-T03 U02 whole-event split lock

**Date:** 2026-07-25

**Issue:** #562

**Implementation source:** `c719bf79b4c01cd4016c33649c17f26f9d4ada97`

**Run:** `BL-2026-07-25-p2o5-t03-u02-whole-event-split-r001`

**Disposition:** `pass-split-locked-test-sealed-training-false`

## Inputs and predeclaration

The ranker binds:

- `DATASET-BUILD-CONTRACT-2026-001`, 29,653 bytes, SHA-256
  `f6106691d42692f39684ed43c35f7c097d51f08b13c3dc3bf1e030ca9687b67f`;
- `DATASET-CANDIDATE-2026-002`, 30,504 bytes, SHA-256
  `4a9646af493cdce81d0cd57405ebccf0dfecf5ca77c96930d0837c3b7d4e65f2`.

The ranking applies, in order:

1. minimum source-regime deviation from one event per regime per role;
2. minimum transfer-status deviation from one event per status per role;
3. maximum accepted training-core pixels;
4. minimum validation/test core-pixel difference;
5. maximum minimum test-event year;
6. maximum test-event year sum;
7. minimum training-event year span;
8. minimum validation-event year span;
9. canonical role/event IDs as the final stable tie-break.

The code freezes this order before generating or inspecting dataset patches.
It reads candidate metadata and hashes only. No imagery or test pixel value is
opened.

## Assignment result

The independent enumerator reproduces 90 complete 2/2/2 assignments. Fifty-four
pass all hard transfer, source-regime, and source-program rules. All 54 valid
assignments receive one unique deterministic rank.

Rank one locks:

| Role | Events | Core pixels | Background / burned | Unknown ring |
|---|---|---:|---:|---:|
| Train | Green Ridge 2020; Tepee 2018 | 109 | 58 / 51 | 185 |
| Validation | Grandview 2021; McKay 2017 | 89 | 32 / 57 | 178 |
| Test | Ward Creek 2019; Windigo 2022 | 89 | 50 / 39 | 168 |

Every role contains one `sentinel2-mtbs-current-v1` event, one
`sentinel2-baer-mtbs-ravg-current-v1` event, and one event with the preserved
never-tuned-transfer designation.

## Exact outputs

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `WHOLE-EVENT-SPLIT-RANKING-2026-001.json` | 173,367 | `a513edff663dea74f5ed5e6a50c9e50175f27bc8fdd9aecf7ebe4056582397f9` |
| `WHOLE-EVENT-SPLIT-2026-001.json` | 12,312 | `a62e66f4f81a95a56a727b29bb382cb87369306f11e2f2a4527d1c7fb68d0b99` |

Both outputs replay byte for byte. Twelve focused U01/U02 tests pass.
Compilation and `git diff --check` pass.

## Boundary

`burnlens-whole-event-split-v0.1.0` is locked. The test roster is visible for
traceability, but its pixel values remain unopened with open count zero.

No dataset patch, normalization statistic, baseline, model, metric result,
training authorization, inference, deployment, or external submission exists.
U03 may now materialize the exact native-grid dataset from this split.
