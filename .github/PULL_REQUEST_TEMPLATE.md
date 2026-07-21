# BurnLens Pull Request

> This template records checkpoint scope, evidence, and review. Author assertions and AI-assisted findings are not independent approval. Required owner decisions apply only to exact candidate evidence or execution-goal stop conditions; routine merge authority comes from the controlling goal.

Checkpoint cadence: `docs/governance/CHECKPOINT_POLICY.md`. Historical review checklists may be used as optional inspection aids, but they do not override the controlling goal or current owner-decision rules.

## Summary and linkage

- Task ID: `P#O#-T## | BL-GOV-### | issue-authorized exception ID`
- Checkpoint class: `milestone | exception`
- Milestone outcome: `[coherent project-truth change]`
- Entry condition: `[verified dependency]`
- Exit condition or exception trigger: `[condition]`
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

## Evidence-unit ledger

| Unit ID | Purpose | Inputs / outputs and hashes | Gate result | Disposition | Retained failure or limitation |
|---|---|---|---|---|---|
| `[ID]` | `[bounded question]` | `[records and hashes]` | `[pass/fail by gate family]` | `pass | remediate | exclude | defer | stop` | `[retained evidence]` |

- [ ] Every registered evidence unit is listed.
- [ ] Failed, superseded, excluded, and deferred units remain visible.
- [ ] The milestone exit condition is satisfied, or the exception trigger is valid and documented.

## Author self-audit

- [ ] PR title uses `P#O#-T## Short checkpoint title` or another issue-authorized checkpoint pattern.
- [ ] The task issue and capsule authorize this exact scope.
- [ ] The branch and base match the task contract.
- [ ] Dependencies are satisfied or accurately described as blocked.
- [ ] Actual changed files match the allowed-file list.
- [ ] No scratch, generated, credential, temporary, or connector-test file is included.
- [ ] Acceptance criteria are mapped to evidence in the diff, research, or verification results.
- [ ] Batching changed release cadence only; it did not weaken source, terms, custody, quality, uncertainty, leakage, owner, rendered-output, privacy, or reproducibility gates.

Author self-audit completed by: `[name or handle]`

> Completing this section does not create independent review or an owner decision.

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
- [ ] AI review was not treated as independent approval, an owner decision, or authority outside the issue.

## Owner decision, when required

- Owner decision required: `yes | no`
- Trigger: `candidate yes/no/uncertain review | execution-goal stop condition | not applicable`
- Exact evidence surface or question: `[artifact / issue / not applicable]`
- Recorded owner outcome: `yes | no | uncertain | direction | not applicable`
- [ ] Author self-audit or AI review was not substituted for a required owner decision.

## Merge authorization

Complete after blocking findings and any required owner decision are resolved.

- Merge authorized: `yes | no | pending`
- Authority: `controlling goal | explicit owner direction | other authorized control`
- Authorization evidence: `[goal / issue / owner direction]`
- Final reviewed head SHA: `[SHA]`
- Merge method: `squash | merge | rebase | pending`
- [ ] All blocking findings are resolved.
- [ ] Dependencies are resolved.
- [ ] The final diff remains within the authorized file scope.
- [ ] Required checks are accurately reported.
- [ ] Unresolved comments or threads are resolved or explicitly accepted.
- [ ] Any required owner evidence decision or stop-condition direction is recorded.
- [ ] Merge authorization does not implicitly authorize settings, data, models, public outputs, tags, Releases, or other separately controlled work.

## Close keyword and handoff

Use exactly the checkpoint-scoped close keyword below and replace the placeholder:

```text
Closes #TASK_ISSUE
```

- [ ] No parent-issue closing keyword is present unless this is an authorized closeout task.
- Next milestone or closeout action: `[milestone / action]`
- Required next context: `[paths / issues / PR]`
- Post-merge status inspection: `README | tracker | prompt logs | other | none`
- Expected status sync: `inspect after merge | expected | not expected`
