# PRECHECK-2026-008 - Exact optical-pair data-touch gate

**Checked:** 2026-07-15 UTC

**Issue:** #343

**Decision:** `PROCEED_EXACT_TWO_PRODUCT_SENTINEL_PAIR_ONLY`

## Passed before-data evidence

- Frozen AOI: `aoi-darlene3-model-v0.2.0`, 12 km by 9 km in EPSG:32610.
- Frozen target: `target-burn-scar-v0.2.0`; experimental binary semantic segmentation only.
- Exact pre/post products: `SOURCE-2026-009` and `SOURCE-2026-010`.
- Terms and attribution: resolved in `TERMS-2026-004` for the bounded action.
- Access: owner-authorized machine-bound CDSE credential; exact runtime contract in `ACCESS-2026-009`.
- Public metadata: exact identity, availability, size, checksums, platform, tile, orbit, baseline, time, and tile cloud fields match.
- Storage: more than 800 GB free at precheck; planned provider transfer is approximately 2.255 GB; raw bytes remain ignored.
- Current tool rerun: `TARGET-DECISION-2026-002` JSON, HTML, and PNG reproduced their three shipped hashes and the PNG was visually reviewed before this cycle.

## Exact action

Acquire only the two complete native SAFE products through the authenticated OData `$value` routes. Validate both provider hashes, local SHA-256, ZIP/CRC/path/root/manifest integrity, required metadata and bands, exact AOI coverage, CRS, transforms, quantification/offsets, nodata, quality classes, and same-grid pair alignment. Atomically register only a complete pair.

Inspect true color plus native 20 m red, B8A narrow-NIR, SWIR-2, and SCL evidence. A continuous spectral-change view may support pair evaluation, but this checkpoint may create no binary label array, dataset, split, baseline mask, model, metric, application, deployment, or official wildfire result.

## Label-protocol gate

The checkpoint must define burned, background-candidate, unknown, excluded, and review-needed states. SCL 7 is review evidence because burned dark features can be unclassified; SCL, VIIRS, NIFC geometry, spectral thresholds, visual appearance, or absence evidence cannot become truth alone. Unknown/excluded/review-needed states must never collapse into background.

## Stop conditions

Stop on source, terms, access, identity, availability, checksum, archive, grid, scaling, AOI, quality, secret, or output verification failure; unresolved licensing; any paid-service need; or inability to preserve the established boundaries.

All pre-data gates pass for the exact action above.

## Fulfillment

Run `BL-2026-07-15-optical-pair-intake-r005` satisfied the bounded data-touch gate and atomically registered the exact pair after repeated provider-hash, local-hash, archive-integrity, single-link, and contract verification. Evidence run `BL-2026-07-15-optical-pair-evidence-r001` then inspected only the required AOI bands and created deterministic source/protocol evidence. No label array, dataset, split, baseline mask, model, metric, application, deployment, or official wildfire result was created.
