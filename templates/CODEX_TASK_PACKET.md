# Codex / ChatGPT Task Packet Template

## Purpose

Use this packet to brief Codex, ChatGPT, or another prompt-assisted coding agent before it starts a BurnLens Deschutes repository task.

A task packet is not a replacement for the issue, branch, pull request, artifact, or prompt/build log. It is the compact operating prompt that keeps prompt-built work scoped, reviewable, and aligned with the repo-level SOP.

## Governing SOP

Before using this packet, use:

```text
docs/governance/CHECKPOINT_POLICY.md
docs/workflows/PROMPT_TO_REPO_SOP.md
```

The checkpoint policy controls cadence, the SOP is the full workflow reference, and this packet is the short executable checkpoint capsule.

## Chat terminology

Use **chat** for ChatGPT conversations.

| Term | Meaning |
|---|---|
| Parent chat | Planning/context chat for an objective or major workstream. |
| Task chat | Focused ChatGPT conversation for one or more closely related GitHub task branches when context remains manageable. |
| Review chat | Focused ChatGPT conversation for PR review, merge, sync, or closeout. |
| Chat handoff | Compact summary passed from one ChatGPT chat to another. |

A new chat is a context-management option, not a GitHub workflow unit. Do not apply a fixed task-count rule per chat.

## Packet use rule

Each milestone or exception checkpoint has one issue, branch, artifact contract, PR, and handoff. Related evidence units may accumulate inside that milestone without separate PRs when each unit retains independent immutable identity, hashes, gates, disposition, and failure evidence.

Every packet must answer:

1. What is the task?
2. What checkpoint class and milestone exit condition apply?
3. What evidence units are registered, and how are failures retained?
4. What files may be changed?
5. What artifacts govern the task?
6. Which context tier applies?
7. What work is forbidden by reference to governing artifacts?
8. What must be verified before PR?
9. What should be handed off next?

## Context-tier quickstart

| Tier | Use |
|---|---|
| Tier 0 | Always governing context. |
| Tier 1 | Task-specific governing context. |
| Tier 2 | Historical or verification context only. |

Do not load Tier 2 unless status, provenance, or historical verification requires it.

## Copy-paste task packet

Copy everything below this line into a Codex or ChatGPT task prompt and fill in the bracketed fields.

```markdown
# BurnLens Task Packet

## Task identity

- Project: BurnLens Deschutes
- Repository: drwbkr1/burnlens-deschutes
- Phase / objective: [Phase and objective]
- Task ID: [P#O#-T## | BL-GOV-### | issue-authorized exception ID]
- Checkpoint class: [milestone | exception]
- Milestone outcome: [coherent result that changes project truth]
- Entry condition: [verified dependency]
- Exit condition: [observable ship/remediate/fallback/stop condition]
- Evidence-unit roster or registration rule: [unit IDs or rule]
- Failure-retention rule: [how failed/superseded/excluded/deferred units remain visible]
- Exception trigger: [not applicable | licensing/security/custody/rollback/stop/urgent correctness]
- Task issue: [#]
- Parent issue: [#]
- Branch to use or create: [branch-name]
- Pull request title: [Task title]
- Primary artifact path(s):
  - [path]
- Artifact type: [documentation | template | records | workflow | data-intake planning | other]

## Chat context

- Chat type: [parent chat | task chat | review chat]
- Previous chat handoff used: [path or summary]
- Required handoff at end: [yes/no]
- Do not carry forward: [drafting details or historical context that should not be reused]

## SOP quickstart

- Full SOP reference: `docs/workflows/PROMPT_TO_REPO_SOP.md`
- Use the full SOP as a reference, not as text to paste into every prompt.
- Use this task packet as the compact operating prompt.

## Context tiers

### Tier 0: always load or summarize

- `AGENTS.md`
- `README.md`
- `VERSIONING.md`
- `docs/governance/BURNLENS_EXECUTION_GOAL.md`
- `docs/governance/CHECKPOINT_POLICY.md`
- `docs/objective-one/TECHNICAL_DESCRIPTION.md`
- `docs/objective-one/USE_BOUNDARIES.md`
- `docs/objective-one/SOURCE_PRECEDENCE.md`
- `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md`
- `docs/phase-one/objective-five/OBJECTIVE_FIVE_HANDOFF.md`
- `records/PROMPT_BUILD_LOG.md`
- `templates/PROMPT_LOG_ENTRY.md`

### Tier 1: load only what applies

- [ ] CV/model direction: Objective Two docs; technical description; reproducibility/release QA.
- [ ] Source/AOI/CRS/provenance: Objective Three docs; source precedence; provenance/run/registry controls.
- [ ] GitHub workflow/templates: Branch/PR workflow; issue/PR templates; prompt-log protocol.
- [ ] Versioning/release/tag: `VERSIONING.md`; version taxonomy; release control; release QA; release note.
- [ ] Claims/public copy: claim protocol; claim evidence template; claims check; source-precedence gate.
- [ ] Reproducibility/release QA: reproducibility checklist; release QA checklist; release control.
- [ ] Research-backed decision: research validation log; claims check.
- [ ] Phase Two / Objective Six handoff: Objective Five closeout, handoff, release note, and relevant Tier 1 controls.

### Tier 2: use only for verification

- [ ] Old prompt logs.
- [ ] Prior PR bodies.
- [ ] Closed task issues.
- [ ] Historical closeouts.
- [ ] Prior current-status files.

Reason Tier 2 is needed, if used: [reason]

## Task objective

[Describe the specific result to produce. Keep the task scoped to the issue and artifact set.]

## Evidence-unit ledger

| Unit ID | Purpose | Inputs and hashes | Outputs and hashes | Gates | Disposition | Retained failure or limitation | Next dependency |
|---|---|---|---|---|---|---|---|
| [ID] | [bounded question] | [records/hashes] | [records/hashes] | [results] | [pass/remediate/exclude/defer/stop] | [retained evidence] | [next unit/exit] |

## Allowed file changes

Only these files may be created or edited unless the user approves a change:

- [path/to/allowed-file-1]
- [path/to/allowed-file-2]

## Forbidden work by reference

Follow the boundary and source-precedence rules in:

- `docs/objective-one/USE_BOUNDARIES.md`
- `docs/objective-one/SOURCE_PRECEDENCE.md`
- `docs/phase-one/objective-five/OBJECTIVE_FIVE_CLAIMS_CHECK.md`
- task-specific Tier 1 controls listed above

Do not repeat long boundary lists in this packet unless a specific task needs them.

## Objective Five control routing

Answer before writing files:

- Does this task touch data, AOI files, labels, models, runs, maps, reports, screenshots, or public demos? [yes/no]
- Does this task create or modify a source, AOI, data, run, or registry record? [yes/no]
- Does this task make a public-facing claim? [yes/no]
- Does this task involve source precedence or official-source conflict? [yes/no]
- Does this task require reproducibility review or release QA? [yes/no]
- Does this task propose a tag or GitHub Release? [yes/no]

If any answer is yes, load the matching Tier 1 controls before writing files.

## Research requirements

Fresh research is required if the task makes current, technical, official, policy, legal, safety, tooling, API, dataset, source, or niche claims.

Required source checks:

- [source or official doc]
- [source or official doc]

If no fresh research is required, state why the merged repo artifacts are sufficient.

## Verification checklist

Before opening a PR, confirm:

- [ ] Issue exists.
- [ ] Branch exists and is based on current `main` unless explicitly otherwise.
- [ ] Only allowed files changed.
- [ ] No temporary or scratch files were added.
- [ ] Required research is complete or not required with rationale.
- [ ] Boundary artifacts were followed by reference.
- [ ] Source precedence is preserved.
- [ ] Unsupported claims are avoided.
- [ ] Acceptance criteria are satisfied.
- [ ] Every registered evidence unit has immutable identity, hashes where bytes exist, gate results, disposition, and retained failures.
- [ ] The milestone exit condition or exception trigger is satisfied.
- [ ] Handoff note is included.
- [ ] No tests are claimed unless actually run.
- [ ] Tag/release status is explicit when relevant.

## PR requirements

Open one milestone or exception pull request with:

- Title: [task title]
- Base: `main`
- Head: [branch]
- Summary: [one-sentence summary]
- Close keyword: `Closes #[task issue only]`

Include the complete evidence-unit ledger and the milestone exit condition. Do not create separate PRs merely to publish intermediate evidence units.

Do not close the parent issue unless this is the approved final closeout task.

## Expected final response

After work is complete, report:

- branch used;
- files changed;
- research sources used or why none were required;
- verification performed;
- PR number;
- merge commit if merged;
- anything not completed;
- next milestone or chat handoff note.
```

## Connector-friction note

If a GitHub issue comment, PR body, or prompt log is blocked by connector filtering, retry once with concise administrative wording. If still blocked, preserve the artifact contract in the prompt log, PR body, or primary artifact and continue with a reviewable PR.
