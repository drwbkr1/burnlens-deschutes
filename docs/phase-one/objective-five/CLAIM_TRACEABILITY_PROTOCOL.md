# Claim Traceability Protocol

## Purpose

This protocol prevents BurnLens Deschutes portfolio claims from becoming stronger than the evidence in the repository.

A claim is any public-facing statement, caption, report sentence, website card, screenshot label, slide, demo note, README statement, release note, portfolio summary, or spoken/written description that tells a reader what BurnLens is, does, used, produced, found, demonstrated, or can support.

The rule is simple:

```text
No public-facing claim without linked evidence.
```

This protocol is documentation and records work only. It does not create a completed claim register, approve any public claim, publish any site asset, create any screenshot, create any run, validate any model, create any map, or authorize any operational wildfire use.

## Boundary statement

Experimental BurnLens CV/GEOINT portfolio work. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

BurnLens may claim reproducibility, traceability, technical workflow demonstration, and transparent limitations only when supporting records exist.

BurnLens must not claim or imply official status, operational status, emergency readiness, agency endorsement, field validation, evacuation support, routing support, tactical support, incident-command support, confirmed hazard status, road-closure authority, or public-safety decision support.

## Current implementation status

No completed claim register exists yet.

No completed claim records are created by P1O5-T08.

No public-facing claim is approved by this task.

This protocol defines the future claim-to-evidence rules and a reusable evidence-link template only.

## Governing basis

No new external model-card, data-card, claims-standard, legal, or policy references are introduced by this protocol. Existing BurnLens repo controls govern this task:

| Governing artifact | Claim-protocol use |
|---|---|
| `README.md` | Scope, current status, source separation rule, use boundary, warning language. |
| `docs/objective-one/TECHNICAL_DESCRIPTION.md` | Technical workflow and appropriate technical-scope claims. |
| `docs/objective-one/USE_BOUNDARIES.md` | Allowed/prohibited uses and required disclaimers. |
| `docs/objective-one/SOURCE_PRECEDENCE.md` | Official sources govern; BurnLens-derived outputs remain lowest precedence. |
| `VERSIONING.md` | Traceability expectations for versions and future outputs. |
| `docs/phase-one/objective-five/VERSION_TAXONOMY.md` | Version/identifier taxonomy for sources, datasets, labels, models, runs, and reports. |
| `docs/phase-one/objective-five/RELEASE_CONTROL.md` | Public release gates and do-not-release triggers. |
| `docs/phase-one/objective-five/PROVENANCE_TRACEABILITY_SPEC.md` | Source-to-claim lineage and entity/activity/agent equivalents. |
| `docs/phase-one/objective-five/RUN_PACKAGE_CONTRACT.md` | Future run ID, manifest, warnings, output inventory, and screenshot rules. |
| `docs/phase-one/objective-five/ARTIFACT_REGISTRY_SPEC.md` | Registry states, origin classes, public-use status, and source-separation controls. |

## Core rule

A future public-facing claim is allowed only when all of the following are true:

1. the claim type is identified;
2. the exact claim text is recorded;
3. the evidence required for that claim type exists;
4. the evidence paths or IDs are linked;
5. the evidence status is complete enough for the claim;
6. source-precedence status is recorded;
7. required warning and limitation language is present;
8. release-control status allows public use;
9. the claim does not use forbidden language;
10. the claim does not exceed what the evidence supports.

If any item is missing, the claim is blocked, draft-only, or internal-only.

## Claim ladder

| Claim type | Evidence required | Minimum status before public use | Notes |
|---|---|---|---|
| Scope claim | `README.md`, technical description, use boundaries | Repo documents are merged and current | Can describe project purpose, experimental scope, and non-operational boundary. |
| Source claim | Source record, access log, license/terms note | Source record/access/terms are complete and source-precedence status is resolved | Cannot imply official endorsement unless the source itself explicitly states that relationship and the repo records it. |
| Data-readiness claim | AOI record, source record, access record, format/CRS precheck, provenance record | All required intake/provenance records exist and are complete | Cannot claim model readiness, output quality, or operational readiness. |
| Model claim | Model card, metrics, dataset version, label version, method/model version, limitations | Model evidence, metrics, dataset/label lineage, and limitations exist and are complete | Cannot claim field validation, emergency readiness, operational readiness, or agency endorsement. |
| Map/output claim | Run ID, run manifest, output inventory, source-precedence note, warning, checksum status | Run package gates pass and output inventory/checksum/source-precedence status are complete | Fire, hazard, road, evacuation, or emergency-context wording requires source-precedence language. |
| Portfolio claim | Claim-register entry, limitation statement, supporting registry entries, release-control decision | Claim record is complete and public-use gates pass | Must not be stronger than the underlying evidence. |

## Claim type definitions

### Scope claim

A scope claim explains what BurnLens is, what phase the project is in, what the technical workflow is intended to demonstrate, or which boundaries apply.

Allowed only when supported by:

- `README.md`;
- `docs/objective-one/TECHNICAL_DESCRIPTION.md`;
- `docs/objective-one/USE_BOUNDARIES.md`;
- current-status artifacts when the claim describes current progress.

Acceptable scope claim pattern:

```text
BurnLens is an experimental CV/GEOINT portfolio project that documents a reproducible wildfire-related screening workflow with traceability and clear limitations.
```

Blocked scope claim pattern:

```text
BurnLens provides operational wildfire intelligence.
```

### Source claim

A source claim describes a source, its provider, access method, license/terms review, or official/reference status.

Allowed only when supported by:

- source record;
- access log;
- license/terms note;
- format/CRS precheck if geospatial or data-format context is involved;
- source-precedence status.

A source claim may say a source is official/reference only when the source record proves that status. It must not convert BurnLens analysis into an official source.

### Data-readiness claim

A data-readiness claim says future BurnLens data inputs, AOI records, source records, CRS checks, or provenance controls are ready for a defined next step.

Allowed only when supported by:

- AOI record;
- source record;
- access log;
- format/CRS precheck;
- provenance manifest or traceability record;
- dataset/data manifest where applicable;
- license/terms status;
- source-precedence status.

A data-readiness claim cannot imply model readiness, output quality, public safety usefulness, or operational use.

### Model claim

A model claim describes a future model, architecture, training run, evaluation metric, limitation, or comparison.

Allowed only when supported by:

- model card;
- model version;
- dataset version;
- label schema/version;
- metrics record;
- method/config version;
- run IDs where applicable;
- limitations;
- source-precedence language if fire, hazard, evacuation, road, or emergency context appears.

Model claims must be scoped to the actual evidence. A metric alone does not justify operational, official, field-validated, emergency-ready, or agency-endorsed language.

### Map/output claim

A map/output claim describes a future raster, vector, exposure-style summary, map overlay, screenshot, report figure, or public image.

Allowed only when supported by:

- run ID;
- run manifest;
- source links;
- processing log;
- output inventory;
- warnings;
- source-precedence note;
- checksum status;
- claim-register entry if public-facing;
- release-control status if public-facing.

Every future public screenshot, map export, website image, case-study figure, or report figure derived from a run must reference a run ID.

### Portfolio claim

A portfolio claim describes what the project demonstrates to a reader, reviewer, employer, funder, or collaborator.

Allowed only when supported by:

- completed claim-register entry;
- limitation statement;
- artifact registry entries;
- relevant source/provenance/run/report evidence;
- release-control decision;
- warning language where BurnLens-derived outputs are involved.

Portfolio claims may describe reproducibility, traceability, transparent limitations, workflow demonstration, documentation maturity, and technical approach only when the supporting records exist.

## Claim strength levels

| Level | Meaning | Public use allowed? | Required evidence |
|---|---|---:|---|
| `level-0-planned` | Future intention or planned control. | Yes, only if clearly framed as planned and non-existent. | Current plan/control document. |
| `level-1-documented` | Documented repo control or template exists. | Yes, for documentation-scope claims only. | Merged document/template and current-status note. |
| `level-2-recorded` | Completed record exists for a source, AOI, claim, run, or review. | Maybe. | Completed record and registry entry. |
| `level-3-generated` | BurnLens output exists. | Maybe. | Run package, output inventory, warning, source-precedence status, checksums. |
| `level-4-reviewed-public` | Public-facing claim reviewed against evidence and release gates. | Yes, if not forbidden. | Claim-register entry, limitation, release-control decision. |
| `never-allowed` | Claim type is forbidden for BurnLens. | No. | Not applicable. |

## Forbidden claims

The following claims are forbidden unless a future project-level decision changes the governing use boundary. T08 does not authorize such a change.

BurnLens must not claim or imply that it is:

- official;
- operational;
- emergency-ready;
- agency-endorsed;
- field-validated;
- an evacuation-order tool;
- routing guidance;
- road-closure guidance;
- tactical fire intelligence;
- incident-command support;
- a substitute for county, state, federal, fire-service, emergency-management, transportation, air-quality, or incident sources.

Forbidden wording includes, but is not limited to:

```text
official wildfire map
operational fire intelligence
emergency-ready model
agency-approved output
field-validated hazard system
evacuation guidance
safe route
road closure authority
tactical fire product
incident command support
confirmed fire boundary
```

If a portfolio asset needs to discuss one of these topics, it must do so as a prohibited-use boundary or source-precedence limitation, not as a BurnLens capability.

## Fire, evacuation, hazard, and road context rule

Any public-facing claim involving fire, wildfire, hotspot, burn scar, smoke, hazard, evacuation, road, routing, closure, emergency, incident, perimeter, structure exposure, or public-safety context must include source-precedence language.

Minimum required language:

```text
Experimental BurnLens output. Official sources govern.
```

Preferred full language when space allows:

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

A claim involving fire, evacuation, hazard, or road context is blocked if it lacks a source-precedence note or if official-source conflict is unresolved.

## Evidence-link requirements

Every future public-facing claim must link to a claim evidence record using `templates/CLAIM_EVIDENCE_LINK_TEMPLATE.md` or a later approved replacement.

Minimum fields:

| Field | Required? | Purpose |
|---|---:|---|
| Claim ID | Yes | Stable claim record identifier. |
| Exact claim text | Yes | The public-facing text being reviewed. |
| Claim type | Yes | Scope, source, data-readiness, model, map/output, portfolio, or mixed. |
| Claim strength level | Yes | Planned, documented, recorded, generated, reviewed-public, or never-allowed. |
| Public surface | Yes | README, website, report, slide, screenshot, release note, portfolio copy, etc. |
| Required evidence | Yes | Evidence required by the claim ladder. |
| Evidence links | Yes | Paths, IDs, PRs, commits, registry rows, source records, run IDs, or reports. |
| Evidence status | Yes | Complete, partial, missing, blocked, superseded, or not applicable. |
| Source-precedence status | Yes | Official/reference/BurnLens-derived/conflict/unresolved status. |
| Limitation statement | Yes | Boundary or caveat required for public use. |
| Forbidden-claim check | Yes | Explicit pass/fail for forbidden claims. |
| Fire/evacuation/hazard/road check | Yes | Whether source-precedence language is required and present. |
| Release-control status | Yes | Not reviewed, blocked, eligible, included, excluded. |
| Decision | Yes | Approved, revise, blocked, internal-only, or archive. |

## Claim review decisions

| Decision | Meaning | Public use allowed? |
|---|---|---:|
| `approved` | Evidence exists, wording matches evidence, warnings/limitations included, release gates passed. | Yes. |
| `revise` | Evidence exists but wording is too broad, missing caveats, or unclear. | No until revised. |
| `blocked` | Evidence is missing, source precedence unresolved, forbidden claim present, or release gate failed. | No. |
| `internal-only` | Useful internal note but not safe for public use. | No. |
| `archive` | Historical/obsolete claim retained for traceability only. | No. |

## Examples

| Draft claim | Claim type | Decision | Reason |
|---|---|---|---|
| `BurnLens is an experimental CV/GEOINT portfolio project.` | Scope | Potentially approved | Supported by README and use-boundary docs if current. |
| `BurnLens has a claim-to-evidence protocol.` | Scope / portfolio | Potentially approved after T08 merge | Supported by this merged protocol and prompt log. |
| `BurnLens is operational wildfire intelligence.` | Portfolio | Blocked | Forbidden operational claim. |
| `BurnLens identified evacuation risks on roads.` | Map/output / hazard-road context | Blocked | Requires run ID, official/reference context, source-precedence language, and cannot imply evacuation guidance. |
| `This screenshot shows a BurnLens experimental output from run BL-...; official sources govern.` | Map/output | Potentially approved | Requires run manifest, output inventory, warning, source-precedence status, and claim-register entry. |
| `The model is field-validated.` | Model | Blocked | Forbidden field-validation claim unless governing boundary changes and evidence exists; not authorized by this project. |

## Public copy rewrite rule

When a claim is too strong but potentially salvageable, rewrite it to match evidence.

| Too strong | Safer direction |
|---|---|
| `BurnLens predicts wildfire hazards.` | `BurnLens demonstrates an experimental workflow for traceable wildfire-related screening outputs.` |
| `BurnLens maps evacuation risk.` | `BurnLens does not provide evacuation guidance; future map outputs must reference official sources and include source-precedence warnings.` |
| `The model is ready for field use.` | `The model, if created in a later phase, would require documented data, labels, metrics, limitations, and review before any public claim.` |
| `This output shows where fire is.` | `This future output would be experimental BurnLens-derived evidence and must be compared with official/reference sources before public use.` |

## Source separation requirement

Claims must preserve the README source separation rule:

```text
official/reference sources
reference-derived labels
baseline outputs
model outputs
map overlays
portfolio interpretations
```

A public claim must not collapse these categories into one undifferentiated source or result.

If a claim uses official/reference material and BurnLens-derived output together, it must say which is which.

## Claim-to-registry relationship

A future claim evidence record must link to registry entries when registry entries exist.

| Claim type | Registry links expected |
|---|---|
| Scope claim | Document registry entries for README, technical description, use boundaries. |
| Source claim | Source record registry entry, access/terms records, source-precedence status. |
| Data-readiness claim | AOI record, source record, data manifest, provenance record. |
| Model claim | Model package, dataset/label manifests, metrics/report records. |
| Map/output claim | Run package, output inventory, screenshot/report entries, source-precedence status. |
| Portfolio claim | Public site asset, report, screenshot, claim record, release-control decision. |

A missing registry entry does not automatically block internal drafting, but it blocks public evidence claims once the registry exists and applies to that artifact class.

## Release-control relationship

A public-facing claim must not be included in a release note, public site, slide deck, public report, screenshot caption, or portfolio case study unless release-control status allows it.

Release-control review must confirm:

- claim text matches evidence;
- claim strength is no higher than evidence supports;
- source-precedence status is resolved;
- warnings and limitations are present;
- forbidden-claim check passes;
- public-use status is eligible;
- required claim evidence link exists.

## Rejection and no-go conditions

Reject, block, or revise any future claim if:

- the evidence link is missing;
- the exact claim text is not recorded;
- claim type is unknown;
- required evidence for the claim ladder is missing;
- source-precedence status is missing or unresolved for fire, evacuation, hazard, road, or emergency context;
- official/reference sources and BurnLens-derived outputs are blurred;
- the claim implies official, operational, emergency-ready, agency-endorsed, or field-validated status;
- the claim implies evacuation, routing, tactical, road-closure, or incident-command support;
- the claim says data, model, map, run, or public assets exist before records prove they exist;
- the limitation statement is missing;
- release-control status is blocked or not reviewed.

## Acceptance criteria

| Check | Status | Notes |
|---|---|---|
| Every public-facing claim must link to evidence. | Satisfied | Core rule and evidence-link requirements included. |
| Forbidden claims repeated. | Satisfied | Official, operational, emergency-ready, agency-endorsed, and field-validated claims are forbidden. |
| Fire/evacuation/hazard/road context requires source-precedence language. | Satisfied | Dedicated context rule included. |
| Use-boundary rule extended. | Satisfied | Reproducibility, traceability, technical workflow demonstration, and transparent limitations require records. |
| Claim ladder included. | Satisfied | Six requested claim types and required evidence included. |
| Template included without creating completed claim records. | Satisfied | `templates/CLAIM_EVIDENCE_LINK_TEMPLATE.md` is a blank scaffold only. |

## Handoff

P1O5-T09 should integrate this claim-to-evidence protocol into source-precedence release gates so release and public-use decisions explicitly check claim type, evidence links, source-precedence status, forbidden-claim status, and limitation language before any public artifact is released.
