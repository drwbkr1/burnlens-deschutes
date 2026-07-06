# Phase 1 / Objective Four - Project Board Specification

## Status

Task 4 is open on issue #121.

- Parent issue: #119
- Working branch: `p1o4t04b`
- Artifact path: `docs/phase-one/objective-four/PROJECT_BOARD_SPEC.md`
- Current file status: drafted for pull request review
- Dependency note: this spec depends on the issue architecture in PR #130 and the issue taxonomy in PR #131. Do not merge this ahead of those PRs unless the dependency order is intentionally overridden.

## Purpose

This artifact specifies the GitHub Project board structure for Objective Four and later BurnLens Deschutes repo-control work. It defines views, fields, status logic, filters, automation guidance, and operating rules so the project board can support traceable task execution rather than becoming a loose checklist.

The board spec is a planning artifact only. It does not create or configure a GitHub Project board by itself.

## Boundary

This artifact is documentation and repo-management guidance only.

It does not authorize data acquisition, imagery download, final AOI selection, label creation, mask creation, baseline generation, model training, inference, metric computation, map publication, website demo integration, outside validation claims, or endorsement claims.

## Research timing

Fresh research was conducted after the task branch was created and before this artifact was written.

## Research validation summary

| Claim ID | Claim | Source authority | Evidence summary | Decision for Task 4 |
|---|---|---|---|---|
| P1O4-T04-R01 | GitHub Projects can integrate issues and pull requests for planning and tracking. | GitHub Docs: About Projects | GitHub describes a project as an adaptable table, board, and roadmap that integrates with issues and pull requests. | Use a Project board as a planning layer over Objective Four issues and PRs. |
| P1O4-T04-R02 | Projects support custom views. | GitHub Docs: About Projects; Changing view layout | GitHub states projects can have multiple customized views and can be shown as table, board, or roadmap layouts. | Define separate table, board, review, dependency, and closeout views. |
| P1O4-T04-R03 | Projects support custom fields. | GitHub Docs: About Projects; Understanding fields | GitHub states Projects can use custom fields for metadata, including text, number, date, single select, and iteration fields. | Define fields for task ID, artifact path, phase, objective, research status, data boundary, PR link, and closeout status. |
| P1O4-T04-R04 | Project data syncs with underlying issues and pull requests. | GitHub Docs: About Projects | GitHub states project information is synced with issues and pull requests and that changes can reflect between the project and issue or PR. | Use the board to surface status, but keep issue and PR records as the source of truth. |
| P1O4-T04-R05 | Built-in automations can update project status and auto-add matching items. | GitHub Docs: Built-in automations and adding items automatically | GitHub states built-in workflows can update item Status, set Done when issues close or PRs merge, and auto-add items from repositories using filters. | Recommend conservative automation only after labels and milestone taxonomy are reviewed. |

## Research links

- GitHub Docs: About Projects - https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects
- GitHub Docs: Changing the layout of a view - https://docs.github.com/en/issues/planning-and-tracking-with-projects/customizing-views-in-your-project/changing-the-layout-of-a-view
- GitHub Docs: Understanding fields - https://docs.github.com/en/issues/planning-and-tracking-with-projects/understanding-fields
- GitHub Docs: Using built-in automations - https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-built-in-automations
- GitHub Docs: Adding items automatically - https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/adding-items-automatically

## Artifact contract

| Field | Requirement |
|---|---|
| Task | P1O4-T04 - Create project board spec |
| Artifact filename | `docs/phase-one/objective-four/PROJECT_BOARD_SPEC.md` |
| Artifact purpose | Define GitHub Project views, fields, status logic, filters, automation guidance, and operating rules. |
| Required decisions | Confirm Project as planning layer only; define views; define fields; define status options; define automation boundaries. |
| Required research claims | GitHub Projects integration, views, layouts, fields, syncing, and automation. |
| Required tables | Research validation table, view table, field table, status table, automation table, acceptance checklist. |
| Too thin if | It names a board without specifying views, fields, filters, status logic, automation rules, or boundaries. |

## Project board decision

Create one Project board for Objective Four once Tasks 2 and 3 are reviewed and merged.

Recommended board name:

```text
BurnLens - Phase 1 Objective Four Repo Ops
```

Recommended description:

```text
Tracks Objective Four repo operating system tasks for BurnLens Deschutes. Documentation and repo-control only. Official source precedence and no-data boundaries remain in force.
```

The board should include Objective Four issues and PRs only until Objective Four is closed. Later phases can copy the field model or create a broader Phase Two board after Phase One closeout.

## Board source of truth rule

The board is not the authoritative artifact record. It is a planning and visibility layer.

| Record type | Source of truth |
|---|---|
| Task scope | Issue body and linked artifact contract |
| Artifact content | Repository file on task branch and merged file on `main` |
| Research basis | Artifact research validation section |
| Review status | Pull request review and merge state |
| Completion status | Merged PR plus tracker/handoff update |
| Public claim status | Claims register and boundary docs |
| Board status | Convenience tracking only |

## Required board items

Initial board items should include:

| Item | Issue/PR | Required? | Notes |
|---|---:|---:|---|
| Objective Four parent | #119 | Yes | Parent tracking item; should not auto-close until full objective is reviewed. |
| P1O4-T01 tracker | #117 | Yes | Existing tracker task. |
| P1O4-T02 issue architecture | #118 / PR #130 | Yes | Dependency for board spec. |
| P1O4-T03 issue taxonomy | #120 / PR #131 | Yes | Dependency for field and label logic. |
| P1O4-T04 project board spec | #121 | Yes | This task. |
| P1O4-T05 branch and PR workflow | #122 | Yes | Next workflow artifact. |
| P1O4-T06 issue and PR templates | #123 | Yes | Requires taxonomy and workflow rules. |
| P1O4-T07 AGENTS instructions | #124 | Yes | Codex repo instruction task. |
| P1O4-T08 Codex task packet | #125 | Yes | Prompt-assisted task packet. |
| P1O4-T09 prompt build log protocol | #126 | Yes | Prompt/build logging. |
| P1O4-T10 Phase Two intake templates | #127 | Yes | Template-only intake prep. |
| P1O4-T11 closeout and handoff docs | #128 | Yes | Depends on prior tasks. |
| P1O4-T12 release note | #129 | Yes | Depends on closeout. |

## Required fields

| Field | Type | Required? | Purpose | Example values |
|---|---|---:|---|---|
| Status | Single select | Yes | Main workflow column and board grouping. | Backlog, Contracted, Branch Created, Research Complete, Artifact Drafted, PR Open, Needs Revision, Ready to Merge, Merged, Deferred |
| Task ID | Text | Yes | Stable task identifier. | P1O4-T04 |
| Phase | Single select | Yes | Phase grouping. | Phase 1 |
| Objective | Single select | Yes | Objective grouping. | Objective 4 |
| Artifact Path | Text | Yes | Expected repo artifact. | `docs/phase-one/objective-four/PROJECT_BOARD_SPEC.md` |
| Artifact Type | Single select | Yes | Artifact class from taxonomy. | documentation, template, records, workflow |
| Parent Issue | Text or issue field | Yes | Parent linkage. | #119 |
| Task Issue | Text or issue field | Yes | Task issue. | #121 |
| Pull Request | Pull request field or text | Conditional | PR link once opened. | #132 |
| Branch | Text | Yes while active | Branch name. | p1o4t04b |
| Requires Research | Single select | Yes | Whether fresh research is required. | yes, no |
| Research Status | Single select | Yes | Research lifecycle. | not-started, in-progress, complete, not-required |
| Claim Boundary | Single select | Yes | Whether task affects project claims. | yes, no |
| Source Precedence Touch | Single select | Yes | Whether task touches source authority. | yes, no |
| Data Boundary | Single select | Yes | Data handling boundary. | no-data, template-only, authorized-later |
| Dependency Status | Single select | Yes | Whether upstream tasks are satisfied. | clear, depends-on-open-pr, blocked, overridden |
| Merge Order | Number | Conditional | Helps sequence dependent PRs. | 4 |
| Closeout Needed | Single select | Yes | Whether tracker/handoff must update after merge. | yes, no |
| Notes | Text | Optional | Human-readable caveat. | Do not merge before #130 and #131. |

## Status field specification

| Status | Meaning | Entry condition | Exit condition |
|---|---|---|---|
| Backlog | Task is planned but not started. | Task issue exists or is planned. | Artifact contract begins. |
| Contracted | Artifact contract exists. | Issue has artifact contract. | Branch is created. |
| Branch Created | Branch exists. | Task branch created. | Fresh research is complete. |
| Research Complete | Research completed and claims identified. | Research validation sources selected. | Artifact is drafted. |
| Artifact Drafted | Repo artifact exists on branch. | File committed on task branch. | PR is opened. |
| PR Open | Pull request is open. | PR created. | Review requests changes or accepts. |
| Needs Revision | Review found gaps. | Reviewer requests changes or self-audit fails. | Revision committed. |
| Ready to Merge | Review complete and dependencies satisfied. | Acceptance criteria met and dependencies clear. | PR merged. |
| Merged | PR merged into `main`. | Merge complete. | Tracker and parent issue updated. |
| Deferred | Task intentionally delayed. | Dependency or scope issue blocks work. | Task is resumed or closed not-planned. |

## Recommended views

| View name | Layout | Filter | Group/sort | Purpose |
|---|---|---|---|---|
| Objective Four Overview | Table | Phase = Phase 1 and Objective = Objective 4 | Sort by Merge Order | Primary operating view for all Objective Four issues and PRs. |
| Repo Ops Board | Board | Objective = Objective 4 | Group by Status | Kanban-style view from contract to merge. |
| Dependency Watch | Table | Dependency Status is not clear | Sort by Merge Order | Shows blocked tasks and tasks depending on open PRs. |
| Research Validation | Table | Requires Research = yes | Group by Research Status | Tracks whether fresh research was completed before artifact writing. |
| Boundary Review | Table | Claim Boundary = yes or Source Precedence Touch = yes or Data Boundary is not no-data | Group by boundary field | Surfaces tasks that need extra boundary review. |
| PR Review | Table | Pull Request is not empty | Group by Status | Tracks PR-open, needs-revision, and ready-to-merge work. |
| Phase Two Intake Prep | Table | Artifact Type = template and Notes contains Phase Two | Sort by Merge Order | Focuses on future intake templates without starting data work. |
| Closeout View | Table | Closeout Needed = yes | Group by Status | Shows what still needs tracker, handoff, or parent issue updates. |

## View operating notes

- Use the table layout for audit-heavy views because it exposes fields clearly.
- Use the board layout for work-in-progress status because it visualizes the task pipeline.
- Do not use roadmap as the default Objective Four view because dates are less important than merge order and dependency control.
- Roadmap may be added later if Phase Two planning needs target dates or iterations.

## Recommended filters

If labels from Task 3 are configured, use label-based filters:

```text
label:phase-1 label:objective-4
```

If labels are not configured yet, use explicit issue lists or title-prefix filters where supported:

```text
P1O4
```

For PR review views, use linked PR field, PR item type, or manual item inclusion.

For auto-add workflows, do not enable until labels and milestone are reviewed. If enabled later, use a conservative filter such as:

```text
label:objective-4
```

## Automation guidance

| Automation | Recommendation | Reason |
|---|---|---|
| Closed issue sets Status to Done/Merged | Allow after manual review | GitHub enables default closed/merged workflows in Projects; this is useful once the board is stable. |
| Merged PR sets Status to Done/Merged | Allow after manual review | Helps keep board aligned with PR state. |
| Auto-add matching items | Use cautiously after labels exist | Auto-add depends on filters; use `label:objective-4` only after labels are configured. |
| Auto-close issues when project Status changes | Do not enable initially | Board movement should not close issues before PR and tracker evidence exist. |
| Auto-archive completed items | Defer | Objective Four closeout should remain visible until release note and handoff are complete. |
| GitHub Actions automation | Defer | Too much automation before workflow docs and templates are complete. |

## Manual update rules

Until automation is configured, use this manual process:

1. Add task issue to the Project board after issue creation.
2. Set Task ID, Phase, Objective, Artifact Path, Artifact Type, and Data Boundary.
3. Move Status to Contracted after the artifact contract comment exists.
4. Move Status to Branch Created after the branch exists.
5. Move Status to Research Complete after sources are validated.
6. Move Status to Artifact Drafted after the repo artifact is committed.
7. Move Status to PR Open after PR creation.
8. Move Status to Ready to Merge only after acceptance criteria and dependency checks pass.
9. Move Status to Merged only after PR merge.
10. Update parent issue #119 after each merge.

## Dependency handling

Task 4 depends on Task 2 and Task 3 because board fields and views rely on the issue architecture and issue taxonomy.

| Dependency | Current state at drafting | Board handling |
|---|---|---|
| P1O4-T02 issue architecture | PR #130 open | Set Dependency Status to `depends-on-open-pr`. |
| P1O4-T03 issue taxonomy | PR #131 open | Set Dependency Status to `depends-on-open-pr`. |
| P1O4-T04 board spec | This branch | Do not mark Ready to Merge until dependency decision is made. |

If Task 4 is reviewed before #130 and #131 merge, the PR can remain open but should not be marked Ready to Merge unless you decide to override dependency order.

## Board creation sequence

When ready to configure the actual GitHub Project:

1. Merge P1O4-T02 issue architecture.
2. Merge P1O4-T03 issue taxonomy.
3. Review and merge this board spec.
4. Create the Project board named `BurnLens - Phase 1 Objective Four Repo Ops`.
5. Add Objective Four issues and PRs.
6. Create required fields.
7. Create recommended views.
8. Apply fields to existing issues.
9. Enable only conservative built-in automations.
10. Record board creation in the parent issue #119.

## Rejection and defer criteria

Defer or revise this board spec if:

- the board depends on labels or milestones that have not been reviewed;
- the board would auto-close issues before PR and tracker evidence exist;
- a required field duplicates another field without adding review value;
- a view cannot answer a clear workflow question;
- a view or field suggests implementation work that Phase One has not authorized;
- the board would become the source of truth instead of the repo artifacts and PRs;
- merge order ignores open dependencies from Tasks 2 and 3.

## Allowed uses

This artifact may be used to create a GitHub Project board, configure views and fields, guide manual board updates, and decide conservative automation settings.

## Forbidden uses

This artifact must not be used to claim that a GitHub Project board already exists, that project automation has been configured, that Objective Four is complete, or that later data, model, run, map, or public-demo work has begun.

## Versioning and provenance implications

Project board setup should be traceable to:

- task issue #121;
- parent issue #119;
- this artifact path;
- PR number;
- merge commit;
- tracker or handoff update;
- board creation date if configured later.

If the board is created later, record the board name, owner, creation date, fields created, views created, automations enabled, and any deviations from this specification.

## Claims-register check

Task 4 creates internal repo-management claims only.

Safe claim after Task 4:

> Objective Four has a documented Project board specification for views, fields, status logic, and conservative automation guidance.

Unsupported claims after Task 4:

- The GitHub Project board has been created.
- Labels or milestones have been configured.
- Automation has been enabled.
- Objective Four is complete.
- Later data, model, run, map, or public-demo work has begun.

## Acceptance checklist

| Check | Status | Notes |
|---|---|---|
| Task issue exists. | Satisfied | #121. |
| Parent issue is referenced. | Satisfied | #119. |
| Branch exists before research and artifact writing. | Satisfied | `p1o4t04b`. |
| Fresh research completed before artifact writing. | Satisfied | Research summarized above. |
| Artifact defines board purpose. | Satisfied | Purpose and decision sections included. |
| Artifact defines required fields. | Satisfied | Required fields table included. |
| Artifact defines status logic. | Satisfied | Status field specification included. |
| Artifact defines views. | Satisfied | Recommended views table included. |
| Artifact defines automation guidance. | Satisfied | Automation table included. |
| Artifact handles dependencies. | Satisfied | T02 and T03 dependencies noted. |
| Artifact includes rejection/defer criteria. | Satisfied | Rejection and defer section included. |
| Artifact preserves documentation-only boundary. | Satisfied | Boundary sections included. |
| Artifact creates no implementation output. | Satisfied | Specification only. |

## Pre-PR self-audit

| Question | Answer |
|---|---|
| Does the artifact answer so what? | Yes. It explains how the Project board should control Objective Four work visibility and review. |
| Does it include at least one decision? | Yes. Create one Objective Four repo-ops board after Tasks 2 and 3 are reviewed. |
| Does it include acceptance and rejection criteria? | Yes. |
| Does it include source-specific facts? | Yes. Research validation cites GitHub Project, view, field, and automation docs. |
| Does it preserve BurnLens boundaries? | Yes. |
| Does it say what is not done? | Yes. It states the board is not created or configured by this artifact. |
| Would a reviewer understand what to do next? | Yes. Proceed to P1O4-T05 after dependency review and merge. |

## Handoff note

Proceed to P1O4-T05 after this artifact is reviewed and merged, or keep this PR open until P1O4-T02 and P1O4-T03 are merged. P1O4-T05 should use this board spec plus the issue architecture and taxonomy to define branch naming, commit naming, PR review rules, merge order, and tracker update requirements.
