# REGISTRY-2026-068 - P2O5-T02 six-event sufficiency

**Issue / branch:** #552 / `codex/p2o5-t02-six-event-sufficiency`

| Unit | Disposition | Evidence | Next |
|---|---|---|---|
| U01 | `pass` | exact six-event v0.4 lineage; prior v0.27 replay retained | U02 |
| U02 | `pass` | BurnLens 0.50.0 evaluator; source `e102874c...`; 12 focused environment/evaluator tests pass | U03 |
| U03 r001 | `failed` | expanded commit string did not equal Git source identity; ignored exact replay retained | r002 |
| U03 r002 | `failed` | scientific decision valid; public JSON encoded output directory and failed byte replay | r003 |
| U03 r003 | `block` | six outputs reproduce exactly; independent audit agrees; 0 valid 2/2/2 assignments | U04 |
| U04 | `block` | 595 tests, one expected skip, 58 warnings, and 86 subtests pass; dataset/split/model path remains closed; one-event replacement is the smallest credible remediation | successor issue |

The tracked run creates no dataset, split, baseline, model, metric, training authorization, deployment, external submission, or public-sharing change.
