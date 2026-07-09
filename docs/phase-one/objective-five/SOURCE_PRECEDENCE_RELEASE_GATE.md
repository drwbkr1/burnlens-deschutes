# Source Precedence Release Gate

## Purpose

This document makes “official sources govern” an enforceable BurnLens Deschutes release requirement.

It integrates existing source-precedence, versioning, claim-traceability, run-package, artifact-registry, and release-control rules into a gate that future run reports, public artifacts, release notes, screenshots, maps, portfolio assets, and release-like statements must pass before publication.

This is documentation and records work only. It does not create a run report, run package, map, screenshot, public artifact, tag, GitHub release, completed claim record, source record, AOI record, data product, model product, or operational wildfire product.

## Boundary statement

Experimental BurnLens CV/GEOINT portfolio work. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

A source-precedence release gate does **not** make BurnLens official, operational, field-validated, emergency-ready, agency-endorsed, production-stable, or suitable for evacuation, routing, tactical, incident-command, road-closure, hazard-confirmation, or public-safety decision support.

## Current implementation status

No future run report exists yet.

No BurnLens-derived output exists yet.

No public release, public screenshot, public map, run package, source-precedence review record, or completed claim record is created by P1O5-T09.

This document defines the future gate only.

## Governing basis

No new external official-source claims are introduced by this gate. Existing BurnLens repo controls govern this task:

| Governing artifact | Gate use |
|---|---|
| `docs/objective-one/SOURCE_PRECEDENCE.md` | Official sources govern, source hierarchy, conflict-handling procedure, and required run-report language. |
| `docs/objective-one/USE_BOUNDARIES.md` | Prohibited emergency, official, operational, evacuation, routing, tactical, and incident-command uses. |
| `docs/phase-one/objective-five/RELEASE_CONTROL.md` | Release classes, source-precedence release gate, boundary gate, and do-not-release triggers. |
| `docs/phase-one/objective-five/CLAIM_TRACEABILITY_PROTOCOL.md` | Evidence-linked claims, forbidden-claim checks, and fire/evacuation/hazard/road source-precedence language requirement. |
| `docs/phase-one/objective-five/ARTIFACT_REGISTRY_SPEC.md` | Origin classes, public-use status, and source-separation controls. |
| `docs/phase-one/objective-five/RUN_PACKAGE_CONTRACT.md` | Future run ID, manifest, output inventory, warnings, and screenshot run-ID rule. |
| `docs/phase-one/objective-five/VERSION_TAXONOMY.md` | Version and identifier classes for sources, methods, datasets, models, runs, and reports. |
| `VERSIONING.md` | Traceability expectations and no-readiness implication from version numbers. |

## Core rule

A BurnLens run report, public artifact, release note, screenshot, map export, portfolio asset, or release-like public statement must not be published unless source-precedence status is recorded and release status is assigned.

The gate has three required decisions:

1. **Hierarchy decision** — which source class governs this topic?
2. **Conflict decision** — does the BurnLens-derived output differ from a higher-priority source?
3. **Release-status decision** — is the public artifact `normal`, `provisional`, `degraded`, `superseded`, or `withheld`?

If any decision is missing, release is blocked.

## Existing source hierarchy

This gate preserves the existing source hierarchy exactly: BurnLens-derived outputs are lowest priority.

| Priority | Source class | Governs | Release implication |
|---:|---|---|---|
| 1 | Emergency and evacuation sources | Warnings, alerts, evacuation orders, road closures, immediate public-safety issues. | BurnLens outputs must not override these. Conflict usually means `withheld` or heavily caveated `degraded`. |
| 2 | Incident and fire-status sources | Current wildfire incident status, public fire updates, suppression information, operational fire context. | BurnLens outputs must not be presented as independent fire-status conclusions. |
| 3 | Official hazard, planning, and GIS sources | Public-agency hazard, land, road, parcel, facility, and planning context. | BurnLens outputs may support technical screening only if separated and caveated. |
| 4 | Public imagery and active-fire reference data | Imagery review, baseline methods, weak labeling, comparison, visualization. | Must be interpreted carefully; not evacuation guidance or field-confirmed incident truth. |
| 5 | BurnLens-derived outputs | Baseline masks, model masks, polygons, summaries, maps, confidence layers, and reports. | Lowest priority; must yield to all higher-priority sources. |

## Release-status vocabulary

Every future public artifact or release-like statement involving BurnLens-derived output must state one of the statuses below.

| Status | Meaning | Public release allowed? | Required action |
|---|---|---:|---|
| `normal` | No known conflict with a higher-priority source; required evidence, warning, and claim gates pass. | Yes, if all release gates pass. | Include standard warning and source-precedence statement. |
| `provisional` | Evidence exists, but source timing, spatial alignment, access state, official comparison, or method state is incomplete or pending. | Maybe; limited public use only if limitation is prominent and no public-safety implication is introduced. | Use provisional limitation language; avoid strong conclusions. |
| `degraded` | Output exists but quality, timeliness, source comparison, CRS alignment, method limitation, or conflict context reduces interpretability. | Maybe; only if caveated responsibly and not public-safety sensitive. | Include degraded-status reason, limitation, and source-precedence note. |
| `superseded` | A newer official source, higher-priority record, newer run, or corrected artifact has replaced the output for public interpretation. | No for active public claims; yes only as historical/internal evidence. | Mark as superseded and link replacement source/artifact. |
| `withheld` | Output cannot be caveated responsibly, conflicts with official information in a public-safety-sensitive way, or lacks required evidence. | No. | Do not publish; record withheld reason and required remediation. |

A missing status is a release blocker.

## Future run-report source-precedence checks

Every future run report must include a source-precedence section before it can support a public artifact.

Minimum run-report checks:

| Check | Required? | Pass condition | Release blocker if missing? |
|---|---:|---|---:|
| Run ID present | Yes | Run report references `BL-YYYY-MM-DD-deschutes-aoiXX-mXXX-dXXX`. | Yes |
| Run manifest linked | Yes | `run_manifest.json` linked from run package. | Yes |
| Output inventory linked | Yes | `output_inventory.md` linked and relevant outputs listed. | Yes |
| Source links present | Yes | `source_links.md` or source record IDs linked. | Yes |
| Source hierarchy reviewed | Yes | Highest relevant source class identified. | Yes |
| Official/reference comparison status recorded | Yes | Compared, not applicable, not available, pending, or unresolved. | Yes if public-facing. |
| Conflict status recorded | Yes | No known conflict, conflict identified, conflict unresolved, or not applicable. | Yes if public-facing. |
| Release status assigned | Yes | `normal`, `provisional`, `degraded`, `superseded`, or `withheld`. | Yes |
| Required warning included | Yes | Full BurnLens warning included or linked. | Yes |
| Claim evidence linked | Yes if public-facing | Claim evidence record exists or public-use status is blocked. | Yes if public-facing. |
| Responsible caveat possible | Yes | Reviewer can state limitations without implying public-safety guidance. | Yes if no |

## Required run-report language pattern

When a BurnLens output differs from an official or higher-priority source, the future run report must include this pattern from `SOURCE_PRECEDENCE.md`:

```text
Source-precedence note: This BurnLens output differs from [official source name] regarding [issue]. Because BurnLens Deschutes is an experimental portfolio workflow, [official source name] governs. This output should be interpreted only as a technical artifact from run [run ID], not as official wildfire, evacuation, hazard, or emergency information.
```

If there is no known conflict, the run report should still include standard source-precedence language:

```text
Official sources govern. BurnLens outputs are experimental and not emergency guidance.
```

If fire, evacuation, hazard, road, routing, closure, emergency, incident, perimeter, structure exposure, or public-safety context appears, the full warning should be used:

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

## Conflict handling

When a BurnLens-derived output differs from official or higher-priority information:

1. identify the BurnLens output and run ID;
2. identify the official or higher-priority source;
3. compare dates, timestamps, spatial extent, data age, and topic scope;
4. determine whether the conflict affects public interpretation;
5. assign a release status;
6. add the required source-precedence note to the run report;
7. update the claim evidence record if a public claim exists;
8. exclude, caveat, supersede, or withhold the artifact according to this gate.

## Conflict-to-status decision table

| Conflict condition | Required status | Public-release decision |
|---|---|---|
| No known conflict; official/reference comparison complete; evidence gates pass. | `normal` | Allowed if all other gates pass. |
| Official/reference comparison not complete, but public copy is clearly documentation-only and non-operational. | `provisional` | Allowed only with prominent limitation. |
| Source timing, CRS, spatial extent, or method limitation reduces interpretability. | `degraded` | Allowed only if limitation is specific and public-safety context is avoided. |
| Higher-priority source or newer run replaces the output. | `superseded` | Block active public release; retain only as historical/internal evidence. |
| Conflict involves emergency, evacuation, road closure, incident command, public-safety direction, or official fire status and cannot be caveated without confusion. | `withheld` | Block release. |
| Official-source conflict exists and no reviewer can state a responsible caveat. | `withheld` | Block release. |
| Evidence link, run ID, source-precedence status, or warning is missing. | `withheld` until fixed | Block release. |

## Responsible caveat test

Before any conflicting or limited BurnLens-derived output is released, ask:

1. Would a reasonable viewer understand that official sources govern?
2. Would a reasonable viewer understand that BurnLens is experimental?
3. Would the caveat prevent the output from being used as evacuation, routing, road-closure, tactical, incident-command, or emergency guidance?
4. Is the limitation visible where the output is viewed, not hidden in a separate file?
5. Is the public claim no stronger than the evidence?
6. Are official/reference sources and BurnLens-derived outputs visibly separated?

If the answer to any question is no, the artifact cannot be caveated responsibly and release is blocked.

## Public artifact gate

Before a public artifact is released, posted, shown, exported, attached, linked, or used in portfolio copy, it must include:

- release status: `normal`, `provisional`, `degraded`, `superseded`, or `withheld`;
- source-precedence status;
- official/reference source link or statement that comparison is not applicable;
- run ID when derived from a run;
- claim evidence link when making a public-facing claim;
- standard or full BurnLens warning;
- limitation statement;
- release-control decision.

A public artifact cannot be released if any required field is missing.

## Versioning relationship

Version numbers, run IDs, report versions, tags, release notes, and GitHub releases do not override source precedence.

Versioning must support the gate by recording:

| Version/identifier | Gate use |
|---|---|
| Source record ID | Identifies official/reference source evidence. |
| AOI version | Identifies the spatial scope being discussed. |
| Dataset/source version | Identifies data basis and source vintage. |
| Method/model version | Identifies how output was created. |
| Run ID | Identifies the exact run producing the output. |
| Report version | Identifies the report state and whether source-precedence notes changed. |
| Commit SHA | Identifies the repo state that produced or reviewed the artifact. |
| Tag/release name | Identifies release class only; does not imply readiness. |

If a source-precedence conflict changes public interpretation, the report version or public artifact status must change. Do not silently edit public claims in place.

## Release-control integration

The source-precedence release gate must be checked before:

- objective baseline release notes;
- Git tags;
- GitHub releases;
- app/site releases;
- data package releases;
- model/baseline releases;
- run/report releases;
- public portfolio releases;
- public screenshots or map exports;
- website cards or case-study assets;
- slide-deck or public-demo claims.

Release is blocked when:

- source-precedence statement is missing;
- official/reference comparison is required but unresolved;
- BurnLens-derived output is presented as independent incident, evacuation, hazard, road, emergency, or public-safety truth;
- release status is missing;
- release status is `withheld`;
- release status is `superseded` but the artifact is being presented as active/current;
- `provisional` or `degraded` artifact lacks a prominent limitation;
- a conflict cannot be caveated responsibly;
- claim evidence link is missing for a public-facing claim;
- public copy implies official, operational, field-validated, emergency-ready, agency-endorsed, evacuation, routing, tactical, road-closure, or incident-command use.

## Release-note requirement

Every future release note that references wildfire, hazard, emergency, transportation, road, air-quality, incident, official-source context, or BurnLens-derived output must include:

```text
Official sources govern when BurnLens differs from county, state, federal, fire-service, emergency-management, transportation, air-quality, or incident sources.
```

If the release includes a BurnLens-derived output, it must also include the output release status and the full warning unless another approved release-control artifact provides a stricter equivalent.

## Public-copy examples

| Unsafe copy | Required decision | Safer direction |
|---|---|---|
| `BurnLens shows the current fire perimeter.` | Block / `withheld` | `BurnLens output is experimental and cannot replace official incident information.` |
| `This map shows evacuation risk.` | Block / `withheld` | `BurnLens does not provide evacuation guidance; official evacuation sources govern.` |
| `The model found a hotspot not shown by official sources.` | `withheld` or `degraded` | `Do not publish as a public claim unless official-source comparison and responsible caveat review pass.` |
| `Experimental output from run BL-...; official sources govern.` | Possible `normal` or `provisional` | Allowed only if run manifest, source-precedence status, claim evidence, and release gates pass. |
| `Older run screenshot retained for method history.` | `superseded` | May be retained as historical/internal evidence with replacement link, not active public interpretation. |

## Acceptance criteria

| Check | Status | Notes |
|---|---|---|
| Matches existing source hierarchy. | Satisfied | Emergency/evacuation, incident/fire status, official hazard/planning/GIS, imagery/reference data, and BurnLens-derived outputs are preserved in priority order. |
| BurnLens-derived outputs are lowest priority. | Satisfied | Gate states BurnLens outputs yield to all higher-priority sources. |
| Required run-report language pattern included. | Satisfied | Pattern from `SOURCE_PRECEDENCE.md` included verbatim with placeholders. |
| Future run-report checks defined. | Satisfied | Run-report source-precedence checklist included. |
| Conflict handling defined. | Satisfied | Conflict procedure and conflict-to-status table included. |
| Public artifact statuses required. | Satisfied | `normal`, `provisional`, `degraded`, `superseded`, and `withheld` required. |
| Irresponsibly caveated outputs blocked. | Satisfied | Responsible caveat test and release blockers included. |
| Versioning and release-control integration included. | Satisfied | Versioning relationship and release-control integration sections included. |

## Handoff

P1O5-T10 should use this gate to create reproducibility and release QA checklists. Those checklists should verify that future release candidates include source-precedence status, responsible caveat review, evidence links, run/report identifiers, warning language, and explicit public-use decisions before any release-like action occurs.
