# Phase 1 / Objective Three — Format and CRS Precheck

Expanded during the Objective Three remediation pass after branch creation and fresh source research.

Documentation only. This precheck does not authorize data acquisition, reprojection, conversion, clipping, tiling, model work, or public output creation.

## Purpose

This document defines the checks that must occur before future BurnLens data is treated as compatible. It covers raster imagery, active-fire reference records, local vector overlays, and provenance metadata.

## Core rule

Do not combine, compare, buffer, rasterize, vectorize, clip, or summarize layers until the source format, geometry type, CRS, units, resolution, and time fields have been recorded.

## Source format policy

| Source type | Expected future formats | Required check | Notes |
|---|---|---|---|
| Sentinel-2 Level-2A | STAC Item metadata and raster assets | item ID, asset keys, band assets, footprint, datetime, CRS/grid | Treat STAC as discovery/provenance pattern; inspect assets before use. |
| Landsat Collection 2 Level-2 | Scene-based raster product files with metadata and QA | scene/product ID, SR/ST availability, QA layers, acquisition date | Preserve product citation and QA metadata. |
| NASA HLS | Cloud Optimized GeoTIFF band files plus QA/angle bands | HLS product, version, MGRS tile, band files, QA band | HLS is 30 m and harmonized; do not mix silently with native resolution products. |
| NASA FIRMS | CSV, SHP, KML, API/table-style detections | source family, coordinates, confidence, acquisition time, product mode | Treat as reference/cue data, not mask truth. |
| Deschutes County GIS | Esri shapefile, KML, CSV, services | layer name, feature class, CRS, geometry type, fields | County data may be State Plane Oregon South or Web Mercator depending access path. |
| STAC metadata | JSON / GeoJSON Item structures | required Item fields, links, assets, datetime | Use as provenance model. |

## CRS policy

Use a three-CRS record for future work:

```text
source_crs:
analysis_crs:
display_crs:
```

Required rules:

1. Record the CRS as reported by the source before any transformation.
2. Store an unchanged source copy if future data is acquired.
3. Choose a single analysis CRS per run before measuring distance or area.
4. Use WGS 84 longitude/latitude for STAC-style geometry and bbox records.
5. Use web display CRS only for visualization, not measurement.
6. Do not buffer or calculate area in degrees.
7. Record units before distance, area, or proximity summaries.
8. Record every reprojection as a processing step in the run manifest.

## Deschutes County CRS handling

Deschutes County documents State Plane Oregon South for public GIS data and WGS 1984 Web Mercator Auxiliary Sphere for data portal downloads. Future local-layer work must therefore inspect downloaded files instead of assuming one CRS. A county layer may be acceptable only after source CRS, units, geometry type, and intended working CRS are recorded.

## Raster handling rules

For future raster imagery:

```text
source_product:
source_product_id:
source_datetime:
source_crs_or_grid:
pixel_size:
band_list:
quality_band_or_mask:
nodata_value:
asset_format:
source_extent:
working_extent:
resampling_method_if_any:
```

Rules:

- Never resample without recording method and target resolution.
- Do not mix resolutions without documenting alignment choices.
- Do not treat cloud/smoke/nodata pixels as background class.
- Any future mask output must carry source raster lineage.

## Vector handling rules

For future vector overlays:

```text
layer_name:
source_format:
geometry_type:
source_crs:
units:
fields_used:
fields_removed:
valid_geometry_check:
working_crs:
```

Rules:

- Validate geometry before overlay or rasterization.
- Keep source attribute fields needed for attribution and interpretation.
- Strip or ignore fields only with a written reason.
- Do not use parcel or place layers for claims about individual properties or emergency service coverage.

## Active-fire reference handling

FIRMS-style detections should be treated as point/pixel reference records. Future conversion into candidate review zones must record:

```text
source_family:
spatial_resolution:
buffer_or_rasterization_rule:
confidence_policy:
time_window:
unknown_zone_rule:
```

Do not turn point detections directly into final binary masks.

## Precheck checklist

A future source passes the format/CRS precheck only if all fields are known:

```text
source_name:
source_role:
source_format:
geometry_or_raster_type:
source_crs:
source_units:
source_resolution_or_feature_scale:
source_datetime_or_update_date:
quality_or_confidence_fields:
working_crs:
display_crs:
reprojection_needed:
conversion_needed:
known_risks:
decision:
```

## Phase One decision

The future data stack is feasible only if Phase Two records source CRS, working CRS, units, and conversion decisions before any processing.
