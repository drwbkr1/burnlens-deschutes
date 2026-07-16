# Locking the First Returned Review Without Publishing What It Says

BurnLens had proved that its isolated reviewer workbench functioned, but the next evidence-visible risk was no longer software interaction. A real completed response had arrived, and opening or summarizing it before preserving its exact bytes would weaken the audit trail and could influence a second reviewer.

Issue #384 takes the narrow path. The exact 16,443-byte response is copied into ignored repository-local storage and verified against SHA-256 `485e80f2563f8b723c16daa8b5e5a1172dd88e8f2a28a7dd8608c933fa64eed9`. A separate ignored receipt binds it to the shipped packet, the 56-unit response contract, the issue, the operator-declared returned-response origin, and a receipt time after completion. Both private files remain outside Git.

BurnLens `0.16.0` then re-verifies that private pair through a new public-QA path that does not import the response-lock builder. The result publishes the evidence needed for audit—exact hashes and byte counts, 56-of-56 completion, one-of-two response state, packet binding, chronology, and explicit reveal withholding—without publishing label counts, confidence, sufficiency, reasons, experience text, response timestamps, notes, private filenames, or private paths.

![BurnLens first returned-response hash lock](../../samples/labels/review/phase-two/LABEL-REVIEW-RESPONSE-LOCK-QA-2026-001.png)

The operator states that the reveal remains unopened. Software explicitly does not claim it can verify that history, the reviewer, or scientific label fitness. One response is not adjudication. The next bounded checkpoint is to obtain and lock a second qualifying response under the same isolation boundary before any comparison or reveal.

Candidate source is `ec41129f9322022f28b8f788a2e08ae22145471b`; public artifacts are `9fbd97fcb66fd76172fff949580f469fc43b3f40`; run is `BL-2026-07-16-label-review-response-lock-qa-r001`. All 158 tests pass. Two fixed-epoch detached-source wheels are byte-identical at 292,068 bytes / SHA-256 `c6a0f320b393ea7aca3aebdc93da97f7ed34901d30df298c1986d1ee4b78ee28`, and an isolated install reports BurnLens `0.16.0` with 26 entry points.

PR #388 reviewed head `7a1345d187def41094ccb9d63d44958a3de809e7` merged to `836eef75495dbc671bd74a8ad4112852bbf50ac6`. The post-merge audit correctly withheld the tag after finding that the candidate manifest's stated creation time was later than both its own commit and the merge. Issue #389 corrects only that chronology and release synchronization; no private byte, public output, code path, or scientific state changes.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
