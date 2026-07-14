# Changelog

All notable BurnLens checkpoints are recorded here. Technical evidence remains in the linked issues, PRs, commits, versions, runs, and phase records.

## v0.5.0-observation-geometry-baseline - 2026-07-14

### P2O2-T04 - Complete NOAA-21 geometry comparison and label-feasibility protocol

- Query the complete official CMR `VJ214IMG.002` inventory for the frozen AOI and event window and inspect all 23 exact active-fire granules.
- Generalize the fail-closed atomic intake boundary for a caller-supplied exact variable-size contract while preserving the shipped three-asset default behavior.
- Acquire one exact `VJ203MODLL.021` companion only after a material candidate is identified; register the final 24-asset / 83,723,055-byte package under contract SHA-256 `af396fcbf6fb32860c4f76111ab74ac0f3d2c810ab2c1aba19903337a757ad3c`.
- Compare real AOI confidence, geolocation QA, residual bowtie, view zenith, time offset, and NIFC-reference agreement for every candidate.
- Select the `A2024179.2118` day observation: 11 qualified AOI records, zero residual-bowtie exclusions, 31.01-degree median view zenith, and more than 1,000 columns from the nearest scan edge, versus the shipped approximately 69-degree scan-edge baseline.
- Add `weak-reference-label-feasibility-v0.1.0`, preserving positive reference, negative candidate, unknown, excluded, and review-needed states without creating labels.
- Render `OBSERVATION-GEOMETRY-2026-001` as deterministic JSON, semantic HTML, and a 1600 by 1100 evidence graphic with complete traceability and public-use boundaries.
- Record decision `ACCEPT_COMPLEMENTARY_REFERENCE_GEOMETRY_DEFER_LABELS`: the 2.48-hour time offset and 375 m support still cannot define 10-20 m segmentation truth.
- Preserve fail-closed link safety when OneDrive temporarily exposed an asset through a second hard link; the unchanged exact retry passed after the link disappeared.

Issue #333 closed through PR #334 at merge `1c85496d9d488c0d2d5a58207d8b4786a683ba52`. Annotated tag object `cb9e675789d8ca4c4f8a5f4828331d41d023038e` remotely dereferences to that exact commit as `v0.5.0-observation-geometry-baseline`. Generator source is `89d50c24a696cc7e3ec023eec00b021a4a0cdda6`. Sixty-five post-merge tests, compilation, dependency health, byte-identical real-package reconstruction, original-resolution visual review, real in-app browser validation, secret/raw-byte exclusion, diff checks, issue closure, and remote tag identity pass. Raw provider bytes committed: zero. Label array, dataset, split, baseline, model, application, deployment, and performance claim: none. Lifecycle synchronization is issue #335 / PR #336.

## v0.4.0-authenticated-source-baseline — 2026-07-14

### P2O2-T03 — Authenticated exact-package acquisition and real-source inspection

- Add a secret-safe CDSE/Earthdata acquisition path for the exact frozen package: exact authentication hosts, HTTPS-only allowlisted redirects, cross-host authorization stripping, redacted errors, sanitized state, bounded/resumable partial downloads, native signatures, exact sizes, checksums, and atomic promotion.
- Exercise the owner-authorized machine-bound credentials without committing usernames, passwords, tokens, cookies, signed URLs, credential payloads, or credential-store details.
- Acquire and register the exact three provider assets totaling 1,169,997,942 bytes in ignored local raw storage; independently re-verify the exact four-entry registered package and all current hashes.
- Open the real Sentinel SAFE/JP2 and VIIRS HDF5/NetCDF-4 files, enforce expected grids and arrays, decode relevant QA flags, and inspect the frozen AOI.
- Render `SOURCE-INSPECTION-2026-001` as normalized JSON, semantic HTML, and a 1600x1100 evidence image with the real Sentinel crop, NIFC incident-reference outline, all eight AOI VIIRS records, residual-bowtie exclusions, scan-edge warning, attribution, and full traceability.
- Record a real-file decision of `ACCEPT_SOURCE_REFERENCE_DEFER_LABELS`: the package is readable and reference-relevant, but approximately 69-degree VIIRS view geometry, residual-bowtie records, temporal offset, and 375 m-to-10/20 m scale mismatch prevent direct label or dataset promotion.
- Pin `h5py==3.16.0`, `numpy==2.5.1`, and `rasterio==1.5.0` for reproducible native source inspection.

Issue #329 closed through PR #330 at merge commit `7678cf41b64e128106c199b913fe74590a52cf80`; the annotated `v0.4.0-authenticated-source-baseline` tag object `98228058b232bc0838eb976f982ef4775b711776` remotely dereferences to that exact commit. Acquisition run `BL-2026-07-14-authenticated-intake-r001` and inspection run `BL-2026-07-14-source-inspection-r001` are the real workflow evidence. All 56 tests, compilation, dependency health, offline wheel build/import, secret/raw-byte exclusion, diff checks, and byte-identical post-merge reconstruction pass. The semantic page passes in-app browser review with no console errors or horizontal overflow. Raw provider bytes committed: zero. Label schema, dataset, split, baseline, model, application, deployment, and performance claim: none.

## v0.3.0-intake-transaction-baseline — 2026-07-14

### P2O2-T02 — Atomic exact-pair intake before credentials

- Add `paired-intake-contract-v0.4.0`, pinning the exact Sentinel-2 SAFE ZIP and NOAA-21 VIIRS active-fire/geolocation files, identities, sizes, containers, pair token, available provider checksums, and transaction invariants under one digest.
- Fail closed on incomplete, unexpected, renamed, malformed, size-mismatched, unsafe/corrupt ZIP, checksum-invalid, pair-mismatched, cross-filesystem, or destination-colliding input.
- Record local SHA-256, MD5, and BLAKE3 only after all three assets pass; write provenance in quarantine and atomically promote the complete directory without overwriting existing raw state.
- Reject symlink/junction-backed quarantine paths and symlinked or multiply-linked asset files so registered bytes cannot alias mutable storage outside the transaction.
- Roll back the provisional registration manifest if atomic rename fails, preserving a clean validated quarantine that can be retried without weakening any gate.
- Add registered-package verification that re-reads the manifest, revalidates exact assets and contract identity, recomputes hashes, and makes post-promotion mutation fail visibly.
- Add a deterministic temporary synthetic rehearsal that proves partial rejection, checksum-tamper rejection, successful complete-set promotion, and zero retained fixture bytes.
- Render `PAIR-INTAKE-REHEARSAL-2026-001` as normalized JSON, semantic HTML, and a 1600x1200 evidence card that separates real `BLOCKED_OWNER_CREDENTIAL` state from synthetic transaction proof.
- Record the exact public CDSE/CMR metadata snapshot with a fixed observation time, explicitly separate it from later deterministic run times, and preserve the owner stop: zero credentials, live provider requests, provider assets, provider bytes, and promoted real packages.
- Record the owner's later CDSE and Earthdata authorization in `ACCESS-2026-006` without storing or exercising credential material; authenticated delivery and provider-file fitness remain unverified.

Issue #325 closed through PR #326 at merge commit `ee1a1d678ad888b595dc3c7b215f787ea5156582`; the annotated `v0.3.0-intake-transaction-baseline` tag resolves to that exact commit. Report-generator source remains `ac8ee43151991c38ccf5d446a53c09b617afeb54`. Thirty-seven post-merge tests, dependency checks, deterministic reconstruction, original-resolution visual review, claims review, remote tag verification, and zero-secret/provider-byte checks pass. This checkpoint does not prove provider delivery, real-file integrity, source fitness, fire presence, label readiness, a dataset, baseline, model, application, deployment, or performance.

## v0.2.0-aoi-baseline — 2026-07-13

### P2O2-T01 — Final Darlene 3 modeling AOI

- Retain the exact public NIFC WFIGS Darlene 3 final-perimeter feature as an immutable 47,483-byte reference snapshot with SHA-256 `3d615d4be88f65806399e3733491ab0d95e16ac91ea86b5a00b3ead81ec17abe`.
- Add checksum/identity/geometry validation plus deterministic WGS84-to-UTM projection that matches NIFC's independent EPSG:32610 extent within 0.000220 m.
- Derive `aoi-darlene3-model-v0.2.0`: 12 km by 9 km / 108 km2, using 2 km context and a 1 km outward grid snap.
- Correct the discovery-box assumption: the final AOI is 48.096% smaller by projected bounding-area comparison but extends 2.883 km farther east to contain the complete official reference.
- Verify the final envelope within Census Deschutes County and within the selected Sentinel/VIIRS metadata footprints.
- Render deterministic JSON, semantic HTML, and PNG evidence; add the living repository case study; pass 16 tests and original-resolution visual review.
- Preserve the credential stop and all no-model/no-operational boundaries. One reference vector exists; provider imagery, labels, datasets, baselines, models, detections, and performance claims do not.

Shipped through PR #322 at merge commit `fffd3dda123d7c43fe678dca9adfd8feb73de158`; issue #321 closed and the annotated `v0.2.0-aoi-baseline` tag resolves to that exact commit. Sixteen post-merge tests pass, a fresh pipeline run reproduces the committed JSON/HTML/PNG hashes byte for byte, and the public PR, README, living case study, source record, and PNG render were verified. Issue #323 / PR #324 records the lifecycle synchronization. No credential, provider imagery, label, dataset, baseline, model, detection, performance result, application, or deployment was added.

## v0.1.2-access-integrity-baseline — 2026-07-13

### P2O1-T03 — VIIRS delivery validation and credential boundary

- Exercise both exact LP DAAC delivery routes without credentials and reject a default-client `401` plus two browser-style `200` Earthdata Login HTML bodies as non-assets.
- Add a fail-closed Python validator that requires the native HDF5/NetCDF-4 signature and a plausible minimum size before provider bytes can enter provenance.
- Add deterministic JSON, semantic HTML, and PNG evidence rendering. The normalized report is `VIIRS-ACCESS-PRECHECK-2026-001`, run `BL-2026-07-14-access-precheck-r001`.
- Verify eight unit checks, deterministic JSON/HTML reconstruction, deterministic PNG reconstruction, visual layout, warning language, no signed-URL/credential retention, and deletion of rejected response bodies.
- Correct the access posture: NASA-led product use remains open and citable, while LP DAAC byte delivery requires Earthdata Login authentication and application authorization.
- Preserve the paired-source STOP. Both CDSE and Earthdata credentials now require explicit owner approval before source-asset intake.

Shipped through PR #318 at merge commit `d4ce26c87341e4d3798a0d84e257a964ebd2cde0`; issue #317 closed and the annotated `v0.1.2-access-integrity-baseline` tag resolves to that exact commit. The rendered PR and branch README, post-merge tests, deterministic report rebuild, and evidence hashes were verified. No provider source asset, fire-mask pixel, geolocation array, label, dataset, baseline, model, analytical metric, raster, vector, map, application, or wildfire detection is created.

## v0.1.1-asset-readiness-baseline — 2026-07-13

### P2O1-T02 — Exact Sentinel/VIIRS asset-access readiness

- Pin one post-report Sentinel-2 L2A scene and its exact CDSE product UUID, stable whole-product route, S3 path, provider checksums, native band/quality candidates, and credential requirements.
- Pin the closest same-day NOAA-21 VIIRS active-fire swath and its required terrain-corrected geolocation companion, stable Earthdata Cloud routes, formats, concept identifiers, and 46-minute-40.976-second offset from the Sentinel acquisition.
- Record the only defensible future reference role: VIIRS classes 8–9 may become candidate positive evidence after valid geolocation, AOI, temporal/view-angle, and human review; class 7 remains review/unknown, and non-detection is not automatic background.
- Retain `ASSET-READINESS-2026-001`, a metadata-only normalized fixture with SHA-256 `c5bcfbf57cf23a7bf3ed9bd1302461b2ba1ee101ab05b7d935419223763e5ce7`.
- Re-open F04-A and stop: Sentinel product access requires an owner-approved CDSE credential, while no provider asset may be downloaded under this checkpoint.

Shipped through PR #314 at merge commit `cf4aba2f40aa426f28f09b1b1b1bad895394198b`; the annotated `v0.1.1-asset-readiness-baseline` tag resolves to that commit. The rendered PR, merged F04-A, normalized fixture, and issue #312 closure were verified on GitHub. This checkpoint creates no application, dataset, source-asset copy, label, baseline, model, metric, run, raster, vector, map, detection, or public analytical result.

## v0.1.0-source-metadata-baseline — 2026-07-13

### P2O1-T01 — First source stack and metadata discovery

- Select a bounded Darlene 3 / La Pine metadata-discovery envelope without representing it as an official perimeter.
- Resolve current primary-source terms and intended evidence roles for Copernicus Sentinel-2 L2A, NASA VIIRS Collection 2 active-fire products, and Oregon incident context.
- Verify no-secret public metadata access through the official CDSE STAC catalog and NASA Common Metadata Repository.
- Retain `METADATA-2026-001`, containing five Sentinel-2 L2A items and 124 VIIRS granule records, with asset hrefs and source bytes excluded.
- Defer FIRMS archive/API delivery because it requires Earthdata/email authentication or a map key.
- Pass F04-A only for the completed metadata action; keep all asset intake, processing, labels, baselines, models, runs, maps, and analytical claims blocked.

Shipped through PR #310 at merge commit `6abe87bba486e3fe49b6c06178b454335663cb73`; the annotated `v0.1.0-source-metadata-baseline` tag resolves to that commit. The rendered Phase Status, F04-A decision, and metadata fixture were verified on GitHub after merge. No application, dataset, label, baseline, model, metric, run, raster, vector, map, or public analytical result is created by this checkpoint.

## v0.0.8-execution-goal-baseline — 2026-07-13

### BL-GOV-001 — Controlling execution goal and roadmap

- Adopt the owner-approved long-running goal as BurnLens's controlling authority.
- Preserve the established portfolio thesis, target reviewer, binary segmentation task, active-fire primary target, burn-scar fallback, GEOINT workflow, use boundaries, source precedence, and traceability requirements.
- Treat the six phase objectives as proof outcomes and their task order as a revisable planning hypothesis.
- Reconcile the latest Phase One planning-only decision with active status and roadmap records.
- Establish standing Codex authority and the exact owner stop conditions.
- Require every BurnLens application, public website, deployment, and case study to live in and ship from `drwbkr1/burnlens-deschutes`.
- Add active phase status, version history, prompt/build logging, and a human-readable devlog.

No data, AOI, labels, pipeline, model, metric, run, map, analytical output, or public performance claim is created by this checkpoint.

Verified merge: `22a8d88435cb8d5b900a398b7482c3b7277d2ee6` via PR #291. The annotated tag resolves to that commit.
