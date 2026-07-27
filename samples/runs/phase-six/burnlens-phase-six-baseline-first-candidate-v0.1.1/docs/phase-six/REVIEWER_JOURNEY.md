# BurnLens reviewer journey

BurnLens is an experimental CV-to-GEOINT portfolio project for technical and
technical-adjacent reviewers. It demonstrates one reproducible route from
versioned wildfire-related evidence through a bounded segmentation experiment
to georeferenced, inspectable outputs.

The strongest result is not the trained model. The bounded U-Net is valid,
reproducible, and rejected because it predicts every selected test core as
burned and loses to the RBR baseline. BurnLens then carries the accepted RBR
route into one Ward Creek GEOINT demonstration while keeping the rejected model
visible only as a diagnostic.

> Experimental BurnLens CV output. Not official wildfire information. Not
> emergency guidance. Not evacuation, routing, tactical, or incident-command
> support. Official sources govern.

## Choose a path

### 30 seconds

1. [Open the exact Ward Creek interface](../../samples/runs/phase-four/burnlens-geoint-evidence-interface-v0.1.0/PHASE-FOUR-EVIDENCE-INTERFACE-2026-001.html).
2. Compare WCP-001 with WCP-002. WCP-002 keeps 66.76 ha of accepted-RBR
   false-positive-risk evidence visible.
3. Remember the decision: RBR is accepted for this bounded demonstration. The
   U-Net is rejected and did not outperform RBR.

### 2 minutes

1. Use the [Ward Creek interface](../../samples/runs/phase-four/burnlens-geoint-evidence-interface-v0.1.0/PHASE-FOUR-EVIDENCE-INTERFACE-2026-001.html).
   Keep **Accepted RBR** visible, focus WCP-001 and WCP-002, and turn on
   **Rejected U-Net** only to inspect the diagnostic.
2. Open the [model decision](../../samples/model-packages/burnlens-unet-binary-v0.1.0/PHASE-THREE-MODEL-DECISION.html).
   The U-Net scores macro Dice `0.29874213836477986` against RBR `1.0` on 89
   selected prototype test cores.
3. Open the [Phase Five reliability candidate](../../samples/runs/phase-five/burnlens-phase-five-baseline-first-candidate-v0.1.1/index.html).
   Review failure/recovery, reconstruction, rollback, and the two visible
   medium [known issues](../../samples/runs/phase-five/burnlens-phase-five-baseline-first-candidate-v0.1.1/KNOWN-ISSUES.md).
4. Read [what the evidence cannot establish](#limitations).

### 5 minutes

1. Read the [immutable run report](../../samples/runs/phase-four/burnlens-ward-creek-rbr-run-v0.1.0/REPORT.md)
   and [warnings](../../samples/runs/phase-four/burnlens-ward-creek-rbr-run-v0.1.0/WARNINGS.md).
2. Inspect the [accepted baseline evaluation](../../samples/baselines/burnlens-baseline-v0.1.0/BASELINE-EVALUATION-2026-001.html)
   and the [rejected-model card](../../samples/model-packages/burnlens-unet-binary-v0.1.0/MODEL-CARD.md).
3. Review the [immutable Phase Four package](../../samples/runs/phase-four/burnlens-ward-creek-rbr-run-v0.1.0/README.md)
   and [Phase Five candidate](../../samples/runs/phase-five/burnlens-phase-five-baseline-first-candidate-v0.1.1/README.md).
4. Use the [replay commands](#reproduce-and-validate) and [trace table](#trace)
   to check the result.
5. Continue into the [living case study](../case-study/BURNLENS_CASE_STUDY.md)
   only if you want the full decision history.

## The evidence chain

1. **Official and optical evidence.** Sentinel-2 supplies controlled optical
   inputs. BAER, MTBS, RAVG, NIFC, and TNM retain bounded, program-specific
   roles. None is silently converted into independent pixel truth.
2. **Owner-confirmed prototype regions.** Burned and affirmative-background
   candidates receive yes/no/uncertain owner review. A yes is necessary but
   never sufficient; source, quality, uncertainty, reproducibility, and
   leakage gates still govern.
3. **Dataset and split.** `burnlens-dataset-v0.1.0` contains twelve 64-by-64
   native-grid patches across six complete events. The 2/2/2 whole-event split
   is locked before patch generation. Unknown rings stay outside loss and
   metrics.
4. **Baseline and model.** The preregistered RBR threshold is selected on
   validation events. One 117,473-parameter CPU U-Net is trained and evaluated
   once under a separate test opening.
5. **Decision.** The U-Net predicts all 89 selected test cores as burned. It is
   reproducible but rejected. RBR remains the analytical method.
6. **GEOINT route.** Exact Ward Creek RBR output becomes native rasters,
   vectors, bounded context, deterministic observations, a self-contained
   interface, and a 66-file immutable run package.
7. **Reliability.** Phase Five proves fail-closed recovery, offline rendered
   behavior, deterministic packaging, clean reconstruction, rollback, and
   visible known issues without changing the analysis.

## Architecture and source precedence

```text
official metadata and controlled source bytes
  -> source, terms, custody, quality, and uncertainty gates
  -> owner-confirmed prototype regions and explicit unknown rings
  -> whole-event split -> versioned patches -> independent dataset QA
  -> preregistered RBR baseline + bounded U-Net experiment
  -> reject U-Net / retain RBR
  -> georeferenced RBR raster and vectors
  -> bounded official context and deterministic observations
  -> offline evidence interface and immutable run package
  -> failure, assurance, reconstruction, rollback, and known-issue QA
```

Official source products govern over every BurnLens derivative. MTBS is
analyst-interpreted reference context, not an operational incident perimeter.
TNM roads are not access, closure, routing, or safety authority. Context layers
are neither labels nor model inputs in the Phase Four run.

## Method and evaluation

The accepted baseline is `burnlens-baseline-v0.1.0`, an RBR threshold selected
from validation events only after train-only fitting. It scores Dice and IoU
`1.0` on 89 selected Ward Creek/Windigo prototype test cores under one sealed
baseline opening.

The bounded model is `burnlens-unet-binary-v0.1.0`: six pre/post Sentinel-2
channels, 64-by-64 patches, train-only normalization, masked binary loss, CPU,
fixed seed, Adam, and a 0.5 threshold. It scores macro Dice
`0.29874213836477986`, macro IoU `0.21474358974358976`, and worst-event Dice
`0.2641509433962264`. The decision is `reject-model-retain-baseline`.

The perfect selected-core baseline result is a bounded comparison, not a
population estimate. Phase Four exposes that boundary: WCP-001 has 141.44 ha
of accepted RBR with 94.19% MTBS overlap, while WCP-002 has 66.76 ha with 0%
MTBS overlap and is presented as false-positive-risk evidence.

## Limitations

- Owner-approved prototype regions are not independent ground truth.
- Twelve balanced patches and 287 selected 20-metre core pixels do not estimate
  natural class prevalence.
- The test covers two events and 89 selected cores, not complete burn scars.
- Candidate construction may favor the spectral separability RBR measures.
- RBR `1.0` on selected cores does not establish generalization.
- The U-Net is not an accepted perimeter, area estimator, calibrated
  confidence product, or evidence of model superiority.
- WCP-002 shows that the accepted baseline can still produce material
  false-positive-risk evidence away from MTBS context.
- The current application is local and offline. It is not deployed,
  operational, field-validated, endorsed, or emergency-ready.
- No Phase 3B or follow-on experiment is planned or implemented in this
  project.

## Reproduce and validate

From a BurnLens checkout with the locked geospatial profile:

```powershell
uv run --locked --extra model --extra geo-research `
  burnlens-validate-phase-four-package `
  --package-path samples/runs/phase-four/burnlens-ward-creek-rbr-run-v0.1.0

uv run --locked --extra model --extra geo-research `
  burnlens-validate-phase-four-package `
  --package-path portfolio/phase-four/BURNLENS-WARD-CREEK-RBR-RUN-2026-001.zip
```

Both commands must report `PACKAGE_VALIDATION_PASS`. The tracked package can be
validated and repacked from a clean checkout. Rebuilding the analytical run
from provider pixels also requires the governed ignored custody named in the
package `REPLAY.md`; raw provider archives are intentionally not published.

## Known issues

The Phase Five candidate has zero open critical/high findings and two visible
medium findings:

- a bounded setuptools advisory under the ZIP-only packaging route;
- an omitted historical setuptools builder identity needed only for exact
  v0.54 wheel reconstruction.

Both have impact and workaround in the exact
[known-issues register](../../samples/runs/phase-five/burnlens-phase-five-baseline-first-candidate-v0.1.1/KNOWN-ISSUES.md).
The naive clean clone also lacks ignored analytical custody required by some
historical builder tests; tracked package validation and byte-identical repack
remain portable.

## Citation and attribution

Use the repository and exact artifact identities below. Preserve these source
notices with derived Ward Creek material:

- `Contains modified Copernicus Sentinel data 2019.`
- `Map services and data available from U.S. Geological Survey, National
  Geospatial Program.`
- `Monitoring Trends in Burn Severity (MTBS), U.S. Geological Survey and USDA
  Forest Service.`

BurnLens-owned code and documentation use the repository MIT license.
Third-party data and derived-artifact notices remain separate. Do not publish
raw provider archives, private owner responses, credentials, retrieval details,
ignored custody, or machine-local paths.

## Trace

| Layer | Exact identity |
|---|---|
| Repository | `drwbkr1/burnlens-deschutes` |
| Verified software baseline | `0.55.0`; tag `v0.55.0-baseline-first-reliability-candidate`; merge `7066dcd9cef555a6df0716dc7568205e7d6d395e` |
| Modeling AOI | `aoi-darlene3-model-v0.2.0` |
| Label schema | `burn-scar-binary-region-label-schema-v0.3.0` |
| Prototype label set | `owner-approved-prototype-region-labels-v0.5.0` |
| Dataset | `burnlens-dataset-v0.1.0` |
| Split | `burnlens-whole-event-split-v0.1.0` |
| Baseline | `burnlens-baseline-v0.1.0`; run `BL-2026-07-25-p2o5-t03-u05-evaluation-r003` |
| Rejected model | `burnlens-unet-binary-v0.1.0`; replay run `BL-2026-07-25-p3o1-t01-u06-replay-r003` |
| Accepted GEOINT run | `BL-2026-07-26-p4o1-t01-u07-package-r001`; source commit `733a3c265be2c351a50bfd356d1b45da15cbfec0` |
| Phase Four ZIP | 487,893 bytes; SHA-256 `91308a2ffe7095d89843edeb1634d6b1e972eb65bf1f67f38f1da0279102d84e` |
| Phase Five candidate | `burnlens-phase-five-baseline-first-candidate-v0.1.1`; run `BL-2026-07-26-p5o1-t01-u06-release-candidate-r002` |
| Phase Five ZIP | 646,513 bytes; SHA-256 `691c4bddb6754d74ca858a0b801fb21e62103032184425d2ba1b1648df1b0c26` |
| Phase Six scope gate | `PHASE-SIX-PUBLIC-SCOPE-RECORD-2026-001`; run `BL-2026-07-27-p6o1-t01-u01-public-scope-r001` |

This guide is a Phase Six pre-publication narrative. It does not itself create
a GitHub Release, deployment, public-sharing change, or external submission.
