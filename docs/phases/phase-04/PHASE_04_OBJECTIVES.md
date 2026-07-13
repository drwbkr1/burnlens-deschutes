# BurnLens Deschutes — Phase Four Objectives

## Document role

This document expands the Phase Four objective summarized in `docs/roadmap/BURNLENS_BUILD_ROADMAP.md`.

It defines the integrated product and run evidence required for Phase Five. It does not authorize retraining, new data, or public release.

## Phase name

**Inference Pipeline, Geospatial Productization, Interactive Tool Integration, and Run Versioning**

## Canonical objective summary

Convert the accepted model or baseline into a reproducible inference-to-GEOINT workflow that preserves georeferencing, creates valid raster/vector artifacts, performs deterministic overlay analysis, presents an accessible evidence interface, and packages every execution as an immutable run.

## Current status

**Proposed — blocked.**

Phase Four depends on an accepted Phase Three model package or an explicitly approved Phase Two baseline-only path.

## Phase purpose

Phase Four is where BurnLens becomes an inspectable tool rather than a dataset or model-development exercise. It runs controlled inference, preserves spatial lineage, creates georeferenced rasters and vectors, combines them with bounded context layers, generates deterministic descriptive summaries, displays one accepted run in an interactive interface, and packages every execution with versions, checksums, warnings, and explicit run state.

The phase must answer:

> Can BurnLens convert one accepted analytical output into a transparent planning-style screening package without obscuring uncertainty or source precedence?

## Recommended architecture

```text
burnlens-deschutes
    analytical pipeline
    accepted source package
    → preprocessing
    → model or baseline inference
    → georeferenced outputs
    → overlay analysis
    → summary generation
    → immutable run package

    repository-owned application
    accepted static run package
    → web-ready raster/vector assets
    → interactive map
    → textual summary
    → methods, metadata, and warnings
```

The analytical system, application, website, and case study are owned by this repository. The interface presents accepted versioned artifacts; it must not silently perform or alter analytical processing.

## Required outcomes

Phase Four must produce:

1. one approved integration architecture and interface contract;
2. one configuration-driven model or baseline inference runner;
3. one immutable run ID per execution;
4. explicit accepted, degraded, no-detection, fallback, failed, and withheld states;
5. georeferenced probability, binary, and exclusion rasters where applicable;
6. validated vector representations with post-processing lineage;
7. deterministic road, structure, facility, AOI, and reference-layer calculations;
8. structured descriptive summary output;
9. an accessible interactive evidence interface and non-map textual equivalent;
10. visible source dates, versions, warnings, limitations, and precedence;
11. complete run manifest, checksums, and artifact inventory;
12. one reproducible end-to-end integrated run package and Phase Five handoff.

## Objective set

### Objective One — Authorize the integration architecture

**Purpose:** Lock the accepted analytical package, in-repository component responsibilities, input/output contracts, run schema, application consumption contract, failure states, and successor gate.

**Acceptance gate:** Work can proceed without ambiguity about which model or baseline is accepted, which in-repository component owns each artifact, how runs are identified, and what Phase Four cannot change.

### Objective Two — Build inference and run orchestration

**Purpose:** Apply the exact accepted model or baseline to approved imagery and record every material input, configuration, warning, and status.

**Required result:** Weight and config verification; band/order/type checks; exclusion preservation; deterministic tiling and stitching; frozen threshold; georeferencing; unique run ID; safe input-contract failures.

**Acceptance gate:** Equivalent approved inputs regenerate equivalent inference artifacts within documented tolerances, and incompatible inputs fail before misleading output is produced.

### Objective Three — Create valid geospatial artifacts

**Purpose:** Transform array output into standards-aligned raster and vector products with explicit CRS, bounds, nodata, units, lineage, and post-processing history.

**Required result:** Canonical GeoTIFF or COG where justified; probability/binary/exclusion products; polygonization; geometry validation; deliberate web reprojection; GeoJSON or PMTiles only when scale justifies it.

**Acceptance gate:** Independent validation confirms CRS, bounds, alignment, nodata, geometry validity, source linkage, and distinction between raw prediction and post-processed representation.

### Objective Four — Integrate context and generate summaries

**Purpose:** Translate spatial relationships into concise, deterministic planning-style observations without making operational recommendations.

**Required result:** Selected roads, structures, facilities, planning boundaries, official/reference layers, prediction, and uncertainty layers; reproducible area, length, count, distance, overlap, and exclusion calculations; descriptive language contract.

**Acceptance gate:** Every observation can be regenerated from versioned inputs, and no wording implies safety, evacuation, routing, spread prediction, or decision authority.

### Objective Five — Build the interactive evidence interface

**Purpose:** Let a user identify the current run, distinguish evidence classes, compare layers, read the summary and warnings, and inspect provenance.

**Required result:** Layer and opacity controls; legend; model/baseline/reference separation; run metadata; warning panel; methods links; loading, degraded, no-detection, fallback, failed, and missing-asset states; keyboard and non-color communication; textual summary.

**Acceptance gate:** A user can understand the run and its limitations without relying solely on the map or hover interactions.

### Objective Six — Package, version, reproduce, and hand off

**Purpose:** Freeze one complete integrated run candidate for reliability hardening.

**Required result:** Run manifest, status, source inventory, configs, raster/vector assets, summary, report, map config, quick-look, checksums, logs, app candidate version, and clean end-to-end reproduction evidence.

**Acceptance gate:** Phase Five receives one internally consistent run package and interface candidate, or the project records a remediation or stop outcome.

## Run-state taxonomy

| State | Meaning |
|---|---|
| `accepted-model` | Model inference completed and passed run-level checks. |
| `accepted-baseline` | Baseline is the intentionally approved analytical path. |
| `degraded` | Output exists, but source or processing warnings limit interpretation. |
| `no-detection` | Processing succeeded and produced no retained positive output; this does not imply no fire or no risk. |
| `fallback-baseline` | The model path failed a use gate and the documented baseline was used. |
| `failed` | No valid run package was produced. |
| `withheld` | Artifacts exist but must not be displayed or interpreted due to a release-blocking condition. |

## Completion evidence

Phase Four is complete only when:

- one accepted analytical package drives the run;
- each run ID is immutable and never reused;
- all artifacts agree with the run manifest and checksums;
- geospatial products align with source imagery and AOI;
- measurements use declared CRS, units, geometry operations, thresholds, and rounding;
- the interface displays the same run and versions as the analytical package;
- official/reference, label, baseline, model, post-processing, context, and interpretation layers remain distinguishable;
- degraded, no-detection, fallback, failed, and withheld behavior is visible and tested;
- the end-to-end run can be reproduced within documented tolerances;
- the Phase Five handoff is reviewed and merged.

## Dependencies

- accepted model package or approved baseline-only path;
- exact inference input/output and exclusion contracts;
- approved context-layer records and terms;
- current geospatial, versioning, run-package, claims, and source-precedence controls;
- repository-owned application structure and exact commit/version linkage.

## Non-goals

Phase Four does not:

- retrain, retune, recalibrate, or silently replace the accepted model;
- change the dataset, labels, split, AOI, or target;
- add live wildfire monitoring or emergency feeds;
- perform user-uploaded inference;
- recommend evacuation routes, closures, tactical actions, or property-level outcomes;
- publish the final case study or production release;
- blend official and BurnLens outputs into one unlabeled fire layer.

## Fixed boundaries

- Static accepted artifacts separate analytical processing from presentation.
- Model, baseline, reference, context, post-processing, and interpretation remain distinct.
- Run IDs are immutable.
- No-detection never means safe or no fire.
- Descriptive summaries must be deterministic and non-operational.
- Official sources govern.
- The interface must offer a meaningful textual alternative to the map.

## Known risks and assumptions

- Tiling can create seams and edge artifacts.
- CRS, affine transform, nodata, or reprojection errors can materially displace outputs.
- Raster-to-vector post-processing can distort raw predictions.
- Large assets may degrade browser performance and tempt uncontrolled simplification.
- Map symbology can imply false authority or confidence.
- Missing assets can appear as empty or safe conditions unless failure states are explicit.
- Deployments can drift from the analytical commit unless version linkage is enforced.

## Authority delegated to Codex

After the predecessor evidence gate and within issue-backed contracts, Codex may:

- implement deterministic inference, tiling, stitching, raster, vector, and summary pipelines;
- choose the simplest approved web artifact format that meets performance needs;
- select bounded post-processing parameters and document them;
- implement accessible interface behavior and failure states;
- create immutable run packages and app candidates;
- recommend model, caveated, baseline-first, remediation, or stop outcomes.

Codex must not silently retrain, change the frozen threshold or calibration, add unevaluated layers, reinterpret descriptive summaries as decisions, or publish an unverified run.

## Changes requiring owner approval

The stop conditions in `docs/governance/BURNLENS_EXECUTION_GOAL.md` control. Codex may build, version, deploy, and verify the repository-owned application and may revise bounded integration details through issue-backed evidence.

Owner approval is required before changing the core task, phase outcome, or use boundaries; crossing a no-go boundary; proceeding with unresolved licensing/terms; spending money or adding a paid service/secret; changing access, ownership, or public-sharing status; taking an irreversible action; implying official/operational/emergency-ready/field-validated/endorsed status; or shipping something unverifiable. Restricted source-derived assets must not be exposed while terms remain unresolved.

## Expected handoff to Phase Five

The handoff must provide:

- accepted run ID and status;
- analytical and application commits;
- app candidate, model/baseline, dataset, label, and AOI versions;
- complete manifest and checksums;
- raster/vector validation results;
- deterministic summary specification and outputs;
- interface routes, assets, and failure states;
- known defects, warnings, size/performance concerns, and inaccessible evidence;
- reproduction steps and tolerances;
- explicit accept, caveated, baseline-first, remediate, or stop outcome.

## Source basis

This document consolidates the supplied Phase Four objective plan and current BurnLens run-package, provenance, source-precedence, versioning, and interface-boundary posture. Detailed implementation tasks remain issue-generated and evidence-responsive.
