# Phase 1 / Objective Three — Imagery Source Access Review

Expanded during the Objective Three remediation pass after branch creation and fresh source research.

This document is documentation-only. It does not authorize data acquisition, imagery download, preprocessing, AOI tile selection, labeling, baseline generation, model work, or public outputs.

## Decision summary

Sentinel-2 Level-2A should remain the primary future imagery candidate. Landsat Collection 2 Level-2 should remain the secondary imagery candidate, especially for surface reflectance, surface temperature, QA, and long-archive context. NASA HLS should remain an optional harmonized imagery candidate when consistent 30 m gridding and temporal compositing are more useful than native Sentinel-2 spatial resolution.

## Reviewed imagery source families

| Source family | Authority | Candidate discovery path | Candidate product level | Format / data structure | Initial BurnLens role | Decision |
|---|---|---|---|---|---|---|
| Sentinel-2 Level-2A | Copernicus / ESA / EU via Copernicus Data Space Ecosystem | CDSE STAC endpoint, CDSE STAC Browser, CDSE collection endpoint | Level-2A surface reflectance | STAC Items with assets; future raster assets to be reviewed before use | Primary multispectral imagery candidate | Keep as primary candidate. |
| Landsat Collection 2 Level-2 | USGS | EarthExplorer, USGS Landsat tools, official product documentation | Level-2 surface reflectance and surface temperature | Scene-based products with metadata and QA layers | Secondary imagery and thermal/context candidate | Keep as secondary candidate. |
| NASA HLS L30/S30 | NASA Earthdata / LP DAAC | NASA Earthdata catalog and LP DAAC paths | Daily global 30 m harmonized products | Cloud Optimized GeoTIFF, separate band files, QA and angle bands | Optional harmonized imagery source | Keep as optional candidate. |
| STAC pattern | STAC specification and CDSE STAC API | Collection, search, queryables, item metadata, assets | Metadata and discovery pattern | JSON / GeoJSON style Items | Reproducible discovery and provenance model | Use as pattern, not standalone data source. |

## Sentinel-2 Level-2A access notes

Future Sentinel-2 planning should start with Copernicus Data Space STAC discovery, not manual screenshots or ad hoc downloads. Required fields to record before later use:

```text
collection: sentinel-2-l2a
search_endpoint: CDSE STAC /search or collection endpoint
bbox_or_geometry: AOI footprint in longitude/latitude
start_datetime:
end_datetime:
cloud_cover_filter:
product_id:
item_datetime:
item_geometry:
item_bbox:
asset_keys:
quality_or_cloud_fields:
access_date:
```

Preferred future discovery logic:

1. Query the `sentinel-2-l2a` collection.
2. Filter to the selected AOI footprint.
3. Filter to the selected candidate date range.
4. Apply an initial cloud-cover ceiling.
5. Inspect returned item metadata and assets.
6. Record product IDs before any download or processing.

## Landsat Collection 2 Level-2 access notes

Landsat Level-2 remains a strong companion source because it provides global scene-based surface reflectance and surface temperature products and has clear citation guidance. Required future fields:

```text
landsat_product_family:
sensor_platform:
path_row:
scene_id_or_product_id:
acquisition_datetime:
surface_reflectance_available:
surface_temperature_available:
qa_bands_available:
processing_level:
citation_note:
access_date:
```

Use Landsat for:

- secondary surface reflectance checks;
- long archive context;
- surface temperature context;
- QA-driven comparison;
- non-primary baseline exploration.

Do not use Landsat as the sole source if the intended future AOI needs finer spatial detail and suitable Sentinel-2 coverage is available.

## NASA HLS access notes

HLS is useful when future work prioritizes a consistent 30 m grid and harmonized Landsat/Sentinel surface reflectance over native Sentinel-2 resolution. Required fields:

```text
hls_product: HLSL30 or HLSS30
version:
MGRS_tile:
observation_datetime:
band_files:
qa_band:
angle_bands:
cloud_mask_or_quality_notes:
COG_asset_paths:
access_date:
```

Use HLS only when the simplification benefit is explicit. Do not silently mix HLS with native Sentinel-2 or Landsat products without documenting resolution, grid, and band differences.

## Imagery acceptance gate

A candidate imagery item may advance only when all are true:

- source authority is official and cited;
- AOI overlap is confirmed;
- acquisition date and time are recorded;
- product ID or item ID is recorded;
- CRS/grid/resolution are recorded;
- cloud or QA fields are recordable;
- bands/assets are inspected before use;
- citation or attribution note is recorded;
- future run can be tied to repo commit, AOI version, dataset version, and source metadata.

## Rejection or defer triggers

Defer imagery if:

- product metadata is incomplete;
- AOI overlap cannot be confirmed;
- cloud/smoke quality cannot be evaluated;
- date range is mismatched with reference products;
- resolution is unsuitable for the task;
- source licensing or citation cannot be recorded;
- use would imply operational wildfire intelligence.

## Boundary

Official sources govern. BurnLens outputs are experimental portfolio artifacts. This review prepares future data planning only.
