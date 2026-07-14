# REGISTRY-2026-003 — Access-Integrity Artifacts

**Checkpoint:** Issue #317; branch `codex/p2o1-t03-viirs-inspection`; PR/merge/tag pending

| Artifact | Class | Version/state | Provider bytes |
|---|---|---|---:|
| `burnlens/access_integrity.py` | Payload validation and report rendering | BurnLens package `0.1.2` | No |
| `burnlens/viirs_access_precheck.py` | Exact-pair fail-closed CLI | BurnLens package `0.1.2` | No |
| `burnlens/render_access_report.py` | Deterministic report rebuild CLI | BurnLens package `0.1.2` | No |
| `tests/test_access_integrity.py` | Unit/contract tests | 8 checks passing | No |
| `VIIRS-ACCESS-PRECHECK-2026-001.json` | Normalized real access observation | SHA-256 `107c08e00539257d7b86265d316060f35c019c821acc59f89dfc4b8875205f7f` | No |
| `VIIRS-ACCESS-PRECHECK-2026-001.html` | Semantic evidence report | SHA-256 `8896bf615148511de95fcc7fcdfcf01eb337da58ca7a4c6a9a6943982ccfe0f4` | No |
| `VIIRS-ACCESS-PRECHECK-2026-001.png` | Rendered evidence card | SHA-256 `ae5ccc6dd6c2665fdf57e4e4b21eab1dcd489b366612252354dbe6a5cc3f5e96` | No |
| `ACCESS-2026-003.md` | Access and credential-boundary record | Complete | No |
| `PRECHECK-2026-003.md` | Payload acceptance contract | Complete | No |
| `ACCESS_INTEGRITY-2026-001.md` | Requirement/portfolio review | Pass; intake blocked | No |
| `MANIFEST-2026-003.json` | Checkpoint provenance manifest | Candidate pending merge | No |

Rejected login-response bodies are not registry artifacts and were deleted. No entry is a provider source asset, fire observation, label, dataset, model input, baseline, model, analytical run, map, application, or official product.
