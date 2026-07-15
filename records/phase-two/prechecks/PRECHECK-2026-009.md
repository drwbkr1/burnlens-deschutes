# PRECHECK-2026-009 - Pair-local content-registration gate

**Checked:** 2026-07-15 UTC

**Issue:** #347

**Decision:** `PROCEED_REGISTRATION_MEASUREMENT_ONLY_DEFER_LABEL_PROPOSAL`

## Cycle-start evidence

The current optical-pair workflow was rerun from synchronized `main` before implementation. `OPTICAL-PAIR-2026-001` reproduced its shipped normalized JSON, semantic HTML, and PNG byte for byte. The accepted predecessor still states the highest-leverage unresolved weakness accurately: exact source-grid equality does not prove local content registration, and no label implementation exists.

## Frozen inputs and boundaries

- Exact registered source package: `darlene3-s2-optical-pair-v0.1.0`.
- Frozen AOI: `aoi-darlene3-model-v0.2.0`, 12 km by 9 km, EPSG:32610.
- Frozen target: `target-burn-scar-v0.2.0`; experimental binary semantic segmentation only.
- Predecessor: `OPTICAL-PAIR-2026-001`, run `BL-2026-07-15-optical-pair-evidence-r001`, decision `ACCEPT_OPTICAL_PAIR_FOR_PROTOCOL_DEFER_LABELS`.
- Label design: `burn-scar-label-protocol-v0.1.0`, implementation false.
- Terms and attribution: `TERMS-2026-004`; no new source, credential, transfer, license, paid service, secret, access change, or public-sharing change is required.

This checkpoint may measure and render pair-local translation residuals. It may not create or imply burned/background labels, a companion label-state array, dataset, split, baseline, model, analytical metric, application, deployment, official result, operational value, field validation, or endorsement.

## Fresh primary-source basis

- Guizar-Sicairos, Thurman, and Fienup, *Efficient subpixel image registration algorithms*, Optics Letters 33(2), DOI `10.1364/OL.33.000156`, supports localized upsampled-DFT cross-correlation for efficient subpixel translation estimation.
- The current official Sentinel-2 product specification states that geometric refinement can introduce small measurable shifts and provides product/geometric context.
- The current January 2026 official Sentinel-2 L2A data-quality report documents Collection-1 / PB05.10 geometric improvements and limitations. It does not prove this pair's local content registration.

Both exact packaged `GEOMETRIC_QUALITY.xml` datastrip reports have global status `PASSED`. Both also say VNIR/SWIR bands have not been registered and spatio-residual histograms were not computed. Those reports are preserved as provenance and caution evidence only; they cannot satisfy the BurnLens pair-local gate.

## Frozen measurement contract

- Use the native 20 m B04, B8A, and B12 reflectance grids without source reprojection or resampling.
- Derive independent pre and post gradient-magnitude signals per band; clip each signal's gradient at its own AOI 1st and 99th percentiles.
- Do not multiply a shared quality, stable-pixel, incident, dNBR, reference, or label mask into the correlation signals. A shared mask can manufacture a zero-shift peak.
- Measure 12 non-overlapping 150 by 150 pixel windows in a deterministic four-column by three-row grid covering the AOI exactly once.
- Apply a Hann taper, phase-only cross-power spectrum, integer peak, and localized 100x upsampled DFT refinement. Record the row/column shift to apply to the post/moving content to align with pre/reference content.
- Require eligible pair-quality fraction at least `0.90`, at least two confident bands, coarse peak ratio at least `2.0`, maximum confident-band deviation at most `0.15` pixel, and consensus residual at most `0.50` native pixel / 10 m.
- Use pair-quality only to classify window usability. A window pass never overrides review/excluded SCL pixels and never assigns burned or background.

## Decision routing

- all windows pass: render for review, then accept local registration only if the real application and evidence remain legible and internally consistent;
- ambiguous or low-quality windows: preserve them as review-needed or spatially excluded;
- any residual above 0.5 pixel: reject and remediate or replace the affected evidence;
- inability to render, inspect, reconstruct, trace, or verify the result: do not ship.

The prior combined “registration plus label proposal” handoff is split at this fail-closed gate. Label proposal remains a separate later checkpoint only if the registration evidence passes or establishes explicit spatial exclusions.
