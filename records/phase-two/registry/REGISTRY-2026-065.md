# REGISTRY-2026-065 - BL-PORT-001 portfolio reviewer experience

**Issue / branch:** #540 / `codex/p2o4-t36-portfolio-reviewer-experience`

**Base:** `3dc057a210da024d4bba4e1db41e8b5c891663aa`

| Unit | Objective | Inputs | Disposition | Retained failures | Next dependency |
|---|---|---|---|---|---|
| `T36-U01` | Run the current tool and inspect the current rendered reviewer surface | exact v0.47 custody; tracked Windigo HTML | `pass` | none | U02 |
| `T36-U02` | Freeze reviewer questions, input roster, claim boundaries, lineage, and local/offline contract | PRECHECK-2026-067; issue #540 | `pass` | none | U03 |
| `T36-U03` | Build one deterministic portfolio manifest and landing surface | five exact bound inputs; source checkpoint pending | `in_progress` | first focused test expected the not-yet-generated self manifest to exist; test corrected to exempt only that future output | U04 |
| `T36-U04` | Align quickstart, case study, and repository handoff | exact U03 output | `blocked_on_U03` | none | U05 |
| `T36-U05` | Real render, accessibility, privacy, link, and reproducibility QA | exact U03/U04 output | `blocked_on_U04` | none | U06 |
| `T36-U06` | Release verification and August 6 submission handoff | complete unit ledger | `blocked_on_U05` | none | milestone exit |

The initial U03 source implementation adds one standard-library generator, one
CLI, focused tests, a quickstart, explicit LF output rules, BurnLens 0.48.0,
and the 87th command. Focused implementation and environment tests pass nine of
nine after the retained self-link test correction.

Dataset, split, baseline, model, deployment, GitHub Release, access, and
public-sharing state remain unchanged.
