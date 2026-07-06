# Phase 1 / Objective Four - Tracker

## Status

Task 1 is open on issue #117.

- Working branch: `p1o4t01`
- Artifact path: `docs/phase-one/objective-four/OBJECTIVE_FOUR_TRACKER.md`
- Current file status: drafted for pull request review
- Objective status: started

## Objective Four name

Repository Operating System, Issue Architecture, and Codex Work Protocol

## Purpose

Objective Four creates the repo operating system for future BurnLens Deschutes work. It defines how later tasks should move through issues, branches, research, repo artifacts, review, pull requests, merges, and handoff updates.

The purpose is not to build the wildfire workflow yet. The purpose is to make future build work traceable, reviewable, and bounded before later phases create data, baseline, model, run, or public-demo artifacts.

## Controlling context

Objective Four follows the updated repo-use pattern and task workflow SOP:

1. Define the objective and task scope.
2. Define the artifact contract.
3. Create the GitHub issue.
4. Create the task branch.
5. Conduct fresh research.
6. Convert research into validated claims.
7. Check claims against the project boundaries.
8. Draft the artifact to portfolio-ready depth.
9. Self-audit before PR.
10. Commit the artifact.
11. Open a pull request.
12. Merge only after review.
13. Update tracker and handoff records.

Task 1 applied the required sequence: issue first, branch second, research third, artifact fourth.

## Boundary

Objective Four is documentation and repo-control only.

It does not authorize data acquisition, imagery download, final AOI selection, label creation, mask creation, baseline generation, model training, inference, metric computation, map publication, website demo integration, outside validation claims, or endorsement claims.

BurnLens Deschutes remains an experimental portfolio-first CV and GEOINT project. Future public-facing statements must be supported by repo evidence and must preserve the source-precedence rule already established elsewhere in the repository.

## Research validation summary

Fresh research was conducted after branch creation and before this artifact was written.

| Claim ID | Claim | Source authority | Evidence summary | Objective Four decision |
|---|---|---|---|---|
| P1O4-R01 | GitHub Issues are appropriate for task tracking. | GitHub Docs: About issues | GitHub states that issues can be used to plan, discuss, and track work, including tasks, bugs, features, and ideas. | Use issues as the required unit of task control. |
| P1O4-R02 | GitHub Projects are appropriate for planning and organizing issue and PR work. | GitHub Docs: About Projects | GitHub describes Projects as adaptable tables, boards, and roadmaps that integrate with issues and pull requests. | Create a future project-board specification in Objective Four. |
| P1O4-R03 | Pull requests are appropriate for reviewable change control. | GitHub Docs: About pull requests | GitHub describes pull requests as proposals to merge changes that support discussion and review before merging. | Require PR review for meaningful repo artifacts. |
| P1O4-R04 | Releases and tags can mark traceable project states. | GitHub Docs: About releases | GitHub says releases are based on Git tags, which mark specific points in repository history. | Use release and tag notes for objective closeouts when appropriate. |
| P1O4-R05 | `AGENTS.md` can carry persistent Codex project instructions. | OpenAI Developers: Custom instructions with AGENTS.md | OpenAI states that Codex reads `AGENTS.md` files before doing work and can layer project guidance with other instructions. | Create a later Objective Four task for repo-level Codex instructions. |

## Research links

- GitHub Docs: About issues - https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/about-issues
- GitHub Docs: About Projects - https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects
- GitHub Docs: About pull requests - https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests
- GitHub Docs: About releases - https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
- OpenAI Developers: AGENTS.md guidance - https://developers.openai.com/codex/guides/agents-md

## Objective Four task table

| Task | Issue | Artifact | Purpose | Status |
|---|---:|---|---|---|
| P1O4-T01 | #117 | `OBJECTIVE_FOUR_TRACKER.md` | Create the parent tracker and apply the research-before-artifact workflow. | In progress |
| P1O4-T02 | TBD | `ISSUE_ARCHITECTURE.md` or issue set | Create parent and subtask issue architecture for Objective Four. | Not started |
| P1O4-T03 | TBD | `ISSUE_TAXONOMY.md` | Define labels, milestones, task metadata, and issue-type rules. | Not started |
| P1O4-T04 | TBD | `PROJECT_BOARD_SPEC.md` | Specify GitHub Project board views, fields, and status logic. | Not started |
| P1O4-T05 | TBD | `BRANCH_AND_PR_WORKFLOW.md` | Define branch naming, commit naming, PR review rules, and merge expectations. | Not started |
| P1O4-T06 | TBD | `.github/ISSUE_TEMPLATE/*` and `.github/PULL_REQUEST_TEMPLATE.md` | Add templates for issues and PRs. | Not started |
| P1O4-T07 | TBD | `AGENTS.md` | Add repo-level Codex operating instructions. | Not started |
| P1O4-T08 | TBD | `templates/CODEX_TASK_PACKET.md` | Create the standard task packet for Codex and prompt-assisted work. | Not started |
| P1O4-T09 | TBD | `records/PROMPT_BUILD_LOG.md` and `templates/PROMPT_LOG_ENTRY.md` | Create prompt/build logging protocol. | Not started |
| P1O4-T10 | TBD | Phase Two intake templates | Create templates for AOI records, source records, access logs, CRS checks, provenance manifests, claims entries, and no-go notes. | Not started |
| P1O4-T11 | TBD | `OBJECTIVE_FOUR_CLOSEOUT.md` and `OBJECTIVE_FOUR_HANDOFF.md` | Create closeout and handoff standards. | Not started |
| P1O4-T12 | TBD | `OBJECTIVE_FOUR_RELEASE_NOTE.md` | Create release/tag note for the repo-control baseline. | Not started |

## Artifact contract for Task 1

| Field | Requirement |
|---|---|
| Task | P1O4-T01 - Create Objective Four tracker |
| Artifact filename | `docs/phase-one/objective-four/OBJECTIVE_FOUR_TRACKER.md` |
| Artifact purpose | Establish the parent tracker for Objective Four and prove that the improved task workflow is being followed. |
| Required decisions | Confirm Objective Four as repo-control only; confirm task sequence; confirm no implementation work is authorized. |
| Required research claims | GitHub issue, project, pull request, release, and Codex instruction-file claims. |
| Required source citations | Official GitHub Docs and OpenAI Developers docs. |
| Required tables | Research validation table, task table, acceptance table, self-audit table. |
| Too thin if | It only lists task names without decisions, evidence, acceptance criteria, or boundaries. |

## Acceptance checklist

| Check | Status | Notes |
|---|---|---|
| Tracker exists at required path. | Satisfied in branch | This file. |
| Issue exists. | Satisfied | Issue #117. |
| Branch exists before artifact. | Satisfied | Branch `p1o4t01`. |
| Fresh research conducted before artifact creation. | Satisfied | Research summarized above. |
| Artifact includes purpose and scope boundary. | Satisfied | Purpose and boundary sections included. |
| Artifact includes task table. | Satisfied | Objective Four task table included. |
| Artifact includes research basis. | Satisfied | Research validation summary included. |
| Artifact includes acceptance criteria. | Satisfied | Acceptance checklist included. |
| Artifact includes rejection/defer criteria. | Satisfied | See next section. |
| Artifact includes versioning/provenance implications. | Satisfied | See dedicated section. |
| Artifact creates no implementation outputs. | Satisfied | Documentation only. |

## Rejection and defer criteria

Defer or reject an Objective Four task if it:

- requires data download or retained source data;
- selects a final AOI;
- creates labels, masks, baselines, model inputs, inference outputs, metrics, or public maps;
- introduces stronger claims than the repo can support;
- bypasses issue, branch, research, artifact, and PR tracking;
- lacks acceptance and rejection criteria;
- lacks a handoff note for the next task.

## Allowed uses of this tracker

This tracker may be used to orient the rest of Objective Four, create and sequence future Objective Four issues, support PR review for repo-control artifacts, document what has and has not been completed, and preserve the docs-only boundary before later phases.

## Forbidden uses of this tracker

This tracker must not be used to imply that BurnLens has acquired or processed data, selected final scenes or AOI tiles, created a dataset, trained or evaluated a model, generated a baseline or inference run, produced public-facing outputs, or received outside validation or endorsement.

## Versioning and provenance implications

Objective Four artifacts should be traceable through:

- GitHub issue number;
- branch name;
- artifact path;
- commit SHA after merge;
- PR number;
- objective handoff update;
- optional closeout tag or release note after the full objective is complete.

Task 1 does not create a release. A release note is reserved for the later Objective Four closeout task.

## Claims-register check

Task 1 adds no public-facing claims about data quality, model performance, planning usefulness, external validation, review, or operational capability.

Safe internal claim after Task 1:

> Objective Four has a tracker that defines the repo-control task sequence and records the research basis for using GitHub Issues, Projects, pull requests, releases/tags, and Codex instruction files in later work.

Unsupported claims after Task 1:

- BurnLens is operational.
- BurnLens has processed imagery or local overlays.
- BurnLens has model outputs or evaluation results.
- BurnLens has externally reviewed outputs.

## Pre-PR self-audit

| Question | Answer |
|---|---|
| Does the artifact answer so what? | Yes. It explains that Objective Four creates the operating system for future controlled work. |
| Does it include at least one decision? | Yes. Objective Four remains repo-control only and Task 1 authorizes no implementation work. |
| Does it include acceptance and rejection criteria? | Yes. |
| Does it include source-specific facts? | Yes. The research table summarizes official GitHub and OpenAI documentation. |
| Does it preserve BurnLens boundaries? | Yes. |
| Does it say what is not done? | Yes. |
| Does it include future fields/templates if implementation comes later? | Yes. Task table includes future template tasks. |
| Would a reviewer understand what to do next? | Yes. Proceed to P1O4-T02 after review and merge. |

## Handoff note

Proceed to P1O4-T02 only after Task 1 is reviewed and merged. The next task should create the Objective Four issue architecture using this tracker as the parent reference. The next task should repeat the same workflow: artifact contract, issue, branch, fresh research, research validation, claims check, artifact draft, self-audit, PR, merge, and tracker update.
