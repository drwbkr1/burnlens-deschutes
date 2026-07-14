# REGISTRY-2026-005 - Paired-Intake Transaction Artifacts

**Checkpoint:** Issue #325 / PR #326; candidate branch `codex/p2o2-t02-intake-transaction`; proposed tag `v0.3.0-intake-transaction-baseline`

| Artifact | Class | Version/state | Provider/synthetic bytes retained |
|---|---|---|---:|
| `burnlens/paired_intake.py` | Exact three-asset validation, hashing, ZIP inspection, atomic registration, report rendering | BurnLens package `0.3.0`; source commit `2491766022b549402b64e3136a79fd9c046beff5` | 0 / 0 |
| `burnlens/rehearse_paired_intake.py` | Real-state and temporary synthetic rehearsal CLI | BurnLens package `0.3.0` | 0 / 0 |
| `tests/test_paired_intake.py` | Unit, integration, contract, transaction, and deterministic-render checks | 15 paired-intake checks; 31 repository tests passing | 0 / 0 |
| `PAIR-INTAKE-REHEARSAL-2026-001.json` | Normalized transaction evidence | SHA-256 `1eae030c41174fa2806f218bc28db143e83ca08b1eb69230385691e29a6bddbc` | 0 / 0 |
| `PAIR-INTAKE-REHEARSAL-2026-001.html` | Semantic evidence report | SHA-256 `f24f2e2006505ba0b9b1f03b3910cfdd83d6ab09744ecce5baaae67f2cfcc62e` | 0 / 0 |
| `PAIR-INTAKE-REHEARSAL-2026-001.png` | Rendered evidence card | SHA-256 `35b1b018b208d819a8d3a785ec40c5bbdfba1cb3899f8527dfa17a72b13beba9` | 0 / 0 |
| `MANIFEST-2026-005.json` | Candidate checkpoint provenance manifest | Issue #325 / PR #326; merge/tag identity pending | 0 / 0 |

The test-only synthetic fixture is created in a temporary directory and deleted in the same run. It is not source data, a retained dataset, a model input, or evidence that the exact provider package is usable.
