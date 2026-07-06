# Phase 1 / Objective Three — Research Validation Log

Created during the Objective Three remediation pass after branch creation and fresh source research.

Documentation only. This log records which source claims support Objective Three planning artifacts. It does not authorize data acquisition, implementation, modeling, public outputs, or operational use.

## Validation method

For each important production claim, record:

```text
claim_id:
claim:
source_authority:
source_type:
evidence_summary:
affected_artifacts:
validation_status:
last_checked:
notes:
```

Validation status values:

| Status | Meaning |
|---|---|
| validated | Supported by official or primary documentation. |
| partial | Supported, but needs future source-specific inspection. |
| unresolved | Not yet supported enough for production use. |
| rejected | Claim should not be used. |

## Validated claims

| Claim ID | Claim | Source authority | Evidence summary | Affected artifacts | Status |
|---|---|---|---|---|---|
| RV-001 | CDSE STAC is a valid discovery/provenance path for Copernicus EO products. | Copernicus Data Space Ecosystem | CDSE STAC standardizes metadata for EO data, exposes an endpoint, and supports browser/search workflows. | Imagery access, data stack, provenance | validated |
| RV-002 | Sentinel-2 Level-2A is available through CDSE STAC collections. | Copernicus Data Space Ecosystem | CDSE lists Sentinel-2 Level-2A as an available STAC collection and exposes a collection endpoint. | Imagery access, data stack | validated |
| RV-003 | CDSE STAC supports filtering by time, spatial extent, and cloud-cover-style item attributes. | Copernicus Data Space Ecosystem | CDSE documents Sentinel-2 Level-2A filtering examples and filter/query extensions. | Imagery access, AOI criteria | validated |
| RV-004 | Landsat Collection 2 Level-2 includes global scene-based surface reflectance and surface temperature products. | USGS | USGS describes Landsat Collection 2 Level-2 science products as global scene-based SR/ST products. | Imagery access, data stack | validated |
| RV-005 | Landsat Level-2 products have no restrictions on use but require appropriate citation. | USGS | USGS provides citation guidance and states no restrictions on Landsat product use. | Imagery access, claims register | validated |
| RV-006 | NASA HLS provides harmonized Landsat/Sentinel 30 m products with COG band files and QA support. | NASA Earthdata / LP DAAC | NASA Earthdata describes HLS as consistent SR/TOA products, 30 m global observations, COG format, separate bands, QA band, and angle bands. | Imagery access, data stack, CRS precheck | validated |
| RV-007 | FIRMS NRT/RT/URT products have different latency expectations. | NASA FIRMS | FIRMS FAQ describes NRT within 3 hours, RT within 30 minutes, and URT within 5 minutes on a best-effort basis. | Active fire review | validated |
| RV-008 | FIRMS confidence values require empirical interpretation and differ by MODIS/VIIRS. | NASA FIRMS | FIRMS FAQ states confidence should be used with caution, differs by MODIS and VIIRS, and has no universal optimal cutoff. | Active fire review, claims register | validated |
| RV-009 | MODIS/VIIRS active-fire detections can misalign with perimeters due to timing, resolution, clouds, smoke, and view geometry. | NASA FIRMS | FIRMS FAQ explains overpass timing, 375 m VIIRS / 1 km MODIS thermal-band representation, obscuration, and view geometry displacement. | Active fire review, claims register | validated |
| RV-010 | Deschutes County GIS provides public layers, weekly updates, and shapefile/KML/CSV formats. | Deschutes County GIS | County GIS page states more than 60 layers, weekly updates, and formats. | Local overlay review, CRS precheck | validated |
| RV-011 | Deschutes County local layers include boundaries, environment, land, place, transportation, and water feature classes relevant to BurnLens context. | Deschutes County GIS | County GIS page lists those feature-class groups and named examples. | Local overlay review, AOI criteria | validated |
| RV-012 | Deschutes County GIS CRS handling requires care because public GIS data and data portal downloads have documented coordinate systems. | Deschutes County GIS | County page documents State Plane Oregon South and WGS 1984 Web Mercator Auxiliary Sphere contexts. | Format/CRS precheck, local overlay review | validated |
| RV-013 | STAC Item records provide a useful provenance model with ID, geometry, bbox, properties, links, assets, and datetime fields. | STAC specification | STAC Item specification defines required Item fields and UTC datetime expectations. | Provenance spec | validated |

## Open research items for Phase Two

| Open item | Why it remains open | Required future action |
|---|---|---|
| Exact Sentinel-2 item/band assets for chosen AOI | No AOI or date range selected yet. | Query CDSE STAC after AOI/date selection. |
| Exact Landsat scenes/path-row for chosen AOI | No AOI or date range selected yet. | Search USGS access path after AOI/date selection. |
| Exact HLS MGRS tile and band assets | No AOI/date selected. | Query NASA Earthdata/LP DAAC after AOI/date selection. |
| Exact FIRMS detection fields for chosen source family/date | No time window selected. | Pull sample metadata only after Phase Two authorization. |
| Exact Deschutes County layer item IDs and fields | Layer choices are not finalized. | Review each portal item before future use. |
| Numeric AOI size limits | Processing and map constraints are not tested. | Set after initial pipeline feasibility tests. |

## Prohibited unresolved claims

Do not claim any of the following until future evidence exists:

- BurnLens identifies official wildfire extent.
- BurnLens predicts fire spread.
- FIRMS detections are ground-truth masks.
- Deschutes County overlays imply parcel-level risk.
- A selected AOI is representative of all Deschutes wildfire conditions.
- Any model is accurate, validated, operational, or field-tested.

## Maintenance rule

Update this log whenever a new external source is used, a public claim is drafted, a data source is promoted, or a source limitation changes.
