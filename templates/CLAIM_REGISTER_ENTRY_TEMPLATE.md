# Claim Register Entry Template

## Template status

This is a blank Phase Two intake template. It does not create a public claim, validate a model, certify a source, or authorize publication.

Do not replace placeholders until Phase Two claim review is authorized.

## Purpose

Use this record to evaluate any statement BurnLens may make about an AOI, source, dataset, precheck, pipeline step, output, limitation, or portfolio result.

A claim is not safe until it is tied to source records, provenance records, verification evidence, and boundary language.

## Boundary warning

Experimental BurnLens claim-control record. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

## Claim identifiers

| Field | Value |
|---|---|
| Claim ID | `CLAIM-YYYY-NNN` |
| Related AOI record | `AOI-YYYY-NNN` |
| Related source record(s) | `SRC-YYYY-NNN` |
| Related access log(s) | `ACCESS-YYYY-NNN` |
| Related precheck(s) | `PRECHECK-YYYY-NNN` |
| Related provenance manifest | `MANIFEST-YYYY-NNN` |
| Related output(s) | `[future output IDs only if authorized]` |
| Task issue / PR | `#`, `#` |
| Created date | `YYYY-MM-DD` |
| Status | draft / supported / unsupported / rejected / retired |

## Claim text

Draft claim:

```text
[Write the exact claim being evaluated.]
```

Claim type:

- [ ] Internal repo-management claim
- [ ] Source or metadata claim
- [ ] AOI scope claim
- [ ] Data fitness claim
- [ ] Pipeline/process claim
- [ ] Output/summary claim
- [ ] Public-facing portfolio claim
- [ ] Limitation or caveat claim

## Source and evidence support

| Evidence type | ID or path | What it supports | Strength | Notes |
|---|---|---|---|---|
| Official source | `[source]` | `[support]` | strong / moderate / weak / none | `[note]` |
| Source record | `SRC-YYYY-NNN` | `[support]` | strong / moderate / weak / none | `[note]` |
| Access log | `ACCESS-YYYY-NNN` | `[support]` | strong / moderate / weak / none | `[note]` |
| Format/CRS precheck | `PRECHECK-YYYY-NNN` | `[support]` | strong / moderate / weak / none | `[note]` |
| Provenance manifest | `MANIFEST-YYYY-NNN` | `[support]` | strong / moderate / weak / none | `[note]` |
| Output record | `[future output]` | `[support]` | strong / moderate / weak / none | `[note]` |

## Source precedence check

| Check | Result | Notes |
|---|---|---|
| Official sources govern. | yes | Non-negotiable. |
| Claim does not override official information. | pending / yes / no | `[note]` |
| Claim does not imply emergency guidance. | pending / yes / no | `[note]` |
| Claim does not imply evacuation, routing, tactical, or incident-command support. | pending / yes / no | `[note]` |
| Claim does not imply agency endorsement. | pending / yes / no | `[note]` |

## Public-language review

| Question | Decision | Notes |
|---|---|---|
| Is the claim internal only? | yes / no | `[note]` |
| Is the claim public-facing? | yes / no | `[note]` |
| Does it need the BurnLens warning? | yes / no | `[note]` |
| Does it use allowed language such as shows, indicates, overlaps, or should be compared? | yes / no | `[note]` |
| Does it avoid words such as safe, unsafe, official, confirmed, evacuate, route, or validated? | yes / no | `[note]` |

## Decision

| Field | Value |
|---|---|
| Claim decision | supported / unsupported / revise / reject / defer |
| Decision date | `YYYY-MM-DD` |
| Reviewer | `[name or handle]` |
| Required caveat | `[warning/caveat text]` |
| Required citation/source link | `[source path or URL]` |
| Publication allowed? | yes / no / internal only |

## Safe wording

If supported, approved wording:

```text
[Approved wording with caveat.]
```

If unsupported, replacement wording:

```text
[Safer wording or no-claim statement.]
```

## Rejection criteria

Reject or defer the claim if:

- it lacks source/provenance support;
- it overstates what BurnLens produced;
- it implies official wildfire information;
- it implies operational reliability, field validation, emergency readiness, or agency endorsement;
- it depends on data that has not passed source/access/format/CRS/provenance checks;
- it omits required caveats.

## Handoff

If accepted, link this entry from the relevant provenance manifest and public-facing artifact. If rejected, create or link a no-go source/claim note where appropriate.
