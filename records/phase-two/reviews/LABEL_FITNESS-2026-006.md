# LABEL_FITNESS-2026-006 - Five-state proposal passes separate software QA

**Issue:** #353

**Decision:** `ACCEPT_REVIEWABLE_LABEL_PROPOSAL_DEFER_DATASET`

## Evidence reviewed

`LABEL-PROPOSAL-2026-001` implements `burn-scar-five-state-schema-v0.1.0` on the exact 600 by 450 native-20m grid. Its candidate binary target includes only background-candidate `0` and burned `1`; unknown, excluded, and review-needed are `255` ignore in every case.

The exact state inventory is:

| State | Pixels | Share |
|---|---:|---:|
| background-candidate | 161,238 | 59.7178% |
| burned | 18,543 | 6.8678% |
| unknown | 71,897 | 26.6285% |
| excluded | 870 | 0.3222% |
| review-needed | 17,452 | 6.4637% |

Candidate-target coverage is 179,781 pixels / 66.5856%; 90,219 pixels / 33.4144% remain explicitly ignored.

## QA finding

`LABEL-QA-2026-001` uses a separately invoked implementation that does not import the proposal classifier. It reopens the registered package, recomputes SCL pair quality and four spectral signals, re-rasterizes the NIFC context, and compares all 270,000 state and target pixels.

- state agreement: 100%; zero mismatches;
- target agreement: 100%; zero mismatches;
- audit: 120 samples; 20 from each state plus 20 burned-transition-boundary samples;
- audit disagreements: zero;
- proposal and QA original-resolution PNGs: reviewed and legible;
- semantic HTML: loaded in the browser with complete 1800 by 1250 evidence images, decision, traceability, warning, and null dataset/model/human-validation boundary visible.

## Narrow acceptance

The exact proposal is accepted as reviewable one-event evidence. This is not accepted ground truth and does not create a dataset. Both implementations share the same frozen conceptual contract and were authored/reviewed by the same Codex director. There is no independent human annotator, inter-rater study, field validation, leakage-resistant multi-event split, baseline, model, or performance result.

The next checkpoint must not tile this one event into train/validation/test partitions and call them independent. It should test cross-event label evidence, review burden, and leakage-resistant grouping before deciding whether a dataset is supportable or whether Phase Two should take a baseline-only/stop route.
