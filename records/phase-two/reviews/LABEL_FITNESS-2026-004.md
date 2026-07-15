# LABEL_FITNESS-2026-004 - Burn-scar protocol gate

**Issue:** #343

**Decision:** `ACCEPT_PROTOCOL_DESIGN_DEFER_LABEL_IMPLEMENTATION`

Protocol `burn-scar-label-protocol-v0.1.0` preserves burned, background-candidate, unknown, excluded, and review-needed states. Only burned/background-candidate may later map to binary 1/0 values; the other three states remain ignored until an explicit resolution permits otherwise.

The protocol prohibits automatic truth from dNBR or another spectral threshold, SCL, VIIRS points/non-detections, the later NIFC outline, MTBS severity classes, or visual appearance alone. It requires local content-registration measurement, boundary/mixed-pixel review, event/scene/geography/time grouping before tiling, independent second-pass QA, disagreement recording, and an audit sample across all five states.

No label array or companion state layer is created. Therefore label fitness is accepted only as an implementable design gate; actual labels, split independence, dataset QA, baselines, and model readiness remain unproved.
