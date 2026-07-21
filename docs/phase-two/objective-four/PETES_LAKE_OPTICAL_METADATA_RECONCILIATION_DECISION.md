# Petes Lake Optical Metadata Reconciliation Decision

## Decision

`PASS_PETES_LAKE_CLOUD_METADATA_RECONCILIATION_AUTHORIZE_U02_PREFLIGHT_ONLY`.

After active-custody migration, BurnLens stopped before provider access because current CDSE OData exposed pre/post `cloudCover` values `0.000358` and `0.008789`, while the immutable P2O4-T33-U01 STAC evidence retained `0.0` and `0.01`. UUIDs, SAFE names, sizes, online state, MD5, and BLAKE3 remained exact.

The v0.2.0 intake contract does not replace or relax either source. It requires each exact current OData value, preserves the frozen U01 STAC value separately, and requires deterministic decimal `ROUND_HALF_UP` reconciliation at two decimal places. Both records pass that bounded comparison. Raw-value, normalization, identity, or checksum drift still fails closed.

Run `BL-2026-07-21-petes-lake-optical-metadata-reconciliation-r001` is bound by `REGISTRY-2026-046`. It used public metadata only, loaded no credential, requested no token, requested or downloaded zero provider product/archive bytes, and created no custody output. The result authorizes only a new clean production preflight after its exact evidence is committed, pushed, and recorded on issue #521.

U02 remains incomplete. Pre archive custody must pass before post access; delivered SCL/SNW, local cloud/smoke/shadow/snow, registration, and rendered-pixel fitness remain U03 gates. No pixel, reference, candidate, owner decision, label, dataset, split, baseline, model, official, field-validated, endorsed, emergency-ready, or operational claim advances.

Primary normalized evidence: [`PETES-LAKE-OPTICAL-METADATA-RECONCILIATION-2026-001.json`](../../../samples/cross-event/phase-two/petes-lake/PETES-LAKE-OPTICAL-METADATA-RECONCILIATION-2026-001.json).
