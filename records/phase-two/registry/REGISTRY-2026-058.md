# REGISTRY-2026-058 - Petes Lake U05R2 terminal r003 NWI intake

**Unit / issue / branch:** `P2O4-T33-U05R2` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Run / intake:** `BL-2026-07-22-petes-lake-nwi-context-r003` / `petes-lake-nwi-context-2026-003`

**Source commit:** `afcbbd2331e2106422940754c6f86b8022e1764b`

**Disposition:** `defer`

**Next dependency:** `P2O4-T33-U11` material-decision closeout only; no r004, U05 scientific-fitness run, or U06-U10 production execution is authorized by this record

## Initialization and current terms

Offline initialization at `2026-07-22T04:27:51.348096Z` bound all five r001 files, all nineteen r002 files, the exact tracked source/terms/precheck/registry inputs, twelve disjoint r003 assets, and the pushed source commit above. The initial contract was 27,152 bytes with SHA-256 `dfa4c4d66801076bdfa0e77b6abf5088358b71c2f9d35bbc196a3ec6508e7b35`; the immutable plan is 26,923 bytes with SHA-256 `6f980a77840c7b69bf5873ab43ec92ab1db8e86b0db1ffdd6613ab56216fc42d`. The exact external validator passed before provider access.

One no-redirect, no-retry refresh of the five registered official USFWS pages ran from `2026-07-22T04:28:31.979411Z` through `2026-07-22T04:28:36.235576Z`. The 5,354-byte receipt has SHA-256 `83f9f36cf8d6415a78c25055762a211039443602e92d3b2db20f110c50c74bcc` and decision `PASS_CURRENT_OFFICIAL_NWI_TERMS_SEMANTICS_FOR_BOUNDED_PROVIDER_INTAKE`. It authorizes r003 only and does not resolve raw redistribution; provider responses and feature attributes remain ignored and unpublished.

## Ordered asset ledger

| Order | Asset / role | Attempt timing (UTC) | Dispatch receipt bytes / SHA-256 | Retained or promoted bytes / SHA-256 | Result |
|---:|---|---|---|---|---|
| 1 | `petes-lake-nwi-r003-wetlands-layer-metadata` | `04:29:10.381812` / `04:29:56.092264` / `04:30:01.625183` | 862 / `1301720b26a381b104bb8eedf93580c0033ad0caa7a67b1cede7309d9cebf4bf` | 21,276 / `975c06d4c44ecedf23d1d5930ac1316913234ed0fd5b3a76fc365d07db466459` | promoted; exact registered identity; 43 qualified fields |
| 2 | `petes-lake-nwi-r003-wetlands-pre-count` | `04:33:21.200284` / `04:33:24.245768` / `04:33:27.478031` | 908 / `b6733dfabebd3661aefce2fdb2c7c60ef3c2782bf96162bc309226bccc034dcf` | 13 / `0aa3cb3ca1de6d4591eed691291545c02dfba8db948d9ec844d73e380d6c5b26` | promoted; count 623 |
| 3 | `petes-lake-nwi-r003-wetlands-pre-ids` | `04:33:33.397624` / `04:33:36.447070` / `04:33:43.408362` | 902 / `f7703c45d0e2479cc226ef99569e02d3d40d9890d6f4b059b5f7cd0504890b61` | 5,662 / `68741e7dafb1177ee471c5f21be33074aab98a7c157fea349f86fcfe343c20f3` | promoted; 623 unique IDs |
| 4 | `petes-lake-nwi-r003-wetlands-features` | `04:33:49.290743` / `04:33:52.584763` / `04:34:07.183656` | 905 / `0a7fbb49077cb9f2f8e48eea486670e3ed623f22e09bf6df263b1bb7b80e17ce` | 4,689,626 / `10d7a283c666d0cd6916b1058cf380a049f2651fe47f84ef5b7c035e35316ef1` | promoted; 623 features; no transfer truncation |
| 5 | `petes-lake-nwi-r003-wetlands-post-count` | `04:34:16.344212` / `04:34:21.043807` / `04:34:25.789943` | 911 / `6af51a13ffc666bbac2e239e78c1c2b0b9a89d196bc3798ab3165ffd2e6a303c` | 13 / `0aa3cb3ca1de6d4591eed691291545c02dfba8db948d9ec844d73e380d6c5b26` | promoted; byte-identical to pre-count |
| 6 | `petes-lake-nwi-r003-wetlands-post-ids` | `04:34:33.519576` / `04:34:37.617713` / `04:34:47.233139` | 905 / `db376cf2eefe84cf902491485989db2fe926ba4e185a7d7eb380b8a18715f425` | 5,662 / `68741e7dafb1177ee471c5f21be33074aab98a7c157fea349f86fcfe343c20f3` | promoted; byte-identical to pre-IDs |
| 7 | `petes-lake-nwi-r003-source-layer-metadata` | `04:40:22.026570` / `04:40:24.968977` / `04:40:28.439035` | 859 / `1a37b7381e4405f42c18ba37ad231b35cafa321fa6b4032626d1aea0e05ee324` | 11,229 / `de5dcacb9531a380ef4c29167031f928e48add79e0410020928e316d5f98cf12` | promoted; exact registered Data Source identity |
| 8 | `petes-lake-nwi-r003-source-pre-count` | `04:41:27.365480` / `04:41:31.491166` / `04:41:35.012285` | 905 / `5296195e6495af4faa3393276a046ceb76ba35c1210c80587728ba45d508d3be` | 0 / `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | failed terminally at `PROVIDER_OPEN`; `NWI_TRANSFER_OR_STRUCTURE_FAILURE_NO_RETRY`; diagnostic `{category: http, http_status: 500}` |
| 9-12 | Data Source pre-IDs, features, post-count, post-IDs | none | none | none | authorized but unexecuted; dependency-blocked |

The timing cells list attempt start, durable dispatch, and completion on 2026-07-22. The observed HTTP status is the complete supported diagnostic. It does not identify whether the provider, intermediary, request, service implementation, network path, or another component caused the response.

## Exact retained state

| Evidence | Bytes | SHA-256 |
|---|---:|---|
| terminal r003 contract | 85,612 | `d85dc5ec8991a50605d4501ee91cb717e4089a5243dba40e6531f520bd5d8dc3` |
| immutable r003 plan | 26,923 | `6f980a77840c7b69bf5873ab43ec92ab1db8e86b0db1ffdd6613ab56216fc42d` |
| r003 terms receipt | 5,354 | `83f9f36cf8d6415a78c25055762a211039443602e92d3b2db20f110c50c74bcc` |
| failed asset-eight partial | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

- The terminal state is exactly seven promoted, one failed, and four authorized-unexecuted assets.
- All r003 contract, plan, terms, dispatch, promoted-payload, and failed-partial files are ignored, untracked, non-symlink, non-reparse, and single-link.
- All five r001 and nineteen r002 bindings remain exact. R003 uses disjoint run, quarantine, and raw-package roots and copies no prior payload.
- Wetlands pre/post counts are byte-identical at 623. Pre/post ID arrays are byte-identical, contain 623 unique IDs, and match the 623 feature IDs including order.
- The EPSG:3857 feature payload contains 623 nonempty polygons, 638 rings, 117,510 finite vertices, 623 outer rings, and 15 holes; zero ring is malformed or open. These are custody and structure facts only.
- The external intake validator, invoked with local-file verification, passes against the terminal contract. BurnLens reload also rehashes the exact failed partial.
- The tracked worktree remained clean at source commit `afcbbd2331e2106422940754c6f86b8022e1764b` throughout the transaction.

## Failure boundary and disposition

R003 was the final automatically authorized same-source attempt. It is never retried, continued, finalized, copied, partially selected for U05 fitness, or used to seed another run. Assets 9-12 remain unexecuted. No r004 exists without a later explicit owner amendment.

U05 scientific fitness therefore does not pass. The seven promoted files cannot partially satisfy wetland, temporal-support, optical-grid-coverage, or source-precedence gates. U06 through production U10 remain unexecuted and deferred. Petes Lake does not become a sixth accepted event, and the accepted prototype state remains five burned and five background regions across five complete events.

The milestone disposition is `defer`, not permanent exclusion. A future official fallback may be registered as a new issue-backed evidence unit with fresh source, terms, custody, integrity, fitness, and failure-retention gates. It may not reuse r001-r003 identities or partial payloads. This record creates no candidate, owner response, prototype label, dataset, split, baseline, model, metric, deployment, field-validation, official, endorsed, operational, or emergency-ready claim.
