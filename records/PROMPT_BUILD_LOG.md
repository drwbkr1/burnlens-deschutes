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
| P2O2-T04-SYNC | `records/prompt-build-log/2026-07-14-p2o2-t04-sync.md` | issue #335 / PR #336; merged | Exact analytical PR/merge/tag/post-merge verification synchronized at `9f684d742839f22e600b8d594b23484f21b0e551`; no code, raw-byte, or scientific-output change. |
| P2O2-T05 | `records/prompt-build-log/2026-07-14-p2o2-t05.md` | issue #337 / PR #338; merged at `68971e9709b886adf8575a58d32694aad42f038e` | Owner-approved `target-burn-scar-v0.2.0`; current MTBS no-Darlene/AOI evidence; no label, dataset, baseline, or model. The initial post-merge reconstruction withheld the tag; the remediation row below completed the release. |
| P2O2-T05-REM | `records/prompt-build-log/2026-07-14-p2o2-t05-rem.md` | issue #339 / PR #340; merged and tagged | Remediation merge `bcb71ebd01d3184f8de24318428309e61d33e54f`; preserve `r001`; publish LF-stable `r002`; verified annotated `v0.6.0-burn-scar-target-baseline`. |
| P2O2-T05-SYNC | `records/prompt-build-log/2026-07-15-p2o2-t05-sync.md` | issue #341 / PR #342; active lifecycle synchronization | Record exact analytical/remediation merge, corrected run, post-merge verification, and annotated tag identities; no code or scientific-output change. |
| P2O2-T06 | `records/prompt-build-log/2026-07-15-p2o2-t06.md` | issue #343 / PR #344; merged and tagged | Exact same-orbit Sentinel-2 pair registered and visually validated; five-state protocol shipped at `v0.7.0-optical-pair-protocol-baseline` without creating label pixels, a dataset, baseline, or model. |
| P2O2-T06-SYNC | `records/prompt-build-log/2026-07-15-p2o2-t06-sync.md` | issue #345 / PR #346; active lifecycle synchronization | Exact analytical PR/merge/tag and clean-main verification synchronized without changing code or analytical outputs. |
| P2O3-T01 | `records/prompt-build-log/2026-07-15-p2o3-t01.md` | issue #347 / PR #348; analytical merge `c01cdb12033e7a9440ad0502b92a8887fd79ed1d` | Exact pair-local content registration accepted across twelve fixed AOI windows; post-merge LF reconstruction defect preserved and routed to #349. |
| P2O3-T01-REM | `records/prompt-build-log/2026-07-15-p2o3-t01-rem.md` | issue #349 / PR #350; merged and tagged | Explicit LF checkout contract at `1297471be45200c40f9f40746e85b437ce6e0c0d`; fresh merged-main clone reconstructs JSON/HTML/PNG byte for byte; verified `v0.8.0-content-registration-baseline`; no analytical change. |
| P2O3-T01-SYNC | `records/prompt-build-log/2026-07-15-p2o3-t01-sync.md` | issue #351 / PR #352; lifecycle synchronization | Exact analytical/remediation merge, failed and corrected release gates, wheel, and annotated tag identities synchronized without changing code or analytical outputs. |
| P2O4-T01 | `records/prompt-build-log/2026-07-15-p2o4-t01.md` | issue #353 / PR #354; shipped at verified `v0.9.0-label-proposal-baseline` | Five-state native-grid proposal, separate all-pixel software QA, deterministic audit, exact merged-main reconstruction, and explicit dataset deferral; lifecycle sync issue #355. |
| P2O4-T01-SYNC | `records/prompt-build-log/2026-07-15-p2o4-t01-sync.md` | issue #355 / PR #356 | Documentation-only synchronization of analytical merge, verified tag, merged-main release gates, and active cross-event next checkpoint. |
| P2O4-T02 | `records/prompt-build-log/2026-07-15-p2o4-t02.md` | issue #357 / PR #358; shipped at verified `v0.10.0-cross-event-feasibility-baseline` | Current MTBS/Census/CDSE metadata selects exact Tepee/McKay acquisition pairs and freezes whole leakage groups; no imagery, dataset, split, baseline, or model. |
| P2O4-T02-SYNC | `records/prompt-build-log/2026-07-15-p2o4-t02-sync.md` | issue #359 / PR #360 lifecycle synchronization | Exact analytical merge, verified tag, merged-main release gates, and source-acquisition next checkpoint synchronized without changing outputs. |
| P2O4-T03 | `records/prompt-build-log/2026-07-15-p2o4-t03.md` | issue #361 / PR #362 / analytical merge `6a6da910849daefa918ed56af6631b2ec44bc211` | Four exact Tepee/McKay archives registered; McKay passes and Tepee is accepted with visible SCL/window exclusions; release completed through remediation #363/#364. |
| P2O4-T03-REM | `records/prompt-build-log/2026-07-16-p2o4-t03-rem.md` | issue #363 / PR #364 / merge `01c3aa4abeb89e3f15771571276a25d33e44d390` | Fresh merged-main semantic readback withheld the first tag attempt; explicit protocol/schema trace now fails closed on drift and real run `r006` preserves all scientific results; verified v0.11 tag shipped. |
| P2O4-T03-SYNC | `records/prompt-build-log/2026-07-16-p2o4-t03-sync.md` | issue #365; verified v0.11 lifecycle synchronization | PRs #362/#364, both merges, merged-main gates, and remote annotated tag are synchronized; next checkpoint is cross-event proposal transfer plus separate QA. |
| P2O4-T04 | `records/prompt-build-log/2026-07-15-p2o4-t04.md` | issue #367 / PR #368; shipped at verified `v0.12.0-cross-event-label-transfer-baseline` | Exact Tepee/McKay proposal transfer and separate 63,930-pixel QA; lifecycle sync issue #369. |
| P2O4-T04-REM | `records/prompt-build-log/2026-07-16-p2o4-t04-rem.md` | issue #371 / PR #372; shipped at verified `v0.12.1-topology-stable-label-transfer` | Removes transient current link counts from public run identity while preserving fail-closed one/exact-two-link verification; analytical output unchanged. |
| P2O4-T04-REM-SYNC | `records/prompt-build-log/2026-07-16-p2o4-t04-rem-sync.md` | issue #373 / PR #374 | Synchronizes reviewed head, merge, fresh-main gates, canonical wheel, remote annotated tag, and resumed adjudication next checkpoint. |
| P2O4-T05 | `records/prompt-build-log/2026-07-16-p2o4-t05.md` | issue #375 / PR #376; shipped at verified `v0.13.0-label-review-readiness` | Rebuilds all three proposals from exact sources and creates a 56-unit proposal-blinded review packet, separate reveal/templates, and independent integrity QA. Completed independent responses/adjudications remain zero; dataset deferred. |
| P2O4-T05-SYNC | `records/prompt-build-log/2026-07-16-p2o4-t05-sync.md` | issue #377 / PR #378; lifecycle synchronization in review | Synchronizes reviewed head, merge, fresh-main gates, canonical source wheel, remote annotated tag, and actual independent-response next checkpoint without changing analytical outputs. |
| P2O4-T06 | `records/prompt-build-log/2026-07-16-p2o4-t06.md` | issue #379 / PR #380; shipped at verified `v0.14.0-offline-reviewer-handoff` | Packages the exact blind packet into a deterministic isolated offline workbench, independently verifies the handoff, and locks returned response bytes before reveal. Human responses/adjudications remain zero; dataset deferred. |
| P2O4-T06-SYNC | `records/prompt-build-log/2026-07-16-p2o4-t06-sync.md` | issue #381 / PR #382; lifecycle synchronization in review | Synchronizes reviewed head, merge, fresh-main gates, canonical source wheel, remote annotated tag, and independent-response next checkpoint without changing code or evidence outputs. |
| P2O4-T07 | `records/prompt-build-log/2026-07-16-p2o4-t07.md` | issue #383 / PR #385; shipped at verified `v0.15.0-live-browser-reviewer-handoff` | Reconstructs the exact handoff and proves invalid-state, draft download/load, full response export, responsive viewport, console/runtime, and fixture-only lock behavior in recorded current Chrome. Zero human responses are used in the QA; dataset deferred. |
| P2O4-T07-SYNC | `records/prompt-build-log/2026-07-16-p2o4-t07-sync.md` | issue #386 / PR #387; verified v0.15.0 lifecycle synchronization | Synchronizes reviewed head, merge, fresh-main gates, canonical source wheel, remote annotated tag, and issue #384 next checkpoint without changing code or evidence outputs. |
| P2O4-T08 | `records/prompt-build-log/2026-07-16-p2o4-t08.md` | issue #384 / PR #388; shipped at verified `v0.16.0-first-reviewer-response-lock` | Preserves one exact returned response and private receipt in ignored storage, publishes content-withheld hash-lock evidence, and keeps the one-of-two/no-reveal/no-dataset gates binding. |
| P2O4-T08-REM | `records/prompt-build-log/2026-07-16-p2o4-t08-rem.md` | issue #389 / PR #390; corrected checkpoint `27fcd3eadb1473bb603b4275f986bf62022c10bf` | Corrects only the candidate-manifest creation time and completes the verified v0.16.0 release without changing evidence bytes or scientific state. |
| P2O4-T08-SYNC | `records/prompt-build-log/2026-07-16-p2o4-t08-sync.md` | issue #391 / PR #392; verified lifecycle synchronization in review | Synchronizes analytical/remediation heads and merges, fresh-main gates, canonical wheel, remote annotated tag, and the second-response next checkpoint. |
| P2O4-T09A | `records/prompt-build-log/2026-07-16-p2o4-t09a.md` | issue #394 / PR #395; shipped at verified `v0.17.0-dual-lock-custody-readiness` | Preserves the exact legacy first response/receipt pair, adds current receipt identity plus an independent two-pair verifier, and proves mixed-version custody with one real returned-response origin plus one explicitly non-human software fixture. Fresh-main and tag gates pass; a second human response, reveal, comparison, adjudication, and dataset work remain absent. |
| P2O4-T09A-SYNC | `records/prompt-build-log/2026-07-16-p2o4-t09a-sync.md` | issue #396 / PR #397; merged at `aabd185e289f8b02bb42ac1b2b9133322df82549` | Synchronizes the merge, fresh-main gates, canonical wheel, remote annotated tag, and active second-response issue #393 without changing code, evidence bytes, private custody state, or scientific state. |
| P2O4-T09A-SYNC-CLOSE | `records/prompt-build-log/2026-07-16-p2o4-t09a-sync-close.md` | issue #398 / PR #399; terminal lifecycle wording closeout | Removes the last provisional draft/in-review wording, records fresh post-sync main verification, and leaves final task-scoped merge evidence in GitHub history so no recursive lifecycle sync is required. |
| BL-GOV-002 | `records/prompt-build-log/2026-07-16-bl-gov-002.md` | issue #400; repository backlog truth reconciliation in review | Re-runs the current user-facing and custody paths, records complete live tag/release state, reconciles obsolete Phase One GitHub backlog, and keeps issue #393 as the active scientific checkpoint without changing analytical or private state. |

## Acceptance and remediation triggers

Revise the protocol, template, or an entry if it stores sensitive material; omits materially applicable authorization, scope, verification, review, or handoff evidence; invents checks; substitutes author/AI review for human approval; represents policy as enforcement; replaces repository evidence; or introduces unsupported readiness, authority, data/model, or release claims.

Safe claim:

> BurnLens has one canonical prompt/build-log protocol and index, one canonical detailed entry template, one non-canonical root router, and dated task records.

The controlling execution goal and six-phase roadmap are merged and tagged at `v0.0.8-execution-goal-baseline`. Phase Two is active. P2O4-T09A ships verified `v0.17.0-dual-lock-custody-readiness`. Reviewable Darlene/Tepee/McKay proposal evidence, a proposal-blinded 56-unit instrument, an isolated offline workbench, exact current-Chrome software acceptance, one exact content-withheld returned-response lock, and one non-human current-protocol compatibility fixture exist. Review content remains withheld, the reveal remains operator-declared unopened, and parent issue #393 requires a second human response. No comparison, adjudication, independently accepted labels, dataset, split, baseline, or model exists. Authorized credentials are used without retaining secrets; exact raw packages, private response bytes, private receipts, and fixture bytes remain local/ignored. Historical Objective Seven restrictions that conflict with the controlling goal are retained only as audit evidence and do not govern current execution.
