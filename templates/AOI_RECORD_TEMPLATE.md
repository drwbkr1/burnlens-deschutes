# AOI Record Template

## Template status

This is a blank Phase Two intake template. It does not select, approve, digitize, download, or publish an Area of Interest.

Do not replace placeholders until Phase Two data intake is authorized.

## Purpose

Use this record to document a candidate Area of Interest before any imagery, vector data, labels, masks, model inputs, or run outputs are created.

An AOI record must make the spatial scope explicit, explain why the AOI is being considered, identify official boundary/source references, and record whether the AOI is accepted, deferred, or rejected for data work.

## Boundary warning

Experimental BurnLens planning record. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

## Required identifiers

| Field | Value |
|---|---|
| AOI record ID | `AOI-YYYY-NNN` |
| Phase | Phase Two |
| Related task issue | `#` |
| Parent issue | `#` |
| Branch / PR | `branch`, `#PR` |
| Record author | `[name or handle]` |
| Created date | `YYYY-MM-DD` |
| Last updated | `YYYY-MM-DD` |
| Status | candidate / accepted / deferred / rejected / retired |

## Candidate AOI summary

| Field | Value |
|---|---|
| Candidate AOI name | `[placeholder only]` |
| County / jurisdiction | `[placeholder only]` |
| Intended analysis purpose | `[why this AOI is being considered]` |
| Intended BurnLens phase use | screening / pipeline test / portfolio demonstration / other |
| Official context source consulted | `[official boundary, hazard, land-management, or planning source]` |
| Source precedence note | Official sources govern; BurnLens does not define official AOI boundaries. |

## Spatial definition

Do not enter coordinates until Phase Two authorizes AOI selection.

| Field | Value |
|---|---|
| Geometry type | polygon / bounding box / administrative unit / other |
| Geometry source | `[placeholder]` |
| Coordinate reference system | `[EPSG code, WKT, or source CRS]` |
| CRS authority/source | `[placeholder]` |
| Bounding box | `[xmin, ymin, xmax, ymax]` |
| Geometry file path | `[future path only after authorized creation]` |
| Geometry checksum | `[future checksum if geometry file created]` |
| Spatial precision note | `[limits or uncertainty]` |
| Known exclusions | `[areas intentionally excluded]` |

## Official-source comparison

| Check | Result | Evidence |
|---|---|---|
| Boundary source is official or primary. | pending / yes / no | `[source]` |
| AOI does not override official boundaries. | pending / yes / no | `[note]` |
| AOI does not imply evacuation, hazard, or tactical status. | pending / yes / no | `[note]` |
| AOI is appropriate for portfolio screening use. | pending / yes / no | `[note]` |

## Data-readiness decision

| Decision field | Value |
|---|---|
| Decision | accept / defer / reject |
| Decision date | `YYYY-MM-DD` |
| Decision basis | `[brief rationale]` |
| Required source records before use | `[SOURCE-ID list]` |
| Required access logs before use | `[ACCESS-ID list]` |
| Required CRS precheck before use | `[PRECHECK-ID]` |
| Required provenance manifest before use | `[MANIFEST-ID]` |

## Acceptance criteria

- [ ] AOI purpose is documented.
- [ ] Boundary or geometry source is documented.
- [ ] CRS or CRS uncertainty is documented.
- [ ] Official-source precedence is stated.
- [ ] No selected AOI geometry is created before authorization.
- [ ] No imagery, labels, masks, model inputs, outputs, metrics, or maps are created by this record.
- [ ] Decision is accept, defer, or reject with rationale.

## No-go criteria

Reject or defer the AOI if:

- the boundary source is unofficial or ambiguous and no official comparison is possible;
- the AOI would imply official hazard, evacuation, or emergency-management status;
- the CRS or geometry cannot be checked well enough for later overlay work;
- the AOI would require data use that violates license, terms, access, or project boundaries;
- the AOI cannot support transparent portfolio documentation.

## Claims-register note

Safe claim after this record is completed:

```text
BurnLens has documented a candidate AOI decision record for future Phase Two data intake.
```

Unsupported claims:

```text
The AOI is official, hazard-confirmed, operationally validated, field-verified, or suitable for emergency decisions.
```

## Handoff

If accepted, create or link the required source records, access logs, format/CRS precheck, provenance manifest, and claims entries before any data use.
