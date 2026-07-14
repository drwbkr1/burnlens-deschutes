# PRECHECK-2026-005 - Atomic Exact-Pair Intake Contract

**Issue:** #325

**Tool version:** BurnLens package `0.3.0`

**Contract:** `paired-intake-contract-v0.3.0`

**Full contract SHA-256:** `3fb736b4af757260f90affd4b5c0b902a44b0b9e3036158d34b7e5563b0809da`

## Required package

Exactly three files must appear together in one quarantine directory:

1. Sentinel-2 L2A SAFE ZIP: `S2B_MSIL2A_20240627T184919_N0510_R113_T10TFP_20240627T213644.SAFE.zip`, exactly 1,127,031,562 bytes, provider MD5 and BLAKE3 matched, valid ZIP, one exact SAFE root, safe member paths, `manifest.safe` present, and CRC test clean.
2. NOAA-21 VIIRS active-fire granule: `VJ214IMG.A2024179.1936.002.2025284191612.nc`, exactly 2,710,616 bytes, native HDF5/NetCDF-4 signature.
3. NOAA-21 VIIRS terrain-corrected geolocation granule: `VJ203MODLL.A2024179.1936.021.2024327213621.h5`, exactly 40,255,764 bytes, native HDF5 signature.

The two VIIRS native IDs must share the recorded acquisition token `A2024179.1936`. Unexpected entries, missing files, type mismatch, size mismatch, corrupt or unsafe ZIP structure, duplicate ZIP members, checksum failure, or destination collision fail closed.

Quarantine directories must not be symlinks or junctions. Expected assets must be ordinary single-link files, not symlinks, junction-backed paths, or hardlink aliases. The contract digest covers these transaction invariants together with the exact asset records.

## Promotion contract

- Validation occurs entirely in quarantine before registration.
- Accepted files receive local SHA-256, MD5, and BLAKE3 values in the registration manifest.
- The complete quarantine directory and destination must share a filesystem.
- The destination must not already exist.
- Only the complete validated directory is renamed with one atomic `os.replace` operation.
- No partial raw package is created.
- If the atomic rename fails, the provisional registration manifest is removed; the validated quarantine remains intact and passes the same gates on retry.

## Actual result

The real package is absent and returns `BLOCKED_OWNER_CREDENTIAL`. A temporary reduced synthetic contract proves the transaction mechanics: partial input fails, checksum tampering fails, a complete exact set promotes atomically, and all synthetic bytes are deleted afterward.

Thirty-six repository tests cover full contract identity, pair identity, missing/unexpected inputs, link-alias rejection, size and magic failures, unsafe/corrupt ZIP cases, provider checksum mismatch, destination protection, failed-rename rollback and retry, complete promotion, deterministic reporting, non-inflating metadata observation time, and the temporary rehearsal.

## Non-implications

The rehearsal does not prove provider delivery, real-file integrity, raster readability, geolocation alignment, AOI fitness, cloud/smoke quality, fire presence, label readiness, dataset readiness, model readiness, or operational fitness.
