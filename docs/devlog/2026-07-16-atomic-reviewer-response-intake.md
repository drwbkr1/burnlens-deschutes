# Atomic Reviewer-Response Intake

BurnLens could validate a returned response and write a private receipt, but the operator still had to copy the inbound file into custody manually. That gap mattered more than adding another report: a partial copy, overwrite, wrong file, or source change could break the evidence chain before the receipt was useful.

Issue #402 adds one bounded transaction. The new command validates the source, rejects duplicate evidence, stages exact bytes in the destination directory, flushes and fsyncs them, rechecks the source, validates the preserved copy, builds the same receipt from both, and promotes response plus receipt without overwrite. A partial failure removes both promoted outputs. Historical receipt protocols remain reconstructable.

The real QA run uses the existing software fixture, not fabricated human evidence. It preserves 14,749 exact bytes, writes a 2,547-byte v0.4.0 receipt, and publishes only content-withheld JSON/HTML/PNG.

![BurnLens atomic reviewer-response intake QA](../../samples/labels/review/phase-two/LABEL-REVIEW-RESPONSE-ATOMIC-INTAKE-QA-2026-001.png)

All 171 tests pass. The six previously shipped first-lock and dual-lock artifacts regenerate byte-for-byte. Compileall, dependency health, Node syntax, 54 tracked JSON parses, 122 local links, the rendered 1800x1280 card, and privacy checks pass. Two fresh-remote fixed-epoch wheels and one detached `git archive` fixed-epoch wheel from PR head `3d0f46c4160bd0e908bf2367288298cce1f97539` are byte-identical at 314,089 bytes / SHA-256 `857fb6686c83581ddbf6ae98370ac151d4b5c40642fb7bc775173a115a1670af`; an isolated install reports BurnLens `0.18.0`, 29 console entry points, and zero private/download/build entries. A stale CRLF main-workspace checkout produced a different noncanonical wheel and is excluded from package proof.

PR #404 shipped reviewed head `70a0d25042fdef09e2ecfdd118bc761b08eebfd5` as squash merge `62a8e8473613938990c40c37f91596470638f036`, closing issue #402. A fresh remote-main clone repeats 171 tests, compileall, dependency health, Node syntax, 54 JSON parses, 122 local links, exact three-output manifest verification, and the canonical wheel. Annotated tag object `572c8cea4314d89717e3c4204078704e799a5fee` remotely peels to the merge as `v0.18.0-atomic-response-intake-readiness`. Issue #405 / PR #406 synchronizes this lifecycle; its own terminal merge identity remains in GitHub history so no recursive synchronization is required.

The owner later waived reviewer two. That does not convert the fixture or waiver into human evidence: the project still has one returned response, no inter-rater validation, and no adjudication. Issue #403 now owns a separate owner-waiver/reveal-readiness and conservative single-reviewer reconciliation checkpoint.
