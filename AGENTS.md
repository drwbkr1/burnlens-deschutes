# AGENTS.md

## Purpose

This file gives Codex repository-level operating instructions for BurnLens Deschutes. It is intended to be read before Codex or another prompt-assisted coding agent starts work in this repository.

Use these instructions together with the repository docs. If a direct user instruction conflicts with this file, follow the user instruction only if it stays within BurnLens safety, source-precedence, and phase-boundary rules.

## Project identity

BurnLens Deschutes is an experimental, portfolio-first computer vision and GEOINT wildfire screening project for Deschutes County, Oregon.

The project is intended to demonstrate reliability, usefulness, technical capacity, reproducibility, and transparency. It is not an official wildfire information source and is not emergency guidance.

## Non-negotiable boundary language

Use this warning, or a tighter equivalent, for future public-facing outputs:

```text
Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
```

Do not describe BurnLens outputs as safe, official, validated, authoritative, emergency-ready, operational, field-confirmed, agency-endorsed, or suitable for evacuation/routing/tactical decisions.

## Source precedence

Official sources govern over BurnLens outputs.

BurnLens outputs are lowest-priority experimental project artifacts and must never override county, state, federal, fire-service, emergency-management, hazard, evacuation, transportation, or incident information.

If project output conflicts with official information, state that official sources govern and do not attempt to reconcile the conflict as if BurnLens were authoritative.

## Current phase boundary

During Phase One / Objective Four, work is repository operating-system work only.

Allowed Objective Four work includes:

- issue architecture;
- issue taxonomy;
- Project board specification;
- branch and PR workflow;
- issue and PR templates;
- this `AGENTS.md` file;
- Codex task packet;
- prompt/build log protocol;
- Phase Two intake templates;
- closeout, handoff, and release note docs.

Forbidden during Objective Four unless explicitly authorized later:

- data acquisition;
- imagery downloads;
- final AOI selection;
- label or mask creation;
- baseline generation;
- model training;
- inference;
- metric computation;
- map publication;
- website demo integration;
- outside validation claims;
- endorsement claims.

## Required task workflow

For every task, use this loop:

```text
artifact contract -> issue comment -> task branch -> fresh research -> artifact file -> self-audit -> PR -> review -> squash merge -> issue/parent/tracker update
```

Use the merged workflow docs as controlling context:

- `docs/phase-one/objective-four/OBJECTIVE_FOUR_TRACKER.md`
- `docs/phase-one/objective-four/ISSUE_ARCHITECTURE.md`
- `docs/phase-one/objective-four/ISSUE_TAXONOMY.md`
- `docs/phase-one/objective-four/PROJECT_BOARD_SPEC.md`
- `docs/phase-one/objective-four/BRANCH_AND_PR_WORKFLOW.md`

Use the repository templates when creating new issues or pull requests:

- `.github/ISSUE_TEMPLATE/task.yml`
- `.github/PULL_REQUEST_TEMPLATE.md`

## Branch and PR rules

Use compact task branches for connector compatibility.

Examples:

```text
p1o4t07b
p1o4t08b
p2o1t01b
```

Avoid slash-heavy branch names unless working locally with Git and explicitly asked.

Every meaningful task artifact needs a pull request. The PR title should follow this pattern:

```text
P1O4-TXX Short task title
```

Use a close keyword only for the task issue. Do not close parent issue `#119` except during deliberate Objective Four closeout after the release note is complete.

Preferred Objective Four merge method: squash merge.

## Research-before-artifact rule

Research must happen after the branch is created and before the artifact is written when the task depends on current, technical, official, policy, legal, safety, tooling, API, or niche claims.

Prefer official or primary sources. For Codex/OpenAI behavior, use official OpenAI docs as the source of truth.

Record research-backed decisions inside the artifact when the artifact is a policy, protocol, workflow, template, or public-claim control file.

## Prompt-built work rules

Codex or prompt-assisted work should be small, reviewable, and traceable.

Before editing files, identify:

- task issue;
- parent issue;
- branch;
- artifact path;
- required decisions;
- required research claims;
- boundary constraints;
- acceptance checklist;
- handoff note.

After editing files, verify:

- changed files are expected;
- no temporary files are included;
- boundary language remains intact;
- unsupported claims are not introduced;
- PR body closes only the task issue;
- next task is clear.

## File creation rule

If the GitHub connector has trouble with normal file creation, do not reduce artifact quality.

Use the safer known path:

```text
update_file with sha: new
```

Then verify the branch diff immediately. If troubleshooting commits occurred, prefer squash merge.

## Claims rules

Safe internal claims after Objective Four tasks may include that the repo has documented workflow, templates, issue structure, or Codex guidance if those artifacts are merged.

Do not claim:

- operational reliability;
- field validation;
- emergency readiness;
- agency endorsement;
- official wildfire information status;
- live incident accuracy;
- completed data/model/map work before the relevant later phase.

## Future implementation caution

When later phases authorize data or model work, add provenance, source metadata, versioning, run IDs, and claim-boundary records before treating outputs as portfolio evidence.

The locked technical chain remains:

```text
imagery -> preprocessing -> segmentation or baseline mask -> raster output -> vector polygons -> map overlay -> exposure-style summary -> documented run package
```

Do not skip traceability steps to make the project look more complete.

## Verification expectations

For documentation-only tasks, verify:

- Markdown is readable;
- paths and issue numbers are correct;
- research links are current;
- acceptance criteria and handoff are present;
- boundaries are preserved.

For future code tasks, run the relevant local tests, linting, type checks, or smoke checks defined by the task packet. If no tests exist yet, state that clearly in the PR body and do not imply tests passed.

## Handoff rule

Every task artifact should end with enough context for the next task to proceed without guessing.

At minimum, include:

- what was created;
- what remains unresolved;
- what the next task should use;
- any merge-order or dependency caveat.
