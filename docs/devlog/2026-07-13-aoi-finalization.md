# Devlog - Let the Reference Correct the Box

**Date:** 2026-07-13 local / 2026-07-14 UTC

**Issue:** #321

## Weakness selected

BurnLens had exact source candidates and a robust access failure mode, but its only AOI was a generous metadata-search rectangle. It was deliberately not a fire perimeter or modeling boundary. Proceeding with it would make every future clip, tile, label review, and map depend on a planning convenience rather than evidence.

## What the real source changed

The official NIFC WFIGS record exists and is specific: Darlene 3, unique fire identifier `2024-ORPRD-000289`, a valid non-quarantined mixed-method final perimeter. It also reaches east of the discovery rectangle. The first proposed gate assumed the final AOI would fit inside that rectangle; the real geometry disproved it.

The right response was not to crop the official reference. Issue #321 recorded the correction and made the discovery AOI historical rather than silently rewriting it.

## Improvement made

BurnLens now validates the exact source checksum and identity, projects it to a metric CRS, compares the result with NIFC's own projected response, adds 2 km of context, and snaps outward to a 1 km grid. The resulting 12 km by 9 km AOI is smaller overall, contains the complete reference, sits inside Deschutes County, and is covered by the selected source metadata footprints.

The evidence map intentionally has no basemap. It shows only the source/reference relationship a reviewer needs to understand, with the experimental warning and the fact that no model output exists.

## Portfolio meaning

This is the first accepted geospatial scope rather than another planning document. It demonstrates that BurnLens can let authoritative evidence revise an earlier assumption, keep the provenance trail intact, and produce a reproducible visual artifact without inflating it into an analytical claim.

## Shipment proof

PR #322 merged at `fffd3dda123d7c43fe678dca9adfd8feb73de158`, issue #321 closed, and the annotated `v0.2.0-aoi-baseline` tag resolves to that exact commit. From merged `main`, all 16 tests passed and a fresh AOI pipeline execution reproduced the committed JSON, HTML, and PNG hashes byte for byte. The public rendered PR, README, living case study, source record, and PNG were also inspected. Issue #323 carries the provenance-only lifecycle sync.

## Next boundary

The AOI is no longer the blocker. Actual source pixels are. Exact paired Sentinel/VIIRS intake still requires explicit owner approval for both credentials and must pass the existing fail-closed validator before any label or model decision.

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
