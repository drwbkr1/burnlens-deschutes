# LABEL_FITNESS-2026-007 - Cross-Event Proposal Reproducible; Dataset Deferred

## Decision

`ACCEPT_CROSS_EVENT_LABEL_TRANSFER_PROPOSAL_DEFER_DATASET`.

Final proposal run `BL-2026-07-16-cross-event-label-transfer-r003` preserves all five states across Tepee and McKay and produces 9,760 candidate pixels while leaving 54,170 pixels ignored. Separate run `BL-2026-07-16-cross-event-label-transfer-qa-r003` independently reproduces all 63,930 state and target pixels with zero mismatch and 45 agreeing deterministic samples.

This passes implementation reproducibility and cross-event uncertainty preservation. It does not pass independent human label review, field validity, universal threshold calibration, class-balance fitness, dataset QA, leakage-resistant split acceptance, baseline comparison, or model readiness. McKay's inherited fixed near-zero stability rule yields zero primary background pixels; its 55 background candidates come from the explicit capped event-relative fallback. That limitation must remain visible in any later sampling or review.

No candidate pixel may be promoted into an accepted dataset until an independent review/adjudication checkpoint passes. Unknown, excluded, and review-needed remain ignored value 255 and may never be silently coerced to background.
