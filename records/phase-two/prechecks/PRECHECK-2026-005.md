# PRECHECK-2026-005 - Atomic Exact-Pair Intake Contract

**Issue:** #325

**Tool version:** BurnLens package `0.3.0`

**Contract:** `paired-intake-contract-v0.1.0`

**Contract SHA-256:** `85b6934ed3fe47dabfdddd47375dc07fc78bd0db8d15c24cb3a50c53e65b8362`

## Required package

Exactly three files must appear together in one quarantine directory:

1. Sentinel-2 L2A SAFE ZIP: `S2B_MSIL2A_20240627T184919_N0510_R113_T10TFP_20240627T213644.SAFE.zip`, exactly 1,127,031,562 bytes, provider MD5 and BLAKE3 matched, valid ZIP, one exact SAFE root, safe member paths, `manifest.safe` present, and CRC test clean.
2. NOAA-21 VIIRS active-fire granule: `VJ214IMG.A2024179.1936.002.2025284191612.nc`, exactly 2,710,616 bytes, native HDF5/NetCDF-4 signature.
3. NOAA-21 VIIRS terrain-corrected geolocation granule: `VJ203MODLL.A2024179.1936.021.2024327213621.h5`, exactly 40,255,764 bytes, native HDF5 signature.

The two VIIRS native IDs must share the recorded acquisition token `A2024179.1936`. Unexpected entries, missing files, type mismatch, size mismatch, corrupt or unsafe ZIP structure, duplicate ZIP members, checksum failure, or destination collision fail closed.

## Promotion contract

- Validation occurs entirely in quarantine before registration.
- Accepted files receive local SHA-256, MD5, and BLAKE3 values in the registration manifest.
- The complete quarantine directory and destination must share a filesystem.
- The destination must not already exist.
- Only the complete validated directory is renamed with one atomic `os.replace` operation.
- No partial raw package is created.

## Actual result

The real package is absent and returns `BLOCKED_OWNER_CREDENTIAL`. A temporary reduced synthetic contract proves the transaction mechanics: partial input fails, checksum tampering fails, a complete exact set promotes atomically, and all synthetic bytes are deleted afterward.

Thirty-one repository tests cover contract identity, pair identity, missing/unexpected inputs, size and magic failures, unsafe/corrupt ZIP cases, provider checksum mismatch, destination protection, complete promotion, deterministic reporting, and the temporary rehearsal.

## Non-implications

The rehearsal does not prove provider delivery, real-file integrity, raster readability, geolocation alignment, AOI fitness, cloud/smoke quality, fire presence, label readiness, dataset readiness, model readiness, or operational fitness.
