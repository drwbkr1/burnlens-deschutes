# PRECHECK-2026-050 - Petes Lake custody verifier replay remediation

**Unit / issue / branch:** `P2O4-T33-U03` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Remediation commit:** `7f6ea500efae5bfb44bf2c6ecc8258ee9d3aab6c`

**Checked:** 2026-07-21T21:21:31.309132Z

## Decision

`PASS_PETES_LAKE_REPLACEMENT_CUSTODY_DESCENDANT_REPLAY`.

The original verifier required the current clean branch HEAD to equal the transaction's immutable trace commit. That was correct during the wrapper run but made the same custody report fail after its evidence commit was added, even when the new HEAD was a clean remote-equal descendant with unchanged source, terms, contract, and report bindings.

The remediation preserves the original trace and every strict binding. It permits only a current trace with the same repository, branch, issue, base, selection/custody ancestry, and tracked-file roster, and requires the recorded transaction commit to be a Git ancestor of the current remote-equal HEAD. Divergent history, changed bindings, missing commits, non-clean state, remote drift, metadata/terms drift, archive drift, or report/private binding drift still fails closed.

The real credential-free verifier passes from descendant head `7f6ea500efae5bfb44bf2c6ecc8258ee9d3aab6c` against transaction trace `9cd81518c8fd859a950eab263e82dc9c9e406c59`, the immutable original pre, the exact replacement post, both private states, and the committed public report. It loaded no credential and changed no custody byte.

Focused replacement/original-custody/provider regression passes 96 tests. The complete repository passes 456 tests plus 50 subtests with the same 20 existing NumPy deprecation warnings. Compilation and diff hygiene pass.

This fixes replay only. It does not change the contract, archive, registration, report, semantic hash, custody decision, local-pixel state, U04 gate, or any reference, candidate, response, label, dataset, split, baseline, or model status.
