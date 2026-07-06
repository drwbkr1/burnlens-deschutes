# Phase 1 / Objective Three — Source Candidate Inventory

Draft created after branch creation and fresh source research.

This inventory is preliminary. It does not select final data, download imagery, ingest files, create labels, generate baselines, or authorize model work.

## Candidate source categories

| Category | Candidate source family | Authority | Candidate role | Initial feasibility note |
|---|---|---|---|---|
| Multispectral imagery | Sentinel-2 MSI | Copernicus / ESA / EU | Imagery source | Strong candidate for later imagery planning because it provides free systematic multispectral products with 10 m, 20 m, and 60 m bands. |
| Multispectral imagery | Landsat Collection 2 Level-2 | USGS | Imagery source | Strong candidate for surface reflectance / surface temperature context and long-running public archive work. |
| Harmonized imagery | HLS Sentinel-2 / Landsat products | NASA Earthdata / LP DAAC | Imagery and metadata source | Strong candidate for harmonized 30 m planning where consistency matters more than maximum spatial resolution. |
| Active-fire reference | FIRMS MODIS / VIIRS / Landsat products | NASA FIRMS | Reference, weak-label, baseline, comparison | Useful for active-fire reference and baseline planning, but not a pixel-perfect mask source. |
| Local overlays | Deschutes County GIS | Deschutes County | Overlay source | Strong candidate for roads, taxlots, public land, wildfire hazard zones, emergency-service locations, and CRS planning. |
| Catalog / metadata pattern | STAC | STAC specification | Metadata and access pattern | Useful for future reproducible discovery and provenance planning. |
| Prototype scaffold | Public sample imagery | Public/open source only | Scaffold only | Allowed only if needed for UI or structure tests and clearly separated from source or model claims. |

## Source role rules

- Imagery sources may support future preprocessing and model-input planning.
- Reference sources may support comparison, sampling, weak labels, or baseline displays.
- Local overlays may support map context and exposure-style summaries.
- Prototype scaffold data must never be used for performance or source claims.
- BurnLens-derived outputs remain experimental and lower priority than official sources.

## Required future review fields

```text
Source family:
Authority:
Candidate role:
Access path:
Spatial resolution:
Temporal resolution:
Coverage over Deschutes County:
Bands or layers:
Quality information:
Known limitations:
Citation notes:
Feasibility decision:
```

## Research references

- Copernicus Sentinel-2
- USGS Landsat Collection 2 Level-2
- NASA FIRMS
- NASA HLS
- Deschutes County GIS
- STAC specification
