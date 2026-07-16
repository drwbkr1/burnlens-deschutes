# Atomic Reviewer-Response Intake

BurnLens could validate a returned response and write a private receipt, but the operator still had to copy the inbound file into custody manually. That gap mattered more than adding another report: a partial copy, overwrite, wrong file, or source change could break the evidence chain before the receipt was useful.

Issue #402 adds one bounded transaction. The new command validates the source, rejects duplicate evidence, stages exact bytes in the destination directory, flushes and fsyncs them, rechecks the source, validates the preserved copy, builds the same receipt from both, and promotes response plus receipt without overwrite. A partial failure removes both promoted outputs. Historical receipt protocols remain reconstructable.

The real QA run uses the existing software fixture, not fabricated human evidence. It preserves 14,749 exact bytes, writes a 2,547-byte v0.4.0 receipt, and publishes only content-withheld JSON/HTML/PNG.

![BurnLens atomic reviewer-response intake QA](../../samples/labels/review/phase-two/LABEL-REVIEW-RESPONSE-ATOMIC-INTAKE-QA-2026-001.png)

All 171 tests pass. The six previously shipped first-lock and dual-lock artifacts regenerate byte-for-byte. Compileall and dependency health pass, the rendered 1800x1280 card is readable, and privacy checks find no private path, filename, first-response hash, label distribution, timestamp, or reviewer text.

The owner later waived reviewer two. That does not convert the fixture or waiver into human evidence: the project still has one returned response, no inter-rater validation, and no adjudication. Issue #403 now owns a separate owner-waiver/reveal-readiness and conservative single-reviewer reconciliation checkpoint.
