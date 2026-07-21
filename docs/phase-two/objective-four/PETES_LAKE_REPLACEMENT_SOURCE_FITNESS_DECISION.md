# Petes Lake Replacement Source Fitness Decision

## Decision

`PASS_EXACT_PETES_LAKE_REPLACEMENT_OPTICAL_SOURCE_FITNESS_WITH_SPATIAL_EXCLUSIONS`.

P2O4-T33-U03 replacement run `BL-2026-07-21-petes-lake-replacement-source-fitness-r002` freshly reopens the immutable original pre archive and the exact October 19 replacement post archive. It re-verifies their separate custody bindings, hashes, SAFE structure, processing baseline 05.10, native EPSG:32610 grids, transforms, shapes, data types, nodata and saturation contracts, full-boundary masks, and single-link custody. The original failed r001 report and deterministic replacement-selection report remain exact immutable inputs.

The catalogue product acquisition time (`2023-10-19T19:04:11.024000Z`) and delivered tile sensing time (`2023-10-19T19:12:24.432471Z`) are preserved as distinct metadata fields. They agree on the UTC date and are not rewritten into one another. The pre scene is 35 days before the 2023-08-25 ignition date and the replacement post scene is 55 days after it, so chronological order passes.

The full frozen MTBS boundary contains 34,103 native 20 m pixel centers. The replacement post contains zero SCL cloud, cloud-shadow, cirrus, snow-or-ice, nodata, or saturated pixels and zero nonzero native cloud/snow-probability pixels. Pair classification retains 33,365 eligible pixels / 97.8360%, 134 review-needed pixels / 0.3929%, and 604 excluded pixels / 1.7711%. The exclusions are preserved and cannot become labels.

Five of eight deterministic registration windows pass and three require spatial exclusion; none fails registration. Consensus residuals are p50 0.1995 pixel, p95 0.3732, and maximum 0.3785 pixel / 7.57 m. The established registration, usable-fraction, SCL, and uncertainty gates are inherited unchanged from r001. No threshold or gate was tuned to rescue the replacement scene.

Continuous dNBR covers the 33,365 valid paired pixels and is retained only as non-thresholded optical-change context. Its distribution, the strong post-fire browning, and the MTBS boundary do not assign severity, burned, background, or unknown labels.

The exact 1,800 x 1,240 PNG passes original-resolution inspection. The pre and replacement-post boundary panels are clear and coherently aligned, with no visible cloud, smoke or haze, snow, clipping, or misleading display artifact. Dark invalid or excluded dNBR pixels remain visible context. This is an AI-assisted author self-audit, not independent review or field validation.

U03 disposition is `pass-with-spatial-exclusions`. U04 is authorized to inspect the exact official reference delivery and its notices; no reference pixel is accepted by this decision. Burned and affirmative-background candidates remain blocked until their separate U04-U07 gates pass. No candidate, owner response, prototype label, sixth complete event, dataset, split, baseline, model, metric, field-validation, official, endorsed, emergency-ready, or operational claim advances.

Primary public evidence: [`PETES-LAKE-REPLACEMENT-SOURCE-FITNESS-2026-001.json`](../../../samples/cross-event/phase-two/petes-lake/PETES-LAKE-REPLACEMENT-SOURCE-FITNESS-2026-001.json) and [`PETES-LAKE-REPLACEMENT-SOURCE-FITNESS-2026-001.png`](../../../samples/cross-event/phase-two/petes-lake/PETES-LAKE-REPLACEMENT-SOURCE-FITNESS-2026-001.png).
