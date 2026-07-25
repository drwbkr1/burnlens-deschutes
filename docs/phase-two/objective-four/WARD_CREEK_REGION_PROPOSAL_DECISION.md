# Ward Creek two-class region proposal decision

**Date:** 2026-07-24
**Milestone / unit:** P2O4-T39 / U05
**Issue:** #554
**Decision:** `pass`

## Decision

Ward Creek has exactly one deterministic burned proposal and one deterministic
affirmative-background proposal eligible for the bounded U06 owner review.

Run `BL-2026-07-24-ward-creek-region-proposal-r001` recomputes both exact
routes from immutable custody. The fixed-bin intact-component selector creates
`WCP-001`, a 14-pixel / 0.56-hectare burned core with 26 unknown-ring pixels,
and `WCP-002`, a 25-pixel / 1.00-hectare background core with 40 unknown-ring
pixels.

The burned core is smaller than the 25-pixel target because it is the nearest
eligible intact component. BurnLens does not clip, pad, merge, or expand it.
That limitation must remain visible in review and any later decision.

All five tracked outputs reproduce byte-for-byte. The exact HTML passes desktop
and narrow browser checks. Focused, full-suite, locked-environment,
fixed-epoch-package, archive-safety, and isolated-install gates pass.
PRECHECK-2026-082 and REGISTRY-2026-077 retain exact identities and the earlier
ordinary-wheel reproducibility failure.

## Boundary and next dependency

U06 may publish one blank two-candidate yes/no/uncertain owner-review batch
bound to the exact proposal JSON, both raster hashes, and each proposal
binding. It may not prefill, bulk approve, imply a preferred decision, omit a
candidate, or combine candidates from another milestone.

Both candidates remain `unreviewed-no-promotion`. The 66 ring pixels remain
excluded. No owner response, label, dataset, split, baseline, model, metric,
inference output, deployment, or external submission is created.

MTBS and optical evidence support a prototype proposal. They do not establish
ground truth, independent validation, field validation, official status,
endorsement, emergency suitability, or operational readiness.
