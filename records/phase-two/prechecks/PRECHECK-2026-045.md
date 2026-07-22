# PRECHECK-2026-045 - Petes Lake exact optical custody

**Unit / issue / branch:** `P2O4-T33-U02` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Acquisition trace commit:** `31eedcddff0a712001181fd282f18f0e41ed5412`

**Post-success CLI fix:** `62e920e272e83b67f096659f77a25eac129f707c`

**Checked:** 2026-07-21T18:59:28Z

## Decision

`PASS_PETES_LAKE_OPTICAL_CUSTODY_AUTHORIZE_U03_ONLY`.

The final clean, remote-equal, credential-free preflight passed at 2026-07-21T18:40:31Z. Production run `BL-2026-07-21-petes-lake-optical-intake-r001` began at 2026-07-21T18:40:41Z and enforced the exact pre-then-post transaction order.

Pre metadata was refreshed at 2026-07-21T18:40:43.953482Z. The pre archive downloaded in one attempt, matched 1,185,284,273 bytes plus provider MD5/BLAKE3 and local SHA-256, passed ZIP/SAFE/manifest/CRC inspection, promoted without replace, registered immutably, wrote exact private state, and passed fresh verification. Only then was post metadata refreshed at 2026-07-21T18:43:18.731216Z. The post archive independently passed the equivalent one-attempt transaction at 1,243,068,088 bytes.

Both archives contain exactly 95 ZIP members under their required SAFE roots and pass full CRC. Raw archives, registration files, and three private state files are ignored, untracked, single-link, no-overwrite, and bound in `REGISTRY-2026-047`. Quarantine retains zero files after successful promotion. No acquisition process remains.

## Retained post-success defect and remediation

The transaction wrote the complete passing private aggregate and 23,521-byte public custody report before the production CLI raised `KeyError: 'decision'`. The report intentionally wraps its decision in `semantic_record`; the CLI incorrectly required a top-level key. The wrapper therefore returned nonzero and skipped its final verifier even though both exact custody transactions had passed.

BurnLens did not delete, reacquire, or rewrite either package. A direct credential-free `--verify-only` run passed immediately against the preserved outputs. Commit `62e920e272e83b67f096659f77a25eac129f707c` makes the CLI accept the report's exact semantic decision while retaining fail-closed behavior if no decision exists. Focused verification passed 64 tests, and the full repository suite passed 395 tests with 20 existing NumPy deprecation warnings. A second credential-free verifier from the pushed fix commit passed with the custody report as the only untracked public artifact and no credential environment before or after.

## Boundary and next dependency

The owner-authorized CDSE credential was exercised only inside the production wrapper and cleared. No token, password, authorization header, cookie, secret, or private credential-store detail is retained or published. Provider archives and private states remain ignored and untracked.

U02 passes custody only. U03 must open and inspect the exact delivered pixels, metadata, CRS, bands, grids, nodata, SCL/SNW, local cloud/smoke/shadow/snow, temporal fitness, registration, and real render. No source-fitness, reference, candidate, owner, label, dataset, split, baseline, model, metric, field, official, endorsed, emergency-ready, or operational gate is implied.
