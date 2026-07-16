# Cross-Event Source-Fitness Decision

## Checkpoint scope

Issue #361 asks whether the four exact Tepee and McKay Sentinel-2 products frozen by P2O4-T02 survive authenticated delivery, byte registration, native-pixel quality inspection, and pair-local content-registration gates. It does not create a label, patch set, dataset, partition, baseline, model, or application.

## Exact acquisition

Authenticated run `BL-2026-07-16-cross-event-optical-intake-r005` registered the exact four-archive package after four fail-closed attempts exposed early EOF, a transient public-metadata failure, a non-resumable OData route, and OneDrive hard-link races. The final package contains 4,551,170,756 provider bytes in ignored local storage. Every archive matches its OData size, MD5, BLAKE3, local SHA-256, ZIP/SAFE root, manifest, path, and CRC contract. Zero native provider bytes or secret material are committed.

The real machine added a second OneDrive staging link to the small registration metadata manifest. BurnLens therefore keeps the generic verifier strict by default but permits a cross-event-only metadata-manifest exception after one-read SHA-256, JSON schema/header, contract, acquisition-run, and every-asset hash comparison. All four provider archives remain single-linked. The public report exposes manifest link count `2`, SHA-256 `7827232e4986d8209fefd4ebbe160d3c9432bcd18562fad0587afcf6d79ed26c`, and reason `REGISTERED_PACKAGE_VERIFIED_WITH_MANIFEST_MULTILINK_EXCEPTION`.

## Native-pixel findings

| Event | Full-boundary pair quality | Registration | Disposition |
|---|---|---|---|
| Tepee 1144 NE / 2018 | 18,706 of 21,620 pixels eligible (86.5217%); 1,804 review-needed (8.3441%); 1,110 excluded (5.1341%) | one pass, one review-needed, one excluded; p95 `0.0976` pixel; max `0.1044` pixel | usable only with the SCL and window exclusions binding |
| McKay 1035 NE / 2017 | 12,359 of 12,359 pixels eligible (100%); zero review-needed or excluded | three of three pass; p95 `0.1008` pixel; max `0.1030` pixel | passes source-fitness gate |

Tepee W-01 is excluded because eligible coverage is insufficient. W-02 remains review-needed because the cross-band consensus exceeds the gate. W-03 passes. These states never assign burned or background. McKay passes all three event-scaled windows.

![BurnLens cross-event source-fitness evidence](../../../samples/cross-event/phase-two/CROSS-EVENT-SOURCE-FITNESS-2026-001.png)

## Decision

Decision code: `ACCEPT_CROSS_EVENT_SOURCE_FITNESS_WITH_EXCLUSIONS`.

Accept the exact Tepee and McKay source pairs for the next bounded cross-event label-protocol transfer and separate software-QA checkpoint. Preserve every current event/scene/geography/time group. Apply Tepee's pixel and window exclusions; do not tune them away, shrink the MTBS boundary, mosaic another tile, or call the groups dataset partitions.

The next checkpoint must test whether the established five-state burn-scar proposal can transfer across both events with transparent unknown/excluded/review coverage. Dataset and split construction remain deferred until cross-event proposal evidence and its separate QA pass.

## Pre-tag trace remediation

Issue #361 / PR #362 merged the analytical checkpoint at `6a6da910849daefa918ed56af6631b2ec44bc211`. Fresh merged-main semantic verification withheld the release tag after finding that the manifest named implemented schema `burn-scar-five-state-schema-v0.1.0` while the report's `label_schema_version` named design protocol `burn-scar-label-protocol-v0.1.0`. Issue #363 separates those identifiers, fails closed if the frozen feasibility schema drifts, and regenerates the real artifacts from source `cf1d9101e2760bf7d779b6fae68e605bb8809c1c` as run `BL-2026-07-16-cross-event-source-fitness-r006`.

The remediated run preserves every source, event, pixel, window, metric, decision, lineage field, and input hash from `r005`. JSON, HTML, and PNG expose both governing label protocol and implemented five-state schema. Issue #363 closed through PR #364 at merge `01c3aa4abeb89e3f15771571276a25d33e44d390`. A fresh no-hardlink merged-main clone passes 129 tests, packaging, exact manifest/semantic/render/LF/link/raw/secret gates, original-resolution review, and live browser review. Verified annotated tag object `eca7ba5362518684f2a1e25d5abdbc1707e24a61` remotely peels to that merge as `v0.11.0-cross-event-source-fitness-baseline`.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
