# BurnLens Pull Request Review Checklist

## Purpose

Use this checklist to record a reusable, human-reviewable decision for a BurnLens pull request.

It supplements, but does not replace:

- `docs/workflows/PROMPT_TO_REPO_SOP.md`;
- `CONTRIBUTING.md`;
- `AGENTS.md`;
- the authorized task issue and task capsule;
- `.github/PULL_REQUEST_TEMPLATE.md`;
- `records/PROMPT_BUILD_LOG.md`.

This checklist documents repository policy. It does not prove that GitHub branch protection, rulesets, required approvals, required checks, CI, CODEOWNERS, conversation-resolution gates, or other platform enforcement is configured.

## Review separation rule

Keep these stages distinct:

1. author self-audit;
2. automated or executable checks;
3. AI-assisted review, when used;
4. human reviewer inspection;
5. merge authorization.

> An author self-audit is not independent human review and is not formal GitHub approval.

> AI-assisted review is supplemental. It does not approve the pull request, authorize scope expansion, or satisfy the human-review gate.

## Review identity

| Field | Value |
|---|---|
| Review date | `YYYY-MM-DD` |
| Task ID | `P#O#-T##` |
| Task issue | `#` |
| Parent issue | `#` |
| Pull request | `#` |
| Author | `[name or handle]` |
| Human reviewer or solo-maintainer evidence owner | `[name or handle]` |
| Branch | `p#o#t##b` |
| Base | `main` or authorized alternative |
| Dependency status | `satisfied | blocked | not applicable` |
| Review target commit or head SHA | `[SHA]` |
| Task or artifact class | `documentation | template | workflow | records | code | configuration | data | model | public output | other` |
| Final human outcome | `Approve | Request changes | Defer or reject | pending` |
| Merge authorized by | `[name / pending]` |
| Limitations or unresolved findings | `[notes / none]` |

## Stage 1 — Author self-audit

The author completes this section before requesting human review.

### Task linkage and dependency

- [ ] The task issue and parent issue are identified.
- [ ] The task capsule matches the issue and does not broaden it.
- [ ] The branch and base match the task contract.
- [ ] Dependencies are satisfied, or the blocking dependency is stated accurately.
- [ ] The pull-request title follows the generic task pattern `P#O#-T## Short task title`.
- [ ] The close keyword is limited to `Closes #TASK_ISSUE`.
- [ ] The parent issue is not closed unless this is an explicitly authorized closeout task.

### Scope and changed files

- [ ] The allowed-file list is recorded.
- [ ] The actual changed-file list matches the allowed-file list.
- [ ] Every changed file is necessary for the task.
- [ ] No scratch, generated, credential, temporary, or connector-test file is present.
- [ ] Any required scope expansion was approved before the additional file changed.

### Prompt/build logging

- [ ] A dated prompt/build log exists when prompt-assisted edits occurred.
- [ ] The log records task identity, branch, files, research, decisions, checks, results, boundaries, claims, and handoff.
- [ ] The log excludes secrets, credentials, private reasoning, raw private transcripts, unnecessary personal information, and unreviewed operational guidance.

### Research and acceptance

- [ ] Current research was completed after branch creation when the task depends on current external facts.
- [ ] Official or primary sources were preferred where available.
- [ ] Each research-backed statement records the source, supported fact, adopted decision, and check date.
- [ ] When fresh research was not required, the task-specific reason is recorded.
- [ ] Every acceptance criterion maps to a file, section, command result, or inspection finding.

### Verification reporting

- [ ] Every applicable check has a name.
- [ ] Every applicable check records the exact command or manual inspection method.
- [ ] Every applicable check records the actual result and any limitation.
- [ ] No generic `tests passed` claim appears without named evidence.
- [ ] Every expected check not run has a task-specific reason.

### Security, boundaries, and claims

- [ ] No secrets, credentials, tokens, cookies, private URLs, or sensitive source material were introduced.
- [ ] No private chain-of-thought or hidden reasoning was recorded.
- [ ] No unnecessary personal information was introduced.
- [ ] BurnLens use boundaries and source precedence are preserved.
- [ ] Official sources govern where applicable.
- [ ] Public-facing claims, when separately authorized, have appropriate evidence and limitations.
- [ ] No unsupported official, operational, field-validation, agency-endorsement, emergency-readiness, data-readiness, model-readiness, or release claim was introduced.
- [ ] Tag and GitHub Release status are explicit when relevant.

### Diff and handoff

- [ ] The branch was compared with the current base.
- [ ] The content of every changed file was reviewed, not only the filenames.
- [ ] The branch is not unintentionally behind the base.
- [ ] The next task or closeout action is stated.
- [ ] Post-merge status inspection is planned for README, tracker, and prompt-log records when their truth may change.

### Author evidence

| Field | Value |
|---|---|
| Author self-audit completed by | `[name or handle]` |
| Date | `YYYY-MM-DD` |
| Allowed files | `[paths]` |
| Actual changed files | `[paths]` |
| Prompt/build log | `[path / not applicable with reason]` |
| Diff evidence | `[comparison / PR files view]` |
| Remaining author-known issues | `[issues / none]` |

## Stage 2 — Automated or executable checks

Record checks that actually apply. Do not invent CI jobs, status checks, or commands.

| Check | Command or inspection method | Result | Output or evidence | Limitation or unresolved failure | Required for this task? |
|---|---|---|---|---|---|
| `[name]` | `[command or method]` | `passed | failed | partial | blocked | not applicable` | `[summary or path]` | `[notes / none]` | `yes | no` |

### Documentation and template tasks

Documentation or template work may mark code, application, model, data, build, lint, type, and executable tests as not applicable only with a task-specific reason.

Appropriate checks may include:

- Markdown structure and readability;
- repository path and relative-link inspection;
- template location and syntax review;
- rendered-document inspection when useful;
- requirement-coverage review;
- checklist and template consistency;
- generic-pattern and stale-example review;
- scope, boundary, source-precedence, claims, security, sensitive-material, and branch-diff review.

### Code or configuration tasks

When code or configuration changes, record the actual applicable commands and results, such as:

- unit, integration, regression, or smoke tests;
- linting and formatting;
- type checking;
- build checks;
- YAML, JSON, schema, or manifest validation;
- security or dependency checks;
- browser, UI, or application smoke inspection.

A repository template does not create or require these checks by itself.

### Checks not run

| Expected check | Why it was not run or does not apply | Reviewer assessment |
|---|---|---|
| `[check]` | `[task-specific reason]` | `acceptable | revise | pending` |

## Stage 3 — AI-assisted review, when used

This section is optional. Label all findings as AI-assisted.

| Field | Value |
|---|---|
| AI tool or mode | `[tool / not used]` |
| Review target | `branch diff | working tree | commit | pull request | named files | other` |
| Base or comparison target | `[branch / SHA / not applicable]` |
| Review focus | `[correctness / security / requirements / boundaries / other]` |
| Findings | `[summary / none]` |
| Severity or priority | `[critical / high / medium / low / informational / none]` |
| Fixes applied | `[summary / none]` |
| Follow-up review | `[result / not run with reason]` |
| Unresolved AI findings | `[findings / none]` |

- [ ] AI findings were reviewed by a human before merge authorization.
- [ ] The authoring agent did not treat its own self-review as independent approval.
- [ ] AI review did not authorize scope expansion, merge, settings changes, tags, Releases, or other separately controlled work.

## Stage 4 — Human reviewer inspection

A human completes this section after the author self-audit and verification evidence are available.

### Required inspection

- [ ] I inspected the task issue and task capsule.
- [ ] I inspected the branch, base, and dependency status.
- [ ] I inspected the complete changed-file list.
- [ ] I inspected the content diff, not only the filenames.
- [ ] I confirmed the diff stays within the allowed-file scope.
- [ ] I inspected the prompt/build-log evidence where required.
- [ ] I inspected current research sources and adopted decisions where applicable.
- [ ] I inspected named tests/checks, exact methods, and actual results.
- [ ] I inspected checks not run and their reasons.
- [ ] I inspected security and sensitive-material status.
- [ ] I inspected unresolved comments, review threads, and AI findings.
- [ ] I compared the result with every acceptance criterion.
- [ ] I inspected BurnLens use boundaries and source precedence.
- [ ] I inspected public claims and evidence limits where applicable.
- [ ] I confirmed the task-only close keyword and parent-issue protection.
- [ ] I inspected the handoff and post-merge status plan.
- [ ] I confirmed that author self-audit and AI review were not treated as human approval.

### Human findings

| Finding | Severity | Required action | Resolution evidence | Status |
|---|---|---|---|---|
| `[finding]` | `blocking | non-blocking | informational` | `[action]` | `[path / comment / commit]` | `open | resolved | accepted` |

### Human outcome

Select exactly one:

- [ ] **Approve** — ready for separately authorized merge.
- [ ] **Request changes** — blocking findings must be addressed and re-reviewed.
- [ ] **Defer or reject** — do not merge in the current form.

| Field | Value |
|---|---|
| Human reviewer or evidence owner | `[name or handle]` |
| Review date | `YYYY-MM-DD` |
| Outcome | `Approve | Request changes | Defer or reject` |
| Outcome evidence | `[GitHub review / PR comment / completed checklist]` |
| Blocking findings remaining | `[findings / none]` |
| Notes | `[notes]` |

### Solo-maintainer evidence

Pull-request authors cannot formally approve their own pull requests on GitHub.

For the current solo-maintainer workflow, Drew may record the human outcome through either:

- an explicit pull-request comment naming the outcome; or
- a completed instance of this checklist stating that the diff and verification evidence were inspected.

This is BurnLens policy evidence. It is not a formal GitHub author self-approval and does not claim platform enforcement.

When another eligible human reviewer is available, request their formal GitHub review where possible. This checklist does not imply that another reviewer currently exists.

## Stage 5 — Merge authorization

Complete this stage only after the human outcome is **Approve**.

- [ ] Human outcome is `Approve`.
- [ ] All blocking findings are resolved.
- [ ] Dependencies are resolved or explicitly accepted by the human owner.
- [ ] The final branch diff remains within the allowed-file contract.
- [ ] Required checks are accurately reported.
- [ ] Unresolved comments or threads are resolved or explicitly accepted by the human reviewer.
- [ ] The PR closes only the task issue.
- [ ] The parent issue remains open unless this is an authorized closeout task.
- [ ] The selected merge method is permitted and appropriate.
- [ ] Post-merge status inspection is planned.
- [ ] This authorization does not implicitly authorize data, models, public outputs, settings, tags, Releases, or other separately controlled work.

| Field | Value |
|---|---|
| Merge authorized | `yes | no` |
| Authorized by | `[name or handle]` |
| Authorization evidence | `[PR comment / review / checklist]` |
| Merge method | `squash | merge | rebase | pending` |
| Final reviewed head SHA | `[SHA]` |
| Close keyword | `Closes #TASK_ISSUE` |
| Parent close avoided | `yes | no` |
| Post-merge sync | `inspect after merge | expected | not expected` |
| Authorization notes | `[notes]` |

## Stop conditions

Do not authorize merge when:

- the issue or capsule is missing or conflicting;
- the base, dependency, or changed-file scope is unclear;
- an unauthorized file is present;
- research-backed claims lack current evidence;
- tests or checks are described vaguely or dishonestly;
- sensitive material or unsupported claims remain;
- source precedence or use boundaries are weakened;
- blocking comments or findings remain unresolved;
- AI review or author self-audit is being substituted for human review;
- the close keyword could close the parent issue unintentionally;
- the task implies settings, data, models, public outputs, tags, Releases, or other blocked work without separate authorization.

## Research basis

This checklist's GitHub behavior statements were checked against official GitHub documentation on 2026-07-11:

- About pull request reviews: `https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews`
- Reviewing proposed changes in a pull request: `https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/reviewing-proposed-changes-in-a-pull-request`
- About protected branches: `https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches`
- Available rules for rulesets: `https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets`
- Creating a pull request template: `https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository`

OpenAI review and verification guidance was checked on 2026-07-11:

- Code review: `https://developers.openai.com/codex/code-review`
- Prompting: `https://developers.openai.com/codex/prompting`

The adopted policy is stricter than an unprotected repository's default behavior: BurnLens requires recorded human review before merge, but this document does not claim that GitHub settings enforce that requirement.

## Handoff record

| Field | Value |
|---|---|
| Current task or review | `[task ID]` |
| Next task or closeout action | `[task ID / action]` |
| Required context | `[paths / issues / PR]` |
| Do not carry forward | `[obsolete drafts or troubleshooting details]` |
