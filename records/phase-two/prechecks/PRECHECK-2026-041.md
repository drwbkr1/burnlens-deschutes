# PRECHECK-2026-041 - Grandview affirmative background evidence

**Checked:** 2026-07-20 UTC

**Issue / branch:** #503 / `codex/p2o4-t29-grandview-background-evidence`

**Decision:** `ACQUIRE_ONE_EXACT_EXTENDED_SCENE_BEFORE_BACKGROUND_ROUTE_DECISION`

## Cycle-start evidence

Verified BurnLens 0.40.0 was run first from lifecycle-synchronized main `c08c861cb73c5ca8ebfa711f240426b413fe48f6`. Exact reconstruction of all three public Grandview reference-fitness artifacts passed. The actual report again showed 58,438 MTBS class 2-4 pixels, 793 MTBS-unresolved boundary pixels, RAVG limited by its exact sparse/no-tree warning, and `BLOCKED_PENDING_AFFIRMATIVE_BACKGROUND_EVIDENCE`. Candidate, label, dataset, split, baseline, and model versions remain null.

## Exact next source

Fresh official CDSE STAC reconnaissance returned complete 3 km context coverage in the bounded 2022 anniversary window. The frozen scene is:

- `S2B_MSIL2A_20220628T184919_N0510_R113_T10TFQ_20240628T114848.SAFE`
- CDSE product `43da9509-e01e-4c33-a85a-0ec45c04035a`
- 2022-06-28T18:49:19.024Z; Sentinel-2B; MGRS-10TFQ; relative orbit 113; processing 05.10
- 950,987,607 bytes; MD5 `f42d0d1e618c712314947de897bd997d`; BLAKE3 `ad2747cb713d6f0cf9f1aba88241cd7c669c2e281b4e155d5ac2278158f7bda2`
- live OData `Online=true`; product cloud metadata 0.169377 percent

It is 25 days after the original 2021-06-03 pre-fire anniversary and is the closest low-cloud same-platform, same-tile, same-orbit scene in the bounded search. The baseline difference is explicit and must pass metadata-derived reflectance plus content-registration gates. Native SCL and required bands must pass after exact acquisition.

The route may use BAER, MTBS, and RAVG official boundary geometries only as conservative exclusion context. RAVG modeled classes remain disallowed as affirmative evidence for this sparse/non-tree event. No candidate or label may advance in this checkpoint.
