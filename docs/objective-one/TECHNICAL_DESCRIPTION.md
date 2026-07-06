# BurnLens Deschutes — Technical Description

## Purpose

This document defines the technical description for BurnLens Deschutes. It explains the intended workflow, core components, outputs, and technical limits. Final datasets, training code, model architecture, and infrastructure are later-phase decisions.

## Technical summary

BurnLens Deschutes is a computer vision and GEOINT workflow for producing experimental wildfire screening outputs for a defined Deschutes County study area.

The project combines wildfire-relevant imagery, public geospatial layers, optional baseline fire-reference products, and future segmentation outputs into map-ready artifacts. Each output should be traceable to source data, processing code, model or baseline method, GitHub commit, version number, and run ID.

## Core workflow

**imagery → preprocessing → segmentation or baseline mask → raster output → vector polygons → map overlay → exposure-style summary → documented run package**

## Workflow stages

### 1. Source selection

Select the demo AOI and candidate public sources: satellite imagery, active-fire or hotspot context, county GIS layers, roads, parcels, facilities, hazard context, and AOI boundaries.

### 2. Preprocessing

Prepare data through clipping, CRS checks, reprojection when needed, tiling, normalization, image-mask alignment, metadata capture, and quality checks. Preprocessing should be scriptable and rerunnable.

### 3. Baseline or model mask

Produce a screening mask through either:

- a **baseline method** using public reference layers, thresholds, or prepared geospatial inputs; or
- a **computer vision method** using a future segmentation model.

The baseline is a required comparison point before relying on a custom model. Any model output must be labeled experimental.

### 4. Raster and vector outputs

Store mask outputs as georeferenced raster files, then convert useful regions into vector polygons for inspection with roads, parcels, facilities, and other overlays. Vector outputs are derived artifacts, not field-verified fire perimeters.

### 5. Geospatial overlay

Overlay derived outputs with public context layers such as AOI boundaries, roads, parcels, facilities, public land, hazard context, vegetation, and reference fire layers. Overlay work supports portfolio interpretation, not official decision-making.

### 6. Exposure-style summary

Generate a concise summary that records run ID, AOI version, source stack, processing date, method, detected or screened area, relevant nearby public layers, warnings, and interpretation limits.

Avoid operational language such as “safe,” “unsafe,” “evacuate,” “official risk,” or “recommended route.”

### 7. Documented run package

Each completed run should produce a folder such as:

```text
/runs/BL-YYYY-MM-DD-deschutes-aoi01-m001-d001/
  run_manifest.json
  prediction_mask.tif
  prediction_polygons.geojson
  exposure_summary.json
  map_export.png
  run_report.md
```

## Primary components

- **Data layer:** inventory, source metadata, manifests, file organization
- **Preprocessing layer:** clipping, tiling, reprojection, normalization, quality checks
- **Model or baseline layer:** experimental mask generation
- **Geospatial conversion layer:** raster-to-vector conversion, polygon cleanup, overlay operations
- **Reporting layer:** maps, summaries, run manifests, limitations notes
- **Website/demo layer:** public presentation through burnlensproject.org

## Versioning requirements

Every output should trace to GitHub commit, app version, dataset version, AOI version, model or baseline version, label schema version where relevant, run ID, and processing timestamp.

No map, summary, screenshot, or portfolio claim should be treated as final unless provenance is recorded.

## Technical limits

BurnLens Deschutes does not claim real-time wildfire detection, official fire perimeter generation, evacuation routing, incident-command support, field-validated performance, agency-reviewed output, parcel-level risk classification, or utility-grade operational readiness.
