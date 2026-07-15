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

## Target decision: burn-scar fallback active

The owner resolved the target-path gate on 2026-07-14: BurnLens will use the established burn-scar binary-mask fallback. The first CV task remains experimental binary semantic segmentation. Active-fire observations remain complementary thermal-anomaly reference evidence, not the direct label target.

Corrected run `TARGET-DECISION-2026-002` makes the choice inspectable. It carries forward the strongest active-fire evidence—375 m support, 2.48 hours from Sentinel, and a 31.01-degree qualified median view angle—while recording why those facts still cannot define genuine 10-20 m pixel truth. It defines burned, background-candidate, unknown, and excluded states as a design gate and creates no label array. The merged `001` run remains preserved because post-merge validation found that its MTBS input byte hash changed with checkout line endings; issue #339 corrected the serialization contract instead of rewriting that history.

MTBS was evaluated from current official sources because its analyst-interpreted fire-level products include pre/post imagery, burn indices, boundaries, thematic severity, and non-processing masks. Its current 2024 occurrence inventory returned 941 records but no Darlene name match, and both the 2024 and all-years occurrence layers returned zero features inside the frozen BurnLens AOI. MTBS therefore remains relevant methodology and potential cross-fire or future reference evidence; it cannot provide the exact Darlene 3 label today, and its severity classes will not expand BurnLens into a multiclass task.

The highest remaining risk is now burn-scar label truth. BurnLens has identified and visually validated one legally usable, temporally defensible pre/post optical pair, defined a reproducible five-state protocol, and passed a separate pair-local translation gate. The next checkpoint must create an independently reviewable label proposal before BurnLens may consider a dataset, spectral baseline, or model.

## Exact optical pair: clear evidence, deferred truth

Issue #343 selects and acquires two Sentinel-2A L2A Collection 1 products from the same tile, relative orbit, and processing baseline: one about an hour before the approximate incident start and one about ten days after. Both complete SAFE archives pass exact provider MD5/BLAKE3, local SHA-256, 95-member root/manifest/CRC, and independent registered-package verification. Their 2,254,805,631 provider bytes remain local and ignored.

![BurnLens exact optical-pair evidence](../../samples/optical/phase-two/OPTICAL-PAIR-2026-001.png)

The exact AOI windows align without reprojection or resampling: 1,200 by 900 true color at 10 m and 600 by 450 B04/B8A/B12/SCL evidence at 20 m. Pairwise SCL rules retain 267,067 pixels / 98.9137% as eligible comparison, 2,063 / 0.7641% as review-needed, and 870 / 0.3222% as excluded. Both scenes are readable; the continuous dNBR view shows a coherent change pattern around the later incident-reference outline.

That is evidence that the pair is useful, not evidence that every changed pixel is burned. The ten-day interval can include vegetation, moisture, atmosphere, soil, mixed-pixel, and registration effects. The dNBR display uses a fixed disclosed color stretch but no classification or severity threshold. SCL 7 remains review-needed, and the mint NIFC outline is later mixed-method context, never a pixel label.

Protocol `burn-scar-label-protocol-v0.1.0` therefore defines five states. Burned and background-candidate may later map to binary 1/0 only after affirmative evidence and independent review. Unknown, excluded, and review-needed remain outside loss and metrics. A later label checkpoint must preserve boundary review bands, group events/scenes/geography/time before tiling, record disagreements, and perform an independent second QA pass.

The acquisition itself adds useful reliability evidence. One response ended early and remained resumable; a later server response ignored Range, so the client safely restarted instead of appending. OneDrive twice created temporary upload-staging hard links, and the transaction rejected both races. The second race exposed an unnormalized local `ValueError`; BurnLens added regression-tested secret-free state normalization before the unchanged retry.

The decision is `ACCEPT_OPTICAL_PAIR_FOR_PROTOCOL_DEFER_LABELS`. No label array, state raster, dataset, split, baseline, model, metric, application, deployment, or operational claim is created.

## Pair-local registration: a prerequisite, not truth

Issue #347 isolates local content registration before any label proposal. Exact source-grid equality is necessary but cannot prove that scene content is aligned. BurnLens `0.8.0` therefore measures twelve fixed native-20m windows with independent pre/post B04, B8A, and B12 reflectance gradients, a Hann taper, phase-only cross-power, and localized 100x DFT refinement.

![BurnLens pair-local content-registration evidence](../../samples/registration/phase-two/CONTENT-REGISTRATION-2026-001.png)

The method deliberately applies no shared quality or stable-pixel mask to the correlation signals; a common mask can create an artificial zero-shift peak. NIFC geometry, VIIRS observations, dNBR, burn/background assumptions, and label thresholds do not steer the measurement. Pair quality determines window usability only.

All twelve windows pass the frozen gate. Median residual is 0.0224 native pixel; p95 and maximum are 0.0361 pixel, about 0.72 m. The least eligible window retains 94.96% eligible pixels, all three bands are confident everywhere, minimum peak ratio is 7.5916, and maximum band disagreement is 0.04 pixel.

The packaged Sentinel geometric reports are preserved but do not substitute for this evidence. Both globally pass, while both also state that VNIR/SWIR bands have not been registered and spatio-residual histograms were not computed. A first final JSON audit caught that the initial parser missed those sibling message/value nodes; BurnLens corrected the parser and fixture before accepting the artifacts.

Decision `ACCEPT_LOCAL_CONTENT_REGISTRATION` clears only the local translation prerequisite. Window passes never override pixel-level SCL review/excluded states and never assign burned or background. The next bounded risk is a reviewable five-state label proposal with independent QA, not dataset construction or model training.

## Traceability snapshot

- AOI: `aoi-darlene3-model-v0.2.0`
- Evidence run: `BL-2026-07-14-aoi-final-r001`
- Latest evidence run: `BL-2026-07-14-target-decision-r002`
- Latest optical evidence run: `BL-2026-07-15-optical-pair-evidence-r001`
- Latest registration evidence run: `BL-2026-07-15-content-registration-r001`
- Acquisition run: `BL-2026-07-14-authenticated-intake-r001`
- Tool: shipped BurnLens `0.7.0` optical baseline plus review-ready BurnLens `0.8.0` registration candidate; registration generator source `5287704a37f03d96e47467afba8623f7be643129`
- Optical shipment: issue #343 / PR #344; merge `136d4d0919eba7144881c22163a149c89fee5a76`; annotated tag object `28d12fb5ef5c70054b8af5fd3c4847ba268000a1`
- Active target: `target-burn-scar-v0.2.0`; active-fire path is complementary reference only
- Target evidence: corrected `TARGET-DECISION-2026-002`; JSON `ac67f6c34a934d639c215ee98b181f1114b5624acafb85f65b1e2f3e804ce4d4`; HTML `0c1279e5e1047ff251dcd65f068d3d45bf2c6982e6a308972205e9d0a76879d4`; PNG `36f221aa6393ad07f14d4d7bb54b1f171ef0636ebb5640a11ab02ab9c5a9b5b0`
- Optical package/protocol: `darlene3-s2-optical-pair-v0.1.0`; `optical-pair-intake-contract-v0.1.0`; `burn-scar-label-protocol-v0.1.0` design only; 2,254,805,631 local/ignored raw bytes; zero committed
- Optical evidence: `OPTICAL-PAIR-2026-001`; pair accepted for protocol evidence; artifact hashes recorded in `MANIFEST-2026-008`
- Registration evidence: `CONTENT-REGISTRATION-2026-001`; all twelve windows pass; artifact hashes recorded in `MANIFEST-2026-009`; exact merge/tag identities pending
- Transaction contract: `paired-intake-contract-v0.4.0`
- Source package: `darlene3-s2-viirs-pair-v0.1.0`; raw bytes local/ignored, zero committed
- Observation package: `darlene3-vj214img-observation-screen-v0.2.0`; 24 assets / 83,723,055 bytes local/ignored, zero committed
- Observation contract/protocol: `observation-screen-contract-v0.2.0`; `weak-reference-label-feasibility-v0.1.0`
- Credential records: `ACCESS-2026-006` authorization and `ACCESS-2026-007` / `ACCESS-2026-008` secret-safe exercises
- Observation generator source: `89d50c24a696cc7e3ec023eec00b021a4a0cdda6`
- Latest shipped repository baseline: `v0.6.0-burn-scar-target-baseline` at remediation merge `bcb71ebd01d3184f8de24318428309e61d33e54f`; annotated tag object `0b4e0ff226be0d78b3b510b7786be0ca1c817887`
- Latest shipped analytical checkpoint: issue #337 / PR #338 plus remediation issue #339 / PR #340; 69 post-merge tests and byte-identical corrected reconstruction pass; lifecycle sync issue #341 / PR #342 is documentation-only
- Active next checkpoint: produce an independently reviewable five-state label proposal with separate QA; dataset construction remains gated
- Dataset / label schema / baseline / model: not created
- Public application: not created; this repository case study, README, source-inspection report, observation-geometry report, target-decision report, optical-pair report, and registration report are the current presentation surfaces

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
