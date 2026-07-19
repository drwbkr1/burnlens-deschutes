# PRECHECK-2026-031 - Additional Whole-Event Group Freeze

**Issue:** #466

## Entry evidence

- The verified v0.31.0 checkpoint contains six owner-approved prototype regions across only three immutable events.
- The cycle-start official-source scout reconstructs all four tracked outputs byte for byte.
- The current scout's highest-ranked fires are mostly Landsat-era or otherwise unsuitable for the main Sentinel comparison pool.
- Current official MTBS and Burn Severity Portal services expose bounded Central Oregon Sentinel-era candidates, while current CDSE STAC metadata can test full-boundary single-item coverage and exact scene identities.

## Allowed work

Capture current official metadata for a bounded five-event pool; verify identity, dates, size, source programs, boundaries, terms, exact Sentinel item coverage, scene comparability, catalogue size, and acquisition routes; freeze three event/scene/geography/time groups; render aggregate evidence; keep provider imagery at zero bytes.

## Prohibited work

Do not download provider imagery, promote a pixel or label, infer background from absence, treat catalogue cloud or an official reference as truth, create a dataset or split, run a baseline or model, spend money, add a secret or service, change sharing/access state, or use `burnlens-site`.

**Entry decision:** `PROCEED_METADATA_ONLY_FREEZE_FAIL_CLOSED_ON_IDENTITY_TERMS_COVERAGE_OR_PAIR_DRIFT`.
