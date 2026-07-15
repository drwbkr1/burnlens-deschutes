# CROSS_EVENT_FITNESS-2026-001 - Two Acquisition Candidates, Groups Frozen

**Issue:** #357

**Decision:** `SELECT_CROSS_EVENT_ACQUISITION_CANDIDATES`

## Evidence reviewed

`CROSS-EVENT-SOURCE-2026-001` freezes current official MTBS, Census, and CDSE metadata from source run `RUN-2026-07-15-CROSS-EVENT-SOURCE-001`. `CROSS-EVENT-FITNESS-2026-001` deterministically evaluates every retained event and renders the decision under run `RUN-2026-07-15-CROSS-EVENT-FITNESS-001`.

| Event | Finding | Darlene center distance | Exact pair status |
|---|---|---:|---|
| Tepee 1144 NE / 2018 | selected | 34.926 km | Sentinel-2B, `MGRS-10TFP`, orbit 13, processing `05.00`, initial post window |
| McKay 1035 NE / 2017 | selected | 10.925 km | Sentinel-2A, `MGRS-10TFP`, orbit 113, processing `05.00`, initial post window |
| Milli 0843 CS / 2017 | excluded | 69.789 km | no one current Sentinel item covers the complete MTBS boundary |

Selected Tepee and McKay representative points are 27.258 km apart. Their MTBS boundaries do not overlap each other or the Darlene modeling AOI. Distance is a disclosed diagnostic, not proof of ecological independence; McKay's 10.925 km proximity remains a risk that future evaluation must not hide.

## Group contract

Event, scene, geography, and time group IDs are frozen before any imagery acquisition or tiling. Every future chip derived from one event or either scene in its pair must remain in one evaluation role. Overlapping AOIs/boundaries and same-event windows may not cross roles. No train, validation, or test assignment exists yet.

## Render and semantic QA

- original PNG reviewed at 1,800 by 1,250 pixels; selected/excluded geometry, trace, warning, and no-partition posture are legible;
- live semantic HTML reviewed in the in-app browser: one H1, ten total headings, three candidate rows, exact scene IDs, warning, source roles, and no-partition boundary visible;
- referenced image loaded completely at native size;
- JSON/HTML/PNG are byte-deterministic for fixed inputs;
- visual decision: `ACCEPT_METADATA_FEASIBILITY`.

## Narrow acceptance

Accept Tepee and McKay for the next exact authenticated source-acquisition and local-fitness checkpoint. This is acquisition planning, not a dataset or split. Catalogue cloud metadata is not AOI-local QA; MTBS is analyst-interpreted reference; county membership uses representative points; no selected archive has been downloaded or inspected; no cross-event label, independent human annotation, baseline, model, accuracy, or generalization evidence exists.
