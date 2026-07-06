# Phase 1 / Objective Three — Data Stack Decision Matrix

Expanded during the Objective Three remediation pass after branch creation and fresh source research.

Documentation only. This matrix does not authorize data acquisition, downloads, preprocessing, AOI selection, labeling, baseline generation, model work, public maps, or operational use.

## Decision summary

The Objective Three candidate stack is feasible for future planning, with Sentinel-2 Level-2A as the primary imagery candidate, Landsat Collection 2 Level-2 as secondary imagery and thermal/context support, NASA HLS as an optional harmonized imagery path, NASA FIRMS as a bounded reference/cue source, Deschutes County GIS as local context, and STAC-style metadata as the provenance pattern.

## Matrix

| Source family | Authority | Future role | Access path to validate | Resolution / scale | Time / latency | Quality fields | Format / CRS concern | Main risk | Decision |
|---|---|---|---|---|---|---|---|---|---|
| Sentinel-2 Level-2A | Copernicus / ESA / EU | Primary multispectral imagery | CDSE STAC, CDSE browser, collection endpoint | Native bands at 10 m, 20 m, and 60 m | Item datetime and selected date range | Cloud and item metadata fields | STAC geometry in WGS 84; asset grid must be inspected | Cloud/smoke and band-resolution differences | Primary candidate. |
| Landsat Collection 2 Level-2 | USGS | Secondary imagery, SR/ST context, QA comparison | EarthExplorer and official Landsat access paths | 30 m reflective bands; thermal product context | Scene acquisition datetime | QA layers and product metadata | Scene grid and product metadata must be recorded | Coarser than Sentinel-2 for many visual details | Secondary candidate. |
| NASA HLS L30/S30 | NASA Earthdata / LP DAAC | Harmonized 30 m option | Earthdata / LP DAAC catalog | 30 m global gridded products | Daily product family; item date must be recorded | QA band and cloud/shadow masking products | COG band files, MGRS tiling, 30 m grid | May hide native sensor differences | Optional candidate. |
| FIRMS MODIS | NASA FIRMS | Coarse active-fire reference | FIRMS files, services, or API | Coarse thermal detections | NRT/RT/URT or archive; overpass-dependent | Confidence, brightness/FRP where available | WGS84 detection records; not mask geometry | Over/under alignment with actual perimeter | Reference only. |
| FIRMS VIIRS | NASA FIRMS | Preferred active-fire hotspot cue | FIRMS files, services, or API | Finer than MODIS, still thermal detection scale | Frequent polar-orbit observations, product latency varies | low/nominal/high confidence | WGS84 detection records; confidence semantics differ | Not a truth mask; cloud/smoke/view limitations | Reference only. |
| FIRMS Landsat active fire | NASA FIRMS | Optional higher-resolution active-fire cue | FIRMS Landsat active-fire product path | Higher-resolution active-fire detections where available | Landsat overpass time | H/M/L confidence, path/row/track/scan | Pixel-center fields and acquisition time must be recorded | Less frequent and not a polygon mask | Optional reference. |
| Deschutes County GIS | Deschutes County | Local overlays and AOI context | County Data Portal | Vector feature classes and tabular downloads | Weekly update note at portal level; layer-specific date needed | Layer attributes and source notes | State Plane Oregon South or Web Mercator depending access path | Parcel/hazard layers invite overclaiming | Context only. |
| STAC Item pattern | STAC specification | Provenance and discovery model | STAC Item fields and collection/search model | N/A | Datetime/start/end metadata | Links, assets, properties | GeoJSON/WGS 84 geometry expectation | Mistaking metadata pattern for data source | Use as metadata pattern. |

## Preferred future stack order

1. **Primary path:** Sentinel-2 Level-2A imagery + FIRMS VIIRS reference/cue + Deschutes County GIS context + STAC-style provenance.
2. **Secondary path:** Landsat Collection 2 Level-2 imagery + FIRMS reference + Deschutes County GIS context.
3. **Simplified harmonized path:** NASA HLS + FIRMS reference + Deschutes County GIS context, used only if 30 m consistency is more important than native Sentinel-2 detail.
4. **Fallback scaffold path:** Public/open sample imagery only for code or UI scaffolding, with no performance, source, or fire claims.

## Go / caution / no-go decisions

| Source family | Decision | Reason |
|---|---|---|
| Sentinel-2 Level-2A | Go for future planning | Strong primary imagery candidate with reproducible STAC discovery. |
| Landsat Collection 2 Level-2 | Go for future planning | Strong secondary imagery and thermal/context candidate. |
| NASA HLS | Caution / optional | Good harmonized 30 m option, but must not be silently mixed with native products. |
| FIRMS MODIS/VIIRS | Caution / reference only | Useful for cues and comparison, not truth masks. |
| FIRMS Landsat active fire | Caution / optional reference | Valuable where available, but still not a segmentation mask. |
| Deschutes County GIS | Go for context only | Useful local context, but high overclaiming risk if used improperly. |
| STAC | Go as metadata pattern | Strong provenance model. |

## Requirements before any Phase Two data use

Before data is used, Phase Two must create:

- AOI record;
- source records for each selected product or layer;
- access log;
- format/CRS precheck;
- provenance manifest;
- source-precedence note;
- claim register entry for any planned public wording;
- no-go note for any rejected source.

## Phase One decision

The stack is feasible, but not yet operationalized. Objective Three ends with a planning scaffold, not a dataset.
