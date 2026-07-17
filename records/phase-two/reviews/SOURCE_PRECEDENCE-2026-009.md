# SOURCE_PRECEDENCE-2026-009 - Owner-Review Evidence Precedence

**Issue / parent:** #425 / #416

## Decision

Source classes have distinct roles and must be compared rather than collapsed into one truth layer. For future owner-confirmed prototype candidates, precedence is:

1. use boundaries, terms, and explicit no-go conditions;
2. exact item identity, archive notices, provenance, CRS/grid/nodata/QA, and temporal relation;
3. native-resolution Sentinel/Landsat optical evidence and quality states;
4. applicable BAER/RAVG/MTBS program evidence with provider and model limitations;
5. Landsat burned-area probability/classification as independent algorithmic reference;
6. NIFC perimeter and NLCD land-cover context;
7. coarse NASA 500 m burned-area context;
8. deterministic BurnLens proposal logic; and
9. explicit owner yes/no/uncertain response.

An owner `yes` is necessary but not sufficient for an owner-approved prototype label. Reproducibility, source, quality, and leakage gates must also pass. `No` and `uncertain` remain excluded. Neither a product class nor the owner response creates independent ground truth, field validation, inter-rater agreement, official status, or operational readiness.

The historical 6 burned / 0 background / 50 ignored reconciliation remains immutable evidence, but those exclusions are not inherited by the newly authorized owner-confirmed route. All original 56 units will be reopened in a later bounded review-surface checkpoint.
