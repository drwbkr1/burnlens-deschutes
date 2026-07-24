# REGISTRY-2026-073 — Ward Creek reproducibility remediation

**Recorded:** 2026-07-24
**Issue:** #554
**Branch:** `codex/p2o4-t39-replacement-event`

| Unit | Run | State | Evidence | Next dependency |
|---|---|---|---|---|
| `P2O4-T39-U03-FITNESS-R002` | `BL-2026-07-24-ward-creek-reference-fitness-r002` | `failed-reproducibility-retained` | HTML/PNG exact; JSON differs only by four ambient extracted paths | r003 |
| `P2O4-T39-U03-FITNESS-R003` | `BL-2026-07-24-ward-creek-reference-fitness-r003` | `pending` | path-free public component identities | committed implementation, production run, detached exact replay |
| `P2O4-T39-U04` | not started | `blocked-by-dependency` | none | U03 exact replay plus render |

The r002 scientific findings remain evidence but cannot pass U03 because its
public JSON is checkout-dependent. R003 changes no scientific computation or
decision. It removes only non-evidentiary local extraction paths.
