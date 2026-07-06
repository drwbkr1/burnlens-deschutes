# Phase One / Objective Four Closeout

## Status

- Objective: Phase One / Objective Four - Repository Operating System, Issue Architecture, and Codex Work Protocol
- Parent issue: #119
- Closeout task issue: #128
- Branch: `p1o4t11b`
- Closeout artifact: `docs/phase-one/objective-four/OBJECTIVE_FOUR_CLOSEOUT.md`
- Handoff artifact: `docs/phase-one/objective-four/OBJECTIVE_FOUR_HANDOFF.md`
- Prompt log entry: `records/prompt-build-log/2026-07-06-p1o4-t11.md`
- Status at drafting: Tasks 1 through 10 are merged; Task 11 is in progress; release/tag note remains a later Objective Four step.

## Purpose

This closeout records what Objective Four created, which issues were closed, which documents now govern future work, what remains prohibited, what is ready for Phase Two, and what must happen before any data is touched.

This closeout is documentation only. It does not start Phase Two data work.

## Boundary warning

Experimental BurnLens repository-transition record. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

## What Objective Four created

| Area | Created artifact(s) | Purpose |
|---|---|---|
| Objective tracking | `docs/phase-one/objective-four/OBJECTIVE_FOUR_TRACKER.md` | Tracks Objective Four task sequence, status, dependencies, and completion evidence. |
| Issue architecture | `docs/phase-one/objective-four/ISSUE_ARCHITECTURE.md` | Defines parent/task issue structure and how task work is organized. |
| Issue taxonomy | `docs/phase-one/objective-four/ISSUE_TAXONOMY.md` | Defines labels, issue types, milestones, and classification logic. |
| Project board specification | `docs/phase-one/objective-four/PROJECT_BOARD_SPEC.md` | Defines project board fields, views, automation expectations, and review use. |
| Branch/PR workflow | `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md` | Defines branch naming, PR titles, close keywords, merge order, review checks, and post-merge updates. |
| Issue and PR templates | `.github/ISSUE_TEMPLATE/task.yml`; `.github/ISSUE_TEMPLATE/config.yml`; `.github/PULL_REQUEST_TEMPLATE.md` | Makes future task and PR creation consistent. |
| Codex guidance | `AGENTS.md` | Gives Codex and prompt-assisted work repo-level project instructions, boundaries, and verification expectations. |
| Codex task packet | `templates/CODEX_TASK_PACKET.md` | Provides a reusable task-packet format for scoped Codex or prompt-assisted tasks. |
| Prompt/build log protocol | `records/PROMPT_BUILD_LOG.md`; `templates/PROMPT_LOG_ENTRY.md` | Defines how prompt-assisted work is logged, what must be recorded, and what must not be recorded. |
| Phase Two intake templates | `templates/AOI_RECORD_TEMPLATE.md`; `templates/SOURCE_RECORD_TEMPLATE.md`; `templates/ACCESS_LOG_TEMPLATE.md`; `templates/FORMAT_CRS_PRECHECK_TEMPLATE.md`; `templates/PROVENANCE_MANIFEST_TEMPLATE.json`; `templates/CLAIM_REGISTER_ENTRY_TEMPLATE.md`; `templates/NO_GO_SOURCE_NOTE_TEMPLATE.md` | Prepares blank records for future AOI, source, access, CRS, provenance, claims, and no-go decisions before data use. |
| Prompt log entries | `records/prompt-build-log/2026-07-06-p1o4-t10.md`; `records/prompt-build-log/2026-07-06-p1o4-t11.md` | Records prompt-assisted work from the point the prompt/build log protocol became active. |
| Closeout and handoff | `docs/phase-one/objective-four/OBJECTIVE_FOUR_CLOSEOUT.md`; `docs/phase-one/objective-four/OBJECTIVE_FOUR_HANDOFF.md` | Provides transition standard and first-context block for Objective Five or Phase Two. |

## Issues closed or expected to close

The following task issues were closed by merged task PRs before this closeout was drafted:

| Task | Issue | PR | Status |
|---|---:|---:|---|
| P1O4-T01 | #117 | #133 | Closed/merged. |
| P1O4-T02 | #118 | #130 | Closed/merged. |
| P1O4-T03 | #120 | #131 | Closed/merged. |
| P1O4-T04 | #121 | #132 | Closed/merged. |
| P1O4-T05 | #122 | #134 | Closed/merged. |
| P1O4-T06 | #123 | #135 | Closed/merged. |
| P1O4-T07 | #124 | #136 | Closed/merged. |
| P1O4-T08 | #125 | #137 | Closed/merged. |
| P1O4-T09 | #126 | #138 | Closed/merged. |
| P1O4-T10 | #127 | #139 | Closed/merged. |

Task 11 issue #128 should close when the PR containing this closeout and handoff is merged. The parent issue #119 should remain open until the Objective Four release/tag note is complete and the objective is deliberately closed.

## Documents that govern future work

Future work should treat these documents as controlling repo standards:

1. `AGENTS.md`
2. `.github/ISSUE_TEMPLATE/task.yml`
3. `.github/PULL_REQUEST_TEMPLATE.md`
4. `docs/phase-one/objective-four/ISSUE_ARCHITECTURE.md`
5. `docs/phase-one/objective-four/ISSUE_TAXONOMY.md`
6. `docs/phase-one/objective-four/PROJECT_BOARD_SPEC.md`
7. `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md`
8. `templates/CODEX_TASK_PACKET.md`
9. `records/PROMPT_BUILD_LOG.md`
10. `templates/PROMPT_LOG_ENTRY.md`
11. `docs/phase-one/objective-four/OBJECTIVE_FOUR_HANDOFF.md`
12. Phase Two intake templates in `templates/`

If future instructions conflict, follow the user only when the requested work remains inside BurnLens safety, source-precedence, phase-boundary, and repository-workflow rules.

## What remains prohibited

Objective Four does not authorize any of the following:

- final AOI selection;
- data acquisition or source downloads;
- imagery downloads;
- retained source data;
- labels or masks;
- baseline outputs;
- model training;
- model inference;
- metric computation;
- raster/vector processing outputs;
- map publication;
- website demo integration;
- public operational claims;
- official, field-validation, agency-endorsement, emergency-readiness, evacuation, routing, tactical, or incident-command claims.

## What is ready for Phase Two

Phase Two can now start with a structured intake process because Objective Four has created:

- the issue/branch/PR workflow for scoped data-readiness tasks;
- Codex guidance and task packet structure for prompt-assisted work;
- prompt/build log protocol and entry template;
- AOI record template;
- source record template;
- access log template;
- format/CRS precheck template;
- provenance manifest template;
- claim-register entry template;
- no-go source note template;
- source-precedence and warning language controls.

This means Phase Two can begin intake records, not data use.

## What must happen before data is touched

Before any data is accessed, downloaded, transformed, inspected for model use, labeled, masked, processed, or mapped, the repo must contain a task-specific record set showing:

| Required gate | Required evidence before data use |
|---|---|
| Task authorization | GitHub task issue, artifact contract, branch, and PR workflow. |
| AOI gate | AOI record with purpose, boundary/geometry source, CRS expectation, official-source comparison, and accept/defer/reject decision. |
| Source gate | Source record with provider, metadata, license/terms, coverage, authority, and use decision. |
| Access gate | Access log with method, parameters, terms review, result, storage/checksum plan, and no credentials in repo. |
| Format/CRS gate | Precheck with format, CRS, units, extent, nodata/geometry checks, and conversion/reprojection decision. |
| Provenance gate | Provenance manifest linking AOI, source, access, files, prechecks, later processing steps, outputs, claims, and no-go notes. |
| Claims gate | Claim-register entry for any source, data, output, limitation, or public-language claim. |
| No-go gate | No-go note for rejected/deferred sources, AOIs, access paths, CRS decisions, or claims. |
| Prompt log gate | Prompt/build log entry for prompt-assisted data-intake or processing work. |
| Boundary gate | Explicit confirmation that official sources govern and BurnLens remains experimental and non-emergency. |

If any gate cannot be completed, data use must stop or be deferred until the missing record is resolved.

## Objective Four acceptance review

| Acceptance question | Status | Evidence |
|---|---|---|
| Every future task can be opened as a GitHub issue. | Satisfied | Issue architecture, taxonomy, and task issue template exist. |
| Every future task can run through a branch/PR workflow. | Satisfied | Branch and PR workflow plus PR template exist. |
| Codex/prompt-assisted work has repo instructions. | Satisfied | `AGENTS.md` and `templates/CODEX_TASK_PACKET.md` exist. |
| Prompt-assisted work can be logged. | Satisfied | Prompt/build log protocol and entry template exist. |
| Phase Two can begin intake records. | Satisfied | Seven Phase Two intake templates exist. |
| Phase Two data work has begun. | Not satisfied and intentionally prohibited | No selected AOI, downloaded data, labels, masks, model outputs, run outputs, metrics, maps, or public demos were created. |
| Objective Four can be fully closed. | Deferred | Release/tag note remains a later closeout step. |

## Claims-register check

Safe claims after Task 11 is merged:

```text
BurnLens has an Objective Four closeout and handoff standard for transitioning future work from repository operations into later objectives or Phase Two intake.
```

```text
BurnLens has repository standards, prompt-assisted work controls, and Phase Two intake templates ready for future intake records.
```

Unsupported claims after Task 11:

```text
Phase Two data work has begun; an AOI has been selected; data has been downloaded; labels, masks, model outputs, run outputs, metrics, maps, or public demos have been created; BurnLens is official, operational, field-validated, emergency-ready, or agency-endorsed.
```

## Handoff

Use `docs/phase-one/objective-four/OBJECTIVE_FOUR_HANDOFF.md` as the first context block for Objective Five or Phase Two. Do not begin data work from this closeout alone; begin by creating the required Phase Two intake records.
