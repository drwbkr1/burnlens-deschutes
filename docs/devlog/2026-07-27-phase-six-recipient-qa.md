# Phase Six recipient QA

## 2026-07-27 — U06 passes the real extracted route

The corrected U05 ZIP was extracted without overwrite into ignored
repository-local staging. The recipient copy contains 117 files and
16,285,070 bytes, with exact path, size, and SHA-256 equality to the tracked
directory form.

The actual package entrypoint, canonical portfolio surface, Ward Creek
interface, and presentation render correctly at 1440×900 and 390×844. There is
no horizontal overflow, console error, page error, or external runtime asset.
The WCP-002 focus control works, and turning on the rejected U-Net keeps it
explicitly diagnostic. A standalone Chrome keyboard pass confirms the skip
link is the first page focus and Return lands on visibly focused `MAIN#main`.

The package serves all 117 files over loopback HTTP with exact byte counts and
zero non-200 response. Its 20 HTML files contain 138 references and no
external auto-fetch or click-only URL.

Fresh-checkout r001 failed safely because the first ignored clone path exceeded
Windows filename limits. The incomplete clone was not used. R002 moved the
same test to a short ignored path with Git long-path support, started clean,
validated the tracked archive, and rebuilt the exact 14,963,469-byte ZIP at
SHA-256 `5a314b69...`. The verified Phase Five predecessor remains available
through its local and remote annotated tag and exact validating ZIP.

The first focused regression attempt deliberately occurs before the evidence
commit. Seven tests pass; the checkout-contract test rejects the changed
worktree because it does not yet equal `HEAD`. The result is retained as an
invalid pre-commit proof and must be replaced by the identical committed-state
run before push.

U06 therefore passes as local recipient QA. This does not publish BurnLens.
RBR remains accepted for the bounded Ward Creek route; the U-Net remains
rejected and did not outperform RBR; WCP-002 remains visible. U07 now owns the
release audit and publication-gate decision.
