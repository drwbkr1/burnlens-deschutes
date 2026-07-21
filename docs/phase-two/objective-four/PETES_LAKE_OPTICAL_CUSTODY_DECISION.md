# Petes Lake Optical Custody Decision

## Decision

`PASS_PETES_LAKE_OPTICAL_CUSTODY_AUTHORIZE_U03_ONLY`.

P2O4-T33-U02 run `BL-2026-07-21-petes-lake-optical-intake-r001` acquired the exact Petes Lake Sentinel-2 pre and post archives as separate ordered transactions. Pre passed live metadata, one-attempt download, provider checksum, local SHA-256, ZIP/SAFE structure, CRC, no-replace promotion, immutable registration, private-state, and fresh-reopen gates before post metadata or archive access began. Post then passed the same gates.

The pre archive is 1,185,284,273 bytes with local SHA-256 `c5b6ededc5a264fcc617f2712093b847351c5b8ed78f2ea9ce0ebc3a33e1bc34`. The post archive is 1,243,068,088 bytes with local SHA-256 `636a3cafe66c16cb20c9fd490a7ad448c939e3476d9ac0a404576638c2cd3a25`. Both match their exact provider MD5 and BLAKE3 values. Each archive contains the required single SAFE root, 95 members, a manifest, and passing CRC checks.

The acquisition process created the complete private aggregate and public report, then exited nonzero because the CLI tried to read the aggregate decision from the wrong result level. This post-success display defect did not change custody. It is retained, regression-tested, and fixed by commit `62e920e272e83b67f096659f77a25eac129f707c`. Credential-free verification from that exact pushed commit freshly reopened both packages and passed with no credential environment.

Native archives, registration manifests, and private run states remain ignored, untracked, repository-local, no-overwrite, and single-link. No credential, token, authorization header, cookie, or provider archive is published. `REGISTRY-2026-047` binds every exact public and private artifact identity.

U02 authorizes only P2O4-T33-U03 source fitness. It does not establish usable pixels. U03 must inspect exact SAFE metadata, bands, CRS, grids, transforms, nodata, SCL/SNW, local cloud/smoke/shadow/snow, temporal fitness, registration, and actual rendered pre/post/change evidence. No reference, candidate, owner decision, prototype label, dataset, split, baseline, model, metric, field-validation, official, endorsed, emergency-ready, or operational claim advances.

Primary public evidence: [`PETES-LAKE-OPTICAL-CUSTODY-2026-001.json`](../../../samples/cross-event/phase-two/petes-lake/PETES-LAKE-OPTICAL-CUSTODY-2026-001.json).
