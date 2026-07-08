# BurnLens Release Note Template

## Release identity

| Field | Value |
|---|---|
| Release title |  |
| Release class |  |
| Version / tag |  |
| Release date |  |
| Commit SHA |  |
| Branch |  |
| Parent issue |  |
| Task issue(s) |  |
| Pull request(s) |  |
| Release owner |  |

## Required boundary statement

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

For documentation-only releases, clarify that this warning applies to future BurnLens outputs and that no data/model/map/run/report/public-demo output is being released unless explicitly listed below.

## Source-precedence statement

```text
Official sources govern when BurnLens differs from county, state, federal, fire-service, emergency-management, transportation, air-quality, or incident sources.
```

## Versioning statement

```text
Version numbers, tags, release names, dataset versions, model versions, run IDs, and report versions support traceability. They do not imply operational readiness, official status, field validation, emergency readiness, agency endorsement, production stability, evacuation support, routing support, tactical support, or incident-command support.
```

## Included work

List every artifact included in this release.

| Artifact | Path / ID | Version / identifier | Evidence link | Notes |
|---|---|---|---|---|
|  |  |  |  |  |

## Excluded work

List work that is not included and claims this release does not support.

| Excluded item or claim | Reason excluded | Future gate if applicable |
|---|---|---|
| Data acquisition | Not authorized by this release. | Source/AOI/provenance gates. |
| Imagery download | Not authorized by this release. | Source access and provenance records. |
| Labels, masks, baselines, models, runs, metrics, maps, reports, or public demos | Not included unless explicitly listed above. | Later Phase Two or later objective gates. |
| Operational, official, field-validated, emergency-ready, agency-endorsed, evacuation, routing, tactical, or incident-command claims | Prohibited by BurnLens boundaries. | Not applicable unless project scope changes through a documented governance decision. |

## Artifact inventory

```text
# Example
README.md
docs/phase-one/objective-five/RELEASE_CONTROL.md
templates/RELEASE_NOTE_TEMPLATE.md
records/prompt-build-log/YYYY-MM-DD-task-id.md
```

## Evidence links

| Evidence type | Link / reference |
|---|---|
| Parent issue |  |
| Task issue(s) |  |
| Pull request(s) |  |
| Merge commit(s) |  |
| Version taxonomy | `docs/phase-one/objective-five/VERSION_TAXONOMY.md` |
| Versioning protocol | `VERSIONING.md` |
| Source-precedence control | `docs/objective-one/SOURCE_PRECEDENCE.md` |
| Use-boundary control | `docs/objective-one/USE_BOUNDARIES.md` |
| Prompt/build log |  |

## Release-class checklist

Select one release class.

- [ ] Documentation task PR
- [ ] Status-sync PR
- [ ] Objective baseline
- [ ] Documentation release note
- [ ] App/site release
- [ ] Data package release
- [ ] Model/baseline release
- [ ] Run/report release
- [ ] Public portfolio release

## Tag checklist

Complete before creating a tag.

- [ ] Tag name matches `VERSION_TAXONOMY.md`.
- [ ] Tag target is the intended `main` commit.
- [ ] Relevant task issues and PRs are merged.
- [ ] Current-status artifacts are synchronized.
- [ ] Prompt/build log entries exist where required.
- [ ] Included artifacts are listed.
- [ ] Excluded artifacts are listed.
- [ ] Boundary warning is present.
- [ ] Source-precedence language is present when relevant.
- [ ] Unsupported claims are absent.
- [ ] Release note exists or is created in the same release-control task.

## GitHub release checklist

Complete before publishing a GitHub release.

- [ ] A deployable app/site/package artifact exists, or a separate documented decision authorizes a GitHub release for another class.
- [ ] Release title and tag are correct.
- [ ] Release target commit is correct.
- [ ] Release notes have been manually reviewed.
- [ ] Automatically generated release notes, if used, have been checked for included and excluded scope.
- [ ] Attached assets, if any, are expected and inventoried.
- [ ] Pre-release checkbox decision is documented.
- [ ] Latest-release decision is documented.
- [ ] Boundary and source-precedence statements are present.
- [ ] No unsupported readiness, official-status, or operational claims are present.

## Verification

| Check | Result | Notes |
|---|---|---|
| Diff reviewed |  |  |
| Markdown reviewed |  |  |
| Links reviewed |  |  |
| Boundary language reviewed |  |  |
| Source-precedence language reviewed |  |  |
| Included/excluded artifacts reviewed |  |  |
| Tests run |  |  |
| Tests not run |  |  |

## Do-not-release review

Stop release if any item is checked.

- [ ] Current-status artifacts are stale.
- [ ] Release note says pending/draft but is being treated as final.
- [ ] Tag target is not a reviewed `main` commit.
- [ ] Version class is unclear.
- [ ] Included artifacts are not listed.
- [ ] Excluded work is not listed.
- [ ] Boundary warning is missing.
- [ ] Source-precedence statement is missing.
- [ ] Generated release notes are unchecked.
- [ ] GitHub release would imply latest/stable status without decision.
- [ ] Data/model/map/run/report/public-demo readiness is implied but artifacts do not exist.
- [ ] Operational, official, field-validation, emergency, agency-endorsement, evacuation, routing, tactical, or incident-command claim appears.
- [ ] Source license/terms/provenance uncertainty affects the release.

## Safe claims

```text

```

## Unsupported claims

```text

```

## Handoff

| Field | Value |
|---|---|
| Next task |  |
| Next issue |  |
| Next branch |  |
| Required follow-up |  |
