# BurnLens Deschutes

BurnLens Deschutes is an experimental, portfolio-first computer vision and GEOINT project. It is designed to show technical and technical-adjacent reviewers how a bounded wildfire-screening workflow can move from versioned imagery through a segmentation model or justified baseline into transparent, reproducible geospatial evidence.

## Verified status

The project has shipped verified Phase Two burn-scar target-decision, real-pixel optical-pair, pair-local content-registration, five-state label-proposal, cross-event metadata-feasibility, exact cross-event source-fitness, cross-event label-transfer, proposal-blinded label-review-readiness, isolated offline reviewer-handoff, live-browser reviewer-handoff QA, first returned-response hash-lock, and mixed-version dual-lock custody-readiness baselines. BurnLens 0.18.0 is the current checkpoint candidate: it adds fail-closed atomic response preservation and proves the path with a non-human fixture while keeping the exact historical lock outputs reproducible. The owner has explicitly waived the planned second-human-response gate; issue #393 is superseded, not satisfied, and issue #403 controls a reduced-validation single-reviewer reveal/reconciliation path. The real first response and private receipts remain only in ignored storage. Review content remains withheld, the reveal remains operator-declared unopened, and software does not qualify a reviewer. No inter-rater validation, adjudication, accepted label set, dataset, split, baseline, model result, or deployed analytical application exists.

- Phase One's documentation and repository-control evidence is complete enough for **Phase Two planning only**, as approved in P1O7-T08 / PR #294 on 2026-07-13.
- The controlling goal remains versioned at `v0.0.8-execution-goal-baseline`; the latest verified tag is `v0.17.0-dual-lock-custody-readiness` at merge `eb84aad222a07b89f03a892c2cc0df9540b20d25`.
- BL-GOV-002 / issue #400 reconciles obsolete Phase One GitHub backlog against current repository truth. Historical issues, PR bodies, and control artifacts remain audit evidence; they do not represent active work or narrow the controlling execution goal. The owner-authorized [single-reviewer path decision](docs/phase-two/objective-four/SINGLE_REVIEWER_PATH_DECISION.md) supersedes issue #393 and makes issue #403 the active scientific checkpoint.
- P2O2-T02 / issue #325 / PR #326 is shipped at `v0.3.0-intake-transaction-baseline`: an exact three-asset intake contract rejects partial or tampered packages and permits raw registration only through one all-or-none atomic promotion. Its proof uses temporary synthetic fixtures; it does not use or validate provider data.
- P2O2-T03 / issue #329 / PR #330 is shipped at `v0.4.0-authenticated-source-baseline`. The exact three-file, 1,169,997,942-byte package passed authenticated delivery, contract validation, atomic registration, independent re-verification, and real-array inspection.
- P2O2-T04 inventories and inspects all 23 bounded NOAA-21 active-fire candidates, registers one exact selected companion, and renders `OBSERVATION-GEOMETRY-2026-001`. The selected day observation improves qualified median view zenith from about 69 to 31 degrees with zero residual-bowtie exclusions, while still deferring labels and a dataset.
- P2O2-T05 / issue #337 / PR #338 records the owner's activation of the controlled burn-scar binary-mask fallback as `target-burn-scar-v0.2.0`. Post-merge verification caught checkout-dependent hashing before release; issue #339 / PR #340 corrected it at merge `bcb71ebd01d3184f8de24318428309e61d33e54f` in `TARGET-DECISION-2026-002` while preserving run `001`. Annotated tag `v0.6.0-burn-scar-target-baseline` is verified; neither run creates a label, dataset, baseline, or model.
- P2O2-T06 / issue #343 / PR #344 is shipped at verified `v0.7.0-optical-pair-protocol-baseline`. It registers one exact same-orbit Sentinel-2A pre/post pair, opens the real native AOI pixels, and renders `OPTICAL-PAIR-2026-001`. Pairwise quality is 98.9137% eligible, 0.7641% review-needed, and 0.3222% excluded. At that checkpoint `burn-scar-label-protocol-v0.1.0` was a design only and created no label pixel; P2O4-T01 later implemented it as proposal evidence.
- P2O3-T01 / issue #347 / PR #348 analytically accepts `CONTENT-REGISTRATION-2026-001`: all twelve native-20m windows pass, with median residual 0.0224 pixel and maximum 0.0361 pixel / about 0.72 m. Post-merge checkout exposed a JSON/HTML line-ending reconstruction defect and correctly withheld release; issue #349 / PR #350 fixed the checkout contract without changing the artifacts or measurements. Verified `v0.8.0-content-registration-baseline` ships that prerequisite; it created no labels at that checkpoint.
- P2O4-T01 / issue #353 / PR #354 is shipped at verified `v0.9.0-label-proposal-baseline`. It implements `burn-scar-five-state-schema-v0.1.0` as `LABEL-PROPOSAL-2026-001`. The native-grid proposal retains 33.4144% of pixels as unknown, excluded, or review-needed; only burned and background-candidate enter the candidate target. `LABEL-QA-2026-001` separately recomputes all 270,000 state and target pixels with zero mismatch and audits 120 deterministic state/boundary samples. This is reviewable one-event evidence, not ground truth or a dataset.
- P2O4-T02 / issue #357 / PR #358 is shipped at verified `v0.10.0-cross-event-feasibility-baseline`. `CROSS-EVENT-FITNESS-2026-001` selects exact Tepee and McKay Sentinel pairs from current MTBS/Census/CDSE metadata, excludes Milli at a tile seam, quantifies 10.925/34.926/27.258 km representative-point separations, and freezes whole event/scene/geography/time groups before acquisition. No selected product was downloaded.
- P2O4-T03 ships through issue #361 / PR #362 and pre-tag trace-remediation issue #363 / PR #364 at merge `01c3aa4abeb89e3f15771571276a25d33e44d390`, verified tag `v0.11.0-cross-event-source-fitness-baseline`. Acquisition run `BL-2026-07-16-cross-event-optical-intake-r005` registers four exact archives / 4,551,170,756 ignored local bytes. Source-fitness run `BL-2026-07-16-cross-event-source-fitness-r006` accepts McKay at 100% pair-eligible quality and 3/3 registration windows, while Tepee retains 8.3441% review-needed, 5.1341% excluded, one excluded window, and one review-needed window. It explicitly traces label protocol `burn-scar-label-protocol-v0.1.0` and implemented schema `burn-scar-five-state-schema-v0.1.0`. No label or dataset is created.
- P2O4-T04 / issue #367 / PR #368 is shipped at verified `v0.12.0-cross-event-label-transfer-baseline`. Two exact public MTBS clips and the four registered Sentinel archives produce 549 background, 9,211 burned, 18,425 unknown, 16,025 excluded, and 19,720 review-needed pixels. Separate QA reopens all six source assets and reproduces all 63,930 state/target pixels with zero mismatch plus 45 agreeing samples. The event-relative background fallback remains explicit; no accepted dataset or independent human validation is claimed.
- P2O4-T04-REM / issue #371 / PR #372 is shipped at verified `v0.12.1-topology-stable-label-transfer`. Both real one-link and exact-two-link MTBS packages produce the same ten `2026-002` files byte for byte, while a third link fails closed. Corrected runs `r004`, `MANIFEST-2026-014`, and the original `2026-001` history make the provenance-only change explicit.
- P2O4-T05 / issue #375 / PR #376 is shipped at verified `v0.13.0-label-review-readiness`. `LABEL-REVIEW-PACKET-2026-001` rebuilds all three proposals from the exact six Sentinel archives and two MTBS clips, then selects 56 deterministic units across 14 present event/state strata. Eight first-pass pages conceal the proposal state/target until a separate reveal. `LABEL-REVIEW-PACKET-QA-2026-001` verifies the packet binding and 14 referenced packet outputs, while `MANIFEST-2026-015` inventories all 18 packet/QA files. Completed independent responses and adjudications remain zero; the label set and dataset are deferred.
- P2O4-T06 / issue #379 / PR #380 is shipped at verified `v0.14.0-offline-reviewer-handoff`. `LABEL-REVIEW-HANDOFF-2026-001` packages the exact blank response contract and eight blind pages into a deterministic 12-member offline archive with no reveal, proposal-bearing packet JSON, adjudication, QA, provider byte, secret, or network dependency. `LABEL-REVIEW-HANDOFF-QA-2026-001` independently verifies the archive and workbench; the response-lock path validates and hashes returned JSON before reveal. `MANIFEST-2026-016` inventories the seven committed handoff/QA outputs and reconstructible local archive. Human responses and adjudications remain zero.
- P2O4-T07 / issue #383 / PR #385 is shipped at verified `v0.15.0-live-browser-reviewer-handoff`. `LABEL-REVIEW-BROWSER-QA-2026-001` records the exact extracted workbench in Chrome `150.0.7871.124`: eight images and 56 fieldsets load; incomplete export fails; a seven-unit draft downloads, clears, and reloads exactly; full review/export passes; desktop and mobile have no horizontal overflow; and the inspected page target records no external resource request, console/runtime error, cookie, or local-storage entry. The generated response and lock are software fixtures that prohibit reveal and cannot count as human evidence. `MANIFEST-2026-017` inventories the five shipped browser artifacts.
- P2O4-T08 / issue #384 / PR #388 merged the `0.16.0` analytical evidence; issue #389 / PR #390 corrected only manifest chronology at `27fcd3eadb1473bb603b4275f986bf62022c10bf`. One exact 16,443-byte returned response and its 2,508-byte private receipt are preserved only in ignored storage. `LABEL-REVIEW-RESPONSE-LOCK-QA-2026-001` proves their exact hashes, the shipped packet binding, 56-of-56 contract completion, chronology, content withholding, and one-of-two response state without publishing response distributions, reviewer text, timestamps, notes, filenames, or paths. The reveal remains operator-declared unopened; software cannot verify that history or the reviewer. Verified tag object is `da94fc97efc07b07d9520022fdbff42a85e8ba00`.
- P2O4-T09A / issue #394 / PR #395 is shipped at verified `v0.17.0-dual-lock-custody-readiness`. It preserves the exact historical v0.2.0 / BurnLens 0.15.0 first receipt, makes new receipts identify v0.3.0 / BurnLens 0.17.0, and independently verifies both exact response/receipt pairs together. Authoritative run `BL-2026-07-16-label-review-dual-lock-readiness-qa-r001` uses one real returned-response origin plus one explicitly non-human, reveal-prohibited software fixture. `LABEL-REVIEW-DUAL-LOCK-READINESS-QA-2026-001` passes mixed-version binding, chronology, distinctness, privacy, semantic, rendered, fresh-main, and reproducible packaging gates. It does not count as a second human response or authorize reveal, comparison, adjudication, or dataset work.
- P2O4-T09B / issue #402 is the BurnLens `0.18.0` checkpoint candidate. It validates, exact-copies, fsyncs, revalidates, and no-overwrite promotes one response plus a v0.4.0 receipt inside ignored storage, with rollback on partial failure and rejection of duplicate evidence, linked custody paths, unignored destinations, overwrite, and source drift. `LABEL-REVIEW-RESPONSE-ATOMIC-INTAKE-QA-2026-001` uses only the existing software fixture, adds zero human responses, and performs zero reveal actions. The v0.4.0 rule now requires a separate public owner-waiver/reveal-readiness checkpoint; issue #403 owns that work.
- `v0.1.2-access-integrity-baseline` adds a runnable fail-closed delivery validator and a rendered precheck proving that the exact unauthenticated LP DAAC responses are login HTML rather than source assets.
- `aoi-darlene3-model-v0.2.0` is the accepted final modeling AOI: a reproducible 12 km by 9 km Deschutes County analysis boundary derived from one cited NIFC reference feature. Its normalized report and static evidence map are geometry evidence, not a wildfire result.
- The local pipeline exercised the authorized credentials without recording secrets, tokens, cookies, signed URLs, or credential-store details. Existing source/observation/optical packages, the four-archive 4,551,170,756-byte cross-event package, and two 84,238-byte public MTBS clips are retained only in ignored local raw storage; zero raw provider bytes are committed. The repository contains bounded multi-event proposal, review-readiness, handoff, and QA evidence plus a shipped local/offline response workbench, but no accepted dataset, split, baseline output, trained model, analytical metric, deployment, or public analytical result.
- The latest verified tag is `v0.17.0-dual-lock-custody-readiness`: annotated tag object `8fca2a51548690b710ad3903a19312e77c748420` remotely peels to merge `eb84aad222a07b89f03a892c2cc0df9540b20d25`. A fresh remote-main clone passes 163 tests, compilation, Node syntax, dependency health, exact historical first-lock and new dual-lock reconstruction, JSON/privacy/link gates, and the canonical 302,018-byte wheel / SHA-256 `cac65ceaf6ce75ef67d16d55379df9234a591563c94800791d972965281f80d2`; isolated install reports `0.17.0` and 27 entry points.
- `ACCESS-2026-006` records the owner's authorization without secret material; `ACCESS-2026-007`, `ACCESS-2026-008`, and `ACCESS-2026-009` record successful runtime-only use. Run `BL-2026-07-14-observation-geometry-r002` accepts one materially improved complementary reference and explicitly defers labels and a dataset because temporal and scale mismatch remain unresolved.
- Corrected run `BL-2026-07-14-target-decision-r002` activates the fallback target without creating label pixels; `r001` is preserved as pre-remediation evidence. Cross-event acquisition/source-fitness prove the exact local pixels; topology-stable proposal run `BL-2026-07-16-cross-event-label-transfer-r004` and QA run `BL-2026-07-16-cross-event-label-transfer-qa-r004` preserve the `r003` analytical result while making public evidence reproducible across approved storage topologies. Shipped review runs `BL-2026-07-16-label-review-packet-r001` and `BL-2026-07-16-label-review-packet-qa-r001` make independent review executable without claiming that it has happened.

Current truth lives in [the phase-status record](docs/status/PHASE_STATUS.md). The approved execution authority lives in [the BurnLens execution goal](docs/governance/BURNLENS_EXECUTION_GOAL.md).

## Project promise

BurnLens will demonstrate one defensible, traceable CV-to-GEOINT workflow for a bounded Deschutes County study area:

```text
versioned imagery
→ deterministic preprocessing
→ segmentation or justified baseline mask
→ georeferenced raster
→ vector polygons
→ transparent geospatial overlays
→ descriptive exposure-style summary
→ immutable run package
→ repository-owned application and portfolio case study
```

The primary audience is technical and technical-adjacent portfolio reviewers. The reference user evaluates whether the work demonstrates credible computer vision, remote-sensing, geospatial engineering, reproducibility, reliability, and responsible judgment.

## Locked computer-vision task

- **Task:** experimental binary semantic segmentation for wildfire-relevant screening.
- **Planned primary target:** active-fire / hotspot-informed binary fire mask; P2O2-T04 rejected direct label promotion and retains this source as complementary native-scale reference only.
- **Active target:** burn-scar binary mask, activated by the owner on 2026-07-14 through P2O2-T05 after Phase Two evidence showed the planned primary could not define defensible 10-20 m labels.
- **Reference model family:** U-Net-style segmentation, evaluated only after a strong non-model baseline.
- **Output posture:** mask-first, georeferenced, uncertainty-aware, and explicit about unknown/excluded areas.

Hotspot detections may support reference, sampling, weak-label, or comparison logic. They are not exact fire perimeters or pixel-perfect ground truth.

## Six outcomes to prove

The [six-phase roadmap](docs/roadmap/BURNLENS_BUILD_ROADMAP.md) is a revisable planning hypothesis. Its task order may change; these outcomes may not change without owner approval.

| Phase | Outcome BurnLens must prove | Current status |
|---|---|---|
| 1 | The promise, task, source posture, controls, traceability, and acceptance evidence are coherent enough to govern implementation. | Planning baseline accepted and versioned for Phase Two planning; no analytical release. |
| 2 | One legally usable, versioned, leakage-resistant data/label/baseline foundation can support a defensible model-or-stop decision. | Active; exact three-event proposal evidence, separate software QA, a proposal-blinded review instrument, a verified isolated offline handoff/response lock, one shipped content-withheld returned-response lock, and shipped mixed-version dual-lock readiness exist. The readiness fixture is not human evidence. The owner waived reviewer two, so inter-rater validation and adjudication will remain absent; issue #403 must prove a conservative single-reviewer reconciliation before accepted labels, dataset, split, baselines, or model-readiness can be considered. |
| 3 | One bounded model either adds reproducible value beyond the strongest baseline or is rejected honestly. | Blocked by Phase Two evidence. |
| 4 | The accepted model or baseline can become a valid, reproducible, georeferenced run and evidence interface. | Blocked by Phase Three/baseline decision. |
| 5 | The integrated system is reproducible, accessible, secure, failure-visible, performant, and reversible. | Blocked by Phase Four. |
| 6 | One coherent, licensed, citable, traceable portfolio release can be published and maintained or closed honestly. | Blocked by Phase Five and publication gates. |

## Repository boundary

This repository owns the full BurnLens product: analytical code, data contracts, model and run artifacts, application, public website, case study, documentation, and release records.

BurnLens execution must not read, change, publish, depend on, or use the separate `burnlens-site` repository. Any future public surface will be built and deployed from `drwbkr1/burnlens-deschutes`.

## Safety and source precedence

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

BurnLens is not field-validated, agency-endorsed, operational, emergency-ready, or suitable for property-level, insurance, legal, regulatory, evacuation, routing, tactical, suppression, or incident-command decisions.

Official county, state, federal, fire-service, emergency-management, transportation, air-quality, and incident sources govern whenever they differ from BurnLens-derived output.

## Traceability requirement

Every future public output and claim must trace to its Git commit, application version, AOI version, source records, dataset version, label-schema version, baseline or model version, immutable run ID, processing timestamp, checksums, warning flags, limitations, and source-precedence note. Traceability is required but does not replace licensing, claims review, release QA, or rendered-output verification.

## Active controls

- [Execution goal](docs/governance/BURNLENS_EXECUTION_GOAL.md)
- [Six-phase roadmap](docs/roadmap/BURNLENS_BUILD_ROADMAP.md)
- [Phase status](docs/status/PHASE_STATUS.md)
- [Version history](docs/status/VERSION_HISTORY.md)
- [Versioning protocol](VERSIONING.md)
- [Changelog](CHANGELOG.md)
- [Agent instructions](AGENTS.md)
- [Prompt-to-repository SOP](docs/workflows/PROMPT_TO_REPO_SOP.md)

Historical Objective Seven trackers, handoffs, audits, and release notes remain the evidence trail for the Phase One planning-only decision. Their obsolete sequencing and permission limits do not override the execution goal.

## Run the current evidence tools

The executable surface now includes fail-closed access validation, deterministic AOI evidence, exact-pair transaction rehearsal, secret-safe authenticated acquisition, registered-package re-verification, real Sentinel/VIIRS source inspection, bounded NOAA-21 observation-geometry screening, deterministic target-decision rendering, exact optical-pair inspection, pair-local content registration, five-state proposal and cross-event transfer paths, separate all-pixel QA, a proposal-blinded label-review packet, and packet/response integrity QA. It is not an accepted dataset, segmentation model, or operational application.

```powershell
python -m pip install .
python -m unittest discover -s tests -v
python -m burnlens.viirs_access_precheck --help
python -m burnlens.render_access_report `
  --input-json samples/access/phase-two/VIIRS-ACCESS-PRECHECK-2026-001.json `
  --output-html samples/access/phase-two/VIIRS-ACCESS-PRECHECK-2026-001.html `
  --output-png samples/access/phase-two/VIIRS-ACCESS-PRECHECK-2026-001.png
python -m burnlens.finalize_aoi `
  --source samples/reference/phase-two/NIFC-DARLENE3-PERIMETER-2026-001.geojson `
  --output-dir samples/aoi/phase-two `
  --generated-at-utc 2026-07-14T01:30:00Z `
  --run-id BL-2026-07-14-aoi-final-r001 `
  --source-commit bcc1d9aa494c5511ff824692199b40717d320dd4
python -m burnlens.rehearse_paired_intake `
  --generated-at-utc 2026-07-14T02:32:52Z `
  --run-id BL-2026-07-14-paired-intake-rehearsal-r001 `
  --source-commit ac8ee43151991c38ccf5d446a53c09b617afeb54 `
  --output-dir samples/intake/phase-two
python -m burnlens.inspect_source_package `
  --package downloads/phase-two/raw/darlene3-s2-viirs-pair-v0.1.0 `
  --aoi-report samples/aoi/phase-two/AOI-FINAL-2026-001.json `
  --reference-geojson samples/reference/phase-two/NIFC-DARLENE3-PERIMETER-2026-001.geojson `
  --output-directory samples/inspection/phase-two `
  --generated-at-utc 2026-07-14T18:22:11Z `
  --run-id BL-2026-07-14-source-inspection-r001 `
  --git-source-commit 9a7e614fbfbbcd4c5a6795417121cafb82ae5dcc
python -m burnlens.screen_observation_geometry `
  --quarantine downloads/phase-two/quarantine `
  --raw-parent downloads/phase-two/raw `
  --aoi-report samples/aoi/phase-two/AOI-FINAL-2026-001.json `
  --reference-geojson samples/reference/phase-two/NIFC-DARLENE3-PERIMETER-2026-001.geojson `
  --baseline-report samples/inspection/phase-two/SOURCE-INSPECTION-2026-001.json `
  --output-directory samples/observation/phase-two `
  --generated-at-utc 2026-07-14T20:09:07Z `
  --run-id BL-2026-07-14-observation-geometry-r002 `
  --git-source-commit 89d50c24a696cc7e3ec023eec00b021a4a0cdda6
python -m burnlens.record_target_decision `
  --observation-report samples/observation/phase-two/OBSERVATION-GEOMETRY-2026-001.json `
  --aoi-report samples/aoi/phase-two/AOI-FINAL-2026-001.json `
  --mtbs-record samples/target/phase-two/MTBS-DARLENE3-AVAILABILITY-2026-001.json `
  --output-directory samples/target/phase-two `
  --generated-at-utc 2026-07-14T22:18:21Z `
  --run-id BL-2026-07-14-target-decision-r002 `
  --git-source-commit cfbf357634cdcf9e68c3af78bfcb3e195bebc17a
python -m burnlens.inspect_optical_pair `
  --package downloads/phase-two/raw/darlene3-s2-optical-pair-v0.1.0 `
  --aoi-report samples/aoi/phase-two/AOI-FINAL-2026-001.json `
  --reference-geojson samples/reference/phase-two/NIFC-DARLENE3-PERIMETER-2026-001.geojson `
  --output-directory samples/optical/phase-two `
  --generated-at-utc 2026-07-15T18:43:26Z `
  --run-id BL-2026-07-15-optical-pair-evidence-r001 `
  --git-source-commit 4b699025f703450f892bc2533c86560f47711aa2 `
  --visual-review-decision ACCEPT_OPTICAL_PAIR_FOR_PROTOCOL_DEFER_LABELS `
  --visual-review-notes "Original-resolution registered-pair PNG and numeric report reviewed: same-grid pre/post scenes are readable; continuous dNBR is spatially coherent around the later NIFC context while non-fire change and review/excluded pixels remain visible. Accept for protocol evidence only; labels deferred."
python -m burnlens.measure_content_registration --help
python -m burnlens.propose_burn_scar_labels --help
python -m burnlens.verify_label_proposal --help
python -m burnlens.capture_cross_event_source --help
python -m burnlens.assess_cross_event_feasibility --help
python -m burnlens.acquire_cross_event_optical --help
python -m burnlens.inspect_cross_event_sources --help
python -m burnlens.build_label_review_packet --help
python -m burnlens.run_label_review_packet_qa --help
python -m burnlens.build_label_review_handoff --help
python -m burnlens.verify_label_review_handoff --help
python -m burnlens.lock_label_review_response --help
python -m burnlens.run_label_review_dual_lock_qa --help
```

The committed rehearsal predates `ACCESS-2026-006` and intentionally exits with status `2`: its `BLOCKED_OWNER_CREDENTIAL` decision is a historical run state. The later acquisition and inspection runs supersede that access state without rewriting the historical output.

The committed [normalized precheck](samples/access/phase-two/VIIRS-ACCESS-PRECHECK-2026-001.json), [semantic report](samples/access/phase-two/VIIRS-ACCESS-PRECHECK-2026-001.html), and [visual evidence card](samples/access/phase-two/VIIRS-ACCESS-PRECHECK-2026-001.png) record the earlier unauthenticated delivery result. They do not contain provider pixels or rejected login-response bodies. The later [owner authorization](records/phase-two/access/ACCESS-2026-006.md) clears the approval stop without claiming that authentication or source delivery has been exercised.

The [final AOI record](records/phase-two/aoi/AOI-2026-002.md), [normalized AOI evidence](samples/aoi/phase-two/AOI-FINAL-2026-001.json), [semantic report](samples/aoi/phase-two/AOI-FINAL-2026-001.html), [visual evidence map](samples/aoi/phase-two/AOI-FINAL-2026-001.png), and [living case study](docs/case-study/BURNLENS_CASE_STUDY.md) explain the source/reference relationship and the remaining credential/data risks. They do not claim a detection, label, model, or operational product.

The [paired-intake decision](docs/phase-two/objective-two/PAIRED_INTAKE_TRANSACTION_DECISION.md), [normalized rehearsal](samples/intake/phase-two/PAIR-INTAKE-REHEARSAL-2026-001.json), [semantic report](samples/intake/phase-two/PAIR-INTAKE-REHEARSAL-2026-001.html), and [rendered evidence card](samples/intake/phase-two/PAIR-INTAKE-REHEARSAL-2026-001.png) show the exact contract, real zero-provider state, and synthetic-only transaction proof. The report pins its public-metadata observation time separately and states that a rehearsal run makes no live provider request. These artifacts do not establish provider delivery or source fitness.

The [authenticated-source decision](docs/phase-two/objective-two/AUTHENTICATED_SOURCE_INSPECTION_DECISION.md), [normalized inspection](samples/inspection/phase-two/SOURCE-INSPECTION-2026-001.json), [semantic report](samples/inspection/phase-two/SOURCE-INSPECTION-2026-001.html), and [rendered evidence](samples/inspection/phase-two/SOURCE-INSPECTION-2026-001.png) show real AOI pixels, provider records, QA exclusions, scan-edge risk, attribution, and traceability. They accept the package as source/reference evidence and prohibit direct label promotion.

The [observation-geometry decision](docs/phase-two/objective-two/OBSERVATION_GEOMETRY_DECISION.md), [normalized inventory and protocol](samples/observation/phase-two/OBSERVATION-GEOMETRY-2026-001.json), [semantic comparison](samples/observation/phase-two/OBSERVATION-GEOMETRY-2026-001.html), and [rendered evidence](samples/observation/phase-two/OBSERVATION-GEOMETRY-2026-001.png) show every candidate, exclusion reason, selected geometry, and weak/reference-label state. They do not contain labels, a dataset, or a model output.

The [burn-scar target decision](docs/phase-two/objective-two/BURN_SCAR_TARGET_DECISION.md), corrected [normalized target evidence](samples/target/phase-two/TARGET-DECISION-2026-002.json), [semantic decision page](samples/target/phase-two/TARGET-DECISION-2026-002.html), and [rendered decision card](samples/target/phase-two/TARGET-DECISION-2026-002.png) activate `target-burn-scar-v0.2.0`, explain the current MTBS no-record result, and define the next source/label gate. They create no label, dataset, baseline, model, detection, or operational output. `TARGET-DECISION-2026-001` remains committed as the immutable pre-remediation run that led to issue #339.

The [optical-pair and label-protocol decision](docs/phase-two/objective-two/OPTICAL_PAIR_LABEL_PROTOCOL_DECISION.md), [normalized real-pixel evidence](samples/optical/phase-two/OPTICAL-PAIR-2026-001.json), [semantic evidence page](samples/optical/phase-two/OPTICAL-PAIR-2026-001.html), and [rendered pair card](samples/optical/phase-two/OPTICAL-PAIR-2026-001.png) accept one exact same-orbit pair for protocol work. Continuous dNBR, SCL, VIIRS, and the later NIFC outline remain evidence rather than truth; this protocol is the design predecessor to the separate five-state proposal below.

The [five-state label-proposal decision](docs/phase-two/objective-four/LABEL_PROPOSAL_DECISION.md), [proposal report](samples/labels/phase-two/LABEL-PROPOSAL-2026-001.html), [proposal render](samples/labels/phase-two/LABEL-PROPOSAL-2026-001.png), [separate QA report](samples/labels/phase-two/LABEL-QA-2026-001.html), and [QA render](samples/labels/phase-two/LABEL-QA-2026-001.png) make one exact proposal and its all-pixel software agreement inspectable. They explicitly defer an accepted dataset, split, baseline, model, human inter-rater claim, and field-validation claim.

The [cross-event feasibility decision](docs/phase-two/objective-four/CROSS_EVENT_FEASIBILITY_DECISION.md), [normalized current source capture](samples/cross-event/phase-two/CROSS-EVENT-SOURCE-2026-001.json), [semantic feasibility report](samples/cross-event/phase-two/CROSS-EVENT-FITNESS-2026-001.html), and [rendered event-separation evidence](samples/cross-event/phase-two/CROSS-EVENT-FITNESS-2026-001.png) select exact Tepee and McKay acquisition candidates and freeze leakage-control groups. They do not establish local pixel fitness or create a dataset partition.

The [cross-event source-fitness decision](docs/phase-two/objective-four/CROSS_EVENT_SOURCE_FITNESS_DECISION.md), [normalized source-fitness report](samples/cross-event/phase-two/CROSS-EVENT-SOURCE-FITNESS-2026-001.json), [semantic evidence page](samples/cross-event/phase-two/CROSS-EVENT-SOURCE-FITNESS-2026-001.html), and [rendered native-pixel evidence](samples/cross-event/phase-two/CROSS-EVENT-SOURCE-FITNESS-2026-001.png) prove exact authenticated delivery and local pixel fitness. McKay passes; Tepee remains accepted only with visible quality/window exclusions. No label, dataset, split, baseline, model, or application is created.

The [cross-event label-transfer decision](docs/phase-two/objective-four/CROSS_EVENT_LABEL_TRANSFER_DECISION.md), topology-stable [semantic proposal report](samples/labels/cross-event/phase-two/CROSS-EVENT-LABEL-TRANSFER-2026-002.html), [proposal render](samples/labels/cross-event/phase-two/CROSS-EVENT-LABEL-TRANSFER-2026-002.png), [separate QA report](samples/labels/cross-event/phase-two/CROSS-EVENT-LABEL-TRANSFER-QA-2026-002.html), and [QA render](samples/labels/cross-event/phase-two/CROSS-EVENT-LABEL-TRANSFER-QA-2026-002.png) compare both events, preserve five-state uncertainty, expose the event-relative fallback, and reproduce every output pixel. The `2026-001` package remains immutable history. These are proposal evidence, not accepted ground truth or a dataset.

The [label-review readiness decision](docs/phase-two/objective-four/LABEL_REVIEW_READINESS_DECISION.md), [packet summary](samples/labels/review/phase-two/LABEL-REVIEW-PACKET-2026-001.html), [proposal-blinded first pass](samples/labels/review/phase-two/LABEL-REVIEW-PACKET-2026-001-BLIND.html), separate [proposal reveal](samples/labels/review/phase-two/LABEL-REVIEW-PACKET-2026-001-REVEAL.html), and [integrity QA](samples/labels/review/phase-two/LABEL-REVIEW-PACKET-QA-2026-001.html) make bounded independent review executable. The packet covers 56 units across 14 present event/state strata and explicitly records the absent McKay/excluded stratum. Completed independent responses and adjudications remain zero, so the evidence accepts only review readiness and defers labels, a dataset, and partition work.

The [isolated handoff decision](docs/phase-two/objective-four/LABEL_REVIEW_HANDOFF_DECISION.md), [offline workbench](samples/labels/review/phase-two/LABEL-REVIEW-HANDOFF-2026-001.html), [handoff evidence card](samples/labels/review/phase-two/LABEL-REVIEW-HANDOFF-2026-001.png), and [independent handoff QA](samples/labels/review/phase-two/LABEL-REVIEW-HANDOFF-QA-2026-001.html) remove proposal-bearing material from the reviewer bundle and provide an exact response export/lock path. They prove software isolation and integrity, not that a human completed the review. The workbench is repository-owned and local/offline; no deployed BurnLens application exists.

The [live-browser QA decision](docs/phase-two/objective-four/LABEL_REVIEW_BROWSER_QA_DECISION.md), [semantic browser report](samples/labels/review/phase-two/LABEL-REVIEW-BROWSER-QA-2026-001.html), [browser evidence card](samples/labels/review/phase-two/LABEL-REVIEW-BROWSER-QA-2026-001.png), [desktop capture](samples/labels/review/phase-two/LABEL-REVIEW-BROWSER-QA-2026-001-DESKTOP.png), and [mobile capture](samples/labels/review/phase-two/LABEL-REVIEW-BROWSER-QA-2026-001-MOBILE.png) prove the exact local workbench's interaction contract in the recorded Chrome runtime. The balanced completed response is a software fixture only; it cannot count as independent review or authorize reveal.

The [first returned-response decision](docs/phase-two/objective-four/LABEL_REVIEW_RESPONSE_LOCK_DECISION.md), [semantic public receipt](samples/labels/review/phase-two/LABEL-REVIEW-RESPONSE-LOCK-QA-2026-001.html), and [public evidence card](samples/labels/review/phase-two/LABEL-REVIEW-RESPONSE-LOCK-QA-2026-001.png) prove one exact private response and receipt passed the bounded software contract without publishing what the reviewer said. They do not verify reviewer fitness, reveal history, agreement, adjudication, or label truth.

The active [dual-lock custody-readiness decision](docs/phase-two/objective-four/LABEL_REVIEW_DUAL_LOCK_READINESS_DECISION.md), [semantic readiness report](samples/labels/review/phase-two/LABEL-REVIEW-DUAL-LOCK-READINESS-QA-2026-001.html), and [rendered readiness card](samples/labels/review/phase-two/LABEL-REVIEW-DUAL-LOCK-READINESS-QA-2026-001.png) prove the exact legacy first lock can coexist with the current receipt protocol and independent two-pair verifier. The second pair is a software fixture, not a reviewer response; the human two-response gate remains unmet.

The current [atomic response-intake decision](docs/phase-two/objective-four/LABEL_REVIEW_RESPONSE_ATOMIC_INTAKE_DECISION.md), [semantic QA report](samples/labels/review/phase-two/LABEL-REVIEW-RESPONSE-ATOMIC-INTAKE-QA-2026-001.html), and [rendered QA card](samples/labels/review/phase-two/LABEL-REVIEW-RESPONSE-ATOMIC-INTAKE-QA-2026-001.png) prove the future intake command can preserve exact bytes without overwrite and publish only bounded fixture evidence. They do not establish a second human response, reveal history, label agreement, or dataset fitness.
