# PRECHECK-2026-097 - verified BurnLens 0.52 lifecycle truth

**Date:** 2026-07-25

**Issue:** #564

**Verified checkpoint:** `dfb11c8b823e224aceb76be74003464973e33c2d`

**Annotated tag object:** `7041ef76ff4aac17f3bc2f8ba07b427dc858d2bf`

**Disposition:** `verified-lifecycle-sync`

## Exact release result

PR #563 squash-merges reviewed head
`3a6871a0c484264c9bb09bd3907d00d0663adf18` at the verified checkpoint.
Issue #562 is closed. Remote tag
`v0.52.0-dataset-baseline-model-readiness` peels exactly to that merge.

Fresh merged `main` repeats the complete locked `dev + geo-research` suite:
695 tests pass, one expected test skips, 228 retained warnings remain visible,
and 86 subtests pass in 577.50 seconds.

The exact reviewer replay reproduces:

- JSON: 7,473 bytes / SHA-256 `1fc9f1e6...`;
- HTML: 15,980 bytes / SHA-256 `cc64bbce...`.

Lifecycle source `b52c9c237ed37ba07707c5339bd4343f3374319a` then builds the
current verified-release reviewer surface under run
`BL-2026-07-25-v052-lifecycle-portfolio-r001`:

- JSON: 7,668 bytes / SHA-256 `3b0db0a2...`;
- HTML: 16,341 bytes / SHA-256 `3c754e56...`.

The prior `2026-004` outputs remain unchanged candidate-era evidence.
An independent ignored replay matches both lifecycle outputs byte for byte.
Real Chrome passes 1,280 by 720 and 390 by 844 views with document widths
equal to each viewport, both 1,800-pixel evidence images loaded, skip-link
keyboard focus first, verified tag/commit/object and null model visible, no
console diagnostics, and zero external requests.

Two merged-main fixed-epoch builds reproduce the audited 1,050,456-byte
BurnLens 0.52.0 wheel at SHA-256 `eff2396b...`. Because the bytes match the
fully inspected candidate exactly, the 221 safe unique entries, version and
license metadata, privacy checks, 13-distribution isolated install, and all
105 command probes remain the release evidence.

## Current analytical boundary

The release accepts:

- `burnlens-dataset-v0.1.0`;
- `burnlens-whole-event-split-v0.1.0`;
- independent dataset QA;
- `burnlens-baseline-v0.1.0`;
- decision `AUTHORIZE_BOUNDED_UNET`;
- experiment mode `REJECTION_FIRST_SINGLE_MODEL_EXPERIMENT`.

The exact owner-approved prototype evidence remains 12 regions, 287 native
20-meter core pixels, and 531 excluded unknown-ring pixels across six
whole-event roles. Candidate construction may favor measured spectral
separability, and the perfect selected-core RBR result is not a full-scene
generalization claim.

No model, weights, training run, model metric, inference output, deployment,
field validation, official status, endorsement, operational readiness,
emergency suitability, or final-submission-ready claim exists.

## Next dependency

After issue #564 synchronizes current truth, open one separate Phase Three
milestone from the verified lifecycle base. It may execute only the exact
frozen rejection-first U-Net contract and may not tune on the sealed test role
or add a second model.
