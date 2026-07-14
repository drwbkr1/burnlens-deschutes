# PRECHECK-2026-007 - Observation Geometry Data-Touch Gate

**Checked:** 2026-07-14 UTC

**Issue:** #333

**Decision:** `PROCEED_BOUNDED_OBSERVATION_SCREEN_ONLY`

## Exact scope

- Official CMR inventory for `VJ214IMG.002` concept `C2831626262-LPCLOUD`
- Frozen AOI bounding box `-121.512668,43.620281,-121.361791,43.703322`
- Window `2024-06-25T00:00:00Z` through `2024-07-01T23:59:59Z`
- All 23 exact inventory granules, plus at most one exact `VJ203MODLL.021` companion after a materially improved candidate is selected
- Internal raw retention only; bounded derived JSON/HTML/PNG evidence may be committed

## Gate evidence

- NASA data-use and exact-product terms remain resolved in `TERMS-2026-002` for internal research acquisition, derived evidence, citation, and acknowledgment.
- The owner explicitly authorized use of the local machine-bound Earthdata account.
- `SOURCE-2026-008` records the live inventory, product roles, selected exact companion, access date, citations, and limitations.
- Raw bytes remain ignored; no redistribution is part of this checkpoint.
- No provider record, point buffer, absence of detection, or later incident perimeter may become segmentation truth.

## No-go conditions

Stop on unresolved terms, credential leakage, non-HTTPS or non-allowlisted delivery, size/container mismatch, inventory drift within the exact run, incomplete package, pair mismatch, unsafe links, failed hashes, or inability to preserve unknown and excluded states.

All gates passed for the bounded screen. This decision does not authorize labels, a dataset, or a target change.

