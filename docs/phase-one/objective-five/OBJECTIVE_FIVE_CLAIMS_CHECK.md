# Objective Five Claims Check

## Purpose

This record defines what can now be safely said after Phase One / Objective Five research validation, what requires caveats, and what remains unsupported.

It is paired with `OBJECTIVE_FIVE_RESEARCH_VALIDATION_LOG.md` and should be used by P1O5-T12 closeout, future release notes, README updates, portfolio copy, website copy, slide decks, and public-demo materials.

This is documentation and records work only. It does not approve a public claim, create a completed claim-register entry, create a public artifact, create a release, create a tag, create a run package, or start data/model/map work.

## Boundary statement

Experimental BurnLens CV/GEOINT portfolio work. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

## Review metadata

| Field | Value |
|---|---|
| Review ID | `P1O5-CLAIMS-CHECK` |
| Objective | Phase One / Objective Five |
| Task | P1O5-T11 |
| Task issue | #179 |
| Branch | `p1o5t11b` |
| Date checked | 2026-07-09 |
| Paired research record | `OBJECTIVE_FIVE_RESEARCH_VALIDATION_LOG.md` |
| Claim posture | Documentation/control claims only unless later records authorize more. |

## Current safe claims

These claims are safe after P1O5-T11 is merged, assuming current-status artifacts are synchronized and no later artifact contradicts them.

| Claim ID | Safe claim | Required evidence | Required caveat? | Public-use status |
|---|---|---|---|---|
| SAFE-P1O5-001 | BurnLens Deschutes has an Objective Five control baseline for versioning, provenance, release control, run-package planning, artifact registry planning, source-precedence release gates, claim traceability, reproducibility review, release QA, research validation, and claims review. | Merged Objective Five artifacts from P1O5-T01 through P1O5-T11; tracker; README; prompt logs. | Yes: documentation/control baseline only. | Allowed with caveat. |
| SAFE-P1O5-002 | BurnLens uses SemVer-style version semantics only for software-like release classes such as app/site, baseline, model, and report-template versions. | `VERSION_TAXONOMY.md`; `VERSIONING.md`; SemVer source in research log. | Yes: not all identifiers are SemVer. | Allowed with caveat. |
| SAFE-P1O5-003 | BurnLens may use Git tags as future objective-baseline markers after closeout approval and status synchronization. | `RELEASE_CONTROL.md`; `RELEASE_QA_CHECKLIST.md`; GitHub release/tag sources in research log. | Yes: no tag is created by Objective Five tasks before explicit approval. | Allowed with caveat. |
| SAFE-P1O5-004 | BurnLens treats GitHub Releases as public-facing release objects that require stricter gates than ordinary documentation PRs. | GitHub release docs; `RELEASE_CONTROL.md`; `RELEASE_QA_CHECKLIST.md`. | Yes: documentation-only baselines usually use release notes rather than GitHub Releases by default. | Allowed with caveat. |
| SAFE-P1O5-005 | BurnLens uses W3C PROV as a conceptual model for source-to-processing-to-output-to-claim traceability. | W3C PROV sources; `PROVENANCE_TRACEABILITY_SPEC.md`; `TRACEABILITY_RECORD_TEMPLATE.md`. | Yes: no full formal PROV implementation exists yet. | Allowed with caveat. |
| SAFE-P1O5-006 | BurnLens uses STAC as a future geospatial asset metadata reference, not as a Phase One compliance target. | OGC STAC source; `RUN_PACKAGE_CONTRACT.md`; `RUN_MANIFEST_TEMPLATE.json`; `ARTIFACT_REGISTRY_SPEC.md`. | Yes: no STAC catalog, collection, item, or API exists. | Allowed with caveat. |
| SAFE-P1O5-007 | BurnLens future public claims must link to evidence and must not be stronger than repo records support. | `CLAIM_TRACEABILITY_PROTOCOL.md`; `CLAIM_EVIDENCE_LINK_TEMPLATE.md`; `RELEASE_QA_CHECKLIST.md`. | Yes: actual public claims still require completed claim evidence. | Allowed with caveat. |
| SAFE-P1O5-008 | BurnLens future public artifacts involving derived outputs must preserve source precedence and release status review. | `SOURCE_PRECEDENCE_RELEASE_GATE.md`; `RELEASE_QA_CHECKLIST.md`; `SOURCE_PRECEDENCE.md`. | Yes: no derived outputs exist yet. | Allowed with caveat. |
| SAFE-P1O5-009 | BurnLens future objective baselines, datasets, model/baseline packages, run/report packages, and public demos have reusable reproducibility and release QA checklists. | `REPRODUCIBILITY_CHECKLIST.md`; `RELEASE_QA_CHECKLIST.md`. | Yes: checklists exist; completed reviews do not. | Allowed with caveat. |
| SAFE-P1O5-010 | BurnLens remains an experimental portfolio project with official sources governing when information differs. | README; `USE_BOUNDARIES.md`; `SOURCE_PRECEDENCE.md`; Objective Five artifacts. | Always include boundary language when public-facing. | Required public posture. |

## Claims that require caveats

These claims may be used only when the caveat is included nearby and the supporting artifact is current.

| Claim ID | Claim pattern | Required caveat | Evidence required before use | Status |
|---|---|---|---|---|
| CAVEAT-P1O5-001 | `BurnLens has a reproducible workflow plan.` | State that this is a documented workflow/control plan, not an executed end-to-end run. | README; run package contract; reproducibility checklist. | Allowed with caveat. |
| CAVEAT-P1O5-002 | `BurnLens has release controls.` | State that no release, tag, or GitHub Release has been created unless a later closeout task explicitly does so. | `RELEASE_CONTROL.md`; release QA checklist; current status. | Allowed with caveat. |
| CAVEAT-P1O5-003 | `BurnLens has provenance controls.` | State that controls are documentation/template-based and not a formal PROV graph or serialization. | Provenance spec; traceability template; research validation log. | Allowed with caveat. |
| CAVEAT-P1O5-004 | `BurnLens has run-package controls.` | State that no run package or `/runs/` folder exists yet. | Run package contract; run manifest template; README. | Allowed with caveat. |
| CAVEAT-P1O5-005 | `BurnLens has QA controls.` | State that no completed reproducibility review or release QA decision exists yet. | Reproducibility checklist; release QA checklist; tracker. | Allowed with caveat. |
| CAVEAT-P1O5-006 | `BurnLens can support future public portfolio claims.` | State that future public claims require evidence links, limitation statements, source-precedence review, and release QA. | Claim protocol; claim evidence template; release QA checklist. | Allowed with caveat. |
| CAVEAT-P1O5-007 | `BurnLens uses STAC-informed metadata ideas.` | State that this is a future metadata reference only, not STAC compliance. | OGC STAC source; run package contract; artifact registry spec. | Allowed with caveat. |
| CAVEAT-P1O5-008 | `BurnLens is ready for Phase Two intake planning.` | State that Phase Two intake is not started until later task authorization and intake records exist. | Objective Five closeout/handoff after P1O5-T12; current status. | Deferred until T12. |

## Unsupported claims

These claims remain unsupported after P1O5-T11 and must not be used in README, release notes, portfolio copy, website copy, public demos, slide decks, or stakeholder-facing summaries.

| Claim ID | Unsupported claim | Why unsupported | What would be required to revisit |
|---|---|---|---|
| UNSUP-P1O5-001 | Objective Five is complete. | P1O5-T12 closeout is still pending. | P1O5-T12 closeout and handoff merged. |
| UNSUP-P1O5-002 | A tag, objective baseline, or GitHub Release has been created. | T11 does not create tags or releases. | Explicit closeout/release-control approval and completed release action. |
| UNSUP-P1O5-003 | BurnLens is SemVer-compliant for every identifier. | Many BurnLens IDs are non-SemVer traceability identifiers. | Only claim SemVer for version classes assigned in taxonomy. |
| UNSUP-P1O5-004 | BurnLens implements full W3C PROV. | Objective Five uses PROV conceptually only. | Formal PROV implementation, serialization, and validation task. |
| UNSUP-P1O5-005 | BurnLens is STAC-compliant or publishes a STAC catalog. | STAC is a future metadata reference only. | Explicit STAC implementation and conformance review. |
| UNSUP-P1O5-006 | BurnLens has selected an AOI or acquired source data. | No AOI selection or source-data acquisition has been authorized. | Later intake task with AOI/source records. |
| UNSUP-P1O5-007 | BurnLens has created labels, masks, baselines, model outputs, maps, reports, screenshots, or public demos. | Objective Five is documentation/control work only. | Later authorized task that creates and records those artifacts. |
| UNSUP-P1O5-008 | BurnLens has completed a reproducibility review or release QA decision. | T10 created reusable checklists only. | Completed review record for a specific release candidate. |
| UNSUP-P1O5-009 | BurnLens has approved public-facing claims. | T08/T11 define claim controls; no completed claim register or public approval exists. | Completed claim-register entry and release QA decision. |
| UNSUP-P1O5-010 | BurnLens outputs are official, operational, field-validated, emergency-ready, agency-endorsed, or suitable for evacuation/routing/tactical/incident-command support. | Current governing boundary explicitly blocks these claims. | Not supported under current project boundary. |

## Public wording guidance

### Safer wording

Use wording like:

```text
BurnLens Deschutes is an experimental CV/GEOINT portfolio project with documented controls for versioning, provenance, release review, source precedence, reproducibility review, and claim traceability.
```

```text
Objective Five documents the control system BurnLens will use before future data, model, run, map, or public-demo artifacts are treated as reviewable or public-facing.
```

```text
BurnLens uses W3C PROV concepts as a lightweight lineage model and treats STAC as a future reference for geospatial asset metadata; neither is fully implemented in Phase One.
```

### Wording that must be caveated

Use only with adjacent limitations:

```text
BurnLens has a reproducible workflow plan.
```

Required adjacent limitation:

```text
This means the workflow controls and review checklists are documented; no end-to-end run package or output has been created yet.
```

```text
BurnLens has release controls.
```

Required adjacent limitation:

```text
This does not mean a tag, GitHub Release, dataset release, model release, or public demo release has been created.
```

### Wording to block

Do not use wording like:

```text
BurnLens is ready for operational wildfire use.
```

```text
BurnLens has validated wildfire outputs.
```

```text
BurnLens publishes official fire information.
```

```text
BurnLens has a production-ready model, dataset, map, or public demo.
```

```text
BurnLens is STAC-compliant or PROV-compliant.
```

## Claim-to-evidence matrix

| Claim category | Minimum evidence before public use | Current status after T11 | Public posture |
|---|---|---|---|
| Objective Five scope claim | Merged Objective Five artifacts and current status. | Mostly satisfied, pending T12 closeout for full objective-complete wording. | Allowed with caveat. |
| Research-backed decision claim | Research validation log and affected artifact. | Satisfied for SemVer, GitHub release/tag, PROV, STAC, and experimental posture claims. | Allowed with caveat. |
| Control-system maturity claim | Merged docs, templates, tracker, prompt logs. | Satisfied for documentation/control maturity. | Allowed with caveat. |
| Phase Two intake-readiness claim | Objective Five closeout and explicit Phase Two handoff. | Pending T12. | Deferred. |
| Data-readiness claim | AOI/source/access/CRS/provenance records. | Not satisfied. | Unsupported. |
| Model claim | Dataset/label/model/method/metrics/model-card records. | Not satisfied. | Unsupported. |
| Map/output claim | Run ID, run manifest, output inventory, source-precedence note, warning, checksum status. | Not satisfied. | Unsupported. |
| Public portfolio output claim | Claim-register entry, limitation statement, release QA decision, supporting registry entries. | Not satisfied. | Unsupported. |

## Required caveat package for future public summaries

When summarizing Objective Five publicly, include these elements:

1. BurnLens is experimental portfolio work.
2. Official sources govern.
3. Objective Five created documentation/control artifacts, not data/model/map/run outputs.
4. W3C PROV and STAC are conceptual/reference inputs at this stage, not implemented compliance targets.
5. Public claims require evidence links and release QA.

## Claims-review checklist

| Check | Status | Notes |
|---|---|---|
| Safe claims listed. | Satisfied | Safe claims table included. |
| Caveated claims listed. | Satisfied | Caveat table included. |
| Unsupported claims listed. | Satisfied | Unsupported table included. |
| Evidence requirement stated. | Satisfied | Claim-to-evidence matrix included. |
| Public wording guidance included. | Satisfied | Safer, caveated, and blocked wording sections included. |
| Boundary language preserved. | Satisfied | Required boundary statement included. |
| No public claim approved. | Satisfied | This is a claims check, not a completed claim-register entry. |

## Handoff

Use this claims check in P1O5-T12 closeout. The Objective Five closeout and release note should include only safe claims, preserve the required caveats, and repeat unsupported-claim exclusions clearly.
