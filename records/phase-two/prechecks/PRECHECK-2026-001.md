# PRECHECK-2026-001 — Metadata Format and CRS

| Field | Result |
|---|---|
| Precheck ID | `PRECHECK-2026-001` |
| Scope | Public metadata only |
| AOI query CRS | `EPSG:4326` longitude/latitude |
| AOI bbox | `[-121.56, 43.61, -121.40, 43.75]` |
| CDSE response | STAC 1.0.0 JSON / GeoJSON; passed |
| NASA response | CMR UMM JSON; passed |
| Normalized fixture | UTF-8 JSON; passed after schema/content checks |
| Source-asset format | Not inspected; blocked |
| Source-asset CRS | Not inspected; blocked |
| Reprojection decision | Not made |
| Status | Passed for metadata discovery only |

## Observed metadata behavior

- CDSE collection metadata exposes WGS 84 item bounding boxes, item datetimes, platform, product type, cloud cover, collection bands, and an official license link.
- Every retained Sentinel item is in MGRS tile `T10TFP`; the item footprints are much larger than `AOI-2026-001`.
- NASA CMR bounding-box searches return VIIRS swath granules whose footprints intersect the query envelope. CMR does not assert that an intersecting granule contains a fire detection inside the AOI.
- NASA product documentation states that the Level-2 fire products require matching geolocation companion products for accurate geolocation.

## Asset-level checks deliberately not performed

- MIME type and file encoding;
- SAFE/JP2/COG/NetCDF/HDF structure;
- per-item projected CRS and affine transform;
- band dimensions, resolution, scaling, nodata, masks, and quality flags;
- companion VIIRS geolocation granule matching;
- checksums, byte sizes, signed URLs, or download resumption;
- reprojection, clipping, resampling, alignment, or tiling.

Those checks require a new issue and F04-A decision for exact assets.
