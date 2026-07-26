# PRECHECK-2026-005 — P3O1-T01 release-candidate checkout remediation

**Recorded:** 2026-07-26

**Issue:** #566

**Candidate before remediation:** `d1101a06e9fd512096aa398687838ab2ab0e8278`

## Retained attempts

1. The first full-suite command used the model-only environment. Collection
   stopped with five missing-optional-geospatial import errors before any test
   or scientific output ran.
2. The first combined-profile wrapper reached its ten-minute outer timeout
   during subprocess-heavy environment verification. Exact lingering
   verification processes were identified by command line and stopped; the two
   intentional local review servers remained running.
3. The complete combined-profile suite then ran to completion: 728 tests
   passed, one expected test skipped, 86 subtests passed, and one checkout
   contract failed. `.gitignore`,
   `docs/phases/phase-03/PHASE_03_OBJECTIVES.md`, and
   `scripts/setup_worktree.ps1` retained pre-contract CRLF working bytes even
   though their current attributes require LF.
4. A targeted rerun passed all eight environment-profile tests but repeated the
   checkout failure because the three portability edits were still uncommitted
   and the patching path preserved their existing CRLF bytes.

## Bounded remediation

The exact three files receive meaningful release-QA documentation plus an
explicit UTF-8-without-BOM LF formatting pass. No dataset, split,
normalization, label, baseline, model, weight, probability, prediction,
evaluation, package, owner-response, provider, or test-opening byte changes.

The remediation must be committed and pushed before verification. From that
clean exact commit, BurnLens must pass the checkout contract, focused model and
portfolio tests, both environment-profile tests, and the complete
combined-profile suite before a pull request may open.

## Disposition

`remediate-checkout-bytes`; release remains blocked pending clean-commit
verification.
