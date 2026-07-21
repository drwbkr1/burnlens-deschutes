# PRECHECK-2026-042 - Grandview Owner Response Intake

**Checked:** 2026-07-21 UTC

**Issue / branch:** #517 / `codex/p2o4-t32-grandview-owner-response-intake`

**Decision:** `PASS_EXACT_GRANDVIEW_OWNER_RESPONSE_LOCK; RECONCILE_TWO_YES_DECISIONS_AGAINST_ALL_NON_OWNER_GATES`

## Exact response custody

The newest completed Grandview export is exactly 887 bytes with SHA-256 `41fe9b3fa731a57d65def5d6952ef029a982ed26bcf62b9bf9cfa5d267018585`. Before any decision value was read, BurnLens validated the response envelope, surface/run/schema/proposal bindings, two exact candidate/raster bindings, completion chronology, and owner attestation. It then preserved those exact bytes without overwrite in ignored repository-local custody.

The 1,835-byte receipt has SHA-256 `0b2fa3360c5c54f39a5b2623ee0cf8acd0ab13ca76b2ef2ecd704c2a699dfa6a`. It records `decisions_revealed=false`, `qualifying_owner_response=null`, and `decision_values_read=false`. Both the response and receipt pass the repository ignore gate. The tracked review surface remains blank and unattested.

Only after that transaction completed were the two allowed decision values read. The aggregate is two yes, zero no, and zero uncertain. Unit decisions and notes remain private.

## Promotion boundary

Owner yes is necessary but insufficient. Each exact core may advance only if the committed intake generator revalidates the response and receipt, exact proposal/raster bytes, native-grid contract, connected core, one-pixel unknown ring, source and terms records, quality/registration evidence, uncertainty exclusion, and immutable event identity. Any failed gate excludes the affected unit. No dataset, split, baseline, model, metric, accuracy, official, field, endorsed, emergency-ready, or operational claim may advance.
