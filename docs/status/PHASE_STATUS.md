# BurnLens Phase Status

## Status as of 2026-07-13

| Phase | Proof outcome | Status | Evidence and next gate |
|---|---|---|---|
| 1 — Scope and controls | Coherent promise, task, source posture, repository controls, traceability, and acceptance evidence | **Accepted and versioned for Phase Two planning; no analytical release** | P1O7-T08 / PR #294 records the decision. #290 / PR #291 and `v0.0.8-execution-goal-baseline` establish the current control baseline. |
| 2 — Data foundation | Legally usable, versioned, leakage-resistant data/label/baseline package with model-readiness decision | **Active; final AOI shipped; atomic intake candidate verified; provider imagery blocked** | Issue #321 / PR #322 ships the final modeling AOI. Issue #325 adds a tested exact-pair transaction candidate without using provider bytes. CDSE and Earthdata credentials remain owner-gated; provider imagery asset count is zero. |
| 3 — Model evidence | One bounded model adds reproducible value beyond the strongest baseline or is rejected honestly | **Blocked** | Requires an accepted Phase Two package and target decision. |
| 4 — CV-to-GEOINT product | Accepted model/baseline becomes a valid georeferenced run and repository-owned evidence interface | **Blocked** | Requires an accepted Phase Three model or Phase Two baseline-only route. |
| 5 — Reliability | Integrated system is reproducible, accessible, secure, failure-visible, performant, and reversible | **Blocked** | Requires an accepted Phase Four run package and interface. |
| 6 — Publication | One coherent, licensed, citable, traceable portfolio release and closeout | **Blocked** | Requires an accepted Phase Five candidate, resolved licensing, verified claims, and a repository-owned production surface. |

## Verified capability inventory

| Evidence class | Current state |
|---|---|
| Latest analytical repository evidence baseline | `fffd3dda123d7c43fe678dca9adfd8feb73de158` via merged PR #322 |
| Objective baseline tag | `v0.0.8-execution-goal-baseline`, verified to resolve to `22a8d88435cb8d5b900a398b7482c3b7277d2ee6` |
| Source-metadata baseline | `v0.1.0-source-metadata-baseline`, verified to resolve to `6abe87bba486e3fe49b6c06178b454335663cb73` via PR #310 |
| Asset-readiness baseline | `v0.1.1-asset-readiness-baseline`, verified annotated tag resolving to `cf4aba2f40aa426f28f09b1b1b1bad895394198b` via PR #314 |
| Access-integrity baseline | `v0.1.2-access-integrity-baseline`, verified annotated tag resolving to `d4ce26c87341e4d3798a0d84e257a964ebd2cde0` via PR #318 |
| AOI baseline | `v0.2.0-aoi-baseline`, verified annotated tag resolving to `fffd3dda123d7c43fe678dca9adfd8feb73de158` via PR #322 |
| Intake transaction candidate | BurnLens `0.3.0`; issue #325; `paired-intake-contract-v0.1.0`; proposed `v0.3.0-intake-transaction-baseline`; provider assets/bytes and retained synthetic fixture bytes all zero |
| Application version | Not created |
| AOI version | `aoi-darlene3-model-v0.2.0`, accepted and shipped final modeling AOI; 12 km by 9 km / 108 km2 in EPSG:32610; lower priority than official sources |
| Source records | `SOURCE-2026-001` through `SOURCE-2026-007`; the newest record is one immutable public NIFC reference vector, not a label or detection |
| Metadata fixture | `METADATA-2026-001`, five Sentinel items and 124 NASA VIIRS granule records; no asset hrefs or source bytes |
| Asset-readiness fixture | `ASSET-READINESS-2026-001`, SHA-256 `c5bcfbf57cf23a7bf3ed9bd1302461b2ba1ee101ab05b7d935419223763e5ce7`; metadata only, zero provider bytes |
| Evidence tooling | BurnLens package `0.3.0` candidate; access-integrity validation, checksum-gated AOI derivation, exact-pair transaction validation, atomic promotion, normalized JSON, semantic HTML, and PNG rendering |
| Access-precheck report | `VIIRS-ACCESS-PRECHECK-2026-001`; JSON SHA-256 `107c08e00539257d7b86265d316060f35c019c821acc59f89dfc4b8875205f7f`; decision `BLOCKED_OWNER_CREDENTIAL` |
| AOI evidence report | `AOI-FINAL-2026-001`; JSON SHA-256 `305ddda2eda96fa31e8fb410891d3dc9c0f2b4930af5fc8ee6d2df9bae0b856c`; decision `ACCEPT_FINAL_MODELING_AOI` |
| Paired-intake rehearsal | `PAIR-INTAKE-REHEARSAL-2026-001`; run `BL-2026-07-14-paired-intake-rehearsal-r001`; JSON SHA-256 `1eae030c41174fa2806f218bc28db143e83ca08b1eb69230385691e29a6bddbc`; real decision `BLOCKED_OWNER_CREDENTIAL`; synthetic transaction checks pass |
| Dataset version | Not created |
| Label-schema implementation | Not created |
| Baseline-method version | Not created |
| Model version | Not created |
| Run IDs | `BL-2026-07-14-aoi-final-r001` (geometry-only) and `BL-2026-07-14-paired-intake-rehearsal-r001` (real blocked state plus temporary synthetic transaction); no imagery/provider pixels or model output |
| Raster/vector/map output | One official reference vector, one derived AOI vector, and one static evidence map; no imagery-derived or analytical output |
| Repository-owned public application | Not created |
| Public performance claim | None authorized or supported |

## Latest shipped checkpoint

P2O2-T01 / issue #321 accepts the final modeling AOI and adds `AOI-FINAL-2026-001`. PR #322 merged at `fffd3dda123d7c43fe678dca9adfd8feb73de158`; the annotated `v0.2.0-aoi-baseline` tag resolves to that exact commit. Sixteen post-merge tests, a byte-identical pipeline rebuild, the public rendered PR/README/case study/source record/PNG, issue closure, and tag identity passed verification.

## Current checkpoint

P2O2-T02 / issue #325 / PR #326 is the active bounded candidate. It proves that the exact Sentinel plus VIIRS fire/geolocation package must validate and register as one atomic unit, using temporary synthetic fixtures while the real provider state remains visibly blocked. The source implementation is commit `2491766022b549402b64e3136a79fd9c046beff5`; merge and tag identities are pending. Provider imagery count and bytes remain zero.

## Selected next checkpoint

After this transaction candidate ships and the owner explicitly approves adding or using both a CDSE credential and an Earthdata Login credential, open one issue-backed checkpoint to acquire into quarantine, validate, checksum, inspect, and render the exact paired Sentinel/VIIRS source package. Until then, take no provider source-asset action. Transaction success, login resolution, and granule intersection are integrity/access/coverage evidence, never a fire detection.

## Boundaries carried forward

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

All BurnLens work and future public surfaces must originate from `drwbkr1/burnlens-deschutes`; the separate site repository is out of scope.

No application or deployed public companion site exists in this repository yet. The repository README, living case study, and static semantic/visual AOI and intake evidence are updated presentation surfaces for this checkpoint.
