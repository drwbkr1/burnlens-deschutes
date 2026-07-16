# Changelog

All notable BurnLens checkpoints are recorded here. Technical evidence remains in the linked issues, PRs, commits, versions, runs, and phase records.

## v0.17.0-dual-lock-custody-readiness - candidate 2026-07-16

### P2O4-T09A - Prove mixed-version two-lock custody before the second reviewer returns

- Preserve compatibility with the exact historical `label-review-response-integrity-lock-v0.2.0` / BurnLens `0.15.0` receipt while making future receipts identify `label-review-response-integrity-lock-v0.3.0` / BurnLens `0.17.0`.
- Add an independently transcribed two-pair verifier that checks exact response and receipt bytes, packet and response-contract binding, supported receipt/software identity pairs, chronology, origin, and cross-pair distinctness without importing the receipt builder.
- Run the verifier against the actual ignored first returned response and receipt plus the exact ignored browser-QA response re-locked as a current-protocol software fixture.
- Publish `LABEL-REVIEW-DUAL-LOCK-READINESS-QA-2026-001` as JSON, semantic HTML, and a rendered 1800-by-1320 evidence card. The public outputs expose one returned-response origin, one software fixture, two distinct exact locks, zero adjudications, and no reveal authorization while withholding response content and private metadata.
- Preserve exact byte reconstruction for the v0.16.0 public first-lock outputs and the new three-output readiness package.
- Pass 163 tests, compilation, dependency health, Node syntax, privacy, semantic, original-resolution rendering, exact-output regeneration, and two byte-identical detached-source fixed-epoch 302,018-byte wheels / SHA-256 `cac65ceaf6ce75ef67d16d55379df9234a591563c94800791d972965281f80d2`; isolated install reports `0.17.0`, 27 entry points, and zero private/download entries. PR merge, fresh-main, tag, and lifecycle gates remain pending.
- Keep the scientific gate binding: the software fixture is not a second human response, minimum human custody is unmet, and no reveal, comparison, adjudication, accepted label, dataset, split, baseline, model, metric, deployment, field, official, endorsed, or operational claim is created.

Issue #394 / draft PR #395; parent second-response issue #393; base `984c6c5c46df765abebb5383877ff89b42c2076d`; response-lock source `397a28cf9c4385050a516a2892085fcd89cbcaae`; verifier source `ac410ed74a6f5abc13dc8191bac5fa4935e211a5`; public artifacts `1fb920eb1476f470ac9f9216e89a70201e643fab`; reviewed candidate head `125fcc677cba114277b8a066709d753c54ba619c`; candidate tag withheld pending merge and fresh-main release gates.

## v0.16.0-first-reviewer-response-lock - 2026-07-16

### P2O4-T08 - Preserve the first returned response before reveal

- Preserve one exact 16,443-byte returned response in ignored repository-local storage and verify SHA-256 `485e80f2563f8b723c16daa8b5e5a1172dd88e8f2a28a7dd8608c933fa64eed9`.
- Preserve a separate ignored 2,508-byte private receipt / SHA-256 `67599f794a1310e9523cded095787c918ed47d88c439e240a0b41ea6e5eb9835`.
- Add an independently transcribed public verifier for exact response/receipt bytes, packet binding, the completed 56-unit proposal-free contract, origin classification, receipt chronology, and downstream-version deferral.
- Publish `LABEL-REVIEW-RESPONSE-LOCK-QA-2026-001` as JSON, semantic HTML, and a rendered evidence card while withholding response distributions, reviewer experience, response timestamps, notes, private filenames, and private paths.
- Record the proposal reveal as operator-declared `withheld-unopened-after-lock` and explicitly state that software cannot verify file-access history, reviewer identity, expertise, independence, or scientific fitness.
- Pass 158 tests, compilation, dependency health, content-leakage and semantic audits, original-resolution review, and two byte-identical detached-source fixed-epoch 292,068-byte wheels / SHA-256 `c6a0f320b393ea7aca3aebdc93da97f7ed34901d30df298c1986d1ee4b78ee28`; isolated install reports `0.16.0` and 26 entry points.
- Keep one-of-two response status binding. Create no adjudication, accepted label set, dataset, split, baseline, model, accuracy estimate, deployment, field claim, official claim, or operational claim.

Issue #384 / PR #388 reviewed head `7a1345d187def41094ccb9d63d44958a3de809e7` merged analytically to `836eef75495dbc671bd74a8ad4112852bbf50ac6`. Record-only issue #389 / PR #390 corrected manifest chronology at checkpoint merge `27fcd3eadb1473bb603b4275f986bf62022c10bf` without changing outputs or scientific state. Source is `ec41129f9322022f28b8f788a2e08ae22145471b`; public artifacts are `9fbd97fcb66fd76172fff949580f469fc43b3f40`; verified tag object `da94fc97efc07b07d9520022fdbff42a85e8ba00`; lifecycle sync issue #391 / PR #392.

## v0.15.0-live-browser-reviewer-handoff - 2026-07-16

### P2O4-T07 - Prove the exact reviewer workbench in a live browser

- Reconstruct the exact v0.14 handoff archive and identify the explicitly unverified browser interaction path as the highest-leverage user-visible weakness.
- Add a dependency-free Node controller that launches installed Chrome with an isolated profile and loopback-only DevTools endpoint, opens the extracted `file://` workbench, records actual downloads and browser observations, and captures desktop/mobile screenshots.
- Add a fail-closed Python verifier and renderer for invalid-state behavior, all eight images and 56 fieldsets, draft download/load, exact progress/value restoration, completed response export, viewport overflow, page-target resource schemes, console/runtime/log errors, cookies, local storage, and fixture locking.
- Harden returned-response receipts with explicit `returned-independent-response` versus `software-browser-fixture` origin, task-issue binding, completion/receipt chronology, distinct decisions, and a fixture reveal prohibition.
- Record authoritative run `BL-2026-07-16-label-review-browser-qa-r001` in Chrome `150.0.7871.124`: 61 incomplete-review issues, seven-unit draft roundtrip, 56-unit completed export, 14 of each response label, no horizontal overflow at 1440 by 1000 or 390 by 844, and zero external page-target resource schemes, console errors, runtime exceptions, cookies, or local-storage entries.
- Preserve the loopback DevTools control plane as disclosed controller transport rather than application traffic.
- Pass 154 tests, compilation, Node syntax, dependency health, original-resolution review, and two byte-identical detached-source fixed-epoch 283,856-byte wheels / SHA-256 `950472207ac8f75208188584e2f8474f88a8a71e0f14fde864aa297b79076352`; isolated install reports `0.15.0`, 25 entry points, and the packaged controller.
- Keep the browser-generated response explicitly non-human and reveal-prohibited. Create no accepted label set, dataset, split, baseline, model, accuracy estimate, deployment, field claim, official claim, or operational claim.

Issue #383 / PR #385 shipped at merge `861716be16be3a0469d2268baed971be65684d48`; reviewed head `1723f87d252bda7a67680a71108fc0a65b42c587`; source `74275a061fb4054a535cc8b660bebb0021999c54`; browser artifacts `97ddbaf71372e119428868a37d214c3327523514`; verified tag object `69b32b076a7fca40ba5eceacb64aeac2a512e7b9`; lifecycle sync issue #386.

## v0.14.0-offline-reviewer-handoff - 2026-07-16

### P2O4-T06 - Isolate reviewer delivery and lock returned responses

- Rerun the shipped v0.13.0 workflow and reproduce all 18 packet/QA files byte for byte; identify manual 56-entry JSON editing beside proposal-bearing files as the highest-leverage user/evidence weakness.
- Pin the exact shipped packet and response template, then build one deterministic ZIP_STORED archive with a single root and exactly 12 allowlisted members.
- Exclude the reveal, proposal-bearing packet JSON, adjudication, QA, provider bytes, secrets, links, traversal, and network dependencies from the reviewer handoff.
- Add a self-contained offline workbench with 56 labelled fieldsets, eight blind images, native controls, decision guidance, errors/progress, local draft roundtrip, review/confirmation, and exact response-schema export.
- Add an independently implemented archive/interface verifier and a fail-closed response-lock receipt that validates the exact packet contract, records SHA-256, rejects overwrite, and rejects proposal-bearing tampering.
- Reproduce the seven committed handoff/QA files and 8,652,301-byte archive byte for byte; pass original-resolution review, served semantic/JavaScript checks, 151 tests, compilation, dependency health, and two byte-identical detached-source fixed-epoch 266,291-byte wheels / SHA-256 `08d81d19940812f51efc2673ac4f2e0e6453e134f40a5e996fe81620e003b0ef`.
- Raise BurnLens to `0.14.0` and expose 24 package entry points.
- Record the interactive browser runtime as unavailable and make no viewport, console, draft/load, or download interaction claim.
- Preserve zero completed independent responses and adjudications. Create no accepted label set, dataset, split, baseline, model, accuracy estimate, deployment, field claim, official claim, or operational claim.

Issue #379 / PR #380 shipped at merge `49c2d2cff03612b9fb4e0644c4c1ee8852a312a4`; reviewed head `50dc6cc81de58b57ee04c2f6d6c3a1499af55a70`; source `75102d79e6e184a1ecac941900fd74938cdaa972`; candidate artifacts `0400b894bcbf3938eb9b4666162512dd4263e45f`; verified tag object `b4f290fdcc8dad859bdecc7eea54866d0e1b727a`; lifecycle sync issue #381 / PR #382.

## v0.13.0-label-review-readiness - 2026-07-16

### P2O4-T05 - Make independent label review executable

- Rerun the exact v0.12.1 real-source workflow first and confirm that all ten topology-stable cross-event proposal/QA outputs remain byte-identical; identify missing independent label review, rather than proposal reproducibility, as the highest-leverage evidence weakness.
- Reopen six registered Sentinel archives and two registered MTBS clips, recompute the Darlene 3, Tepee, and McKay proposal state/target arrays, and require exact agreement with the committed rasters before sampling.
- Select 56 deterministic review units: four from every state present in each event, covering 14 present event/state strata while recording McKay/excluded as structurally absent.
- Render eight proposal-blinded first-pass pages with pre/post Sentinel imagery, continuous dNBR, and NIFC or MTBS context; keep sample-specific proposal state/target values on a separate reveal page.
- Add proposal-value-free response/adjudication templates and a separately implemented verifier that checks the packet JSON binding plus 14 referenced packet outputs, bindings, coverage, blind/reveal separation, blank evidence state, response domains, attestations, timestamps, and target-ignore invariants.
- Reproduce all 18 real-source packet/QA files byte for byte; pass original-resolution review, 144 tests, compilation, dependency health, and two byte-identical fresh-checkout fixed-epoch 240,661-byte wheels / SHA-256 `6451105a7090e67f2d4b1dee5d28d455db118f9efaf07985b76a948ef388cfeb`.
- Raise BurnLens to `0.13.0` and expose 21 package entry points, including packet generation and integrity QA.
- Record zero completed independent responses and zero adjudications. Accept the review instrument only; create no accepted label set, dataset, split, baseline, model, accuracy estimate, application, field claim, official claim, or operational claim.

Issue #375 / PR #376 shipped at merge `67dc6023859ba3ec9ce6bb375ae001ff962639c6`; reviewed head `119b1e98f7928bb1c2f09d577bfa270d903766c7`; generator/verifier source `a11ae5123728d3823ba67d22d49250d4affb18f6`; candidate artifacts `f15cc0608e2093daf0ca339c17145d50933cc743`; verified tag object `2f4db3e24e1a9bcb82ab56026b13e833004ef453`; lifecycle sync issue #377 / PR #378.

## v0.12.1-topology-stable-label-transfer - 2026-07-16

### P2O4-T04-REM - Remove filesystem topology from public run identity

- Run the shipped v0.12.0 tool first and isolate a two-file reproducibility failure: all rasters and renders remain exact, while proposal JSON changes only with an approved OneDrive link-topology transition and QA JSON changes only through the proposal hash.
- Keep fail-closed runtime verification for both approved one-link and exact-two-link topologies; add registration-manifest enforcement and reject a third link.
- Preserve exact byte, SHA-256, grid, transform, value-domain, and value-count checks while publishing a stable policy/result summary instead of the transient observed count.
- Preserve immutable v0.12.0 / `2026-001` evidence and create corrected `2026-002` proposal/QA reports and `r004` runs.
- Reproduce all ten real outputs byte for byte under ignored one-link and exact-two-link MTBS packages; retain 9,760 candidate and 54,170 ignored pixels plus zero mismatch across 63,930 QA pixels.
- Raise BurnLens to `0.12.1`; pass 137 tests, dependency health, two byte-identical fresh-checkout fixed-epoch 215,461-byte wheels / SHA-256 `e6e45cfc69aebb17b9a6396d593508b297b8461deb69463edd1ba04cc4ad99d3`, isolated import, and all 19 entry points.
- Change no classifier, threshold, source, target, label protocol, label schema, event group, output pixel, dataset, split, baseline, model, application, field claim, or operational claim.

Issue #371 / PR #372 shipped at merge `e00028509145b439d95eb302591e7cb19bd073fd`; reviewed head `345dd72363377aad3215d23a8120c42edbe85278`; source `0c2b489f34915e352cefe72ca76dea488bc8a4db`; candidate artifacts `567b9cd986a44c3a9b320f558ab7cd156d451fb4`; verified tag object `8606c61f0e1668f2b057abca177144937eae1036`; lifecycle sync issue #373 / PR #374.

## v0.12.0-cross-event-label-transfer-baseline - 2026-07-16

### P2O4-T04 - Transfer five-state proposals across Tepee and McKay

- Reproduce the shipped v0.11 source-fitness JSON/HTML/PNG byte for byte before selecting cross-event proposal transfer as the highest-leverage weakness.
- Register two exact public MTBS annual thematic clips under `SOURCE-2026-013`, with event-year nearest-neighbor U8 byte/grid/value contracts and joint USGS/USDA Forest Service attribution; commit zero provider bytes.
- Preserve Tepee SCL/window restrictions, frozen whole-event groups, five-state uncertainty, and source precedence; MTBS and SCL never independently create burn truth.
- Add the owner-authorized binary-mask fallback as an explicit event-relative background stability screen: lowest 15% normalized non-burn tail, cap 6.0, seven-of-nine coherence, no boundary-absence inference.
- Produce four traceable GeoTIFFs plus proposal JSON/HTML/PNG. Aggregate: 549 background, 9,211 burned, 18,425 unknown, 16,025 excluded, and 19,720 review-needed pixels.
- Add a separately invoked QA path that does not import the transfer classifier, reopens all six exact source assets, and reproduces 63,930 state/target pixels with zero mismatch plus 45 deterministic audits.
- Remediate live-browser claim grammar so every boundary item is explicitly `Not proven`; pass original-resolution and semantic-browser review plus four HTTP-200 raster links.
- Extend the deterministic LF checkout contract to nested cross-event JSON/HTML after fresh remote-head verification exposes Windows CRLF conversion; add a regression test before merge.
- Extend the LF contract to Python package sources and build metadata after fresh-wheel inspection proves the only source-entry differences are checkout line endings; use a fixed `SOURCE_DATE_EPOCH` for the authoritative release wheel.
- Raise BurnLens to `0.12.0`; pass 137 tests, compilation, dependency health, two byte-identical fixed-epoch 214,749-byte wheels / SHA-256 `525038b78dbc199be9851dc1b4f5854b7bd49093047c8a761446616e921e865c`, isolated import, and three new entry points.
- Accept reproducible cross-event proposal evidence while deferring accepted labels, dataset, split, baseline, model, independent human validation, field validation, and operational claims.

Issue #367 / PR #368 shipped at merge `9679e53783500c437de44fc0d033b64f0bacb0df`; reviewed head `3d49b6237cbb96356d5808723ddd5e74ecfb58c0`; generator/QA source `6d9bb2a34a32f775e4bf83249151e41c25998ee5`; proposal/QA runs `r003`; verified tag object `83a0371b9c7e75163b2e4ef5c6368103347740b4`; lifecycle sync issue #369.

## v0.11.0-cross-event-source-fitness-baseline - 2026-07-16

### P2O4-T03 - Acquire and inspect the exact cross-event pixels

- Reproduce the shipped v0.10 feasibility evidence before selecting the four exact frozen archives as the highest-leverage weakness.
- Freeze route precedence so current OData sizes/checksums govern OData archive bytes while STAC remains scene-discovery provenance.
- Preserve four fail-closed authenticated attempts that exposed early EOF, transient metadata access, non-resumable full responses, and OneDrive hard-link races.
- Register run `BL-2026-07-16-cross-event-optical-intake-r005`: four exact Sentinel-2 archives / 4,551,170,756 ignored local bytes; provider MD5/BLAKE3, local SHA-256, ZIP/SAFE/root/manifest/CRC/path and atomic-promotion gates pass; zero provider bytes committed.
- Keep provider archives single-linked while exposing a two-link OneDrive exception for the small registration metadata manifest; verify its one-read SHA-256 and every registration/header/asset field.
- Inspect full MTBS boundaries on exact native 10 m TCI and 20 m B04/B8A/B12/SCL grids without reprojection, resampling, upsampling, mosaic, or boundary shrink.
- Accept McKay at 100% pair-eligible quality and 3/3 registration windows. Accept Tepee only with 8.3441% review-needed, 5.1341% excluded, one excluded window, and one review-needed window binding.
- Render traceable JSON, semantic HTML, and 1,800 by 1,450 PNG; pass original-resolution and live semantic-browser review.
- Correct a pre-tag trace mismatch found by fresh merged-main semantic readback: fail closed on frozen feasibility schema drift and expose both label protocol `burn-scar-label-protocol-v0.1.0` and implemented schema `burn-scar-five-state-schema-v0.1.0` across JSON, HTML, and PNG.
- Raise BurnLens to `0.11.0`; pass 129 tests, compilation, dependency health, candidate and fresh merged-main wheel / isolated-import gates, and four cross-event console entry points.
- Create no label, dataset, split, baseline, model, application, accuracy/generalization claim, independent human validation, or field claim.

Issue #361 / PR #362 / analytical merge `6a6da910849daefa918ed56af6631b2ec44bc211`; trace-remediation issue #363 / PR #364 / shipped merge `01c3aa4abeb89e3f15771571276a25d33e44d390`; source `cf1d9101e2760bf7d779b6fae68e605bb8809c1c`; artifacts `621c74f4e6f2d691438736b38d3019a6bd453f50`; verified tag object `eca7ba5362518684f2a1e25d5abdbc1707e24a61`; lifecycle sync issue #365.

## v0.10.0-cross-event-feasibility-baseline - 2026-07-15

### P2O4-T02 - Freeze exact cross-event acquisitions and leakage groups

- Re-run all eight shipped label-proposal/QA artifacts from synchronized `main`; confirm byte-identical predecessor evidence before selecting work.
- Add a fail-closed current-source capture for official Census TIGERweb, MTBS occurrence/boundary, and CDSE Sentinel-2 L2A STAC metadata, including current collection/license identity and zero imagery download.
- Select exact Tepee and McKay pre/post product pairs under same-platform/tile/orbit/processing rules; expose and exclude Milli because no one tile covers its full MTBS boundary.
- Freeze event, scene, geography, and time group IDs before acquisition or tiling; report 10.925 km Darlene-McKay, 34.926 km Darlene-Tepee, and 27.258 km McKay-Tepee representative-point distances as diagnostics, not independence proof.
- Render deterministic JSON, semantic HTML, and 1,800 by 1,250 PNG; pass original-resolution and live semantic-browser review.
- Raise BurnLens to `0.10.0`; add five tests for group selection, tile-seam exclusion, source-boundary failure, inclusive geometry, and deterministic rendering. Both the candidate and fresh merged-main clone pass 110 tests, compilation, dependency health, isolated `0.10.0` import, and exact three-artifact reconstruction.
- Preserve null application/dataset/split/baseline/model state and zero provider imagery bytes. A fresh no-hardlink clone of merged `main` passes manifest, LF, local-link, secret/raw-exclusion, original-resolution, and live semantic-browser gates.
- Ship issue #357 through PR #358 at squash merge `5bfa1527410e98d8034b35ad68f6c50d5a1ec628`; verified annotated tag object `dbfda10ca50c39d8e8924096e740e71643e1f133` remotely peels to that exact merge as `v0.10.0-cross-event-feasibility-baseline`.

Issue #357 / PR #358; generator/assessor source `ea3e164d09872825a0fadc64b9492e30c85c83c8`; lifecycle synchronization issue #359 / PR #360.

## v0.9.0-label-proposal-baseline - 2026-07-15

### P2O4-T01 - Build a reviewable five-state proposal and separate QA

- Run the shipped content-registration tool first and reproduce its JSON, HTML, and PNG byte for byte before choosing the next weakness.
- Reverify the exact registered pair, AOI, NIFC snapshot, accepted optical/registration predecessors, source roles, terms, and null dataset/split/baseline/model state.
- Implement `burn-scar-five-state-schema-v0.1.0` and `darlene3-burn-scar-label-proposal-v0.1.0` on the exact 600 by 450 native-20m grid without source reprojection or resampling.
- Require affirmative context, multi-signal change, and local coherence for burned candidates; affirmative four-signal stability away from expanded context for background candidates; preserve unknown, excluded, and review-needed as explicit `255` ignore.
- Retain 161,238 background, 18,543 burned, 71,897 unknown, 870 excluded, and 17,452 review-needed pixels; candidate target coverage is 66.5856% and explicit ignore is 33.4144%.
- Add a separately invoked verifier that imports no proposal-classification helper, reopens exact source pixels, recomputes every signal/state, validates GeoTIFF trace contracts, and compares all 270,000 state and target pixels.
- Record 100% state and target agreement, zero all-pixel mismatch, and zero disagreement across a deterministic 120-sample audit covering all five states and the candidate-burn transition boundary.
- Render `LABEL-PROPOSAL-2026-001` and `LABEL-QA-2026-001` as traceable JSON/HTML/PNG plus companion-state and candidate-target GeoTIFFs. Verify both original-resolution images and live semantic HTML in the browser.
- Make the limitation explicit: separate software agreement under one shared contract is not independent human annotation, field validation, ground truth, accuracy, or generalization evidence.
- Accept the exact result as reviewable one-event proposal evidence and defer a dataset, split, baseline, model, application, deployment, performance claim, and operational wildfire result.

Issue #353 / PR #354 shipped the analytical checkpoint at squash merge `55c70d076c97f5d2727bdd0d91f39be0f9bac1d3`. Generator/verifier source `814bb5402c04708f1515135683eac1304bf075c1` produces the eight exact artifacts recorded in `MANIFEST-2026-010`. A fresh no-hardlink clone of merged `main` passes 105 tests, compilation, dependency health, isolated `0.9.0` wheel import, exact eight-artifact reconstruction, LF checks, manifest readback, original-resolution and live-browser review, raw-byte exclusion, and secret scan. The fresh merged-source wheel is 142,050 bytes; its first gate archive is SHA-256 `9f2dbb851cf9bef26c7154842350e26d2fe803efd6a303e6f374d9c32c48c176`. Repeated builds have identical extracted contents but timestamp-dependent ZIP hashes. Annotated tag object `5a95b4d39710fc81a1193a83ad41a766cba61834` remotely peels to the analytical merge as `v0.9.0-label-proposal-baseline`; lifecycle synchronization is issue #355 / PR #356.

## v0.8.0-content-registration-baseline - 2026-07-15

### P2O3-T01 - Measure pair-local optical content registration

- Split registration measurement from later label proposal work at the fail-closed prerequisite instead of creating labels against unproved alignment.
- Reverify the exact two-product registered package, accepted optical predecessor, AOI, source scaling, native B04/B8A/B12/SCL grids, and null label/dataset/baseline/model state.
- Freeze `local-content-registration-v0.1.0`: independent per-scene reflectance gradients, no shared correlation mask, twelve fixed 150 by 150 native-20m windows, Hann taper, phase-only cross-power, and localized 100x DFT refinement.
- Gate each window at 90% eligible pair-quality pixels, two confident bands, peak ratio 2.0, 0.15-pixel maximum band deviation, and 0.50-native-pixel / 10 m consensus residual.
- Preserve current official Sentinel product-quality context without allowing it to replace local measurement. Both packaged reports pass global QC while explicitly saying VNIR/SWIR bands were not registered and spatio-residual histograms were not computed.
- Recover synthetic translations within 0.02 pixel at 0.01-pixel sampling and fail closed on textureless signals or incompatible human/machine decisions.
- Measure the exact pair: all 12 windows pass; median residual `0.0224` pixel, p95/max `0.0361` pixel, minimum eligible coverage `94.9556%`, minimum peak ratio `7.5916`, maximum band deviation `0.0400` pixel.
- Catch and correct a real XML provenance defect before acceptance: provider messages/values are siblings of inspection metadata, not descendants. The final evidence preserves the exact cautions and values.
- Render `CONTENT-REGISTRATION-2026-001` as normalized JSON, semantic HTML, and a deterministic 1800 by 1250 PNG with complete source/version/run trace and a visible no-label boundary.
- Accept local content registration only. Create no label array, companion state layer, dataset, split, baseline, model, metric, application, deployment, performance claim, or operational wildfire result.

Issue #347 / PR #348 merged the analytical candidate at `c01cdb12033e7a9440ad0502b92a8887fd79ed1d`. Generator source `5287704a37f03d96e47467afba8623f7be643129` produces JSON `f0682f51bebe93d970774748c23317d8759bae4b7e34478fb6659d9606b28645`, HTML `b8ed29f1f18acc75275e0cbef0fd6d0b1d6764ef2737d1f5e53bb45d5fcd407f`, and PNG `70ba55e6a15f2b712bd167e8d3d0736daf19284bae0f3f0f721a07a3e1c017f1`. Post-merge Windows checkout reproduced the PNG but exposed CRLF JSON/HTML against the declared LF contract, so the release tag was withheld. Issue #349 / PR #350 added explicit registration-artifact LF attributes and regression coverage at remediation merge `1297471be45200c40f9f40746e85b437ce6e0c0d`; no analytical output changed. A fresh no-hardlink clone of that merged `main` checks both text artifacts out with LF, reconstructs all three hashes byte for byte, passes 94 tests, compilation, dependency health, a 115,120-byte wheel build and isolated `0.8.0` import, and confirms zero tracked download files. Annotated tag object `14edfad3ce89dbd9179a54eb1e29811e41d258c0` remotely peels to the remediation merge as `v0.8.0-content-registration-baseline`. Wheel SHA-256 is `98100911ab3b75cd38aac740e1ffe7cecf212b9164f8a1000f2ccf4072dfd497`; lifecycle synchronization is issue #351 / PR #352.

## v0.7.0-optical-pair-protocol-baseline - 2026-07-15

### P2O2-T06 - Prove the exact optical pair and five-state burn-scar protocol

- Freeze and freshly validate one exact same-Sentinel-2A, same-tile, same-relative-orbit, same-baseline pre/post L2A pair around the approximate Darlene 3 start.
- Resolve current Copernicus terms, attribution, OData authentication, quota, Collection 1 L2A, and baseline-05.10 SCL semantics from official primary sources.
- Add a CDSE-only protected-credential boundary, exact public-metadata drift gate, sequential bounded delivery, safe full-response fallback when a server ignores Range, provider MD5/BLAKE3 checks, local SHA-256, SAFE/ZIP/root/manifest/CRC checks, and all-or-none atomic registration.
- Preserve four failed runs rather than hiding them: an OData attribute projection defect, an early post response, a pre-archive OneDrive hard-link race, and a post-archive promotion race. Add tested safe-state normalization after the fourth run exposed a generic transaction traceback.
- Open the real TCI/B04/B8A/B12/SCL AOI windows, read product scaling/offsets, require EPSG:32610 and exact native-grid equality, and disclose that source-grid equality does not prove subpixel content registration.
- Correct the real-file metadata join from raster filename `B04` to physical band `B4` and retain a regression test.
- Render `OPTICAL-PAIR-2026-001` as deterministic LF-stable JSON, semantic HTML, and an 1800 by 1250 original-resolution pre/post/continuous-dNBR evidence card with Copernicus attribution, NIFC-context limits, warnings, and full null-version traceability.
- Record pairwise AOI quality of 98.9137% eligible comparison, 0.7641% review-needed, and 0.3222% excluded; accept the pair for protocol evidence only.
- Version `burn-scar-label-protocol-v0.1.0`: burned/background-candidate may later map to 1/0, while unknown/excluded/review-needed remain ignored. Require a companion state layer, local registration measurement, boundary review, event/scene/geography/time grouping before tiling, independent QA, and disagreement audit.
- Create no label array, dataset, split, baseline, model, analytical metric, application, deployment, performance claim, or operational wildfire result.

Issue #343 / PR #344 shipped this checkpoint at merge `136d4d0919eba7144881c22163a149c89fee5a76`. Clean-main pair re-verification, 86 tests, compilation, dependency health, byte-identical JSON/HTML/PNG reconstruction, and wheel/isolated-import checks pass. Annotated tag object `28d12fb5ef5c70054b8af5fd3c4847ba268000a1` remotely peels to that merge as `v0.7.0-optical-pair-protocol-baseline`; lifecycle issue #345 / PR #346 records the provenance-only synchronization.

## v0.6.0-burn-scar-target-baseline - 2026-07-15

### P2O2-T05 - Activate burn-scar binary-mask fallback and publish target-path evidence

- Record the owner's decision to activate the already-established burn-scar binary-mask fallback as `target-burn-scar-v0.2.0` without changing the project promise, audience, binary CV task, phase outcomes, GEOINT workflow, or use boundaries.
- Retain the best bounded NOAA-21 active-fire observation as complementary native-scale reference evidence only; reject direct labels because 375 m support and a 2.48-hour optical offset cannot define 10-20 m pixel truth.
- Query the current official MTBS 2024 and all-years occurrence services. The 2024 inventory returns 941 records, no Darlene name match, and zero AOI features; the all-years layer also returns zero AOI features.
- Preserve MTBS as methodology and potential cross-fire/future reference evidence, not field truth or an available exact Darlene 3 label. Do not convert its six severity classes into a multiclass BurnLens target.
- Add deterministic `0.6.0` target-decision tooling with fail-closed source evidence validation and render the decision as normalized JSON, semantic HTML, and a 1600 by 1050 evidence card.
- Preserve merged run `TARGET-DECISION-2026-001` after post-merge reconstruction exposed checkout-dependent source-record hashing; issue #339 adds LF-normalized structured-input hashes, explicit LF target serialization, a line-ending regression test, and immutable corrected run `TARGET-DECISION-2026-002` before the release tag is created.
- Define the next gate: one legally usable, visually validated pre/post optical pair plus an uncertainty-preserving binary protocol before any label array, dataset, spectral baseline, or model.
- Update the README, controlling goal, agent instructions, roadmap, phase status, version history, case study, prompt/build log, and devlog so no active control still says the owner choice is pending.

Issue #337 closed through PR #338 at analytical merge `68971e9709b886adf8575a58d32694aad42f038e`. Sixty-eight post-merge tests, compilation, and dependency health passed, but reconstruction correctly failed because the newly checked-out MTBS record's CRLF bytes changed the `r001` JSON input hash; HTML and PNG remained byte-identical. The tag was withheld. Issue #339 closed through PR #340 at remediation merge `bcb71ebd01d3184f8de24318428309e61d33e54f`. Source `cfbf357634cdcf9e68c3af78bfcb3e195bebc17a` produces corrected run `BL-2026-07-14-target-decision-r002`: JSON `ac67f6c34a934d639c215ee98b181f1114b5624acafb85f65b1e2f3e804ce4d4`, HTML `0c1279e5e1047ff251dcd65f068d3d45bf2c6982e6a308972205e9d0a76879d4`, and PNG `36f221aa6393ad07f14d4d7bb54b1f171ef0636ebb5640a11ab02ab9c5a9b5b0`. All 69 post-merge tests, compilation, dependency health, canonical LF checkout, three byte-identical fresh-`main` reconstructions, offline wheel build/import, secret/raw-byte exclusion, issue closure, PR merge, and remote tag identity pass. Annotated tag object `0b4e0ff226be0d78b3b510b7786be0ca1c817887` remotely peels to the remediation merge as `v0.6.0-burn-scar-target-baseline`. Wheel SHA-256 is `5915c9c707123df7b913e7564e9c20469c31cd3df494966d66a48dda298f3d3d`. The unavailable `python -m build` entry point and browser policy block remain recorded limitations, not passing claims. Raw provider bytes, label arrays, datasets, splits, baselines, models, analytical metrics, applications, deployments, and performance claims created: zero. Lifecycle synchronization is issue #341 / PR #342.

## v0.5.0-observation-geometry-baseline - 2026-07-14

### P2O2-T04 - Complete NOAA-21 geometry comparison and label-feasibility protocol

- Query the complete official CMR `VJ214IMG.002` inventory for the frozen AOI and event window and inspect all 23 exact active-fire granules.
- Generalize the fail-closed atomic intake boundary for a caller-supplied exact variable-size contract while preserving the shipped three-asset default behavior.
- Acquire one exact `VJ203MODLL.021` companion only after a material candidate is identified; register the final 24-asset / 83,723,055-byte package under contract SHA-256 `af396fcbf6fb32860c4f76111ab74ac0f3d2c810ab2c1aba19903337a757ad3c`.
- Compare real AOI confidence, geolocation QA, residual bowtie, view zenith, time offset, and NIFC-reference agreement for every candidate.
- Select the `A2024179.2118` day observation: 11 qualified AOI records, zero residual-bowtie exclusions, 31.01-degree median view zenith, and more than 1,000 columns from the nearest scan edge, versus the shipped approximately 69-degree scan-edge baseline.
- Add `weak-reference-label-feasibility-v0.1.0`, preserving positive reference, negative candidate, unknown, excluded, and review-needed states without creating labels.
- Render `OBSERVATION-GEOMETRY-2026-001` as deterministic JSON, semantic HTML, and a 1600 by 1100 evidence graphic with complete traceability and public-use boundaries.
- Record decision `ACCEPT_COMPLEMENTARY_REFERENCE_GEOMETRY_DEFER_LABELS`: the 2.48-hour time offset and 375 m support still cannot define 10-20 m segmentation truth.
- Preserve fail-closed link safety when OneDrive temporarily exposed an asset through a second hard link; the unchanged exact retry passed after the link disappeared.

Issue #333 closed through PR #334 at merge `1c85496d9d488c0d2d5a58207d8b4786a683ba52`. Annotated tag object `cb9e675789d8ca4c4f8a5f4828331d41d023038e` remotely dereferences to that exact commit as `v0.5.0-observation-geometry-baseline`. Generator source is `89d50c24a696cc7e3ec023eec00b021a4a0cdda6`. Sixty-five post-merge tests, compilation, dependency health, byte-identical real-package reconstruction, original-resolution visual review, real in-app browser validation, secret/raw-byte exclusion, diff checks, issue closure, and remote tag identity pass. Raw provider bytes committed: zero. Label array, dataset, split, baseline, model, application, deployment, and performance claim: none. Lifecycle synchronization is issue #335 / PR #336.

## v0.4.0-authenticated-source-baseline — 2026-07-14

### P2O2-T03 — Authenticated exact-package acquisition and real-source inspection

- Add a secret-safe CDSE/Earthdata acquisition path for the exact frozen package: exact authentication hosts, HTTPS-only allowlisted redirects, cross-host authorization stripping, redacted errors, sanitized state, bounded/resumable partial downloads, native signatures, exact sizes, checksums, and atomic promotion.
- Exercise the owner-authorized machine-bound credentials without committing usernames, passwords, tokens, cookies, signed URLs, credential payloads, or credential-store details.
- Acquire and register the exact three provider assets totaling 1,169,997,942 bytes in ignored local raw storage; independently re-verify the exact four-entry registered package and all current hashes.
- Open the real Sentinel SAFE/JP2 and VIIRS HDF5/NetCDF-4 files, enforce expected grids and arrays, decode relevant QA flags, and inspect the frozen AOI.
- Render `SOURCE-INSPECTION-2026-001` as normalized JSON, semantic HTML, and a 1600x1100 evidence image with the real Sentinel crop, NIFC incident-reference outline, all eight AOI VIIRS records, residual-bowtie exclusions, scan-edge warning, attribution, and full traceability.
- Record a real-file decision of `ACCEPT_SOURCE_REFERENCE_DEFER_LABELS`: the package is readable and reference-relevant, but approximately 69-degree VIIRS view geometry, residual-bowtie records, temporal offset, and 375 m-to-10/20 m scale mismatch prevent direct label or dataset promotion.
- Pin `h5py==3.16.0`, `numpy==2.5.1`, and `rasterio==1.5.0` for reproducible native source inspection.

Issue #329 closed through PR #330 at merge commit `7678cf41b64e128106c199b913fe74590a52cf80`; the annotated `v0.4.0-authenticated-source-baseline` tag object `98228058b232bc0838eb976f982ef4775b711776` remotely dereferences to that exact commit. Acquisition run `BL-2026-07-14-authenticated-intake-r001` and inspection run `BL-2026-07-14-source-inspection-r001` are the real workflow evidence. All 56 tests, compilation, dependency health, offline wheel build/import, secret/raw-byte exclusion, diff checks, and byte-identical post-merge reconstruction pass. The semantic page passes in-app browser review with no console errors or horizontal overflow. Raw provider bytes committed: zero. Label schema, dataset, split, baseline, model, application, deployment, and performance claim: none.

## v0.3.0-intake-transaction-baseline — 2026-07-14

### P2O2-T02 — Atomic exact-pair intake before credentials

- Add `paired-intake-contract-v0.4.0`, pinning the exact Sentinel-2 SAFE ZIP and NOAA-21 VIIRS active-fire/geolocation files, identities, sizes, containers, pair token, available provider checksums, and transaction invariants under one digest.
- Fail closed on incomplete, unexpected, renamed, malformed, size-mismatched, unsafe/corrupt ZIP, checksum-invalid, pair-mismatched, cross-filesystem, or destination-colliding input.
- Record local SHA-256, MD5, and BLAKE3 only after all three assets pass; write provenance in quarantine and atomically promote the complete directory without overwriting existing raw state.
- Reject symlink/junction-backed quarantine paths and symlinked or multiply-linked asset files so registered bytes cannot alias mutable storage outside the transaction.
- Roll back the provisional registration manifest if atomic rename fails, preserving a clean validated quarantine that can be retried without weakening any gate.
- Add registered-package verification that re-reads the manifest, revalidates exact assets and contract identity, recomputes hashes, and makes post-promotion mutation fail visibly.
- Add a deterministic temporary synthetic rehearsal that proves partial rejection, checksum-tamper rejection, successful complete-set promotion, and zero retained fixture bytes.
- Render `PAIR-INTAKE-REHEARSAL-2026-001` as normalized JSON, semantic HTML, and a 1600x1200 evidence card that separates real `BLOCKED_OWNER_CREDENTIAL` state from synthetic transaction proof.
- Record the exact public CDSE/CMR metadata snapshot with a fixed observation time, explicitly separate it from later deterministic run times, and preserve the owner stop: zero credentials, live provider requests, provider assets, provider bytes, and promoted real packages.
- Record the owner's later CDSE and Earthdata authorization in `ACCESS-2026-006` without storing or exercising credential material; authenticated delivery and provider-file fitness remain unverified.

Issue #325 closed through PR #326 at merge commit `ee1a1d678ad888b595dc3c7b215f787ea5156582`; the annotated `v0.3.0-intake-transaction-baseline` tag resolves to that exact commit. Report-generator source remains `ac8ee43151991c38ccf5d446a53c09b617afeb54`. Thirty-seven post-merge tests, dependency checks, deterministic reconstruction, original-resolution visual review, claims review, remote tag verification, and zero-secret/provider-byte checks pass. This checkpoint does not prove provider delivery, real-file integrity, source fitness, fire presence, label readiness, a dataset, baseline, model, application, deployment, or performance.

## v0.2.0-aoi-baseline — 2026-07-13

### P2O2-T01 — Final Darlene 3 modeling AOI

- Retain the exact public NIFC WFIGS Darlene 3 final-perimeter feature as an immutable 47,483-byte reference snapshot with SHA-256 `3d615d4be88f65806399e3733491ab0d95e16ac91ea86b5a00b3ead81ec17abe`.
- Add checksum/identity/geometry validation plus deterministic WGS84-to-UTM projection that matches NIFC's independent EPSG:32610 extent within 0.000220 m.
- Derive `aoi-darlene3-model-v0.2.0`: 12 km by 9 km / 108 km2, using 2 km context and a 1 km outward grid snap.
- Correct the discovery-box assumption: the final AOI is 48.096% smaller by projected bounding-area comparison but extends 2.883 km farther east to contain the complete official reference.
- Verify the final envelope within Census Deschutes County and within the selected Sentinel/VIIRS metadata footprints.
- Render deterministic JSON, semantic HTML, and PNG evidence; add the living repository case study; pass 16 tests and original-resolution visual review.
- Preserve the credential stop and all no-model/no-operational boundaries. One reference vector exists; provider imagery, labels, datasets, baselines, models, detections, and performance claims do not.

Shipped through PR #322 at merge commit `fffd3dda123d7c43fe678dca9adfd8feb73de158`; issue #321 closed and the annotated `v0.2.0-aoi-baseline` tag resolves to that exact commit. Sixteen post-merge tests pass, a fresh pipeline run reproduces the committed JSON/HTML/PNG hashes byte for byte, and the public PR, README, living case study, source record, and PNG render were verified. Issue #323 / PR #324 records the lifecycle synchronization. No credential, provider imagery, label, dataset, baseline, model, detection, performance result, application, or deployment was added.

## v0.1.2-access-integrity-baseline — 2026-07-13

### P2O1-T03 — VIIRS delivery validation and credential boundary

- Exercise both exact LP DAAC delivery routes without credentials and reject a default-client `401` plus two browser-style `200` Earthdata Login HTML bodies as non-assets.
- Add a fail-closed Python validator that requires the native HDF5/NetCDF-4 signature and a plausible minimum size before provider bytes can enter provenance.
- Add deterministic JSON, semantic HTML, and PNG evidence rendering. The normalized report is `VIIRS-ACCESS-PRECHECK-2026-001`, run `BL-2026-07-14-access-precheck-r001`.
- Verify eight unit checks, deterministic JSON/HTML reconstruction, deterministic PNG reconstruction, visual layout, warning language, no signed-URL/credential retention, and deletion of rejected response bodies.
- Correct the access posture: NASA-led product use remains open and citable, while LP DAAC byte delivery requires Earthdata Login authentication and application authorization.
- Preserve the paired-source STOP. Both CDSE and Earthdata credentials now require explicit owner approval before source-asset intake.

Shipped through PR #318 at merge commit `d4ce26c87341e4d3798a0d84e257a964ebd2cde0`; issue #317 closed and the annotated `v0.1.2-access-integrity-baseline` tag resolves to that exact commit. The rendered PR and branch README, post-merge tests, deterministic report rebuild, and evidence hashes were verified. No provider source asset, fire-mask pixel, geolocation array, label, dataset, baseline, model, analytical metric, raster, vector, map, application, or wildfire detection is created.

## v0.1.1-asset-readiness-baseline — 2026-07-13

### P2O1-T02 — Exact Sentinel/VIIRS asset-access readiness

- Pin one post-report Sentinel-2 L2A scene and its exact CDSE product UUID, stable whole-product route, S3 path, provider checksums, native band/quality candidates, and credential requirements.
- Pin the closest same-day NOAA-21 VIIRS active-fire swath and its required terrain-corrected geolocation companion, stable Earthdata Cloud routes, formats, concept identifiers, and 46-minute-40.976-second offset from the Sentinel acquisition.
- Record the only defensible future reference role: VIIRS classes 8–9 may become candidate positive evidence after valid geolocation, AOI, temporal/view-angle, and human review; class 7 remains review/unknown, and non-detection is not automatic background.
- Retain `ASSET-READINESS-2026-001`, a metadata-only normalized fixture with SHA-256 `c5bcfbf57cf23a7bf3ed9bd1302461b2ba1ee101ab05b7d935419223763e5ce7`.
- Re-open F04-A and stop: Sentinel product access requires an owner-approved CDSE credential, while no provider asset may be downloaded under this checkpoint.

Shipped through PR #314 at merge commit `cf4aba2f40aa426f28f09b1b1b1bad895394198b`; the annotated `v0.1.1-asset-readiness-baseline` tag resolves to that commit. The rendered PR, merged F04-A, normalized fixture, and issue #312 closure were verified on GitHub. This checkpoint creates no application, dataset, source-asset copy, label, baseline, model, metric, run, raster, vector, map, detection, or public analytical result.

## v0.1.0-source-metadata-baseline — 2026-07-13

### P2O1-T01 — First source stack and metadata discovery

- Select a bounded Darlene 3 / La Pine metadata-discovery envelope without representing it as an official perimeter.
- Resolve current primary-source terms and intended evidence roles for Copernicus Sentinel-2 L2A, NASA VIIRS Collection 2 active-fire products, and Oregon incident context.
- Verify no-secret public metadata access through the official CDSE STAC catalog and NASA Common Metadata Repository.
- Retain `METADATA-2026-001`, containing five Sentinel-2 L2A items and 124 VIIRS granule records, with asset hrefs and source bytes excluded.
- Defer FIRMS archive/API delivery because it requires Earthdata/email authentication or a map key.
- Pass F04-A only for the completed metadata action; keep all asset intake, processing, labels, baselines, models, runs, maps, and analytical claims blocked.

Shipped through PR #310 at merge commit `6abe87bba486e3fe49b6c06178b454335663cb73`; the annotated `v0.1.0-source-metadata-baseline` tag resolves to that commit. The rendered Phase Status, F04-A decision, and metadata fixture were verified on GitHub after merge. No application, dataset, label, baseline, model, metric, run, raster, vector, map, or public analytical result is created by this checkpoint.

## v0.0.8-execution-goal-baseline — 2026-07-13

### BL-GOV-001 — Controlling execution goal and roadmap

- Adopt the owner-approved long-running goal as BurnLens's controlling authority.
- Preserve the established portfolio thesis, target reviewer, binary segmentation task, active-fire primary target, burn-scar fallback, GEOINT workflow, use boundaries, source precedence, and traceability requirements.
- Treat the six phase objectives as proof outcomes and their task order as a revisable planning hypothesis.
- Reconcile the latest Phase One planning-only decision with active status and roadmap records.
- Establish standing Codex authority and the exact owner stop conditions.
- Require every BurnLens application, public website, deployment, and case study to live in and ship from `drwbkr1/burnlens-deschutes`.
- Add active phase status, version history, prompt/build logging, and a human-readable devlog.

No data, AOI, labels, pipeline, model, metric, run, map, analytical output, or public performance claim is created by this checkpoint.

Verified merge: `22a8d88435cb8d5b900a398b7482c3b7277d2ee6` via PR #291. The annotated tag resolves to that commit.
