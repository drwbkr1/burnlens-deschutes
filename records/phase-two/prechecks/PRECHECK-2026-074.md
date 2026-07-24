# PRECHECK-2026-074 — Ward Creek optical custody

**Date:** 2026-07-24  
**Unit / issue / branch:** `P2O4-T39-U02` / #554 / `codex/p2o4-t39-replacement-event`  
**Disposition:** `pass`  
**Next dependency:** `P2O4-T39-U03`

## Bound entry

U02 starts only after U01 passes and is recoverably pushed at
`11c5ad377cb6a65242720ae819c769b29b82cee2`. The acquisition implementation
is pushed at `8a0b1ee39e06b75a87bf594b80e3a69805f2bfa0`. The first credential-free
preflight then fails closed on two mistyped U01 digest constants. It acquires
zero provider bytes and creates no custody target. Correction
`3b3406b` repairs only those constants and adds an all-binding regression test.

The corrected preflight verifies:

- the canonical repository root, exact branch, origin, committed and pushed
  head, clean tracked worktree, and required base/U01 ancestry;
- eight exact U01 tracked paths by byte count and SHA-256;
- ignored, untracked, repository-local quarantine, raw, run-state, and contract
  paths;
- an unignored, absent, no-overwrite public report path;
- current OData identity, online state, byte count, acquisition/publication
  time, S3 identity, MD5, and BLAKE3 for exactly two products.

## Controlled intake contract

Ignored contract
`downloads/phase-two/contracts/P2O4-T39-U02/ward-creek-optical-intake-r001.json`
is 3,895 bytes with SHA-256
`12fa376d58c7104e12bbd04e2883cb9d1517e289dda573f934653a3068e0c391`.
The external controlled-intake validator passes before acquisition and again
with `--verify-files` after promotion. It records fail-on-collision,
atomic-no-replace promotion, reference-only secrets, exact routes, exact
expected sizes, provider MD5/BLAKE3, local SHA-256, one successful attempt per
asset, and exact staged/promoted equality. CDSE publishes no upstream SHA-256;
the contract states that limitation instead of inventing one.

## Exact custody

Run `BL-2026-07-24-ward-creek-optical-intake-r001` acquires one asset at a time.
The post request is unreachable until the promoted pre package passes a fresh
registration rehash. A local command-display timeout does not stop the child
transaction or alter bytes. It is not recorded as a provider failure.

| Role | Provider UUID | Bytes | Local SHA-256 | Provider MD5 | Provider BLAKE3 |
|---|---|---:|---|---|---|
| pre | `f6b6697d-5b7d-4049-8caf-8b0c7fdad4b7` | 1,198,399,787 | `0c03929bcc8697ab83eedcc2a4bbe6e1f428f2636a3477533ca101101b724961` | `7de4c0076a9ed4a3024ef46474b2aaac` | `737a71d70c36ae8d65d26df28e87730d08ed0bade1d2a327cce8a6b812a32c2a` |
| post | `51ddb0b7-8456-40a2-8301-e1651c951116` | 1,198,420,414 | `4374b4bf5a446244b7d8ad6ce6eed1fa8e93aef711df7e785a95581698fd53d0` | `28f18e0328dd4cb8ab45446a1a238fb0` | `eaf090416dd240478d85389ba018f1d193e09c270ff40a6f346ee9c4f8110eaf` |

Combined custody is 2,396,820,201 bytes. Both archives are regular,
single-linked files. Each SAFE ZIP has one expected root, `manifest.safe`, 95
members, a passing full CRC test, and 41 quality-mask or quality-metadata
members. The pre and post 10 m B04/B08 grids are 10,980 by 10,980. The 20 m
B11/B12/SCL grids are 5,490 by 5,490. Every inspected raster is EPSG:32610,
single-band, has the expected integer type and resolution, and reports no
embedded nodata value. B04/B08 align exactly at 10 m. B11/B12/SCL align exactly
at 20 m. Both dates use the same transform origins.

The exact temporal order is pre acquisition
`2019-08-01T18:59:21.024000Z`, MTBS ignition `2019-08-12`, and post acquisition
`2019-08-31T18:59:21.024000Z`.

## Evidence identities

| Evidence | Bytes | SHA-256 |
|---|---:|---|
| Pre registration manifest | 942 | `7dfaf433af866fbd6064e35b04825a3aa1ce303c88e981616ab8821245399b98` |
| Post registration manifest | 945 | `d4511d52832fad466c4d843f1c16d1246235afad36dbe7f50883303a99fe0f43` |
| Pre private state | 10,773 | `b466fe15e8166f09e646a8d802bb7df98fdd8d4736fc0d15b8fa9e2289271435` |
| Post private state | 10,785 | `b791b109df86c5f6231a589cfd540d73fc89f1983550e50c6c161cffc3814e3a` |
| Aggregate private state | 2,703 | `7d291d86a4f57eaa357fc44f817231246776a2dd6a86583a52baba5af4b86250` |
| Tracked custody report | 16,317 | `a8d89779b7508b439fee6cb5bc99dd926a62c56ab58da181b0f1b40b1bcc1f2f` |

Credential-free completed-custody verification and the independent
contract/file verifier both pass. Focused custody/provider/intake tests pass
65/65. The package-aware runtime and geo profiles pass after the command roster
advances from 90 to 91. The full suite reached 606 passes, one expected skip,
86 subtests, and one stale 90-command assertion; the assertion was corrected
and the exact 11-test runtime/custody rerun passes.

## Boundary and next gate

U02 proves exact optical custody and native archive structure. It does not
claim local fire-boundary pixel fitness, burn truth, labels, a dataset, a split,
a baseline, or a model. U03 must acquire and inspect the exact current MTBS
reference, including delivered notices, rights, identity, class domain, masks,
CRS/grid, nodata, cautions, and local fitness. Any unresolved archive term or
identity stops the milestone.
