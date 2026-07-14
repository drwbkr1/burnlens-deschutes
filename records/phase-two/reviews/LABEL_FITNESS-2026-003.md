# LABEL_FITNESS-2026-003 - Alternate-Geometry Decision

**Decision:** `DEFER - MATERIAL GEOMETRY IMPROVEMENT IS STILL REFERENCE-ONLY`

The complete bounded NOAA-21 inventory contains a materially better day observation than the shipped scan-edge baseline. The selected `A2024179.2118` granule has 11 qualified AOI records, zero residual-bowtie exclusions, and a 31.01-degree median view zenith. Its exact companion places the AOI more than 1,000 columns from the nearest scan edge.

This resolves the pass-selection weakness but not segmentation truth. The thermal observation occurs 2.48 hours after the Sentinel scene, and the 375 m support cannot define genuine 10-20 m boundaries. `weak-reference-label-feasibility-v0.1.0` therefore preserves positive reference, negative candidate, unknown, excluded, and review-needed states and creates no label array.

No provider hotspot, buffered point, absence of detection, NIFC perimeter, or optical quality class may be coerced into segmentation truth. Activating the established burn-scar fallback or stopping the active-fire path is an owner-reserved target decision.

