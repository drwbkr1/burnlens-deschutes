# Observation Geometry and Label-Feasibility Decision

## Decision

Accept the `A2024179.2118` NOAA-21 observation as materially improved complementary native-scale reference geometry. Defer labels and a dataset.

Decision code: `ACCEPT_COMPLEMENTARY_REFERENCE_GEOMETRY_DEFER_LABELS`.

## Weakness addressed

The shipped source baseline used one temporally close VIIRS swath whose qualified AOI records were observed at approximately 69 degrees view zenith, near the scan edge. BurnLens had not proved whether that weakness was specific to the selected pass, whether another bounded observation materially improved geometry, or whether positive, negative, unknown, excluded, and review-needed states could be preserved without manufacturing labels.

## Bounded implementation

- Query the complete official CMR `VJ214IMG.002` inventory intersecting the frozen AOI from 2024-06-25 through 2024-07-01.
- Acquire and inspect all 23 exact active-fire granules in a fail-closed, variable-size extension of the shipped atomic intake transaction.
- Compare actual AOI sparse-record confidence, geolocation QA, residual-bowtie flags, view zenith, reference agreement, day/night regime, and time offset.
- Select at most one exact `VJ203MODLL.021` companion after a materially improved candidate is identified, then verify its actual AOI geolocation geometry.
- Render normalized JSON, semantic HTML, and a static evidence graphic while retaining provider bytes only in ignored local storage.
- Define a feasibility protocol that keeps native-scale positive references, negative candidates, unknowns, exclusions, and review-needed cases distinct. It creates no label array.

## Real evidence

Run `BL-2026-07-14-observation-geometry-r002` found 23 inventory candidates, nine with AOI fire records, eight with reference-qualified records, and five satisfying the conservative material-improvement screen. The selected day candidate is `VJ214IMG.A2024179.2118.002.2025284191612`, observed 2.478049 hours after the Sentinel scene.

Its 13 AOI fire records include 11 nominal/high, nominal-geolocation, non-bowtie references. Qualified view zenith spans 30.86 to 31.20 degrees with a 31.01-degree median. Ten of the 11 qualified records fall inside the later NIFC reference. The exact companion geolocation arrays are `3216 x 3200`; 141 AOI bounding-box pixels span columns 1085 to 1097, at least 1085 columns from the nearest scan edge.

The shipped comparison observation had eight AOI records, three residual-bowtie records, five non-bowtie records, qualified view zenith of 69.02 to 69.07 degrees, and AOI geolocation only seven columns from the eastern scan edge. The new observation materially improves geometry under the declared BurnLens rule.

## Why labels remain deferred

Better geometry does not solve cross-sensor truth. The selected thermal observation is 2.48 hours after the optical scene, and 375 m anomaly support cannot define genuine 10-20 m segmentation boundaries. The protocol therefore permits native-scale reference evidence only. It prohibits buffered-point truth, resampled pseudo-precision, use of the later NIFC perimeter as pixel-perfect active-fire truth, and conversion of VIIRS non-detection to background.

Protocol `weak-reference-label-feasibility-v0.1.0` defines:

- **positive reference:** qualified native-scale thermal-anomaly evidence, never a segmentation-positive pixel;
- **negative candidate:** a review candidate only, because omission, timing, atmosphere, mixed pixels, and scan geometry remain possible;
- **unknown:** the default unresolved state, never silently background;
- **excluded:** invalid coordinates, non-nominal geolocation QA, residual bowtie, or unusable optical quality;
- **review needed:** qualified records that still require time, scale, disagreement, and intended-use review.

## Reliability findings

The package `darlene3-vj214img-observation-screen-v0.2.0` contains exactly 24 provider assets and 83,723,055 bytes. Contract `observation-screen-contract-v0.2.0` has SHA-256 `af396fcbf6fb32860c4f76111ab74ac0f3d2c810ab2c1aba19903337a757ad3c`. Every asset passed exact identity, size, HDF5 signature, local multihash, atomic promotion, and independent registered-package verification.

During the first final promotion attempt, OneDrive temporarily exposed one file with an additional hard link. BurnLens rejected the package with `ASSET_MULTILINK_NOT_ALLOWED`; after the external link disappeared, an unchanged exact retry passed. No gate was weakened.

The committed JSON, HTML, and PNG reproduce byte for byte. The real semantic page has 23 candidate rows, no horizontal overflow, a fully loaded 1600 by 1100 graphic, intact traceability and warnings, and no browser console warnings or errors.

## Primary-source basis

- NASA's `VJ214IMG.002` catalog defines the 375 m six-minute active-fire swath, required geolocation relationship, variables, citation, and open-sharing posture.
- NASA's Collection 2 active-fire guide defines confidence, QA, bow-tie, scan-geometry, false-alarm, and omission limitations.
- The official LAADS file specification documents the variable along-track fire-mask dimension observed across the inventory.
- NASA's `VJ203MODLL.021` product documentation defines the moderate-resolution terrain-corrected geolocation product.
- NASA CMR is the authoritative inventory source used for the bounded query.

Current NASA terms remain resolved for this internal research acquisition and bounded derived evidence. Raw provider redistribution is not part of this checkpoint.

## Phase and portfolio meaning

BurnLens now demonstrates a complete observation search, exact multi-asset intake, actual geometry comparison, and an uncertainty-preserving label-feasibility decision. It also demonstrates that better source geometry is not permission to overstate label quality.

This advances Phase Two source comparison, raw integrity, QA, and label-semantics outcomes. It does not satisfy label implementation, dataset versioning, split independence, baselines, model readiness, model performance, application, deployment, or operational fitness.

## Next gate

The active-fire target still lacks defensible segmentation truth after the best bounded complementary reference was inspected. Activating the established burn-scar fallback or stopping active-fire modeling changes the target path and therefore requires the owner's explicit decision under the controlling goal.

## Shipment

Issue #333 closed through PR #334 at merge `1c85496d9d488c0d2d5a58207d8b4786a683ba52`. Annotated `v0.5.0-observation-geometry-baseline` tag object `cb9e675789d8ca4c4f8a5f4828331d41d023038e` remotely dereferences to that exact commit. Generator source remains `89d50c24a696cc7e3ec023eec00b021a4a0cdda6`; merged-main verification passes. Lifecycle synchronization is issue #335.
