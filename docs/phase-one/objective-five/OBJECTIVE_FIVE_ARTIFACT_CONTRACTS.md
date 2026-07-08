# Objective Five Artifact Contracts

## Purpose

This file defines the artifact contracts for Phase One / Objective Five before detailed task work begins.

Objective Five is the traceability-hardening objective for BurnLens Deschutes. It converts repo, version, provenance, source-precedence, and claims-control expectations into reviewable task artifacts that later phases can use before data, model, run, map, or public-demo work begins.

This file is a planning and control artifact. It does not create releases, select an AOI, approve a source, download data, create labels, create masks, generate baselines, train models, run inference, compute metrics, publish maps, or update the public website.

## Universal boundary statement

Experimental BurnLens CV/GEOINT portfolio work. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

## Universal artifact requirements

Every Objective Five task artifact should include, where applicable:

| Required section | Purpose |
|---|---|
| Purpose | State why the artifact exists and what later work it controls. |
| Scope boundary | State what the artifact does and does not authorize. |
| Controlling docs | List repo docs and project-source records consulted. |
| Research basis | Record current/technical/source claims and source links when required. |
| Decision or result | Make the task decision explicit. |
| Acceptance criteria | Define what must be true before the task can merge. |
| Rejection or defer criteria | Define what should block or narrow the task. |
| Versioning/provenance implications | State how the artifact affects traceability. |
| Boundary and source-precedence check | Confirm official sources govern and unsupported claims are excluded. |
| Claims check | Separate safe claims from unsupported claims. |
| Handoff | Tell the next task what to use and what remains unresolved. |

## Universal forbidden work

No Objective Five task may do any of the following unless a later user instruction explicitly changes the phase boundary and the repo contains the required gate records:

- final AOI selection;
- source data acquisition;
- imagery download;
- retained source data;
- preprocessing;
- labels;
- masks;
- baseline outputs;
- model inputs;
- model training;
- inference;
- metric computation;
- raster/vector processing outputs;
- map publication;
- website demo integration;
- public operational claims;
- official, field-validation, agency-endorsement, emergency-readiness, evacuation, routing, tactical, or incident-command claims.

## Task contract summary

| Task | Issue | Primary artifact(s) | Contract type | Research requirement | Expected handoff |
|---|---:|---|---|---|---|
| P1O5-T01 | #145 | `OBJECTIVE_FIVE_TRACKER.md`; `OBJECTIVE_FIVE_ARTIFACT_CONTRACTS.md`; P1O5-T01 prompt log | Objective setup | Controlling docs only | P1O5-T02 |
| P1O5-T02 | #146 | `CURRENT_STATUS_RECONCILIATION.md`; README update if needed; P1O5-T02 prompt log | Status reconciliation | Repo state / issue records | P1O5-T03 |
| P1O5-T03 | planned | `VERSION_TAXONOMY.md`; `VERSIONING.md` if protocol changes | Versioning protocol | Fresh external / primary sources required | P1O5-T04 and P1O5-T05 |
| P1O5-T04 | planned | `RELEASE_CONTROL.md`; `templates/RELEASE_NOTE_TEMPLATE.md` | Release control | Fresh external / primary sources required | P1O5-T05 or T06 |
| P1O5-T05 | planned | `PROVENANCE_TRACEABILITY_SPEC.md`; `templates/TRACEABILITY_RECORD_TEMPLATE.md` | Provenance | Fresh external / primary sources required | P1O5-T06 |
| P1O5-T06 | planned | `RUN_PACKAGE_CONTRACT.md`; `templates/RUN_MANIFEST_TEMPLATE.json` | Run package contract | Fresh research if metadata standards are invoked | P1O5-T07 |
| P1O5-T07 | planned | `ARTIFACT_REGISTRY_SPEC.md` | Registry | Conditional | P1O5-T08 |
| P1O5-T08 | planned | `CLAIM_TRACEABILITY_PROTOCOL.md`; `templates/CLAIM_EVIDENCE_LINK_TEMPLATE.md` | Claims control | Conditional | P1O5-T09 |
| P1O5-T09 | planned | `SOURCE_PRECEDENCE_RELEASE_GATE.md` | Source precedence | Conditional | P1O5-T10 |
| P1O5-T10 | planned | `REPRODUCIBILITY_CHECKLIST.md`; `RELEASE_QA_CHECKLIST.md` | QA/release control | Conditional | P1O5-T11 |
| P1O5-T11 | planned | `OBJECTIVE_FIVE_RESEARCH_VALIDATION_LOG.md`; `OBJECTIVE_FIVE_CLAIMS_CHECK.md` | Research/claims record | Required, based on T03-T10 | P1O5-T12 |
| P1O5-T12 | planned | `OBJECTIVE_FIVE_CLOSEOUT.md`; `OBJECTIVE_FIVE_HANDOFF.md`; `OBJECTIVE_FIVE_RELEASE_NOTE.md` | Closeout/handoff | Merged artifacts govern | Phase Two or next objective |

## P1O5-T01 contract

| Field | Requirement |
|---|---|
| Task ID | P1O5-T01 |
| Parent issue | #144 |
| Task issue | #145 |
| Branch | `p1o5t01b` |
| PR title | `P1O5-T01 Create Objective Five tracker and artifact contracts` |
| Primary artifacts | `docs/phase-one/objective-five/OBJECTIVE_FIVE_TRACKER.md`; `docs/phase-one/objective-five/OBJECTIVE_FIVE_ARTIFACT_CONTRACTS.md`; `records/prompt-build-log/2026-07-07-p1o5-t01.md` |
| Adjacent artifacts | `records/PROMPT_BUILD_LOG.md` index update if needed |
| Required decisions | Parent issue, task issue, branch, task sequence, boundary, handoff to T02 |
| Research required | No external research required; controlling repo docs and SOP govern |
| PR close keyword | `Closes #145` only |

Acceptance criteria:

- parent issue #144 exists;
- task issue #145 exists;
- P1O5-T02 issue #146 exists or is named as the next planned task;
- `p1o5t01b` is the task branch;
- artifact contract is posted to #145;
- tracker exists;
- this artifact-contract file exists;
- prompt/build log entry exists;
- prompt/build log index is updated if needed;
- boundary and source-precedence language are present;
- claims check is present;
- handoff identifies P1O5-T02.

Reject or revise if:

- the artifact sequence authorizes data/model/map work;
- the tracker implies Objective Five is complete;
- the tracker implies Phase Two has begun;
- the prompt/build log records private reasoning or secrets;
- the PR closes parent #144.

## P1O5-T02 contract

| Field | Requirement |
|---|---|
| Task ID | P1O5-T02 |
| Parent issue | #144 |
| Task issue | #146 |
| Branch | `p1o5t02b` |
| Primary artifact | `docs/phase-one/objective-five/CURRENT_STATUS_RECONCILIATION.md` |
| Adjacent artifacts | `README.md` if current status/control handoff is stale; `records/prompt-build-log/2026-07-07-p1o5-t02.md`; prompt-log index if needed |
| Required decisions | Confirm live Objective Four status, current Phase One status, current controlling handoff, and whether README needs update |
| Research required | Repo state and issue/PR records; no external research expected |
| PR close keyword | `Closes #146` only |

Acceptance criteria:

- current status memo exists;
- Objective Four issue and release-note status are checked against GitHub records;
- README is updated only if top-level status, handoff, repo structure, or version posture is stale;
- old objective records are not rewritten except for factual correction explicitly in scope;
- boundary and unsupported-claims checks are present;
- handoff identifies P1O5-T03.

Reject or revise if:

- it silently rewrites archival Objective Four records;
- it updates README without a truth change;
- it creates data/model/map/public-output work;
- it overstates the release/tag state.

## P1O5-T03 contract

| Field | Requirement |
|---|---|
| Task ID | P1O5-T03 |
| Parent issue | #144 |
| Recommended branch | `p1o5t03b` |
| Primary artifacts | `docs/phase-one/objective-five/VERSION_TAXONOMY.md`; `VERSIONING.md` if protocol changes |
| Required decisions | Define version taxonomy and increment rules for objective baselines, app/site, AOI, sources, datasets, label schemas, baselines, models, runs, and reports |
| Research required | Yes. Use primary sources for software versioning and repository release/version semantics. |
| PR close keyword | Task issue only |

Acceptance criteria:

- version classes are separated;
- examples are included;
- protocol changes are reflected in `VERSIONING.md` only if needed;
- version numbers do not imply operational readiness;
- no data/model/map work is created.

## P1O5-T04 contract

| Field | Requirement |
|---|---|
| Task ID | P1O5-T04 |
| Parent issue | #144 |
| Recommended branch | `p1o5t04b` |
| Primary artifacts | `docs/phase-one/objective-five/RELEASE_CONTROL.md`; `templates/RELEASE_NOTE_TEMPLATE.md` |
| Required decisions | Define objective baseline release notes, tag/release eligibility, release classes, and do-not-release triggers |
| Research required | Yes. Use GitHub release/tag documentation and existing repo workflow. |
| PR close keyword | Task issue only |

Acceptance criteria:

- release classes are defined;
- release notes state included and excluded work;
- release gates include boundary and source-precedence checks;
- release/tag creation cannot imply data/model/map/public-output readiness unless those artifacts exist.

## P1O5-T05 contract

| Field | Requirement |
|---|---|
| Task ID | P1O5-T05 |
| Parent issue | #144 |
| Recommended branch | `p1o5t05b` |
| Primary artifacts | `docs/phase-one/objective-five/PROVENANCE_TRACEABILITY_SPEC.md`; `templates/TRACEABILITY_RECORD_TEMPLATE.md` |
| Required decisions | Define BurnLens source-to-output-to-claim traceability chain and required provenance fields |
| Research required | Yes. Use W3C PROV or comparable primary provenance references if invoked. |
| PR close keyword | Task issue only |

Acceptance criteria:

- BurnLens entity/activity/agent equivalents are defined;
- source, access, CRS, provenance, method, output, claim, and public language links are specified;
- existing Objective Four intake templates remain scaffolding, not completed records;
- no data is touched.

## P1O5-T06 contract

| Field | Requirement |
|---|---|
| Task ID | P1O5-T06 |
| Parent issue | #144 |
| Recommended branch | `p1o5t06b` |
| Primary artifacts | `docs/phase-one/objective-five/RUN_PACKAGE_CONTRACT.md`; `templates/RUN_MANIFEST_TEMPLATE.json` |
| Required decisions | Define future run folder contents, manifest fields, warning flags, and source-precedence fields |
| Research required | Conditional. Use external metadata standards only if they are cited. |
| PR close keyword | Task issue only |

Acceptance criteria:

- manifest JSON template is valid JSON;
- future outputs are named but not created;
- run ID linkage to commit, version, AOI, source, dataset, method, and warnings is explicit;
- no run package is implied to exist yet.

## P1O5-T07 contract

| Field | Requirement |
|---|---|
| Task ID | P1O5-T07 |
| Parent issue | #144 |
| Recommended branch | `p1o5t07b` |
| Primary artifact | `docs/phase-one/objective-five/ARTIFACT_REGISTRY_SPEC.md` |
| Required decisions | Define artifact classes, registry fields, paths, naming expectations, and template-vs-record separation |
| Research required | Conditional |
| PR close keyword | Task issue only |

Acceptance criteria:

- registry distinguishes templates from completed records;
- official/reference sources remain distinct from BurnLens-derived outputs;
- public artifacts and screenshots require evidence links;
- no public demo work is created.

## P1O5-T08 contract

| Field | Requirement |
|---|---|
| Task ID | P1O5-T08 |
| Parent issue | #144 |
| Recommended branch | `p1o5t08b` |
| Primary artifacts | `docs/phase-one/objective-five/CLAIM_TRACEABILITY_PROTOCOL.md`; `templates/CLAIM_EVIDENCE_LINK_TEMPLATE.md` |
| Required decisions | Define claim categories, evidence requirements, public-language gates, and unsupported-claim handling |
| Research required | Conditional |
| PR close keyword | Task issue only |

Acceptance criteria:

- claim types and evidence requirements are listed;
- public-facing claims cannot exceed repo evidence;
- official, operational, field-validated, emergency-ready, and endorsed claims remain prohibited;
- source-precedence language is preserved.

## P1O5-T09 contract

| Field | Requirement |
|---|---|
| Task ID | P1O5-T09 |
| Parent issue | #144 |
| Recommended branch | `p1o5t09b` |
| Primary artifact | `docs/phase-one/objective-five/SOURCE_PRECEDENCE_RELEASE_GATE.md` |
| Required decisions | Define how official-source conflicts affect release, report status, public display, and withholding decisions |
| Research required | Conditional; existing `SOURCE_PRECEDENCE.md` governs unless new external claims are introduced |
| PR close keyword | Task issue only |

Acceptance criteria:

- release statuses such as normal, provisional, degraded, superseded, or withheld are defined;
- official sources govern;
- conflicting outputs cannot be presented as independent BurnLens conclusions;
- no operational guidance is introduced.

## P1O5-T10 contract

| Field | Requirement |
|---|---|
| Task ID | P1O5-T10 |
| Parent issue | #144 |
| Recommended branch | `p1o5t10b` |
| Primary artifacts | `docs/phase-one/objective-five/REPRODUCIBILITY_CHECKLIST.md`; `docs/phase-one/objective-five/RELEASE_QA_CHECKLIST.md` |
| Required decisions | Define pre-release and reproducibility QA checks for future objective baselines, dataset records, model packages, run packages, and public releases |
| Research required | Conditional |
| PR close keyword | Task issue only |

Acceptance criteria:

- checklist is BurnLens-specific;
- issue/branch/PR/commit/version/source/provenance/run/claim checks are included where relevant;
- tests/checks-not-run language is honest;
- no future tests are claimed to have passed.

## P1O5-T11 contract

| Field | Requirement |
|---|---|
| Task ID | P1O5-T11 |
| Parent issue | #144 |
| Recommended branch | `p1o5t11b` |
| Primary artifacts | `docs/phase-one/objective-five/OBJECTIVE_FIVE_RESEARCH_VALIDATION_LOG.md`; `docs/phase-one/objective-five/OBJECTIVE_FIVE_CLAIMS_CHECK.md` |
| Required decisions | Summarize source-backed decisions and safe/unsupported claims across Objective Five |
| Research required | Yes. Use the sources actually cited in T03-T10. |
| PR close keyword | Task issue only |

Acceptance criteria:

- each research claim links to a source and affected artifact;
- claims are separated into safe, conditional, unsupported, and prohibited where useful;
- unresolved items are handed to T12;
- no unsupported public claim is introduced.

## P1O5-T12 contract

| Field | Requirement |
|---|---|
| Task ID | P1O5-T12 |
| Parent issue | #144 |
| Recommended branch | `p1o5t12b` |
| Primary artifacts | `docs/phase-one/objective-five/OBJECTIVE_FIVE_CLOSEOUT.md`; `docs/phase-one/objective-five/OBJECTIVE_FIVE_HANDOFF.md`; `docs/phase-one/objective-five/OBJECTIVE_FIVE_RELEASE_NOTE.md` |
| Required decisions | Define completion state, governing artifacts, remaining prohibitions, Phase Two readiness, and optional proposed tag |
| Research required | No external research expected; merged Objective Five artifacts govern |
| PR close keyword | Task issue only unless deliberate parent closeout happens after merge review |

Acceptance criteria:

- closeout summarizes completed Objective Five tasks;
- handoff can serve as first context block for Phase Two or next objective;
- release note states what the baseline does and does not authorize;
- parent issue #144 is not closed by the task PR unless explicitly reviewed after release note completion.

## Claims check

Safe claim after P1O5-T01 merge:

```text
BurnLens has an Objective Five tracker and artifact-contract baseline for versioning, provenance, release-control, and claim-traceability work.
```

Unsupported claims after P1O5-T01 merge:

```text
Objective Five is complete; versioning has been fully expanded; release/tag control has been finalized; provenance traceability has been implemented; run packages exist; data/model/map/public-demo work has begun; BurnLens is official, operational, field-validated, emergency-ready, agency-endorsed, or suitable for evacuation, routing, tactical, or incident-command support.
```

## Handoff

P1O5-T02 should use this contract file and `OBJECTIVE_FIVE_TRACKER.md` as the current Objective Five controls. It should reconcile the live repo status and update README only if the top-level status, current controlling handoff, repo structure, or version posture is stale.
