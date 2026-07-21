# Grandview Owner Review Surface Decision

**Issue / PR / branch:** #511 / #518 / `codex/p2o4-t31-grandview-owner-review-surface`

**Run:** `BL-2026-07-21-grandview-owner-review-surface-r001`

**Generator / artifacts:** `91ba39ceb4b6d8444255d734eb7a6cc393f933af` / `33c7c871dcdb2546cf3fd8fe97e01e109cee8026`

## Candidate decision

`SURFACE_READY_FOR_GRANDVIEW_OWNER_REVIEW_KEEP_RESPONSE_INTAKE_SEPARATE`.

BurnLens 0.43.0 rebuilds and byte-binds all five verified v0.42 proposal outputs before it renders a question. It reopens both candidate rasters and verifies EPSG:32610, the 0/1/2 domain, exact 25-pixel cores, 46/52-pixel unknown rings, source/run tags, and `label_created=false`.

Each question shows actual pre-fire, post-fire, and extended 2022 optical pixels. `GVP-001` then shows pre/post dNBR and MTBS classes 2-4; `GVP-002` shows anniversary dNBR and the affirmative background route. The page makes the burned proposal's low observed positive dNBR visible. RAVG modeled classes remain context-only under the exact sparse/non-tree warning and are not shown or used as affirmative evidence.

The response contract permits only yes, no, or uncertain. It exports deterministic UTF-8 LF bytes to a SHA-256-named file, supports draft reload only after exact surface/run/schema/proposal/raster binding checks, clears stale choices, requires owner attestation, and locks controls after a completed export or reload. The tracked template remains blank. No completed response is inspected or accepted here.

Six outputs reconstruct byte for byte. The original-resolution overview exposes all ten evidence panels and the zero-response/zero-label boundary. Controller syntax, focused real-custody tests, semantic checks, proposal/raster bindings, and no-external-link checks pass. Agent navigation to a local `file://` page remains policy-blocked and is not bypassed; issue #517 owns exact completed-response custody only after this release is verified.

This checkpoint establishes review-surface readiness, not owner acceptance, independent ground truth, inter-rater agreement, field validation, official or endorsed status, a dataset, split, baseline, model, metric, accuracy, operational readiness, or emergency readiness.

PR #518 reviewed head `248f601485c813d7dd2f629195ead75eb325465f` merges at verified checkpoint `aeea6f5cc488ae975badbdf654d0164570db77c4`. Fresh main passes 313 tests with 17 expected custody skips, 111 JSON parses, zero surface JSON/HTML CRLF, all six exact hashes, and canonical clean-clone packaging. Annotated tag object `d679521edcc1d5b1bfd3e8022036cae06a9f1978` remotely peels to the checkpoint. Issue #517 remains blocked on a later completed owner export.
