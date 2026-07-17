# P2O4-T13 Official Source Scout Decision

**Issue / branch / parent:** #425 / `codex/p2o4-t13-official-source-scout` / #416

**Run:** `BL-2026-07-17-official-source-scout-r004`

## Decision

`PRIORITIZE_LANDSAT_BURNED_AREA_AND_CROSS_PROGRAM_FIRE_SCOUTS_DEFER_ACQUISITION_LABELS_DATASET_MODEL`.

While the accepted seven-product Burn Severity Portal request remains pending, BurnLens now has a reproducible, live official-source map for useful work that does not duplicate or substitute that request. The scout records seven source classes, 23 current Deschutes MTBS fires, 37 cross-program products, and 21 candidate fires outside the pending McKay/Tepee request set.

GW Fire is the highest-value first acquisition candidate because it combines 2007 event/time diversity, roughly 71.7 km separation from the current events, BAER/MTBS/RAVG coverage, and 64 current Landsat burned-area metadata matches. The rank is reconnaissance, not fitness or truth.

## Access result

The public Landsat STAC catalog is live. The advertised asset route tested for the top candidate redirects to EROS authentication. No credentials were sent and no asset bytes were retained. A later bounded issue may test a small metadata/COG window only after authorized EROS access is resolved and exact terms, coverage, QA, grid, and time relation pass.

## Owner-confirmed route

The owner-confirmed prototype workflow is now the prospective label route: Codex proposes disclosed burned/background candidates; the owner answers yes/no/uncertain. A yes can advance only after reproducibility, source, quality, and event-level leakage gates. No and uncertain remain excluded. The original 56 units will be reopened in a separate review-surface checkpoint; the historical 6/0/50 reconciliation remains immutable evidence but is not a final exclusion decision under this route.

This workflow does not support claims of independent ground truth, inter-rater agreement, field validation, official status, endorsement, or operational/enterprise readiness.

## State

- New large acquisitions: 0
- Original units changed: 0
- Owner responses collected: 0
- Labels promoted: 0
- Dataset/split/baseline/model: absent
- Pending seven-bundle request: unchanged under #416

The next evidence move is not a broad download. It is one exact small Landsat burned-area access/fitness proof or, if that access remains unavailable, the separate owner-review-surface checkpoint using already verified evidence.
