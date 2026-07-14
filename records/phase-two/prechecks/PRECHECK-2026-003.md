# PRECHECK-2026-003 — Provider Payload Integrity Contract

**Issue:** #317

**Tool version:** BurnLens package `0.1.2`

**Report contract:** `viirs-access-precheck-v0.1.0`

## Acceptance order

BurnLens must not trust an expected filename suffix, redirect, or final HTTP status. For each exact VIIRS response it must:

1. require a regular local file;
2. reject HTML/login/error content before source registration;
3. require the HDF5/NetCDF-4 first-eight-byte signature `894844460d0a1a0a`;
4. require a conservative source-specific minimum byte count;
5. compute and retain SHA-256 only for an accepted source asset;
6. preserve exact stable route, native ID, source record, access time, and decision;
7. fail closed with a nonzero process exit if either member of the required VIIRS pair fails.

The active-fire minimum is 1,000,000 bytes and the geolocation minimum is 20,000,000 bytes, both below their current CMR-reported sizes. These thresholds catch obvious delivery failures but do not replace provider metadata, HDF parsing, structural validation, pairing checks, or local SHA-256.

## Actual P2O1-T03 result

Both browser-style responses began with `<!DOCTYP` (`3c21444f43545950`), carried the title `Earthdata Login`, and were far below their minimum size. Both were rejected despite final HTTP `200`. The precheck exited `2`, emitted a normalized blocked report, and retained zero provider source bytes.

## Deferred real-file checks

Only after owner-approved Earthdata authentication may a later issue inspect HDF groups, attributes, fire mask, algorithm QA, sparse fire-pixel arrays, latitude/longitude arrays, fill values, scan alignment, geolocation QA, AOI intersection, or candidate class 7/8/9 evidence. This contract creates no label or detection.
