# REGISTRY-2026-068 - P2O5-T02 six-event sufficiency

**Issue / branch:** #552 / `codex/p2o5-t02-six-event-sufficiency`

| Unit | Disposition | Evidence | Next |
|---|---|---|---|
| U01 | `pass` | exact six-event v0.4 lineage; prior v0.27 replay retained | U02 |
| U02 | `pass` | BurnLens 0.50.0 evaluator; source `e102874c...`; 12 focused environment/evaluator tests pass | U03 |
| U03 r001 | `failed` | expanded commit string did not equal Git source identity; ignored exact replay retained | r002 |
| U03 r002 | `failed` | scientific decision valid; public JSON encoded output directory and failed byte replay | r003 |
| U03 r003 | `block` | six outputs reproduce exactly; independent audit agrees; 0 valid 2/2/2 assignments | U04 |
| U04 r001 | `failed` | the package verifier used an invalid PowerShell selector; ignored exact attempt retained | r002 |
| U04 r002 | `failed` | two 899,515-byte wheels differed without a fixed build epoch; ignored exact attempt retained | r003 |
| U04 r003 | `block` | fixed-epoch wheels repeat at SHA-256 `c3aa9706...`; isolated 0.50.0 install, 89 commands, PNG render, 595 tests, one expected skip, 58 warnings, and 86 subtests pass; the exact HTML desktop/narrow render remains pending | exact HTML render |

The tracked run creates no dataset, split, baseline, model, metric, training authorization, deployment, external submission, or public-sharing change.
