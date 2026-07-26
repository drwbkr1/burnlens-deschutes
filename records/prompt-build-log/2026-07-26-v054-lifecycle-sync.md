# BurnLens 0.54 lifecycle sync

**Lifecycle issue / branch:** #572 / `codex/v054-lifecycle-sync`

## Verified release

P4O1-T01 / issue #570 / PR #571 merges exact reviewed head
`d856a06cf9c62d12d633dacd614237baf912b24f` through two-parent commit
`8660ccba893b7e3acfdc361e663a6b8d59d52a34`. Both trees equal
`f6eca3779cd3d6928214bacb84f1a2ff11d87828`. Annotated tag object
`4a7a54b7fea0cba3a1c7151630e7d4ecf2d8bf82` remotely peels exactly to
that merge as `v0.54.0-rbr-geoint-milestone`.

The accepted run remains
`BL-2026-07-26-p4o1-t01-u07-package-r001`. Its 66 extracted files occupy
1,795,388 bytes. The exact 487,893-byte ZIP retains SHA-256
`91308a2ffe7095d89843edeb1634d6b1e972eb65bf1f67f38f1da0279102d84e`.
Both tracked package forms pass the authoritative validator.

## Fresh-main evidence

The first naive tracked-only full suite is retained rather than rewritten:
686 pass, two fail, 47 skip, 25 error, 112 warnings, and 86 subtests. Every
failure/error requires controlled provider archives, finalized context
custody, or ignored U02-U05 intermediate runs. The explicit portable roster
passes 686 tests with 47 existing skips, two exact custody assertions
deselected, 112 warnings, and 86 subtests.

Two fresh-main fixed-epoch wheels are byte-identical to the reviewed candidate
at 1,166,315 bytes and SHA-256
`ad3ae7c8e382fa8bc01ed0e9f9f073ad628432bb9efbae92ac15afcffb619d94`.
An isolated CPython 3.12.10 environment installs 71 compatible distributions,
imports BurnLens 0.54.0, Torch 2.13.0+cpu, Rasterio 1.5.0, and GeoPandas
1.1.4, and passes all 114 installed command-help routes. A disposable helper
attempt that counted a JSON array as one object is retained; it executed zero
commands and changed no package or project byte.

## Boundary and handoff

This sync changes lifecycle and current-truth records only. It does not change
source code, dataset, split, label, threshold, baseline, model, training,
evaluation, raster, vector, interface, package, ZIP, provider, custody,
deployment, GitHub Release, external submission, access, ownership, or public
sharing. RBR remains the accepted analytical method. The bounded U-Net remains
a rejected diagnostic and is never claimed to outperform RBR. No Phase 3B or
second experiment is created or planned.

Phase Four is verified. After this bounded synchronization merges, the next
cycle begins from the exact run/interface and selects the highest-leverage
Phase Five reliability checkpoint. The synchronization PR's own terminal
merge remains in GitHub history; no recursive lifecycle sync is required.
