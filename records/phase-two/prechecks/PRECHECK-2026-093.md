# PRECHECK-2026-093 - P2O5-T03 U04 independent dataset QA

**Date:** 2026-07-25

**Issue:** #562

**Initial implementation:** `d63c8a5ad9de825e13804394c295205393be6133`

**Accepted source:** `86d5e4555a51f791426c3d0f20e901cbdbf18f3c`

**Accepted run:** `BL-2026-07-25-p2o5-t03-u04-dataset-qa-r004`

**Disposition:** `pass-independent-qa-authorize-baseline-preregistration-only`

## Independent reconstruction

The U04 implementation does not import the U03 materializer. It independently
binds the exact dataset manifest, U01 contract, U02 split, and v0.51 candidate.
It rehashes all twelve registered, single-link Sentinel archives:
13,633,040,965 bytes total.

The independent path reopens the tracked candidate rasters and exact JP2 source
members, then reconstructs all twelve patch feature, state, input-valid, and
loss-mask arrays. All 48 file bindings pass. The reconstructed inventory is:

| Property | Value |
|---|---:|
| Event groups | 6 |
| Patches reconstructed | 12 / 12 |
| Patch files verified | 48 / 48 |
| Accepted core pixels | 287 |
| Background / burned core pixels | 140 / 147 |
| Explicit unknown-ring pixels | 531 |
| Exact duplicate feature arrays | 0 |
| Cross-role spatial overlaps | 0 |
| Cross-role source-product overlaps | 0 |

## Train-only normalization

`TRAIN-NORMALIZATION-2026-001.json` uses only Green Ridge and Tepee, the
locked training events. Every channel uses 14,723 eligible training pixels.
No validation or test pixel contributes to a mean, standard deviation,
minimum, or maximum.

| Output | Bytes | SHA-256 |
|---|---:|---|
| `DATASET-QA-2026-001.json` | 5,648 | `90aafef4c9deb8e9d06c2c2dc63f4f238e0229e4615dc29e1686803efa342f5a` |
| `DATASET-QA-2026-001.html` | 4,794 | `6092266fc4518950524c01c93c922e0a2366cd0f8d0503ef1307650855c3a899` |
| `DATASET-QA-2026-001.png` | 281,760 | `c1f8fe50b326f2ae75fdd6babc4103eaf9599c6ea4ad3b04811954ab7a5becde` |
| `TRAIN-NORMALIZATION-2026-001.json` | 2,694 | `6344861677753e9c96840f47e7a038a15f12a0c29759285c073f5cc6ea4bc255` |

The exact r004 generation repeats to ignored repository-local storage with
identical JSON, HTML, PNG, and normalization hashes.

## Retained failures

Three attempts remain immutable and are not promoted:

1. r001 accepted a caller-supplied nonexistent commit identity. Commit
   `dcb2afc6d08e6faeb81703762aeb3fa988b16d7f` adds a full lowercase SHA and
   exact-HEAD gate before output construction.
2. r002 rendered correctly at 1280 by 720, but 650-pixel tables expanded the
   390 by 844 document to 764 pixels. Commit `4df233f...` makes the tables fit
   the narrow breakpoint.
3. r003 fixed the tables, but the unbroken machine decision token still
   expanded the narrow document to 764 pixels. Commit `86d5e45...` safely
   wraps decision text.

Every retained attempt includes exact bytes, hashes, its failure decision, and
the no-promotion boundary.

## Real rendered application gate

The accepted r004 HTML and PNG were served from the canonical checkout and
inspected in the in-app browser:

| Viewport | Document client / scroll width | Result |
|---|---:|---|
| 1280 by 720 | 1,265 / 1,265 | pass |
| 390 by 844 | 375 / 375 | pass |

The 1800 by 1240 evidence image loads at both viewports. Desktop and narrow
screens show zero overflowing elements and zero browser warnings or errors.
Only eight train and validation patches render. Test patches, statistics, and
results do not render.

Forty focused contract, split, materialization, sufficiency, and independent-QA
tests pass with 204 retained NumPy deprecation warnings. Compilation and
`git diff --check` pass.

After the U04 outputs and records commit at
`289ed09b7760a0f2e00efbdbf8f4939dd8aa5b04`, the clean full repository suite
passes 683 tests, one expected skip, 228 retained NumPy deprecation warnings,
and 86 subtests in 713.56 seconds.

## Boundary and handoff

The accepted decision is:

`PASS_INDEPENDENT_DATASET_QA_AUTHORIZE_BASELINE_PREREGISTRATION_ONLY`

Analytical test-open count remains zero. No baseline method, threshold, metric,
model, training run, inference, deployment, or external submission advances.
U05 must research and freeze the non-model baselines before the one authorized
test opening. Training remains unauthorized.
