# BurnLens Deschutes - Living Case Study

## The portfolio promise

BurnLens is an experimental CV-to-GEOINT portfolio project for technical and technical-adjacent reviewers. It aims to show one deep, reproducible path from versioned remote-sensing evidence to a segmentation model or justified baseline, georeferenced outputs, transparent maps, and an immutable run package.

It is not official wildfire information, emergency guidance, or an operational system.

## Current evidence, not future aspiration

BurnLens has established its governing task and source boundaries, selected exact Sentinel-2 and NOAA-21 VIIRS candidates, and implemented a fail-closed download validator. The validator caught a subtle but consequential failure: an unauthenticated data-looking URL returned an Earthdata Login HTML page with HTTP 200. BurnLens rejected and deleted it instead of registering it as NetCDF/HDF5.

The next evidence-visible weakness was spatial scope. The original AOI was only a metadata-discovery box. Issue #321 found the exact public NIFC Darlene 3 final-perimeter reference and used it to derive a reproducible modeling boundary.

![BurnLens final modeling AOI evidence](../../samples/aoi/phase-two/AOI-FINAL-2026-001.png)

With the boundary fixed, issue #325 addressed the next reliability gap before credentials: the exact Sentinel scene and its VIIRS fire/geolocation pair must enter raw registration together or not at all.

![BurnLens paired-intake transaction evidence](../../samples/intake/phase-two/PAIR-INTAKE-REHEARSAL-2026-001.png)

Issue #329 then crossed the data-evidence boundary. BurnLens acquired the exact package through the authorized CDSE and Earthdata accounts, re-verified all three files, opened the real raster and swath arrays, and rendered the result without committing raw provider bytes.

![BurnLens authenticated source inspection](../../samples/inspection/phase-two/SOURCE-INSPECTION-2026-001.png)

Issue #333 tested whether the extreme VIIRS scan geometry was a source limitation or a pass-selection limitation. BurnLens inspected every bounded NOAA-21 candidate and one exact selected companion, then rendered the complete comparison and uncertainty-preserving label-feasibility protocol.

![BurnLens observation geometry comparison](../../samples/observation/phase-two/OBSERVATION-GEOMETRY-2026-001.png)

## Why the AOI matters

The final AOI is a 12 km by 9 km rectangle in WGS 84 / UTM zone 10N. It is derived by adding 2 km of context around the complete NIFC reference and snapping outward to a 1 km grid. That makes later clipping, tiling, checks, and explanation deterministic.

The source roles stay separate:

- NIFC geometry: authoritative incident-reference evidence, with mixed-method and no-warranty limitations.
- BurnLens AOI: an experimental analysis boundary.
- Model output: does not exist yet.

The real reference exposed and corrected an earlier planning assumption: it extends east of the discovery box. The final AOI is 48.1% smaller by projected bounding-area comparison but reaches 2.88 km farther east so the official reference is not clipped.

## Reliability evidence

- Immutable reference SHA-256: `3d615d4be88f65806399e3733491ab0d95e16ac91ea86b5a00b3ead81ec17abe`.
- Local projection matches NIFC's independent EPSG:32610 response within 0.000220 m.
- Official Census TIGERweb confirms the final envelope is within Deschutes County.
- Selected Sentinel and exact VIIRS pair metadata footprints contain the AOI.
- Sixteen repository tests pass, including checksum tamper failure, projection, containment, rendering, and byte-for-byte deterministic rebuilds.

These are source, geometry, coverage, and reproducibility claims. They are not fire-detection, label, dataset, baseline, model, or accuracy claims.

## Reliability before data touch

BurnLens `0.3.0` pins all three expected filenames, provider/native identifiers, exact sizes, container signatures, the VIIRS pair token, and the provider checksums that actually exist. A package fails before raw registration if any file is missing, unexpected, renamed, malformed, corrupt, unsafe, mismatched, checksum-invalid, link-backed, or multiply linked. Only a complete validated quarantine directory can be atomically promoted; an existing destination is protected. Contract `v0.4.0` hashes the asset identities and the complete transaction-invariant set together. If the final rename fails, its provisional manifest is removed and the same validated quarantine remains retryable. After promotion, the verifier rechecks the manifest, contract digest, exact files, and current hashes so later mutation is visible.

Before the owner authorized real access, BurnLens tested the transaction state machine with small temporary synthetic fixtures. The rehearsal rejects a partial set, rejects checksum tampering, promotes a complete set atomically, and deletes the synthetic tree. Its rendered `BLOCKED_OWNER_CREDENTIAL` state is historical evidence from before `ACCESS-2026-006`; its zero-provider values remain truthful for that run but no longer describe the current local workspace.

Thirty-seven repository tests and a byte-identical second report build pass. The report fixes the public-metadata observation at 2026-07-14 and explicitly states that deterministic rehearsals make no live provider request, so a later run time cannot masquerade as fresh research. A fourth rendered rehearsal check proves post-promotion mutation is detected. This proves transaction behavior and evidence honesty, not source delivery or remote-sensing fitness.

## What the real files prove

BurnLens `0.4.0` adds a runtime-only credential wrapper and exact-provider acquisition client. Authentication is host-scoped; redirects are HTTPS-only and allowlisted; cross-host authorization is stripped; signed queries never enter evidence; partial downloads are resumable but size-bounded; invalid partials are deleted. No username, password, token, cookie, signed URL, or credential-store detail is committed.

Acquisition run `BL-2026-07-14-authenticated-intake-r001` registered the exact three-file, 1,169,997,942-byte package in ignored local raw storage. The Sentinel ZIP has 95 members, one expected SAFE root, `manifest.safe`, matching provider MD5/BLAKE3, and clean CRC results. The two VIIRS assets match their exact sizes and native HDF5 signatures; their local SHA-256/MD5/BLAKE3 values are recorded without inventing provider checksums.

Inspection run `BL-2026-07-14-source-inspection-r001` reads the actual arrays:

- Sentinel true color: exact `1,200 x 900` AOI crop at 10 m on EPSG:32610.
- Sentinel SCL: exact `600 x 450` crop at 20 m, 9.0281% medium/high cloud, 0.1163% cloud shadow, and zero no-data pixels.
- VIIRS fire product: `6464 x 6400` mask, 65 consistent sparse records, and eight records inside the AOI.
- AOI fire records: six nominal, two high confidence, three residual-bowtie, and zero non-nominal-geolocation QA flags.
- Companion geolocation: all 10,342,400 coordinate pairs pass the implemented validity checks; AOI candidates lie only seven columns from the swath edge.

The strongest finding is a limit. The AOI fire records are observed at 69.02-69.07 degrees view zenith. The Sentinel and VIIRS observations are almost 47 minutes apart, and 375 m thermal anomalies cannot define 10-20 m segmentation boundaries. BurnLens therefore accepts the package for source/reference use and defers labels and a dataset. A second full inspection reproduces JSON, HTML, and PNG byte for byte; the semantic page was also verified in the in-app browser with no console errors or horizontal overflow.

## What the observation screen changes

BurnLens `0.5.0` queries the complete official CMR `VJ214IMG.002` inventory for the frozen AOI from June 25 through July 1, 2024. All 23 exact active-fire granules were acquired, integrity-checked, registered together, and inspected for actual AOI records. Nine contain AOI records, eight contain reference-qualified records, and five pass the declared conservative material-improvement rule.

The selected `A2024179.2118` day observation is genuinely better source geometry:

- 13 AOI records and 11 qualified native-scale references;
- zero residual-bowtie exclusions;
- 30.86-31.20 degree qualified view zenith, with a 31.01-degree median;
- 10 of 11 qualified records inside the later NIFC reference;
- an exact companion whose AOI geolocation pixels are more than 1,000 columns from the nearest scan edge.

This corrects the shipped pass-selection weakness. It does not create segmentation truth. The selected observation is 2.48 hours after Sentinel, and its 375 m support cannot define genuine 10-20 m boundaries. Protocol `weak-reference-label-feasibility-v0.1.0` therefore keeps positive references, negative candidates, unknowns, exclusions, and review-needed cases separate. No label array or dataset is created.

The exact 24-asset / 83,723,055-byte package remains ignored locally. An initial final-promotion attempt was rejected when OneDrive temporarily exposed one asset through a second hard link. The unchanged retry passed after the link disappeared, showing that an environmental race remains visible without weakening the gate. The committed JSON, HTML, and PNG rebuild byte for byte, and the semantic report passes real browser review with 23 candidate rows, no overflow, and no console warnings or errors.

## Current risk and next checkpoint

Access, native-file uncertainty, and bounded pass geometry are now resolved. Label truth is the highest remaining risk. A substantially better thermal swath exists, but it is still insufficient for a leakage-resistant image/label dataset with credible 10-20 m positives and negatives.

The next step is a product decision, not another silent implementation choice: activate the established burn-scar fallback or stop active-fire modeling. The controlling goal reserves that target-path change for the owner. Until that decision, BurnLens will not buffer points into truth, turn non-detections into background, or use the later NIFC perimeter as a pixel-perfect active-fire label.

## Traceability snapshot

- AOI: `aoi-darlene3-model-v0.2.0`
- Evidence run: `BL-2026-07-14-aoi-final-r001`
- Latest evidence run: `BL-2026-07-14-observation-geometry-r002`
- Acquisition run: `BL-2026-07-14-authenticated-intake-r001`
- Tool: BurnLens package `0.5.0`, shipped observation-geometry baseline
- Transaction contract: `paired-intake-contract-v0.4.0`
- Source package: `darlene3-s2-viirs-pair-v0.1.0`; raw bytes local/ignored, zero committed
- Observation package: `darlene3-vj214img-observation-screen-v0.2.0`; 24 assets / 83,723,055 bytes local/ignored, zero committed
- Observation contract/protocol: `observation-screen-contract-v0.2.0`; `weak-reference-label-feasibility-v0.1.0`
- Credential records: `ACCESS-2026-006` authorization and `ACCESS-2026-007` / `ACCESS-2026-008` secret-safe exercises
- Observation generator source: `89d50c24a696cc7e3ec023eec00b021a4a0cdda6`
- Latest shipped repository baseline: `v0.5.0-observation-geometry-baseline` at `1c85496d9d488c0d2d5a58207d8b4786a683ba52`
- Shipped checkpoint: issue #333 / PR #334; annotated tag object `cb9e675789d8ca4c4f8a5f4828331d41d023038e`; lifecycle sync issue #335 / PR #336
- Dataset / label schema / baseline / model: not created
- Public application: not created; this repository case study, README, source-inspection report, and observation-geometry report are the current presentation surfaces

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
