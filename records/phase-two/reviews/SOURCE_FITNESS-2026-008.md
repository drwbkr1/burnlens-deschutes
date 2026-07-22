# SOURCE_FITNESS-2026-008 - Petes Lake replacement optical pair

**Issue / unit:** #521 / `P2O4-T33-U03_REPLACEMENT_SOURCE_FITNESS_R002`

**Runs:** `BL-2026-07-21-petes-lake-replacement-source-fitness-preview-r002`; `BL-2026-07-21-petes-lake-replacement-source-fitness-r002`

**Decision:** `PASS_EXACT_PETES_LAKE_REPLACEMENT_OPTICAL_SOURCE_FITNESS_WITH_SPATIAL_EXCLUSIONS`.

The source commit is `d42022b5bfd1eb58f487666745e1d8f1c33db45c`. The evaluator freshly re-verifies the exact 1,185,284,273-byte original pre archive and the separately registered 1,195,226,823-byte replacement post archive against the 22,246-byte replacement custody report and semantic hash. It also hard-binds the 56,285-byte failed r001 report and 10,127-byte deterministic selection report, so remediation does not erase or reinterpret the planned-pair failure.

Both delivered products use processing baseline 05.10, EPSG:32610, the exact 20 m source transform `[20, 0, 499980, 0, -20, 4900020]`, the exact 349 x 259 crop transform `[20, 0, 584560, 0, -20, 4871520]`, BOA quantification 10,000 with -1,000 offsets for B04/B8A/B12, nodata DN 0, and saturated DN 65,535. TCI remains 10 m preview only. B04/B8A/B12/SCL/CLD/SNW remain aligned native 20 m evidence without reprojection, resampling, or upsampling.

The 34,103-pixel full boundary contains 33,365 eligible pair pixels / 97.8360%, 134 review-needed / 0.3929%, and 604 excluded / 1.7711%. Replacement-post SCL contains 13,216 vegetation, 20,399 bare-soil, and 488 water pixels; every cloud, shadow, cirrus, snow, nodata, and saturation class is zero. Native CLD and SNW values are zero throughout the boundary, summarized without inventing a threshold.

Five of eight registration windows pass, three remain review-needed spatial exclusions, and none is excluded or fail-registration. The residual distribution is p50 0.1995 pixel, p95 0.3732, maximum 0.3785 pixel / 7.57 m. Thirty-three thousand three hundred sixty-five continuous-dNBR pixels are retained without severity or label semantics.

The 1,800 x 1,240 preview and final renders were each inspected at original resolution. Both clearly show aligned pre/post boundary imagery, no visible cloud, smoke or haze, snow, clipping, or misleading artifact, and a full valid change footprint with invalid/excluded pixels exposed. The final records an AI-assisted author self-audit only.

The result accepts the optical source with spatial exclusions and authorizes U04 reference inspection only. It does not accept any official reference pixel, candidate, owner response, label, dataset, split, baseline, model, accuracy, field-validation, official, endorsed, operational, or emergency-ready claim.
