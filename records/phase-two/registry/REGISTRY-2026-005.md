# REGISTRY-2026-005 - Paired-Intake Transaction Artifacts

**Checkpoint:** Issue #325 / PR #326; candidate branch `codex/p2o2-t02-intake-transaction`; proposed tag `v0.3.0-intake-transaction-baseline`

| Artifact | Class | Version/state | Provider/synthetic bytes retained |
|---|---|---|---:|
| `burnlens/paired_intake.py` | Exact validation, link-alias rejection, hashing, ZIP inspection, retry-safe atomic registration, registered-package verification, report rendering | BurnLens package `0.3.0`; report-generator source `ac8ee43151991c38ccf5d446a53c09b617afeb54` | 0 / 0 |
| `burnlens/rehearse_paired_intake.py` | Real-state and temporary synthetic rehearsal CLI | BurnLens package `0.3.0` | 0 / 0 |
| `tests/test_paired_intake.py` | Unit, integration, contract, transaction, and deterministic-render checks | 21 paired-intake checks; 37 repository tests passing | 0 / 0 |
| `PAIR-INTAKE-REHEARSAL-2026-001.json` | Normalized transaction evidence | SHA-256 `94e311fd608f9c10e024138d9eff6abf0f70187a69c031264e91cb8d9d1af234` | 0 / 0 |
| `PAIR-INTAKE-REHEARSAL-2026-001.html` | Semantic evidence report | SHA-256 `b76cbf50f60dd112430616b4a472ac440444cbf48194a0672df91876e78ea20c` | 0 / 0 |
| `PAIR-INTAKE-REHEARSAL-2026-001.png` | Rendered evidence card | SHA-256 `c38bf7fc825dd780affe3f8d1080cffb3bdb90ef2164cb27b1295b4e54bbfcd0` | 0 / 0 |
| `MANIFEST-2026-005.json` | Candidate checkpoint provenance manifest | Issue #325 / PR #326; merge/tag identity pending | 0 / 0 |
| `ACCESS-2026-006` | Owner authorization record; no secret material or provider request | `AUTHORIZED_NOT_ACCESSED` | 0 / 0 |

The test-only synthetic fixture is created in a temporary directory and deleted in the same run. It is not source data, a retained dataset, a model input, or evidence that the exact provider package is usable.
