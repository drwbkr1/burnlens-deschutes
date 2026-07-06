# P1O2-T02 — First Segmentation Target Decision

## Status

Phase 1 / Objective Two task artifact.

This document chooses the first BurnLens Deschutes segmentation target for later data, label, baseline, and model work. It does not download imagery, ingest fire products, create labels, train a model, or run inference.

## Decision

**Primary target:** active-fire / hotspot-informed binary fire mask.

**Fallback target:** burn-scar binary mask, only if active-fire label feasibility is too weak for a defensible portfolio model.

## Short rationale

BurnLens Deschutes should start with an active-fire / hotspot-informed binary mask because it best matches the existing project spine:

```text
imagery → preprocessing → segmentation or baseline mask → raster output → vector polygons → map overlay → exposure-style summary → documented run package
```

This target keeps the project close to the original active-fire semantic-segmentation workstream while still allowing a baseline-first approach using public active-fire products. The target is narrow enough for a one-person portfolio project and broad enough to support later map-ready GEOINT outputs.

## Target options reviewed

| Candidate target | Strengths | Risks | Decision |
|---|---|---|---|
| Active-fire binary mask | Closest to the original technical spine; pairs naturally with active-fire reference products; supports current-fire-context storytelling. | Active fire can be spatially small, time-sensitive, and affected by satellite timing, resolution, smoke, clouds, and geolocation uncertainty. | Keep as primary, but use conservative language. |
| Hotspot-informed fire mask | Practical for a baseline-first workflow; public hotspot products can guide reference or weak-label logic. | Hotspot points are not the same thing as exact pixel masks or ground truth. Buffers/rasterization must be documented as approximations. | Use as the primary target framing: active-fire / hotspot-informed. |
| Burn-scar binary mask | More stable after an event; easier to compare visually in some imagery. | Shifts project away from current fire context and toward post-fire mapping. | Keep as fallback only. |
| Wildfire-context mask | Flexible and easy to explain at a high level. | Too vague; risks becoming an undefined AI wildfire layer. | Reject for Objective Two. |

## Research basis

NASA FIRMS uses MODIS and VIIRS satellite observations to detect active fires and thermal anomalies and deliver near-real-time information. FIRMS also notes that near-real-time archive data is replaced with standard MODIS and VIIRS active-fire products when available and advises scientific users to use standard science-quality data when available.

Sentinel-2 MSI is a plausible imagery candidate for later feasibility review because it samples 13 spectral bands across 10 m, 20 m, and 60 m spatial resolutions. This does not mean Sentinel-2 is automatically the selected Phase Two data source; it only supports keeping multispectral wildfire-relevant imagery in the candidate stack.

Research references:

- NASA FIRMS active fire data: https://firms.modaps.eosdis.nasa.gov/active_fire/
- NASA Earthdata Sentinel-2 MSI: https://www.earthdata.nasa.gov/data/instruments/sentinel-2-msi

## Definition of the selected target

The selected target is a **binary mask representing active-fire or hotspot-informed fire-relevant areas** in a future image tile or raster product.

The positive class should represent pixels or regions that are reasonably associated with active-fire or active-fire reference evidence under a documented label rule.

The negative/background class should represent pixels or regions not associated with that fire-relevant class under the same rule.

Ambiguous areas should not be forced into either class. Phase Two must preserve an `unknown`, `exclude`, or `review_needed` pathway for ambiguous labeling cases.

## Important caveat

Active-fire reference products are not exact segmentation masks. They may support baseline comparison, weak-label generation, candidate sampling, or reference review, but they must not be silently treated as perfect ground truth.

## Why burn scar is the fallback

If Phase Two shows that active-fire / hotspot-informed labels are too sparse, noisy, mismatched, or hard to align with imagery, the fallback target is burn-scar binary segmentation.

A fallback decision must be documented before any fallback data build begins. The fallback may not expand the project into burn severity, recovery analysis, or multi-class post-fire mapping without a separate scope update.

## Portfolio claim allowed

Allowed:

> BurnLens Deschutes explores whether a binary segmentation workflow can turn wildfire-relevant imagery and public reference products into traceable, map-ready experimental outputs.

Not allowed:

> BurnLens detects active wildfires for emergency use.

> BurnLens provides authoritative fire perimeters.

> BurnLens improves evacuation decisions.

> BurnLens replaces official wildfire or emergency-management sources.

## Acceptance checklist

- [x] Primary target selected: active-fire / hotspot-informed binary fire mask.
- [x] Fallback target selected: burn-scar binary mask if active-fire labels are not feasible.
- [x] Rejected vague wildfire-context mask as too broad.
- [x] Research basis recorded.
- [x] Source-precedence and non-operational boundaries preserved.
- [x] Phase boundary preserved: no download, ingestion, labeling, training, inference, or demo integration.
