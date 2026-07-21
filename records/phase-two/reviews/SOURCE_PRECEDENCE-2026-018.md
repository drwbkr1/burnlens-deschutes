# SOURCE_PRECEDENCE-2026-018 - Petes Lake entry evidence

**Unit / issue:** `P2O4-T33-U01` / #521

## Decision

1. Current source terms and exact identity records `SOURCE-2026-028`, `SOURCE-2026-029`, `TERMS-2026-024`, and `TERMS-2026-025` govern all use.
2. Current CDSE OData UUID, SAFE name, size, online state, MD5, and BLAKE3 govern U02 archive custody; STAC preserves discovery and tile-wide quality metadata.
3. Delivered Sentinel pixels, SCL/SNW, metadata, and registration will govern optical fitness only after U02/U03 pass.
4. Current MTBS event/map identity and the newest exact delivered bundle govern official-reference evidence. The current Portal lookup row governs acquisition while frozen row `50884` remains historical discovery provenance; no service-level replacement semantics are inferred.
5. MTBS remains analyst-interpreted, revisable reference evidence. Its boundary is not an incident perimeter, its severity is not automatic pixel-perfect truth, and its wetland warning remains unresolved until measured.
6. BurnLens-derived change evidence and later deterministic proposals remain lower-priority experimental artifacts.
7. Owner yes/no/uncertain is a later evidence decision. Yes is necessary but never sufficient, and no per-candidate decision or non-owner gate may be batched away.

U01 authorizes only sequential optical custody in U02. It does not authorize reference pixels, candidates, labels, a dataset, a split, a baseline, a model, or a public performance claim.
