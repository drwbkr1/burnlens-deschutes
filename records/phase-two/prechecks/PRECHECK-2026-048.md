# PRECHECK-2026-048 - Petes Lake replacement optical contract

**Unit / issue / branch:** `P2O4-T33-U03` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Contract checkpoint:** `ab6ecc04d847aba848f0fc1f384405b10f0d8f9f`

**Checked:** 2026-07-21T20:56:29.367477Z

## Decision

`PASS_PETES_LAKE_REPLACEMENT_CONTRACT_AND_PREFLIGHT_AUTHORIZE_ONE_SINGLETON_TRANSACTION`.

The exact contract authorizes only product UUID `31fa8699-175b-4fd7-91c3-dd727a1576f5`, expected ZIP `S2A_MSIL2A_20231019T190411_N0510_R013_T10TEP_20241107T024526.SAFE.zip`, 1,195,226,823 bytes, provider MD5 `4cf05a073b4c67f5e92e052ed1eb32bc`, and provider BLAKE3 `1b28f566aee5619ea9a48c8dd042f209194a40989ba4b54cfe4e14904a0ad878`.

The clean production CLI preflight ran from exact remote-equal commit `ab6ecc04d847aba848f0fc1f384405b10f0d8f9f` and passed:

- canonical repository, issue branch, origin, committed HEAD, base, U02 custody, and selection ancestry;
- exact tracked source, terms, selection, failed U03, and original-custody bytes;
- current CDSE Terms page at 77,530 bytes / SHA-256 `e17c490e30a0544880e0ead78dcc4f749409d8ca4de67f003b2823203f864948`;
- current Sentinel Data Legal Notice at 115,881 bytes / SHA-256 `fa2955ff48a1d82e77fc7296d63681670ecdb9d2811a0505ae60d0683b62fa64`;
- exact live OData UUID, SAFE name, online state, size, sensing/publication time, platform, tile, orbit, baseline, product type, cloud value, MD5, BLAKE3, and privacy-preserving S3 suffix check;
- fresh original-pre registration, archive, checksum, local SHA-256, CRC/SAFE, ignore, untracked, and single-link verification; and
- absent, ignored, untracked, revisioned, no-overwrite replacement quarantine/raw/private-state targets plus an absent unignored public report target.

The preflight loaded no credential and requested no provider product/archive bytes. It created no quarantine, raw package, private state, or public report. The full repository suite passes 455 tests plus 50 subtests with 20 existing NumPy deprecation warnings; the focused replacement/original-custody/provider suite passes 95 tests. Lock, dependency, compilation, diff, privacy, exact-hash, and live-source gates pass.

Next dependency: record this checkpoint on issue #521, then run the exact DPAPI wrapper once. Custody may authorize only replacement U03 source-fitness r002; U04 and every reference, candidate, response, label, dataset, split, baseline, and model gate remain blocked.
