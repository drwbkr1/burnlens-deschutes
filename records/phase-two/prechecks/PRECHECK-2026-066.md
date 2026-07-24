# PRECHECK-2026-066 - Windigo fresh-main byte-stability remediation

**Exception / parent:** `BL-EXC-002` / issue #536 / P2O4-T35 issue #534 / PR #535

**Failed merged checkpoint:** `00d01402657e92357f5f4c795ba9a4f4fd99038a`

**Branch:** `codex/bl-exc-002-windigo-byte-stability`

**Disposition:** `REMEDIATE_CHECKOUT_BYTES_WITHOUT_CHANGING_EVIDENCE`

## Fresh-main failure

PR #535 squash-merged at `00d01402657e92357f5f4c795ba9a4f4fd99038a`. The canonical checkout then rebuilt the locked CPython 3.12.10 geospatial environment successfully: 66 compatible distributions, BurnLens 0.47.0, and all 86 command probes passed.

The full custody-enabled suite reached 569 passing tests, one expected skip, and 86 passing subtests before all six original Windigo response-intake tests errored at setup. The first exact failure was:

`record size changed: SOURCE-2026-036`

Windows checkout had converted exact-byte-bound Markdown records to CRLF because they lacked explicit path rules. The same missing nested rule converted the final intake JSON and HTML. The fail-closed code correctly refused reconciliation. The annotated release tag was withheld.

No source pixel, candidate, owner decision, label, dataset, split, baseline, model, version, or tracked Git blob changed.

## Exact remediation

The exception adds explicit `text eol=lf` rules for all nine `RECORD_BINDINGS` paths:

- `SOURCE-2026-036`;
- `SOURCE-2026-037`;
- `TERMS-2026-031`;
- `TERMS-2026-032`; and
- `PRECHECK-2026-059` through `PRECHECK-2026-063`.

It also adds nested Windigo intake rules:

- `samples/labels/review/windigo/phase-two/intake/*.json text eol=lf`;
- `samples/labels/review/windigo/phase-two/intake/*.html text eol=lf`; and
- `samples/labels/review/windigo/phase-two/intake/*.png -text`.

The regression test asks Git for the effective `text` and `eol` attributes on every exact path. It runs even when ignored provider custody is absent.

## Candidate verification

- All nine bound records return to their exact recorded LF sizes and SHA-256 values.
- Final public JSON / HTML / PNG return exactly to 6,787 / 3,582 / 79,681 bytes and their original hashes.
- First focused remediation run: seven tests reached scientific replay; six passed and the public HTML self-binding exposed the missing nested rule.
- Second focused run: seven scientific tests passed; the new path assertion exposed Windows separator quoting in the test itself.
- Corrected focused run: eight passed with two retained NumPy deprecation warnings.
- Complete custody-enabled suite: 577 passed, one expected skip, 22 retained warnings, and 86 subtests in 523.58 seconds.

The working-tree line-ending normalization is mechanical only. Git blob hashes for every bound record and public output equal the merged index; the exception changes only `.gitattributes`, the regression test, and release-truth records.

## Remaining exit gates

Commit and push the exception. Prove its fixed-epoch wheel is byte-identical to SHA-256 `1fabf5408113dcd238871070a3fbe0105526a845c66eb8f0f48edcb99595aea7`. Open and merge one exception PR. Then repeat the focused/full suite from fresh corrected `origin/main`, reproduce the exact public outputs and package, and remotely peel the annotated v0.47 tag to the corrected merge.

No GitHub Release, deployment, dataset, split, baseline, or model is authorized.
