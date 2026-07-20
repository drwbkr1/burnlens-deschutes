# Grandview Source Fitness Decision

## Decision

`ACCEPT_EXACT_GRANDVIEW_OPTICAL_SOURCE; DEFER_REFERENCE_PIXELS_CANDIDATES_LABELS_DATASET_MODEL`.

BurnLens 0.39.0 preserves and re-verifies the two exact Sentinel-2B Level-2A archives frozen for Grandview 0558 OD, event `OR4446612140020210711`. The registered pair contains 1,923,481,794 provider bytes. Both archives pass exact size, provider MD5/BLAKE3, local SHA-256, 109-member SAFE root, manifest, CRC, and no-unexpected-entry gates.

The actual full MTBS boundary contains 62,588 native 20 m pixel centers. Pair quality is 97.5794% eligible, 1.0337% review-needed, and 1.3868% excluded. All nine deterministic registration windows pass; p95 residual is 0.1158 pixel and the maximum is 0.153 pixel / 3.06 m. The continuous dNBR distribution is visible and reproducible but is not thresholded or treated as severity or label truth.

Current official metadata identifies Grandview BAER map `10019092`, MTBS map `10023989`, and RAVG map `10019464`. Their pixels were not acquired or opened in this run. These identities therefore cannot support a burned, background, unknown, or owner-review decision.

The burned-candidate route remains pending official reference pixels plus owner review. The background route remains blocked pending affirmative background evidence plus owner review. Unknown handling remains required. No Grandview candidate, owner-confirmed region, label, dataset, split, baseline, model, metric, field validation, official status, endorsement, operational readiness, or emergency-ready claim is created.

The public evidence is `GRANDVIEW-SOURCE-FITNESS-2026-001`, run `BL-2026-07-20-grandview-source-fitness-r001`, sourced from commit `527caeb0c83fb70bdd0af37d11a1215914ca0be9`.
