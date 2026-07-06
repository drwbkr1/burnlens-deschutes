# No-Go Source Note Template

## Template status

This is a blank Phase Two intake template. It does not reject any real source until Phase Two review is authorized and completed.

Do not replace placeholders until a candidate AOI, source, access event, CRS precheck, provenance issue, or claim is actually reviewed.

## Purpose

Use this note when BurnLens decides not to use a candidate source, AOI, access path, format, CRS, claim, or output pathway.

A no-go note should make the rejection or deferral transparent so future work does not accidentally reuse an unsuitable source or repeat the same evaluation.

## Boundary warning

Experimental BurnLens no-go record. Not official wildfire information. Not emergency guidance. Official sources govern.

## Identifiers

| Field | Value |
|---|---|
| No-go note ID | `NOGO-YYYY-NNN` |
| Subject type | AOI / source / access / format / CRS / provenance / claim / output / other |
| Related AOI record | `AOI-YYYY-NNN` |
| Related source record | `SRC-YYYY-NNN` |
| Related access log | `ACCESS-YYYY-NNN` |
| Related precheck | `PRECHECK-YYYY-NNN` |
| Related claim | `CLAIM-YYYY-NNN` |
| Related provenance manifest | `MANIFEST-YYYY-NNN` |
| Task issue / PR | `#`, `#` |
| Created date | `YYYY-MM-DD` |
| Status | draft / active / superseded / retired |

## Subject summary

| Field | Value |
|---|---|
| Candidate name | `[placeholder]` |
| Candidate provider or source | `[placeholder]` |
| Candidate URL or path | `[placeholder]` |
| Intended use before no-go | `[placeholder]` |
| Decision | reject / defer / retire |
| Decision date | `YYYY-MM-DD` |
| Reviewer | `[name or handle]` |

## No-go reason categories

Check all that apply:

- [ ] Source is not official or primary enough for intended use.
- [ ] Source conflicts with higher-authority official information.
- [ ] Terms, license, or access restrictions are incompatible.
- [ ] Metadata is missing, insufficient, or contradictory.
- [ ] Spatial extent does not cover the AOI.
- [ ] Temporal extent or update cadence is unsuitable.
- [ ] Format cannot be read or used reproducibly.
- [ ] CRS is missing, ambiguous, or unsuitable.
- [ ] Data quality or resolution is insufficient.
- [ ] Sensitive, restricted, or privacy-related concern exists.
- [ ] Source would create unsupported official, operational, validation, or endorsement claims.
- [ ] Source would imply emergency guidance or incident support.
- [ ] Other: `[describe]`

## Evidence summary

| Evidence | Source/path | What it shows | Notes |
|---|---|---|---|
| `[evidence item]` | `[URL or record path]` | `[support]` | `[note]` |

## Decision rationale

```text
[Short explanation of why the source/path/claim is no-go.]
```

## Impact on project work

| Area | Impact | Follow-up |
|---|---|---|
| AOI selection | none / low / medium / high | `[note]` |
| Source intake | none / low / medium / high | `[note]` |
| Pipeline design | none / low / medium / high | `[note]` |
| Claims/public language | none / low / medium / high | `[note]` |
| Schedule/scope | none / low / medium / high | `[note]` |

## Alternative path

| Field | Value |
|---|---|
| Alternative source or action | `[placeholder]` |
| Required new source record? | yes / no |
| Required new access log? | yes / no |
| Required new precheck? | yes / no |
| Required claim revision? | yes / no |

## Reconsideration rule

This no-go decision may be reconsidered only if:

- new official or primary metadata becomes available;
- license/terms change;
- CRS/format issue is resolved reproducibly;
- a safer source or narrower use case is identified;
- the claim is rewritten to avoid unsupported authority or emergency-use implications.

## Repository hygiene

- [ ] No source data was downloaded because of this no-go decision.
- [ ] No labels, masks, model inputs, outputs, metrics, maps, or demo artifacts were created.
- [ ] No credentials or private access details were recorded.
- [ ] Related source/access/precheck/claim records are linked.
- [ ] The provenance manifest is updated if this decision affects a manifest.

## Handoff

Record the alternative path or state that work should stop for this source/claim until a future task explicitly reopens it.
