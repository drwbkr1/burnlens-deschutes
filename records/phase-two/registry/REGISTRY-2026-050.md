# REGISTRY-2026-050 - Petes Lake replacement optical contract

**Unit / issue / branch:** `P2O4-T33-U03` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Contract checkpoint:** `ab6ecc04d847aba848f0fc1f384405b10f0d8f9f`

**Contract / package:** `petes-lake-optical-post-remediation-contract-v0.1.0` / `petes-lake-s2-optical-post-remediation-v0.2.0`

**Planned transaction / aggregate:** `BL-2026-07-21-petes-lake-optical-post-remediation-r001` / `BL-2026-07-21-petes-lake-optical-remediation-intake-r001`

**Decision:** `PASS_PETES_LAKE_REPLACEMENT_CONTRACT_AND_PREFLIGHT_AUTHORIZE_ONE_SINGLETON_TRANSACTION`

## Exact tracked input bindings

| Artifact | Bytes | SHA-256 | Role |
|---|---:|---|---|
| `records/phase-two/sources/SOURCE-2026-030.md` | 3,544 | `8a79758b2059f1cf240963b28c86a1ac69edd27626652d16fcc7323bdc160b8d` | exact source/timing/selection interpretation |
| `records/phase-two/terms/TERMS-2026-026.md` | 3,322 | `abcfc1ac94b5f886131f46049c9e98ae503ea7e1b6a12bc87c8d6e26073888d9` | exact one-replacement-archive authorization |
| `records/phase-two/terms/TERMS-2026-024.md` | 1,982 | `31179a8ce2754da7e73248e0fe667fd9a928c38d759d2b5f47db918028559d61` | immutable original two-archive authorization |
| `samples/cross-event/phase-two/petes-lake/PETES-LAKE-SOURCE-REMEDIATION-2026-001.json` | 10,127 | `7fa82a61fa70d47364db29493700beedd60c9114a4b3a6d8ddbafdf77aecfc8c` | deterministic replacement selection |
| `samples/cross-event/phase-two/petes-lake/PETES-LAKE-SOURCE-FITNESS-2026-001.json` | 56,285 | `ac9befd021d71ff779ec56ddefc894f4e39b92e64e65c2c4afb815663d1ad443` | immutable planned-pair failure |
| `samples/cross-event/phase-two/petes-lake/PETES-LAKE-OPTICAL-CUSTODY-2026-001.json` | 23,521 | `46f72f7fa7dc3b6fc3f96f6023b0d7b14f6990bcef8945a878ae04600d2e571d` | immutable original pre/post custody |

## Contract implementation and public decision

| Artifact | Bytes | SHA-256 | Role |
|---|---:|---|---|
| `burnlens/petes_lake_replacement_optical_contract.py` | 61,238 | `fe7e56f8ba0c2b5855e76532ac3747e8453857325229b1bdb1027ca66c3f58ab` | exact contract, live gates, no-overwrite custody, recovery, and verifier |
| `burnlens/acquire_petes_lake_replacement_post.py` | 3,801 | `9dcaaa29b1cdc242060cdc2441205f3b3f7cfc546248f66b1bbbcf22b76fdc3f` | preflight/acquire/finalize/verify CLI |
| `scripts/invoke_petes_lake_replacement_post_intake.ps1` | 3,464 | `acbc235f2562f0f69102958cacdeaf3a468292a0d081970c5190647176e8e45f` | DPAPI wrapper with pre-credential and post-clear gates |
| `tests/test_petes_lake_replacement_optical_contract.py` | 24,586 | `603caf86c9127997934a1d608ea2658d4361374f59fce56179ea999994a6c38c` | exact contract, drift, ordering, failure, recovery, privacy, and CLI regression |
| `pyproject.toml` | 7,434 | `74982033cdc19a5ba3d694f7dc6692605a15f6e710f25995c79c3f42bcca2817` | installed `burnlens-acquire-petes-lake-replacement-post` entry point |
| `.gitattributes` | 5,670 | `0147570363c7e9f6281c4a06e853b95cc0706969900098d7724835e1c8976316` | LF checkout stability for exact terms/wrapper/decision/precheck/registry bytes |
| `docs/phase-two/objective-four/PETES_LAKE_REPLACEMENT_OPTICAL_CONTRACT_DECISION.md` | 2,808 | `ddf46b9038ca50b1273f8e1163429e5bdf2f1392fde1fb52ea4e3cd518c6aa71` | human-readable bounded decision |
| `records/phase-two/prechecks/PRECHECK-2026-048.md` | 2,434 | `6d3b973a5343288760d819e2650ca6119e806869541a87337db41f0e96925b84` | clean live preflight result |

## Exact singleton and retained-pre identities

| Role | Exact identity | Gate result |
|---|---|---|
| Retained pre | package `petes-lake-s2-optical-pre-v0.1.0`; run `BL-2026-07-21-petes-lake-optical-pre-r001`; 1,185,284,273 bytes; local SHA-256 `c5b6ededc5a264fcc617f2712093b847351c5b8ed78f2ea9ce0ebc3a33e1bc34` | fresh registration/archive/hash/CRC/SAFE/ignore/untracked/single-link verification passes; no reacquisition |
| Replacement post | UUID `31fa8699-175b-4fd7-91c3-dd727a1576f5`; `S2A_MSIL2A_20231019T190411_N0510_R013_T10TEP_20241107T024526.SAFE.zip`; 1,195,226,823 bytes; MD5 `4cf05a073b4c67f5e92e052ed1eb32bc`; BLAKE3 `1b28f566aee5619ea9a48c8dd042f209194a40989ba4b54cfe4e14904a0ad878` | exact live OData identity passes; provider archive not yet requested |

## Planned no-overwrite output roster at preflight

| Artifact | State at 2026-07-21T20:56:29.367477Z |
|---|---|
| `downloads/phase-two/quarantine/P2O4-T33-U03/petes-lake-optical-post-remediation-r001` | absent, ignored, untracked |
| `downloads/phase-two/raw/petes-lake-s2-optical-post-remediation-v0.2.0` | absent, ignored, untracked |
| `downloads/phase-two/runs/P2O4-T33-U03/BL-2026-07-21-petes-lake-optical-post-remediation-r001.json` | absent, ignored, untracked |
| `downloads/phase-two/runs/P2O4-T33-U03/BL-2026-07-21-petes-lake-optical-remediation-intake-r001.json` | absent, ignored, untracked |
| `samples/cross-event/phase-two/petes-lake/PETES-LAKE-OPTICAL-REMEDIATION-CUSTODY-2026-001.json` | absent, unignored, untracked |

## Verification and boundary

- Exact clean branch and remote equality at `ab6ecc04d847aba848f0fc1f384405b10f0d8f9f`: pass.
- Current CDSE Terms and Sentinel Data Legal Notice exact source bytes: pass at the hashes bound in `TERMS-2026-026`.
- Current OData UUID/SAFE/size/online/checksum/sensing/publication/platform/tile/orbit/baseline/type/cloud identity: pass; S3 identity is checked only as a suffix and its path is not retained.
- Focused replacement/original-custody/provider regression: 95 passed. Full repository: 455 passed plus 50 subtests; 20 existing NumPy deprecation warnings. `uv lock --check`, `uv pip check`, compilation, diff, privacy, and exact-hash checks pass.
- Credential exercised: false. Provider product/archive bytes requested or acquired: zero. No quarantine, raw target, transaction state, aggregate state, or custody report exists at this checkpoint.
- Recovery is revisioned and no-overwrite. An already promoted archive may be finalized at r002+ without reacquisition; distinct retained evidence cannot be silently selected or overwritten.

This registry authorizes only one exact wrapper transaction after issue #521 records the checkpoint. Custody may authorize replacement U03 source-fitness r002 only. It does not authorize U04 or establish local pixel, source, reference, candidate, owner-response, label, sixth-event, dataset, split, baseline, model, field-validation, official, endorsed, operational, or emergency-ready status.
