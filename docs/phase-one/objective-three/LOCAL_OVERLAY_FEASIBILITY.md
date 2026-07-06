# Phase 1 / Objective Three — Local Overlay Feasibility

Draft created after branch creation and fresh source research.

This document is documentation-only. It does not authorize data acquisition, local data download, preprocessing, AOI selection, public outputs, or operational use.

## Reviewed source family

Deschutes County GIS is the primary local overlay candidate source for Objective Three planning.

## Candidate overlay groups

| Group | Candidate layers | BurnLens role |
|---|---|---|
| Boundary | County boundary, city limits, unincorporated communities, urban growth boundaries | AOI context and map framing. |
| Transportation | county routes, road centerlines, state routes, streets maintained by 911, USFS roads | Future access and proximity context. |
| Land | taxlots, public land, wildfire hazard zones, zoning | Planning-style context only. |
| Place | emergency service locations, features of interest, schools | Exposure-style summary context only. |
| Environment | slope, soils, vegetation, precipitation, landslide areas | Optional context for later planning review. |
| Water | streams, rivers, lakes, watershed boundaries, wetlands | Optional map context. |

## Feasibility findings

- Deschutes County GIS is feasible for future local overlay planning.
- The county portal lists relevant feature classes for roads, taxlots, wildfire hazard zones, public land, emergency service locations, schools, and watershed boundaries.
- CRS handling must be planned before any future use.
- Overlay layers must support context and summaries only; they must not become official determinations.

## Future review fields

```text
Layer name:
Source authority:
Feature class group:
Geometry type:
CRS:
Download or service path:
Update note:
Use role:
Known limitation:
Source precedence note:
Decision:
```

## Boundary

Official sources govern. BurnLens-derived maps and summaries remain experimental portfolio artifacts.
