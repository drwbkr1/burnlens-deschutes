# Replacement Six-Event Dataset Sufficiency Decision

**Issue / branch:** #554 / `codex/p2o4-t39-replacement-event`

**Run:** `BL-2026-07-25-replacement-six-event-dataset-sufficiency-r003`

**Software / source:** BurnLens 0.50.0 / `af37f80dd17febacfbb1cf2801665d74edb16475`

## Decision

`PASS_SIX_EVENT_DATASET_SUFFICIENCY_AUTHORIZE_DATASET_SPLIT_QA_BASELINE_CHECKPOINT`.

The exact candidate contains McKay, Tepee, Green Ridge, Grandview, Windigo,
and Ward Creek. Darlene is excluded.

All ten required non-count gates pass. The candidate contains 12 balanced
owner-approved prototype regions across six whole events.

The candidate retains 287 accepted core pixels and 531 excluded unknown-ring
pixels. It contains three events from each exact source regime.

Fifty-four of 90 prospective 2/2/2 assignments satisfy every frozen grouping
rule. Validation and test can each reserve never-tuned transfer evidence.

The independent readiness audit returns `pass`. It also returns
`training_authorized: false`.

## Next checkpoint

Open a separate milestone to create the accepted dataset. Lock one whole-event
split before patch extraction.

Run dataset QA against that exact dataset and split. Evaluate the strongest
justified non-model baselines before model readiness.

This decision creates no dataset, split, baseline, model, metric, or training
authorization.

## Limitations

These labels are disclosed owner-approved prototype regions. They are not
independent ground truth or field validation.

The balanced review roster does not estimate natural prevalence. The accepted
core contains only 287 native 20-meter pixels.

BurnLens remains experimental. It is not official wildfire information,
emergency guidance, endorsed, or operational.

Official sources govern.
