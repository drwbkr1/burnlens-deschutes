# P2O4-T12 Current Reference Bundle Fitness Decision

**Issue / PR / branch:** #416 / #430 / `codex/p2o4-t12-bundle-fitness`

**Run:** `BL-2026-07-17-current-reference-bundle-fitness-r003`

## Decision

`ACCEPT_CURRENT_BUNDLES_AS_BOUNDED_OWNER_REVIEW_EVIDENCE_DEFER_LABELS_DATASET_MODEL`.

Both exact deliveries and all seven product identities pass byte, archive, metadata, CRS, grid, nodata, class-domain, and rendered-output inspection. The products materially improve the evidence available for owner review:

- all 9,119 McKay burned proposal pixels and all 92 Tepee burned proposal pixels are affirmative in both current MTBS dNBR6 and RAVG CBI4;
- all 55 McKay background proposal pixels and 493 of 494 Tepee background proposal pixels are non-affirmative in both programs;
- Darlene burned proposal pixels show a median BAER dNBR of 335 and 99.9946% positive change, while current RAVG supplies categorical evidence;
- existing unknown, excluded, and review-needed states remain visible and unchanged.

![Current official reference bundle fitness](../../../samples/reference/phase-two/CURRENT-REFERENCE-BUNDLE-FITNESS-2026-001.png)

## Product and terms boundary

MTBS is analyst interpreted; RAVG is forest calibrated and timing sensitive. Neither is independent ground truth or comprehensive field validation. BAER BARC is preliminary input to field/team assessment. The current Darlene BAER delivery contains no classified BARC or SBS raster. The legacy Tepee thresholded BARC4/BARC256 has a distribution restriction and remains private and excluded; only its separately public unthresholded dNBR is summarized.

## Next checkpoint

Build a repository-owned owner yes/no/uncertain review surface that reopens all original 56 units. Each unit must show appropriate frozen optical evidence and permitted current reference evidence. A yes is necessary but not sufficient: prototype-label acceptance still requires reproducibility, source, quality, and event-level leakage gates. No/uncertain remain excluded.

This checkpoint records zero owner responses, promotes zero labels, and creates no dataset, split, baseline, model, field-validation, independent-review, inter-rater, official, endorsed, operational, emergency-ready, or enterprise claim.

## Verified release

PR #430 merged at `a91103a01787e3d8de09522527be13efbc7c1828`. Fresh main passes 207 tests, exact three-output reconstruction, compilation, dependency health, and canonical 383,225-byte packaging / SHA-256 `8e32a8a0494ae5c261f4ebb442b21c348c8ef3bb218be8fdf438471ad9b0bc03`. Annotated tag object `b6578ca80ff3d3418335f0ae76cc12f6b4183fca` remotely peels to the merge as `v0.24.0-current-reference-bundle-fitness`. Issue #432 owns the next owner-review checkpoint.
