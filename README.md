# BurnLens Deschutes

BurnLens Deschutes is an experimental, portfolio-first computer vision and GEOINT project. It is designed to show technical and technical-adjacent reviewers how a bounded wildfire-screening workflow can move from versioned imagery through a segmentation model or justified baseline into transparent, reproducible geospatial evidence.

## Verified status

The project has an owner-approved Phase Two burn-scar target path and a shipped observation-geometry evidence baseline. It is not an analytical release.

- Phase One's documentation and repository-control evidence is complete enough for **Phase Two planning only**, as approved in P1O7-T08 / PR #294 on 2026-07-13.
- The controlling goal remains versioned at `v0.0.8-execution-goal-baseline`; Phase Two metadata, access, AOI, intake-transaction, source inspection, and observation-geometry evidence are shipped through P2O2-T04 / issue #333 / PR #334 at `v0.5.0-observation-geometry-baseline`.
- P2O2-T02 / issue #325 / PR #326 is shipped at `v0.3.0-intake-transaction-baseline`: an exact three-asset intake contract rejects partial or tampered packages and permits raw registration only through one all-or-none atomic promotion. Its proof uses temporary synthetic fixtures; it does not use or validate provider data.
- P2O2-T03 / issue #329 / PR #330 is shipped at `v0.4.0-authenticated-source-baseline`. The exact three-file, 1,169,997,942-byte package passed authenticated delivery, contract validation, atomic registration, independent re-verification, and real-array inspection.
- P2O2-T04 inventories and inspects all 23 bounded NOAA-21 active-fire candidates, registers one exact selected companion, and renders `OBSERVATION-GEOMETRY-2026-001`. The selected day observation improves qualified median view zenith from about 69 to 31 degrees with zero residual-bowtie exclusions, while still deferring labels and a dataset.
- P2O2-T05 / issue #337 / PR #338 merged at `68971e9709b886adf8575a58d32694aad42f038e` and records the owner's decision to activate the controlled burn-scar binary-mask fallback as `target-burn-scar-v0.2.0`. Post-merge verification caught checkout-dependent hashing before release; issue #339 corrects that reliability defect in `TARGET-DECISION-2026-002` while preserving run `001` as historical evidence. Neither run creates a label, dataset, baseline, or model.
- `v0.1.2-access-integrity-baseline` adds a runnable fail-closed delivery validator and a rendered precheck proving that the exact unauthenticated LP DAAC responses are login HTML rather than source assets.
- `aoi-darlene3-model-v0.2.0` is the accepted final modeling AOI: a reproducible 12 km by 9 km Deschutes County analysis boundary derived from one cited NIFC reference feature. Its normalized report and static evidence map are geometry evidence, not a wildfire result.
- The local pipeline exercised the authorized credentials without recording secrets, tokens, cookies, signed URLs, or credential-store details. The exact three-asset source package and 24-asset observation-screen package are retained only in ignored local raw storage; zero raw provider bytes are committed. The repository contains bounded derived source/reference and target-decision evidence, not labels or detections. No label schema implementation, dataset, split, baseline output, trained model, analytical metric, application demonstration, deployment, or public analytical result exists yet.
- The latest verified repository evidence baseline is `1c85496d9d488c0d2d5a58207d8b4786a683ba52` from issue #333 / PR #334; annotated tag object `cb9e675789d8ca4c4f8a5f4828331d41d023038e` remotely dereferences to that exact merge commit as `v0.5.0-observation-geometry-baseline`.
- `ACCESS-2026-006` records the owner's authorization without secret material; `ACCESS-2026-007` and `ACCESS-2026-008` record successful runtime-only use. Run `BL-2026-07-14-observation-geometry-r002` accepts one materially improved complementary reference and explicitly defers labels and a dataset because temporal and scale mismatch remain unresolved.
- Corrected run `BL-2026-07-14-target-decision-r002` activates the fallback target without creating label pixels; `r001` is preserved as pre-remediation evidence. The next gate is one legally usable, visually validated pre/post optical pair and an uncertainty-preserving burn-scar label protocol.

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
| 2 | One legally usable, versioned, leakage-resistant data/label/baseline foundation can support a defensible model-or-stop decision. | Active; the burn-scar fallback is approved, the active-fire path is retained as reference only, and current MTBS availability is documented. A real pre/post optical pair, label protocol, dataset, and baseline remain unproved. |
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

The executable surface now includes fail-closed access validation, deterministic AOI evidence, exact-pair transaction rehearsal, secret-safe authenticated acquisition, registered-package re-verification, real Sentinel/VIIRS source inspection, bounded NOAA-21 observation-geometry screening, and deterministic target-decision rendering. It is not a segmentation pipeline or operational application.

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
```

The committed rehearsal predates `ACCESS-2026-006` and intentionally exits with status `2`: its `BLOCKED_OWNER_CREDENTIAL` decision is a historical run state. The later acquisition and inspection runs supersede that access state without rewriting the historical output.

The committed [normalized precheck](samples/access/phase-two/VIIRS-ACCESS-PRECHECK-2026-001.json), [semantic report](samples/access/phase-two/VIIRS-ACCESS-PRECHECK-2026-001.html), and [visual evidence card](samples/access/phase-two/VIIRS-ACCESS-PRECHECK-2026-001.png) record the earlier unauthenticated delivery result. They do not contain provider pixels or rejected login-response bodies. The later [owner authorization](records/phase-two/access/ACCESS-2026-006.md) clears the approval stop without claiming that authentication or source delivery has been exercised.

The [final AOI record](records/phase-two/aoi/AOI-2026-002.md), [normalized AOI evidence](samples/aoi/phase-two/AOI-FINAL-2026-001.json), [semantic report](samples/aoi/phase-two/AOI-FINAL-2026-001.html), [visual evidence map](samples/aoi/phase-two/AOI-FINAL-2026-001.png), and [living case study](docs/case-study/BURNLENS_CASE_STUDY.md) explain the source/reference relationship and the remaining credential/data risks. They do not claim a detection, label, model, or operational product.

The [paired-intake decision](docs/phase-two/objective-two/PAIRED_INTAKE_TRANSACTION_DECISION.md), [normalized rehearsal](samples/intake/phase-two/PAIR-INTAKE-REHEARSAL-2026-001.json), [semantic report](samples/intake/phase-two/PAIR-INTAKE-REHEARSAL-2026-001.html), and [rendered evidence card](samples/intake/phase-two/PAIR-INTAKE-REHEARSAL-2026-001.png) show the exact contract, real zero-provider state, and synthetic-only transaction proof. The report pins its public-metadata observation time separately and states that a rehearsal run makes no live provider request. These artifacts do not establish provider delivery or source fitness.

The [authenticated-source decision](docs/phase-two/objective-two/AUTHENTICATED_SOURCE_INSPECTION_DECISION.md), [normalized inspection](samples/inspection/phase-two/SOURCE-INSPECTION-2026-001.json), [semantic report](samples/inspection/phase-two/SOURCE-INSPECTION-2026-001.html), and [rendered evidence](samples/inspection/phase-two/SOURCE-INSPECTION-2026-001.png) show real AOI pixels, provider records, QA exclusions, scan-edge risk, attribution, and traceability. They accept the package as source/reference evidence and prohibit direct label promotion.

The [observation-geometry decision](docs/phase-two/objective-two/OBSERVATION_GEOMETRY_DECISION.md), [normalized inventory and protocol](samples/observation/phase-two/OBSERVATION-GEOMETRY-2026-001.json), [semantic comparison](samples/observation/phase-two/OBSERVATION-GEOMETRY-2026-001.html), and [rendered evidence](samples/observation/phase-two/OBSERVATION-GEOMETRY-2026-001.png) show every candidate, exclusion reason, selected geometry, and weak/reference-label state. They do not contain labels, a dataset, or a model output.

The [burn-scar target decision](docs/phase-two/objective-two/BURN_SCAR_TARGET_DECISION.md), corrected [normalized target evidence](samples/target/phase-two/TARGET-DECISION-2026-002.json), [semantic decision page](samples/target/phase-two/TARGET-DECISION-2026-002.html), and [rendered decision card](samples/target/phase-two/TARGET-DECISION-2026-002.png) activate `target-burn-scar-v0.2.0`, explain the current MTBS no-record result, and define the next source/label gate. They create no label, dataset, baseline, model, detection, or operational output. `TARGET-DECISION-2026-001` remains committed as the immutable pre-remediation run that led to issue #339.
