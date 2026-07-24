# REGISTRY-2026-074 — Ward Creek U03 closure

**Recorded:** 2026-07-24
**Issue:** #554
**Branch:** `codex/p2o4-t39-replacement-event`

| Unit | Run / commit | State | Evidence | Next dependency |
|---|---|---|---|---|
| `P2O4-T39-U03-FITNESS-R001` | `BL-2026-07-24-ward-creek-reference-fitness-r001` | `failed-retained` | supplied commit was not repository HEAD; ignored outputs only | r002 |
| `P2O4-T39-U03-FITNESS-R002` | `BL-2026-07-24-ward-creek-reference-fitness-r002` | `failed-reproducibility-retained` | HTML/PNG exact; JSON contains four ambient extraction paths | r003 |
| `P2O4-T39-U03-FITNESS-R003` | `BL-2026-07-24-ward-creek-reference-fitness-r003` / `b1614fe...` | `pass` | exact archive/terms/native rasters/class domain/optical quality/registration; three public files reproduce exactly | package and render |
| `P2O4-T39-U03-PACKAGE-R001` | wheel at `b1614fe...` | `failed-retained` | runtime-only `--help` fails on eager optional `geopandas` import | wrapper remediation |
| `P2O4-T39-U03-PACKAGE-R002` | `0006643...` | `pass` | 946,331-byte wheel; fresh runtime install; 94/94 command help checks; explicit missing-geo guidance | U03 closure |
| `P2O4-T39-U03` | `WARD-CREEK-REFERENCE-FITNESS-2026-002` | `pass` | exact replay plus owner-confirmed render equivalence; no analytical promotion | U04 |
| `P2O4-T39-U04` | not started | `eligible` | U03 dependency satisfied | independent affirmative background |

PRECHECK-2026-079 is the controlling U03 closure. PRECHECK-2026-078 and
REGISTRY-2026-073 remain immutable failure/remediation history.

No reference layer becomes a model input. No candidate, owner response, label,
dataset, split, baseline, model, metric, inference output, deployment, or
external submission exists from this unit.
