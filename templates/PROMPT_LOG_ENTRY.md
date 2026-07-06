# Prompt Log Entry Template

Use this template with `records/PROMPT_BUILD_LOG.md` for prompt-assisted BurnLens Deschutes repository work.

Do not record secrets, credentials, private chain-of-thought, private session material, or unreviewed operational wildfire guidance.

## Entry metadata

| Field | Value |
|---|---|
| Log entry date | YYYY-MM-DD |
| Task ID | P1O4-TXX |
| Task title |  |
| Task issue | # |
| Parent issue | #119 |
| Branch |  |
| Pull request | # |
| Merge method | squash / merge / rebase / pending |
| Primary artifact path |  |
| Artifact type | documentation / template / records / workflow / implementation |
| Prompt assistant or Codex mode | ChatGPT / Codex app / Codex CLI / Codex IDE / other |

## Task summary

Briefly state what the prompt-assisted task was asked to produce.

```text
[One to three sentences.]
```

## Prompt or task packet summary

Record the durable task instruction or summary. Do not paste private reasoning or sensitive transcript material.

```text
[Prompt summary or task packet summary.]
```

## Governing standards used

Check all that apply:

- [ ] `AGENTS.md`
- [ ] `.github/ISSUE_TEMPLATE/task.yml`
- [ ] `.github/PULL_REQUEST_TEMPLATE.md`
- [ ] `templates/CODEX_TASK_PACKET.md`
- [ ] `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md`
- [ ] `docs/phase-one/objective-four/ISSUE_ARCHITECTURE.md`
- [ ] `docs/phase-one/objective-four/ISSUE_TAXONOMY.md`
- [ ] `docs/phase-one/objective-four/PROJECT_BOARD_SPEC.md`
- [ ] Other: 

## Allowed file scope

Files the assistant/Codex was allowed to change:

```text
[path]
[path]
```

## Actual files changed

Files actually changed:

```text
[path]
[path]
```

## Research/source checks

| Claim ID | Source name | Source URL | What it supports | Decision made | Date checked |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## Material decisions

| Decision | Rationale | Source or artifact basis |
|---|---|---|
|  |  |  |

## Verification performed

| Check | Result | Notes |
|---|---|---|
| Diff check | pending / passed / failed / not applicable |  |
| File review | pending / passed / failed / not applicable |  |
| Markdown/YAML/schema review | pending / passed / failed / not applicable |  |
| Tests | not run / passed / failed / not applicable | Do not claim tests passed unless actually run. |
| Boundary check | pending / passed / failed |  |
| Claims check | pending / passed / failed |  |

## Tests or checks not run

State any checks not run and why.

```text
[Example: No code tests run because documentation-only files changed.]
```

## Boundary review

- [ ] Work stayed within the task issue.
- [ ] Work stayed within the current phase boundary.
- [ ] No imagery, AOI data, labels, masks, model outputs, metrics, maps, or public-demo artifacts were created.
- [ ] No official, operational, field-validation, emergency-readiness, or endorsement claims were introduced.
- [ ] Official source precedence was preserved.

## Claims-register check

Safe claim after this task:

```text
[Safe claim.]
```

Unsupported claims after this task:

```text
[Unsupported claims.]
```

## Sensitive material exclusion check

- [ ] No secrets, API keys, credentials, tokens, cookies, or private URLs were recorded.
- [ ] No private chain-of-thought or hidden reasoning was recorded.
- [ ] No unnecessary personal information was recorded.
- [ ] No unreviewed emergency guidance was recorded.

## PR and issue linkage

| Field | Value |
|---|---|
| PR title |  |
| PR close keyword | Closes # |
| Parent issue close avoided? | yes / no |
| Parent issue update needed? | yes / no |
| Tracker or handoff update needed? | yes / no |

## Handoff note

State what the next task should use from this work.

```text
[Handoff note.]
```

## Entry completeness checklist

- [ ] Task identity recorded.
- [ ] Prompt/task packet summarized.
- [ ] Governing standards listed.
- [ ] Allowed files and actual changed files recorded.
- [ ] Research/source checks recorded or explicitly not required.
- [ ] Verification recorded.
- [ ] Boundary and claims checks completed.
- [ ] Sensitive material excluded.
- [ ] PR and issue linkage recorded.
- [ ] Handoff note included.
