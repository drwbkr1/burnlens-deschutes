# PRECHECK-2026-051 - Petes Lake replacement optical source fitness

**Unit / issue / branch:** `P2O4-T33-U03_REPLACEMENT_SOURCE_FITNESS_R002` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Source commit:** `d42022b5bfd1eb58f487666745e1d8f1c33db45c`

**Final run:** `BL-2026-07-21-petes-lake-replacement-source-fitness-r002`

**Checked:** 2026-07-21T21:49:10.2092124Z

## Decision

`PASS_EXACT_PETES_LAKE_REPLACEMENT_OPTICAL_SOURCE_FITNESS_WITH_SPATIAL_EXCLUSIONS`.

The production preview and final run began from the exact clean, pushed, remote-equal evaluator commit. Fresh source-fitness verification rehashed and reopened the original pre archive and replacement post archive, their immutable registrations, the replacement custody report, failed r001 evidence, deterministic selection report, and frozen additional-event plan. No provider request, credential use, custody mutation, or overwrite occurred.

SAFE metadata, exact product and tile identities, processing baseline 05.10, EPSG:32610 CRS, native 10 m TCI and 20 m B04/B8A/B12/SCL/CLD/SNW members, transforms, shapes, data types, reflectance offsets, nodata and saturation contracts, and full-boundary masks pass. Catalogue product acquisition and delivered tile sensing timestamps are retained separately. Pre/ignition/post chronology passes at 35 days before and 55 days after ignition.

Local quality passes with explicit exclusions: 33,365 of 34,103 boundary pixels are pair-eligible / 97.8360%; 134 are review-needed and 604 are excluded. Replacement-post SCL cloud, cloud shadow, cirrus, snow/ice, nodata, and saturation are all zero, as are every native CLD/SNW probability value inside the boundary.

Five registration windows pass, three remain review-needed, and zero are excluded or fail-registration. The p95 residual is 0.3732 pixel and the maximum is 0.3785 pixel / 7.57 m. The unchanged r001 gates return `ACCEPT_REGISTRATION_WITH_SPATIAL_EXCLUSIONS`; no threshold or gate changed.

The 1,800 x 1,240 preview and final PNGs pass original-resolution inspection for cloud, smoke/haze, shadow, snow, clipping, alignment, change-footprint, warning, trace, and no-label boundaries. Final JSON and PNG reconstruct byte-identically from source: 60,069 bytes / SHA-256 `1aa88c0021c610e492d2645e3f2c49a4afe96d9d907e2ee4481948a4c58f2ebd`, and 588,891 bytes / SHA-256 `fd5b9ae54e1b9c3e0d495e337387d874ae911bd0f586e835b4184312d486d931`.

The focused original/replacement source-fitness suite passes nine tests. The complete repository passes 460 tests plus 50 subtests with 20 existing NumPy deprecation warnings. The 66-package dependency check, lock check, compilation, and diff hygiene pass. U04 is authorized, but all reference, candidate, response, label, dataset, split, baseline, model, release, and readiness claims remain outside this unit.
