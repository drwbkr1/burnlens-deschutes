# Phase One / Objective Five Tracker

## Objective Five

**Versioning, Provenance, Release Control, and Claim Traceability**

Objective Five expands BurnLens Deschutes' lightweight traceability rules into a complete Phase Two-ready control system. It defines how future AOI records, source records, dataset records, baseline methods, model packages, run packages, maps, screenshots, reports, and portfolio claims will trace back to issues, branches, pull requests, commits, versions, source records, provenance records, run IDs, source-precedence notes, and use-boundary statements.

## Current status

| Field | Status |
|---|---|
| Parent issue | #144 |
| Current task | P1O5-T05 |
| Current task issue | #155 |
| Current branch | `p1o5t05b` |
| Current artifact set | `PROVENANCE_TRACEABILITY_SPEC.md`; `templates/TRACEABILITY_RECORD_TEMPLATE.md`; `records/prompt-build-log/2026-07-08-p1o5-t05.md`; README/tracker/index updates |
| Previous task | P1O5-SYNC-04 / #157 / PR #158 / merged |
| Previous primary task | P1O5-T04 / #150 / PR #156 / merged |
| Next task issue | #159 |
| Next task | P1O5-T06 - Define future run manifest and run package contract |
| Objective status | Active; provenance traceability artifacts drafted in branch for PR review |
| Data-work status | Not started and still prohibited |
| Model/map/public-output status | Not started and still prohibited |
| Tag/release status | Not created and still prohibited unless release-control gates pass and user explicitly authorizes publication |

## Boundary

Objective Five is documentation, workflow, template, release-control, provenance-planning, claims-control, and records work only.

It does not authorize final AOI selection, source data acquisition, imagery download, retained source data, preprocessing, labels, masks, baseline outputs, model inputs, model training, inference, metric computation, raster/vector processing outputs, map publication, website demo integration, public operational claims, tag creation, GitHub release publication, or official, field-validation, agency-endorsement, emergency-readiness, evacuation, routing, tactical, or incident-command claims.

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
| Current reconciliation | `docs/phase-one/objective-five/CURRENT_STATUS_RECONCILIATION.md` | Live status reconciliation after Objective Four and P1O5-T01. |

## Required workflow

```text
prompt -> task framing -> artifact contract -> issue -> branch -> research if needed -> artifact work -> prompt log if needed -> self-audit -> PR -> merge -> parent/current-status update
```

For Objective Five:

1. Use one task issue per task unless the user explicitly approves bundling.
2. Post the artifact contract before artifact creation.
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
| P1O5-T05 Create provenance traceability spec | #155 | `p1o5t05b` | `PROVENANCE_TRACEABILITY_SPEC.md`; `templates/TRACEABILITY_RECORD_TEMPLATE.md`; prompt log | In progress | No |
| P1O5-T06 Define future run manifest and run package contract | #159 | `p1o5t06b` | `RUN_PACKAGE_CONTRACT.md`; `templates/RUN_MANIFEST_TEMPLATE.json`; prompt log | Open / next | No |
| P1O5-T07 Create artifact registry specification | planned | `p1o5t07b` | `ARTIFACT_REGISTRY_SPEC.md`; prompt log | Planned | No |
| P1O5-T08 Define claim-to-evidence protocol | planned | `p1o5t08b` | `CLAIM_TRACEABILITY_PROTOCOL.md`; prompt log | Planned | No |
| P1O5-T09 Integrate source precedence into release control | planned | `p1o5t09b` | `SOURCE_PRECEDENCE_RELEASE_GATE.md`; prompt log | Planned | No |
| P1O5-T10 Create reproducibility and release QA checklist | planned | `p1o5t10b` | `REPRODUCIBILITY_CHECKLIST.md`; `RELEASE_QA_CHECKLIST.md`; prompt log | Planned | No |
| P1O5-T11 Create Objective Five research and claims records | planned | `p1o5t11b` | `OBJECTIVE_FIVE_RESEARCH_VALIDATION_LOG.md`; `OBJECTIVE_FIVE_CLAIMS_CHECK.md`; prompt log | Planned | No |
| P1O5-T12 Close out Objective Five and prepare handoff | planned | `p1o5t12b` | `OBJECTIVE_FIVE_CLOSEOUT.md`; `OBJECTIVE_FIVE_HANDOFF.md`; `OBJECTIVE_FIVE_RELEASE_NOTE.md`; prompt log | Planned | No |

## Research requirements by task

| Task | Fresh research required? | Minimum source standard |
|---|---:|---|
| P1O5-T01 | No external research required | Controlling repo docs and SOP were sufficient. |
| P1O5-T02 | No external research required | Repo state and GitHub issue/PR records govern. |
| P1O5-T03 | Complete | SemVer 2.0.0 and GitHub release/tag docs; existing `VERSIONING.md`. |
| P1O5-SYNC-03 | No external research required | Repo state and current-status artifacts govern. |
| P1O5-T04 | Complete | GitHub releases/tags docs and existing repo workflow. |
| P1O5-SYNC-04 | No external research required | Repo state and current-status artifacts govern. |
| P1O5-T05 | Complete in branch | W3C PROV overview/data model and existing Objective Four intake/provenance templates. |
| P1O5-T06 | Yes | Existing technical/run package requirements; STAC or geospatial metadata references if invoked. |
| P1O5-T07 | Conditional | Repo artifacts govern unless registry claims invoke external metadata standards. |
| P1O5-T08 | Conditional | Repo claims controls govern; external model/data-card standards only if cited. |
| P1O5-T09 | Conditional | Existing `SOURCE_PRECEDENCE.md` governs unless new official-source claims are added. |
| P1O5-T10 | Conditional | Repo QA/release controls govern; external QA claims require primary sources. |
| P1O5-T11 | Yes | Sources actually used in T03-T10. |
| P1O5-T12 | No external research expected | Merged Objective Five artifacts govern. |

## Current safe claims

After P1O5-T05 is merged, safe claims will be limited to:

```text
BurnLens has a provenance traceability spec and reusable traceability record template that map W3C PROV-inspired entity, activity, and agent concepts to BurnLens source records, access logs, prechecks, provenance manifests, processing steps, method versions, output artifacts, run reports, claim-register entries, and public-facing claims.
```

```text
BurnLens provenance traceability does not create data, models, maps, runs, reports, public demos, tags, GitHub releases, operational wildfire products, or official wildfire information.
```

## Unsupported claims

Do not claim:

- Objective Five is complete;
- a full formal W3C PROV implementation exists;
- run package contracts exist;
- Phase Two data work has begun;
- an AOI has been selected;
- data has been downloaded;
- labels, masks, baseline outputs, model outputs, run outputs, metrics, maps, reports, or public demos have been created;
- a tag or GitHub release has been created;
- provenance traceability makes BurnLens official, operational, field-validated, emergency-ready, agency-endorsed, production-stable, or suitable for evacuation/routing/tactical/incident-command support.

## Handoff

After the P1O5-T05 PR is reviewed and merged:

1. confirm issue #155 closes;
2. comment on parent #144 with the PR number, changed files, and next task;
3. proceed to P1O5-T06 / #159 from current `main`;
4. keep Phase Two data work blocked until later tasks explicitly authorize intake records and all required gates exist.
