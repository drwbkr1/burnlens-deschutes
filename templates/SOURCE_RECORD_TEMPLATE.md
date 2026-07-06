# Source Record Template

## Template status

This is a blank Phase Two intake template. It does not approve, download, transform, or use any data source.

Do not replace placeholders until Phase Two source intake is authorized.

## Purpose

Use this record to evaluate a candidate data source before access or use. The record must document source authority, coverage, license/terms, metadata quality, update cadence, format/CRS expectations, and whether the source can be used in BurnLens.

FGDC metadata guidance supports documenting geospatial resources with structured metadata, and STAC collection patterns support recording spatial/temporal extent, license, providers, and collection-level descriptors.

## Boundary warning

Experimental BurnLens source-intake record. Not official wildfire information. Not emergency guidance. Official sources govern.

## Required identifiers

| Field | Value |
|---|---|
| Source record ID | `SRC-YYYY-NNN` |
| Related AOI record | `AOI-YYYY-NNN` |
| Related access log | `ACCESS-YYYY-NNN` |
| Related CRS precheck | `PRECHECK-YYYY-NNN` |
| Phase | Phase Two |
| Task issue / PR | `#`, `#` |
| Created date | `YYYY-MM-DD` |
| Status | candidate / approved-for-access / deferred / rejected / retired |

## Source identity

| Field | Value |
|---|---|
| Source name | `[placeholder]` |
| Provider / steward | `[organization]` |
| Provider type | official government / public research / commercial / community / unknown |
| Source URL | `[URL placeholder]` |
| Landing page URL | `[URL placeholder]` |
| Metadata URL | `[URL placeholder]` |
| API endpoint or catalog URL | `[URL placeholder]` |
| Citation text | `[future citation]` |
| Contact or maintainer | `[name/role/email if public]` |

## Source authority and precedence

| Check | Result | Notes |
|---|---|---|
| Source is official or primary for its topic. | pending / yes / no | `[note]` |
| Source can be compared with higher-authority sources if needed. | pending / yes / no | `[note]` |
| Source does not override official emergency information. | pending / yes / no | Official sources govern. |
| Source is suitable only for experimental BurnLens screening. | pending / yes / no | `[note]` |

## Use rights and access constraints

| Field | Value |
|---|---|
| License / terms | `[placeholder]` |
| Terms reviewed date | `YYYY-MM-DD` |
| Access method | browser / API / bulk download / request form / other |
| Account required? | yes / no / unknown |
| Credentials stored in repo? | no |
| Redistribution allowed? | yes / no / unknown |
| Attribution required? | yes / no / unknown |
| Commercial restriction? | yes / no / unknown |
| Privacy / sensitive-data concern? | yes / no / unknown |
| Access decision | approve / defer / reject |

## Coverage and fitness

| Field | Value |
|---|---|
| Spatial coverage | `[placeholder]` |
| Temporal coverage | `[placeholder]` |
| Update frequency | `[placeholder]` |
| Resolution / scale | `[placeholder]` |
| Data type | raster / vector / tabular / catalog / API / other |
| Format candidates | GeoTIFF / GeoPackage / Shapefile / GeoJSON / STAC / CSV / other |
| CRS or CRS source | `[placeholder]` |
| Known limitations | `[placeholder]` |
| BurnLens intended use | AOI context / imagery candidate / mask support / exposure context / validation comparison / other |

## Metadata quality checklist

| Check | Status | Notes |
|---|---|---|
| Identification metadata found. | pending / yes / no | `[title, description, provider]` |
| Spatial extent found. | pending / yes / no | `[extent]` |
| Temporal extent or date found. | pending / yes / no | `[date]` |
| CRS or spatial reference found. | pending / yes / no | `[CRS]` |
| Data quality or limitations found. | pending / yes / no | `[limitations]` |
| Distribution/access details found. | pending / yes / no | `[download/API]` |
| License/terms found. | pending / yes / no | `[license]` |

## Required downstream records before data use

- [ ] Access log created.
- [ ] Format/CRS precheck completed.
- [ ] Provenance manifest updated.
- [ ] Claim register entry created if this source supports any project claim.
- [ ] No-go note created if source is rejected.

## Acceptance criteria

- [ ] Source identity and provider are documented.
- [ ] Metadata and license/terms are reviewed.
- [ ] CRS/format expectations are recorded or flagged unknown.
- [ ] Access decision is approve, defer, or reject.
- [ ] No data is downloaded by this template.
- [ ] No labels, masks, model inputs, outputs, metrics, maps, or public-demo artifacts are created.

## No-go criteria

Reject or defer if:

- terms prohibit intended use;
- source is not authoritative enough for the intended claim;
- metadata is missing or contradictory;
- CRS/format cannot be checked;
- source access requires storing credentials in the repo;
- source would imply official emergency guidance or operational reliability.

## Handoff

If approved, create an access log before retrieving anything and complete the format/CRS precheck before use in any pipeline step.
