# PRECHECK-2026-002 — Exact Asset Format, Grid, and Quality Contract

| Field | Sentinel-2 scene | NOAA-21 fire/geolocation pair |
|---|---|---|
| Source IDs | `SOURCE-2026-004` | `SOURCE-2026-005`, `SOURCE-2026-006` |
| Native format | SAFE; JPEG 2000 band/quality assets plus XML | NetCDF-4 fire swath plus HDF-EOS5/HDF5 geolocation swath |
| Source geometry | MGRS tile `10TFP`; UTM/WGS84 family | Cartesian swath indices geolocated by companion latitude/longitude arrays |
| Expected CRS | EPSG:32610 inference from zone 10 northern MGRS tile; verify in actual metadata | No single raster CRS assumption; geolocation arrays are geodetic coordinates |
| Resolution | 10 m and 20 m selected assets | 375 m fire mask; 750 m companion geolocation grid |
| Quality layers | `SCL_20m`, `CLD_20m`, product metadata | `fire mask`, `algorithm QA`, geolocation QA, sparse fire-pixel fields |
| Provider checksum | Whole product MD5 and BLAKE3 | None in current CMR granule records |
| Pixel metadata inspected | No | No |
| Decision | Contract ready; source verification blocked | Contract ready; source verification blocked |

## Sentinel inspection contract

The provisional optical set is `B02`, `B03`, `B04`, `B08`, `B11`, and `B12`, with `SCL` and `CLD` for quality review. Native resolutions remain distinct; no 20 m band may be silently described as native 10 m information.

The official CDSE Sentinel-2 L2A documentation states that optical bands are reflectance data, documents 10/20/60 m resolutions, and defines SCL classes 0–11. It also warns that processing baseline 04.00 changed digital-number interpretation. Because this item embeds baseline `N0510`, a future intake must parse `MTD_MSIL2A.xml` for the actual quantification and offset rather than assume a universal divide-by-10,000 rule for native JP2 values.

Expected quality handling before any label work:

- SCL 0 (no data), 1 (saturated/defective), 3 (cloud shadow), 7–10 (unclassified/cloud/cirrus), and 11 (snow/ice) cannot become ordinary background;
- SCL 2 (dark area) and smoke-adjacent pixels require review;
- tile cloud cover is not an AOI cloud/smoke measurement;
- actual CRS, transform, dimensions, pixel alignment, JP2 nodata metadata, and AOI coverage must be read from the acquired product.

## VIIRS inspection contract

The active-fire mask has classes 0–9. Classes 7/8/9 encode low/nominal/high-confidence fire pixels; classes 0–6 include not processed, bow-tie deletion, glint, water, cloud, land, and unclassified states. `algorithm QA` contains input/geolocation quality and detection-condition bits. The companion geolocation product supplies height, latitude, and longitude arrays; current catalog metadata lists 999.9 as the latitude/longitude fill value.

Before any spatial comparison:

1. verify matching array dimensions and scan indexing;
2. reject geolocation fill values and non-nominal geolocation QA;
3. inspect `FirePix`, mask classes, view angle, bow-tie, glint, cloud, and adjacency fields;
4. transform valid geodetic coordinates into the chosen analysis CRS with an explicit method;
5. keep the native 375 m evidence footprint and never represent resampling as new 10–20 m truth.

## Working/display CRS

The likely local analysis CRS is EPSG:32610 because the optical tile is in UTM zone 10 north, but the choice remains provisional until the actual source metadata is inspected and the final modeling AOI is approved. WGS 84 longitude/latitude remains the provenance geometry; any future web-display CRS is visualization-only.
