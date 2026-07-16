# First Returned Response Lock Decision

## Decision

`ACCEPT_FIRST_RETURNED_RESPONSE_HASH_LOCK_WITHHOLD_CONTENT_DEFER_DATASET`.

Issue #384 preserves and operator-locks one exact returned 56-unit response before any proposal reveal is opened or released. The ignored private copy is 16,443 bytes with SHA-256 `485e80f2563f8b723c16daa8b5e5a1172dd88e8f2a28a7dd8608c933fa64eed9`. Its ignored private receipt is 2,508 bytes with SHA-256 `67599f794a1310e9523cded095787c918ed47d88c439e240a0b41ea6e5eb9835`.

BurnLens `0.16.0` adds an independently transcribed public verifier. It checks the exact response and receipt byte bindings, the shipped packet identity, all 56 completed response units, the proposal-free contract, receipt chronology, and operator-declared evidence origin. The tracked JSON, HTML, and PNG publish only the bounded hash-lock state. They withhold label, evidence-sufficiency, confidence, and reason distributions; reviewer experience; response timestamps; free-text notes; private filenames; and private paths.

The proposal reveal remains operator-declared `withheld-unopened-after-lock`. Software cannot verify file-access history, reviewer identity, expertise, independence, or scientific fitness. One response is insufficient for adjudication. A second qualifying response must be preserved and locked before comparison, reveal, or adjudication.

## Evidence boundary

This checkpoint proves:

- one exact private response matches the operator-supplied byte count and SHA-256 digest;
- the response passes the shipped proposal-free 56-unit contract;
- one exact private receipt binds that response to the shipped packet, issue, origin declaration, and chronology;
- the public evidence excludes the review content categories declared private;
- the tracked repository contains no response bytes, reviewer notes, private filenames, private paths, provider bytes, credentials, or secrets.

It does not prove:

- reviewer identity, qualifications, independence, or scientific fitness;
- inter-rater agreement, adjudication readiness, accepted labels, ground truth, accuracy, or field validation;
- a dataset, split, baseline, model, deployment, official status, endorsement, or operational readiness;
- that the proposal reveal has remained unopened as a software-verifiable fact.

## Traceability

- Issue: #384
- Pull request: #388
- Reviewed head: `7a1345d187def41094ccb9d63d44958a3de809e7`
- Analytical merge: `836eef75495dbc671bd74a8ad4112852bbf50ac6`
- Release-record remediation: issue #389 / PR #390 / branch `codex/p2o4-t08-rem-release-sync`
- Branch: `codex/p2o4-t08-first-reviewer-response-lock`
- Base: `6b13c4f5f128615f42b8897e9c6d8442446a86a2`
- Software: BurnLens `0.16.0`
- Generator source: `ec41129f9322022f28b8f788a2e08ae22145471b`
- Candidate public artifacts: `9fbd97fcb66fd76172fff949580f469fc43b3f40`
- Public run: `BL-2026-07-16-label-review-response-lock-qa-r001`
- Public report: `LABEL-REVIEW-RESPONSE-LOCK-QA-2026-001`
- Private receipt run: `BL-2026-07-16-label-review-response-lock-r001`
- Packet: `LABEL-REVIEW-PACKET-2026-001`; SHA-256 `77067063a769645af13886b6c87cc236a10e06199d091743908d63556e07637c`
- Application: `label-review-handoff-workbench-v0.1.0`; local/offline, not deployed
- Label schema: `burn-scar-five-state-schema-v0.1.0`
- AOI: `aoi-darlene3-model-v0.2.0`
- Dataset / split / baseline / model: none
- Exact inventory: `MANIFEST-2026-018`
- Intended tag after issue #389 and all release gates pass: `v0.16.0-first-reviewer-response-lock`

## Next gate

Preserve reviewer independence by withholding the first response contents. Deliver the same isolated handoff to a second qualifying reviewer, preserve and lock the exact returned bytes before reveal, then compare responses and adjudicate disagreements or retain ignored states. Do not create a dataset partition before those gates pass.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
