# Phase 1 / Objective Four - Branch and PR Workflow

## Status

Task 5 is open on issue #122.

- Parent issue: #119
- Working branch: `p1o4t05b`
- Artifact path: `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md`
- Current file status: drafted for pull request review
- Prior dependency status: P1O4-T01, P1O4-T02, P1O4-T03, and P1O4-T04 are merged.

## Purpose

This artifact defines the branch, commit, pull request, review, merge, and post-merge update workflow for Objective Four and later BurnLens Deschutes task work.

The goal is to keep repo history clean, make every task traceable, prevent accidental closure of parent issues, and ensure that future prompt-built work remains reviewable before it is treated as portfolio evidence.

## Boundary

This artifact is documentation and repo-management guidance only.

It does not authorize data acquisition, imagery download, final AOI selection, label creation, mask creation, baseline generation, model training, inference, metric computation, map publication, website demo integration, outside validation claims, or endorsement claims.

## Research timing

Fresh research was conducted after the task branch was created and before this artifact was written.

## Research validation summary

| Claim ID | Claim | Source authority | Evidence summary | Decision for Task 5 |
|---|---|---|---|---|
| P1O4-T05-R01 | Pull requests are the correct review unit for proposed repo changes. | GitHub Docs: About pull requests | GitHub states that pull requests propose, review, and merge code changes, and support discussion and review before merging. | Require a PR for every meaningful task artifact. |
| P1O4-T05-R02 | PR pages expose conversation, commits, checks, file changes, and merge status. | GitHub Docs: About pull requests | GitHub describes PR tabs for conversation, commits, checks, files changed, and merge status. | Require PR reviewers to check changed files, commits, status, and task linkage before merge. |
| P1O4-T05-R03 | Draft PRs are useful for work in progress and cannot be merged. | GitHub Docs: About pull requests | GitHub states draft PRs cannot be merged and are useful for sharing work-in-progress before formal review. | Use draft PRs for incomplete artifacts or dependency-blocked tasks. |
| P1O4-T05-R04 | PR closing keywords can automatically close linked issues when merged into the default branch. | GitHub Docs: Linking a pull request to an issue | GitHub states linked PRs can close issues when merged into the default branch, and gives keyword syntax such as `Closes #10`. | Use `Closes #task-issue` only for the specific task issue, never the parent issue. |
| P1O4-T05-R05 | Squash merging combines multiple topic-branch commits into one commit on the default branch. | GitHub Docs: About merge methods | GitHub states squash and merge combines a pull request's commits into one commit on the default branch and can create a clear history. | Prefer squash merges for Objective Four docs tasks, especially prompt-built branches with troubleshooting commits. |
| P1O4-T05-R06 | Protected branches can require reviews, checks, conversation resolution, and linear history. | GitHub Docs: About protected branches | GitHub states branch protection rules can require reviews, status checks, conversation resolution, signed commits, and linear history. | Recommend optional branch protection later, but do not require it for this personal repo until templates and workflow docs are stable. |

## Research links

- GitHub Docs: About pull requests - https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests
- GitHub Docs: Linking a pull request to an issue - https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue
- GitHub Docs: About merge methods on GitHub - https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github
- GitHub Docs: About protected branches - https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches

## Artifact contract

| Field | Requirement |
|---|---|
| Task | P1O4-T05 - Define branch and PR workflow |
| Artifact filename | `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md` |
| Artifact purpose | Define branch naming, commit naming, PR review rules, merge expectations, and post-merge update requirements. |
| Required decisions | Confirm branch naming, PR body rules, close-keyword rule, squash-merge preference, dependency handling, and post-merge updates. |
| Required research claims | GitHub PR structure, draft PRs, issue linking, merge methods, and protected branches. |
| Required tables | Branch naming table, commit naming table, PR checklist, merge decision table, post-merge table, acceptance checklist. |
| Too thin if | It only says create a branch and PR without defining naming, review, dependency, merge, or update rules. |

## Workflow decision

Use this loop for every remaining Objective Four task:

```text
artifact contract -> issue comment -> task branch -> fresh research -> artifact file -> self-audit -> PR -> review -> squash merge -> issue/parent/tracker update
```

For later phases, the same pattern applies, but data or model work must add extra provenance, run, and boundary records before PR review.

## Branch naming standard

Use short, predictable branch names that avoid punctuation issues in connector workflows.

| Work type | Pattern | Example | Notes |
|---|---|---|---|
| Objective Four task | `p1o4tXXb` | `p1o4t05b` | Preferred for connector compatibility. |
| Later Phase One task | `p1oXtYYb` | `p1o5t01b` | Keep phase/objective/task visible. |
| Later phase task | `pXoYtZZb` | `p2o1t01b` | Use same compact pattern. |
| Remediation | `p1o4tXXfixb` | `p1o4t05fixb` | Use only after PR review identifies needed changes. |
| Experimental local branch | `scratch-brief-name` | `scratch-table-test` | Do not open PR unless converted to a task branch. |

Avoid branch names with slashes for this prompt-built workflow unless using local Git directly. Slashes are normal in Git but have caused connector friction in this project.

## Commit naming standard

| Artifact type | Commit message pattern | Example |
|---|---|---|
| Documentation | `docs(p1o4): short action` | `docs(p1o4): define branch and pr workflow` |
| Template | `templates(p1o4): short action` | `templates(p1o4): add issue template` |
| Records | `records(p1o4): short action` | `records(p1o4): add prompt build log` |
| Workflow config | `workflow(p1o4): short action` | `workflow(p1o4): add pr template` |
| Cleanup | `chore(p1o4): short action` | `chore(p1o4): remove temporary file` |

Use concise messages on task branches. Squash merge commit titles should match the PR title.

## Pull request title standard

Use this format:

```text
P1O4-TXX Short task title
```

Examples:

```text
P1O4-T05 Define branch and PR workflow
P1O4-T06 Add issue and PR templates
P1O4-T07 Add AGENTS instructions
```

## Pull request body standard

Each task PR should include:

```text
Summary:
- Adds or updates <artifact path>.
- Records fresh research before artifact writing.
- Preserves documentation-only boundary.

Acceptance:
- [ ] Artifact path is correct.
- [ ] Research validation is present.
- [ ] Boundary language is present.
- [ ] Rejection/defer criteria are present.
- [ ] Claims-register check is present.
- [ ] Handoff note is present.

Close:
Closes #TASK_ISSUE
```

Keep the PR close keyword scoped to the task issue only. Do not write `Closes #119` unless deliberately closing the Objective Four parent after final closeout review.

## Close-keyword rule

| Issue type | Use closing keyword? | Example | Notes |
|---|---:|---|---|
| Task issue | Yes | `Closes #122` | Use exactly one task issue unless the PR truly completes multiple tasks. |
| Parent issue | No | N/A | Parent #119 closes only after Objective Four closeout and release note are complete. |
| Dependency issue | No | `Refs #120` | Use `Refs` or plain text for dependencies. |
| Outside issue | Rare | `Refs owner/repo#123` | Avoid unless cross-repo work is intentional. |

## Required pre-PR checks

Before opening a PR, verify:

| Check | Required result |
|---|---|
| Branch exists | Branch is created from current `main` unless deliberately based on another task branch. |
| Research completed | Fresh research is done after branch creation and before artifact writing. |
| Diff is clean | Only intended files are changed. |
| Artifact contract satisfied | Purpose, decisions, research claims, tables, and boundary language are present. |
| Boundary preserved | No unauthorized data/model/map/public-output work. |
| Claims checked | Artifact states safe and unsupported claims. |
| Dependencies noted | Open dependency PRs are named. |
| Handoff included | Next task is clear. |

## Pull request review checklist

| Review area | Reviewer question |
|---|---|
| Scope | Does the PR do only the task it claims to do? |
| Path | Is the artifact in the correct repo path? |
| Research | Are research claims current and source-backed? |
| Boundary | Does the artifact preserve documentation-only/no-data constraints? |
| Source precedence | Does it avoid implying official authority? |
| Dependency | Does it merge in the correct order? |
| Diff | Are there accidental files or temporary files? |
| Close keyword | Does it close only the task issue? |
| Handoff | Does it tell the next task what to do? |

## Merge method decision

| Situation | Merge method | Reason |
|---|---|---|
| Normal Objective Four doc task | Squash merge | Keeps main history clean and one task equals one commit. |
| Branch has connector troubleshooting commits | Squash merge | Preserves final artifact without noisy intermediate commits. |
| Multiple meaningful commits that should be retained | Merge commit | Use rarely; explain in PR body. |
| Linear-history policy requires it | Rebase or squash | Follow repo settings. |
| PR has unresolved dependency | Do not merge | Keep open or draft until dependency is resolved. |
| PR has accidental files | Do not merge | Clean diff first. |

Preferred default for Objective Four is squash merge.

## Merge order rules

| Case | Rule |
|---|---|
| Independent tasks | Merge after review. |
| Task depends on prior artifact | Merge dependency first. |
| Task references open PR output | Keep as draft or mark dependency clearly. |
| Later task supersedes earlier artifact | Update both PR body and artifact handoff note. |
| Parent issue closure | Only after closeout and release note are merged. |

## Post-merge update rules

After each task merge:

| Update target | Required update |
|---|---|
| Task issue | Confirm PR merged and artifact path. Usually auto-closed by PR close keyword. |
| Parent issue #119 | Add comment with task, PR, artifact, status, and next task. |
| Objective tracker | Update status if tracker update is in scope for the task or closeout. |
| Handoff artifact | Update only in closeout/handoff tasks. |
| Project board | If configured, move item to Merged and record PR number. |

Recommended parent issue comment:

```text
P1O4-TXX merged.
PR: #PR_NUMBER
Artifact: path/to/artifact.md
Status: complete
Next task: P1O4-TYY
```

## Dependency handling for open PRs

| Dependency state | Allowed action |
|---|---|
| Dependency merged | Proceed normally. |
| Dependency PR open and artifact needed | Draft artifact may be created, but PR should not merge until dependency is resolved. |
| Dependency unclear | Add `Dependency Status: blocked` in artifact and PR body. |
| User intentionally overrides order | Record override in PR body and parent issue comment. |

## Connector-friction rule

If the GitHub connector blocks a normal create-file action:

1. Do not downgrade artifact quality.
2. Try the known safer `update_file` new-file path with `sha: new`.
3. Verify the diff immediately.
4. Remove any temporary test files before opening PR.
5. Use squash merge if the branch history contains troubleshooting commits.
6. Record material deviations in the final task summary.

## Branch protection recommendation

Branch protection is not required yet for Objective Four because this is a personal portfolio repo and the workflow is still being documented. Once Objective Four is complete, consider a `main` branch protection rule that requires:

- PR before merge;
- conversation resolution;
- no force pushes;
- no branch deletion;
- optional status checks if tests or linting are added;
- optional linear history if squash merges remain standard.

Do not enable strict required checks before tests or templates exist, because that could block documentation PRs unnecessarily.

## Allowed uses

This workflow may be used to create task branches, write task artifacts, open PRs, review PRs, merge completed documentation tasks, update parent issue records, and guide later issue/PR templates.

## Forbidden uses

This workflow must not be used to bypass research, bypass PR review, close parent issues early, merge implementation work before authorization, or imply that BurnLens outputs are official, operational, externally validated, or emergency-ready.

## Versioning and provenance implications

Every task should be traceable to:

- issue number;
- branch name;
- artifact path;
- research validation section;
- PR number;
- merge method;
- merge commit SHA;
- parent issue update;
- tracker or handoff update when applicable.

## Claims-register check

Task 5 creates internal repo-management claims only.

Safe claim after Task 5:

> Objective Four has a documented branch, PR, review, merge, and post-merge workflow for repo-control tasks.

Unsupported claims after Task 5:

- Branch protection has been configured.
- Required reviews or status checks have been enabled.
- PR templates have been created.
- Issue templates have been created.
- Later data, model, run, map, or public-demo work has begun.

## Acceptance checklist

| Check | Status | Notes |
|---|---|---|
| Task issue exists. | Satisfied | #122. |
| Parent issue is referenced. | Satisfied | #119. |
| Branch exists before research and artifact writing. | Satisfied | `p1o4t05b`. |
| Fresh research completed before artifact writing. | Satisfied | Research summarized above. |
| Artifact defines branch naming. | Satisfied | Branch naming standard included. |
| Artifact defines commit naming. | Satisfied | Commit naming table included. |
| Artifact defines PR body standard. | Satisfied | PR body standard included. |
| Artifact defines close-keyword rules. | Satisfied | Close-keyword table included. |
| Artifact defines merge method decision. | Satisfied | Merge decision table included. |
| Artifact defines post-merge updates. | Satisfied | Post-merge table included. |
| Artifact preserves documentation-only boundary. | Satisfied | Boundary sections included. |
| Artifact creates no implementation output. | Satisfied | Workflow documentation only. |

## Pre-PR self-audit

| Question | Answer |
|---|---|
| Does the artifact answer so what? | Yes. It defines how future work moves safely from issue to merge. |
| Does it include at least one decision? | Yes. Compact branch names, task-scoped PR close keywords, and squash merges are the Objective Four defaults. |
| Does it include acceptance and rejection criteria? | Yes. |
| Does it include source-specific facts? | Yes. Research validation cites GitHub PR, issue-linking, merge-method, and branch-protection docs. |
| Does it preserve BurnLens boundaries? | Yes. |
| Does it say what is not done? | Yes. It states branch protection and templates are not yet configured. |
| Would a reviewer understand what to do next? | Yes. Proceed to P1O4-T06 after review and merge. |

## Handoff note

Proceed to P1O4-T06 after this artifact is reviewed and merged. P1O4-T06 should create issue and PR templates that encode the artifact contract, research-before-artifact rule, boundary checks, close-keyword rule, and post-merge update requirements defined here.
