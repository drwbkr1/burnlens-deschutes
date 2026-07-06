# Phase 1 / Objective Four - Issue Taxonomy

## Status

Task 3 is open on issue #120.

- Parent issue: #119
- Working branch: `p1o4t03b`
- Artifact path: `docs/phase-one/objective-four/ISSUE_TAXONOMY.md`
- Current file status: drafted for pull request review

## Purpose

This artifact defines the issue taxonomy for Objective Four and later BurnLens Deschutes task work. It specifies label families, milestone guidance, issue-type policy, required task metadata, and application rules so future work can be filtered, reviewed, sequenced, and audited without relying on memory.

The taxonomy is a documentation standard. It does not create labels, milestones, or organization issue types by itself. Configuration can be done later, manually or through an allowed GitHub action, only after this document is reviewed.

## Boundary

This artifact is documentation and repo-management guidance only.

It does not authorize data acquisition, imagery download, final AOI selection, label creation, mask creation, baseline generation, model training, inference, metric computation, map publication, website demo integration, outside validation claims, or endorsement claims.

## Research timing

Fresh research was conducted after the task branch was created and before this artifact was written.

## Research validation summary

| Claim ID | Claim | Source authority | Evidence summary | Decision for Task 3 |
|---|---|---|---|---|
| P1O4-T03-R01 | Labels can classify issues, pull requests, and discussions. | GitHub Docs: Managing labels | GitHub states that labels can classify issues, pull requests, and discussions and can be created, edited, applied, and deleted. | Define BurnLens label families for phase, objective, artifact type, boundary, workflow status, and future implementation class. |
| P1O4-T03-R02 | Labels are repository-scoped. | GitHub Docs: Managing labels | GitHub states labels can be used in the repository where they are created and that changes in one repository do not affect labels in other repositories. | Define taxonomy for `drwbkr1/burnlens-deschutes`; do not assume labels exist in the site repo. |
| P1O4-T03-R03 | Default labels exist but can be edited or deleted. | GitHub Docs: Managing labels | GitHub lists default labels such as `bug`, `documentation`, `enhancement`, `question`, and `wontfix`, and notes they can be edited or deleted. | Keep GitHub defaults only where useful; add BurnLens-specific labels for project-control needs. |
| P1O4-T03-R04 | Milestones track progress on groups of issues and pull requests. | GitHub Docs: About milestones | GitHub states milestones can track progress on groups of issues or pull requests in a repository. | Use milestones for phase/objective gates, not individual files. |
| P1O4-T03-R05 | Issue types are organization-level controls. | GitHub Docs: Managing issue types | GitHub states organization owners can modify issue types, that issue types classify issues across an organization, and that default types include task, bug, and feature. | Treat issue types as optional; use labels and title prefixes as the primary taxonomy for this personal repo unless organization settings are available. |

## Research links

- GitHub Docs: Managing labels - https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels
- GitHub Docs: About milestones - https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/about-milestones
- GitHub Docs: Managing issue types - https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/managing-issue-types-in-an-organization

## Artifact contract

| Field | Requirement |
|---|---|
| Task | P1O4-T03 - Create issue taxonomy |
| Artifact filename | `docs/phase-one/objective-four/ISSUE_TAXONOMY.md` |
| Artifact purpose | Define labels, milestones, issue-type policy, task metadata, and application rules. |
| Required decisions | Confirm taxonomy groups, label naming pattern, milestone plan, issue-type fallback, and per-task metadata requirements. |
| Required research claims | GitHub labels, milestones, repository scope, default labels, and organization issue types. |
| Required tables | Label families, milestone plan, issue-type policy, task metadata, application rules, acceptance checklist. |
| Too thin if | It lists labels without explaining when to use them, what not to use them for, or how they support review and traceability. |

## Taxonomy decision

BurnLens should use labels as the primary issue taxonomy, milestones as objective/phase progress gates, and issue types only if the repository context supports them.

Because `burnlens-deschutes` is a personal repository rather than an organization-level planning environment, the reliable default structure is:

1. title prefixes for task identity;
2. labels for filtering and review state;
3. milestones for objective-level grouping;
4. Project board fields later in P1O4-T04;
5. issue types only if available through GitHub settings.

## Required issue title pattern

Use this pattern for Objective Four task issues:

```text
P1O4-TXX Short task name
```

Examples:

```text
P1O4-T03 Create issue taxonomy
P1O4-T04 Create project board spec
P1O4-T05 Define branch and PR workflow
```

For later objectives, preserve the same pattern:

```text
P1O5-T01 Short task name
P2O1-T01 Short task name
```

## Required label families

| Family | Purpose | Required? | Examples |
|---|---|---:|---|
| Phase | Shows the project phase. | Yes | `phase-1`, `phase-2`, `phase-3` |
| Objective | Shows the objective. | Yes | `objective-4`, `objective-5` |
| Artifact type | Shows what kind of repo output is being changed. | Yes | `documentation`, `template`, `records`, `workflow` |
| Research | Shows whether outside validation is required or complete. | Conditional | `research-required`, `research-complete` |
| Boundary | Shows special review boundaries. | Conditional | `no-data`, `claim-boundary`, `source-precedence` |
| Work status | Shows workflow state when not represented by PR status. | Conditional | `blocked`, `needs-review`, `ready-to-merge` |
| Tooling | Shows the work mode or tool context. | Conditional | `codex-task`, `repo-ops`, `prompt-built` |
| Future implementation class | Reserved for later phases. | Future | `aoi-record`, `source-record`, `provenance`, `baseline`, `model`, `run-package` |

## Recommended Objective Four labels

| Label | Family | Use when | Do not use when |
|---|---|---|---|
| `phase-1` | Phase | Any Phase One issue or PR. | Work belongs to later phases. |
| `objective-4` | Objective | Any Objective Four issue or PR. | Work belongs to another objective. |
| `documentation` | Artifact type | Markdown docs, policy docs, trackers, handoffs, closeouts. | Code, data, or generated outputs are being changed. |
| `template` | Artifact type | Reusable task, issue, PR, manifest, or intake templates. | One-off docs that are not intended for reuse. |
| `records` | Artifact type | Prompt logs, decision logs, research logs, claims registers. | Static guidance documents. |
| `workflow` | Artifact type | Branch/PR rules, board specs, issue architecture, repo processes. | Technical model/data workflow code. |
| `repo-ops` | Tooling | Repository organization and operating-system work. | Data/model implementation work. |
| `codex-task` | Tooling | Work directly affects Codex or prompt-assisted task execution. | Generic documentation with no Codex effect. |
| `prompt-built` | Tooling | Work documents or supports prompt-assisted production. | Manual-only administrative updates. |
| `research-required` | Research | Task must validate current or technical claims before artifact writing. | No source-backed claim is involved. |
| `research-complete` | Research | Research was performed and recorded in the artifact. | Research has not yet been documented. |
| `claim-boundary` | Boundary | Task affects what BurnLens can safely say. | Task has no project-claim implication. |
| `source-precedence` | Boundary | Task affects source authority, official-source language, or public-context claims. | Task is purely internal repo management. |
| `no-data` | Boundary | Task must not create, download, process, or retain data. | Later phases explicitly authorize data handling. |
| `blocked` | Work status | Task cannot proceed until a dependency is resolved. | Work is merely waiting for normal review. |
| `needs-review` | Work status | Artifact is ready for human review but should not merge yet. | PR is already approved or ready to merge. |
| `ready-to-merge` | Work status | Review is complete and branch is ready to merge. | Any acceptance criteria remain unresolved. |

## Future implementation labels

These labels should be reserved for later phases. They should not be applied during Objective Four unless the task is creating a template or policy for that future class.

| Label | Use later for | Allowed in Objective Four? |
|---|---|---|
| `aoi-record` | AOI candidate or selected AOI records. | Template/policy only. |
| `source-record` | Imagery, reference, or local overlay source records. | Template/policy only. |
| `access-log` | Source access attempts and results. | Template/policy only. |
| `crs-precheck` | Format and CRS checks. | Template/policy only. |
| `provenance` | Provenance manifests or metadata records. | Template/policy only. |
| `claims-register` | Allowed, conditional, and forbidden claims. | Yes, if record-related. |
| `baseline` | Baseline method or output work. | No, until later phase authorization. |
| `model` | Model architecture, training, evaluation, or inference. | No, until later phase authorization. |
| `run-package` | Timestamped run bundles. | No, until later phase authorization. |
| `public-artifact` | Site, demo, map, case study, or public portfolio artifact. | No, unless a docs-only public-claim policy task. |

## Label application rules

| Rule | Requirement |
|---|---|
| Minimum task labels | Every Objective Four issue should have `phase-1`, `objective-4`, and at least one artifact-type label. |
| Boundary label | Use `no-data` for every Objective Four task unless a later task explicitly leaves the documentation-only scope. |
| Research label | Use `research-required` before branch research is complete; replace or supplement with `research-complete` after the artifact records validation. |
| Claim label | Use `claim-boundary` when the task changes wording about what BurnLens can safely claim. |
| Source label | Use `source-precedence` when the task touches official-source hierarchy or conflict language. |
| Status label | Use only one of `blocked`, `needs-review`, or `ready-to-merge` at a time. |
| Future labels | Do not use `baseline`, `model`, `run-package`, or `public-artifact` for Phase One Objective Four implementation claims. |

## Recommended milestone plan

| Milestone | Purpose | Issues included | Close condition |
|---|---|---|---|
| `Phase 1 / Objective Four` | Track all Objective Four repo-control tasks. | #117, #118, #120-#129 | All Objective Four artifacts merged or explicitly deferred. |
| `Phase 1 Closeout` | Track final Phase One closure and transition readiness. | Later closeout/exit tasks only. | Phase One handoff complete. |
| `Phase 2 Intake` | Track future data-intake preparation work. | Future Phase Two issues only. | Phase Two intake templates used or superseded. |

Milestones should not be used for single documents. They should group issues and pull requests that represent a meaningful objective, phase, or release gate.

## Issue-type policy

| Issue type | GitHub default? | BurnLens use | Fallback if unavailable |
|---|---:|---|---|
| Task | Yes | Standard unit of work for objective tasks. | Use title prefix `P1O4-TXX`. |
| Bug | Yes | Later code or workflow defects. | Use label `bug` only if actual defect exists. |
| Feature | Yes | Later app/tool feature requests. | Use label `enhancement` or objective label. |
| Documentation | Custom if supported | Documentation-only artifacts. | Use label `documentation`. |
| Research validation | Custom if supported | Source-backed validation tasks. | Use labels `research-required` and `research-complete`. |
| Claim boundary | Custom if supported | Tasks that affect allowed or forbidden project claims. | Use label `claim-boundary`. |

Do not depend on custom issue types unless the repository or organization settings clearly support them. Labels and title prefixes must remain sufficient for the workflow to function.

## Required issue metadata

Every future task issue should include these fields in the issue body or task packet:

```text
task_id:
+ parent_issue:
+ branch:
+ artifact_path:
+ artifact_type:
+ phase:
+ objective:
+ required_labels:
+ milestone:
+ dependencies:
+ research_required: yes | no
+ claim_boundary: yes | no
+ source_precedence_touch: yes | no
+ data_boundary: no-data | template-only | authorized-later
+ expected_pr_close_keyword:
+ acceptance_checklist:
+ handoff_note:
```

The plus signs above are placeholders indicating required fields; they should not be copied into final issue forms unless a template requires them.

## Objective Four task label recommendations

| Task | Issue | Recommended labels | Recommended milestone |
|---|---:|---|---|
| P1O4-T01 | #117 | `phase-1`, `objective-4`, `documentation`, `workflow`, `repo-ops`, `research-complete`, `no-data` | `Phase 1 / Objective Four` |
| P1O4-T02 | #118 | `phase-1`, `objective-4`, `documentation`, `workflow`, `repo-ops`, `research-complete`, `no-data` | `Phase 1 / Objective Four` |
| P1O4-T03 | #120 | `phase-1`, `objective-4`, `documentation`, `workflow`, `repo-ops`, `research-complete`, `no-data` | `Phase 1 / Objective Four` |
| P1O4-T04 | #121 | `phase-1`, `objective-4`, `documentation`, `workflow`, `repo-ops`, `no-data` | `Phase 1 / Objective Four` |
| P1O4-T05 | #122 | `phase-1`, `objective-4`, `documentation`, `workflow`, `repo-ops`, `no-data` | `Phase 1 / Objective Four` |
| P1O4-T06 | #123 | `phase-1`, `objective-4`, `template`, `workflow`, `repo-ops`, `no-data` | `Phase 1 / Objective Four` |
| P1O4-T07 | #124 | `phase-1`, `objective-4`, `documentation`, `codex-task`, `repo-ops`, `no-data` | `Phase 1 / Objective Four` |
| P1O4-T08 | #125 | `phase-1`, `objective-4`, `template`, `codex-task`, `prompt-built`, `no-data` | `Phase 1 / Objective Four` |
| P1O4-T09 | #126 | `phase-1`, `objective-4`, `records`, `prompt-built`, `repo-ops`, `no-data` | `Phase 1 / Objective Four` |
| P1O4-T10 | #127 | `phase-1`, `objective-4`, `template`, `provenance`, `claims-register`, `no-data` | `Phase 1 / Objective Four` |
| P1O4-T11 | #128 | `phase-1`, `objective-4`, `documentation`, `workflow`, `repo-ops`, `claim-boundary`, `no-data` | `Phase 1 / Objective Four` |
| P1O4-T12 | #129 | `phase-1`, `objective-4`, `documentation`, `workflow`, `repo-ops`, `claim-boundary`, `no-data` | `Phase 1 / Objective Four` |

## Configuration sequence

If labels and milestones are later created manually, use this order:

1. Review and merge this taxonomy.
2. Create or confirm the milestone `Phase 1 / Objective Four`.
3. Create or confirm phase/objective labels.
4. Create or confirm artifact-type labels.
5. Create or confirm research/boundary/status labels.
6. Apply labels to existing Objective Four issues.
7. Apply the milestone to Objective Four task issues.
8. Do not configure organization issue types unless the account context supports them.

## Rejection and defer criteria

Defer or revise the taxonomy if:

- a label name is ambiguous;
- a label overlaps heavily with another label;
- a status label could conflict with PR state;
- a milestone is too narrow to track meaningful progress;
- an issue type is recommended even though repository settings do not support it;
- a label implies implementation work that Phase One has not authorized;
- the taxonomy cannot be applied consistently to #117, #118, and #120-#129.

## Allowed uses

This artifact may be used to create labels, define milestones, plan Project board fields, improve issue templates, and filter Objective Four issues.

## Forbidden uses

This artifact must not be used to claim that labels or milestones already exist, that Project board work is complete, that issue templates are complete, or that any later implementation phase has begun.

## Versioning and provenance implications

Each issue taxonomy change should be traceable to:

- task issue number;
- parent issue #119;
- taxonomy artifact path;
- PR number;
- merge commit;
- tracker or handoff update.

If labels or milestones are later created in GitHub settings, record the configuration date and the source artifact that authorized them.

## Claims-register check

Task 3 creates internal repo-management claims only.

Safe claim after Task 3:

> Objective Four has a documented issue taxonomy for labels, milestones, issue-type policy, and required task metadata.

Unsupported claims after Task 3:

- Labels have been configured in GitHub.
- Milestones have been configured in GitHub.
- Organization issue types have been changed.
- Project board fields have been created.
- Later data, model, run, map, or public-demo work has begun.

## Acceptance checklist

| Check | Status | Notes |
|---|---|---|
| Task issue exists. | Satisfied | #120. |
| Parent issue is referenced. | Satisfied | #119. |
| Branch exists before research and artifact writing. | Satisfied | `p1o4t03b`. |
| Fresh research completed before artifact writing. | Satisfied | Research summarized above. |
| Artifact defines label families. | Satisfied | Required label families table included. |
| Artifact defines recommended labels. | Satisfied | Objective Four label recommendations included. |
| Artifact defines milestone plan. | Satisfied | Recommended milestone plan included. |
| Artifact defines issue-type policy. | Satisfied | Issue-type policy table included. |
| Artifact defines required metadata. | Satisfied | Required metadata block included. |
| Artifact includes rejection/defer criteria. | Satisfied | Rejection and defer section included. |
| Artifact preserves documentation-only boundary. | Satisfied | Boundary sections included. |
| Artifact creates no implementation output. | Satisfied | Taxonomy only. |

## Pre-PR self-audit

| Question | Answer |
|---|---|
| Does the artifact answer so what? | Yes. It explains how issues should be classified, filtered, and governed. |
| Does it include at least one decision? | Yes. Labels are primary, milestones group objective work, issue types are optional. |
| Does it include acceptance and rejection criteria? | Yes. |
| Does it include source-specific facts? | Yes. Research validation cites GitHub label, milestone, and issue-type docs. |
| Does it preserve BurnLens boundaries? | Yes. |
| Does it say what is not done? | Yes. It states configuration is not complete by this artifact alone. |
| Would a reviewer understand what to do next? | Yes. Proceed to P1O4-T04 after review and merge. |

## Handoff note

Proceed to P1O4-T04 after this artifact is reviewed and merged. P1O4-T04 should use this taxonomy to define GitHub Project board views and fields, including phase, objective, status, artifact path, research requirement, claim-boundary flag, source-precedence flag, and PR link fields.
