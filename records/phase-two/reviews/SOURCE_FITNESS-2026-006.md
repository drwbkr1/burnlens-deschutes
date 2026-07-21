# SOURCE_FITNESS-2026-006 - Petes Lake planned optical pair

**Issue / unit:** #521 / `P2O4-T33-U03`

**Runs:** `BL-2026-07-21-petes-lake-source-fitness-preview-r001`; `BL-2026-07-21-petes-lake-source-fitness-preview-r002`; `BL-2026-07-21-petes-lake-source-fitness-r001`

**Decision:** `FAIL_EXACT_PETES_LAKE_OPTICAL_SOURCE_FITNESS_REMEDIATE_POST_SCENE`.

The exact registered Sentinel-2A pair remains byte-identical to U02 custody. Both packages have processing baseline 05.10, matching native EPSG:32610 grids, aligned B04/B8A/B12/SCL/CLD/SNW rasters at 20 m, aligned TCI at 10 m, and the same 34,103-pixel full-boundary mask. Pre/ignition/post chronology passes.

The pre scene is locally clear enough for this gate: 33,763 SCL-eligible land pixels / 99.0030%, with zero cloud- or snow-probability pixels above zero. The post scene is not: 26,627 SCL snow-or-ice pixels / 78.0782%; snow probability p50 60%, p95 100%, maximum 100%; only 7,454 SCL-eligible land pixels / 21.8573%.

Pair classification retains 7,439 eligible pixels / 21.8133%, three review-needed pixels, and 26,661 excluded pixels / 78.1779%. All eight deterministic registration windows are excluded by the established 90% usable-fraction gate. The measured consensus residual distribution is retained—p50 0.4607 pixel, p95 0.6199, maximum 0.6251 / 12.502 m—but cannot convert an excluded window into a passing one. The 7,439 valid continuous-dNBR pixels remain non-thresholded optical-change evidence only.

Preview r001 proved the PNG rendering but included an HTML companion that browser policy would not open. It remains ignored and immutable. Committed preview r002 narrowed the roster to JSON and PNG and reproduced the exact scientific metrics. Final r001 renders the same evidence and passes original-resolution author inspection. No HTML is tracked, and no browser-policy workaround was attempted.

The pair is unfit for downstream use. A same-event, same-source-regime replacement post scene may be researched and proposed only through current primary metadata and an exact contract revision before acquisition. No threshold, quality class, registration limit, event boundary, or desired candidate result may be tuned to rescue the planned scene.

No official reference, candidate, owner response, label, dataset, split, baseline, model, accuracy, field-validation, official, endorsed, operational, or emergency-ready claim is created.
