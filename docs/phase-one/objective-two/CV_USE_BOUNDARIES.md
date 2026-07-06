# P1O2-T11 — CV-Specific Use Boundaries

## Status

Phase 1 / Objective Two task artifact.

This document defines the use boundaries for future BurnLens Deschutes computer vision outputs. It does not ingest data, create labels, generate baselines, train a model, run inference, compute metrics, publish a map, or update the public website.

## Applies to

Current Objective Two decisions:

- CV task: experimental binary semantic segmentation for wildfire-relevant screening
- Primary target: active-fire / hotspot-informed binary fire mask
- Fallback target: burn-scar binary mask if active-fire label feasibility fails
- Output contract: mask-first, traceable output that can later become georeferenced raster, vector polygons, map overlay, exposure-style summary, and run package
- Baseline rule: future model outputs must be compared against simpler non-model baselines before any model-value claim
- Model family: U-Net-style binary semantic segmentation, documentation-only at this stage
- Evaluation primary metric: IoU / Jaccard, supported by Dice/F1, precision, recall, false-positive review, false-negative review, area difference, and qualitative review
- Known failure modes: imagery/source-quality, reference/label, baseline/model, geospatial-processing, evaluation/metric, and communication/use-boundary risks

## Boundary statement

BurnLens Deschutes CV outputs are experimental portfolio artifacts for demonstrating a transparent CV-to-GEOINT workflow.

They are not official wildfire information, emergency guidance, evacuation routing, tactical intelligence, incident command support, field-validated hazard assessment, or a substitute for county, state, federal, fire-service, emergency-management, transportation, or incident sources.

Official sources govern when information differs.

## Allowed uses

Future BurnLens CV outputs may be used for:

| Use | Allowed scope |
|---|---|
| Portfolio demonstration | Show how a prompt-built CV + GEOINT workflow can be scoped, versioned, evaluated, and communicated. |
| Methods explanation | Explain imagery-to-mask, mask-to-raster, raster-to-vector, and map-overlay concepts. |
| Reproducibility demonstration | Show manifests, run IDs, source metadata, model/baseline versions, and limitations. |
| Non-operational screening example | Demonstrate how a future analyst might inspect experimental outputs alongside official/reference layers. |
| Error analysis | Show false positives, false negatives, unknown/exclude handling, baseline comparison, and failure modes. |
| Case-study storytelling | Communicate project decisions, tradeoffs, limitations, and technical lessons. |

Allowed uses must remain framed as experimental and portfolio-oriented.

## Prohibited uses

Future BurnLens CV outputs must not be used for:

| Prohibited use | Reason |
|---|---|
| Emergency alerts | BurnLens is not an alerting authority or real-time warning system. |
| Evacuation decisions | Evacuation recommendations or orders must come from authorized officials. |
| Routing or road-closure guidance | BurnLens does not validate road conditions, closures, traffic, responder access, or safe routes. |
| Tactical fire decisions | BurnLens outputs are not suitable for tactical decision-making or local-scale fire conditions. |
| Incident command | BurnLens is not an incident command, dispatch, or operations-support system. |
| Property-level hazard determination | The CV task does not produce field-validated parcel or structure-level risk assessments. |
| Insurance, legal, regulatory, or compliance decisions | The outputs are experimental and not authoritative. |
| Public safety claims | The project may not claim it improves safety outcomes without appropriate validation and authority. |
| Official map replacement | BurnLens maps must not replace county, state, federal, fire-service, emergency-management, or incident maps. |
| Standalone public interpretation | Outputs should not be presented without context, caveats, source metadata, and limitations. |

## Source separation rule

BurnLens must keep these output types separate:

| Type | Meaning | Use boundary |
|---|---|---|
| Official/reference source | Source from an agency or authoritative public data provider. | Governs over BurnLens when information differs. |
| Reference-derived label | Label or weak label created from a source product. | Not pixel-perfect ground truth unless separately validated. |
| Baseline output | Non-model output such as all-background, reference display, reference buffer/raster, or threshold mask. | Comparison artifact only. |
| Model output | Future U-Net-style segmentation output. | Experimental model artifact only. |
| Map overlay | Visualization combining BurnLens outputs with context layers. | Must include visible caveats and source metadata. |

No report, model card, run manifest, website card, map, screenshot, or case-study text may blur these categories.

## Required visible warning language

Every future BurnLens CV map, screenshot, report, model card, public site card, or run package must include visible warning language.

Minimum warning:

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

Short warning for small UI surfaces:

```text
Experimental CV output — official sources govern.
```

Expanded warning for reports:

```text
BurnLens Deschutes outputs are experimental portfolio artifacts. They are intended to demonstrate a transparent CV + GEOINT workflow and may contain false positives, false negatives, timing mismatch, geospatial misalignment, label uncertainty, source-resolution limits, and other failure modes. Do not use for emergency decisions, evacuation routing, tactical operations, incident command, or official wildfire information.
```

## Claim boundaries

Allowed claims:

- BurnLens demonstrates a versioned CV-to-GEOINT workflow.
- BurnLens compares future model outputs against non-model baselines.
- BurnLens documents known limitations, failure modes, and source precedence.
- BurnLens produces experimental mask-like outputs for portfolio demonstration when future implementation exists.
- BurnLens shows how computer vision outputs can be packaged with run metadata and caveats.

Prohibited claims:

- BurnLens detects active fires accurately in real time.
- BurnLens is more accurate than official wildfire data.
- BurnLens predicts fire spread.
- BurnLens provides evacuation guidance.
- BurnLens identifies safe routes.
- BurnLens supports incident command decisions.
- BurnLens provides field-validated hazard assessments.
- BurnLens can be relied on for local conditions.
- BurnLens outputs are authoritative.

## Map and visualization boundaries

Future maps must:

- label BurnLens layers as experimental
- show source dates when available
- distinguish model, baseline, and official/reference layers
- include run ID or version metadata where possible
- include warning language on or near the visual output
- avoid symbology that implies official alert, evacuation, order, or incident status
- avoid color/label choices that could be confused with official warning systems
- link to limitations, source metadata, and official sources

Future maps must not:

- mimic official evacuation zones
- mimic official incident perimeter maps
- imply active emergency status
- imply public-safety instruction
- hide uncertainty or excluded areas
- present model positives as confirmed fire boundaries

## Model-card and run-report boundaries

Future model cards and run reports must include:

- model or baseline version
- dataset version
- label schema version
- AOI version
- source dates
- source commit
- run ID
- threshold and ignore/exclude policy
- baseline comparison
- metrics and qualitative review notes
- failure modes and warning flags
- use boundaries
- source-precedence statement

A model card is not complete unless these boundaries are visible and traceable.

## Website and portfolio boundaries

Public website copy may present BurnLens as:

- a portfolio case study
- a prompt-built CV + GEOINT prototype
- an experimental methods demonstration
- a transparent versioning and evaluation example

Public website copy must not present BurnLens as:

- a live wildfire monitor
- an emergency tool
- an official map
- an evacuation decision aid
- an agency partner product
- a field-validated hazard model
- a sponsored or authoritative operational system

## Emergency and official-source precedence

Any future public-facing BurnLens page should direct users to official sources for current wildfire, evacuation, road, air quality, and emergency information.

Minimum official-source statement:

```text
For current wildfire, evacuation, road, air-quality, and emergency information, use official county, state, federal, fire-service, emergency-management, transportation, air-quality, and incident sources.
```

## Data-use basis

This boundary is supported by source guidance already relevant to BurnLens:

- NASA FIRMS provides near-real-time satellite imagery, active fire/hotspots, and related products, but NASA notes that due to spatial resolution and other characteristics, using FIRMS data for tactical decision-making or local-scale conditions is not advised.
- NASA FIRMS states MODIS active-fire locations represent the center of a 1 km pixel and VIIRS active-fire locations represent the center of a 375 m pixel, supporting the rule that active-fire points should not be treated as exact segmentation boundaries.
- NWS emergency-message guidance identifies evacuation-immediate and fire-warning messages as warnings issued or recommended by authorized officials under law or ordinance, supporting BurnLens' exclusion from evacuation and fire-warning authority.

## Stop conditions

Do not mark any future BurnLens output as portfolio-ready if:

- the visible warning language is missing
- model, baseline, and official/reference layers are not separated
- official-source precedence is missing
- source dates are missing where needed
- run ID or version metadata is missing
- unknown/exclude handling is hidden
- failure modes are not disclosed
- a map could be mistaken for an official incident or evacuation product
- language implies emergency, tactical, routing, field-validated, or official use

## Phase boundary

This task does not authorize:

- data ingestion
- imagery download
- source selection
- label creation
- baseline generation
- model training
- inference
- metric computation
- public map publication
- website demo integration

Those belong to later phases or later objectives.

## Acceptance checklist

- [x] Allowed CV uses defined.
- [x] Prohibited CV uses defined.
- [x] Model, baseline, and official/reference source separation preserved.
- [x] Emergency, evacuation, routing, tactical, and incident-command exclusions preserved.
- [x] Required warning language defined.
- [x] Claim boundaries defined.
- [x] Map, model-card, run-report, and website boundaries defined.
- [x] Source precedence preserved.
- [x] Phase boundary preserved: no data, labels, model work, inference, metric computation, or site integration.
