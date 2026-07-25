# DATASET_FITNESS-2026-003 - Replacement six-event sufficiency

**Issue:** #554

**Run:** `BL-2026-07-25-replacement-six-event-dataset-sufficiency-r003`

**Generator source:** `af37f80dd17febacfbb1cf2801665d74edb16475`

## Decision

`PASS_SIX_EVENT_DATASET_SUFFICIENCY_AUTHORIZE_DATASET_SPLIT_QA_BASELINE_CHECKPOINT`.

All ten required gate families pass: source/terms, provenance/custody,
schema/quality, coverage/balance, uncertainty/exclusions, leakage/split
fitness, reproducibility, evaluation design, human review, and
claims/privacy.

The evaluator reconstructs 12 owner-approved prototype regions across McKay,
Tepee, Green Ridge, Grandview, Windigo, and Ward Creek. Darlene is excluded.

The cores contain 287 native 20-meter pixels, or 11.48 hectares. All 531
unknown-ring pixels remain excluded. No event contributes more than 20.5575
percent of accepted core pixels.

Three events use current MTBS evidence. Three use current BAER/MTBS/RAVG
evidence. Fifty-four of 90 prospective whole-event 2/2/2 assignments preserve
both exact source regimes and reserve never-tuned transfer events for
validation and test.

The independent audit reproduces the tracked decision byte for byte and
returns `training_authorized: false`.

This result authorizes only a separate checkpoint to create an accepted
dataset, lock one whole-event split before patch extraction, run dataset QA,
and evaluate the strongest justified non-model baselines.

It does not create a dataset, split, baseline, model, metric, training run, or
independent-ground-truth claim.
