# REGISTRY-2026-070 — P2O4-T39 Ward Creek optical custody

**Recorded:** 2026-07-24
**Issue:** #554
**Repository:** `drwbkr1/burnlens-deschutes`
**Branch:** `codex/p2o4-t39-replacement-event`

| Unit | Run | State | Immutable output | Next dependency |
|---|---|---|---|---|
| `P2O4-T39-U01` | `BL-2026-07-24-p2o4-t39-u01-r008` | `pass` | Ward Creek official source/terms/exact-pair gate at `11c5ad377cb6a65242720ae819c769b29b82cee2` | U02 |
| `P2O4-T39-U02-PREFLIGHT-R001` | credential-free | `failed-retained` | Exact preflight rejects two mistyped U01 hashes before credential use; zero provider bytes and zero custody targets | remediated by `3b3406b5e875889b4c282130d1ed5270e33a7572` |
| `P2O4-T39-U02` | `BL-2026-07-24-ward-creek-optical-intake-r001` | `pass` | Exact two-archive ignored custody plus tracked `WARD-CREEK-OPTICAL-CUSTODY-2026-001.json` | U03 |
| `P2O4-T39-U03-REQUEST` | `BL-2026-07-24-ward-creek-reference-request-r001` | `request-accepted-delivery-pending` | One exact MTBS-only map-10016337 queue receipt; zero delivered bytes | exact delivery custody |

## U02 registered packages

| Package | Role | Bytes | Local SHA-256 | Registration manifest |
|---|---|---:|---|---|
| `ward-creek-s2-optical-pre-v0.1.0` | pre | 1,198,399,787 | `0c03929bcc8697ab83eedcc2a4bbe6e1f428f2636a3477533ca101101b724961` | 942 bytes / `7dfaf433af866fbd6064e35b04825a3aa1ce303c88e981616ab8821245399b98` |
| `ward-creek-s2-optical-post-v0.1.0` | post | 1,198,420,414 | `4374b4bf5a446244b7d8ad6ce6eed1fa8e93aef711df7e785a95581698fd53d0` | 945 bytes / `d4511d52832fad466c4d843f1c16d1246235afad36dbe7f50883303a99fe0f43` |

The ignored controlled-intake contract is 3,895 bytes / SHA-256
`12fa376d58c7104e12bbd04e2883cb9d1517e289dda573f934653a3068e0c391`.
It and both promoted files pass the independent contract validator. The public
report is 16,317 bytes / SHA-256
`a8d89779b7508b439fee6cb5bc99dd926a62c56ab58da181b0f1b40b1bcc1f2f`.

## Decision

`PASS_WARD_CREEK_OPTICAL_CUSTODY_AUTHORIZE_U03_REFERENCE_INTAKE`

U02 advances only the exact Ward Creek optical pair. U03 is the sole eligible
next unit. No candidate, owner response, label, dataset, split, baseline,
model, metric, inference output, deployment, or external submission exists.

At `2026-07-24T20:22:15.169Z`, the official queue accepts the single exact
Ward Creek MTBS request. Its tracked public report is 3,413 bytes / SHA-256
`ad8f70ee3cbda8fcff77755486d0cb400a3a5b3c2bc09b99813e8a95abd3d54f`.
Request acceptance changes neither the U03 `pending` disposition nor any
scientific/data/model gate.
