# Phase Four milestone registry

Issue #570 controls milestone `P4O1-T01` on branch
`codex/p4o1-t01-rbr-geoint-milestone`. Exact branch base
`e8745b70c4cfe0d070e08e399efbab09e74cd06f` is the verified lifecycle merge
from PR #569.

## Unit ledger

| Unit or attempt | Immutable identity | Inputs and outputs | Gates and disposition | Next dependency |
|---|---|---|---|---|
| `P4O1-T01-U01-ENTRY-R001` | retained validation attempt | Eleven frozen control artifacts and the eight-file rejected-model package | Every file identity passes; package inventory reconstruction fails because the first checker uses case-sensitive order instead of the established Windows canonical case-insensitive order. `retained-tool-reconstruction-failure`; no data drift and no arrays opened. | Correct only the inventory ordering |
| `P4O1-T01-U01-ENTRY-R002` | accepted entry attempt | Same eleven frozen bindings; eight package members / 583,992 bytes; two exact Ward Creek patch rosters and eight patch-array hashes | Exact 1,185-byte inventory reproduces at `ce39c41c...`; every binding, roster, CRS, transform, shape, class, byte count, and SHA-256 passes. `pass`; no arrays opened, provider call, or new source byte. | Freeze U01 contract |
| `P4O1-T01-U01-CONTRACT-R001` | run `BL-2026-07-26-p4o1-t01-u01-contract-r001` | Contract JSON 19,991 bytes / `a50966b3...`; fail-closed loader 9,285 bytes / `877fd1aa...`; four-test validator 2,463 bytes / `0f4810cf...` | Candidate freezes RBR primary, rejected U-Net diagnostic, exact roster and bytes, component ownership, state taxonomy, output/run contracts, failure behavior, claims, no-Phase-3B and no-second-experiment boundaries. | Independent validation, commit, and recoverable push; then U02 |
| `P4O1-T01-U01-PORTABILITY-R001` | post-commit checkout gate | Commit `09eaf6b...`; new Phase Four text families | Index and current worktree contain LF, but the first committed checkpoint lacks explicit Phase Four checkout attributes. Correct within U01 before detached verification; no artifact bytes or semantics changed. `remediate`. | Add exact LF/binary rules and verify clean checkout |

## Current truth

- Accepted analytical method: `burnlens-baseline-v0.1.0`,
  `rbr-threshold`, frozen threshold `0.041043221950531006`.
- Rejected diagnostic: `burnlens-unet-binary-v0.1.0`, frozen threshold
  `0.5`, never accepted and never described as outperforming RBR.
- Integration roster: only Ward Creek `WCP-001` burned and `WCP-002`
  background on their exact EPSG:32610 native 20 m grids.
- Existing Phase Two and Phase Three artifacts are read-only inputs.
- No Phase 3B, second experiment, new label, dataset, split, AOI, threshold,
  provider transaction, context acquisition, inference output, deployment, or
  public-sharing change exists at U01.

All later failed, superseded, degraded, no-detection, fallback, failed, and
withheld attempts remain in this registry rather than being rewritten as
success.
