# Phase 1 / Objective Four - Issue Architecture

## Status

Task 2 is open on issue #118.

- Parent issue: #119
- Working branch: `p1o4t02b`
- Artifact path: `docs/phase-one/objective-four/ISSUE_ARCHITECTURE.md`
- Current file status: drafted for pull request review

## Purpose

This artifact defines the Objective Four issue architecture for BurnLens Deschutes. It converts the Objective Four task list into a controlled issue set with a parent issue, task issues, recommended sequencing, dependency logic, and pull-request linkage rules.

The issue architecture is intended to keep the rest of Objective Four organized without allowing the work to drift into implementation before the repo operating system is complete.

## Boundary

This artifact is documentation and issue-control only.

It does not authorize data acquisition, imagery download, final AOI selection, label creation, mask creation, baseline generation, model training, inference, metric computation, map publication, website demo integration, outside validation claims, or endorsement claims.

## Research timing

Fresh research was conducted after the task branch was created and before this artifact was written.

## Research validation summary

| Claim ID | Claim | Source authority | Evidence summary | Decision for Task 2 |
|---|---|---|---|---|
| P1O4-T02-R01 | GitHub issues can track tasks and can be broken down with sub-issues. | GitHub Docs: About issues | GitHub states that issues can plan, discuss, and track work, and that work can be broken down by adding sub-issues and browsing the hierarchy. | Use one parent issue plus task issues for Objective Four. |
| P1O4-T02-R02 | Issue dependencies can represent blocked or blocking relationships. | GitHub Docs: About issues | GitHub states that issue dependencies let teams identify issues blocked by or blocking other work. | Record sequencing and dependency rules in this artifact. |
| P1O4-T02-R03 | Issue metadata can organize work. | GitHub Docs: About issues | GitHub states that issues can include issue types, labels, and milestones. | Leave detailed label and milestone rules for P1O4-T03, but define required metadata fields here. |
| P1O4-T02-R04 | Projects integrate with issues and pull requests. | GitHub Docs: About Projects | GitHub describes Projects as tables, boards, and roadmaps that integrate with issues and pull requests. | Design this issue set so it can be moved into a Project board in P1O4-T04. |
| P1O4-T02-R05 | Pull requests can be linked to issues and close them when merged. | GitHub Docs: Linking a pull request to an issue | GitHub states that linking a PR to an issue shows work is in progress and can automatically close the issue when the PR is merged into the default branch. | Each task PR should use `Closes #issue-number` only for the specific task issue it completes. |

## Research links

- GitHub Docs: About issues - https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/about-issues
- GitHub Docs: About Projects - https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects
- GitHub Docs: Linking a pull request to an issue - https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue

## Artifact contract

| Field | Requirement |
|---|---|
| Task | P1O4-T02 - Create issue architecture |
| Artifact filename | `docs/phase-one/objective-four/ISSUE_ARCHITECTURE.md` |
| Artifact purpose | Define the parent issue, task issues, dependency model, and PR linkage rules for Objective Four. |
| Required decisions | Confirm parent issue #119; map task issues #117, #118, and #120-#129; define issue sequencing and linkage rules. |
| Required research claims | GitHub issue hierarchy, dependencies, metadata, Projects integration, and PR-to-issue linking. |
| Required tables | Research validation table, issue architecture table, dependency table, PR linkage table, acceptance checklist. |
| Too thin if | It lists issue numbers without dependency rules, PR rules, acceptance criteria, or boundary language. |

## Issue architecture decision

Objective Four uses one parent issue and one task issue per task.

- Parent issue: #119 - Phase 1 Objective Four parent
- Task issues: #117, #118, #120, #121, #122, #123, #124, #125, #126, #127, #128, #129

Because the connector currently creates normal issue references but does not expose a dedicated sub-issue mutation in this workflow, formal sub-issue relationships may be added later through GitHub UI if desired. For now, the architecture is encoded through issue titles, issue bodies, references to parent #119, artifact paths, and this register.

## Objective Four issue table

| Task | Issue | Artifact | Primary purpose | Dependency | Status |
|---|---:|---|---|---|---|
| Objective parent | #119 | N/A | Group Objective Four task issues and objective status. | None | Open |
| P1O4-T01 | #117 | `OBJECTIVE_FOUR_TRACKER.md` | Create the parent tracker and define the objective task sequence. | None | Artifact drafted on `p1o4t01`; PR pending |
| P1O4-T02 | #118 | `ISSUE_ARCHITECTURE.md` | Create this issue architecture. | Should follow T01 tracker draft | In progress |
| P1O4-T03 | #120 | `ISSUE_TAXONOMY.md` | Define labels, milestones, metadata, and issue-type rules. | T02 | Open |
| P1O4-T04 | #121 | `PROJECT_BOARD_SPEC.md` | Define GitHub Project board views, fields, and status logic. | T02 and T03 | Open |
| P1O4-T05 | #122 | `BRANCH_AND_PR_WORKFLOW.md` | Define branch naming, commit naming, PR review rules, and merge expectations. | T02 | Open |
| P1O4-T06 | #123 | `.github/ISSUE_TEMPLATE/*` and `.github/PULL_REQUEST_TEMPLATE.md` | Add reusable issue and PR templates. | T03 and T05 | Open |
| P1O4-T07 | #124 | `AGENTS.md` | Add repo-level Codex operating instructions. | T05 | Open |
| P1O4-T08 | #125 | `templates/CODEX_TASK_PACKET.md` | Create a task packet for Codex and prompt-assisted work. | T05 and T07 | Open |
| P1O4-T09 | #126 | `records/PROMPT_BUILD_LOG.md` and `templates/PROMPT_LOG_ENTRY.md` | Create prompt/build logging protocol. | T08 | Open |
| P1O4-T10 | #127 | Phase Two intake templates | Create templates for future AOI, source, access, CRS, provenance, claims, and no-go records. | T03 and T05 | Open |
| P1O4-T11 | #128 | `OBJECTIVE_FOUR_CLOSEOUT.md` and `OBJECTIVE_FOUR_HANDOFF.md` | Create closeout and handoff standards. | T01-T10 | Open |
| P1O4-T12 | #129 | `OBJECTIVE_FOUR_RELEASE_NOTE.md` | Create release/tag note for the repo-control baseline. | T11 | Open |

## Recommended dependency model

| Dependency | Meaning | Enforcement method |
|---|---|---|
| T02 after T01 | Issue architecture should follow the tracker. | This artifact references T01 and parent issue #119. |
| T03 after T02 | Taxonomy should use the issue set created here. | T03 artifact should cite this file. |
| T04 after T03 | Project board fields depend on issue labels and metadata. | T04 should not finalize board fields before T03. |
| T05 after T02 | Branch and PR workflow depends on issue architecture. | T05 should reference this file and #119. |
| T06 after T03 and T05 | Templates need metadata and PR workflow rules. | T06 should wait for taxonomy and workflow rules. |
| T07 after T05 | AGENTS.md should reflect branch/PR protocol. | T07 should cite T05. |
| T08 after T07 | Codex task packet should include AGENTS.md rules. | T08 should cite T07. |
| T09 after T08 | Prompt log protocol should reflect task packet fields. | T09 should cite T08. |
| T10 after T03 and T05 | Phase Two intake templates need metadata and PR workflow standards. | T10 should cite T03 and T05. |
| T11 after T01-T10 | Closeout and handoff should summarize completed objective artifacts. | T11 should wait until all prior artifacts are merged or explicitly deferred. |
| T12 after T11 | Release note should follow closeout. | T12 should cite T11. |

## Required task issue structure going forward

Each future Objective Four task issue should include:

1. Task ID and title.
2. Parent issue reference: `#119`.
3. Artifact path.
4. Purpose.
5. Required decisions.
6. Required research claims.
7. Required acceptance checklist.
8. Boundary statement.
9. Dependency note.
10. Expected PR close keyword.

## Pull request linkage rule

Each task PR should target `main` and should include a close keyword only for the task issue it completes.

| Task | PR body should include | Do not include |
|---|---|---|
| P1O4-T02 | `Closes #118` | Do not close #119. |
| P1O4-T03 | `Closes #120` | Do not close #119. |
| P1O4-T04 | `Closes #121` | Do not close #119. |
| P1O4-T05 | `Closes #122` | Do not close #119. |
| P1O4-T06 | `Closes #123` | Do not close #119. |
| P1O4-T07 | `Closes #124` | Do not close #119. |
| P1O4-T08 | `Closes #125` | Do not close #119. |
| P1O4-T09 | `Closes #126` | Do not close #119. |
| P1O4-T10 | `Closes #127` | Do not close #119. |
| P1O4-T11 | `Closes #128` | Do not close #119 unless Objective Four is complete and manually reviewed. |
| P1O4-T12 | `Closes #129` | Do not close #119 unless the parent issue is deliberately closed after the release note. |

## Parent issue update rule

The parent issue #119 should be updated by comment, not auto-closed by task PRs.

Recommended comment format after each task merge:

```text
P1O4-TXX merged.
Artifact: path/to/artifact.md
PR: #PR_NUMBER
Status: complete
Next task: P1O4-TYY
```

## Issue creation results

| Created item | Issue |
|---|---:|
| Objective Four parent | #119 |
| P1O4-T01 tracker | #117 |
| P1O4-T02 issue architecture | #118 |
| P1O4-T03 issue taxonomy | #120 |
| P1O4-T04 project board spec | #121 |
| P1O4-T05 branch and PR workflow | #122 |
| P1O4-T06 issue and PR templates | #123 |
| P1O4-T07 AGENTS instructions | #124 |
| P1O4-T08 Codex task packet | #125 |
| P1O4-T09 prompt build log protocol | #126 |
| P1O4-T10 Phase Two intake templates | #127 |
| P1O4-T11 closeout and handoff docs | #128 |
| P1O4-T12 release note | #129 |

## Rejection and defer criteria

Defer or revise this architecture if:

- a task lacks an artifact path;
- a task lacks a parent reference;
- a task depends on an artifact that has not been created or explicitly deferred;
- a task would create implementation outputs before later phases;
- a PR would close the parent issue accidentally;
- task issues contain stronger claims than repo artifacts support.

## Allowed uses

This artifact may be used to create Objective Four issues, sequence future Objective Four task work, guide task PR linkage, support a future GitHub Project board, and preserve parent-issue visibility.

## Forbidden uses

This artifact must not be used to claim that future Objective Four tasks are complete, that the repo operating system is finished, or that BurnLens has started data, model, run, map, or public-demo work.

## Versioning and provenance implications

Each task should remain traceable to:

- task issue number;
- parent issue #119;
- task branch;
- artifact path;
- PR number;
- merge commit;
- updated tracker or handoff note.

## Claims-register check

Task 2 creates internal repo-management claims only.

Safe claim after Task 2:

> Objective Four now has a parent issue and a complete issue architecture for the remaining repo-control tasks.

Unsupported claims after Task 2:

- Objective Four is complete.
- Task artifacts after T02 have been created.
- The Project board, labels, templates, AGENTS.md, Codex packet, prompt log, Phase Two templates, closeout, or release note already exist.

## Acceptance checklist

| Check | Status | Notes |
|---|---|---|
| Task issue exists. | Satisfied | #118. |
| Branch exists before research and artifact writing. | Satisfied | `p1o4t02b`. |
| Fresh research completed before artifact writing. | Satisfied | Research summarized above. |
| Parent issue exists. | Satisfied | #119. |
| Remaining Objective Four task issues exist. | Satisfied | #120-#129. |
| Artifact includes issue table. | Satisfied | Objective Four issue table included. |
| Artifact includes dependency rules. | Satisfied | Recommended dependency model included. |
| Artifact includes PR linkage rules. | Satisfied | PR close-keyword table included. |
| Artifact preserves documentation-only boundary. | Satisfied | Boundary sections included. |
| Artifact creates no implementation output. | Satisfied | Issue-control and documentation only. |

## Pre-PR self-audit

| Question | Answer |
|---|---|
| Does the artifact answer so what? | Yes. It explains how Objective Four work is organized and sequenced. |
| Does it include at least one decision? | Yes. Parent issue #119 and task issues #117, #118, and #120-#129 are the issue architecture. |
| Does it include acceptance and rejection criteria? | Yes. |
| Does it include source-specific facts? | Yes. Research validation cites GitHub issue, project, and PR linkage docs. |
| Does it preserve BurnLens boundaries? | Yes. |
| Does it say what is not done? | Yes. |
| Would a reviewer understand what to do next? | Yes. Proceed to P1O4-T03 after review and merge. |

## Handoff note

Proceed to P1O4-T03 after this artifact is reviewed and merged. P1O4-T03 should use this issue architecture as controlling context and should define the labels, milestones, and task metadata needed to make the issue set easier to filter and review.
