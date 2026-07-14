# REGISTRY-2026-006 - Authenticated Source Inspection Artifacts

**Checkpoint:** Issue #329 / PR #330; merge `7678cf41b64e128106c199b913fe74590a52cf80`; verified annotated `v0.4.0-authenticated-source-baseline`; lifecycle sync issue #331 / PR #332

| Artifact | Class | Version/state | Committed provider raw bytes |
|---|---|---|---:|
| `burnlens/provider_acquisition.py` | Secret-safe exact-provider acquisition, resume, size/magic/checksum gates, atomic intake | BurnLens package `0.4.0` | 0 |
| `scripts/invoke_authenticated_intake.ps1` | Local protected-credential wrapper and environment cleanup | Runtime-only secret boundary | 0 |
| `burnlens/source_inspection.py` | Real Sentinel/VIIRS array inspection and evidence rendering | `source-inspection-v0.1.0`; source `9a7e614fbfbbcd4c5a6795417121cafb82ae5dcc` | 0 |
| `tests/test_provider_acquisition.py` and `tests/test_source_inspection.py` | Transport security, redaction, integrity, scientific-array, and deterministic-render checks | 56 repository tests passing | 0 |
| `SOURCE-INSPECTION-2026-001.json` | Normalized source/reference evidence | SHA-256 `cbd4dfba840680256a100aeca1a2e0b28483796f7e7b79b90de8b933d58b0a53` | 0 |
| `SOURCE-INSPECTION-2026-001.html` | Semantic evidence report | SHA-256 `76d13d3e105f053410d0063b17eb740f732c786dc395fe13335701496cbb41a0` | 0 |
| `SOURCE-INSPECTION-2026-001.png` | Rendered real-source evidence card | SHA-256 `da93de6e432296f72c8f420d0181cfc81d99be7cf70ad96fe5b7bba619739966` | 0 |
| `MANIFEST-2026-006.json` | Checkpoint provenance manifest | Issue #329 / PR #330; exact merge/tag identity verified; lifecycle sync issue #331 / PR #332 | 0 |
| `ACCESS-2026-007` | Successful authenticated delivery record without secret material | `AUTHENTICATED_REGISTERED_EXACT_PACKAGE` | 0 |
| `SOURCE_FITNESS-2026-001` / `LABEL_FITNESS-2026-002` | Real-file source acceptance and label deferral | `ACCEPT_REFERENCE`; `DEFER_LABELS` | 0 |

Three raw provider assets totaling 1,169,997,942 bytes are retained only in ignored local storage for reproducible inspection. Their exact identities and hashes are recorded; their bytes, credential material, signed delivery URLs, and provider response bodies are not committed.
