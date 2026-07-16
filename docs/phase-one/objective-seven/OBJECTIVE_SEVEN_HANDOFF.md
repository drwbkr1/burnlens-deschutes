# Objective Seven Handoff

> **Historical snapshot.** This handoff predates the controlling execution goal and all Phase Two implementation. Current authority and status live in `docs/governance/BURNLENS_EXECUTION_GOAL.md`, `docs/status/PHASE_STATUS.md`, and `docs/roadmap/BURNLENS_BUILD_ROADMAP.md`. BL-GOV-002 preserves this file as audit evidence but supersedes its active routing, permission, tag, issue, and approval language.

## One-sentence project state

BurnLens Deschutes has a review-ready Objective Seven closeout package on `p1o7t09b`; Drew’s controlling decision is `APPROVE — PHASE TWO PLANNING ONLY`, while G10 still blocks full Phase One completion and F04-A still blocks every data-touch action.

## Handoff metadata

| Field | Current state |
|---|---|
| Task | P1O7-T09 — Close out Objective Seven and prepare the reviewed baseline candidate |
| Task issue | #298 — open |
| Parent issue | #246 — open and protected |
| Branch / authorized base | `p1o7t09b` / `23d57ab96071e21068ab7c02ae970b2968e10c04` |
| Pull request | Not opened |
| Human review | Pending |
| Merge authorization | Pending |
| Objective Seven state | Active and incomplete |
| Phase One state | Planning-only decision recorded; full completion blocked by G10 |
| Data-touch state | Not authorized; blocked by F04-A |
| Candidate | `v0.0.7-objective-seven-phase-one-baseline` — candidate only |
| Candidate target | Unresolved until reviewed merge and bounded post-merge synchronization |
| Tag | Not created and not authorized |
| GitHub Release | Not published, not authorized, and not recommended |

## Required governing boundary

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

This warning governs future BurnLens-derived outputs. The T09 package contains documentation and review records only; it contains no data, model, run, map, report, screenshot, demo, deployment, or public-output artifact.

## Controlling decision and consequences

The controlling human decision remains:

```text
APPROVE — PHASE TWO PLANNING ONLY
```

The decision permits separate issue-backed planning and control tasks. It does not permit:

- source access or source queries;
- AOI geometry creation;
- imagery download, retention, or processing;
- labels, masks, datasets, baselines, models, metrics, or runs;
- maps, reports, screenshots, demos, deployments, or site publication;
- public claim approval;
- tag creation;
- GitHub Release publication;
- repository settings or Project changes.

## Exact next-work order

### 1. Review and merge P1O7-T09

Before any downstream dependency is treated as satisfied:

1. open one task-scoped PR from `p1o7t09b` to `main` using `Closes #298` only;
2. inspect the complete diff against the authorized base;
3. record a human outcome under `docs/phase-one/objective-six/PR_REVIEW_CHECKLIST.md` or an explicit PR comment;
4. obtain separate exact-head merge authorization after an **Approve** outcome;
5. use a permitted merge method, preferably squash for the bounded task branch.

This handoff does not open the PR or authorize the merge.

### 2. Run a bounded post-merge synchronization

After T09 merges, inspect README, the Objective Seven tracker, the canonical prompt-log index, the T09 dated log, release note, closeout, handoff, and review records.

A bounded synchronization is expected because the following facts cannot be known during the source-branch build:

- T09 PR number;
- exact reviewed head;
- human review outcome and evidence;
- merge authorization;
- T09 merge commit;
- exact eligible synchronized `main` target for the candidate.

The synchronization must record the exact T09 merge SHA as the potential candidate target only after verifying that the merged status records are coherent. It must not create a tag or GitHub Release.

### 3. First permitted Phase Two action

The first permitted Phase Two action is:

```text
Create the Phase Two planning parent issue and current planning tracker.
```

That task may define:

- planning objectives and task order;
- dependency and blocker routing;
- planning-only artifact contracts;
- no-data source/AOI intake sequence;
- verification and stop rules;
- handoff conditions.

It must explicitly adopt the T08 planning-only decision and preserve the rule that planning permission is not data permission.

### 4. Keep #293 blocked until its parent dependency exists

Issue #293 remains blocked until a Phase Two planning parent:

1. exists;
2. adopts the planning-only boundary;
3. links #293;
4. confirms that #293 creates reviewable intake records only and does not authorize source access.

Even after #293 is unblocked and its records are reviewed and merged, another separately authorized exact action issue remains mandatory before any metadata query or source access.

### 5. Keep #292 blocked until the T09 target is synchronized

Issue #292 remains blocked until:

1. T09 is human-reviewed and merged;
2. the bounded post-merge synchronization records the exact eligible `main` target;
3. the release note and both review records reflect the reviewed lifecycle accurately.

#292 may then attempt complete authenticated tag enumeration and produce a readiness decision. It cannot create a tag.

### 6. Require a separate exact T10 authorization

A future P1O7-T10 may be considered only if #292 records:

```text
READY FOR SEPARATE T10 AUTHORIZATION
```

The T10 issue must name:

- exact tag spelling;
- exact synchronized `main` target SHA;
- exact creation method;
- exact verification method;
- allowed action and forbidden side effects;
- task-only close behavior;
- parent-close behavior.

No such exact tag action is authorized by T09 or #292.

### 7. Do not pursue a GitHub Release for the current candidate

The reviewed T06 release-class decision remains controlling: a repository release note is sufficient for the present documentation/control candidate. No deployable app, package, data, model, run, report, map, demo, or release asset is included.

P1O7-T11 remains optional and is not recommended. Any future reconsideration would require a separate issue, new value justification, an existing authorized tag, and a fresh release-QA decision.

## Current blockers and owners

| Item | State | Effect | Next owner or route |
|---|---|---|---|
| G10 | `evidence incomplete` | Blocks full Phase One completion and parent #246 closure | #292, then a separately authorized exact T10 if ready |
| F04-A | `evidence incomplete` | Blocks all data touch | Future Phase Two planning parent, #293 record task, then separate exact action issue |
| F06-C | `inaccessible/unresolved` | Supporting fact only | Reverify only when a later issue makes Project state material |
| F10-R | `inaccessible/unresolved` | Supporting fact only | No action for current candidate; GitHub Release not recommended |
| T09 human gate | Pending | Blocks merge and downstream target selection | Drew or another eligible human reviewer |
| Candidate target | Unresolved | Blocks #292 and any tag-readiness conclusion | Bounded post-T09 merge synchronization |

## Current authoritative context for the next chat

Load or summarize:

```text
README.md
docs/workflows/PROMPT_TO_REPO_SOP.md
docs/phase-one/objective-seven/OBJECTIVE_SEVEN_TRACKER.md
docs/phase-one/objective-seven/PHASE_1_EXIT_CHECKLIST.md
docs/phase-one/objective-seven/PHASE_1_DECISION_MEMO.md
docs/phase-one/objective-seven/OBJECTIVE_SEVEN_CLOSEOUT.md
docs/phase-one/objective-seven/OBJECTIVE_SEVEN_HANDOFF.md
docs/phase-one/objective-seven/PHASE_1_RELEASE_NOTE.md
docs/phase-one/objective-seven/OBJECTIVE_SEVEN_REPRODUCIBILITY_REVIEW.md
docs/phase-one/objective-seven/OBJECTIVE_SEVEN_RELEASE_QA_REVIEW.md
records/PROMPT_BUILD_LOG.md
records/prompt-build-log/2026-07-13-p1o7-t09.md
```

Also inspect live issue and branch state before acting:

```text
#246
#298
#292
#293
#194
p1o7t09b
main
```

## Safe claims

After the branch build, it is safe to say only that:

- T09 has a review-ready, issue-backed documentation package on its authorized branch;
- the T08 decision authorizes Phase Two planning only;
- the baseline identifier is a conditional candidate and not a tag;
- G10 and F04-A remain blockers for their respective lanes;
- the GitHub Release path is not recommended for the current candidate;
- no data, model, output, tag, or Release action occurred.

## Do not carry forward

Do not carry forward:

- the former pending T08 decision or date;
- duplicate issue #295 as an active authorization;
- PR #258 or its wrong-repository findings;
- the deleted `__invalid__` or `__invalid2__` paths;
- exact-ref failures as evidence of an empty tag inventory;
- the conditional candidate as an existing tag;
- the T09 planning base as the final candidate target;
- a branch head or open PR head as an eligible tag target;
- planning permission as data permission;
- #292 as tag authorization;
- #293 as source-access authorization;
- a repository release note as a GitHub Release;
- author or AI self-review as human approval;
- any implication that Objective Seven or Phase One is complete;
- any implication that Phase Two data work has begun;
- any implication that a tag or GitHub Release is authorized or published;
- any implication that BurnLens is operational, official, field-validated, agency-endorsed, emergency-ready, or suitable for evacuation, routing, tactical, or incident-command use.

## Stop conditions

Stop and create or revise an authorization record before acting if the next request would:

- change a file outside the next issue’s allowed paths;
- create a tag before #292 and exact T10 authorization;
- publish a GitHub Release;
- query or access a source before the before-data gate is satisfied for one exact action;
- create an AOI, data, labels, models, runs, maps, or public outputs under planning-only permission;
- close parent #246 while G10 remains incomplete;
- use a target SHA that was not reviewed and synchronized on `main`.
