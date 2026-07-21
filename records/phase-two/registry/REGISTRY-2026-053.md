# REGISTRY-2026-053 - Petes Lake replacement U03 source fitness

**Unit / issue / branch:** `P2O4-T33-U03_REPLACEMENT_SOURCE_FITNESS_R002` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Final run:** `BL-2026-07-21-petes-lake-replacement-source-fitness-r002`

**Source commit:** `d42022b5bfd1eb58f487666745e1d8f1c33db45c`

**Decision:** `PASS_EXACT_PETES_LAKE_REPLACEMENT_OPTICAL_SOURCE_FITNESS_WITH_SPATIAL_EXCLUSIONS`

**Disposition / next dependency:** `pass-with-spatial-exclusions` / `P2O4-T33-U04`

## Public tracked evidence

| Artifact | Bytes | SHA-256 | State |
|---|---:|---|---|
| `samples/cross-event/phase-two/petes-lake/PETES-LAKE-REPLACEMENT-SOURCE-FITNESS-2026-001.json` | 60,069 | `1aa88c0021c610e492d2645e3f2c49a4afe96d9d907e2ee4481948a4c58f2ebd` | exact machine, custody, prior-evidence, and visual disposition; U04 authorized |
| `samples/cross-event/phase-two/petes-lake/PETES-LAKE-REPLACEMENT-SOURCE-FITNESS-2026-001.png` | 588,891 | `fd5b9ae54e1b9c3e0d495e337387d874ae911bd0f586e835b4184312d486d931` | exact 1,800 x 1,240 actual render; original-resolution inspection pass |
| `docs/phase-two/objective-four/PETES_LAKE_REPLACEMENT_SOURCE_FITNESS_DECISION.md` | 3,341 | `1a939282ad4f43c68e9e1e0383b525e8547be5a884cc4896d7ee14884c016506` | bounded human-readable pass-with-exclusions decision |
| `records/phase-two/prechecks/PRECHECK-2026-051.md` | 2,821 | `b028738a0dbb5e7f75fbb98edf6b64c2349f0792abaf39547b29fb11fa5d3c80` | exact gate and reproduction summary |
| `records/phase-two/reviews/SOURCE_FITNESS-2026-008.md` | 2,689 | `0c6905ad040ba2d80b7779c0b87da333d69f3723c2c3d7f26dbbf9ba7f0d88fa` | source-fitness review |

No HTML output is in the tracked U03 replacement roster.

## Immutable ignored runs

| Run / artifact | Bytes | SHA-256 | Custody state |
|---|---:|---|---|
| preview r002 JSON | 59,756 | `398f3e0e137efa58814a9ea238851092423804a8bf11a72639c25cfdff0e3a42` | no-overwrite; ignored; untracked; pending visual state |
| preview r002 PNG | 588,662 | `5d471201366d8402259c442a341b0fab24b18fc00698f7171d151b9c84ac80df` | no-overwrite; ignored; untracked; original-resolution inspection pass |
| replay r002 JSON | 60,069 | `1aa88c0021c610e492d2645e3f2c49a4afe96d9d907e2ee4481948a4c58f2ebd` | no-overwrite; ignored; untracked; byte-identical to final JSON |
| replay r002 PNG | 588,891 | `fd5b9ae54e1b9c3e0d495e337387d874ae911bd0f586e835b4184312d486d931` | no-overwrite; ignored; untracked; byte-identical to final PNG |

The preview differs only in generation time, run ID, and pending visual state. The replay uses the final report's exact generation time, run ID, source commit, decision, and notes and reproduces both tracked bytes exactly. No run is overwritten or deleted.

## Exact input bindings

| Input | Exact binding | Fresh r002 result |
|---|---|---|
| Additional-event plan | SHA-256 `65fd567e234cbb521ead6b7071cab9914c672df169e3987af0c3ddfc66ccf622`; frozen source snapshot SHA-256 `3d6ca59b8071461aa925a3b270300deea1f53c8bd46aedeaec10ddd5301fc241` | Petes Lake remains third, MTBS-only event group; full boundary unchanged |
| Failed planned-pair report | 56,285 bytes / SHA-256 `ac9befd021d71ff779ec56ddefc894f4e39b92e64e65c2c4afb815663d1ad443` | exact immutable U03 r001 failure retained |
| Replacement-selection report | 10,127 bytes / SHA-256 `7fa82a61fa70d47364db29493700beedd60c9114a4b3a6d8ddbafdf77aecfc8c` | exact deterministic Oct. 19 selection retained |
| Replacement custody report | 22,246 bytes / SHA-256 `e23d601959d09fb54fc6409f5a073df4f1a3a3a8a0d040e04a9b46c2594537b1`; semantic SHA-256 `78c888b4a3b954c4038a3454773b1cd7c922bc5f71957524e803ee6534d71f75` | exact decision and original-pre/replacement-post transaction bindings pass |
| Original pre archive | 1,185,284,273 bytes / local SHA-256 `c5b6ededc5a264fcc617f2712093b847351c5b8ed78f2ea9ce0ebc3a33e1bc34` | fresh registered-package verification and native raster inspection pass |
| Replacement post archive | 1,195,226,823 bytes / local SHA-256 `8bf6ffac0d46d17b6f3716250aed9dff49b9f89b62a310c296a5d36f41a0e1d9` | fresh registered-package verification and native raster inspection pass |

Both archives remain ignored, untracked, no-overwrite, single-link, and byte-identical to custody. No credential, token, provider request, or custody mutation occurs in source fitness.

## Code and test checkpoint

| Artifact | Bytes | SHA-256 | Role |
|---|---:|---|---|
| `burnlens/petes_lake_source_fitness.py` | 32,824 | `defccdc78a7748b80c6d940a74fb92e2649f8a0512092549a2e98463d2a94407` | established measurement/render helpers with product-derived dates |
| `burnlens/petes_lake_replacement_source_fitness.py` | 19,125 | `981f38526df2a66726f9ee7a192c59c25183681e96f1df874227dadd807c6013` | exact replacement custody/prior-evidence binding, measurement, decision, render, and no-overwrite outputs |
| `burnlens/inspect_petes_lake_replacement_source_fitness.py` | 5,481 | `f3fc8be9962ccc7ac7311011bab38cf4d98f16dac926391590bb2b7d3744117f` | clean, committed, remote-equal preview/final production CLI |
| `tests/test_petes_lake_replacement_source_fitness.py` | 5,513 | `3ad662ea87cc8ac71e960c25e943d5382cce7b410ab2567085f1c2926ccfaae9` | exact custody, prior-failure, real-pair metric, no-label, no-overwrite, and output-roster regression |

## Gate results

- Exact source, terms, custody, prior-failure, selection, archive hash, SAFE structure, processing baseline, raster member, CRS, native resolution, grid, transform, shape, data type, nodata, saturation, reflectance-offset, full-boundary, chronology, no-overwrite, ignore/privacy, warning, and trace gates: pass.
- Timestamp reconciliation: catalogue product start `2023-10-19T19:04:11.024000Z`; delivered tile sensing `2023-10-19T19:12:24.432471Z`; distinct fields retained on the same UTC date.
- Pair quality: 33,365 eligible / 97.8360%; 134 review-needed / 0.3929%; 604 excluded / 1.7711%.
- Replacement local quality: zero SCL cloud, cloud shadow, cirrus, snow/ice, nodata, or saturation; native CLD/SNW minimum, maximum, mean, and every percentile are zero.
- Registration: eight windows; five pass; three review-needed; zero excluded; zero fail-registration; p50 0.1995 pixel; p95 0.3732; maximum 0.3785 pixel / 7.57 m. Established untuned event gate returns pass with spatial exclusions.
- Continuous dNBR: 33,365 valid pixels retained without threshold, severity, burned, background, or unknown semantics.
- Actual render: preview and final 1,800 x 1,240 PNGs pass original-resolution author audit for alignment, cloud, smoke/haze, shadow, snow, clipping, invalid/excluded display, warning, trace, and no-label boundaries.
- Reproduction: final JSON and PNG reconstruct byte-identically from the exact source commit and ignored custody.
- Verification: nine focused tests pass; full repository passes 460 tests plus 50 subtests with 20 existing NumPy deprecation warnings; all 66 installed packages are compatible; lock, compilation, and diff hygiene pass.

U03 replacement disposition is `pass-with-spatial-exclusions`. U04 is authorized to inspect the exact official reference delivery, but this unit creates no reference, candidate, owner response, prototype label, sixth complete event, dataset, split, baseline, model, metric, release, field-validation, official, endorsed, operational, or emergency-ready claim.
