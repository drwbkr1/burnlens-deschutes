# Phase One / Objective Four Closeout

## Status

- Objective: Phase One / Objective Four - Repository Operating System, Issue Architecture, and Codex Work Protocol
- Parent issue: #119
- Completed task issues: #117, #118, #120, #121, #122, #123, #124, #125, #126, #127, #128, #141
- Release-note task issue: #129
- Release note artifact: `docs/phase-one/objective-four/OBJECTIVE_FOUR_RELEASE_NOTE.md`
- Proposed tag: `v0.0.4-objective-four-repo-ops`
- Closeout artifact: `docs/phase-one/objective-four/OBJECTIVE_FOUR_CLOSEOUT.md`
- Handoff artifact: `docs/phase-one/objective-four/OBJECTIVE_FOUR_HANDOFF.md`
- Status after Task 12 artifact drafting: Objective Four repo-control baseline is documented for release-note PR review; tag/release should be created only after merge if desired.

## Purpose

This closeout records what Objective Four created, which issues were closed, which documents now govern future work, what remains prohibited, what is ready for Phase Two, and what must happen before any data is touched.

This closeout is documentation only. It does not start Phase Two data work.

## Boundary warning

Experimental BurnLens repository-transition record. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

## What Objective Four created

| Area | Created artifact(s) | Purpose |
|---|---|---|
| Objective tracking | `docs/phase-one/objective-four/OBJECTIVE_FOUR_TRACKER.md` | Current status map for Objective Four task sequence, governing artifacts, and release-note work. |
| Issue architecture | `docs/phase-one/objective-four/ISSUE_ARCHITECTURE.md` | Defines parent/task issue structure and how task work is organized. |
| Issue taxonomy | `docs/phase-one/objective-four/ISSUE_TAXONOMY.md` | Defines labels, issue types, milestones, and classification logic. |
| Project board specification | `docs/phase-one/objective-four/PROJECT_BOARD_SPEC.md` | Defines project board fields, views, automation expectations, and review use. |
| Branch/PR workflow | `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md` | Defines branch naming, PR titles, close keywords, merge order, review checks, and post-merge updates. |
| Issue and PR templates | `.github/ISSUE_TEMPLATE/task.yml`; `.github/ISSUE_TEMPLATE/config.yml`; `.github/PULL_REQUEST_TEMPLATE.md` | Makes future task and PR creation consistent. |
| Codex guidance | `AGENTS.md` | Gives Codex and prompt-assisted work repo-level project instructions, boundaries, and verification expectations. |
| Codex task packet | `templates/CODEX_TASK_PACKET.md` | Provides a reusable task-packet format for scoped Codex or prompt-assisted tasks. |
| Prompt/build log protocol | `records/PROMPT_BUILD_LOG.md`; `templates/PROMPT_LOG_ENTRY.md` | Defines how prompt-assisted work is logged, what must be recorded, and what must not be recorded. |
| Phase Two intake templates | `templates/AOI_RECORD_TEMPLATE.md`; `templates/SOURCE_RECORD_TEMPLATE.md`; `templates/ACCESS_LOG_TEMPLATE.md`; `templates/FORMAT_CRS_PRECHECK_TEMPLATE.md`; `templates/PROVENANCE_MANIFEST_TEMPLATE.json`; `templates/CLAIM_REGISTER_ENTRY_TEMPLATE.md`; `templates/NO_GO_SOURCE_NOTE_TEMPLATE.md` | Prepares blank records for future AOI, source, access, CRS, provenance, claims, and no-go decisions before data use. |
| Prompt log entries | `records/prompt-build-log/2026-07-06-p1o4-t10.md`; `records/prompt-build-log/2026-07-06-p1o4-t11.md`; `records/prompt-build-log/2026-07-06-p1o4-qa.md`; `records/prompt-build-log/2026-07-06-p1o4-t12.md` | Records prompt-assisted work from the point the prompt/build log protocol became active. |
| Closeout and handoff | `docs/phase-one/objective-four/OBJECTIVE_FOUR_CLOSEOUT.md`; `docs/phase-one/objective-four/OBJECTIVE_FOUR_HANDOFF.md` | Provides transition standard and first-context block for Objective Five or Phase Two. |
| Release note | `docs/phase-one/objective-four/OBJECTIVE_FOUR_RELEASE_NOTE.md` | Summarizes the Objective Four repo-operations baseline and proposed tag. |

## Issues closed or expected to close

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
| P1O4-T11 | #128 | #140 | Closed/merged. |
| P1O4-QA | #141 | #142 | Closed/merged. |
| P1O4-T12 | #129 | pending | Should close when the release-note PR merges. |

## Documents that govern future work

Future work should treat these documents as controlling repo standards:

1. `AGENTS.md`
2. `.github/ISSUE_TEMPLATE/task.yml`
3. `.github/PULL_REQUEST_TEMPLATE.md`
4. `docs/phase-one/objective-four/OBJECTIVE_FOUR_TRACKER.md`
5. `docs/phase-one/objective-four/ISSUE_ARCHITECTURE.md`
6. `docs/phase-one/objective-four/ISSUE_TAXONOMY.md`
7. `docs/phase-one/objective-four/PROJECT_BOARD_SPEC.md`
8. `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md`
9. `templates/CODEX_TASK_PACKET.md`
10. `records/PROMPT_BUILD_LOG.md`
11. `templates/PROMPT_LOG_ENTRY.md`
12. `docs/phase-one/objective-four/OBJECTIVE_FOUR_CLOSEOUT.md`
13. `docs/phase-one/objective-four/OBJECTIVE_FOUR_HANDOFF.md`
14. `docs/phase-one/objective-four/OBJECTIVE_FOUR_RELEASE_NOTE.md`
15. Phase Two intake templates in `templates/`

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

Phase Two can start structured intake records because Objective Four created:

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
| Prompt-assisted work can be logged. | Satisfied | Prompt/build log protocol, entry template, and dated entries exist. |
| Phase Two can begin intake records. | Satisfied | Seven Phase Two intake templates exist. |
| Release-note baseline is drafted. | Satisfied in branch | `OBJECTIVE_FOUR_RELEASE_NOTE.md`. |
| Phase Two data work has begun. | Not satisfied and intentionally prohibited | No selected AOI, downloaded data, labels, masks, model outputs, run outputs, metrics, maps, or public demos were created. |
| Objective Four can be fully closed. | Pending | Release-note PR must merge; optional tag/release can follow. |

## Claims-register check

Safe claims after this Task 12 branch:

```text
BurnLens has a drafted Objective Four release-note baseline for repository operations and Phase Two intake readiness.
```

Unsupported claims after this Task 12 branch:

```text
Objective Four is tagged/released; Phase Two data work has begun; an AOI has been selected; data has been downloaded; labels, masks, model outputs, run outputs, metrics, maps, or public demos have been created; BurnLens is official, operational, field-validated, emergency-ready, or agency-endorsed.
```

## Handoff

Use `docs/phase-one/objective-four/OBJECTIVE_FOUR_HANDOFF.md` as the first context block for Objective Five or Phase Two. Do not begin data work from this closeout alone; begin by creating the required Phase Two intake records. After the release-note PR is reviewed and merged, update parent issue #119 with the final Objective Four completion summary and decide whether to create tag `v0.0.4-objective-four-repo-ops`.
