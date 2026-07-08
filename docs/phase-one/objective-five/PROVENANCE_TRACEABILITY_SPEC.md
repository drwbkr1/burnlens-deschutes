# Provenance Traceability Spec

## Purpose

This document defines how BurnLens Deschutes will prove lineage from source to processing to output to claim.

It creates a lightweight BurnLens provenance model that maps W3C PROV concepts to the existing BurnLens repo workflow, Phase Two intake templates, versioning rules, release-control gates, and source-precedence boundaries.

This spec is documentation and records work only. It does not create, approve, access, download, inspect, transform, label, mask, process, model, map, publish, or release any data or output.

## Boundary statement

Experimental BurnLens CV/GEOINT portfolio work. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

A provenance record proves that BurnLens can trace a statement or artifact back to documented records. It does **not** prove operational readiness, official status, field validation, emergency readiness, agency endorsement, production stability, evacuation support, routing support, tactical support, or incident-command suitability.

## Research basis

| Source | What it supports | BurnLens decision |
|---|---|---|
| W3C PROV-Overview, `https://www.w3.org/TR/prov-overview/` | Provenance is information about entities, activities, and people involved in producing a data item or thing, supporting assessment of quality, reliability, or trustworthiness. PROV supports interoperable interchange of provenance information. | Use PROV as the conceptual basis for BurnLens traceability. |
| W3C PROV-DM, `https://www.w3.org/TR/prov-dm/` | PROV-DM defines entities, activities, agents, usage, generation, derivation, attribution, and association. It is domain-agnostic and extensible. | Map BurnLens source records, processing steps, outputs, and claims to entity/activity/agent equivalents without requiring full formal PROV serialization yet. |
| `templates/SOURCE_RECORD_TEMPLATE.md` | Source records capture provider, authority, coverage, license/terms, metadata quality, CRS expectations, and use decisions before access. | Treat source records and candidate sources as BurnLens provenance entities. |
| `templates/ACCESS_LOG_TEMPLATE.md` | Access logs capture method, parameters, terms review, access result, storage/checksum plan, and credential exclusions. | Treat access as a BurnLens provenance activity. |
| `templates/FORMAT_CRS_PRECHECK_TEMPLATE.md` | Format/CRS prechecks capture technical fitness, CRS, extent, validity checks, and conversion/reprojection decisions. | Treat format/CRS precheck as a BurnLens provenance activity and evidence gate. |
| `templates/PROVENANCE_MANIFEST_TEMPLATE.json` | Existing manifest links AOI, source, access, files, prechecks, processing steps, outputs, claims, and no-go notes. | Keep this spec compatible with the existing manifest structure. |
| `templates/CLAIM_REGISTER_ENTRY_TEMPLATE.md` | Claim entries evaluate source, provenance, evidence strength, source precedence, public-language safety, and publication decision. | Treat claim-register entries and public-facing claims as downstream provenance entities and release gates. |
| `docs/phase-one/objective-five/RELEASE_CONTROL.md` | Release control requires included/excluded artifacts, boundary checks, source-precedence gates, do-not-release triggers, and evidence links. | Provenance records must support release-control decisions before public claims. |
| `VERSIONING.md` and `VERSION_TAXONOMY.md` | Versioning separates source IDs, dataset versions, method versions, model versions, run IDs, reports, and objective/app versions. | Provenance records must preserve the relevant version/identifier class without treating every ID as SemVer. |

## Formal implementation status

BurnLens is **not** implementing a full formal W3C PROV graph, PROV-O ontology, PROV-N notation, RDF serialization, XML serialization, or validator at this stage.

For P1O5-T05, BurnLens uses PROV as a conceptual model:

```text
entity + activity + agent/tool + relationship + evidence field
```

Future tasks may convert the lightweight template into JSON, PROV-N, PROV-O/RDF, or another machine-readable provenance graph if that becomes useful. Until then, Markdown traceability records and the existing JSON provenance manifest are sufficient.

## BurnLens PROV equivalents

| W3C PROV concept | BurnLens equivalent | Examples | Required role |
|---|---|---|---|
| Entity | A thing with a stable identity or state that can be used, generated, derived, cited, or claimed. | source candidate, source record, access file, precheck record, provenance manifest, method config, output artifact, run report, claim-register entry, public-facing claim. | Must have an entity ID or record path. |
| Activity | A time-bounded action that uses or generates entities. | source evaluation, access event, format/CRS precheck, preprocessing step, inference step, vectorization, report generation, claim review. | Must have an activity ID, timestamp, agent/tool, and input/output links when applicable. |
| Agent | A person, organization, software tool, model, prompt assistant, or service responsible for an activity or entity. | Drew Baker, ChatGPT/Codex, GDAL, rasterio, Python script, source provider, model package. | Must be named when responsible for a recorded action. |
| Usage | An activity uses an existing entity. | format/CRS precheck uses source file and access log. | Must list input IDs or record paths. |
| Generation | An activity creates an entity. | processing step generates a mask, vector file, report, or claim entry. | Must list generated output IDs or paths. |
| Derivation | One entity is based on another. | output artifact derived from source file through method version. | Must link upstream source/access/precheck/method records. |
| Attribution | An entity is attributed to an agent. | a claim entry attributed to reviewer/assistant/tool. | Must name agent/tool and role. |
| Association | An activity is associated with an agent/tool. | preprocessing activity associated with script/tool version. | Must record tool/agent and version where available. |
| Bundle / provenance of provenance | A grouped record about provenance records themselves. | provenance manifest, traceability record, run package. | Use manifest/traceability record ID and commit SHA. |

## Required provenance chain

BurnLens traceability must support this chain before any public-facing output or claim is allowed:

```text
source candidate
→ access record
→ format/CRS precheck
→ provenance manifest
→ processing step
→ method version
→ output artifact
→ run report
→ claim-register entry
→ public-facing claim
```

The chain may stop early for documentation-only or intake-only work. If the chain stops early, downstream fields must say `not created`, `not authorized`, or `not applicable` rather than inventing outputs.

## Chain stages

| Stage | BurnLens record/entity | Activity | Agent/tool | Output / next link | Gate status |
|---|---|---|---|---|---|
| 1. Source candidate | `SRC-YYYY-NNN` source record | source evaluation | reviewer / prompt assistant / source provider | source decision | Required before access. |
| 2. Access record | `ACCESS-YYYY-NNN` access log | access event | browser/API/CLI/tool/user | source file candidate or no-go note | Required before file use. |
| 3. Format/CRS precheck | `PRECHECK-YYYY-NNN` precheck | format and CRS inspection | GDAL/rasterio/geopandas/STAC client/other | precheck decision | Required before processing. |
| 4. Provenance manifest | `MANIFEST-YYYY-NNN` | manifest update | reviewer / prompt assistant / repo workflow | linked provenance bundle | Required before later use. |
| 5. Processing step | `STEP-YYYY-NNN` | preprocessing / mask / vector / summary activity | script/tool/model | output artifact | Future only; not authorized by T05. |
| 6. Method version | method/model/baseline version | method selection/execution | method owner / tool | method-output relationship | Future only; governed by version taxonomy. |
| 7. Output artifact | `OUTPUT-YYYY-NNN` or file path | generation activity | processing tool/model | output file and checksum plan | Future only. |
| 8. Run report | run ID and report version | report generation | report template/tool/reviewer | report artifact | Future only; T06 will define run package. |
| 9. Claim-register entry | `CLAIM-YYYY-NNN` | claim review | reviewer / prompt assistant | approved/rejected wording | Required before public claim. |
| 10. Public-facing claim | website/report/card text | publication/release review | reviewer / site/release process | public wording | Allowed only after claim and release gates pass. |

## Required fields

Every traceability record must include these fields where applicable.

| Field | Required? | BurnLens use |
|---|---:|---|
| Entity ID | Yes | Stable ID or path for source, file, output, report, claim, or public artifact. |
| Activity ID | Yes when an action occurs | Stable ID for access, precheck, processing, review, report generation, or publication. |
| Agent/tool | Yes | Person, organization, tool, model, prompt assistant, or service responsible for the activity. |
| Source record | Yes for data/source lineage | `SRC-YYYY-NNN` or `not applicable` for documentation-only work. |
| Access method | Yes for access lineage | browser/API/CLI/bulk download/manual request/none/not authorized. |
| Processing timestamp | Yes when processing/review occurs | UTC timestamp for activity start/end or recorded review time. |
| Commit SHA | Yes | Commit that created/updated the record or produced the output package. |
| Method version | Yes when a method is used | Baseline/model/report/template/method version; `not applicable` if no method used. |
| Output file path | Yes when output exists | Repo path or storage path; `not created` if future-only. |
| Checksum plan | Yes | Algorithm and timing plan; actual checksum only when files exist and are allowed. |
| Warnings | Yes | Required BurnLens warning and stage-specific caveats. |
| Source-precedence status | Yes | official-sources-govern status, conflict status, and allowed public posture. |

## Identifier patterns

| Record type | Pattern | Notes |
|---|---|---|
| Source record | `SRC-YYYY-NNN` | Existing template pattern. |
| Access log | `ACCESS-YYYY-NNN` | Existing template pattern. |
| Format/CRS precheck | `PRECHECK-YYYY-NNN` | Existing template pattern. |
| Provenance manifest | `MANIFEST-YYYY-NNN` | Existing JSON manifest pattern. |
| Traceability record | `TRACE-YYYY-NNN` | New template pattern introduced by T05. |
| Processing step | `STEP-YYYY-NNN` | Existing manifest placeholder pattern. |
| File entity | `FILE-YYYY-NNN` | Existing manifest placeholder pattern. |
| Output artifact | `OUTPUT-YYYY-NNN` | Existing manifest placeholder pattern. |
| Claim entry | `CLAIM-YYYY-NNN` | Existing claim template pattern. |
| No-go note | `NOGO-YYYY-NNN` | Existing manifest placeholder pattern. |
| Run ID | `BL-YYYY-MM-DD-deschutes-aoiXX-mXXX-dXXX` | Defined by version taxonomy; T06 will specify run package details. |

## Relationship rules

| Relationship | BurnLens rule |
|---|---|
| `used` | Every activity must list the entities it used when those entities exist. |
| `generated` | Every activity that creates a record, output, report, or claim must list the generated entity. |
| `derived from` | Every output, report, or claim must point to upstream source/access/precheck/manifest/method records. |
| `associated with` | Every activity must list a person, organization, prompt assistant, software tool, model, or workflow responsible for it. |
| `attributed to` | Every generated record or claim must identify who/what is responsible for its creation or review. |
| `invalidated / superseded` | If a source, output, report, or claim is replaced, the later record must identify what it supersedes and why. |
| `had member` | A manifest or run package may group multiple source, file, output, and claim entities. |

## Compatibility with Objective Four templates

This spec does not replace Objective Four intake templates. It connects them.

| Existing template | Compatible role in this spec |
|---|---|
| `SOURCE_RECORD_TEMPLATE.md` | Creates the source entity and source-precedence basis. |
| `ACCESS_LOG_TEMPLATE.md` | Records the access activity and any source-file entity creation. |
| `FORMAT_CRS_PRECHECK_TEMPLATE.md` | Records the technical precheck activity and pre-use decision. |
| `PROVENANCE_MANIFEST_TEMPLATE.json` | Groups AOI, source, access, files, prechecks, processing steps, outputs, claims, and no-go notes. |
| `CLAIM_REGISTER_ENTRY_TEMPLATE.md` | Records claim review before public-facing wording. |
| `NO_GO_SOURCE_NOTE_TEMPLATE.md` | Records rejected/deferred source, access, CRS, or claim decisions where applicable. |
| `AOI_RECORD_TEMPLATE.md` | Provides the spatial-scope entity when AOI records are authorized. |

Future records should link to existing template IDs instead of duplicating entire records. For example, a traceability record should cite `SRC-2026-001`, `ACCESS-2026-001`, and `PRECHECK-2026-001` rather than copying their full content.

## Checksum plan

Checksums are required when files exist and are permitted to be recorded.

Before files exist, records must still define a checksum plan:

| Field | Value |
|---|---|
| Algorithm | `sha256` unless a later task approves another algorithm. |
| Timing | Record after authorized file creation/download and before downstream use. |
| Scope | Original source file, derived file, model weights, report artifact, or package archive as applicable. |
| Storage | Store checksum text in the relevant record/manifest; do not store restricted files in repo. |
| Missing checksum status | `not created`, `not authorized`, `pending`, or `not applicable`; never blank for required fields. |

## Source-precedence status

Each traceability record must state one of these statuses.

| Status | Meaning | Public posture |
|---|---|---|
| `official-source-record` | Record references an official source for its topic. | Can cite source, but BurnLens still does not become official. |
| `official-source-compared` | BurnLens output was compared to official/reference source. | Public wording must say official sources govern. |
| `burnlens-derived-experimental` | Record references BurnLens-derived processing/output. | Must use experimental warning. |
| `conflict-with-official-source` | BurnLens artifact conflicts with official/reference source. | Public release blocked unless conflict is prominently stated or artifact excluded. |
| `source-precedence-unresolved` | Authority, conflict, or source precedence has not been resolved. | Public claim blocked. |
| `not-applicable-documentation-only` | Documentation/control artifact with no data/source claim. | Use documentation boundary language. |

## Claim gating rule

A public-facing claim is not allowed unless a traceability record can answer all questions below:

1. Which entity or output does the claim refer to?
2. Which source record(s) support the claim?
3. Which access and precheck records show the source was usable?
4. Which processing activity and method version produced the output, if any?
5. Which commit SHA contains the record/output/report?
6. Which run report or release note includes the output, if any?
7. Which claim-register entry approved the wording?
8. What warning and source-precedence status must accompany the claim?
9. What excluded work prevents the claim from being stronger?
10. Has release control approved publication, if public?

If any answer is missing, the claim must remain internal, be revised, or be rejected.

## Public-facing claim chain

A public-facing claim must preserve this minimum chain:

```text
PUBLIC-CLAIM
  uses CLAIM-YYYY-NNN
  derived from REPORT/RUN/OUTPUT if applicable
  derived from METHOD-VERSION if applicable
  derived from STEP-YYYY-NNN if applicable
  derived from MANIFEST-YYYY-NNN
  derived from PRECHECK-YYYY-NNN
  derived from ACCESS-YYYY-NNN
  derived from SRC-YYYY-NNN
  reviewed in PR #
  recorded at commit SHA
  governed by source-precedence status
```

Documentation-only claims may omit data, method, output, and run stages, but must explicitly mark them `not applicable` or `not created`.

## Example lightweight relationship block

```text
Traceability record: TRACE-2026-001
Claim: CLAIM-2026-001
Public claim status: blocked / internal only / approved with warning

Entity used: SRC-2026-001
Activity: ACCESS-2026-001 used SRC-2026-001
Activity: PRECHECK-2026-001 used FILE-2026-001 and generated PRECHECK decision
Entity: MANIFEST-2026-001 had member SRC-2026-001, ACCESS-2026-001, PRECHECK-2026-001
Activity: STEP-2026-001 used FILE-2026-001 and method burnlens-baseline-v0.1.0
Entity generated: OUTPUT-2026-001 at path [future path]
Entity generated: run report [future report path]
Entity generated: CLAIM-2026-001
Public-facing claim derived from CLAIM-2026-001
Warning: Experimental BurnLens CV output...
Source precedence: official sources govern
```

This example is a structure example only. It does not assert that any actual data, processing step, output, report, or claim exists.

## No-go conditions

Create or link a no-go note if:

- source authority is unclear or too weak for the intended claim;
- source access requires credentials or terms that cannot be documented safely;
- file checksum cannot be planned or recorded when files exist;
- format/CRS precheck fails or is unresolved;
- processing method version is missing;
- output path or run report cannot be traced;
- source-precedence status is unresolved;
- public wording lacks a claim-register entry;
- the claim implies operational, official, field-validated, emergency-ready, agency-endorsed, evacuation, routing, tactical, or incident-command use.

## Acceptance criteria

| Check | Status | Notes |
|---|---|---|
| BurnLens entity/activity/agent equivalents defined. | Satisfied | See PROV equivalents table. |
| Full source-to-claim chain defined. | Satisfied | Required provenance chain and chain stages. |
| Required fields included. | Satisfied | Required fields table. |
| Full formal PROV implementation not required yet. | Satisfied | Formal implementation status section. |
| Compatible with Objective Four provenance/intake templates. | Satisfied | Compatibility table. |
| No data/model/map/public-output work authorized. | Satisfied | Boundary and no-go sections. |
| Source precedence preserved. | Satisfied | Source-precedence status and claim gate. |

## Handoff

P1O5-T06 should use this spec to define the future run manifest and run package contract. T06 should make the run ID, run manifest, output inventory, method/model version links, checksums, report version, warnings, and claim-register links concrete while preserving the same no-data/no-output boundary until future Phase Two gates authorize actual work.
