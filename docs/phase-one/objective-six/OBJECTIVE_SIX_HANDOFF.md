# Phase One / Objective Six — Handoff

## Handoff status

Objective Six is complete as a documented, reviewable repository-control baseline after P1O6-T09 merged through PR #243 and the final status was rechecked and synchronized.

Parent issue #195 remains open only for a separate manual-closure action. Drew must explicitly authorize that closure after P1O6-SYNC-09 reaches `main` and the final completion summary is posted.

## Completed baseline

Objective Six connects:

```text
task issue
→ canonical task capsule
→ bounded branch
→ Tier 0 plus selective Tier 1 context
→ justified Tier 2 only when needed
→ fresh research when required
→ allowed-file edits
→ dated prompt/build log
→ named verification and actual results
→ complete diff review
→ task-scoped pull request
→ optional AI-assisted review
→ mandatory human review
→ separate merge authorization
→ authorized merge
→ parent update and conditional status synchronization
→ handoff
```

This is a repository-control baseline. It is not an executed data, model, run, map, demo, or operational baseline.

## Minimum governing context for future tasks

Every future BurnLens repository task should begin with Tier 0 from the SOP and then select only the Tier 1 controls relevant to the task.

### Core workflow and current status

```text
README.md
AGENTS.md
CONTRIBUTING.md
docs/workflows/PROMPT_TO_REPO_SOP.md
docs/phase-one/objective-six/OBJECTIVE_SIX_CLOSEOUT.md
docs/phase-one/objective-six/OBJECTIVE_SIX_HANDOFF.md
docs/phase-one/objective-six/OBJECTIVE_SIX_TRACKER.md
docs/phase-one/objective-six/PROMPT_BUILT_DEVELOPMENT_PROTOCOL.md
docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md
```

### Task, issue, PR, and prompt-log interfaces

```text
.github/ISSUE_TEMPLATE/task.yml
.github/PULL_REQUEST_TEMPLATE.md
templates/CODEX_TASK_PACKET.md
templates/CODEX_TASK_TEMPLATE.md
PROMPT_LOG.md
records/PROMPT_BUILD_LOG.md
templates/PROMPT_LOG_ENTRY.md
```

### Project boundary and source precedence

```text
docs/objective-one/TECHNICAL_DESCRIPTION.md
docs/objective-one/USE_BOUNDARIES.md
docs/objective-one/SOURCE_PRECEDENCE.md
```

### Version, provenance, claims, reproducibility, and release gates

```text
VERSIONING.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_HANDOFF.md
docs/phase-one/objective-five/VERSION_TAXONOMY.md
docs/phase-one/objective-five/RELEASE_CONTROL.md
docs/phase-one/objective-five/PROVENANCE_TRACEABILITY_SPEC.md
docs/phase-one/objective-five/RUN_PACKAGE_CONTRACT.md
docs/phase-one/objective-five/ARTIFACT_REGISTRY_SPEC.md
docs/phase-one/objective-five/CLAIM_TRACEABILITY_PROTOCOL.md
docs/phase-one/objective-five/SOURCE_PRECEDENCE_RELEASE_GATE.md
docs/phase-one/objective-five/REPRODUCIBILITY_CHECKLIST.md
docs/phase-one/objective-five/RELEASE_QA_CHECKLIST.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_RESEARCH_VALIDATION_LOG.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_CLAIMS_CHECK.md
```

Do not load every Objective Five file for every task. Use the SOP to select only the controls matching the proposed work.

## Non-negotiable workflow rules

Future tasks must:

1. start from an authorized GitHub issue;
2. instantiate the canonical task capsule without broadening the issue;
3. create a compact task branch from current `main` unless another base is authorized;
4. load Tier 0 and only relevant Tier 1 artifacts;
5. use Tier 2 only for a specific verification question and record why it was needed;
6. research current external claims after branch creation when the task depends on them;
7. edit only allowed files and stop before scope expansion;
8. create or update a dated prompt/build log for material prompt-assisted changes;
9. name checks, methods, actual results, limitations, and task-specific non-applicability;
10. inspect the complete branch and PR diff;
11. use a PR that closes only the task issue;
12. keep author self-audit, executable checks, AI-assisted review, human review, and merge authorization distinct;
13. require a human **Approve** outcome and separate merge authorization before merge;
14. inspect current status after merge and synchronize only when truth is stale;
15. protect parent issues until their explicit closeout gate is satisfied.

Written policy must not be represented as configured GitHub enforcement.

## Use-boundary baseline

BurnLens Deschutes remains an experimental, non-operational computer vision and GEOINT portfolio project.

Required boundary:

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

BurnLens must not be presented as:

- emergency-response or evacuation guidance;
- incident-command or suppression support;
- an official fire perimeter or hazard product;
- a field-validated or agency-endorsed model;
- a utility-grade operational system;
- a replacement for authoritative public-agency information.

## Source-precedence baseline

**Official sources govern.**

Future work must keep these categories separate:

```text
official/reference sources
reference-derived labels
baseline outputs
model outputs
map overlays
portfolio interpretations
```

BurnLens-derived outputs are the lowest-priority category. When a BurnLens output conflicts with official wildfire, evacuation, emergency-management, hazard, transportation, or incident information, the official source governs and the BurnLens output must be caveated, withheld, marked provisional, or superseded.

## Before-data gate

No Phase Two data or implementation work has begun.

A future task may touch source data, imagery, AOI files, labels, masks, baselines, model inputs, or run outputs only after the repository has a task-specific record set that includes:

1. an issue explicitly authorizing the specific action;
2. a bounded branch and PR contract;
3. source candidate or source record;
4. access method record;
5. license or terms note;
6. format and CRS precheck;
7. AOI record and identifier;
8. provenance or traceability record;
9. artifact registry classification;
10. source-precedence review;
11. use-boundary review;
12. prompt/build log for prompt-assisted changes;
13. README or tracker updates when repository truth changes.

If those records do not exist, stop before touching data and create a planning or control task instead.

## Version, tag, and Release baseline

`VERSIONING.md` governs version identifiers. Version numbers do not imply operational readiness, authority, field validation, emergency readiness, or production stability.

Current state:

```text
Proposed Objective Five baseline tag: v0.0.5-objective-five-traceability
Tag status: proposed only; not created
GitHub Release status: not created
```

A future tag or Release requires a separately authorized issue, applicable release QA, accurate release notes, claim review, and explicit creation authorization.

## Claims baseline

### Safe claim

> BurnLens Deschutes has a documented, reviewable prompt-built development protocol that connects issue-backed authorization, bounded task capsules and branches, selective context loading, prompt/build logging, named verification, task-scoped pull requests, mandatory human review distinct from AI-assisted review, controlled merge authorization, conditional status synchronization, and handoff.

### Caveated claims

| Claim | Required caveat |
|---|---|
| BurnLens has a reproducible development workflow. | The repository-control workflow is documented; no executed data/model/run workflow has been demonstrated. |
| BurnLens has human review controls. | The controls are documented policy and records; configured GitHub enforcement is not claimed. |
| BurnLens is ready for Phase Two planning. | Only a bounded planning/control task may begin; data and implementation remain separately gated. |
| Objective Six is complete. | This means the documented repository-control baseline is complete; it does not mean implementation reliability was demonstrated. |

### Unsupported claims

Do not claim that:

- data, imagery, an AOI, labels, masks, baselines, models, metrics, runs, reports, maps, screenshots, demos, or public outputs exist;
- Phase Two implementation has started;
- an end-to-end CV/GEOINT workflow has been executed or proven reliable;
- GitHub settings enforce the documented protocol;
- AI-assisted review or author self-audit is human approval;
- the proposed tag or a GitHub Release exists;
- BurnLens is official, operational, field-validated, emergency-ready, production-ready, suitable for evacuation or incident-command use, or agency-endorsed.

## Recommended next bounded workstream

### Selected recommendation: Phase Two data-intake preparation

The first Phase Two task should remain planning and control work only.

It should create:

```text
Phase Two parent issue and tracker
Phase Two task sequence and artifact contracts
first source/AOI intake planning issue
allowed-file and stop-condition contract
required source/access/license/CRS/AOI/provenance records list
```

It must not:

```text
download or modify data
select or create a final AOI geometry
create source packages
create labels or masks
run preprocessing
create a baseline or model
run inference
produce maps, screenshots, demos, or public outputs
create a tag or GitHub Release
```

The Phase Two planning task should use Objective Five's before-data controls and Objective Six's issue-to-merge workflow.

## Unselected alternative workstreams

These remain valid but are not selected by this handoff:

1. **Objective Five baseline-tag QA** — review whether `v0.0.5-objective-five-traceability` is eligible for tag creation. It must not create the tag or a GitHub Release without explicit authorization.
2. **Objective Six portfolio-packaging planning** — plan how the documented protocol may be summarized for portfolio use. It must not publish claims, screenshots, maps, demos, or website changes without claim evidence and release QA.

Choosing an alternative requires a new issue and must not be treated as Phase Two authorization.

## Required context for the next workstream

At minimum, load:

```text
README.md
docs/workflows/PROMPT_TO_REPO_SOP.md
AGENTS.md
CONTRIBUTING.md
VERSIONING.md
docs/objective-one/USE_BOUNDARIES.md
docs/objective-one/SOURCE_PRECEDENCE.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_HANDOFF.md
docs/phase-one/objective-five/PROVENANCE_TRACEABILITY_SPEC.md
docs/phase-one/objective-five/RUN_PACKAGE_CONTRACT.md
docs/phase-one/objective-five/ARTIFACT_REGISTRY_SPEC.md
docs/phase-one/objective-five/SOURCE_PRECEDENCE_RELEASE_GATE.md
docs/phase-one/objective-six/OBJECTIVE_SIX_CLOSEOUT.md
docs/phase-one/objective-six/OBJECTIVE_SIX_HANDOFF.md
docs/phase-one/objective-six/PROMPT_BUILT_DEVELOPMENT_PROTOCOL.md
templates/CODEX_TASK_PACKET.md
records/PROMPT_BUILD_LOG.md
```

Then select only the additional Objective Three or Objective Five Tier 1 controls needed for the exact source/AOI planning question.

## Parent closure sequence

After P1O6-SYNC-09 reaches `main`:

1. confirm issue #244 closed;
2. confirm parent #195 remains open;
3. post the final Objective Six completion summary to #195;
4. obtain Drew's explicit manual-closure authorization;
5. close #195 as completed;
6. do not create a tag or GitHub Release as part of parent closure.

## Do not carry forward

Do not carry forward:

- obsolete review-branch, PR-pending, or T09-unmerged language;
- REM-09A, SYNC-09A, T09, or SYNC-09 drafting and connector troubleshooting details;
- the assumption that documented protocol controls prove executed reliability;
- the assumption that Phase Two data work is authorized by this handoff;
- sponsor, partner, field-review, agency-endorsement, or authoritative-field-note expectations;
- any plan to create a tag, GitHub Release, public map, demo, screenshot, or portfolio claim without a separate issue and applicable gates;
- duplicate task packets, prompt-log systems, review authorities, or workflow sources.
