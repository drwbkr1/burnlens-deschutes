# Objective Five Handoff

Use this document as the first context block for Phase Two or Objective Six.

## One-sentence project state

BurnLens Deschutes has completed Phase One / Objective Five documentation and control work for versioning, provenance, release control, run-package planning, artifact registry planning, source-precedence gates, reproducibility QA, and claim traceability; no Phase Two data, model, map, run, report, public-demo, tag, or GitHub Release work has begun.

## Required boundary

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

This boundary governs every future Phase Two or Objective Six task.

## Current status after Objective Five

| Field | Status |
|---|---|
| Objective Five | Complete after P1O5-T12 merge and final status sync |
| Parent issue | #144; closeable after final sync |
| Last Objective Five task issue | #183 |
| Proposed baseline tag | `v0.0.5-objective-five-traceability` |
| Proposed tag status | Proposed only; not created |
| GitHub Release status | Not created |
| Phase Two data work | Not started |
| AOI selection | Not started |
| Source data acquisition | Not started |
| Labels/masks/baselines/models | Not started |
| Runs/reports/maps/screenshots/public demo | Not started |
| Completed claim register | Not created |
| Completed reproducibility review | Not created |
| Release QA decision | Not created |

## What Objective Five added

Objective Five added the following control layers:

1. Objective tracker and artifact contracts.
2. Current-status reconciliation.
3. Version taxonomy and top-level `VERSIONING.md` updates.
4. Release and tag control.
5. Provenance traceability specification.
6. Future run package and run manifest contract.
7. Artifact registry specification.
8. Claim-to-evidence protocol and claim evidence template.
9. Source-precedence release gate.
10. Reproducibility and release QA checklists.
11. Research validation log.
12. Claims check.
13. Closeout, handoff, and release-note draft.

## Governing artifacts for next work

Do not start Phase Two or Objective Six without these artifacts in context:

```text
README.md
VERSIONING.md
docs/objective-one/TECHNICAL_DESCRIPTION.md
docs/objective-one/USE_BOUNDARIES.md
docs/objective-one/SOURCE_PRECEDENCE.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_CLOSEOUT.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_HANDOFF.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_RELEASE_NOTE.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_TRACKER.md
docs/phase-one/objective-five/VERSION_TAXONOMY.md
docs/phase-one/objective-five/RELEASE_CONTROL.md
docs/phase-one/objective-five/PROVENANCE_TRACEABILITY_SPEC.md
docs/phase-one/objective-five/RUN_PACKAGE_CONTRACT.md
docs/phase-one/objective-five/ARTIFACT_REGISTRY_SPEC.md
docs/phase-one/objective-five/CLAIM_TRACEABILITY_PROTOCOL.md
docs/phase-one/objective-five/SOURCE_PRECEDENCE_RELEASE_GATE.md
docs/phase-one/objective-five/REPRODUCIBILITY_CHECKLIST.md
docs/phase-one/objective-five/RELEASE_QA_CHECKLIST.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_RESEARCH_VALIDATION_LOG.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_CLAIMS_CHECK.md
templates/RELEASE_NOTE_TEMPLATE.md
templates/TRACEABILITY_RECORD_TEMPLATE.md
templates/RUN_MANIFEST_TEMPLATE.json
templates/CLAIM_EVIDENCE_LINK_TEMPLATE.md
records/PROMPT_BUILD_LOG.md
```

## First safe next-task options

Choose one next path before starting new work.

| Path | Safe first task | What it may do | What it must not do yet |
|---|---|---|---|
| Phase Two data-intake preparation | Create a Phase Two parent tracker and first source/AOI intake task issue. | Define intake sequence, required records, allowed files, and stop conditions. | Touch data, download imagery, create AOI files, create labels, create masks, or run processing. |
| Objective Six portfolio packaging | Define Objective Six scope and public-facing portfolio constraints. | Plan how existing documentation/control artifacts will be summarized for portfolio use. | Publish public claims, screenshots, maps, demos, tags, or releases without claim evidence and release QA. |
| Objective Five baseline tagging | Prepare a release QA review for proposed tag `v0.0.5-objective-five-traceability`. | Review whether a tag should be created and what release note would say. | Create the tag or GitHub Release unless explicitly authorized after QA. |

## What must exist before data is touched

A future task may touch source data, imagery, AOI files, labels, masks, baselines, model inputs, or run outputs only after the repo has:

1. a task issue explicitly authorizing the specific data action;
2. a branch and PR scope limiting allowed file changes;
3. source candidate/source record;
4. access method record;
5. license/terms note;
6. format/CRS precheck;
7. AOI record and AOI identifier;
8. provenance or traceability record;
9. artifact registry entry;
10. source-precedence review;
11. use-boundary review;
12. prompt/build log where prompt-assisted edits occur;
13. README/tracker updates if repo truth changes.

If those records are missing, stop before touching data.

## Safe claims going forward

Safe claims must stay narrow:

```text
BurnLens Deschutes has completed documentation and control planning for Objective Five: versioning, provenance, release control, run-package planning, artifact registry planning, source-precedence gates, reproducibility QA, research validation, and claim traceability.
```

```text
BurnLens remains experimental and non-operational. Official sources govern.
```

```text
The proposed Objective Five baseline tag is v0.0.5-objective-five-traceability, but it has not been created unless a later authorized release task creates it.
```

## Claims requiring caveats

| Claim | Required caveat |
|---|---|
| BurnLens has a reproducible workflow plan. | This means documentation and QA controls exist; no executed end-to-end run package exists yet. |
| BurnLens has release controls. | No tag or GitHub Release exists unless a later authorized task creates one. |
| BurnLens has provenance controls. | W3C PROV is used conceptually; no full formal PROV implementation exists. |
| BurnLens uses STAC concepts. | STAC is a future metadata reference; no STAC catalog, item, collection, API, or compliance claim exists. |
| BurnLens can support future portfolio claims. | Future claims still require evidence links, limitations, source-precedence review, and release QA. |

## Unsupported claims

Do not claim:

- BurnLens has started Phase Two data work;
- an AOI has been selected;
- source data has been acquired;
- labels, masks, baselines, models, runs, metrics, maps, reports, screenshots, or public demos exist;
- a completed claim register exists;
- public claims have been approved;
- a completed reproducibility review exists;
- a release QA decision exists;
- `v0.0.5-objective-five-traceability` has been created;
- a GitHub Release exists;
- BurnLens is official, operational, field-validated, agency-endorsed, emergency-ready, production-stable, or suitable for evacuation, routing, tactical, or incident-command support.

## Source-precedence rule

Future artifacts must keep these categories separate:

```text
official/reference sources
reference-derived labels
baseline outputs
model outputs
map overlays
portfolio interpretations
```

BurnLens-derived outputs are always lower priority than official/reference sources. If BurnLens output conflicts with official information, official information governs and the BurnLens output must be caveated, withheld, or superseded.

## Versioning and tag guidance

`VERSIONING.md` was updated during P1O5-T03. The expanded taxonomy is controlled by `VERSION_TAXONOMY.md`.

The proposed Objective Five baseline tag is:

```text
v0.0.5-objective-five-traceability
```

Do not create it automatically. A future tag task must:

1. confirm Objective Five closeout and final status sync are merged;
2. run the release QA checklist;
3. verify the release note is accurate;
4. confirm no unsupported claims are introduced;
5. receive explicit authorization to create the tag;
6. avoid publishing a GitHub Release unless separately authorized.

## Handoff prompt for the next dialogue

```text
We are starting from completed Phase One / Objective Five of BurnLens Deschutes. Use README.md, OBJECTIVE_FIVE_CLOSEOUT.md, OBJECTIVE_FIVE_HANDOFF.md, OBJECTIVE_FIVE_RELEASE_NOTE.md, VERSIONING.md, VERSION_TAXONOMY.md, RELEASE_CONTROL.md, PROVENANCE_TRACEABILITY_SPEC.md, RUN_PACKAGE_CONTRACT.md, ARTIFACT_REGISTRY_SPEC.md, CLAIM_TRACEABILITY_PROTOCOL.md, SOURCE_PRECEDENCE_RELEASE_GATE.md, REPRODUCIBILITY_CHECKLIST.md, RELEASE_QA_CHECKLIST.md, OBJECTIVE_FIVE_RESEARCH_VALIDATION_LOG.md, and OBJECTIVE_FIVE_CLAIMS_CHECK.md as governing context. No Phase Two data work has begun. Do not touch data, select an AOI, download imagery, create labels, create masks, run models, generate maps, publish screenshots, approve public claims, create tags, or create GitHub Releases unless the new task explicitly authorizes that work and the required records/gates exist. Official sources govern.
```

## Stop conditions for the next task

Stop and create a planning/control task instead if the next request implies:

- data download before source/access/precheck records;
- AOI selection before AOI record rules are stated;
- imagery or map output before run-package controls are satisfied;
- model, label, or baseline work before dataset/source/label/method version rules are in place;
- screenshots or public demos before claim evidence and release QA exist;
- tag or GitHub Release creation without explicit authorization;
- any official, operational, emergency, field-validation, agency-endorsement, evacuation, routing, tactical, or incident-command implication.
