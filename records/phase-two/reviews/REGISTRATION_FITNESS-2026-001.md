# REGISTRATION_FITNESS-2026-001 - Exact optical-pair content registration

**Issue:** #347

**Decision:** `ACCEPT_LOCAL_CONTENT_REGISTRATION`

Protocol `local-content-registration-v0.1.0` measures the translation required to align post/moving content with pre/reference content in twelve fixed native-20m windows. It uses independent B04, B8A, and B12 reflectance gradients, a Hann taper, phase-only cross-power, and localized 100x DFT refinement. It applies no shared quality/stability mask and no incident geometry, dNBR, VIIRS, burn assumption, or label threshold to the estimator.

All twelve windows pass the frozen gates:

- median residual: `0.0224` pixel;
- p95 residual: `0.0361` pixel;
- maximum residual: `0.0361` pixel / approximately `0.72` m;
- minimum eligible pair-quality fraction: `0.949556`;
- confident bands: all three in all windows;
- minimum coarse peak ratio: `7.5916` against a `2.0` gate;
- maximum band-to-consensus deviation: `0.0400` pixel against a `0.15` gate;
- residual gate: `0.50` native pixel / 10 m.

The exact package, AOI, native grids, source scaling, predecessor evidence, and product-quality reports were reverified. The packaged Sentinel reports are provenance context only: both are globally `PASSED`, but both say VNIR/SWIR bands have not been registered and spatio-residual histograms were not computed.

This decision establishes pair-local translation fitness for a later label proposal. It does not prove fire cause, a burn boundary, burned/background truth, deformation-free imagery, field validation, provider accuracy, dataset readiness, model readiness, or operational value. Pixel-level review and excluded states remain unchanged inside every passing window.
