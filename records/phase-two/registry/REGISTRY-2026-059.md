# REGISTRY-2026-059 - Petes Lake milestone material-defer closeout candidate

**Unit / issue / branch:** `P2O4-T33-U11` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Run:** `BL-2026-07-22-petes-lake-milestone-closeout-r001`

**Exact base / terminal evidence checkpoint:** `0d41942dc6c3c307a9a146a2d38fb816e038bb42` / `52310531ad0b8e6d07800fc752f7bf65b5fdea9a`

**Milestone decision / U11 disposition / execution status / release state:** `DEFER_PETES_LAKE_DO_NOT_PROMOTE_SIXTH_EVENT` / `defer` / `in-progress` / `candidate`; the disposition completes the reviewable ledger but is not a U11 `pass`, and the milestone remains unshipped until PR, merge, clean-main verification, and tag gates pass

**Candidate software / tag:** BurnLens `0.45.0` / `v0.45.0-petes-lake-material-defer`; PR, merge, clean-main verification, and annotated tag remain pending until this candidate is committed and reviewed

## Material boundary

The final automatically authorized same-source NWI run is terminal. Run `BL-2026-07-22-petes-lake-nwi-context-r003`, intake `petes-lake-nwi-context-2026-003`, has seven promoted assets, one failed asset, and four authorized-unexecuted assets. Its eighth ordered asset observed HTTP status 500 at `PROVIDER_OPEN` during its only durable attempt. The supported diagnostic does not establish a cause. No retry, continuation, partial selection, seed, r004, or U05 scientific-fitness run exists.

PRECHECK-2026-056 authorizes only this material-defer closeout. The decision is `defer`, not permanent exclusion: there is no tested same-source correction, no alternate route registered in #521, insufficient evidence for permanent exclusion, and no reason to stop the BurnLens project. Any official fallback requires a new issue, identities, source/terms decision, custody transaction, and scientific-fitness gate.

## Complete evidence-unit ledger

| Unit | Immutable run or evidence identity | Outcome and exact controlling record | Retained limitation / next dependency |
|---|---|---|---|
| `P2O4-T33-U01` | `BL-2026-07-21-petes-lake-entry-gate-r001`; `BL-2026-07-21-petes-lake-live-source-gate-r002`; `BL-2026-07-21-petes-lake-entry-gate-r003` | r001 `remediate`; r002 `remediate`; r003 `pass`; REGISTRY-2026-045 | Tile-wide snow and the exact MTBS wetland warning remain visible; U02 followed only after the qualifying r003 gate. |
| `P2O4-T33-U02` | `BL-2026-07-21-petes-lake-optical-metadata-reconciliation-r001`; `BL-2026-07-21-petes-lake-optical-intake-r001` | metadata normalization and exact two-archive custody `pass`; REGISTRY-2026-046 and REGISTRY-2026-047 | A post-success wrapper defect was retained and fixed without reacquisition or package rewrite; local source fitness remained U03. |
| `P2O4-T33-U03` | planned run `BL-2026-07-21-petes-lake-source-fitness-r001`; replacement run `BL-2026-07-21-petes-lake-replacement-source-fitness-r002` plus selection/custody intermediates | planned post `remediate`; replacement `pass-with-spatial-exclusions`; REGISTRY-2026-048 through REGISTRY-2026-053 | The planned post is snow-dominated. The replacement retains 134 review-needed and 604 excluded boundary pixels plus three review-needed registration windows; no label semantics are inferred. |
| `P2O4-T33-U04` | `BL-2026-07-21-petes-lake-reference-request-r001`; `BL-2026-07-21-petes-lake-reference-delivery-r001`; `BL-2026-07-21-petes-lake-reference-native-contract-r001` | exact request, delivery, custody, notices, safe structure, native grids/vectors/classes/media, privacy, and replay `pass`; REGISTRY-2026-054 | Zero reference pixels are accepted. MTBS's wetland warning and native class limitations remain unresolved input to U05. |
| `P2O4-T33-U05` | `BL-2026-07-21-petes-lake-nwi-context-r001` | retained validator failure, `remediate`; REGISTRY-2026-055 | One exact official response is preserved but never retried, promoted, or selected for fitness. |
| `P2O4-T33-U05R1` | `BL-2026-07-22-petes-lake-nwi-context-r002` | seven promoted, one unknown-cause provider-open failure, four unexecuted; `remediate`; REGISTRY-2026-056 | Old code did not retain a controlled diagnostic; r002 is immutable and never continued or copied. |
| `P2O4-T33-U05R2` | code checkpoint `1b8c1ad52043536f243b178d279922ceb469103d`; run `BL-2026-07-22-petes-lake-nwi-context-r003` from source `afcbbd2331e2106422940754c6f86b8022e1764b` | offline observability/disjoint-custody code `pass`; final intake `defer`; REGISTRY-2026-057 and REGISTRY-2026-058 | Asset eight records only `{category: http, http_status: 500}`; assets 9-12 are unexecuted; no causal attribution, partial U05 fitness, or r004. |
| `P2O4-T33-U06` | no-run disposition record `P2O4-T33-U11-DISP-U06` | disposition `defer`; execution status `unexecuted`; no output | U05 scientific pass is absent, so no affirmative-background source contract or custody exists. |
| `P2O4-T33-U07` | no-run disposition record `P2O4-T33-U11-DISP-U07` | disposition `defer`; execution status `unexecuted`; no output | U06 is absent, so no affirmative-background evidence exists. |
| `P2O4-T33-U08` | no-run disposition record `P2O4-T33-U11-DISP-U08` | disposition `defer`; execution status `unexecuted`; no candidate, raster, unknown ring, or output | The required two-class evidence chain is incomplete. |
| `P2O4-T33-U09A` | registered batching utility and synthetic QA | preparatory software `pass`; integrated at `addb88bd1cd6c5e1b184914f5c5015ada95f304e` | No production Petes roster, response, or owner decision was created. |
| `P2O4-T33-U09B` | `BL-2026-07-21-localhost-review-transport-qa-r001` | preparatory loopback transport and software-fixture browser QA `pass`; integrated at `b28ce065afc8a06c0b2c1607f05f37218bae4ce0` and `08de31b24dd54ab4b4f74f6bb33bf62540dc10bc` | The Grandview fixture/export is non-ingest software evidence, not Petes or owner evidence. |
| `P2O4-T33-U09C` | `BL-2026-07-21-geospatial-environment-qa-r001` | locked Python 3.12.10 environment and offline capability checks `pass`; integrated through `3ae2f9e01fd369572596cf5b7606e4e012d65f33` | Environment capability is not data, scientific, candidate, label, or model fitness. |
| `P2O4-T33-U09` | no-run disposition record `P2O4-T33-U11-DISP-U09` | disposition `defer`; execution status `unexecuted`; no Petes surface, batch, export, or owner decision | U08 is absent. Owner yes/no/uncertain remains required for any future exact eligible roster. |
| `P2O4-T33-U10` | no-run disposition record `P2O4-T33-U11-DISP-U10` | disposition `defer`; execution status `unexecuted`; no response lock, receipt, reconciliation, or label | U09 has no production export; both-class and no-partial-promotion gates remain controlling. |
| `P2O4-T33-U11` | `BL-2026-07-22-petes-lake-milestone-closeout-r001` | disposition `defer`; execution status `in-progress`; release state `candidate`; material-defer decision and BurnLens 0.45.0 candidate | This is not a U11 `pass`; one milestone PR, verified clean main, exact annotated-tag peel, and a bounded lifecycle sync remain shipment gates. |
| `P2O4-T33-U11R1` | `BL-2026-07-22-petes-lake-u04-descendant-trace-remediation-r001`; failed candidate `9f44099922485b9c26b4cadcc029a67423434877`; correction checkpoint `fcbaa4c1044672352227f6a3047d998967d1d114` | precursor clean-checkout replay `remediate`; trace-code correction and canonical actual replay `pass`; final clean-candidate release verification pending | Exact U04 output remains 32,991 bytes / `b489bd30b467ab38f7320c9b313f904e0bbe9a33e2bed8b346230b9f48a6053c`; no custody, reference-pixel, scientific, label, data, or model state changed. |

## Exact closeout inputs and rendered evidence

| Artifact | Bytes | SHA-256 | Result |
|---|---:|---|---|
| PRECHECK-2026-056 at failed candidate `9f440999...` | 3,710 | `016b9a899e436b880e99d547c5363802431a3f9a5e7eed1a6334dc40b06d9934` | immutable precursor authorizes closeout only; retained in Git |
| PRECHECK-2026-056 current | 5,384 | `0cd3d368d883a6bbd9791ce1063a96268bf98c5357e6451ae84683c31b0c234f` | authorizes corrected closeout and true-merge topology only |
| PETES_LAKE_MATERIAL_DEFER_DECISION | 6,050 | `6e0cb457261cc0ef48b86b15e8b21a83ec21c4b880990d83b0c79834a26c31e7` | defer; no event promotion |
| REGISTRY-2026-058 | 7,408 | `8ed73d3f9a85216e2b88b5283cff68ba81e9e040fadcaddd921a9b8d6f398525` | exact terminal r003 record |
| SOURCE-2026-033 | 3,665 | `421d0ec4d94438f3f87bd6fac170699bb5e49701f5aec5d2ec662bd23169959a` | public metadata-only HUC8 fallback observation; no archive body |
| planned U03 JSON | 56,285 | `ac9befd021d71ff779ec56ddefc894f4e39b92e64e65c2c4afb815663d1ad443` | exact replay; rejected planned post |
| planned U03 PNG | 626,846 | `4ed3870e37bf68db24805540f00614c5050c064b621ca3fc5e3c0ef244bf0d42` | original-resolution visual inspection passed; failure and no-label boundary legible |
| replacement U03 JSON | 60,069 | `1aa88c0021c610e492d2645e3f2c49a4afe96d9d907e2ee4481948a4c58f2ebd` | exact replay; pass with exclusions |
| replacement U03 PNG | 588,891 | `fd5b9ae54e1b9c3e0d495e337387d874ae911bd0f586e835b4184312d486d931` | original-resolution visual inspection passed; exclusions and no-label boundary legible |
| U04 native-contract JSON | 32,991 | `b489bd30b467ab38f7320c9b313f904e0bbe9a33e2bed8b346230b9f48a6053c` | exact replay; five rasters, twenty archive members, zero accepted pixels |
| corrected U04 native-contract module | 47,189 | `8e164b2a091c098e7c762e74f6d1a66eb243b1de25c7da09bfe10741717782d4` | descendant trace correction only; computation remains AST-identical outside trace helpers |
| U11R1 descendant-trace regression | 12,566 | `fcfb67ff06a7552959bff22f20841933642bbf68e960fc82fa1e790ef34d070c` | adversarial branch, ancestry, remote, hidden-drift, LF, mapping, CLI/test, and AST coverage |
| historical U04 CLI | 1,855 | `a874d6e3bd47c1e524948c8a8c9a357942588c3d0d13e8ff29a43ca55d028fec` | exact source and current bytes remain identical |
| historical U04 native-contract test | 6,896 | `94fbd24fcbc898c112888e71245d99fcd8bb2d91e269139db29cdde634948bca` | exact source and current bytes remain identical |

## Custody, reproducibility, and package verification

- The external controlled-intake validator with local-file hashing passes independently for r001, r002, and r003. BurnLens's own r003 loader rehashes the prior chain and reloads exactly twelve assets in states `promoted x7 / failed x1 / authorized x4`.
- The r003 terminal contract is 85,612 bytes / SHA-256 `d85dc5ec8991a50605d4501ee91cb717e4089a5243dba40e6531f520bd5d8dc3`. Its immutable plan is 26,923 bytes / `6f980a77840c7b69bf5873ab43ec92ab1db8e86b0db1ffdd6613ab56216fc42d`; terms receipt 5,354 bytes / `83f9f36cf8d6415a78c25055762a211039443602e92d3b2db20f110c50c74bcc`; asset-eight dispatch 905 bytes / `5296195e6495af4faa3393276a046ceb76ba35c1210c80587728ba45d508d3be`; failed partial 0 bytes / `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- No r004/U05R3 path and no matching Petes/NWI acquisition process exists. No provider transaction runs during closeout.
- The canonical environment rebuild passes on Python 3.12.10 with 66 locked distributions, offline runtime/geospatial checks, `uv lock --check`, compilation, and dependency integrity. A first wheel-build attempt from the lean runtime environment failed before output because that profile intentionally omits setuptools; the failure is retained and no dependency contract was weakened.
- Failed candidate `9f44099922485b9c26b4cadcc029a67423434877` retains two clean-checkout wheels built with Python 3.12.10, setuptools 82.0.1, `SOURCE_DATE_EPOCH=1784696539`, and `PYTHONHASHSEED=0`: each is 798,433 bytes / SHA-256 `8e3f28e1ad49ea0f7d3eb9663e70fd981052c8cbccd01055ff43e4314adfbb79`. Its isolated install, 169-entry / 81-command roster, eleven new-command help probes, required-argument failure, and both U03 replays pass, but U04 stops before output with `native-contract source bytes differ from the trace commit`. This precursor is not releasable.
- Correction checkpoint `fcbaa4c1044672352227f6a3047d998967d1d114` preserves historical CLI/test bytes and an invariant non-trace AST fingerprint `3e6a940b62a99c17e1b91099ce5aae66a76494b8575d8f11830b3fc551e4ec59`. From the clean, live-remote-equal canonical checkout, planned U03 reproduces 56,285-byte JSON / 626,846-byte PNG, replacement U03 reproduces 60,069-byte JSON / 588,891-byte PNG, and U04 reproduces the exact 32,991-byte JSON with zero accepted pixels.
- Post-hardening Petes regression passes 126 tests, one expected skip, and 28 subtests in 117.37 seconds. Full repository regression passes 533 tests, one expected skip, 20 retained NumPy 2.5 shape-deprecation warnings, and 78 subtests in 515.15 seconds. Final dual clean-checkout wheel, isolated-install, and replay evidence remains pending until the corrected record state is committed.
- Read-only AI-assisted audits find no remaining U11R1 trace-code blocker under the true-merge contract. These are engineering audits, not independent scientific or human-review evidence. Final clean-candidate package/replay, milestone PR review, fresh-main verification, and remote tag peel remain deliberately pending.

## Version and public-claim boundary

BurnLens package/version controls advance to 0.45.0 because this milestone adds material source-fitness, custody, review-batching, pre-reveal lock, loopback delivery, and reproducible-environment capabilities. Historical Petes run artifacts and their generators retain software version 0.44.0; changing them would break exact provenance. The label schema, accepted prototype label set, dataset, split, baseline, and model versions do not advance.

The accepted state remains `owner-approved-prototype-region-labels-v0.3.0`: five burned and five background regions across Darlene, McKay, Tepee, Green Ridge, and Grandview, with 236 core pixels / 9.44 ha and 431 excluded unknown-ring pixels. Petes Lake is not event six. This milestone creates no ground truth, inter-rater agreement, field validation, dataset, split, baseline, model, performance metric, deployment, GitHub Release object, official information, endorsement, operational readiness, or emergency-ready claim.

## Release dependency

Commit and push this corrected candidate, reproduce its wheel from independent clean checkouts, open one coherent milestone PR that closes #521, and merge it with a true merge commit. Fresh `origin/main` must preserve `20d6991cbc079f87db6a789717ebd01595c0b05c` as an ancestor and the exact reviewed head as a merge parent; squash and rebase merge are invalid. Verify the actual outputs and package from fresh main, then create and remotely peel the annotated `v0.45.0-petes-lake-material-defer` tag. A bounded lifecycle sync is required afterward to record the exact PR, merge, and tag identities, set U11 execution status to `complete`, and set release state to `verified`; U11 disposition remains `defer`. SOURCE-2026-033 preserves the public metadata-only McKenzie HUC8 fallback observation; the fallback is a separate checkpoint and cannot acquire bytes under this record.
