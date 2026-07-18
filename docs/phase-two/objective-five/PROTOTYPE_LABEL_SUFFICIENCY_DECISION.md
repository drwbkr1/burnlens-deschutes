# Prototype Label Sufficiency Decision

**Issue / PR:** #443 / #445

**Run:** `BL-2026-07-18-prototype-label-sufficiency-r002`

**Generator source:** `89e69172163c97ea8f4c86e72867578065626f22`

## Decision

`REMEDIATE_LABEL_COVERAGE_BEFORE_DATASET_SPLIT_BASELINE_MODEL`.

The 24 owner-approved prototype labels retain exact lineage and spatially distinct centers, but they are reviewed center pixels rather than contiguous segmentation masks. They cover 0.012662% of 189,541 candidate-domain pixels. Their balanced 12/12 class design is useful for audit but does not preserve event prevalence, which ranges from 10.3142% to 99.4005% burned within the candidate domain.

Only three immutable event groups exist. Every nonempty train/validation/test assignment therefore gives one event to each role, with no replicated event evidence. Each event also has a distinct current-reference regime, confounding event transfer with evidence regime. Selection was stratified from BurnLens proposals, and the owner saw optical/current-reference evidence, so these points cannot serve as independent ground truth or evaluation.

BurnLens must create reviewed contiguous burned/background/unknown regions, add event and source-regime diversity, preserve natural prevalence separately from balanced audit samples, and reserve independent evaluation evidence before creating a dataset, split, baseline, or model.
