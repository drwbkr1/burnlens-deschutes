# Cross-Event Feasibility and Leakage-Group Decision

## Checkpoint scope

Issue #357 starts from the verified one-event proposal and asks one bounded question: do current official metadata and resolved source terms support at least two additional whole-event acquisition candidates before BurnLens creates a dataset or split?

It does not download imagery, create cross-event labels, assign train/validation/test roles, or authorize model work.

## Current source screen

BurnLens captured current MTBS all-years occurrences and burned-area boundaries, the official Census Deschutes County polygon, and CDSE Sentinel-2 L2A STAC metadata. The normalized source snapshot records service versions, exact queries, geometries, source roles, collection/license identity, item routes, sizes, checksums, platforms, tiles, orbits, processing baselines, cloud metadata, and a zero-data-touch boundary.

Of 84 MTBS records in the discovery envelope, 23 have representative points inside Census GEOID `41017`. Three 2017-or-later wildfire records pass the bounded date/type/size filter.

## Result

- Tepee 1144 NE / 2018 is selected with one exact Sentinel-2B pre/post pair. It is 34.926 km from the Darlene AOI center.
- McKay 1035 NE / 2017 is selected with one exact Sentinel-2A pre/post pair. It is 10.925 km from Darlene.
- Milli 0843 CS / 2017 is excluded because no one current Sentinel item contains its complete MTBS boundary; BurnLens does not splice tiles or shrink the boundary silently.

The two selected MTBS boundaries do not overlap Darlene or each other. Their representative points are 27.258 km apart. These distances are diagnostics, not proof of ecological independence.

![BurnLens cross-event feasibility evidence](../../../samples/cross-event/phase-two/CROSS-EVENT-FITNESS-2026-001.png)

## Leakage-control contract

The exact event, scene, geography, and time group IDs are frozen now, before any acquisition or tiling. All future derivatives from one event and either scene in its pair must remain indivisible in any later evaluation role. Overlapping geographies and same-event time windows may not cross roles.

No train, validation, or test partition exists. A later checkpoint must assign whole groups, prove zero cross-role group overlap, preserve unknown/excluded evidence, and keep the test group untouched by method selection.

## Decision

Decision code: `SELECT_CROSS_EVENT_ACQUISITION_CANDIDATES`.

Proceed next with exact authenticated acquisition, integrity validation, native-pixel inspection, local quality evidence, and pair registration for the frozen Tepee and McKay products. Treat MTBS as analyst-interpreted reference and STAC cloud cover as availability metadata only. Do not call these groups a dataset or split until the exact source pixels and cross-event label/review evidence pass their own gates.

Shipment: issue #357 / PR #358 squash-merged at `5bfa1527410e98d8034b35ad68f6c50d5a1ec628`; verified annotated tag object `dbfda10ca50c39d8e8924096e740e71643e1f133` remotely peels to that merge as `v0.10.0-cross-event-feasibility-baseline`.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
