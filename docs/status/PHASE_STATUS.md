# BurnLens Phase Status

## Status as of 2026-07-13

| Phase | Proof outcome | Status | Evidence and next gate |
|---|---|---|---|
| 1 — Scope and controls | Coherent promise, task, source posture, repository controls, traceability, and acceptance evidence | **Accepted and versioned for Phase Two planning; no analytical release** | P1O7-T08 / PR #294 records the decision. #290 / PR #291 and `v0.0.8-execution-goal-baseline` establish the current control baseline. |
| 2 — Data foundation | Legally usable, versioned, leakage-resistant data/label/baseline package with model-readiness decision | **Active; final AOI candidate accepted; provider imagery intake blocked** | Issue #321 accepts a deterministic Deschutes County modeling AOI from one public NIFC reference. CDSE and Earthdata credentials remain owner-gated; provider imagery asset count is zero. |
| 3 — Model evidence | One bounded model adds reproducible value beyond the strongest baseline or is rejected honestly | **Blocked** | Requires an accepted Phase Two package and target decision. |
| 4 — CV-to-GEOINT product | Accepted model/baseline becomes a valid georeferenced run and repository-owned evidence interface | **Blocked** | Requires an accepted Phase Three model or Phase Two baseline-only route. |
| 5 — Reliability | Integrated system is reproducible, accessible, secure, failure-visible, performant, and reversible | **Blocked** | Requires an accepted Phase Four run package and interface. |
| 6 — Publication | One coherent, licensed, citable, traceable portfolio release and closeout | **Blocked** | Requires an accepted Phase Five candidate, resolved licensing, verified claims, and a repository-owned production surface. |

## Verified capability inventory

| Evidence class | Current state |
|---|---|
| Latest repository evidence baseline | `d4ce26c87341e4d3798a0d84e257a964ebd2cde0` via merged PR #318 |
| Objective baseline tag | `v0.0.8-execution-goal-baseline`, verified to resolve to `22a8d88435cb8d5b900a398b7482c3b7277d2ee6` |
| Source-metadata baseline | `v0.1.0-source-metadata-baseline`, verified to resolve to `6abe87bba486e3fe49b6c06178b454335663cb73` via PR #310 |
| Asset-readiness baseline | `v0.1.1-asset-readiness-baseline`, verified annotated tag resolving to `cf4aba2f40aa426f28f09b1b1b1bad895394198b` via PR #314 |
| Access-integrity baseline | `v0.1.2-access-integrity-baseline`, verified annotated tag resolving to `d4ce26c87341e4d3798a0d84e257a964ebd2cde0` via PR #318 |
| AOI baseline candidate | `v0.2.0-aoi-baseline`, proposed on issue #321 branch; not yet a tag or shipped baseline |
| Application version | Not created |
| AOI version | `aoi-darlene3-model-v0.2.0`, accepted final modeling AOI candidate; 12 km by 9 km / 108 km2 in EPSG:32610; lower priority than official sources |
| Source records | `SOURCE-2026-001` through `SOURCE-2026-007`; the newest record is one immutable public NIFC reference vector, not a label or detection |
| Metadata fixture | `METADATA-2026-001`, five Sentinel items and 124 NASA VIIRS granule records; no asset hrefs or source bytes |
| Asset-readiness fixture | `ASSET-READINESS-2026-001`, SHA-256 `c5bcfbf57cf23a7bf3ed9bd1302461b2ba1ee101ab05b7d935419223763e5ce7`; metadata only, zero provider bytes |
| Evidence tooling | BurnLens package `0.2.0`; access-integrity validation plus checksum-gated AOI projection, derivation, normalized JSON, semantic HTML, and PNG rendering |
| Access-precheck report | `VIIRS-ACCESS-PRECHECK-2026-001`; JSON SHA-256 `107c08e00539257d7b86265d316060f35c019c821acc59f89dfc4b8875205f7f`; decision `BLOCKED_OWNER_CREDENTIAL` |
| AOI evidence report | `AOI-FINAL-2026-001`; JSON SHA-256 `305ddda2eda96fa31e8fb410891d3dc9c0f2b4930af5fc8ee6d2df9bae0b856c`; decision `ACCEPT_FINAL_MODELING_AOI` |
| Dataset version | Not created |
| Label-schema implementation | Not created |
| Baseline-method version | Not created |
| Model version | Not created |
| Run ID | `BL-2026-07-14-aoi-final-r001`; geometry-only evidence run; no imagery/provider pixels or model output |
| Raster/vector/map output | One official reference vector, one derived AOI vector, and one static evidence map; no imagery-derived or analytical output |
| Repository-owned public application | Not created |
| Public performance claim | None authorized or supported |

## Latest shipped checkpoint

P2O1-T03 / issue #317 adds the fail-closed delivery validator and `VIIRS-ACCESS-PRECHECK-2026-001`. PR #318 merged at `d4ce26c87341e4d3798a0d84e257a964ebd2cde0`; the annotated `v0.1.2-access-integrity-baseline` tag resolves to that exact commit. The rendered PR, branch README, normalized and visual evidence, closed issue, eight tests, and deterministic report rebuild passed post-merge verification.

## Current checkpoint

P2O2-T01 / issue #321 is active on `codex/p2o2-t01-final-aoi`. It accepts the AOI portion of Phase Two Objective Two while keeping the full source-stack objective incomplete. PR, merge, tag, issue closure, and post-merge verification remain pending. Provider imagery count and bytes remain zero.

## Selected next checkpoint

After the owner explicitly approves adding or using both a CDSE credential and an Earthdata Login credential, open one issue-backed checkpoint to acquire, checksum, inspect, and render the exact paired Sentinel/VIIRS source package. Until then, take no provider source-asset action. Login redirects, route resolution, and granule intersection are access/coverage evidence, never a fire detection.

## Boundaries carried forward

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

All BurnLens work and future public surfaces must originate from `drwbkr1/burnlens-deschutes`; the separate site repository is out of scope.

No application or deployed public companion site exists in this repository yet. The repository README, living case study, and static semantic/visual AOI evidence are updated presentation surfaces for this checkpoint.
