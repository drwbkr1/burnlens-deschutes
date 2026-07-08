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

P1O5-T04 / #150 is active on branch `p1o5t04b`. It defines release and tag control using the expanded version taxonomy, GitHub release/tag semantics, and the existing repo workflow controls.

The current repository state is still documentation, workflow, template, traceability-control, and records work. No data ingestion, imagery download, AOI selection, source-data acquisition, label creation, mask creation, baseline generation, model training, inference, metric computation, raster/vector output generation, map publication, website demo integration, public performance claim, tag, or GitHub release has been authorized.

Current controlling handoff / current-status records:

```text
docs/phase-one/objective-five/CURRENT_STATUS_RECONCILIATION.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_TRACKER.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_ARTIFACT_CONTRACTS.md
docs/phase-one/objective-five/VERSION_TAXONOMY.md
docs/phase-one/objective-five/RELEASE_CONTROL.md
VERSIONING.md
templates/RELEASE_NOTE_TEMPLATE.md
```

Current parent/task issues:

```text
#144 - Phase 1 Objective Five parent
#150 - P1O5-T04 Define release and tag control
#155 - P1O5-T05 Create provenance traceability spec
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
templates/RELEASE_NOTE_TEMPLATE.md
records/prompt-build-log/2026-07-07-p1o5-t01.md
records/prompt-build-log/2026-07-08-p1o5-t02.md
records/prompt-build-log/2026-07-08-p1o5-t03.md
records/prompt-build-log/2026-07-08-p1o5-t04.md
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

After P1O5-T04 is reviewed and merged, proceed to:

```text
P1O5-T05 - Create provenance traceability spec
```

Recommended focus:

> Define how BurnLens source, activity, artifact, version, output, report, and claim records connect before future data/model/run/report releases can be considered.

P1O5-T05 should complete fresh research after branch creation because provenance traceability requires source-backed technical claims.

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

Every future public-facing output should be traceable to a commit, version, source metadata, run ID where relevant, timestamp, warning flags, and limitations.

## Public site

The public website lives separately at `burnlensproject.org` and is backed by the `burnlens-site` repository.

This technical repository controls the scope, documentation, versioning, and future CV/GEOINT workflow artifacts. The public site should not make claims that are stronger than the artifacts in this repository support.
