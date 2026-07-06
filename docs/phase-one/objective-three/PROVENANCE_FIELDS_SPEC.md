# Phase 1 / Objective Three — Provenance Fields Spec

Expanded during the Objective Three remediation pass after branch creation and fresh source research.

Documentation only. This specification defines future metadata requirements; it does not create data, run models, or publish outputs.

## Purpose

BurnLens outputs are not portfolio-ready unless they are traceable. This document defines the minimum provenance fields for future source records, AOI records, data selection records, model/baseline runs, and public artifacts.

## Provenance principles

1. Record source metadata before processing.
2. Preserve original source IDs and dates.
3. Record every transformation from source to output.
4. Tie outputs to Git commit, app/repo version, AOI version, dataset version, and run ID.
5. Keep official source metadata separate from BurnLens-derived metadata.
6. Make uncertainty and limits visible.
7. Do not publish a map, screenshot, summary, metric, or claim without a provenance record.

## STAC-aligned source metadata

STAC Items are GeoJSON Features with required fields such as type, STAC version, ID, geometry, bbox, properties, links, and assets. BurnLens should not require full STAC compliance for every source, but future source records should map as closely as practical to the same ideas.

| STAC-aligned concept | BurnLens field | Required? | Notes |
|---|---|---:|---|
| Item ID | source_item_id | Yes | Provider product ID, scene ID, item ID, or layer ID. |
| Collection | source_collection | Yes when available | Example: Sentinel-2 Level-2A collection or HLS product family. |
| Geometry | source_geometry | Yes when available | Store WGS 84 geometry or link to source footprint. |
| BBox | source_bbox_wgs84 | Yes | Minimum future spatial index field. |
| Datetime | source_datetime_utc | Yes when temporal | Use UTC. If interval-based, record start and end. |
| Links | source_links | Yes | Official landing page, collection page, item page, or service path. |
| Assets | source_assets | Yes for imagery | Band files, QA files, metadata sidecars, thumbnails if used. |
| Properties | source_properties_used | Yes | Record only fields used for decisions. |

## Required BurnLens source record

```yaml
record_type: source_record
record_id:
source_name:
source_authority:
source_family:
source_collection:
source_item_id:
source_version:
source_landing_page:
source_access_path:
access_date_utc:
source_datetime_utc:
source_start_datetime_utc:
source_end_datetime_utc:
source_geometry:
source_bbox_wgs84:
source_crs:
source_units:
source_resolution:
source_format:
source_assets:
source_quality_fields:
source_citation:
known_limitations:
allowed_burnlens_role:
forbidden_burnlens_role:
source_precedence_note:
review_status:
```

## Required AOI record

```yaml
record_type: aoi_record
aoi_id:
aoi_version:
aoi_name:
aoi_geometry_wgs84:
aoi_bbox_wgs84:
aoi_area_method:
aoi_area_value:
created_date_utc:
created_by:
reason_for_selection:
source_overlap_checks:
local_overlay_checks:
known_sensitive_features:
allowed_use:
forbidden_use:
change_log:
```

## Required future run record

```yaml
record_type: run_record
run_id:
run_datetime_utc:
git_commit:
repo_version:
app_version:
aoi_version:
dataset_version:
source_record_ids:
model_or_baseline_id:
label_schema_version:
input_assets:
processing_steps:
parameters:
random_seed:
output_assets:
metrics_record_id:
limitations:
review_status:
```

## Required future public artifact record

```yaml
record_type: public_artifact_record
artifact_id:
artifact_type: map | screenshot | report | figure | demo | metric | claim
artifact_title:
created_datetime_utc:
git_commit:
repo_version:
run_id:
aoi_version:
dataset_version:
source_record_ids:
claim_ids:
required_disclaimer:
source_precedence_note:
review_status:
```

## Naming conventions

Use stable IDs.

```text
source-<family>-<date-or-id>
aoi-<name>_vYYYYMMDD
dataset-<aoi>-<source-stack>_vYYYYMMDD
run-YYYYMMDD-HHMM-<short-purpose>
artifact-<type>-YYYYMMDD-<short-purpose>
claim-YYYYMMDD-<number>
```

## Minimum public-output rule

No public BurnLens output may be called portfolio-ready unless it records:

- git commit;
- repo or app version;
- AOI version;
- dataset version;
- source IDs;
- source dates;
- access dates;
- model or baseline version;
- label schema version when labels exist;
- run ID;
- output timestamp;
- limitations/disclaimer.

## Review states

| State | Meaning |
|---|---|
| draft | Record exists but is incomplete. |
| reviewed | Required fields are filled and internally consistent. |
| superseded | Record has been replaced by a newer version. |
| rejected | Source/run/artifact is not acceptable for the intended role. |

## Phase One decision

The provenance model is feasible. Future Phase Two work must instantiate these records before data is processed or outputs are published.
