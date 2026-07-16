# Isolated Offline Label-Review Handoff Decision

## Decision

`ACCEPT_ISOLATED_OFFLINE_REVIEWER_HANDOFF_DEFER_DATASET`.

Issue #379 addresses the highest-leverage weakness observed after rerunning shipped BurnLens `0.13.0`: the packet was scientifically traceable, but an independent reviewer still had to hand-edit a 56-entry JSON file in the same repository directory as proposal-bearing material.

BurnLens `0.14.0` builds a deterministic offline archive from the exact shipped packet. The archive contains only the handoff record, one accessible-by-construction HTML form, safe reviewer instructions, the existing blank response template, and the eight proposal-blinded pages. The reveal, proposal-bearing packet JSON, adjudication material, QA output, provider bytes, secrets, network dependencies, links, and path traversal are excluded.

The workbench supports labelled native controls, decision guidance, error and progress feedback, local draft save/load, review and confirmation, and completed response export under `burnlens-label-review-response-v0.1.0`. It does not transmit data or persist responses in browser storage. A separate response-lock command validates returned bytes, pins the exact packet, records a SHA-256 receipt, and refuses overwrite.

## Evidence boundary

This checkpoint proves an isolated, deterministic software handoff and a fail-closed response-return path. It does not prove:

- that any independent human opened or completed the handoff;
- reviewer identity, expertise, independence, or scientific agreement;
- browser-specific save/load/download behavior in the unavailable interactive runtime;
- label fitness, adjudication, accuracy, field validation, or ground truth;
- a dataset, split, baseline, model, deployment, official status, endorsement, or operational readiness.

The repository test suite includes a synthetic complete-response roundtrip. That fixture proves schema and lock behavior only and remains explicitly separate from human evidence.

## Fresh standards basis

The interface and integrity design was checked against current primary sources on 2026-07-16:

- [WHATWG HTML Living Standard - forms](https://html.spec.whatwg.org/multipage/forms.html) for native form, label, validation, and download semantics;
- [W3C Web Content Accessibility Guidelines 2.2](https://www.w3.org/TR/WCAG22/) for labels or instructions, error identification and suggestions, status communication, and review/correction;
- [W3C File API](https://www.w3.org/TR/FileAPI/) for local `Blob` and object-URL downloads;
- [NIST FIPS 180-4](https://csrc.nist.gov/pubs/fips/180-4/upd1/final) for SHA-256 integrity semantics.

These sources informed the implementation. BurnLens does not claim formal accessibility certification or identity assurance.

## Traceability

- Issue: #379
- Branch: `codex/p2o4-t06-reviewer-handoff`
- Pull request: #380
- Reviewed head: `50dc6cc81de58b57ee04c2f6d6c3a1499af55a70`
- Merge: `49c2d2cff03612b9fb4e0644c4c1ee8852a312a4`
- Base: `12dc92e0c78433a8f306ab221bdfa890ca55331a`
- Software: BurnLens `0.14.0`
- Generator/verifier/lock source: `75102d79e6e184a1ecac941900fd74938cdaa972`
- Candidate artifacts: `0400b894bcbf3938eb9b4666162512dd4263e45f`
- Handoff run: `BL-2026-07-16-label-review-handoff-r001`
- QA run: `BL-2026-07-16-label-review-handoff-qa-r001`
- Application version: `label-review-handoff-workbench-v0.1.0`; local/offline, not deployed
- Packet: `LABEL-REVIEW-PACKET-2026-001`; SHA-256 `77067063a769645af13886b6c87cc236a10e06199d091743908d63556e07637c`
- Response schema: `burnlens-label-review-response-v0.1.0`
- Label schema: `burn-scar-five-state-schema-v0.1.0`
- AOI: `aoi-darlene3-model-v0.2.0`
- Dataset / split / baseline / model: none
- Exact inventory: `MANIFEST-2026-016`
- Verified tag: `v0.14.0-offline-reviewer-handoff`; object `b4f290fdcc8dad859bdecc7eea54866d0e1b727a`

## Next gate

Deliver the isolated archive to a qualifying independent reviewer. Validate and lock the returned response before reveal. Do not count software fixtures, Codex, or proposal authors as independent evidence, and do not create a dataset partition until the review/adjudication gate passes.

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
