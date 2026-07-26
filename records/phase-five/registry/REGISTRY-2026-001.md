# Phase Five evidence registry

Milestone: `P5O1-T01`

Issue: #574

Branch: `codex/p5o1-t01-reliability-release-candidate`

Verified base: `3c0ec9ef893b0e610c6c38c70a191e5e67c09ca9`

| Unit ID | Purpose | Inputs and hashes | Outputs and hashes | Gates | Disposition | Failure or limitation retained | Next dependency |
|---|---|---|---|---|---|---|---|
| `P5O1-T01-U01` | Lock QA and release-control standard | Verified v0.54 ZIP `91308a2f...`; receipt `e2c80230...`; manifest `b15f5d00...`; checksums `eb08e659...`; interface `7a657ad7...`; status `1a720a44...`; release audit `3942190b...` | Contract 10,836 bytes / `a187a9d1...`; research 2,401 bytes / `a6884674...`; loader 7,976 bytes / `d7131942...`; CLI 1,237 bytes / `10abcb0f...`; tests 3,011 bytes / `f1ce0b7d...` | Ten focused contract/package tests pass with 20 existing NumPy warnings; contract CLI passes six units/five injections; both canonical package forms pass at 66 files/10 GeoTIFFs; JSON, lock, and diff gates pass | `pass` | Attempt r001a omitted the `dev` extra, removed pytest, and did not run the test gate; later commands passed because PowerShell did not stop on the native failure. Corrected r001b restores `dev`, checks every native exit, and passes. Local `file://` browser automation remains policy-blocked and is not bypassed. | `P5O1-T01-U02` |
| `P5O1-T01-U02` | Prove fail-closed diagnosis and safe recovery | Passed U01 contract `a187a9d1...`; canonical ZIP `91308a2f...`; extracted interface `7a657ad7...` | Hardened package validator; deterministic five-fixture runner; focused regression tests; production evidence not yet executed | Code-level fixture determinism, exact diagnoses, no-overwrite, canonical validation after every injection, compile | `remediate` pending clean-code production run | Pre-fix r001: partial package leaked raw `FileNotFoundError`; wrong accepted method, route, and run ID unexpectedly returned `PACKAGE_VALIDATION_PASS`. Missing, corrupt, and traversal fixtures rejected. Canonical forms remained valid. | Commit/push clean U02 implementation, then execute immutable r002 |
| `P5O1-T01-U03` | Validate accessibility, browser posture, and reviewer clarity | blocked by U02 | not created | not run | pending | none yet | U02 |
| `P5O1-T01-U04` | Validate security, integrity, licenses, claims, and performance | blocked by U03 | not created | not run | pending | none yet | U03 |
| `P5O1-T01-U05` | Prove clean reconstruction, release identity, and rollback | blocked by U04 | not created | not run | pending | none yet | U04 |
| `P5O1-T01-U06` | Freeze candidate and Phase Six recommendation | blocked by U05 | not created | not run | pending | none yet | U05 |
