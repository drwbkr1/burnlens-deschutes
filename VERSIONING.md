# BurnLens Deschutes — Versioning Protocol

## Purpose

This file defines the controlling versioning protocol for BurnLens Deschutes.

The detailed taxonomy and increment rules live in:

```text
docs/phase-one/objective-five/VERSION_TAXONOMY.md
```

This protocol is expanded during Phase One / Objective Five because BurnLens is moving from a lightweight versioning placeholder to a Phase Two-ready traceability rule set.

## Boundary statement

BurnLens Deschutes is an experimental computer vision + GEOINT portfolio project.

Version numbers, tags, release names, dataset versions, model versions, run IDs, and report versions do **not** imply operational readiness, official wildfire information, field validation, emergency readiness, agency endorsement, production stability, evacuation support, routing support, tactical support, or incident-command support.

Official sources govern when BurnLens differs from county, state, federal, fire-service, emergency-management, transportation, air-quality, or incident sources.

Required warning for future BurnLens CV outputs:

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

## Research basis

| Source | Rule adopted |
|---|---|
| Semantic Versioning 2.0.0, `https://semver.org/spec/v2.0.0.html` | Use `MAJOR.MINOR.PATCH` for software/release-style identifiers. Use `0.y.z` while BurnLens is in initial development and not stable or production-facing. Do not modify a released version in place. |
| GitHub Docs, About releases, `https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases` | Treat GitHub releases and tags as repository-history anchors that require clear release notes, included/excluded artifacts, and boundary checks. |
| BurnLens Prompt-to-Repo SOP | Update `VERSIONING.md` only when the protocol itself changes. P1O5-T03 changes the protocol, so this update is allowed. |

## Core traceability rule

No public map, screenshot, summary, report, model output, application view, run artifact, case-study card, or portfolio claim is portfolio-ready unless it can trace back to the applicable items below:

- GitHub commit;
- objective baseline or application version;
- AOI version;
- source record ID(s);
- dataset version, when data exists;
- label schema version, when labels exist;
- baseline method version or model version, when a method exists;
- run ID, when an output is generated;
- report version, when a report is generated;
- source metadata and processing timestamp;
- warning flags and limitations;
- source-precedence note.

Traceability is necessary but not sufficient for public release. Release control, claim review, and boundary checks still govern whether an artifact may be published.

## Version and identifier classes

| Component | Example | Type | Rule summary |
|---|---|---|---|
| Objective baseline | `v0.0.5-objective-five-traceability` | Repository baseline tag / release label | Use a SemVer-core tag plus descriptive suffix for reviewed objective-level repository states. |
| Application version | `burnlens-app-v0.1.0` | Software/application version | Use SemVer. Stay in `0.y.z` until later release-control criteria define stability. |
| AOI version | `deschutes-aoi01-v0.1` | Geospatial scope identifier | Use a SemVer-inspired AOI version tied to geometry/source/rationale records. |
| Source record ID | `SRC-2026-001` | Immutable record ID | Use sequential IDs, not SemVer. Revisions occur inside the record or through superseding records. |
| Dataset version | `deschutes-aoi01-dataset-v0.1.0` | Data package version | Use SemVer-inspired data package versions tied to AOI/source/access/CRS/provenance records. |
| Label schema version | `fire-mask-labels-v0.1` | Annotation/class contract version | Use SemVer-inspired label schema versions for class definitions and annotation rules. |
| Review protocol version | `proposal-blinded-label-review-readiness-v0.1.0` | Review workflow contract version | Use SemVer-inspired versions for sampling, blind/reveal ordering, response/adjudication schemas, reviewer qualification, and evidence-sufficiency rules. |
| Baseline method version | `burnlens-baseline-v0.1.0` | Method artifact version | Use SemVer-inspired artifact versions for non-ML baseline methods. |
| Model version | `burnlens-cv-unet-v0.1.0` | Model artifact version | Use SemVer-inspired artifact versions for trained model packages and lineage. |
| Run ID | `BL-YYYY-MM-DD-deschutes-aoiXX-mXXX-dXXX` | Unique run identifier | Use unique immutable run IDs, not SemVer. Never reuse a run ID. |
| Report version | `run-report-v0.1.0` | Report template/package version | Use SemVer-inspired report versions tied to report structure, logic, warnings, and claim gates. |

## Increment rule summary

| Component | Increment or creation rule |
|---|---|
| Objective baseline | Increment the `v0.0.N` baseline for each reviewed objective-level baseline. |
| Application version | Increment MINOR for material new user-visible capability; PATCH for compatible fixes/copy/metadata corrections. |
| AOI version | New AOI number for a different geography; increment MINOR for geometry/scope changes; PATCH or record revision for metadata-only fixes. |
| Source record ID | Assign a new sequential `SRC-YYYY-NNN`; do not treat as a version. Use internal revision or superseding records for changes. |
| Dataset version | Increment MINOR for data/source/time-window/tile/label changes affecting downstream use; PATCH for metadata/checksum/manifest corrections that do not change the package. |
| Label schema version | Increment MINOR for class/rule/format changes affecting labels; PATCH or revision for clarifications. |
| Review protocol version | Increment MINOR for sampling, presentation ordering, response/adjudication behavior, reviewer qualification, or acceptance-rule changes; PATCH for compatible clarifications or metadata-only corrections. |
| Baseline method version | Increment MINOR for method/output behavior changes; PATCH for corrections that do not change output behavior. |
| Model version | Increment MINOR for architecture/data/schema/training/output-contract changes; PATCH for packaging or metadata fixes that do not materially reinterpret the model. |
| Run ID | Create a new run ID for every execution, rerun, failed run worth preserving, or public-output run. Never increment or reuse. |
| Report version | Increment MINOR for new sections, evidence requirements, warning logic, summary logic, or claim gates; PATCH for formatting/typo/metadata corrections. |

## Current development posture

BurnLens uses `0.y.z` versions because the project is experimental, portfolio-first, and not stable or production-facing.

While BurnLens remains in `0.y.z`:

- compatibility expectations are provisional;
- public API or output contracts are not stable unless a specific artifact says otherwise;
- breaking changes must be documented;
- a versioned artifact may still be experimental;
- a release or tag may mark repository state without authorizing data/model/map/public-output work.

## Source-precedence rule

Versioned BurnLens artifacts remain below official/reference sources in the source-precedence hierarchy.

If a BurnLens versioned artifact conflicts with an official source, the report, map, screenshot, or public claim must state that official sources govern. Version numbers must never be used to imply BurnLens is more authoritative than official records.

## Public claim rule

Safe versioning claim:

```text
BurnLens has a versioning protocol that separates software versions, geospatial identifiers, data/model artifact versions, run IDs, and report versions so future outputs can trace back to commits, source records, methods, and limitations.
```

Unsupported versioning claims:

```text
A BurnLens version number means the artifact is operational, official, field-validated, emergency-ready, agency-endorsed, production-stable, or suitable for evacuation, routing, tactical, or incident-command support.
```

## Current protocol status

| Field | Value |
|---|---|
| Controlling execution authority | `docs/governance/BURNLENS_EXECUTION_GOAL.md` |
| Current taxonomy artifact | `docs/phase-one/objective-five/VERSION_TAXONOMY.md` |
| Current phase posture | Phase Two active; verified topology-stable three-event proposal/QA, proposal-blinded review readiness, isolated offline reviewer handoff, and live-browser handoff QA are shipped; first returned-response public-lock candidate exists; dataset deferred |
| Current repository baseline | Latest shipped: `v0.15.0-live-browser-reviewer-handoff` at `861716be16be3a0469d2268baed971be65684d48` via issue #383 / PR #385 |
| Active analytical candidate | P2O4-T08 / issue #384 / PR #388 merged at `836eef75495dbc671bd74a8ad4112852bbf50ac6`; issue #389 corrects manifest chronology and completes release gates before tag. A second response remains the next scientific gate. |
| Baseline verification | Annotated tag object `69b32b076a7fca40ba5eceacb64aeac2a512e7b9` remotely dereferences to PR #385 merge `861716be16be3a0469d2268baed971be65684d48`; fresh remote-main tests, exact handoff reconstruction, fresh browser run, canonical source wheel, manifest/link/LF, and remote-tag gates pass |
| Data/model/run/map/application status | Exact provider packages, exact returned-review bytes, and the private receipt remain in ignored local storage. Public run `BL-2026-07-16-label-review-response-lock-qa-r001` exposes only content-withheld cryptographic and completeness evidence. Shipped local application version `label-review-handoff-workbench-v0.1.0` is not deployed. No independently accepted labels, adjudication, dataset, split, baseline, model, analytical inference result, or deployment exists |
| Repository boundary | Application, website, and case study must live in `drwbkr1/burnlens-deschutes` |

## Handoff

Every shipped checkpoint must update `docs/status/VERSION_HISTORY.md` with the exact identifier, commit, evidence meaning, and explicit non-implications. Tags and releases are governed by the execution goal, issue-backed quality gates, and the existing release-control evidence—not by stale historical sequencing restrictions.
