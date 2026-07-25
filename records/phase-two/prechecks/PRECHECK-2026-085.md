# PRECHECK-2026-085 - Ward Creek U07 owner-response intake

**Date:** 2026-07-25
**Unit / issue:** `P2O4-T39-U07` / #554
**Final run:** `BL-2026-07-25-ward-creek-owner-response-intake-r002`
**Scientific source commit:** `a7f599c`
**Disposition:** `pass`
**Next dependency:** U08 exact six-event sufficiency rerun excluding Darlene

## Exact response and private reconciliation

The only valid completed response remains 1,041 bytes at SHA-256
`aadd221da037ab7fc89bd04fb4532651b917190ac55e97ee7f4d5ce4eb951dbc`.
Its 2,692-byte pre-reveal receipt remains
`dba7d81aa21dde09b21d549dba7440363906ab3cebfb4d14e958588fb2efc4bf`.

Aggregate reveal finds two yes, zero no, and zero uncertain decisions. Notes
and unit decisions remain private.

R002 recomputes the exact Sentinel/MTBS source chain, U04 routes, U05 proposal,
both candidate rasters, native CRS/grid/domain, quality and registration,
unknown rings, source/terms records, event identity, and proposal-time leakage
gate. The 8,810-byte private reconciliation is preserved without overwrite in
ignored custody at SHA-256
`25bf6ac1c4e8bfc3bea697f8e2e84053d3122b89681ea1cdafb058515afef93c`.

Both candidates pass every owner and non-owner gate together. Ward Creek adds
one 14-pixel burned core and one 25-pixel background core. All 66 ring pixels
remain unknown and excluded. Partial promotion remains forbidden.

## Required readiness audit

The customized 6,343-byte prototype-label audit input is SHA-256
`ae4badb8b45153174c20280dce88c7650c08a3fcecf3647d858ea5f299b352bf`.
The skill self-test passes. The 6,613-byte decision is SHA-256
`8c4c5decaa783dfe8c50bab83da34aef25ac69a00d445bfb6dbea918a794cb1e`.

Every required non-count gate passes:

- source and terms;
- provenance and no-overwrite custody;
- schema, raster quality, and registration;
- uncertainty and exclusions;
- event identity and proposal-time leakage control;
- exact reproducibility; and
- one unambiguous owner-returned response.

Coverage/balance and evaluation design remain explicitly deferred to U08.
The audit records `training_authorized=false`. Passing counts do not create a
dataset, split, baseline, model, or training authorization.

## Retained render failure and accepted outputs

R001 produced scientifically identical aggregate evidence but failed the real
390 by 844 browser gate because the long machine decision caused horizontal
overflow. Its exact public outputs remain in ignored failure custody:

| Output | Bytes | SHA-256 |
|---|---:|---|
| JSON | 7,513 | `3e43cd403014ed330c8bee6705e35bec2be076f90b5788d11276b43e0889539f` |
| HTML | 3,538 | `45b14510fd4e69cb3c7ed8e9d23dc8c115f00ade737f6dced9b2ee420659ab17` |
| PNG | 71,166 | `3ef086ec09130f472264ce202f1acb8edb513ade47af0456d1ef58f40a6cd9a8` |

Commit `a7f599c` adds only bounded wrapping and responsive-image constraints.
R002 reruns the entire reconciliation from that committed source:

| Output | Bytes | SHA-256 |
|---|---:|---|
| JSON | 7,513 | `091adcf7e60c15c12dfb11449e4b46a6ebf95c0ad259592fc5915836d6c1df3d` |
| HTML | 3,589 | `16d57c1a736d5fce5cc143bd89dfa999862cf81344798533e307019ff4d1a749` |
| PNG | 71,166 | `3ef086ec09130f472264ce202f1acb8edb513ade47af0456d1ef58f40a6cd9a8` |

The actual localhost HTML passes default 1280 by 720 and exact 390 by 844
inspection. Images load, desktop and narrow body widths remain inside their
viewports, metrics become two columns, the decision wraps inside its card, and
browser warning/error logs are empty. The narrow viewport screenshot is
visually correct. The browser's full-page narrow capture visually mis-stitches
the page despite correct element geometry; it is not used as evidence.

Focused Ward Creek intake tests pass 8 of 8 after tracked outputs exist.
The combined Ward Creek review/proposal/intake suites previously pass 13 with
one expected missing-output skip. Both runtime profiles pass the installed
98-command roster. NumPy emits two existing deprecation warnings during raster
reads; they do not alter output or gate state.

## Outcome and boundary

`owner-approved-prototype-region-labels-v0.5.0` now contains 14 balanced
prototype regions, 325 accepted core pixels / 13.00 hectares, and 599 excluded
ring pixels across seven events.

This is owner-approved prototype evidence, not ground truth, independent
validation, a dataset, a split, a baseline, a model, accuracy evidence,
official status, endorsement, field validation, emergency suitability, or
operational readiness. U08 must build the exact six-event candidate that drops
Darlene and rerun every Phase Two sufficiency gate before any data or model
state may advance.
