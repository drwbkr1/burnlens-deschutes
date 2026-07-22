# PRECHECK-2026-047 - Petes Lake replacement-post metadata selection

**Unit / issue / branch:** `P2O4-T33-U03` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Source commit:** `cfa5d1923feb413859c3aa20ebc40df3e0ee2ee6`

**Run:** `BL-2026-07-21-petes-lake-replacement-post-selection-r001`

**Checked:** 2026-07-21T19:57:43Z

## Decision

`SELECT_REPLACEMENT_POST_AUTHORIZE_CONTRACT_REVISION_ONLY`.

The exact failed U03 r001 report is unchanged at SHA-256 `ac9befd021d71ff779ec56ddefc894f4e39b92e64e65c2c4afb815663d1ad443`. Current public STAC metadata returns the frozen six-item Sentinel-2A / 10TEP / orbit 13 / PB05.10 remediation roster. The deterministic selector rejects three early scenes under the conservative official-incident timing boundary and rejects two later scenes above the established 20% catalogue-cloud gate.

The October 19 product is the only remaining candidate. Current OData agrees on UUID, SAFE identity, 1,195,226,823 bytes, online state, sensing time, platform, tile, orbit, baseline, type, MD5, BLAKE3, and two-decimal cloud representation. Its 0.564076% tile-wide STAC snow value remains an unresolved local SCL/SNW and render risk.

This was a public metadata-only run. It used no credential and acquired zero provider product/archive bytes. It authorizes only an exact committed replacement contract and a new clean preflight. No provider request, custody, local pixel, source acceptance, U04, reference, candidate, response, label, dataset, split, baseline, or model is authorized.
