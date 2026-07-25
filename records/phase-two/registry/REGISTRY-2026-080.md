# REGISTRY-2026-080 - Ward Creek U07 promotion and U08 handoff

**Recorded:** 2026-07-25
**Issue:** #554
**Branch:** `codex/p2o4-t39-replacement-event`

| Unit | Identity | State | Evidence | Next dependency |
|---|---|---|---|---|
| `P2O4-T39-U06-LOCK` | response `aadd221d...` / receipt `dba7d81a...` | `pass` | PRECHECK-2026-084 | reveal |
| `P2O4-T39-U07-R001` | private `8c7f3a6f...` / public JSON `3e43cd40...` | `failed-render-retained` | exact science; 390-pixel overflow | r002 |
| `P2O4-T39-U07-R002` | `BL-2026-07-25-ward-creek-owner-response-intake-r002` | `pass` | private `25bf6ac1...`; public JSON `091adcf7...`; PRECHECK-2026-085 | readiness audit |
| `P2O4-T39-U07-AUDIT` | `ward-creek-prototype-label-readiness-2026-001` | `pass-training-false` | audit input `ae4badb8...`; decision `8c4c5dec...` | U08 |
| `owner-approved-prototype-region-labels-v0.5.0` | 14 regions / 325 core pixels / 599 excluded ring pixels / 7 events | `prototype-only` | aggregate public intake; private unit decisions retained | U08 |
| `P2O4-T39-U08` | exact six-event candidate excluding Darlene | `eligible-not-started` | coverage and evaluation design still unresolved | full sufficiency rerun |

Both Ward Creek classes pass together. No partial event promotion occurs.
Dataset, split, baseline, model, metric, inference, deployment, or external
submission state changes.
