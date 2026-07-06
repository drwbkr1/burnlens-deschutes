# BurnLens Deschutes — Model Card Template

Use this template for every BurnLens Deschutes model version.

Do not publish a model output without a completed model card or an explicit note that the output is baseline-only and not model-generated.

## Model overview

**Model name:**  
**Model version:**  
**Short description:**  
**Model type:**  
**Architecture:**  
**Task:**  
**Output type:**  
**Project:** BurnLens Deschutes  
**Status:** Experimental / draft / evaluated / archived

## Intended use

Describe what the model is intended to support inside BurnLens Deschutes.

Example: experimental segmentation masks from wildfire-relevant imagery for portfolio demonstration and planning-style screening outputs.

## Unsupported uses

This model must not be used for emergency response, evacuation orders or routing, incident command, official fire perimeter generation, official hazard classification, parcel enforcement, utility operations, insurance/lending/regulatory decisions, field-validation claims, or agency-endorsement claims.

## Training data

**Dataset version:**  
**Source imagery:**  
**Reference or label sources:**  
**Geographic scope:**  
**Time period:**  
**Number of images/tiles:**  
**Label schema version:**  
**Preprocessing version:**  
**Known data gaps:**

## Evaluation data

**Evaluation dataset version:**  
**Train/validation/test split logic:**  
**Held-out geography or events:**  
**Number of evaluated samples/tiles:**  
**Known degraded conditions:**

## Metrics

Report only metrics that were actually calculated.

| Metric | Value | Notes |
|---|---:|---|
| Loss |  |  |
| IoU / Jaccard |  |  |
| Dice / F1 |  |  |
| Precision |  |  |
| Recall |  |  |
| False positive notes |  |  |
| False negative notes |  |  |

## Baseline comparison

**Baseline version:**  
**Baseline method:**  
**Comparison result:**  
**Where the model improved:**  
**Where the model failed or added risk:**

## Known limitations and failure modes

Document cloud, smoke, snow, haze, shadow, sensor limits, coarse resolution, label uncertainty, temporal mismatch, false positives, false negatives, and geographic limits outside the selected AOI.

| Failure mode | Description | Mitigation |
|---|---|---|
|  |  |  |

## Version and provenance

**Model version:**  
**Dataset version:**  
**Label schema version:**  
**Training script version:**  
**GitHub commit:**  
**Training date:**  
**Run ID examples:**  
**Weights filename:**  
**Config filename:**

## Release decision

**Ready for public portfolio display?** Yes / No / With caveats  
**Required caveats:**  
**Next evaluation step:**

## Required note

This model is experimental. It is not field verified, not official wildfire information, and not emergency guidance. Official sources govern when they differ from model output.
