# REGISTRY-2026-052 - Petes Lake custody verifier replay remediation

**Unit / issue / branch:** `P2O4-T33-U03` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Remediation commit:** `7f6ea500efae5bfb44bf2c6ecc8258ee9d3aab6c`

**Decision:** `PASS_PETES_LAKE_REPLACEMENT_CUSTODY_DESCENDANT_REPLAY`

## Code and regression bindings

| Artifact | Bytes | SHA-256 | Role |
|---|---:|---|---|
| `burnlens/petes_lake_replacement_optical_contract.py` | 62,425 | `e2ffa995039f444309222851321dde0aa47cc1e445e78b317d3d5e73e749582a` | ancestry-constrained descendant replay plus unchanged exact custody contract |
| `tests/test_petes_lake_replacement_optical_contract.py` | 27,796 | `6fc99d3c9b6054cc6640358b3d49528f21991e1911bfa6e2551d4399631814cf` | accepts clean descendant, rejects divergent ancestry, retains timestamp/tamper checks |

## Immutable evidence under replay

| Binding | Exact value | Result |
|---|---|---|
| Transaction trace | `9cd81518c8fd859a950eab263e82dc9c9e406c59` | preserved in public/private semantic record |
| Evidence commit | `af481f21cc74ce12a8aa3e0e81cab46225c8f83b` | contains exact custody report and REGISTRY-2026-051 |
| Verifier head | `7f6ea500efae5bfb44bf2c6ecc8258ee9d3aab6c` | clean, pushed, remote-equal descendant of transaction/evidence commits |
| Public report | 22,246 bytes / SHA-256 `e23d601959d09fb54fc6409f5a073df4f1a3a3a8a0d040e04a9b46c2594537b1` | unchanged |
| Semantic core | SHA-256 `78c888b4a3b954c4038a3454773b1cd7c922bc5f71957524e803ee6534d71f75` | unchanged |
| Replacement archive | 1,195,226,823 bytes / local SHA-256 `8bf6ffac0d46d17b6f3716250aed9dff49b9f89b62a310c296a5d36f41a0e1d9` | fresh verify pass; unchanged |
| Original pre | 1,185,284,273 bytes / local SHA-256 `c5b6ededc5a264fcc617f2712093b847351c5b8ed78f2ea9ce0ebc3a33e1bc34` | fresh verify pass; unchanged |

## Gate result

- Real `--verify-only` at 2026-07-21T21:21:31.309132Z from head `7f6ea500...`: pass without credentials.
- Recorded transaction source must be an ancestor of current HEAD. A non-ancestor returns `REPLACEMENT_TRACE_SOURCE_NOT_ANCESTOR_OF_CURRENT_HEAD`.
- Every non-commit trace field remains exact. Current HEAD must still be committed, clean, issue-branch scoped, and remote-equal before archive/report verification.
- Current terms and OData metadata, exact source bindings, original/replacement registrations and hashes, public/private semantic equality, and report path/bytes/hash are recomputed.
- Focused suite: 96 passed. Full repository: 456 passed plus 50 subtests; 20 existing NumPy deprecation warnings.

Disposition: `pass` for reproducible descendant replay of the already accepted custody evidence. Next dependency remains replacement U03 source-fitness r002. No provider request, archive mutation, scientific pass, U04, label, dataset, split, baseline, or model advances.
