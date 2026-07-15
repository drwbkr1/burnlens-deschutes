# REGISTRY-2026-001 — Phase Two Metadata Artifacts

| Artifact | Class | State | Public-facing | Source/derived distinction |
|---|---|---|---:|---|
| `AOI-2026-001.md` | AOI decision record | Complete for discovery | No | BurnLens-created research envelope, not official geometry |
| `SOURCE-2026-001.md` | Source record | Reviewed | No | Official Copernicus metadata described by BurnLens |
| `SOURCE-2026-002.md` | Source record | Reviewed | No | Official NASA metadata described by BurnLens |
| `SOURCE-2026-003.md` | Source-context record | Reviewed | No | Official Oregon facts described by BurnLens |
| `ACCESS-2026-001.md` | Access log | Complete | No | BurnLens process record |
| `TERMS-2026-001.md` | Terms review | Complete for metadata | No | BurnLens decision backed by official terms |
| `PRECHECK-2026-001.md` | Technical precheck | Complete for metadata | No | BurnLens verification record |
| `METADATA-2026-001.json` | Normalized metadata fixture | Complete | No | BurnLens normalization of official metadata; no source asset bytes |
| `MANIFEST-2026-001.json` | Provenance manifest | Complete for checkpoint | No | BurnLens traceability record |
| `SOURCE_PRECEDENCE-2026-001.md` | Review | Complete | No | BurnLens control record |
| `USE_BOUNDARY-2026-001.md` | Review | Complete | No | BurnLens control record |
| `SOURCE-2026-009.md` | Exact source record | Public metadata accepted; raw acquisition pending | No | Official Sentinel-2 pre-fire product described by BurnLens |
| `SOURCE-2026-010.md` | Exact source record | Public metadata accepted; raw acquisition pending | No | Official Sentinel-2 post-fire product described by BurnLens |
| `TERMS-2026-004.md` | Terms review | Complete for issue #343 bounded action | No | BurnLens decision backed by current official terms and legal notice |
| `ACCESS-2026-009.md` | Access log | Authorized; exact delivery pending | No | BurnLens secret-safe access record |
| `PRECHECK-2026-008.md` | Technical precheck | Passed for exact two-product action | No | BurnLens before-data verification record |

No entry is a dataset, implemented label, model input, baseline output, model, metric, application result, operational release, or official product. The new source records identify exact provider products; their raw bytes remain ignored and uncommitted.

The fixture checksum is recorded in `MANIFEST-2026-001.json` after file creation and verification.
