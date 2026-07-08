# Version Taxonomy

## Purpose

This taxonomy expands the lightweight BurnLens Deschutes versioning protocol into a Phase Two-ready rule set.

It defines how future BurnLens objective baselines, app/site versions, AOI versions, source records, datasets, label schemas, baseline methods, model packages, run IDs, and reports are named, incremented, and linked.

This is a documentation and traceability-control artifact only. It does not create a tag, release, AOI, source record, dataset, label schema, baseline, model, run, report, map, screenshot, public demo, or operational wildfire product.

## Boundary statement

Experimental BurnLens CV/GEOINT portfolio work. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

Version numbers in BurnLens identify repository state, artifact state, compatibility expectations, lineage, and review status. They do **not** imply operational readiness, official status, field validation, emergency readiness, agency endorsement, production stability, or fitness for evacuation, routing, tactical, or incident-command decisions.

## Research basis

| Source | What it supports | BurnLens decision |
|---|---|---|
| Semantic Versioning 2.0.0, `https://semver.org/spec/v2.0.0.html` | SemVer uses `MAJOR.MINOR.PATCH`; major increments for incompatible API changes, minor for backward-compatible functionality, patch for backward-compatible bug fixes; `0.y.z` is initial development and public API should not be considered stable; released package contents must not be modified. | Use SemVer for software/release-style BurnLens identifiers and keep BurnLens in `0.y.z` while it is experimental and not production-facing. |
| GitHub Docs, About releases, `https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases` | GitHub releases are deployable software iterations; releases are based on Git tags that mark a specific point in repository history. | Treat objective baseline tags and future app/site releases as repository-history anchors that require release notes and boundary checks. |
| Existing `VERSIONING.md` | Current lightweight traceability rule and existing examples. | Replace the lightweight field list with the fuller taxonomy and increment rules defined here. |
| Current Prompt-to-Repo SOP | VERSIONING.md should be updated only when the versioning protocol changes. | Updating `VERSIONING.md` is in scope for P1O5-T03 because the protocol changes. |

## Taxonomy overview

| Version or identifier type | Example | Class | SemVer use | Creates artifact? | Primary purpose |
|---|---|---|---|---|---|
| Objective baseline | `v0.0.5-objective-five-traceability` | Repository baseline tag / release label | SemVer core plus descriptive suffix | No, tag/release only when later authorized | Mark a reviewed objective-level repository state. |
| App/site version | `burnlens-app-v0.1.0` | Software/app version | Yes | Future | Version deployed public/site or app code. |
| AOI version | `deschutes-aoi01-v0.1` | Geospatial scope identifier | SemVer-inspired, simplified | Future | Identify an AOI definition and geometry lineage. |
| Source record ID | `SRC-2026-001` | Immutable record identifier | No | Future | Identify a candidate or approved source record. |
| Dataset version | `deschutes-aoi01-dataset-v0.1.0` | Data package version | SemVer-inspired, adapted | Future | Identify a dataset package built from AOI/source/label decisions. |
| Label schema version | `fire-mask-labels-v0.1` | Annotation/class contract version | SemVer-inspired, simplified | Future | Identify label class definitions and annotation rules. |
| Baseline method version | `burnlens-baseline-v0.1.0` | Method artifact version | SemVer-inspired, adapted | Future | Identify a non-ML baseline method package. |
| Model version | `burnlens-cv-unet-v0.1.0` | Model artifact version | SemVer-inspired, adapted | Future | Identify a trained model package and its training lineage. |
| Run ID | `BL-YYYY-MM-DD-deschutes-aoiXX-mXXX-dXXX` | Unique run identifier | No | Future | Identify one processing/inference/export run. |
| Report version | `run-report-v0.1.0` | Report template or report package version | SemVer-inspired, adapted | Future | Identify report format, logic, and evidence requirements. |

## Universal rules

1. Every public-facing BurnLens artifact must be traceable to a Git commit and to the relevant version or identifier set.
2. Version numbers do not override source precedence. Official sources govern when BurnLens differs.
3. No version number, tag, release, run ID, report version, or model version may imply operational status.
4. BurnLens remains in `0.y.z` development versions until a later explicit release-control decision defines stability criteria.
5. A versioned artifact should not be modified in place after it is published or used in a run. Corrections require a new version, revision, or superseding record.
6. Templates are not completed records. A template version records the template contract, not the existence of a dataset, run, model, or report.
7. IDs and versions must be lowercase except fixed prefixes such as `BL` and `SRC`.
8. Use hyphens, not spaces, in public identifiers.
9. Do not reuse an identifier for a different artifact state.
10. If an artifact changes in a way that would affect a downstream claim, report, run, or public screenshot, create a new version or explicit revision.

## Objective baseline version

### Pattern

```text
v0.0.N-short-objective-slug
```

Example:

```text
v0.0.5-objective-five-traceability
```

### Meaning

An objective baseline marks a reviewed repository state for an objective-level documentation/control milestone.

The `v0.0.N` core is a tag-style prefix. The descriptive suffix explains the objective baseline. The baseline tag is not itself proof that software, data, models, maps, or public demos exist.

### Increment rules

| Change | Rule |
|---|---|
| New objective-level documentation/control baseline | Increment `N` by one. |
| Correction to an existing objective baseline before tag/release creation | Correct in the task PR before merging. |
| Correction after tag/release creation | Create a superseding patch or correction release note; do not silently alter the meaning of the old baseline. |
| Start of runnable app/site release work | Do not use objective baseline alone; use app/site version rules. |

### Required trace links

- parent issue;
- completed task issues;
- merged PRs;
- commit SHA;
- release note or baseline note;
- boundary statement;
- included and excluded artifact list.

## App/site version

### Pattern

```text
burnlens-app-vMAJOR.MINOR.PATCH
```

Example:

```text
burnlens-app-v0.1.0
```

### Meaning

The app/site version applies to deployed website, app, or demo code. It follows SemVer because it is software-facing.

### Increment rules while `0.y.z`

| Change | Rule |
|---|---|
| First usable app/site milestone | Start at `burnlens-app-v0.1.0`. |
| Material new user-visible feature or demo capability | Increment MINOR: `v0.1.0` → `v0.2.0`. |
| Backward-compatible fix, copy correction, metadata correction, or small UI fix | Increment PATCH: `v0.1.0` → `v0.1.1`. |
| Breaking route/API/data-contract change during experimental development | Increment MINOR and document the break because `0.y.z` is not stable. |
| Stable public API or production-facing app claim | Not allowed until a later release-control decision defines `1.0.0` readiness. |

### Required trace links

- Git commit;
- deployment URL or deployment record, when applicable;
- repo PR;
- release note;
- source versions shown by the app, when data/model outputs are displayed;
- boundary warning displayed or linked.

## AOI version

### Pattern

```text
{geography}-aoiNN-v0.MINOR[.PATCH]
```

Example:

```text
deschutes-aoi01-v0.1
```

Optional patch example:

```text
deschutes-aoi01-v0.1.1
```

### Meaning

An AOI version identifies a defined area of interest, geometry source, CRS expectation, inclusion/exclusion rule, and planning rationale.

AOI versions are SemVer-inspired but not software API versions. They identify geospatial scope state.

### Increment rules

| Change | Rule |
|---|---|
| First candidate AOI definition | `deschutes-aoi01-v0.1`. |
| New AOI family or substantially different geography | New AOI number: `deschutes-aoi02-v0.1`. |
| Boundary/geometry change that changes downstream data selection or claims | Increment MINOR: `v0.1` → `v0.2`. |
| Metadata-only correction that does not change geometry, source, or downstream selection | Optional PATCH: `v0.1` → `v0.1.1`. |
| Final AOI selection | Requires an authorized AOI record and later-phase decision; version number alone does not select the AOI. |

### Required trace links

- AOI record;
- geometry source;
- CRS expectation;
- boundary rationale;
- source-precedence note;
- accept/defer/reject decision;
- commit SHA.

## Source record ID

### Pattern

```text
SRC-YYYY-NNN
```

Example:

```text
SRC-2026-001
```

Optional revision field inside the record:

```text
record_revision: r01
```

### Meaning

A source record ID identifies one source-candidate record or approved source record. It is not a version number and is not incremented like SemVer.

The record ID should remain stable. Changes to the record are handled by a revision field or a superseding source record.

### Increment rules

| Change | Rule |
|---|---|
| New source candidate record | Assign next sequential ID for the year: `SRC-2026-001`, `SRC-2026-002`, etc. |
| Metadata correction that does not change source decision | Increment `record_revision` inside the record. |
| License/terms/authority/access decision changes materially | Create a new revision and update the decision log; consider superseding the source record. |
| Different provider, product, authority, or data family | Create a new source record ID. |
| Data file derived from source | Do not use the source record ID as the dataset version; link it from the dataset manifest. |

### Required trace links

- provider;
- product name;
- access URL or access method;
- license/terms note;
- coverage note;
- authority classification;
- source-precedence role;
- accept/defer/reject decision;
- access log, if any;
- commit SHA.

## Dataset version

### Pattern

```text
{aoi-id}-dataset-vMAJOR.MINOR.PATCH
```

Example:

```text
deschutes-aoi01-dataset-v0.1.0
```

### Meaning

A dataset version identifies a data package assembled from one AOI version, source records, access logs, CRS/format prechecks, label schema versions, and provenance records.

Dataset versions are SemVer-inspired but adapted to data lineage. They do not imply statistical validity, label quality, model quality, or operational readiness.

### Increment rules while `0.y.z`

| Change | Rule |
|---|---|
| First retained dataset package for an AOI | Start at `v0.1.0`. |
| Add or remove source products, time windows, tiles, bands, labels, or examples in a way that affects downstream training/evaluation | Increment MINOR. |
| Metadata correction, manifest correction, checksum correction, or typo that does not change files/records used downstream | Increment PATCH. |
| Change AOI family | New dataset family tied to the new AOI ID. |
| Change label schema used by the dataset | Increment dataset MINOR and link the label schema version. |
| Stable data contract claim | Not allowed until later release-control and QA criteria define stability. |

### Required trace links

- AOI version;
- source record IDs;
- access logs;
- format/CRS prechecks;
- label schema version, if labels exist;
- provenance manifest;
- dataset manifest;
- checksum list, when files exist;
- commit SHA.

## Label schema version

### Pattern

```text
{target}-labels-v0.MINOR[.PATCH]
```

Example:

```text
fire-mask-labels-v0.1
```

Optional patch example:

```text
fire-mask-labels-v0.1.1
```

### Meaning

A label schema version identifies class definitions, inclusion/exclusion rules, ambiguity handling, annotation format, nodata/ignore handling, and QA expectations.

It is SemVer-inspired but adapted to annotation contracts.

### Increment rules

| Change | Rule |
|---|---|
| First label schema draft for the target | Start at `v0.1`. |
| Class definition, inclusion/exclusion, ambiguity, ignore/nodata, or annotation-format change that affects labels | Increment MINOR. |
| Clarification that does not change label decisions | Increment PATCH if using patch notation; otherwise record schema revision in the schema file. |
| New target class family | New schema family, such as `burn-scar-labels-v0.1`. |
| Operational label-quality claim | Not allowed; label schema version identifies rules, not field validation. |

### Required trace links

- class definitions;
- target decision;
- annotation format;
- examples and non-examples;
- QA checklist;
- dataset versions using the schema;
- commit SHA.

## Baseline method version

### Pattern

```text
burnlens-baseline-vMAJOR.MINOR.PATCH
```

Example:

```text
burnlens-baseline-v0.1.0
```

### Meaning

A baseline method version identifies a non-ML or simple reference method package used for comparison with future model outputs.

It is SemVer-inspired but adapted to method reproducibility rather than public API compatibility.

### Increment rules while `0.y.z`

| Change | Rule |
|---|---|
| First baseline method package | Start at `v0.1.0`. |
| Method logic, thresholds, source handling, preprocessing, output contract, or evaluation behavior changes | Increment MINOR. |
| Documentation, config comment, or implementation fix that does not change output behavior | Increment PATCH. |
| Different baseline family | Use a new method family name or explicit method identifier. |
| Method used in a run | Record the baseline version in the run manifest and run ID method token. |

### Required trace links

- method description;
- input contract;
- output contract;
- config;
- dataset version;
- commit SHA;
- run IDs using the method;
- limitations.

## Model version

### Pattern

```text
burnlens-cv-{architecture}-vMAJOR.MINOR.PATCH
```

Example:

```text
burnlens-cv-unet-v0.1.0
```

### Meaning

A model version identifies a trained model package, architecture, configuration, dataset lineage, label schema, metrics, known limitations, and intended portfolio use.

It is SemVer-inspired but adapted to model artifact lineage. A model version does not imply production readiness, emergency readiness, field validation, or agency endorsement.

### Increment rules while `0.y.z`

| Change | Rule |
|---|---|
| First trained package for a model family | Start at `v0.1.0`. |
| Architecture, training dataset, label schema, loss function, major hyperparameters, preprocessing, or output contract changes | Increment MINOR. |
| Retraining with same contract but corrected seed/config/weights packaging, metadata correction, or documentation fix | Increment PATCH if output behavior is not materially reinterpreted; otherwise increment MINOR. |
| New architecture family | New family name, such as `burnlens-cv-segformer-v0.1.0`. |
| Public performance claim | Requires evidence, metrics, limitations, and claim traceability; version number alone is not evidence. |

### Required trace links

- model card;
- architecture;
- training commit;
- dataset version;
- label schema version;
- config;
- weights checksum, when weights exist;
- metrics;
- known limitations;
- intended use boundary;
- run IDs using the model.

## Run ID

### Pattern

```text
BL-YYYY-MM-DD-deschutes-aoiXX-mXXX-dXXX
```

Example:

```text
BL-2026-07-08-deschutes-aoi01-m001-d001
```

### Meaning

A run ID identifies one execution of a processing, baseline, inference, export, overlay, or report workflow.

A run ID is not SemVer. It should be unique and immutable. It should never be reused for a rerun, even if inputs are unchanged.

### Token rules

| Token | Meaning | Example |
|---|---|---|
| `BL` | BurnLens run prefix | `BL` |
| `YYYY-MM-DD` | Run date in local project date or UTC, recorded explicitly in manifest | `2026-07-08` |
| `deschutes-aoiXX` | AOI family token | `deschutes-aoi01` |
| `mXXX` | method/model/baseline token | `m001` |
| `dXXX` | dataset token | `d001` |

### Increment / uniqueness rules

| Change | Rule |
|---|---|
| Any new execution | Create a new run ID. |
| Rerun with same inputs and code | Create a new run ID and link it to the prior run as a rerun. |
| Failed run worth preserving | Keep the run ID and mark status as failed/incomplete in the manifest. |
| Deleted or discarded run | Do not reuse the ID; record deletion/discard note if it was referenced. |
| Public screenshot/report generated from run | Must cite the run ID and linked versions. |

### Required trace links

- commit SHA;
- app/site version if app output is involved;
- AOI version;
- source record IDs;
- dataset version;
- label schema version, if labels used;
- baseline or model version;
- run manifest;
- output inventory;
- warnings;
- limitations;
- report version, if a report is generated.

## Report version

### Pattern

```text
run-report-vMAJOR.MINOR.PATCH
```

Example:

```text
run-report-v0.1.0
```

Optional report instance naming:

```text
BL-2026-07-08-deschutes-aoi01-m001-d001-run-report-v0.1.0
```

### Meaning

A report version identifies the report template, summary logic, evidence requirements, warnings, limitations, and claim language used to describe a run.

A report version does not validate the run or make the output official.

### Increment rules while `0.y.z`

| Change | Rule |
|---|---|
| First report template | Start at `v0.1.0`. |
| New sections, evidence requirements, summary logic, warning logic, or claim gates | Increment MINOR. |
| Typo, formatting, or metadata correction that does not change interpretation | Increment PATCH. |
| Report generated for a run | Record both report version and run ID. |
| Public report claim | Must link to evidence, source precedence, limitations, and boundary text. |

### Required trace links

- report template version;
- run ID;
- run manifest;
- source records;
- dataset/model/baseline versions;
- commit SHA;
- claim-evidence links;
- warnings and limitations.

## Method token registry rule

Run ID method tokens such as `m001` must resolve to a method or model record.

| Token | Resolves to | Example |
|---|---|---|
| `m001` | Baseline or model record | `burnlens-baseline-v0.1.0` or `burnlens-cv-unet-v0.1.0` |
| `d001` | Dataset record | `deschutes-aoi01-dataset-v0.1.0` |

Future run-package work should create the registry file or manifest fields that map `mXXX` and `dXXX` tokens to full versions. Until that registry exists, run IDs should be treated as future contract patterns, not completed records.

## Public claim and portfolio readiness rule

A BurnLens output, screenshot, summary, report, website card, or portfolio claim is not portfolio-ready unless it can trace to:

- Git commit;
- relevant repo/objective baseline or app/site version;
- AOI version;
- source record IDs;
- dataset version, when data exists;
- label schema version, when labels exist;
- baseline or model version, when a method exists;
- run ID, when an output is generated;
- report version, when a report is generated;
- warning flags;
- limitations;
- source-precedence note.

Even when all trace links exist, the artifact remains experimental unless a later release-control record explicitly says otherwise.

## Version comparison rule

SemVer comparison rules apply only to software/release-style identifiers with a SemVer core, such as:

- `burnlens-app-v0.1.0`;
- `burnlens-baseline-v0.1.0`, as an adapted artifact-version convention;
- `burnlens-cv-unet-v0.1.0`, as an adapted artifact-version convention;
- `run-report-v0.1.0`, as an adapted report-template convention.

Do not compare source record IDs, AOI numbers, dataset IDs, or run IDs as if they were software compatibility promises.

## Acceptance criteria

| Check | Status | Notes |
|---|---|---|
| Version classes separated. | Satisfied | Taxonomy table and sections separate each class. |
| Examples included. | Satisfied | Each class includes the requested example. |
| Increment rules defined. | Satisfied | Each class has rules. |
| SemVer basis recorded. | Satisfied | Research basis section. |
| BurnLens-specific GEOINT IDs adapted. | Satisfied | AOI, source, dataset, label, and run sections. |
| Version numbers do not imply operational readiness. | Satisfied | Boundary and claim rules. |
| No data/model/map work created. | Satisfied | Documentation only. |

## Reject or revise if

Revise this taxonomy if it:

- treats source records or run IDs as SemVer software versions;
- allows version numbers to imply official, operational, field-validated, emergency-ready, or agency-endorsed status;
- allows data/model/map/public outputs without linked records;
- permits overwriting a published versioned artifact without a superseding version or revision;
- fails to keep official/reference sources separate from BurnLens-derived outputs.

## Handoff

P1O5-T04 should use this taxonomy and `VERSIONING.md` to define release and tag control. It should decide when objective baseline tags, GitHub releases, app/site releases, and release notes are allowed, and what release gates block publication.
