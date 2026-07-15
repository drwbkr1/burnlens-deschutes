# REGISTRY-2026-011 - Cross-Event Feasibility Artifacts

**Checkpoint:** Issue #357 / PR #358; merge `5bfa1527410e98d8034b35ad68f6c50d5a1ec628`; verified tag `v0.10.0-cross-event-feasibility-baseline`, object `dbfda10ca50c39d8e8924096e740e71643e1f133`; generator/assessor source `ea3e164d09872825a0fadc64b9492e30c85c83c8`; candidate artifact commit `58261756a456e5d5963302c9d62c8a6b13d07f14`; lifecycle sync issue #359

| Artifact | Class | Version/state | Committed provider imagery bytes |
|---|---|---|---:|
| `burnlens/cross_event_source.py` and capture CLI | Current Census/MTBS/CDSE metadata capture with schema, route, transfer-limit, geometry, terms-link, and no-data-touch gates | BurnLens `0.10.0`; `CROSS-EVENT-SOURCE-2026-001` | 0 |
| `burnlens/cross_event_feasibility.py` and assessor CLI | Exact scene pairing, candidate eligibility, whole-group freeze, separation evidence, JSON/HTML/PNG rendering | `cross-event-feasibility-v0.1.0` | 0 |
| Repository tests | Geometry boundary inclusion, source-boundary rejection, tile-seam exclusion, two-group selection, byte-deterministic rendering | 110 tests pass in a fresh merged-main clone | 0 |
| `burnlens_deschutes-0.10.0-py3-none-any.whl` | Candidate and merged-main wheel/import evidence; not committed | Candidate 164,450 bytes / SHA-256 `d619c35ab16353768a90cb613a278b7f64006cce353b47e575c24c5b6e9bc87f`; merged-main 164,552 bytes / SHA-256 `38cf2c3eea1d97564fd1977fe4d40665e86771068c130652534cb74d06af2451`; isolated import `0.10.0`; both new entry points present | 0 |
| `CROSS-EVENT-SOURCE-2026-001.json` | Normalized current provider metadata, source geometry, exact query/route and trace record | 921,818 bytes; SHA-256 `2c78984d790046db73de68b25e2e0c87a062e2b63a5b957ed10f72382687f6ba` | 0 |
| `CROSS-EVENT-FITNESS-2026-001.json` | Candidate rules, all dispositions, exact pairs, frozen groups, separation, terms, claims, and trace | 278,263 bytes; SHA-256 `d320cee1e121c63a5ac8c5cd9f893fb63e6b8bc795b3671e62945850b1d02273` | 0 |
| `CROSS-EVENT-FITNESS-2026-001.html` | Semantic metadata-feasibility and leakage-group evidence | 11,603 bytes; SHA-256 `2fc3bb9b9b69ea494f53c8711d845030ca7a960494664c895d0f8a1b7ed3de13` | 0 |
| `CROSS-EVENT-FITNESS-2026-001.png` | Original-resolution event-separation and decision evidence | 122,947 bytes; SHA-256 `19eeb95e4e5362523e308233b6347a620f7c2ed7cb3beccf728522fd2255a1e0` | 0 |
| `MANIFEST-2026-011.json` | Checkpoint provenance and exact artifact manifest | Shipped analytical baseline; merged-main and remote-tag gates pass | 0 |
| `SOURCE-2026-011`, `TERMS-2026-006`, `PRECHECK-2026-011`, `CROSS_EVENT_FITNESS-2026-001`, `SOURCE_PRECEDENCE-2026-004`, and `USE_BOUNDARY-2026-010` | Source, rights, method, fitness, authority, and public-claim decisions | `SELECT_CROSS_EVENT_ACQUISITION_CANDIDATES` | 0 |

No provider imagery route was exercised. No credential, token, cookie, signed request, credential-store detail, native Sentinel archive, label pixel, dataset, partition, baseline, model, application, deployment, metric, independent human validation, or field validation is retained or claimed.
