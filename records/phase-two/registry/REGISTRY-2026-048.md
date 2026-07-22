# REGISTRY-2026-048 - Petes Lake U03 planned-pair source fitness

**Unit / issue / branch:** `P2O4-T33-U03` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Final run:** `BL-2026-07-21-petes-lake-source-fitness-r001`

**Source commit:** `a7b76c662e277242d31980dcf0d815401787c2c7`

**Decision:** `FAIL_EXACT_PETES_LAKE_OPTICAL_SOURCE_FITNESS_REMEDIATE_POST_SCENE`

**Disposition / next dependency:** `remediate` / U03 replacement-post metadata research and contract revision before any provider transaction

## Public tracked evidence

| Artifact | Bytes | SHA-256 | State |
|---|---:|---|---|
| `samples/cross-event/phase-two/petes-lake/PETES-LAKE-SOURCE-FITNESS-2026-001.json` | 56,285 | `ac9befd021d71ff779ec56ddefc894f4e39b92e64e65c2c4afb815663d1ad443` | exact final machine and visual disposition; U04 unauthorized |
| `samples/cross-event/phase-two/petes-lake/PETES-LAKE-SOURCE-FITNESS-2026-001.png` | 626,846 | `4ed3870e37bf68db24805540f00614c5050c064b621ca3fc5e3c0ef244bf0d42` | exact 1,800 x 1,240 actual render; original-resolution inspection pass |
| `docs/phase-two/objective-four/PETES_LAKE_SOURCE_FITNESS_DECISION.md` | 3,058 | `264d09ea3005e061fb690482b65aee1d4bdb4b7713543d46fbea0edc736eb721` | bounded human-readable remediation decision |
| `records/phase-two/prechecks/PRECHECK-2026-046.md` | 1,791 | `a48541d41f167640f23d519b1ad99021d8c64dd11820ee7367e2a8348c030263` | exact gate summary |
| `records/phase-two/reviews/SOURCE_FITNESS-2026-006.md` | 2,421 | `1e02ef8386bff0933eead824830e55de084735a9dec6fd6d7d854161e872d6e9` | source-fitness review |

No HTML output is in the tracked U03 roster.

## Immutable ignored preview runs

| Run / artifact | Bytes | SHA-256 | Link / custody state |
|---|---:|---|---|
| preview r001 JSON | 55,921 | `da755ad9e9f83f5856954dceb3d9c208c605a1af6720afa5fcfec9709f3e09cc` | single-link; ignored; untracked; retained |
| preview r001 PNG | 627,117 | `d3e17134c7da9fe8aacb1b69e30ba0d20d237384544a0ec7501979d8fd5f6ba0` | single-link; ignored; untracked; original-resolution inspection pass |
| preview r001 HTML | 4,324 | `2646d61db4e3d076b3801d1e9c0ca7cf4275b2709fb2982b2db0132780cda0e0` | single-link; ignored; untracked; browser-policy navigation blocked; superseded, never promoted |
| preview r002 JSON | 55,921 | `3255c867046f113bc6081156a2890fb6901b3f38c96ea3dcc7dd70ec1bc26e78` | single-link; ignored; untracked; narrowed output roster |
| preview r002 PNG | 626,836 | `422cd69e587c45378533167b6fc32424124b288dd66ecf425b0506c2ebc9f418` | single-link; ignored; untracked; original-resolution inspection pass |

Preview r001 and r002 have identical scientific metrics. Commit, run ID, generation time, output roster, and visual decision state account for their expected byte differences. No preview was overwritten or deleted.

## Exact input bindings

| Input | Exact binding | Fresh U03 result |
|---|---|---|
| Additional-event plan | SHA-256 `65fd567e234cbb521ead6b7071cab9914c672df169e3987af0c3ddfc66ccf622`; frozen source snapshot SHA-256 `3d6ca59b8071461aa925a3b270300deea1f53c8bd46aedeaec10ddd5301fc241` | Petes Lake remains third, MTBS-only event group |
| U02 custody report | SHA-256 `46f72f7fa7dc3b6fc3f96f6023b0d7b14f6990bcef8945a878ae04600d2e571d`; semantic SHA-256 `a9218a830d729af8712b525acf5365f6ed1d355407947606f1491c538f30f748` | exact report/decision/transaction binding passes |
| Pre archive | 1,185,284,273 bytes; local SHA-256 `c5b6ededc5a264fcc617f2712093b847351c5b8ed78f2ea9ce0ebc3a33e1bc34` | fresh registered-package verification and native raster inspection pass |
| Post archive | 1,243,068,088 bytes; local SHA-256 `636a3cafe66c16cb20c9fd490a7ad448c939e3476d9ac0a404576638c2cd3a25` | fresh registered-package verification passes; local snow fitness fails |

Both archives remain ignored, untracked, no-overwrite, single-link, and byte-identical to U02. No credential or provider transaction occurred in U03.

## Code and test checkpoint

| Artifact | Bytes | SHA-256 | Role |
|---|---:|---|---|
| `burnlens/cross_event_source_fitness.py` | 37,684 | `2725b47a4cb43347e7ad81fd678f932d6bc886a92e24bf4c3f20f9b2089cb31c` | smallest shared extension for native CLD/SNW reads; legacy default unchanged |
| `burnlens/petes_lake_source_fitness.py` | 32,610 | `15a9d5a107fa4554f82c9bcfe51916f07d04a9192bd26c6756e52cf29db7e348` | exact U03 measurement, decision, render, and no-overwrite outputs |
| `burnlens/inspect_petes_lake_source_fitness.py` | 4,809 | `88d4838550cfc405ffc3ce5b7a653c67dec5039a79159de7034e16be0692fba9` | clean-branch preview/final production CLI |
| `tests/test_petes_lake_source_fitness.py` | 5,997 | `a2de1649d70e404e9be2f178b50dee0ecf5c5cae5e60e0513d806424b991d98c` | exact real-pair metric, no-label, no-overwrite, and output-roster regression |

## Gate results

- Custody/source identity, exact hashes, SAFE structure, processing baseline, raster member identity, EPSG:32610 CRS, native resolution, grid/transform/shape, data type, nodata contract, aligned boundary masks, chronology, no-overwrite, ignore/privacy, warning, and trace gates: pass.
- Pre local quality: 33,763 / 34,103 SCL-eligible land pixels, 99.0030%; cloud and snow probabilities all zero.
- Post local quality: 26,627 SCL snow-or-ice pixels, 78.0782%; snow p50/p95/max 60% / 100% / 100%; fail.
- Paired quality: 7,439 eligible / 21.8133%; three review-needed; 26,661 excluded / 78.1779%.
- Registration: eight windows; zero pass; eight excluded below unchanged 90% usable fraction; zero fail-registration windows; event source gate rejects zero-pass result.
- Continuous dNBR: 7,439 valid pixels retained without threshold, severity, or label semantics.
- Actual render: final 1,800 x 1,240 PNG passes original-resolution author audit. Direct local-file HTML navigation was policy-blocked and not bypassed; HTML is not tracked.
- Tests: 73 focused Petes/provider/dependency tests passed before the first code commit; full repository suite passed 399 tests with 20 existing NumPy deprecation warnings; after narrowing outputs, 10 focused source-fitness tests passed. Compilation, dependency health, and diff hygiene pass.
- Disposition: `remediate`. U04 and all dependent units remain blocked pending an evidence-backed replacement post scene that independently passes every applicable gate.

U03 creates no reference, candidate, owner response, prototype label, sixth accepted event, dataset, split, baseline, model, metric, field-validation, official, endorsed, operational, or emergency-ready claim.
