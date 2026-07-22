# PRECHECK-2026-046 - Petes Lake exact optical source fitness

**Unit / issue / branch:** `P2O4-T33-U03` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Source commit:** `a7b76c662e277242d31980dcf0d815401787c2c7`

**Run:** `BL-2026-07-21-petes-lake-source-fitness-r001`

**Checked:** 2026-07-21T19:37:41Z

## Decision

`FAIL_EXACT_PETES_LAKE_OPTICAL_SOURCE_FITNESS_REMEDIATE_POST_SCENE`.

Fresh U03 prerequisite verification rehashed and reopened both exact U02 packages, their registrations, the public custody report, and frozen plan bindings. SAFE metadata, native B04/B8A/B12/SCL/CLD/SNW/TCI rasters, CRS, grids, transforms, data types, nodata contracts, and full-boundary masks pass. Chronology is pre 35 days before ignition and post 65 days after ignition.

Local source fitness fails closed. The post scene contains 26,627 SCL snow-or-ice pixels / 78.0782% of 34,103 boundary pixels. Paired eligibility is 7,439 pixels / 21.8133%; 26,661 pixels / 78.1779% are excluded. Each of eight deterministic registration windows falls below the unchanged 90% usable-fraction gate, so zero windows pass and U04 remains unauthorized.

The exact final PNG was inspected at 1,800 x 1,240 and accurately exposes the clear pre scene, snow-dominated post scene, sparse valid continuous dNBR, zero-of-eight window result, warning, and trace without clipping. Browser policy blocked direct `file://` HTML navigation and was not bypassed; tracked outputs are therefore limited to exact JSON and PNG plus human-readable records.

Disposition is `remediate`, not `pass`, `exclude`, `defer`, or `stop`. The next dependency remains U03 metadata-only replacement-scene research and contract revision before any new provider transaction. Existing packages, previews, and tracked r001 outputs are immutable.
