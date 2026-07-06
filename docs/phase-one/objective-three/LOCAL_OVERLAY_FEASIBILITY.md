# Phase 1 / Objective Three — Local Overlay Feasibility

Expanded during the Objective Three remediation pass after branch creation and fresh source research.

This document is documentation-only. It does not authorize data acquisition, local data download, preprocessing, AOI selection, public outputs, parcel-level claims, regulatory conclusions, emergency use, or operational use.

## Decision summary

Deschutes County GIS is feasible as the primary local overlay candidate source for later BurnLens planning. Its role is context only: map framing, AOI explanation, non-authoritative exposure-style summaries, and portfolio transparency. It must not be used to make official hazard, parcel, evacuation, access, eligibility, or regulatory determinations.

## Source access facts to preserve

Deschutes County GIS data is provided through the Deschutes County Data Portal, with more than 60 map layers, weekly updates, and downloadable Esri shapefile, KML, and CSV formats. Future work must record the exact portal item, layer name, download date, file format, and coordinate system for every layer used.

## Candidate overlay groups

| Group | Candidate layers | BurnLens role | Priority |
|---|---|---|---|
| Boundary | County boundary, city limits, unincorporated communities, urban growth boundaries | AOI framing and map extent | High |
| Transportation | county routes, road centerlines, state routes, streets maintained by 911, USFS roads | Non-operational proximity/context | Medium |
| Land | taxlots, public land, wildfire hazard zones, zoning | Planning-style context only | High for context, restricted for claims |
| Place | emergency service locations, features of interest, schools | Exposure-style summaries only | Medium, sensitive wording required |
| Environment | slope, soils, vegetation, precipitation, landslide areas | Optional environmental context | Medium |
| Water | streams, rivers, lakes, watershed boundaries, wetlands | Optional map context and AOI explanation | Low to medium |
| PLSS / USGS quad | PLSS lines, section boundaries, township boundaries, USGS quad boundaries | Reference grid and map orientation | Optional |

## Required layer review fields

Every future local overlay layer must be documented before use:

```text
layer_name:
source_authority: Deschutes County GIS
portal_item_or_service_name:
feature_class_group:
geometry_type:
source_format: shapefile | KML | CSV | service | other
source_crs:
working_crs:
units:
download_or_access_date:
update_note:
field_names_used:
field_names_ignored:
allowed_burnlens_role:
forbidden_burnlens_role:
known_limitations:
source_precedence_note:
provenance_record_id:
decision:
```

## CRS policy for local overlays

Deschutes County documents State Plane Oregon South as the coordinate system used by GIS professionals and public GIS data, with Lambert projection, NAD83 datum, and international feet units. The county also documents WGS 1984 Web Mercator Auxiliary Sphere for data portal downloads. Future work must therefore:

1. inspect the CRS of every downloaded layer;
2. record whether the source came from public GIS data or a data portal export;
3. avoid assuming two county layers share a CRS merely because both came from the county;
4. reproject copies into a documented project working CRS only after recording source CRS;
5. preserve original source files unchanged in any future raw-data area;
6. record units before buffering, measuring, or summarizing distance/area.

## Allowed overlay uses

Allowed later, with caveats:

- show AOI boundary context;
- show roads or public lands as general map context;
- summarize approximate intersection or proximity only if clearly labeled experimental;
- support portfolio explanation of why an AOI was chosen;
- support reproducibility and provenance examples.

## Forbidden overlay uses

Not allowed:

- parcel-level risk claims;
- official wildfire hazard determinations;
- evacuation routing;
- emergency service coverage claims;
- legal, zoning, insurance, permitting, or compliance conclusions;
- replacement of county, state, federal, incident, or emergency-management information.

## Priority local layer shortlist

The first future AOI planning pass should consider only a small set of layers:

| Priority | Layer family | Reason |
|---:|---|---|
| 1 | County boundary | Required for project geography and AOI containment. |
| 2 | Wildfire hazard zones | Useful context only; must be clearly non-authoritative in BurnLens outputs. |
| 3 | Public land | Useful for map context and non-parcel AOI explanation. |
| 4 | Road centerlines / county routes / state routes | Useful for non-operational proximity context. |
| 5 | Water features or watershed boundaries | Optional context for map readability. |
| 6 | Schools / emergency service locations | Sensitive; use only if exposure-style summary wording is tightly bounded. |

## Phase One decision

Deschutes County GIS is feasible for local overlay planning. Future use requires layer-level review, CRS inspection, provenance records, and strong source-precedence language.
