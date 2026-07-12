# Phase One / Objective Seven Artifact Contracts

## Status and purpose

This file defines the planned artifact contract for every Objective Seven task named by parent issue #246. Objective Seven is active and incomplete. These contracts plan later work; they do not authorize that work without a separate task issue.

P1O7-T01 does not conduct the Phase One gate, assign a passing state, audit prior objectives, remediate findings, decide a release identifier or release class, create a tag, or publish a GitHub Release.

A future task issue may narrow its contract. It must not broaden the paths or controlled actions listed here without separate human-approved scope revision.

## Common governing controls

Every Objective Seven task must use:

```text
docs/workflows/PROMPT_TO_REPO_SOP.md
AGENTS.md
README.md
VERSIONING.md
docs/objective-one/TECHNICAL_DESCRIPTION.md
docs/objective-one/USE_BOUNDARIES.md
docs/objective-one/SOURCE_PRECEDENCE.md
docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md
docs/phase-one/objective-five/OBJECTIVE_FIVE_HANDOFF.md
records/PROMPT_BUILD_LOG.md
templates/PROMPT_LOG_ENTRY.md
```

Add only the Tier 1 controls named by the task issue. Do not load Tier 2 unless a specific verification question cannot be answered from current controls and live repository state.

Every prompt-assisted file task requires an exact dated log path in its issue using:

```text
records/prompt-build-log/YYYY-MM-DD-task-id.md
```

The task issue must replace `YYYY-MM-DD` with the actual task date before work begins. A path pattern in this planning contract is not file authorization.

## Common forbidden work

Unless a later task contract explicitly authorizes the exact action and its gates are satisfied, Objective Seven tasks must not:

- touch data, AOIs, imagery, labels, masks, baselines, models, metrics, runs, reports, maps, screenshots, demos, or public outputs;
- change repository settings, CI, Actions, branch protection, rulesets, Projects, labels, or milestones;
- claim official, operational, emergency-ready, field-validated, agency-endorsed, production-ready, evacuation, routing, tactical, or incident-command status;
- rewrite completed-objective trackers, handoffs, closeouts, or historical logs;
- create a tag or GitHub Release;
- treat a version, identifier, candidate, tag, or release note as a readiness claim.

Official sources govern. Human review and separate merge authorization remain mandatory.

---

## P1O7-T01 — Establish Objective Seven controls and artifact contracts

| Field | Contract |
|---|---|
| Purpose | Create the current Objective Seven tracker and exact task contracts without conducting the gate. |
| Dependencies | Parent #246 open; current `main` verified; #195 closed; #194 separate and untouched. |
| Primary paths | `docs/phase-one/objective-seven/OBJECTIVE_SEVEN_TRACKER.md`; `docs/phase-one/objective-seven/OBJECTIVE_SEVEN_ARTIFACT_CONTRACTS.md` |
| Supporting paths | `README.md`; `records/PROMPT_BUILD_LOG.md`; `records/prompt-build-log/2026-07-12-p1o7-t01.md` |
| Allowed files | Exactly the five paths above. |
| Forbidden work | No gate result, criterion pass, audit, remediation, release identifier/class decision, tag, Release, earlier-objective rewrite, or controlled implementation work. |
| Research | Repository-internal verification only: `main`, README, issue states, path uniqueness, task sequence, and #194 separation. |
| Verification | Base SHA; path uniqueness; sequence/dependency coverage; contract completeness; README truth; prompt-log structure/index; boundary/claims review; Markdown consistency; complete branch diff against `main`. |
| Acceptance | Tracker covers all tasks/dependencies; contracts cover required fields; Objective Seven is active/incomplete; release path is conditional; README does not imply Phase One passed; only five paths change; no Objective Six archival file changes. |
| Handoff | P1O7-T02 after review, merge, and required synchronization. |

---

## P1O7-T02 — Define the Phase One gate evidence model

| Field | Contract |
|---|---|
| Purpose | Define criterion categories, required evidence, evidence authority, state vocabulary, blocking logic, and decision routing without evaluating any criterion. |
| Dependencies | P1O7-T01 merged; tracker/contracts current; parent #246 open. |
| Primary path | `docs/phase-one/objective-seven/PHASE_1_GATE_EVIDENCE_MODEL.md` |
| Allowed files | Primary path; `docs/phase-one/objective-seven/OBJECTIVE_SEVEN_TRACKER.md`; `README.md`; `records/PROMPT_BUILD_LOG.md`; exact dated `records/prompt-build-log/YYYY-MM-DD-p1o7-t02.md`. |
| Forbidden work | No audit findings, criterion scores, gate conclusion, remediation, identifier decision, tag, Release, data/model/public-output work, or archival rewrite. |
| Research | Repository-internal control mapping. External research only if the issue introduces a current external or platform claim; otherwise record the no-research rationale. |
| Verification | Every criterion has evidence requirements, authority, acceptable states, blocking behavior, and owner task; model separates evidence from decision; paths and terms agree with tracker and controls. |
| Acceptance | Evidence model is complete enough for T03–T08; no criterion is evaluated; missing evidence cannot be silently treated as passing; release actions remain separate. |
| Handoff | P1O7-T03. |

---

## P1O7-T03 — Audit project identity, boundaries, and active-scope language

| Field | Contract |
|---|---|
| Purpose | Compare current project identity, use boundaries, source precedence, README language, and active-scope statements against the T02 evidence model. |
| Dependencies | T02 merged. |
| Primary path | `docs/phase-one/objective-seven/PROJECT_IDENTITY_BOUNDARY_AUDIT.md` |
| Allowed files | Primary path; `docs/phase-one/objective-seven/OBJECTIVE_SEVEN_TRACKER.md`; `README.md` only for issue-authorized current-status correction, not remediation; `records/PROMPT_BUILD_LOG.md`; exact dated `records/prompt-build-log/YYYY-MM-DD-p1o7-t03.md`. |
| Forbidden work | No silent remediation of Objective One or other completed records; no public-copy publication; no gate conclusion; no identifier, tag, or Release action. |
| Research | Repository-internal audit by default. Use live repository state only where current status is part of the criterion. |
| Verification | Audit inventory; evidence citations by repo path; contradiction and stale-status checks; finding severity; unsupported-claim check; scope-only diff. |
| Acceptance | Every in-scope identity/boundary criterion receives an evidence-backed finding or explicit unresolved state; remediation needs are routed to separate issues; no finding is presented as the final gate decision. |
| Handoff | P1O7-T04 or a separately authorized remediation issue for a gate-critical finding. |

---

## P1O7-T04 — Audit CV and Phase Two technical readiness

| Field | Contract |
|---|---|
| Purpose | Assess whether the documented CV task, data-intake prerequisites, provenance, reproducibility, and Phase Two planning controls are coherent enough for the gate. This audits documentation readiness, not executed model or data readiness. |
| Dependencies | T02 and T03 merged; any T03 blocker affecting this audit resolved or explicitly carried. |
| Primary path | `docs/phase-one/objective-seven/CV_PHASE_TWO_READINESS_AUDIT.md` |
| Allowed files | Primary path; `docs/phase-one/objective-seven/OBJECTIVE_SEVEN_TRACKER.md`; `README.md` only for issue-authorized status wording; `records/PROMPT_BUILD_LOG.md`; exact dated `records/prompt-build-log/YYYY-MM-DD-p1o7-t04.md`. |
| Forbidden work | No data acquisition, AOI selection, labels, masks, baselines, models, training, inference, metrics, run packages, maps, or remediation of Objective Two/Three/Five records. No claim of executed technical readiness. |
| Research | Repository-internal evidence review by default. Fresh external research is required only if the issue adds a current technical or source claim. |
| Verification | Required-control inventory; missing prerequisite check; distinction between documented planning and executed evidence; contradiction/failure-mode review; finding severity; diff check. |
| Acceptance | Audit states what documentation exists, what executed evidence does not exist, what blocks later data-touch authorization, and what requires separate remediation; no Phase Two work begins. |
| Handoff | P1O7-T05 or a separately authorized remediation issue. |

---

## P1O7-T05 — Audit repository controls and live GitHub state

| Field | Contract |
|---|---|
| Purpose | Compare documented repository policy with current repository files and live GitHub issue/branch/tag/Release state without changing settings. |
| Dependencies | T02 through T04 merged; relevant blockers resolved or carried explicitly. |
| Primary path | `docs/phase-one/objective-seven/REPOSITORY_CONTROL_STATE_AUDIT.md` |
| Allowed files | Primary path; `docs/phase-one/objective-seven/OBJECTIVE_SEVEN_TRACKER.md`; `README.md` only for issue-authorized current-status wording; `records/PROMPT_BUILD_LOG.md`; exact dated `records/prompt-build-log/YYYY-MM-DD-p1o7-t05.md`. |
| Forbidden work | No settings, CI, Actions, rulesets, protection, labels, milestones, Projects, issue closure, tag creation, Release publication, or earlier-objective remediation. Written policy must not be represented as enforcement. |
| Research | Repository files and live GitHub connector state. External platform documentation is required only if the task makes a current GitHub capability claim beyond observed state. |
| Verification | Current `main`; open/closed issues; branches; tags/Releases; policy-versus-enforcement distinction; stale-status check; finding severity; complete diff. |
| Acceptance | Audit accurately separates documented policy, observed live state, and unverified settings; all blockers are explicit; no settings are changed. |
| Handoff | P1O7-T06 or a separately authorized remediation issue. |

---

## P1O7-T06 — Decide the Phase One baseline identifier and release class

| Field | Contract |
|---|---|
| Purpose | Decide whether a Phase One baseline identifier and release class should be proposed, deferred, or rejected based on T03–T05 evidence. This is a decision record, not a tag or Release action. |
| Dependencies | T03 through T05 complete; gate-critical findings resolved, explicitly accepted, or documented as blocking. |
| Primary path | `docs/phase-one/objective-seven/PHASE_1_BASELINE_RELEASE_DECISION.md` |
| Allowed files | Primary path; `docs/phase-one/objective-seven/OBJECTIVE_SEVEN_TRACKER.md`; `README.md`; `records/PROMPT_BUILD_LOG.md`; exact dated `records/prompt-build-log/YYYY-MM-DD-p1o7-t06.md`. |
| Forbidden work | No tag creation, GitHub Release, retargeting of #194, release asset creation, implementation claim, or final Phase One gate decision. |
| Research | Repository-internal release controls and completed Objective Seven audits. Live GitHub state may verify nonexistence or conflicts. |
| Verification | Identifier syntax if proposed; release-class mapping; target-state rationale; limitation language; #194 separation; no tag/Release side effect; cross-file consistency. |
| Acceptance | Record selects `propose`, `defer`, or `reject`; any proposed identifier and class are explicitly conditional; decision does not imply readiness or guarantee tag/Release creation. |
| Handoff | Required remediation or P1O7-T07. |

---

## P1O7-REM-## — Conditional gate remediation

| Field | Contract |
|---|---|
| Purpose | Resolve one named gate-critical finding without broad cleanup or unrelated improvement. |
| Dependencies | A finding from T03–T06 identifies exact remediation need; a separate issue is approved. |
| Primary path | The remediation issue must replace the placeholder with one exact record path, normally `docs/phase-one/objective-seven/remediation/P1O7-REM-##_REMEDIATION_RECORD.md`. |
| Allowed files | Only the exact remediation record, exact affected paths, tracker, canonical prompt-log index, and exact dated task log named by the remediation issue. The pattern above is not authorization until instantiated. |
| Forbidden work | No bundled findings, opportunistic cleanup, uncontrolled archival rewrites, gate conclusion, tag, Release, data/model/public-output work, or unlisted path. |
| Research | The issue must state whether repository evidence is sufficient or current official/primary research is required for the finding. |
| Verification | Reproduce finding; inspect exact diff; run finding-specific checks; verify no new contradiction; update originating audit only when explicitly allowed. |
| Acceptance | Named finding is resolved, accepted with documented limitation, or remains open; all actual changes stay inside the remediation issue; evidence returns to the originating task/gate. |
| Handoff | Return to the blocked audit, T06 decision, or T07 checklist. |

---

## P1O7-T07 — Create the Phase One exit checklist

| Field | Contract |
|---|---|
| Purpose | Assemble the evidence-model criteria and completed audit/remediation evidence into a reviewable Phase One exit checklist. |
| Dependencies | T03 through T06 complete; required remediation merged or explicitly deferred with consequence. |
| Primary path | `docs/phase-one/objective-seven/PHASE_1_EXIT_CHECKLIST.md` |
| Allowed files | Primary path; `docs/phase-one/objective-seven/OBJECTIVE_SEVEN_TRACKER.md`; `README.md`; `records/PROMPT_BUILD_LOG.md`; exact dated `records/prompt-build-log/YYYY-MM-DD-p1o7-t07.md`. |
| Forbidden work | No invented evidence, hidden waiver, tag, Release, new audit, remediation, or final decision memo. |
| Research | Repository-internal evidence reconciliation only unless an unresolved criterion explicitly requires current external verification. |
| Verification | Criterion-to-evidence trace; state vocabulary; blocker and limitation consistency; unresolved-item check; no unsupported pass state; complete diff. |
| Acceptance | Every criterion has evidence, state, limitation, and source task; unresolved blockers remain visible; checklist does not itself create a tag or Release. |
| Handoff | P1O7-T08. |

---

## P1O7-T08 — Create the Phase One decision memo

| Field | Contract |
|---|---|
| Purpose | Issue the evidence-based Phase One gate decision and state the authorized next posture. |
| Dependencies | T07 complete and coherent; required evidence reviewed; blocking contradictions resolved or explicitly decisive. |
| Primary path | `docs/phase-one/objective-seven/PHASE_1_DECISION_MEMO.md` |
| Allowed files | Primary path; `docs/phase-one/objective-seven/OBJECTIVE_SEVEN_TRACKER.md`; `README.md`; `records/PROMPT_BUILD_LOG.md`; exact dated `records/prompt-build-log/YYYY-MM-DD-p1o7-t08.md`. |
| Forbidden work | No tag, GitHub Release, Phase Two data action, implementation work, or remediation hidden inside the memo. |
| Research | Repository-internal synthesis of T02–T07 and live status where required. |
| Verification | Decision matches checklist; limitations and blockers carried; next-authorized-work language bounded; release actions separated; human decision review recorded. |
| Acceptance | Memo records one explicit outcome such as proceed to bounded planning, proceed with limitations, defer, or reject; it explains evidence and consequences; it does not guarantee a tag or Release. |
| Handoff | P1O7-T09 only after recorded human review of the decision. |

---

## P1O7-T09 — Close out Objective Seven and prepare the reviewed baseline candidate

| Field | Contract |
|---|---|
| Purpose | Record Objective Seven closeout, hand off the reviewed decision, and prepare a baseline candidate only when T08 supports one. |
| Dependencies | T08 reviewed; planned tasks complete or intentionally deferred; current status coherent. |
| Primary paths | `docs/phase-one/objective-seven/OBJECTIVE_SEVEN_CLOSEOUT.md`; `docs/phase-one/objective-seven/OBJECTIVE_SEVEN_HANDOFF.md`; conditional `docs/phase-one/objective-seven/PHASE_1_BASELINE_CANDIDATE.md`. |
| Allowed files | Primary paths; `docs/phase-one/objective-seven/OBJECTIVE_SEVEN_TRACKER.md`; `README.md`; `records/PROMPT_BUILD_LOG.md`; exact dated `records/prompt-build-log/YYYY-MM-DD-p1o7-t09.md`. |
| Forbidden work | No tag, Release, parent closure without explicit authorization, Phase Two implementation, or claim stronger than T08. Do not create the conditional candidate when T08 does not support it. |
| Research | Repository-internal closeout verification and live issue/status state. |
| Verification | Task completion/defer inventory; checklist/memo/closeout agreement; current-status truth; candidate limitations; parent protection; complete diff. |
| Acceptance | Closeout and handoff accurately record the decision; candidate exists only if supported; no controlled action occurs; parent close readiness is explicit rather than automatic. |
| Handoff | Conditional P1O7-T10, the next approved planning workstream, or stop. |

---

## P1O7-T10 — Conditional tag creation

| Field | Contract |
|---|---|
| Purpose | Create one exact Git tag only after a separate issue names the identifier, target commit, and authorization evidence. |
| Dependencies | T09 supports tagging; exact tag and target SHA approved; required QA and human authorization recorded. |
| Primary artifact | Git tag named in the T10 issue. No identifier is selected by this contract. |
| Allowed files | None by default. Any repository-file update requires a separate authorized task; issue and live tag state are the action record. |
| Forbidden work | No GitHub Release, retargeting, extra tags, file edits, parent closure, or readiness claim. Do not execute #194 through this task. |
| Research | Live repository verification of target commit, tag nonexistence, decision/QA evidence, and authorization. |
| Verification | Exact tag spelling; exact target SHA; tag exists once; no Release created; #194 remains separate; no file diff. |
| Acceptance | Authorized tag exists at the exact target; no other repository state changes; tag is not described as operational or public-release approval. |
| Handoff | Conditional P1O7-T11 or stop. |

---

## P1O7-T11 — Conditional GitHub Release publication

| Field | Contract |
|---|---|
| Purpose | Publish one GitHub Release only after separate authorization names the existing tag, release title, body source, and allowed assets. |
| Dependencies | Authorized tag exists; T09 candidate/release basis is current; separate Release authorization recorded. |
| Primary artifact | GitHub Release named in the T11 issue. No Release title or publication promise is selected by this contract. |
| Allowed files | None by default. File changes or generated assets require a separate authorized task. |
| Forbidden work | No tag creation, extra assets, file edits, broad public claims, implementation claims, or publication when authorization is incomplete. |
| Research | Live verification of tag, absence of conflicting Release, exact authorized notes/assets, and current limitations. |
| Verification | Release targets exact tag; title/body/assets match authorization; limitations and boundaries present; no unrelated files or releases change. |
| Acceptance | Exactly one authorized Release is published, or the task is deferred/rejected without publication; publication does not imply operational readiness or official status. |
| Handoff | Release handoff, post-release verification, or stop as named in the issue. |

## Contract completeness rule

Before any future Objective Seven task begins, its issue must resolve:

```text
task and parent issue
branch and verified base
dependencies
exact primary and supporting paths
exact allowed files
forbidden work and governing references
Tier 0 acknowledgement
exact Tier 1 selection
Tier 2 use and reason
research requirement
exact dated prompt-log path or non-applicability reason
verification methods
acceptance criteria
PR close keyword when a PR applies
parent-close behavior
handoff target
```

If an exact path, identifier, target commit, release title, or controlled action is not yet known, the task is not authorized to perform it.

## P1O7-T01 handoff

After review and merge, P1O7-T02 should create only `PHASE_1_GATE_EVIDENCE_MODEL.md` and its explicitly allowed supporting records. It must not evaluate the criteria it defines.