# Phase Five reliability milestone

## Current result

P5O1-T01 / issue #574 has completed U01 through U06. The verified Phase Four
RBR-primary package remains analytically unchanged: RBR is accepted, the
trained U-Net remains a rejected diagnostic that did not outperform RBR, and
WCP-002 remains visible false-positive-risk evidence.

U06 accepts corrected candidate
`burnlens-phase-five-baseline-first-candidate-v0.1.1`. PR #575 subsequently
merges the exact reviewed head, fresh-main verification passes, and the remote
annotated tag peels to the merge. Phase Five is now verified; lifecycle details
are recorded in `docs/devlog/2026-07-27-v055-lifecycle-sync.md`.

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

## U06 candidate freeze

Run `BL-2026-07-26-p5o1-t01-u06-release-candidate-r002` freezes 23 files /
981,264 bytes into one deterministic 646,513-byte ZIP at SHA-256
`691c4bddb6754d74ca858a0b801fb21e62103032184425d2ba1b1648df1b0c26`.
Both extracted and archive validators pass, and a separate ignored replay
reproduces the archive byte-for-byte.

Microsoft Edge renders the exact candidate index at 1440-by-1000 and
390-by-844 without horizontal overflow. All six local links and both core
interfaces return HTTP 200, keyboard-first focus is visible, and no external
resource or browser error occurs. The temporary server is stopped.

Two fixed-epoch BurnLens 0.55.0 wheels are byte-identical at 1,207,948 bytes /
SHA-256 `1d0e862c9c7d30f148352ebcc45f22a9deb2e010dd61ba63a02db50f700177f6`.
A fresh CPython 3.12.10 environment contains 75 compatible distributions,
imports BurnLens only from isolated `site-packages`, and passes all 120
console routes in both geospatial and model profiles.

The first clean candidate suite exposed a missing explicit LF checkout rule
for the Phase Five objectives file. That 787-pass / two-failure run remains
retained. Commit `a53bcd85413c524ae9fd0ac6007ba59ba778d532` adds the
exact rule; both failed tests pass, and the complete clean suite then passes
789 tests, one expected skip, 422 existing warnings, and 86 subtests in
665.38 seconds.

The immutable pre-merge controlling record is 11,367 bytes / SHA-256
`76c2c129...`; its pre-merge release audit is 7,005 bytes / SHA-256
`9f47ecbd...`. They retain the superseded r001
candidate, all pre-remediation and dirty-checkout failures, the wrapper
timeout, and the LF failure. The later lifecycle audit verifies the single
milestone PR, reviewed merge, fresh-main suite, exact wheel, and annotated tag.
Phase Six is eligible for issue-backed activation.

## Boundaries

No analytical byte, dataset, split, label, model decision, threshold,
deployment, access, ownership, public-sharing status, or external submission
changed. No Phase 3B or second experiment was created. The candidate has zero
open critical/high findings and two visible medium findings with impact and
workaround; rollback is verified. No GitHub Release, deployment, access,
ownership, public-sharing, or external-submission change occurred.
