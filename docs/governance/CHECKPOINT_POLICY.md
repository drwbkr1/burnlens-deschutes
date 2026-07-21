# BurnLens Checkpoint Policy

## Status and authority

Policy identifier: `checkpoint-policy-v0.1.0`

This policy controls BurnLens checkpoint cadence under `docs/governance/BURNLENS_EXECUTION_GOAL.md`. It changes when related evidence is shipped; it does not change the project promise, phase outcomes, computer-vision task, source precedence, use boundaries, owner-review route, or any scientific, custody, privacy, rendered-output, or reproducibility gate.

When an active workflow document conflicts with this policy, the execution goal and this policy govern. Historical issues, pull requests, logs, task packets, and phase artifacts remain immutable audit evidence.

## Checkpoint classes

### Evidence unit

An evidence unit is the smallest independently verifiable piece of work inside a milestone. Examples include one event acquisition, source or terms check, archive inspection, optical/reference assessment, candidate proposal, owner response, reconciliation, or QA run.

Every evidence unit must retain:

- a stable unit, record, or immutable run identifier;
- exact input and output identities, sizes, and hashes where bytes exist;
- applicable source, terms, access, custody, provenance, quality, uncertainty, leakage, privacy, and use-boundary gates;
- the method and actual result for every applicable check;
- a disposition of `pass`, `remediate`, `exclude`, `defer`, or `stop`;
- every failed or superseded run needed to explain the final disposition.

An evidence unit may accumulate on the milestone issue and branch. Completing one does not automatically require a separate pull request, BurnLens software version, repository tag, GitHub Release, deployment, changelog release entry, or lifecycle-sync pull request.

### Milestone checkpoint

A milestone checkpoint is a coherent batch of evidence units that materially changes accepted project truth. A milestone ships when its declared exit condition is met or when the accumulated evidence supports a material remediation, fallback, deferral, or stop decision.

A milestone requires:

- one issue-backed outcome and branch-scoped contract;
- a declared evidence-unit roster or registration rule;
- explicit entry, exit, failure-retention, and stop conditions;
- one complete evidence-unit ledger with no omitted failures;
- rendered and actual-output verification appropriate to the result;
- one reviewable pull request and verified merged state;
- applicable artifact, dataset, label, baseline, model, report, or software versions;
- a tag, GitHub Release, deployment, or post-merge lifecycle action only when the governing release controls and the milestone outcome require it;
- roadmap, status, changelog, version-history, prompt/build-log, devlog, website, and case-study updates when their truth materially changes.

Milestones should be large enough to change project truth and small enough to review, reproduce, remediate, or roll back as one bounded result.

### Exception checkpoint

An exception checkpoint may ship independently before a planned milestone when waiting would create material risk or leave repository truth unsafe. Valid triggers are:

- unresolved or changed licensing or source terms;
- security or sensitive-material exposure;
- custody, provenance, hash, or privacy failure;
- rollback or release-withdrawal need;
- a controlling stop condition;
- an urgent correctness defect that invalidates accepted evidence or public truth.

The exception issue and pull request must name the trigger, affected evidence, containment, verification, rollback posture, and effect on the active milestone. Convenience, small diff size, elapsed time, or a desire to publish progress is not an exception trigger.

## Batching safeguards

Batching changes release cadence only. It never weakens or postpones a gate that must pass before the next evidence action.

1. Acquire and inspect one event or custody transaction at a time unless the active issue proves parallel access is equally safe.
2. Stop an evidence unit before downstream use when source identity, terms, custody, quality, uncertainty, privacy, or leakage is unresolved.
3. Keep owner decisions separate from non-owner gates. Owner `yes` is necessary but never sufficient for prototype-label promotion; `no` and `uncertain` remain excluded.
4. Never partially promote an owner-reviewed unit. The exact response, proposal, source, quality, uncertainty, and leakage bindings must pass together.
5. Preserve failed, superseded, excluded, and deferred units in the milestone ledger. A successful batch cannot hide them or count only favorable units.
6. Give every public output the applicable commit, artifact version, run ID, hashes, limitations, warning, and source-precedence note.
7. Push completed evidence-unit records to the remote milestone branch at sensible recovery points; branch history is not a substitute for durable manifests and ledgers.
8. Run the smallest verification set that proves the changed scope. Do not rerun unrelated analytical, package, deployment, or lifecycle gates for a documentation-only or unchanged layer.
9. Use a separate post-merge sync only when merged repository truth is actually stale. Do not create recursive synchronization churn.
10. Stop and ask immediately when the execution goal's owner stop conditions are reached; batching never delays escalation.

## Milestone issue contract

Before the first evidence unit, the milestone issue must state:

- checkpoint class and milestone identifier;
- outcome and why it materially changes project truth;
- branch and verified base;
- dependencies and entry conditions;
- evidence-unit roster or the rule for registering later units;
- allowed path families and prohibited work;
- per-unit required records, hashes, and gates;
- milestone exit condition;
- failure-retention, remediation, fallback, and stop rules;
- public-claim and version/tag/deployment impact;
- validation and handoff plan.

Scope may be refined within the declared outcome. A materially different outcome, new phase result, new use boundary, or unlisted high-risk data/source action requires an issue revision or a separate checkpoint before work continues.

## Evidence-unit ledger

The milestone's durable records must make this table reconstructible:

| Unit ID | Purpose | Inputs and hashes | Outputs and hashes | Gates | Disposition | Failure or limitation retained | Next dependency |
|---|---|---|---|---|---|---|---|
| `[stable ID]` | `[bounded question]` | `[records / hashes]` | `[records / hashes]` | `[pass/fail by gate family]` | `[pass/remediate/exclude/defer/stop]` | `[exact retained evidence]` | `[next unit or milestone exit]` |

The ledger may live in one milestone record or be assembled from linked immutable manifests, provided a reviewer can enumerate every unit and disposition without relying on chat history.

## Shipping and versioning rules

- Evidence-unit identifiers and run IDs remain immutable and unique even when no repository version changes.
- Repository SemVer, analytical tags, GitHub Releases, and deployments belong to milestone or exception outcomes only when the relevant artifact changed and its release gates pass.
- A governance-only milestone may use a governance identifier without changing BurnLens software or creating a tag.
- A milestone PR may contain several independently recorded evidence units, but it must present one coherent final decision and complete ledger.
- Post-merge verification must match the changed risk. A separate lifecycle-sync PR is required only when the merge leaves active repository truth stale and that fact cannot be captured accurately in the milestone closeout.

## First prospective Phase Two sequence

After BL-GOV-003, the current best sequence is:

1. **Six-event evidence milestone** — complete the Petes Lake source, terms, custody, optical/reference/background, proposal, owner-response, quality, uncertainty, and leakage chain under issue #521. One accepted sixth event is necessary but not sufficient for a dataset.
2. **Dataset-fitness milestone** — rerun the separate sufficiency evaluator across the complete accepted evidence and decide `pass`, `remediate`, `fallback`, `defer`, or `stop`.
3. **Dataset-and-split milestone, conditional** — create a versioned dataset and leakage-resistant split only if dataset fitness passes every required class, unknown, regime, transfer, dominance, and separation gate.
4. **Baseline milestone, conditional** — establish and evaluate the strongest justified non-model baseline only from the accepted locked dataset and split.

This sequence is a planning hypothesis. Verified evidence may reorder, combine, remediate, or stop it without changing the Phase Two outcome or the safeguards above.

## Non-implications

This policy does not create or imply a dataset, split, baseline, model, metric, deployment, ground truth, independent review, inter-rater agreement, field validation, official status, endorsement, emergency readiness, or operational readiness.
