# Devlog - A Matching Grid Is Not Matching Content

**Date:** 2026-07-15

**Issue:** #347

## Weakness selected

BurnLens had exact native-grid equality and a five-state label protocol, but no evidence that corresponding pre/post content was locally aligned. Label work was therefore split from registration rather than allowed to run past an unproved prerequisite.

## What changed

BurnLens `0.8.0` measures twelve fixed windows over the exact AOI using independent pre/post B04, B8A, and B12 reflectance gradients. A Hann taper and phase-only correlation find the integer peak; a localized 100x DFT refines it to 0.01-pixel samples. The estimator deliberately avoids a shared quality or stable-pixel mask because a common mask can manufacture a zero-shift peak.

The gate is visible and fail-closed: at least 90% eligible pixels, two confident bands, peak ratio at least 2, maximum band deviation 0.15 pixel, and residual at most 0.5 native pixel. Pair quality controls window usability but never overrides pixel-level review/exclusion states.

## Evidence and meaning

All twelve windows pass. Median residual is 0.0224 pixel; p95 and maximum are 0.0361 pixel, about 0.72 m. The weakest eligible fraction is 94.96%, all three bands are confident everywhere, the minimum peak ratio is 7.5916, and maximum band disagreement is 0.04 pixel.

The result is strong enough to clear the registration prerequisite. It is not a label. It says nothing by itself about fire cause, burn boundaries, background truth, deformation, provider accuracy, or field validity.

## Reliability lesson

The first final JSON audit found that the Sentinel QC parser captured inspection attributes but missed sibling message/value nodes. The registration measurements were unchanged, but the evidence would have omitted the provider report's most important cautions. The parser and its realistic XML fixture were corrected before artifact acceptance. Both exact reports now preserve that VNIR/SWIR bands have not been registered and spatio-residual histograms were not computed.

This is the checkpoint's deeper reliability point: passing scientific numbers are not enough if the evidence package drops the caveat that explains why local measurement was needed.

## Next gate

The next bounded checkpoint may create a reviewable five-state label proposal. It must preserve pixel-level quality, boundary/mixed-pixel uncertainty, temporal ambiguity, disagreement, and independent second-pass QA. No dataset, split, baseline, or model may be created until that separate label gate passes.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
