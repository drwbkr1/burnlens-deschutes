# Phase 1 / Objective Three — Imagery Source Access Review

Draft created after branch creation and fresh source research.

This document is documentation-only. It does not authorize data acquisition, imagery download, preprocessing, AOI tile selection, labeling, baseline generation, model work, or public outputs.

## Reviewed source families

| Source family | Authority | Candidate path | Feasibility note |
|---|---|---|---|
| Sentinel-2 MSI | Copernicus Data Space Ecosystem | CDSE catalog, STAC, browser, APIs | Strong future imagery candidate. STAC supports discovery and metadata review before acquisition. |
| Landsat Collection 2 Level-2 | USGS | EarthExplorer and Landsat access tools | Strong future imagery candidate for surface reflectance and surface temperature. Includes metadata and QA products. |
| HLS Sentinel/Landsat products | NASA Earthdata / LP DAAC | Earthdata and LP DAAC catalog paths | Strong future harmonized imagery candidate at 30 m when consistency matters more than maximum resolution. |
| STAC pattern | STAC / CDSE | Catalog and item search pattern | Useful as a reproducible discovery and provenance model. |

## Findings

- Sentinel-2 should remain a leading candidate for visible and multispectral imagery planning.
- Landsat Level-2 should remain a candidate for surface reflectance, surface temperature, quality bands, and long archive support.
- HLS should remain a candidate when harmonized Landsat/Sentinel surface reflectance simplifies later data management.
- STAC should be treated as a discovery/provenance pattern, not as a data source by itself.
- Future work must record product ID, source date, access date, CRS, resolution, cloud/quality information, and citation notes before any data is used.

## Future access review checklist

```text
Source family:
Authority:
Discovery path:
Account or key requirement:
Product level:
Product format:
Resolution:
Date fields:
Cloud or quality fields:
Metadata fields:
Citation notes:
BurnLens role:
Decision:
```

## Boundary

Official sources govern. BurnLens outputs are experimental portfolio artifacts. This review prepares future data planning only.
