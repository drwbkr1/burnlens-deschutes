# Pair-Local Content-Registration Decision

## Checkpoint scope

Issue #347 isolates the unresolved registration requirement from later label proposal work. The accepted optical pair already proves exact native-grid identity; this checkpoint measures whether corresponding local content is sufficiently aligned for a later reviewable label proposal.

This sequencing change is deliberate. Registration is a fail-closed input to label construction, so bundling both would either hide a failed prerequisite or produce disposable label work. The Phase Two outcomes do not change, and label implementation, independent QA, dataset construction, baselines, and models remain later gates.

## Method decision

Protocol `local-content-registration-v0.1.0` measures translation from post/moving content to pre/reference content in twelve fixed native-20m windows. For each B04, B8A, and B12 band, it derives an independent reflectance gradient-magnitude signal, clips only that signal's AOI gradient extremes, applies a window-local Hann taper, and estimates phase correlation with a localized 100x upsampled DFT.

The estimator does not use a shared quality or stable-pixel mask because a shared mask can create an artificial zero-shift peak. NIFC geometry, VIIRS observations, dNBR, spectral thresholds, burn assumptions, and later label states do not select pixels, windows, correlation peaks, or decisions. Pair-quality evidence only determines whether a window has enough eligible pixels to be usable.

## Gates

| Gate | Requirement |
|---|---:|
| Window grid | 4 columns by 3 rows; 12 fixed 150 x 150 native-20m windows; full AOI coverage |
| Eligible pair-quality fraction | at least 0.90 per window |
| Confident spectral bands | at least 2 of B04, B8A, B12 |
| Coarse peak ratio | at least 2.0 per confident band |
| Maximum band-to-consensus deviation | at most 0.15 pixel |
| Consensus residual | at most 0.50 native pixel / 10 m |
| Source reprojection/resampling | prohibited for this measurement |
| Label effect | none |

A passing window establishes bounded translation evidence only. It never establishes fire cause, a burn boundary, burned or background truth, severity, field validity, or operational value. Pixel-level quality review and exclusions remain binding within passing windows.

## Product-quality context

Both packaged Sentinel datastrip geometric-quality reports have global status `PASSED`, image-refining checks marked `PASSED`, absolute-location values of 20 m against 30 m expectations, and planimetric-stability values of 3 m against 5 m expectations. They also state that VNIR/SWIR bands have not been registered and spatio-residual histograms were not computed. BurnLens therefore records these fields as provenance context and requires its own pair-local evidence.

## Current state

The method and gates are frozen for the bounded run. Machine measurements on the exact pair produced a provisional all-window pass, with residuals far inside the 0.5-pixel gate. The decision remains `PENDING_VISUAL_REVIEW` until the source-bearing implementation is committed, the exact run is reconstructed from that commit, and the real JSON, HTML, and PNG are inspected.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
