# PRECHECK-2026-053 - Petes Lake NWI controlled-intake authorization

**Unit / issue / branch:** `P2O4-T33-U05` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Planned run:** `BL-2026-07-21-petes-lake-nwi-context-r001`

**Checked:** 2026-07-22T00:43:21.277914Z

## Decision

`PASS_EXACT_PETES_LAKE_NWI_BOUNDED_CONTEXT_INTAKE_ONLY`.

**Current status:** `PLANNED_UNDER_FINAL_AUDIT_NOT_YET_EFFECTIVE`. The implementation and these records are uncommitted. This decision becomes operative only after the final audit passes and the exact code/record state is committed, pushed, recorded on issue #521, and verified remote-equal. Zero NWI provider feature bytes have been requested or acquired.

`SOURCE-2026-032` and `TERMS-2026-028` pass for one bounded anonymous USFWS NWI transaction. The exact tracked bytes of this precheck and both prerequisite records must be code-bound in the same clean, pushed, remote-equal Git HEAD used to initialize custody. Runtime initialization records that resulting source commit and refuses another branch, dirty worktree, remote mismatch, or later commit during the transaction.

Offline initialization creates only the immutable plan and mutable intake contract. Before authorization or any NWI provider-data request, the five exact `fws.gov` pages in `TERMS-2026-028` require one request each, no automatic retry, a passing semantic terms refresh, and an ignored current hash receipt at `downloads/phase-two/runs/P2O4-T33-U05/petes-lake-nwi-context-r001-terms-refresh.json`. That terms-only refresh is separate from the provider-data roster below and authorizes no layer request by itself.

## Exact request roster

After the terms refresh passes, the provider-data transaction contains twelve and only twelve requests, in this dependency order:

1. `wetlands-layer-metadata` GET
2. `wetlands-pre-count` POST body SHA-256 `606e99684ad220d949b4c0175655067bf64e125c6cf583fc5d6b20eed0138442`
3. `wetlands-pre-ids` POST `0410618153b5352b07cb6957b97f0692aca501ac1faa4387bdc6bb7ae18f86c0`
4. `wetlands-features` POST `01bebd0807f008ba0841104c0c635a6b8db12157d285bc5f7431b34c6267b72e`
5. `wetlands-post-count` POST `606e99684ad220d949b4c0175655067bf64e125c6cf583fc5d6b20eed0138442`
6. `wetlands-post-ids` POST `0410618153b5352b07cb6957b97f0692aca501ac1faa4387bdc6bb7ae18f86c0`
7. `source-layer-metadata` GET
8. `source-pre-count` POST `606e99684ad220d949b4c0175655067bf64e125c6cf583fc5d6b20eed0138442`
9. `source-pre-ids` POST `0410618153b5352b07cb6957b97f0692aca501ac1faa4387bdc6bb7ae18f86c0`
10. `source-features` POST `46adcbc1c688746b53b8665687c2bdba57a598cd0b9920ad78a9228ccb179d3b`
11. `source-post-count` POST `606e99684ad220d949b4c0175655067bf64e125c6cf583fc5d6b20eed0138442`
12. `source-post-ids` POST `0410618153b5352b07cb6957b97f0692aca501ac1faa4387bdc6bb7ae18f86c0`

The first six use metadata GET `https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0?f=pjson` and query POST `https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0/query`. The last six use metadata GET `https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Data_Source/MapServer/0?f=pjson` and query POST `https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Data_Source/MapServer/0/query`. The observed metadata responses were `text/plain; charset=UTF-8`; only JSON-compatible media followed by strict duplicate-key, structure, schema, and value validation is acceptable.

Every POST uses exact query bounds `[584460, 4866240, 591640, 4871620]`, input CRS EPSG:32610, spatial intersection, and JSON output. Feature geometry is retained in provider EPSG:3857 for one pinned local transformation. No query token, cookie, credential, recipient, secret, paid service, or private route exists.

## Prospective source and derived-output gates

Before any feature value is observed, the source-project gate requires: nonplaceholder `PROJECT_NAME`, `DATA_SOURCE`, and `EMULSION`, excluding the case-normalized set `{unknown, none, null, <null>, n/a, na}`; exact `STATUS=Complete`; exact `SOURCE_TYPE` in `{BW,CIR,TC}`; positive `IMAGE_YR` no later than 2023; an exact pre-2023-08-25 `IMAGE_DATE` when the source year is 2023; date/year agreement whenever a date exists; positive `IMAGE_SCALE` no greater than 100,000 and present in parsed `ALL_SCALES`; and at least one `SUPPMAPINFO` or `FGDC_METADATA` locator outside the same placeholder set. The eligible source union is eroded inward by the 20 m cell half-diagonal before center sampling so the complete frozen boundary requires full-pixel eligible source coverage. Any-touch overlap from an ineligible or unknown source project excludes the affected cells and fails complete eligible coverage.

Mapped wetland/deepwater geometry is an exclusion only. It uses any-touch rasterization plus a policy buffer equal to the greater of 20 m and 1 mm at the maximum eligible source scale, with a 100 m hard maximum matching the acquired query halo. NWI absence never proves wetland absence or background. Public evidence is derived-only: neutral local IDs/hashes, normalized gate outcomes/reasons, necessary normalized dates/scales, and aggregate measurements. Provider geometry and verbatim feature attributes remain ignored and unpublished.

## Custody and stop gates

An exclusive per-worktree mutex, immutable plan receipt, exact ordered contract, passed current semantic terms receipt, single-link empty reservation, pre-network no-overwrite dispatch receipt, one-way dispatch marker, one attempt, no automatic retry, bounded size, allowed JSON-compatible media type, duplicate-key rejection, complete 2D finite polygon topology, exact count/ID bracketing, single-link promotion, exact package roster, empty staging roster, fresh final recomputation, and ignored/untracked verification all fail closed.

Every response must be individually started, fetched, verified, promoted, and externally contract-validated before the next request. A failed, interrupted, ambiguous, redirected, malformed, over-limit, stale, duplicate, extra, symlinked, multilinked, reordered, retrograde-time, terms-drifted, or Git-drifted attempt is retained and blocks every dependent request. No retry or replacement identity is inferred.

Passing custody authorizes only U05 reference-fitness inspection. It accepts zero reference pixels and creates no candidate, owner response, label, sixth event, dataset, split, baseline, model, release, field-validation, official, endorsed, operational, or emergency-ready result.
