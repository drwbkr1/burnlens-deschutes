# Phase Two Objective Two - AOI Finalization Decision

**Issue:** #321

**Shipment:** PR #322; merge `fffd3dda123d7c43fe678dca9adfd8feb73de158`; verified annotated tag `v0.2.0-aoi-baseline`

**Decision:** `ACCEPT AOI-2026-002; CONTINUE OBJECTIVE TWO AFTER CREDENTIAL APPROVAL`

## Evidence-driven checkpoint choice

After P2O1-T03 shipped, paired imagery acquisition remained blocked on explicit owner approval for CDSE and Earthdata credentials. The next highest-leverage unblocked weakness was the discovery-only AOI: it could find catalog records but was expressly not suitable as the final modeling scope.

Fresh official NIFC research located the exact public final-perimeter feature for Darlene 3. The real geometry proved that the discovery envelope clipped the source on its east side, so issue #321 revised its initial containment assumption rather than forcing the evidence into the old box.

## Accepted outcome

- Final AOI: `aoi-darlene3-model-v0.2.0`.
- Analysis CRS: EPSG:32610.
- Extent: `[620000, 4831000, 632000, 4840000]`.
- Area: 108.0 km2.
- Reference: NIFC WFIGS `OBJECTID 36462`, `2024-ORPRD-000289`.
- Derivation: reference extent plus 2 km context, snapped outward to a 1 km UTM grid.
- Evidence: normalized JSON, semantic HTML, and reviewed 1600x1200 PNG.

The final AOI contains the complete reference, is within Deschutes County, and remains covered by the selected Sentinel/VIIRS metadata footprints. It supersedes the discovery AOI for modeling while preserving the old record for provenance.

## Objective status

The AOI portion of Phase Two Objective Two passed at this checkpoint. At that time the full objective did not pass because provider assets had not been acquired or inspected. P2O2-T03 / issue #329 later acquired the exact package and added real usable-pixel, quality, geolocation, reference-evidence, and label-fitness findings without changing `AOI-2026-002`.

## Next gate

P2O2-T03 fulfilled the acquisition/validation gate against `AOI-2026-002`; see `AUTHENTICATED_SOURCE_INSPECTION_DECISION.md`. The AOI remains frozen. Do not revise it merely because a scene is inconvenient; any geometry change requires a new AOI version, source/rationale record, and downstream-impact review.
