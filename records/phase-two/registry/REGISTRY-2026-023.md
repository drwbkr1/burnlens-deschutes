# REGISTRY-2026-023 - Current Cross-Program Reference Inventory

**Checkpoint:** Issue #411 / PR #415; checkout-stability issue #417 / PR #418; lifecycle sync #419; next scientific issue #416; analytical source `98a9895d203c778dad332db5bdc62b498aa2cd00`; evidence `f5d4d528263bfc2cf93cb7f128bcb051732797b3`; failed-release merge/tag `f96146aa0702d27eef4964cb61bd7a05d566d7c3` / `0370bedfce1279da2d104c1ebfd3c1d143ce79ca`; remediation source `c99d6f7c932e0f64e5107da0e985ab3bcc2594e7`; verified merge/tag object `65ef67a206ebfa697e6047ca09ce26eec6a24dd7` / `1b84f92cf4e7249e524fab095e233192698b7666`

| Artifact | Class | Version/state | Committed provider/private bytes |
|---|---|---|---:|
| Current-reference inventory builder and CLI | Public WFS capture, exact seven-product gate, JSON/HTML/PNG rendering | BurnLens `0.21.0`; contract v0.1.0 | 0 |
| `CROSS-EVENT-REFERENCE-INVENTORY-2026-001` JSON/HTML/PNG | Current catalog availability and freshness evidence | Run `BL-2026-07-17-current-reference-inventory-r002` | 0 |
| `SOURCE-2026-014`, `TERMS-2026-009` | Current source and bounded acquisition/terms decisions | Catalog resolved; bundle redistribution pending inspection | 0 |
| `PRECHECK-2026-019`, `LABEL_FITNESS-2026-015`, `SOURCE_PRECEDENCE-2026-007`, `USE_BOUNDARY-2026-018` | Entry, scientific, authority, and use gates | Label promotion closed | 0 |
| Original evidence-card and installed-Chrome render checks | Real rendered output | Complete and readable | 0 |
| Clean-checkout tests and packaging | Tests, compilation, dependencies, wheel, isolated install, privacy | 188 tests; identical 348,034-byte wheels; 0.21.0 / 34 entry points | 0 |
| `MANIFEST-2026-023.json` | Exact three-output inventory and release gates | Analytical evidence complete; 0.21.0 release verification failed and retained; 0.21.1 remediation verified | 0 |

The current official catalog contains seven exact records across three events and three programs. Catalog identity is not pixel fitness. No bundle is accepted, no provider byte is committed, and no label, dataset, split, baseline, or model is created.

`SOURCE-2026-013` remains frozen historical proposal provenance. The official 2026 archive-modernization record requires current exact product comparison before any new promotion.

Fresh merged main passed tests, compilation, dependency health, a live normalized-inventory match, JSON/link checks, and packaging, but failed exact output reconstruction because the JSON/HTML checkout lacked an LF contract. The 0.21.0 tag is retained as analytical history and is not a verified repository baseline.

BurnLens 0.21.1 / source `c99d6f7c932e0f64e5107da0e985ab3bcc2594e7` adds the LF rules. PR #418 merges at `65ef67a206ebfa697e6047ca09ce26eec6a24dd7`; tag object `1b84f92cf4e7249e524fab095e233192698b7666` remotely peels to that merge. Fresh merged main preserves all three authoritative sizes and hashes, passes 188 tests, and produces two byte-identical 348,032-byte wheels / SHA-256 `f8b1f2464fe0599d2bd5f7617a5cbfce244f94e0f3ef68952f84b7d9520d74c2`.
