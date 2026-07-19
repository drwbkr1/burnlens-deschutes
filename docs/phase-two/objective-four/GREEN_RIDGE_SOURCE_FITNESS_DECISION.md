# Green Ridge Source Fitness Decision

## Decision

`ACCEPT_EXACT_GREEN_RIDGE_OPTICAL_SOURCE; DEFER_REFERENCE_PIXELS_CANDIDATES_LABELS_DATASET_MODEL`.

BurnLens 0.33.0 preserves and re-verifies the two exact Sentinel-2B Level-2A archives frozen for Green Ridge 0684 CS, event `OR4446712160520200817`. The registered pair contains 2,388,456,138 provider bytes. Both archives pass exact size, MD5, BLAKE3, local SHA-256, 95-member SAFE root, manifest, CRC, and no-unexpected-entry gates.

The actual full MTBS boundary contains 44,110 native 20 m pixel centers. Pair quality is 99.9887% eligible, 0.0023% review-needed, and 0.0091% excluded. All nine deterministic registration windows pass; p95 residual is 0.1091 pixel and the maximum is 0.1204 pixel / 2.408 m. The continuous dNBR distribution is visible and reproducible but is not thresholded or treated as severity or label truth.

Current official metadata identifies Green Ridge BAER map `10015623`, MTBS map `10021333`, and RAVG map `10016049`. Their pixels were not acquired or opened in this run. A broad CDSE STAC search and the public MTBS image-service route each had a live availability failure during bounded prechecks; exact Sentinel item routes and authoritative OData records passed. No route or product was substituted.

The burned-candidate route remains pending official reference pixels plus owner review. The background route remains blocked pending affirmative background evidence plus owner review. Unknown handling remains required. No owner-confirmed region, label, dataset, split, baseline, model, metric, field validation, official status, endorsement, operational readiness, or emergency-ready claim is created.

The public evidence is `GREEN-RIDGE-SOURCE-FITNESS-2026-001`, run `BL-2026-07-19-green-ridge-source-fitness-r001`, sourced from commit `4e95c66f164cb78e8ffdd45049db3051e55e0f18`.
