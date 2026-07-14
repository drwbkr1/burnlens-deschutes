# BurnLens Phase Status

## Status as of 2026-07-13

| Phase | Proof outcome | Status | Evidence and next gate |
|---|---|---|---|
| 1 — Scope and controls | Coherent promise, task, source posture, repository controls, traceability, and acceptance evidence | **Accepted and versioned for Phase Two planning; no analytical release** | P1O7-T08 / PR #294 records the decision. #290 / PR #291 and `v0.0.8-execution-goal-baseline` establish the current control baseline. |
| 2 — Data foundation | Legally usable, versioned, leakage-resistant data/label/baseline package with model-readiness decision | **Active; fail-closed delivery check added; provider asset intake blocked** | Issue #317 verifies that both exact LP DAAC routes return login HTML without Earthdata authentication. CDSE and Earthdata credentials remain owner-gated; provider asset count is zero. |
| 3 — Model evidence | One bounded model adds reproducible value beyond the strongest baseline or is rejected honestly | **Blocked** | Requires an accepted Phase Two package and target decision. |
| 4 — CV-to-GEOINT product | Accepted model/baseline becomes a valid georeferenced run and repository-owned evidence interface | **Blocked** | Requires an accepted Phase Three model or Phase Two baseline-only route. |
| 5 — Reliability | Integrated system is reproducible, accessible, secure, failure-visible, performant, and reversible | **Blocked** | Requires an accepted Phase Four run package and interface. |
| 6 — Publication | One coherent, licensed, citable, traceable portfolio release and closeout | **Blocked** | Requires an accepted Phase Five candidate, resolved licensing, verified claims, and a repository-owned production surface. |

## Verified capability inventory

| Evidence class | Current state |
|---|---|
| Latest repository evidence baseline | `cf4aba2f40aa426f28f09b1b1b1bad895394198b` via merged PR #314 |
| Objective baseline tag | `v0.0.8-execution-goal-baseline`, verified to resolve to `22a8d88435cb8d5b900a398b7482c3b7277d2ee6` |
| Source-metadata baseline | `v0.1.0-source-metadata-baseline`, verified to resolve to `6abe87bba486e3fe49b6c06178b454335663cb73` via PR #310 |
| Asset-readiness baseline | `v0.1.1-asset-readiness-baseline`, verified annotated tag resolving to `cf4aba2f40aa426f28f09b1b1b1bad895394198b` via PR #314 |
| Application version | Not created |
| AOI version | `aoi-darlene3-discovery-v0.1.0`, accepted for metadata discovery only; not a fire perimeter or final modeling AOI |
| Source records | `SOURCE-2026-001` through `SOURCE-2026-006`, reviewed for discovery and exact-route roles |
| Metadata fixture | `METADATA-2026-001`, five Sentinel items and 124 NASA VIIRS granule records; no asset hrefs or source bytes |
| Asset-readiness fixture | `ASSET-READINESS-2026-001`, SHA-256 `c5bcfbf57cf23a7bf3ed9bd1302461b2ba1ee101ab05b7d935419223763e5ce7`; metadata only, zero provider bytes |
| Access-integrity tool | BurnLens package `0.1.2`; HDF5/NetCDF4 signature, minimum-size, HTML/login, checksum, normalized JSON, semantic HTML, and PNG rendering paths |
| Access-precheck report | `VIIRS-ACCESS-PRECHECK-2026-001`; JSON SHA-256 `107c08e00539257d7b86265d316060f35c019c821acc59f89dfc4b8875205f7f`; decision `BLOCKED_OWNER_CREDENTIAL` |
| Dataset version | Not created |
| Label-schema implementation | Not created |
| Baseline-method version | Not created |
| Model version | Not created |
| Run ID | `BL-2026-07-14-access-precheck-r001`; access-only, zero accepted provider assets; not an analytical/model run |
| Raster/vector/map output | Not created |
| Repository-owned public application | Not created |
| Public performance claim | None authorized or supported |

## Latest shipped checkpoint

P2O1-T02 / issue #312 pins one exact Sentinel-2 L2A product plus the closest same-day NOAA-21 VIIRS active-fire/geolocation pair and retains `ASSET-READINESS-2026-001` as metadata only. PR #314 merged at `cf4aba2f40aa426f28f09b1b1b1bad895394198b`; the annotated `v0.1.1-asset-readiness-baseline` tag resolves to that commit. The rendered PR, merged F04-A, normalized fixture, and closed issue passed post-merge verification.

## Current checkpoint

P2O1-T03 / issue #317 is active on `codex/p2o1-t03-viirs-inspection`. The exact NASA routes were exercised without credentials. A default GET ended at `401`; browser-style GETs ended at `200` Earthdata Login HTML. The new validator rejected both bodies, generated a normalized and rendered blocked report, and deleted the rejected responses. Provider asset count and retained provider bytes remain zero.

## Selected next checkpoint

After P2O1-T03 ships and the owner explicitly approves adding or using both a CDSE credential and an Earthdata Login credential, open one issue-backed checkpoint to acquire, checksum, inspect, and render the exact paired Sentinel/VIIRS source package. Until then, take no provider source-asset action. Login redirects, route resolution, and granule intersection are access/coverage evidence, never a fire detection.

## Boundaries carried forward

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

All BurnLens work and future public surfaces must originate from `drwbkr1/burnlens-deschutes`; the separate site repository is out of scope.

No application or public companion site exists in this repository yet; public-surface updates therefore remain not applicable at this checkpoint.
