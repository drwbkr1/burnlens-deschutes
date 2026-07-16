# BurnLens Phase Status

## Status as of 2026-07-16

| Phase | Proof outcome | Status | Evidence and next gate |
|---|---|---|---|
| 1 — Scope and controls | Coherent promise, task, source posture, repository controls, traceability, and acceptance evidence | **Accepted and versioned for Phase Two planning; no analytical release** | P1O7-T08 / PR #294 records the decision. #290 / PR #291 and `v0.0.8-execution-goal-baseline` establish the current control baseline. |
| 2 — Data foundation | Legally usable, versioned, leakage-resistant data/label/baseline package with model-readiness decision | **Active; verified cross-event proposal and separate QA shipped; dataset not created** | P2O4-T04 / issue #367 / PR #368 is shipped at verified `v0.12.0-cross-event-label-transfer-baseline`: all 63,930 Tepee/McKay state and target pixels reproduce with zero mismatch while Tepee exclusions bind. Independent human review, a split, baselines, and model-readiness remain open. |
| 3 — Model evidence | One bounded model adds reproducible value beyond the strongest baseline or is rejected honestly | **Blocked** | The target decision is resolved; an accepted Phase Two label/dataset/baseline package and model-readiness decision are still missing. |
| 4 — CV-to-GEOINT product | Accepted model/baseline becomes a valid georeferenced run and repository-owned evidence interface | **Blocked** | Requires an accepted Phase Three model or Phase Two baseline-only route. |
| 5 — Reliability | Integrated system is reproducible, accessible, secure, failure-visible, performant, and reversible | **Blocked** | Requires an accepted Phase Four run package and interface. |
| 6 — Publication | One coherent, licensed, citable, traceable portfolio release and closeout | **Blocked** | Requires an accepted Phase Five candidate, resolved licensing, verified claims, and a repository-owned production surface. |

## Verified capability inventory

| Evidence class | Current state |
|---|---|
| Latest repository evidence baseline | Shipped `v0.12.0-cross-event-label-transfer-baseline` at merge `9679e53783500c437de44fc0d033b64f0bacb0df`; tag object `83a0371b9c7e75163b2e4ef5c6368103347740b4`; generator/QA source `6d9bb2a34a32f775e4bf83249151e41c25998ee5` |
| Observation-geometry baseline | BurnLens `0.5.0`; issue #333 / PR #334; generator source `89d50c24a696cc7e3ec023eec00b021a4a0cdda6`; tag object `cb9e675789d8ca4c4f8a5f4828331d41d023038e`; 65 post-merge tests passing |
| Burn-scar target decision baseline | BurnLens `0.6.0`; issue #337 / PR #338 plus issue #339 / PR #340; remediation merge `bcb71ebd01d3184f8de24318428309e61d33e54f`; generator source `cfbf357634cdcf9e68c3af78bfcb3e195bebc17a`; target `target-burn-scar-v0.2.0`; verified annotated tag; 69 post-merge tests; no label, dataset, baseline, or model |
| Optical-pair protocol baseline | BurnLens `0.7.0`; issue #343 / PR #344; merge `136d4d0919eba7144881c22163a149c89fee5a76`; verified tag object `28d12fb5ef5c70054b8af5fd3c4847ba268000a1`; exact same-orbit Sentinel-2A pair; 2,254,805,631 local/ignored bytes; `burn-scar-label-protocol-v0.1.0` design only; label pixels, dataset, baseline, and model remain absent |
| Content-registration baseline | BurnLens `0.8.0`; issue #347 / PR #348 analytical merge `c01cdb12033e7a9440ad0502b92a8887fd79ed1d`; issue #349 / PR #350 remediation merge `1297471be45200c40f9f40746e85b437ce6e0c0d`; generator `5287704a37f03d96e47467afba8623f7be643129`; verified tag object `14edfad3ce89dbd9179a54eb1e29811e41d258c0`; all 12 windows pass; labels remain unimplemented |
| Label-proposal baseline | BurnLens `0.9.0`; issue #353 / PR #354; merge `55c70d076c97f5d2727bdd0d91f39be0f9bac1d3`; verified tag object `5a95b4d39710fc81a1193a83ad41a766cba61834`; source `814bb5402c04708f1515135683eac1304bf075c1`; `burn-scar-five-state-schema-v0.1.0`; five native-grid states; 33.4144% explicit ignore; separate all-pixel software QA and 120-sample audit pass; dataset and independent human validation absent |
| Cross-event feasibility baseline | BurnLens `0.10.0`; issue #357 / PR #358; merge `5bfa1527410e98d8034b35ad68f6c50d5a1ec628`; tag object `dbfda10ca50c39d8e8924096e740e71643e1f133`; generator/assessor `ea3e164d09872825a0fadc64b9492e30c85c83c8`; Tepee and McKay selected, Milli tile-seam exclusion; whole groups frozen before acquisition; provider imagery, dataset, and split absent |
| Cross-event source-fitness baseline | BurnLens `0.11.0`; issue #361 / PR #362 and trace-remediation issue #363 / PR #364; merge `01c3aa4abeb89e3f15771571276a25d33e44d390`; verified tag object `eca7ba5362518684f2a1e25d5abdbc1707e24a61`; source `cf1d9101e2760bf7d779b6fae68e605bb8809c1c`; four exact archives / 4,551,170,756 ignored local bytes; McKay 100% eligible and 3/3 registration pass; Tepee 86.5217% eligible with visible quality/window exclusions |
| Cross-event label-transfer baseline | BurnLens `0.12.0`; issue #367 / PR #368; merge `9679e53783500c437de44fc0d033b64f0bacb0df`; tag object `83a0371b9c7e75163b2e4ef5c6368103347740b4`; source `6d9bb2a34a32f775e4bf83249151e41c25998ee5`; exact Tepee/McKay proposals; 9,760 candidate / 54,170 ignored; separate QA reproduces 63,930 pixels with zero mismatch; dataset and independent human validation absent |
| Authenticated source baseline | BurnLens `0.4.0`; issue #329 / PR #330; generator source `9a7e614fbfbbcd4c5a6795417121cafb82ae5dcc`; annotated tag object `98228058b232bc0838eb976f982ef4775b711776`; 56 post-merge tests passing |
| Objective baseline tag | `v0.0.8-execution-goal-baseline`, verified to resolve to `22a8d88435cb8d5b900a398b7482c3b7277d2ee6` |
| Source-metadata baseline | `v0.1.0-source-metadata-baseline`, verified to resolve to `6abe87bba486e3fe49b6c06178b454335663cb73` via PR #310 |
| Asset-readiness baseline | `v0.1.1-asset-readiness-baseline`, verified annotated tag resolving to `cf4aba2f40aa426f28f09b1b1b1bad895394198b` via PR #314 |
| Access-integrity baseline | `v0.1.2-access-integrity-baseline`, verified annotated tag resolving to `d4ce26c87341e4d3798a0d84e257a964ebd2cde0` via PR #318 |
| AOI baseline | `v0.2.0-aoi-baseline`, verified annotated tag resolving to `fffd3dda123d7c43fe678dca9adfd8feb73de158` via PR #322 |
| Intake transaction baseline | BurnLens `0.3.0`; issue #325 / PR #326; merge `ee1a1d678ad888b595dc3c7b215f787ea5156582`; annotated `v0.3.0-intake-transaction-baseline`; `paired-intake-contract-v0.4.0`; full contract SHA-256 `5135b6b0b554e533df98ede568b1eafbd45c692b73a1e1abd3e50ba098f0958d`; provider assets/bytes and retained synthetic fixture bytes all zero |
| Credential use | `ACCESS-2026-006` authorizes both providers; `ACCESS-2026-007`, `ACCESS-2026-008`, and `ACCESS-2026-009` record successful runtime-only use with no credential, token, cookie, signed URL, or credential-store detail retained |
| Application version | Not created |
| AOI version | `aoi-darlene3-model-v0.2.0`, accepted and shipped final modeling AOI; 12 km by 9 km / 108 km2 in EPSG:32610; lower priority than official sources |
| Source records | `SOURCE-2026-001` through `SOURCE-2026-013`; the newest record freezes two exact public MTBS annual-reference clips; all native provider bytes remain local/ignored |
| Metadata fixture | `METADATA-2026-001`, five Sentinel items and 124 NASA VIIRS granule records; no asset hrefs or source bytes |
| Asset-readiness fixture | `ASSET-READINESS-2026-001`, SHA-256 `c5bcfbf57cf23a7bf3ed9bd1302461b2ba1ee101ab05b7d935419223763e5ce7`; metadata only, zero provider bytes |
| Evidence tooling | Shipped BurnLens `0.12.0` adds exact MTBS registration, cross-event five-state/binary rasters, transparent fallback diagnostics, and separately invoked all-source/all-pixel QA |
| Access-precheck report | `VIIRS-ACCESS-PRECHECK-2026-001`; JSON SHA-256 `107c08e00539257d7b86265d316060f35c019c821acc59f89dfc4b8875205f7f`; decision `BLOCKED_OWNER_CREDENTIAL` |
| AOI evidence report | `AOI-FINAL-2026-001`; JSON SHA-256 `305ddda2eda96fa31e8fb410891d3dc9c0f2b4930af5fc8ee6d2df9bae0b856c`; decision `ACCEPT_FINAL_MODELING_AOI` |
| Paired-intake rehearsal | `PAIR-INTAKE-REHEARSAL-2026-001`; run `BL-2026-07-14-paired-intake-rehearsal-r001`; JSON SHA-256 `94e311fd608f9c10e024138d9eff6abf0f70187a69c031264e91cb8d9d1af234`; historical pre-authorization decision `BLOCKED_OWNER_CREDENTIAL`; metadata observed 2026-07-14 with no live request; four synthetic transaction/integrity checks pass |
| Authenticated raw package | `darlene3-s2-viirs-pair-v0.1.0`; acquisition run `BL-2026-07-14-authenticated-intake-r001`; three exact provider assets / 1,169,997,942 bytes in ignored local storage; zero raw provider bytes committed |
| Source inspection report | `SOURCE-INSPECTION-2026-001`; run `BL-2026-07-14-source-inspection-r001`; JSON `cbd4dfba840680256a100aeca1a2e0b28483796f7e7b79b90de8b933d58b0a53`; HTML `76d13d3e105f053410d0063b17eb740f732c786dc395fe13335701496cbb41a0`; PNG `da93de6e432296f72c8f420d0181cfc81d99be7cf70ad96fe5b7bba619739966`; decision `ACCEPT_SOURCE_REFERENCE_DEFER_LABELS` |
| Observation geometry report | `OBSERVATION-GEOMETRY-2026-001`; run `BL-2026-07-14-observation-geometry-r002`; JSON `c1da1c47483ab573a8a123a26f7c5b2f111b57b4eaedb05ffb2d3aafa46e881d`; HTML `a63ee62c660c7b573d829847ac008786a6ecff91c61f5433365e640f64742ad2`; PNG `4dd21c3df693856fda47d23cd763054016a105d8c760181c4052411fa4ff6687`; decision `ACCEPT_COMPLEMENTARY_REFERENCE_GEOMETRY_DEFER_LABELS` |
| Target decision report | Corrected `TARGET-DECISION-2026-002`; run `BL-2026-07-14-target-decision-r002`; JSON `ac67f6c34a934d639c215ee98b181f1114b5624acafb85f65b1e2f3e804ce4d4`; HTML `0c1279e5e1047ff251dcd65f068d3d45bf2c6982e6a308972205e9d0a76879d4`; PNG `36f221aa6393ad07f14d4d7bb54b1f171ef0636ebb5640a11ab02ab9c5a9b5b0`; fallback active; all analytical versions null; `001` retained as the superseded pre-remediation run |
| Authenticated optical pair | `darlene3-s2-optical-pair-v0.1.0`; two exact Sentinel-2A SAFE products / 2,254,805,631 bytes in ignored local storage; provider MD5/BLAKE3 and local SHA-256 reverified; zero raw provider bytes committed |
| Optical-pair report | `OPTICAL-PAIR-2026-001`; run `BL-2026-07-15-optical-pair-evidence-r001`; exact artifact hashes recorded in `MANIFEST-2026-008`; decision `ACCEPT_OPTICAL_PAIR_FOR_PROTOCOL_DEFER_LABELS`; 98.9137% eligible pair quality; no label pixels |
| Content-registration report | `CONTENT-REGISTRATION-2026-001`; run `BL-2026-07-15-content-registration-r001`; exact artifact hashes recorded in `MANIFEST-2026-009`; decision `ACCEPT_LOCAL_CONTENT_REGISTRATION`; 12 of 12 windows pass; no label pixels |
| Label-proposal report | `LABEL-PROPOSAL-2026-001`; run `BL-2026-07-15-label-proposal-r001`; exact artifacts in `MANIFEST-2026-010`; 161,238 background, 18,543 burned, 71,897 unknown, 870 excluded, and 17,452 review-needed pixels |
| Label-QA report | `LABEL-QA-2026-001`; run `BL-2026-07-15-label-qa-r001`; 100% state/target agreement; zero all-pixel or 120-sample disagreement; independent human inter-rater validation absent |
| Cross-event report | `CROSS-EVENT-FITNESS-2026-001`; run `RUN-2026-07-15-CROSS-EVENT-FITNESS-001`; decision `SELECT_CROSS_EVENT_ACQUISITION_CANDIDATES`; two groups selected, one tile-seam exclusion; zero provider imagery bytes; no partition |
| Cross-event raw package | `burnlens-cross-event-optical-package-v0.1.0`; acquisition `BL-2026-07-16-cross-event-optical-intake-r005`; four exact archives / 4,551,170,756 ignored local bytes; zero raw bytes committed; all provider archives single-linked |
| Cross-event source-fitness report | `CROSS-EVENT-SOURCE-FITNESS-2026-001`; run `BL-2026-07-16-cross-event-source-fitness-r006`; decision `ACCEPT_CROSS_EVENT_SOURCE_FITNESS_WITH_EXCLUSIONS`; McKay passes and Tepee exclusions bind; protocol/schema trace is explicit; exact shipped hashes in `MANIFEST-2026-012` |
| Cross-event label-transfer report | `CROSS-EVENT-LABEL-TRANSFER-2026-001`; run `BL-2026-07-16-cross-event-label-transfer-r003`; 549 background, 9,211 burned, 18,425 unknown, 16,025 excluded, 19,720 review-needed; exact shipped hashes in `MANIFEST-2026-013` |
| Cross-event transfer QA | `CROSS-EVENT-LABEL-TRANSFER-QA-2026-001`; run `BL-2026-07-16-cross-event-label-transfer-qa-r003`; 63,930 state/target pixels, zero mismatch, 45 deterministic samples; human inter-rater validation absent |
| Dataset version | Not created |
| Label-schema implementation | `burn-scar-five-state-schema-v0.1.0` implemented as reviewable Darlene/Tepee/McKay proposal evidence; not accepted ground truth or a dataset |
| Baseline-method version | Not created |
| Model version | Not created |
| Run IDs | Latest shipped evidence runs are MTBS registration `BL-2026-07-16-mtbs-cross-event-reference-r003`, proposal `BL-2026-07-16-cross-event-label-transfer-r003`, and QA `BL-2026-07-16-cross-event-label-transfer-qa-r003`; no accepted dataset, split, baseline, model, or inference output |
| Raster/vector/map output | One official reference vector, one derived AOI vector, static evidence, and two derived native-grid proposal GeoTIFFs; no accepted dataset, model output, or BurnLens fire perimeter |
| Repository-owned public application | Not created |
| Public performance claim | None authorized or supported |

## Latest shipped checkpoint

P2O4-T02 / issue #357 / PR #358 accepts metadata-feasible Tepee/McKay acquisitions and frozen whole-event groups at analytical merge `5bfa1527410e98d8034b35ad68f6c50d5a1ec628`. A fresh no-hardlink clone reconstructs JSON, HTML, and PNG byte for byte and passes 110 tests, compilation, dependency health, merged-source wheel/isolated import, LF, manifest, links, raw exclusion, secret, original-resolution, browser, and remote-tag gates. Annotated tag object `dbfda10ca50c39d8e8924096e740e71643e1f133` peels to that merge as `v0.10.0-cross-event-feasibility-baseline`. Lifecycle synchronization is issue #359 / PR #360.

## Current checkpoint

P2O4-T04 / issue #367 / PR #368 is shipped at verified `v0.12.0-cross-event-label-transfer-baseline`. The next bounded checkpoint is independent label-fitness/adjudication evidence and a dataset-candidacy or deferral decision; no split creation is authorized yet.

## Boundaries carried forward

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

All BurnLens work and future public surfaces must originate from `drwbkr1/burnlens-deschutes`; the separate site repository is out of scope.

No application or deployed public companion site exists in this repository yet. The repository README, living case study, and static semantic/visual evidence reports, including the cross-event proposal/QA, are the presentation surfaces for this checkpoint.
