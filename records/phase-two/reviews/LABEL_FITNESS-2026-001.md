# LABEL_FITNESS-2026-001 — Sentinel/VIIRS Pair

**Decision:** `CONDITIONAL — INSPECTION CANDIDATE, NOT LABEL-READY`

## Evidence alignment

The Sentinel scene begins at `2024-06-27T18:49:19.024Z`. The selected VIIRS swath begins at `2024-06-27T19:36:00Z`, a 46-minute 40.976-second offset. Both metadata footprints intersect `AOI-2026-001`, but neither provider asset was opened. This is adequate to choose a future inspection pair and inadequate to assert a detection or construct a label.

## Provisional label semantics after asset review

| Evidence | Earliest allowed role | Required treatment |
|---|---|---|
| VIIRS class 8/9 | Candidate positive/reference region | Require valid geolocation QA, actual AOI intersection, temporal review, view-angle review, and human optical review |
| VIIRS class 7 | Review-needed/unknown | Never promote automatically; inspect glint/water/SAA and QA flags |
| VIIRS classes 0, 1, 2, 4, 6 | Exclusion/unknown | Do not treat as background |
| VIIRS class 3 water | Exclusion/context | Not a wildfire negative by default |
| VIIRS class 5 land with no detection | Unresolved background candidate | Absence is not proof of no fire; require independent negative evidence |
| Sentinel SCL invalid/cloud/shadow/snow classes | Exclusion/unknown | Preserve outside training/evaluation denominators as defined by the later label schema |
| Clear Sentinel pixels near valid VIIRS evidence | Human-review candidate | No direct 375 m-to-10/20 m truth expansion |

## Why direct labels remain indefensible

- `FirePix` and actual mask values are unknown.
- The VIIRS mask is 375 m and its companion geolocation grid is 750 m; Sentinel bands are 10–20 m.
- A 46-minute offset permits fire evolution, smoke movement, and radiometric differences.
- VIIRS documentation records glint, bow-tie, cloud, saturation, parallax, omission, and false-alarm risks.
- Sentinel tile cloud cover does not establish a clear AOI.
- No official perimeter or independently reviewed positive/negative geometry exists.

## Decision rule for the next checkpoint

After authorized acquisition and rendering, continue toward weak/reference labels only if valid VIIRS fire pixels actually intersect the AOI and are visually/temporally plausible in the Sentinel scene. Otherwise evaluate the later clear Sentinel scenes for the controlled burn-scar fallback or stop active-fire label work. Changing targets still requires the controlling goal's owner decision.
