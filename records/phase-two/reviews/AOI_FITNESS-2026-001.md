# AOI_FITNESS-2026-001 - Final Modeling AOI Review

**Issue:** #321

**Decision:** `ACCEPT FINAL MODELING AOI; PHASE TWO OBJECTIVE TWO REMAINS INCOMPLETE`

| Criterion | Evidence | Result |
|---|---|---|
| Bounded Deschutes County geography | Census TIGERweb `GEOID 41017` within count 1 | Pass |
| Relevant historical context | Exact NIFC `2024-ORPRD-000289` final-perimeter reference | Pass with source limitations |
| Reproducible geometry | Checksum-gated source, metric projection, fixed buffer/snap, frozen polygons | Pass |
| Source imagery coverage | Selected Sentinel item bbox contains AOI | Pass for metadata only |
| Reference coverage | Both selected VIIRS CMR polygons contain AOI corners | Pass for metadata only |
| Local/context source | Official NIFC reference plus Census county containment and OSFM incident context | Pass for AOI selection; later overlay package pending |
| Workflow fit | 12 km by 9 km; 108 km2; metric grid; reviewable evidence map | Pass |
| Uncertainty/source roles | Official reference, analysis boundary, and nonexistent model output visually separated | Pass |
| Manual reviewability | 1600x1200 evidence map inspected at original resolution | Pass |
| Operational/no-go boundary | Required warning and prohibited-use copy present | Pass |

## Why this AOI is accepted

The final AOI is the smallest simple grid-aligned rectangle produced by the documented 2 km context and 1 km outward-snap rule. It contains the complete exact reference and remains small enough for later manual review and portfolio-scale tiling. It is narrower than the original discovery envelope while correcting the earlier box's unsupported east edge.

## What remains incomplete

Phase Two Objective Two also requires an access-tested source stack capable of supporting target and uncertainty handling. Metadata coverage and open terms are known, but exact Sentinel and VIIRS provider assets remain unacquired. Actual CRS declarations, transforms, pixel arrays, QA, cloud/smoke state, geolocation, detection presence, and label fitness are therefore unknown.

The AOI is final. The source stack is not yet pixel-inspected, and the credential stop remains in force.
