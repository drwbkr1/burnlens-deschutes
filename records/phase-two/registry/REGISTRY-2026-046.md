# REGISTRY-2026-046 - Petes Lake U02 metadata reconciliation

**Unit / issue / branch:** `P2O4-T33-U02` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Run:** `BL-2026-07-21-petes-lake-optical-metadata-reconciliation-r001`

**Code checkpoint:** `c4987ce53a7606d828caf2db134a28f160bc867d`

**Decision:** `PASS_PETES_LAKE_CLOUD_METADATA_RECONCILIATION_AUTHORIZE_U02_PREFLIGHT_ONLY`

## Exact inputs

| Input | Bytes | SHA-256 | Role |
|---|---:|---|---|
| `downloads/phase-two/runs/P2O4-T33-U01/ADDITIONAL-EVENT-GROUP-SOURCE-LIVE-r003.json` | 1,213,547 | `1d99d32f6610e64eed5a310d58c9ee730e6f9be691b6f7eb2ed00044018b559c` | ignored frozen U01 STAC discovery representation |
| `samples/cross-event/phase-two/petes-lake/PETES-LAKE-ENTRY-GATE-2026-001.json` | 18,270 | `ac5d7498f847e0df973c58445188b422d919dc5c195e832e518ba5dbf11d6bec` | qualifying U01 gate and exact pair contract |
| Current public CDSE OData snapshot | canonical JSON | `248fbfbea4e82a6f93360fdb6cde987b31898278dc4c6faaa4f288dbfcc92847` | live UUID/SAFE/size/online/checksum and raw cloud metadata |

## Tracked outputs

| Artifact | Bytes | SHA-256 | State |
|---|---:|---|---|
| `samples/cross-event/phase-two/petes-lake/PETES-LAKE-OPTICAL-METADATA-RECONCILIATION-2026-001.json` | 8,750 | `b1062e8e8f298087852cd0199d83482a20873bcc90bd5d777c5c6e91c69aaa52` | fixed-path, no-overwrite live reconciliation report |
| `docs/phase-two/objective-four/PETES_LAKE_OPTICAL_METADATA_RECONCILIATION_DECISION.md` | 1,781 | `e19a6ce07558f4e5a546248c8a99d07d50cf7f655624ad066eb7e7783108cd32` | bounded human-readable decision |
| `burnlens/acquire_petes_lake_optical.py` | 4,993 | `5496f06058bd440d6def4830079e2153d7091ecbc5842b01af9e97e1db9cd037` | credential-free metadata-only CLI route |
| `burnlens/petes_lake_optical_contract.py` | 75,630 | `ff234cc1fb1594628584b805ddf4b401065fd06ad571d69e6965dabdc94d0620` | v0.2.0 exact precision-reconciliation and report contract |
| `tests/test_petes_lake_optical_contract.py` | 41,742 | `041ba74d38a0c2c5446a1c342f89bec89975efae04f90c883e4ce57a68a15d1f` | raw, normalized, drift, no-overwrite, and credential-free regression gates |

## Exact live identities

| Role | UUID / SAFE | Bytes | Provider checksums | Cloud metadata |
|---|---|---:|---|---|
| pre | `bf275eb0-7e50-4d4d-a01b-fbaaa18e5142` / `S2A_MSIL2A_20230721T185921_N0510_R013_T10TEP_20240911T103205.SAFE` | 1,185,284,273 | MD5 `c41d10e4e895839132c0ad4ee47100e1`; BLAKE3 `49d13b491c1e4a979d65dc870daf2d72f940bfc910abb19c00e1a485992ed17b` | exact OData `0.000358`; frozen STAC `0.0`; two-decimal comparison `0.0` |
| post | `80363c3a-8c04-4ed3-8e2a-d1f35e7a62c6` / `S2A_MSIL2A_20231029T190511_N0510_R013_T10TEP_20241106T074945.SAFE` | 1,243,068,088 | MD5 `bf9383d434448998f5025494d0a43320`; BLAKE3 `9814e80893321d86b9aec796651aaf811d8e31df6ed98413519bbeab1141d105` | exact OData `0.008789`; frozen STAC `0.01`; two-decimal comparison `0.01` |

Both records were online. Raw values remain independently required; normalization is only a cross-endpoint precision comparison and is not a pixel-quality shortcut.

## Gates and disposition

- Exact branch, ancestry, clean worktree, entry-gate binding, ignored/untracked custody destinations, and remote commit equality before the live run: pass.
- Exact UUID, SAFE, size, online, MD5, BLAKE3, raw OData cloud value, frozen U01 STAC value, two-decimal comparison, source precedence, terms binding, privacy, and warning gates: pass.
- Credential use, token request, product/archive request, archive download, raw custody, quarantine, private state, aggregate state, and U02 custody report: not executed; zero provider product/archive bytes.
- Local SCL/SNW, cloud, smoke, shadow, snow, raster, registration, and render gates: not executed; remain U03 dependencies after U02 passes.
- Disposition: `pass` for this pre-provider metadata reconciliation only. U02 itself remains in progress and cannot pass until both separate archive transactions pass.
- Retained limitation: the initial migrated-checkout metadata probe failed closed on the pre/post precision mismatch. A current STAC post-item probe returned `0.01`; the corresponding pre-item request timed out and was not guessed or substituted. The immutable U01 pre/post STAC values remain the comparison binding.
- Next dependency: commit and push this registry/report, record the exact evidence commit on issue #521, rerun the clean production preflight, and only then consider the exact pre archive transaction.

No Petes Lake pixel, candidate, owner response, label, dataset, split, baseline, model, metric, field-validation, official, endorsed, emergency-ready, or operational status is created.
