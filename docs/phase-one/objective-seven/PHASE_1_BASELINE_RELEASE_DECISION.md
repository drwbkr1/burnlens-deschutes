# Phase One Baseline Identifier and Release-Class Decision

## Status

| Field | Current state |
|---|---|
| Task | P1O7-T06 — Decide the Phase One baseline identifier and release class |
| Task issue | #277 — closed as completed |
| Parent issue | #246 — open and protected |
| Repository | `drwbkr1/burnlens-deschutes` |
| Branch / base | `p1o7t06b` / `main` at `6691cb8986df879e4b81b0704fe33ec0b92ca06c` |
| Decision date | 2026-07-12 local / 2026-07-13 UTC research verification |
| Decision state | **Approved with conditions** |
| Human review | Drew — **Approve** at exact head `7d912920e09a22dff9b90a2104a2112b1a237cc1` |
| Merge authorization | Separate squash authorization recorded for the exact reviewed head |
| Pull request / merge | PR #278 / `3f0e158c44e608267cfbba31d21103f99f584123` |
| Inventory remediation | P1O7-REM-06A / #279 merged through PR #280 at `5e6d0d111dc44eabfb056426c1d1c9bb868456c7` |
| Final Phase One gate decision | Not made by T06 |
| Tag action | Not authorized or performed |
| GitHub Release action | Not authorized or performed |
| `VERSIONING.md` | Read-only; no genuine protocol change is required |

## Decision summary

T06, as reviewed and merged, approves the existing **objective baseline** identifier class and the conditional decision candidate:

```text
v0.0.7-objective-seven-phase-one-baseline
```

This is an approved decision candidate only. It is not a Git tag, does not satisfy G10, does not authorize tag creation, and does not imply that tags `v0.0.1` through `v0.0.6` exist.

The candidate remains conditional because the complete live tag inventory is `inaccessible/unresolved`. P1O7-REM-06A accepted T06-F01 with documented limitation for T07 sequencing, but successful complete tag enumeration remains mandatory before any P1O7-T10 tag action and before parent #246 can close. The later Objective Seven decision, closeout, baseline-note, QA, synchronization, and exact T10 authorization gates also remain required.

The selected release posture is:

```text
conditional objective-baseline tag
+
repository release-note / baseline-note document
+
no GitHub Release for this documentation/control baseline
```

A GitHub Release does not add sufficient legitimate value for the present documentation/control scope. Current GitHub documentation describes Releases as tag-based, deployable iterations distributed to a wider audience, with optional assets and explicit pre-release/latest behavior. BurnLens has no deployable app, package, data, model, run, report, map, or public-output artifact in this baseline. Current BurnLens release control therefore favors a repository release-note document and treats a GitHub Release as blocked for this candidate.

## Decision authority and boundary

This record applies current merged controls and reviewed T03–T05 evidence. It decides only the identifier path and release class.

It does not:

- make the P1O7-T08 Phase One gate decision;
- create, move, retarget, annotate, sign, push, or delete a tag;
- create or publish a GitHub Release;
- create release assets, packages, archives, deployments, screenshots, maps, reports, demos, or public release statements;
- modify or execute issue #194;
- authorize Phase Two planning, data touch, implementation, or public-output work;
- remediate any source file or live platform state beyond the separately reviewed REM-06A evidence disposition.

Official sources govern. A version, identifier, tag, release-note document, or GitHub Release never implies operational, official, field-validated, agency-endorsed, emergency-ready, production-stable, evacuation, routing, tactical, or incident-command status.

## Evidence used

### Current governing controls

| Evidence | Decision use |
|---|---|
| `VERSIONING.md` | Defines objective baselines as SemVer-core repository-state labels and separates versioning from readiness. |
| `docs/phase-one/objective-five/VERSION_TAXONOMY.md` | Defines `v0.0.N-short-objective-slug`, increments `N` for a new reviewed objective-level baseline, and requires issue/PR/commit/release-note/boundary/included-excluded trace links. |
| `docs/phase-one/objective-five/RELEASE_CONTROL.md` | Defines objective-baseline tags, reviewed `main` targets, documentation release notes, GitHub Release eligibility, and do-not-release triggers. |
| `docs/phase-one/objective-five/RELEASE_QA_CHECKLIST.md` | Requires class, identifier, commit, closeout, synchronized status, release note, exclusions, and exact tag authorization. |
| `docs/phase-one/objective-five/REPRODUCIBILITY_CHECKLIST.md` | Requires closed/deferred objective tasks, current tracker/README, release note, taxonomy match, and no implied technical readiness. |
| `docs/phase-one/objective-five/OBJECTIVE_FIVE_RELEASE_NOTE.md` | Records `v0.0.5-objective-five-traceability` as a proposed Objective Five documentation/control baseline only. |
| Objective Seven evidence matrix | Keeps G10 tag existence separate from T06’s identifier decision and keeps F10-R GitHub Release existence separate from G10. |
| Reviewed T03–T05 audits | Establish current identity/boundary, planning-readiness, repository-control, versioning, and live-state findings without making the final Phase One decision. |
| P1O7-REM-06A remediation record | Records owner approval, post-branch inventory attempts, accepted limitation for T07 sequencing, and the retained hard gate before T10 and parent closure. |

### Current official GitHub documentation checked

| Source | Current fact used | Decision effect |
|---|---|---|
| GitHub Docs — About releases, `https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases` | Releases are based on Git tags marking repository history and are deployable iterations packaged for wider use; GitHub also provides tag-point source archives and supports assets. | A Release is a higher-friction publication object, not a synonym for a tag or repository note. |
| GitHub Docs — Managing releases, `https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository` | Release creation selects or creates a tag and target, can attach binary assets, can mark pre-release, and can set or derive the latest release. | Pre-release, latest, title/body, target, and assets require separate explicit decisions if a Release is ever proposed. |
| GitHub Docs — Viewing releases and tags, `https://docs.github.com/en/repositories/releasing-projects-on-github/viewing-your-repositorys-releases-and-tags` | GitHub exposes release and tag views as separate repository-history surfaces. | Live tags and Releases must be inventoried separately. |

No Semantic Versioning revalidation was performed. The conditional protocol-change gate was not triggered because the existing objective-baseline class expresses this decision without changing naming or increment rules.

## Live tag and GitHub Release research

### Complete inventory result

| Inventory | Exact methods | Result | Decision consequence |
|---|---|---|---|
| All Git tags and targets | T06 connector action-catalog inspection; `git ls-remote --tags`; REST matching-refs attempt; REM-06A repeated connector, CLI, REST, and public-page attempts after branch creation | **`inaccessible/unresolved`**. No complete tag list or targets were returned. | No empty-inventory claim. Candidate remains conditional. T06-F01 is accepted with documented limitation for T07 sequencing, but complete enumeration is mandatory before tag QA, T10 authorization, tag creation, and parent closure. |
| All GitHub Releases | T06 connector action-catalog inspection, REST and public-page attempts; REM-06A repeated connector, REST, and public-page attempts | **`inaccessible/unresolved`**. No complete Release list or states were returned. | F10-R remains `evidence incomplete`. No existence or absence claim. This does not block rejecting a GitHub Release for the current candidate. |

### Exact candidate-ref checks

Targeted exact-ref checks are not a complete inventory.

| Ref | Exact check result | Meaning |
|---|---|---|
| `v0.0.1-project-scope` | `No commit found for the ref` | This exact ref did not resolve during T06 and REM-06A. It does not prove no other tag exists. |
| `v0.0.1-objective-one` | `No commit found for the ref` | This exact historical proposal did not resolve during the targeted checks. |
| `v0.0.5-objective-five-traceability` | `No commit found for the ref` | The exact Objective Five candidate did not resolve during the targeted checks; issue #194 remains separate. |
| `v0.0.7-objective-seven-phase-one-baseline` | `No commit found for the ref` | The approved conditional candidate did not resolve during targeted checks, but complete collision verification remains required before T10. |

## Legacy identifier dispositions

### `v0.0.1-project-scope`

**Disposition: rejected and approved.**

Rationale:

1. The exact string is not present as the historical Objective One issue proposal; issue #1 proposed `v0.0.1-objective-one`.
2. The exact ref did not resolve during T06 or REM-06A.
3. The string does not reflect the current Objective Seven Phase One acceptance and closeout scope.
4. Reusing `v0.0.1` now would retrospectively restart or renumber the current objective-baseline sequence without a protocol-supported reason.
5. The current taxonomy already provides a later sequential objective-baseline class.

The rejection is a naming decision only. It is not a claim that the complete tag inventory is empty.

### `v0.0.1-objective-one`

**Disposition: historical proposal replaced for current use; not created retroactively; approved.**

Issue #1 records this as the original Objective One first-tag proposal. It was a plausible early objective-level label, but it is not the current Phase One baseline candidate because:

- its scope is Objective One, not the reviewed Phase One / Objective Seven baseline;
- its exact ref did not resolve during T06 or REM-06A;
- its historical “Phase 2 can begin” implication is superseded by current Objective Five and Seven authorization gates;
- creating it now would backfill an earlier milestone rather than mark the exact future reviewed Phase One baseline commit.

Historical issue #1 remains explanatory Tier 2 evidence only and does not control the current decision.

## Objective Five candidate and issue #194

### Candidate classification

```text
v0.0.5-objective-five-traceability
```

is a taxonomy-conforming **Objective Five objective-baseline candidate** supported by an Objective Five release-note draft. It is not a Phase One / Objective Seven baseline identifier.

### Issue #194 classification

Issue #194 remains an open, separate controlled-action authorization for only:

- tag name `v0.0.5-objective-five-traceability`;
- target commit `bc565d9dae884cb7bb8f88dfb1bf7ddab1abcfff`;
- tag creation only;
- no GitHub Release;
- no retargeting to later commits.

T06 and REM-06A do not edit, close, execute, supersede, absorb, or retarget #194. Its historical target must not be reused for the Phase One baseline.

Whether #194 should later execute, be withdrawn, or receive a separate administrative decision is outside T06. Its open state is not evidence that the tag exists.

## Phase One identifier path

### Alternatives evaluated

| Alternative | Result | Rationale |
|---|---|---|
| Continue the existing sequential objective-baseline class | **Selected and approved conditionally** | Current taxonomy already expresses a reviewed Objective Seven documentation/control baseline and preserves the existing naming logic. |
| Define a separate Phase One baseline class | Rejected | A new class would duplicate the objective-baseline purpose and create unnecessary protocol complexity. No controlling rule change is needed. |
| Defer all identifier selection | Rejected as the primary outcome | Current controls are sufficient to approve a taxonomy-conforming decision candidate. Final collision verification and tag eligibility remain deferred until complete live inventory succeeds. |

### Conditional candidate

```text
v0.0.7-objective-seven-phase-one-baseline
```

Interpretation:

- `v0.0.7` follows the current objective-baseline namespace for Objective Seven;
- `objective-seven-phase-one-baseline` identifies the reviewed repository-state milestone;
- the number is an identifier namespace decision, not a claim that preceding tags exist;
- the candidate is owner-approved as a decision candidate;
- the candidate remains conditional on complete tag enumeration and all later gates.

No alternate candidate should be silently substituted. A name change after T06 review requires a recorded decision revision or a separate exact-scope remediation task.

## Release-class decision

| Item | T06 decision | Status after T06 and REM-06A |
|---|---|---|
| Identifier class | Existing `objective baseline` | Approved with conditions |
| Candidate identifier | `v0.0.7-objective-seven-phase-one-baseline` | Approved conditional decision candidate; not a tag |
| Repository release note | Required later as an Objective Seven baseline note/release note | Not created by T06 or REM-06A |
| Git tag | Potential later P1O7-T10 controlled action | Not authorized or created |
| GitHub Release | **Rejected for this documentation/control candidate** | No T11 publication recommended from current evidence |
| Release assets | N/A | No Release or asset package proposed |
| Pre-release setting | N/A | No GitHub Release candidate |
| Latest-release setting | N/A | No GitHub Release candidate |

### GitHub Release value test

A GitHub Release would add a public release object, tag association, source archives, optional assets, release feed visibility, and pre-release/latest semantics. Those features do not add enough value for the current candidate because:

- the included scope is repository documentation and controls;
- there is no deployable software iteration or package;
- there are no release assets;
- there is no data, model, run, report, map, or demo package;
- a reviewed repository release-note document can state exact included/excluded scope without implying a deployable release;
- BurnLens release control blocks a documentation-only GitHub Release when a repository release note is sufficient.

A later T11 could revisit GitHub Release publication only under a separate explicit authorization and new evidence. It must not inherit T06’s N/A pre-release/latest/assets fields as an approval.

## Future tag target requirements

A future P1O7-T10 issue may authorize the proposed tag only when all conditions below are met:

1. Complete live tag enumeration succeeds and confirms no name collision or incompatible existing sequence.
2. T06 has been reviewed and merged.
3. T06-F01 has been accepted with documented limitation for sequencing, while its complete-enumeration requirement remains a hard pre-tag gate.
4. P1O7-T07 exit checklist is complete and reviewed.
5. P1O7-T08 final Phase One decision supports a baseline candidate.
6. P1O7-T09 closeout and handoff are reviewed and merged.
7. An Objective Seven baseline note/release-note document exists and lists exact included and excluded artifacts.
8. README, tracker, canonical prompt-log index, and dated logs reflect the final reviewed state.
9. Release QA and objective-baseline reproducibility checks are completed against the exact candidate.
10. The target is one exact reviewed commit on `main` after all required merges and final status synchronization.
11. The T10 issue records the exact tag name, exact target SHA, allowed action, verification method, and parent-close behavior.
12. Separate human approval and exact action authorization exist.

The future target must not be:

- `p1o7t06b` or any task branch head;
- the T06 or REM-06A merge commit merely because those tasks approved the candidate or accepted the limitation;
- an open PR head;
- a commit with stale status records;
- the historical #194 target;
- a commit preceding required decision, closeout, baseline-note, or QA work.

After tag creation, live tag name and target must be reverified and current-status/closeout records synchronized before G10 can change or parent #246 can close.

## Included-work requirements for the future baseline note

The future Objective Seven baseline note must inventory exact paths and evidence links for the reviewed Phase One documentation/control baseline. At minimum, it must cover the applicable merged artifacts from:

- Objective One project identity, thesis, technical description, use boundaries, source precedence, and transparency controls;
- Objective Two bounded CV task, target/fallback, class, output, assumption, baseline, model-family, metrics, failure, and use-boundary planning controls;
- Objective Three data-feasibility, candidate-source, AOI, format/CRS, provenance, research, and claims controls;
- Objective Four issue, taxonomy, Project specification, branch/PR, and intake controls;
- Objective Five versioning, release, provenance, artifact-registry, run-package, source-precedence, reproducibility, QA, claim, closeout, and handoff controls;
- Objective Six prompt-built issue-to-merge workflow and review controls;
- Objective Seven tracker, evidence matrix, reviewed audits, decision, remediation records, exit checklist, decision memo, closeout, handoff, and baseline-candidate record when those later exist;
- current README, canonical prompt/build-log index, relevant dated logs, and exact issue/PR/commit evidence.

The note must list exact included paths rather than claiming that all repository content is released.

## Excluded-work requirements

The future documentation/control baseline must explicitly exclude, unless a later independent authorization and evidence package says otherwise:

- Phase Two authorization and all data-touch actions;
- AOI selection or geometry;
- source acquisition, download, retained imagery, or source files;
- source/access/terms records for real intake;
- labels, masks, datasets, splits, or manifests;
- baseline implementation or outputs;
- model training, weights, inference, or metrics;
- run folders or run packages;
- raster/vector outputs, exposure summaries, maps, reports, screenshots, demos, or deployments;
- release assets or packaged binaries;
- approved public claims or public release statements;
- GitHub Project configuration or repository enforcement not live-verified;
- official, operational, field-validated, emergency-ready, agency-endorsed, production-stable, evacuation, routing, tactical, or incident-command claims;
- a GitHub Release unless separately authorized and published later.

## G10 and F10-R after T06 and REM-06A

| Evidence row | Current state | Reason |
|---|---|---|
| G10 — first Phase One release tag exists | `evidence incomplete` | T06 and REM-06A create no tag; complete inventory is unresolved; candidate and future target remain conditional. Mandatory blocker to claiming Phase One complete. |
| F10-R — GitHub Release exists | `evidence incomplete` | Complete inventory is unresolved and no Release is authorized or recommended for this candidate. Supporting fact only; not required to satisfy G10. |

## Finding and remediation routing

| ID | Finding | Reviewed disposition / effect | Consequence | Route |
|---|---|---|---|---|
| T06-F01 | Complete live tag inventory and targets could not be enumerated. | **Accepted with documented limitation** through P1O7-REM-06A / #279 and PR #280. It no longer blocks T07 sequencing after status synchronization. | Complete inventory remains `inaccessible/unresolved`; candidate collision and sequence cannot be conclusively ruled out. It remains a mandatory blocker before T10/tag creation and parent closure. | Carry the limitation through T07–T09; require successful complete enumeration in the exact T10 authorization and before parent closure. |
| T06-F02 | Complete GitHub Release inventory could not be enumerated. | Supporting limitation retained. | No Release existence/absence claim is supported. | Reverify only if a separately authorized T11 or later decision relies on live Release existence. |
| T06-F03 | Issue #194 remains open for a different Objective Five tag and historical target. | Non-blocking administrative separation retained. | Readers must not conflate or retarget it to the Phase One candidate. | Keep #194 untouched. Any withdrawal, execution, or administrative closure requires separate human authorization outside T06. |
| T06-F04 | T05 proposed active-routing corrections in `AGENTS.md` and `CONTRIBUTING.md`. | Carried non-blocking limitation. | Current README/tracker govern, but active routing remains imperfect. | P1O7-REM-05A remains a proposal only; T06 does not create or execute it. |

REM-06A did not create a tag, publish a Release, change settings, or bundle unrelated cleanup.

## Acceptance self-audit

| Acceptance criterion | Reviewed result |
|---|---|
| `v0.0.1-project-scope` explicitly accepted/replaced/rejected | Satisfied — rejected with rationale and owner approval |
| Historical `v0.0.1-objective-one` separately reconciled | Satisfied — historical proposal replaced for current use; no retroactive tag; owner approved |
| Objective Five candidate, release note, #194, and target classified | Satisfied — separate Objective Five controlled action, untouched |
| One identifier path selected | Satisfied — existing sequential objective-baseline class, conditional candidate |
| Taxonomy match | Satisfied with live-inventory condition |
| Release class explicit | Satisfied — objective baseline plus repository release-note document |
| Tag and GitHub Release separately evaluated | Satisfied |
| GitHub Release value evaluated | Satisfied — rejected for current documentation/control candidate |
| Target-commit requirements exact | Satisfied |
| Pre-release/latest/assets behavior explicit | Satisfied — N/A because no GitHub Release candidate |
| Included and excluded requirements complete | Satisfied |
| Complete live inventories recorded | Satisfied with `inaccessible/unresolved` limitation and REM-06A disposition |
| G10 remains incomplete | Satisfied |
| F10-R remains separate | Satisfied |
| Protocol-change gate applied | Satisfied — no protocol change; `VERSIONING.md` read-only |
| No tag, Release, asset, deployment, public statement, final gate decision, or Phase Two work | Satisfied |
| Blocking finding routed separately | Satisfied — REM-06A merged; limitation accepted for sequencing with hard pre-tag gate retained |
| Human review and merge | Satisfied — Drew approved; PR #278 squash-merged; REM-06A merged through PR #280 |

## Safe claims

The merged records support only these narrow claims:

- BurnLens uses the existing objective-baseline class for the approved conditional Phase One candidate `v0.0.7-objective-seven-phase-one-baseline`.
- The candidate is not a tag and remains conditional on complete live inventory and later decision, closeout, QA, synchronization, and T10 authorization.
- T06-F01 is accepted with documented limitation for T07 sequencing, while complete enumeration remains mandatory before T10 and parent closure.
- A repository release-note document is the appropriate documentation/control evidence package.
- A GitHub Release is not recommended for the current candidate.
- G10 and F10-R remain `evidence incomplete`.
- Issue #194 remains separate and untouched.

## Unsupported claims

T06 and REM-06A do not support claims that:

- Phase One passed, closed, or was released;
- the approved conditional candidate exists as a tag or is conclusively collision-free;
- the repository has no tags or no GitHub Releases;
- `v0.0.1-project-scope`, `v0.0.1-objective-one`, or `v0.0.5-objective-five-traceability` never existed in any form;
- issue #194 was replaced, retargeted, executed, or closed;
- the T06 branch, T06 merge, or REM-06A merge is the future tag target;
- a GitHub Release exists, is required, is latest, or is pre-release;
- a data, AOI, label, baseline, model, run, metric, map, report, screenshot, deployment, or public-output artifact exists;
- Phase Two or data touch is authorized;
- BurnLens is official, operational, field-validated, agency-endorsed, emergency-ready, production-stable, or suitable for public-safety decisions.

## Handoff

After P1O7-SYNC-06A merges and repository status is coherent:

1. P1O7-T07 is the next task, but it must begin only under its own issue and task capsule;
2. carry the approved conditional candidate and the accepted T06-F01 limitation;
3. carry successful complete tag enumeration as mandatory before T10 and parent closure;
4. carry G10 as `evidence incomplete` and mandatory for Phase One completion;
5. carry F10-R separately as supporting evidence;
6. keep issue #194 open and untouched unless separately authorized;
7. do not create a tag before P1O7-T10 or a GitHub Release before a separately authorized P1O7-T11.

## Do not carry forward

Do not carry forward:

- `v0.0.1-project-scope` as an accepted candidate;
- `v0.0.1-objective-one` as the current baseline candidate or as Phase Two authorization;
- `v0.0.5-objective-five-traceability` as a Phase One / Objective Seven tag;
- the historical #194 target as a future Phase One target;
- an inference that exact-ref failure or inaccessible enumeration proves an empty tag or Release inventory;
- an assumption that the approved conditional candidate is authorized for creation;
- a GitHub-Release-latest, pre-release, or asset decision from this documentation-only candidate;
- an assumption that identifier selection or accepted limitation equals G10 satisfaction or the final Phase One decision.