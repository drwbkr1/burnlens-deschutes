# Phase 1 / Objective Two Handoff

## Current objective

Objective Two defines the first BurnLens Deschutes computer vision task before Phase Two data, label, baseline, or model work begins.

The current focus is documentation and scope control only.

## Repo use pattern

For P1O2 onward, each task should continue to use this loop:

```text
GitHub issue
→ task branch
→ repo artifact
→ commit
→ pull request
→ merge
→ objective handoff update
```

## Completed tasks

| Task | Issue | Branch | PR | Artifact | Status |
|---|---:|---|---:|---|---|
| P1O2-T01 — Define CV task | #7 | `p1o2/t01-cv-task-definition` | #8 | `docs/phase-one/objective-two/CV_TASK_DEFINITION.md` | Complete |
| P1O2-T02 — Choose first segmentation target | #9 | `p1o2/t02-segmentation-target` | #10 | `docs/phase-one/objective-two/TARGET_CLASS_DECISION.md` | Complete |
| P1O2-T03 — Define positive, negative, and ambiguous classes | #11 | `p1o2/t03-class-definitions` | #12 | `docs/phase-one/objective-two/CLASS_DEFINITIONS.md` | Complete |
| P1O2-T04 — Define model output contract | #15 | `p1o2/t04-output-contract` | #16 | `docs/phase-one/objective-two/CV_OUTPUT_CONTRACT.md` | Complete |
| P1O2-T05 — Define imagery assumptions | #17 | `p1o2/t05-imagery-assumptions` | #18 | `docs/phase-one/objective-two/IMAGERY_ASSUMPTIONS.md` | Complete |
| P1O2-T06 — Define label assumptions | #19 | `p1o2/t06-label-assumptions` | #20 | `docs/phase-one/objective-two/LABEL_ASSUMPTIONS.md` | Complete |

## Current locked decisions

### CV task

BurnLens Deschutes' first computer vision task is:

**experimental binary semantic segmentation for wildfire-relevant screening.**

It is not wildfire prediction, evacuation routing, incident detection, fire spread modeling, emergency guidance, or official wildfire information.

### Primary target

The selected primary target is:

**active-fire / hotspot-informed binary fire mask.**

### Fallback target

The fallback target is:

**burn-scar binary mask**, only if Phase Two shows that active-fire / hotspot-informed labels are too weak, noisy, sparse, or misaligned for a defensible portfolio model.

### Class handling

Future label logic should preserve three pathways:

| Value | Class | Role |
|---:|---|---|
| 1 | Positive / fire-relevant | Positive class |
| 0 | Negative / background | Negative class |
| 255 or null | Unknown / exclude / review needed | Excluded or flagged for review |

Ambiguous pixels or regions should not be forced into positive or negative classes.

### Output contract

Future CV or baseline outputs must remain mask-first and traceable. Expected future levels are:

1. input tile or scene reference
2. binary mask
3. unknown/exclude mask when needed
4. optional confidence/probability raster
5. georeferenced raster
6. vector polygons in a later integration phase
7. exposure-style summary fields in a later integration phase
8. documented run package once inference exists

Model outputs, baseline outputs, and official/reference source outputs must remain separated.

### Imagery assumptions

Imagery remains a Phase Two feasibility question. Candidate categories include Sentinel-2 MSI, Landsat Collection 2 Level-2, NASA FIRMS / MODIS / VIIRS active-fire products, harmonized Landsat/Sentinel sources, and public sample imagery if needed for prototype scaffolding.

No final imagery source, AOI tile, band set, cloud mask, preprocessing method, or data-access path has been selected yet.

### Label assumptions

Future labels may be reference-derived, weak, manually reviewed, or baseline-derived. NASA FIRMS and other active-fire products may support reference, baseline, weak-label, sampling, or comparison logic, but must not be treated as pixel-perfect ground-truth segmentation masks.

Future labels must preserve ambiguity/exclusion handling and document source, source time, conversion method, quality flags, review status, and label schema version.

## Still in scope for Objective Two

Remaining Objective Two tasks should define:

- baseline comparison plan
- model family decision
- evaluation metrics plan
- failure modes
- CV-specific use boundaries
- final Objective Two handoff

## Next task

**P1O2-T07 — Define baseline comparison plan**

Recommended branch:

```text
p1o2/t07-baseline-comparison
```

Recommended artifact:

```text
docs/phase-one/objective-two/BASELINE_COMPARISON_PLAN.md
```

## Phase boundary

Do not start:

- data ingestion
- final AOI tile selection
- imagery download
- label creation
- dataset splitting
- baseline generation
- model training
- inference
- website demo integration

Those belong to later phases or later objectives.

## Persistent source-precedence rule

Official sources govern.

BurnLens outputs are experimental portfolio artifacts and must never override county, state, federal, fire-service, emergency-management, transportation, evacuation, hazard, or incident information.
