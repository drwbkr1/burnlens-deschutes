# REGISTRY-2026-054 - Petes Lake U04 exact MTBS native contract

**Unit / issue / branch:** `P2O4-T33-U04` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Final run:** `BL-2026-07-21-petes-lake-reference-native-contract-r001`

**Source commit:** `20d6991cbc079f87db6a789717ebd01595c0b05c`

**Decision:** `PASS_EXACT_PETES_LAKE_MTBS_NATIVE_REFERENCE_CONTRACT_FOR_U05`

**Disposition / next dependency:** `pass` / `P2O4-T33-U05_OFFICIAL_REFERENCE_FITNESS_AND_SOURCE_PRECEDENCE`

## Public tracked evidence

| Artifact | Bytes | SHA-256 | State |
|---|---:|---|---|
| `samples/cross-event/phase-two/petes-lake/PETES-LAKE-REFERENCE-NATIVE-CONTRACT-2026-001.json` | 32,991 | `b489bd30b467ab38f7320c9b313f904e0bbe9a33e2bed8b346230b9f48a6053c` | exact request/custody trace, notice gate, member manifest, native contract, limits, and U05 handoff; zero accepted reference pixels |
| `docs/phase-two/objective-four/PETES_LAKE_REFERENCE_NATIVE_CONTRACT_DECISION.md` | 3,511 | `5a96d8e18b0d8398656f1b81731cc14b44146d73961d67a920e3d30db10ca4a9` | bounded human-readable U04 pass and U05 dependency |
| `records/phase-two/prechecks/PRECHECK-2026-052.md` | 2,747 | `5ad54eec04f50e20c82bb5af6f24e25819a3042c851c7d96e883c34b49b31972` | exact production, replay, privacy, dependency, and test gate |
| `records/phase-two/sources/SOURCE-2026-031.md` | 3,352 | `428a5a55fbe8262756a04c62cebda8ef6c86889fd55b97cae899807dad3b5f79` | exact delivered-source identity, authority, provenance, custody, and intended role |
| `records/phase-two/terms/TERMS-2026-027.md` | 2,350 | `e42d8f19600ea127c0569ee307feec501e44cf1442ccd5c3761de3fe0c0b763e` | exact delivered-notice hashes, rights, attribution, restrictions, and wetland boundary |

No public HTML, PNG, reference-fit raster, candidate, review surface, response, or label is in the U04 output roster.

## Immutable request, delivery, and ignored custody

| Run / artifact | Bytes | SHA-256 | Custody state |
|---|---:|---|---|
| request receipt / `BL-2026-07-21-petes-lake-reference-request-r001` | 4,775 | `8f29336c5c9f79a0ceb90b65f97f9434b71bbad8087b6dda36abf188a92aa595` | accepted once; ignored; untracked; single-link; recipient redacted; no automatic retry |
| delivery attempt / `BL-2026-07-21-petes-lake-reference-delivery-r001` | 1,192 | `b1d6572b33bbdb03594779f26a5b60a860f7bb78a94847c06a1f4412d08824ff` | one GET attempt; ignored; untracked; private route absent |
| delivery final state | 3,841 | `5a65cada71c845395001a109e8a93129abd4baa8691697176f6e6be3e93007b5` | exact custody pass; ignored; untracked; single-link |
| raw MTBS archive | 5,963,437 | `f17db688309c72eb84460f67476c116525ae3727bddfd406a8616f1fe0fad6da` | ignored; untracked; no-overwrite; single-link; native provider bytes unpublished |
| native-contract replay JSON | 32,991 | `b489bd30b467ab38f7320c9b313f904e0bbe9a33e2bed8b346230b9f48a6053c` | ignored; untracked; no-overwrite; byte-identical to tracked final |

The private retrieval URL, recipient, mailbox message ID, provider filename, and survey URL are not serialized in any tracked or ignored U04 state. The one exact delivery has not been requested or downloaded again.

## Exact delivered-source bindings

| Input | Exact binding | U04 result |
|---|---|---|
| Event and map | Petes Lake `OR4396912190120230825`; MTBS map `10031414`; extended assessment | one exact source identity; no cross-program member |
| FGDC notice | 38,018 bytes / `b7d1832aef2a3a95b3c3fda01563daf04a98c8611586c9bf0d6ad3a170678411` | access/use, credit, liability, and wetland warning pass before pixel open |
| ISO notice | 53,205 bytes / `eff0822a866dc23c7755fd67f5eefeafe6d637df12bc33b2faab2f3dc7604c4e` | acknowledgement, no-warranty, revision, identity, and wetland warning pass before pixel open |
| Complete archive roster | three directories plus 17 files; manifest SHA-256 `25e60214418dc3fcb1c619ee6f57b7512448b955a67e499710fa39f3e32388b0` | exact root/roster; all member hashes, byte counts, compression, and CRC values retained |
| Native raster grid | 434 x 374; 30 m; EPSG:32610; affine `[30, 0, 581520, 0, -30, 4874520]`; bounds `[581520, 4863300, 594540, 4874520]` | all five exact; no resampling or reprojection |
| dNBR6 domain | `{0: 147156, 1: 1524, 2: 3191, 3: 4371, 4: 5873, 6: 201}` | 0 outside/nodata; 1 ambiguous; 2-4 bounded reference; 6 excluded; zero accepted reference pixels |
| Burn/mask vectors | one polygon each; complete shapefile parts; EPSG:32610; exact DBF identity and warning | exact; WFS raw and delivered semantic threshold fields remain separate |
| PDF/KMZ | PDF magic pass; KMZ 188 members / 1,181,609 uncompressed bytes | safe structure, bounded expansion, event KML, suffix, and CRC pass |

## Code and test checkpoint

| Artifact | Bytes | SHA-256 | Role |
|---|---:|---|---|
| `burnlens/petes_lake_reference_native_contract.py` | 33,743 | `4d86b914e0811ec70f151eae2e44663ac0773e5718c5743fa1a67951ddb0224f` | exact trace, upstream custody, notice-first, roster, vector, raster, media, semantics, privacy, and no-overwrite contract |
| `burnlens/inspect_petes_lake_reference_native_contract.py` | 1,855 | `a874d6e3bd47c1e524948c8a8c9a357942588c3d0d13e8ff29a43ca55d028fec` | repository-bounded production and replay CLI |
| `tests/test_petes_lake_reference_native_contract.py` | 6,896 | `94fbd24fcbc898c112888e71245d99fcd8bb2d91e269139db29cdde634948bca` | roster, notice, semantics, trace-input, shifted-grid, stale-temp/no-overwrite, and exact-custody regression |

## Gate results

- Source identity, publisher authority, access/custody provenance, exact delivered rights, archive/member integrity, scope/format/resolution fitness for native inspection, privacy, and security: pass for U04's bounded use.
- Repository root, branch, remote equality, source-commit ancestry, exact source bytes, immutable run ID, UTC timestamp, request receipt, delivery state, archive bytes/hash/link count, ignore status, and no-overwrite: pass.
- ZIP roster, terms-before-content order, FGDC/ISO parsing, conflict/third-party-term check, shapefile parts/geometry/records/DBF/CRS/bounds, raster driver/shape/bands/dtypes/CRS/resolution/affine/bounds/nodata/masks/domains/common grid, PDF, KMZ expansion/safe paths/event/CRC, and complete manifest: pass.
- Privacy scan: no private host, retrieval route, recipient, mailbox message ID, email address, credential, token, authorization header, cookie, or secret in public evidence.
- Reproduction: ignored final replay matches all 32,991 tracked bytes.
- Verification: 13 focused native/custody/delivery tests; 37 current/historical reference tests; full repository 480 tests plus 50 subtests with 20 existing NumPy deprecation warnings; 66-package integrity, lock, compilation, JSON, link, LF, and diff checks pass.

U04 disposition is `pass`. U05 is authorized to measure exact wetland overlap, optical-grid coverage, temporal support, source precedence, and bounded reference fitness. U04 creates no accepted reference pixel, candidate, owner response, prototype label, sixth complete event, dataset, split, baseline, model, accuracy, release, field-validation, official, endorsed, operational, or emergency-ready claim.
