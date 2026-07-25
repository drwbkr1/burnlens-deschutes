# REGISTRY-2026-072 — Ward Creek native source-fitness candidate

**Recorded:** 2026-07-24
**Issue:** #554
**Branch:** `codex/p2o4-t39-replacement-event`
**Source commit:** `b5272bc28275b100fa142fee46fec5a2c97576f9`

| Unit | Run | State | Immutable output | Next dependency |
|---|---|---|---|---|
| `P2O4-T39-U03-FITNESS-R001` | `BL-2026-07-24-ward-creek-reference-fitness-r001` | `failed-retained` | ignored non-HEAD-trace outputs | r002 |
| `P2O4-T39-U03-FITNESS-R002` | `BL-2026-07-24-ward-creek-reference-fitness-r002` | `machine-pass-render-pending` | exact JSON/PNG/HTML source-fitness surface | exact HTML desktop/narrow render |
| `P2O4-T39-U04` | not started | `blocked-by-dependency` | none | U03 render pass |

## Candidate evidence

The r002 report passes exact archive, embedded terms, boundary identity,
analyst-threshold, five-raster, CRS/grid/nodata, class-domain, optical custody,
pair-quality, registration, and nearest-neighbor comparison gates.

Its decision is:

`ACCEPT_REFERENCE_FITNESS_DEFER_CANDIDATES_OWNER_DECISIONS_LABELS_DATASET_SPLIT_BASELINE_MODEL`

The PNG is visually inspected. The browser refuses automated local-file
navigation. BurnLens retains that limitation and waits for exact user-render
confirmation instead of bypassing the browser policy.

## Subsequent replay result

REGISTRY-2026-073 supersedes the r002 state. Exact detached replay reproduces
HTML and PNG but not JSON because four public fields contain ambient extracted
paths. R002 is retained as `failed-reproducibility-retained`. U04 remains
closed.
