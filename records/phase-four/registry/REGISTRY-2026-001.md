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
| `P4O1-T01-U01-CUSTODY-R001` | detached-checkout preflight | Contract-declared `runs/phase-four/` root | The first preflight finds the path is not ignored and creates no directory. Add a repository-local ignore rule before any Phase Four attempt or clean-checkout state is created. `remediate`; zero run bytes created. | Verify ignore behavior, commit, and run detached checkout |
| `P4O1-T01-U01-VERIFY-R001` | detached commit `f43907f0fc770351514410621e8bc07cd6a18195` | Fresh ignored worktree; locked 18-distribution dev environment; exact contract `a50966b3...` | Phase Four evidence checks out LF; four focused tests, loader, compilation, lock, dependency, diff, and clean-status gates pass. Temporary worktree is removed after verification. U01 `pass`. | P4O1-T01-U02 deterministic analytical runner |
| `P4O1-T01-U02-IMPLEMENTATION-R001` | source `cf67113dbae0e05dd034b0cca5d2a98f2a4bfb9f` | Fail-closed runner, CLI, four focused runner tests, one package entry point | Exact contract/array/hash/shape/channel/normalization/weight/threshold gates; RBR primary; rejected U-Net diagnostic; no tuning or selection path; 8 combined U01/U02 tests, compilation, CLI help, lock, dependency, and diff checks pass. | Execute immutable U02 run |
| `P4O1-T01-U02-ANALYSIS-R001` | run `BL-2026-07-26-p4o1-t01-u02-analysis-r001` | 14 ignored files / 104,703 bytes; inventory 1,416 bytes / `28739c6d...`; manifest 12,244 bytes / `c969bb10...` | State `accepted-baseline`. WCP-001: RBR 3,536 positives, rejected U-Net 4,095. WCP-002: RBR 1,669, rejected U-Net 3,206. No accepted model or geospatial product. | Independent validation |
| `P4O1-T01-U02-VERIFY-R001` | record `PHASE-FOUR-ANALYSIS-RECORD-2026-001` | Exact U02 arrays plus frozen Phase Three probability/prediction arrays | Independent RBR formula replay is exact; rejected-U-Net probability and binary arrays equal Phase Three values; exclusion equals inverse input-valid; receipts pass; 8 focused tests pass. U02 `pass`. | U03 geospatial products |
| `P4O1-T01-U02-DUPLICATE-R002` | retained no-overwrite attempt | Existing U02 run ID and 14 files | Duplicate invocation exits 1 with `run already exists`; file count and every SHA-256 remain unchanged. `retained-no-overwrite-refusal`. | U03 |
| `P4O1-T01-U03-GEOSPATIAL-R001` | run `BL-2026-07-26-p4o1-t01-u03-geospatial-r001`; source `6c085c9...` | Ten GeoTIFFs, GeoPackage, GeoJSON, quicklook, validation, status, and custody files | Raster/vector integrity passes, but the Windows font fallback renders portfolio evidence text too small. `retained-failed-render-qa`. | Correct deterministic fallback sizing |
| `P4O1-T01-U03-GEOSPATIAL-R002` | run `BL-2026-07-26-p4o1-t01-u03-geospatial-r002`; source `618fdd4...` | Same bounded product roster; sized fallback quicklook 41,774 bytes / `be12c40e...` | Visual hierarchy is restored, but the fallback font lacks the em-dash glyph and renders a visible square. `retained-failed-render-qa`. | Use a portable separator |
| `P4O1-T01-U03-GEOSPATIAL-R003` | run `BL-2026-07-26-p4o1-t01-u03-geospatial-r003`; source `761ef33...` | 18 ignored files / 549,068 bytes; inventory 1,827 bytes / `79124d13...`; manifest 11,446 bytes / `dc751576...`; 10 rasters, 202 accepted RBR polygons, GeoJSON, and 1280x720 quicklook | Native-grid GeoTIFFs pass; GeoPackage opens in the locked stack; every geometry is valid; polygon rasterization exactly reproduces 3,536 and 1,669 RBR-positive pixels; rendered quicklook passes visual QA; model remains rejected. U03 `pass`. | U04 context source and terms gate |
| `P4O1-T01-U03-DUPLICATE-R004` | retained no-overwrite attempt | Existing accepted U03 run ID and 18 files | Duplicate invocation exits 1 with `run already exists`; file count and every SHA-256 remain unchanged. `retained-no-overwrite-refusal`. | U04 |
| `P4O1-T01-U04-SOURCE-GATE-R001` | `PHASE-FOUR-CONTEXT-SOURCE-GATE-2026-001`; commit `73d565e...` | Four separate sources; 32 required criteria; 35 evidence items, including 23 fresh live observations | TNM NTD, NSD, NBD and exact local Ward Creek MTBS reuse pass identity, authority, access, rights, provenance, integrity, fitness, and privacy/security. Bounded GeoJSON intake only; no bulk package or new MTBS request. `ready`. | Commit exact intake plan |
| `P4O1-T01-U04-INTAKE-R001` | run `BL-2026-07-26-p4o1-t01-u04-context-r001`; source `2094043...` | Eight promoted GeoJSON responses / 890,072 bytes; final contract 17,290 bytes / `3cc26f5b...`; run inventory 25,215 bytes / `948f6b26...` | Exact counts: 169 roads, eight selected public facilities, and one BLM boundary; minimal fields, valid finite EPSG:4326 geometry, HTTPS, no redirects, no auth, no overwrite, and single-link custody pass. | Revalidate exact local MTBS boundary |
| `P4O1-T01-U04-MTBS-REUSE-R001` | archive `d94dfb16...`; event `OR4494912090120190812`; map `10016337` | Existing governed 4,385,952-byte archive; 16 members / 13 files; one valid EPSG:32610 boundary / 8,378,927.386 m2 | Full CRC, exact four-member boundary hashes, event/map identity, geometry, embedded rights, and live role cautions pass. Reference context only, never ground truth or operational incident perimeter. U04 `pass`. | U05 overlays and deterministic summary |
| `P4O1-T01-U05-OVERLAY-R001` | run `BL-2026-07-26-p4o1-t01-u05-overlay-r001`; source `2f96cc6...` | 10 ignored files / 774,062 bytes; inventory 945 bytes / `770f580e...`; manifest 8,088 bytes / `cf235bee...`; four web context layers, five observations, and 1600x1000 quicklook | Native EPSG:32610 measurements and web EPSG:4326 context independently pass. WCP-001 RBR is 141.44 ha with 94.19% MTBS overlap. WCP-002 RBR is 66.76 ha with zero MTBS overlap, retained as visible baseline false-positive-risk evidence. The rendered quicklook and all claim boundaries pass. U05 `pass`. | U06 repository-owned evidence interface |
| `P4O1-T01-U05-DUPLICATE-R002` | retained no-overwrite attempt | Existing accepted U05 run ID and manifest `cf235bee...` | Duplicate invocation exits 1 with `run already exists`; the manifest hash remains exact. `retained-no-overwrite-refusal`. | U06 |

## Current truth

- Accepted analytical method: `burnlens-baseline-v0.1.0`,
  `rbr-threshold`, frozen threshold `0.041043221950531006`.
- Rejected diagnostic: `burnlens-unet-binary-v0.1.0`, frozen threshold
  `0.5`, never accepted and never described as outperforming RBR.
- Integration roster: only Ward Creek `WCP-001` burned and `WCP-002`
  background on their exact EPSG:32610 native 20 m grids.
- Existing Phase Two and Phase Three artifacts are read-only inputs.
- No Phase 3B, second experiment, new label, dataset, split, AOI, threshold,
  provider transaction, deployment, or public-sharing change exists through
  U05.
- U01 is complete at the independently verified `f43907f...` checkpoint; its
  next eligible dependency is U02.
- U02 is complete at source `cf67113...` and run
  `BL-2026-07-26-p4o1-t01-u02-analysis-r001`. RBR is the accepted analytical
  output; the U-Net remains a visibly rejected diagnostic.
- U03 is complete at source `761ef33...` and accepted run
  `BL-2026-07-26-p4o1-t01-u03-geospatial-r003`. Its ten native-grid rasters,
  accepted RBR vectors, web representation, and rendered quicklook pass.
- U04 is complete at source `2094043...` and run
  `BL-2026-07-26-p4o1-t01-u04-context-r001`. Eight exact public TNM query
  responses and the already-governed exact Ward Creek MTBS boundary pass.
- U05 is complete at source `2f96cc6...` and run
  `BL-2026-07-26-p4o1-t01-u05-overlay-r001`. Its exact native measurements,
  web context layers, deterministic observations, and rendered quicklook pass.
  The background patch visibly preserves the accepted baseline's
  false-positive risk. U06 is eligible.

All later failed, superseded, degraded, no-detection, fallback, failed, and
withheld attempts remain in this registry rather than being rewritten as
success.
