# Phase 1 / Objective Three — Active Fire Reference Review

Expanded during the Objective Three remediation pass after branch creation and fresh source research.

Documentation only. No data use, download, implementation, public safety guidance, or operational interpretation is authorized.

## Decision summary

NASA FIRMS remains feasible as a future active-fire reference family for reference display, sampling support, weak-label exploration, and baseline comparison. FIRMS is not feasible as a standalone pixel-perfect mask source and must never be represented as ground truth fire extent.

## Candidate roles

| Role | Status | Required caveat |
|---|---|---|
| Reference display | Allowed later with caveats | Displayed points or pixels are satellite detections at observation time, not official perimeters. |
| Weak-label support | Allowed later with caveats | Can cue candidate positive regions, but must be buffered, filtered, inspected, and treated as noisy. |
| Sampling support | Allowed later with caveats | Can help choose candidate scenes/dates, not final labels. |
| Baseline comparison | Allowed later with caveats | Baseline must compare against a defined proxy, not truth. |
| Pixel-perfect mask | Not allowed | FIRMS pixel/point detections are not semantic segmentation masks. |
| Public safety guidance | Not allowed | BurnLens does not provide emergency, evacuation, incident, or operational fire guidance. |

## FIRMS source family comparison

| Source family | Approximate role | Strength | Limitation | BurnLens decision |
|---|---|---|---|---|
| MODIS active fire | Broad active-fire reference | Long historical record and frequent global coverage | Coarser thermal-band resolution; not aligned to fire perimeter boundaries | Keep for coarse reference and historical context. |
| VIIRS active fire | Primary hotspot reference candidate | Finer thermal-band resolution than MODIS and frequent coverage | Still detects thermal anomalies at overpass time; confidence semantics require care | Keep as leading FIRMS reference candidate. |
| Landsat active fire | Higher-resolution active-fire candidate where available | More spatially explicit active-fire detections | Less frequent revisit; product availability and fields must be checked | Keep as optional reference source. |
| NIFS / official incident perimeter layers | Official incident context if used later | More authoritative for incident perimeters | Update frequency and incident-team inputs vary | Official perimeter data would govern BurnLens interpretation if introduced later. |

## Required field handling

Future FIRMS-derived records must capture:

```text
firms_source_family: MODIS | VIIRS | Landsat
platform_or_satellite:
product_mode: URT | RT | NRT | archive
acquisition_datetime_utc:
latitude:
longitude:
spatial_resolution_or_pixel_size:
confidence:
brightness_or_frp_fields_if_available:
day_night:
version:
access_date:
known_latency:
known_limitations:
allowed_role:
forbidden_role:
```

For Landsat active-fire data, also capture:

```text
path:
row:
track:
scan:
acquire_time:
confidence_domain: H | M | L
version:
```

## Confidence policy

Confidence fields are useful but cannot be treated as probability of truth. The future policy is:

1. Record the raw confidence field exactly as provided.
2. Record the sensor family before interpreting confidence.
3. Do not compare MODIS numeric confidence directly with VIIRS low/nominal/high confidence without a documented translation rule.
4. Do not select a confidence threshold until the AOI, date range, and target label strategy are known.
5. For any future weak-label experiment, report at least two sensitivity settings: a conservative setting and an inclusive setting.
6. Never count low-confidence detections as background by default; mark them as uncertain or excluded until reviewed.

## Alignment and labeling caveats

FIRMS detections must be treated as noisy observations because:

- detections are tied to satellite overpass time;
- clouds, smoke, atmospheric conditions, and view geometry can create omissions;
- thermal pixels may overrepresent or underrepresent actual active fire extent;
- cumulative detections do not equal a fire perimeter;
- MODIS, VIIRS, and Landsat have different resolution, revisit, and algorithm behavior;
- a point or pixel center is not a polygon boundary.

## Allowed future weak-label strategy

A future weak-label experiment may use FIRMS only if it follows this pattern:

1. Select candidate imagery date range first.
2. Pull same-window active-fire detections second.
3. Split detections by source family.
4. Apply documented confidence policy.
5. Convert detections into candidate review zones, not final labels.
6. Mark nearby ambiguous pixels as unknown or review-needed.
7. Compare model outputs to FIRMS only as a proxy reference, not as truth.
8. Report this limitation in any public portfolio artifact.

## Rejection triggers

Do not use FIRMS-derived records if:

- acquisition time is missing;
- source family is unclear;
- confidence field cannot be interpreted;
- spatial resolution cannot be stated;
- product latency or mode is unknown;
- the planned use would imply official fire location, perimeter, evacuation, or incident status.

## Phase One decision

FIRMS remains feasible as a future reference, weak-label, sampling, baseline, and comparison source. It is not feasible as a standalone mask source. Future work must preserve this distinction in labels, code comments, maps, model cards, and portfolio text.
