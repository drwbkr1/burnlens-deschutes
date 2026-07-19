# Region Owner Response Intake Decision

**Issue / PR / branch:** #461 / #463 / `codex/p2o4-t19-region-response-intake`

**Run:** `BL-2026-07-19-region-owner-response-intake-r001`

**Source / public artifacts:** `1d6966880278264154977ef4287b2db2e0a24026` / `d8a13facd78c12e70dadbe9e9a397122cce46883`

## Decision

`ACCEPT_OWNER_APPROVED_PROTOTYPE_REGION_LABELS_DEFER_DATASET_SPLIT_BASELINE_MODEL`.

BurnLens preserves the exact 1,635-byte completed owner export under ignored, no-overwrite repository-local custody. Its SHA-256 is `f5b97af85579412b66e2bb773684b02230b9cf216cdb4c70313c9636b634c1e6`. All six responses are yes, but yes alone does not promote a region: the intake reopens every candidate raster and independently verifies exact bytes, native grid, CRS, nodata, 0/1/2 domain, 8-connected core, one-pixel unknown ring, source and terms records, quality/registration, and event identity.

All six candidates pass. The resulting `owner-approved-prototype-region-labels-v0.1.0` contains three burned and three background regions across Darlene, McKay, and Tepee, totaling 136 accepted core pixels / 5.44 hectares. All 246 ring pixels remain unknown and excluded. Unit decisions, notes, private paths, and seed identities remain private; the public report contains aggregate bindings only.

Three event groups remain below the required six. BurnLens therefore creates no dataset, split, baseline, model, metric, or readiness claim. These labels are owner-approved prototype evidence, not independent ground truth, inter-rater agreement, field validation, official information, endorsement, or operational evidence.
