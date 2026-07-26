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

The first disposition was `remediate-checkout-bytes`.

The bounded formatting correction was committed and pushed. Exact clean,
remote-equal candidate `938cc94d5a8cb952054977fa765b9400a66daf02`
then passed:

- 11 focused checkout/model/package/portfolio tests in 67.11 seconds;
- compilation, `uv lock --check`, dependency health, and diff checks;
- the complete combined-profile suite with 729 passes, one expected skip, 228
  warnings, and 86 subtests in 2,032.18 seconds;
- two independent fixed-epoch wheels at 1,106,162 bytes and SHA-256
  `15b8b84f5fa6a60c51cb82dc2fc001dd4740a84704ee1ecf2c827da1e7961b8b`;
- a fresh Python 3.12.10 install with 23 compatible distributions, BurnLens
  0.53.0, Torch 2.13.0+cpu, no CUDA build or availability, and all 107 command
  help routes.

Final disposition: `pass-clean-candidate`. The retained failures above remain
part of the release history; no scientific, package, model, evaluation, or test
opening byte was changed by the remediation.
