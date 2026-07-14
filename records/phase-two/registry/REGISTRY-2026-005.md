# REGISTRY-2026-005 - Paired-Intake Transaction Artifacts

**Checkpoint:** Issue #325 / PR #326; candidate branch `codex/p2o2-t02-intake-transaction`; proposed tag `v0.3.0-intake-transaction-baseline`

| Artifact | Class | Version/state | Provider/synthetic bytes retained |
|---|---|---|---:|
| `burnlens/paired_intake.py` | Exact three-asset validation, link-alias rejection, hashing, ZIP inspection, atomic registration, report rendering | BurnLens package `0.3.0`; report-generator source `8f1f82f97afc4fb52f787c6353a9aedd0f36cea3` | 0 / 0 |
| `burnlens/rehearse_paired_intake.py` | Real-state and temporary synthetic rehearsal CLI | BurnLens package `0.3.0` | 0 / 0 |
| `tests/test_paired_intake.py` | Unit, integration, contract, transaction, and deterministic-render checks | 19 paired-intake checks; 35 repository tests passing | 0 / 0 |
| `PAIR-INTAKE-REHEARSAL-2026-001.json` | Normalized transaction evidence | SHA-256 `c2bed364223184e176b8b58fa366f97df5143b5d3c59bafadacebcaa504f08da` | 0 / 0 |
| `PAIR-INTAKE-REHEARSAL-2026-001.html` | Semantic evidence report | SHA-256 `d47a912d1326743b2a2da64cabeda8321d319ecf81578ae5aea1d4ead797b33c` | 0 / 0 |
| `PAIR-INTAKE-REHEARSAL-2026-001.png` | Rendered evidence card | SHA-256 `06d32c6cac853fe3c9c7eea3e042c8612467959536a26a8cfddc64dfde492f1a` | 0 / 0 |
| `MANIFEST-2026-005.json` | Candidate checkpoint provenance manifest | Issue #325 / PR #326; merge/tag identity pending | 0 / 0 |

The test-only synthetic fixture is created in a temporary directory and deleted in the same run. It is not source data, a retained dataset, a model input, or evidence that the exact provider package is usable.
