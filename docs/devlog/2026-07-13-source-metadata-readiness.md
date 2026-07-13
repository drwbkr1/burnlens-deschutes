# Devlog — First Source Stack and Metadata Readiness

**Date:** 2026-07-13

**Issue:** #293

**Branch:** `codex/p2o1-t01-source-readiness`

**Shipment:** PR #310; merge `6abe87bba486e3fe49b6c06178b454335663cb73`; annotated tag `v0.1.0-source-metadata-baseline`

## Weakness selected

At cycle start, BurnLens still could not demonstrate that its preferred sources existed for a concrete historical Deschutes experiment under current access and licensing conditions. The repository had excellent source templates but no instantiated AOI, source record, access result, terms decision, or verified sample metadata.

## Improvement made

The checkpoint chose one Darlene 3 metadata-discovery envelope, resolved the first source roles, executed read-only public catalog queries, and retained a minimal normalized fixture. The source stack is now evidence-backed rather than hypothetical:

- Copernicus Sentinel-2 L2A is the primary optical candidate.
- NASA VIIRS Collection 2 active-fire products are coarse reference candidates, not ground truth.
- Oregon State Fire Marshal information provides historical event context only.
- The U.S. Census La Pine point anchors a BurnLens-created discovery envelope, not a fire perimeter.

## What the queries proved

The official CDSE STAC catalog returned five event-window Sentinel-2 L2A items. NASA CMR returned 124 intersecting VIIRS granule records across S-NPP, NOAA-20, and NOAA-21, including four granules beginning after the incident's approximate reported ignition time.

This proves source metadata availability and coverage candidates. It does not prove that a VIIRS fire pixel exists at Darlene 3 or that any optical scene is label-ready.

The committed result was independently re-queried before review, merged through PR #310, tagged at the exact merge commit, and checked in GitHub's rendered Phase Status, F04-A decision, and metadata-fixture views.

## Reliability decisions

- No secret, account, token, map key, or paid service was added.
- No imagery or active-fire asset was downloaded.
- Provider asset hrefs were excluded from the fixture.
- Failed network and timeout attempts are recorded rather than hidden.
- The fixture has a recorded SHA-256 checksum.
- FIRMS archive/API delivery is deferred because its historical routes require authentication.
- F04-A passes only for metadata discovery and must be re-opened for exact asset access.

## Portfolio meaning

BurnLens now has its first reproducible external evidence artifact. The most important remaining weakness is still visible: the project cannot yet show a real source image, reference fire mask, aligned label, baseline, or end-to-end output. The next checkpoint should test the asset boundary for one scene/reference pair, not broaden the source catalog.

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
