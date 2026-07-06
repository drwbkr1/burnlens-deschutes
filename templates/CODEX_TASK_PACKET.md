# Codex Task Packet Template

## Purpose

Use this packet to brief Codex or another prompt-assisted coding agent before it starts a BurnLens Deschutes repository task.

A task packet is not a replacement for the issue, branch, pull request, or artifact. It is the reusable instruction bundle that keeps prompt-built work small, reviewable, source-backed, and inside the current project boundary.

## Research basis

| Claim ID | Claim | Source authority | Decision for this template |
|---|---|---|---|
| P1O4-T08-R01 | Codex reads `AGENTS.md` files before doing work and uses project-level guidance from the repository root downward. | OpenAI Codex docs: Custom instructions with AGENTS.md | Require every task packet to tell Codex to read and follow `AGENTS.md` and the Objective Four standards artifacts. |
| P1O4-T08-R02 | Codex produces higher-quality outputs when it can verify work. | OpenAI Codex docs: Prompting | Include explicit verification, acceptance, and no-tests-if-no-tests rules. |
| P1O4-T08-R03 | Codex handles complex work better when work is broken into smaller, focused steps. | OpenAI Codex docs: Prompting | Keep one packet scoped to one task issue and one primary artifact set. |
| P1O4-T08-R04 | Codex prompts should include useful context such as relevant file references. | OpenAI Codex docs: Prompting | Require file targets, controlling docs, dependencies, and source links in the packet. |
| P1O4-T08-R05 | Codex threads should not modify the same files in parallel. | OpenAI Codex docs: Prompting | Require active-file and dependency checks before starting a packet. |

## Source links

- OpenAI Codex docs: Custom instructions with AGENTS.md - https://developers.openai.com/codex/guides/agents-md
- OpenAI Codex docs: Prompting - https://developers.openai.com/codex/prompting

## When to use this packet

Use this packet before asking Codex to do repository work that changes files, drafts artifacts, updates templates, creates records, or proposes implementation work.

Do not use this packet as permission to skip the GitHub issue, branch, research, or PR workflow.

## Packet use rule

Each packet should map to exactly one task issue unless the user explicitly approves a bundled task.

Every packet must answer:

1. What is the task?
2. What files may be changed?
3. What sources or artifacts govern the task?
4. What work is forbidden?
5. What must be verified before PR?
6. What should be handed off next?

---

# Copy-paste task packet

Copy everything below this line into a Codex task prompt and fill in the bracketed fields.

```markdown
# BurnLens Codex Task Packet

## Task identity

- Project: BurnLens Deschutes
- Repository: drwbkr1/burnlens-deschutes
- Phase: [Phase number]
- Objective: [Objective number]
- Task ID: [P1O4-T08]
- Task issue: [#125]
- Parent issue: [#119]
- Branch to use or create: [p1o4t08b]
- Pull request title: [P1O4-T08 Create Codex task packet]
- Primary artifact path: [templates/CODEX_TASK_PACKET.md]
- Artifact type: [documentation | template | records | workflow]

## Required repository standards

Before doing work, read and follow:

- AGENTS.md
- docs/phase-one/objective-four/OBJECTIVE_FOUR_TRACKER.md
- docs/phase-one/objective-four/ISSUE_ARCHITECTURE.md
- docs/phase-one/objective-four/ISSUE_TAXONOMY.md
- docs/phase-one/objective-four/PROJECT_BOARD_SPEC.md
- docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md
- .github/PULL_REQUEST_TEMPLATE.md

Use the workflow:

artifact contract -> issue comment -> task branch -> fresh research -> artifact file -> self-audit -> PR -> review -> squash merge -> issue/parent/tracker update

## Task objective

[Describe the specific result Codex should produce. Keep it scoped to one task and one artifact set.]

## Allowed file changes

Codex may create or edit only these files unless the user approves a change:

- [path/to/allowed-file-1]
- [path/to/allowed-file-2]

Codex must not create temporary test files, scratch files, data files, generated outputs, or public-demo files unless explicitly requested and allowed by the current phase.

## Current phase boundary

This task is documentation, template, workflow, or records work only unless explicitly stated otherwise.

This task must not create or process:

- imagery;
- AOI data;
- source downloads;
- labels;
- masks;
- baselines;
- model outputs;
- metrics;
- maps;
- website demo artifacts;
- public claims of operational reliability;
- outside validation or endorsement claims.

## Required warning language

For any future public-facing output, preserve this warning or a tighter equivalent:

Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

## Source precedence

Official county, state, federal, fire-service, emergency-management, hazard, evacuation, transportation, and incident sources govern over BurnLens outputs.

BurnLens outputs are experimental and must never be described as official, authoritative, operational, field-validated, agency-endorsed, or emergency-ready.

## Research requirements

Fresh research is required for this task if it makes current, technical, official, policy, legal, safety, tooling, API, or niche claims.

Required source checks:

- [source or official doc to check]
- [source or official doc to check]

Record source-backed claims in the artifact or task notes before drafting final language.

## Required artifact sections

The artifact should include, where applicable:

- Purpose
- Scope boundary
- Research basis
- Source-specific facts
- Decision or recommendation
- Acceptance criteria
- Rejection or defer criteria
- Required future metadata fields
- Allowed uses
- Forbidden uses
- Versioning/provenance implications
- Claims-register check
- Handoff note

## Implementation instructions

1. Confirm the branch is correct before editing.
2. Review the allowed file list.
3. Do fresh research before writing the artifact if research is required.
4. Draft the artifact with clear headings and decision tables where useful.
5. Preserve BurnLens boundary and source-precedence language.
6. Do not add unsupported claims.
7. Verify the diff before opening a PR.
8. Use a PR body that closes only the task issue.

## Verification checklist

Before opening a PR, confirm:

- [ ] Only allowed files changed.
- [ ] No temporary or scratch files were added.
- [ ] Research basis is recorded if required.
- [ ] Boundary language is present.
- [ ] Source precedence is preserved.
- [ ] Unsupported claims are explicitly avoided.
- [ ] Acceptance criteria are included.
- [ ] Rejection or defer criteria are included where relevant.
- [ ] Handoff note is included.
- [ ] No tests were claimed unless actually run.

## PR requirements

Open a pull request with:

- Title: [P1O4-T08 Create Codex task packet]
- Base: main
- Head: [branch]
- Body summary: [one-sentence summary]
- Close keyword: Closes #[task issue only]

Do not close the parent issue unless this is the approved final closeout task.

## Expected final response

After work is complete, report:

- branch used;
- files changed;
- research sources used;
- verification performed;
- PR number;
- anything not completed;
- next task or handoff note.
```

---

## Filled example for Objective Four Task 8

```markdown
# BurnLens Codex Task Packet

## Task identity

- Project: BurnLens Deschutes
- Repository: drwbkr1/burnlens-deschutes
- Phase: Phase One
- Objective: Objective Four
- Task ID: P1O4-T08
- Task issue: #125
- Parent issue: #119
- Branch to use or create: p1o4t08b
- Pull request title: P1O4-T08 Create Codex task packet
- Primary artifact path: templates/CODEX_TASK_PACKET.md
- Artifact type: template

## Required repository standards

Read `AGENTS.md` and the Objective Four standards artifacts before writing the template. Use the merged branch/PR workflow and preserve documentation-only boundaries.

## Task objective

Create a reusable Codex task packet template that can be copied into future Codex prompts so task work remains traceable, scoped, source-backed, boundary-safe, and reviewable.

## Allowed file changes

- templates/CODEX_TASK_PACKET.md

## Current phase boundary

Documentation/template work only. Do not create data, model, map, or public-demo outputs.

## Research requirements

Use official OpenAI Codex docs for AGENTS.md and prompting behavior. Record why the packet requires context, verification steps, smaller task scope, and file targets.

## Verification checklist

- [ ] Only `templates/CODEX_TASK_PACKET.md` changed.
- [ ] OpenAI docs are cited in the research basis.
- [ ] Packet includes allowed files, forbidden work, verification, PR, and handoff sections.
- [ ] Boundary and source-precedence language remain intact.
- [ ] PR closes only #125.
```

## Design decisions

| Decision | Rationale |
|---|---|
| One packet per task issue | Keeps Codex work small enough to verify and review. |
| File targets are mandatory | Prevents accidental edits outside task scope. |
| Research gate is explicit | Ensures current or technical claims are checked before drafting. |
| Boundary section is mandatory | Prevents Phase One repo-ops work from drifting into data/model/public-output work. |
| Verification checklist is mandatory | OpenAI Codex guidance emphasizes verification for higher-quality outputs. |
| Parent issue close is forbidden | Prevents task PRs from accidentally closing the Objective Four parent. |

## Acceptance checklist

| Check | Status | Notes |
|---|---|---|
| Task issue exists. | Satisfied | #125. |
| Parent issue is referenced. | Satisfied | #119. |
| Branch exists before artifact writing. | Satisfied | `p1o4t08b`. |
| Fresh research completed before artifact writing. | Satisfied | OpenAI Codex docs checked. |
| Packet includes task identity fields. | Satisfied | Copy-paste packet section. |
| Packet includes allowed file list. | Satisfied | Allowed file changes section. |
| Packet includes forbidden actions. | Satisfied | Phase boundary section. |
| Packet includes research gate. | Satisfied | Research requirements section. |
| Packet includes verification checklist. | Satisfied | Verification checklist section. |
| Packet includes PR requirements. | Satisfied | PR requirements section. |
| Packet includes handoff/reporting expectations. | Satisfied | Expected final response section. |

## Rejection and defer criteria

Revise or defer this template if:

- it lets Codex work without a task issue;
- it omits allowed file targets;
- it does not require research for current or technical claims;
- it allows parent issue closure in ordinary task PRs;
- it omits BurnLens phase boundaries;
- it allows unsupported official, operational, validation, or endorsement claims;
- it is too long to use in practice.

## Allowed uses

This template may be copied into Codex prompts, future task packets, issue comments, or handoff notes to keep prompt-built work scoped and reviewable.

## Forbidden uses

This template must not be used to bypass repository issues, skip branch/PR review, authorize implementation work early, claim tests passed without evidence, or permit data/model/map/public-demo work outside the current phase boundary.

## Versioning and provenance implications

Future task packets should preserve:

- task issue number;
- parent issue number;
- branch name;
- artifact path;
- source links;
- PR number;
- merge method;
- handoff note.

## Claims-register check

Safe claim after Task 8:

> BurnLens has a reusable Codex task packet template for scoping prompt-assisted repository tasks.

Unsupported claims after Task 8:

- Codex automation has been fully configured.
- Codex has executed future implementation tasks.
- Data, model, run, map, or public-demo work has begun.
- The project has operational reliability, field validation, official status, or agency endorsement.

## Handoff note

Proceed to P1O4-T09 after this template is reviewed and merged. P1O4-T09 should use this task packet to define the prompt/build log protocol and should capture how prompts, decisions, source checks, file edits, and verification notes are recorded across future Codex-assisted work.
