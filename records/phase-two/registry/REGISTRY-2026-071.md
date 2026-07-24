# REGISTRY-2026-071 — Ward Creek MTBS delivery custody

**Recorded:** 2026-07-24
**Issue:** #554
**Repository:** `drwbkr1/burnlens-deschutes`
**Branch:** `codex/p2o4-t39-replacement-event`

| Unit | Run | State | Immutable output | Next dependency |
|---|---|---|---|---|
| `P2O4-T39-U03-REQUEST` | `BL-2026-07-24-ward-creek-reference-request-r001` | `pass` | Exact accepted MTBS-only request report | delivery |
| `P2O4-T39-U03-CUSTODY` | `BL-2026-07-24-ward-creek-reference-delivery-r001` | `pass` | Exact ignored 4,385,952-byte archive plus tracked custody report | native source fitness |
| `P2O4-T39-U03-FITNESS` | `BL-2026-07-24-ward-creek-reference-fitness-r001` | `pending` | Terms-first inspector and deterministic render code | execute after committed code |

## Exact identities

The ignored archive SHA-256 is
`d94dfb1609c882fdd26119b2be03cea486af1bbb85e4c9607f108f9455f61d18`.
The tracked custody report is 2,476 bytes / SHA-256
`e248ac4da7b37a1421093ef0bc9009f033ffeba9af73b2d4742c2ab5f6045ed7`.
The private retrieval route, recipient, and message identity are not retained.

Both exact embedded notices pass the bounded-use gate with acknowledgement,
update, location, warranty, and fitness cautions preserved. Native pixels have
not yet been accepted as evidence.

## Decision

`PASS_WARD_CREEK_REFERENCE_CUSTODY_OPEN_NATIVE_SOURCE_FITNESS`

This registry advances custody only. It creates no candidate, owner response,
label, dataset, split, baseline, model, metric, or readiness claim.
