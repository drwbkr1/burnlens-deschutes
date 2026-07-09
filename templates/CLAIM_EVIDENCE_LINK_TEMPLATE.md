# Claim Evidence Link Template

## Template status

This is a blank reusable template.

It is not a completed claim record, not a public approval, not a release-control decision, not a source record, not a run record, not a model record, not a map/output record, and not evidence that any public-facing claim is approved.

## Required warning

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

## Claim identity

| Field | Value |
|---|---|
| Claim ID | `CLAIM-YYYY-NNN` |
| Claim title | `[short title]` |
| Claim owner/reviewer | `[person or role]` |
| Date drafted | `YYYY-MM-DD` |
| Date reviewed | `YYYY-MM-DD | pending` |
| Public surface | `README | website | report | slide | screenshot | release note | portfolio copy | other` |
| Related issue/PR | `#[issue] / #[PR]` |
| Related commit SHA | `[commit SHA or pending]` |

## Exact claim text

```text
[Paste the exact public-facing claim text here.]
```

## Claim classification

| Field | Value |
|---|---|
| Claim type | `scope | source | data-readiness | model | map-output | portfolio | mixed` |
| Claim strength level | `level-0-planned | level-1-documented | level-2-recorded | level-3-generated | level-4-reviewed-public | never-allowed` |
| Origin class | `official-reference | reference-derived | third-party-reference | burnlens-control | burnlens-derived-output | public-portfolio-asset | mixed` |
| Public-use status | `internal-only | public-blocked | public-eligible-after-review | public-used` |
| Release-control status | `not-reviewed | blocked | eligible | included | excluded` |

## Evidence checklist by claim type

Use the rows that match the claim type. Mark unrelated rows `not applicable`.

| Claim type | Required evidence | Evidence path / ID | Status |
|---|---|---|---|
| Scope claim | README | `README.md` | `complete | partial | missing | not applicable` |
| Scope claim | Technical description | `docs/objective-one/TECHNICAL_DESCRIPTION.md` | `complete | partial | missing | not applicable` |
| Scope claim | Use boundaries | `docs/objective-one/USE_BOUNDARIES.md` | `complete | partial | missing | not applicable` |
| Source claim | Source record | `SRC-YYYY-NNN` | `complete | partial | missing | not applicable` |
| Source claim | Access log | `ACCESS-YYYY-NNN` | `complete | partial | missing | not applicable` |
| Source claim | License/terms note | `[path or ID]` | `complete | partial | missing | not applicable` |
| Data-readiness claim | AOI record | `AOI-YYYY-NNN` | `complete | partial | missing | not applicable` |
| Data-readiness claim | Source/access records | `[source/access IDs]` | `complete | partial | missing | not applicable` |
| Data-readiness claim | Format/CRS precheck | `PRECHECK-YYYY-NNN` | `complete | partial | missing | not applicable` |
| Data-readiness claim | Provenance record | `MANIFEST-YYYY-NNN | TRACE-YYYY-NNN` | `complete | partial | missing | not applicable` |
| Model claim | Model card | `[path or ID]` | `complete | partial | missing | not applicable` |
| Model claim | Metrics record | `[path or ID]` | `complete | partial | missing | not applicable` |
| Model claim | Dataset version | `[dataset version]` | `complete | partial | missing | not applicable` |
| Model claim | Label version | `[label version]` | `complete | partial | missing | not applicable` |
| Map/output claim | Run ID | `BL-YYYY-MM-DD-deschutes-aoiXX-mXXX-dXXX` | `complete | partial | missing | not applicable` |
| Map/output claim | Run manifest | `runs/[run-id]/run_manifest.json` | `complete | partial | missing | not applicable` |
| Map/output claim | Output inventory | `runs/[run-id]/output_inventory.md` | `complete | partial | missing | not applicable` |
| Map/output claim | Source-precedence note | `[path or ID]` | `complete | partial | missing | not applicable` |
| Portfolio claim | Claim-register entry | `CLAIM-YYYY-NNN` | `complete | partial | missing | not applicable` |
| Portfolio claim | Limitation statement | `[text or path]` | `complete | partial | missing | not applicable` |
| Portfolio claim | Registry entries | `[registry IDs]` | `complete | partial | missing | not applicable` |
| Portfolio claim | Release-control decision | `[path or ID]` | `complete | partial | missing | not applicable` |

## Source-precedence review

| Field | Value |
|---|---|
| Source-precedence status | `official-source-record | official-source-compared | burnlens-derived-experimental | conflict-with-official-source | source-precedence-unresolved | not-applicable-documentation-only` |
| Official/reference source linked? | `yes | no | not applicable` |
| BurnLens-derived output involved? | `yes | no` |
| Official/reference and BurnLens-derived categories kept separate? | `yes | no | not applicable` |
| Official-source conflict present? | `yes | no | unknown` |
| If conflict present, public use decision | `blocked | revised with explicit conflict note | not applicable` |

## Fire, evacuation, hazard, and road context check

| Question | Answer |
|---|---|
| Does the claim mention fire, wildfire, hotspot, burn scar, smoke, hazard, evacuation, road, routing, closure, emergency, incident, perimeter, structure exposure, or public-safety context? | `yes | no` |
| If yes, is source-precedence language included? | `yes | no | not applicable` |
| If yes, is the required BurnLens warning included or linked? | `yes | no | not applicable` |
| If yes, does the wording avoid evacuation, routing, tactical, road-closure, and incident-command guidance? | `yes | no | not applicable` |
| If any answer blocks public use, decision | `revise | blocked | not applicable` |

## Forbidden-claim check

A claim is blocked if any row is marked `yes`.

| Forbidden implication | Present? | Notes |
|---|---|---|
| Official status | `yes | no` |  |
| Operational status | `yes | no` |  |
| Emergency-ready status | `yes | no` |  |
| Agency endorsement | `yes | no` |  |
| Field validation | `yes | no` |  |
| Evacuation guidance | `yes | no` |  |
| Routing guidance | `yes | no` |  |
| Road-closure guidance or authority | `yes | no` |  |
| Tactical fire intelligence | `yes | no` |  |
| Incident-command support | `yes | no` |  |
| Substitute for official sources | `yes | no` |  |

## Limitation statement

```text
[Insert the limitation statement required for this claim.]
```

Minimum limitation when BurnLens-derived output is involved:

```text
Experimental BurnLens output. Official sources govern.
```

Preferred full limitation when space allows:

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

## Evidence decision

| Field | Value |
|---|---|
| Evidence complete? | `yes | no | partial` |
| Claim matches evidence strength? | `yes | no` |
| Required warning present? | `yes | no | not applicable` |
| Required limitation present? | `yes | no` |
| Release-control review complete? | `yes | no | not applicable` |
| Final decision | `approved | revise | blocked | internal-only | archive` |
| Reviewer notes | `[notes]` |

## Safer rewrite if needed

Original claim:

```text
[Original claim text]
```

Revised claim:

```text
[Safer wording that matches the evidence]
```

## Handoff

| Field | Value |
|---|---|
| Next action | `approve | revise | gather evidence | add source-precedence note | add limitation | release-control review | archive` |
| Owner | `[person or role]` |
| Blocking issue(s) | `#[issue] | none` |
| Follow-up PR | `#[PR] | pending | none` |
