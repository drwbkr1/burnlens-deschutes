# REGISTRY-2026-005 - Paired-Intake Transaction Artifacts

**Checkpoint:** Issue #325 / PR #326; candidate branch `codex/p2o2-t02-intake-transaction`; proposed tag `v0.3.0-intake-transaction-baseline`

| Artifact | Class | Version/state | Provider/synthetic bytes retained |
|---|---|---|---:|
| `burnlens/paired_intake.py` | Exact three-asset validation, link-alias rejection, hashing, ZIP inspection, retry-safe atomic registration, report rendering | BurnLens package `0.3.0`; report-generator source `41f86dec62f0a5e8cd159c75932999790ab0f840` | 0 / 0 |
| `burnlens/rehearse_paired_intake.py` | Real-state and temporary synthetic rehearsal CLI | BurnLens package `0.3.0` | 0 / 0 |
| `tests/test_paired_intake.py` | Unit, integration, contract, transaction, and deterministic-render checks | 20 paired-intake checks; 36 repository tests passing | 0 / 0 |
| `PAIR-INTAKE-REHEARSAL-2026-001.json` | Normalized transaction evidence | SHA-256 `e6a137eaf8a96a9a5a1362d6564aa3690691ea1b8b1a107a4873f1b173ad2970` | 0 / 0 |
| `PAIR-INTAKE-REHEARSAL-2026-001.html` | Semantic evidence report | SHA-256 `1be709541ebc23c8ee128dacca3ae63e978ccfd8f2b62eed9516f653bfe4b444` | 0 / 0 |
| `PAIR-INTAKE-REHEARSAL-2026-001.png` | Rendered evidence card | SHA-256 `4a3462c766b030277a8d6bf16ce435d39eebaf95a6a4fe6163c63118c494be88` | 0 / 0 |
| `MANIFEST-2026-005.json` | Candidate checkpoint provenance manifest | Issue #325 / PR #326; merge/tag identity pending | 0 / 0 |

The test-only synthetic fixture is created in a temporary directory and deleted in the same run. It is not source data, a retained dataset, a model input, or evidence that the exact provider package is usable.
