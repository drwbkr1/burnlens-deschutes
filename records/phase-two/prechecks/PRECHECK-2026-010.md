# PRECHECK-2026-010 - Reviewable five-state label proposal

**Checked:** 2026-07-15 UTC

**Issue:** #353

**Decision:** `PROCEED_FIVE_STATE_PROPOSAL_AND_SEPARATE_QA_ONLY`

## Cycle-start evidence

The current content-registration tool was run first from synchronized `main` against the exact ignored optical package. JSON, HTML, and PNG reproduced their shipped SHA-256 values byte for byte, all twelve windows still passed, and the decision remained `ACCEPT_LOCAL_CONTENT_REGISTRATION`. The evidence-visible weakness was unchanged: the five-state protocol existed only as design, with no reviewable pixels, companion raster, target raster, or separate QA.

## Frozen inputs and boundaries

- Exact package: `darlene3-s2-optical-pair-v0.1.0`; 2,254,805,631 bytes local and ignored; exact registration reverified.
- AOI: `aoi-darlene3-model-v0.2.0`; 600 by 450 native 20 m cells; EPSG:32610.
- Target: `target-burn-scar-v0.2.0`; binary semantic segmentation only.
- Source roles: Sentinel change/quality evidence; NIFC later mixed-method context; VIIRS complementary native-scale reference only; MTBS methodology/future cross-fire reference only.
- Predecessors: `OPTICAL-PAIR-2026-001` and `CONTENT-REGISTRATION-2026-001` accepted.
- Terms: `TERMS-2026-003`, `TERMS-2026-004`, and `TERMS-2026-005`; no unresolved licensing, credential, paid-service, secret, access, ownership, or public-sharing change.

This checkpoint may implement a label proposal and software-independent QA. It may not call candidate pixels ground truth, create a versioned dataset or split, train/evaluate a baseline or model, report accuracy, or imply official, operational, emergency-ready, field-validated, or endorsed status.

## Frozen five-state proposal contract

| State | Code | Candidate target | Rule posture |
|---|---:|---:|---|
| background-candidate | 0 | 0 | outside expanded NIFC context, affirmative four-signal stability, and at least 7 of 9 stable neighbors |
| burned | 1 | 1 | inside eroded NIFC context, dNBR at least 0.10, at least two of three supporting changes, and at least 5 of 9 burn-support neighbors |
| unknown | 2 | ignore / 255 | valid evidence satisfying neither conservative candidate class nor a review trigger |
| excluded | 3 | ignore / 255 | excluded pair quality or invalid spectral arithmetic |
| review-needed | 4 | ignore / 255 | SCL 7, NIFC boundary, candidate-burn transition, or spectral/reference disagreement |

Supporting changes are NDVI loss at least 0.05, SWIR gain at least 0.02, and NIR loss at least 0.02. Stable evidence requires absolute dNBR and NDVI change at most 0.03 and absolute SWIR/NIR change at most 0.01. These are conservative screens frozen for this exact pair, not universal or field-calibrated burn/severity thresholds.

## Separate-QA contract

- Invoke a separate module and CLI that do not import proposal classification helpers.
- Reopen the immutable sources and recompute pair quality, four spectral signals, NIFC rasterization, state rules, and target rules.
- Verify exact GeoTIFF grid, nodata, semantic tags, run ID, source commit, filenames, and report hashes.
- Compare every state and target pixel.
- Audit 20 deterministic pixels from every state plus 20 candidate-burn transition-boundary pixels.
- Preserve the fact that the same Codex director authored both implementations and that no independent human inter-rater or field validation exists.

## Decision routing

- exact machine agreement and acceptable rendered evidence: accept the exact proposal as reviewable evidence and defer dataset work;
- machine agreement with presentation or boundary defects: retain and remediate before acceptance;
- any machine disagreement, missing state, trace failure, uninspectable output, or misleading presentation: reject and preserve the failure;
- inability to verify the shipped outputs: do not ship.
