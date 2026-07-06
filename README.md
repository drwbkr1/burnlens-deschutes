# BurnLens Deschutes

BurnLens Deschutes is a computer vision + GEOINT portfolio project focused on experimental wildfire-related screening in Deschutes County, Oregon.

The project demonstrates a reproducible workflow for turning wildfire-relevant imagery, public geospatial layers, and experimental segmentation or baseline outputs into traceable map-ready artifacts.

## Core workflow

```text
imagery → preprocessing → segmentation or baseline mask → raster output → vector polygons → map overlay → exposure-style summary → documented run package
```

## Current status

This repository is in **Phase 1 / Objective One**: project identity, scope, audience, technical description, use boundaries, source precedence, and transparency requirements.

No model training, data ingestion, or operational wildfire product has been started in this objective.

## Use boundary

BurnLens Deschutes is an experimental portfolio project. It is not emergency guidance, not official wildfire information, not an evacuation-order tool, not an incident-command product, and not a field-validated hazard system. Official county, state, federal, fire-service, and emergency-management sources govern when information differs.

## Repository structure

```text
docs/objective-one/    Phase 1 / Objective One scope and trust documents
templates/             Reusable documentation templates
```

## Public site

The public website lives separately at `burnlensproject.org` and is backed by the `burnlens-site` repository.
