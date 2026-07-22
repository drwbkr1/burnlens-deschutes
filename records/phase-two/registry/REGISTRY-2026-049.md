# REGISTRY-2026-049 - Petes Lake replacement-post metadata selection

**Unit / issue / branch:** `P2O4-T33-U03` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Run:** `BL-2026-07-21-petes-lake-replacement-post-selection-r001`

**Source commit:** `cfa5d1923feb413859c3aa20ebc40df3e0ee2ee6`

**Decision:** `SELECT_REPLACEMENT_POST_AUTHORIZE_CONTRACT_REVISION_ONLY`

**Disposition / next dependency:** `pass` / pass scope is metadata selection for contract revision only; commit, push, and record the exact replacement contract and clean preflight before any provider transaction

## Public tracked evidence

| Artifact | Bytes | SHA-256 | State |
|---|---:|---|---|
| `samples/cross-event/phase-two/petes-lake/PETES-LAKE-SOURCE-REMEDIATION-2026-001.json` | 10,127 | `7fa82a61fa70d47364db29493700beedd60c9114a4b3a6d8ddbafdf77aecfc8c` | exact metadata-only selection report; no archive authorization |
| `docs/phase-two/objective-four/PETES_LAKE_SOURCE_REMEDIATION_DECISION.md` | 2,240 | `e81b42dcec1ce7c9a09441c8bce0983ce18cfac80bdd1cd4c66075b2303fc939` | bounded human-readable remediation decision |
| `records/phase-two/sources/SOURCE-2026-030.md` | 3,544 | `8a79758b2059f1cf240963b28c86a1ac69edd27626652d16fcc7323bdc160b8d` | six-item official-source roster and exact selected identity |
| `records/phase-two/prechecks/PRECHECK-2026-047.md` | 1,518 | `d322b6afec22411f1ded710d001677bd882ce1117d69b94cd983e3bfa0993162` | exact metadata gate summary |
| `records/phase-two/reviews/SOURCE_FITNESS-2026-007.md` | 1,771 | `57dc520ea935d7e0d139907cf88d884d0a4537b1b37cf0b5ff1b877697042c09` | metadata-fitness review and unresolved local-snow risk |

## Code and test checkpoint

| Artifact | Bytes | SHA-256 | Role |
|---|---:|---|---|
| `burnlens/capture_petes_lake_replacement_post.py` | 18,597 | `8d3d84bad6ec41d51ded6dc8840adb35bc4579868731d3ef80e8df63bc7a5c34` | deterministic current STAC/OData selection and no-overwrite report writer |
| `tests/test_petes_lake_replacement_post.py` | 2,695 | `c9ba3edcbd9337ed33b0be8d682644b05b81841ce17dbd07d328351c57c420fc` | candidate-roster, timing/cloud, ambiguity, and no-overwrite regression |

The production CLI entry point is `burnlens-capture-petes-lake-replacement-post`. Commit `cfa5d1923feb413859c3aa20ebc40df3e0ee2ee6` is pushed and remote-equal before this evidence is recorded.

## Exact input and selection bindings

| Binding | Exact value | Result |
|---|---|---|
| Failed U03 prerequisite | `PETES-LAKE-SOURCE-FITNESS-2026-001.json`; SHA-256 `ac9befd021d71ff779ec56ddefc894f4e39b92e64e65c2c4afb815663d1ad443` | pass; immutable planned-pair failure retained |
| Additional-event plan | LF-normalized SHA-256 `65fd567e234cbb521ead6b7071cab9914c672df169e3987af0c3ddfc66ccf622` | pass; exact Petes Lake boundary and event identity required |
| Search regime | Sentinel-2 L2A; Sentinel-2A; MGRS-10TEP; relative orbit 13; PB05.10; full frozen boundary coverage | six exact candidates |
| Incident-status boundary | first eligible date 2023-09-23 | August 30, September 9, and September 19 rejected before acquisition |
| Catalogue-cloud gate | at most 20% | September 29 and October 9 rejected above 99% |
| Selected product | UUID `31fa8699-175b-4fd7-91c3-dd727a1576f5`; `S2A_MSIL2A_20231019T190411_N0510_R013_T10TEP_20241107T024526.SAFE.zip` | only candidate eligible for contract revision |
| Selected provider identity | 1,195,226,823 bytes; MD5 `4cf05a073b4c67f5e92e052ed1eb32bc`; BLAKE3 `1b28f566aee5619ea9a48c8dd042f209194a40989ba4b54cfe4e14904a0ad878` | OData/STAC identity binding passes |
| Selected catalogue quality | OData cloud 0.098782%; STAC cloud 0.10%; STAC snow 0.564076% | cloud representations reconcile; snow remains an explicit local-fitness risk |

## Gate results

- Current public STAC roster, full-boundary coverage, exact source regime, deterministic ranking, official incident-timing boundary, catalogue-cloud, OData identity, online state, size, checksum, sensing, publication, platform, tile, orbit, baseline, type, two-decimal cloud reconciliation, S3-suffix privacy, no-overwrite, source, terms, warning, and trace gates: pass. This pass authorizes contract revision only.
- Exact reconstruction with the original timestamp and source commit: 10,127 bytes and SHA-256 `7fa82a61fa70d47364db29493700beedd60c9114a4b3a6d8ddbafdf77aecfc8c`, byte-identical to the tracked report.
- Credentials used: false. Provider product/archive bytes: zero. No raw, quarantine, registration, transaction-state, or custody target was created.
- No catalogue-snow threshold is introduced. The selected product must independently pass delivered native SCL/CLD/SNW, local usable-fraction, registration, paired-quality, continuous-change, actual-render, and no-label gates.
- Selection is not acquisition or source acceptance. A committed, pushed, issue-recorded replacement contract and a new clean live preflight remain mandatory before the exact singleton archive may be requested.

No U04, reference, candidate, owner response, prototype label, sixth accepted event, dataset, split, baseline, model, metric, field-validation, official, endorsed, operational, or emergency-ready claim advances.
