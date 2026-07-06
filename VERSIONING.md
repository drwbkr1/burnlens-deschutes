# BurnLens Deschutes — Versioning Protocol

## Purpose

This file defines the first lightweight versioning protocol for BurnLens Deschutes. It is intentionally simple during Objective One and should become more specific as Phase 2 and Phase 3 create real datasets, baselines, models, labels, and runs.

## Core traceability rule

No public map, screenshot, summary, report, model output, or portfolio claim is portfolio-ready unless it can trace back to:

- GitHub commit
- app or repo version
- AOI version
- dataset version, when data exists
- model or baseline version, when a method exists
- label schema version, when labels exist
- run ID, when an output is generated
- source metadata and processing timestamp

## Version fields

| Component | Example | Status |
|---|---|---|
| Repo/scope version | `v0.0.1-objective-one` | Phase 1 |
| App version | `burnlens-app-v0.1.0` | future |
| Dataset version | `deschutes-aoi-dataset-v0.1.0` | future |
| AOI version | `deschutes-aoi01-v0.1` | future |
| Model version | `burnlens-cv-unet-v0.1.0` | future |
| Baseline version | `burnlens-baseline-v0.1.0` | future |
| Label schema version | `fire-mask-labels-v0.1` | future |
| Run ID | `BL-YYYY-MM-DD-deschutes-aoi01-m001-d001` | future |
| Report version | `run-report-v0.1.0` | future |

## Run ID pattern

```text
BL-YYYY-MM-DD-deschutes-aoiXX-mXXX-dXXX
```

Where:

- `BL` = BurnLens
- `YYYY-MM-DD` = run date
- `deschutes-aoiXX` = named AOI version family
- `mXXX` = model or baseline method identifier
- `dXXX` = dataset identifier

## Objective One baseline

The first proposed scope tag is:

```text
v0.0.1-objective-one
```

This tag should represent identity, scope, technical description, use boundaries, source precedence, transparency requirements, and templates only.

It should not imply that data ingestion, model training, final AOI selection, or operational wildfire functionality exists.
