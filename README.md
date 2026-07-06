# BurnLens Deschutes

BurnLens Deschutes is a computer vision + GEOINT portfolio project focused on experimental wildfire-related screening in Deschutes County, Oregon.

The project demonstrates a reproducible workflow for turning wildfire-relevant imagery, public geospatial layers, and experimental segmentation or baseline outputs into traceable map-ready artifacts.

## Current status

**Phase 1 / Objective Two is complete.**

Objective Two defined the first BurnLens Deschutes computer vision task tightly enough that later Phase One objectives and Phase Two data, label, baseline, and model work can proceed without ambiguity, scope creep, or operational overclaiming.

The current repository state is still documentation and scope-control focused. No data ingestion, imagery download, AOI tile selection, label creation, baseline generation, model training, inference, metric computation, model-card completion, website demo integration, or public performance claim has been authorized by Objective Two.

Current controlling handoff:

```text
docs/phase-one/objective-two/OBJECTIVE_TWO_FINAL_HANDOFF.md
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
  phase-one/
    objective-two/       Completed Objective Two CV task-definition docs and final handoff
templates/               Reusable documentation templates
records/                 Project logs, claims register, research validation, and decision records when present
README.md                Repository overview and current status
VERSIONING.md            Versioning and traceability expectations
```

Key Objective Two artifacts:

```text
docs/phase-one/objective-two/CV_TASK_DEFINITION.md
docs/phase-one/objective-two/TARGET_CLASS_DECISION.md
docs/phase-one/objective-two/CLASS_DEFINITIONS.md
docs/phase-one/objective-two/CV_OUTPUT_CONTRACT.md
docs/phase-one/objective-two/IMAGERY_ASSUMPTIONS.md
docs/phase-one/objective-two/LABEL_ASSUMPTIONS.md
docs/phase-one/objective-two/BASELINE_COMPARISON_PLAN.md
docs/phase-one/objective-two/MODEL_FAMILY_DECISION.md
docs/phase-one/objective-two/EVALUATION_METRICS_PLAN.md
docs/phase-one/objective-two/FAILURE_MODES.md
docs/phase-one/objective-two/CV_USE_BOUNDARIES.md
docs/phase-one/objective-two/OBJECTIVE_TWO_FINAL_HANDOFF.md
```

## Recommended next objective

The next objective should begin turning Objective Two's scope decisions into data/source feasibility and research records while avoiding premature implementation.

Recommended next-objective focus:

> Determine which imagery, reference products, AOI constraints, and data-access paths are feasible for the locked binary segmentation task.

Recommended early tasks:

1. Create the next objective tracker issue.
2. Define candidate data/source feasibility criteria.
3. Inventory source access paths for Sentinel-2, Landsat, FIRMS, and allowed public sample imagery.
4. Define AOI tile-selection criteria without downloading imagery unless the next objective explicitly authorizes source testing.
5. Update research validation logs and the claims register.
6. Preserve Objective Two boundaries in every future data decision.

## Repo workflow

Use this loop for objective tasks:

```text
GitHub issue
→ task branch
→ repo artifact
→ commit
→ pull request
→ merge
→ objective handoff update
```

Every future public-facing output should be traceable to a commit, version, source metadata, run ID where relevant, timestamp, warning flags, and limitations.

## Public site

The public website lives separately at `burnlensproject.org` and is backed by the `burnlens-site` repository.

This technical repository controls the scope, documentation, versioning, and future CV/GEOINT workflow artifacts. The public site should not make claims that are stronger than the artifacts in this repository support.
