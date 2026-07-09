# Release QA Checklist

## Purpose

This checklist defines what BurnLens Deschutes must verify before any objective baseline, future dataset release, future model/baseline release, future run/report release, or future public demo release is approved.

It is specific to BurnLens release-control, source-precedence, claim-traceability, provenance, run-package, artifact-registry, and use-boundary rules. It is not a generic software QA checklist.

This is documentation and records work only. It does not create a release, tag, GitHub release, run report, run package, dataset release, model release, public demo, screenshot, map, completed claim record, source-precedence review record, source record, AOI record, data product, model product, or operational wildfire product.

## Boundary statement

Experimental BurnLens CV/GEOINT portfolio work. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

Passing this checklist does **not** make BurnLens official, operational, field-validated, emergency-ready, agency-endorsed, production-stable, or suitable for evacuation, routing, road-closure, tactical, incident-command, hazard-confirmation, or public-safety decisions.

## Reuse rule

Use this checklist for release-like actions, including:

- objective baseline release notes;
- objective baseline tag proposals;
- future dataset package release candidates;
- future model or baseline package release candidates;
- future run/report release candidates;
- future app/site or public demo release candidates;
- public screenshots, website cards, case-study assets, report figures, or slide/demo assets that use BurnLens-derived output.

Use one checklist instance per release candidate. If a row is not applicable, mark `N/A` and state why. Do not delete rows.

## Release candidate identity

| Field | Value |
|---|---|
| Release QA ID | `RELQA-YYYY-NNN` |
| Review date | `YYYY-MM-DD` |
| Reviewer | `[person / role / tool-assisted review]` |
| Release class | `objective-baseline | documentation-release-note | dataset-package | model-baseline-package | run-report-package | app-site-release | public-demo-release | public-portfolio-release | other` |
| Candidate title | `[title]` |
| Candidate version/tag/run/report ID | `[version/tag/run/report ID]` |
| Candidate commit SHA | `[commit SHA]` |
| Candidate branch | `[branch]` |
| Candidate PR | `#[PR]` |
| Related issue(s) | `#[issue]` |
| Release note path | `[path]` |
| Final release QA decision | `approved | approved-with-limitations | blocked | not applicable` |

## Required workflow checks

| Check | Status | Evidence path / ID | Notes |
|---|---|---|---|
| [ ] Issue exists. | `pass | fail | N/A` | `#[issue]` | Required for release candidate or release-control task. |
| [ ] Branch exists. | `pass | fail | N/A` | `[branch]` | Required before PR review. |
| [ ] PR exists. | `pass | fail | N/A` | `#[PR]` | Required for repo artifact changes. |
| [ ] PR closes only the intended task issue. | `pass | fail | N/A` | PR body | Parent issue must not close accidentally. |
| [ ] Prompt/build log exists where required. | `pass | fail | N/A` | prompt log path | Required for prompt-assisted file creation or material edits. |
| [ ] Files changed are allowed. | `pass | fail | N/A` | PR diff / artifact contract | All changes must match scope or be justified. |
| [ ] Current-status artifacts are synchronized. | `pass | fail | N/A` | README / tracker / log index | Stale status blocks release. |
| [ ] Review target is on an allowed commit/branch. | `pass | fail | N/A` | commit SHA / branch | Tags and releases must target reviewed `main` commits only. |

## Release-class checks

| Check | Status | Evidence path / ID | Notes |
|---|---|---|---|
| [ ] Release class is identified. | `pass | fail | N/A` | release note | Objective baseline, dataset, model/baseline, run/report, app/site, public demo, or portfolio release. |
| [ ] Release class is allowed now. | `pass | fail | N/A` | release-control artifact | Future data/model/map/public-demo release classes remain blocked until authorized. |
| [ ] Tag eligibility is reviewed. | `pass | fail | N/A` | release note / tag checklist | Documentation task PRs and status-sync PRs do not get tags. |
| [ ] GitHub release eligibility is reviewed. | `pass | fail | N/A` | release note / release-control decision | GitHub releases require public-release justification and stricter gates. |
| [ ] `latest` or stable implication is reviewed if GitHub release is considered. | `pass | fail | N/A` | release decision | Do not imply latest/stable without explicit decision. |
| [ ] Pre-release status is reviewed if relevant. | `pass | fail | N/A` | release decision | Required for non-production or unstable future artifacts. |

## Versioning and reproducibility checks

| Check | Status | Evidence path / ID | Notes |
|---|---|---|---|
| [ ] Version fields are present. | `pass | fail | N/A` | release note / manifest / report | Required where release-like action uses versioned artifacts. |
| [ ] Version/tag name matches `VERSION_TAXONOMY.md`. | `pass | fail | N/A` | version/tag | Required before objective baseline, app/site, dataset, model, baseline, or report release. |
| [ ] Commit SHA is recorded. | `pass | fail | N/A` | release note / manifest | Required. |
| [ ] Source, AOI, dataset, label, method, model, run, and report IDs are recorded where relevant. | `pass | fail | N/A` | manifests / reports | Required for future data/model/run/public releases. |
| [ ] Version labels do not imply readiness. | `pass | fail | N/A` | public copy / release note | Versions do not prove operational, official, data, model, map, or public-demo readiness. |
| [ ] Reproducibility checklist is complete or linked. | `pass | fail | N/A` | `REPRO-YYYY-NNN` / checklist path | Required before release-like action. |

## Provenance and artifact inventory checks

| Check | Status | Evidence path / ID | Notes |
|---|---|---|---|
| [ ] Provenance fields are present where relevant. | `pass | fail | N/A` | provenance manifest / traceability record | Required for source/data/model/run/output/public artifacts. |
| [ ] Source records and access logs are linked where relevant. | `pass | fail | N/A` | source/access IDs | Required before source/data/run/model/output claims. |
| [ ] Format/CRS prechecks are linked where relevant. | `pass | fail | N/A` | precheck IDs | Required for geospatial processing or data-readiness claims. |
| [ ] Method/tool/model versions are linked where relevant. | `pass | fail | N/A` | method/model records | Required for baseline/model/run outputs. |
| [ ] Output inventory exists where outputs exist. | `pass | fail | N/A` | output inventory path | Every output path, type, checksum, public status, and warning requirement must be listed. |
| [ ] Checksums or checksum plans are recorded where files exist. | `pass | fail | N/A` | manifest / inventory | Use `sha256` unless later approved otherwise. |
| [ ] Artifact registry status is reviewed where relevant. | `pass | fail | N/A` | registry entry / spec | Templates and completed records must stay distinct. |
| [ ] Official/reference sources and BurnLens-derived outputs are separated. | `pass | fail | N/A` | release note / registry / artifact | Required source separation rule. |

## Source-precedence release gate

| Check | Status | Evidence path / ID | Notes |
|---|---|---|---|
| [ ] Official sources govern. | `pass | fail | N/A` | release note / public artifact | Required when wildfire, hazard, emergency, transportation, road, air-quality, incident, or official-source context appears. |
| [ ] Source hierarchy is preserved. | `pass | fail | N/A` | source-precedence review / run report | BurnLens-derived outputs remain lowest priority. |
| [ ] Source-precedence status is recorded. | `pass | fail | N/A` | status / evidence record | Missing status blocks public use. |
| [ ] Public artifact status is recorded where relevant. | `pass | fail | N/A` | `normal | provisional | degraded | superseded | withheld` | Required for BurnLens-derived public artifacts. |
| [ ] Required run-report source-precedence language is included where a conflict exists. | `pass | fail | N/A` | run report | Use the exact pattern from `SOURCE_PRECEDENCE.md` / T09 gate. |
| [ ] Conflicts with official or higher-priority sources are resolved. | `pass | fail | N/A` | source-precedence note | Exclude, caveat, supersede, degrade, or withhold. |
| [ ] `withheld` artifacts are not released. | `pass | fail | N/A` | release note / decision | Required. |
| [ ] `superseded` artifacts are not presented as active/current. | `pass | fail | N/A` | release note / public copy | Historical/internal use only unless explicitly framed. |
| [ ] `provisional` or `degraded` artifacts have prominent limitations. | `pass | fail | N/A` | release note / public artifact | Required. |
| [ ] Outputs that cannot be caveated responsibly are blocked. | `pass | fail | N/A` | release decision | Required. |

Required source-precedence statement when relevant:

```text
Official sources govern when BurnLens differs from county, state, federal, fire-service, emergency-management, transportation, air-quality, or incident sources.
```

## Use-boundary and public-language checks

| Check | Status | Evidence path / ID | Notes |
|---|---|---|---|
| [ ] Use boundaries are preserved. | `pass | fail | N/A` | release note / public copy | Required. |
| [ ] Not emergency guidance review is complete. | `pass | fail | N/A` | release note / public copy | Must not imply emergency guidance. |
| [ ] Not official wildfire information review is complete. | `pass | fail | N/A` | release note / public copy | Must not imply official wildfire information. |
| [ ] Not evacuation guidance review is complete. | `pass | fail | N/A` | release note / public copy | Must not imply evacuation support. |
| [ ] Not routing or road-closure guidance review is complete. | `pass | fail | N/A` | release note / public copy | Must not imply routing/closure authority. |
| [ ] Not tactical or incident-command support review is complete. | `pass | fail | N/A` | release note / public copy | Must not imply operational fire use. |
| [ ] Not field-validated review is complete. | `pass | fail | N/A` | release note / public copy | Must not imply field validation. |
| [ ] Not agency-endorsed review is complete. | `pass | fail | N/A` | release note / public copy | Must not imply endorsement. |
| [ ] No unsupported claims are introduced. | `pass | fail | N/A` | claim evidence / public copy | Claims must not exceed evidence. |

Required full warning when BurnLens-derived output or public-facing wildfire context is involved:

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

For documentation-only release notes, phrase the warning as applying to future BurnLens outputs rather than implying outputs already exist.

## Release-note checks

| Check | Status | Evidence path / ID | Notes |
|---|---|---|---|
| [ ] Release note exists where release-like action occurs. | `pass | fail | N/A` | release note path | Required for objective baseline, dataset, model, run/report, app/site, public demo, or portfolio release. |
| [ ] Release note states what is included and excluded. | `pass | fail | N/A` | release note path | Required. |
| [ ] Included artifacts are listed exactly. | `pass | fail | N/A` | release note path | Avoid broad claims. |
| [ ] Excluded artifacts and unsupported claims are listed. | `pass | fail | N/A` | release note path | Required to prevent overclaiming. |
| [ ] Boundary statement is included. | `pass | fail | N/A` | release note path | Required. |
| [ ] Source-precedence statement is included where relevant. | `pass | fail | N/A` | release note path | Required. |
| [ ] Versioning statement is included. | `pass | fail | N/A` | release note path | Versions do not imply readiness. |
| [ ] Artifact inventory is included or linked. | `pass | fail | N/A` | inventory / release note | Required. |
| [ ] Evidence links are included. | `pass | fail | N/A` | issue/PR/commit/source/manifest/run/report IDs | Required. |
| [ ] Verification performed and checks not run are included. | `pass | fail | N/A` | release note path | Required. |
| [ ] Do-not-use language is included. | `pass | fail | N/A` | release note path | Required for public-facing artifacts. |
| [ ] Handoff or next release-control action is stated. | `pass | fail | N/A` | release note path | Required. |

## Release-class addenda

### Objective baseline QA

| Check | Status | Evidence path / ID | Notes |
|---|---|---|---|
| [ ] Objective baseline is authorized by closeout task. | `pass | fail | N/A` | closeout issue/PR | Objective baseline tags require explicit approval. |
| [ ] All task and sync issues needed for the objective are resolved or deferred. | `pass | fail | N/A` | issue list | Required. |
| [ ] Objective tracker, README, and prompt-log index are current. | `pass | fail | N/A` | current-status artifacts | Stale status blocks baseline. |
| [ ] Objective release note states documentation/control scope only unless otherwise authorized. | `pass | fail | N/A` | release note | Required. |
| [ ] Tag is not created unless explicitly authorized. | `pass | fail | N/A` | tag decision | Required. |

### Future dataset release QA

| Check | Status | Evidence path / ID | Notes |
|---|---|---|---|
| [ ] Dataset release is authorized. | `pass | fail | N/A` | issue/contract | Objective Five does not authorize dataset release. |
| [ ] Dataset source lineage is complete. | `pass | fail | N/A` | source/access/precheck/provenance records | Required. |
| [ ] License/terms review passes. | `pass | fail | N/A` | source/access records | Unresolved terms block release. |
| [ ] Dataset version and manifest exist. | `pass | fail | N/A` | dataset manifest | Required. |
| [ ] Data package does not blur official/reference and BurnLens-derived categories. | `pass | fail | N/A` | registry / release note | Required. |

### Future model or baseline release QA

| Check | Status | Evidence path / ID | Notes |
|---|---|---|---|
| [ ] Model/baseline release is authorized. | `pass | fail | N/A` | issue/contract | Objective Five does not authorize model release. |
| [ ] Dataset and label lineage are complete. | `pass | fail | N/A` | dataset/label records | Required. |
| [ ] Method/model version is recorded. | `pass | fail | N/A` | version/method record | Required. |
| [ ] Model card or baseline method record exists. | `pass | fail | N/A` | model card / method record | Required. |
| [ ] Metrics claims are backed by metrics records. | `pass | fail | N/A` | metrics record | Metrics do not imply operational readiness. |
| [ ] Limitations are included. | `pass | fail | N/A` | model card / release note | Required. |
| [ ] No operational, emergency-ready, field-validated, agency-endorsed, evacuation, routing, tactical, or incident-command claim appears. | `pass | fail | N/A` | public copy / release note | Required. |

### Future run/report or public demo QA

| Check | Status | Evidence path / ID | Notes |
|---|---|---|---|
| [ ] Run/report/public demo release is authorized. | `pass | fail | N/A` | issue/contract | Objective Five does not authorize public demo release. |
| [ ] Run package gates pass. | `pass | fail | N/A` | run manifest / run package | Required for run-derived artifacts. |
| [ ] Every public screenshot, map export, or figure references a run ID. | `pass | fail | N/A` | caption / metadata | Required. |
| [ ] Public artifact status is visible. | `pass | fail | N/A` | normal/provisional/degraded/superseded/withheld | Required. |
| [ ] Warning language is visible in or near public artifact. | `pass | fail | N/A` | screenshot/site/report | Required. |
| [ ] Claim evidence link exists. | `pass | fail | N/A` | claim evidence record | Required for public-facing claims. |
| [ ] Public demo copy remains portfolio/demo language, not operational wildfire guidance. | `pass | fail | N/A` | public copy | Required. |

## Automatic blockers

Release QA is blocked if any of the following are true:

- issue, branch, or PR evidence is missing where required;
- prompt/build log is missing where required;
- changed files are outside allowed scope without explanation;
- version class is unclear;
- required version fields are missing;
- provenance fields are missing where relevant;
- current-status artifacts are stale;
- release note does not state what is included and excluded;
- source-precedence language is missing where relevant;
- source-precedence conflict is unresolved;
- public artifact status is missing where relevant;
- output is `withheld`;
- output is `superseded` but presented as current;
- output cannot be caveated responsibly;
- official/reference source and BurnLens-derived output categories are blurred;
- public claim lacks evidence;
- public artifact lacks required warning;
- release implies data/model/map/run/report/public-demo readiness that does not exist or is not authorized;
- release implies official, operational, field-validated, emergency-ready, agency-endorsed, evacuation, routing, road-closure, tactical, or incident-command use.

## Final QA decision

| Field | Value |
|---|---|
| Release QA decision | `approved | approved-with-limitations | blocked | not applicable` |
| Required limitation(s) | `[text]` |
| Required exclusions | `[artifacts/claims to exclude]` |
| Required follow-up issue(s) | `#[issue] | none` |
| Release/tag/GitHub release allowed? | `yes | no | not applicable` |
| Reviewer notes | `[notes]` |

## Handoff

If this checklist blocks a candidate, do not publish, tag, create a GitHub release, demo, export, attach, or promote the artifact. Revise the candidate or open a follow-up issue until all BurnLens-specific release, source-precedence, evidence, use-boundary, and claim checks pass.
