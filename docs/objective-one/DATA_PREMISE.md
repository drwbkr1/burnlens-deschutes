# BurnLens Deschutes — Public Data Premise

## Purpose

This document defines the public-data premise for BurnLens Deschutes. It identifies plausible public source categories, expected roles, and limits before data ingestion begins.

## Data premise statement

BurnLens Deschutes will use public or open geospatial data, wildfire-relevant imagery, and documented processing steps to produce experimental, map-ready screening outputs for a defined Deschutes County study area.

Every source remains a candidate until its access method, license or use terms, spatial coverage, update cadence, coordinate reference system, and suitability for the selected demo AOI are checked.

## Candidate source categories

### 1. Satellite imagery

**Likely role:** image input for inspection, preprocessing, baseline screening, and future computer vision experiments.

**Candidate sources:** Sentinel-2 and Landsat Collection 2 products.

**Limits:** cloud, smoke, haze, snow, shadows, revisit timing, spatial resolution, and temporal mismatch may degrade interpretation. Imagery must be tiled, normalized, documented, and versioned before model use.

### 2. Active fire and hotspot data

**Likely role:** public reference layer, context layer, weak-label candidate, or baseline comparison source.

**Candidate sources:** NASA FIRMS MODIS and VIIRS active-fire data.

**Limits:** hotspot detections are not exact fire perimeters, evacuation products, or field-verified incident truth. Near-real-time active-fire products require careful caveats.

### 3. Deschutes County GIS layers

**Likely role:** local planning and overlay context.

**Candidate layers:** county boundary, city limits, communities, taxlots, wildfire hazard zones, public land, vegetation, slope, emergency service locations, schools, county routes, road centerlines, state routes, USFS roads, and watershed boundaries.

**Limits:** layer freshness, CRS, and appropriate use must be checked. Parcel/taxlot context must not be used for enforcement claims.

### 4. Wildfire risk and hazard context

**Likely role:** planning context, comparison layer, or explanatory overlay.

**Candidate sources:** Oregon wildfire risk or hazard products and relevant county hazard layers.

**Limits:** risk and hazard products are not interchangeable with active-fire detections. BurnLens Deschutes must not present itself as an official hazard classification tool.

### 5. Roads, access, structures, and facilities

**Likely role:** exposure-style map context.

**Candidate sources:** county road layers, state routes, USFS roads, emergency service locations, schools, public facilities, and property-related public layers.

**Limits:** road presence does not imply road condition, capacity, closure status, or safety. Facility or parcel overlays do not imply property-specific risk.

## Required source metadata

Each source considered in Phase 2 should record:

- source name and organization
- source URL and access method
- source date or update date
- download date
- license or use terms
- spatial coverage
- coordinate reference system
- resolution or scale
- update cadence
- intended BurnLens use
- known limitations
- versioned local filename
- checksum or file hash when practical

## Data-use rules

BurnLens Deschutes must:

1. Use public or open data where possible.
2. Avoid confidential, restricted, or nonpublic operational data.
3. Preserve source metadata for downloaded or transformed files.
4. Label model-generated and baseline outputs as experimental.
5. Avoid presenting public datasets as field validation.
6. Avoid implying official endorsement from data providers.
7. Yield to official sources when information differs.

## Phase 2 handoff

Phase 2 should convert this premise into a concrete data inventory by selecting a final demo AOI, primary imagery source, fire-reference source, local overlay package, baseline comparison approach, dataset manifest format, and version naming pattern.
