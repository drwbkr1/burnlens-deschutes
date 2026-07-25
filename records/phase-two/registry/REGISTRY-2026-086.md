# REGISTRY-2026-086 - P2O5-T03 U03 dataset materialization

**Recorded:** 2026-07-25

**Issue:** #562

| Unit | Run / source | Inputs | Outputs | Gates | Disposition | Next dependency |
|---|---|---|---|---|---|---|
| `P2O5-T03-U03-R001` | `BL-2026-07-25-p2o5-t03-u03-dataset-r001`; source `59610b2...` | 12 registered archives; contract/split/candidate exact | no promoted dataset | archive custody passed; Grandview all-pass registration semantics were over-constrained; 50 cores failed closed | `remediate-retained` | event-level all-pass correction |
| `P2O5-T03-U03-R002` | `BL-2026-07-25-p2o5-t03-u03-dataset-r002`; source `3e383ec...` | 13,633,040,965 registered archive bytes; contract `f6106691...`; split `a62e66f4...`; candidate `4a9646af...` | 49 files / 1,388,556 bytes; manifest `e0b7ac66...`; tree `9fb4f839...` | all archive identities/hashes/single links; native grids; cores/unknowns; no overlap/clipping; exact full replay; 18 focused tests | `pass-dataset-created-test-sealed-training-false` | `P2O5-T03-U04` |
| `P2O5-T03-U03-SUITE-R001` | foreground full suite | U03 working tree | no terminal result | caller time box exceeded at five minutes | `incomplete-retained` | logged suite |
| `P2O5-T03-U03-SUITE-R002` | logged full suite | U03 working tree | 674 pass / 1 skip / 2 fail | dataset tests pass; stale bundle assertion and expected uncommitted checkout-byte failure isolated | `remediate-retained` | commit and final rerun |

The accepted dataset contains twelve 64 by 64 native-grid patches, six
unstandardized float32 reflectance channels, explicit state and validity
masks, 287 accepted cores, and all 531 unknown-ring pixels.

The locked test roster was processed only by the deterministic materializer.
Analytical open count remains zero. No independent QA, normalization statistic,
baseline, model, metric result, training authorization, inference, deployment,
or external submission advances.
