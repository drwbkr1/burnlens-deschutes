# BurnLens Pull Request

> This template records author assertions and review evidence. Author checkboxes are not independent human review or formal GitHub approval. AI-assisted review is supplemental. A human must record the final outcome before merge.

Detailed review record: `docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md`

## Summary and linkage

- Task ID: `P#O#-T##`
- Task issue: `#`
- Parent issue: `#`
- Branch: `p#o#t##b`
- Base: `main`
- Dependencies: `[issues / PRs / none]`
- Primary artifact(s):
  - `[path]`
- Changed files:
  - `[path]`
- Summary:
  - `[what changed]`
- Material decisions:
  - `[decision and rationale]`

## Author self-audit

- [ ] PR title uses `P#O#-T## Short task title` or another issue-authorized task pattern.
- [ ] The task issue and capsule authorize this exact scope.
- [ ] The branch and base match the task contract.
- [ ] Dependencies are satisfied or accurately described as blocked.
- [ ] Actual changed files match the allowed-file list.
- [ ] No scratch, generated, credential, temporary, or connector-test file is included.
- [ ] Acceptance criteria are mapped to evidence in the diff, research, or verification results.

Author self-audit completed by: `[name or handle]`

> Completing this section does not satisfy the independent human-review requirement.

## Prompt/build log

- Prompt-assisted edits used: `yes | no`
- Prompt/build log: `[records/prompt-build-log/... / not applicable with reason]`
- [ ] The log records task identity, files, research, decisions, verification, boundaries, claims, and handoff where required.
- [ ] The log excludes secrets, credentials, private reasoning, raw private transcripts, unnecessary personal information, and unreviewed operational guidance.

## Research

- Research required: `yes | no`
- Official or primary sources checked:
  - `[source and URL / none]`
- Adopted decisions:
  - `[decision]`
- No-research rationale, when applicable: `[task-specific reason]`
- [ ] Current external claims are source-backed and were not adopted from memory alone.

## Tests and checks

Do not write `tests passed` without naming the checks or commands that actually ran.

| Check | Command or inspection method | Actual result | Limitation or evidence |
|---|---|---|---|
| `[name]` | `[command or method]` | `passed | failed | partial | blocked | not applicable` | `[notes / path]` |

Checks not run or not applicable:

| Check | Task-specific reason |
|---|---|
| `[check]` | `[reason]` |

- [ ] Documentation/template work still received applicable Markdown, path, link, structure, requirement-coverage, consistency, scope, boundary, claims, sensitive-material, and diff checks.
- [ ] Code/configuration work reports the actual applicable test, build, lint, type, schema, security, or smoke commands and results.
- [ ] No nonexistent CI job or status check is claimed or required.

## Security and sensitive material

- [ ] No secrets, credentials, tokens, cookies, private URLs, or sensitive source material are included.
- [ ] No private chain-of-thought or hidden reasoning is included.
- [ ] No unnecessary personal information is included.
- [ ] No unreviewed operational wildfire or emergency guidance is included.

## Boundaries, source precedence, and claims

- [ ] The work stays within the authorized issue and phase boundary.
- [ ] Official sources govern where applicable.
- [ ] BurnLens remains experimental and non-operational.
- [ ] No unsupported official, operational, field-validation, agency-endorsement, emergency-readiness, data-readiness, model-readiness, or release claim was introduced.
- [ ] Public-facing claims, when separately authorized, have evidence and limitations.
- [ ] Tag and GitHub Release status are explicit when relevant.
- [ ] This PR does not imply that repository settings, required approvals, required checks, CI, CODEOWNERS, branch protection, or rulesets are configured.

## AI-assisted review, when used

- AI-assisted review used: `yes | no`
- Tool or mode: `[tool / not used]`
- Review target: `branch diff | working tree | commit | PR | named files | other`
- Findings and severity: `[summary / none]`
- Fixes applied: `[summary / none]`
- Follow-up result: `[result / not run with reason]`
- Unresolved AI findings: `[findings / none]`

- [ ] AI findings are labeled as AI-assisted.
- [ ] AI review was not treated as human approval or merge authorization.

## Human review

A human reviewer or solo-maintainer evidence owner completes this section after inspecting the issue, capsule, full diff, research, checks, acceptance criteria, boundaries, claims, close keyword, and handoff.

- Human reviewer or evidence owner: `[name or handle]`
- Review evidence: `[GitHub review / PR comment / completed checklist]`
- Blocking findings remaining: `[findings / none]`
- Human outcome: `Approve | Request changes | Defer or reject | pending`

- [ ] The complete changed-file list and content diff were inspected.
- [ ] Checks and actual results, including non-applicability reasons, were inspected.
- [ ] Unresolved comments, review threads, and AI findings were inspected.
- [ ] Author self-audit and AI review were not treated as independent approval.

For the current solo-maintainer workflow, Drew may record the human outcome through an explicit PR comment or a completed `docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md`. This is project-policy evidence, not formal author self-approval.

## Merge authorization

Complete only after the human outcome is `Approve`.

- Merge authorized: `yes | no | pending`
- Authorized by: `[name or handle]`
- Authorization evidence: `[comment / review / checklist]`
- Final reviewed head SHA: `[SHA]`
- Merge method: `squash | merge | rebase | pending`
- [ ] All blocking findings are resolved.
- [ ] Dependencies are resolved.
- [ ] The final diff remains within the authorized file scope.
- [ ] Required checks are accurately reported.
- [ ] Unresolved comments or threads are resolved or explicitly accepted by the human reviewer.
- [ ] Merge authorization does not implicitly authorize settings, data, models, public outputs, tags, Releases, or other separately controlled work.

## Close keyword and handoff

Use exactly the task-scoped close keyword below and replace the placeholder:

```text
Closes #TASK_ISSUE
```

- [ ] No parent-issue closing keyword is present unless this is an authorized closeout task.
- Next task or closeout action: `[task / action]`
- Required next context: `[paths / issues / PR]`
- Post-merge status inspection: `README | tracker | prompt logs | other | none`
- Expected status sync: `inspect after merge | expected | not expected`
