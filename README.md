# BurnLens Deschutes

BurnLens Deschutes is a computer vision + GEOINT portfolio project focused on experimental wildfire-related screening in Deschutes County, Oregon.

The project demonstrates a reproducible workflow for turning wildfire-relevant imagery, public geospatial layers, and experimental segmentation or baseline outputs into traceable map-ready artifacts.

## Current status

**Phase One / Objective Six is the active repository-control workstream.**

Objective Five is complete and remains the control baseline for versioning, provenance, release control, future run-package planning, artifact registry planning, source-precedence gates, reproducibility QA, research validation, and claim traceability.

Objective Six defines how prompt-assisted repository work is issue-backed, branch-scoped, prompt-logged, test-aware, reviewed by a human, merged, and handed off without creating duplicate sources of truth.

Current Objective Six status:

```text
#195 - Phase 1 Objective Six parent — open
P1O6-T01 / #196 - merged through PR #197
P1O6-T02 / #200 - merged through PR #201
P1O6-T03 - next planned task; task issue and branch not yet created
```

Current Objective Six records:

```text
docs/phase-one/objective-six/OBJECTIVE_SIX_TRACKER.md
docs/phase-one/objective-six/OBJECTIVE_SIX_ARTIFACT_CONTRACTS.md
docs/phase-one/objective-six/PROMPT_BUILT_DEVELOPMENT_PROTOCOL.md
```

The proposed Objective Five baseline tag remains:

```text
v0.0.5-objective-five-traceability
```

The proposed tag has not been created. No GitHub Release has been published.

## Prompt-built development architecture

The controlling relationship is:

```text
full workflow reference: docs/workflows/PROMPT_TO_REPO_SOP.md
canonical task capsule: templates/CODEX_TASK_PACKET.md
root prompt-log navigation: PROMPT_LOG.md (non-canonical)
canonical prompt-log protocol/index: records/PROMPT_BUILD_LOG.md
canonical prompt-log entry template: templates/PROMPT_LOG_ENTRY.md
current Objective Six architecture: docs/phase-one/objective-six/PROMPT_BUILT_DEVELOPMENT_PROTOCOL.md
```

Root `PROMPT_LOG.md` is a concise navigation and compatibility entry point only. It does not replace the canonical protocol, entry index, or detailed entry template.

Future `templates/CODEX_TASK_TEMPLATE.md` remains a planned compatibility and discoverability entry point. It does not exist yet and must not become a duplicate task schema.

Human review is distinct from AI-assisted review. AI may draft, test, inspect, and recommend changes, but a human must inspect the proposed diff and record the merge decision.

Every task must report named tests or checks and actual results, or state a task-specific reason that a check does not apply.

## Objective Five governing records

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
docs/phase-one/objective-five/OBJECTIVE_FIVE_RESEARCH_VALIDATION_LOG.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_CLAIMS_CHECK.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_CLOSEOUT.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_HANDOFF.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_RELEASE_NOTE.md
VERSIONING.md
templates/RELEASE_NOTE_TEMPLATE.md
templates/TRACEABILITY_RECORD_TEMPLATE.md
templates/RUN_MANIFEST_TEMPLATE.json
templates/CLAIM_EVIDENCE_LINK_TEMPLATE.md
records/PROMPT_BUILD_LOG.md
```

## Current work boundary

BurnLens remains an experimental, non-operational portfolio project. Official sources govern. Future public-facing output must follow `docs/objective-one/USE_BOUNDARIES.md`, `docs/objective-one/SOURCE_PRECEDENCE.md`, and Objective Five release, source-precedence, reproducibility, QA, and claim-traceability controls.

Phase Two data work has not begun. No AOI, source-data, label, model, run, map, public-demo, completed claim, tag, or GitHub Release artifact has been created by Objective Six.

Objective Six does not authorize repository settings, branch protection, rulesets, Actions, labels, milestones, Projects, later operational templates, implementation work, or public-output work unless a later task explicitly allows the named change.

## Locked computer vision task

BurnLens Deschutes' first computer vision task is experimental binary semantic segmentation for wildfire-relevant screening.

The primary target is active-fire / hotspot-informed binary fire mask. The fallback target is burn-scar binary mask. The fallback may be used only if later feasibility work shows the primary target is not defensible for the portfolio model. Changing to the fallback requires a documented decision update.

## Core workflow

```text
imagery → preprocessing → segmentation or baseline mask → raster output → vector polygons → map overlay → exposure-style summary → documented run package
```

This chain is a future workflow contract. It does not mean those stages have already been implemented.

## Source separation rule

Future BurnLens artifacts must keep these categories separate:

- official/reference sources
- reference-derived labels
- baseline outputs
- model outputs
- map overlays
- portfolio interpretations

## Recommended next task

Proceed to:

```text
P1O6-T03 — Create the Codex task template entry point
```

P1O6-T03 must preserve `templates/CODEX_TASK_PACKET.md` as the canonical executable task capsule and may create `templates/CODEX_TASK_TEMPLATE.md` only as a concise compatibility and discoverability wrapper.

## Public site

The public website lives separately at `burnlensproject.org` and is backed by the `burnlens-site` repository.

This technical repository controls the scope, documentation, versioning, and future CV/GEOINT workflow artifacts. The public site should not make claims that are stronger than the artifacts in this repository support.
