# PRECHECK-2026-034 - Green Ridge Reference Request

**Date:** 2026-07-19 UTC

**Issue / branch:** #477 / `codex/p2o4-t22-green-ridge-reference-fitness`

## Result

`PASS_EXACT_THREE_MAP_NATIVE_UTM_REQUEST_PRECHECK`.

The verified v0.33.0 tool reconstructed exactly at cycle start and again identified zero Green Ridge official reference pixels as the highest-leverage evidence weakness. The ignored repository custody contains the earlier seven Darlene/McKay/Tepee deliveries but no Green Ridge reference archive. Reusing those products would violate event and map identity; no existing Green Ridge request evidence was found.

The current official Burn Severity Portal WFS returned exactly three property-only Green Ridge rows / 1,631 UTF-8 bytes / SHA-256 `54822347ae68c0e423667942d580ec6632cdbe879fb3124ba86aeda5052530a5`: BAER `10015623`, MTBS `10021333`, and RAVG `10016049`. All three are standard records. The official viewer currently submits standard map IDs to `https://burnseverity.cr.usgs.gov/downloads/addQueue.php`, exposes 18 mapping-product families, and defaults to UTM. BurnLens freezes that exact native-UTM request rather than selecting Albers reprojection.

The official 2026 first-quarter release notice says the refreshed portal can introduce pixel-level differences from legacy products because imagery/calibration and native-UTM processing were modernized. Therefore these current bundles cannot silently replace or be compared as byte-equivalent to older annual-service clips. Exact archive notices, identities, structure, CRS, grids, nodata, masks, class domains, and pixels remain post-delivery gates.

## Request safety

- one POST only after exact metadata validation;
- no automatic retry when a POST outcome is unknown;
- recipient supplied only through a process environment variable and never written to the receipt;
- exact metadata/queue response bytes and a private-safe receipt atomically preserved under ignored repository storage;
- no overwrite, substitution, label, dataset, split, baseline, or model action.

