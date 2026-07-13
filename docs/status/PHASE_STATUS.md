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
| Source-metadata baseline | `v0.1.0-source-metadata-baseline`, verified to resolve to `6abe87bba486e3fe49b6c06178b454335663cb73` via PR #310 |
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

P2O1-T01 / issue #293 selected the first source roles, verified no-secret public metadata discovery for the Darlene 3 feasibility slice, and retained `METADATA-2026-001`. PR #310 merged at `6abe87bba486e3fe49b6c06178b454335663cb73`; the annotated `v0.1.0-source-metadata-baseline` tag resolves to that commit, and the rendered status, F04-A, and fixture views passed post-merge verification.

## Current checkpoint

P2O1-T02 / issue #312 is active. It will verify one exact Sentinel-2 scene and temporally relevant NASA VIIRS product route at the asset-access boundary, including access, format, CRS, geolocation, quality, checksum, retention, terms, and defensible reference role. It is a readiness checkpoint only.

## Selected next checkpoint

Complete P2O1-T02's fresh primary-source review and re-open F04-A for one precisely described future action. Stop before credentials or provider-asset download if access, terms, retention, or label fitness cannot be verified. Granule intersection remains coverage evidence, never a fire detection.

## Boundaries carried forward

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

All BurnLens work and future public surfaces must originate from `drwbkr1/burnlens-deschutes`; the separate site repository is out of scope.
