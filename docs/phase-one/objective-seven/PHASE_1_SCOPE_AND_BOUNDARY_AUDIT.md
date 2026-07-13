# Phase One Scope and Boundary Audit

## Status

| Field | Current state |
|---|---|
| Task | P1O7-T03 — Audit project identity, boundaries, and active-scope language |
| Task issue | #257 |
| Parent issue | #246 — open and protected |
| Branch / base | `p1o7t03b` / `main` at `103b7078bbe4ca81b4ac4a10437d1aad7c4c6d0c` |
| Technical-repository evidence ref | `drwbkr1/burnlens-deschutes@103b7078bbe4ca81b4ac4a10437d1aad7c4c6d0c` |
| Public-site source evidence ref | `drwbkr1/burnlens-site@deece3782e4edd72e5afd61f9fe05e681d769661` |
| Deployed-site inspection | `https://burnlensproject.org`, inspected 2026-07-12 |
| Audit scope | G01, G02, and G11 only |
| Phase One decision | Not made by this audit |
| Remediation | Not performed |
| Human review | Pending |

This audit applies the merged evidence matrix to project identity, thesis, use boundaries, source precedence, and prohibited legacy relationship or validation language. It records findings only. It does not edit audited sources, approve public claims, make the final Phase One decision, or authorize remediation, data work, a tag, or a GitHub Release.

## Governing evidence rules

The matrix requires current, authoritative, human-reviewed evidence rather than document existence alone. For this audit:

- current merged technical controls on `main` govern the technical repository;
- current public-site source and rendered copy are active evidence because the technical README identifies the site as the public surface;
- archival, superseded, and historical material is excluded unless an active surface presents or relies on it as current;
- a negative guardrail does not cure a stronger affirmative capability or relationship claim elsewhere on the same active surface;
- criterion statuses below are author-audit findings pending human review and are not the final Phase One gate decision.

## Exact active-scope inventory

### Governing and current-status surfaces in `burnlens-deschutes`

All entries use ref `main` at `103b7078bbe4ca81b4ac4a10437d1aad7c4c6d0c`.

| Path | Role | Classification | Inclusion rationale |
|---|---|---|---|
| `AGENTS.md` | Project identity, boundaries, current workflow routing | Active governing control | Contains the explicit project thesis, mandatory warning, and current-phase statement. |
| `README.md` | Public repository identity, current status, public-site routing | Active current-status surface | Defines the project and identifies `burnlensproject.org` as the public surface. |
| `VERSIONING.md` | Version and readiness boundaries | Active governing control | Repeats the experimental portfolio posture and blocks readiness implications. |
| `docs/objective-one/TECHNICAL_DESCRIPTION.md` | Technical identity, workflow, output and use limits | Active governing control | Defines the technical thesis and identifies the website/demo layer. |
| `docs/objective-one/USE_BOUNDARIES.md` | Allowed/prohibited uses and required warnings | Active governing control | Primary G02 authority. |
| `docs/objective-one/SOURCE_PRECEDENCE.md` | Official-source precedence | Active governing control | Primary source-precedence authority. |
| `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md` | Workflow and documentation-only boundaries | Active workflow control | Retained by the SOP for later tasks and includes boundary language. |
| `docs/phase-one/objective-five/OBJECTIVE_FIVE_HANDOFF.md` | Latest safe control handoff | Active handoff control | Preserves experimental posture, source precedence, and unsupported-claim exclusions. |
| `records/PROMPT_BUILD_LOG.md` | Canonical current prompt-log index and status statement | Active current-status surface | Records the active objective and next task. |
| `docs/phase-one/objective-seven/OBJECTIVE_SEVEN_TRACKER.md` | Current Objective Seven state | Active current-status surface | Owns current task ordering and gate state. |
| `docs/phase-one/objective-seven/PHASE_1_GATE_EVIDENCE_MATRIX.md` | Criterion definitions and authority rules | Active governing control | Defines G01, G02, and G11. |
| `docs/phase-one/objective-two/CV_USE_BOUNDARIES.md` | CV and public-site boundaries | Active governing control | Defines mandatory warnings and prohibited public-site positioning. |
| `docs/phase-one/objective-five/OBJECTIVE_FIVE_CLAIMS_CHECK.md` | Safe, caveated, and unsupported claim inventory | Active governing control | Defines the required experimental public posture and unsupported capability claims. |
| `docs/phase-one/objective-five/CLAIM_TRACEABILITY_PROTOCOL.md` | Claim-to-evidence and public-use gate | Active governing control | Requires evidence, warnings, and release status before public claims. |

### Public-site source and deployed surfaces

All source entries use default branch `main` at `deece3782e4edd72e5afd61f9fe05e681d769661`.

| Repository or URL | Path / surface | Role | Classification | Inclusion rationale |
|---|---|---|---|---|
| `drwbkr1/burnlens-site` | `README.md` | Site identity | Active public-source evidence | Describes BurnLens as a public-interest wildfire planning support initiative. |
| `drwbkr1/burnlens-site` | `app/layout.tsx` | Page title, metadata, social descriptions | Active public-source evidence | Publishes the site's thesis and planning-ready capability framing. |
| `drwbkr1/burnlens-site` | `app/page.tsx` | Landing-page body copy | Active public-source evidence | Contains identity, capability, pilot, partner, reviewer, sponsor, and boundary language. |
| `https://burnlensproject.org` | Rendered landing page | Deployed public copy | Active public-facing evidence | Rendered text materially matches the source passages inspected. |

No other rendered-copy source file was identified. Contact-route implementation and styling files do not contain additional project identity, thesis, relationship, validation, or use-boundary copy and were excluded from criterion evidence.

## Archive exclusion

The audit did not open or treat old issues, old PR bodies, historical prompt logs, completed-objective closeouts, external FireSight/funder/pilot planning documents, or superseded drafts as active authority.

No `FireSight` name was found in the active inventory. Archived FireSight, funder, sponsorship, reviewer, partner, and pilot material remains outside cleanup unless an active surface presents it as current. The public site's pilot, sponsor, partner, and reviewer wording is evaluated because it is active source and deployed copy, not because an archival source exists.

Tier 2 was not used.

## Research and search method

### Repository and source verification

1. Verified `burnlens-deschutes` current `main` as `103b7078bbe4ca81b4ac4a10437d1aad7c4c6d0c`.
2. Created `p1o7t03b` from that exact commit.
3. Verified `burnlens-site` current default-branch head as `deece3782e4edd72e5afd61f9fe05e681d769661`.
4. Fetched and manually reviewed the exact active files listed above.
5. Inspected `https://burnlensproject.org` rendered text on 2026-07-12.
6. Compared rendered passages with `burnlens-site/app/layout.tsx` and `app/page.tsx`.

### Lexical-search limitation and fallback

Connector code-search attempts for `FireSight`, `sponsor`, and the known-positive control term `experimental` returned zero results. Because the control term is present in current files, repository code search was treated as unavailable or unreliable for this audit.

The authoritative method was therefore a case-insensitive manual lexical review of the 14 exact technical-repository surfaces, three exact public-site source files, and the rendered landing page. Counts below are deduplicated material passage groups; matching source and rendered text is counted once and recorded as corroboration rather than as two separate findings.

### Search results

| Term cluster | Material active passage groups | Classification result |
|---|---:|---|
| `FireSight` | 0 | No active naming hit. |
| `funder`, `funding`, `grant`, `sponsor`, `fiscal sponsor` | 4 | Active public-site relationship/funding positioning; mandatory-blocker evidence for G11. |
| `partner`, `partnership`, `collaborator` | 5 | Active public-site partner positioning; mandatory-blocker evidence for G11 where presented as current relationship or delivery audience. |
| `reviewer`, `external reviewer` | 4 | Active reviewer-outreach and reviewer-structure positioning; mandatory-blocker evidence for G11. |
| `pilot` | 7 | Active Phase 0/pilot framing; supporting evidence of a competing current thesis and legacy portfolio framing. |
| `field validation`, `field-validated`, `agency review`, `agency endorsement` | 0 affirmative | Technical hits are prohibitions. No affirmative active validation or endorsement claim was found. |
| `official`, `operational`, `real-time` | 0 affirmative direct claims | Technical hits are prohibitions. The site still lacks the required experimental/not-official warning package and uses stronger capability framing. |
| `emergency`, `evacuation`, `route`, `routing`, `road closure`, `tactical`, `incident command` | 5 affirmative or capability-positioning groups; 4 negative guardrail items | Technical hits are boundaries. Public-site evacuation/access and decision-support framing is materially stronger than permitted; guardrails do not cure it. |
| `decision support`, `planning-ready` | 5 | Active public capability framing without completed evidence or claim approval. |

## Controlling project-name and thesis evidence

### Current technical identity

The active technical repository consistently names the project `BurnLens Deschutes`:

- `README.md:1-7`
- `AGENTS.md:7-15`
- `VERSIONING.md:3-21`
- `docs/objective-one/TECHNICAL_DESCRIPTION.md:3-13`
- `docs/objective-one/USE_BOUNDARIES.md:3-15`
- `docs/objective-one/SOURCE_PRECEDENCE.md:3-19`

The clearest existing thesis is the exact sentence in `AGENTS.md:13-15`:

> BurnLens Deschutes is an experimental, portfolio-first computer vision and GEOINT wildfire screening project for Deschutes County, Oregon. The project is intended to demonstrate technical capability, reproducibility, traceability, usefulness, and transparent limitations. It is not an official wildfire information source and is not emergency guidance.

This audit does not invent or adopt replacement wording.

### Conflicting active public thesis

The active public surface presents a different identity and product posture:

- `burnlens-site/README.md:3-5` — “Public landing page for BurnLens, a public-interest wildfire planning support initiative.”
- `burnlens-site/app/layout.tsx:7-12` — “Wildfire planning support for resilient communities” and a “public-interest wildfire planning initiative” producing “planning-ready maps, memos, and screening materials.”
- `burnlens-site/app/page.tsx:206-214` — “Wildfire planning support,” “Clearer wildfire planning,” and current transformation of imagery and fire information into planning-ready materials.
- `burnlens-site/app/page.tsx:235-237` — primary task stated as “Evacuation-access and exposure screening.”
- Rendered `burnlensproject.org`, inspected 2026-07-12, hero and primary-task sections — same active thesis and task.

`BurnLens` may function as a short brand, but the public surface does not frame it as shorthand for the locked experimental portfolio thesis. The public initiative/product thesis competes with the technical-repository thesis.

## Controlling boundary and source-precedence evidence

Current technical controls are explicit and internally coherent:

- `docs/objective-one/USE_BOUNDARIES.md:7-21` defines experimental portfolio use and prohibits emergency-response, evacuation-order, incident-command, official-hazard, field-validation, and official-source replacement positioning.
- `docs/objective-one/USE_BOUNDARIES.md:36-44` blocks operational and official implications and states that official sources govern.
- `docs/objective-one/USE_BOUNDARIES.md:60-70` requires visible experimental/not-official disclaimers and limits portfolio claims.
- `docs/objective-one/SOURCE_PRECEDENCE.md:7-23` states “Official sources govern” and provides standard public wording.
- `docs/phase-one/objective-two/CV_USE_BOUNDARIES.md:24-30` defines the CV outputs as experimental portfolio artifacts and not evacuation, tactical, incident-command, field-validated, or official information.
- `docs/phase-one/objective-two/CV_USE_BOUNDARIES.md:78-98` requires visible warning language on public-site cards and outputs.
- `docs/phase-one/objective-two/CV_USE_BOUNDARIES.md:164-181` allows experimental portfolio/prototype framing and prohibits an evacuation decision aid, agency partner product, field-validated model, or sponsored/authoritative operational system.
- `docs/phase-one/objective-five/OBJECTIVE_FIVE_CLAIMS_CHECK.md:30-46` requires experimental portfolio framing and official-source precedence.
- `docs/phase-one/objective-five/OBJECTIVE_FIVE_CLAIMS_CHECK.md:62-77` blocks public claims of created outputs, public-claim approval, operational use, field validation, agency endorsement, evacuation/routing support, and related authority.
- `docs/phase-one/objective-five/CLAIM_TRACEABILITY_PROTOCOL.md:7-25` defines website copy as a claim surface, requires linked evidence, and blocks operational, emergency, endorsement, validation, evacuation, routing, tactical, incident-command, and public-safety support claims.
- `docs/phase-one/objective-five/CLAIM_TRACEABILITY_PROTOCOL.md:54-80` requires evidence, warning language, source-precedence status, and release status before public use.

## Findings

### T03-F01 — Competing active project thesis

| Field | Finding |
|---|---|
| Criterion | G01 |
| Exact evidence | Technical thesis: `AGENTS.md:13-15`, `README.md:1-7`, `TECHNICAL_DESCRIPTION.md:7-13`. Conflicting public thesis: `burnlens-site/README.md:3-5`, `app/layout.tsx:7-12`, `app/page.tsx:206-214`, rendered hero lines inspected 2026-07-12. |
| Authority and currency | Current merged technical controls at `103b7078`; current site source at `deece378`; rendered site inspected 2026-07-12. |
| Classification | Active identity/thesis contradiction. |
| Severity / blocker | High; `mandatory blocker`. |
| Consequence | The project name/thesis is not locked across active technical and public surfaces. |
| Owner | Separate public-site remediation task; T03 must not supply replacement thesis text. |

### T03-F02 — Public capability and evacuation-access framing exceeds current evidence and warnings

| Field | Finding |
|---|---|
| Criterion | G02 |
| Exact evidence | `burnlens-site/app/layout.tsx:9-11,23-35`; `app/page.tsx:23-48,206-214,235-237,261-288,385-388,424-448,455-458,484-486`; rendered site hero, workflow, pilot, outputs, and founder sections inspected 2026-07-12. |
| Contradicting controls | `USE_BOUNDARIES.md:9-21,25-40,60-70`; `SOURCE_PRECEDENCE.md:11-23`; `CV_USE_BOUNDARIES.md:24-39,78-98,164-181`; `CLAIM_TRACEABILITY_PROTOCOL.md:7-25,54-80`. |
| Authority and currency | Current merged controls and current public source/rendered copy. |
| Classification | Active capability and use-positioning contradiction; required warning package absent from the rendered landing page. |
| Severity / blocker | High; `mandatory blocker`. |
| Consequence | Written boundaries exist, but active public language is materially weaker and stronger capability claims are unsupported. |
| Owner | Separate public-site boundary/claim remediation task with exact site paths and claim-review evidence. |

The visible guardrails in `app/page.tsx:455-458` (“Not incident command,” “Not evacuation orders or emergency direction,” and related items) are useful but insufficient. They do not label the project experimental, do not state that BurnLens is not official wildfire information, do not state that official sources govern, and do not cure affirmative “planning-ready,” “evacuation-access,” “decision-support,” and delivery claims elsewhere on the same page.

### T03-F03 — Active sponsor, partner, reviewer, grant, and pilot positioning

| Field | Finding |
|---|---|
| Criterion | G11; pilot framing is also supporting G01 evidence |
| Exact evidence | `burnlens-site/app/page.tsx:212-214` (“local partners”); `261-288` (public agencies/resilience partners, local teams, real coordination); `345` (reviewer, fiscal-sponsor, and grant outreach); `375-402` (Phase 0 pilot, reviewer structure, sponsor readiness, reviewer outreach, pilot packaging); `424` (“What partners receive”); `551-556` (sponsorship fit, county/city partners, prospective reviewers, fiscal sponsors). The rendered page presents the same passages at inspection time. |
| Authority and currency | Current site source at `deece378`; current rendered site inspected 2026-07-12. |
| Classification | Active relationship, funding, reviewer, and pilot positioning. |
| Severity / blocker | High; `mandatory blocker` for G11. |
| Consequence | Prohibited legacy relationship language remains in active working scope. |
| Owner | Separate public-site relationship-language remediation task. Archival sources remain untouched. |

No affirmative field-validation or agency-endorsement claim was found. G11 is still disqualified because sponsor, partner, fiscal-sponsor, reviewer, and related current-positioning language remains active.

### T03-F04 — Current-status surfaces contain stale task or phase language

| Field | Finding |
|---|---|
| Criterion | Supporting current-framing finding; does not create a new gate criterion |
| Exact evidence | `AGENTS.md:51-64` still identifies Objective Six as the active repository-control workstream; `README.md:52-64` says the T03 issue is not yet created. |
| Authority and currency | Current `main` at T03 branch creation. |
| Classification | Stale active status language. |
| Severity / blocker | Medium; `non-blocking limitation` for this audit, but must remain visible for later synchronization/remediation. |
| Consequence | Current workflow/status framing is not fully synchronized even though project identity and boundaries remain otherwise explicit in the technical controls. |
| Owner | A separately authorized status/control remediation or post-merge synchronization task; T03 cannot edit these files. |

## Criterion dispositions

| Criterion | Matrix status | Audit disposition | Blocker class | Evidence owner | Rationale |
|---|---|---|---|---|---|
| G01 — Project name and thesis are locked | `does not meet` | `blocked` | `mandatory blocker` | P1O7-T03; remediation owner to be separately authorized | The technical thesis is identifiable, but active public-source and rendered copy presents a competing initiative/product thesis and primary task. |
| G02 — Use boundaries are written and current | `does not meet` | `blocked` | `mandatory blocker` | P1O7-T03; remediation owner to be separately authorized | Boundary controls are strong, but active public capability, evacuation-access, and decision-support framing conflicts with them and omits the required warning package. |
| G11 — Prohibited legacy relationship and validation language is absent from active working scope | `does not meet` | `blocked` | `mandatory blocker` | P1O7-T03; remediation owner to be separately authorized | Active public copy retains sponsor, fiscal-sponsor, grant, partner, reviewer, and pilot positioning. |

These statuses are scoped criterion findings pending human review. They do not decide Phase One acceptance and do not evaluate G03-G10.

## Public-site source-to-deployment limitation

The rendered landing-page text materially matches the inspected source passages in `app/layout.tsx` and `app/page.tsx`. The deployed page does not expose a source commit or deployment identifier, so this audit cannot prove cryptographically that `deece3782e4edd72e5afd61f9fe05e681d769661` is the deployed build.

This limitation does not remove the findings because the same material language is present independently in current source and current rendered copy.

## Remediation routing

T03 does not perform remediation. Before T04 proceeds without an explicit human-approved carry decision, create separately authorized bounded remediation tasks for:

1. active public identity/thesis alignment, without inventing a new thesis;
2. active public boundary, warning, and unsupported capability language;
3. active sponsor, partner, reviewer, grant, and pilot positioning;
4. stale active status/control language where a separate synchronization task is insufficient.

Each remediation issue must name exact affected paths, verification, claim-review requirements, and return evidence to this audit or its successor record.

## Safe claims

- The current technical repository has explicit experimental portfolio identity, use-boundary, and source-precedence controls.
- T03 found three mandatory blockers in active public scope.
- No active `FireSight` naming, affirmative field-validation claim, or affirmative agency-endorsement claim was found in the audited active inventory.
- The public site was inspected read-only; no source or deployed copy was changed.
- Phase One acceptance remains undecided.

## Unsupported claims

- G01, G02, or G11 passes.
- Phase One has passed, been accepted, or been released.
- Public-site claims are approved.
- BurnLens currently produces validated planning-ready maps, memos, evacuation-access products, decision-support products, or partner deliverables.
- BurnLens has sponsor, partner, reviewer, funder, fiscal-sponsor, agency, or field-validation commitments.
- Phase Two data work is authorized.
- A tag or GitHub Release exists because a proposal or document exists.

## Verification summary

| Check | Method | Actual result |
|---|---|---|
| Base and dependency verification | Live GitHub commit, issue, branch, PR, and path checks | Passed; branch created from current `main`; #251 closed; #246 and #257 open; #194 separate. |
| Active-scope inventory | Exact-file fetch and manual role/classification review | Passed; 14 technical surfaces, three site source files, and one live URL recorded. |
| Public-site inventory | Current source-head verification, exact source fetch, and rendered-page inspection | Passed with deployment-SHA limitation. |
| Term search | Connector search attempts plus exact-file case-insensitive manual review | Passed with connector-index limitation recorded; material passage counts and classifications recorded. |
| Exact citation | Manual path/line and live-section review | Passed; every finding identifies exact evidence. |
| Project name and thesis | Cross-surface comparison | Failed criterion; G01 `does not meet` / `blocked`. |
| Boundaries and precedence | Control-to-public-copy comparison | Failed criterion; G02 `does not meet` / `blocked`. |
| Legacy relationship language | Active/archival classification | Failed criterion; G11 `does not meet` / `blocked`. |
| Archive exclusion | Scope inspection without opening Tier 2 | Passed. |
| Public-claim approval | Manual audit of artifact language and actions | Passed; no claim approved or rewritten. |
| Controlled-work boundary | Changed-file and action review | Passed; no source, site, data, settings, tag, or Release action. |

## Handoff

The audit is ready for human review. Because mandatory blockers are recorded, the default handoff is separately authorized `P1O7-REM-03*` work, not silent progression to T04.

T04 may begin only after the blockers are remediated and re-audited, or after an explicit human-approved carry decision records the consequence. Parent #246 remains open.
