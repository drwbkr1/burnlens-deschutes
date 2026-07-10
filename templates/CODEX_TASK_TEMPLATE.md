# BurnLens Codex Task Template Entry Point

## Purpose

This file is a compatibility and discoverability entry point for BurnLens task briefing.

The [canonical BurnLens task packet](CODEX_TASK_PACKET.md) is the sole executable task capsule and source of truth for task identity, context tiers, file scope, research, verification, pull-request requirements, and handoff.

## Instantiate the canonical packet

1. Confirm the authorized task issue.
2. Open the canonical task packet.
3. Instantiate it for the authorized task, branch, and file scope.
4. Complete its context, research, verification, PR, and handoff sections.
5. Use the completed packet as the operating prompt.

## Minimal invocation example

```text
Use templates/CODEX_TASK_PACKET.md to prepare the operating capsule for task P1O6-TXX, issue #NNN, branch p1o6tXXb, limited to the files authorized by that issue. Do not broaden the issue scope.
```

## No-duplicate-source rule

Do not copy or maintain a second packet, required-field schema, context-tier table, verification checklist, PR checklist, or independent workflow here. Update the canonical packet when an authorized task changes the task-capsule contract.

## What this file is not

This file is not the canonical packet, a replacement packet, an independent workflow, a task issue, a branch, a pull request, a prompt/build log, or authorization to broaden task scope.
