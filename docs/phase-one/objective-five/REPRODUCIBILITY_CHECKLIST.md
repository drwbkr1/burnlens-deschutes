# Reproducibility Checklist

## Purpose

This checklist defines what BurnLens Deschutes must confirm before treating an objective baseline, future dataset release, model/baseline release, run/report release, or public demo release as reproducible enough for review.

It is specific to BurnLens CV/GEOINT portfolio work. It is not a generic software QA checklist.

This is documentation and records work only. It does not create an objective baseline, dataset release, model release, run package, public demo, tag, GitHub release, source record, AOI record, data product, model product, map product, screenshot, completed claim record, or source-precedence review record.

## Boundary statement

Experimental BurnLens CV/GEOINT portfolio work. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

Passing this checklist does **not** mean BurnLens is official, operational, field-validated, emergency-ready, agency-endorsed, production-stable, or suitable for evacuation, routing, road-closure, tactical, incident-command, hazard-confirmation, or public-safety decisions.

## Reuse rule

Copy this checklist into later PR descriptions, release notes, run reports, dataset package reviews, model package reviews, or objective closeout reviews when a reproducibility decision is needed.

Use one checklist instance per release candidate or review target.

If a row is not applicable, mark it `N/A` and state why. Do not delete rows.

## Review target

| Field | Value |
|---|---|
| Review ID | `REPRO-YYYY-NNN` |
| Review date | `YYYY-MM-DD` |
| Reviewer | `[person / role / tool-assisted review]` |
| Release/review class | `objective-baseline | dataset-release | model-release | run-report-release | public-demo-release | documentation-only | other` |
| Candidate title | `[title]` |
| Candidate branch | `[branch]` |
| Candidate PR | `#[PR]` |
| Candidate commit SHA | `[commit SHA]` |
| Related issue(s) | `#[issue]` |
| Related release note | `[path or not created]` |
| Final reproducibility decision | `pass | pass-with-limitations | blocked | not applicable` |

## Minimum workflow evidence

These checks apply to every BurnLens reproducibility review.

| Check | Status | Evidence path / ID | Notes |
|---|---|---|---|
| [ ] Issue exists. | `pass | fail | N/A` | `#[issue]` | Required for all task-scoped changes. |
| [ ] Branch exists. | `pass | fail | N/A` | `[branch]` | Must be traceable to the task or release candidate. |
| [ ] PR exists. | `pass | fail | N/A` | `#[PR]` | Required before merge/release review. |
| [ ] Artifact contract exists. | `pass | fail | N/A` | issue comment / task packet | Must define primary artifacts, allowed files, forbidden work, and acceptance. |
| [ ] Prompt/build log exists where required. | `pass | fail | N/A` | `records/prompt-build-log/...` | Required when prompt assistant or Codex materially creates or edits files. |
| [ ] Files changed are allowed. | `pass | fail | N/A` | PR diff / artifact contract | Changed files must match the task contract or be explicitly justified. |
| [ ] Parent issue is not closed by task PR. | `pass | fail | N/A` | PR body | Task PRs close only the task issue unless explicitly authorized. |
| [ ] Current-status artifacts are synchronized. | `pass | fail | N/A` | README / tracker / prompt log index | Stale status blocks release-like action. |

## Version and identifier evidence

Use the version class that matches the candidate. Do not treat every identifier as SemVer.

| Check | Status | Evidence path / ID | Notes |
|---|---|---|---|
| [ ] Version fields are present. | `pass | fail | N/A` | `[path / ID]` | Required for release-like candidates. |
| [ ] Version class is identified. | `pass | fail | N/A` | `objective baseline | app/site | source | AOI | dataset | labels | baseline | model | run | report | claim` | Must match `VERSION_TAXONOMY.md`. |
| [ ] Commit SHA is recorded. | `pass | fail | N/A` | `[commit SHA]` | Required for reproducibility and release traceability. |
| [ ] Repository branch or tag target is recorded. | `pass | fail | N/A` | `[branch/tag]` | Tags must target reviewed `main` commits only. |
| [ ] AOI version is recorded where relevant. | `pass | fail | N/A` | `[AOI ID/version]` | Required for data, run, report, map, screenshot, or public demo candidates. |
| [ ] Dataset/source version is recorded where relevant. | `pass | fail | N/A` | `[dataset/source version]` | Required for dataset, model, run, report, map, screenshot, or public demo candidates. |
| [ ] Method/model/baseline version is recorded where relevant. | `pass | fail | N/A` | `[method/model/baseline version]` | Required for processing, baseline, model, run, or output candidates. |
| [ ] Run ID is recorded where relevant. | `pass | fail | N/A` | `BL-YYYY-MM-DD-deschutes-aoiXX-mXXX-dXXX` | Required for run/report/map/screenshot/public-demo artifacts derived from a run. |
| [ ] Report version is recorded where relevant. | `pass | fail | N/A` | `[report version]` | Required when a report is reviewed or released. |
| [ ] Version number does not imply readiness. | `pass | fail | N/A` | release note / README / candidate artifact | Must not imply operational, official, production, data, model, or map readiness unless evidence exists and release gates allow it. |

## Provenance evidence

Use this section when the candidate involves sources, AOIs, data, methods, outputs, runs, reports, screenshots, or public claims.

| Check | Status | Evidence path / ID | Notes |
|---|---|---|---|
| [ ] Provenance fields are present where relevant. | `pass | fail | N/A` | `[path / ID]` | Required for source/data/model/run/output/public candidates. |
| [ ] Entity ID is recorded. | `pass | fail | N/A` | `[entity ID/path]` | Source, file, output, report, claim, or public artifact. |
| [ ] Activity ID is recorded when an action occurs. | `pass | fail | N/A` | `[activity ID]` | Access, precheck, processing, review, report generation, publication, or release. |
| [ ] Agent/tool is recorded. | `pass | fail | N/A` | `[agent/tool]` | Person, provider, script, model, prompt assistant, or software tool. |
| [ ] Source record is linked where relevant. | `pass | fail | N/A` | `SRC-YYYY-NNN` | Required for source/data/run/model/output/public-source claims. |
| [ ] Access record is linked where relevant. | `pass | fail | N/A` | `ACCESS-YYYY-NNN` | Required before file use. |
| [ ] Format/CRS precheck is linked where relevant. | `pass | fail | N/A` | `PRECHECK-YYYY-NNN` | Required before geospatial processing. |
| [ ] Provenance manifest or traceability record exists where relevant. | `pass | fail | N/A` | `MANIFEST-YYYY-NNN / TRACE-YYYY-NNN` | Required for downstream use. |
| [ ] Processing timestamp is recorded where processing/review occurs. | `pass | fail | N/A` | `[UTC timestamp]` | Required for run/report/release review activities. |
| [ ] Output file path is recorded where output exists. | `pass | fail | N/A` | `[path]` | Required for data/model/run/output candidates. |
| [ ] Checksum plan or checksum is recorded where files exist. | `pass | fail | N/A` | `[sha256 / plan]` | Use `not created`, `not authorized`, `pending`, or `not applicable`; never leave blank. |
| [ ] Downstream claims link to upstream evidence. | `pass | fail | N/A` | `[claim evidence path]` | Required for public claims. |

## Run package reproducibility evidence

Use this section for future run, report, screenshot, map, public-demo, model-output, or exposure-summary candidates.

| Check | Status | Evidence path / ID | Notes |
|---|---|---|---|
| [ ] Run package exists only if authorized. | `pass | fail | N/A` | `/runs/[run-id]/` | Objective Five does not authorize run package creation. |
| [ ] Run manifest exists where a run exists. | `pass | fail | N/A` | `runs/[run-id]/run_manifest.json` | Required for future runs. |
| [ ] Source links file exists where a run exists. | `pass | fail | N/A` | `runs/[run-id]/source_links.md` | Must connect source records, access logs, terms, CRS/prechecks. |
| [ ] Processing log exists where a run exists. | `pass | fail | N/A` | `runs/[run-id]/processing_log.md` | Must record tools, parameters, timestamps, errors, rerun notes, exclusions. |
| [ ] Output inventory exists where outputs exist. | `pass | fail | N/A` | `runs/[run-id]/output_inventory.md` | Must list every output path, media type, checksum plan/status, public status. |
| [ ] Warnings file exists where a run exists. | `pass | fail | N/A` | `runs/[run-id]/warnings.md` | Must include BurnLens warning, source-precedence status, limitations, prohibited uses. |
| [ ] Run report exists before report/public use. | `pass | fail | N/A` | `runs/[run-id]/run_report.md` | Required before report/public artifact claims. |
| [ ] Every public screenshot references a run ID. | `pass | fail | N/A` | `[screenshot path / caption]` | Required for screenshots, website images, report figures, demo cards. |
| [ ] Future output files are not implied unless created and authorized. | `pass | fail | N/A` | output inventory / release note | `prediction_mask.tif`, polygons, exposure summary, or map export cannot be implied by template-only work. |

## Source-precedence and use-boundary evidence

These checks are required for every candidate that touches wildfire, hazard, emergency, transportation, road, air-quality, incident, official-source context, or BurnLens-derived output.

| Check | Status | Evidence path / ID | Notes |
|---|---|---|---|
| [ ] Official sources govern. | `pass | fail | N/A` | release note / run report / public artifact | Required statement must be present where relevant. |
| [ ] Source hierarchy is preserved. | `pass | fail | N/A` | source-precedence review / run report | BurnLens-derived outputs remain lowest priority. |
| [ ] Source-precedence status is recorded. | `pass | fail | N/A` | `[status]` | Use existing statuses or release gate statuses as applicable. |
| [ ] Public artifact status is recorded where relevant. | `pass | fail | N/A` | `normal | provisional | degraded | superseded | withheld` | Missing status blocks public use. |
| [ ] Conflict handling is recorded where relevant. | `pass | fail | N/A` | source-precedence note / review | Conflicts with official or higher-priority sources must be excluded, caveated, superseded, or withheld. |
| [ ] Outputs that cannot be caveated responsibly are blocked. | `pass | fail | N/A` | release QA decision | Required for fire, evacuation, hazard, road, incident, or public-safety context. |
| [ ] Use boundaries are preserved. | `pass | fail | N/A` | release note / artifact | Must preserve experimental/non-operational boundary. |
| [ ] Not emergency guidance review is complete. | `pass | fail | N/A` | release note / artifact | Artifact must not imply emergency guidance. |
| [ ] Not official wildfire information review is complete. | `pass | fail | N/A` | release note / artifact | Artifact must not imply official wildfire information. |
| [ ] Evacuation/routing/tactical/incident-command language is absent or explicitly prohibited. | `pass | fail | N/A` | release note / artifact | Required for public-facing artifacts. |

Required full warning when BurnLens-derived output or public-facing wildfire context is involved:

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

## Claim and release-note evidence

| Check | Status | Evidence path / ID | Notes |
|---|---|---|---|
| [ ] No unsupported claims are introduced. | `pass | fail | N/A` | PR/release note/claim record | Claims must not exceed evidence. |
| [ ] Claim type is identified where public-facing. | `pass | fail | N/A` | claim evidence record | Scope, source, data-readiness, model, map/output, portfolio, or mixed. |
| [ ] Claim evidence link exists where public-facing. | `pass | fail | N/A` | `CLAIM-YYYY-NNN` / evidence template | Public claims require linked evidence. |
| [ ] No data/model/map work is implied unless authorized. | `pass | fail | N/A` | release note / README / artifact | Templates and plans must not imply outputs exist. |
| [ ] Release note states what is included and excluded. | `pass | fail | N/A` | release note path | Required for every release-like action. |
| [ ] Release note lists unsupported claims. | `pass | fail | N/A` | release note path | Required to prevent overclaiming. |
| [ ] Release note links evidence. | `pass | fail | N/A` | issue/PR/commit/source/manifest/run/report IDs | Evidence differs by release class. |
| [ ] Release note includes verification performed and checks not run. | `pass | fail | N/A` | release note path | Do not claim tests passed unless they ran. |

## Release-class addenda

### Objective baseline reproducibility

Use for objective closeout or objective baseline tag candidates.

| Check | Status | Evidence path / ID | Notes |
|---|---|---|---|
| [ ] All objective task issues are closed or explicitly deferred. | `pass | fail | N/A` | issue list | Required before objective baseline. |
| [ ] Objective tracker and README are current. | `pass | fail | N/A` | README / tracker | Stale status blocks baseline. |
| [ ] Objective release note exists. | `pass | fail | N/A` | release note path | Must state included/excluded work and limitations. |
| [ ] Objective baseline version matches taxonomy. | `pass | fail | N/A` | `v0.0.N-short-objective-slug` | Tag creation still requires explicit authorization. |
| [ ] No data/model/map readiness is implied by documentation baseline. | `pass | fail | N/A` | release note / README | Objective Five is control documentation unless later authorization exists. |

### Future dataset release reproducibility

Use only when dataset work is authorized in a later phase.

| Check | Status | Evidence path / ID | Notes |
|---|---|---|---|
| [ ] Dataset release is authorized by issue/contract. | `pass | fail | N/A` | `#[issue]` | Dataset work is not authorized by Objective Five. |
| [ ] Source records and access logs are complete. | `pass | fail | N/A` | source/access IDs | Required before dataset release. |
| [ ] License/terms status is recorded. | `pass | fail | N/A` | source record / access log | Unresolved terms block release. |
| [ ] CRS/format prechecks pass or limitations are documented. | `pass | fail | N/A` | precheck IDs | Required for geospatial data. |
| [ ] Dataset version and manifest are present. | `pass | fail | N/A` | dataset version / manifest | Must match version taxonomy. |
| [ ] Checksums or checksum plans are recorded. | `pass | fail | N/A` | manifest | Required for reproducibility. |
| [ ] Official/reference and BurnLens-derived categories remain separated. | `pass | fail | N/A` | registry / manifest | Source separation rule applies. |

### Future model or baseline release reproducibility

Use only when model/baseline work is authorized in a later phase.

| Check | Status | Evidence path / ID | Notes |
|---|---|---|---|
| [ ] Model/baseline release is authorized by issue/contract. | `pass | fail | N/A` | `#[issue]` | Model work is not authorized by Objective Five. |
| [ ] Dataset and label versions are linked. | `pass | fail | N/A` | dataset/label IDs | Required for model claims. |
| [ ] Method/model/baseline version is recorded. | `pass | fail | N/A` | method/model/baseline version | Must match version taxonomy. |
| [ ] Model card or baseline method record exists. | `pass | fail | N/A` | model card / method record | Required before model/baseline public claims. |
| [ ] Metrics record exists if metrics are claimed. | `pass | fail | N/A` | metrics path | Metrics do not imply operational readiness. |
| [ ] Limitations are explicit. | `pass | fail | N/A` | model card / release note | Must include data, label, method, and use limitations. |
| [ ] No field-validation, emergency-ready, agency-endorsed, or operational claim appears. | `pass | fail | N/A` | release note / model card | Required. |

### Future public demo reproducibility

Use only when public demo work is authorized in a later phase.

| Check | Status | Evidence path / ID | Notes |
|---|---|---|---|
| [ ] Public demo release is authorized by issue/contract. | `pass | fail | N/A` | `#[issue]` | Public demo work is not authorized by Objective Five. |
| [ ] Public copy links to claim evidence. | `pass | fail | N/A` | claim evidence record | Public claims require evidence. |
| [ ] Screenshots/maps/images reference run ID when derived from a run. | `pass | fail | N/A` | caption / metadata / source file | Required. |
| [ ] Warning language is visible in or near the public artifact. | `pass | fail | N/A` | screenshot/site/report | Warning must not be hidden. |
| [ ] Official/reference sources and BurnLens-derived outputs are visually/textually separated. | `pass | fail | N/A` | public artifact | Required source separation. |
| [ ] Public artifact status is visible. | `pass | fail | N/A` | normal/provisional/degraded/superseded/withheld | Required by T09 gate. |
| [ ] Public copy does not imply emergency guidance or official wildfire information. | `pass | fail | N/A` | public copy | Required. |

## Blocking conditions

A reproducibility review is blocked when any of these conditions are true:

- no issue, branch, or PR exists for a task/release candidate that requires them;
- prompt/build log is missing where prompt-assisted work materially changed files;
- changed files are outside the artifact contract without explanation;
- required version or provenance fields are missing;
- source-precedence status is missing where relevant;
- official-sources-govern language is missing where relevant;
- use boundaries are missing or weakened;
- release note fails to state included and excluded work;
- public claim lacks evidence;
- public artifact lacks run ID where required;
- release implies data/model/map/run/report/public-demo work that is not authorized or does not exist;
- output cannot be caveated responsibly;
- artifact implies official, operational, field-validated, emergency-ready, agency-endorsed, evacuation, routing, road-closure, tactical, or incident-command use.

## Final decision

| Field | Value |
|---|---|
| Reproducibility decision | `pass | pass-with-limitations | blocked | not applicable` |
| Required limitation(s) | `[text]` |
| Required follow-up issue(s) | `#[issue] | none` |
| Release allowed from reproducibility standpoint? | `yes | no | not applicable` |
| Reviewer notes | `[notes]` |

## Handoff

If this checklist blocks a candidate, do not publish, tag, release, demo, or promote the artifact. Open a follow-up issue or revise the candidate until all required evidence, boundary, source-precedence, and claim checks pass.
