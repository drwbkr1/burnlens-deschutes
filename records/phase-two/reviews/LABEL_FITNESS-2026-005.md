# LABEL_FITNESS-2026-005 - Registration prerequisite passes; labels remain deferred

**Issue:** #347

**Decision:** `PASS_REGISTRATION_PREREQUISITE_DEFER_LABEL_PROPOSAL`

The 0.5-native-pixel content-registration prerequisite in `burn-scar-label-protocol-v0.1.0` now passes for all twelve fixed AOI windows under `local-content-registration-v0.1.0`. No spatial registration exclusion is required at the window level.

This does not implement or approve the five-state label schema. Burned, background-candidate, unknown, excluded, and review-needed remain design states only. A next checkpoint may construct a reviewable proposal, but it must preserve pixel-level SCL review/exclusions, mixed/boundary uncertainty, temporal ambiguity, source disagreement, and independent second-pass QA. It must not turn NIFC geometry, dNBR, SCL, VIIRS, MTBS absence, or visual appearance into truth alone.

No label array, companion state layer, audit sample, dataset, split, baseline, or model exists. Dataset work remains prohibited until a separate label-proposal and independent-QA gate passes.
