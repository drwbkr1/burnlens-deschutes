# Active Fire Reference Review

Draft created after branch creation and fresh source research.

Documentation only. No data use or implementation is authorized.

## Reviewed source family

NASA FIRMS is the primary candidate active fire reference family for Objective Three planning.

## Candidate roles

| Role | Status |
|---|---|
| Reference display | Allowed later with caveats. |
| Weak label support | Allowed later with caveats. |
| Sampling support | Allowed later with caveats. |
| Baseline comparison | Allowed later with caveats. |
| Pixel perfect mask | Not allowed. |
| Public safety guidance | Not allowed. |

## Key constraints

- Products are tied to satellite overpass timing.
- Clouds, smoke, view geometry, and sensor limits can create missed detections.
- Product resolution and actual fire extent are not the same thing.
- Confidence values are useful but require empirical handling.
- Faster products may require stronger quality caveats.

## Phase One decision

FIRMS remains feasible as a future reference, weak label, sampling, baseline, and comparison source. It is not feasible as a standalone mask source.
