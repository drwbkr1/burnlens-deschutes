# Phase One / Objective Five Tracker

## Objective Five

**Versioning, Provenance, Release Control, and Claim Traceability**

Objective Five expands BurnLens Deschutes' lightweight traceability rules into a complete Phase Two-ready control system. It defines how future AOI records, source records, dataset records, baseline methods, model packages, run packages, maps, screenshots, reports, and portfolio claims will trace back to issues, branches, pull requests, commits, versions, source records, provenance records, run IDs, source-precedence notes, use-boundary statements, claim-evidence links, release-status decisions, reproducibility reviews, release QA decisions, research validation, claims checks, closeout records, handoff records, and release-note drafts.

## Current status

| Field | Status |
|---|---|
| Parent issue | #144 |
| Current task | P1O5-T12 |
| Current task issue | #183 |
| Current branch | `p1o5t12b` |
| Current artifact set | `OBJECTIVE_FIVE_CLOSEOUT.md`; `OBJECTIVE_FIVE_HANDOFF.md`; `OBJECTIVE_FIVE_RELEASE_NOTE.md`; `records/prompt-build-log/2026-07-08-p1o5-t12.md`; README/tracker/index updates |
| Previous task | P1O5-SYNC-11 / #185 / PR #186 / merged |
| Previous primary task | P1O5-T11 / #179 / PR #184 / merged |
| Objective status | Active; closeout, handoff, and release-note draft in branch for PR review |
| Proposed baseline tag | `v0.0.5-objective-five-traceability` |
| Proposed tag status | Proposed only; not created by this task |
| GitHub Release status | Not created |
| Data-work status | Not started and still prohibited |
| Model/map/public-output status | Not started and still prohibited |
| Run package status | Not created; T06 defined contract/template only |
| Registry database status | Not created; T07 defined spec only |
| Completed claim-register status | Not created; T08 defined protocol/template only; T11 defined claims check only |
| Source-precedence review record status | Not created; T09 defined gate only |
| Reproducibility review status | Not created; T10 defined reusable checklist only |
| Release QA decision status | Not created; T10 defined reusable checklist only |
| Research/claims records status | Merged via PR #184 |
| Closeout/handoff/release-note status | Drafted in branch; not merged until PR closes #183 |
| Parent close readiness | Ready after P1O5-T12 PR and final status sync merge |

## Boundary

Objective Five is documentation, workflow, template, release-control, provenance-planning, claims-control, QA-control, research-validation, closeout, handoff, release-note drafting, and records work only.

It does not authorize final AOI selection, source data acquisition, imagery download, retained source data, preprocessing, labels, masks, baseline outputs, model inputs, model training, inference, metric computation, raster/vector processing outputs, map publication, website demo integration, public operational claims, tag creation, GitHub release publication, run folder creation, run package creation, run output creation, public screenshot creation, registry database creation, completed claim record creation, source-precedence review record creation, completed reproducibility review creation, release QA decision creation, approved public-facing claim creation, or official, field-validation, agency-endorsement, emergency-readiness, evacuation, routing, tactical, or incident-command claims.

Required warning for future public-facing outputs remains:

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

## Controlling sources for Objective Five

Use the current Prompt-to-Repo SOP as the primary operating instruction for task workflow. Use these repo artifacts as controlling context for Objective Five work:

| Control area | Governing artifact(s) | Objective Five use |
|---|---|---|
| Repo-agent instructions | `AGENTS.md` | Boundary language, source precedence, task loop, prompt-built work expectations. |
| Issue creation | `.github/ISSUE_TEMPLATE/task.yml` | Required task issue fields, boundary checks, research gate, acceptance checklist. |
| Pull requests | `.github/PULL_REQUEST_TEMPLATE.md` | Task linkage, artifact contract, research gate, boundary gate, close keyword. |
| Branch/PR workflow | `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md` | Branch naming, PR title/body rules, close-keyword rule, merge/update sequence. |
| Prompt/build logging | `records/PROMPT_BUILD_LOG.md`; `templates/PROMPT_LOG_ENTRY.md` | Required task log for prompt-assisted file creation or edits. |
| Project identity and technical chain | `README.md`; `docs/objective-one/TECHNICAL_DESCRIPTION.md` | Portfolio-first CV/GEOINT identity and future technical workflow. |
| Use boundaries | `docs/objective-one/USE_BOUNDARIES.md` | Appropriate/prohibited uses, stop rules, disclaimer language. |
| Source precedence | `docs/objective-one/SOURCE_PRECEDENCE.md` | Official sources govern; BurnLens-derived outputs remain lowest priority. |
| Versioning | `VERSIONING.md`; `docs/phase-one/objective-five/VERSION_TAXONOMY.md` | Expanded traceability rule and version/identifier taxonomy. |
| Release control | `docs/phase-one/objective-five/RELEASE_CONTROL.md`; `templates/RELEASE_NOTE_TEMPLATE.md` | Release classes, tag eligibility, release-note requirements, and do-not-release triggers. |
| Provenance traceability | `docs/phase-one/objective-five/PROVENANCE_TRACEABILITY_SPEC.md`; `templates/TRACEABILITY_RECORD_TEMPLATE.md` | Source-to-claim lineage, BurnLens entity/activity/agent equivalents, and claim evidence gates. |
| Run package control | `docs/phase-one/objective-five/RUN_PACKAGE_CONTRACT.md`; `templates/RUN_MANIFEST_TEMPLATE.json` | Future run folder contract, manifest requirements, output inventory, warnings, and screenshot run-ID rule. |
| Artifact registry | `docs/phase-one/objective-five/ARTIFACT_REGISTRY_SPEC.md` | Future artifact locations, naming patterns, registry states, and source-separation controls. |
| Claim traceability | `docs/phase-one/objective-five/CLAIM_TRACEABILITY_PROTOCOL.md`; `templates/CLAIM_EVIDENCE_LINK_TEMPLATE.md` | Future claim ladder, evidence links, forbidden-claim checks, and source-precedence language requirements. |
| Source-precedence release gate | `docs/phase-one/objective-five/SOURCE_PRECEDENCE_RELEASE_GATE.md` | Future run-report conflict handling, public artifact status decisions, and release blockers. |
| Reproducibility and release QA | `docs/phase-one/objective-five/REPRODUCIBILITY_CHECKLIST.md`; `docs/phase-one/objective-five/RELEASE_QA_CHECKLIST.md` | Future objective baseline, dataset, model/baseline, run/report, and public demo review gates. |
| Research validation and claims check | `docs/phase-one/objective-five/OBJECTIVE_FIVE_RESEARCH_VALIDATION_LOG.md`; `docs/phase-one/objective-five/OBJECTIVE_FIVE_CLAIMS_CHECK.md` | Source-backed decisions, safe/caveated/unsupported claim boundaries, and closeout claim control. |
| Closeout, handoff, release note | `OBJECTIVE_FIVE_CLOSEOUT.md`; `OBJECTIVE_FIVE_HANDOFF.md`; `OBJECTIVE_FIVE_RELEASE_NOTE.md` | Objective closeout, next-context handoff, and proposed tag release-note draft. |
| Current reconciliation | `docs/phase-one/objective-five/CURRENT_STATUS_RECONCILIATION.md` | Live status reconciliation after Objective Four and P1O5-T01. |

## Required workflow

```text
prompt -> task framing -> artifact contract -> issue -> branch -> research if needed -> artifact work -> prompt log if needed -> self-audit -> PR -> merge -> parent/current-status update
```

For Objective Five:

1. Use one task issue per task unless the user explicitly approves bundling.
2. Post or preserve the artifact contract before artifact creation.
3. Create a compact task branch from current `main`.
4. Complete fresh research after branch creation and before artifact writing when the task makes current, technical, source, tooling, policy, legal, safety, data, model, or public-claim statements.
5. Create or update a prompt/build log entry when ChatGPT/Codex creates or materially changes files.
6. Open a PR that closes only the task issue.
7. Do not close parent #144 from a normal task PR.
8. Update this tracker and other current-status artifacts whenever their truth changes, especially after merge.
9. Historical logs should not be rewritten unless stale pending status affects current handoff clarity.

## Objective Five task sequence

| Task | Issue | Branch | Primary artifact(s) | Status | Starts data/model/map work? |
|---|---:|---|---|---|---|
| P1O5-T01 Create Objective Five tracker and artifact contracts | #145 | `p1o5t01b` | `OBJECTIVE_FIVE_TRACKER.md`; `OBJECTIVE_FIVE_ARTIFACT_CONTRACTS.md`; P1O5-T01 prompt log | Merged via PR #147 | No |
| P1O5-T02 Reconcile current repo status and README handoff | #146 | `p1o5t02b` | `CURRENT_STATUS_RECONCILIATION.md`; README update; tracker update; prompt-log updates | Merged via PR #149 | No |
| P1O5-T03 Expand version taxonomy | #148 | `p1o5t03b` | `VERSION_TAXONOMY.md`; `VERSIONING.md`; prompt log | Merged via PR #152 | No |
| P1O5-SYNC-03 Sync status after version taxonomy merge | #153 | `p1o5sync03` | README; tracker; prompt-log index; P1O5-T03 log | Merged via PR #154 | No |
| P1O5-T04 Define release and tag control | #150 | `p1o5t04b` | `RELEASE_CONTROL.md`; `templates/RELEASE_NOTE_TEMPLATE.md`; prompt log | Merged via PR #156 | No |
| P1O5-SYNC-04 Sync status after release-control merge | #157 | `p1o5sync04` | README; tracker; prompt-log index; P1O5-T04 log | Merged via PR #158 | No |
| P1O5-T05 Create provenance traceability spec | #155 | `p1o5t05b` | `PROVENANCE_TRACEABILITY_SPEC.md`; `templates/TRACEABILITY_RECORD_TEMPLATE.md`; prompt log | Merged via PR #160 | No |
| P1O5-SYNC-05 Sync status after provenance traceability merge | #161 | `p1o5sync05` | README; tracker; prompt-log index; P1O5-T05 log | Merged via PR #162 | No |
| P1O5-T06 Define future run manifest and run package contract | #159 | `p1o5t06b` | `RUN_PACKAGE_CONTRACT.md`; `templates/RUN_MANIFEST_TEMPLATE.json`; prompt log | Merged via PR #164 | No |
| P1O5-SYNC-06 Sync status after run package contract merge | #165 | `p1o5sync06` | README; tracker; prompt-log index; P1O5-T06 log | Merged via PR #166 | No |
| P1O5-T07 Create artifact registry specification | #163 | `p1o5t07b` | `ARTIFACT_REGISTRY_SPEC.md`; prompt log | Merged via PR #168 | No |
| P1O5-SYNC-07 Sync status after artifact registry merge | #169 | `p1o5sync07` | README; tracker; prompt-log index; P1O5-T07 log | Merged via PR #170 | No |
| P1O5-T08 Define claim-to-evidence protocol | #167 | `p1o5t08b` | `CLAIM_TRACEABILITY_PROTOCOL.md`; `templates/CLAIM_EVIDENCE_LINK_TEMPLATE.md`; prompt log | Merged via PR #172 | No |
| P1O5-SYNC-08 Sync status after claim protocol merge | #173 | `p1o5sync08` | README; tracker; prompt-log index; P1O5-T08 log | Merged via PR #174 | No |
| P1O5-T09 Integrate source precedence into release control | #171 | `p1o5t09b` | `SOURCE_PRECEDENCE_RELEASE_GATE.md`; prompt log | Merged via PR #176 | No |
| P1O5-SYNC-09 Sync status after source-precedence release gate merge | #177 | `p1o5sync09` | README; tracker; prompt-log index; P1O5-T09 log | Merged via PR #178 | No |
| P1O5-T10 Create reproducibility and release QA checklist | #175 | `p1o5t10b` | `REPRODUCIBILITY_CHECKLIST.md`; `RELEASE_QA_CHECKLIST.md`; prompt log | Merged via PR #180 | No |
| P1O5-SYNC-10 Sync status after T10 merge | #181 | `p1o5sync10` | README; tracker; prompt-log index; P1O5-T10 log | Merged via PR #182 | No |
| P1O5-T11 Create Objective Five research and claims records | #179 | `p1o5t11b` | `OBJECTIVE_FIVE_RESEARCH_VALIDATION_LOG.md`; `OBJECTIVE_FIVE_CLAIMS_CHECK.md`; prompt log | Merged via PR #184 | No |
| P1O5-SYNC-11 Sync status after T11 merge | #185 | `p1o5sync11` | README; tracker; prompt-log index; P1O5-T11 log | Merged via PR #186 | No |
| P1O5-T12 Close out Objective Five and prepare handoff | #183 | `p1o5t12b` | `OBJECTIVE_FIVE_CLOSEOUT.md`; `OBJECTIVE_FIVE_HANDOFF.md`; `OBJECTIVE_FIVE_RELEASE_NOTE.md`; prompt log | In progress | No |

## Research requirements by task

| Task | Fresh research required? | Minimum source standard |
|---|---:|---|
| P1O5-T01 | No external research required | Controlling repo docs and SOP were sufficient. |
| P1O5-T02 | No external research required | Repo state and GitHub issue/PR records govern. |
| P1O5-T03 | Complete | SemVer 2.0.0 and GitHub release/tag docs; existing `VERSIONING.md`. |
| P1O5-SYNC-03 | No external research required | Repo state and current-status artifacts govern. |
| P1O5-T04 | Complete | GitHub releases/tags docs and existing repo workflow. |
| P1O5-SYNC-04 | No external research required | Repo state and current-status artifacts govern. |
| P1O5-T05 | Complete | W3C PROV overview/data model and existing Objective Four intake/provenance templates. |
| P1O5-SYNC-05 | No external research required | Repo state and current-status artifacts govern. |
| P1O5-T06 | Complete | W3C PROV overview/data model, OGC STAC Community Standard as lightweight geospatial asset metadata reference, and existing repo controls. |
| P1O5-SYNC-06 | No external research required | Repo state and current-status artifacts govern. |
| P1O5-T07 | Not required | Existing repo controls govern; no external metadata-standard claims introduced. |
| P1O5-SYNC-07 | No external research required | Repo state and current-status artifacts govern. |
| P1O5-T08 | Not required | Existing repo controls govern; no external model-card, data-card, or claims-standard references introduced. |
| P1O5-SYNC-08 | No external research required | Repo state and current-status artifacts govern. |
| P1O5-T09 | Not required | Existing source-precedence, claim protocol, release-control, run-package, artifact-registry, and versioning controls govern; no new official-source claims introduced. |
| P1O5-SYNC-09 | No external research required | Repo state and current-status artifacts govern. |
| P1O5-T10 | Not required | Existing repo QA/release controls govern; no new external QA or reproducibility claims introduced. |
| P1O5-SYNC-10 | No external research required | Repo state and current-status artifacts govern. |
| P1O5-T11 | Complete | SemVer 2.0.0, GitHub release/tag docs, W3C PROV overview/data model, OGC STAC Community Standard, and current merged repo controls. |
| P1O5-SYNC-11 | No external research required | Repo state and current-status artifacts govern. |
| P1O5-T12 | No new external research required | Merged Objective Five artifacts, especially research validation and claims check, govern. |

## Current safe claims

After P1O5-T12 is merged and final status synchronization is complete, safe claims will be limited to:

```text
BurnLens has completed Phase One / Objective Five documentation and control work for versioning, provenance, release control, run-package planning, artifact registry planning, source-precedence release gates, reproducibility QA, research validation, and claim traceability.
```

```text
BurnLens remains experimental and non-operational. Official sources govern.
```

```text
The proposed Objective Five baseline tag is v0.0.5-objective-five-traceability, but it has not been created unless a later authorized release task creates it.
```

## Unsupported claims

Do not claim:

- Phase Two data work has begun;
- an AOI has been selected;
- data has been downloaded;
- source records, AOI records, labels, masks, baseline outputs, model outputs, run outputs, metrics, maps, reports, screenshots, or public demos have been created;
- a tag or GitHub Release has been created;
- the proposed tag has been created;
- a completed claim register exists;
- any public-facing claim has been approved;
- a completed reproducibility review exists;
- a release QA decision exists;
- Objective Five controls make BurnLens official, operational, field-validated, emergency-ready, agency-endorsed, production-stable, or suitable for evacuation/routing/tactical/incident-command support.

## Handoff

After the P1O5-T12 PR is reviewed and merged:

1. confirm issue #183 closes;
2. run a final current-status sync if README, tracker, or prompt logs still describe P1O5-T12 as active;
3. confirm parent issue #144 is closeable;
4. keep Phase Two data work blocked until later tasks explicitly authorize intake records and all required gates exist;
5. use `OBJECTIVE_FIVE_HANDOFF.md` as the first context block for Phase Two or Objective Six.
