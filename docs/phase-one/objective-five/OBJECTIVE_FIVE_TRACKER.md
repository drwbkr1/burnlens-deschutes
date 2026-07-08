# Phase One / Objective Five Tracker

## Objective Five

**Versioning, Provenance, Release Control, and Claim Traceability**

Objective Five expands BurnLens Deschutes' lightweight traceability rules into a complete Phase Two-ready control system. It defines how future AOI records, source records, dataset records, baseline methods, model packages, run packages, maps, screenshots, reports, and portfolio claims will trace back to issues, branches, pull requests, commits, versions, source records, provenance records, run IDs, source-precedence notes, and use-boundary statements.

## Current status

| Field | Status |
|---|---|
| Parent issue | #144 |
| Current task | P1O5-T02 |
| Current task issue | #146 |
| Current branch | `p1o5t02b` |
| Current artifact set | `CURRENT_STATUS_RECONCILIATION.md`; README update; tracker update; `records/PROMPT_BUILD_LOG.md`; `records/prompt-build-log/2026-07-08-p1o5-t02.md` |
| Previous task | P1O5-T01 / #145 / PR #147 / merged |
| Next task issue | #148 |
| Next task | P1O5-T03 - Expand version taxonomy |
| Objective status | Active; current-status reconciliation drafted in branch for PR review |
| Data-work status | Not started and still prohibited |
| Model/map/public-output status | Not started and still prohibited |

## Boundary

Objective Five is documentation, workflow, template, release-control, provenance-planning, claims-control, and records work only.

It does not authorize:

- final AOI selection;
- source data acquisition;
- imagery download;
- retained source data;
- preprocessing;
- labels;
- masks;
- baseline outputs;
- model inputs;
- model training;
- inference;
- metric computation;
- raster/vector processing outputs;
- map publication;
- website demo integration;
- public operational claims;
- official, field-validation, agency-endorsement, emergency-readiness, evacuation, routing, tactical, or incident-command claims.

Required warning for future public-facing outputs remains:

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

## Controlling sources for Objective Five

Use the current Prompt-to-Repo SOP as the primary operating instruction for task workflow. Use the following repo artifacts as controlling context for Objective Five work:

| Control area | Governing artifact(s) | Objective Five use |
|---|---|---|
| Repo-agent instructions | `AGENTS.md` | Boundary language, source precedence, task loop, prompt-built work expectations. |
| Issue creation | `.github/ISSUE_TEMPLATE/task.yml` | Required task issue fields, boundary checks, research gate, acceptance checklist. |
| Pull requests | `.github/PULL_REQUEST_TEMPLATE.md` | Task linkage, artifact contract, research gate, boundary gate, close keyword. |
| Branch/PR workflow | `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md` | Branch naming, PR title/body rules, close-keyword rule, merge/update sequence. |
| Codex task packet | `templates/CODEX_TASK_PACKET.md` | Prompt-assisted task framing and verification expectations. |
| Prompt/build logging | `records/PROMPT_BUILD_LOG.md`; `templates/PROMPT_LOG_ENTRY.md` | Required task log for prompt-assisted file creation or edits. |
| Project identity and technical chain | `README.md`; `docs/objective-one/TECHNICAL_DESCRIPTION.md` | Portfolio-first CV/GEOINT identity and future technical workflow. |
| Use boundaries | `docs/objective-one/USE_BOUNDARIES.md` | Appropriate/prohibited uses, stop rules, disclaimer language. |
| Source precedence | `docs/objective-one/SOURCE_PRECEDENCE.md` | Official sources govern; BurnLens-derived outputs remain lowest priority. |
| Versioning | `VERSIONING.md` | Existing traceability rule and version fields to be expanded in P1O5-T03. |
| Objective Four handoff | `docs/phase-one/objective-four/OBJECTIVE_FOUR_HANDOFF.md` | Starting instruction for Objective Five and no-data transition rule. |
| Objective Four release note | `docs/phase-one/objective-four/OBJECTIVE_FOUR_RELEASE_NOTE.md` | Repo-ops baseline and Phase Two intake-readiness boundary. |
| Current reconciliation | `docs/phase-one/objective-five/CURRENT_STATUS_RECONCILIATION.md` | Live status reconciliation after Objective Four and P1O5-T01. |

## Required workflow

Use this loop for each Objective Five task:

```text
prompt -> task framing -> artifact contract -> issue -> branch -> research if needed -> artifact work -> prompt log if needed -> self-audit -> PR -> merge -> parent/current-status update
```

For Objective Five, this means:

1. Use one task issue per task unless the user explicitly approves bundling.
2. Post the artifact contract before artifact creation.
3. Create a compact task branch from current `main`.
4. Complete fresh research after branch creation and before artifact writing when the task makes current, technical, source, tooling, policy, legal, safety, data, model, or public-claim statements.
5. Create or update a prompt/build log entry when ChatGPT/Codex creates or materially changes files.
6. Open a PR that closes only the task issue.
7. Do not close parent #144 from a normal task PR.
8. Update this tracker only when current Objective Five status changes.

## Objective Five task sequence

| Task | Issue | Branch | Primary artifact(s) | Status | Starts data/model/map work? |
|---|---:|---|---|---|---|
| P1O5-T01 Create Objective Five tracker and artifact contracts | #145 | `p1o5t01b` | `OBJECTIVE_FIVE_TRACKER.md`; `OBJECTIVE_FIVE_ARTIFACT_CONTRACTS.md`; P1O5-T01 prompt log | Merged via PR #147 | No |
| P1O5-T02 Reconcile current repo status and README handoff | #146 | `p1o5t02b` | `CURRENT_STATUS_RECONCILIATION.md`; README update; tracker update; prompt-log updates | In progress | No |
| P1O5-T03 Expand version taxonomy | #148 | `p1o5t03b` | `VERSION_TAXONOMY.md`; `VERSIONING.md` if protocol changes; prompt log | Open / next | No |
| P1O5-T04 Define release and tag control | planned | `p1o5t04b` | `RELEASE_CONTROL.md`; `templates/RELEASE_NOTE_TEMPLATE.md`; prompt log | Planned | No |
| P1O5-T05 Create provenance traceability spec | planned | `p1o5t05b` | `PROVENANCE_TRACEABILITY_SPEC.md`; `templates/TRACEABILITY_RECORD_TEMPLATE.md`; prompt log | Planned | No |
| P1O5-T06 Define future run manifest and run package contract | planned | `p1o5t06b` | `RUN_PACKAGE_CONTRACT.md`; `templates/RUN_MANIFEST_TEMPLATE.json`; prompt log | Planned | No |
| P1O5-T07 Create artifact registry specification | planned | `p1o5t07b` | `ARTIFACT_REGISTRY_SPEC.md`; prompt log | Planned | No |
| P1O5-T08 Define claim-to-evidence protocol | planned | `p1o5t08b` | `CLAIM_TRACEABILITY_PROTOCOL.md`; `templates/CLAIM_EVIDENCE_LINK_TEMPLATE.md`; prompt log | Planned | No |
| P1O5-T09 Integrate source precedence into release control | planned | `p1o5t09b` | `SOURCE_PRECEDENCE_RELEASE_GATE.md`; prompt log | Planned | No |
| P1O5-T10 Create reproducibility and release QA checklist | planned | `p1o5t10b` | `REPRODUCIBILITY_CHECKLIST.md`; `RELEASE_QA_CHECKLIST.md`; prompt log | Planned | No |
| P1O5-T11 Create Objective Five research and claims records | planned | `p1o5t11b` | `OBJECTIVE_FIVE_RESEARCH_VALIDATION_LOG.md`; `OBJECTIVE_FIVE_CLAIMS_CHECK.md`; prompt log | Planned | No |
| P1O5-T12 Close out Objective Five and prepare handoff | planned | `p1o5t12b` | `OBJECTIVE_FIVE_CLOSEOUT.md`; `OBJECTIVE_FIVE_HANDOFF.md`; `OBJECTIVE_FIVE_RELEASE_NOTE.md`; prompt log | Planned | No |

## Task dependency notes

| Dependency | Rule |
|---|---|
| T02 after T01 | Current status reconciliation uses the tracker and artifact-contracts file after merge. |
| T03 after T02 | Version taxonomy should happen after top-level status and current controlling handoff are reconciled. |
| T04 after T03 | Release control should use the expanded version taxonomy. |
| T05 after T03 | Provenance traceability should use the version taxonomy and existing Objective Three provenance fields. |
| T06 after T05 | Future run package contract should link to provenance entities, activities, outputs, and source records. |
| T07 after T06 | Artifact registry should know the version and run-package naming rules. |
| T08 after T07 | Claim-to-evidence protocol should point claims to registered artifact classes. |
| T09 after T08 | Source-precedence release gate should connect claims, run reports, and official-source conflict handling. |
| T10 after T04 and T09 | Release QA should use release-control rules and source-precedence gates. |
| T11 after T03-T10 | Research and claims records should summarize decisions made across the objective. |
| T12 after T01-T11 | Closeout and handoff should summarize merged Objective Five artifacts and preserve Phase Two readiness boundaries. |

## Research requirements by task

| Task | Fresh research required? | Minimum source standard |
|---|---:|---|
| P1O5-T01 | No external research required | Controlling repo docs and SOP were sufficient. |
| P1O5-T02 | No external research required | Repo state and GitHub issue/PR records govern. |
| P1O5-T03 | Yes | SemVer and existing `VERSIONING.md`; official/primary versioning references. |
| P1O5-T04 | Yes | GitHub releases/tags docs and existing repo workflow. |
| P1O5-T05 | Yes | W3C PROV or comparable primary provenance standard; Objective Three provenance fields. |
| P1O5-T06 | Yes | Existing technical/run package requirements; STAC or geospatial metadata references if invoked. |
| P1O5-T07 | Conditional | Repo artifacts govern unless registry claims invoke external metadata standards. |
| P1O5-T08 | Conditional | Repo claims controls govern; external model/data-card standards only if cited. |
| P1O5-T09 | Conditional | Existing `SOURCE_PRECEDENCE.md` governs unless new official-source claims are added. |
| P1O5-T10 | Conditional | Repo QA/release controls govern; external QA claims require primary sources. |
| P1O5-T11 | Yes | Sources actually used in T03-T10. |
| P1O5-T12 | No external research expected | Merged Objective Five artifacts govern. |

## Current safe claims

After P1O5-T02 is merged, safe claims will be limited to:

```text
BurnLens has reconciled its current repository status for Phase One / Objective Five and updated current-status records so future Objective Five tasks begin from the correct handoff.
```

```text
Objective Five is active documentation and traceability-control work; Phase Two data work has not begun.
```

## Unsupported claims

Do not claim:

- Objective Five is complete;
- Versioning has already been expanded beyond `VERSIONING.md`;
- release/tag policy has been finalized;
- provenance traceability has been fully specified;
- run package contracts exist;
- Phase Two data work has begun;
- an AOI has been selected;
- data has been downloaded;
- labels, masks, baseline outputs, model outputs, run outputs, metrics, maps, or public demos have been created;
- BurnLens outputs are official, operational, field-validated, emergency-ready, agency-endorsed, or suitable for evacuation/routing/tactical/incident-command support.

## Acceptance checklist for P1O5-T02

| Check | Status | Notes |
|---|---|---|
| Parent issue exists. | Satisfied | #144. |
| Task issue exists. | Satisfied | #146. |
| Next task issue exists. | Satisfied | #148. |
| Task branch exists. | Satisfied | `p1o5t02b`. |
| Artifact contract posted to task issue. | Satisfied | Comment on #146. |
| Current status reconciliation created. | Satisfied in branch | `CURRENT_STATUS_RECONCILIATION.md`. |
| README update justified. | Satisfied in branch | README previously pointed to Objective Two. |
| Tracker update justified. | Satisfied in branch | P1O5-T01 merged; P1O5-T02 active; P1O5-T03 issue exists. |
| Prompt/build log entry created. | Pending until log file exists | `records/prompt-build-log/2026-07-08-p1o5-t02.md`. |
| Prompt/build log index updated. | Pending | `records/PROMPT_BUILD_LOG.md`. |
| Boundary language present. | Satisfied | Boundary section above. |
| Claims check present. | Satisfied | Safe and unsupported claims listed above. |
| Handoff present. | Satisfied | Handoff section below. |

## Handoff

After the P1O5-T02 PR is reviewed and merged:

1. confirm issue #146 closes;
2. comment on parent #144 with the PR number, changed files, and next task;
3. proceed to P1O5-T03 / #148;
4. keep Phase Two data work blocked until later tasks explicitly authorize intake records and all required gates exist.
