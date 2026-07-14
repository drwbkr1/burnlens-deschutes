# Devlog — When HTTP 200 Is Not Data

**Date:** 2026-07-13 local / 2026-07-14 UTC

**Issue:** #317

## Weakness selected

BurnLens had exact VIIRS URLs but no executable guard proving that their responses were actually the promised NetCDF/HDF5 files. The existing HEAD result showed redirects and encouraged a reasonable but unverified assumption that NASA bytes could be inspected without a credential.

## What the real run found

That assumption failed. Without authentication, a default download ended at `401`. Adding a normal browser user agent changed the final status to `200`, but both `.nc` and `.h5` targets contained an Earthdata Login page beginning with `<!DOCTYP` and were only about 11 KB. A workflow that trusted URL suffixes or HTTP status would have accepted the wrong files.

## Improvement made

BurnLens now fails closed. The repository-owned validator checks body type, HDF5/NetCDF-4 magic, plausible minimum size, and pair completeness before source registration. It generates normalized and human-readable blocked evidence without retaining the login page, signed redirect, or any credential material. A separate renderer rebuilds the HTML and visual evidence exactly from committed JSON.

## Portfolio meaning

This checkpoint is deliberately small: it demonstrates reliability judgment at the first real byte boundary. The visual report makes the failure visible to a reviewer, while the records prevent an access success from being mistaken for a wildfire result. No NASA pixel was opened, so HDF structure, mask values, geolocation, AOI intersection, and label fitness remain unknown.

## Next boundary

The exact pair now has two owner-gated credentials: CDSE for Sentinel and Earthdata Login for LP DAAC. Acquisition may resume only after explicit approval for both, using secret-safe handling and the validator added here.

## Shipment evidence

Issue #317 closed through PR #318. The pull request was squash-merged at `d4ce26c87341e4d3798a0d84e257a964ebd2cde0`, and the annotated `v0.1.2-access-integrity-baseline` tag was verified to dereference to that exact commit. The rendered PR and branch README passed review; all eight tests and deterministic HTML/PNG rebuild checks passed again on `main`.

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
