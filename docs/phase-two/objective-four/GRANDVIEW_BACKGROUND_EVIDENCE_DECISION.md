# Grandview Background Evidence Decision

**Issue:** #503

**Candidate version:** BurnLens 0.41.0

**Decision:** `ACCEPT_AFFIRMATIVE_BACKGROUND_ROUTE_DEFER_CANDIDATES_LABELS_DATASET_MODEL`

BurnLens first reran verified v0.40.0 and reproduced the Grandview affirmative-background blocker. Fresh official CDSE discovery then froze one near-anniversary Sentinel-2B scene: `S2B_MSIL2A_20220628T184919_N0510_R113_T10TFQ_20240628T114848.SAFE`. Its exact 950,987,607 provider bytes pass MD5, BLAKE3, local SHA-256, ZIP, registration, and no-overwrite custody gates.

The original pair is baseline 05.00 and the extended scene is 05.10. BurnLens uses product-metadata BOA scale and offsets, then measures actual registration on the complete fire boundary. Seven of nine windows pass; two review-needed windows are spatially excluded; none fail; p95 residual is 0.0944 pixel.

The route transfers the established Darlene dNBR, NDVI, SWIR, NIR, and 7-of-9 neighbor thresholds without search or tuning. It parses the exact delivered BAER, MTBS, and RAVG burn-area vectors, rasterizes pixel-center inclusion on the 20 m context grid, and excludes their union plus 60 m. RAVG modeled classes remain disallowed because the exact delivery warns of sparse to no pre-fire tree cover.

Run `BL-2026-07-20-grandview-background-evidence-r001` leaves 67,782 route-evidence pixels / 2,711.28 ha, 1,533 components, and 181 components at least one hectare. Public JSON/HTML/PNG reconstruct exactly from generator `08e04b71836ffbcb8d59761c53586ece6f85687f`.

The result permits only a separate deterministic region-proposal checkpoint followed by owner yes/no/uncertain review. It is not ground truth, field validation, an official unburned product, a candidate, a label, endorsement, operational readiness, or emergency guidance. Dataset, split, baseline, and model versions remain null.
