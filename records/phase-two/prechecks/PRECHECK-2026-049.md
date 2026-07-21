# PRECHECK-2026-049 - Petes Lake replacement optical custody

**Unit / issue / branch:** `P2O4-T33-U03` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Run:** `BL-2026-07-21-petes-lake-optical-remediation-intake-r001`

**Trace commit:** `9cd81518c8fd859a950eab263e82dc9c9e406c59`

**Started:** 2026-07-21T21:05:57.352596Z

## Decision

`PASS_PETES_LAKE_REPLACEMENT_OPTICAL_CUSTODY_AUTHORIZE_U03_SOURCE_FITNESS_R002_ONLY`.

The production wrapper reran every credential-free contract gate before DPAPI import. Current official terms were observed at 2026-07-21T21:06:11.103154Z and exact OData metadata at 2026-07-21T21:06:32.523750Z. The committed/remote branch, source/terms/selection/failure/custody bindings, absent no-overwrite targets, and freshly rehashed original-pre registration all passed.

The exact singleton downloaded in one attempt from offset zero. It matched 1,195,226,823 bytes, provider MD5/BLAKE3, local SHA-256 `8bf6ffac0d46d17b6f3716250aed9dff49b9f89b62a310c296a5d36f41a0e1d9`, ZIP magic, one expected SAFE root, 95 members, 1,195,191,837 uncompressed bytes, manifest presence, and full CRC. Promotion was no-replace; the immutable registration and fresh reopen passed. Archive and manifest link counts are one.

The 11,748-byte transaction state, 24,685-byte private aggregate, and 22,246-byte public report were written once. The private aggregate binds public bytes at SHA-256 `e23d601959d09fb54fc6409f5a073df4f1a3a3a8a0d040e04a9b46c2594537b1`; both bind semantic SHA-256 `78c888b4a3b954c4038a3454773b1cd7c922bc5f71957524e803ee6534d71f75`. The wrapper's credential-free final verifier passed and returned zero. Credential environment variables were absent afterward. Quarantine is absent and no acquisition process remains.

Post-transaction credential-free verifier attempts at 2026-07-21T21:12:49.731932Z and 2026-07-21T21:13:25.729861Z failed closed on transient remote-query and official-terms transport errors. The branch was immediately confirmed unchanged and remote-equal. A bounded retry at 2026-07-21T21:13:55.263189Z passed with no credential or custody mutation.

The process audit found five stale broad loopback servers on ports 8765/8767, two launched from the retired OneDrive checkout plus two runtime children and one remaining generic Python server. Exact process/listener identity was verified before termination. All five stopped and both ports closed. This is retained operational-security drift; it did not alter archive or evidence bytes.

Custody authorizes only a new replacement U03 source-fitness r002 run from the immutable original pre plus replacement post. No local-pixel fitness, source pass, U04, reference, candidate, owner response, label, sixth event, dataset, split, baseline, or model is authorized.
