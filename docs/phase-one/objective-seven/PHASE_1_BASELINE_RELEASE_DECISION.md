# Phase One Baseline Identifier and Release-Class Decision

## Status

| Field | Current state |
|---|---|
| Task | P1O7-T06 — Decide the Phase One baseline identifier and release class |
| Task issue | #277 — open |
| Parent issue | #246 — open and protected |
| Repository | `drwbkr1/burnlens-deschutes` |
| Branch / base | `p1o7t06b` / `main` at `6691cb8986df879e4b81b0704fe33ec0b92ca06c` |
| Decision date | 2026-07-12 local / 2026-07-13 UTC research verification |
| Decision state | **Propose with conditions** |
| Human review | Pending |
| Merge authorization | Pending and separate |
| Final Phase One gate decision | Not made by T06 |
| Tag action | Not authorized or performed |
| GitHub Release action | Not authorized or performed |
| `VERSIONING.md` | Read-only; no genuine protocol change is required |

## Decision summary

T06 conditionally proposes the existing **objective baseline** identifier class and the candidate:

```text
v0.0.7-objective-seven-phase-one-baseline
```

This is a proposed identifier only. It is not a Git tag, does not satisfy G10, does not authorize tag creation, and does not imply that tags `v0.0.1` through `v0.0.6` exist.

The candidate is conditional because the complete live tag inventory remains `inaccessible/unresolved`. It may advance only after a separately authorized read-only verification confirms that the candidate is not already used or conflicting and after the later Objective Seven decision, closeout, baseline-note, QA, synchronization, and P1O7-T10 authorization gates are satisfied.

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
- remediate any source file or live platform state.

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
| All Git tags and targets | GitHub connector action-catalog inspection; `git ls-remote --tags https://github.com/drwbkr1/burnlens-deschutes.git`; REST attempt to `GET /repos/drwbkr1/burnlens-deschutes/git/matching-refs/tags/` | **`inaccessible/unresolved`**. Connector exposed no complete tag-list action. At `2026-07-13T04:20:25Z`, `git ls-remote` failed because `github.com` could not be resolved. At `2026-07-13T04:22:00Z`, the REST attempt failed because `api.github.com` could not be resolved. | No empty-inventory claim. Candidate remains conditional. Complete enumeration is required before T07 finalization, tag QA, T10 authorization, and parent closure. |
| All GitHub Releases | GitHub connector action-catalog inspection; REST attempt to `GET /repos/drwbkr1/burnlens-deschutes/releases?per_page=100&page=1`; public repository page retrieval attempt | **`inaccessible/unresolved`**. Connector exposed no Release-list action. At `2026-07-13T04:22:00Z`, the REST attempt failed because `api.github.com` could not be resolved. | F10-R remains `evidence incomplete`. No existence or absence claim. This does not block rejecting a GitHub Release for the current candidate. |

### Exact candidate-ref checks

Targeted exact-ref checks are not a complete inventory.

| Ref | Exact check result | Meaning |
|---|---|---|
| `v0.0.1-project-scope` | `No commit found for the ref` | This exact ref did not resolve during T06. It does not prove no other tag exists. |
| `v0.0.1-objective-one` | `No commit found for the ref` | This exact historical proposal did not resolve during T06. |
| `v0.0.5-objective-five-traceability` | `No commit found for the ref` | The exact Objective Five candidate did not resolve during T06; issue #194 remains separate. |
| `v0.0.7-objective-seven-phase-one-baseline` | `No commit found for the ref` | The proposed T06 candidate did not resolve during the targeted check, but complete collision verification remains required. |

## Legacy identifier dispositions

### `v0.0.1-project-scope`

**Disposition: rejected.**

Rationale:

1. The exact string is not present as the historical Objective One issue proposal; issue #1 proposed `v0.0.1-objective-one`.
2. The exact ref did not resolve during T06.
3. The string does not reflect the current Objective Seven Phase One acceptance and closeout scope.
4. Reusing `v0.0.1` now would retrospectively restart or renumber the current objective-baseline sequence without a protocol-supported reason.
5. The current taxonomy already provides a later sequential objective-baseline class.

The rejection is a naming decision only. It is not a claim that the complete tag inventory is empty.

### `v0.0.1-objective-one`

**Disposition: historical proposal replaced for current use; not created retroactively.**

Issue #1 records this as the original Objective One first-tag proposal. It was a plausible early objective-level label, but it is not the current Phase One baseline candidate because:

- its scope is Objective One, not the reviewed Phase One / Objective Seven baseline;
- its exact ref did not resolve during T06;
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

T06 does not edit, close, execute, supersede, absorb, or retarget #194. Its historical target must not be reused for the Phase One baseline.

Whether #194 should later execute, be withdrawn, or receive a separate administrative decision is outside T06. Its open state is not evidence that the tag exists.

## Phase One identifier path

### Alternatives evaluated

| Alternative | Result | Rationale |
|---|---|---|
| Continue the existing sequential objective-baseline class | **Selected conditionally** | Current taxonomy already expresses a reviewed Objective Seven documentation/control baseline and preserves the existing naming logic. |
| Define a separate Phase One baseline class | Rejected | A new class would duplicate the objective-baseline purpose and create unnecessary protocol complexity. No controlling rule change is needed. |
| Defer all identifier selection | Rejected as the primary outcome | Current controls are sufficient to propose a taxonomy-conforming candidate. Final conflict-free approval and tag eligibility remain deferred until complete live inventory succeeds. |

### Conditional candidate

```text
v0.0.7-objective-seven-phase-one-baseline
```

Interpretation:

- `v0.0.7` follows the current objective-baseline namespace for Objective Seven;
- `objective-seven-phase-one-baseline` identifies the reviewed repository-state milestone;
- the number is an identifier namespace decision, not a claim that preceding tags exist;
- the candidate remains conditional on complete tag enumeration and all later gates.

No alternate candidate should be silently substituted. A name change after T06 review requires a recorded decision revision or a separate exact-scope remediation task.

## Release-class decision

| Item | T06 decision | Status after T06 |
|---|---|---|
| Identifier class | Existing `objective baseline` | Conditionally selected |
| Candidate identifier | `v0.0.7-objective-seven-phase-one-baseline` | Proposed with conditions; not a tag |
| Repository release note | Required later as an Objective Seven baseline note/release note | Not created by T06 |
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
3. Any gate-critical T06 remediation is reviewed and resolved or the candidate is revised accordingly.
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
- the T06 merge commit merely because T06 selected a name;
- an open PR head;
- a commit with stale status records;
- the historical #194 target;
- a commit preceding required remediation, decision, closeout, baseline-note, or QA work.

After tag creation, live tag name and target must be reverified and current-status/closeout records synchronized before G10 can change or parent #246 can close.

## Included-work requirements for the future baseline note

The future Objective Seven baseline note must inventory exact paths and evidence links for the reviewed Phase One documentation/control baseline. At minimum, it must cover the applicable merged artifacts from:

- Objective One project identity, thesis, technical description, use boundaries, source precedence, and transparency controls;
- Objective Two bounded CV task, target/fallback, class, output, assumption, baseline, model-family, metrics, failure, and use-boundary planning controls;
- Objective Three data-feasibility, candidate-source, AOI, format/CRS, provenance, research, and claims controls;
- Objective Four issue, taxonomy, Project specification, branch/PR, and intake controls;
- Objective Five versioning, release, provenance, artifact-registry, run-package, source-precedence, reproducibility, QA, claim, closeout, and handoff controls;
- Objective Six prompt-built issue-to-merge workflow and review controls;
- Objective Seven tracker, evidence matrix, reviewed audits, decision, exit checklist, decision memo, closeout, handoff, and baseline-candidate record when those later exist;
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

## G10 and F10-R after T06

| Evidence row | T06 state | Reason |
|---|---|---|
| G10 — first Phase One release tag exists | `evidence incomplete` | T06 creates no tag; complete inventory is unresolved; candidate and future target remain conditional. Mandatory blocker to claiming Phase One complete. |
| F10-R — GitHub Release exists | `evidence incomplete` | Complete inventory is unresolved and no Release is authorized or recommended for this candidate. Supporting fact only; not required to satisfy G10. |

## Finding and remediation routing

| ID | Finding | Severity / effect | Consequence | Proposed separate route |
|---|---|---|---|---|
| T06-F01 | Complete live tag inventory and targets could not be enumerated. | Gate-critical evidence gap; mandatory blocker to unconditional candidate approval, G10 completion, tag action, and parent closure | Candidate collision and sequence cannot be conclusively ruled out. T07 must not be finalized while this remains unreviewed. | **Proposed P1O7-REM-06A** — read-only live tag/Release inventory verification with an exact evidence record and narrowly authorized decision/tracker/log corrections only if the inventory changes T06. Not created by T06. |
| T06-F02 | Complete GitHub Release inventory could not be enumerated. | Supporting evidence gap for F10-R | No Release existence/absence claim is supported. | Include in P1O7-REM-06A read-only verification; does not by itself require a Release or block the objective-baseline class. |
| T06-F03 | Issue #194 remains open for a different Objective Five tag and historical target. | Non-blocking administrative separation | Readers must not conflate or retarget it to the Phase One candidate. | Keep #194 untouched. Any withdrawal, execution, or administrative closure requires separate human authorization outside T06. |
| T06-F04 | T05 proposed active-routing corrections in `AGENTS.md` and `CONTRIBUTING.md`. | Carried non-blocking limitation | Current README/tracker govern, but active routing remains imperfect. | P1O7-REM-05A remains a proposal only; T06 does not create or execute it. |

Suggested P1O7-REM-06A scope must be approved separately and must identify exact files. It must not inherit broad permission from T06, create a tag, publish a Release, change settings, or bundle unrelated cleanup.

## Acceptance self-audit

| Acceptance criterion | Author result |
|---|---|
| `v0.0.1-project-scope` explicitly accepted/replaced/rejected | Satisfied — rejected with rationale |
| Historical `v0.0.1-objective-one` separately reconciled | Satisfied — historical proposal replaced for current use; no retroactive tag |
| Objective Five candidate, release note, #194, and target classified | Satisfied — separate Objective Five controlled action, untouched |
| One identifier path selected | Satisfied — existing sequential objective-baseline class, conditional candidate |
| Taxonomy match | Satisfied with live-inventory condition |
| Release class explicit | Satisfied — objective baseline plus repository release-note document |
| Tag and GitHub Release separately evaluated | Satisfied |
| GitHub Release value evaluated | Satisfied — rejected for current documentation/control candidate |
| Target-commit requirements exact | Satisfied |
| Pre-release/latest/assets behavior explicit | Satisfied — N/A because no GitHub Release candidate |
| Included and excluded requirements complete | Satisfied |
| Complete live inventories recorded | Satisfied with `inaccessible/unresolved` limitation and REM-06A route |
| G10 remains incomplete | Satisfied |
| F10-R remains separate | Satisfied |
| Protocol-change gate applied | Satisfied — no protocol change; `VERSIONING.md` read-only |
| No tag, Release, asset, deployment, public statement, final gate decision, Phase Two work, or remediation | Satisfied |
| Blocking finding routed separately | Satisfied — proposed P1O7-REM-06A only |

Human review remains required. These author findings are not approval or merge authorization.

## Safe claims

After human review and merge, T06 may support only these narrow claims:

- BurnLens uses the existing objective-baseline class for the conditional Phase One candidate `v0.0.7-objective-seven-phase-one-baseline`.
- The candidate is not a tag and is conditional on complete live inventory and later decision, closeout, QA, synchronization, and T10 authorization.
- A repository release-note document is the appropriate documentation/control evidence package.
- A GitHub Release is not recommended for the current candidate.
- G10 and F10-R remain `evidence incomplete`.
- Issue #194 remains separate and untouched.

## Unsupported claims

T06 does not support claims that:

- Phase One passed, closed, or was released;
- the proposed candidate exists as a tag or is conclusively collision-free;
- the repository has no tags or no GitHub Releases;
- `v0.0.1-project-scope`, `v0.0.1-objective-one`, or `v0.0.5-objective-five-traceability` never existed in any form;
- issue #194 was replaced, retargeted, executed, or closed;
- the T06 branch or merge commit is the future tag target;
- a GitHub Release exists, is required, is latest, or is pre-release;
- a data, AOI, label, baseline, model, run, metric, map, report, screenshot, deployment, or public-output artifact exists;
- Phase Two or data touch is authorized;
- BurnLens is official, operational, field-validated, agency-endorsed, emergency-ready, production-stable, or suitable for public-safety decisions.

## Handoff

After human review, approved merge, and any materially necessary bounded status synchronization:

1. create and review a separately authorized P1O7-REM-06A evidence task for complete live tag and GitHub Release inventory;
2. revise the candidate only if that inventory identifies a collision or sequence conflict;
3. do not finalize P1O7-T07 while T06-F01 remains unresolved or unreviewed;
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
- an assumption that the conditional candidate is already approved for creation;
- a GitHub-Release-latest, pre-release, or asset decision from this documentation-only candidate;
- an assumption that identifier selection equals G10 satisfaction or the final Phase One decision.
