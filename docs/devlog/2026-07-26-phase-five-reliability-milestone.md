# Phase Five reliability milestone

## Current result

P5O1-T01 / issue #574 has completed U01 through U05. The verified Phase Four
RBR-primary package remains analytically unchanged: RBR is accepted, the
trained U-Net remains a rejected diagnostic that did not outperform RBR, and
WCP-002 remains visible false-positive-risk evidence.

U06 is now eligible. It must freeze or reject one coherent baseline-first
candidate, complete the known-issues and QA evidence package, and make an
explicit Phase Six recommendation. No Phase Five candidate or new software
release is accepted merely because U05 passed.

## Evidence completed

- U01 locks the six-unit QA and release-control contract against the immutable
  Phase Four package.
- U02 proves five controlled failures are rejected without path escape or
  accepted-output leakage, then revalidates the canonical package after every
  injection.
- U03 supplies a separate offline reliability interface. The owner confirmed
  its desktop, 390-by-844 narrow, and keyboard journey; that confirmation is
  not formal accessibility certification.
- U04 passes security, integrity, source-rights, privacy, claims, performance,
  and full-regression gates while disclosing one medium setuptools advisory
  and its bounded ZIP-only mitigation.
- U05 reconstructs the 66-file Phase Four package byte-for-byte from a fresh
  remote-equal checkout, installs a deterministic candidate wheel from
  isolated site-packages, passes the 711-test portable roster, and reproduces
  the exact historical v0.54 wheel in a separate rollback checkout.

## U05 retained truth

The naive tracked-only clone cannot satisfy ignored custody prerequisites. It
records 711 passes, two exact custody failures, 25 custody-dependent errors,
and 47 skips. The explicit portable roster then passes 711 tests with those
two exact assertions deselected and the five custody-bound builder files
excluded. BurnLens does not mislabel the naive result as portable.

Rollback first produced a deterministic but byte-different wheel because the
locked runtime uses setuptools 82.0.0 while the historical wheel embeds
setuptools 82.0.1. Exact archive comparison isolated the difference to the
`WHEEL` generator field and dependent `RECORD`. A dedicated build-only
setuptools 82.0.1 environment reproduces the historical 1,166,315-byte wheel
at SHA-256 `ad3ae7c8e382fa8bc01ed0e9f9f073ad628432bb9efbae92ac15afcffb619d94`
twice. The missing historical builder identity is retained as a visible medium
known issue with an exact workaround; it is not suppressed.

The public U05 report renders correctly at desktop and 390-by-844 narrow
widths without overflow, external resources, browser warnings, or console
errors. The browser's full-page screenshot stitcher produced one duplicated
capture despite correct DOM geometry; the normal viewport captures and
computed layout pass, and the tooling artifact is disclosed rather than used
as evidence.

## Boundaries

No analytical byte, dataset, split, label, model decision, threshold,
deployment, access, ownership, public-sharing status, or external submission
changed. No Phase 3B or second experiment was created. Phase Six remains
blocked until U06 accepts a complete inspectable and reproducible candidate
with all critical and high gates passed, every medium issue visible with
impact and workaround, and rollback verified.
