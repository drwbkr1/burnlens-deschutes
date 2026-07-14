# REGISTRY-2026-005 - Paired-Intake Transaction Artifacts

**Checkpoint:** Issue #325 / PR #326; candidate branch `codex/p2o2-t02-intake-transaction`; proposed tag `v0.3.0-intake-transaction-baseline`

| Artifact | Class | Version/state | Provider/synthetic bytes retained |
|---|---|---|---:|
| `burnlens/paired_intake.py` | Exact three-asset validation, hashing, ZIP inspection, atomic registration, report rendering | BurnLens package `0.3.0`; report-generator source `5cd157aaf0a5b372d2052acd7c19fda6b9fbef8f` | 0 / 0 |
| `burnlens/rehearse_paired_intake.py` | Real-state and temporary synthetic rehearsal CLI | BurnLens package `0.3.0` | 0 / 0 |
| `tests/test_paired_intake.py` | Unit, integration, contract, transaction, and deterministic-render checks | 16 paired-intake checks; 32 repository tests passing | 0 / 0 |
| `PAIR-INTAKE-REHEARSAL-2026-001.json` | Normalized transaction evidence | SHA-256 `7293b8523d4193d0511426ac06e83353f3b33921b0059ebe3c38fa7f093e8a0b` | 0 / 0 |
| `PAIR-INTAKE-REHEARSAL-2026-001.html` | Semantic evidence report | SHA-256 `767c59ab0a9c4c01968b27169cfcf3157c634cc930a00d8c732720ee74674f14` | 0 / 0 |
| `PAIR-INTAKE-REHEARSAL-2026-001.png` | Rendered evidence card | SHA-256 `c35a30384bc1098b361b9cb5ce1036b193b87edf6a9bf7054b40d74ffcbead4c` | 0 / 0 |
| `MANIFEST-2026-005.json` | Candidate checkpoint provenance manifest | Issue #325 / PR #326; merge/tag identity pending | 0 / 0 |

The test-only synthetic fixture is created in a temporary directory and deleted in the same run. It is not source data, a retained dataset, a model input, or evidence that the exact provider package is usable.
