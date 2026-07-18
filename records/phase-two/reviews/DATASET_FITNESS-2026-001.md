# DATASET_FITNESS-2026-001 - Prototype Label Sufficiency

**Issue:** #443

## Decision

`NOT_FIT_FOR_SEGMENTATION_DATASET_OR_INDEPENDENT_SPLIT`.

Twenty-four reviewed center pixels cover 0.012662% of 189,541 candidate pixels. They are spatially dispersed audit evidence, not contiguous masks or accepted patches. Three events provide no replicated event evidence across train, validation, and test, while three distinct reference regimes are confounded with those events. Balanced proposal-stratified selection cannot support prevalence, calibration, independent accuracy, or per-pixel segmentation claims.
