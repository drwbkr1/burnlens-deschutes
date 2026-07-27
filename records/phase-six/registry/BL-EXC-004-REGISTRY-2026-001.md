# BL-EXC-004 fresh-main fixture registry

Issue: #580

Exact base: `35e68a517ed08359c813c59392f74049bd699074`

| Unit ID | Purpose | Inputs | Outputs | Gates | Disposition | Retained failure or limitation | Next dependency |
|---|---|---|---|---|---|---|---|
| `BL-EXC-004-U01` | Restore honest fresh-main Phase Six verification | PR #579 merge `35e68a5...`; exact reviewed tree `a9a4185...`; clean fresh main; Phase Six focused roster | Fix `0ea5543...`; two test files / exact hashes; record `BL-EXC-004-FRESH-MAIN-VERIFICATION-2026-001` | Clean remote clone, locked dev profile, 15 focused tests, both candidate validators, structured release audit, and 18-distribution dependency health pass | `pass-pending-exception-pr-merge` | Lean-environment no-pytest attempt, five missing-parent failures, and expected pre-commit checkout failure remain retained. No product, candidate, or scientific byte changed. | One reviewed exception PR, exact merge-tree and fresh-main verification, then owner publication gate |
