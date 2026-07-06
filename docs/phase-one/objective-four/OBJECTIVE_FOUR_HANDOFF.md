# Objective Four Handoff

## First context block for Objective Five or Phase Two

BurnLens Deschutes is an experimental, portfolio-first computer vision and GEOINT wildfire screening project for Deschutes County, Oregon. It is not official wildfire information, not emergency guidance, and not evacuation, routing, tactical, or incident-command support. Official sources govern.

Objective Four created the repository operating system for future work: issue architecture, issue taxonomy, project board specification, branch/PR workflow, issue and PR templates, Codex guidance, Codex task packet, prompt/build log protocol, Phase Two intake templates, and closeout/handoff docs.

Use this handoff before starting Objective Five or Phase Two.

## Current objective state

- Phase One / Objective Four task issues #117 through #127 are merged/closed.
- Task 11 issue #128 should close when this handoff PR merges.
- Parent issue #119 should remain open until the release/tag note is complete.
- Objective Four has prepared future data intake, but it has not started data work.

## Core rule

The next objective may use the repo standards and intake templates. It must not treat them as completed data records.

Templates are scaffolding. They do not mean an AOI has been selected, a source has been approved, data has been downloaded, CRS has been checked, provenance has been established, claims have been approved, or no-go decisions have been made.

## Required workflow for next task

Use this loop for every task:

```text
artifact contract -> issue comment -> task branch -> fresh research -> artifact file -> self-audit -> PR -> review -> squash merge -> issue/parent/tracker update
```

After Task 9, prompt-assisted work also needs a prompt/build log entry when it changes files or creates task artifacts.

## Governing files

Read these first:

```text
AGENTS.md
.github/ISSUE_TEMPLATE/task.yml
.github/PULL_REQUEST_TEMPLATE.md
docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md
docs/phase-one/objective-four/ISSUE_ARCHITECTURE.md
docs/phase-one/objective-four/ISSUE_TAXONOMY.md
docs/phase-one/objective-four/PROJECT_BOARD_SPEC.md
templates/CODEX_TASK_PACKET.md
records/PROMPT_BUILD_LOG.md
templates/PROMPT_LOG_ENTRY.md
docs/phase-one/objective-four/OBJECTIVE_FOUR_CLOSEOUT.md
```

For Phase Two intake, use these templates:

```text
templates/AOI_RECORD_TEMPLATE.md
templates/SOURCE_RECORD_TEMPLATE.md
templates/ACCESS_LOG_TEMPLATE.md
templates/FORMAT_CRS_PRECHECK_TEMPLATE.md
templates/PROVENANCE_MANIFEST_TEMPLATE.json
templates/CLAIM_REGISTER_ENTRY_TEMPLATE.md
templates/NO_GO_SOURCE_NOTE_TEMPLATE.md
```

## What is ready

The repo is ready to create:

- AOI candidate records;
- source candidate records;
- access logs;
- format/CRS prechecks;
- provenance manifests;
- claim-register entries;
- no-go source or claim notes;
- prompt/build log entries;
- task-scoped issues and PRs;
- release notes and objective-level handoffs.

## What remains prohibited

Do not create or perform the following until a later task explicitly authorizes them and the required intake records exist:

- final AOI selection;
- source data download;
- imagery download;
- retained raw data;
- preprocessing;
- labels;
- masks;
- baseline outputs;
- model inputs;
- model training;
- inference;
- metrics;
- raster/vector outputs;
- public map outputs;
- website demo integration;
- operational wildfire claims;
- official, field-validation, agency-endorsement, emergency-readiness, evacuation, routing, tactical, or incident-command claims.

## Before touching data

Before any data is touched, create and review the following records in this order:

1. Task issue and artifact contract.
2. Prompt/build log entry for prompt-assisted work.
3. AOI record.
4. Source record.
5. Access log.
6. Format/CRS precheck.
7. Provenance manifest.
8. Claim-register entry for any statement the work may support.
9. No-go note for any rejected/deferred source, AOI, claim, access route, or CRS issue.

The access log should not record credentials. The source record must document terms/license. The precheck must record CRS/format decisions. The provenance manifest must link records before data enters any later processing chain.

## Required warning language

Use this warning, or a tighter equivalent, for future public-facing outputs:

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

## Allowed phrasing

Use language such as:

- This output shows...
- This record indicates...
- This layer overlaps...
- This result should be compared with official sources...
- This source is approved/deferred/rejected for experimental BurnLens use only...

Avoid language such as:

- safe;
- unsafe;
- evacuate;
- use this route;
- official hazard;
- confirmed fire perimeter;
- emergency guidance;
- operationally validated;
- agency endorsed.

## Phase Two starting recommendation

If Phase Two begins next, start with an issue for the first AOI/source-intake planning task. The task should not download data. It should create a candidate AOI record and identify candidate official/primary sources that need source records.

Recommended first Phase Two task shape:

```text
Task: Create first candidate AOI/source intake record set
Artifacts:
- records/phase-two/aoi/AOI-YYYY-NNN.md
- records/phase-two/sources/SRC-YYYY-NNN.md
- records/prompt-build-log/YYYY-MM-DD-phase-two-intake.md
Boundary: no data download; no labels; no masks; no outputs; no maps.
```

## Objective Five starting recommendation

If Objective Five begins before Phase Two, start by defining exactly what Objective Five is meant to produce and which Objective Four standards govern it. Create an objective parent issue, task sequence, artifact contracts, and prompt/build log entries before writing new deliverables.

## Handoff checklist

Before proceeding, confirm:

- [ ] The next objective or phase has a parent issue.
- [ ] The first task has an artifact contract.
- [ ] A task branch is created from current `main`.
- [ ] Fresh research is completed before current/technical/source claims are written.
- [ ] Prompt/build log entry is created if prompt-assisted work changes files.
- [ ] Required intake records exist before any data is touched.
- [ ] The task PR closes only the task issue, not the parent issue.
- [ ] Official source precedence and BurnLens boundary language are preserved.

## One-paragraph handoff summary

Objective Four established the BurnLens repository operating system: issue architecture, taxonomy, project-board rules, branch/PR workflow, templates, Codex instructions, task packets, prompt/build logging, Phase Two intake templates, and closeout/handoff standards. Future work should use these artifacts as controlling context. Phase Two is ready to begin intake records, but not data use. Before any data is touched, create AOI, source, access, format/CRS, provenance, claims, no-go, and prompt-log records. BurnLens remains experimental, non-official, and non-emergency; official sources govern.
