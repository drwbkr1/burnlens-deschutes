# BurnLens Deschutes

BurnLens Deschutes is a computer vision + GEOINT portfolio project focused on experimental wildfire-related screening in Deschutes County, Oregon.

The project demonstrates a reproducible workflow for turning wildfire-relevant imagery, public geospatial layers, and experimental segmentation or baseline outputs into traceable map-ready artifacts.

## Current status

**Phase One / Objective Five is active.**

Objective Five is expanding BurnLens Deschutes' lightweight versioning and traceability posture into a fuller control baseline for versioning, provenance, release control, run packages, artifact registries, source-precedence gates, QA, and claim traceability.

P1O5-T01 is complete. It created the Objective Five parent issue, first task issue, tracker, artifact-contract baseline, and prompt/build log entry for Task 1.

P1O5-T02 is complete. It reconciled the current repository status after Objective Four and P1O5-T01, updated this README, updated the Objective Five tracker, and updated the prompt/build log index.

P1O5-T03 is complete. It created the expanded version taxonomy and updated `VERSIONING.md` because the versioning protocol itself changed.

P1O5-SYNC-03 is complete. It synchronized current-status artifacts after the P1O5-T03 merge.

P1O5-T04 is complete. It created release and tag control, a reusable release-note template, and current-status updates.

P1O5-SYNC-04 is complete. It synchronized current-status artifacts after the P1O5-T04 merge.

P1O5-T05 is complete. It created the provenance traceability spec and reusable traceability record template.

P1O5-SYNC-05 is complete. It synchronized current-status artifacts after the P1O5-T05 merge.

P1O5-T06 is complete. It created the future run package contract and reusable run manifest template.

P1O5-SYNC-06 is complete. It synchronized current-status artifacts after the P1O5-T06 merge.

P1O5-T07 is complete. It created the artifact registry specification.

P1O5-SYNC-07 is complete. It synchronized current-status artifacts after the P1O5-T07 merge.

P1O5-T08 is complete. It created the claim-to-evidence protocol and reusable claim evidence link template.

P1O5-SYNC-08 is complete. It synchronized current-status artifacts after the P1O5-T08 merge.

P1O5-T09 is complete. It created the source-precedence release gate.

P1O5-SYNC-09 is complete. It synchronized current-status artifacts after the P1O5-T09 merge.

P1O5-T10 / #175 is active on branch `p1o5t10b`. It creates reusable BurnLens-specific reproducibility and release QA checklists for objective baselines, future dataset releases, model/baseline releases, run/report releases, and public demo releases.

The current repository state is still documentation, workflow, template, traceability-control, QA-control, and records work. No data ingestion, imagery download, AOI selection, source-data acquisition, label creation, mask creation, baseline generation, model training, inference, metric computation, raster/vector output generation, map publication, website demo integration, public performance claim, tag, GitHub release, run folder, run package, run output, report package, public screenshot, registry database, completed claim record, source-precedence review record, completed reproducibility review, or release QA decision has been authorized.

Current controlling handoff / current-status records:

```text
docs/phase-one/objective-five/CURRENT_STATUS_RECONCILIATION.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_TRACKER.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_ARTIFACT_CONTRACTS.md
docs/phase-one/objective-five/VERSION_TAXONOMY.md
docs/phase-one/objective-five/RELEASE_CONTROL.md
docs/phase-one/objective-five/PROVENANCE_TRACEABILITY_SPEC.md
docs/phase-one/objective-five/RUN_PACKAGE_CONTRACT.md
docs/phase-one/objective-five/ARTIFACT_REGISTRY_SPEC.md
docs/phase-one/objective-five/CLAIM_TRACEABILITY_PROTOCOL.md
docs/phase-one/objective-five/SOURCE_PRECEDENCE_RELEASE_GATE.md
docs/phase-one/objective-five/REPRODUCIBILITY_CHECKLIST.md
docs/phase-one/objective-five/RELEASE_QA_CHECKLIST.md
VERSIONING.md
templates/RELEASE_NOTE_TEMPLATE.md
templates/TRACEABILITY_RECORD_TEMPLATE.md
templates/RUN_MANIFEST_TEMPLATE.json
templates/CLAIM_EVIDENCE_LINK_TEMPLATE.md
```

Current parent/task issues:

```text
#144 - Phase 1 Objective Five parent
#175 - P1O5-T10 Create reproducibility and release QA checklist
#179 - P1O5-T11 Create Objective Five research and claims records
```

## Locked computer vision task

BurnLens Deschutes' first computer vision task is:

> **Experimental binary semantic segmentation for wildfire-relevant screening.**

The primary target is:

> **Active-fire / hotspot-informed binary fire mask.**

The fallback target is:

> **Burn-scar binary mask.**

The fallback may be used only if later feasibility work shows active-fire / hotspot-informed labels are too weak, sparse, noisy, misaligned, or otherwise indefensible for a portfolio model. Changing to the fallback requires a documented decision update.

## Core workflow

```text
imagery → preprocessing → segmentation or baseline mask → raster output → vector polygons → map overlay → exposure-style summary → documented run package
```

This chain is a future workflow contract. It does not mean those stages have already been implemented.

## Use boundary

BurnLens Deschutes is an experimental portfolio project.

It is not emergency guidance, not official wildfire information, not an evacuation-order tool, not routing or road-closure guidance, not tactical fire intelligence, not an incident-command product, not a field-validated hazard system, and not a substitute for county, state, federal, fire-service, emergency-management, transportation, air-quality, or incident sources.

Official sources govern when information differs.

Required warning language for future BurnLens CV outputs:

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

## Source separation rule

Future BurnLens artifacts must keep these categories separate:

- official/reference sources
- reference-derived labels
- baseline outputs
- model outputs
- map overlays
- portfolio interpretations

No report, map, model card, run package, website card, or screenshot should blur those categories.

## Claim boundary rule

Every future public-facing claim must link to evidence. Claims involving fire, wildfire, evacuation, hazard, road, routing, closure, emergency, or public-safety context must include source-precedence language. BurnLens may claim reproducibility, traceability, technical workflow demonstration, and transparent limitations only when supporting records exist.

## Source-precedence release gate

Future public artifacts involving BurnLens-derived outputs must state whether the output is `normal`, `provisional`, `degraded`, `superseded`, or `withheld`. Outputs that conflict with official information or cannot be caveated responsibly are blocked from release.

## Reproducibility and release QA gates

Future objective baselines, dataset releases, model/baseline releases, run/report releases, and public demo releases must pass BurnLens-specific reproducibility and release QA checks before release-like action. These checks include issue, branch, PR, prompt-log, allowed-file, version, provenance, source-precedence, use-boundary, claim-evidence, and included/excluded release-note review.

## Repository structure

```text
docs/
  objective-one/          Project identity, thesis, technical description, source precedence, and use boundaries
  phase-one/
    objective-two/        Completed CV task-definition docs and final handoff
    objective-three/      Completed source/AOI/CRS/provenance feasibility controls
    objective-four/       Completed repo operating-system, workflow, and release-note baseline
    objective-five/       Active versioning, provenance, release-control, and claim-traceability objective
templates/                Reusable documentation and future intake templates
records/                  Prompt/build logs, claims records, research validation, and decision records when present
README.md                 Repository overview and current status
VERSIONING.md             Versioning and traceability expectations
```

Key current Objective Five artifacts:

```text
docs/phase-one/objective-five/CURRENT_STATUS_RECONCILIATION.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_TRACKER.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_ARTIFACT_CONTRACTS.md
docs/phase-one/objective-five/VERSION_TAXONOMY.md
docs/phase-one/objective-five/RELEASE_CONTROL.md
docs/phase-one/objective-five/PROVENANCE_TRACEABILITY_SPEC.md
docs/phase-one/objective-five/RUN_PACKAGE_CONTRACT.md
docs/phase-one/objective-five/ARTIFACT_REGISTRY_SPEC.md
docs/phase-one/objective-five/CLAIM_TRACEABILITY_PROTOCOL.md
docs/phase-one/objective-five/SOURCE_PRECEDENCE_RELEASE_GATE.md
docs/phase-one/objective-five/REPRODUCIBILITY_CHECKLIST.md
docs/phase-one/objective-five/RELEASE_QA_CHECKLIST.md
templates/RELEASE_NOTE_TEMPLATE.md
templates/TRACEABILITY_RECORD_TEMPLATE.md
templates/RUN_MANIFEST_TEMPLATE.json
templates/CLAIM_EVIDENCE_LINK_TEMPLATE.md
records/prompt-build-log/2026-07-07-p1o5-t01.md
records/prompt-build-log/2026-07-08-p1o5-t02.md
records/prompt-build-log/2026-07-08-p1o5-t03.md
records/prompt-build-log/2026-07-08-p1o5-t04.md
records/prompt-build-log/2026-07-08-p1o5-t05.md
records/prompt-build-log/2026-07-08-p1o5-t06.md
records/prompt-build-log/2026-07-08-p1o5-t07.md
records/prompt-build-log/2026-07-08-p1o5-t08.md
records/prompt-build-log/2026-07-08-p1o5-t09.md
records/prompt-build-log/2026-07-08-p1o5-t10.md
```

Key earlier governing artifacts:

```text
AGENTS.md
VERSIONING.md
docs/objective-one/TECHNICAL_DESCRIPTION.md
docs/objective-one/USE_BOUNDARIES.md
docs/objective-one/SOURCE_PRECEDENCE.md
docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md
templates/CODEX_TASK_PACKET.md
records/PROMPT_BUILD_LOG.md
templates/PROMPT_LOG_ENTRY.md
```

## Recommended next task

After P1O5-T10 is reviewed and merged, proceed to:

```text
P1O5-T11 - Create Objective Five research and claims records
```

Recommended focus:

> Create Objective Five research validation and claims-check records using the sources actually relied on during P1O5-T03 through P1O5-T10 and the merged repo controls.

P1O5-T11 requires research and claims reconciliation across the Objective Five artifact set.

## Repo workflow

Use this loop for objective tasks:

```text
prompt
→ task framing
→ artifact contract
→ issue
→ branch
→ research if needed
→ artifact work
→ prompt log if needed
→ self-audit
→ pull request
→ merge
→ parent/current-status update
```

Every future public-facing output should be traceable to a commit, version, source metadata, run ID where relevant, timestamp, warning flags, limitations, source-precedence release status, reproducibility review, release QA decision, and claim-evidence links.

## Public site

The public website lives separately at `burnlensproject.org` and is backed by the `burnlens-site` repository.

This technical repository controls the scope, documentation, versioning, and future CV/GEOINT workflow artifacts. The public site should not make claims that are stronger than the artifacts in this repository support.
