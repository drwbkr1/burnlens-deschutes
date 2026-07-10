# Prompt Build Log Entry - SOP Context-Tiered Chats

## Entry metadata

| Field | Value |
|---|---|
| Log entry date | 2026-07-09 |
| Task | Update Prompt-to-Repo SOP for context-tiered chats |
| Task issue | #190 |
| Branch | `sop-context-chats` |
| Pull request | #191 |
| Merge method | squash |
| Merge commit | `5989d6eff3c4848ae2669218b25430179835b258` |
| Primary artifact | `docs/workflows/PROMPT_TO_REPO_SOP.md` |
| Supporting artifact | `templates/CODEX_TASK_PACKET.md` |
| Prompt assistant | ChatGPT |

## Task summary

Create a repo-level SOP that distinguishes the full reference SOP from compact operational task capsules, uses ChatGPT chat terminology, and keeps new chats as a context-management option rather than a hard workflow requirement.

## User adjustments incorporated

| Adjustment | Result |
|---|---|
| Use chat terminology instead of dialogue terminology. | SOP now uses parent chat, task chat, review chat, and chat handoff. |
| Avoid making 3-4 tasks per chat a rule. | SOP says a new chat is optional when context is saturated or the workstream changes. |
| Keep comprehensive SOP usable. | SOP has a quickstart and says the full SOP is a repo reference, not a paste-every-time prompt. |

## Files changed

```text
docs/workflows/PROMPT_TO_REPO_SOP.md
templates/CODEX_TASK_PACKET.md
records/prompt-build-log/2026-07-09-sop-context-chats.md
```

## Research/source checks

No new external research was required. The task updates internal workflow guidance based on merged BurnLens Objective Five controls and the user's operating preference.

## Verification

| Check | Result |
|---|---|
| Issue exists | Passed: #190. |
| Branch exists | Passed: `sop-context-chats`. |
| SOP uses chat terminology | Passed. |
| SOP avoids fixed task-count rule | Passed. |
| SOP distinguishes full reference from quickstart | Passed. |
| Task packet references SOP | Passed. |
| PR merged | Passed: #191. |
| Tests | Not run; documentation/template only. |

## Handoff

Use `docs/workflows/PROMPT_TO_REPO_SOP.md` as the repo-level SOP and `templates/CODEX_TASK_PACKET.md` as the compact task-chat packet.
