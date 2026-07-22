# Petes Lake Source Fitness Decision

## Decision

`FAIL_EXACT_PETES_LAKE_OPTICAL_SOURCE_FITNESS_REMEDIATE_POST_SCENE`.

P2O4-T33-U03 run `BL-2026-07-21-petes-lake-source-fitness-r001` freshly reopens the exact U02 Sentinel-2A archives and verifies their registered identities, SAFE structure, processing baseline 05.10, native EPSG:32610 grids, transforms, shapes, data types, boundary masks, and single-link custody. The 2023-07-21 pre scene is 35 days before ignition and the 2023-10-29 post scene is 65 days after ignition, so chronological order passes.

Local pixel fitness does not pass. The full MTBS boundary contains 34,103 native 20 m pixel centers. The pre scene is 99.0030% SCL-eligible land, but the post scene contains 26,627 SCL snow-or-ice pixels / 78.0782% of the boundary. Native Sen2Cor post snow probability has p50 60%, p95 100%, and maximum 100%. These probability values remain quality context without a classification threshold; SCL and the complete quality contract govern exclusions.

Only 7,439 pixels / 21.8133% remain eligible for paired comparison, while 26,661 / 78.1779% are excluded. All eight deterministic registration windows fall below the established 90% usable-fraction gate. Zero windows pass; none fails for a measured translation residual. The shared registration summary therefore accepts only spatial exclusions, but the event-level source-fitness invariant rejects a pair with zero passing windows. Continuous dNBR is retained for the 7,439 valid pixels and is never interpreted as a severity class or label.

The exact 1,800 x 1,240 final PNG passes the actual-render audit: it visibly shows the clear pre scene, snow-dominated post scene, sparse valid dNBR footprint, zero-of-eight result, warning, trace, and no-label boundary without clipping. Direct local-file HTML navigation was blocked by browser security policy and was not bypassed, so HTML is excluded from the tracked U03 output roster. This is an AI-assisted author self-audit, not independent review or field validation.

U03 disposition is `remediate`. U04 is not authorized. Before any replacement archive request, BurnLens must perform a current metadata-only search for a same-event, same-source-regime post scene; record exact identity, availability, terms, timing, catalogue quality, acquisition cost, and expected local-fitness value; and revise the optical contract without weakening any checksum, custody, SCL, registration, render, or source-precedence gate. The current archives and r001 evidence remain immutable.

No official reference pixel, candidate, owner decision, prototype label, sixth accepted event, dataset, split, baseline, model, metric, field-validation, official, endorsed, emergency-ready, or operational claim advances.

Primary public evidence: [`PETES-LAKE-SOURCE-FITNESS-2026-001.json`](../../../samples/cross-event/phase-two/petes-lake/PETES-LAKE-SOURCE-FITNESS-2026-001.json) and [`PETES-LAKE-SOURCE-FITNESS-2026-001.png`](../../../samples/cross-event/phase-two/petes-lake/PETES-LAKE-SOURCE-FITNESS-2026-001.png).
