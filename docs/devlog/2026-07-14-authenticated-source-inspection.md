# Devlog - Real Files, Honest Limits

**Date:** 2026-07-14

**Issue / PR:** #329 / #330

## Weakness selected

BurnLens could prove its intake transaction with synthetic bytes, but it still did not know whether the exact Sentinel and VIIRS products could be delivered, opened, aligned to the AOI, or used responsibly. That was the largest evidence gap in the portfolio: strong controls around data that had never actually arrived.

## Improvement made

The checkpoint adds a runtime-only authenticated acquisition path for the already-pinned CDSE and Earthdata assets. It is deliberately hostile to secret leakage and provider drift: exact auth hosts, HTTPS-only allowlisted redirects, stripped cross-host authorization, sanitized state, bounded response sizes, resumable partials, native signatures, full contract validation, and atomic promotion.

The full 1.17 GB three-file package arrived and independently re-verified. Raw files remain ignored. A second tool then opened the real Sentinel JP2 assets and real VIIRS HDF5/NetCDF-4 arrays, cropped the frozen AOI exactly, decoded the relevant QA flags, compared provider points with the retained incident-reference geometry, and rendered a reviewable report.

## What the real files changed

The source pair is real and relevant, but it is not training truth. The Sentinel crop is readable and the VIIRS file contains eight AOI fire records. Three are residual-bowtie observations. All sit near 69 degrees view zenith at the far edge of the swath. The optical and thermal observations differ by almost 47 minutes, and the 375 m product cannot define 10-20 m segmentation boundaries.

That makes the checkpoint more valuable than a simple success state. BurnLens now demonstrates both reliable data handling and the judgment to stop at reference evidence when the pixels do not support a stronger claim.

## Verification

- Exact three-asset registration and independent registered-package verification pass.
- Sentinel ZIP contains 95 members, one exact SAFE root, `manifest.safe`, and clean CRC results.
- Real AOI crops are `1,200 x 900` RGB at 10 m and `600 x 450` SCL at 20 m on EPSG:32610.
- VIIRS fire-mask, sparse-vector, QA, and geolocation-array invariants pass.
- A second full inspection reproduces all committed JSON/HTML/PNG bytes exactly.
- The rendered semantic page loads without console errors or horizontal overflow; the 1600 x 1100 image, eight-row table, warnings, exclusions, attribution, and traceability are visible.
- All 56 repository tests, compilation, dependency health, offline wheel build, isolated wheel import, secret scan, raw-provider exclusion, and diff checks pass. The local wheel reports package `0.4.0`.

## What remains

No label schema, dataset, split, baseline, model, application, or deployed analytical result exists. The next checkpoint will investigate better observation geometry and a defensible weak/reference-label protocol; it will not force the current package into labels.

## Shipment proof

PR #330 merged at `7678cf41b64e128106c199b913fe74590a52cf80`, closing issue #329. The annotated `v0.4.0-authenticated-source-baseline` tag object `98228058b232bc0838eb976f982ef4775b711776` remotely dereferences to the same commit. All 56 tests, compilation, dependency health, and byte-identical real-source reconstruction pass again from merged `main`. Issue #331 carries the provenance-only lifecycle sync.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
