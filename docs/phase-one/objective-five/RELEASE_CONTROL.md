# Release Control

## Purpose

This document defines BurnLens Deschutes release and tag control for Phase One / Objective Five.

It uses the expanded version taxonomy and the current `VERSIONING.md` protocol to define when a tag, release note, GitHub release, or release-like public statement is allowed, what must be included, and what blocks release.

This is documentation and records work only. It does not create a tag, GitHub release, app/site release, AOI, source record, dataset, label schema, baseline, model, run, report, map, screenshot, public demo, or operational wildfire product.

## Boundary statement

Experimental BurnLens CV/GEOINT portfolio work. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

A BurnLens tag, release note, GitHub release, version number, or baseline label does **not** imply operational readiness, official status, field validation, emergency readiness, agency endorsement, production stability, data readiness, model readiness, map readiness, or fitness for evacuation, routing, tactical, or incident-command decisions.

## Research basis

| Source | What it supports | BurnLens decision |
|---|---|---|
| GitHub Docs, About releases, `https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases` | GitHub releases package software and release notes; releases are deployable software iterations; releases are based on Git tags that mark a specific point in repository history. | Treat GitHub releases as a higher-friction public release class, not the default for every documentation milestone. Use tags and release notes only after explicit gates pass. |
| GitHub Docs, Managing releases in a repository, `https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository` | GitHub release creation includes tag selection or creation, target branch selection, release title/description, optional binary assets, pre-release marking, and latest-release behavior. | Require explicit tag target, release title, included/excluded artifacts, pre-release decision, latest-release decision, and no unsupported readiness claims. |
| GitHub Docs, Automatically generated release notes, `https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes` | Automatically generated release notes summarize merged PRs, contributors, and changelog links; generated notes should be checked to ensure only intended information is included; labels can customize categories and exclusions. | Generated notes may be used only as draft input. BurnLens release notes must be manually reviewed against boundary, source-precedence, included/excluded-work, and claims gates. |
| `VERSIONING.md` | Defines BurnLens version/identifier classes and states version numbers do not imply operational readiness. | Release control must apply the version taxonomy without overclaiming readiness. |
| `docs/phase-one/objective-five/VERSION_TAXONOMY.md` | Defines objective baseline, app/site, AOI, source, dataset, label, baseline, model, run, and report naming rules. | Release/tag names must use the relevant taxonomy pattern and must not blur version classes. |
| `docs/objective-one/SOURCE_PRECEDENCE.md` | Official sources govern when BurnLens differs. | Every release note must include source-precedence language when BurnLens-derived outputs or claims are involved. |
| `docs/objective-one/USE_BOUNDARIES.md` | Defines appropriate and prohibited BurnLens uses. | Every release class must preserve the experimental/non-operational boundary. |

## Release-control principles

1. A release is a claim event, not just a file event.
2. Every release-like action must state what is included and what is excluded.
3. A tag marks a repository state; it does not prove that every planned artifact exists.
4. A GitHub release is treated as public-facing and must pass stricter gates than a task PR.
5. Generated release notes may assist drafting, but they are not sufficient for BurnLens publication.
6. Version numbers and release labels never override source precedence.
7. Official sources govern whenever BurnLens differs from county, state, federal, fire-service, emergency-management, transportation, air-quality, or incident sources.
8. No release may imply data/model/map/run/report/public-demo readiness unless those artifacts exist and are explicitly included.
9. No release may imply operational, official, field-validated, emergency-ready, agency-endorsed, evacuation, routing, tactical, or incident-command use.
10. If status artifacts are stale, release is blocked until they are synchronized.

## Release classes

| Release class | Example | Git tag allowed? | GitHub release allowed? | Purpose | Default status |
|---|---|---:|---:|---|---|
| Documentation task PR | PR #150 | No | No | Merge ordinary documentation/records work. | Normal task workflow only. |
| Status-sync PR | PR #154 | No | No | Reconcile current-status artifacts after a merge. | Normal task workflow only. |
| Objective baseline | `v0.0.5-objective-five-traceability` | Yes, only after objective closeout approval | Usually no; release note document preferred | Mark a reviewed objective-level repo state. | Later closeout task only. |
| Documentation release note | `OBJECTIVE_FIVE_RELEASE_NOTE.md` | Optional if paired with objective baseline | No by default | Summarize completed documentation/control scope. | Allowed after closeout review. |
| App/site release | `burnlens-app-v0.1.0` | Yes | Yes, if deployable app/site artifact exists | Package app/site iteration or website deployment milestone. | Future only. |
| Data package release | `deschutes-aoi01-dataset-v0.1.0` | Future only | Future only | Publish a data package manifest and inventory. | Blocked until data gates exist. |
| Model/baseline release | `burnlens-cv-unet-v0.1.0`; `burnlens-baseline-v0.1.0` | Future only | Future only | Publish model/baseline package and evidence. | Blocked until model/method gates exist. |
| Run/report release | `BL-YYYY-MM-DD-deschutes-aoiXX-mXXX-dXXX`; `run-report-v0.1.0` | Future only | Future only | Publish one run package or report package. | Blocked until run-package gates exist. |
| Public portfolio release | site case study or demo card | Future only | Maybe, only if app/site artifact exists | Public-facing portfolio milestone. | Blocked until claim evidence exists. |

## Tag-control rules

### Allowed tag targets

A BurnLens tag may target only a commit on `main` after the relevant PRs are merged and current-status artifacts are synchronized.

A tag must not target:

- an unmerged task branch;
- an open PR head;
- a commit whose status artifacts are stale;
- a commit whose release note contains unresolved pending language;
- a commit with unsupported official, operational, emergency, field-validation, endorsement, evacuation, routing, tactical, or incident-command claims.

### Naming rules

Use `VERSION_TAXONOMY.md` for tag naming.

| Tag/use case | Pattern | Example |
|---|---|---|
| Objective baseline | `v0.0.N-short-objective-slug` | `v0.0.5-objective-five-traceability` |
| App/site release | `burnlens-app-vMAJOR.MINOR.PATCH` | `burnlens-app-v0.1.0` |
| Data package release | `{aoi-id}-dataset-vMAJOR.MINOR.PATCH` | `deschutes-aoi01-dataset-v0.1.0` |
| Baseline method release | `burnlens-baseline-vMAJOR.MINOR.PATCH` | `burnlens-baseline-v0.1.0` |
| Model release | `burnlens-cv-{architecture}-vMAJOR.MINOR.PATCH` | `burnlens-cv-unet-v0.1.0` |
| Report template release | `run-report-vMAJOR.MINOR.PATCH` | `run-report-v0.1.0` |

Source record IDs and run IDs are not software release tags by default. If they appear in a release, they must be linked as included evidence or artifact IDs, not treated as SemVer compatibility promises.

### Tag approval checklist

Before creating any tag, confirm:

- [ ] tag name matches `VERSION_TAXONOMY.md`;
- [ ] tag target is the intended `main` commit;
- [ ] release class is identified;
- [ ] relevant task issues and PRs are merged;
- [ ] current-status artifacts are synchronized;
- [ ] prompt/build log entries exist where required;
- [ ] included artifacts are listed;
- [ ] excluded artifacts are listed;
- [ ] boundary warning is present;
- [ ] source-precedence language is present when relevant;
- [ ] unsupported claims are absent;
- [ ] release note exists or is created in the same release-control task.

## GitHub release-control rules

GitHub releases are public-facing release objects and should be used only when the release class justifies them.

### GitHub release allowed

A GitHub release may be allowed when:

- an app/site artifact, package, or other release-ready artifact exists;
- the release note is complete and reviewed;
- the tag target is approved;
- included and excluded artifacts are explicit;
- the release is marked as pre-release when the artifact is not production-ready or may be unstable;
- the `latest` release setting is explicitly reviewed;
- attached assets, if any, are inventoried and expected;
- boundary, source-precedence, and claims checks pass.

### GitHub release blocked

A GitHub release is blocked when:

- the release is documentation-only and a release note document is sufficient;
- no deployable app/site/package artifact exists;
- generated release notes have not been manually reviewed;
- included/excluded artifacts are ambiguous;
- the release could imply data/model/map/public-output readiness that does not exist;
- the release could imply official, operational, emergency, field-validated, or agency-endorsed status;
- the release would be labeled latest without an explicit decision;
- release assets are missing, unexpected, or not inventoried;
- source-precedence conflicts are unresolved.

## Release-note requirements

Every BurnLens release note or baseline note must include:

| Required section | Purpose |
|---|---|
| Release identity | Release class, version/tag, date, commit, branch, PRs, issues. |
| Included work | Exact artifacts included in the release. |
| Excluded work | Work that is not included and claims that are not supported. |
| Boundary statement | Experimental/non-operational warning. |
| Source-precedence statement | Official sources govern. |
| Versioning statement | Version numbers do not imply readiness. |
| Artifact inventory | Files, templates, records, packages, or assets included. |
| Evidence links | Issues, PRs, commits, source records, manifests, run IDs, or reports as applicable. |
| Verification | Checks run and checks not run. |
| Do-not-use language | Prohibited emergency, operational, evacuation, routing, tactical, or incident-command uses. |
| Handoff | Next task or next release-control action. |

Use `templates/RELEASE_NOTE_TEMPLATE.md` for future release notes.

## Do-not-release triggers

Stop release or tag creation if any trigger below is true.

| Trigger | Required action |
|---|---|
| Current-status artifacts are stale. | Run a status-sync PR first. |
| Release note says pending/draft but is being treated as final. | Revise before release. |
| Tag target is not a reviewed `main` commit. | Retarget or defer. |
| Version class is unclear. | Reconcile with `VERSION_TAXONOMY.md`. |
| Included artifacts are not listed. | Add inventory. |
| Excluded work is not listed. | Add exclusion statement. |
| Boundary warning is missing. | Add required warning. |
| Source-precedence statement is missing. | Add official-sources-govern language. |
| Generated release notes are unchecked. | Review and edit manually. |
| GitHub release would imply latest/stable status without decision. | Mark as pre-release or defer. |
| Data/model/map/run/report/public-demo readiness is implied but artifacts do not exist. | Remove claim or defer release. |
| Operational, official, field-validation, emergency, agency-endorsement, evacuation, routing, tactical, or incident-command claim appears. | Remove claim and re-audit. |
| Source license/terms/provenance uncertainty affects the release. | Defer until provenance/source review resolves it. |
| Security-sensitive release claim appears. | Defer to appropriate advisory/security workflow. |

## Source-precedence release gate

Before any release-like action, check whether the release references wildfire, hazard, emergency, transportation, road, air-quality, incident, or official source information.

If yes, the release note must state:

```text
Official sources govern when BurnLens differs from county, state, federal, fire-service, emergency-management, transportation, air-quality, or incident sources.
```

If a BurnLens artifact conflicts with an official source, the release must either:

1. exclude the conflicting artifact;
2. mark the artifact as superseded/degraded;
3. state the conflict explicitly and defer publication;
4. publish only if the release class permits a documented limitation and the limitation is prominent.

## Boundary release gate

Every release note must include:

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

For documentation-only releases, phrase the boundary as applying to future BurnLens outputs, not as a claim that outputs already exist.

## Generated release notes rule

Automatically generated GitHub release notes may be used only as a draft input.

Before publication:

- review generated notes for included and excluded scope;
- remove irrelevant PRs, labels, or contributor sections if they obscure the release claim;
- add BurnLens boundary language;
- add source-precedence language;
- add unsupported-claims language;
- verify the notes do not imply readiness that does not exist;
- preserve the manually reviewed release note in the repo when the release is project-significant.

## Objective baseline release rule

Objective baseline tags are allowed only from objective closeout or release-note tasks.

For Objective Five, the proposed future baseline is:

```text
v0.0.5-objective-five-traceability
```

That tag is not created by P1O5-T04. It should be considered only during P1O5-T12 closeout after Objective Five artifacts are merged and current-status artifacts are synchronized.

## App/site release rule

An app/site release may use:

```text
burnlens-app-v0.1.0
```

Only create an app/site release if an app/site artifact exists and the release note links to:

- repository commit;
- app/site repository or deployment record;
- versioned data/model/run artifacts displayed by the app, if any;
- boundary warning;
- source-precedence statement;
- claim-evidence links.

If app/site release content is experimental or unstable, mark it as pre-release or use documentation-only publication until a later release-control decision permits broader release.

## Data, model, run, and report release rule

Data, model, run, and report releases are blocked until their respective specs exist and are satisfied.

| Release type | Required future gates before release |
|---|---|
| Data package | AOI version, source records, access logs, CRS/format checks, provenance manifest, dataset manifest, checksums where files exist. |
| Label schema | Label schema record, class definitions, examples/non-examples, QA expectations, dataset links if used. |
| Baseline method | Method record, input/output contract, config, dataset link, limitations. |
| Model | Model card, dataset version, label schema version, training config, weights checksum if weights exist, metrics, limitations. |
| Run package | Run ID, run manifest, output inventory, source links, method/model versions, warnings, limitations. |
| Report package | Report version, run ID, evidence links, source-precedence note, boundary warning, claim checks. |

## Release approval roles

For this portfolio workflow, approval means a reviewed repo record exists, not external agency endorsement.

| Approval level | Required evidence |
|---|---|
| Task PR approval | PR merged with correct close keyword and boundary checks. |
| Status-sync approval | Current-status artifacts updated after merge. |
| Objective baseline approval | Objective closeout, release note, prompt log, tracker, and parent issue update complete. |
| GitHub release approval | Release-control checklist complete and explicit user authorization to publish a GitHub release. |

No approval level creates official status or agency endorsement.

## Acceptance criteria

| Check | Status | Notes |
|---|---|---|
| Release classes defined. | Satisfied | Release classes table. |
| Tag eligibility defined. | Satisfied | Tag-control rules and approval checklist. |
| Release-note requirements defined. | Satisfied | Release-note requirements section and template. |
| Do-not-release triggers defined. | Satisfied | Trigger table. |
| Boundary gate included. | Satisfied | Boundary release gate. |
| Source-precedence gate included. | Satisfied | Source-precedence release gate. |
| Tags/releases cannot imply missing readiness. | Satisfied | Blocked release and readiness language throughout. |
| No data/model/map/public-output work created. | Satisfied | Documentation only. |

## Handoff

P1O5-T05 should use this release-control spec, `VERSION_TAXONOMY.md`, and `VERSIONING.md` to define provenance traceability. It should explain how source, activity, artifact, and claim records connect before future data/model/run/report releases can be considered.
