# REGISTRY-2026-066 - deterministic August 6 submission bundle

**Issue / branch:** #544 / `codex/p2o4-t37-august6-submission-bundle`

| Unit | Disposition | Evidence | Next |
|---|---|---|---|
| T37-U01 | `pass` | verified v0.48 tool rerun; extract-and-open gap | U02 |
| T37-U02 | `pass` | PRECHECK-2026-069; exact 11-asset public roster | U03 |
| T37-U03 | `pass` | source `7d972bfa...`; LF remediation `660f54f...`; focused tests pass | U04 |
| T37-U04 | `pass` | final r002 exact ZIP and receipt; replay byte-identical | U05 |
| T37-U05 | `pass` | final r002 extraction; safe structure; real desktop/narrow Chrome QA | U06 |
| T37-U06 | `pass` | PR #545; merge `8d4b81f...`; 10 focused / 586 full fresh-main tests; exact bundle and package replay; isolated install; tag `f46c73a...` | final submission review |

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
  package D completed separately and is byte-identical; and
- the first fresh-main focused run passed nine tests and timed out one
  30-second help probe. The exact command then passed in 2.564 seconds, the
  complete geo profile passed all 88 routes, and the repeated focused suite
  passed 10 of 10 without changing code or environment.

No scientific, label, dataset, split, baseline, model, metric, deployment,
access, or public-sharing state changes.
