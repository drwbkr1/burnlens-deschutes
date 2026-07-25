# REGISTRY-2026-085 - P2O5-T03 U02 split lock

**Recorded:** 2026-07-25

**Issue:** #562

| Unit | Run / source | Inputs | Outputs | Gates | Disposition | Next dependency |
|---|---|---|---|---|---|---|
| `P2O5-T03-U02-R001` | `BL-2026-07-25-p2o5-t03-u02-whole-event-split-r001`; source `c719bf7...` | contract `f6106691...`; candidate `4a9646af...`; metadata only | ranking 173,367 / `a513edff...`; split 12,312 / `a62e66f4...` | 90 enumerated; 54 valid; rank unique; exact replay; 12 focused tests; test open count zero | `pass-split-locked-test-sealed-training-false` | `P2O5-T03-U03` |

The exact split version is `burnlens-whole-event-split-v0.1.0`.

- Train: Green Ridge and Tepee.
- Validation: Grandview and McKay.
- Test: Ward Creek and Windigo.

Each role contains one event from each source regime and one preserved
never-tuned-transfer event. No event, scene, geography, time, source-regime,
candidate, or future patch may cross roles.

No pixel value was opened. No dataset, patch, normalization statistic,
baseline, model, metric result, training authorization, inference, deployment,
or external submission advances.
