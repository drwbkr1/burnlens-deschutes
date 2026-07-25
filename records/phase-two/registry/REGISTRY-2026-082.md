# REGISTRY-2026-082 - BL-EXC-003 v0.51 checkout-byte exception

**Recorded:** 2026-07-25

**Issue / PR:** #558 / #559

**Branch:** `codex/bl-exc-003-v051-checkout-bytes`

| Unit | Inputs and hashes | Outputs and hashes | Gates | Disposition | Failure or limitation retained | Next dependency |
|---|---|---|---|---|---|---|
| `BL-EXC-003-R001` | P2O4-T39 merge `7f7b332...`; first fresh-main checkout | 5 failed / 645 passed / 1 skipped / 6 errors / 94 warnings / 86 subtests | exact checkout and scientific bindings fail | `remediate-retained` | 40 worktree byte mismatches; tag withheld | declare exact checkout contracts |
| `BL-EXC-003-R002` | implementation `cb1f383...`; immutable PRECHECK-2026-081 CRLF identity | `.gitattributes`; two checkout regression tests | fresh clone 4/4; focused 25/25; clean checkout | `pass` | one intentional CRLF path; all other affected text LF | full custody and product gates |
| `BL-EXC-003-R003` | implementation `cb1f383...`; complete ignored custody | repository suite | 658 passed / 1 skipped / 96 warnings / 86 subtests | `pass` | existing NumPy warnings retained | replay and package |
| `BL-EXC-003-R004` | exact science `af37f80...`; frozen run metadata | six replay outputs at accepted sizes and hashes | 6/6 byte-identical; training false | `pass` | no scientific state changes | package |
| `BL-EXC-003-R005` | fixed epoch `1784996074`; implementation `cb1f383...` | two 993,480-byte wheels / `414fa8c1...`; fresh 13-distribution runtime | deterministic; safe prior package identity; 99/99 help | `pass` | original 993,307-byte optional-import failure remains historical evidence | PR merge and fresh main |
| `BL-EXC-003` | PRECHECK-2026-088; RELEASE-AUDIT-2026-006 | draft PR #559 | branch gates pass; tag absent | `candidate-pass-tag-withheld` | first fresh-main failure remains immutable | merge, fresh-main repetition, tag peel |

The exception changes checkout behavior only. It creates no provider bytes,
scientific output, owner decision, label, dataset, split, baseline, model,
metric, training authorization, inference, deployment, GitHub Release,
external submission, access, ownership, or public-sharing change.
