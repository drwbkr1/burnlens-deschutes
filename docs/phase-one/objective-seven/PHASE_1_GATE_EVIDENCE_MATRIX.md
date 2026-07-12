# Phase One Gate Evidence Matrix

## Status

| Field | Current state |
|---|---|
| Task | P1O7-T02 — Define the Phase One gate evidence model |
| Task issue | #251 |
| Parent issue | #246 — open |
| Branch | `p1o7t02b` |
| Artifact role | Evidence requirements and decision-routing model only |
| Phase One acceptance | Not evaluated |
| Criterion verdicts | Every gate criterion remains `not evaluated` in this task |
| Data-touch authorization | Not granted |
| Release identifier or class | Not decided |
| Tag | Not created or authorized by this task |
| GitHub Release | Not created or authorized by this task |

This matrix converts the original Phase One exit statements into measurable evidence requirements. It does not audit the evidence, assign a verdict, remediate a finding, authorize controlled work, or make the Phase One decision.

## Core evidence rule

A file, tracker row, closeout sentence, specification, proposed identifier, release-note draft, issue, or old approval statement is never sufficient by itself to produce `meets criterion`.

A criterion may move out of `not evaluated` only when its responsible audit or review task:

1. identifies the exact current evidence;
2. applies the criterion definition and minimum evidence set;
3. checks evidence authority and currency;
4. records disqualifying conditions and limitations;
5. assigns a status using this matrix;
6. records blocker severity;
7. receives human review.

Missing, stale, contradictory, archival-only, or proposal-only evidence cannot be silently treated as passing.

## Original criterion mapping

| Original ID | Original gate statement | Matrix rows | Primary future evidence owner |
|---|---|---|---|
| O1 | Project name and thesis are locked. | G01 | P1O7-T03 |
| O2 | Use boundaries are written. | G02 | P1O7-T03 |
| O3 | The computer-vision task is bounded. | G03 | P1O7-T04 |
| O4 | Data feasibility is researched. | G04; F04-A | P1O7-T04; future data authorization task for F04-A |
| O5 | Repository structure exists. | G05 | P1O7-T05 |
| O6 | GitHub issues and project-board controls exist. | G06-A; G06-B; F06-C | P1O7-T05 |
| O7 | A versioning protocol exists. | G07 | P1O7-T05 |
| O8 | A prompt-built workflow protocol exists. | G08 | P1O7-T05 |
| O9 | A documentation skeleton exists. | G09 | P1O7-T05 |
| O10 | A first release tag exists. | G10; F10-R | P1O7-T05, P1O7-T06, and an authorized P1O7-T10 for tag creation |
| O11 | No sponsor, partner, field-validation, or agency-endorsement language remains in the active working scope. | G11 | P1O7-T03 |

Rows beginning with `G` are gate criteria or explicit gate subcriteria. Rows beginning with `F` are supporting or controlled-action facts that preserve a required distinction but do not silently add a new gate requirement.

## Evidence authority hierarchy

Use the highest applicable authority. Lower-ranked evidence may support history or interpretation but cannot override current evidence.

| Rank | Evidence class | Authority rule |
|---:|---|---|
| 1 | Official or authoritative source, when wildfire, emergency, evacuation, hazard, transportation, incident, or public-safety context is involved | Official sources govern. BurnLens evidence cannot override them. |
| 2 | Live GitHub repository state | Current issues, pull requests, branches, commits, tags, Releases, and observable Project state must be verified live during the responsible audit or action task. |
| 3 | Current merged governing control on `main` | The file must be merged, not superseded, internally coherent, and still designated as governing. |
| 4 | Current task, review, and merge evidence | Issue, task capsule, branch diff, PR, review outcome, merge record, and synchronized prompt/build records prove bounded workflow events. |
| 5 | Current research record | The responsible audit must review the record for relevance, unresolved caveats, and staleness. |
| 6 | Archival, superseded, or historical material | May explain history only. It cannot satisfy an active criterion unless a current merged control explicitly adopts it. |

When evidence classes conflict, the responsible audit must record the conflict. A criterion cannot be `meets criterion` while a material authority conflict is unresolved.

## Evidence currency classes

There is no universal calendar age for every evidence type.

| Currency class | Acceptable evidence age or currency rule |
|---|---|
| Current merged control | Current on `main`, not superseded, and still governing at the audit date. Recheck after any material merge that changes its scope or role. |
| Live GitHub state | Reverified during the responsible audit, decision, or controlled-action task. Old screenshots, issue text, or tracker statements do not prove current state. |
| Current-status record | Synchronized after the latest material merge affecting the stated status. A stale README, tracker, index, or prompt log cannot establish current truth. |
| Research record | Reviewed at the responsible audit date for source availability, relevance, unresolved caveats, and whether later project decisions changed the conclusion. |
| Static project decision | Current until explicitly superseded, but the audit must verify that no active merged artifact contradicts it. |
| Archival evidence | Historical only unless a current merged control explicitly adopts it. No age converts archival evidence into active authority. |
| Tag or GitHub Release existence | Verified from live repository state at the release audit, controlled action, and final closeout review. A proposed identifier or draft release note is not existence evidence. |

## Status vocabulary

| Status | Meaning |
|---|---|
| `not evaluated` | No authorized audit or review has applied this matrix to the criterion. This is the status of every criterion in P1O7-T02. |
| `evidence incomplete` | One or more required evidence items are missing, stale, inaccessible, contradictory, or below the required authority. |
| `meets criterion` | The minimum evidence set is current, authoritative enough, coherent, human-reviewed, and no mandatory blocker remains. |
| `meets with limitation` | The minimum evidence set is sufficient, but a recorded non-blocking limitation remains with an owner and consequence. |
| `does not meet` | A disqualifying condition exists or evidence demonstrates that the measurable definition is not satisfied. |
| `deferred` | The responsible decision intentionally postpones the criterion with rationale, consequence, and owner. Deferred is never an automatic pass. |
| `not applicable` | The matrix and responsible human review establish that the criterion does not apply. Original gate criteria are presumed applicable unless the Phase One decision explicitly determines otherwise. |

Supporting and controlled-action fact rows may use the same vocabulary for consistency, but their status does not by itself change the Phase One gate decision.

## Blocker classes

| Blocker class | Effect |
|---|---|
| `mandatory blocker` | Prevents a full Phase One completion claim while unresolved. It may also prevent planning-only authorization when the definition says so. |
| `conditional blocker` | Blocks a named downstream action or decision lane but may allow a narrower planning-only outcome when explicitly documented. |
| `non-blocking limitation` | Does not block the applicable decision, but must be recorded with consequence and owner. |
| `informational or supporting fact` | Preserves a distinction or current fact. It does not become a gate requirement without explicit parent-level authorization. |

A criterion cannot be `meets criterion` when its mandatory blocker is unresolved. `Meets with limitation` is allowed only for a non-blocking limitation, not as a substitute for missing mandatory evidence.

## Readiness lanes

| Readiness lane | Evidence meaning | What it does not authorize |
|---|---|---|
| Phase Two planning readiness | Phase One scope, boundaries, CV task, feasibility research, repository controls, and documentation are sufficient to plan the next workstream. | Data access, AOI creation, downloads, labels, masks, baselines, models, runs, maps, or public outputs. |
| Data-touch readiness | A later issue explicitly authorizes the exact data action and the before-data records exist: source/access/terms, format and CRS precheck, AOI record, provenance, registry classification, source-precedence review, use-boundary review, branch/PR scope, and prompt log where required. | Model readiness, output quality, operational use, or public release. |
| Executed technical readiness | Authorized data, method, model, run, evaluation, and output evidence actually exists and has been reviewed. | Official, operational, emergency, field-validation, agency-endorsement, or decision-authority claims. |

Phase One planning readiness must not be described as data-touch readiness. Data-touch readiness must not be described as executed technical readiness.

## Required factual separations

| Fact A | Fact B | Rule |
|---|---|---|
| A Project board specification exists. | A GitHub Project board is configured and observable. | The specification is a planning/control artifact. Only live state can prove configuration. F06-C is supporting unless the parent explicitly makes live configuration a gate requirement. |
| Data feasibility has been researched. | A later task is authorized to touch data. | G04 can be satisfied without F04-A. F04-A is mandatory before data touch, not before planning-only approval. |
| A Git tag exists. | A GitHub Release exists. | G10 requires live tag evidence. F10-R remains separate and optional unless explicitly authorized and required. |
| Active working-scope evidence exists. | Archival or superseded evidence exists. | Only active current evidence can satisfy an active criterion. Archival evidence may explain history. |
| A documentation or control artifact exists. | The artifact is current, coherent, reviewed, and sufficient. | Existence is only one evidence element. Sufficiency requires the full minimum evidence set and audit. |
| Phase Two planning readiness exists. | Data-touch or executed technical readiness exists. | These are separate lanes with separate authorization and evidence. |

## Criterion evidence requirements

### G01 — Project name and thesis are locked

| Field | Requirement |
|---|---|
| Original parent | O1 — Project name and thesis are locked. |
| Criterion class | Gate criterion |
| Measurable definition | One current project name and one concise thesis are used consistently across active merged scope and status artifacts, with no unresolved rename, competing active thesis, or legacy project identity presented as current. |
| Qualifying evidence and minimum set | Exact current name and thesis text; active-scope file inventory; consistency review across current merged Tier 0 scope/status artifacts; human-reviewed P1O7-T03 audit record. |
| Evidence authority | Current merged scope controls and current-status artifacts on `main`, interpreted by the T03 audit. Archival project names or historical funding material are not active authority. |
| Disqualifying condition | Conflicting active names or theses; unresolved placeholder language; an active file presents a legacy identity as current; no exact thesis can be identified. |
| Currency rule | Current merged controls at T03 review time, with current-status records synchronized after the latest material scope merge. |
| Evidence owner | P1O7-T03; compiled by P1O7-T07; decision owned by P1O7-T08. |
| Allowed status vocabulary | Full gate vocabulary. |
| Blocker rule | Conflicting or unlocked identity is a `mandatory blocker`. Missing inventory is `evidence incomplete`. |
| Future verdict task | P1O7-T03 |
| Anti-auto-pass rule | The presence of a project-name string in one document does not prove a locked name or thesis. |
| P1O7-T02 status | `not evaluated` |

### G02 — Use boundaries are written and current

| Field | Requirement |
|---|---|
| Original parent | O2 — Use boundaries are written. |
| Criterion class | Gate criterion |
| Measurable definition | Active merged controls state allowed uses, prohibited uses, non-operational status, required warnings, and official-source precedence without weaker contradictory language in active scope. |
| Qualifying evidence and minimum set | Current `USE_BOUNDARIES.md`; current `SOURCE_PRECEDENCE.md`; active-scope consistency inventory; T03 review of current scope/status language; human review. |
| Evidence authority | Current merged boundary and source-precedence controls. Official sources govern where applicable. |
| Disqualifying condition | Missing boundary or precedence rule; active operational, emergency, official, field-validation, endorsement, evacuation, routing, tactical, or incident-command implication; contradictory active language. |
| Currency rule | Current on `main` and rechecked after any material public-scope or use-boundary change. |
| Evidence owner | P1O7-T03; compiled by T07; decision owned by T08. |
| Allowed status vocabulary | Full gate vocabulary. |
| Blocker rule | Missing or materially contradictory boundaries are a `mandatory blocker`. Minor non-contradictory wording variance may be a `non-blocking limitation`. |
| Future verdict task | P1O7-T03 |
| Anti-auto-pass rule | A boundary file existing is insufficient if active scope contradicts it or omits required precedence. |
| P1O7-T02 status | `not evaluated` |

### G03 — The computer-vision task is bounded

| Field | Requirement |
|---|---|
| Original parent | O3 — The computer-vision task is bounded. |
| Criterion class | Gate criterion |
| Measurable definition | The planned CV problem identifies the target task, target/fallback distinction, output contract, imagery and label assumptions, baseline comparison, evaluation approach, failure modes, and use boundaries clearly enough for Phase Two planning. |
| Qualifying evidence and minimum set | Current Objective Two task-definition, class, output-contract, assumptions, baseline, model-family, metrics, failure-mode, and CV-use-boundary artifacts; T04 coherence review; human review. |
| Evidence authority | Current merged technical and CV controls. Plans may establish planning readiness only; they do not prove an executed model or run. |
| Disqualifying condition | Ambiguous target; undefined output; target and fallback conflated; missing baseline comparison; missing failure/use boundaries; claims of model or operational readiness without evidence. |
| Currency rule | Current merged controls at T04 review time and rechecked if the task, output contract, imagery assumptions, or label assumptions changed. |
| Evidence owner | P1O7-T04; compiled by T07; decision owned by T08. |
| Allowed status vocabulary | Full gate vocabulary. |
| Blocker rule | An unbounded task or unresolved target/output contradiction is a `mandatory blocker` for planning readiness. |
| Future verdict task | P1O7-T04 |
| Anti-auto-pass rule | The number of CV documents does not prove that the task is coherent or bounded. |
| P1O7-T02 status | `not evaluated` |

### G04 — Data feasibility is researched

| Field | Requirement |
|---|---|
| Original parent | O4 — Data feasibility is researched. |
| Criterion class | Gate criterion |
| Measurable definition | Repository research identifies plausible source candidates, access constraints, terms or licensing considerations, imagery/reference suitability, AOI criteria, format/CRS risks, provenance fields, and unresolved feasibility blockers sufficiently for planning. |
| Qualifying evidence and minimum set | Current Objective Three feasibility criteria, candidate inventory, source-access reviews, imagery/reference reviews, AOI criteria, format/CRS precheck plan, provenance specification, decision matrix, and research-validation record; T04 review. |
| Evidence authority | Current merged research and feasibility controls, reviewed for staleness and unresolved caveats at T04. |
| Disqualifying condition | No plausible source path; unsupported access assumptions; unresolved terms, format, CRS, coverage, timing, or provenance issues that prevent a feasible planning path; research is stale or contradicted. |
| Currency rule | Research is reviewed at T04 for source availability, relevance, and changed project assumptions. No fixed calendar age automatically makes it current. |
| Evidence owner | P1O7-T04; compiled by T07; decision owned by T08. |
| Allowed status vocabulary | Full gate vocabulary. |
| Blocker rule | No feasible planning path is a `mandatory blocker`. A known manageable source limitation may be a `non-blocking limitation` with an owner. |
| Future verdict task | P1O7-T04 |
| Anti-auto-pass rule | A source inventory or research document existing does not prove feasibility; the combined evidence must support a plausible path and state blockers. |
| P1O7-T02 status | `not evaluated` |

### F04-A — Authorization to touch data

| Field | Requirement |
|---|---|
| Original parent | O4 distinction — separate feasibility research from data-touch authorization. |
| Criterion class | Controlled-action fact; not a new Phase One gate requirement |
| Measurable definition | A later issue explicitly authorizes the exact data action and all before-data records required by the SOP exist and are reviewable. |
| Qualifying evidence and minimum set | Exact task issue and branch/PR scope; source/access/terms record; format/CRS precheck; AOI record and ID; provenance/traceability record; registry classification; source-precedence and use-boundary review; prompt log when required. |
| Evidence authority | Live issue and repository evidence for the future data task. |
| Disqualifying condition | Feasibility documents only; implied permission; missing source/access/AOI/provenance records; authorization for a different action. |
| Currency rule | Verified immediately before the authorized data action and rechecked when scope or sources change. |
| Evidence owner | Future Phase Two intake or data task; T04 and T08 preserve the distinction. |
| Allowed status vocabulary | Same vocabulary for factual consistency, but the status is not itself the Phase One gate decision. |
| Blocker rule | `mandatory blocker` for touching data; `informational or supporting fact` for planning-only Phase One evaluation. |
| Future verdict task | Future explicitly authorized data task |
| Anti-auto-pass rule | G04 feasibility evidence can never substitute for F04-A authorization. |
| P1O7-T02 status | `not evaluated` |

### G05 — Repository structure exists and is coherent

| Field | Requirement |
|---|---|
| Original parent | O5 — Repository structure exists. |
| Criterion class | Gate criterion |
| Measurable definition | Required canonical directories, controls, templates, records, and objective paths exist on current `main`, use consistent references, and do not create conflicting sources of truth. |
| Qualifying evidence and minimum set | Current repository path manifest; canonical-role mapping; link/path inspection; duplicate-source review; T05 live repository audit; human review. |
| Evidence authority | Live repository tree and current merged controls. README descriptions do not override actual paths. |
| Disqualifying condition | Missing canonical paths; broken required references; contradictory duplicate controls; required artifacts exist only on an unmerged branch. |
| Currency rule | Live repository state at T05, rechecked after material structural merges. |
| Evidence owner | P1O7-T05; compiled by T07; decision owned by T08. |
| Allowed status vocabulary | Full gate vocabulary. |
| Blocker rule | Missing canonical structure or conflicting sources of truth is a `mandatory blocker`; minor navigation debt may be a `non-blocking limitation`. |
| Future verdict task | P1O7-T05 |
| Anti-auto-pass rule | A README tree or documentation skeleton list does not prove that the paths exist or agree. |
| P1O7-T02 status | `not evaluated` |

### G06-A — GitHub issue controls and authorization records exist

| Field | Requirement |
|---|---|
| Original parent | O6 — GitHub issues and project-board controls exist. |
| Criterion class | Gate subcriterion |
| Measurable definition | The repository has a current issue-first task contract, parent/task separation, task-scoped close behavior, and observable issues/PR records demonstrating bounded authorization. |
| Qualifying evidence and minimum set | Current issue template and workflow controls; live parent and task issues; representative task PR with task-only close keyword; T05 live-state review. |
| Evidence authority | Live GitHub issue/PR state plus current merged workflow controls. |
| Disqualifying condition | No issue authorization mechanism; task work not traceable to issues; parent closure not protected; written template exists but no live bounded records can be verified. |
| Currency rule | Live state reverified during T05. |
| Evidence owner | P1O7-T05; compiled by T07; decision owned by T08. |
| Allowed status vocabulary | Full gate vocabulary. |
| Blocker rule | Missing authorization records or unsafe close behavior is a `mandatory blocker`. |
| Future verdict task | P1O7-T05 |
| Anti-auto-pass rule | An issue-template file alone does not prove the issue-first workflow is present and reviewable. |
| P1O7-T02 status | `not evaluated` |

### G06-B — Project board specification and controls exist

| Field | Requirement |
|---|---|
| Original parent | O6 — GitHub issues and project-board controls exist. |
| Criterion class | Gate subcriterion |
| Measurable definition | A current merged specification defines the board's intended role, fields, views, statuses, source-of-truth boundaries, and automation limits without claiming that a live board is configured. |
| Qualifying evidence and minimum set | Current `PROJECT_BOARD_SPEC.md`; T05 review that it is merged, current enough for its role, and explicitly distinguishes planning specification from configuration. |
| Evidence authority | Current merged project-board specification and current workflow controls. |
| Disqualifying condition | Specification missing or superseded; no source-of-truth distinction; specification falsely represented as live configuration or enforcement. |
| Currency rule | Current merged control at T05; recheck if issue taxonomy or workflow architecture materially changes. |
| Evidence owner | P1O7-T05; compiled by T07; decision owned by T08. |
| Allowed status vocabulary | Full gate vocabulary. |
| Blocker rule | Missing or materially misleading board controls are a `mandatory blocker` for O6. |
| Future verdict task | P1O7-T05 |
| Anti-auto-pass rule | The specification can support G06-B only; it cannot prove F06-C. |
| P1O7-T02 status | `not evaluated` |

### F06-C — A GitHub Project board is configured and observable

| Field | Requirement |
|---|---|
| Original parent | O6 distinction — separate a board specification from live configuration. |
| Criterion class | Supporting fact; not an automatic gate requirement |
| Measurable definition | A specific live Project board can be observed and linked to the repository or workstream during T05, with no inference from specification text alone. |
| Qualifying evidence and minimum set | Live board identifier or URL and observable state recorded by T05; relationship to the repository/workstream stated. |
| Evidence authority | Live GitHub state at T05. |
| Disqualifying condition | Specification-only evidence; an inaccessible or unrelated board; an old screenshot or tracker statement without live verification. |
| Currency rule | Reverified during T05 or any decision that relies on it. |
| Evidence owner | P1O7-T05 |
| Allowed status vocabulary | Same vocabulary for factual consistency, but the result is supporting unless the parent explicitly promotes it. |
| Blocker rule | `informational or supporting fact` by default. It cannot silently become a mandatory gate requirement. |
| Future verdict task | P1O7-T05 |
| Anti-auto-pass rule | `PROJECT_BOARD_SPEC.md` is never evidence that a live board exists. |
| P1O7-T02 status | `not evaluated` |

### G07 — A versioning protocol exists and is coherent

| Field | Requirement |
|---|---|
| Original parent | O7 — A versioning protocol exists. |
| Criterion class | Gate criterion |
| Measurable definition | Current merged controls define identifier classes, increment/creation rules, traceability, and the rule that versions and tags do not imply readiness; adjacent release controls do not contradict the protocol. |
| Qualifying evidence and minimum set | Current `VERSIONING.md`; current version taxonomy and release controls; T05 consistency review; human review. |
| Evidence authority | Current merged versioning and release-control artifacts. |
| Disqualifying condition | Missing protocol; conflicting identifier rules; versions represented as readiness; proposed and created states conflated. |
| Currency rule | Current merged controls at T05 and rechecked when taxonomy or release control changes. |
| Evidence owner | P1O7-T05; release-class implications reviewed by T06; compiled by T07. |
| Allowed status vocabulary | Full gate vocabulary. |
| Blocker rule | Missing or contradictory protocol is a `mandatory blocker`. Minor example drift may be a `non-blocking limitation` only when the rule remains unambiguous. |
| Future verdict task | P1O7-T05 |
| Anti-auto-pass rule | A `VERSIONING.md` path existing does not prove a coherent or current protocol. |
| P1O7-T02 status | `not evaluated` |

### G08 — A prompt-built workflow protocol exists and is usable

| Field | Requirement |
|---|---|
| Original parent | O8 — A prompt-built workflow protocol exists. |
| Criterion class | Gate criterion |
| Measurable definition | Current controls define and align issue authorization, task capsule, branch/base, allowed files, selective context, research, prompt logging, named checks, diff review, task-only PR closure, human review, merge authorization, synchronization, and handoff. |
| Qualifying evidence and minimum set | Current SOP, AGENTS instructions, contribution guide, issue form, task packet, prompt-log protocol/template, PR/review controls, and representative live task records; T05 cohesion review. |
| Evidence authority | Current merged workflow controls plus live issue/PR/merge evidence. |
| Disqualifying condition | Missing workflow stage; contradictory controls; AI/author review treated as human approval; written policy represented as platform enforcement; no representative bounded record. |
| Currency rule | Current merged controls and live representative records at T05. |
| Evidence owner | P1O7-T05; compiled by T07; decision owned by T08. |
| Allowed status vocabulary | Full gate vocabulary. |
| Blocker rule | Missing authorization, review, or merge separation is a `mandatory blocker`. Minor wording drift may be a `non-blocking limitation` only when execution remains unambiguous. |
| Future verdict task | P1O7-T05 |
| Anti-auto-pass rule | A workflow protocol document alone is insufficient without aligned controls and reviewable application records. |
| P1O7-T02 status | `not evaluated` |

### G09 — A documentation skeleton exists and is coherent

| Field | Requirement |
|---|---|
| Original parent | O9 — A documentation skeleton exists. |
| Criterion class | Gate criterion |
| Measurable definition | Current project scope, boundaries, CV planning, feasibility research, repository controls, Objective Seven controls, templates, and traceability records occupy known canonical paths with clear roles and navigation. |
| Qualifying evidence and minimum set | T05 path/category manifest; canonical-role mapping; current tracker and status references; broken-link/path review; duplicate-source review; human review. |
| Evidence authority | Live repository tree and current merged canonical-role controls. |
| Disqualifying condition | Missing core documentation class; unclear canonical role; active duplicate source of truth; required path references do not resolve. |
| Currency rule | Live repository state at T05 and rechecked after material documentation restructuring. |
| Evidence owner | P1O7-T05; compiled by T07; decision owned by T08. |
| Allowed status vocabulary | Full gate vocabulary. |
| Blocker rule | Missing core documentation classes or conflicting canonical roles are a `mandatory blocker`; minor navigation gaps may be a `non-blocking limitation`. |
| Future verdict task | P1O7-T05 |
| Anti-auto-pass rule | A folder or placeholder file does not prove a coherent documentation skeleton. |
| P1O7-T02 status | `not evaluated` |

### G10 — A first release tag exists

| Field | Requirement |
|---|---|
| Original parent | O10 — A first release tag exists. |
| Criterion class | Gate criterion and controlled-action criterion |
| Measurable definition | A Git tag with the approved Phase One baseline identifier exists in live repository state, targets the exact reviewed `main` commit authorized for tagging, and is supported by the applicable identifier/release decision and QA evidence. |
| Qualifying evidence and minimum set | Live tag name and target commit; T06 identifier/release-class decision; reviewed baseline candidate and QA evidence; exact T10 issue and authorization if tag creation occurs; post-tag live verification. |
| Evidence authority | Live Git tag state plus current approved decision and authorization records. |
| Disqualifying condition | Tag absent; proposed identifier only; release-note draft only; wrong or unreviewed target; identifier not approved; tag created without exact authorization. |
| Currency rule | Verified live at T05/T06 for initial state and again immediately after any T10 action and before parent closure. |
| Evidence owner | T05 verifies initial state; T06 decides identifier/class; T10 may create and verify the tag; T07/T08/T09 must carry the unresolved status accurately. |
| Allowed status vocabulary | Full gate vocabulary. |
| Blocker rule | An absent or unauthorized tag is a `mandatory blocker` to claiming Phase One complete. T08 may only authorize a narrower planning outcome with an explicit condition if permitted by its decision rules. |
| Future verdict task | Initial evidence: P1O7-T05 and T06. Final factual satisfaction: an explicitly authorized P1O7-T10 plus post-tag closeout verification. |
| Anti-auto-pass rule | A proposed tag, release-note draft, issue, or identifier string cannot satisfy G10. |
| P1O7-T02 status | `not evaluated` |

### F10-R — A GitHub Release exists

| Field | Requirement |
|---|---|
| Original parent | O10 distinction — separate tag existence from GitHub Release existence. |
| Criterion class | Controlled-action fact; not an automatic Phase One gate requirement |
| Measurable definition | A specific GitHub Release has been published from an authorized tag under a separate explicit Release authorization. |
| Qualifying evidence and minimum set | Live Release record; associated tag; separate T11 issue and authorization; reviewed Release body and boundary/QA evidence. |
| Evidence authority | Live GitHub Release state and T11 authorization records. |
| Disqualifying condition | Tag only; release-note document only; draft text; implied publication; Release published without separate authorization. |
| Currency rule | Verified live during T11 and any final status review that mentions publication. |
| Evidence owner | P1O7-T11 if separately authorized |
| Allowed status vocabulary | Same vocabulary for factual consistency, but the result is not required for G10 unless T06/T08 explicitly says otherwise. |
| Blocker rule | `informational or supporting fact` by default. Absence of a GitHub Release does not make an existing authorized tag absent. |
| Future verdict task | P1O7-T11 if authorized |
| Anti-auto-pass rule | A tag or release-note file does not prove a GitHub Release exists. |
| P1O7-T02 status | `not evaluated` |

### G11 — Prohibited legacy relationship and validation language is absent from active working scope

| Field | Requirement |
|---|---|
| Original parent | O11 — No sponsor, partner, field-validation, or agency-endorsement language remains in the active working scope. |
| Criterion class | Gate criterion |
| Measurable definition | Active current project, scope, status, and public-facing repository language contains no unsupported sponsor, partner, fiscal-sponsor, field-validation, agency-review, or agency-endorsement representation. Archival material is clearly historical and is not presented as current authority. |
| Qualifying evidence and minimum set | Explicit active-scope inventory; repository search and manual review by T03; exact findings and exclusions; classification of archival/superseded material; human review. |
| Evidence authority | Current merged active-scope artifacts. Archival files, old issues, PRs, closeouts, handoffs, and historical logs may explain history but cannot satisfy or contradict the active-scope result unless current files present them as active. |
| Disqualifying condition | Unsupported relationship or validation language in active scope; archival language surfaced as current; active status files link to or repeat unsupported claims without historical framing. |
| Currency rule | Current `main` at T03 review time and rechecked after material scope or public-copy changes. |
| Evidence owner | P1O7-T03; compiled by T07; decision owned by T08. |
| Allowed status vocabulary | Full gate vocabulary. |
| Blocker rule | Unsupported active sponsor, partner, field-validation, or agency-endorsement language is a `mandatory blocker`. Clearly archived historical material is not a blocker when excluded from active scope. |
| Future verdict task | P1O7-T03 |
| Anti-auto-pass rule | An old closeout statement that says legacy language was removed is not sufficient; T03 must inspect current active scope. |
| P1O7-T02 status | `not evaluated` |

## Gate aggregation and decision routing

1. P1O7-T03, T04, and T05 assign evidence-backed statuses only for their authorized criteria and facts.
2. P1O7-T06 decides the baseline identifier and release class; it does not create a tag.
3. P1O7-T07 assembles the exit checklist from reviewed evidence. Missing evidence remains `evidence incomplete`.
4. P1O7-T08 owns the Phase One decision and must distinguish:
   - planning-only approval;
   - approval with conditions;
   - data-touch consideration subject to a later exact authorization;
   - block.
5. P1O7-T09 records the reviewed decision and prepares a baseline candidate only when supported.
6. P1O7-T10 may create a tag only under an exact separate authorization.
7. P1O7-T11 may publish a GitHub Release only under a separate exact authorization.
8. Parent #246 cannot close while a mandatory blocker to Phase One completion remains unresolved.

## Sequencing limitation to preserve

The original gate includes G10, a live first release tag. The current task sequence places the Phase One decision and closeout preparation before conditional tag creation. Therefore:

- T07 and T08 must report G10 accurately if the tag is still absent;
- a planning-only or conditional decision must not be rewritten as full Phase One completion;
- after any authorized T10 tag creation, live tag state must be reverified and current-status/closeout records must be synchronized before parent #246 can close;
- P1O7-T02 does not change the task sequence or authorize that synchronization.

## P1O7-T02 boundary and handoff

Safe claim:

> BurnLens has a defined Phase One evidence model that requires current, authoritative, human-reviewed evidence and prevents document-existence-only passing.

Unsupported claims:

- Phase One has passed.
- Any criterion meets the gate.
- Phase Two data work is authorized.
- A Project board is configured because a specification exists.
- Data feasibility research authorizes data access.
- A proposed tag or release note proves a tag exists.
- A tag proves a GitHub Release exists.
- BurnLens is official, operational, field-validated, agency-endorsed, emergency-ready, or suitable for public-safety decisions.

After review, merge, and any materially required status synchronization, hand off to:

```text
P1O7-T03 — Audit project identity, boundaries, and active-scope language
```

T03 must apply this matrix only to its authorized scope and must not silently remediate source artifacts.
