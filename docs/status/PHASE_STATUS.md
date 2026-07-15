# BurnLens Phase Status

## Status as of 2026-07-14

| Phase | Proof outcome | Status | Evidence and next gate |
|---|---|---|---|
| 1 — Scope and controls | Coherent promise, task, source posture, repository controls, traceability, and acceptance evidence | **Accepted and versioned for Phase Two planning; no analytical release** | P1O7-T08 / PR #294 records the decision. #290 / PR #291 and `v0.0.8-execution-goal-baseline` establish the current control baseline. |
| 2 — Data foundation | Legally usable, versioned, leakage-resistant data/label/baseline package with model-readiness decision | **Active; burn-scar fallback approved; labels and dataset not created** | P2O2-T04 rejects direct active-fire label promotion. P2O2-T05 / #337 / PR #338 activates `target-burn-scar-v0.2.0`; #339 corrects a caught post-merge determinism defect before tagging. A defensible pre/post optical pair plus label protocol remains next. |
| 3 — Model evidence | One bounded model adds reproducible value beyond the strongest baseline or is rejected honestly | **Blocked** | The target decision is resolved; an accepted Phase Two label/dataset/baseline package and model-readiness decision are still missing. |
| 4 — CV-to-GEOINT product | Accepted model/baseline becomes a valid georeferenced run and repository-owned evidence interface | **Blocked** | Requires an accepted Phase Three model or Phase Two baseline-only route. |
| 5 — Reliability | Integrated system is reproducible, accessible, secure, failure-visible, performant, and reversible | **Blocked** | Requires an accepted Phase Four run package and interface. |
| 6 — Publication | One coherent, licensed, citable, traceable portfolio release and closeout | **Blocked** | Requires an accepted Phase Five candidate, resolved licensing, verified claims, and a repository-owned production surface. |

## Verified capability inventory

| Evidence class | Current state |
|---|---|
| Latest repository evidence baseline | `1c85496d9d488c0d2d5a58207d8b4786a683ba52` via merged PR #334 and verified annotated `v0.5.0-observation-geometry-baseline` |
| Observation-geometry baseline | BurnLens `0.5.0`; issue #333 / PR #334; generator source `89d50c24a696cc7e3ec023eec00b021a4a0cdda6`; tag object `cb9e675789d8ca4c4f8a5f4828331d41d023038e`; 65 post-merge tests passing |
| Burn-scar target decision candidate | BurnLens `0.6.0`; issue #337 / PR #338 merged at `68971e9709b886adf8575a58d32694aad42f038e`; issue #339 / PR #340 remediation source `cfbf357634cdcf9e68c3af78bfcb3e195bebc17a`; target `target-burn-scar-v0.2.0`; tag pending; no label, dataset, baseline, or model |
| Authenticated source baseline | BurnLens `0.4.0`; issue #329 / PR #330; generator source `9a7e614fbfbbcd4c5a6795417121cafb82ae5dcc`; annotated tag object `98228058b232bc0838eb976f982ef4775b711776`; 56 post-merge tests passing |
| Objective baseline tag | `v0.0.8-execution-goal-baseline`, verified to resolve to `22a8d88435cb8d5b900a398b7482c3b7277d2ee6` |
| Source-metadata baseline | `v0.1.0-source-metadata-baseline`, verified to resolve to `6abe87bba486e3fe49b6c06178b454335663cb73` via PR #310 |
| Asset-readiness baseline | `v0.1.1-asset-readiness-baseline`, verified annotated tag resolving to `cf4aba2f40aa426f28f09b1b1b1bad895394198b` via PR #314 |
| Access-integrity baseline | `v0.1.2-access-integrity-baseline`, verified annotated tag resolving to `d4ce26c87341e4d3798a0d84e257a964ebd2cde0` via PR #318 |
| AOI baseline | `v0.2.0-aoi-baseline`, verified annotated tag resolving to `fffd3dda123d7c43fe678dca9adfd8feb73de158` via PR #322 |
| Intake transaction baseline | BurnLens `0.3.0`; issue #325 / PR #326; merge `ee1a1d678ad888b595dc3c7b215f787ea5156582`; annotated `v0.3.0-intake-transaction-baseline`; `paired-intake-contract-v0.4.0`; full contract SHA-256 `5135b6b0b554e533df98ede568b1eafbd45c692b73a1e1abd3e50ba098f0958d`; provider assets/bytes and retained synthetic fixture bytes all zero |
| Credential use | `ACCESS-2026-006` authorizes both providers; `ACCESS-2026-007` and `ACCESS-2026-008` record successful runtime-only use with no credential, token, cookie, signed URL, or credential-store detail retained |
| Application version | Not created |
| AOI version | `aoi-darlene3-model-v0.2.0`, accepted and shipped final modeling AOI; 12 km by 9 km / 108 km2 in EPSG:32610; lower priority than official sources |
| Source records | `SOURCE-2026-001` through `SOURCE-2026-008`; the newest record is the exact NOAA-21 observation inventory and selected companion, not a label or detection |
| Metadata fixture | `METADATA-2026-001`, five Sentinel items and 124 NASA VIIRS granule records; no asset hrefs or source bytes |
| Asset-readiness fixture | `ASSET-READINESS-2026-001`, SHA-256 `c5bcfbf57cf23a7bf3ed9bd1302461b2ba1ee101ab05b7d935419223763e5ce7`; metadata only, zero provider bytes |
| Evidence tooling | BurnLens `0.6.0` branch candidate; shipped acquisition/intake/source/geometry paths plus deterministic burn-scar target-decision validation and JSON/HTML/PNG rendering |
| Access-precheck report | `VIIRS-ACCESS-PRECHECK-2026-001`; JSON SHA-256 `107c08e00539257d7b86265d316060f35c019c821acc59f89dfc4b8875205f7f`; decision `BLOCKED_OWNER_CREDENTIAL` |
| AOI evidence report | `AOI-FINAL-2026-001`; JSON SHA-256 `305ddda2eda96fa31e8fb410891d3dc9c0f2b4930af5fc8ee6d2df9bae0b856c`; decision `ACCEPT_FINAL_MODELING_AOI` |
| Paired-intake rehearsal | `PAIR-INTAKE-REHEARSAL-2026-001`; run `BL-2026-07-14-paired-intake-rehearsal-r001`; JSON SHA-256 `94e311fd608f9c10e024138d9eff6abf0f70187a69c031264e91cb8d9d1af234`; historical pre-authorization decision `BLOCKED_OWNER_CREDENTIAL`; metadata observed 2026-07-14 with no live request; four synthetic transaction/integrity checks pass |
| Authenticated raw package | `darlene3-s2-viirs-pair-v0.1.0`; acquisition run `BL-2026-07-14-authenticated-intake-r001`; three exact provider assets / 1,169,997,942 bytes in ignored local storage; zero raw provider bytes committed |
| Source inspection report | `SOURCE-INSPECTION-2026-001`; run `BL-2026-07-14-source-inspection-r001`; JSON `cbd4dfba840680256a100aeca1a2e0b28483796f7e7b79b90de8b933d58b0a53`; HTML `76d13d3e105f053410d0063b17eb740f732c786dc395fe13335701496cbb41a0`; PNG `da93de6e432296f72c8f420d0181cfc81d99be7cf70ad96fe5b7bba619739966`; decision `ACCEPT_SOURCE_REFERENCE_DEFER_LABELS` |
| Observation geometry report | `OBSERVATION-GEOMETRY-2026-001`; run `BL-2026-07-14-observation-geometry-r002`; JSON `c1da1c47483ab573a8a123a26f7c5b2f111b57b4eaedb05ffb2d3aafa46e881d`; HTML `a63ee62c660c7b573d829847ac008786a6ecff91c61f5433365e640f64742ad2`; PNG `4dd21c3df693856fda47d23cd763054016a105d8c760181c4052411fa4ff6687`; decision `ACCEPT_COMPLEMENTARY_REFERENCE_GEOMETRY_DEFER_LABELS` |
| Target decision report | Corrected `TARGET-DECISION-2026-002`; run `BL-2026-07-14-target-decision-r002`; JSON `ac67f6c34a934d639c215ee98b181f1114b5624acafb85f65b1e2f3e804ce4d4`; HTML `0c1279e5e1047ff251dcd65f068d3d45bf2c6982e6a308972205e9d0a76879d4`; PNG `36f221aa6393ad07f14d4d7bb54b1f171ef0636ebb5640a11ab02ab9c5a9b5b0`; fallback active; all analytical versions null; `001` retained as the superseded pre-remediation run |
| Dataset version | Not created |
| Label-schema implementation | Not created |
| Baseline-method version | Not created |
| Model version | Not created |
| Run IDs | Latest corrected evidence run is `BL-2026-07-14-target-decision-r002`; `r001` is preserved as pre-remediation evidence; no label, dataset, baseline, model, or analytical inference output |
| Raster/vector/map output | One official reference vector, one derived AOI vector, static control evidence, one source-inspection visualization, and one observation-comparison visualization; no segmentation, imagery-derived analytical raster/vector, or fire perimeter |
| Repository-owned public application | Not created |
| Public performance claim | None authorized or supported |

## Latest shipped checkpoint

P2O2-T04 / issue #333 accepts the `A2024179.2118` observation as materially improved complementary native-scale reference evidence while deferring labels and a dataset. PR #334 merged at `1c85496d9d488c0d2d5a58207d8b4786a683ba52`; annotated `v0.5.0-observation-geometry-baseline` tag object `cb9e675789d8ca4c4f8a5f4828331d41d023038e` remotely dereferences to that exact commit. Sixty-five post-merge tests, compilation, dependency health, byte-identical real-package reconstruction, rendered-browser review, issue closure, raw-byte/secret exclusion, and remote tag identity passed verification.

## Current checkpoint

P2O2-T05 / issue #337 / PR #338 merged at `68971e9709b886adf8575a58d32694aad42f038e`. Post-merge verification correctly withheld the tag when `r001` reconstruction exposed checkout-dependent input hashing. Issue #339 / PR #340 on `codex/p2o2-t05-eol-determinism` is the active bounded remediation; it preserves `r001`, adds explicit LF-normalized structured-input hashes and LF serialization, and publishes immutable corrected run `r002`. It changes no target, phase outcome, use boundary, or scientific finding and creates no label, dataset, baseline, model, or analytical wildfire output.

The next analytical gate is one exact, legally usable, visually inspected pre/post optical pair and an uncertainty-preserving binary burn-scar label protocol. The protocol must distinguish burned, background-candidate, unknown, excluded, and review-needed states and address georegistration, optical quality, temporal leakage, and independent QA before label construction.

## Boundaries carried forward

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

All BurnLens work and future public surfaces must originate from `drwbkr1/burnlens-deschutes`; the separate site repository is out of scope.

No application or deployed public companion site exists in this repository yet. The repository README, living case study, and static semantic/visual AOI, intake, source-inspection, observation-geometry, and target-decision evidence are the updated presentation surfaces for this checkpoint.
