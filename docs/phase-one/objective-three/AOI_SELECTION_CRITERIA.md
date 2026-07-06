# Phase 1 / Objective Three — AOI Selection Criteria

Expanded during the Objective Three remediation pass after branch creation and fresh source research.

Documentation only. No final area of interest is selected here.

## Purpose

This document defines how future BurnLens Deschutes AOI candidates should be evaluated before any imagery, labels, baselines, model inputs, map layers, or public outputs are created. The AOI must be small enough for a one-person portfolio build and large enough to demonstrate the full imagery-to-mask-to-map workflow.

## AOI decision principles

A future AOI must:

1. be inside Deschutes County;
2. be covered by candidate imagery sources;
3. have at least one relevant local overlay source;
4. fit the locked binary segmentation workflow;
5. avoid operational wildfire claims;
6. be reproducible and versionable;
7. support transparent limitations;
8. be explainable in a portfolio case study.

## Preferred AOI size guidance

The first production AOI should be conservative.

| Candidate size | Recommended use | Notes |
|---|---|---|
| Small test AOI | Early pipeline proof | Good for confirming raster/vector handling and provenance. |
| Medium portfolio AOI | Preferred first public demonstration scale | Large enough for map context, small enough for manual review. |
| Large county-scale AOI | Defer | Too broad for first build and may invite overclaiming. |

Do not finalize numeric area limits until Phase Two tooling confirms available imagery tile sizes, processing cost, and map performance. The first implementation should favor a bounded area that can be manually inspected.

## Candidate AOI types

| AOI type | Feasibility | Why it might be useful | Main risk |
|---|---|---|---|
| County-contained landscape sample | High | Demonstrates imagery and overlay workflow without parcel-level claims. | May feel abstract if not tied to a visible context. |
| Wildland/community interface style sample | Medium | Portfolio-relevant for wildfire screening. | Must avoid official hazard or evacuation language. |
| Public land / road context sample | Medium | Easy to explain with local overlays. | Road context must not imply access or evacuation advice. |
| Historic fire-adjacent sample | Medium | May align with active-fire or burn-scar source review. | Needs careful date/source handling. |
| Parcel-heavy residential sample | Low for first build | Could be visually compelling. | High risk of parcel-level or individual-property claims. |

## Required AOI candidate record

Every future AOI candidate must be recorded before selection:

```text
candidate_name:
aoi_version_family:
proposal_date:
proposed_by:
geometry_type:
bounding_box_wgs84:
approximate_area:
county_containment_check:
reason_for_consideration:
source_imagery_overlap:
source_reference_overlap:
local_overlay_overlap:
known_sensitive_features:
expected_workflow_fit:
expected_limitations:
source_precedence_note:
allowed_use:
forbidden_use:
decision: accept | defer | reject
review_notes:
```

## Required tile-selection fields

When a future AOI is used to search imagery, record:

```text
aoi_version:
imagery_source_family:
collection_or_product:
tile_or_scene_id:
path_row_or_mgrs_tile:
observation_datetime:
cloud_or_quality_filter:
source_crs:
working_crs:
asset_ids:
selected_bands:
reason_selected:
reason_rejected_if_not_selected:
```

## AOI acceptance gate

An AOI can advance only if all are true:

- it is fully inside the intended project geography;
- it has at least one feasible imagery source;
- it has at least one feasible reference or context source;
- local overlays can be used without parcel-level or operational claims;
- expected outputs can be labeled experimental;
- provenance fields can be recorded;
- official-source precedence can be explained clearly;
- the AOI can be reviewed manually by the builder.

## Defer or reject triggers

Defer or reject an AOI if:

- it depends on emergency-response interpretation;
- it centers individual homes or parcels in a way that invites risk claims;
- imagery quality is likely poor across the selected period;
- local context layers are unavailable or too sensitive;
- the AOI is too large to inspect;
- CRS or geometry handling is unclear;
- the source date cannot be aligned with reference products;
- the AOI cannot be versioned.

## Naming and versioning convention

Use this pattern for future AOI versions:

```text
aoi-descriptive-name_vYYYYMMDD
```

Example placeholder:

```text
aoi-deschutes-test-landscape_v20260706
```

Each AOI version must have a frozen geometry, source note, author/date, and changelog entry. If the geometry changes, create a new AOI version instead of silently replacing the old one.

## Phase One decision

Objective Three does not select an AOI. It defines the acceptance gate and metadata template required before future AOI selection.
