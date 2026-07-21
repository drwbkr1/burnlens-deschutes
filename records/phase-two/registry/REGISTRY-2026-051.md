# REGISTRY-2026-051 - Petes Lake replacement optical custody

**Unit / issue / branch:** `P2O4-T33-U03` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Aggregate run:** `BL-2026-07-21-petes-lake-optical-remediation-intake-r001`

**Transaction run:** `BL-2026-07-21-petes-lake-optical-post-remediation-r001`

**Trace commit:** `9cd81518c8fd859a950eab263e82dc9c9e406c59`

**Decision:** `PASS_PETES_LAKE_REPLACEMENT_OPTICAL_CUSTODY_AUTHORIZE_U03_SOURCE_FITNESS_R002_ONLY`

## Public tracked evidence

| Artifact | Bytes | SHA-256 | State |
|---|---:|---|---|
| `samples/cross-event/phase-two/petes-lake/PETES-LAKE-OPTICAL-REMEDIATION-CUSTODY-2026-001.json` | 22,246 | `e23d601959d09fb54fc6409f5a073df4f1a3a3a8a0d040e04a9b46c2594537b1` | exact aggregate custody report; semantic SHA-256 `78c888b4a3b954c4038a3454773b1cd7c922bc5f71957524e803ee6534d71f75` |
| `docs/phase-two/objective-four/PETES_LAKE_REPLACEMENT_OPTICAL_CUSTODY_DECISION.md` | 3,523 | `f7a1ab5a021f4fa0c260325deee9af4bc133dfca094e206e02f3dab7a93bc03d` | bounded human-readable custody decision |
| `records/phase-two/prechecks/PRECHECK-2026-049.md` | 2,766 | `97b628051051ddd7f616cc4b1c54830f29ad623855dd3a69d3f67794bafc1782` | production and post-transaction gate record |

The public report was created once as an unignored, untracked, single-link regular file. The private aggregate binds its exact relative path, bytes, and SHA-256. Public and private objects contain the same canonical semantic record and semantic hash.

## Ignored exact replacement custody

| Artifact | Bytes | SHA-256 | Provider identity / state |
|---|---:|---|---|
| `downloads/phase-two/raw/petes-lake-s2-optical-post-remediation-v0.2.0/S2A_MSIL2A_20231019T190411_N0510_R013_T10TEP_20241107T024526.SAFE.zip` | 1,195,226,823 | `8bf6ffac0d46d17b6f3716250aed9dff49b9f89b62a310c296a5d36f41a0e1d9` | MD5 `4cf05a073b4c67f5e92e052ed1eb32bc`; BLAKE3 `1b28f566aee5619ea9a48c8dd042f209194a40989ba4b54cfe4e14904a0ad878`; single-link, ignored, untracked, no-overwrite |
| replacement `.burnlens-registration.json` | 989 | `65c9ca00af753d6151275c2ed7088da03fc1da5b5a5d49dbf2dd18f4f6bab93c` | contract SHA-256 `d271b16da7581eed3b0f2efdc9d8cf9433673ac86d38929951774a191daefee3`; single-link immutable registration |
| `downloads/phase-two/runs/P2O4-T33-U03/BL-2026-07-21-petes-lake-optical-post-remediation-r001.json` | 11,748 | `54dc16258dff0265cd2177bf04a1ca6e1358d2b9f3a21cc8fc11ebe05c9770b0` | private single-transaction state; single-link, ignored, untracked |
| `downloads/phase-two/runs/P2O4-T33-U03/BL-2026-07-21-petes-lake-optical-remediation-intake-r001.json` | 24,685 | `a63b3fb9f4c10b239c0da9a0129da4b87fdec6a31d31866f3c767b580d873f81` | private aggregate binding public report; single-link, ignored, untracked |

The archive contains 95 members and 1,195,191,837 uncompressed bytes under exactly `S2A_MSIL2A_20231019T190411_N0510_R013_T10TEP_20241107T024526.SAFE`. ZIP magic, SAFE root, manifest, complete CRC, exact bytes, MD5, BLAKE3, local SHA-256, no-replace promotion, registration, and repeated fresh reopen all pass. Quarantine is absent after promotion.

## Retained input and preservation bindings

| Evidence | Exact binding | Result |
|---|---|---|
| Contract gate | `petes-lake-optical-post-remediation-contract-v0.1.0`; contract checkpoint `ab6ecc04d847aba848f0fc1f384405b10f0d8f9f`; REGISTRY-2026-050 | pass; one exact provider UUID only |
| Source selection | `PETES-LAKE-SOURCE-REMEDIATION-2026-001.json`; 10,127 bytes; SHA-256 `7fa82a61fa70d47364db29493700beedd60c9114a4b3a6d8ddbafdf77aecfc8c` | pass; immutable contract-revision selection retained |
| Failed planned pair | `PETES-LAKE-SOURCE-FITNESS-2026-001.json`; 56,285 bytes; SHA-256 `ac9befd021d71ff779ec56ddefc894f4e39b92e64e65c2c4afb815663d1ad443` | unchanged; failure remains authoritative for the original post |
| Original custody | `PETES-LAKE-OPTICAL-CUSTODY-2026-001.json`; 23,521 bytes; SHA-256 `46f72f7fa7dc3b6fc3f96f6023b0d7b14f6990bcef8945a878ae04600d2e571d` | unchanged |
| Retained pre | `petes-lake-s2-optical-pre-v0.1.0`; 1,185,284,273 bytes; local SHA-256 `c5b6ededc5a264fcc617f2712093b847351c5b8ed78f2ea9ce0ebc3a33e1bc34` | freshly reverified; no reacquisition or mutation |
| Replacement terms | TERMS-2026-026; CDSE Terms 77,530 / `e17c490...`; Sentinel notice 115,881 / `fa2955...` | exact current source bytes pass; native redistribution remains excluded |

## Transaction, verification, and retained failures

- Production started at 2026-07-21T21:05:57.352596Z from clean remote-equal trace commit `9cd81518c8fd859a950eab263e82dc9c9e406c59`.
- Current terms observed at 2026-07-21T21:06:11.103154Z; live OData metadata observed at 2026-07-21T21:06:32.523750Z.
- Download status: `DOWNLOADED`; one attempt; resumed from zero; exact singleton only. Wrapper decision and credential-free final verifier passed; wrapper exit code zero.
- Credential variables are absent after the wrapper. No password, token, authorization header, cookie, secret, protected-store detail, or retained S3 path appears in public evidence.
- Post-transaction verifier attempt at 2026-07-21T21:12:49.731932Z failed closed on a transient remote-head query. Direct `ls-remote` immediately proved the local/remote head unchanged at `9cd81518...`.
- Post-transaction verifier attempt at 2026-07-21T21:13:25.729861Z failed closed on a transient official-terms `URLError`. No credential or custody path changed.
- Bounded retry at 2026-07-21T21:13:55.263189Z passed every credential-free gate. Transport availability is not scientific evidence; both failed attempts remain disclosed.

## Legacy-server containment

The cleanup audit identified five stale `python -m http.server` processes: two launchers rooted in the retired OneDrive checkout, their two Codex-runtime children, and one generic Python listener. Exact PID, parent PID, executable, command, and loopback-listener identity were verified before termination. The only listeners were `127.0.0.1:8765` and `127.0.0.1:8767`. All five processes stopped, both ports closed, and no acquisition process remains. No old-checkout file was used or changed.

## Gate disposition and next dependency

- Source/terms/access/custody/provenance/hash/ignore/untracked/single-link/no-overwrite/privacy/warning/reproducibility gates: pass for replacement custody.
- Focused contract/provider suite before transaction: 95 passed. Full repository before transaction: 455 passed plus 50 subtests; 20 existing NumPy deprecation warnings. Production wrapper and final verifier pass on actual provider bytes.
- Catalogue cloud/snow remains discovery context only. No local SCL/SNW, usable-fraction, registration, or render gate has yet passed for the replacement pair.
- Disposition: `pass` for replacement custody only. Next: `P2O4-T33-U03_REPLACEMENT_SOURCE_FITNESS_R002` using the immutable original pre plus exact replacement post.

No U04, reference, candidate, owner response, prototype label, sixth accepted event, dataset, split, baseline, model, metric, field-validation, official, endorsed, operational, or emergency-ready claim advances.
