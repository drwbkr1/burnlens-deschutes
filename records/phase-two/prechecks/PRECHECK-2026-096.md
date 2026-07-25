# PRECHECK-2026-096 - P2O5-T03 U07 coherent release candidate

**Date:** 2026-07-25

**Issue:** #562

**Package-sensitive candidate:** `4655db6232077445de6da8a775499d558d8a8443`

**Accepted portfolio run:** `BL-2026-07-25-p2o5-t03-u07-portfolio-r003`

**Disposition:** `candidate-pass-not-released`

## Coherent Phase Two outcome

U07 packages the accepted Phase Two evidence without changing its analytical
values:

- dataset `burnlens-dataset-v0.1.0`;
- split `burnlens-whole-event-split-v0.1.0`;
- baseline `burnlens-baseline-v0.1.0`;
- model-readiness decision `AUTHORIZE_BOUNDED_UNET`;
- model version null.

The authorization remains delayed until this release is merged, tagged, and
verified. It permits only the exact rejection-first single-model experiment
in `BOUNDED-UNET-TRAINING-CONTRACT-2026-001`.

## Repository-owned reviewer experience

Generator source `403a2f3b74cadca59f81a1bf68ab0a4e1d451906` creates:

| Output | Bytes | SHA-256 |
|---|---:|---|
| `BURNLENS-PORTFOLIO-REVIEWER-EXPERIENCE-2026-004.json` | 7,473 | `1fc9f1e66af44aeb20e7168c1e9b3fde63579117647212680d5f0e94429a6d94` |
| `BURNLENS-PORTFOLIO-REVIEWER-EXPERIENCE-2026-004.html` | 15,980 | `cc64bbceb2f6c490dc4a84e6bf9322800820591a5c05e252f665da2ce7d9ee10` |

An independent ignored replay matches both bytes exactly.

Real Chromium rendering passes:

- desktop: document 1,280 / viewport 1,280 CSS pixels;
- narrow: document 390 / viewport 390 CSS pixels;
- both 1,800-pixel evidence images load;
- the first keyboard focus is `Skip to evidence`;
- the dataset, split, baseline, null model, source roles, selected-core risk,
  and Petes Lake stop are visible;
- browser diagnostics and external requests are empty.

## Retained reviewer failures

R001 / report `2026-002` is retained in ignored no-overwrite custody. Shifted
positional bindings linked the Petes image and decision to the dataset and
split. Exact output hashes are `66dbd4aa...` and `681c1433...`.

R002 / report `2026-003` corrects those bindings but does not explicitly show
that candidate construction may favor spectral separability. Exact output
hashes are `0c4f6ba6...` and `927af4a2...`.

R003 uses unique role-based binding lookup, verifies that every rendered image
is a PNG, and displays the candidate-selection-bias warning.

## Runtime and regression verification

The first lean-profile full-suite command is invalid evidence: the lean
environment intentionally lacks GeoPandas and stops during collection. The
locked `dev + geo-research` profile is restored.

Canonical r002 then reports 693 passes, one expected skip, 228 warnings, 86
subtests, and two release-contract failures:

1. runtime smoke expected the previous 99-command roster;
2. the new devlog lacked an explicit LF checkout rule.

Commit `4655db6232077445de6da8a775499d558d8a8443` updates only those
release contracts. The focused six-test gate passes. Canonical r003 then
passes 695 tests, one expected skip, 228 retained warnings, and 86 subtests in
649.22 seconds.

`uv lock --check`, locked profile synchronization, compilation, focused
portfolio/data/model tests, and `git diff --check` pass.

## Deterministic package and isolated runtime

Two exact Git archives of candidate `4655db6...`, built at
`SOURCE_DATE_EPOCH=1785016562` and `PYTHONHASHSEED=0`, produce identical
wheels:

- `burnlens_deschutes-0.52.0-py3-none-any.whl`;
- 1,050,456 bytes;
- SHA-256
  `eff2396b1c9bde38b0b5de5464169798874015259659dd460dc035186e22db99`.

The wheel contains 221 unique safe entries, correct 0.52.0 and Python 3.12
metadata, the MIT license, and no private/download/credential path.

A fresh ignored CPython 3.12.10 environment installs 13 compatible
distributions and imports BurnLens from isolated `site-packages`. All 105
console commands, including the six dataset/readiness commands, pass
`--help`.

The first command-roster query is retained as invalid verification because a
PowerShell newline escaped into the Python expression and returned zero
commands. The delimiter-safe rerun establishes the 105-command result.

## Boundary and next dependency

No model, weights, training run, model evaluation, inference, deployment,
external submission, GitHub Release, access, ownership, or public-sharing
change exists. One milestone PR, fresh-main repetition, and exact annotated
tag peel remain mandatory before Phase Three may execute the training
contract.
