# Format and CRS Precheck Template

## Template status

This is a blank Phase Two intake template. It does not inspect, transform, reproject, rasterize, vectorize, label, mask, or publish data.

Do not replace placeholders until Phase Two data access is authorized.

## Purpose

Use this record to check whether a candidate dataset is technically usable before BurnLens processing. The precheck must document format, driver/tool expectations, coordinate reference system, units, extent, resolution, nodata, geometry validity, and any conversion or reprojection decision before data enters the pipeline.

OGC CRS/WKT guidance supports recording CRS definitions in machine- and human-readable form, and FGDC metadata guidance supports documenting spatial reference information for geospatial resources.

## Boundary warning

Experimental BurnLens technical precheck. Not official wildfire information. Not emergency guidance. Official sources govern.

## Precheck identifiers

| Field | Value |
|---|---|
| Precheck ID | `PRECHECK-YYYY-NNN` |
| Related source record | `SRC-YYYY-NNN` |
| Related access log | `ACCESS-YYYY-NNN` |
| Related AOI record | `AOI-YYYY-NNN` |
| Related provenance manifest | `MANIFEST-YYYY-NNN` |
| Task issue / PR | `#`, `#` |
| Created date | `YYYY-MM-DD` |
| Status | planned / passed / failed / deferred / no-go |

## Dataset identity

| Field | Value |
|---|---|
| Candidate file or asset name | `[placeholder]` |
| Asset type | raster / vector / table / catalog / API response / other |
| Source format | `[GeoTIFF, COG, GeoPackage, Shapefile, GeoJSON, CSV, STAC, other]` |
| Expected reader/tool | `[GDAL, rasterio, geopandas, STAC client, other]` |
| File path or URI | `[future path only after authorized access]` |
| Checksum | `[future checksum]` |
| File size | `[placeholder]` |
| Compression / tiling | `[placeholder]` |

## CRS and spatial reference

| Field | Value |
|---|---|
| CRS present? | yes / no / unknown |
| CRS authority | EPSG / OGC WKT / PROJJSON / source metadata / unknown |
| CRS code | `[EPSG:XXXX or placeholder]` |
| CRS WKT or source text stored? | yes / no / not applicable |
| Horizontal datum / reference frame | `[placeholder]` |
| Vertical datum | `[placeholder or not applicable]` |
| Units | meters / feet / degrees / unknown |
| Axis order concern? | yes / no / unknown |
| Coordinate epoch concern? | yes / no / unknown |
| Reprojection required? | yes / no / unknown |
| Target CRS if needed | `[placeholder]` |
| CRS decision | use as-is / reproject / reject / defer |

## Extent and alignment

| Check | Value |
|---|---|
| Dataset bounding box | `[xmin, ymin, xmax, ymax]` |
| AOI overlap confirmed? | yes / no / unknown |
| Pixel size / ground sample distance | `[placeholder]` |
| Raster dimensions | `[rows x columns]` |
| Vector feature count | `[placeholder]` |
| Geometry types | point / line / polygon / mixed / unknown |
| Nodata value | `[placeholder]` |
| Band count / band names | `[placeholder]` |
| Temporal timestamp or range | `[placeholder]` |

## Format validity checks

| Check | Result | Notes |
|---|---|---|
| File opens with expected tool. | pending / yes / no / not applicable | `[note]` |
| CRS can be read. | pending / yes / no / not applicable | `[note]` |
| Bounds can be read. | pending / yes / no / not applicable | `[note]` |
| Raster nodata is known. | pending / yes / no / not applicable | `[note]` |
| Raster bands are interpretable. | pending / yes / no / not applicable | `[note]` |
| Vector geometries are valid. | pending / yes / no / not applicable | `[note]` |
| Geometry repair needed. | pending / yes / no / not applicable | `[note]` |
| Format conversion needed. | pending / yes / no | `[target format]` |

## BurnLens pipeline fit

| Pipeline question | Decision | Notes |
|---|---|---|
| Can this source support AOI/context work? | pending / yes / no | `[note]` |
| Can this source support imagery preprocessing? | pending / yes / no / not applicable | `[note]` |
| Can this source support mask/label preparation? | pending / yes / no / not applicable | `[note]` |
| Can this source support exposure-style summary later? | pending / yes / no / not applicable | `[note]` |
| Can this source be used without public/official claims? | pending / yes / no | `[note]` |

## No-go conditions

Reject or defer the dataset if:

- CRS is missing or contradictory and cannot be resolved from metadata;
- source CRS is inappropriate for overlay or distance/area work and no safe reprojection plan exists;
- format cannot be opened by the expected toolchain;
- geometry or raster metadata is too damaged for reproducible use;
- license or source record is unresolved;
- use would create unsupported operational, official, validation, or endorsement claims.

## Acceptance criteria

- [ ] Source and access records exist.
- [ ] Format is documented.
- [ ] CRS is documented or unresolved CRS is explicitly flagged.
- [ ] Extent/AOI overlap is checked or deferred with reason.
- [ ] Conversion/reprojection decision is recorded.
- [ ] No data processing beyond precheck is performed by this record.
- [ ] Provenance manifest is updated before later use.

## Handoff

If passed, update the provenance manifest with source, access, format, CRS, checksum, and precheck decision before any preprocessing or model pipeline work.
