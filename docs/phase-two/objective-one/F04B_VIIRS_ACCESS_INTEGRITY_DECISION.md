# F04-B VIIRS Access-Integrity Decision

**Decision date:** 2026-07-13 local / 2026-07-14 UTC

**Issue:** #317

**Branch:** `codex/p2o1-t03-viirs-inspection`

**Repository base:** `1858f3d5ad3c193f997bef4f9142c996e174af27`

**Decision:** `STOP — DELIVERY VALIDATOR PASSES; EARTHDATA CREDENTIAL REQUIRED`

## Action reviewed

Exercise the two exact LP DAAC routes selected by P2O1-T02 without credentials, validate the returned bodies independently of filename/status, render a traceable access report, and delete non-source responses. Do not add an account, secret, provider source asset, pixel parser, label, or analytical claim.

## Gate evidence

| Evidence | Record/artifact | Result |
|---|---|---|
| Issue/branch contract | Issue #317; `codex/p2o1-t03-viirs-inspection` | Passed after evidence-driven narrowing |
| Fresh terms/access research | `TERMS-2026-002`; `ACCESS-2026-003` | Open-use terms confirmed; credentialed delivery confirmed |
| Fail-closed behavior | BurnLens package `0.1.2`; 8 tests | Passed |
| Actual route responses | `VIIRS-ACCESS-PRECHECK-2026-001.json` | Both HTML responses rejected; zero source assets |
| Deterministic presentation | HTML and PNG report rebuild | Passed; exact hashes reproduced |
| Rendered review | `VIIRS-ACCESS-PRECHECK-2026-001.png` | Passed after missing-glyph remediation |
| Traceability and claims | `MANIFEST-2026-003`; `ACCESS_INTEGRITY-2026-001` | Passed for access evidence only |
| Secret/body retention | Working tree and content scans | Passed; zero rejected bodies retained |

## Why this gate stops

The exact LP DAAC product bytes require an owner-supplied Earthdata Login credential and application authorization. Adding or using that credential crosses an explicit controlling-goal stop condition. The selected Sentinel product independently requires an owner-supplied CDSE credential. Neither credential is present or implied.

## Next action after owner authorization

One new issue may acquire and validate the exact paired package only after the owner approves both credential boundaries. It must use secure out-of-repository credential handling, pass the payload-integrity validator before registration, verify provider/local checksums, inspect the real fire/QA/geolocation and Sentinel raster metadata, and render a bounded review before any label decision.

This checkpoint creates no provider source asset, wildfire observation, label, dataset, baseline, model, metric, map, application, official status, or operational capability.

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
