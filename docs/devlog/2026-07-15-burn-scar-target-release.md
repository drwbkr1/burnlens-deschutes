# Devlog - The Tag Came After the Failure

**Date:** 2026-07-15

**Issue:** #341

The first target-decision merge was not released merely because tests passed. Its post-merge real reconstruction failed, so BurnLens withheld the tag, preserved the failed run, corrected the serialization contract, and tried the exact workflow again from `main`.

That second check passed. Corrected run `r002` reproduced JSON, HTML, and PNG byte for byte. All 69 tests, compilation, dependency health, canonical LF checkout, secret/raw-byte exclusion, issue closure, PR merge, and remote tag identity also passed.

The accepted repository state is remediation merge `bcb71ebd01d3184f8de24318428309e61d33e54f`. Annotated tag object `0b4e0ff226be0d78b3b510b7786be0ca1c817887` remotely peels to that exact commit as `v0.6.0-burn-scar-target-baseline`.

The result is deliberately modest: BurnLens has a defensible target decision and reliable evidence package, not a burn-scar label, dataset, baseline, model, detection, application, or deployment. The next work is no longer target ideation. It is evidence on real pre/post optical pixels and a label protocol that preserves ambiguity.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
