# Owner-Authorized Single-Reviewer Path Decision

## Decision

`ACCEPT_SINGLE_REVIEWER_PATH_WITH_EXPLICIT_REDUCED_VALIDATION`.

On 2026-07-16, the repository owner explicitly waived the planned second-human-response requirement. Issue #393 is closed as superseded, not satisfied. BurnLens still has exactly one returned independent response and must never represent the waiver as a second review, inter-rater validation, reviewer consensus, or adjudication.

The Phase Two outcome is unchanged: BurnLens must still produce defensible, uncertainty-preserving label evidence strong enough to justify a dataset-candidacy, remediation, baseline-only, or stop decision. Only the planning hypothesis for reaching that outcome changes.

## Replacement route

Issue #403 controls the replacement checkpoint:

1. Reverify the exact first response, receipt, packet, and reveal bindings before content access.
2. Publish a bounded owner-waiver and reveal-readiness record.
3. Open the first response and proposal reveal only in an ignored, deterministic reconciliation run.
4. Compare the single independent response with the proposal and source evidence.
5. Accept no unit merely because the proposal and reviewer agree. Apply explicit evidence rules.
6. Retain disagreements, low-confidence units, insufficient-evidence units, unknown, excluded, review-needed, and otherwise unresolved units as ignored.
7. Publish aggregate, privacy-preserving reconciliation evidence and make a dataset-candidacy, remediation, baseline-only, or stop decision.

## Evidence consequence

The single-reviewer route is weaker than the planned two-reviewer route:

- no inter-rater agreement can be measured;
- no human consensus or adjudication can be claimed;
- one reviewer may introduce systematic interpretation bias;
- proposal/reviewer agreement is not independent ground truth because the proposal is one side of the comparison;
- accepted units require conservative source-evidence checks and explicit uncertainty retention;
- model and portfolio claims must carry this limitation permanently unless later independent validation is added.

This waiver does not authorize automatic label acceptance, a dataset, split, baseline, model, metric, deployment, or public performance claim.

## Reveal boundary

The reveal remains unopened at this decision. The owner waiver permits BurnLens to build and execute a separate reveal-readiness checkpoint; it does not make the historical no-reveal controls false retroactively. Receipt protocol v0.4.0 therefore requires a separate public owner-waiver/reveal-readiness checkpoint before content access.

## Traceability

- Owner decision date: 2026-07-16
- Superseded issue: #393
- Replacement issue: #403
- Atomic custody issue: #402
- First response: one exact ignored/private response and receipt; public binding remains `LABEL-REVIEW-RESPONSE-LOCK-QA-2026-001`
- Reveal state at this decision: operator-declared `withheld-unopened-after-lock`
- Dataset / split / baseline / model: none

## Boundaries

The project promise, target user, burn-scar binary segmentation task, six phase outcomes, official-source precedence, uncertainty states, source licensing controls, and experimental/non-operational use boundary remain unchanged. Work remains strictly inside `drwbkr1/burnlens-deschutes`; `burnlens-site` is not used.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
