# Run Package Contract

## Purpose

This document defines the future BurnLens Deschutes run folder and run package contract before any run exists.

A run package will be the smallest reviewable bundle that connects one future processing, baseline, inference, export, overlay, or report workflow to its source records, versions, provenance, outputs, warnings, and claims.

This contract is documentation and records work only. It does not create a run folder, run package instance, source data, imagery, labels, masks, prediction masks, vector outputs, exposure summaries, map exports, screenshots, public demos, tags, GitHub releases, or operational wildfire products.

## Boundary statement

Experimental BurnLens CV/GEOINT portfolio work. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

A run package proves traceability for a future BurnLens workflow. It does **not** prove operational readiness, official status, field validation, emergency readiness, agency endorsement, production stability, evacuation support, routing support, tactical support, or incident-command suitability.

## Current implementation status

No BurnLens run package exists yet.

No `/runs/` folder is created by Objective Five / Task 6.

No files below are created by this task:

```text
/runs/BL-YYYY-MM-DD-deschutes-aoiXX-mXXX-dXXX/
  run_manifest.json
  source_links.md
  processing_log.md
  output_inventory.md
  warnings.md
  run_report.md
  prediction_mask.tif
  prediction_polygons.geojson
  exposure_summary.json
  map_export.png
```

T06 defines the contract and reusable manifest template only.

## Research basis

| Source | What it supports | BurnLens decision |
|---|---|---|
| W3C PROV-Overview, `https://www.w3.org/TR/prov-overview/` | Provenance is information about entities, activities, and people involved in producing data or things and can support quality, reliability, and trustworthiness assessment. | Treat each future run package as a provenance bundle that must connect inputs, activities, agents/tools, generated outputs, reports, and claims. |
| W3C PROV-DM, `https://www.w3.org/TR/prov-dm/` | PROV-DM defines entities, activities, agents, usage, generation, derivation, attribution, and association. | Require run package records to identify used entities, generated entities, processing activities, tools/agents, and derivation links. |
| OGC STAC Community Standard 1.1, `https://docs.ogc.org/cs/25-004/25-004.html` | STAC standardizes geospatial asset metadata and describes spatiotemporal assets as files representing information about Earth at a place and time; STAC Items include asset links and metadata. | Use STAC only as a lightweight reference for geospatial asset inventory concepts such as asset paths, media types, roles, links, and metadata. Do not claim STAC compliance in T06. |
| `docs/phase-one/objective-five/VERSION_TAXONOMY.md` | Defines the run ID pattern, version classes, uniqueness rules, and required trace links for runs and reports. | Use `BL-YYYY-MM-DD-deschutes-aoiXX-mXXX-dXXX` as the required run ID and require AOI, dataset/source, method, commit, output inventory, warnings, and report links. |
| `docs/phase-one/objective-five/PROVENANCE_TRACEABILITY_SPEC.md` | Defines the source-to-claim chain and BurnLens entity/activity/agent equivalents. | Make the run package the future bundle that connects provenance manifest, processing step, method version, output artifact, report, claim-register entry, and public claim. |
| `docs/phase-one/objective-five/RELEASE_CONTROL.md` | Defines release classes, do-not-release triggers, included/excluded work, evidence links, and source-precedence gates. | Block public release, screenshots, and report publication unless run package evidence and release-control gates pass. |
| `docs/objective-one/SOURCE_PRECEDENCE.md` and `docs/objective-one/USE_BOUNDARIES.md` | Official sources govern and BurnLens must preserve non-operational boundaries. | Require warnings and source-precedence status in every run manifest, warning file, run report, and screenshot reference. |

## Future run ID

### Pattern

```text
BL-YYYY-MM-DD-deschutes-aoiXX-mXXX-dXXX
```

Example only:

```text
BL-2026-07-08-deschutes-aoi01-m001-d001
```

This example is not an existing run.

### Token meanings

| Token | Meaning | Required source |
|---|---|---|
| `BL` | BurnLens run prefix | Fixed project prefix. |
| `YYYY-MM-DD` | Run date | Recorded in manifest with timezone basis. |
| `deschutes-aoiXX` | AOI family token | Must link to AOI version and AOI record when AOI exists. |
| `mXXX` | Method/model/baseline token | Must link to method version and method record/config when method exists. |
| `dXXX` | Dataset token | Must link to dataset version, source records, access logs, and prechecks when dataset exists. |

### Run ID rules

1. A run ID identifies one future execution or preserved failed execution.
2. A run ID is not SemVer.
3. A run ID must never be reused.
4. A rerun with the same inputs and code still gets a new run ID.
5. A failed run may keep its run ID if it is worth preserving for troubleshooting.
6. A discarded run ID must not be reused once referenced.
7. Every public screenshot, map export, report figure, website card image, or portfolio case-study image generated from a future run must reference the run ID.

## Future run folder structure

The required future run folder shape is:

```text
/runs/BL-YYYY-MM-DD-deschutes-aoiXX-mXXX-dXXX/
  run_manifest.json
  source_links.md
  processing_log.md
  output_inventory.md
  warnings.md
  run_report.md
```

Later phases may add output files:

```text
prediction_mask.tif
prediction_polygons.geojson
exposure_summary.json
map_export.png
```

Objective Five must not create those output files.

## Required files

| File | Required in future run package? | Purpose | Objective Five status |
|---|---:|---|---|
| `run_manifest.json` | Yes | Machine-readable run identity, versions, inputs, provenance links, warnings, outputs, checksums, and review status. | Template only. |
| `source_links.md` | Yes | Human-readable source record, access log, precheck, terms/licensing, and source-precedence links. | Contract only. |
| `processing_log.md` | Yes | Human-readable processing steps, commands/configs, timestamps, tools, parameters, errors, rerun notes, and exclusions. | Contract only. |
| `output_inventory.md` | Yes | Human-readable inventory of planned/created outputs, paths, media types, checksums, public-facing status, and exclusions. | Contract only. |
| `warnings.md` | Yes | Required warning, source-precedence status, limitations, prohibited uses, and unresolved caveats. | Contract only. |
| `run_report.md` | Yes | Human-readable run summary, evidence, limitations, output inventory, warning, claim links, and public-language review. | Contract only. |

## Optional later output files

| File | Future role | Creation status in Objective Five | Public rule |
|---|---|---|---|
| `prediction_mask.tif` | Future raster mask output. | Not created. | Must be listed in manifest and output inventory before use. |
| `prediction_polygons.geojson` | Future vectorized polygon output. | Not created. | Must reference source mask/run ID and warning. |
| `exposure_summary.json` | Future exposure-style summary output. | Not created. | Must preserve non-operational wording and source precedence. |
| `map_export.png` | Future static map/screenshot export. | Not created. | Must reference run ID, warning, and source-precedence status. |

## Minimum manifest fields

The future `run_manifest.json` must record:

| Field group | Required content |
|---|---|
| Run identity | Run ID, run folder, status, type, created/started/completed timestamps, rerun/supersession links. |
| Repository state | Repository name, branch, commit SHA, app/repo version or objective baseline, version taxonomy reference, release-control reference. |
| AOI version | AOI ID, AOI version, AOI record, geometry path, geometry checksum when geometry exists. |
| Dataset/source versions | Dataset ID/version/manifest, source records, access logs, format/CRS prechecks, license/terms status, checksums. |
| Method version | Method token, method kind, baseline/model/method version, config path, config checksum, model weights checksum when applicable. |
| Provenance links | Provenance manifest, traceability record, used/generated entities, activities, agents/tools. |
| Required files | Required future run documents and their status. |
| Output inventory | Output IDs, paths, media types, artifact kinds, created-by activity, checksum plan, public-facing status. |
| Warnings/use boundary | Required BurnLens warning, official-sources-govern flag, prohibited uses, source-precedence status, limitations. |
| Public artifact rules | Screenshot rule, claim-register requirement, release-control requirement, public use status. |
| Validation/review | JSON validation, source-links completion, processing-log completion, output-inventory completion, warning completion, report completion, claim review, release-control review. |
| Prohibited status | Explicit booleans confirming the template did not create data, imagery, labels, masks, outputs, maps, demos, or official/operational claims. |

## Required run package gates

A future run package must not be treated as complete unless all required gates pass.

| Gate | Required evidence |
|---|---|
| Task authorization | GitHub task issue, artifact contract, branch, and PR. |
| Source/AOI lineage | AOI record/version, source records, access logs, and format/CRS prechecks where applicable. |
| Provenance | Provenance manifest and traceability record linking source, access, precheck, processing, method, outputs, report, and claims. |
| Versioning | Run ID, commit SHA, app/repo version, AOI version, dataset/source versions, method version, and report version if report exists. |
| Processing log | Parameters/configs, tools, timestamps, errors, rerun notes, and exclusions. |
| Output inventory | Every output path, media type, checksum plan or checksum, public-facing status, and warning requirement. |
| Warnings | Required BurnLens warning, source-precedence status, limitations, and prohibited-use language. |
| Claims | Claim-register entry for any run, output, report, screenshot, or public-facing claim. |
| Release control | Release-control review before any public package, screenshot, report, case-study figure, or website/demo use. |

If any gate cannot be completed, the run package must be marked `failed`, `incomplete`, `blocked`, `discarded`, or `not ready for public use`.

## Public screenshot and map-export rule

Every future public screenshot, `map_export.png`, website image, report figure, slide image, case-study image, or portfolio card image derived from BurnLens output must visibly or nearby reference:

- run ID;
- run manifest path;
- warning path or warning text;
- source-precedence status;
- output inventory entry;
- claim-register entry if the screenshot supports a claim.

A screenshot without a run ID is not publishable as BurnLens evidence.

## Checksum and inventory rule

Use `sha256` as the default checksum algorithm unless a later task approves another algorithm.

Required checksum states:

| State | Meaning |
|---|---|
| `not-created` | File does not exist yet. |
| `not-authorized` | File is outside current task/phase scope. |
| `pending` | File exists or is planned but checksum is not yet recorded. Public claim blocked. |
| `complete` | Checksum recorded in manifest and inventory. |
| `superseded` | File was replaced by a later output/version and must not be used without explanation. |

No downstream claim may rely on an output whose checksum status is missing or unresolved.

## Source-precedence requirement

Every future run package must record one source-precedence status:

| Status | Use |
|---|---|
| `official-source-record` | Source record is official/primary for the topic. |
| `official-source-compared` | BurnLens output was compared to official/reference source. |
| `burnlens-derived-experimental` | Output is BurnLens-derived and experimental. |
| `conflict-with-official-source` | Public release blocked unless conflict is prominently stated or artifact excluded. |
| `source-precedence-unresolved` | Public claim blocked. |
| `not-applicable-documentation-only` | Documentation/control artifact with no data/source claim. |

Official sources govern in every case.

## Future run report rule

`run_report.md` is a required future run package file, but T06 does not create a report instance.

A future run report must include:

- run ID;
- report version;
- run manifest path;
- source links path;
- processing log path;
- output inventory path;
- warnings path;
- source-precedence status;
- limitations;
- claim-register links;
- public-language decision;
- excluded claims.

A run report does not make the run official or operational.

## Release-control relationship

A run package is not a release by itself.

A run package may become part of a future release only after:

1. required run package files exist;
2. output checksums and inventories are complete;
3. warnings and source-precedence status are complete;
4. claim-register entries support any public statements;
5. release-control gates pass;
6. the user explicitly authorizes public release action.

No tag or GitHub release is created by this contract.

## Rejection and no-go conditions

Reject, block, or mark incomplete any future run package if:

- run ID is missing, reused, or ambiguous;
- commit SHA is missing;
- AOI, dataset, source, access, precheck, method, or provenance links are missing when applicable;
- output inventory omits a generated output;
- checksum plan is missing;
- warnings are missing;
- source-precedence status is unresolved for a public artifact;
- report or screenshot lacks run ID;
- public claim lacks a claim-register entry;
- release control has not reviewed a public artifact;
- the run package implies operational, official, field-validated, emergency-ready, agency-endorsed, evacuation, routing, tactical, or incident-command use.

## Acceptance criteria

| Check | Status | Notes |
|---|---|---|
| Future run folder structure defined. | Satisfied | Required `/runs/BL-.../` contract included. |
| Contract says no run package exists yet. | Satisfied | Current implementation status section. |
| Manifest records commit and version fields. | Satisfied | Minimum manifest fields and JSON template. |
| Manifest records AOI, dataset/source, method, timestamps, warnings, and use boundary. | Satisfied | Minimum manifest fields and JSON template. |
| Future public screenshots must reference run ID. | Satisfied | Screenshot rule included. |
| Later output files listed but not created. | Satisfied | Optional output table. |
| No data/model/map/public-output work authorized. | Satisfied | Boundary, optional-output status, and prohibited-status fields. |

## Handoff

P1O5-T07 should use this run package contract to define an artifact registry specification that can index future manifests, source records, outputs, reports, screenshots, and claim evidence without creating those artifacts yet.
