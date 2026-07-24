# PRECHECK-2026-072 - Six-event dataset sufficiency

**Issue / branch:** #552 / `codex/p2o5-t02-six-event-sufficiency`

**Exact base:** `1c4df18d273bfa908737dca6831121db16af1d89`

## Entry

- Canonical checkout: `C:\Projects\Active\burnlens-deschutes`.
- Active labels: `owner-approved-prototype-region-labels-v0.4.0`.
- Six complete whole-event groups contain one owner-approved burned region, one owner-approved affirmative-background region, and excluded unknown rings.
- Dataset, split, baseline, and model versions are null.
- The verified August 6 ZIP is preserved as an interim contingency technical case study.

## Authorized question

Decide whether the exact six-event prototype evidence is sufficient to open a separate dataset-and-split milestone. Do not create a dataset, split, baseline, model, metric, inference output, deployment, or external submission.

## Required gates

Source/terms, provenance/custody, raster schema/quality, class and uncertainty coverage, whole-event split fitness, source-program and regime replication, never-tuned transfer reservation, event dominance, overlap/leakage control, reproducibility, owner-review custody, evaluation design, privacy, and claims must all pass.

Count thresholds never authorize training. A passing readiness audit must still set `training_authorized` to false.

