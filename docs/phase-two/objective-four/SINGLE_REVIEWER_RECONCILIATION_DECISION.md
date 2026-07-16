# Single-Reviewer Reconciliation Decision

## Decision

`REMEDIATE_LABEL_EVIDENCE_DEFER_DATASET_SINGLE_REVIEWER`.

The owner-authorized route reconciles one exact blinded response against the exact proposal without pretending a second reviewer, consensus, or adjudication exists. Six burned units survive the conservative rule as candidate evidence. Zero background units survive. Fifty units remain ignored, including every Tepee unit.

This is useful proposal-diagnostic evidence, but it is not balanced cross-event label evidence and cannot support a dataset, split, baseline, model, validation, or accuracy claim. Issue #411 owns reference-evidence remediation.

## Deterministic rule

A unit is an accepted candidate only when:

- the proposal is a binary `burned` or `background-candidate` state;
- the reviewer independently chose the matching binary label;
- evidence sufficiency is `sufficient`;
- no source-conflict, cloud/smoke/shadow, registration, boundary, low-severity, non-fire-change, or unclassified `other` reason is present; and
- the label and directional reason codes are semantically consistent.

Every other unit remains ignored. Accepted-candidate means bounded supporting evidence only; it does not mean ground truth.

## Result

| Event | Accepted candidate | Ignored |
|---|---:|---:|
| Darlene 3 (Oregon, 2024) | 3 | 17 |
| McKay (Nebraska, 2017) | 3 | 13 |
| Tepee (Nebraska, 2018) | 0 | 20 |
| **Total** | **6** | **50** |

Accepted-candidate labels are 6 burned and 0 background. The absence of background and Tepee candidates is an automatic remediation trigger.

## Sequence transparency

During issue-#403 preflight, a repository search displayed exact reveal HTML before the explicit authorization-verifier command was invoked. Exact authorization and response/receipt/packet/reveal bindings passed immediately afterward at `2026-07-16T22:40:40Z`, before private response content was opened or any unit comparison was performed.

This is recorded as a disclosed sequence exception, not a passing pre-access gate. It did not alter the already-locked response, reviewer blindness, receipt, packet, reveal, authorization, or proposal bytes.

## Traceability

- Issue: #403
- Pull request: #412
- Next remediation issue: #411
- Base: `1c5cadcb6dca9664979ad87a3503f06aeea5fd0f`
- Source: `fda69a60b0a5e350bfe10e7388571d7c1c103735`
- Public artifacts: `57f116aabb7c15e5d0f9d88e8088d2e50c46eb7e`
- Reviewed candidate head: `67216dc9952427a9c511eb871c12a87f94171bea`
- BurnLens: `0.20.0`
- Private report version: `label-review-single-reviewer-reconciliation-v0.1.0`
- Private run: `BL-2026-07-16-single-reviewer-reconciliation-r001`
- Private report: 72,628 bytes; SHA-256 `a04dd629551a2163e5e7a31f61c3aa95d4fdba136563f3a42940a2e9d1e9249d`; ignored and untracked
- Public QA version: `label-review-single-reviewer-reconciliation-qa-v0.1.0`
- Public QA run: `BL-2026-07-16-single-reviewer-reconciliation-qa-r001`
- AOI: `aoi-darlene3-model-v0.2.0`
- Target: `target-burn-scar-v0.2.0`
- Label schema: `burn-scar-five-state-schema-v0.1.0`
- Dataset / split / baseline / model: none

## Current primary-source basis

- [MTBS Mapping Methods](https://www.mtbs.gov/mapping-methods), accessed 2026-07-16: supports pre/post scene review, co-registration inspection, cloud/shadow masking, analyst interpretation, and explicit uncertainty.
- [CEOS LPV Burned Area Validation Protocol](https://lpvs.gsfc.nasa.gov/PDF/BurnedAreaValidationProtocol.pdf), accessed 2026-07-16: separates burned, unburned, and unmapped areas and requires independent, representative reference evidence for accuracy claims.
- [CEOS LPV Fire Disturbance 2025](https://lpvs.gsfc.nasa.gov/PDF/LPV_Plenary_2025/LPV_Fire_202505_v3.pdf), accessed 2026-07-16: records continuing protocol/sample-size questions and the need for QA alongside limited independent validation samples.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
