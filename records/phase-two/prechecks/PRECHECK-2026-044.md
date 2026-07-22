# PRECHECK-2026-044 - Petes Lake cloud-metadata precision reconciliation

**Unit / issue / branch:** `P2O4-T33-U02` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Code checkpoint:** `c4987ce53a7606d828caf2db134a28f160bc867d`

**Checked:** 2026-07-21T18:30:01Z

## Decision

`PASS_PETES_LAKE_CLOUD_METADATA_RECONCILIATION_AUTHORIZE_U02_PREFLIGHT_ONLY`.

The first public metadata probe after active-custody migration failed closed before credentials or provider-product access. Current CDSE OData returned exact Sentinel-2 `cloudCover` values `0.000358` and `0.008789`; the frozen P2O4-T33-U01 STAC representation retained `0.0` and `0.01`. UUID, SAFE identity, size, online state, MD5, and BLAKE3 were unchanged.

BurnLens does not treat this as permission to weaken an exact-source gate. Contract `petes-lake-optical-intake-contract-v0.2.0` now preserves and requires each exact current OData value, preserves the frozen U01 STAC value separately, and requires deterministic decimal `ROUND_HALF_UP` comparison at two decimal places. The exact pairs reconcile as `0.000358 -> 0.00` and `0.008789 -> 0.01`. A raw-value drift, invalid percentage, normalization drift, STAC-binding drift, or identity/checksum drift still fails closed.

Current official CDSE documentation describes Sentinel-2 OData `cloudCover` as a `DoubleAttribute` and STAC `eo:cloud_cover` as a complementary catalogue representation rather than an OData replacement. Neither value establishes local pixel fitness. U03 must still inspect the delivered SCL/SNW layers, local cloud, smoke, shadow, and snow, registration, grids, and real rendered pixels.

## Exact live gate

- Run: `BL-2026-07-21-petes-lake-optical-metadata-reconciliation-r001`.
- Tracked report: `samples/cross-event/phase-two/petes-lake/PETES-LAKE-OPTICAL-METADATA-RECONCILIATION-2026-001.json`, 8,750 bytes, SHA-256 `b1062e8e8f298087852cd0199d83482a20873bcc90bd5d777c5c6e91c69aaa52`.
- Frozen U01 source binding: 1,213,547 bytes, SHA-256 `1d99d32f6610e64eed5a310d58c9ee730e6f9be691b6f7eb2ed00044018b559c`.
- Exact live metadata snapshot: SHA-256 `248fbfbea4e82a6f93360fdb6cde987b31898278dc4c6faaa4f288dbfcc92847`.
- Production credential-free preflight passed from exact local and remote commit `c4987ce53a7606d828caf2db134a28f160bc867d` immediately before the live metadata run.
- Focused Petes/provider tests: 64 passed. Full repository suite: 395 passed with 20 existing NumPy deprecation warnings. Compilation and diff hygiene passed.

## Custody and non-implications

The run used only public OData metadata. It loaded no credential, requested no token, requested or downloaded zero provider product/archive bytes, and created no raw, quarantine, private run-state, aggregate, or custody-report target. U02 acquisition is not passed; U03 and all later units remain closed.

The report must be committed, pushed, registered, and recorded on issue #521 before the exact production pre-archive preflight. Only after that clean-commit gate may the pre archive transaction be considered. The post archive remains blocked until the pre archive independently passes every acquisition, checksum, archive, promotion, private-state, and fresh-reopen gate.

No Petes Lake pixel, reference, candidate, owner decision, prototype label, dataset, split, baseline, model, metric, official status, endorsement, field validation, emergency readiness, or operational claim advances through this remediation.
