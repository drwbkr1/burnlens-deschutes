# Phase 1 / Objective Three — Handoff

## Status

Objective Three is complete and remediation-expanded. It is ready to hand off to the next Phase One objective.

## What this objective established

- Candidate source categories are identified.
- Feasibility criteria now include scoring and pass/fail rules.
- Imagery access planning now includes Sentinel-2, Landsat, HLS, and STAC details.
- Active-fire reference planning now includes FIRMS roles, confidence policy, caveats, and weak-label rules.
- Local overlay planning now includes Deschutes County layer groups, CRS handling, allowed uses, forbidden uses, and a priority layer shortlist.
- AOI planning now includes acceptance gates, tile-selection fields, defer triggers, reject triggers, and versioning conventions.
- Format and CRS planning now includes raster, vector, FIRMS, local overlay, and STAC handling rules.
- Provenance planning now includes source, AOI, run, and public-artifact schemas.
- The data-stack matrix now compares candidate sources by role, access path, scale, timing, quality fields, CRS concerns, risks, and decision.
- Research validation and claims register records now exist.
- The work remains documentation-only.

## Accepted candidate roles

| Role | Candidate source family | Status |
|---|---|---|
| Primary imagery | Sentinel-2 Level-2A | Feasible candidate. |
| Secondary imagery | Landsat Collection 2 Level-2 | Feasible candidate. |
| Harmonized imagery | NASA HLS | Optional candidate. |
| Reference source | NASA FIRMS products | Feasible with caveats. |
| Local context | Deschutes County GIS | Feasible context source only. |
| Provenance pattern | STAC fields plus BurnLens versioning | Feasible pattern. |

## Not completed here

No final AOI, scenes, dates, labels, masks, model inputs, baselines, metrics, or public outputs were created.

## Handoff decision

Proceed to the next Phase One objective. Future work should use this source stack as a planning scaffold, not as a completed dataset. Before any data is processed, future work must instantiate AOI, source, format/CRS, provenance, and claim records.
