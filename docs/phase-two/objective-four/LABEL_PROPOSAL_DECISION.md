# Five-State Burn-Scar Label-Proposal Decision

## Checkpoint scope

Issue #353 implements the already-versioned five-state label protocol after the exact optical pair and pair-local registration prerequisites passed. It asks one bounded question: can BurnLens create a reviewable one-event proposal that preserves uncertainty and reproduces exactly through a separate software path?

It does not create an accepted dataset or authorize model work.

## Proposal method

The proposal uses the exact native 600 by 450 Sentinel-2 20 m grid without source reprojection or resampling. It recomputes dNBR, NDVI loss, SWIR gain, and NIR loss from the two registered L2A products.

- Burned candidates require the one-pixel-eroded NIFC reference context, dNBR at least 0.10, at least two of three supporting change signals, and support from at least 5 of 9 neighboring pixels.
- Background candidates require location outside the one-pixel-expanded reference, affirmative stability across all four signals, and at least 7 of 9 stable neighbors.
- Review-needed retains SCL 7, the incident-reference boundary, candidate-burn transition boundary, and spectral/reference disagreement.
- Unknown retains valid but inconclusive evidence.
- Excluded retains unusable pair quality or invalid spectral arithmetic.

Only burned and background-candidate enter the candidate binary target. The other three states are `255` ignore. The thresholds are conservative screens frozen for this exact pair, not universal burn/severity rules or field calibration.

## Result

`LABEL-PROPOSAL-2026-001` contains all five required states. It proposes 161,238 background pixels and 18,543 burned pixels while keeping 90,219 pixels / 33.4144% ignored as unknown, excluded, or review-needed.

The visual result is coherent around the later NIFC context while preserving substantial uncertainty and dispersed non-fire change outside it. NIFC geometry, SCL, VIIRS, MTBS, dNBR, and visual appearance never act as sufficient truth alone.

## Separate QA

`LABEL-QA-2026-001` is produced by a separate module and CLI that do not import proposal-classification helpers. The verifier reopens the registered source package, independently computes quality and spectral evidence, re-rasterizes the context, checks both GeoTIFF contracts and trace tags, and compares every pixel.

All 270,000 state pixels and all 270,000 target pixels agree. The deterministic audit contains 20 samples from each state plus 20 candidate-burn transition-boundary samples; all 120 agree. Both original-resolution PNGs and both semantic HTML pages were reviewed, and the evidence images, decisions, warnings, traceability, and null dataset/model/human-validation state render correctly.

This is implementation-path independence, not independent human annotation. The same Codex director authored both paths and both implement one shared conceptual contract.

## Decision

Decision code: `ACCEPT_REVIEWABLE_LABEL_PROPOSAL_DEFER_DATASET`.

Accept the exact five-state proposal as reviewable, reproducible, one-event evidence. Do not call it ground truth and do not create a versioned dataset or split from it yet. The next checkpoint should test whether cross-event evidence and a genuinely leakage-resistant grouping/review plan can support a dataset, or whether Phase Two should defer modeling and take a baseline-only or stop decision.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

## Successor status

P2O4-T02 / issue #357 has now completed the metadata-feasibility step named above. `CROSS-EVENT-FITNESS-2026-001` selects exact Tepee and McKay future acquisitions and freezes whole event/scene/geography/time groups without creating a dataset or split. Its PR/merge/tag shipment gates are tracked separately; exact cross-event source pixels and label fitness remain the next evidence boundary.
