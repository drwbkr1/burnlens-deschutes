# Artifact Registry Spec

## Purpose

This document defines where future BurnLens Deschutes artifacts live and how they are named.

The artifact registry is a planning and traceability-control specification. It tells future tasks how to index documents, records, sources, AOIs, manifests, packages, reports, screenshots, and public site assets without mixing templates, completed records, official/reference sources, or BurnLens-derived outputs.

This spec is documentation and records work only. It does not create, approve, access, download, inspect, transform, label, mask, process, model, map, publish, release, or register any data or output.

## Boundary statement

Experimental BurnLens CV/GEOINT portfolio work. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

An artifact registry entry proves that BurnLens can identify and locate an artifact class. It does **not** prove that the artifact exists, is official, is operational, is field-validated, is emergency-ready, is agency-endorsed, is production-stable, or is suitable for evacuation, routing, tactical, or incident-command use.

## Current implementation status

No registry file or registry database exists yet.

No future artifact listed in this spec is created by P1O5-T07.

This spec defines the naming/location contract that future registry entries should follow once artifacts are authorized.

## Governing basis

No new external metadata-standard claims are introduced by this spec. Existing BurnLens repo controls govern this registry:

| Governing artifact | Registry use |
|---|---|
| `README.md` | Project identity, source separation rule, core workflow, current boundaries. |
| `VERSIONING.md` | Current versioning and traceability expectations. |
| `docs/phase-one/objective-five/VERSION_TAXONOMY.md` | Identifier patterns for objective baselines, AOIs, sources, datasets, labels, methods, models, runs, and reports. |
| `docs/phase-one/objective-five/RELEASE_CONTROL.md` | Release classes, do-not-release triggers, public release gates, and included/excluded artifact rules. |
| `docs/phase-one/objective-five/PROVENANCE_TRACEABILITY_SPEC.md` | Source-to-claim lineage and BurnLens entity/activity/agent equivalents. |
| `docs/phase-one/objective-five/RUN_PACKAGE_CONTRACT.md` | Future run folder contract, output inventory, warnings, and public screenshot run-ID rule. |
| `docs/objective-one/SOURCE_PRECEDENCE.md` | Official sources govern; BurnLens-derived outputs must not outrank official/reference sources. |
| `docs/objective-one/USE_BOUNDARIES.md` | Prohibited operational/emergency/public-safety claims. |

## Source separation rule

The registry must preserve the README source separation rule.

Future BurnLens artifacts must keep these categories separate:

```text
official/reference sources
reference-derived labels
baseline outputs
model outputs
map overlays
portfolio interpretations
```

No registry table, report, map, model card, run package, website card, screenshot, or public site asset may blur those categories.

## Template versus completed record rule

The registry must never treat a template as a completed record.

| Registry state | Meaning | Public claim allowed? |
|---|---|---:|
| `template` | Blank reusable scaffold. | No. |
| `planned` | Future artifact expected but not created. | No. |
| `draft-record` | Record exists but review or required fields are incomplete. | No, unless explicitly marked internal-only. |
| `completed-record` | Record is complete for its intended documentation purpose. | Maybe, only if claim and release gates pass. |
| `superseded-record` | Record was replaced by a newer record/version. | No, except as historical evidence. |
| `rejected-record` | Candidate was rejected or marked no-go. | No, except to explain exclusion. |
| `future-output` | Output may exist in a later phase but does not exist yet. | No. |
| `generated-output` | Output exists and must link to run/package/provenance/checksum records. | Maybe, only if warning, claim, and release gates pass. |

Templates live under `templates/` unless a later task creates a versioned template package. Completed records should live under `records/` or another approved future package location.

## Official/reference versus BurnLens-derived rule

Every future registry entry must include an origin class.

| Origin class | Meaning | Examples | Source-precedence rule |
|---|---|---|---|
| `official-reference` | Source or record from an official/primary authority. | county/state/federal/fire/emergency/transportation/air-quality/incident source record. | Highest precedence for its topic. |
| `reference-derived` | BurnLens record derived from official/reference material without being official itself. | reference-derived labels, source summaries, source comparison notes. | Must cite upstream official/reference source. |
| `third-party-reference` | Non-official source used for context or technical evidence. | standards docs, technical references, public datasets from non-authoritative publishers. | Must not override official sources. |
| `burnlens-control` | BurnLens documentation, workflow, template, or registry/control artifact. | this spec, version taxonomy, release control, run package contract. | Controls BurnLens process only. |
| `burnlens-derived-output` | Future output generated by BurnLens methods/models/runs. | prediction mask, polygons, exposure summary, map export. | Lowest precedence; must be warned as experimental. |
| `public-portfolio-asset` | Site or presentation artifact derived from BurnLens evidence. | website card, screenshot, case study image. | Must cite evidence and not exceed support. |

## Universal registry fields

Every future registry table should preserve these fields when applicable.

| Field | Required? | Purpose |
|---|---:|---|
| Registry ID | Yes | Stable row or artifact ID. |
| Artifact class | Yes | Document, record, source record, AOI record, manifest, package, report, screenshot, or public site asset. |
| Artifact name/title | Yes | Human-readable label. |
| Path or location | Yes | Repo path, future package path, or external source URL/reference. |
| State | Yes | Template, planned, draft, completed, superseded, rejected, future-output, generated-output. |
| Origin class | Yes | Official/reference, reference-derived, BurnLens control, BurnLens-derived output, public portfolio asset. |
| Version or ID | Yes where applicable | Version taxonomy ID, source ID, run ID, report version, or `not applicable`. |
| Parent/related IDs | Yes where applicable | Source ID, AOI version, dataset version, method version, run ID, claim ID, report ID. |
| Commit SHA | Yes for repo artifacts | Commit that created or last materially changed the artifact. |
| Checksum status | Yes for data/output assets | `not-created`, `not-authorized`, `pending`, `complete`, or `superseded`. |
| Source-precedence status | Yes | Official-sources-govern status and conflict status. |
| Warning required | Yes | Whether the BurnLens warning must accompany public use. |
| Public-use status | Yes | Internal-only, public-blocked, public-eligible-after-review, public-used. |
| Claim-register link | Yes for public-facing artifacts | Claim record or `not created`. |
| Release-control status | Yes for public-facing artifacts | Not reviewed, blocked, eligible, included, excluded. |
| Notes | Optional | Caveats, exclusions, or reviewer notes. |

## Identifier patterns

| Registry class | Registry ID pattern | Example | Notes |
|---|---|---|---|
| Document | `DOC-YYYY-NNN` | `DOC-2026-001` | For project docs and technical docs when a registry row is needed. |
| General record | `REC-YYYY-NNN` | `REC-2026-001` | For decision/review/QA/claim support records not covered by a specific ID. |
| Source record | `SRC-YYYY-NNN` | `SRC-2026-001` | Uses existing source record pattern. |
| AOI record | `AOI-YYYY-NNN` | `AOI-2026-001` | Future AOI record; separate from AOI version. |
| Data manifest | `DATA-YYYY-NNN` | `DATA-2026-001` | Future dataset/data manifest registry row. |
| Label manifest | `LABEL-YYYY-NNN` | `LABEL-2026-001` | Future label manifest/label schema registry row. |
| Model package | `MODEL-YYYY-NNN` | `MODEL-2026-001` | Future model package registry row. |
| Baseline package | `BASELINE-YYYY-NNN` | `BASELINE-2026-001` | Future baseline package registry row. |
| Run package | `RUNPKG-YYYY-NNN` | `RUNPKG-2026-001` | Future run package registry row; must link run ID. |
| Report | `REPORT-YYYY-NNN` | `REPORT-2026-001` | Future report registry row; must link report version/run ID where applicable. |
| Screenshot | `SHOT-YYYY-NNN` | `SHOT-2026-001` | Future screenshot/map-export registry row; must link run ID. |
| Public site asset | `SITEASSET-YYYY-NNN` | `SITEASSET-2026-001` | Future website/demo/case-study asset registry row. |

These registry IDs are row identifiers. They do not replace version taxonomy identifiers, run IDs, source IDs, claim IDs, or commit SHAs.

## Registry table: documents

| Field | Rule |
|---|---|
| Primary location | `docs/`; `README.md`; `VERSIONING.md`; approved docs paths. |
| Naming pattern | Descriptive uppercase snake-case for objective artifacts, e.g. `ARTIFACT_REGISTRY_SPEC.md`. |
| Registry state | Usually `completed-record` after merge; `template` only if stored under `templates/`. |
| Origin class | `burnlens-control`. |
| Required links | Issue, PR, commit SHA, parent objective, prompt log when prompt-assisted. |
| Public-use status | Public-eligible only if boundaries and claims are accurate. |
| Notes | Documents can describe future artifacts without proving those artifacts exist. |

Example future row shape:

```text
DOC-YYYY-NNN | ARTIFACT_REGISTRY_SPEC.md | docs/phase-one/objective-five/ARTIFACT_REGISTRY_SPEC.md | completed-record | burnlens-control | commit SHA | public-eligible-after-review
```

## Registry table: records

| Field | Rule |
|---|---|
| Primary location | `records/` and subdirectories such as `records/prompt-build-log/`. |
| Naming pattern | `YYYY-MM-DD-task-id.md` for prompt logs; `REC-YYYY-NNN.md` for general future records. |
| Registry state | `completed-record`, `draft-record`, `superseded-record`, or `rejected-record`. |
| Origin class | Usually `burnlens-control`; claim/evidence records may also reference official/reference sources. |
| Required links | Issue, PR, commit SHA, source/provenance/claim links where applicable. |
| Public-use status | Depends on content; records containing unresolved claims remain public-blocked. |
| Notes | Prompt logs summarize decisions and verification, not private reasoning. |

## Registry table: source records

| Field | Rule |
|---|---|
| Primary location | Future `records/phase-two/sources/` or another approved source-record directory. |
| Naming pattern | `SRC-YYYY-NNN.md`. |
| Registry state | `draft-record`, `completed-record`, `rejected-record`, or `superseded-record`. |
| Origin class | `official-reference`, `third-party-reference`, or `reference-derived` depending on the source. |
| Required links | Provider, access log, license/terms review, format/CRS precheck, provenance manifest, source-precedence status. |
| Public-use status | Public-blocked until source-precedence and license/terms status are resolved. |
| Notes | A source record can cite an official source without becoming official itself. |

## Registry table: AOI records

| Field | Rule |
|---|---|
| Primary location | Future `records/phase-two/aoi/`. |
| Naming pattern | `AOI-YYYY-NNN.md`; AOI version follows `{geography}-aoiNN-v0.MINOR[.PATCH]`. |
| Registry state | `planned`, `draft-record`, `completed-record`, `superseded-record`, or `rejected-record`. |
| Origin class | `burnlens-control` for the record; geometry sources may be `official-reference` or `third-party-reference`. |
| Required links | AOI version, geometry source, CRS expectation, boundary rationale, source-precedence note, commit SHA. |
| Public-use status | Public-blocked until AOI record and source-precedence status are complete. |
| Notes | An AOI version identifies scope state; it does not select or validate data by itself. |

## Registry table: data manifests

| Field | Rule |
|---|---|
| Primary location | Future `records/phase-two/data/` or future dataset package folder. |
| Naming pattern | `DATA-YYYY-NNN.json` or `{aoi-id}-dataset-vMAJOR.MINOR.PATCH-manifest.json`. |
| Registry state | `planned`, `draft-record`, `completed-record`, `superseded-record`, or `rejected-record`. |
| Origin class | `reference-derived` for source-derived datasets; `burnlens-control` for manifest template/record only. |
| Required links | AOI version, source records, access logs, format/CRS prechecks, provenance manifest, checksum list, dataset version. |
| Public-use status | Public-blocked until license/terms, source-precedence, provenance, and checksum gates pass. |
| Notes | A data manifest does not imply model quality or operational readiness. |

## Registry table: label manifests

| Field | Rule |
|---|---|
| Primary location | Future `records/phase-two/labels/` or future label package folder. |
| Naming pattern | `LABEL-YYYY-NNN.json` or `{target}-labels-v0.MINOR[.PATCH]-manifest.json`. |
| Registry state | `planned`, `draft-record`, `completed-record`, `superseded-record`, or `rejected-record`. |
| Origin class | `reference-derived` when labels are derived from official/reference sources; `burnlens-control` for schema/control records. |
| Required links | Label schema version, target decision, source records, annotation rules, QA notes, dataset version, commit SHA. |
| Public-use status | Public-blocked until ambiguity, source-precedence, and QA notes are complete. |
| Notes | Labels must remain separate from baseline/model outputs and portfolio interpretations. |

## Registry table: model packages

| Field | Rule |
|---|---|
| Primary location | Future `models/` or future approved package directory. |
| Naming pattern | `burnlens-cv-{architecture}-vMAJOR.MINOR.PATCH/` plus registry ID `MODEL-YYYY-NNN`. |
| Registry state | `planned`, `draft-record`, `completed-record`, `superseded-record`, or `rejected-record`. |
| Origin class | `burnlens-derived-output`. |
| Required links | Model version, architecture, training commit, dataset version, label schema version, config, weights checksum, metrics, limitations, run IDs using model. |
| Public-use status | Public-blocked until model card, metrics, limitations, warning, and claim gates pass. |
| Notes | A model package version does not imply operational readiness or field validation. |

## Registry table: baseline packages

| Field | Rule |
|---|---|
| Primary location | Future `baselines/` or future approved package directory. |
| Naming pattern | `burnlens-baseline-vMAJOR.MINOR.PATCH/` plus registry ID `BASELINE-YYYY-NNN`. |
| Registry state | `planned`, `draft-record`, `completed-record`, `superseded-record`, or `rejected-record`. |
| Origin class | `burnlens-derived-output` for generated baseline outputs; `burnlens-control` for method documentation. |
| Required links | Baseline method version, input contract, output contract, config, dataset version, commit SHA, run IDs, limitations. |
| Public-use status | Public-blocked until output inventory, warnings, provenance, and claim gates pass. |
| Notes | Baseline outputs must remain separate from model outputs and official/reference sources. |

## Registry table: run packages

| Field | Rule |
|---|---|
| Primary location | Future `/runs/BL-YYYY-MM-DD-deschutes-aoiXX-mXXX-dXXX/`. |
| Naming pattern | Run ID plus registry ID `RUNPKG-YYYY-NNN`. |
| Registry state | `planned`, `draft-record`, `completed-record`, `failed`, `discarded`, or `superseded-record` when supported by future registry values. |
| Origin class | `burnlens-derived-output` for outputs; `burnlens-control` for package records. |
| Required links | Run ID, `run_manifest.json`, source links, processing log, output inventory, warnings, run report, commit SHA, versions, checksums. |
| Public-use status | Public-blocked until run package gates and release-control gates pass. |
| Notes | No run package exists yet. Future public screenshots must reference a run ID. |

## Registry table: reports

| Field | Rule |
|---|---|
| Primary location | Future run folder, report package folder, or `records/phase-two/reports/`. |
| Naming pattern | `REPORT-YYYY-NNN.md`; report version follows `run-report-vMAJOR.MINOR.PATCH`. |
| Registry state | `planned`, `draft-record`, `completed-record`, `superseded-record`, or `rejected-record`. |
| Origin class | `burnlens-control` for report template/record; `public-portfolio-asset` if adapted for website/presentation. |
| Required links | Report version, run ID, run manifest, source records, dataset/model/baseline versions, claim-evidence links, warnings and limitations. |
| Public-use status | Public-blocked until claim-register and release-control review pass. |
| Notes | A report does not make a run official or operational. |

## Registry table: screenshots

| Field | Rule |
|---|---|
| Primary location | Future run folder or public-site asset folder only after authorization. |
| Naming pattern | `SHOT-YYYY-NNN-{run-id}-{short-description}.png` or approved derivative. |
| Registry state | `planned`, `generated-output`, `superseded-record`, or `rejected-record`. |
| Origin class | `burnlens-derived-output` or `public-portfolio-asset`. |
| Required links | Run ID, run manifest, output inventory entry, warning, source-precedence status, claim-register entry if supporting a claim. |
| Public-use status | Public-blocked until all links exist and warning/claim/release gates pass. |
| Notes | A screenshot without a run ID is not publishable as BurnLens evidence. |

## Registry table: public site assets

| Field | Rule |
|---|---|
| Primary location | `burnlens-site` repository or approved public-site asset directory, not this technical repo by default. |
| Naming pattern | `SITEASSET-YYYY-NNN-{purpose}` for registry row; site repo filenames follow site conventions. |
| Registry state | `planned`, `draft-record`, `completed-record`, `superseded-record`, or `rejected-record`. |
| Origin class | `public-portfolio-asset`. |
| Required links | Source technical artifact, run ID if derived from a run, screenshot ID if visual, claim-register entry, release-control decision, warning text. |
| Public-use status | Public-blocked until claim and release gates pass. |
| Notes | Public site assets must not make claims stronger than supported by this technical repository. |

## Registry grouping rules

Future registry implementations may be a Markdown table, JSON manifest, CSV, SQLite database, or generated index. Regardless of format, the registry must keep these groups separate:

1. Templates.
2. Completed documentation/control records.
3. Official/reference source records.
4. Reference-derived labels and datasets.
5. BurnLens baseline/model/run outputs.
6. Reports and portfolio interpretations.
7. Public site assets.

A public-facing artifact may link across groups, but it must not collapse them into one undifferentiated “source” or “result.”

## Public-use gates

Before a registry entry can support a public-facing claim, screenshot, report, site asset, or release note, it must have:

- artifact class and state;
- origin class;
- path/location;
- version or ID where applicable;
- commit SHA for repo artifacts;
- source-precedence status;
- warning requirement;
- claim-register link;
- release-control status;
- output inventory and checksum status if data/output files exist;
- explicit boundary language when BurnLens-derived outputs are involved.

## Rejection and no-go conditions

Reject, block, or mark incomplete any future registry entry if:

- it treats a template as a completed record;
- it treats a planned artifact as if it exists;
- it mixes official/reference sources with BurnLens-derived outputs;
- it fails to preserve the README source separation rule;
- it omits source-precedence status;
- it omits a run ID for a screenshot or run-derived public asset;
- it lacks a claim-register link for a public-facing claim;
- it implies data/model/map/run/report/public-demo readiness that is not supported;
- it implies official, operational, field-validated, emergency-ready, agency-endorsed, evacuation, routing, tactical, or incident-command use.

## Acceptance criteria

| Check | Status | Notes |
|---|---|---|
| Registry tables defined for all requested classes. | Satisfied | Documents, records, source records, AOI records, data manifests, label manifests, model packages, baseline packages, run packages, reports, screenshots, and public site assets included. |
| Templates distinguished from completed records. | Satisfied | Template versus completed record rule and state table included. |
| Official/reference sources distinguished from BurnLens-derived outputs. | Satisfied | Origin-class table and table-specific rules included. |
| README source separation rule preserved. | Satisfied | Source separation rule included and applied as registry no-go condition. |
| Future locations and naming patterns defined. | Satisfied | Registry table rules and identifier patterns included. |
| No future artifacts created. | Satisfied | Spec only; no records, packages, outputs, screenshots, or public assets created. |

## Handoff

P1O5-T08 should use this registry specification to define the claim-to-evidence protocol. That protocol should explain what evidence a future claim must cite, which registry entries can support it, and which claims are blocked when evidence is incomplete, ambiguous, unofficial, BurnLens-derived, or source-precedence unresolved.
