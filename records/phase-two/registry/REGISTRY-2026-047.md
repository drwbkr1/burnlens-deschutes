# REGISTRY-2026-047 - Petes Lake U02 exact optical custody

**Unit / issue / branch:** `P2O4-T33-U02` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Aggregate run:** `BL-2026-07-21-petes-lake-optical-intake-r001`

**Acquisition trace commit:** `31eedcddff0a712001181fd282f18f0e41ed5412`

**Post-success CLI fix:** `62e920e272e83b67f096659f77a25eac129f707c`

**Decision:** `PASS_PETES_LAKE_OPTICAL_CUSTODY_AUTHORIZE_U03_ONLY`

## Public tracked output

| Artifact | Bytes | SHA-256 | State |
|---|---:|---|---|
| `samples/cross-event/phase-two/petes-lake/PETES-LAKE-OPTICAL-CUSTODY-2026-001.json` | 23,521 | `46f72f7fa7dc3b6fc3f96f6023b0d7b14f6990bcef8945a878ae04600d2e571d` | exact aggregate custody report; semantic SHA-256 `a9218a830d729af8712b525acf5365f6ed1d355407947606f1491c538f30f748` |
| `docs/phase-two/objective-four/PETES_LAKE_OPTICAL_CUSTODY_DECISION.md` | 2,356 | `8ab768be6e8cc136a00c616e852422bc443b7a676c0fc1cd264ed075f401de0b` | bounded human-readable custody decision |

## Ignored exact archive custody

| Role / run | Archive | Bytes | Local SHA-256 | Provider MD5 / BLAKE3 | Archive gate |
|---|---|---:|---|---|---|
| pre / `BL-2026-07-21-petes-lake-optical-pre-r001` | `downloads/phase-two/raw/petes-lake-s2-optical-pre-v0.1.0/S2A_MSIL2A_20230721T185921_N0510_R013_T10TEP_20240911T103205.SAFE.zip` | 1,185,284,273 | `c5b6ededc5a264fcc617f2712093b847351c5b8ed78f2ea9ce0ebc3a33e1bc34` | `c41d10e4e895839132c0ad4ee47100e1` / `49d13b491c1e4a979d65dc870daf2d72f940bfc910abb19c00e1a485992ed17b` | 95 members; 1,185,249,287 uncompressed bytes; expected SAFE root; manifest present; CRC pass |
| post / `BL-2026-07-21-petes-lake-optical-post-r001` | `downloads/phase-two/raw/petes-lake-s2-optical-post-v0.1.0/S2A_MSIL2A_20231029T190511_N0510_R013_T10TEP_20241106T074945.SAFE.zip` | 1,243,068,088 | `636a3cafe66c16cb20c9fd490a7ad448c939e3476d9ac0a404576638c2cd3a25` | `bf9383d434448998f5025494d0a43320` / `9814e80893321d86b9aec796651aaf811d8e31df6ed98413519bbeab1141d105` | 95 members; 1,243,033,102 uncompressed bytes; expected SAFE root; manifest present; CRC pass |

Both downloads used one attempt from offset zero. Every archive is a single-link regular file, ignored, untracked, no-overwrite, and accepted as an unchanged registered package by the final credential-free verifier.

## Ignored registrations and private states

| Artifact | Bytes | SHA-256 | State |
|---|---:|---|---|
| pre `.burnlens-registration.json` | 941 | `260b0d3ae7c5415c110851874b09a43bf2e2b3c83e0539a764d8c0bd94077f32` | exact immutable registration |
| post `.burnlens-registration.json` | 944 | `c1321b878fae9495d7eb8810a43c0b4b5254053373b91459fa8f42951c3173d7` | exact immutable registration |
| `downloads/phase-two/runs/P2O4-T33-U02/BL-2026-07-21-petes-lake-optical-pre-r001.json` | 8,766 | `cbbea6c630eeb28544d0d0f37f3f2cc9541f9556226460169306e0be2a34d1c7` | private pre transaction state |
| `downloads/phase-two/runs/P2O4-T33-U02/BL-2026-07-21-petes-lake-optical-post-r001.json` | 8,777 | `7aa02f6169651249bf0d9754de04b8ab824680edfdfb404c319922621e12bbec` | private post transaction state |
| `downloads/phase-two/runs/P2O4-T33-U02/BL-2026-07-21-petes-lake-optical-intake-r001.json` | 24,552 | `ec5e6be00ef0b635b036450a6ee0747caf001d50700ae8eb4299b4a575a3b3ee` | private aggregate state binding planned public bytes |

Every listed file is single-link, ignored, and untracked. Quarantine contains zero files after successful no-replace promotion. No token, password, authorization header, cookie, credential, or private credential-store detail is retained.

## Code remediation artifacts

| Artifact | Bytes | SHA-256 | State |
|---|---:|---|---|
| `burnlens/acquire_petes_lake_optical.py` | 5,333 | `0551674fd0a0679bf55ecbd76e9aade9aa50952780a59e8e133bdcceeec5cea7` | exact aggregate-decision extraction with missing-decision fail close |
| `tests/test_petes_lake_optical_contract.py` | 41,763 | `d94cb4f8696d18c5e8d4fb3ad6e4ff04d7c3a1bff4691542e15188f3bcb36166` | regression fixture uses the real semantic-result shape |

## Gate disposition

- Exact live metadata, transaction order, UUID/SAFE/size, provider checksum, local SHA-256, archive magic, expected SAFE root, manifest, CRC, registration, no-replace promotion, private state, aggregate binding, fresh reopen, ignore, untracked, single-link, privacy, warning, and reproducibility gates: pass.
- Pre observed at 2026-07-21T18:40:43.953482Z; post observed only after pre pass at 2026-07-21T18:43:18.731216Z.
- Retained defect: after all output writes, the original CLI invocation raised `KeyError: 'decision'` because the public aggregate uses `semantic_record.decision`. It caused a nonzero wrapper exit but no custody mutation. Direct verifier passed; commit `62e920e272e83b67f096659f77a25eac129f707c` fixes and regression-tests display extraction without reacquisition.
- Verification: 64 focused tests; full suite 395 passed with 20 existing NumPy deprecation warnings; compilation and diff hygiene pass; final credential-free `--verify-only` pass from the exact pushed fix commit; zero acquisition processes remain.
- Disposition: `pass` for U02 exact optical custody. Next dependency: U03 source-fitness and real-render inspection from these immutable packages.

U02 creates no usable-pixel, reference, candidate, owner, label, dataset, split, baseline, model, metric, field-validation, official, endorsed, emergency-ready, or operational claim.
