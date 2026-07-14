# Changelog

All notable BurnLens checkpoints are recorded here. Technical evidence remains in the linked issues, PRs, commits, versions, runs, and phase records.

## v0.2.0-aoi-baseline — 2026-07-13

### P2O2-T01 — Final Darlene 3 modeling AOI

- Retain the exact public NIFC WFIGS Darlene 3 final-perimeter feature as an immutable 47,483-byte reference snapshot with SHA-256 `3d615d4be88f65806399e3733491ab0d95e16ac91ea86b5a00b3ead81ec17abe`.
- Add checksum/identity/geometry validation plus deterministic WGS84-to-UTM projection that matches NIFC's independent EPSG:32610 extent within 0.000220 m.
- Derive `aoi-darlene3-model-v0.2.0`: 12 km by 9 km / 108 km2, using 2 km context and a 1 km outward grid snap.
- Correct the discovery-box assumption: the final AOI is 48.096% smaller by projected bounding-area comparison but extends 2.883 km farther east to contain the complete official reference.
- Verify the final envelope within Census Deschutes County and within the selected Sentinel/VIIRS metadata footprints.
- Render deterministic JSON, semantic HTML, and PNG evidence; add the living repository case study; pass 16 tests and original-resolution visual review.
- Preserve the credential stop and all no-model/no-operational boundaries. One reference vector exists; provider imagery, labels, datasets, baselines, models, detections, and performance claims do not.

Shipped through PR #322 at merge commit `fffd3dda123d7c43fe678dca9adfd8feb73de158`; issue #321 closed and the annotated `v0.2.0-aoi-baseline` tag resolves to that exact commit. Sixteen post-merge tests pass, a fresh pipeline run reproduces the committed JSON/HTML/PNG hashes byte for byte, and the public PR, README, living case study, source record, and PNG render were verified. Issue #323 records the lifecycle synchronization. No credential, provider imagery, label, dataset, baseline, model, detection, performance result, application, or deployment was added.

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
