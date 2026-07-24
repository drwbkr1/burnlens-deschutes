# REGISTRY-2026-066 - deterministic August 6 submission bundle

**Issue / branch:** #544 / `codex/p2o4-t37-august6-submission-bundle`

| Unit | Disposition | Evidence | Next |
|---|---|---|---|
| T37-U01 | `pass` | verified v0.48 tool rerun; extract-and-open gap | U02 |
| T37-U02 | `pass` | PRECHECK-2026-069; exact 11-asset public roster | U03 |
| T37-U03 | `pass` | source `7d972bfa...`; LF remediation `660f54f...`; focused tests pass | U04 |
| T37-U04 | `pass` | final r002 exact ZIP and receipt; replay byte-identical | U05 |
| T37-U05 | `pass` | final r002 extraction; safe structure; real desktop/narrow Chrome QA | U06 |
| T37-U06 | `in_progress` | 586 full tests pass; exact bundle replay; reproducible wheel; isolated 0.49 install; valid release audit blocked only on PR/merge/fresh-main/tag | milestone exit |

Retained failures:

- the first environment smoke correctly found installed metadata still at
  0.48.0 after the 0.49.0 source bump; locked environment refresh resolved it;
- production r001 exposed five missing LF checkout contracts and remains
  ignored; r002 binds checkout-stable bytes;
- the first Playwright launch lacked its managed browser binary; installed
  local Chrome was used without download; and
- the first mobile check assumed an absent CSS class; corrected inspection
  changes no artifact;
- the first full candidate suite passed 557 tests and failed only 29 stale
  current-package `0.48.0` assertions after the intentional `0.49.0` bump; and
- the first affected-test rerun exceeded a two-minute shell limit without a
  reported failure; the bounded longer rerun passed all 187 affected tests;
- the first package-isolation attempt corrupted a binary TAR stream through
  PowerShell and was rejected before build; file-based Git ZIP archives
  supersede it; and
- the first ZIP package command exceeded two minutes after package C finished;
  package D completed separately and is byte-identical.

No scientific, label, dataset, split, baseline, model, metric, deployment,
access, or public-sharing state changes.
