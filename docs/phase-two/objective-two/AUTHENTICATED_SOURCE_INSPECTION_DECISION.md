# Authenticated Source Inspection Decision

## Decision

Accept `darlene3-s2-viirs-pair-v0.1.0` as an authenticated, integrity-verified source and reference package. Do not promote the package, its VIIRS records, or the NIFC reference geometry to labels or a dataset.

Decision code: `ACCEPT_SOURCE_REFERENCE_DEFER_LABELS`.

## Weakness addressed

The previous checkpoint proved a fail-closed intake transaction using temporary fixtures, but BurnLens still had no provider pixels and no evidence that the exact files were readable, spatially relevant, or useful. Authentication, delivery, native containers, real raster grids, real swath arrays, AOI fire records, view geometry, and label fitness were all unknown.

## Adopted implementation

- Load the owner-authorized machine-bound credentials only through the local wrapper and remove plaintext environment values immediately.
- Restrict authentication and redirects to exact HTTPS host allowlists, strip authorization across host boundaries, and exclude signed queries from state and evidence.
- Resume partial downloads safely, enforce exact expected size during transport, and delete oversized or invalid partials.
- Validate the complete three-file quarantine against `paired-intake-contract-v0.4.0` before one atomic raw promotion.
- Independently re-verify the registered package, current hashes, Sentinel SAFE structure, and exact entry set before inspection.
- Read the actual Sentinel TCI/SCL arrays and the actual VIIRS fire/QA/geolocation arrays.
- Render bounded JSON, semantic HTML, and PNG evidence; retain raw provider bytes only in ignored local storage.

## Real evidence

Acquisition run `BL-2026-07-14-authenticated-intake-r001` registered the exact 1,169,997,942-byte package. Inspection run `BL-2026-07-14-source-inspection-r001` found:

- a `1,200 x 900` Sentinel true-color AOI crop at 10 m and a `600 x 450` SCL crop at 20 m on EPSG:32610;
- 9.0281% SCL medium/high cloud, 0.1163% cloud shadow, and zero no-data pixels in the AOI;
- a `6464 x 6400` VIIRS fire mask with 65 consistent sparse records, eight inside the modeling AOI;
- six nominal and two high-confidence AOI records, with three residual-bowtie flags and zero non-nominal-geolocation flags;
- five non-bowtie AOI records, four inside the later NIFC final-perimeter reference;
- 69.02-69.07 degree view zenith and companion geolocation pixels only seven columns from the swath edge.

The evidence is reproducible: a second full inspection run with the same package, run identity, source commit, and timestamp reproduced JSON, HTML, and PNG byte for byte. The semantic page loaded in the in-app browser with no console errors or horizontal overflow and preserved all warnings, exclusions, attribution, and traceability.

## Primary-source basis

- NASA's VJ214IMG.002 catalog defines the 375 m active-fire product, its VJ203MODLL companion need, citation, and open-sharing posture.
- NASA's Collection 2 active-fire guide defines fire-mask classes, sparse arrays, QA bits, scan geometry, and documented false-alarm/omission limitations.
- CDSE Sentinel-2 L2A documentation defines band resolutions and SCL classes.
- CDSE guidance supplies the required modified-Sentinel attribution wording.
- Current CDSE and NASA terms records remain resolved for this bounded source/reference and derived-evidence use. Raw source files remain uncommitted.

## Phase and portfolio meaning

BurnLens now has real, inspectable source evidence and a demonstrably secret-safe acquisition boundary. The most important result is negative: successful access did not justify labels. The report makes source uncertainty visible instead of turning coarse, oblique thermal anomalies into persuasive-looking training truth.

This advances Phase Two source acquisition, raw integrity, inspection, and QA outcomes. It does not satisfy label schema, dataset versioning, split independence, baselines, model readiness, model performance, application, deployment, or operational fitness.

## Next gate

Test whether alternate temporally relevant VIIRS observations materially improve scan geometry and whether a versioned weak/reference-label protocol can preserve positive, negative, unknown, and excluded states. If no defensible path emerges, evaluate the established burn-scar fallback or stop active-fire modeling only through the controlling goal's owner-decision boundary.

## Shipment

Issue #329 closed through PR #330 at merge `7678cf41b64e128106c199b913fe74590a52cf80`. The verified annotated `v0.4.0-authenticated-source-baseline` tag object `98228058b232bc0838eb976f982ef4775b711776` remotely dereferences to that exact commit. Post-merge tests, dependency health, and byte-identical real-source reconstruction pass. Lifecycle synchronization is tracked by issue #331 / PR #332.
