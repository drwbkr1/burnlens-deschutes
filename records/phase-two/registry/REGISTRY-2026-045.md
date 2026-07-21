# REGISTRY-2026-045 - Petes Lake U01 Entry Gate

**Unit / issue / branch:** `P2O4-T33-U01` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Capsule commit:** `43635eb20183f49864397f8b74db4f49eb7a3b7e`

**Qualifying run:** `BL-2026-07-21-petes-lake-entry-gate-r003`

**Decision:** `PASS_PETES_LAKE_ENTRY_GATE_AUTHORIZE_SEQUENTIAL_U02_OPTICAL_CUSTODY_ONLY`

## Tracked immutable U01 evidence

| Artifact | Bytes | SHA-256 | State |
|---|---:|---|---|
| `samples/cross-event/phase-two/petes-lake/PETES-LAKE-ENTRY-GATE-2026-001.json` | 18,270 | `ac5d7498f847e0df973c58445188b422d919dc5c195e832e518ba5dbf11d6bec` | normalized U01 r003 evidence |
| `docs/phase-two/objective-four/PETES_LAKE_ENTRY_GATE_DECISION.md` | 2,027 | `1c415ae4329efb5b380e0e7019b6e7b9abf24ade59046bc76c93e35d1553a88f` | bounded decision |
| `records/phase-two/sources/SOURCE-2026-028.md` | 3,055 | `8e55d44c26bfbe93442068cf2edca88eca16e788cdb4061e005d436508de6e91` | Sentinel identities and routes |
| `records/phase-two/sources/SOURCE-2026-029.md` | 3,170 | `8538ae6d6b1a364592b72b3be213f77d65b4fab348b644419ab6838008254a81` | MTBS event and delivery identity |
| `records/phase-two/terms/TERMS-2026-024.md` | 1,963 | `24b4024243e2b4dc2a5ec9235aef1f4b5b56ec9de96af0d675c5719f00ea7326` | Sentinel terms and attribution |
| `records/phase-two/terms/TERMS-2026-025.md` | 2,096 | `e37b620c759f1dcb8228ec41b62745c20a76c98bc6335bc2a7ff9a9f0d91f85b` | MTBS request and use terms |
| `records/phase-two/access/ACCESS-2026-018.md` | 1,800 | `c8fb869f46c967cbeabc3a4f3cf5795372e0f170ebd9c1ae89df349dccb7d346` | token-only access and custody destinations |
| `records/phase-two/prechecks/PRECHECK-2026-043.md` | 2,996 | `f9418b7270f6ed1ddf0b223e9e64a063b3bd201feb82482b72e69c2d5654f8ab` | integrated U01 gate |
| `records/phase-two/reviews/SOURCE_PRECEDENCE-2026-018.md` | 1,501 | `2b3045a4778c69279302d7f17c61528d163ddda7540c1ff543d7100709994595` | source-role boundary |
| `records/phase-two/reviews/USE_BOUNDARY-2026-039.md` | 1,118 | `ce8238e5482e85fd7dac6ba054f134309eeb03581a6f708527c12b31231aa7d6` | use and claim boundary |
| `tests/test_petes_lake_entry_gate.py` | 5,291 | `139e2c535148c98db1a343a8e17ad6c467141552f88edd203f98bf6eca69b1c9` | deterministic contract checks |

The milestone prompt/build log and devlog are rolling controls and are byte-bound only by the eventual U11 milestone manifest. This registry is immutable after the U01 commit; later units must create their own sequential records and must not rewrite these entries.

## Ignored retained runs

| Run / artifact | Bytes | SHA-256 | Disposition |
|---|---:|---|---|
| r001 live source JSON | 1,213,547 | `100e880d0aa7c3b3ceff2a663dfd3704b624552fe5df5a16c8fc995eed05ba3c` | `remediate`: useful pre-capsule rehearsal |
| r001 plan JSON | 877,732 | `09a131be06751185649a9bb81f428c8619b47b6fcd7c2ba65264844375f0bb74` | `remediate` |
| r001 plan HTML | 10,936 | `0cfddc5a4e1fcc1c04a01d11e729ee3f7e46c8adb4a32e08d4a4d0bc3c90d78b` | `remediate` |
| r001 plan PNG | 108,974 | `b80283d004a216fd4d99d8498423e2c0629f7e437bd987e16a2027616e4f37da` | `remediate` |
| r002 live source attempt | no output created | not applicable | `remediate`: failed closed with `SOURCE_REQUEST_FAILED:https://stac.dataspace.copernicus.eu/v1/search`; direct official probe later returned HTTP 200 |
| r003 live source JSON | 1,213,547 | `1d99d32f6610e64eed5a310d58c9ee730e6f9be691b6f7eb2ed00044018b559c` | `pass`; ignored, no-overwrite execution path |
| r003 plan JSON | 877,732 | `0e0deed4a54ae0dc2ae8def2596b200d1aa2891f0822b8e2a3c3fca3ec292f9e` | `pass` |
| r003 plan HTML | 10,936 | `f271312a3bee0bcdcc204a40a1b6fdd11140f9c15696f39d079bdf80d21110be` | `pass` |
| r003 plan PNG | 109,173 | `b7f9dc420c70d3d064dd51f5880b1d2f43ce34745301f7c7fba353ad5c3780c8` | `pass`; original 1800 x 1250 render inspected |

R001 and r003 paths are ignored and untracked. R002 has no file because the capture writes only after all metadata gates pass; its exact command, error, and disposition remain in the milestone log and this registry. Zero provider product/archive bytes were requested or downloaded in every U01 run.

## External source-byte bindings

| Source | Bytes | SHA-256 |
|---|---:|---|
| Burn Severity Viewer JavaScript | 405,895 | `15c84c7f7a3007d9226a37df59156fb96ea3dccfcc7ad223fd67d360f07cd46d` |
| MTBS burn-area boundary XML | 23,634 | `e56b96c0366a4da515f18664c1fcfad838616f5ba67c68c92f7a492d3ac412c1` |
| MTBS fire-occurrence XML | 21,884 | `807638cf7b91d9847e0a87d178d7c77a4e59b35808c9930df4d683eff14e8b88` |
| CDSE Terms and Conditions | 77,530 | `e17c490e30a0544880e0ead78dcc4f749409d8ca4de67f003b2823203f864948` |
| Sentinel Data Legal Notice | 115,881 | `fa2955ff48a1d82e77fc7296d63681670ecdb9d2811a0505ae60d0683b62fa64` |

## Actual gates

- Current Petes Lake event/map identity, current Portal row, exact Sentinel pair, UUIDs, SAFE names, sizes, online state, MD5, BLAKE3, STAC quality metadata, official delivery route, source roles, terms, attribution, token-only access, exact future custody destinations, source precedence, use boundary, and uncertainty carry-forward: pass.
- Post-scene 9.841206 percent tile-wide snow and the exact MTBS wetland warning: retained for mandatory local measurement.
- Exact official archive notices: U04 gate, not inferred.
- Provider archive custody, pixels, source fitness, reference fitness, candidates, owner decisions, labels, dataset, split, baseline, model, metric, and operational status: not created or not executed.
- U02 is authorized only for sequential custody of the two exact UUID-bound Sentinel archives. Pre must pass full promotion and post-verification before post may be requested.
