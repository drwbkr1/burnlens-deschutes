# BurnLens Deschutes — Phase One Objectives

## Document role

This document expands the Phase One objective summarized in `docs/roadmap/BURNLENS_BUILD_ROADMAP.md`.

It is a status-aware control document, not a declaration that Phase One is complete. Current merged trackers, audits, handoffs, and the Phase One decision memo control live gate truth.

## Phase name

**Scope, Technical Contracts, Repository Controls, and Acceptance Gate**

## Canonical objective summary

Establish the documented project identity, bounded CV task, source-feasibility posture, repository operating system, version/provenance/claims controls, and prompt-built workflow, then make an evidence-backed Phase One acceptance decision before implementation begins.

## Current status

**Active — incomplete.**

- Objectives One through Six are complete as documentation and repository-control baselines.
- Objective Seven is active and incomplete.
- P1O7-T08 is reserved for the Phase One decision memo.
- No final Phase One acceptance or release decision exists.
- Phase Two planning and all data touch remain separately gated.

## Phase purpose

Phase One converts the portfolio idea into a durable, reviewable operating baseline. It defines what BurnLens is, what the first CV task is, what evidence and sources may support it, how repository work is controlled, how every future artifact will be versioned and traced, and how the project decides whether it is ready to enter implementation.

The phase protects later work from scope drift, undocumented source assumptions, unsupported claims, untraceable outputs, and conversational context loss.

## Position in the six-phase build

| Before Phase One | Phase One creates | Phase Two may receive only after the gate |
|---|---|---|
| Portfolio concept and prior planning material | Project identity, target user, use boundaries, CV contract, source-feasibility plan, repository workflow, version/provenance/claims controls, prompt-built development protocol, acceptance evidence | A reviewed control baseline and explicit authorization route for data-intake work |

## Required outcomes

Phase One must establish:

1. one portfolio-first project identity and thesis;
2. one reference user and bounded planning-style use case;
3. one experimental binary segmentation task with a controlled fallback;
4. explicit positive, negative, and unknown/exclude handling;
5. a mask-first output and evaluation contract;
6. candidate source and AOI feasibility rules without pretending data exists;
7. issue, branch, PR, review, and prompt-log controls;
8. versioning, provenance, artifact registry, run-package, claims, and release rules;
9. a documented prompt-built development workflow;
10. an evidence matrix, audits, exit checklist, and final Phase One decision route;
11. a clear distinction between planning readiness and authorization to touch data.

## Objective set

### Objective One — Lock project identity, audience, promise, and boundaries

**Purpose:** Define BurnLens Deschutes as an experimental, portfolio-first computer vision + GEOINT project and remove obsolete sponsor, partner, field-validation, and operational framing.

**Required result:** A cohesive project identity, thesis, category, reference user, user story, AOI rationale, data premise, technical description, use boundaries, source precedence, transparency requirements, and model-card scaffold.

**Status:** Complete as a merged documentation baseline.

**Gate:** Project identity and boundary language are internally consistent; official sources govern; no data or performance is implied.

### Objective Two — Define the first CV task and output contract

**Purpose:** Specify exactly what the first model or baseline should do, what it should output, how it should be evaluated, and which failure modes and prohibited uses govern it.

**Required result:** Experimental binary semantic segmentation; active-fire or hotspot-informed mask as primary target; burn-scar fallback; positive/background/unknown handling; mask-first outputs; U-Net-style reference family; IoU primary metric; baseline comparison; explicit failure modes and warning language.

**Status:** Complete.

**Gate:** Later data and model work can proceed without ambiguity, but no implementation is authorized by this objective.

### Objective Three — Establish source, AOI, CRS, provenance, and feasibility controls

**Purpose:** Identify candidate source roles and the decision records required before any data is retained or processed.

**Required result:** Source feasibility criteria; Sentinel-2, Landsat, HLS, FIRMS, and local-context candidate roles; AOI selection criteria; access and terms planning; format/CRS rules; provenance fields; data-stack decision matrix; research validation and claims records.

**Status:** Complete and remediation-expanded as documentation-only planning.

**Gate:** Candidate roles are usable as a planning scaffold. No final AOI, imagery, labels, masks, or dataset exists.

### Objective Four — Build the repository operating system

**Purpose:** Convert project controls into repeatable issue-first repository work.

**Required result:** Issue architecture and taxonomy; project-board specification; branch and PR workflow; task and PR templates; Codex task packet; prompt/build-log controls; Phase Two intake templates; closeout and handoff standards.

**Status:** Complete as a repository-control baseline.

**Gate:** Future tasks have a controlled path from artifact contract to human-reviewed merge. Templates remain scaffolding, not evidence that data work occurred.

### Objective Five — Establish traceability, versioning, claims, reproducibility, and release control

**Purpose:** Ensure every future public artifact can be traced, reviewed, and withheld when its evidence or boundaries are insufficient.

**Required result:** Version taxonomy; top-level versioning protocol; release and tag control; provenance specification; run-package and manifest contract; artifact registry; claim-to-evidence protocol; source-precedence release gate; reproducibility and release-QA checklists.

**Status:** Complete as documentation/control planning.

**Gate:** Future artifacts have a lineage and release-control design. No tag, GitHub Release, run package, data, model, map, or public output is implied.

### Objective Six — Establish the prompt-built development protocol

**Purpose:** Make prompt-assisted work durable, issue-backed, selective in context, verifiable, reviewable, and human-governed.

**Required result:** Canonical task capsule; context-tier rules; dated prompt/build logs; named checks; diff review; task-scoped PRs; optional AI-assisted review distinct from mandatory human review; separate merge authorization; status synchronization and handoff.

**Status:** Complete as a documented, reviewable repository-control baseline.

**Gate:** Prompt-assisted agents have an executable operating route. Written policy is not represented as configured platform enforcement.

### Objective Seven — Apply the Phase One acceptance gate

**Purpose:** Audit the current control baseline, identify blockers and limitations, decide whether Phase One is acceptable, and close out the phase without overstating implementation readiness.

**Required result:** Gate evidence matrix; scope/boundary audit; technical-readiness audit; repository-control audit; baseline/release decision; remediation records; exit checklist; Phase One decision memo; required follow-up and closeout.

**Status:** Active and incomplete.

**Current known constraints:** Data touch remains blocked by incomplete before-data evidence. Full Phase One completion remains blocked by unresolved gate evidence. The final decision belongs to P1O7-T08 and subsequent controlled closeout work.

**Gate:** A reviewed human decision determines whether Phase One is accepted, accepted with limitations, remediated, or stopped. This document does not make that decision.

## Completion evidence

Phase One is complete only when:

- the Objective Seven decision memo is reviewed and merged;
- every mandatory blocker is resolved or explicitly routed according to the gate rules;
- the Phase One status is synchronized across current controls;
- the parent acceptance-gate issue is closed through its authorized sequence;
- any approved objective-baseline identifier is handled through separate tag/release controls;
- the handoff states exactly what Phase Two planning may begin and what data actions remain blocked.

Completion does not mean that data, imagery, an AOI, labels, baselines, models, metrics, runs, maps, demos, tags, or GitHub Releases exist.

## Dependencies

Phase One has no predecessor phase, but its tasks depend on:

- current merged repository truth;
- the user-authorized portfolio-first scope;
- human review distinct from agent authorship;
- issue-backed changes and explicit merge authorization.

## Non-goals

Phase One does not:

- acquire or retain imagery or other source data;
- select a final AOI geometry;
- create labels, masks, datasets, baselines, models, metrics, runs, maps, screenshots, or demos;
- validate outputs with agencies or field observations;
- make operational, emergency, adoption, impact, or performance claims;
- automatically create tags or GitHub Releases.

## Fixed boundaries

- BurnLens is experimental and portfolio-first.
- Official sources govern.
- The first CV task remains bounded binary semantic segmentation unless a human-approved objective change occurs.
- Unknown and excluded pixels must not be silently treated as background.
- Model evidence must be compared with a relevant non-model baseline.
- Every later public claim must trace to versioned evidence.
- Human review and separate merge authorization remain mandatory.

## Known risks and assumptions

- Planning controls can appear more mature than the unexecuted technical workflow; status language must keep that distinction visible.
- Candidate source feasibility may change before Phase Two access tests; current source roles are planning hypotheses.
- Repository metadata or platform state may remain inaccessible; unresolved evidence must not be converted into unsupported certainty.
- Long documentation can fragment current truth; the roadmap, current tracker, and handoff must remain synchronized through scoped tasks.

## Authority delegated to Codex

Within an authorized Phase One task, Codex may:

- inspect merged controls and repository metadata available through approved tools;
- draft audits, matrices, decision support, remediation, and status records;
- identify inconsistencies and propose bounded fixes;
- maintain roadmap and phase-document consistency when explicitly in scope;
- recommend acceptance, limitation, remediation, or stop outcomes based on evidence.

Codex may not:

- make the human Phase One acceptance decision on its own;
- treat its self-audit as human approval;
- activate Phase Two or touch data;
- create tags, Releases, settings changes, or public claims without separate authorization;
- merge its own work without the required human review and merge authorization.

## Changes requiring explicit approval

- changing the project promise, target user, CV task, fallback target, or use boundaries;
- weakening official-source precedence or traceability;
- treating incomplete evidence as passed;
- marking Phase One accepted or complete;
- authorizing Phase Two planning or data touch;
- changing release class, tag posture, access, ownership, or public status.

## Expected handoff to Phase Two

The Phase One handoff must identify:

- the reviewed acceptance outcome;
- all carried limitations and unresolved findings;
- the exact first Phase Two planning task allowed;
- whether the before-data gate is satisfied;
- which source, AOI, access, terms, CRS, provenance, registry, boundary, and prompt-log records must exist before acquisition;
- the fact that Phase Two objective documentation does not itself authorize data touch.

## Controlling source basis

Use current merged versions of:

- `AGENTS.md`
- `README.md`
- `VERSIONING.md`
- `docs/workflows/PROMPT_TO_REPO_SOP.md`
- Objective One identity and boundary documents
- Objective Two final handoff
- Objective Three handoff
- Objective Four handoff
- Objective Five handoff
- Objective Six handoff
- Objective Seven tracker, evidence matrix, audits, exit checklist, and future decision memo
