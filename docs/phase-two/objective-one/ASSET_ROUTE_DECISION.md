# Phase Two Exact Asset-Route Decision

**Decision ID:** `P2O1-ASSET-ROUTE-2026-001`

**Date:** 2026-07-13

**Status:** Routes verified; source-asset intake blocked

## Selected optical scene

`S2B_MSIL2A_20240627T184919_N0510_R113_T10TFP_20240627T213644` is the first post-report Sentinel-2 L2A acquisition in `METADATA-2026-001` and has 0.534711% tile-level cloud cover in current OData metadata. The clear June 25 scene begins about one hour before the approximate reported fire start, so it remains a pre-event candidate rather than the first active-event input.

The selected scene is product UUID `58cebcf0-c417-4384-a93a-2d6b15344117`, a 1,127,031,562-byte SAFE package in MGRS tile `10TFP`, relative orbit 113. CDSE currently reports provider checksums:

- MD5 `3806a834a97ab2eb41f1edf5496b433c`
- BLAKE3 `546336e996586f4c276eb9ed3d9818f9574edbed24334dce74a394bd3759cb10`

The first inspection package is provisionally limited to `B02_10m`, `B03_10m`, `B04_10m`, `B08_10m`, `B11_20m`, `B12_20m`, `SCL_20m`, `CLD_20m`, and the SAFE/product/granule metadata needed to interpret scaling, nodata, grid, and quality. This is an inspection set, not a frozen model input contract.

## Selected thermal-reference pair

The closest intersecting VIIRS swath in the retained source families is NOAA-21 `VJ214IMG.A2024179.1936.002.2025284191612`, beginning at 19:36 UTC—46 minutes 40.976 seconds after the Sentinel acquisition. The exact terrain-corrected geolocation companion is `VJ203MODLL.A2024179.1936.021.2024327213621`, with the same platform, day, and six-minute interval.

| Role | Concept ID | Format | CMR size | Provider checksum |
|---|---|---|---:|---|
| Active-fire swath | `G3944882727-LPCLOUD` | NetCDF-4 | 2.5850448608398438 MB | Not provided |
| Terrain-corrected geolocation | `G4037038741-LPCLOUD` | HDF-EOS5 / HDF5 | 38.39088821411133 MB | Not provided |

Both stable LP DAAC HTTPS paths returned `303` to transient signed CloudFront URLs on no-secret HEAD requests. Signed targets were not followed or retained.

## Alignment and evidence decision

Matching times and swath intersection make this pair suitable for a future inspection. They do not establish that a fire pixel exists in `AOI-2026-001`. The `VJ214IMG` fire mask, `algorithm QA`, sparse fire-pixel arrays, and `FirePix` attribute must be read before any detection claim. Accurate full-swath geolocation requires the matching `VJ203MODLL` latitude/longitude arrays.

VIIRS may become reference, cue, sampling, non-model baseline, or weak-label evidence. It may not become pixel-perfect truth or be upsampled and described as genuine 10–20 m labels. Even nominal/high-confidence detections require spatial, temporal, scan-angle, cloud/glint, bow-tie, and human review.

## Access decision

Choose the whole-product CDSE OData route for the first Sentinel intake because it carries provider checksums and preserves the native SAFE structure. Do not use Sentinel Hub processing, a preview, or a manually exported image as a substitute for source provenance. The OData route requires a bearer token, so acquisition is blocked pending owner approval for the credential boundary.

NASA may use the stable HTTPS routes discovered through CMR. Never persist a redirected signed query string. Compute local SHA-256 after a later authorized download because provider checksums are absent.
