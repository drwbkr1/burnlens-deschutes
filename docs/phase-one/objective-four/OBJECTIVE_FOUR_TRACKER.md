# Phase One / Objective Four Tracker

## Objective Four

**Repository Operating System, Issue Architecture, and Codex Work Protocol**

Objective Four created the repository operating system for BurnLens Deschutes: issues, labels, project-board logic, branch/PR rules, Codex guidance, prompt/build logging, Phase Two intake templates, transition records, and a release-note baseline.

## Current status

| Field | Status |
|---|---|
| Parent issue | #119 |
| Completed task issues | #117, #118, #120, #121, #122, #123, #124, #125, #126, #127, #128, #141 |
| Release-note task issue | #129 |
| Release-note artifact | `docs/phase-one/objective-four/OBJECTIVE_FOUR_RELEASE_NOTE.md` |
| Proposed tag | `v0.0.4-objective-four-repo-ops` |
| Objective status | Portfolio-quality repo-operations baseline drafted for release-note PR review |
| Data-work status | Not started and still prohibited |

## Boundary

Objective Four is documentation, repository-control, prompt-control, release-note, and intake-template work only.

It does not authorize data acquisition, imagery download, final AOI selection, retained source data, label creation, mask creation, baseline generation, model training, inference, metric computation, map publication, website demo integration, outside validation claims, or endorsement claims.

BurnLens Deschutes remains an experimental portfolio-first CV and GEOINT project. Future public-facing statements must be supported by repo evidence and must preserve source precedence: official sources govern.

## Required workflow for future tasks

Use this loop for every task unless a later merged governance artifact supersedes it:

```text
artifact contract -> issue comment -> task branch -> fresh research -> artifact file -> self-audit -> PR -> review -> squash merge -> issue/parent/tracker update
```

Prompt-assisted work that changes files or creates task artifacts must also create or update a prompt/build log entry.

## Governing artifacts created by Objective Four

| Artifact | Status | Purpose |
|---|---|---|
| `docs/phase-one/objective-four/OBJECTIVE_FOUR_TRACKER.md` | Updated in Task 12 branch | Current objective map and completion tracker. |
| `docs/phase-one/objective-four/ISSUE_ARCHITECTURE.md` | Merged | Defines parent/task issue structure and task sequencing. |
| `docs/phase-one/objective-four/ISSUE_TAXONOMY.md` | Merged | Defines labels, issue types, metadata, and classification logic. |
| `docs/phase-one/objective-four/PROJECT_BOARD_SPEC.md` | Merged | Defines project-board fields, views, and status logic. |
| `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md` | Merged | Defines branch naming, PR titles, close-keyword use, review, merge, and update rules. |
| `.github/ISSUE_TEMPLATE/task.yml` | Merged | Standard task issue intake form. |
| `.github/ISSUE_TEMPLATE/config.yml` | Merged | Issue-template configuration and safety redirect. |
| `.github/PULL_REQUEST_TEMPLATE.md` | Merged | Standard PR checklist. |
| `AGENTS.md` | Merged | Repository-level Codex and prompt-assisted work instructions. |
| `templates/CODEX_TASK_PACKET.md` | Merged | Reusable task packet for Codex or prompt-assisted repository work. |
| `records/PROMPT_BUILD_LOG.md` | Updated in Task 12 branch | Prompt/build log protocol and index. |
| `templates/PROMPT_LOG_ENTRY.md` | Merged | Reusable prompt-log entry template. |
| Phase Two intake templates in `templates/` | Merged | Blank AOI, source, access, CRS, provenance, claim, and no-go templates. |
| `docs/phase-one/objective-four/OBJECTIVE_FOUR_CLOSEOUT.md` | Updated in Task 12 branch | Closeout standard and pre-data gates. |
| `docs/phase-one/objective-four/OBJECTIVE_FOUR_HANDOFF.md` | Updated in Task 12 branch | First context block for Objective Five or Phase Two. |
| `docs/phase-one/objective-four/OBJECTIVE_FOUR_RELEASE_NOTE.md` | Drafted in Task 12 branch | Objective Four repo-operations release-note baseline. |

## Task completion table

| Task | Issue | PR | Artifact(s) | Status |
|---|---:|---:|---|---|
| P1O4-T01 | #117 | #133 | `OBJECTIVE_FOUR_TRACKER.md` | Merged |
| P1O4-T02 | #118 | #130 | `ISSUE_ARCHITECTURE.md` | Merged |
| P1O4-T03 | #120 | #131 | `ISSUE_TAXONOMY.md` | Merged |
| P1O4-T04 | #121 | #132 | `PROJECT_BOARD_SPEC.md` | Merged |
| P1O4-T05 | #122 | #134 | `BRANCH_AND_PR_WORKFLOW.md` | Merged |
| P1O4-T06 | #123 | #135 | issue and PR templates | Merged |
| P1O4-T07 | #124 | #136 | `AGENTS.md` | Merged |
| P1O4-T08 | #125 | #137 | `templates/CODEX_TASK_PACKET.md` | Merged |
| P1O4-T09 | #126 | #138 | `records/PROMPT_BUILD_LOG.md`; `templates/PROMPT_LOG_ENTRY.md` | Merged |
| P1O4-T10 | #127 | #139 | Phase Two intake templates; Task 10 prompt log entry | Merged |
| P1O4-T11 | #128 | #140 | closeout; handoff; Task 11 prompt log entry | Merged |
| P1O4-QA | #141 | #142 | tracker, closeout, handoff, prompt-log cohesion updates | Merged |
| P1O4-T12 | #129 | pending | `OBJECTIVE_FOUR_RELEASE_NOTE.md`; adjacent tracker/closeout/handoff/log updates | Drafted in branch |

## Research validation summary

| Claim ID | Claim | Source authority | Objective Four decision |
|---|---|---|---|
| P1O4-R01 | GitHub Issues are appropriate for task tracking. | GitHub Docs: About issues | Use issues as the required unit of task control. |
| P1O4-R02 | GitHub Projects are appropriate for planning and organizing issue/PR work. | GitHub Docs: About Projects | Use project-board logic for task status and review readiness. |
| P1O4-R03 | Pull requests are appropriate for reviewable change control. | GitHub Docs: About pull requests | Require PR review for meaningful repo artifacts. |
| P1O4-R04 | Releases and tags can mark traceable project states. | GitHub Docs: About releases | Reserve release/tag note for Objective Four final baseline. |
| P1O4-R05 | `AGENTS.md` can carry persistent Codex project instructions. | OpenAI Developers: Custom instructions with AGENTS.md | Maintain repository-level Codex guidance. |
| P1O4-R06 | Prompt-assisted work benefits from verification, clear file scope, and focused tasks. | OpenAI Codex prompting docs | Use task packets and prompt/build log entries for prompt-built work. |
| P1O4-R07 | Phase Two intake should record metadata, CRS, provenance, source rights, claims, and no-go decisions before data use. | FGDC, OGC, W3C PROV, STAC references recorded in Task 10 prompt log | Require intake records before any data is touched. |

## Research links

- GitHub Docs: About issues - https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/about-issues
- GitHub Docs: About Projects - https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects
- GitHub Docs: About pull requests - https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests
- GitHub Docs: About releases - https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
- OpenAI Developers: AGENTS.md guidance - https://developers.openai.com/codex/guides/agents-md
- OpenAI Developers: Codex prompting - https://developers.openai.com/codex/prompting

## Portfolio-quality acceptance check

| Check | Status | Evidence |
|---|---|---|
| Future task work is issue-controlled. | Satisfied | Issue architecture, issue taxonomy, and task issue template. |
| Future work is branch/PR controlled. | Satisfied | Branch/PR workflow and PR template. |
| Prompt-assisted work has explicit standards. | Satisfied | `AGENTS.md`, Codex task packet, and prompt/build log protocol. |
| Phase Two can begin intake records. | Satisfied | Seven blank intake templates. |
| Phase Two data use is blocked until intake gates exist. | Satisfied | Closeout, handoff, intake templates, and prompt log entries preserve no-data boundary. |
| Public/portfolio claims are constrained. | Satisfied | Claims checks and warning language across governing docs. |
| Release-note artifact is drafted. | Satisfied in branch | `OBJECTIVE_FOUR_RELEASE_NOTE.md`. |
| Objective Four is fully released/tagged. | Pending | Release-note PR must merge; tag/release can be created after merge if desired. |

## Safe claims after this Task 12 branch

```text
BurnLens has a drafted Objective Four release note for the repo-operations baseline.
```

```text
BurnLens has blank Phase Two intake templates and pre-data gates, but no Phase Two data work has begun.
```

## Unsupported claims after this Task 12 branch

- Objective Four has been tagged/released.
- Phase Two data work has begun.
- An AOI has been selected.
- Data has been downloaded.
- Labels, masks, model outputs, run outputs, metrics, maps, or public demos have been created.
- BurnLens outputs are official, operational, field-validated, emergency-ready, or agency-endorsed.

## Handoff

After the Task 12 PR is reviewed and merged, update parent issue #119 with the final Objective Four completion summary and decide whether to create the proposed tag `v0.0.4-objective-four-repo-ops`.
