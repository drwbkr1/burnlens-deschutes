# Windigo Region Proposal Decision

## Decision

`PROPOSE_EXACT_WINDIGO_TWO_CLASS_REGIONS_KEEP_OWNER_REVIEW_AND_PROMOTION_CLOSED`.

P2O4-T35-U04 run `BL-2026-07-23-windigo-region-proposal-r001` deterministically proposes exactly two Windigo review candidates from source commit `fc8c81ad7e0fff081299e6f72a68c957081f7867`.

`WDP-001` is a 25-pixel burned core with a 51-pixel unknown ring. Every core pixel passes the frozen optical burn screen, BAER SBS class 2-4 primary evidence, and MTBS dNBR6 class 2-4 corroboration.

`WDP-002` is a 25-pixel background core with a 51-pixel unknown ring. Every core pixel passes the frozen optical stability screen and lies outside a 60 m buffer around conservative BAER, MTBS, and RAVG raster-domain footprints.

The background route is affirmative evidence for this bounded proposal. It does not prove that the land was never burned. RAVG remains context and conservative exclusion only. BAER, MTBS, and RAVG low or zero classes remain disallowed as affirmative background evidence.

The [public proposal](../../../samples/labels/pilot/windigo/phase-two/WINDIGO-REGION-PROPOSAL-2026-001.html) exposes the actual pre/post optical evidence, dNBR or stability evidence, source roles, unknown rings, candidate bindings, limitations, and zero-promotion state. Production and replay JSON, HTML, PNG, and both rasters match byte for byte.

U04 creates two proposals, not labels. Owner decisions, event-six acceptance, dataset fitness, split, baseline, model, metric, accuracy, independent ground truth, BurnLens field validation, official status, endorsement, emergency suitability, and operational readiness remain absent.

Only the exact two-card owner review may open next. It must accept one yes/no/uncertain answer per candidate with no prefills, bulk approval, or missing-answer inference. Both owner yes decisions are necessary but insufficient; every non-owner gate must be recomputed before any promotion.

The July 27 cutoff and technical-case-study-only fallback remain active.
