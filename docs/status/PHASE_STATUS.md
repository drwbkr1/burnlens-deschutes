# BurnLens Phase Status

## Status as of 2026-07-14

| Phase | Proof outcome | Status | Evidence and next gate |
|---|---|---|---|
| 1 — Scope and controls | Coherent promise, task, source posture, repository controls, traceability, and acceptance evidence | **Accepted and versioned for Phase Two planning; no analytical release** | P1O7-T08 / PR #294 records the decision. #290 / PR #291 and `v0.0.8-execution-goal-baseline` establish the current control baseline. |
| 2 — Data foundation | Legally usable, versioned, leakage-resistant data/label/baseline package with model-readiness decision | **Active; final AOI and atomic intake shipped; provider intake authorized but not executed** | Issue #321 / PR #322 ships the final modeling AOI. Issue #325 / PR #326 ships the exact-pair transaction without using provider bytes. `ACCESS-2026-006` records owner authorization for CDSE and Earthdata; authentication and delivery remain unverified, and provider imagery asset count is zero. |
| 3 — Model evidence | One bounded model adds reproducible value beyond the strongest baseline or is rejected honestly | **Blocked** | Requires an accepted Phase Two package and target decision. |
| 4 — CV-to-GEOINT product | Accepted model/baseline becomes a valid georeferenced run and repository-owned evidence interface | **Blocked** | Requires an accepted Phase Three model or Phase Two baseline-only route. |
| 5 — Reliability | Integrated system is reproducible, accessible, secure, failure-visible, performant, and reversible | **Blocked** | Requires an accepted Phase Four run package and interface. |
| 6 — Publication | One coherent, licensed, citable, traceable portfolio release and closeout | **Blocked** | Requires an accepted Phase Five candidate, resolved licensing, verified claims, and a repository-owned production surface. |

## Verified capability inventory

| Evidence class | Current state |
|---|---|
| Latest repository evidence baseline | `ee1a1d678ad888b595dc3c7b215f787ea5156582` via merged PR #326 and annotated `v0.3.0-intake-transaction-baseline` |
| Objective baseline tag | `v0.0.8-execution-goal-baseline`, verified to resolve to `22a8d88435cb8d5b900a398b7482c3b7277d2ee6` |
| Source-metadata baseline | `v0.1.0-source-metadata-baseline`, verified to resolve to `6abe87bba486e3fe49b6c06178b454335663cb73` via PR #310 |
| Asset-readiness baseline | `v0.1.1-asset-readiness-baseline`, verified annotated tag resolving to `cf4aba2f40aa426f28f09b1b1b1bad895394198b` via PR #314 |
| Access-integrity baseline | `v0.1.2-access-integrity-baseline`, verified annotated tag resolving to `d4ce26c87341e4d3798a0d84e257a964ebd2cde0` via PR #318 |
| AOI baseline | `v0.2.0-aoi-baseline`, verified annotated tag resolving to `fffd3dda123d7c43fe678dca9adfd8feb73de158` via PR #322 |
| Intake transaction baseline | BurnLens `0.3.0`; issue #325 / PR #326; merge `ee1a1d678ad888b595dc3c7b215f787ea5156582`; annotated `v0.3.0-intake-transaction-baseline`; `paired-intake-contract-v0.4.0`; full contract SHA-256 `5135b6b0b554e533df98ede568b1eafbd45c692b73a1e1abd3e50ba098f0958d`; provider assets/bytes and retained synthetic fixture bytes all zero |
| Credential authorization | `ACCESS-2026-006`; both provider boundaries owner-authorized on 2026-07-14; owner reports authentication setup `PASS`; BurnLens has not accessed or independently exercised either credential |
| Application version | Not created |
| AOI version | `aoi-darlene3-model-v0.2.0`, accepted and shipped final modeling AOI; 12 km by 9 km / 108 km2 in EPSG:32610; lower priority than official sources |
| Source records | `SOURCE-2026-001` through `SOURCE-2026-007`; the newest record is one immutable public NIFC reference vector, not a label or detection |
| Metadata fixture | `METADATA-2026-001`, five Sentinel items and 124 NASA VIIRS granule records; no asset hrefs or source bytes |
| Asset-readiness fixture | `ASSET-READINESS-2026-001`, SHA-256 `c5bcfbf57cf23a7bf3ed9bd1302461b2ba1ee101ab05b7d935419223763e5ce7`; metadata only, zero provider bytes |
| Evidence tooling | BurnLens package `0.3.0`, shipped at `v0.3.0-intake-transaction-baseline`; access-integrity validation, checksum-gated AOI derivation, exact-pair transaction validation, atomic promotion, normalized JSON, semantic HTML, and PNG rendering |
| Access-precheck report | `VIIRS-ACCESS-PRECHECK-2026-001`; JSON SHA-256 `107c08e00539257d7b86265d316060f35c019c821acc59f89dfc4b8875205f7f`; decision `BLOCKED_OWNER_CREDENTIAL` |
| AOI evidence report | `AOI-FINAL-2026-001`; JSON SHA-256 `305ddda2eda96fa31e8fb410891d3dc9c0f2b4930af5fc8ee6d2df9bae0b856c`; decision `ACCEPT_FINAL_MODELING_AOI` |
| Paired-intake rehearsal | `PAIR-INTAKE-REHEARSAL-2026-001`; run `BL-2026-07-14-paired-intake-rehearsal-r001`; JSON SHA-256 `94e311fd608f9c10e024138d9eff6abf0f70187a69c031264e91cb8d9d1af234`; historical pre-authorization decision `BLOCKED_OWNER_CREDENTIAL`; metadata observed 2026-07-14 with no live request; four synthetic transaction/integrity checks pass |
| Dataset version | Not created |
| Label-schema implementation | Not created |
| Baseline-method version | Not created |
| Model version | Not created |
| Run IDs | `BL-2026-07-14-aoi-final-r001` (geometry-only) and `BL-2026-07-14-paired-intake-rehearsal-r001` (real blocked state plus temporary synthetic transaction); no imagery/provider pixels or model output |
| Raster/vector/map output | One official reference vector, one derived AOI vector, and one static evidence map; no imagery-derived or analytical output |
| Repository-owned public application | Not created |
| Public performance claim | None authorized or supported |

## Latest shipped checkpoint

P2O2-T02 / issue #325 accepts the exact-pair transaction and adds `PAIR-INTAKE-REHEARSAL-2026-001`. PR #326 merged at `ee1a1d678ad888b595dc3c7b215f787ea5156582`; the annotated `v0.3.0-intake-transaction-baseline` tag resolves to that exact commit. Thirty-seven post-merge tests, dependency health, byte-identical report reconstruction, original-resolution rendered review, issue closure, and remote tag identity passed verification. No credential or provider byte was exercised.

## Current checkpoint

P2O2-T02-SYNC / issue #327 / PR #328 is the active provenance-only checkpoint. It records PR #326, merge `ee1a1d678ad888b595dc3c7b215f787ea5156582`, the verified annotated tag, post-merge checks, and the fact that `ACCESS-2026-006` arrived after the historical rehearsal. It changes no output bytes and exercises no credential.

## Selected next checkpoint

After issue #327 ships, open one issue-backed checkpoint to exercise the now-authorized CDSE and Earthdata credentials, acquire into excluded quarantine, validate, checksum, inspect, and render the exact paired Sentinel/VIIRS source package. Until that branch exists, take no provider source-asset action. Transaction success, login resolution, and granule intersection are integrity/access/coverage evidence, never a fire detection.

## Boundaries carried forward

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

All BurnLens work and future public surfaces must originate from `drwbkr1/burnlens-deschutes`; the separate site repository is out of scope.

No application or deployed public companion site exists in this repository yet. The repository README, living case study, and static semantic/visual AOI and intake evidence are updated presentation surfaces for this checkpoint.
