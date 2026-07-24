# PRECHECK-2026-078 — Ward Creek source-fitness reproducibility remediation

**Date:** 2026-07-24
**Unit / issue:** `P2O4-T39-U03` / #554
**Disposition:** `r002-failed-retained-r003-pending`

## Exact replay finding

The exact r002 source commit
`b5272bc28275b100fa142fee46fec5a2c97576f9` was checked out in a detached,
ignored repository-local verification worktree. The replay used the exact
generated timestamp, run ID, source commit, optical packages, MTBS archive,
and scientific code.

Two outputs reproduce exactly:

- HTML: 3,227 bytes / SHA-256
  `0ede181bf2b8d868ab45a87dd5e734047869f1254430ec8a707f9b1dca5dcfa3`;
- PNG: 385,352 bytes / SHA-256
  `7797c3846e0036f65f6adf4ff98bee8537708c01e6ac046e19ea2655c52ca44a`.

The JSON fails exact reproduction:

- tracked: 62,022 bytes / SHA-256
  `835ae480d097c8e4de6a44f53d16bbd696caf9ff2a53e956af1152c9144282e0`;
- replay: 62,086 bytes / SHA-256
  `187f9561ca01339e9396a1a4855dac95e7b5fcdfbfe99bd742d6087f010566f0`.

The only semantic differences are four extracted-vector `path` strings. They
encode the invoking checkout and output directory. Those ambient paths are
not scientific evidence and cannot be public reproducibility inputs.

## Remediation contract

R002 is retained unchanged as a failed reproducibility attempt. R003:

- uses run `BL-2026-07-24-ward-creek-reference-fitness-r003`;
- uses report `WARD-CREEK-REFERENCE-FITNESS-2026-002`;
- removes only the four ambient extraction paths;
- retains exact member names, sizes, SHA-256 hashes, and all scientific facts;
- writes to a new no-overwrite `reference-fitness-v0.1.1` directory;
- must reproduce all three public files byte-for-byte from its exact source
  commit before render confirmation can close U03.

No source, class, boundary, optical, candidate, label, dataset, split,
baseline, or model decision changes.
