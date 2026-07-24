# PRECHECK-2026-073 - Ward Creek U01 source-gate handoff

**Unit / issue / branch:** `P2O4-T39-U01` / #554 / `codex/p2o4-t39-replacement-event`

**Final run:** `BL-2026-07-24-p2o4-t39-u01-r008`

**Base / implementation / final-code commits:** `657ba657ab9d23964dcaf76d377aec3a10e814da` / `61e7f3d56784e41db98e89782b607076d388e8aa` / `41b451d180f962aa1216384925c650fa43fcb9d6`

**Disposition:** `pass`

**Next eligible unit:** `P2O4-T39-U02`

## Entry and scope

Verified v0.50 lifecycle main is the exact branch base. Issue #554 is open and owns one replacement event. Ward Creek is the primary candidate. Akawana remains unopened because Ward Creek passes U01. No provider transaction, credential, archive request, custody mutation, candidate, owner response, label, dataset, split, baseline, model, inference, deployment, or external submission existed at entry.

The new command performs credential-free public metadata and terms requests only. It fails closed on exact Portal, MTBS, geometry, STAC, OData, pair, rights, and repository-trace contracts. It uses full Shapely polygon coverage and refuses a mismatched source commit or relevant dirty code before contacting a source.

## Exact tracked outputs

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `samples/reference/phase-two/REPLACEMENT-EVENT-SOURCE-2026-001.json` | 23,919 | `2038ffb62bd065779a59593fd4e4f1756ba418da857091a1226850ca92717895` |
| `samples/reference/phase-two/REPLACEMENT-EVENT-SOURCE-GATE-2026-001.json` | 15,015 | `77b30f5aec41473bc631684c48ba21b2d28d1c3f51d49d6e788393643af91559` |
| `samples/reference/phase-two/REPLACEMENT-EVENT-SOURCE-GATE-REPORT-2026-001.json` | 2,619 | `40edad405ac13bfd080b71d19de04ce7fc576577816cdb2fc9495ce6c3832c4f` |
| `samples/reference/phase-two/REPLACEMENT-EVENT-SOURCE-GATE-REPORT-2026-001.html` | 3,998 | `a645602eea5df31508353175abeefaff73fb8d39f0e432597a1d4374d75f1ec4` |

The source binds run r008, exact commit `41b451d...`, and access time `2026-07-24T19:01:34.734Z`. The gate validator reports valid and ready with two sources, 16 criteria, 31 evidence items, 12 fresh live evidence items, zero stale items, zero errors, zero blockers, and zero warnings.

## Retained attempts

| Attempt | Result | Retention |
|---|---|---|
| r001 | Portal WFS timeout before output | error trace retained in task execution history; zero output or provider byte |
| r002 | failed on the unseparated provider-area / Shapely-area values | exact failure retained; zero output or provider byte |
| r003 | failed on a stale Sentinel legal-notice URL | exact 404 trace retained; zero output or provider byte |
| r004 | generated a structurally invalid source-gate evidence shape | ignored quartet retained; gate validator reports the exact schema blockers |
| r005 | first structurally valid and ready ignored quartet | ignored quartet retained; superseded by repository-trace hardening |
| r006 | terminated shell child wrote late with a rejected invented commit string | exact ignored quartet retained under `P2O4-T39-U01-R006-LATE`; never promoted |
| r007 | valid tracked candidate from exact `b67091b...` | moved intact to ignored superseded custody after real narrow review exposed generic field labels |
| r008 | valid final tracked output from exact `41b451d...` | promoted as U01 evidence |

r004, r005, r006, and r007 retain exact file bytes and hashes in ignored repository-local run custody. No attempt contains a credential, token, private provider route, recipient detail, or archive byte.

## Code and environment validation

- Six replacement-source-gate tests pass.
- The full-polygon test rejects a footprint hole that a boundary-vertex-only shortcut can miss.
- OData size drift, source-commit mismatch, relevant dirty code, roster drift, and output overwrite fail closed.
- The locked runtime smoke passes after the one new command updates count, help count, and names length from 89 to 90.
- Python compilation, `uv lock --check`, locked environment sync, and `git diff --check` pass.
- The source-gate contract validator passes with no warnings.

## Real rendered output

The exact r008 HTML was served only on `127.0.0.1` from the tracked directory. The server was stopped after inspection.

- 1440 by 1000: title, decision, three metrics, event binding, and both exact product rows render without horizontal overflow.
- 390 by 844: the responsive table stacks both products with visible Role, SAFE identity, Bytes, and Provider UUID labels; no horizontal overflow.
- Both viewports show one candidate, two authorized optical archives, and zero U01 provider bytes.
- Browser warning and error logs are empty.
- No script or external page asset exists.

## Handoff

U01 passes. U02 may authenticate only through the existing protected CDSE account and acquire only the exact two products in SOURCE-2026-038. U02 must use ignored no-overwrite custody, retain every attempt, and verify exact OData size, MD5, BLAKE3, safe archive structure, native metadata, grids, CRS, nodata, masks, temporal relation, local quality, and registration before U03.

Any identity, checksum, online-state, rights, quota, custody, privacy, structure, or reproducibility drift stops U02. The source gate does not authorize a second event, Akawana acquisition, MTBS pixels, labels, a dataset, a split, a baseline, or a model.
