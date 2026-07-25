# PRECHECK-2026-087 - P2O4-T39 release candidate

**Date:** 2026-07-25

**Issue / PR:** #554 / #557

**Release-code candidate:** `064da9a89202f84fe377d74a01caa4e81a88252d`

**Disposition:** `candidate-pass-not-released`

## Exact milestone result

P2O4-T39 completes U01 through U08. Ward Creek passes the complete source,
custody, reference, background, proposal, owner-review, pre-reveal lock, and
two-class promotion path.

The accepted sufficiency run remains
`BL-2026-07-25-replacement-six-event-dataset-sufficiency-r003` at scientific
source `af37f80dd17febacfbb1cf2801665d74edb16475`.

The exact McKay, Tepee, Green Ridge, Grandview, Windigo, and Ward Creek
candidate excludes Darlene. It contains 12 balanced prototype regions, 287
accepted core pixels, and 531 excluded unknown-ring pixels.

All ten readiness gates pass. Fifty-four of 90 whole-event 2/2/2 assignments
pass the frozen transfer, source-program, and exact source-regime rules.
Training remains unauthorized.

## Release verification

- The six accepted readiness artifacts replay byte for byte from their exact
  scientific source.
- The full custody-enabled suite passes 656 tests, one expected skip, 96
  retained NumPy deprecation warnings, and 86 subtests.
- Compilation, `uv lock --check`, `uv pip check`, and `git diff --check` pass.
- All 175 tracked JSON documents parse.
- All 810 tracked Markdown files scan with zero missing targets among 239
  detected local links.
- Added-line privacy checks find no private path, credential, token, recipient,
  or live retrieval URL.
- The accepted HTML passes real 1280 by 720 and 390 by 844 browser checks with
  no body overflow or warning/error logs.
- Draft PR #557 targets exact base
  `657ba657ab9d23964dcaf76d377aec3a10e814da`, initially binds remote head
  `064da9a89202f84fe377d74a01caa4e81a88252d`, and is `MERGEABLE` / `CLEAN`
  with no configured checks.

## Package verification

Two fixed-epoch builds at `SOURCE_DATE_EPOCH=1784996074` produce the same
209-member wheel:

- `burnlens_deschutes-0.51.0-py3-none-any.whl`
- 993,480 bytes
- SHA-256
  `414fa8c118ac538239906c4b6e9437eaaeb07fd27be40b44c617415791674477`

The wheel has unique safe paths, no symlinks, BurnLens version 0.51.0, the MIT
license, Python 3.12-or-newer metadata, and 99 console commands.

A fresh isolated CPython 3.12.10 base-runtime install resolves 13 compatible
packages. All 99 commands load and pass `--help`.

## Retained release attempts

The first full-suite run at version-preparation source `35e1173...` reported
652 passes, two failures, one expected skip, 96 warnings, and 86 subtests.
Only the environment-profile tests failed because the local installed
distribution still reported 0.50.0. The repository setup path refreshed the
environment, after which the suite passed.

The first deterministic wheel is retained at 993,307 bytes / SHA-256
`b1bc02ad4c6828e1a43b4dc9ced1ad024f1d5cc504ffdaacef9461cd2abf1458`.
Its lean-runtime verifier fails because the Ward Creek response-intake command
eagerly imports optional GeoPandas.

Commit `064da9a...` moves that optional import behind argument parsing, keeps
base-runtime help available, and emits the exact `geo-research` setup guidance
for real execution. Fifteen focused tests and the complete final suite pass.
No scientific output changes.

Replay r001 ran from the canonical working directory and therefore loaded
BurnLens 0.51.0 instead of the recorded 0.50.0 source. It retained the same
science and PNG but correctly failed exact text identity.

Replay r002 runs from the extracted exact scientific source and reproduces all
six accepted artifacts byte for byte.

## Boundary and next dependency

This release candidate creates no dataset, split, baseline, model, metric,
training run, inference output, deployment, or external submission.

Merge, fresh-main repetition, annotated-tag creation, and remote tag peel
remain required before the release becomes verified. After that verification,
open the separate accepted-dataset, whole-event split, QA, and strongest
justified non-model baseline milestone.
