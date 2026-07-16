# LABEL_FITNESS-2026-008 - Review Instrument Ready; Dataset Deferred

## Decision

`ACCEPT_PROPOSAL_BLINDED_REVIEW_READINESS_DEFER_DATASET`.

BurnLens can now present exact Darlene 3, Tepee, and McKay source pixels for a proposal-blinded first pass. The packet selects 56 deterministic units: four from every proposal state present within each event. All five states are present in Darlene 3 and Tepee; McKay contains background-candidate, burned, unknown, and review-needed but no excluded pixels. The missing McKay/excluded stratum is explicit.

The generator reopens the registered optical and MTBS packages, recomputes the three proposal state/target arrays, and fails unless they exactly match the committed rasters. The first-pass pages include pre/post Sentinel-2 true color, continuous dNBR, and NIFC or MTBS context. The sample-specific proposal state and target are confined to a separate reveal page.

`LABEL-REVIEW-PACKET-QA-2026-001` independently verifies the packet JSON binding and 14 referenced packet outputs, 56 unique pixel bindings, 15 event/state coverage records, eight blind pages, blank response/adjudication templates, blind/reveal separation, and the invariant that only background-candidate and burned may carry binary target values. `MANIFEST-2026-015` separately inventories all 18 packet/QA files.

## What remains absent

Completed independent response files: 0.

Completed adjudications: 0.

Codex cannot count as an independent reviewer because it authored the proposal and review tooling. Software QA is not human review. No accuracy, inter-rater, field-validation, accepted-label, dataset, split, baseline, model, application, official, endorsed, or operational claim is authorized.

## Predeclared next gate

Before adjudication:

1. two independent reviewers complete all 56 units;
2. each uses an opaque reviewer ID and attests independence;
3. neither opens the reveal before locking and hashing the first-pass response;
4. response files pass the fail-closed schema verifier.

Before dataset candidacy:

1. all reviewer disagreements are adjudicated or the affected unit remains ignored;
2. insufficient, uncertain, unusable, source-conflicted, or unresolved units remain unknown, excluded, or review-needed;
3. systematic event/class contradictions trigger proposal remediation and a new packet;
4. the bounded packet is not used as a statistical accuracy estimate.

Unknown, excluded, and review-needed remain target value 255. No candidate pixel may enter an accepted dataset before the independent review/adjudication evidence passes.
