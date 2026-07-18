# Region-Candidate Pilot Decision

**Issue / branch:** #453 / `codex/p2o4-t17-region-pilot`

**Run:** `BL-2026-07-18-region-candidate-pilot-r006`

**Generator source / public artifacts:** `407981e1f98570bb8bd7695951d6cc5d67dab042` / `0e5306c6d94c54b47df40486a75e5bbd69bab62f`

## Decision

`PILOT_REGION_CANDIDATES_REVIEWABLE_KEEP_PROMOTION_CLOSED`.

BurnLens can deterministically turn the 24 exact owner-approved prototype center pixels into a small, inspectable set of intact region candidates without buffering, arbitrary tiling, or label promotion. The pilot selects one proposed burned and one proposed background component for each of Darlene 3, McKay, and Tepee. A core pixel must share the seed's frozen five-state class, quality and registration eligibility, exact categorical reference context, and fixed 0.05 dNBR bin. Selection targets one hectare only when ranking intact components; it never clips or expands a component. A one-native-pixel unknown ring surrounds each core, and overlap or grid-edge truncation fails closed.

The six candidates contain 136 core pixels and 246 unknown-ring pixels. Each candidate is published as a full native-grid EPSG:32610 GeoTIFF whose only data values are 0 outside, 1 candidate core, and 2 unknown ring. The evidence plate shows actual pre/post optical imagery, dNBR, official reference context, the core, and the ring. It does not create a label.

The next bounded checkpoint may build a separately versioned owner yes/no/uncertain surface for these six exact candidates. A future yes remains necessary but not sufficient: reproducibility, source, quality, terms, and event-level leakage gates still govern. No response may be inferred from the earlier 56-point review.

No region label, accepted dataset, split, baseline, model, accuracy, independent-ground-truth, inter-rater, field-validation, official, endorsed, operational, emergency-ready, or enterprise claim is created. Three events remain below the six-event advancement gate.
