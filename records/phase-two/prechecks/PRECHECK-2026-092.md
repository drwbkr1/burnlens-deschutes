# PRECHECK-2026-092 - P2O5-T03 U03 dataset materialization

**Date:** 2026-07-25

**Issue:** #562

**Implementation source:** `59610b232107b0027d949e907b66a56a22722ad2`

**Remediation source:** `3e383ec413dad5ece1245951660197051a401e1c`

**Accepted run:** `BL-2026-07-25-p2o5-t03-u03-dataset-r002`

**Disposition:** `pass-dataset-created-test-sealed-training-false`

## Exact entry

U03 binds the exact U01 contract, U02 split, and v0.51 candidate:

| Input | Bytes | SHA-256 |
|---|---:|---|
| `DATASET-BUILD-CONTRACT-2026-001.json` | 29,653 | `f6106691d42692f39684ed43c35f7c097d51f08b13c3dc3bf1e030ca9687b67f` |
| `WHOLE-EVENT-SPLIT-2026-001.json` | 12,312 | `a62e66f4f81a95a56a727b29bb382cb87369306f11e2f2a4527d1c7fb68d0b99` |
| `DATASET-CANDIDATE-2026-002.json` | 30,504 | `4a9646af493cdce81d0cd57405ebccf0dfecf5ca77c96930d0837c3b7d4e65f2` |

The build rehashes all twelve exact single-link registered Sentinel archives:
13,633,040,965 bytes total. Every local SHA-256, native ID, filename, byte
count, registration identity, and one-link custody gate passes.

## Retained failed attempt

Run `BL-2026-07-25-p2o5-t03-u03-dataset-r001` failed before promotion:

> accepted core fails source validity: event-grandview-0558-od-2021
> (50 pixels)

The first implementation treated unsampled portions of an event-level
all-pass registration result as invalid. It created no dataset destination.
Source `3e383ec...` now accepts the complete event grid only when every sampled
window passes, no review/excluded/failure window exists, and the machine
decision is explicitly `PASS_*`. Events with explicit review or exclusion
windows retain fail-closed spatial masks. Twelve focused tests pass after the
correction.

## Accepted dataset

Run r002 creates `burnlens-dataset-v0.1.0`:

| Property | Value |
|---|---:|
| Files | 49 |
| Total tracked bytes | 1,388,556 |
| Dataset manifest | 55,308 bytes |
| Manifest SHA-256 | `e0b7ac666a70e96f979c386a9d503ad45ed0baea8f21e3838ba4530d5e3d2d16` |
| Canonical tree SHA-256 | `9fb4f83984ef94f2286ca59447fecd40c42cd2fcae3212f573df8575ad78b10f` |
| Event groups | 6 |
| Patches | 12 |
| Train / validation / test patches | 4 / 4 / 4 |
| Accepted core pixels | 287 |
| Background / burned core pixels | 140 / 147 |
| Explicit unknown-ring pixels retained | 531 |

Each patch contains deterministic `.npy` arrays for six float32 reflectance
channels, the four-state label layer, input-valid mask, and byte-identical
loss/metric mask. No pickle, reprojection, resampling, mosaicking, padding, or
augmentation is used.

All 48 patch-file bindings pass byte and SHA-256 verification. A second full
archive rehash and independent materialization reproduces all 49 files and
1,388,556 bytes exactly. Eighteen focused U01-U03 tests pass. Compilation,
JSON parsing, and `git diff --check` pass.

The first full-suite invocation exceeded its five-minute caller time box and
returned no terminal result. A logged rerun completed in 596.29 seconds with
674 passes, one expected skip, 120 warnings, 86 subtests, and two failures.
One failure was the checkout-byte guard observing this unit's intentionally
uncommitted records. The other was a stale frozen-bundle test that expected
the mutable case study to be the first changed bound asset; v0.51 now changes
the portfolio page first. The assertion now expects that earlier valid safety
failure. Thirteen focused bundle/materialization tests pass after correction.

After commit `b7a58b3900ea4ff2d3ace5f5e819f2269bb41e62`, the checkout-byte
guard, frozen-bundle guard, and dataset tests pass together: 15 tests with 24
retained warnings. The final logged full suite passes 676 tests, one expected
skip, 120 retained warnings, and 86 subtests in 694.96 seconds. No failure or
stderr remains.

## Test and training boundary

The test source bytes were processed mechanically into their predeclared
patches. They were not viewed, scored, summarized spectrally, used for
normalization, or used for any method, threshold, stopping, or selection
choice. Analytical test open count remains zero.

No normalization statistic, independent dataset QA, baseline, model, metric
result, training authorization, inference, deployment, or external submission
exists. U04 must independently reconstruct and inspect the dataset before U05.
