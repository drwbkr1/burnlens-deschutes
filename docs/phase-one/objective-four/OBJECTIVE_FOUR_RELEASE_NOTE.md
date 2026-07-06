# Objective Four Release Note

## Release candidate

| Field | Value |
|---|---|
| Objective | Phase One / Objective Four - Repository Operating System, Issue Architecture, and Codex Work Protocol |
| Parent issue | #119 |
| Release-note task issue | #129 |
| Branch | `p1o4t12b` |
| Release note artifact | `docs/phase-one/objective-four/OBJECTIVE_FOUR_RELEASE_NOTE.md` |
| Proposed tag | `v0.0.4-objective-four-repo-ops` |
| Release status | Drafted for PR review; tag/release should be created only after merge |
| Data-work status | Not started and still prohibited |

## Purpose

This release note defines the Objective Four repo-control baseline for BurnLens Deschutes. It summarizes the repository operating system created during Objective Four and records what is ready, what remains prohibited, and what must happen before any Phase Two data work begins.

This release note is documentation only. It does not create a Git tag, GitHub release, data artifact, model artifact, map, website update, or public demo.

## Boundary warning

Experimental BurnLens repository release note. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

## Release summary

Objective Four established a portfolio-level repository operating system for issue-controlled, branch-controlled, PR-reviewed, prompt-logged work.

The baseline includes:

- issue architecture and taxonomy;
- project-board specification;
- branch and PR workflow;
- issue and PR templates;
- repo-level Codex instructions;
- Codex task packet template;
- prompt/build log protocol and entry template;
- Phase Two intake templates;
- closeout and handoff standards;
- QA-refreshed tracker, closeout, handoff, and prompt-log index.

## Completed issues and pull requests

| Work item | Issue | PR | Status |
|---|---:|---:|---|
| Objective Four tracker | #117 | #133 | Merged |
| Issue architecture | #118 | #130 | Merged |
| Issue taxonomy | #120 | #131 | Merged |
| Project board specification | #121 | #132 | Merged |
| Branch and PR workflow | #122 | #134 | Merged |
| Issue and PR templates | #123 | #135 | Merged |
| AGENTS.md Codex instructions | #124 | #136 | Merged |
| Codex task packet | #125 | #137 | Merged |
| Prompt/build log protocol | #126 | #138 | Merged |
| Phase Two intake templates | #127 | #139 | Merged |
| Objective Four closeout and handoff | #128 | #140 | Merged |
| Objective Four quality pass | #141 | #142 | Merged |
| Objective Four release note | #129 | pending | Drafted in this branch |

## Release artifact inventory

| Category | Artifact(s) | Release role |
|---|---|---|
| Tracker | `docs/phase-one/objective-four/OBJECTIVE_FOUR_TRACKER.md` | Current Objective Four task map and portfolio-quality status record. |
| Issue system | `ISSUE_ARCHITECTURE.md`; `ISSUE_TAXONOMY.md`; `.github/ISSUE_TEMPLATE/task.yml`; `.github/ISSUE_TEMPLATE/config.yml` | Governs issue creation, classification, and task identity. |
| Project board | `PROJECT_BOARD_SPEC.md` | Defines project-board fields/views/status logic. |
| PR system | `BRANCH_AND_PR_WORKFLOW.md`; `.github/PULL_REQUEST_TEMPLATE.md` | Governs branch naming, PR rules, close keywords, merge order, review, and handoff updates. |
| Codex/prompt work | `AGENTS.md`; `templates/CODEX_TASK_PACKET.md` | Gives prompt-assisted and Codex-assisted work project rules and task-packet format. |
| Prompt/build logging | `records/PROMPT_BUILD_LOG.md`; `templates/PROMPT_LOG_ENTRY.md`; entries under `records/prompt-build-log/` | Records prompt-assisted work and evidence without exposing private reasoning or secrets. |
| Phase Two readiness | `templates/AOI_RECORD_TEMPLATE.md`; `templates/SOURCE_RECORD_TEMPLATE.md`; `templates/ACCESS_LOG_TEMPLATE.md`; `templates/FORMAT_CRS_PRECHECK_TEMPLATE.md`; `templates/PROVENANCE_MANIFEST_TEMPLATE.json`; `templates/CLAIM_REGISTER_ENTRY_TEMPLATE.md`; `templates/NO_GO_SOURCE_NOTE_TEMPLATE.md` | Creates blank intake scaffolding before data use. |
| Transition | `OBJECTIVE_FOUR_CLOSEOUT.md`; `OBJECTIVE_FOUR_HANDOFF.md`; this release note | Defines transition state and first context block for Objective Five or Phase Two. |

## Governing documents after release

Future work should begin from these files:

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
14. Phase Two intake templates in `templates/`

## What is ready for Phase Two

Phase Two is ready to begin intake records, not data work.

Ready now:

- candidate AOI record creation;
- candidate source record creation;
- access log creation;
- format/CRS precheck planning;
- provenance manifest creation;
- claim-register entry creation;
- no-go source/claim note creation;
- prompt/build logging for intake work;
- task-scoped GitHub issues and PRs for each intake step.

## What remains prohibited

This release does not authorize:

- final AOI selection;
- data acquisition or source downloads;
- imagery downloads;
- retained source data;
- preprocessing;
- labels;
- masks;
- baseline outputs;
- model inputs;
- model training;
- model inference;
- metric computation;
- raster/vector processing outputs;
- map publication;
- website demo integration;
- public operational claims;
- official, field-validation, agency-endorsement, emergency-readiness, evacuation, routing, tactical, or incident-command claims.

## Before any data is touched

Before any data is accessed, downloaded, transformed, inspected for model use, labeled, masked, processed, or mapped, the repo must contain task-specific evidence for these gates:

| Gate | Required evidence |
|---|---|
| Task authorization | GitHub task issue, artifact contract, branch, and PR workflow. |
| Prompt log | Prompt/build log entry for prompt-assisted intake or processing work. |
| AOI | AOI record with purpose, boundary/geometry source, CRS expectation, official-source comparison, and accept/defer/reject decision. |
| Source | Source record with provider, metadata, license/terms, coverage, authority, and use decision. |
| Access | Access log with method, parameters, terms review, result, storage/checksum plan, and no credentials in repo. |
| Format/CRS | Precheck with format, CRS, units, extent, nodata/geometry checks, and conversion/reprojection decision. |
| Provenance | Manifest linking AOI, source, access, files, prechecks, later processing steps, outputs, claims, and no-go notes. |
| Claims | Claim-register entry for any source, data, output, limitation, or public-language claim. |
| No-go | No-go note for rejected/deferred sources, AOIs, access paths, CRS decisions, or claims. |
| Boundary | Explicit confirmation that official sources govern and BurnLens remains experimental and non-emergency. |

If any gate cannot be completed, data use must stop or be deferred.

## Proposed tag and release handling

Proposed tag:

```text
v0.0.4-objective-four-repo-ops
```

Recommended release title:

```text
Objective Four Repo-Operations Baseline
```

Tag/release creation should happen only after:

1. the release-note PR is reviewed and merged;
2. issue #129 is closed by the release-note PR;
3. parent issue #119 receives a final closeout comment;
4. no data/model/map/public-output work has been introduced.

## Release acceptance checklist

| Check | Status | Notes |
|---|---|---|
| Issue-controlled workflow exists. | Satisfied | Issue architecture, taxonomy, and templates exist. |
| Branch/PR workflow exists. | Satisfied | Branch/PR workflow and PR template exist. |
| Codex/prompt instructions exist. | Satisfied | `AGENTS.md` and Codex task packet exist. |
| Prompt/build logging exists. | Satisfied | Protocol, template, and dated entries exist. |
| Phase Two intake templates exist. | Satisfied | Seven blank intake templates exist. |
| Closeout/handoff exists. | Satisfied | Closeout and handoff docs exist. |
| Quality pass completed before release note. | Satisfied | QA PR #142 merged before this branch. |
| Data work has begun. | Not satisfied and intentionally prohibited | No AOI, data, labels, masks, outputs, metrics, maps, or public demos created. |
| Release note PR merged. | Pending | This branch must be reviewed and merged. |
| Tag/release created. | Pending | Create only after merge if desired. |

## Safe claims after merge

```text
BurnLens has completed an Objective Four repo-operations baseline for issue-controlled, branch-controlled, PR-reviewed, prompt-logged future work.
```

```text
BurnLens has Phase Two intake templates ready for future intake records, but Phase Two data work has not begun.
```

## Unsupported claims after merge

```text
Phase Two data work has begun; an AOI has been selected; data has been downloaded; labels, masks, model outputs, run outputs, metrics, maps, or public demos have been created; BurnLens outputs are official, operational, field-validated, emergency-ready, or agency-endorsed.
```

## Handoff after release-note merge

After this release note is merged, update parent issue #119 with the final Objective Four completion summary. Then either:

- create the `v0.0.4-objective-four-repo-ops` tag/release if using GitHub releases for objective baselines; or
- proceed to the next objective/Phase Two intake using `OBJECTIVE_FOUR_HANDOFF.md` as the first context block.
