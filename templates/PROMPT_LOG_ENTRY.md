# Prompt Log Entry Template

Use this with `records/PROMPT_BUILD_LOG.md`. This is the canonical detailed prompt/build-log entry template; it is not a transcript, task authorization, task packet, PR, or approval record.

Do not record secrets, credentials, tokens, cookies, private URLs, private chain-of-thought, raw private transcripts, unnecessary personal information, unapproved proprietary material, or unreviewed operational wildfire guidance.

## Entry metadata

| Field | Value |
|---|---|
| Date | `YYYY-MM-DD` |
| Task ID and title | `P#O#-T## — title | BL-GOV-### — title | issue-authorized exception ID — title` |
| Checkpoint class | milestone / exception |
| Milestone outcome / exit condition or exception trigger |  |
| Task issue / parent issue | `# / #` |
| Branch / base | `branch / main` |
| Dependencies | issues, PRs, commits, artifacts, or `None` |
| PR / reviewed head | `# or pending / SHA or pending` |
| Merge method / merge commit | `pending / pending` |
| Primary artifacts |  |
| Supporting artifacts |  |
| Artifact class | documentation / template / workflow / records / code / configuration / data / model / public output / other |
| Prompt-assisted mode | ChatGPT / Codex cloud / Codex CLI / Codex IDE / other |
| Current state | draft / blocked / review-ready / merged / deferred / rejected |

## Authorized task summary

```text
[Durable task instruction derived from the issue and templates/CODEX_TASK_PACKET.md.]
```

## Governing context

- Tier 0 loaded or summarized: `yes / no`
- Exact Tier 1 artifacts:

```text
[path]
```

- Tier 2 used: `yes / no`
- Exact Tier 2 artifacts and why current controls were insufficient:

```text
[path and reason / not used]
```

## File scope

Allowed files:

```text
[path]
```

Actual files changed:

```text
[path]
```

- Scope expansion: `none / requested`
- Issue-revision or owner-authorization evidence, when required: `[evidence / not applicable]`
- Overlapping-branch or dependency caveat: `[none / explanation]`

## Research

| Claim ID | Official or primary source | URL or repo path | Fact supported | Affected artifact or decision | Adopted wording or decision | Date checked | Status |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  | supported / caveated / obsolete / unresolved |

No-research rationale:

```text
[Task-specific reason repository-internal verification was sufficient / not applicable.]
```

## Material decisions

| Decision | Rationale | Evidence |
|---|---|---|
|  |  |  |

## Evidence-unit ledger

| Unit ID | Purpose | Inputs and hashes | Outputs and hashes | Gates | Disposition | Retained failure or limitation | Next dependency |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  | pass / remediate / exclude / defer / stop |  |  |

Every registered evidence unit must remain visible, including failed, superseded, excluded, and deferred units. A governance-only milestone may use one policy-amendment unit when no analytical or custody unit exists.

## Verification

| Check | Exact command or inspection method | Actual result | Evidence or output | Limitation or unresolved finding |
|---|---|---|---|---|
|  |  | passed / failed / partial / blocked / not applicable |  |  |

Checks not run or not applicable:

| Check | Task-specific reason |
|---|---|
|  |  |

Do not write `tests passed` unless named tests or commands actually ran.

## Boundary, claims, and controlled-work status

- [ ] Work stayed within the issue, approved files, and current phase boundary.
- [ ] Official source precedence was preserved.
- [ ] No unsupported official, operational, field-validation, emergency-readiness, agency-endorsement, production-readiness, or decision-authority claim was introduced.
- [ ] Written policy was not represented as configured platform enforcement.
- [ ] Sensitive and private material was excluded.

```text
Data/AOI/imagery:
Labels/masks/baselines/models:
Runs/reports/maps/screenshots/demos:
Repository settings or CI:
Tag:
GitHub Release:
Safe claims:
Unsupported claims:
```

## Review separation

| Stage | Evidence and status |
|---|---|
| Author self-audit | completed by / date / known findings |
| Executable checks | named methods and actual results |
| AI-assisted review | tool, target, findings, fixes, unresolved findings, or not used |
| Required owner decision | candidate yes/no/uncertain or stop-condition direction, evidence, outcome, or not applicable |
| Merge authority | controlling goal or explicit owner direction, evidence, final head, method, task-only close keyword, parent protection |

Author self-audit and AI review are supplemental evidence. Neither is independent approval, supplies a required owner decision, authorizes work outside the issue, or waives an evidence gate. Routine merge authority comes from the controlling goal after blocking findings and required owner decisions are resolved.

## Review-driven revisions

| Finding or request | Source and severity | Revision | Follow-up verification | Status |
|---|---|---|---|---|
|  |  |  |  | resolved / accepted / open |

## PR, issue, and synchronization status

| Field | Value |
|---|---|
| PR title / close keyword | `title / Closes #TASK_ISSUE` |
| Task issue closure | confirmed / pending |
| Parent issue protected and updated | yes / no / pending |
| README inspection | current / stale / not applicable / pending |
| Tracker inspection | current / stale / not applicable / pending |
| Canonical index inspection | current / stale / not applicable / pending |
| Dated task-log inspection | current / stale / not applicable / pending |
| Separate sync task | issue/PR / not required / pending |

## Handoff

```text
[Next task or action and required context.]
```

## Do not carry forward

```text
[Superseded drafting details, resolved findings, temporary troubleshooting, or historical material to discard.]
```

## Completeness check

- [ ] Identity, authorization, branch/base, dependencies, artifacts, and state are recorded.
- [ ] Tier 0, exact Tier 1, and justified Tier 2 use are recorded.
- [ ] Allowed and actual files are recorded.
- [ ] Research and decisions are recorded, or a no-research rationale is present.
- [ ] Named checks, exact methods, actual results, limitations, and non-applicability reasons are recorded.
- [ ] Boundaries, claims, sensitive material, and controlled-work status are recorded.
- [ ] Author self-audit, executable checks, AI review, required owner decisions, and merge authority remain distinct.
- [ ] PR linkage, parent protection, synchronization, handoff, and `Do not carry forward` are complete.
