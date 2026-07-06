# P1O2-T01 — Computer Vision Task Definition

## Status

Phase 1 / Objective Two task artifact.

This document defines the first BurnLens Deschutes computer vision task. It does not start data ingestion, label creation, model training, inference, or demo integration.

## Task name

**Experimental binary semantic segmentation for wildfire-relevant screening.**

BurnLens Deschutes will frame its first computer vision workstream as a segmentation task, not as wildfire prediction, evacuation routing, fire spread modeling, incident detection, or emergency decision support.

## Task statement

BurnLens Deschutes will use wildfire-relevant imagery and public reference information to produce a mask-like output that can later be converted into geospatial artifacts for portfolio demonstration:

```text
imagery → preprocessing → segmentation or baseline mask → raster output → vector polygons → map overlay → exposure-style summary → documented run package
```

The first task is to define and eventually test whether a binary segmentation workflow can create a traceable mask that supports planning-style visualization and exposure-summary artifacts.

## Why segmentation is the right first CV task

BurnLens needs map-ready spatial outputs. Image classification would only answer whether an image tile contains a class. Object detection would draw boxes. Semantic segmentation is a better first fit because it assigns labels at the pixel or region level, which can later become rasters, polygons, overlays, and run reports.

PyTorch / Torchvision lists pixelwise semantic segmentation as a standard computer vision task category alongside classification, object detection, and related tasks. U-Net is also a defensible starting family because the original U-Net paper describes a contracting path for context and an expanding path for precise localization, designed for image segmentation with efficient use of annotated samples.

Research references:

- Torchvision models documentation: https://docs.pytorch.org/vision/main/models.html
- U-Net original paper: https://arxiv.org/abs/1505.04597

## Initial task boundary

### In scope

- Binary semantic segmentation.
- One positive class and one negative/background class.
- Wildfire-relevant imagery prepared in a later phase.
- Baseline or model-generated mask outputs.
- Future conversion of masks into geospatial rasters, polygons, overlays, and exposure-style summaries.
- Transparent documentation of source metadata, task limits, and uncertainty.

### Out of scope

- Operational wildfire detection.
- Fire spread prediction.
- Evacuation routing.
- Evacuation orders or emergency guidance.
- Incident command, suppression, alerting, or dispatch support.
- Parcel-level enforcement or regulatory decision support.
- Field validation or agency endorsement claims.
- Smoke detection, burn severity, multi-class fire behavior modeling, or utility-grade operational workflows.

## First model family assumption

The default future model family is a **U-Net-style binary semantic segmentation model**.

This is a model-family decision for planning purposes only. It does not commit the project to a trained model yet. Phase Two must still determine data feasibility, label feasibility, and baseline comparison strategy before model training can begin.

## Expected future output contract

The eventual CV output should be compatible with this chain:

```text
input image tile
→ predicted binary mask or baseline mask
→ georeferenced raster output
→ vector polygons in a later integration phase
→ map overlay
→ exposure-style summary
→ documented run package
```

Future outputs must be traceable to:

- Git commit
- repo/app version
- AOI version
- dataset version, where relevant
- model or baseline version, where relevant
- label schema, where relevant
- run ID
- source metadata
- processing timestamp

## Use boundary

BurnLens segmentation outputs are experimental portfolio artifacts. They are not official wildfire information, not emergency guidance, not evacuation routing, not incident command products, not field-validated hazard assessments, and not agency-endorsed outputs.

Official county, state, federal, fire-service, emergency-management, transportation, evacuation, and incident information governs when information differs.

## Acceptance checklist

- [x] Task is defined as binary semantic segmentation.
- [x] Task is connected to the locked BurnLens workflow chain.
- [x] U-Net-style segmentation is identified as the default future model family.
- [x] Operational and emergency-use claims are excluded.
- [x] Research basis is recorded.
- [x] Phase boundary is preserved: no ingestion, labeling, training, inference, or demo integration in this task.
