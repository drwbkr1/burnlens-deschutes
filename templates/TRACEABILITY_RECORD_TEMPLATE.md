# BurnLens Traceability Record Template

## Template status

This is a blank traceability template. It does not approve, access, download, inspect, transform, label, mask, process, model, map, publish, or release any data or output.

Do not replace placeholders until the relevant task authorizes the record.

## Boundary warning

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

A traceability record proves lineage and evidence linkage only. It does not imply operational readiness, official status, field validation, emergency readiness, agency endorsement, production stability, or suitability for evacuation, routing, tactical, or incident-command use.

## Record identity

| Field | Value |
|---|---|
| Traceability record ID | `TRACE-YYYY-NNN` |
| Record status | template / planned / active / complete / superseded / rejected |
| Phase / objective | `[phase/objective]` |
| Parent issue | `#` |
| Task issue | `#` |
| Pull request | `#` |
| Commit SHA | `[commit]` |
| Created date UTC | `YYYY-MM-DDTHH:MM:SSZ` |
| Updated date UTC | `YYYY-MM-DDTHH:MM:SSZ` |
| Created by | `[person / prompt assistant / tool]` |
| Reviewer | `[person / handle]` |

## PROV-style summary

| PROV concept | BurnLens value |
|---|---|
| Primary entity | `[entity ID/path]` |
| Primary activity | `[activity ID]` |
| Primary agent/tool | `[agent/tool/version]` |
| Used entities | `[IDs/paths]` |
| Generated entities | `[IDs/paths]` |
| Derived-from entities | `[IDs/paths]` |
| Attributed-to agent | `[agent]` |
| Associated-with agent/tool | `[agent/tool]` |

## Source-to-claim chain

Complete every applicable row. Use `not applicable`, `not created`, or `not authorized` rather than leaving required fields blank.

| Chain stage | Entity/activity ID | Path or reference | Status | Notes |
|---|---|---|---|---|
| Source candidate | `SRC-YYYY-NNN` | `records/phase-two/sources/...` | planned / complete / not applicable |  |
| Access record | `ACCESS-YYYY-NNN` | `records/phase-two/access/...` | planned / complete / not authorized |  |
| Format/CRS precheck | `PRECHECK-YYYY-NNN` | `records/phase-two/prechecks/...` | planned / complete / not authorized |  |
| Provenance manifest | `MANIFEST-YYYY-NNN` | `records/phase-two/manifests/...` | planned / complete / not authorized |  |
| Processing step | `STEP-YYYY-NNN` | `[future path]` | not authorized / planned / complete |  |
| Method version | `[method version]` | `[method record/config]` | not applicable / planned / complete |  |
| Output artifact | `OUTPUT-YYYY-NNN` | `[future path]` | not created / planned / complete |  |
| Run report | `[run ID / report version]` | `[future report path]` | not created / planned / complete |  |
| Claim-register entry | `CLAIM-YYYY-NNN` | `records/phase-two/claims/...` | draft / supported / rejected / not applicable |  |
| Public-facing claim | `[claim text/path]` | `[site/report/card path]` | blocked / internal only / approved |  |

## Required field block

| Field | Value |
|---|---|
| Entity ID | `[entity ID]` |
| Activity ID | `[activity ID or not applicable]` |
| Agent/tool | `[person/org/software/prompt assistant/tool/version]` |
| Source record | `SRC-YYYY-NNN / not applicable` |
| Access method | `browser / API / CLI / bulk download / manual request / none / not authorized` |
| Processing timestamp | `YYYY-MM-DDTHH:MM:SSZ / not processed` |
| Commit SHA | `[commit]` |
| Method version | `[method/model/baseline/report version or not applicable]` |
| Output file path | `[path / not created]` |
| Checksum plan | `sha256 after authorized file creation/download / not applicable` |
| Warnings | `[required BurnLens warning and stage-specific caveats]` |
| Source-precedence status | `official-source-record / official-source-compared / burnlens-derived-experimental / conflict-with-official-source / source-precedence-unresolved / not-applicable-documentation-only` |

## Agents and tools

| Agent/tool | Type | Version / identifier | Role | Notes |
|---|---|---|---|---|
| `[person/org/tool/model]` | person / organization / software / model / prompt assistant / service | `[version]` | source evaluation / access / precheck / processing / review / publication |  |

## Activities

| Activity ID | Activity type | Start time UTC | End time UTC | Used entities | Generated entities | Agent/tool |
|---|---|---|---|---|---|---|
| `ACT-YYYY-NNN` | source review / access / precheck / processing / report generation / claim review / publication |  |  |  |  |  |

## Entities

| Entity ID | Entity type | Path / reference | Version / identifier | Checksum | Status |
|---|---|---|---|---|---|
| `SRC-YYYY-NNN` | source record |  |  | not applicable | candidate / approved / rejected |
| `FILE-YYYY-NNN` | source file |  |  | sha256 pending / not authorized | not created / complete |
| `OUTPUT-YYYY-NNN` | output artifact |  |  | sha256 pending / not created | not created / complete |
| `CLAIM-YYYY-NNN` | claim-register entry |  |  | not applicable | draft / supported / rejected |

## Source-precedence review

| Check | Result | Notes |
|---|---|---|
| Official sources govern. | yes | Non-negotiable. |
| Source authority is documented. | pending / yes / no / not applicable |  |
| Conflict with official source? | unknown / no / yes / not applicable |  |
| Public wording avoids official/emergency implication. | pending / yes / no / not applicable |  |
| Required warning included. | pending / yes / no |  |
| Source-precedence status selected. | pending / yes / no |  |

## Checksum plan

| Item | Algorithm | When checksum is recorded | Where checksum is recorded | Status |
|---|---|---|---|---|
| Source file | sha256 | after authorized access/download | access log + provenance manifest | not authorized / pending / complete |
| Derived output | sha256 | after authorized processing output creation | provenance manifest + run package | not created / pending / complete |
| Report/package artifact | sha256 | after report/package creation if packaged | run report / release note | not created / pending / complete |

## Warning and limitation text

Required warning:

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

Additional limitations:

```text
[Add source, data, method, output, report, or claim-specific limitations here.]
```

## Claim gate

| Question | Answer | Evidence |
|---|---|---|
| Which entity/output does the claim refer to? |  |  |
| Which source record supports it? |  |  |
| Which access/precheck records support data usability? |  |  |
| Which method version or processing step produced the output? |  |  |
| Which commit contains the record/output/report? |  |  |
| Which run report or release note includes it? |  |  |
| Which claim-register entry approved it? |  |  |
| What warning/source-precedence language must accompany it? |  |  |
| What excluded work prevents stronger wording? |  |  |
| Has release control approved publication? |  |  |

## Decision

| Field | Value |
|---|---|
| Traceability decision | complete / incomplete / blocked / rejected / superseded |
| Public-facing claim allowed? | no / internal only / yes with warning |
| Required follow-up | `[task/issue/path]` |
| No-go note required? | yes / no |
| Supersedes traceability record | `TRACE-YYYY-NNN / none` |

## Handoff

If complete, link this record from the relevant provenance manifest, claim-register entry, run report, release note, or public-facing artifact.

If incomplete or blocked, create or link a no-go note and do not publish the claim.
