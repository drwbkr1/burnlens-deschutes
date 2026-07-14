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

Load Tier 0 from `docs/workflows/PROMPT_TO_REPO_SOP.md`, then record only the relevant Tier 1 artifacts. Common routes include `AGENTS.md`, `CONTRIBUTING.md`, issue/PR templates, the canonical task packet, the branch/PR workflow, the Objective Six protocol and review checklist, and applicable data/provenance/claim/version/release controls.

Historical controls may remain baselines, but current merged controls govern when requirements differ.

## Required entry content

Use `templates/PROMPT_LOG_ENTRY.md`. Each material prompt-assisted entry must record identity, authorization, artifacts, context, file scope, research, decisions, named verification and actual results, boundaries and claims, review separation, revisions, PR/issue/sync linkage, handoff, and `Do not carry forward`.

## Research and verification rules

When current external behavior matters, use official or primary sources and record the source, fact supported, affected decision, adopted wording, date, and status. Do not carry platform claims forward solely from an old log.

`Not applicable` requires a task-specific reason. Do not write `tests passed` unless named tests or commands ran. Written templates do not create CI, required checks, branch protection, rulesets, required approvals, CODEOWNERS, or other enforcement.

## Review separation

Keep author self-audit, executable checks, AI-assisted review, human review, and merge authorization distinct. Author assertions and AI findings are evidence only. Neither satisfies the human gate or authorizes merge or scope expansion.

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

Update entries when authorization, branch, research, files, checks, PR, review, merge, or post-merge truth changes.

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
| P1O7-SYNC-02 | `records/prompt-build-log/2026-07-12-p1o7-sync-02.md` | final synchronization record | Issue #253 and PR #254 contain source sync evidence; issue #255 retains final record correction evidence. |
| P1O7-REM-03A | `records/prompt-build-log/2026-07-12-p1o7-rem-03a.md` | merged via PR #260 | Issue #259 closed; status-routing remediation merged at `d1cb6cffa01402627c9e4b208139dc1a87c97552`. |
| P1O7-SYNC-03A | `records/prompt-build-log/2026-07-12-p1o7-sync-03a.md` | final synchronization record | Issue #261; PR and merge evidence are retained in the issue, PR, and dated log. |
| P1O7-T03 | `records/prompt-build-log/2026-07-12-p1o7-t03.md` | merged via PR #263 | Corrected repository-only audit; issue #257 closed; G01, G02, and G11 reviewed `meets criterion` / `pass`. |
| P1O7-SYNC-03 | `records/prompt-build-log/2026-07-12-p1o7-sync-03.md` | final synchronization record | Issue #264; source T03 review and merge evidence are retained in issue #257, PR #263, and the dated logs. |
| P1O7-T04 | `records/prompt-build-log/2026-07-12-p1o7-t04.md` | merged via PR #270 | Issue #269 closed; G03 reviewed `meets criterion`, G04 reviewed `meets with limitation`, and F04-A remains `evidence incomplete`. |
| P1O7-SYNC-04 | `records/prompt-build-log/2026-07-12-p1o7-sync-04.md` | final synchronization record | Issue #271; PR #272 and final merge evidence are retained in the issue, PR, and dated log. |
| P1O7-T05 | `records/prompt-build-log/2026-07-12-p1o7-t05.md` | merged via PR #274 | Issue #273 closed; G05/G06-B/G08/G09 reviewed `meets with limitation`, G06-A/G07 reviewed `meets criterion`, and F06-C/G10/F10-R remain `evidence incomplete`. |
| P1O7-SYNC-05 | `records/prompt-build-log/2026-07-12-p1o7-sync-05.md` | final synchronization record | Issue #275; PR and merge evidence are retained in the issue, PR, and dated log. |
| P1O7-T06 | `records/prompt-build-log/2026-07-12-p1o7-t06.md` | merged via PR #278 | Issue #277 closed; conditional candidate approved; no tag or GitHub Release created. |
| P1O7-REM-06A | `records/prompt-build-log/2026-07-12-p1o7-rem-06a.md` | merged via PR #280 | Issue #279 closed; inventory limitation accepted for sequencing; complete enumeration remains mandatory. |
| P1O7-SYNC-06A | `records/prompt-build-log/2026-07-12-p1o7-rem-06a.md` | final synchronization record | Issue #281; final evidence remains in issue and PR history. |
| P1O7-T07 | `records/prompt-build-log/2026-07-13-p1o7-t07.md` | merged via PR #284 | Issue #283 closed; exit checklist reviewed and merged; G10 and F04-A preserved. |
| P1O7-SYNC-07 | `records/prompt-build-log/2026-07-13-p1o7-sync-07.md` | final synchronization record | Issue #285 and finalization #287 synchronized T07 truth. |
| P1O7-T08 | `records/prompt-build-log/2026-07-13-p1o7-t08.md` | merged via PR #294 | Issue #289 closed; Drew recorded planning-only approval; blockers preserved. |
| P1O7-SYNC-08 | `records/prompt-build-log/2026-07-13-p1o7-sync-08.md` | final synchronization record | Issue #296 synchronized T08 truth. |
| P1O7-T09 | `records/prompt-build-log/2026-07-13-p1o7-t09.md` | merged via PR #299 | Issue #298 closed; Drew approved exact head; separate squash authorization; merge `d7ad8f063239a61e9212e6eac562deffa50a7a88`. |
| P1O7-SYNC-09 | `records/prompt-build-log/2026-07-13-p1o7-sync-09.md` | merged via PR #301 | Issue #300 closed; lifecycle truth synchronized at `10caebb3d61ff622dc6dfe8809a63886089eba4e`. |
| P1O7-SYNC-09F | `records/prompt-build-log/2026-07-13-p1o7-sync-09f.md` | merged via PR #303 | Issue #302 closed; exact eligible target finalized as `10caebb3d61ff622dc6dfe8809a63886089eba4e`; merge `49701a42b4dda849cea5976fb580dbd155931195`. |
| P1O7-SYNC-09F-SYNC | `records/prompt-build-log/2026-07-13-p1o7-sync-09f-sync.md` | final synchronization record | Issue #304; final task-scoped PR and merge evidence remain in GitHub history. No further T09 lifecycle sync expected. |
| BL-GOV-001 | `docs/devlog/2026-07-13-goal-activation.md` | merged via PR #291; tagged | Controlling execution goal and roadmap at `v0.0.8-execution-goal-baseline`. |
| BL-GOV-001-SYNC | `records/prompt-build-log/2026-07-13-bl-gov-001-sync.md` | merged via PR #309 | Governance lifecycle truth synchronized; issue #308 closed. |
| P2O1-T01 | `records/prompt-build-log/2026-07-13-p2o1-t01.md` | merged via PR #310; tagged | Issue #293 closed; merge `6abe87bba486e3fe49b6c06178b454335663cb73`; `v0.1.0-source-metadata-baseline`. |
| P2O1-T02 | `records/prompt-build-log/2026-07-13-p2o1-t02.md` | merged via PR #314; tagged | Issue #312 closed; merge `cf4aba2f40aa426f28f09b1b1b1bad895394198b`; `v0.1.1-asset-readiness-baseline`; credential-boundary STOP preserved. |
| P2O1-T03 | `records/prompt-build-log/2026-07-13-p2o1-t03.md` | merged via PR #318; tagged | Issue #317 closed; merge `d4ce26c87341e4d3798a0d84e257a964ebd2cde0`; `v0.1.2-access-integrity-baseline`; two-credential STOP preserved. |
| P2O1-T03-SYNC | `records/prompt-build-log/2026-07-13-p2o1-t03.md` | merged via PR #320 | Issue #319 closed; exact access-integrity shipment lifecycle synchronized at `23affc85ac2c2c6cfd427cb954739e6c7b44fa66`. |
| P2O2-T01 | `records/prompt-build-log/2026-07-13-p2o2-t01.md` | merged via PR #322; tagged | Issue #321 closed; merge `fffd3dda123d7c43fe678dca9adfd8feb73de158`; `v0.2.0-aoi-baseline`; final modeling AOI and deterministic evidence shipped. |
| P2O2-T01-SYNC | `records/prompt-build-log/2026-07-13-p2o2-t01-sync.md` | issue #323 / PR #324 lifecycle synchronization | Exact analytical PR/merge/tag/post-merge verification synchronized without changing outputs. |
| P2O2-T02 | `records/prompt-build-log/2026-07-13-p2o2-t02.md` | merged via PR #326; tagged | Issue #325 closed; merge `ee1a1d678ad888b595dc3c7b215f787ea5156582`; `v0.3.0-intake-transaction-baseline`; historical credential-blocked report plus later owner authorization; zero provider or retained fixture bytes. |
| P2O2-T02-SYNC | `records/prompt-build-log/2026-07-14-p2o2-t02-sync.md` | issue #327 / PR #328 lifecycle synchronization | Exact analytical PR/merge/tag/post-merge verification synchronized without changing outputs or exercising credentials. |
| P2O2-T03 | `records/prompt-build-log/2026-07-14-p2o2-t03.md` | merged via PR #330; tagged | Issue #329 closed; merge `7678cf41b64e128106c199b913fe74590a52cf80`; `v0.4.0-authenticated-source-baseline`; authenticated source/reference evidence accepted and labels/dataset deferred. |
| P2O2-T03-SYNC | `records/prompt-build-log/2026-07-14-p2o2-t03-sync.md` | issue #331 / PR #332; shipped | Exact analytical PR/merge/tag/post-merge verification synchronized at `5f7461ac4cc8caa48f029776e5797023f27eaec5`; no credential, raw-byte, or scientific-output change. |
| P2O2-T04 | `records/prompt-build-log/2026-07-14-p2o2-t04.md` | merged via PR #334; tagged | Issue #333 closed; merge `1c85496d9d488c0d2d5a58207d8b4786a683ba52`; `v0.5.0-observation-geometry-baseline`; complementary reference accepted and labels/dataset deferred. |
| P2O2-T04-SYNC | `records/prompt-build-log/2026-07-14-p2o2-t04-sync.md` | issue #335; active lifecycle synchronization | Exact analytical PR/merge/tag/post-merge verification synchronization; no code, raw-byte, or scientific-output change. |

## Acceptance and remediation triggers

Revise the protocol, template, or an entry if it stores sensitive material; omits materially applicable authorization, scope, verification, review, or handoff evidence; invents checks; substitutes author/AI review for human approval; represents policy as enforcement; replaces repository evidence; or introduces unsupported readiness, authority, data/model, or release claims.

Safe claim:

> BurnLens has one canonical prompt/build-log protocol and index, one canonical detailed entry template, one non-canonical root router, and dated task records.

The controlling execution goal and six-phase roadmap are merged and tagged at `v0.0.8-execution-goal-baseline`. Phase Two is active. P2O2-T04 / issue #333 / PR #334 is shipped at `v0.5.0-observation-geometry-baseline` / `1c85496d9d488c0d2d5a58207d8b4786a683ba52`: the complete bounded inventory yields a materially improved complementary reference but still no defensible labels or dataset. Authorized credentials were exercised without retaining secrets; exact raw packages remain local/ignored. P2O2-T04-SYNC / issue #335 is the active provenance-only checkpoint. The next target-path decision is owner-reserved. Historical Objective Seven restrictions that conflict with the controlling goal are retained only as audit evidence and do not govern current execution.
