# Petes Lake Entry-Gate Decision

## Decision

`PASS_PETES_LAKE_ENTRY_GATE_AUTHORIZE_SEQUENTIAL_U02_OPTICAL_CUSTODY_ONLY`.

P2O4-T33-U01 r003 re-runs the current frozen event workflow after durable capsule commit `43635eb20183f49864397f8b74db4f49eb7a3b7e`, captures fresh official metadata, checks current use terms, verifies the official reference route without submitting a request, and exercises CDSE token-only authentication without exposing a secret or requesting provider product/archive bytes.

The Petes Lake event, MTBS map, two frozen Sentinel products, UUIDs, SAFE identities, sizes, checksums, access route, and source roles pass. The current Burn Severity Portal lookup returns catalogue row `50890` rather than frozen row `50884`; the governing event `OR4396912190120230825`, MTBS map `10031414`, program, standard status, name, ignition date, and acreage remain unchanged. BurnLens accepts the bounded current-row drift for acquisition and preserves both identities without claiming replacement semantics.

The pass is intentionally narrow. The post Sentinel product's 9.841206 percent tile-wide snow value requires local SCL/SNW and rendered-pixel inspection. The MTBS record says severity could be misrepresented in wetland areas; that uncertainty must be measured and excluded from any later core or ring. The optical post date and the MTBS extended-assessment post image are not temporally equivalent.

The pre-capsule r001 rehearsal and transient post-capsule r002 STAC failure remain visible as remediation evidence. U02 may acquire only the two exact Sentinel archives, one fail-closed transaction at a time, into the exact ignored no-overwrite destinations bound by r003. No pixel, reference, candidate, owner, label, dataset, split, baseline, model, metric, field, official, endorsed, emergency-ready, or operational gate advances through U01.

Primary normalized evidence: [`PETES-LAKE-ENTRY-GATE-2026-001.json`](../../../samples/cross-event/phase-two/petes-lake/PETES-LAKE-ENTRY-GATE-2026-001.json).
