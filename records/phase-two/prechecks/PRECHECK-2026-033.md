# PRECHECK-2026-033 - Green Ridge Exact Optical Pair

**Issue:** #472

## Entry evidence

- Verified `v0.32.0-additional-event-groups` freezes Green Ridge event `OR4446712160520200817` first in the one-event-at-a-time acquisition order.
- The released JSON, HTML, and PNG reconstruct byte for byte at cycle start.
- Current OData records independently pass exact UUID, SAFE, size, online, checksum, platform, tile, orbit, baseline, type, time, and path checks for both frozen products.
- Both exact STAC items are live. The broad all-candidate STAC search route failed during one recapture and is disclosed rather than bypassed with a substitute.
- The pair totals 2,388,456,138 bytes / about 2.224 GiB; local free space exceeds 770 GiB.
- `TERMS-2026-016` resolves bounded acquisition and modified evidence; `ACCESS-2026-011` binds the existing protected credential boundary.
- Seven focused contract tests, live metadata validation, PowerShell syntax, and diff checks pass before data touch.

## Allowed work

Acquire only the exact Green Ridge pair into ignored no-overwrite custody; validate bytes, checksums, safe archive structure, metadata, CRS, grids, nodata, masks/SCL, local quality, temporal relationship, and registration; render actual evidence; acquire only minimum official reference bytes later needed for bounded fitness.

## Prohibited work

Do not substitute scenes, acquire Grandview or Petes Lake, commit native provider bytes or secrets, infer local quality from catalogue cloud, create labels, accept a dataset, assign a split, run a baseline/model, spend money, change sharing/access, or imply field, official, endorsed, operational, or emergency-ready status.

**Entry decision:** `PROCEED_EXACT_GREEN_RIDGE_PAIR_FAIL_CLOSED`.
