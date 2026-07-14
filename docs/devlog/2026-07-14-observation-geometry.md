# Devlog - Better Geometry, Still Not Truth

**Date:** 2026-07-14

**Issue / PR:** #333 / #334

## Weakness selected

BurnLens had one real active-fire reference, but it sat at the far scan edge. The evidence could not distinguish a genuinely weak label path from a poor observation choice. The highest-leverage next question was whether any bounded NOAA-21 pass materially improved actual AOI record geometry.

## Improvement made

BurnLens queried the complete official CMR inventory for the frozen AOI and event window, acquired all 23 exact active-fire granules, inspected their real sparse records, and compared confidence, QA, bow-tie state, view angle, time offset, and reference agreement. Only after a material candidate existed did it acquire the exact matching geolocation companion.

An exploratory selection rule exposed an important design flaw: minimizing angle alone chose a low-angle night pass more than 32 hours before the Sentinel scene. The final rule therefore prefers the Sentinel day regime, then temporal proximity, then geometry and usable-record strength among candidates that already pass the declared material-improvement gate. That revision is evidence-driven and recorded rather than hidden.

## What the files changed

The `A2024179.2118` day observation is materially better than the shipped `A2024179.1936` pass. It has 11 qualified AOI records, no residual-bowtie exclusions, a 31.01-degree median view zenith, and a geolocation intersection more than 1,000 columns from the nearest scan edge. The prior pass had five non-bowtie records near 69 degrees and was seven columns from the edge.

That is a real source improvement, but it is still not a segmentation label. The selected observation is 2.48 hours after Sentinel, and 375 m support cannot define 10-20 m truth. BurnLens keeps five distinct states and creates no label array or dataset.

## Reliability lesson

The final raw package was rejected once because OneDrive temporarily gave one asset an extra hard link. The existing multi-link gate caught it before registration. Once OneDrive released the link, the exact retry succeeded without changing the contract or weakening validation. This is the kind of environmental failure visibility BurnLens is meant to preserve.

## Verification

- 23 exact `VJ214IMG.002` candidates and one selected `VJ203MODLL.021` companion are locally registered; 83,723,055 raw bytes remain ignored and zero are committed.
- Contract SHA-256 is `af396fcbf6fb32860c4f76111ab74ac0f3d2c810ab2c1aba19903337a757ad3c`.
- A second real run reproduces JSON, HTML, and PNG byte for byte.
- The semantic page renders 23 candidate rows, one complete 1600 by 1100 image, no overflow, and no console warnings or errors.
- Sixty-five repository tests, compilation, dependency health, packaging, secret/raw-byte scans, and diff checks are the release quality gates.
- The first wheel command hit a local pip-cache ACL denial; the same offline no-cache wheel and isolated `0.5.0` import passed. Wheel SHA-256 is `9e005af427a7872f549a93f9e26b9f7afc8c1922a3e838a1a96d2aabee86b1f4`.

## What remains

No segmentation label schema implementation, dataset, split, baseline, model, analytical application, or deployment exists. The next product decision is whether to activate the already-defined burn-scar fallback or stop the active-fire modeling path; the controlling goal reserves that target change for the owner.

## Shipment proof

PR #334 merged at `1c85496d9d488c0d2d5a58207d8b4786a683ba52`, closing issue #333. Annotated tag object `cb9e675789d8ca4c4f8a5f4828331d41d023038e` remotely dereferences to that exact commit as `v0.5.0-observation-geometry-baseline`. From merged `main`, all 65 tests, compilation, dependency health, clean-worktree checks, and byte-identical real-package JSON/HTML/PNG reconstruction pass. Issue #335 / PR #336 carries the provenance-only lifecycle synchronization.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
