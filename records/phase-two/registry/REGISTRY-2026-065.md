# REGISTRY-2026-065 - BL-PORT-001 portfolio reviewer experience

**Issue / branch:** #540 / `codex/p2o4-t36-portfolio-reviewer-experience`

**Base:** `3dc057a210da024d4bba4e1db41e8b5c891663aa`

| Unit | Objective | Inputs | Disposition | Retained failures | Next dependency |
|---|---|---|---|---|---|
| `T36-U01` | Run the current tool and inspect the current rendered reviewer surface | exact v0.47 custody; tracked Windigo HTML | `pass` | none | U02 |
| `T36-U02` | Freeze reviewer questions, input roster, claim boundaries, lineage, and local/offline contract | PRECHECK-2026-067; issue #540 | `pass` | none | U03 |
| `T36-U03` | Build one deterministic portfolio manifest and landing surface | five exact bound inputs; source `7ffb8ce74350c34f60c36765e194a2aab29dbcd9` | `pass` | first focused test expected the not-yet-generated self manifest to exist; first production render exposed one missing-favicon request; first favicon-focused run exposed a test-only inline-data-link assumption | U04 |
| `T36-U04` | Align quickstart, case study, and repository handoff | exact U03 output | `pass` | none | U05 |
| `T36-U05` | Real render, accessibility, privacy, link, and reproducibility QA | exact U03/U04 output; owner render confirmation | `pass` | first render retained as failed because its missing favicon made the console non-clean | U06 |
| `T36-U06` | Release verification and August 6 submission handoff | complete unit ledger | `pass` | first full suite retained 553 passes / one skip / 28 stale current-version failures; first isolated check used omitted pip and source-tree import; corrected candidate and fresh-main gates pass | deterministic August 6 submission bundle |

The U03 source implementation adds one standard-library generator, one CLI,
focused tests, a quickstart, explicit LF output rules, BurnLens 0.48.0, and the
87th command.

Final run `BL-2026-07-24-portfolio-reviewer-experience-r002` produces:

| Output | Bytes | SHA-256 |
|---|---:|---|
| JSON | 5,675 | `cfab6176a9e5f1e9c4636e56658cf1ded9092825c3f55c7ebfb9968b2a68a078` |
| HTML | 14,602 | `e133a22978d73335c8a67fa39ae5ff48279b67ac6f71c615d95f62c021fda3ae` |

An independent ignored replay matches both outputs byte for byte. Desktop and
narrow browser checks pass without overflow. Both images and all nine local
destinations load, keyboard order is reviewer-first, the console is clean, and
no external request occurs. The owner confirmed the exact page renders
correctly.

PRECHECK-2026-068 and MANIFEST-2026-050 bind the output and QA state. U06 must
still pass full repository, package, isolated-install, release-truth, and
merged-main gates before shipment.

The corrected full suite passes 581 tests, one expected skip, 22 warnings, and
86 subtests. Two exact Git archives produce the same 881,588-byte wheel at
SHA-256
`4966fd403f6207a4afd63c1fa68658091467e6744dfc332313ca72b2e9811c9b`.
The isolated install resolves BurnLens 0.48.0 from `site-packages`, has 13
compatible distributions, and passes 87 command probes.

PR #541 merges at `05140217066277b254e78abb74cd8f61295449d0`.
Fresh main repeats nine focused tests, the 581-test full suite, exact outputs,
the canonical wheel, isolated install, and all 87 command probes. Remote
annotated tag object `c6ed831c106da44bad3ced010fafe5abc46bd537`
peels exactly to that merge.

The structured release audit computes `verified`. U06 and P2O4-T36 pass.

Dataset, split, baseline, model, deployment, GitHub Release, access, and
public-sharing state remain unchanged.
