# Phase 1 / Objective Three — Data Feasibility Criteria

Expanded during the Objective Three remediation pass after branch creation and fresh source research.

This document is documentation-only. It defines how candidate source families will be judged before any future data acquisition, download, preprocessing, labeling, model work, public map, or portfolio output.

## Purpose

Objective Three exists to determine whether the source stack needed by the locked BurnLens computer-vision task is feasible enough to support later planning. A source is not approved for use merely because it appears in this document. A source advances only when it satisfies the criteria below and remains compatible with Objective Two boundaries.

## Feasibility scoring

Use a 0-2 score for each criterion.

| Score | Meaning |
|---:|---|
| 0 | Not acceptable for the intended BurnLens role. |
| 1 | Potentially acceptable, but requires caveats, fallback, or additional review. |
| 2 | Acceptable for future planning with documented limits. |

A source may advance to Phase Two planning only if all required criteria score at least 1 and the total score is 20 or higher out of 30. A source that fails source authority, source-precedence compatibility, or provenance readiness cannot advance even if other scores are strong.

## Required criteria

| Criterion | Requirement | Pass condition | Fail condition |
|---|---|---|---|
| Source authority | Source must come from a public, official, or well-documented open-data authority. | Source authority is identifiable and citeable. | Source is informal, untraceable, or not allowed for open portfolio use. |
| Access path reproducibility | Future user can repeat discovery without private handoffs. | Endpoint, portal, catalog, collection, or documented workflow exists. | Access depends on undocumented manual steps or non-public files. |
| Spatial resolution | Resolution must support the intended role. | Imagery/reference/overlay scale is recorded and fit for planning. | Scale is unknown or too coarse for the proposed role. |
| Temporal resolution and latency | Acquisition date, update cadence, and latency must be known. | Source has clear date fields or update notes. | Source timing is unclear or misleading. |
| Deschutes County coverage | Source must cover the project geography or relevant local context. | Coverage intersects Deschutes County or is a county source. | Coverage cannot be confirmed. |
| Band or layer suitability | Source must contain bands/layers needed for its role. | Relevant bands/layers are named. | Source lacks usable bands/layers or they are unclear. |
| Quality and uncertainty handling | Quality, cloud, confidence, or caveat fields must be recordable. | Known quality fields or caveats are documented. | Quality cannot be inspected or explained. |
| Segmentation suitability | Imagery source must be plausible for the locked image-to-mask workflow. | Source can feed future raster preprocessing and mask generation. | Source is only a point/table product or unsuitable for raster model input. |
| Reference suitability | Reference source must support comparison or weak-label work without pretending to be truth. | Reference role and limitations are explicit. | Source would invite pixel-perfect or operational claims. |
| Baseline suitability | Source can support a simple non-model baseline or comparison. | Baseline role is bounded and explainable. | Baseline would be misleading or unverifiable. |
| Overlay suitability | Vector/context source can support map context only. | Context layer role is explicit and non-authoritative. | Layer would be used as a regulatory or emergency determination. |
| Format and CRS compatibility | Format, geometry, CRS, units, and reprojection needs can be recorded. | Data can be converted into a known future workflow. | CRS/format assumptions are unknown. |
| Citation and attribution | Source has a citation, DOI, agency page, or attribution note. | Citation note is recordable in provenance. | Citation cannot be determined. |
| Source-precedence compatibility | Official sources govern all interpretation. | BurnLens output remains experimental and subordinate. | Source use would imply official authority or override official information. |
| Provenance readiness | Source supports product IDs, source dates, access dates, extents, and versioning. | Required metadata can be captured in future run records. | Future run cannot be traced. |

## Source-family scoring summary

| Source family | Intended role | Initial score | Decision |
|---|---|---:|---|
| Sentinel-2 Level-2A through Copernicus Data Space STAC | Primary multispectral imagery candidate | 27/30 | Advance to future planning as primary imagery candidate. |
| Landsat Collection 2 Level-2 | Secondary imagery and thermal/context candidate | 26/30 | Advance to future planning as secondary imagery candidate. |
| NASA HLS L30/S30 | Harmonized 30 m surface-reflectance candidate | 24/30 | Keep as optional simplification layer when temporal consistency matters. |
| NASA FIRMS MODIS/VIIRS | Active-fire reference, sampling, weak-label support, comparison | 20/30 | Advance only as reference/cue source with strong caveats. |
| NASA FIRMS Landsat active fire | Higher-resolution active-fire reference candidate where available | 21/30 | Keep as optional reference source; do not treat as mask truth. |
| Deschutes County GIS | Local overlay and AOI context | 24/30 | Advance for context layers only. |
| STAC Item pattern | Metadata/provenance pattern | 25/30 | Use as provenance and discovery pattern, not as a standalone dataset. |

## Mandatory future source review record

Every source promoted beyond Objective Three must receive a source review record with these fields:

```text
source_family:
source_authority:
official_reference:
candidate_role:
access_path:
collection_or_product_id:
account_or_key_requirement:
spatial_extent:
spatial_resolution:
temporal_extent:
temporal_resolution_or_latency:
format:
crs_or_coordinate_reference:
key_bands_or_layers:
quality_fields_or_caveats:
known_limitations:
allowed_burnlens_use:
forbidden_burnlens_use:
provenance_fields_available:
score_summary:
decision:
review_date:
reviewer:
```

## Phase One decision

The candidate source stack is feasible enough for the next Phase One objective. The decision does not authorize data acquisition or implementation. Future work must still select an AOI, choose dates, record provenance, and run source-specific validation before data is used.
