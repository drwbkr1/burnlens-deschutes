# GitHub Backlog Reconciliation

## Decision

BL-GOV-002 treats the obsolete Phase One GitHub backlog as a public repository-truth defect and reconciles it without changing BurnLens software or science.

Checkpoint source commit: `845125070d5e4c3c4132bae027a786e1cc25bc9c`.

The application-facing and custody-facing paths pass on merged `main`:

- `BL-2026-07-16-cycle-post-v017-browser-r001` returns `PASS_LIVE_BROWSER_RESPONSE_ROUNDTRIP_NO_HUMAN_EVIDENCE_DEFER_DATASET` in Chrome `150.0.7871.124`;
- `BL-2026-07-16-cycle-post-v017-dual-lock-r001` returns `PASS_MIXED_VERSION_DUAL_LOCK_READINESS_ONE_RETURNED_ONE_FIXTURE_NO_REVEAL`;
- the repository still has one qualifying returned response, one non-human fixture, two exact locks, zero adjudications, and no reveal authorization.

The user-visible weakness is GitHub state. PR #307 and issues #292, #306, #246, #194, and #91 remained open after their premises were superseded by the controlling execution goal, verified `v0.0.8-execution-goal-baseline`, current Phase Two work, and complete live tag access.

## Live evidence

At `2026-07-16T20:39:43Z`:

- `main` was `93aa62b5833c1e084194b7ee3788d1772eb714a6`;
- authenticated GitHub API enumeration returned 21 tags;
- the normalized `name<TAB>target<LF>` inventory was 1,600 bytes / SHA-256 `cf9baa414ceca9416a37c4c69621ab4d39c958ff3724973b9ebe05233ce09acf`;
- `git ls-remote --tags origin` independently returned each tag object and peeled target;
- GitHub Release inventory was empty;
- PR #307 remained open and unmerged at head `4e536e034d9c4fe97b723e381ffef26166c295fd`;
- issues #91, #194, #246, #292, #306, #393, and #400 were open.

## Reconciliation

The checkpoint closes PR #307 unmerged and closes issues #91, #194, #246, #292, and #306 with explicit comments that link the superseding evidence. It preserves every commit, branch, issue body, discussion, and PR diff. It does not delete the stale branch.

Issue #393 remains open because it represents a real unmet Phase Two scientific gate: a second qualifying human response must be returned and exact-locked before reveal, comparison, adjudication, or dataset work.

## Boundaries

This checkpoint:

- creates, moves, retargets, or deletes no tag;
- creates or changes no GitHub Release;
- changes no access, ownership, repository visibility, or public-sharing state;
- changes no BurnLens software version, CV task, phase outcome, source precedence, use boundary, analytical artifact, private response, receipt, fixture, or reveal state;
- makes no dataset, model, accuracy, field, official, endorsed, emergency-ready, or operational claim.

The exact machine-readable state and verification contract are in `records/governance/GITHUB-BACKLOG-RECONCILIATION-2026-001.json`.
