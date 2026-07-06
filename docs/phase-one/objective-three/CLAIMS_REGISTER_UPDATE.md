# Phase 1 / Objective Three — Claims Register Update

Created during the Objective Three remediation pass after branch creation and fresh source research.

Documentation only. This register defines what BurnLens may and may not say after Objective Three. It does not authorize public claims, data acquisition, implementation, model work, or operational use.

## Claim classes

| Class | Meaning |
|---|---|
| Allowed | Safe to use in internal planning and later portfolio copy if still true. |
| Conditional | Allowed only with caveats, provenance, and source-precedence language. |
| Forbidden | Do not use. |

## Allowed claims after Objective Three

| Claim ID | Claim | Required qualifier |
|---|---|---|
| CR-001 | BurnLens has identified a feasible candidate data stack for future planning. | Say candidate or planning stack, not completed dataset. |
| CR-002 | Sentinel-2 Level-2A is the preferred primary imagery candidate. | Say candidate; no scenes or AOI selected yet. |
| CR-003 | Landsat Collection 2 Level-2 is a feasible secondary imagery candidate. | Mention SR/ST and QA context when relevant. |
| CR-004 | NASA HLS is a feasible optional harmonized 30 m imagery path. | Say optional; do not imply it replaces native-resolution products. |
| CR-005 | NASA FIRMS is feasible as a bounded active-fire reference/cue source. | Always include not a ground-truth mask. |
| CR-006 | Deschutes County GIS is feasible for local context overlays. | Always say context only and official sources govern. |
| CR-007 | STAC-style metadata is suitable as a provenance pattern. | Say pattern, not source by itself. |
| CR-008 | Objective Three remained documentation-only. | Mention no data acquisition, model work, or public outputs. |

## Conditional claims

| Claim ID | Conditional claim | Conditions before use |
|---|---|---|
| CR-101 | A selected source covers the AOI. | Requires AOI version, source query result, and source record. |
| CR-102 | A scene is usable for future segmentation work. | Requires cloud/quality review, asset review, and CRS/format precheck. |
| CR-103 | FIRMS detections align with a candidate imagery window. | Requires source family, time window, confidence policy, and alignment caveat. |
| CR-104 | A local overlay supports exposure-style summary context. | Requires layer review, source date, CRS, fields used, and context-only wording. |
| CR-105 | A future output is reproducible. | Requires run record, commit SHA, AOI version, dataset version, and source records. |
| CR-106 | A baseline is useful. | Requires baseline definition, reference proxy, limitations, and no ground-truth claim. |

## Forbidden claims

| Claim ID | Forbidden claim | Reason |
|---|---|---|
| CR-201 | BurnLens provides official wildfire information. | Project is experimental and portfolio-oriented. |
| CR-202 | BurnLens detects active fire with operational reliability. | No model or validation exists. |
| CR-203 | BurnLens maps official fire perimeters. | FIRMS and BurnLens outputs are not official perimeter products. |
| CR-204 | FIRMS detections are ground truth labels. | FIRMS is a noisy satellite reference source. |
| CR-205 | Deschutes County GIS layers prove parcel-level wildfire risk. | Local overlays are context only. |
| CR-206 | BurnLens supports evacuation, access, incident command, emergency response, or public safety decisions. | Outside project boundary. |
| CR-207 | BurnLens results are field validated. | Field validation has been explicitly excluded. |
| CR-208 | BurnLens is endorsed by an agency, utility, sponsor, or partner. | No partnership or sponsorship claim exists. |
| CR-209 | The candidate data stack is a finished dataset. | Objective Three only defines feasibility. |
| CR-210 | Any model is accurate, reliable, or deployable. | No training, inference, metric, or validation work exists. |

## Required disclaimer language

Use this language, or a close equivalent, in future public artifacts:

> BurnLens is an experimental portfolio project. It uses public/open geospatial sources to explore computer-vision and mapping workflows. It is not official wildfire information, emergency guidance, evacuation guidance, incident intelligence, field validation, or agency endorsement. Official county, state, federal, fire-service, emergency-management, and incident sources govern.

## Public wording examples

Allowed:

- Candidate source stack for future wildfire-related computer-vision planning.
- Experimental image-to-mask planning workflow.
- Documentation-only source feasibility review.
- Local context overlays for portfolio map explanation.

Avoid:

- operational wildfire detection;
- official hazard map;
- validated burn boundary;
- emergency-ready tool;
- incident intelligence;
- parcel risk score.

## Maintenance rule

Every future public sentence that summarizes data, model output, map output, reliability, accuracy, coverage, or use case should be checked against this register before publication.
