# P2O4-T11 Current Reference Inventory Decision

**Issue:** #411

**Branch:** `codex/p2o4-t11-reference-evidence-remediation`

**Software:** BurnLens `0.21.0`

**Source implementation:** `98a9895d203c778dad332db5bdc62b498aa2cd00`

## Decision

`ACQUIRE_CURRENT_CROSS_PROGRAM_REFERENCE_BUNDLES_DEFER_LABELS_DATASET_MODEL`.

The cycle began by rerunning the exact proposal, independent QA, and single-reviewer reconciliation. All public outputs were byte-identical to the authoritative checkpoint when given the same inputs and timestamps. The weakness is therefore evidence fitness, not pipeline drift.

Fresh primary-source inspection found a material source-currentness problem. The official 2026 Burn Severity Portal release says the archive was reprocessed and redistributed in late 2025. The two `SOURCE-2026-013` annual ImageServer clips remain immutable historical proposal provenance, but they are not sufficient current evidence for a new promotion decision.

The current official catalog supplies seven exact records:

- Darlene: BAER and RAVG;
- McKay: MTBS and RAVG; and
- Tepee: BAER, MTBS, and RAVG.

This is stronger cross-event availability than the prior two-clip path. It is not product fitness. Exact product bytes and pixels remain uninspected, program differences remain unresolved, and zero labels change.

## Shipped bounded improvement

BurnLens `0.21.0` adds a public, property-only WFS capture and a fail-closed seven-product normalization contract. It publishes `CROSS-EVENT-REFERENCE-INVENTORY-2026-001` as JSON, semantic HTML, and a 1800-by-1340 evidence card.

The tool fails on catalog identity drift, unexpected events/programs, geometry, duplicates, field-type changes, or missing records. It records source response and normalized hashes, software, commit, run, AOI, target, label schema, and null dataset/split/baseline/model versions.

## What this does not prove

It does not download or inspect a product bundle, compare pixels, promote a label, create a dataset, train a model, provide field validation, or establish official or endorsed status. Reviewer two remains waived and absent; no inter-rater evidence, consensus, or adjudication exists.

## Next gate

Receive and preserve exact current bundles; inspect their attribution, notices, bytes, identity, CRS, grids, nodata, masks, and class domains; then compare current cross-program pixels with the optical evidence and reviewer dispositions. Publish a rendered fitness decision before changing any label.

## Release status

Issue #411 / PR #415 merged at `f96146aa0702d27eef4964cb61bd7a05d566d7c3`. Annotated tag object `0370bedfce1279da2d104c1ebfd3c1d143ce79ca` remotely peels to that merge, but final release verification found checkout-dependent JSON/HTML bytes because their directory lacked an explicit LF rule. The tag remains analytical history, not a verified repository baseline. Issue #417 / PR #418 ships the BurnLens 0.21.1 checkout-stability patch at merge `65ef67a206ebfa697e6047ca09ce26eec6a24dd7`; verified tag object `1b84f92cf4e7249e524fab095e233192698b7666` remotely peels to that merge. Issue #416 owns the next scientific gate.
