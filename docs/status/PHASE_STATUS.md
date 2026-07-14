# BurnLens Phase Status

## Status as of 2026-07-14

| Phase | Proof outcome | Status | Evidence and next gate |
|---|---|---|---|
| 1 — Scope and controls | Coherent promise, task, source posture, repository controls, traceability, and acceptance evidence | **Accepted and versioned for Phase Two planning; no analytical release** | P1O7-T08 / PR #294 records the decision. #290 / PR #291 and `v0.0.8-execution-goal-baseline` establish the current control baseline. |
| 2 — Data foundation | Legally usable, versioned, leakage-resistant data/label/baseline package with model-readiness decision | **Active; authenticated source/reference package accepted; labels and dataset deferred** | The final AOI and atomic transaction are shipped. Issue #329 / PR #330 acquires, registers, re-verifies, and inspects the exact provider package. Real scan-edge and resolution evidence prevents direct label promotion. |
| 3 — Model evidence | One bounded model adds reproducible value beyond the strongest baseline or is rejected honestly | **Blocked** | Requires an accepted Phase Two package and target decision. |
| 4 — CV-to-GEOINT product | Accepted model/baseline becomes a valid georeferenced run and repository-owned evidence interface | **Blocked** | Requires an accepted Phase Three model or Phase Two baseline-only route. |
| 5 — Reliability | Integrated system is reproducible, accessible, secure, failure-visible, performant, and reversible | **Blocked** | Requires an accepted Phase Four run package and interface. |
| 6 — Publication | One coherent, licensed, citable, traceable portfolio release and closeout | **Blocked** | Requires an accepted Phase Five candidate, resolved licensing, verified claims, and a repository-owned production surface. |

## Verified capability inventory

| Evidence class | Current state |
|---|---|
| Latest repository evidence baseline | `7678cf41b64e128106c199b913fe74590a52cf80` via merged PR #330 and verified annotated `v0.4.0-authenticated-source-baseline` |
| Authenticated source baseline | BurnLens `0.4.0`; issue #329 / PR #330; generator source `9a7e614fbfbbcd4c5a6795417121cafb82ae5dcc`; annotated tag object `98228058b232bc0838eb976f982ef4775b711776`; 56 post-merge tests passing |
| Objective baseline tag | `v0.0.8-execution-goal-baseline`, verified to resolve to `22a8d88435cb8d5b900a398b7482c3b7277d2ee6` |
| Source-metadata baseline | `v0.1.0-source-metadata-baseline`, verified to resolve to `6abe87bba486e3fe49b6c06178b454335663cb73` via PR #310 |
| Asset-readiness baseline | `v0.1.1-asset-readiness-baseline`, verified annotated tag resolving to `cf4aba2f40aa426f28f09b1b1b1bad895394198b` via PR #314 |
| Access-integrity baseline | `v0.1.2-access-integrity-baseline`, verified annotated tag resolving to `d4ce26c87341e4d3798a0d84e257a964ebd2cde0` via PR #318 |
| AOI baseline | `v0.2.0-aoi-baseline`, verified annotated tag resolving to `fffd3dda123d7c43fe678dca9adfd8feb73de158` via PR #322 |
| Intake transaction baseline | BurnLens `0.3.0`; issue #325 / PR #326; merge `ee1a1d678ad888b595dc3c7b215f787ea5156582`; annotated `v0.3.0-intake-transaction-baseline`; `paired-intake-contract-v0.4.0`; full contract SHA-256 `5135b6b0b554e533df98ede568b1eafbd45c692b73a1e1abd3e50ba098f0958d`; provider assets/bytes and retained synthetic fixture bytes all zero |
| Credential use | `ACCESS-2026-006` authorizes both providers; `ACCESS-2026-007` records successful runtime-only use with no credential, token, cookie, signed URL, or credential-store detail retained |
| Application version | Not created |
| AOI version | `aoi-darlene3-model-v0.2.0`, accepted and shipped final modeling AOI; 12 km by 9 km / 108 km2 in EPSG:32610; lower priority than official sources |
| Source records | `SOURCE-2026-001` through `SOURCE-2026-007`; the newest record is one immutable public NIFC reference vector, not a label or detection |
| Metadata fixture | `METADATA-2026-001`, five Sentinel items and 124 NASA VIIRS granule records; no asset hrefs or source bytes |
| Asset-readiness fixture | `ASSET-READINESS-2026-001`, SHA-256 `c5bcfbf57cf23a7bf3ed9bd1302461b2ba1ee101ab05b7d935419223763e5ce7`; metadata only, zero provider bytes |
| Evidence tooling | Shipped BurnLens `0.4.0`; secret-safe acquisition, resumable exact-size delivery, authenticated atomic registration, real JP2/HDF5 inspection, geolocation/QA checks, normalized JSON, semantic HTML, and PNG rendering |
| Access-precheck report | `VIIRS-ACCESS-PRECHECK-2026-001`; JSON SHA-256 `107c08e00539257d7b86265d316060f35c019c821acc59f89dfc4b8875205f7f`; decision `BLOCKED_OWNER_CREDENTIAL` |
| AOI evidence report | `AOI-FINAL-2026-001`; JSON SHA-256 `305ddda2eda96fa31e8fb410891d3dc9c0f2b4930af5fc8ee6d2df9bae0b856c`; decision `ACCEPT_FINAL_MODELING_AOI` |
| Paired-intake rehearsal | `PAIR-INTAKE-REHEARSAL-2026-001`; run `BL-2026-07-14-paired-intake-rehearsal-r001`; JSON SHA-256 `94e311fd608f9c10e024138d9eff6abf0f70187a69c031264e91cb8d9d1af234`; historical pre-authorization decision `BLOCKED_OWNER_CREDENTIAL`; metadata observed 2026-07-14 with no live request; four synthetic transaction/integrity checks pass |
| Authenticated raw package | `darlene3-s2-viirs-pair-v0.1.0`; acquisition run `BL-2026-07-14-authenticated-intake-r001`; three exact provider assets / 1,169,997,942 bytes in ignored local storage; zero raw provider bytes committed |
| Source inspection report | `SOURCE-INSPECTION-2026-001`; run `BL-2026-07-14-source-inspection-r001`; JSON `cbd4dfba840680256a100aeca1a2e0b28483796f7e7b79b90de8b933d58b0a53`; HTML `76d13d3e105f053410d0063b17eb740f732c786dc395fe13335701496cbb41a0`; PNG `da93de6e432296f72c8f420d0181cfc81d99be7cf70ad96fe5b7bba619739966`; decision `ACCEPT_SOURCE_REFERENCE_DEFER_LABELS` |
| Dataset version | Not created |
| Label-schema implementation | Not created |
| Baseline-method version | Not created |
| Model version | Not created |
| Run IDs | Latest evidence runs are `BL-2026-07-14-authenticated-intake-r001` and `BL-2026-07-14-source-inspection-r001`; no label, dataset, baseline, model, or analytical inference output |
| Raster/vector/map output | One official reference vector, one derived AOI vector, static control evidence, and one real-source inspection visualization; no segmentation, imagery-derived analytical raster/vector, or fire perimeter |
| Repository-owned public application | Not created |
| Public performance claim | None authorized or supported |

## Latest shipped checkpoint

P2O2-T03 / issue #329 accepts the exact authenticated package for source/reference use and adds `SOURCE-INSPECTION-2026-001` while deferring labels and a dataset. PR #330 merged at `7678cf41b64e128106c199b913fe74590a52cf80`; the annotated `v0.4.0-authenticated-source-baseline` tag object `98228058b232bc0838eb976f982ef4775b711776` remotely dereferences to that exact commit. Fifty-six post-merge tests, compilation, dependency health, byte-identical real-source reconstruction, rendered-browser review, issue closure, raw-byte/secret exclusion, and remote tag identity passed verification.

## Current checkpoint

P2O2-T03-SYNC / issue #331 on `codex/p2o2-t03-sync` is the active provenance-only checkpoint. It records the exact PR #330 merge, annotated tag, post-merge checks, run/output identities, and next evidence checkpoint. It changes no scientific output, credential state, or raw provider byte.

## Selected next checkpoint

After P2O2-T03-SYNC ships, investigate whether alternate temporally relevant VIIRS observations materially improve scan geometry and define a versioned weak/reference-label feasibility protocol that preserves unknown and excluded pixels. The current package remains valid source/reference evidence but cannot be promoted directly to labels. Changing to the controlled burn-scar fallback still requires the owner decision defined by the execution goal.

## Boundaries carried forward

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

All BurnLens work and future public surfaces must originate from `drwbkr1/burnlens-deschutes`; the separate site repository is out of scope.

No application or deployed public companion site exists in this repository yet. The repository README, living case study, and static semantic/visual AOI, intake, and source-inspection evidence are the updated presentation surfaces for this checkpoint.
