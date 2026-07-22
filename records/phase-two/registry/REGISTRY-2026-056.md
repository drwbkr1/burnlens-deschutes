# REGISTRY-2026-056 - Petes Lake U05 r002 terminal NWI intake

**Unit / issue / branch:** `P2O4-T33-U05R1` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Run / intake:** `BL-2026-07-22-petes-lake-nwi-context-r002` / `petes-lake-nwi-context-2026-002`

**Source commit:** `87a852c750fe7527bd018c32f630c8447e61fc47`

**Disposition:** `remediate`

**Next dependency:** `P2O4-T33-U05R2` offline observability remediation and complete disjoint r003 preflight

## Initialization and terms

An initial offline invocation supplied a seven-digit fractional UTC timestamp and was rejected before any r002 path existed. It made no network call and created no run state. The accepted initialization at `2026-07-22T02:54:31.466962Z` bound pushed source `87a852c750fe7527bd018c32f630c8447e61fc47`, all five r001 evidence identities, three tracked source/precheck records, twelve unique r002 assets, and disjoint custody paths.

The initialized 20,913-byte contract passed the external intake validator. One no-redirect/no-retry refresh of the five registered official FWS pages then passed from `2026-07-22T02:55:10.329541Z` through `2026-07-22T02:55:13.878514Z`. Its exact 5,354-byte receipt has SHA-256 `1cdbad419ccc9804cbbbeb1aa45466cb1fb882ae855ed3759cc91ced7ed48fbc`. That receipt authorizes r002 only.

## Ordered asset ledger

| Order | Asset / role | Dispatch receipt bytes / SHA-256 | Retained or promoted bytes / SHA-256 | Result |
|---:|---|---|---|---|
| 1 | `petes-lake-nwi-r002-wetlands-layer-metadata` | 862 / `c55e1c9f3d0fca9d04783558c4ca1afcc4a693b0f569da2576793d1814b2dffa` | 21,276 / `975c06d4c44ecedf23d1d5930ac1316913234ed0fd5b3a76fc365d07db466459` | promoted; exact registered identity; 43 qualified fields |
| 2 | `petes-lake-nwi-r002-wetlands-pre-count` | 908 / `9c7ffd000c9b9c3d9ab3fadeaaa2df56646031c04139155f8059b59f8d1edcb3` | 13 / `0aa3cb3ca1de6d4591eed691291545c02dfba8db948d9ec844d73e380d6c5b26` | promoted; count 623 |
| 3 | `petes-lake-nwi-r002-wetlands-pre-ids` | 902 / `a23d95354a53df4eb7cb174071f0596516cb6694f8d9406ae5ddc183de32d79e` | 5,662 / `68741e7dafb1177ee471c5f21be33074aab98a7c157fea349f86fcfe343c20f3` | promoted; 623 IDs |
| 4 | `petes-lake-nwi-r002-wetlands-features` | 905 / `d286a7459a0e23f208b53df4e6ba21124d6f449d130bbd03b63a3eff75a072ad` | 4,689,626 / `10d7a283c666d0cd6916b1058cf380a049f2651fe47f84ef5b7c035e35316ef1` | promoted; 623 features; no transfer truncation |
| 5 | `petes-lake-nwi-r002-wetlands-post-count` | 911 / `a7f7a0af621b9429053d32d5a7713fd8be99f31864b0c7a45206e447e6f73f57` | 13 / `0aa3cb3ca1de6d4591eed691291545c02dfba8db948d9ec844d73e380d6c5b26` | promoted; pre/post count exact |
| 6 | `petes-lake-nwi-r002-wetlands-post-ids` | 905 / `d8d2702e5d04f2a35004a43c754e2af9bc4b4908e54126e8ccbdc59de1336f17` | 5,662 / `68741e7dafb1177ee471c5f21be33074aab98a7c157fea349f86fcfe343c20f3` | promoted; pre/post IDs byte-identical |
| 7 | `petes-lake-nwi-r002-source-layer-metadata` | 859 / `e3823948901a61a0e0448a5225136d66b077ef14a289db42e3c2e2d756b1e51f` | 11,229 / `de5dcacb9531a380ef4c29167031f928e48add79e0410020928e316d5f98cf12` | promoted; exact registered identity |
| 8 | `petes-lake-nwi-r002-source-pre-count` | 905 / `5a841bdb72f597d2a470eb88f6eb5425f8d580767a1e76ec936df9aefe9d2058` | 0 / `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | failed at `PROVIDER_OPEN`; one attempt; no response object |
| 9-12 | source pre-IDs, features, post-count, post-IDs | none | none | authorized but unexecuted; dependency-blocked |

The Wetlands feature payload contains 623 unique object IDs, 117,510 coordinates, 623 outer rings, 15 hole rings, and 638 total rings in provider EPSG:3857; `exceeded_transfer_limit=false`. These are custody/structure facts only, not wetland fitness or label truth.

## Terminal identity and validation

| Evidence | Bytes | SHA-256 |
|---|---:|---|
| terminal r002 contract | 79,265 | `37cd244ecba3e19db978505fb1dbecfc08ac68752a2e41352fbdad5f9ad6479a` |
| immutable r002 plan | 20,684 | `ea1a23462f7395a2d8c5bf64e672d557c3aa6120106bdd78c038a84683c98a62` |
| r002 terms receipt | 5,354 | `1cdbad419ccc9804cbbbeb1aa45466cb1fb882ae855ed3759cc91ced7ed48fbc` |

- All nineteen terminal r002 evidence files are ignored, single-link, and unchanged: contract, plan, terms receipt, eight dispatch receipts, seven promoted payloads, and one zero-byte failed partial.
- The external intake validator passes with local-file verification against the terminal contract.
- All five r001 evidence hashes still match their registered values.
- The tracked worktree remained clean through the terminal provider transaction.
- Independent read-only audit confirms the seven promoted assets, exact Wetlands pre/post agreement, no transfer truncation, one terminal failed attempt, and four unexecuted later assets.

## Failure boundary and next action

The failed POST was durably dispatched, but no response object, headers, or body were obtained. Current code discards the underlying open exception. The retained evidence cannot distinguish HTTP status or redirect, timeout, DNS/TLS/socket failure, provider availability, request construction, or local interruption. No root-cause claim is supported.

R002 is immutable and terminal. Its promoted files may be rehashed and inspected read-only as failure evidence, but they may not be copied, moved, relabeled, partially finalized, selected for U05 fitness, or used to seed a new run. Issue #521 now registers `P2O4-T33-U05R2` and a wholly disjoint complete r003 reacquisition after privacy-safe failure-classification code passes offline and is pushed remote-equal. R003 is the final automatically authorized same-source attempt; another failure routes the milestone to a material decision exit.

U05 accepts zero reference pixels. U06 and every candidate, owner response, prototype label, sixth event, dataset, split, baseline, model, version, release, tag, deployment, field-validation, official, endorsed, operational, and emergency-ready claim remain blocked.
