# BurnLens Phase Status

## Status as of 2026-07-13

| Phase | Proof outcome | Status | Evidence and next gate |
|---|---|---|---|
| 1 — Scope and controls | Coherent promise, task, source posture, repository controls, traceability, and acceptance evidence | **Accepted and versioned for Phase Two planning; no analytical release** | P1O7-T08 / PR #294 records the decision. #290 / PR #291 and `v0.0.8-execution-goal-baseline` establish the current control baseline. |
| 2 — Data foundation | Legally usable, versioned, leakage-resistant data/label/baseline package with model-readiness decision | **Active; metadata verified; asset intake blocked** | Issue #293 verifies a no-secret public metadata path for Sentinel-2 L2A and NASA VIIRS, plus a versioned discovery envelope. Re-open F04-A for one exact asset-readiness action before any source asset access. |
| 3 — Model evidence | One bounded model adds reproducible value beyond the strongest baseline or is rejected honestly | **Blocked** | Requires an accepted Phase Two package and target decision. |
| 4 — CV-to-GEOINT product | Accepted model/baseline becomes a valid georeferenced run and repository-owned evidence interface | **Blocked** | Requires an accepted Phase Three model or Phase Two baseline-only route. |
| 5 — Reliability | Integrated system is reproducible, accessible, secure, failure-visible, performant, and reversible | **Blocked** | Requires an accepted Phase Four run package and interface. |
| 6 — Publication | One coherent, licensed, citable, traceable portfolio release and closeout | **Blocked** | Requires an accepted Phase Five candidate, resolved licensing, verified claims, and a repository-owned production surface. |

## Verified capability inventory

| Evidence class | Current state |
|---|---|
| Git baseline | `22a8d88435cb8d5b900a398b7482c3b7277d2ee6` via merged PR #291 |
| Objective baseline tag | `v0.0.8-execution-goal-baseline`, verified to resolve to the Git baseline |
| Application version | Not created |
| AOI version | `aoi-darlene3-discovery-v0.1.0`, accepted for metadata discovery only; not a fire perimeter or final modeling AOI |
| Source records | `SOURCE-2026-001` through `SOURCE-2026-003`, reviewed for metadata roles |
| Metadata fixture | `METADATA-2026-001`, five Sentinel items and 124 NASA VIIRS granule records; no asset hrefs or source bytes |
| Dataset version | Not created |
| Label-schema implementation | Not created |
| Baseline-method version | Not created |
| Model version | Not created |
| Run ID | Not created |
| Raster/vector/map output | Not created |
| Repository-owned public application | Not created |
| Public performance claim | None authorized or supported |

## Latest shipped checkpoint

Issue #290 / PR #291 adopted the controlling execution goal, reconciled active repository instructions, and established the six-phase roadmap and required status/version/log records. The checkpoint is merged, tagged, rendered, and verified.

## Current checkpoint

P2O1-T01 / issue #293 is the active checkpoint. It selects Copernicus Sentinel-2 L2A as the primary optical candidate, NASA VIIRS Collection 2 active-fire products as coarse reference candidates, and official Oregon incident context for the historical Darlene 3 feasibility slice. Its candidate version is `v0.1.0-source-metadata-baseline`. Merge, tag, and rendered-repository verification remain pending.

## Selected next checkpoint

After P2O1-T01 ships, verify one exact Sentinel scene and temporally relevant VIIRS reference path at the asset-access boundary. That issue must resolve access, format, CRS, companion geolocation, quality fields, immutable retention, checksums, and terms before any asset is downloaded. It must not add a secret or treat granule intersection as a fire detection without owner approval and direct evidence.

## Boundaries carried forward

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

All BurnLens work and future public surfaces must originate from `drwbkr1/burnlens-deschutes`; the separate site repository is out of scope.
