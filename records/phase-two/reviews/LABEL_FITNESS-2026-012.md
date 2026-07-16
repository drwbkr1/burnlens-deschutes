# LABEL_FITNESS-2026-012 - Dual-Lock Tooling Is Ready; Label Fitness Is Still Open

## Decision

`PASS_MIXED_VERSION_DUAL_LOCK_READINESS_ONE_RETURNED_ONE_FIXTURE_NO_REVEAL`.

BurnLens can now validate the exact legacy first response lock alongside a current-version second-slot receipt without publishing response content. The current evidence run uses the real first private pair and one explicitly non-human software fixture.

## What this establishes

- Both exact 56-unit response/receipt pairs pass packet, contract, hash, chronology, and receipt-binding checks.
- Response hashes, opaque slots, receipt hashes, receipt IDs, receipt runs, and task issues are distinct.
- The first v0.2.0 / BurnLens 0.15.0 receipt remains historically exact.
- Future receipts default to v0.3.0 / BurnLens 0.17.0.
- Public JSON/HTML/PNG excludes response distributions, reviewer text, response timestamps, private filenames, and private paths.

## What remains absent

The software fixture is not a second independent human response and cannot authorize reveal. Software does not verify reviewer identity, expertise, independence, scientific fitness, or file-access history. Inter-rater agreement, adjudication, accepted truth, accuracy, and field validity remain unproved.

Unknown, excluded, and review-needed remain ignored. No accepted label set, dataset, split, baseline, or model is authorized. Parent issue #393 remains the next scientific gate.
