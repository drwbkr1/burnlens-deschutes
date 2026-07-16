# PRECHECK-2026-015 - First Returned Response Lock Entry Gate

**Issue / branch / base:** #384 / `codex/p2o4-t08-first-reviewer-response-lock` / `6b13c4f5f128615f42b8897e9c6d8442446a86a2`

## Cycle-start evidence

BurnLens `0.15.0` passes the exact offline and live-browser reviewer workflow. One actual 56-unit response arrived with an operator-supplied SHA-256 and validated packet contract. The highest-leverage action is to preserve and bind those exact bytes before any reveal or content inspection, then publish only the minimum audit evidence needed to prove custody and completeness.

## Frozen inputs

- Packet: `LABEL-REVIEW-PACKET-2026-001`; run `BL-2026-07-16-label-review-packet-r001`; SHA-256 `77067063a769645af13886b6c87cc236a10e06199d091743908d63556e07637c`.
- Response schema: `burnlens-label-review-response-v0.1.0`.
- Application: `label-review-handoff-workbench-v0.1.0`.
- Label schema: `burn-scar-five-state-schema-v0.1.0`.
- AOI: `aoi-darlene3-model-v0.2.0`.
- Expected private response: 16,443 bytes; SHA-256 `485e80f2563f8b723c16daa8b5e5a1172dd88e8f2a28a7dd8608c933fa64eed9`.

## Allowed action

Preserve the exact response and receipt under ignored repository-local storage; independently validate their byte, packet, contract, binding, chronology, and origin-declaration fields; publish a content-withheld JSON/HTML/PNG receipt; and update repository status and traceability records.

## Prohibited action

Do not open or release the reveal, publish response contents or private paths, qualify the reviewer through software, adjudicate one response, accept labels, create a dataset or split, train a baseline or model, deploy, or make accuracy, field, official, endorsement, or operational claims. Do not use `burnlens-site`.

## Entry gates passed

- Issue #384 freezes the exact response binding, allowed files, non-goals, quality gates, and public-claim boundary.
- The source and preserved copy match the supplied byte count and SHA-256 digest.
- Private storage is ignored; no private response or receipt byte is tracked.
- The public verifier is separated from the private lock builder.
- The second-response and no-reveal gates remain binding.

Decision: `PASS_FIRST_RETURNED_RESPONSE_LOCK_ENTRY_GATE`.
