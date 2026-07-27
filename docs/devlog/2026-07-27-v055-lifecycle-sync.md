# BurnLens 0.55 lifecycle sync

## Verified result

P5O1-T01 / issue #574 / PR #575 is verified. Exact reviewed head
`3eb2d0a58bd7236c28df4ba50058afcedd581003` merges through true two-parent
commit `7066dcd9cef555a6df0716dc7568205e7d6d395e`. Both commits have tree
`cf7c6e184e402fd2183e40d7da2ba3b2cb95a23a`.

Remote annotated tag object
`33072144767e70bfa538079bda3be6f798477a9f` peels exactly to that merge as
`v0.55.0-baseline-first-reliability-candidate`.

## Fresh-main evidence

Fresh merged main passes 789 tests, one expected skip, 422 existing warnings,
and 86 subtests in 656.97 seconds. The exact 9,639-byte stdout log has SHA-256
`afa98909452a64b963ad6f934ab89cdf81a4c81984180d3abe5c0d0b01518a5f`.
Focused checkout and candidate validation passes seven tests. Both candidate
directory and archive validators pass.

The first fresh-main wheel wrapper is retained as a tool failure because it
promoted uv's normal build-progress stderr line to failure. The corrected
native-exit wrapper changes no source and builds the exact reviewed
1,207,948-byte BurnLens 0.55.0 wheel at SHA-256
`1d0e862c9c7d30f148352ebcc45f22a9deb2e010dd61ba63a02db50f700177f6`.
Its 115,240-byte native build log has SHA-256
`35bbe6c303aec75f2c69ee86c8c735cfc1a547daab2747343317448166ce64a3`.

## Candidate and findings

The verified Phase Five candidate remains
`burnlens-phase-five-baseline-first-candidate-v0.1.1`, run
`BL-2026-07-26-p5o1-t01-u06-release-candidate-r002`: 23 files / 981,264
bytes and one 646,513-byte ZIP at SHA-256
`691c4bddb6754d74ca858a0b801fb21e62103032184425d2ba1b1648df1b0c26`.
The exact rendered application, links, keyboard route, isolated profiles,
deterministic replay, and rollback remain passed.

Two medium findings remain visible with impact and workaround: the bounded
Windows ZIP-only setuptools advisory and the historical Phase Four builder
identity omission. No critical or high finding is open.

## Boundary and handoff

This lifecycle sync changes records and current-truth documentation only. It
does not change software, analytical bytes, dataset, split, label, threshold,
source, AOI, baseline, model, geospatial product, candidate package, ZIP,
provider custody, deployment, access, ownership, sharing, or submission.

RBR remains the accepted analytical method. The trained U-Net remains a
rejected first-class diagnostic and did not outperform RBR. No Phase 3B or
second experiment is created.

Phase Five is accepted and verified. Phase Six is eligible for a separate
issue-backed publication-and-closeout checkpoint. No GitHub Release,
deployment, public-sharing change, or external submission has occurred.
