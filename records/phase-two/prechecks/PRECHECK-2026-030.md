# PRECHECK-2026-030 - Exact Owner Region Response Intake

**Issue:** #461

## Entry evidence

- Verified `v0.30.0-region-owner-review-surface` binds six exact candidates and intentionally contains zero responses and zero labels.
- The owner completed the exact surface on 2026-07-19. The hash-named export is 1,635 bytes with SHA-256 `f5b97af85579412b66e2bb773684b02230b9cf216cdb4c70313c9636b634c1e6`.
- The export binds run `BL-2026-07-18-region-owner-review-surface-r005`, pilot SHA-256 `1db602a721373f29f31f9d720ea9871b99d6e391e598236681a9cb438a51b55f`, all six candidate IDs and raster hashes, six completed decisions, and owner attestation.
- Cycle-start reconstruction opened the actual three-event local optical/reference packages and reproduced all nine pilot outputs plus the private mapping byte for byte. The ten-file owner surface also reproduced byte for byte.
- Dataset, split, baseline, and model versions remain absent. Three event groups remain below the required six.

## Allowed work

Preserve the exact response and receipt only in ignored repository-local custody. Privately reconcile each decision against exact raster, source, terms, quality, uncertainty, and event-identity gates. Publish only aggregate counts, hashes, gate results, and limitations. A yes may become an explicitly owner-approved prototype region label only when every non-owner gate passes.

## Prohibited work

Do not publish notes or unit decisions, alter candidate bytes, convert unknown rings or outside pixels to background, create a dataset or split, begin a baseline or model, or claim independent ground truth, inter-rater agreement, field validation, official status, endorsement, accuracy, or operational/emergency readiness.

**Entry decision:** `PROCEED_EXACT_PRIVATE_INTAKE_AND_GATE_RECONCILIATION_KEEP_DATASET_CLOSED`.
