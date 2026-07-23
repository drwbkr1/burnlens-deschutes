# PRECHECK-2026-061 - Windigo exact source-fitness pass

**Unit / issue / branch:** `P2O4-T35-U03` / #534 / `codex/p2o4-t35-windigo-deadline-gate`

**Run:** `BL-2026-07-23-windigo-source-fitness-r004`

**Source code:** `d7ab33568445b90a3e5961927c9d780d6b934032`

**Decision:** `ACCEPT_SOURCE_FITNESS_DEFER_CANDIDATES_OWNER_DECISIONS_LABELS_DATASET_SPLIT_BASELINE_MODEL`

## Entry and exact inputs

U03 begins after U01/U02 pass. It reopens without mutation:

- the exact 12,526,858-byte reference archive / SHA-256 `defd99749a28bd311bcab9bc75631447e1e42eecf3da66adbb3c9c1e2d6b0804`;
- the exact 1,185,125,439-byte pre Sentinel archive / SHA-256 `6a62dd98ce619f53a2dc4e8348de5503edac6cfe3cf58449cdb0de98750d8034`;
- the exact 1,187,986,637-byte post Sentinel archive / SHA-256 `18a40c3c7a8c14443892461876ed1deafab1b22d54446802cc394bd465910987`;
- the registered U01 event, product, geometry, terms, and deadline records; and
- the valid provider-generated MTBS GeoJSON boundary.

No provider request, download, credential use, custody mutation, overwrite, or public-sharing action occurs in U03.

## Gate ledger

| Gate | Result |
|---|---|
| source identity and authority | pass: exact Windigo event and BAER `10022395`, RAVG `10022960`, MTBS `10029547` roster |
| delivered terms and roles | pass with explicit preliminary, analyst, model, warranty, update, acknowledgement, and no-field-claim limits |
| custody and integrity | pass: exact archive and extracted bytes, safe unique paths, no encryption/symlinks, CRC, 54-member roster |
| raster structure | pass: 21 readable native rasters, EPSG:32610, explicit transforms, nodata, class domains, and nearest-neighbor comparison |
| topology | pass with exclusions: MTBS vector and provider GeoJSON valid; invalid BAER/RAVG vectors retained, unrepaired, and unused |
| optical quality | pass: 10,601 of 10,778 boundary pixels support paired comparison; 177 remain excluded |
| registration | pass: 9/9 windows; p95 0.1014 pixel; maximum 0.102 pixel / 2.04 m |
| positive reference | pass for later proposal only: BAER SBS 2-4 primary, MTBS 2-4 corroborating |
| background evidence | not created here; no delivered class is affirmative background truth |
| uncertainty | pass: class ambiguity, nodata, vector failures, native grids, continuous dNBR, and source roles remain visible |
| leakage | pass for this unit: event group stays Windigo; no split, tuning, transfer evaluation, or cross-event promotion occurs |
| privacy and security | pass: no recipient, retrieval URL, credentials, tokens, cookies, provider bytes, or private attributes enter tracked evidence |
| render | pass: original 1800 by 1260 PNG inspected; desktop 1440 HTML has no overflow; 390 by 844 HTML has no document overflow and readable internally scrolling tables |
| reproducibility | pass: ignored replay JSON/HTML/PNG are byte-identical to the tracked trio |

## Retained failed attempts

The following ignored evidence remains immutable and excluded from production:

1. `windigo-source-fitness-r001-trace-failure`: the generator was supplied a mistyped expanded commit. JSON 105,348 bytes / `0ccb291ac0d6d2754799cf30545763628189fd48a48805b5657cbcd26528da4f`; HTML 6,195 / `3e30c309c82c3dde2f5a3906dc945cedb2d284697b7bc6f265b1227d1772698e`; PNG 409,644 / `d49def5dba07b5377236adf61fee38b7e19b7b01ae09aae571e0ce9d95ccc8d2`.
2. `windigo-source-fitness-r002-mobile-render-failure`: the 390-pixel page overflowed to 878 pixels because a long trace token could not wrap. JSON 105,348 / `c593ab6224aa232122a7edff7946458c39366d013739cab5eaf8b2c4d693217f`; HTML 6,195 / `8e10279fd98eb2fdec878254f66cdb08acbb5d0a528baa7783c294de3be56cd0`; PNG 409,542 / `1c20cee8fd91113a816ed4a0c61a36e475c6c807f0c4a9c4abe8ab8ef1646faa`.
3. `windigo-source-fitness-r003-mobile-table-legibility`: page overflow was fixed, but table columns compressed to character-wide cells. JSON 105,348 / `6b17db024f7974d44b44f65058ac55f3ac966bc84ee374e3c6e3a4f67821e033`; HTML 6,406 / `d98c686580d7be5b44edf14e42f73e4ff827bce19c0d2c24b56a63706b679db6`; PNG 409,770 / `cf9057735020eb89b3ec7b44d9ea51bb1211528fdaaf96e55e9ec41c17c7a73f`.

The final r004 table cards scroll internally at narrow width while the document remains contained.

## Exact outputs

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| JSON | 105,348 | `7168a43f1d80b792ed1f8d03550a0d2eedc8bd158e1d28c2679875f1f6694ba5` |
| HTML | 6,454 | `312043fe0d94bf8393f16b0726c064b6a064d326874e172888f4272726f3766c` |
| PNG | 409,864 | `b82cf65b432c66b1ea4d179737c90c6713e25a629fbc14125d101ba8e3ad56d1` |

## Validation and next dependency

- focused Windigo source-fitness tests: four passed;
- environment/profile plus source-fitness checks: nine passed after the declared console-command count advanced from 82 to 83;
- full repository suite: 563 passed, one expected skip, 20 retained NumPy deprecation warnings, and 86 subtests passed in 568.56 seconds;
- dependency lock/environment refresh, 66-distribution compatibility, compilation, 132 JSON parses, 218 local Markdown links, diff hygiene, static PNG review, live desktop HTML, live narrow HTML, and exact replay: pass.

The first compatibility probe used `python -m pip check`; the locked uv environment intentionally has no importable pip module, so that probe is inapplicable rather than a dependency result. The correct `uv pip check --python .venv\Scripts\python.exe` verification checks all 66 installed distributions and passes.

U03 disposition is `pass`. Only `P2O4-T35-U04_EXACT_TWO_CARD_PROPOSAL` is eligible next. U04 must propose exactly one burned and one separately justified affirmative-background region with explicit unknown rings. Both candidates and every non-owner gate must pass together. No candidate, owner decision, label, sixth-event acceptance, dataset, split, baseline, model, metric, accuracy, field-validation, official, endorsed, emergency-ready, or operational claim exists at this checkpoint.
