# PRECHECK-2026-061 - Windigo exact source-fitness pass

**Unit / issue / branch:** `P2O4-T35-U03` / #534 / `codex/p2o4-t35-windigo-deadline-gate`

**Final run:** `BL-2026-07-23-windigo-source-fitness-r006`

**Source code:** `a88b539f50262683c88ec75286ec2d60892d25fd`

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
| render | pass with inherited browser proof: r006 original 1800 by 1260 PNG inspected; r006 HTML differs from browser-validated r004 only in image filename, exact commit, and run ID; local-file r006 navigation was security-policy blocked and not bypassed |
| reproducibility | pass: ignored replay JSON/HTML/PNG are byte-identical to the tracked trio |

## Retained failed attempts

The following failed or superseded evidence remains immutable and excluded from final production:

1. `windigo-source-fitness-r001-trace-failure`: the generator was supplied a mistyped expanded commit. JSON 105,348 bytes / `0ccb291ac0d6d2754799cf30545763628189fd48a48805b5657cbcd26528da4f`; HTML 6,195 / `3e30c309c82c3dde2f5a3906dc945cedb2d284697b7bc6f265b1227d1772698e`; PNG 409,644 / `d49def5dba07b5377236adf61fee38b7e19b7b01ae09aae571e0ce9d95ccc8d2`.
2. `windigo-source-fitness-r002-mobile-render-failure`: the 390-pixel page overflowed to 878 pixels because a long trace token could not wrap. JSON 105,348 / `c593ab6224aa232122a7edff7946458c39366d013739cab5eaf8b2c4d693217f`; HTML 6,195 / `8e10279fd98eb2fdec878254f66cdb08acbb5d0a528baa7783c294de3be56cd0`; PNG 409,542 / `1c20cee8fd91113a816ed4a0c61a36e475c6c807f0c4a9c4abe8ab8ef1646faa`.
3. `windigo-source-fitness-r003-mobile-table-legibility`: page overflow was fixed, but table columns compressed to character-wide cells. JSON 105,348 / `6b17db024f7974d44b44f65058ac55f3ac966bc84ee374e3c6e3a4f67821e033`; HTML 6,406 / `d98c686580d7be5b44edf14e42f73e4ff827bce19c0d2c24b56a63706b679db6`; PNG 409,770 / `cf9057735020eb89b3ec7b44d9ea51bb1211528fdaaf96e55e9ec41c17c7a73f`.
4. Tracked `WINDIGO-SOURCE-FITNESS-2026-004` is superseded because its report named `owner-approved-prototype-region-labels-v0.2.0` after v0.3.0 was already verified. Its scientific results and browser render remain exact historical evidence, never final trace.
5. Ignored `production-r005` supplied a non-existent expanded commit and failed trace binding before promotion. JSON 105,348 / `522d74622d7eee766d2101a55d8998b1f4398a1a3f2618b623fc394407eca8e2`; HTML 6,454 / `4a26a385d58ba7db9a162d66b1674127efe9436105031b4e72762511e98cad17`; PNG 409,850 / `83a19194bd5efc73183926a07dfe290b1d41ec7388f7a45346e856cfe805ea1a`.

R004 first established the corrected mobile table behavior. R006 preserves that exact structure and CSS while correcting trace only.

## Exact outputs

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| JSON | 105,348 | `7e0ede49bcee692c130c6f04fe90898f6c393fb57f64191da1f16c1567b724b2` |
| HTML | 6,454 | `d1fb9dd36ae8d00bdc31a0a1d6aa8e00b5446896c5857b3488062123598037a1` |
| PNG | 409,992 | `8aeb001f0e926a262f52e1235cafc9dbc0480ffa1255180036174a50c00295fe` |

## Validation and next dependency

- focused Windigo source-fitness tests: four passed;
- environment/profile plus source-fitness checks: nine passed after the declared console-command count advanced from 82 to 83;
- full repository suite: 563 passed, one expected skip, 20 retained NumPy deprecation warnings, and 86 subtests passed in 568.56 seconds;
- dependency lock/environment refresh, 66-distribution compatibility, compilation, 132 JSON parses, 218 local Markdown links, diff hygiene, static PNG review, live desktop HTML, live narrow HTML, and exact replay: pass.

The first compatibility probe used `python -m pip check`; the locked uv environment intentionally has no importable pip module, so that probe is inapplicable rather than a dependency result. The correct `uv pip check --python .venv\Scripts\python.exe` verification checks all 66 installed distributions and passes.

U03 disposition is `pass`. Only `P2O4-T35-U04_EXACT_TWO_CARD_PROPOSAL` is eligible next. U04 must propose exactly one burned and one separately justified affirmative-background region with explicit unknown rings. Both candidates and every non-owner gate must pass together. No candidate, owner decision, label, sixth-event acceptance, dataset, split, baseline, model, metric, accuracy, field-validation, official, endorsed, emergency-ready, or operational claim exists at this checkpoint.
