# Prompt Build Log Protocol

## Purpose and canonical roles

This file is the canonical BurnLens prompt/build-log protocol and dated-entry index. Prompt/build logs record durable task traceability; they are not transcripts, authorization, PRs, approvals, release notes, or substitutes for repository artifacts.

| Artifact | Role |
|---|---|
| `records/PROMPT_BUILD_LOG.md` | Canonical protocol and dated-entry index |
| `templates/PROMPT_LOG_ENTRY.md` | Canonical detailed entry template |
| `PROMPT_LOG.md` | Non-canonical root navigation |
| `records/prompt-build-log/` | Dated task records |
| GitHub task issue | Authorization |
| `templates/CODEX_TASK_PACKET.md` | Canonical executable task capsule |
| PR and review record | Proposed-change, review, approval, and merge evidence |

Do not create a second protocol, index, detailed template, transcript store, or approval mechanism.

## Governing routes

Load Tier 0 from `docs/workflows/PROMPT_TO_REPO_SOP.md`, then record only the relevant Tier 1 artifacts. Common routes include:

- `AGENTS.md`;
- `CONTRIBUTING.md`;
- `.github/ISSUE_TEMPLATE/task.yml`;
- `.github/PULL_REQUEST_TEMPLATE.md`;
- `templates/CODEX_TASK_PACKET.md`;
- `templates/CODEX_TASK_TEMPLATE.md`;
- `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md`;
- `docs/phase-one/objective-six/PROMPT_BUILT_DEVELOPMENT_PROTOCOL.md`;
- `docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md`;
- applicable data, provenance, claim, version, release, or workstream controls selected through the SOP.

Historical controls may remain baselines, but current merged controls govern when requirements differ.

## Required entry content

Use `templates/PROMPT_LOG_ENTRY.md`. Each material prompt-assisted entry must record:

| Group | Required record |
|---|---|
| Identity | Date, task, issue, parent, branch, base, dependencies, PR, reviewed/merge SHA, artifact class, state |
| Artifacts and prompt | Primary/supporting artifacts and durable issue-backed task summary |
| Context | Tier 0 acknowledgement, exact Tier 1 selection, justified Tier 2 use |
| File scope | Allowed files, actual files, approved expansion, concurrency caveats |
| Research and decisions | Sources, supported facts, adopted decisions, dates, status, or no-research rationale |
| Verification | Named checks, exact methods, actual results, evidence, limitations, and task-specific non-applicability |
| Boundaries and claims | Source precedence, sensitive-material status, safe/unsupported claims, data/model/public-output/settings/tag/Release status |
| Review | Author self-audit, executable checks, optional AI review, mandatory human outcome, separate merge authorization |
| Revisions | Findings, changes, follow-up checks, unresolved items |
| Linkage and sync | PR, task-only close keyword, parent protection, issue closure, parent update, README/tracker/index/log inspection |
| Handoff | Next action, required context, remaining caveats, and `Do not carry forward` |

## Research and verification rules

When current external behavior matters, use official or primary sources and record the source, fact supported, affected decision, adopted wording, date, and status. Do not carry platform claims forward solely from an old log.

For every applicable check record:

```text
check name
exact command or manual method
actual result: passed, failed, partial, blocked, or not applicable
evidence or output
limitation or unresolved finding
```

`Not applicable` requires a task-specific reason. Do not write `tests passed` unless named tests or commands ran. Written templates do not create CI, required checks, branch protection, rulesets, required approvals, CODEOWNERS, or other enforcement.

## Review separation

Keep these stages distinct:

1. author self-audit;
2. automated or executable checks;
3. AI-assisted review, when used;
4. human review and outcome;
5. merge authorization.

Author assertions and AI findings are evidence only. Neither satisfies the human gate or authorizes merge or scope expansion. Solo-maintainer policy evidence may be an explicit PR comment or completed checklist; it is not formal GitHub author self-approval.

## Sensitive-material and boundary rules

Do not record secrets, credentials, tokens, cookies, private URLs, private reasoning, unnecessary transcripts, unnecessary personal information, unapproved proprietary material, or unreviewed operational guidance.

Every entry must accurately state the current boundary; data/model/run/map/public-output status; repository-settings/CI status; tag and Release status; source precedence; safe claims; and unsupported claims. This protocol does not authorize controlled work.

## Location and timing

```text
Canonical protocol/index: records/PROMPT_BUILD_LOG.md
Canonical detailed template: templates/PROMPT_LOG_ENTRY.md
Root router: PROMPT_LOG.md
Dated entries: records/prompt-build-log/YYYY-MM-DD-task-id.md
```

Update entries when the issue/capsule is approved, branch is created, research completes, files change, checks complete, a PR opens, review changes the work, the human outcome is recorded, merge occurs, and post-merge status is inspected.

## Entry index

| Task | Entry path | Status | Notes |
|---|---|---|---|
| P1O4-T01 through P1O4-T08 | Not retroactively required | historical | Traceability exists through issues, PRs, and artifacts. |
| P1O4-T09 | `records/PROMPT_BUILD_LOG.md` | merged via PR #138 | Original protocol and template task. |
| P1O4-T10 | `records/prompt-build-log/2026-07-06-p1o4-t10.md` | merged via PR #139 | Phase Two intake template. |
| P1O4-T11 | `records/prompt-build-log/2026-07-06-p1o4-t11.md` | merged via PR #140 | Closeout and handoff. |
| P1O4-QA | `records/prompt-build-log/2026-07-06-p1o4-qa.md` | merged via PR #142 | Quality pass. |
| P1O4-T12 | `records/prompt-build-log/2026-07-06-p1o4-t12.md` | merged via PR #143 | Objective Four release note. |
| P1O5-T01 | `records/prompt-build-log/2026-07-07-p1o5-t01.md` | merged via PR #147 | Objective Five tracker and artifact-contract baseline. |
| P1O5-T02 | `records/prompt-build-log/2026-07-08-p1o5-t02.md` | merged via PR #149 | Current-status reconciliation and README handoff update. |
| P1O5-T03 | `records/prompt-build-log/2026-07-08-p1o5-t03.md` | merged via PR #152 | Expanded version taxonomy and VERSIONING protocol. |
| P1O5-SYNC-03 | `records/prompt-build-log/2026-07-08-p1o5-sync-03.md` | merged via PR #154 | Status synchronization. |
| P1O5-T04 | `records/prompt-build-log/2026-07-08-p1o5-t04.md` | merged via PR #156 | Release and tag control. |
| P1O5-SYNC-04 | `records/prompt-build-log/2026-07-08-p1o5-sync-04.md` | merged via PR #158 | Status synchronization. |
| P1O5-T05 | `records/prompt-build-log/2026-07-08-p1o5-t05.md` | merged via PR #160 | Provenance traceability and template. |
| P1O5-SYNC-05 | `records/prompt-build-log/2026-07-08-p1o5-sync-05.md` | merged via PR #162 | Status synchronization. |
| P1O5-T06 | `records/prompt-build-log/2026-07-08-p1o5-t06.md` | merged via PR #164 | Run-package contract and manifest template. |
| P1O5-SYNC-06 | `records/prompt-build-log/2026-07-08-p1o5-sync-06.md` | merged via PR #166 | Status synchronization. |
| P1O5-T07 | `records/prompt-build-log/2026-07-08-p1o5-t07.md` | merged via PR #168 | Artifact registry specification. |
| P1O5-SYNC-07 | `records/prompt-build-log/2026-07-08-p1o5-sync-07.md` | merged via PR #170 | Status synchronization. |
| P1O5-T08 | `records/prompt-build-log/2026-07-08-p1o5-t08.md` | merged via PR #172 | Claim-to-evidence protocol and template. |
| P1O5-SYNC-08 | `records/prompt-build-log/2026-07-08-p1o5-sync-08.md` | merged via PR #174 | Status synchronization. |
| P1O5-T09 | `records/prompt-build-log/2026-07-08-p1o5-t09.md` | merged via PR #176 | Source-precedence release gate. |
| P1O5-SYNC-09 | `records/prompt-build-log/2026-07-08-p1o5-sync-09.md` | merged via PR #178 | Status synchronization. |
| P1O5-T10 | `records/prompt-build-log/2026-07-08-p1o5-t10.md` | merged via PR #180 | Reproducibility and release QA. |
| P1O5-SYNC-10 | `records/prompt-build-log/2026-07-08-p1o5-sync-10.md` | merged via PR #182 | Status synchronization. |
| P1O5-T11 | `records/prompt-build-log/2026-07-08-p1o5-t11.md` | merged via PR #184 | Research validation and claims check. |
| P1O5-SYNC-11 | `records/prompt-build-log/2026-07-08-p1o5-sync-11.md` | merged via PR #186 | Status synchronization. |
| P1O5-T12 | `records/prompt-build-log/2026-07-08-p1o5-t12.md` | merged via PR #187 | Objective Five closeout, handoff, and release-note draft. |
| P1O5-SYNC-12 | `records/prompt-build-log/2026-07-08-p1o5-sync-12.md` | drafted in branch | Historical status retained from the prior index. |
| P1O6-T01 | `records/prompt-build-log/2026-07-09-p1o6-t01.md` | merged via PR #197 | Objective Six architecture. |
| P1O6-SYNC-01 | `records/prompt-build-log/2026-07-09-p1o6-sync-01.md` | merged via PR #199 | Status sync. |
| P1O6-T02 | `records/prompt-build-log/2026-07-09-p1o6-t02.md` | merged via PR #201 | Root prompt-log router. |
| P1O6-SYNC-02 | `records/prompt-build-log/2026-07-09-p1o6-sync-02.md` | merged via PR #203 | Status sync. |
| P1O6-T03 | `records/prompt-build-log/2026-07-09-p1o6-t03.md` | merged via PR #206 | Task-template entry point. |
| P1O6-SYNC-03 | `records/prompt-build-log/2026-07-10-p1o6-sync-03.md` | merged via PR #208 | Status sync. |
| P1O6-T04 | `records/prompt-build-log/2026-07-10-p1o6-t04.md` | merged via PR #209 | Agent instructions. |
| P1O6-SYNC-04 | `records/prompt-build-log/2026-07-10-p1o6-sync-04.md` | merged via PR #211 | Status sync. |
| P1O6-T05 | `records/prompt-build-log/2026-07-11-p1o6-t05.md` | merged via PR #213 | Contributor guidance. |
| P1O6-SYNC-05 | `records/prompt-build-log/2026-07-11-p1o6-sync-05.md` | merged via PR #215 | Status sync. |
| P1O6-T06 | `records/prompt-build-log/2026-07-11-p1o6-t06.md` | merged via PR #217 | PR review controls. |
| P1O6-SYNC-06 | `records/prompt-build-log/2026-07-11-p1o6-sync-06.md` | merged via PR #219 | Status sync. |
| P1O6-T07 | `records/prompt-build-log/2026-07-11-p1o6-t07.md` | merged via PR #221 | Issue form and SOP integration. |
| P1O6-SYNC-07 | `records/prompt-build-log/2026-07-11-p1o6-sync-07.md` | merged via PR #225 | Status sync. |
| P1O6-T08 | `records/prompt-build-log/2026-07-11-p1o6-t08.md` | merged via PR #235 | Research validation and cohesion review; issue #226 closed. |
| P1O6-REM-08A | `records/prompt-build-log/2026-07-11-p1o6-rem-08a.md` | merged via PR #228 | Canonical prompt-log controls aligned; issue #227 closed. |
| P1O6-SYNC-08A | `records/prompt-build-log/2026-07-11-p1o6-sync-08a.md` | merged via PR #230 | REM-08A status synchronized; issue #229 closed. |
| P1O6-REM-08B | `records/prompt-build-log/2026-07-11-p1o6-rem-08b.md` | merged via PR #232 | Objective Six routing and path wording reconciled; issue #231 closed. |
| P1O6-SYNC-08B | `records/prompt-build-log/2026-07-11-p1o6-sync-08b.md` | merged via PR #234 | REM-08B status synchronized; issue #233 closed. |
| P1O6-SYNC-08 | `records/prompt-build-log/2026-07-11-p1o6-sync-08.md` | merged via PR #237 | T08 status synchronized; issue #236 closed. |
| P1O6-REM-09A | `records/prompt-build-log/2026-07-12-p1o6-rem-09a.md` | merged via PR #240 | Remaining stale Objective Six status controls reconciled; issue #238 closed. |
| P1O6-SYNC-09A | `records/prompt-build-log/2026-07-12-p1o6-sync-09a.md` | merged via PR #242 | REM-09A merge evidence synchronized; issue #241 closed. |
| P1O6-T09 | `records/prompt-build-log/2026-07-12-p1o6-t09.md` | merged via PR #243 | Objective Six closeout and handoff; issue #239 closed. |
| P1O6-SYNC-09 | `records/prompt-build-log/2026-07-12-p1o6-sync-09.md` | final synchronization record | Issue #244; PR and merge evidence are retained in the issue, PR, and dated log. |
| P1O7-T01 | `records/prompt-build-log/2026-07-12-p1o7-t01.md` | merged via PR #248 | Objective Seven tracker and artifact contracts; issue #247 closed and status synchronized through #249. |
| P1O7-SYNC-01 | `records/prompt-build-log/2026-07-12-p1o7-sync-01.md` | final synchronization record | Issue #249; PR and merge evidence are retained in the issue, PR, and dated log. |
| P1O7-T02 | `records/prompt-build-log/2026-07-12-p1o7-t02.md` | merged via PR #252 | Phase One gate evidence matrix; issue #251 closed and status synchronized through #253. |
| P1O7-SYNC-02 | `records/prompt-build-log/2026-07-12-p1o7-sync-02.md` | final synchronization record | Issue #253 and PR #254 contain the source sync evidence; issue #255 authorizes final record correction and its GitHub history retains completion evidence. |
| P1O7-REM-03A | `records/prompt-build-log/2026-07-12-p1o7-rem-03a.md` | merged via PR #260 | Issue #259 closed; status-routing remediation merged at `d1cb6cffa01402627c9e4b208139dc1a87c97552`. |
| P1O7-SYNC-03A | `records/prompt-build-log/2026-07-12-p1o7-sync-03a.md` | final synchronization record | Issue #261; PR and merge evidence are retained in the issue, PR, and dated log. |
| P1O7-T03 | `records/prompt-build-log/2026-07-12-p1o7-t03.md` | merged via PR #263 | Corrected repository-only audit; issue #257 closed; G01, G02, and G11 reviewed `meets criterion` / `pass`. |
| P1O7-SYNC-03 | `records/prompt-build-log/2026-07-12-p1o7-sync-03.md` | final synchronization record | Issue #264; source T03 review and merge evidence are retained in issue #257, PR #263, and the dated logs. |
| P1O7-T04 | `records/prompt-build-log/2026-07-12-p1o7-t04.md` | merged via PR #270 | Issue #269 closed; G03 reviewed `meets criterion`, G04 reviewed `meets with limitation`, and F04-A remains `evidence incomplete`. |
| P1O7-SYNC-04 | `records/prompt-build-log/2026-07-12-p1o7-sync-04.md` | final synchronization record | Issue #271; PR #272 and final merge evidence are retained in the issue, PR, and dated log. |
| P1O7-T05 | `records/prompt-build-log/2026-07-12-p1o7-t05.md` | merged via PR #274 | Issue #273 closed; G05/G06-B/G08/G09 reviewed `meets with limitation`, G06-A/G07 reviewed `meets criterion`, and F06-C/G10/F10-R remain `evidence incomplete`. |
| P1O7-SYNC-05 | `records/prompt-build-log/2026-07-12-p1o7-sync-05.md` | final synchronization record | Issue #275; PR and merge evidence are retained in the issue, PR, and dated log. |
| P1O7-T06 | `records/prompt-build-log/2026-07-12-p1o7-t06.md` | merged via PR #278 | Issue #277 closed; conditional candidate approved; legacy dispositions approved; no tag or GitHub Release created. |
| P1O7-REM-06A | `records/prompt-build-log/2026-07-12-p1o7-rem-06a.md` | merged via PR #280 | Issue #279 closed; T06-F01 accepted with documented limitation; inventory remains unresolved and mandatory before T10 and parent closure. |
| P1O7-SYNC-06A | `records/prompt-build-log/2026-07-12-p1o7-rem-06a.md` | final synchronization record | Issue #281; final PR and merge evidence remain in issue and PR history. |
| P1O7-T07 | `records/prompt-build-log/2026-07-13-p1o7-t07.md` | merged via PR #284 | Issue #283 closed; exit checklist reviewed and merged at `69eea57597a27c58d3e9b8ffe2a1b07a8c4826ae`; G10 and F04-A blockers preserved. |
| P1O7-SYNC-07 | `records/prompt-build-log/2026-07-13-p1o7-sync-07.md` | final synchronization record | Issue #285 and finalization #287; README, tracker, checklist lifecycle, and prompt-log truth synchronized after T07 merge. |
| P1O7-T08 | `records/prompt-build-log/2026-07-13-p1o7-t08.md` | merged via PR #294 | Issue #289 closed; Drew recorded `APPROVE — PHASE TWO PLANNING ONLY` on 2026-07-13; merge `69c0b7322f5c2a556f285ad639a8df467494979f`; G10 and F04-A blockers preserved. |
| P1O7-SYNC-08 | `records/prompt-build-log/2026-07-13-p1o7-sync-08.md` | final synchronization record | Issue #296; T08 decision, review, merge, blocker, routing, and handoff truth synchronized. Final PR and merge evidence remain in GitHub history. |

## Acceptance and remediation triggers

An entry is reviewable when a reviewer can identify authorization, context, file scope, research, decisions, checks, boundaries, review separation, merge state, sync state, and handoff.

Revise the protocol, template, or an entry if it:

- stores sensitive/private material;
- omits materially applicable issue, branch/base, file-scope, research, verification, review, or handoff evidence;
- describes checks without methods and actual results;
- allows AI or author self-audit to satisfy human approval;
- represents written policy as configured enforcement;
- replaces issues, PRs, artifacts, reviews, or releases;
- introduces unsupported readiness, authority, data/model, or release claims.

Safe claim:

> BurnLens has one canonical prompt/build-log protocol and index, one canonical detailed entry template, one non-canonical root router, and dated task records.

Objective Six is complete as a documented, reviewable repository-control baseline, and parent #195 is closed. Objective Seven remains active and incomplete under parent #246. P1O7-T08 / #289 is reviewed and merged through PR #294 at `69c0b7322f5c2a556f285ad639a8df467494979f`. Drew’s decision authorizes bounded, separately issue-backed Phase Two planning and control work only. G10 remains `evidence incomplete` and blocks full Phase One completion; F04-A remains `evidence incomplete` and blocks every data-touch action. F06-C and F10-R remain separate supporting incomplete facts. Complete Project/tag/Release inventories remain `inaccessible/unresolved` where stated. No Objective Seven tag or GitHub Release was authorized or created. P1O7-T09 is next; issues #292 and #293 remain blocked preparation tasks under their own dependency gates.
